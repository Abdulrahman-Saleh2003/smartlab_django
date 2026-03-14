

from django.urls import path
from doctors.views import *
# accounts/urls.py


# urlpatterns = [
#     path('me/update/', views.update_doctor_profile, name='update-doctor-profile'),
#     path('register/', views.doctor_register, name='doctor-register'),
# ]


urlpatterns = [
    path('register/', doctor_register, name='doctor-register'),
    path('login/', doctor_login, name='doctor-login'),
    path('profile/', doctor_profile, name='doctor-profile'),
    path('forget-password/', doctor_forget_password, name='doctor-forget-password'),
    path('reset-password/', doctor_reset_password, name='doctor-reset-password'),
    path('me/update/', update_doctor_profile, name='update-doctor-profile'),
]