from django.urls import path
from . import views

urlpatterns = [
    path('llama/', views.chat_llama, name='chat-llama'),
    path('voiceflow/', views.chat_voiceflow, name='chat-voiceflow'),
     path(
        'full-analysis/',
        views.full_medical_analysis
    ),
]