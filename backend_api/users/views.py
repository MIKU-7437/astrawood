from .models import User
from .serializers import RegisterSerializer, UserSerializer, EmailVerificationSerializer, ChangePasswordSerializer
from .utils import Util
from rest_framework import status, generics, viewsets, permissions, mixins
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer

from rest_framework.response import Response
from rest_framework.decorators import action
from django.http import Http404

#Imports for RegisterView and VerifyEmailView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
import jwt

#Testing imports
from rest_framework.views import APIView


#Метод который будет 
class RegisterView(viewsets.GenericViewSet):
    serializer_class = RegisterSerializer

    def post(self, request):
        """
        RegisterView (Регистрация нового пользователя):

        Описание: Регистрирует нового пользователя в системе и отправляет электронное письмо для подтверждения адреса электронной почты.
        без активации через почту не получится зайти в аккаунт
        Параметры:
        first_name (обязательный): Имя пользователя.
        last_name (обязательный): Фамилия пользователя.
        email (обязательный): Адрес электронной почты пользователя. (также есть проверка на уникальность)
        password (обязательный): Пароль пользователя.
        password_conf (обязательный): Подтверждение пароля пользователя.
        city (обязательный)
        region (обязательный)
        address (обязательный)
        phone (обязательный) (также есть проверка на уникальность)
        Ответ:
        user_data: Данные пользователя.
        """
        # Получение пароля и его подтверждения из запроса
        password = request.data.get('password')
        password_conf = request.data.get('password_conf')

        # Проверка соответствия паролей
        if password != password_conf:
            return Response({'error': 'Passwords didn\'t match'}, status=status.HTTP_400_BAD_REQUEST)

        # Создание экземпляра сериализатора
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user = serializer.data

        # Получение токенов доступа
        user_email = User.objects.get(email=user['email'])
        token = RefreshToken.for_user(user_email).access_token

        # Формирование URL для верификации по электронной почте
        current_site = get_current_site(request).domain
        relative_link = reverse('email-verify')
        verify_url = 'http://' + current_site + relative_link + "?token=" + str(token)

        # Формирование текста электронного письма
        email_body = f"Hi {user['email']}, verify your email.\n{verify_url}"

        # Подготовка данных и отправка электронного письма
        data = {
            'email_body': email_body,
            'to_email': user['email'],
            'email_subject': 'Verify your email'
        }
        Util.send_email(data=data)

        # Возврат ответа с данными пользователя и токеном доступа
        return Response({'user_data': user, 'access_token': str(token)}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], name='check_status')
    def check_status(self, request):
        """
        Описание: Проверяет статус подтверждения адреса электронной почты для указанного пользователя.
        Параметры:
        email (обязательный): Адрес электронной почты пользователя.
        Ответ:
        status: Статус подтверждения (verified - подтверждено, error - не подтверждено).
        """
        email = request.data.get('email')
        user = User.objects.get(email=email)
        if user:
            if user.is_active:
                return Response({'status':"verified"})
            else:
                return Response({'error':f"User with email {email} is not activated yet"})
        else:
            return Response({'error':f"User with email {email} was not found"})

    # Функция для повторной отправки токена, если истечет время
    @action(detail=False, methods=['post'], name='get_another_mail')
    def getAnotherMail(self, request):
        """
        Метод: POST
        Описание: Повторно отправляет токен подтверждения адреса электронной почты для указанного пользователя.
        Параметры:
        email (обязательный): Адрес электронной почты пользователя.
        Ответ:
        email: Адрес электронной почты пользователя.
        """
        try:
            # Проверка корректности и наличия email в базе данных
            email = request.data.get('email')
            if not email:
                raise ValidationError({'email': 'Email is required'})

            user = User.objects.get(email=email)

            # Создание токена доступа
            token = RefreshToken.for_user(user).access_token

            # Формирование URL для верификации по электронной почте
            current_site = get_current_site(request).domain
            relative_link = reverse('email-verify')
            verify_url = 'http://' + current_site + relative_link + "?token=" + str(token)

            # Формирование текста электронного письма
            email_body = f"Hi {user.username}, verify your email.\n{verify_url}"

            # Подготовка данных и отправка электронного письма
            data = {
                'email_body': email_body,
                'to_email': user.email,
                'email_subject': 'Verify your email'
            }
            Util.send_email(data=data)

            # Возврат ответа с адресом электронной почты пользователя и токеном доступа
            return Response({'email': user.email, 'access_token': str(token)}, status=status.HTTP_201_CREATED)

        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response(e.message_dict, status=status.HTTP_400_BAD_REQUEST)
        

