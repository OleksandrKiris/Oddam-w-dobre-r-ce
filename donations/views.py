# Importowanie potrzebnych bibliotek
import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.paginator import Paginator
from django.db.models import Sum, Q
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from charity_platform import settings
from .forms import ContactForm, ProblemReportForm
from .models import EmailVerificationToken, PasswordResetToken, Institution, Category, Donation


# Widok dla strony głównej
def index(request):
    """
    Widok strony głównej serwisu, który wyświetla główne statystyki oraz listę instytucji.
    Zlicza łączną liczbę worków z darowizn oraz liczbę wspieranych instytucji.
    Umożliwia paginację dla listy instytucji w trzech kategoriach: fundacje, NGO i zbiórki lokalne.
    """
    total_bags = Donation.objects.aggregate(total_bags=Sum('quantity'))[
                     'total_bags'] or 0  # Zliczenie łącznej ilości worków
    supported_institutions = Institution.objects.count()  # Zliczenie liczby wspieranych instytucji

    # Paginacja dla każdej sekcji instytucji
    foundations = Institution.objects.filter(type=Institution.FOUNDATION)  # Pobranie listy fundacji
    ngos = Institution.objects.filter(type=Institution.NGO)  # Pobranie listy NGO
    local_collections = Institution.objects.filter(
        type=Institution.LOCAL_COLLECTION)  # Pobranie listy lokalnych zbiórek

    paginator_foundations = Paginator(foundations, 5)  # Paginacja dla fundacji (5 na stronę)
    paginator_ngos = Paginator(ngos, 5)  # Paginacja dla NGO (5 na stronę)
    paginator_local_collections = Paginator(local_collections, 5)  # Paginacja dla lokalnych zbiórek (5 na stronę)

    page_number_foundations = request.GET.get('page_foundations')  # Numer strony dla fundacji
    page_number_ngos = request.GET.get('page_ngos')  # Numer strony dla NGO
    page_number_local_collections = request.GET.get('page_local_collections')  # Numer strony dla lokalnych zbiórek

    page_obj_foundations = paginator_foundations.get_page(
        page_number_foundations)  # Pobranie odpowiedniej strony dla fundacji
    page_obj_ngos = paginator_ngos.get_page(page_number_ngos)  # Pobranie odpowiedniej strony dla NGO
    page_obj_local_collections = paginator_local_collections.get_page(
        page_number_local_collections)  # Pobranie odpowiedniej strony dla lokalnych zbiórek

    context = {
        'total_bags': total_bags,  # Przekazanie do szablonu łącznej ilości worków
        'supported_institutions': supported_institutions,  # Przekazanie do szablonu liczby wspieranych instytucji
        'page_obj_foundations': page_obj_foundations,  # Przekazanie do szablonu strony fundacji
        'page_obj_ngos': page_obj_ngos,  # Przekazanie do szablonu strony NGO
        'page_obj_local_collections': page_obj_local_collections,  # Przekazanie do szablonu strony lokalnych zbiórek
    }

    return render(request, 'index.html', context)  # Renderowanie strony głównej z danymi kontekstowymi


