from django.shortcuts import render
# patients/views.py

from django.contrib.auth import authenticate, login


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import PatientRegisterSerializer, PatientSerializer
from accounts.serializers import UserSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from datetime import timedelta
import random
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password

from .models import Patient

from accounts.models import CustomUser

@api_view(['POST'])
@permission_classes([AllowAny])
def patient_register(request):
    serializer = PatientRegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        login(request, user)  # تسجيل دخول تلقائي

        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'patient': PatientSerializer(user.patient_profile).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': 'تم إنشاء حساب المريض بنجاح'
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([AllowAny])
def patient_register(request):
    serializer = PatientRegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        
        # تسجيل دخول تلقائي (مهم عشان يولد session إذا كنت تستخدمها)
        login(request, user)
        
        # توليد توكنات JWT
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'تم إنشاء حساب المريض بنجاح وتسجيل الدخول تلقائيًا',
            # 'refresh': str(refresh),
            # 'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)  # ← غيرناه إلى 200 كما طلبت

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def patient_profile(request):
    if request.user.role != 'patient':
        return Response({"error": "لست مريضًا"}, status=403)
    
    try:
        patient = request.user.patient_profile
        serializer = PatientSerializer(patient)
        return Response(serializer.data)
    except Patient.DoesNotExist:
        return Response({"error": "بروفايل المريض غير موجود"}, status=404)


# 2. نسيان كلمة المرور (إرسال كود إلى الإيميل) - خاص بالمريض
@api_view(['POST'])
@permission_classes([AllowAny])
def patient_forget_password(request):
    email = request.data.get('email')
    if not email:
        return Response({'error': 'الإيميل مطلوب'}, status=400)

    try:
        user = CustomUser.objects.get(email=email, role='patient')
    except CustomUser.DoesNotExist:
        return Response({'detail': 'إذا كان الإيميل مسجل كمريض، تم إرسال كود إعادة تعيين'}, status=200)

    # توليد كود 6 أرقام
    code = str(random.randint(100000, 999999))
    expiry = timezone.now() + timedelta(minutes=30)

    user.password_reset_code = code
    user.password_reset_code_expiry = expiry
    user.save()

    # محتوى الإيميل
    subject = 'كود إعادة تعيين كلمة المرور - حساب مريض'
    message = f'كود إعادة تعيين كلمة المرور الخاص بحسابك كمريض هو: {code}\n\nهذا الكود صالح لمدة 30 دقيقة فقط.'
    from_email = 'noreply@yourdomain.com'  # ← غيّره لإيميلك الحقيقي

    try:
        send_mail(subject, message, from_email, [email])
        return Response({'detail': 'تم إرسال كود إعادة تعيين كلمة المرور إلى بريدك الإلكتروني'}, status=200)
    except Exception as e:
        return Response({'error': 'حدث خطأ أثناء إرسال الإيميل، حاول لاحقًا'}, status=500)


# 3. إعادة تعيين كلمة المرور باستخدام الكود - خاص بالمريض
@api_view(['POST'])
@permission_classes([AllowAny])
def patient_reset_password(request):
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
            role='patient'  # حماية: الكود لمريض فقط
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
def patient_login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({'error': 'الإيميل وكلمة المرور مطلوبان'}, status=status.HTTP_400_BAD_REQUEST)

    # التحقق من المستخدم
    user = authenticate(request, email=email, password=password)

    if user is None:
        return Response({'error': 'بيانات الدخول غير صحيحة'}, status=status.HTTP_401_UNAUTHORIZED)

    # التحقق إن الدور هو patient فقط
    if user.role != 'patient':
        return Response({'error': 'هذا الحساب ليس لحساب مريض'}, status=status.HTTP_403_FORBIDDEN)

    # تسجيل الدخول
    login(request, user)

    # توليد التوكن
    refresh = RefreshToken.for_user(user)

    # جلب بيانات المريض
    try:
        patient = user.patient_profile
        patient_data = PatientSerializer(patient).data
    except Patient.DoesNotExist:
        patient_data = None  # لو ما في بروفايل (نادر)

    return Response({
        # 'user': UserSerializer(user).data,
        'patient': patient_data,
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'message': 'تم تسجيل الدخول بنجاح كمريض'
    }, status=status.HTTP_200_OK)