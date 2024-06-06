import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.paginator import Paginator
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from charity_platform import settings
from .models import Donation, Institution, Category, EmailVerificationToken, PasswordResetToken

from django.urls import reverse


def index(request):
    total_bags = Donation.objects.aggregate(total_bags=Sum('quantity'))['total_bags'] or 0
    supported_institutions = Institution.objects.count()

    # Пагинация для каждой секции
    foundations = Institution.objects.filter(type=Institution.FOUNDATION)
    ngos = Institution.objects.filter(type=Institution.NGO)
    local_collections = Institution.objects.filter(type=Institution.LOCAL_COLLECTION)

    paginator_foundations = Paginator(foundations, 5)
    paginator_ngos = Paginator(ngos, 5)
    paginator_local_collections = Paginator(local_collections, 5)

    page_number_foundations = request.GET.get('page_foundations')
    page_number_ngos = request.GET.get('page_ngos')
    page_number_local_collections = request.GET.get('page_local_collections')

    page_obj_foundations = paginator_foundations.get_page(page_number_foundations)
    page_obj_ngos = paginator_ngos.get_page(page_number_ngos)
    page_obj_local_collections = paginator_local_collections.get_page(page_number_local_collections)

    context = {
        'total_bags': total_bags,
        'supported_institutions': supported_institutions,
        'page_obj_foundations': page_obj_foundations,
        'page_obj_ngos': page_obj_ngos,
        'page_obj_local_collections': page_obj_local_collections,
    }

    return render(request, 'index.html', context)


@login_required
def add_donation(request):
    if request.method == 'POST':
        categories = request.POST.getlist('categories')
        quantity = request.POST.get('bags')
        institution_id = request.POST.get('organization')
        address = request.POST.get('address')
        city = request.POST.get('city')
        postcode = request.POST.get('postcode')
        phone = request.POST.get('phone')
        pick_up_date = request.POST.get('date')
        pick_up_time = request.POST.get('time')
        more_info = request.POST.get('more_info', '')

        try:
            institution = Institution.objects.get(id=institution_id)
        except Institution.DoesNotExist:
            messages.error(request, "Wybrana instytucja nie istnieje.")
            return redirect('donations:form')

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
        donation.save()
        donation.categories.set(categories)

        return redirect('donations:form_confirmation')

    categories = Category.objects.all()
    institutions = Institution.objects.prefetch_related('categories').all()
    return render(request, 'form.html', {'categories': categories, 'institutions': institutions})


@login_required
def form_confirmation(request):
    return render(request, 'form-confirmation.html')


def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('/admin/' if user.is_superuser else 'donations:index')
        else:
            errors = {'email': 'Nieprawidłowy email lub hasło'}
            return render(request, 'login.html', {'errors': errors})
    return render(request, 'login.html')


def register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        surname = request.POST.get('surname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        errors = {}
        if not name:
            errors['name'] = 'Imię jest wymagane'
        if not surname:
            errors['surname'] = 'Nazwisko jest wymagane'
        if not email:
            errors['email'] = 'Email jest wymagany'
        if not password:
            errors['password'] = 'Hasło jest wymagane'
        if password != password2:
            errors['password2'] = 'Hasła nie są zgodne'
        if User.objects.filter(username=email).exists():
            errors['email'] = 'Email już istnieje'

        if errors:
            return render(request, 'register.html', {'errors': errors})
        else:
            user = User.objects.create_user(username=email, password=password, first_name=name, last_name=surname,
                                            email=email)
            user.is_active = False
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
            plain_message = f"Cześć {user.first_name},\n\nDziękujemy za zarejestrowanie się na naszej stronie. Proszę kliknij poniższy link, aby aktywować swoje konto:\n\nhttp://{current_site.domain}{reverse('donations:activate', kwargs={'uidb64': urlsafe_base64_encode(force_bytes(user.pk)), 'token': token.token})}\n\nJeśli nie rejestrowałeś się na naszej stronie, zignoruj tę wiadomość."

            email = EmailMultiAlternatives(mail_subject, plain_message, settings.DEFAULT_FROM_EMAIL, [email])
            email.attach_alternative(message, "text/html")
            email.send()

            return redirect('donations:login')
    return render(request, 'register.html')


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and EmailVerificationToken.objects.filter(user=user, token=token).exists():
        user.is_active = True
        user.save()
        EmailVerificationToken.objects.filter(user=user).delete()
        return redirect('donations:login')
    else:
        return render(request, 'activation_invalid.html')


def logout(request):
    auth_logout(request)
    return redirect('donations:index')


@login_required
def user_profile(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            donation_id = data.get('donation_id')
            donation = Donation.objects.get(id=donation_id, user=request.user)
            donation.is_taken = not donation.is_taken
            donation.save()
            return JsonResponse({'status': 'success', 'is_taken': donation.is_taken})
        except (Donation.DoesNotExist, KeyError, ValueError):
            return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

    donations_list = Donation.objects.filter(user=request.user).order_by('is_taken', 'pick_up_date', 'pick_up_time')
    paginator = Paginator(donations_list, 8)  # Пагинация: 6 пожертвований на страницу

    page_number = request.GET.get('page')
    donations = paginator.get_page(page_number)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'user_profile.html', {'donations': donations})

    return render(request, 'user_profile.html', {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'email': request.user.email,
        'date_joined': request.user.date_joined,
        'last_login': request.user.last_login,
        'donations': donations,
    })


@login_required
def edit_profile(request):
    if request.method == 'POST':
        user = request.user
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if user.check_password(password):
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.save()
            return redirect('donations:user_profile')
        else:
            return render(request, 'edit_profile.html', {'error': 'Incorrect password'})

    return render(request, 'edit_profile.html')


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            return redirect('donations:user_profile')
        else:
            return render(request, 'change_password.html', {'form': form})
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})


def password_reset_request(request):
    if request.method == "POST":
        email = request.POST.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            token = PasswordResetToken.objects.create(user=user)

            # Send password reset email
            current_site = get_current_site(request)
            mail_subject = 'Reset your password'
            message = render_to_string('password_reset_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': token.token,
            })
            plain_message = f"Cześć {user.first_name},\n\nProszę kliknij poniższy link, aby zresetować swoje hasło:\n\nhttp://{current_site.domain}{reverse('donations:password_reset_confirm', kwargs={'uidb64': urlsafe_base64_encode(force_bytes(user.pk)), 'token': token.token})}\n\nJeśli nie prosiłeś o zresetowanie hasła, zignoruj tę wiadomość."

            email = EmailMultiAlternatives(mail_subject, plain_message, settings.DEFAULT_FROM_EMAIL, [email])
            email.attach_alternative(message, "text/html")
            email.send()

            return render(request, 'password_reset.html',
                          {'message': 'Link do resetowania hasła został wysłany na Twój email.'})
        else:
            return render(request, 'password_reset.html', {'message': 'Email nie został znaleziony.'})
    return render(request, 'password_reset.html')


def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and PasswordResetToken.objects.filter(user=user, token=token).exists():
        if request.method == "POST":
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            if password1 == password2:
                user.set_password(password1)
                user.save()
                PasswordResetToken.objects.filter(user=user).delete()
                return redirect('donations:login')
            else:
                return render(request, 'password_reset_confirm.html', {'error': 'Hasła nie są zgodne.'})
        return render(request, 'password_reset_confirm.html')
    else:
        return render(request, 'password_reset_confirm.html', {'error': 'Nieprawidłowy link do resetowania hasła.'})
