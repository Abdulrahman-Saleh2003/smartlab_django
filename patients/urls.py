

# patients/urls.py

from django.urls import path
from .views import patient_register
from .views import patient_register,patient_profile,patient_reset_password,patient_forget_password,patient_login

urlpatterns = [
    path('register/', patient_register, name='patient-register'),
    path('profile/', patient_profile, name='patient-profile'),
    path('login/', patient_login, name='patient-login'),   # ← أضف هذا
    path('forget-password/', patient_forget_password, name='patient-forget-password'),
    path('reset-password/', patient_reset_password, name='patient-reset-password'),
]