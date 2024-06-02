from django.shortcuts import render
from django.db.models import Sum
from .models import Donation, Institution


def index(request):
    total_bags = Donation.objects.aggregate(total_bags=Sum('quantity'))['total_bags'] or 0
    supported_institutions = Institution.objects.count()
    context = {
        'total_bags': total_bags,
        'supported_institutions': supported_institutions,
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
