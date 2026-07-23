# lab_technicians/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login, authenticate
from .serializers import LabTechnicianRegisterSerializer, LabTechnicianSerializer   
from accounts.serializers import UserSerializer
from .models import LabTechnician

from patients.serializers import PatientSearchSerializer, PatientSerializer


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from patients.models import Patient
from lab_reports.models import LabReport
from .models import LabTechnician


from lab_reports.serializers import LabReportSerializer






@api_view(['POST'])
@permission_classes([AllowAny])
def lab_technician_register(request):
    serializer = LabTechnicianRegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        login(request, user)
        refresh = RefreshToken.for_user(user)

        return Response({
            'message': 'تم إنشاء حساب المخبري بنجاح وتسجيل الدخول تلقائيًا',
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=200)

    return Response(serializer.errors, status=400)










@api_view(['POST'])
@permission_classes([AllowAny])
def lab_technician_login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({'error': 'الإيميل وكلمة المرور مطلوبان'}, status=400)

    user = authenticate(request, email=email, password=password)

    if user is None:
        return Response({'error': 'بيانات الدخول غير صحيحة'}, status=401)

    if user.role != 'lab_technician':
        return Response({'error': 'هذا الحساب ليس لحساب مخبري'}, status=403)

    login(request, user)

    refresh = RefreshToken.for_user(user)

    try:
        technician = user.lab_technician_profile
        technician_data = LabTechnicianSerializer(technician).data
    except LabTechnician.DoesNotExist:
        technician_data = None

    return Response({
        'message': 'تم تسجيل الدخول بنجاح كمخبري',
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'technician': technician_data,
    }, status=200)








@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lab_technician_profile(request):
    if request.user.role != 'lab_technician':
        return Response({"error": "لست مخبريًا"}, status=403)

    try:
        technician = request.user.lab_technician_profile
        serializer = LabTechnicianSerializer(technician)
        return Response(serializer.data)
    except LabTechnician.DoesNotExist:
        return Response({"error": "بروفايل المخبري غير موجود"}, status=404)
    




def is_lab_technician(user):
    return user.role == 'lab_technician'



@api_view(['GET'])
@permission_classes([IsAuthenticated])

def search_patient(request):
    if not is_lab_technician(request.user):
        return Response({"error": "Unauthorized"}, status=403)

    code = request.query_params.get('code')

    if not code:
        return Response({"error": "Code must be sent"}, status=400)

    try:
        patient = Patient.objects.select_related('user').get(user__random_code=code)
    except Patient.DoesNotExist:
        return Response({"error": "Patient does not exist"}, status=404)

    serializer = PatientSearchSerializer(patient)
    return Response(serializer.data)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def patient_overview(request, patient_id):
    if not is_lab_technician(request.user):
        return Response({"error": "Unauthorized"}, status=403)

    try:
        patient = Patient.objects.select_related('user').get(patient_id=patient_id)
    except Patient.DoesNotExist:
        return Response({"error": "Patient does not exist"}, status=404)

    serializer = PatientSerializer(patient)
    return Response(serializer.data)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def patient_record(request, patient_id):
    if not is_lab_technician(request.user):
        return Response({"error": "Unauthorized"}, status=403)

    try:
        patient = Patient.objects.get(patient_id=patient_id)
    except Patient.DoesNotExist:
        return Response({"error": "Patient does not exist"}, status=404)

    reports = LabReport.objects.filter(patient=patient).order_by('-report_date')
    serializer = LabReportSerializer(reports, many=True)

    return Response({
        "patient_id": str(patient.patient_id),
        "reports": serializer.data
    })




@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_analysis(request, patient_id):
    if not is_lab_technician(request.user):
        return Response({"error": "Unauthorized"}, status=403)

    try:
        patient = Patient.objects.get(patient_id=patient_id)
    except Patient.DoesNotExist:
        return Response({"error": "Patient does not exist"}, status=404)

    serializer = LabReportSerializer(data=request.data)

    if serializer.is_valid():
        report = serializer.save(
            patient=patient,
            created_by=request.user
        )

        return Response({
            "message": "Analysis uploaded successfully",
            "report_id": report.report_id
        }, status=201)

    return Response(serializer.errors, status=400)





@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_uploaded_analyses(request):
    if not is_lab_technician(request.user):
        return Response({"error": "Unauthorized"}, status=403)

    reports = LabReport.objects.filter(created_by=request.user).order_by('-created_at')

    serializer = LabReportSerializer(reports, many=True)

    return Response(serializer.data)














