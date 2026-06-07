from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import User
from .serializers import (
    MeUpdateSerializer, UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    ChangePasswordSerializer, LoginSerializer,
    AdminResetPasswordSerializer, CreateUserForEmployeeSerializer
)


class LoginView(APIView):
    """
    POST /api/v1/auth/login/
    Returns JWT access + refresh tokens along with user profile.
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=LoginSerializer, responses={200: dict})
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        return Response({
            'access':  str(refresh.access_token),
            'refresh': str(refresh),
            'user':    UserSerializer(user).data,
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    POST /api/v1/auth/logout/
    Blacklists the refresh token so it can't be reused.
    """
    @extend_schema(request={'refresh': str}, responses={204: None})
    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'detail': 'refresh token is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response(
                {'detail': 'Invalid or already blacklisted token.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(generics.RetrieveUpdateAPIView):
    """
    GET  /api/v1/auth/me/  → current user profile
    PATCH /api/v1/auth/me/ → update profile fields
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser, JSONParser]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return UserUpdateSerializer
        return UserSerializer


class ChangePasswordView(APIView):
    """POST /api/v1/auth/change-password/"""

    @extend_schema(request=ChangePasswordSerializer, responses={200: dict})
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {'old_password': 'Wrong password.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'detail': 'Password updated successfully.'})


@extend_schema_view(
    list=extend_schema(description='List all users (admin only)'),
    create=extend_schema(description='Create new user (admin only)'),
)
class UserListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/auth/users/  → list users
    POST /api/v1/auth/users/  → create user
    """
    queryset = User.objects.all().order_by('username')
    permission_classes = [permissions.IsAdminUser]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer


class UserRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    """
    GET   /api/v1/auth/users/<id>/  → user detail
    PATCH /api/v1/auth/users/<id>/  → update user
    """
    queryset = User.objects.all()
    permission_classes = [permissions.IsAdminUser]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return UserUpdateSerializer
        return UserSerializer

class WhoAmIView(APIView):
    """
    GET /api/v1/auth/whoami/
    
    Return info lengkap user + flag superuser + employee profile.
    Dipakai Vue buat setup initial state setelah login.
    
    Response:
    {
        "id": 1,
        "username": "admin",
        "full_name": "Admin",
        "is_superuser": true,
        "is_staff": true,
        "employee": {
            "employee_id": "ADM0001",
            "position": "Accounting Manager",
            "department": "Akuntansi"
        },
        "authorization_groups": [...]
    }
    """
    def get(self, request):
        user = request.user
        
        # Employee profile kalau ada
        employee_data = None
        if hasattr(user, 'employee_profile'):
            emp = user.employee_profile
            employee_data = {
                'id':          emp.id,
                'employee_id': emp.employee_id,
                'position':    emp.position.name,
                'department':  emp.position.department.name,
                'status':      emp.status,
            }

        return Response({
            'id':           user.id,
            'username':     user.username,
            'full_name':    user.full_name,
            'email':        user.email,
            'is_superuser': user.is_superuser,
            'is_staff':     user.is_staff,
            'employee':     employee_data,
            'authorization_groups': [
                {
                    'id':          ug.authorization_group.id,
                    'group_name':  ug.authorization_group.group_name,
                    'description': ug.authorization_group.description,
                }
                for ug in user.authorization_groups
            ],
        })


class AdminResetPasswordView(APIView):
    """
    POST /api/v1/auth/users/<id>/reset-password/
    Superuser reset password user lain. Tidak perlu old_password.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        # Hanya superuser yang boleh reset password orang lain
        if not request.user.is_superuser:
            return Response(
                {'detail': 'Hanya superuser yang dapat mereset password.'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            target_user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'detail': 'User tidak ditemukan.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = AdminResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        target_user.set_password(serializer.validated_data['new_password'])
        target_user.save()
        return Response({'detail': f'Password untuk "{target_user.username}" berhasil direset.'})


class CreateUserForEmployeeView(APIView):
    """
    POST /api/v1/org/employees/<pk>/create-user/
    Buat user baru untuk employee seed yang belum punya user.
    Hanya superuser yang boleh.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        if not request.user.is_superuser:
            return Response(
                {'detail': 'Hanya superuser yang dapat membuat user untuk employee.'},
                status=status.HTTP_403_FORBIDDEN
            )

        from apps.organization.models import Employee

        try:
            employee = Employee.objects.select_related('user').get(pk=pk)
        except Employee.DoesNotExist:
            return Response({'detail': 'Employee tidak ditemukan.'}, status=status.HTTP_404_NOT_FOUND)

        if employee.user is not None:
            return Response(
                {'detail': 'Employee ini sudah memiliki user account.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = CreateUserForEmployeeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_user = User.objects.create_user(
            username  = serializer.validated_data['username'],
            password  = serializer.validated_data['password'],
            email     = employee.email,
            full_name = employee.full_name,
        )

        employee.user = new_user
        employee.save(update_fields=['user'])

        return Response({
            'detail': f'User "{new_user.username}" berhasil dibuat untuk employee {employee.employee_id}.',
            'user_id': new_user.id,
            'username': new_user.username,
        }, status=status.HTTP_201_CREATED)
    
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

class MeView(generics.RetrieveUpdateAPIView):
    """
    GET  /api/v1/auth/me/  → current user profile
    PATCH /api/v1/auth/me/ → update profile fields
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser, JSONParser]   # ← tambah

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return MeUpdateSerializer
        return MeUpdateSerializer   # pakai yang sama untuk GET juga