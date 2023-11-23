from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    # Регистрация нового пользователя
    path('register/', views.RegisterView.as_view({'post': 'post'}), name='register'),

    # Подтверждение электронной почты
    path('email-verify/', views.VerifyEmailView.as_view(), name='email-verify'),

    # Повторная отправка подтверждения на почту
    path('another-mail/', views.RegisterView.as_view({'post': 'getAnotherMail'}), name='get-another-mail'),
    path('check_status/', views.RegisterView.as_view({'post': 'check_status'}), name='check_status'),

    # Вход с использованием токенов
    path('login/', views.CustomTokenObtainPairView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('list/', views.AllUsersView.as_view(), name='account-list'),
    # Получение, обновление и удаление данных аккаунта пользователя по email
    path('', views.UserDetailView.as_view(), name='account-detail'),

    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
]