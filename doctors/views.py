import random

from django.shortcuts import render

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model, authenticate, login, update_session_auth_hash

from report_reviews.models import report_review
from report_reviews.serializers import  ReportReviewSerializer
from .serializers import  UserSerializer
from .models import Doctor
from accounts.models import CustomUser

from .serializers import DoctorSerializer,DoctorRegisterSerializer

from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta

from django.contrib.auth.hashers import make_password
from  patients.serializers import PatientRegisterSerializer, PatientSearchSerializer, PatientSerializer

 
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from accounts.models import CustomUser
from patients.models import Patient
from .models import Doctor



 
from django.shortcuts import get_object_or_404
from lab_reports.models import LabReport
from lab_reports.serializers import LabReportSerializer

 


User = get_user_model()

# Create your views here.
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_doctor_profile(request):
    if request.user.role != 'doctor':
        return Response({"error": "لست طبيبًا"}, status=403)
    
    try:
        doctor = request.user.doctor_profile
    except Doctor.DoesNotExist:
        return Response({"error": "لم يتم إنشاء بروفايل الطبيب بعد"}, status=404)

    serializer = DoctorSerializer(doctor, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)





@api_view(['POST'])
@permission_classes([AllowAny])
def doctor_login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({'error': 'الإيميل وكلمة المرور مطلوبان'}, status=400)

    user = authenticate(request, email=email, password=password)

    if user is None:
        return Response({'error': 'بيانات الدخول غير صحيحة'}, status=401)

    if user.role != 'doctor':
        return Response({'error': 'هذا الحساب ليس لحساب طبيب'}, status=403)

    login(request, user)

    refresh = RefreshToken.for_user(user)

    try:
        doctor = user.doctor_profile
        doctor_data = DoctorSerializer(doctor).data
    except Doctor.DoesNotExist:
        doctor_data = None

    return Response({
        'message': 'تم تسجيل الدخول بنجاح كطبيب',
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'doctor': doctor_data,  # اختياري: لو بدك ترجع البروفايل
    }, status=200)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def doctor_profile(request):
    if request.user.role != 'doctor':
        return Response({"error": "لست طبيبًا"}, status=403)
    
    try:
        doctor = request.user.doctor_profile
        serializer = DoctorSerializer(doctor)
        return Response(serializer.data)
    except Doctor.DoesNotExist:
        return Response({"error": "بروفايل الطبيب غير موجود"}, status=404)
    
    



@api_view(['POST'])
@permission_classes([AllowAny])
def doctor_forget_password(request):
    email = request.data.get('email')
    if not email:
        return Response({'error': 'الإيميل مطلوب'}, status=400)

    try:
        user = CustomUser.objects.get(email=email, role='doctor')
    except CustomUser.DoesNotExist:
        return Response({
            'detail': 'إذا كان الإيميل مسجل ك طبيب تم إرسال كود إعادة تعيين',
            
            "email":email 
            }, status=200)

    # توليد كود 6 أرقام
    code = str(random.randint(100000, 999999))
    expiry = timezone.now() + timedelta(minutes=30)

    user.password_reset_code = code
    user.password_reset_code_expiry = expiry
    user.save()

    # محتوى الإيميل
    subject = 'كود إعادة تعيين كلمة المرور - حساب مريض'
    message = f'كود إعادة تعيين كلمة المرور الخاص بحسابك كمريض هو: {code}\n\nهذا الكود صالح لمدة 30 دقيقة فقط.'
    from_email = 'dentistai404@gmail.com'

    try:
        send_mail(subject, message, from_email, [email])

        return Response({
            
                          "code":code ,

            
            'detail': 'تم إرسال كود إعادة تعيين كلمة المرور إلى بريدك الإلكتروني',
              "email":"{email} تم ارسال الكود اللى الايميل ",
            
            
            }, status=200)
    except Exception as e:
        print(f"خطأ في إرسال الإيميل: {str(e)}")  
        return Response({'error': 'حدث خطأ أثناء إرسال الإيميل، حاول لاحقًا'}, status=500)





