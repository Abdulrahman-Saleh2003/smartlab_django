# lab_technicians/urls.py
from django.urls import path
from .views import lab_technician_register, lab_technician_login, lab_technician_profile

urlpatterns = [
    path('register/', lab_technician_register, name='lab-technician-register'),
    path('login/', lab_technician_login, name='lab-technician-login'),
    path('profile/', lab_technician_profile, name='lab-technician-profile'),
]