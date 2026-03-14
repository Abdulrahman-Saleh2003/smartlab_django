# receptionists/urls.py

from django.urls import path
from receptionists.views import *

urlpatterns = [
    path('register/', receptionist_register, name='receptionist-register'),
    path('login/', receptionist_login, name='receptionist-login'),
    path('profile/', receptionist_profile, name='receptionist-profile'),
]