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