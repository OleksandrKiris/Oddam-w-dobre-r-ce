from django.shortcuts import render


def index(request):
    return render(request, 'index.html')


def add_donation(request):
    return render(request, 'form.html')


def login(request):
    return render(request, 'login.html')


def register(request):
    return render(request, 'register.html')


def form_confirmation(request):
    return render(request, 'form-confirmation.html')
