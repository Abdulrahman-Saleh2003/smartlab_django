

# lab_reports/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('analyze/', views.analyze_report, name='analyze-report'),
    path('result/<str:job_id>/', views.check_result, name='check-result'),
    path('result/<str:job_id>/', views.check_result, name='check-result'),  # ← هاد ناقص
    

]