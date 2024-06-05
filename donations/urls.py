from django.urls import path
from . import views

app_name = 'donations'

urlpatterns = [
    path('', views.index, name='index'),
    path('add_donation/', views.add_donation, name='add_donation'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
    path('form_confirmation/', views.form_confirmation, name='form_confirmation'),
    path('user_profile/', views.user_profile, name='user_profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('change_password/', views.change_password, name='change_password'),
]
