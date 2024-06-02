from django.shortcuts import render

from donations.models import Donation, Institution
from django.db.models import Sum


def index(request):
    total_bags = Donation.objects.aggregate(total=Sum('quantity'))['total'] or 0
    supported_institutions = Institution.objects.filter(donation__isnull=False).distinct().count()

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
