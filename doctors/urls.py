

from django.urls import path
from doctors import views
from doctors.views import *
from doctors.views import doctor_link_patient_by_credentials,doctor_register,doctor_login,doctor_profile,doctor_reset_password,update_doctor_profile,doctor_forget_password,doctor_unlink_patient


from doctors.views import search_patient , create_medical_review , create_medical_review_via_url , get_patient_laboratory_reports , get_patient_reviews_by_doctor
from doctors.views import get_full_report_details , get_doctor_reviews , get_reviewed_patients_details , get_specific_patient_details , update_medical_review 
from doctors.views import get_reports_by_body_part , get_reports_by_category , get_reports_by_priority , get_reports_by_report_type , get_reports_by_status 


urlpatterns = [
    path('link-patient/', doctor_link_patient_by_credentials, name='doctor-link-patient'),

    path('register/', doctor_register, name='doctor-register'),
    path('login/', doctor_login, name='doctor-login'),
    path('profile/', doctor_profile, name='doctor-profile'),
    path('forget-password/', doctor_forget_password, name='doctor-forget-password'),
    path('reset-password/', doctor_reset_password, name='doctor-reset-password'),
    path('me/update/', update_doctor_profile, name='update-doctor-profile'),
    path('my-patients/', doctor_get_my_patients, name='doctor-my-patients'),
    path('unlink-patient/', doctor_unlink_patient, name='doctor-unlink-patient'),



    path('search-patient/', search_patient, name='doctor-search-patient'),
    path('report_details/<uuid:report_id>/', get_full_report_details, name='report_details'),

    path('patient/<uuid:patient_id>/body-part/<str:part_name>/', get_reports_by_body_part, name='reports-by-body-part'),
    path('patient/<uuid:patient_id>/report_type/<str:type_name>/', get_reports_by_report_type, name='reports-by-report_type'),

    path('patient/<uuid:patient_id>/category/<str:category_name>/', get_reports_by_category, name='reports-by-category'),

    path('patient/<uuid:patient_id>/priority/<str:priority_name>/', get_reports_by_priority, name='reports-by-priority'),
    path('patient/<uuid:patient_id>/status/<str:status_name>/', get_reports_by_status, name='reports-by-status'),

    path('patient/<uuid:patient_id>/laboratory/', get_patient_laboratory_reports, name='patient-lab-reports'),
    path('create-review/', create_medical_review, name='create-medical-review'),

    path('patient/<uuid:patient_id>/report/<uuid:report_id>/review/', create_medical_review_via_url, name='create-medical-review-url'),
    path('my-reviews/', get_doctor_reviews, name='doctor-reviews'), 

    path('my-reviewed-patients/', get_reviewed_patients_details, name='reviewed-patients-details'),
    path('patient/<uuid:patient_id>/my-reviews/', get_patient_reviews_by_doctor, name='get-my-reviews-for-patient'),

    path('patient/<uuid:patient_id>/details/', get_specific_patient_details, name='specific-patient-details'),
    path('review/<uuid:review_id>/update/', update_medical_review, name='update-medical-review'),
]

  
      