# Widok do dodania darowizny
@login_required(login_url='donations:register')
def add_donation(request):
    """
    Widok formularza dodawania darowizny, umożliwiający zalogowanemu użytkownikowi przekazanie darowizny.
    Sprawdza poprawność wprowadzonych danych i zapisuje darowiznę do bazy danych.
    """
    if request.method == 'POST':
        categories = request.POST.getlist('categories')  # Pobranie listy kategorii z formularza
        quantity = request.POST.get('bags')  # Pobranie ilości worków z formularza
        institution_id = request.POST.get('organization')  # Pobranie ID instytucji z formularza
        address = request.POST.get('address')  # Pobranie adresu z formularza
        city = request.POST.get('city')  # Pobranie miasta z formularza
        postcode = request.POST.get('postcode')  # Pobranie kodu pocztowego z formularza
        phone = request.POST.get('phone')  # Pobranie numeru telefonu z formularza
        pick_up_date = request.POST.get('date')  # Pobranie daty odbioru z formularza
        pick_up_time = request.POST.get('time')  # Pobranie czasu odbioru z formularza
        more_info = request.POST.get('more_info', '')  # Pobranie dodatkowych informacji z formularza (opcjonalne)

        # Sprawdzenie, czy wszystkie wymagane dane są obecne
        if not categories or not quantity or not institution_id or not address or not city or not postcode or not phone or not pick_up_date or not pick_up_time:
            return JsonResponse({'success': False, 'error': 'Wszystkie pola muszą być wypełnione.'})

        try:
            institution = Institution.objects.get(id=institution_id)  # Pobranie instytucji na podstawie ID
        except Institution.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Wybrana instytucja nie istnieje.'})

        try:
            # Tworzenie obiektu darowizny i zapisanie go do bazy danych
            donation = Donation(
                quantity=quantity,
                institution=institution,
                address=address,
                phone_number=phone,
                city=city,
                zip_code=postcode,
                pick_up_date=pick_up_date,
                pick_up_time=pick_up_time,
                pick_up_comment=more_info,
                user=request.user
            )
            donation.save()  # Zapisanie darowizny do bazy danych
            donation.categories.set(categories)  # Przypisanie kategorii do darowizny

            return redirect('donations:form_success')  # Przekierowanie na stronę potwierdzenia
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})  # Obsługa błędów i zwrócenie odpowiedzi JSON

    categories = Category.objects.all()  # Pobranie wszystkich kategorii
    institutions = Institution.objects.prefetch_related(
        'categories').all()  # Pobranie wszystkich instytucji z powiązanymi kategoriami
    return render(request, 'form.html',
                  {'categories': categories, 'institutions': institutions})  # Renderowanie formularza z danymi


# Widok dla potwierdzenia formularza
@login_required
def form_success(request):
    """
    Widok potwierdzenia formularza dodawania darowizny, wyświetlany po pomyślnym dodaniu darowizny.
    """
    return render(request, 'form_success.html')  # Renderowanie strony potwierdzenia


# Widok logowania
def login(request):
    """
    Widok logowania użytkownika. Umożliwia użytkownikom logowanie się na swoje konto.
    Weryfikuje dane logowania i autoryzuje użytkownika.
    """
    if request.method == 'POST':
        email = request.POST.get('email')  # Pobranie adresu email z formularza logowania
        password = request.POST.get('password')  # Pobranie hasła z formularza logowania

        user = authenticate(request, username=email, password=password)  # Uwierzytelnienie użytkownika
        if user is not None:
            auth_login(request, user)  # Zalogowanie użytkownika
            return redirect('/admin/' if user.is_superuser else 'donations:index')  # Przekierowanie po zalogowaniu
        else:
            errors = {'email': 'Nieprawidłowy email lub hasło'}  # Błąd uwierzytelnienia
            return render(request, 'login.html', {'errors': errors})  # Renderowanie strony logowania z błędami
    return render(request, 'login.html')  # Renderowanie strony logowania


# Widok rejestracji
def register(request):
    """
    Widok rejestracji nowego użytkownika. Umożliwia tworzenie nowych kont użytkowników.
    Sprawdza poprawność danych rejestracyjnych i zapisuje użytkownika do bazy danych.
    """
    if request.method == 'POST':
        name = request.POST.get('name')  # Pobranie imienia z formularza rejestracji
        surname = request.POST.get('surname')  # Pobranie nazwiska z formularza rejestracji
        email = request.POST.get('email')  # Pobranie adresu email z formularza rejestracji
        password = request.POST.get('password')  # Pobranie hasła z formularza rejestracji
        password2 = request.POST.get('password2')  # Pobranie potwierdzenia hasła z formularza rejestracji

        errors = {}
        if not name:
            errors['name'] = ['Imię jest wymagane']  # Błąd braku imienia
        if not surname:
            errors['surname'] = ['Nazwisko jest wymagane']  # Błąd braku nazwiska
        if not email:
            errors['email'] = ['Email jest wymagany']  # Błąd braku emaila
        if not password:
            errors['password'] = ['Hasło jest wymagane']  # Błąd braku hasła
        if password != password2:
            errors['password2'] = ['Hasła nie są zgodne']  # Błąd niezgodności haseł
        try:
            validate_password(password)  # Walidacja hasła
        except ValidationError as e:
            errors['password'] = list(e.messages)  # Błędy walidacji hasła
        if User.objects.filter(username=email).exists():
            errors['email'] = ['Email już istnieje']  # Błąd istnienia użytkownika z takim emailem

        if errors:
            return render(request, 'register.html', {'errors': errors})  # Renderowanie strony rejestracji z błędami
        else:
            user = User.objects.create_user(username=email, password=password, first_name=name, last_name=surname,
                                            email=email)
            user.is_active = False  # Ustawienie konta jako nieaktywne
            user.save()

            # Tworzenie tokenu weryfikacyjnego
            token = EmailVerificationToken.objects.create(user=user)

            # Wysyłanie emaila weryfikacyjnego
            current_site = get_current_site(request)
            mail_subject = 'Aktywuj swoje konto'
            message = render_to_string('email_verification.html', {
                'user': user,
                'domain': current_site.domain,
                'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': token.token,
            })
            plain_message = (
                f"Cześć {user.first_name},\n\nDziękujemy za zarejestrowanie się na naszej stronie. "
                f"Proszę kliknij poniższy link, aby aktywować swoje konto:\n\n"
                f"http://{current_site.domain}{reverse('donations:activate', kwargs={'uidb64': urlsafe_base64_encode(force_bytes(user.pk)), 'token': token.token})}\n\n"
                "Jeśli nie rejestrowałeś się na naszej stronie, zignoruj tę wiadomość."
            )

            email = EmailMultiAlternatives(mail_subject, plain_message, settings.DEFAULT_FROM_EMAIL, [email])
            email.attach_alternative(message, "text/html")
            email.send()

            return redirect('donations:login')  # Przekierowanie na stronę logowania po rejestracji
    return render(request, 'register.html')  # Renderowanie strony rejestracji


