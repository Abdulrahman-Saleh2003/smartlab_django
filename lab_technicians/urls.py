# lab_technicians/urls.py
from django.urls import path
from .views import lab_technician_register, lab_technician_login, lab_technician_profile


from .views import search_patient , patient_overview , patient_record , upload_analysis , my_uploaded_analyses


urlpatterns = [
    path('register/', lab_technician_register, name='lab-technician-register'),
    path('login/', lab_technician_login, name='lab-technician-login'),
    path('profile/', lab_technician_profile, name='lab-technician-profile'),



    path('search/', search_patient, name='search_patient'),
    path('patient/<uuid:patient_id>/overview/', patient_overview, name='patient_overview'),
    path('patient/<uuid:patient_id>/record/', patient_record, name='patient_record'),
    path('patient/<uuid:patient_id>/upload/', upload_analysis, name='upload_analysis'),
    path('my-uploads/', my_uploaded_analyses, name='my_uploaded_analyses'),

]

