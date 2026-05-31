from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Read serializer — safe for public exposure."""
    authorization_groups = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'full_name',
            'employee_id', 'is_active', 'created_at', 'authorization_groups',
        ]
        read_only_fields = ['id', 'created_at']

    def get_authorization_groups(self, obj):
        return [
            {
                'id': ug.authorization_group.id,
                'group_name': ug.authorization_group.group_name,
                'description': ug.authorization_group.description,
            }
            for ug in obj.authorization_groups
        ]


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new user."""
    password  = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, label='Confirm password')

    class Meta:
        model = User
        fields = ['username', 'email', 'full_name', 'employee_id', 'password', 'password2']

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password2'):
            raise serializers.ValidationError({'password2': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'full_name', 'employee_id', 'is_active']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password2 = serializers.CharField(write_only=True, label='Confirm new password')

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({'new_password2': 'Passwords do not match.'})
        return attrs


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs['username'], password=attrs['password'])
        if not user:
            raise serializers.ValidationError('Invalid credentials.')
        if not user.is_active:
            raise serializers.ValidationError('User account is disabled.')
        attrs['user'] = user
        return attrs


class TokenResponseSerializer(serializers.Serializer):
    """Response shape after successful login."""
    access  = serializers.CharField()
    refresh = serializers.CharField()
    user    = UserSerializer()