# Widok aktywacji konta
def activate(request, uidb64, token):
    """
    Widok aktywacji konta użytkownika za pomocą emaila weryfikacyjnego.
    Weryfikuje token i aktywuje konto użytkownika.
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and EmailVerificationToken.objects.filter(user=user, token=token).exists():
        user.is_active = True  # Aktywacja konta użytkownika
        user.save()
        EmailVerificationToken.objects.filter(user=user).delete()  # Usunięcie tokenu weryfikacyjnego
        return redirect('donations:login')  # Przekierowanie na stronę logowania po aktywacji
    else:
        return render(request, 'activation_invalid.html')  # Renderowanie strony błędu aktywacji


# Widok wylogowania
def logout(request):
    """
    Widok wylogowania użytkownika. Wylogowuje użytkownika z sesji.
    """
    auth_logout(request)
    return redirect('donations:index')  # Przekierowanie na stronę główną po wylogowaniu


# Widok profilu użytkownika
@login_required
def user_profile(request):
    """
    Widok profilu użytkownika, wyświetlający dane użytkownika oraz listę jego darowizn.
    Umożliwia filtrowanie i wyszukiwanie darowizn.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            donation_id = data.get('donation_id')

            donation = get_object_or_404(Donation, id=donation_id, user=request.user)

            donation.is_taken_by_user = not donation.is_taken_by_user
            donation.save()
            return JsonResponse({'status': 'success', 'is_taken_by_user': donation.is_taken_by_user})
        except Donation.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Darowizna nie istnieje'}, status=400)
        except KeyError:
            return JsonResponse({'status': 'error', 'message': 'Nieprawidłowe dane żądania'}, status=400)
        except ValueError as e:
            return JsonResponse({'status': 'error', 'message': 'Nieprawidłowe żądanie'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'Wystąpił nieoczekiwany błąd'}, status=500)

    donations_list = Donation.objects.filter(user=request.user)

    # Obsługa wyszukiwania i filtrowania
    search_query = request.GET.get('search', '')  # Pobranie zapytania wyszukiwania z parametrów URL
    filter_status = request.GET.get('status', '')  # Pobranie statusu filtra z parametrów URL

    if search_query:
        donations_list = donations_list.filter(
            Q(institution__name__icontains=search_query) |
            Q(categories__name__icontains=search_query) |
            Q(address__icontains=search_query) |
            Q(city__icontains=search_query)
        ).distinct()  # Filtrowanie darowizn na podstawie zapytania wyszukiwania

    if filter_status:
        donations_list = donations_list.filter(status=filter_status)  # Filtrowanie darowizn na podstawie statusu

    donations_list = donations_list.order_by('is_taken_by_user', 'pick_up_date', 'pick_up_time')  # Sortowanie darowizn

    paginator = Paginator(donations_list, 8)  # Paginacja listy darowizn (8 na stronę)
    page_number = request.GET.get('page')  # Pobranie numeru strony z parametrów URL
    donations = paginator.get_page(page_number)  # Pobranie odpowiedniej strony darowizn

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'user_profile.html',
                      {'donations': donations})  # Renderowanie strony profilu z danymi darowizn

    return render(request, 'user_profile.html', {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'email': request.user.email,
        'date_joined': request.user.date_joined,
        'last_login': request.user.last_login,
        'donations': donations,
        'search_query': search_query,
        'filter_status': filter_status,
    })  # Renderowanie strony profilu z danymi użytkownika i darowizn