class VerifyEmailView(generics.GenericAPIView):
    
    serializer_class = EmailVerificationSerializer

    def get(self, request):
        """
        Описание: Подтверждает адрес электронной почты пользователя по токену, отправленному на почту.
        Параметры:
        token (в параметрах запроса): Токен подтверждения.
        Ответ:
        email: Статус успешного подтверждения.
        """
        # Получение токена из параметра запроса
        token = request.GET.get('token')

        try:
            # Декодирование токена 
            token_data = jwt.decode(token, options={"verify_signature": False}) # ("verify_signature": False) не обращать внимание

            # Получение пользователя по ID из токена и поиск пользователя с таким id
            user = User.objects.get(id=token_data['user_id'])

            # Проверка, что пользователь не подтвержден, и если так, подтверждение
            if not user.is_active:
                user.is_active = True
                user.save()

            # Возврат успешного ответа
            return Response({'email': 'Successfully activated'}, status=status.HTTP_200_OK)

        except jwt.ExpiredSignatureError as identifier:
            # Обработка исключения истекшего срока действия токена
            return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)

        except jwt.exceptions.DecodeError as identifier:
            # Обработка исключения невозможности декодирования токена
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Описание: логин пользователя по его данным входа
    Параметры:
    почта (обязательное)
    пароль (обязательное)
    Ответ:
    пара токенов access и refresh
    данные пользователя
    """
    serializer_class = CustomTokenObtainPairSerializer
#Testing logic
class UserDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get_object(self, queryset=None):
        obj = self.request.user
        return obj
    # Функция которая будет срабатывать только на GET-запросы(возващает только один аккаунт)
    def get(self, request):
        """"
        Логика для работы с аккаунтом (нужно предоставить access токен):

        Описание: Получает данные аутентифицированного пользователя.
        для работы с эндпоинтом, нужно предоставить access токен
        Ответ: Данные пользователя
        """
        # Получение объекта пользователя
        user = self.get_object()
        # Сериализация и возврат данных пользователя
        serializer = UserSerializer(user)
        return Response(serializer.data)
    

    # Функция которая будет срабатывать только на PUT-запросы(обновить данные и пользователе)
    def put(self, request):
        """
        Описание: Обновляет данные аутентифицированного пользователя.
        Параметры которые можно редактировать:
        first_name (необязательный)
        last_name (необязательный)
        photo (необязательный)
        city (необязательный)
        region (необязательный)
        address (необязательный)
        phone (необязательный)
        не редактируются:
        username - полное имя пользователя, состоит из first_name и last_name
        email
        password
        Ответ: Обновленные данные пользователя.
        """
        # Получение объекта пользователя по email
        user = self.get_object()

        # Проверка, что пользователь обновляет самого себя
        if user != request.user:
            return Response({'error': 'You do not have permission to update this user.'}, status=status.HTTP_403_FORBIDDEN)

        # Сериализация и обновление данных пользователя
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        # В случае ошибок валидации, возврат ошибок
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    #TESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTEST
    def delete(self, request,format=None):
        """
        (тестовая функция)
        Описание: просто удаляет аутентифицированного пользователя.
        Ответ: Сообщение об успешном удалении.
        """
        # Получение объекта пользователя
        user = self.get_object()

        # Проверка, что пользователь удаляет самого себя
        if user != request.user:
            return Response({'error': 'You do not have permission to delete this user.'}, status=status.HTTP_403_FORBIDDEN)

        # Удаление пользователя
        email = user.email
        user.delete()
        return Response({'message': f'User with email {email} deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


#TESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTEST
class AllUsersView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        """
        Тестовая функция вообще бесполезная
        """
        # Получение всех пользователей
        users = User.objects.all()

        # Сериализация и возврат данных всех пользователей
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class ChangePasswordView(generics.UpdateAPIView):
    """
    Описание: Изменяет пароль пользователя.
    (Пока без подтверждения через почту скоро добавлю)
    Параметры:
    old_password (обязательный): Текущий пароль пользователя.
    new_password (обязательный): Новый пароль пользователя.
    Ответ: Сообщение об успешном обновлении пароля.
    """
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes =[JWTAuthentication]

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
