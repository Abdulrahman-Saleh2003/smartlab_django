# # accounts/urls.py
# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from .views import UserViewSet, UserActivityLogViewSet   # ← تأكد من import الـ views صح

# router = DefaultRouter()
# router.register(r'users', UserViewSet)
# router.register(r'activity-logs', UserActivityLogViewSet)

# urlpatterns = [                          # ← هذا الاسم بالضبط: urlpatterns (لا urls_patterns ولا urlspatterns)
#     path('', include(router.urls)),
# ]


from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('me/', views.current_user, name='current_user'),
    path('update/', views.update_user, name='update_user'),
    # path('change-password/', views.change_password, name='change_password'),
    
  
]