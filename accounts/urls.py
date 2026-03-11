

from django.urls import path
from . import views
# accounts/urls.py


urlpatterns = [
    path('register/', views.register, name='register'),
    path('signup/',    views.signup,    name='signup'),

    path('login/',     views.login_view, name='login'),
    path('me/',        views.current_user, name='current_user'),
    path('update/',    views.update_user, name='update_user'),
        path('forget-password/', views.forget_password, name='forget_password'),
    path('reset-password/', views.reset_password, name='reset_password'),
]