@api_view(['POST'])
@permission_classes([AllowAny])
def doctor_reset_password(request):
    code = request.data.get('code')
    password = request.data.get('password')
    confirm_password = request.data.get('confirm_password')

    if not code or not password or not confirm_password:
        return Response({'error': 'الكود وكلمة المرور وتأكيدها مطلوبة'}, status=400)

    if password != confirm_password:
        return Response({'error': 'كلمتا المرور غير متطابقتين'}, status=400)

    try:
        user = CustomUser.objects.get(
            password_reset_code=code,
            password_reset_code_expiry__gt=timezone.now(),
            role='doctor'
        )
    except CustomUser.DoesNotExist:
        return Response({'error': 'الكود غير صحيح أو منتهي الصلاحية أو ليس لحساب مريض'}, status=400)

    # تغيير كلمة المرور
    user.set_password(password)
    user.password_reset_code = None
    user.password_reset_code_expiry = None
    user.save()

    return Response({'detail': 'تم إعادة تعيين كلمة المرور بنجاح، يمكنك الآن تسجيل الدخول'}, status=200)





@api_view(['POST'])
@permission_classes([AllowAny])
def doctor_register(request):
    serializer = DoctorRegisterSerializer(data=request.data)
    if serializer.is_valid():
        # فصل الـ signal لو موجود
        from django.db.models.signals import post_save
        from .signals import create_doctor_profile
        post_save.disconnect(create_doctor_profile, sender=CustomUser)

        try:
            user = serializer.save()
            login(request, user)
            refresh = RefreshToken.for_user(user)

            return Response({
                'message': 'تم إنشاء حساب الطبيب بنجاح ',
                # 'refresh': str(refresh),
                # 'access': str(refresh.access_token),
            }, status=200)  # ← 200 كما طلبت

        finally:
            post_save.connect(create_doctor_profile, sender=CustomUser)

    return Response(serializer.errors, status=400)

























# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@








@api_view(['POST'])
@permission_classes([IsAuthenticated])
def search_patient(request):
    if request.user.role != 'doctor':
        return Response(
            {"detail":  "this endpoint is for doctors only."}, 

            status=status.HTTP_403_FORBIDDEN
        )

    serializer = PatientSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 

    random_code = request.data.get('random_code')
    national_id = request.data.get('national_id')


    try:
        patient = Patient.objects.select_related('user').get(
            user__random_code=random_code,
            user__national_id=national_id
        )
        
        
        patient_data = {
            "patient_id": patient.patient_id,
            "name": patient.user.name,
            "email": patient.user.email,
            "gender": patient.user.get_gender_display(),
            "blood_type": patient.blood_type,
            "birth_date": patient.user.birth_date,
        }
        
        return Response({
            "message": "Patient found successfully",

            "patient": patient_data
        }, status=status.HTTP_200_OK)

    except Patient.DoesNotExist:
        return Response(
            {"detail": "Patient not found. Please check the random code and national ID."}, 

            status=status.HTTP_404_NOT_FOUND
        )









 
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_patient_laboratory_reports(request, patient_id):
  
    if request.user.role != 'doctor':
        return Response(
            {"error": "Access Denied: Doctor permissions required."}, 
            status=status.HTTP_403_FORBIDDEN
        )
 
    try:
        doctor = request.user.doctor_profile
    except Doctor.DoesNotExist:
        return Response(
            {"error": "Profile Error: Your doctor profile is missing or inactive."}, 
            status=status.HTTP_404_NOT_FOUND
        )
 
    try:
        import uuid
        uuid.UUID(str(patient_id))
    except ValueError:
        return Response(
            {"error": "Invalid Format: The patient ID provided is not a valid UUID."}, 
            status=status.HTTP_400_BAD_REQUEST
        )
 
    try:
        patient = Patient.objects.get(patient_id=patient_id)
    except Patient.DoesNotExist:
        return Response(
            {"error": "Not Found: No patient record exists with this ID."}, 
            status=status.HTTP_404_NOT_FOUND
        )
 
    reports = LabReport.objects.filter(
        patient=patient, 
        category='laboratory'
    ).order_by('-report_date')
 
    if not reports.exists():
        return Response({
            "message": "Information: No laboratory reports found for this patient.",
            "results": []
        }, status=status.HTTP_200_OK)
 
    serializer = LabReportSerializer(reports, many=True)
    
    return Response({
        "message": f"Success: Retrieved {reports.count()} laboratory reports.",
        "patient_name": patient.user.name,
        "results": serializer.data
    }, status=status.HTTP_200_OK)











