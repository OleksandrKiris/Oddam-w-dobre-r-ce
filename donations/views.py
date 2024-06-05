from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Sum
from .models import Donation, Institution, Category
from django.contrib.auth import logout as auth_logout


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
            user.save()
            return redirect('donations:login')

    return render(request, 'register.html')


def logout(request):
    auth_logout(request)
    return redirect('donations:index')


@login_required
def user_profile(request):
    return render(request, 'user_profile.html', {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'email': request.user.email,
        'date_joined': request.user.date_joined,
        'last_login': request.user.last_login,
    })