# Widok edycji profilu
@login_required
def edit_profile(request):
    """
    Widok edycji profilu użytkownika, umożliwiający aktualizację danych osobowych.
    """
    if request.method == 'POST':
        user = request.user
        first_name = request.POST.get('first_name')  # Pobranie nowego imienia z formularza
        last_name = request.POST.get('last_name')  # Pobranie nowego nazwiska z formularza
        email = request.POST.get('email')  # Pobranie nowego emaila z formularza
        password = request.POST.get('password')  # Pobranie hasła do potwierdzenia zmiany danych

        if user.check_password(password):  # Sprawdzenie poprawności hasła
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.save()  # Zapisanie zmian w danych użytkownika
            return redirect('donations:user_profile')  # Przekierowanie na stronę profilu użytkownika
        else:
            return render(request, 'edit_profile.html',
                          {'error': 'Incorrect password'})  # Renderowanie strony edycji profilu z błędem

    return render(request, 'edit_profile.html')  # Renderowanie strony edycji profilu


# Widok zmiany hasła
@login_required
def change_password(request):
    """
    Widok zmiany hasła użytkownika, umożliwiający aktualizację hasła.
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)  # Formularz zmiany hasła
        if form.is_valid():
            user = form.save()  # Zapisanie nowego hasła
            update_session_auth_hash(request, user)  # Aktualizacja sesji użytkownika
            return redirect('donations:user_profile')  # Przekierowanie na stronę profilu użytkownika
        else:
            return render(request, 'change_password.html', {'form': form})  # Renderowanie strony zmiany hasła z błędami
    else:
        form = PasswordChangeForm(request.user)  # Inicjalizacja formularza zmiany hasła
    return render(request, 'change_password.html', {'form': form})  # Renderowanie strony zmiany hasła


# Widok resetowania hasła
def password_reset_request(request):
    """
    Widok żądania resetowania hasła, umożliwiający użytkownikowi zainicjowanie procesu resetowania hasła.
    Wysyła email z linkiem do resetowania hasła.
    """
    if request.method == "POST":
        # Pobranie adresu email z formularza
        email = request.POST.get('email')
        # Sprawdzenie, czy użytkownik o podanym adresie email istnieje
        if User.objects.filter(email=email).exists():
            # Pobranie użytkownika na podstawie adresu email
            user = User.objects.get(email=email)
            # Utworzenie tokenu do resetowania hasła
            token = PasswordResetToken.objects.create(user=user)

            # Pobranie bieżącej domeny
            current_site = get_current_site(request)
            # Temat wiadomości email
            mail_subject = 'Reset your password'
            # Renderowanie wiadomości email
            message = render_to_string('password_reset_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': token.token,
            })
            # Treść wiadomości w formacie tekstowym
            plain_message = f"Cześć {user.first_name},\n\nProszę kliknij poniższy link, aby zresetować swoje hasło:\n\nhttp://{current_site.domain}{reverse('donations:password_reset_confirm', kwargs={'uidb64': urlsafe_base64_encode(force_bytes(user.pk)), 'token': token.token})}\n\nJeśli nie prosiłeś o zresetowanie hasła, zignoruj tę wiadomość."

            # Utworzenie i wysłanie wiadomości email
            email = EmailMultiAlternatives(mail_subject, plain_message, settings.DEFAULT_FROM_EMAIL, [email])
            email.attach_alternative(message, "text/html")
            email.send()

            # Powiadomienie użytkownika, że link do resetowania hasła został wysłany
            return render(request, 'password_reset.html', {'message': 'Link do resetowania hasła został wysłany na Twój email.'})
        else:
            # Powiadomienie użytkownika, że podany email nie został znaleziony
            return render(request, 'password_reset.html', {'message': 'Email nie został znaleziony.'})
    # Renderowanie strony żądania resetowania hasła
    return render(request, 'password_reset.html')


# Widok potwierdzenia resetu hasła
def password_reset_confirm(request, uidb64=None, token=None):
    """
    Widok potwierdzenia resetu hasła, umożliwiający użytkownikowi ustawienie nowego hasła.
    Weryfikuje token resetu hasła i zapisuje nowe hasło użytkownika.
    """
    if request.method == 'POST':
        # Pobranie nowego hasła z formularza
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        # Sprawdzenie, czy hasła są zgodne
        if password1 != password2:
            return render(request, 'password_reset_confirm.html', {'error': 'Hasła nie są zgodne'})
        try:
            # Walidacja nowego hasła
            validate_password(password1)
        except ValidationError as e:
            # Wyświetlenie błędów walidacji hasła
            return render(request, 'password_reset_confirm.html', {'error': list(e.messages)})

        try:
            # Dekodowanie UID użytkownika
            uid = force_str(urlsafe_base64_decode(uidb64))
            # Pobranie użytkownika na podstawie UID
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        # Sprawdzenie, czy użytkownik i token istnieją
        if user is not None and PasswordResetToken.objects.filter(user=user, token=token).exists():
            # Ustawienie nowego hasła
            user.set_password(password1)
            user.save()
            # Usunięcie tokenu resetu hasła
            PasswordResetToken.objects.filter(user=user).delete()
            # Przekierowanie na stronę logowania po zmianie hasła
            return redirect('donations:login')
        else:
            # Renderowanie strony błędu aktywacji
            return render(request, 'activation_invalid.html')
    # Renderowanie strony potwierdzenia resetu hasła
    return render(request, 'password_reset_confirm.html')



# Widok kontaktowy
def contact(request):
    """
    Widok kontaktowy, umożliwiający użytkownikom wysyłanie wiadomości kontaktowych do administratorów serwisu.
    """
    if request.method == 'POST':
        form = ContactForm(request.POST)  # Formularz kontaktowy
        if form.is_valid():
            contact_message = form.save()  # Zapisanie wiadomości kontaktowej
            # Wysłanie emaila administratorom
            subject = f"Nowa wiadomość kontaktowa od {contact_message.name} {contact_message.surname}"
            message = f"Imię: {contact_message.name}\nNazwisko: {contact_message.surname}\nEmail: {contact_message.email}\n\nWiadomość:\n{contact_message.message}"
            admin_emails = [user.email for user in
                            User.objects.filter(is_superuser=True)]  # Pobranie emaili administratorów
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, admin_emails)  # Wysłanie emaila
            messages.success(request, 'Twoja wiadomość została wysłana. Dziękujemy za kontakt!')
            return redirect('donations:index')  # Przekierowanie na stronę główną po wysłaniu wiadomości
        else:
            for field, error_list in form.errors.items():
                for error in error_list:
                    messages.error(request, error)  # Wyświetlenie błędów formularza
    else:
        form = ContactForm()  # Inicjalizacja formularza kontaktowego
    return render(request, 'base.html', {'form': form})  # Renderowanie strony kontaktowej


# Widok polityki prywatności
def privacy_policy(request):
    """
    Widok polityki prywatności, wyświetlający zasady ochrony danych osobowych.
    """
    return render(request, 'privacy_policy.html')  # Renderowanie strony polityki prywatności


# Widok warunków korzystania z usługi
def terms_of_service(request):
    """
    Widok warunków korzystania z usługi, wyświetlający zasady korzystania z serwisu.
    """
    return render(request, 'terms_of_service.html')  # Renderowanie strony warunków korzystania z usługi


# Widok zgłaszania problemów
@login_required
def report_problem(request):
    """
    Widok zgłaszania problemów, umożliwiający użytkownikom zgłaszanie problemów z serwisem.
    """
    if request.method == 'POST':
        form = ProblemReportForm(request.POST, request.FILES)  # Formularz zgłaszania problemów
        if form.is_valid():
            report = form.save(commit=False)
            report.user = request.user  # Przypisanie zgłoszenia do zalogowanego użytkownika
            report.save()
            messages.success(request, 'Your problem report has been submitted successfully.')
            return redirect(
                'donations:user_profile')  # Przekierowanie na stronę profilu użytkownika po zgłoszeniu problemu
        else:
            messages.error(request, 'There was an error with your submission.')  # Wyświetlenie błędów formularza
    else:
        form = ProblemReportForm()  # Inicjalizacja formularza zgłaszania problemów
    return render(request, 'report_problem.html', {'form': form})  # Renderowanie strony zgłaszania problemów
