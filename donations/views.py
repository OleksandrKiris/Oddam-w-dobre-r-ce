from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Sum
from .models import Donation, Institution


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


def add_donation(request):
    return render(request, 'form.html')


def login(request):
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


def form_confirmation(request):
    return render(request, 'form-confirmation.html')