@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_full_report_details(request, report_id):
  
    if request.user.role != 'doctor':
        return Response(
            {"error": "Access Denied: Only doctors are authorized to view full report details."}, 
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        import uuid
        uuid.UUID(str(report_id))
    except ValueError:
        return Response(
            {"error": "Invalid Format: The provided report ID is not a valid UUID."}, 
            status=status.HTTP_400_BAD_REQUEST
        )
 
    try:
      
        report = LabReport.objects.select_related('patient__user').get(report_id=report_id)
    except LabReport.DoesNotExist:
        return Response(
            {"error": "Not Found: No laboratory report matches the provided ID."}, 
            status=status.HTTP_404_NOT_FOUND
        )
   

    serializer = LabReportSerializer(report)
 
    return Response({
        "message": "Success: Report details retrieved successfully.",
        "report_type": report.get_category_display(),
        "patient_name": report.patient.user.name,
        "details": serializer.data
    }, status=status.HTTP_200_OK)











@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_reports_by_body_part(request, patient_id, part_name):
  
    if request.user.role != 'doctor':
        return Response({"error": "Forbidden: Doctor access only"}, status=status.HTTP_403_FORBIDDEN)

    valid_parts = [choice[0] for choice in LabReport.BODY_PART_CHOICES]
    if part_name not in valid_parts:
        return Response({
            "error": f"Invalid body part: '{part_name}'",
            "valid_options": valid_parts
        }, status=status.HTTP_400_BAD_REQUEST)

   
    reports = LabReport.objects.filter(patient_id=patient_id, body_part=part_name)

    if not reports.exists():
        return Response({
            "message": f"No reports found for {part_name} for this patient",
            "reports": []
        }, status=status.HTTP_200_OK)

    
    serializer = LabReportSerializer(reports, many=True)

    return Response({
        "message": f"Found {reports.count()} reports for {part_name}",
        "reports": serializer.data
    }, status=status.HTTP_200_OK)






 


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_reports_by_report_type(request, patient_id, type_name):
  
    if request.user.role != 'doctor':
        return Response({"error": "Forbidden: Doctor access only"}, status=status.HTTP_403_FORBIDDEN)

    valid_parts = [choice[0] for choice in LabReport.REPORT_TYPE_CHOICES]
    if type_name not in valid_parts:
        return Response({
            "error": f"Invalid body part: '{type_name}'",
            "valid_options": valid_parts
        }, status=status.HTTP_400_BAD_REQUEST)

   
    reports = LabReport.objects.filter(patient_id=patient_id, report_type=type_name)

    if not reports.exists():
        return Response({
            "message": f"No reports found for {type_name} for this patient",
            "reports": []
        }, status=status.HTTP_200_OK)

    
    serializer = LabReportSerializer(reports, many=True)

    return Response({
        "message": f"Found {reports.count()} reports for {type_name}",
        "reports": serializer.data
    }, status=status.HTTP_200_OK)











@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_reports_by_category(request, patient_id, category_name):
  
    if request.user.role != 'doctor':
        return Response({"error": "Forbidden: Doctor access only"}, status=status.HTTP_403_FORBIDDEN)

    valid_parts = [choice[0] for choice in LabReport.CATEGORY_CHOICES]
    if category_name not in valid_parts:
        return Response({
            "error": f"Invalid body part: '{category_name}'",
            "valid_options": valid_parts
        }, status=status.HTTP_400_BAD_REQUEST)

   
    reports = LabReport.objects.filter(patient_id=patient_id, category=category_name)

    if not reports.exists():
        return Response({
            "message": f"No reports found for {category_name} for this patient",
            "reports": []
        }, status=status.HTTP_200_OK)

    
    serializer = LabReportSerializer(reports, many=True)

    return Response({
        "message": f"Found {reports.count()} reports for {category_name}",
        "reports": serializer.data
    }, status=status.HTTP_200_OK)











@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_reports_by_priority(request, patient_id, priority_name):
  
    if request.user.role != 'doctor':
        return Response({"error": "Forbidden: Doctor access only"}, status=status.HTTP_403_FORBIDDEN)

    valid_parts = [choice[0] for choice in LabReport.PRIORITY_CHOICES]
    if priority_name not in valid_parts:
        return Response({
            "error": f"Invalid body part: '{priority_name}'",
            "valid_options": valid_parts
        }, status=status.HTTP_400_BAD_REQUEST)

   
    reports = LabReport.objects.filter(patient_id=patient_id, priority=priority_name)

    if not reports.exists():
        return Response({
            "message": f"No reports found for {priority_name} for this patient",
            "reports": []
        }, status=status.HTTP_200_OK)

    
    serializer = LabReportSerializer(reports, many=True)

    return Response({
        "message": f"Found {reports.count()} reports for {priority_name}",
        "reports": serializer.data
    }, status=status.HTTP_200_OK)











@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_reports_by_status(request, patient_id, status_name):
  
    if request.user.role != 'doctor':
        return Response({"error": "Forbidden: Doctor access only"}, status=status.HTTP_403_FORBIDDEN)

    valid_parts = [choice[0] for choice in LabReport.STATUS_CHOICES]
    if status_name not in valid_parts:
        return Response({
            "error": f"Invalid body part: '{status_name}'",
            "valid_options": valid_parts
        }, status=status.HTTP_400_BAD_REQUEST)

   
    reports = LabReport.objects.filter(patient_id=patient_id, status=status_name)

    if not reports.exists():
        return Response({
            "message": f"No reports found for {status_name} for this patient",
            "reports": []
        }, status=status.HTTP_200_OK)

    
    serializer = LabReportSerializer(reports, many=True)

    return Response({
        "message": f"Found {reports.count()} reports for {status_name}",
        "reports": serializer.data
    }, status=status.HTTP_200_OK)











@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_medical_review(request):
 
    if request.user.role != 'doctor':
        return Response(
            {"error": "Access Denied: Only doctors are authorized to create medical reviews."}, 
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        doctor_profile = request.user.doctor_profile
    except Doctor.DoesNotExist:
        return Response(
            {"error": "Profile Error: Your doctor profile is missing or inactive."}, 
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = ReportReviewSerializer(data=request.data)
    
    if serializer.is_valid():
       
        patient_id = request.data.get('patient')
        report_id = request.data.get('report')

        patient = get_object_or_404(Patient, patient_id=patient_id)
        report = get_object_or_404(LabReport, report_id=report_id)
         
        if serializer.is_valid():
        
            serializer.save(
                doctor=request.user.doctor_profile, 
                patient=patient, 
                report=report
            )

        return Response({
            "message": "Success: Medical review has been created successfully.",
            "review_id": serializer.data.get('review_id'),
            "details": serializer.data
        }, status=status.HTTP_201_CREATED)

   
    return Response({
        "error": "Validation Failed: Please check the provided data.",
        "details": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


 
 







@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_medical_review_via_url(request, patient_id, report_id):
 
    if request.user.role != 'doctor':
        return Response(
            {"error": "Forbidden: Only doctors can create medical reviews."}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    patient = get_object_or_404(Patient, patient_id=patient_id)
    report = get_object_or_404(LabReport, report_id=report_id)

   
    if report.patient_id != patient.patient_id:
        return Response(
            {"error": "Integrity Error: This report does not belong to the specified patient."}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = ReportReviewSerializer(data=request.data)
    
    if serializer.is_valid():
       
        serializer.save(
            doctor=request.user.doctor_profile, 
            patient=patient, 
            report=report
        )

        return Response({
            "message": "Success: Medical review created successfully via URL parameters.",
            "results": serializer.data
        }, status=status.HTTP_201_CREATED)

 
    return Response({
        "error": "Validation Failed: Check your clinical findings data.",
        "details": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)








@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_patient_reviews_by_doctor(request, patient_id):

    try:
        doctor_profile = request.user.doctor_profile
    except AttributeError:
        return Response(
            {"error": "Unauthorized: Only doctors can access this information."}, 
            status=status.HTTP_403_FORBIDDEN
        )

    reviews = report_review.objects.filter(
        patient__patient_id=patient_id,
        doctor=doctor_profile
    ).select_related('report', 'patient__user')
    
    if not reviews.exists():
        return Response(
            {"message": "No reviews found by you for this patient."}, 
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = ReportReviewSerializer(reviews, many=True)
    return Response({
        "doctor_name": request.user.name,
        "patient_id": patient_id,
        "count": reviews.count(),
        "reviews": serializer.data
    }, status=status.HTTP_200_OK)








 


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_doctor_reviews(request):

    if request.user.role != 'doctor':
        return Response(
            {"error": "Access Denied: This endpoint is restricted to doctor accounts only."}, 
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        doctor_profile = request.user.doctor_profile
    except Exception:  
        return Response(
            {"error": "Profile Error: No doctor profile is associated with this user account."}, 
            status=status.HTTP_404_NOT_FOUND
        )

   
    reviews = report_review.objects.filter(doctor=doctor_profile)\
        .select_related('patient__user', 'report')\
        .order_by('-created_at')  
     
    serializer = ReportReviewSerializer(reviews, many=True)
    
    return Response({
        "status": "success",
        "doctor_info": {
            "name": request.user.name,
            "specialization": doctor_profile.specialization if hasattr(doctor_profile, 'specialization') else None
        },
        "total_reviews": reviews.count(),
        "reviews": serializer.data
    }, status=status.HTTP_200_OK)











@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_reviewed_patients_details(request):
  
    if request.user.role != 'doctor':
        return Response(
            {"error": "Access Denied: Only doctors can view reviewed patient lists."}, 
            status=status.HTTP_403_FORBIDDEN
        )

    if not hasattr(request.user, 'doctor_profile'):
        return Response(
            {"error": "Profile Error: Doctor profile not found for the current user."}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    doctor_profile = request.user.doctor_profile
   
    reviewed_patient_ids = report_review.objects.filter(doctor=doctor_profile)\
        .values_list('patient_id', flat=True)\
        .distinct()

    if not reviewed_patient_ids:
        return Response({
            "message": "No patients found. You haven't submitted any reviews yet.",
            "patients_list": []
        }, status=status.HTTP_200_OK)

    patients = Patient.objects.filter(patient_id__in=reviewed_patient_ids)\
        .select_related('user') 

    serializer = PatientSerializer(patients, many=True)
    
    return Response({
        "status": "success",
        "doctor": request.user.name,
        "reviewed_patients_count": patients.count(),
        "patients_list": serializer.data
    }, status=status.HTTP_200_OK)











@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_specific_patient_details(request, patient_id):

    if request.user.role != 'doctor':
        return Response(
            {"error": "Access Denied: This information is only accessible by doctors."}, 
            status=status.HTTP_403_FORBIDDEN
        )

    patient = get_object_or_404(Patient, patient_id=patient_id)

    serializer = PatientSerializer(patient)
    
    return Response({
        "status": "success",
        "patient_details": serializer.data
    }, status=status.HTTP_200_OK)











@api_view(['PUT'])  
@permission_classes([IsAuthenticated])
def update_medical_review(request, review_id):

    if request.user.role != 'doctor':
        return Response(
            {"error": "Access Denied: Only doctors can edit medical reviews."}, 
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        review_instance = report_review.objects.get(
            review_id=review_id, 
            doctor=request.user.doctor_profile
        )
    except report_review.DoesNotExist:
        return Response(
            {"error": "Review not found or you do not have permission to edit it."}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception:
        return Response(
            {"error": "Profile Error: Doctor profile not found."}, 
            status=status.HTTP_404_NOT_FOUND
        )

    review_instance.clinical_finding = request.data.get('clinical_finding', review_instance.clinical_finding)
    review_instance.diagnosis = request.data.get('diagnosis', review_instance.diagnosis)
    review_instance.comparison_with_previous = request.data.get('comparison_with_previous', review_instance.comparison_with_previous)
    review_instance.recommendations = request.data.get('recommendations', review_instance.recommendations)
    review_instance.prescribed_medication = request.data.get('prescribed_medication', review_instance.prescribed_medication)
    review_instance.require_urgent_action = request.data.get('require_urgent_action', review_instance.require_urgent_action)
    review_instance.result_interpretation = request.data.get('result_interpretation', review_instance.result_interpretation)
    review_instance.doctor_notes = request.data.get('doctor_notes', review_instance.doctor_notes)

    review_instance.save()

    return Response({
        "message": "Success: Medical review updated successfully.",
        "review_id": review_instance.review_id,
        "updated_data": {

            "diagnosis": review_instance.diagnosis,
            "clinical_finding": review_instance.clinical_finding,
            "updated_at": review_instance.updated_at ,

            "comparison_with_previous": review_instance.comparison_with_previous,
            "recommendations": review_instance.recommendations,

            "prescribed_medication": review_instance.prescribed_medication,
            "require_urgent_action": review_instance.require_urgent_action,

            "result_interpretation": review_instance.result_interpretation,
            "doctor_notes": review_instance.doctor_notes

        }
    }, status=status.HTTP_200_OK)



 
     
   
     
   




# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@






























# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@







@api_view(['POST'])
@permission_classes([IsAuthenticated])
def doctor_link_patient_by_credentials(request):
  
    if request.user.role != 'doctor':
        return Response({"error": "لست طبيبًا"}, status=403)

    national_id = request.data.get('national_id')
    random_code = request.data.get('random_code')

    if not national_id or not random_code:
        return Response(
            {"error": "الرقم الوطني والكود العشوائي مطلوبان"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # البحث عن المستخدم (المريض) بالرقم الوطني + الكود + الدور
        patient_user = CustomUser.objects.get(
            national_id=national_id,
            random_code=random_code,
            role='patient'
        )

        # جلب بروفايل المريض
        patient = patient_user.patient_profile

    except (CustomUser.DoesNotExist, Patient.DoesNotExist):
        return Response(
            {"error": "المريض غير موجود أو بيانات التحقق غير صحيحة"},
            status=status.HTTP_404_NOT_FOUND
        )

    # جلب بروفايل الطبيب الحالي
    try:
        doctor = request.user.doctor_profile
    except Doctor.DoesNotExist:
        return Response(
            {"error": "بروفايل الطبيب غير موجود"},
            status=status.HTTP_404_NOT_FOUND
        )

    # # التحقق إذا كان المريض مرتبط بالفعل
    # if patient in doctor.patients.all():
    #     return Response(
    #         {"message": "المريض مرتبط بالفعل بهذا الطبيب"},
    #         status=status.HTTP_200_OK
    #     )

    # # الربط الفعلي (ManyToMany)
    # doctor.patients.add(patient)

    return Response({
        # "message": f"تم ربط المريض {patient.user.name} بنجاح",
        "patient_name": patient.user.name,
        "patient_national_id": patient_user.national_id,
        "patient_random_code": patient_user.random_code
    }, status=status.HTTP_201_CREATED)
    
    



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def doctor_get_my_patients(request):
    """
    إرجاع قائمة جميع المرضى المرتبطين بالطبيب الحالي
    """
    if request.user.role != 'doctor':
        return Response({"error": "لست طبيبًا"}, status=status.HTTP_403_FORBIDDEN)

    try:
        doctor = request.user.doctor_profile
    except Doctor.DoesNotExist:
        return Response({"error": "بروفايل الطبيب غير موجود"}, status=status.HTTP_404_NOT_FOUND)

    # جلب جميع المرضى المرتبطين
    patients = doctor.patients.all()

    if not patients.exists():
        return Response({
            "message": "ليس لديك مرضى مرتبطين حاليًا",
            "patients": []
        }, status=status.HTTP_200_OK)

    # تسلسل البيانات (يمكنك تخصيص الحقول حسب الحاجة)
    # serializer = PatientSerializer(patients, many=True)
    serializer = PatientSearchSerializer(patients, many=True)

    return Response({
        "message": f"عدد المرضى المرتبطين: {patients.count()}",
        "patients": serializer.data
    }, status=status.HTTP_200_OK)    
    
    
     


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def doctor_unlink_patient(request):
  
    if request.user.role != 'doctor':
        return Response({"error": "لست طبيبًا"}, status=status.HTTP_403_FORBIDDEN)

    national_id = request.data.get('national_id')
    patient_id = request.data.get('patient_id')  # UUID للمريض

    if not national_id and not patient_id:
        return Response(
            {"error": "الرقم الوطني أو معرف المريض (patient_id) مطلوب"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # البحث عن المريض
        if national_id:
            patient_user = CustomUser.objects.get(
                national_id=national_id,
                role='patient'
            )
            patient = patient_user.patient_profile
        else:
            patient = Patient.objects.get(patient_id=patient_id)

    except (CustomUser.DoesNotExist, Patient.DoesNotExist):
        return Response(
            {"error": "المريض غير موجود أو البيانات غير صحيحة"},
            status=status.HTTP_404_NOT_FOUND
        )

    # جلب بروفايل الطبيب الحالي
    try:
        doctor = request.user.doctor_profile
    except Doctor.DoesNotExist:
        return Response(
            {"error": "بروفايل الطبيب غير موجود"},
            status=status.HTTP_404_NOT_FOUND
        )

    # التحقق إذا كان المريض مرتبط أصلاً
    if patient not in doctor.patients.all():
        return Response(
            {"message": "المريض غير مرتبط بهذا الطبيب أصلاً"},
            status=status.HTTP_200_OK
        )

    # حذف الارتباط
    doctor.patients.remove(patient)

    return Response({
        "message": f"تم حذف ارتباط المريض {patient.user.name} بنجاح",
        "patient_name": patient.user.name,
        # "patient_national_id": patient.user.national_id if patient.user.national_id else "غير متوفر"
    }, status=status.HTTP_200_OK)            







# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


