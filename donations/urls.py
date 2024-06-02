from django.urls import path
from . import views

app_name = 'donations'

urlpatterns = [
    path('', views.index, name='index'),
    path('add_donation/', views.add_donation, name='add_donation'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('form-confirmation/', views.form_confirmation, name='form_confirmation'),
]
