
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model, authenticate, login, update_session_auth_hash
from .serializers import RegisterSerializer, UserSerializer
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
import random
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.hashers import make_password
User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        login(request, user)  # ← أضف هذا السطر
       
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=201)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)









@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'message': 'تم إنشاء الحساب بنجاح',
            'email': user.email,
            'detail': 'يرجى تسجيل الدخول الآن باستخدام الإيميل وكلمة المرور للحصول على التوكن'
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)









@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({'detail': 'الإيميل وكلمة المرور مطلوبان'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(request, email=email, password=password)

    if user is None:
        return Response({'detail': 'بيانات الدخول غير صحيحة'}, status=status.HTTP_401_UNAUTHORIZED)

    login(request, user)

    refresh = RefreshToken.for_user(user)

    return Response({
        'user': UserSerializer(user).data,
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'message': 'تم تسجيل الدخول بنجاح'
    }, status=status.HTTP_200_OK)









@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)









@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_user(request):
    user = request.user
    serializer = UserSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)









@api_view(['POST'])
@permission_classes([AllowAny])
def forget_password(request):
    email = request.data.get('email')
    if not email:
        return Response({'error': 'الإيميل مطلوب'}, status=400)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # عشان ما نعطي معلومة إن الإيميل موجود أو لا (أمان)
        return Response({'detail': 'إذا كان الإيميل موجودًا، تم إرسال كود إعادة تعيين كلمة المرور'}, status=200)

    # توليد كود 6 أرقام
    code = str(random.randint(100000, 999999))
    expiry = timezone.now() + timedelta(minutes=30)

    user.password_reset_code = code
    user.password_reset_code_expiry = expiry
    user.save()

    # محتوى الإيميل
    subject = 'كود إعادة تعيين كلمة المرور'
    message = f'كود إعادة تعيين كلمة المرور الخاص بك هو: {code}\n\nهذا الكود صالح لمدة 30 دقيقة فقط.'
    from_email = 'noreply@yourdomain.com'  # غيّره لإيميلك الحقيقي

    try:
        send_mail(subject, message, from_email, [email])
        return Response({'detail': 'تم إرسال كود إعادة تعيين كلمة المرور إلى بريدك الإلكتروني'}, status=200)
    except Exception as e:
        # في الـ production، ما ترجع الخطأ الحقيقي
        return Response({'error': 'حدث خطأ أثناء إرسال الإيميل، حاول لاحقًا'}, status=500)
    







    
@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    code = request.data.get('code')
    password = request.data.get('password')
    confirm_password = request.data.get('confirm_password')

    if not code or not password or not confirm_password:
        return Response({'error': 'الكود وكلمة المرور وتأكيدها مطلوبة'}, status=400)

    if password != confirm_password:
        return Response({'error': 'كلمتا المرور غير متطابقتين'}, status=400)

    try:
        user = User.objects.get(
            password_reset_code=code,
            password_reset_code_expiry__gt=timezone.now()
        )
    except User.DoesNotExist:
        return Response({'error': 'الكود غير صحيح أو منتهي الصلاحية'}, status=400)

    # تغيير كلمة المرور
    user.set_password(password)
    user.password_reset_code = None
    user.password_reset_code_expiry = None
    user.save()

    return Response({'detail': 'تم إعادة تعيين كلمة المرور بنجاح، يمكنك الآن تسجيل الدخول'}, status=200)