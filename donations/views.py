from django.shortcuts import render
from django.db.models import Sum
from .models import Donation, Institution


def index(request):
    total_bags = Donation.objects.aggregate(total_bags=Sum('quantity'))['total_bags'] or 0
    supported_institutions = Institution.objects.count()
    foundations = Institution.objects.filter(type=Institution.FOUNDATION)
    ngos = Institution.objects.filter(type=Institution.NGO)
    local_collections = Institution.objects.filter(type=Institution.LOCAL_COLLECTION)

    context = {
        'total_bags': total_bags,
        'supported_institutions': supported_institutions,
        'foundations': foundations,
        'ngos': ngos,
        'local_collections': local_collections,
    }
    return render(request, 'index.html', context)


def add_donation(request):
    return render(request, 'form.html')


def login(request):
    return render(request, 'login.html')


def register(request):
    return render(request, 'register.html')


def form_confirmation(request):
    return render(request, 'form-confirmation.html')
