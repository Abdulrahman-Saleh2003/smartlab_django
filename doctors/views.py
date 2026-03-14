import random

from django.shortcuts import render

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model, authenticate, login, update_session_auth_hash
from .serializers import  UserSerializer
from .models import Doctor
from accounts.models import CustomUser

from .serializers import DoctorSerializer,DoctorRegisterSerializer

from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta

from django.contrib.auth.hashers import make_password
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