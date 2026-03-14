# receptionists/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login, authenticate
from .serializers import ReceptionistRegisterSerializer, ReceptionistSerializer
from accounts.serializers import UserSerializer
from .models import Receptionist


@api_view(['POST'])
@permission_classes([AllowAny])
def receptionist_register(request):
    serializer = ReceptionistRegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        login(request, user)
        refresh = RefreshToken.for_user(user)

        return Response({
            'message': 'تم إنشاء حساب موظف الاستقبال بنجاح ',
            # 'refresh': str(refresh),
            # 'access': str(refresh.access_token),
        }, status=200)

    return Response(serializer.errors, status=400)


@api_view(['POST'])
@permission_classes([AllowAny])
def receptionist_login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({'error': 'الإيميل وكلمة المرور مطلوبان'}, status=400)

    user = authenticate(request, email=email, password=password)

    if user is None:
        return Response({'error': 'بيانات الدخول غير صحيحة'}, status=401)

    if user.role != 'receptionist':
        return Response({'error': 'هذا الحساب ليس لحساب موظف استقبال'}, status=403)

    login(request, user)

    refresh = RefreshToken.for_user(user)

    try:
        receptionist = user.receptionist_profile
        receptionist_data = ReceptionistSerializer(receptionist).data
    except Receptionist.DoesNotExist:
        receptionist_data = None

    return Response({
        'message': 'تم تسجيل الدخول بنجاح كموظف استقبال',
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'receptionist': receptionist_data,
    }, status=200)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def receptionist_profile(request):
    if request.user.role != 'receptionist':
        return Response({"error": "لست موظف استقبال"}, status=403)

    try:
        receptionist = request.user.receptionist_profile
        serializer = ReceptionistSerializer(receptionist)
        return Response(serializer.data)
    except Receptionist.DoesNotExist:
        return Response({"error": "بروفايل موظف الاستقبال غير موجود"}, status=404)