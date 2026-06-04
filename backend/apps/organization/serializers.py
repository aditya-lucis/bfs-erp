from django.contrib.auth import get_user_model
from rest_framework import serializers
from apps.rbac.models import AuthorizationGroup, UserAuthorizationGroup
from .models import Company, Department, Position, Employee

User = get_user_model()

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Company
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class DepartmentSerializer(serializers.ModelSerializer):
    level       = serializers.SerializerMethodField()
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    children    = serializers.SerializerMethodField()

    class Meta:
        model  = Department
        fields = ['id', 'code', 'name', 'parent', 'parent_name',
                  'order', 'level', 'is_active', 'children']
        
    def get_level(self, obj):
        return obj.level
        
    def get_children(self, obj):
        kids = obj.children.filter(is_active=True).order_by('order')
        return DepartmentSerializer(kids, many=True).data

class PositionSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    employee_count  = serializers.SerializerMethodField()

    class Meta:
        model  = Position
        fields = ['id', 'code', 'name', 'description',
                  'department', 'department_name', 'is_active', 'employee_count']

    def get_employee_count(self, obj):
        return obj.employees.filter(status='active').count()
    
class EmployeeCreateSerializer(serializers.Serializer):
    """
    Serializer khusus untuk CREATE employee sekaligus user.
    Semua dalam 1 request.
    """
    # ── Employee fields ────────────────────────────────────────────────────
    position        = serializers.PrimaryKeyRelatedField(
                          queryset=Position.objects.filter(is_active=True)
                      )
    full_name       = serializers.CharField(max_length=150)
    email           = serializers.EmailField()
    phone           = serializers.CharField(max_length=30, required=False, allow_blank=True)
    join_date       = serializers.DateField(required=False, allow_null=True)
    status          = serializers.ChoiceField(
                          choices=['active', 'inactive', 'resigned', 'terminated'],
                          default='active'
                      )

    # ── User fields ────────────────────────────────────────────────────────
    username        = serializers.CharField(max_length=50)
    password        = serializers.CharField(write_only=True, min_length=8)
    authorization_group_ids = serializers.ListField(
                          child=serializers.IntegerField(),
                          required=False,
                          default=list,
                          help_text='List of AuthorizationGroup IDs'
                      )

    # ── Signature ──────────────────────────────────────────────────────────
    signature_draw  = serializers.CharField(required=False, allow_blank=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Username sudah digunakan.')
        return value.lower().strip()

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email sudah digunakan.')
        return value.lower().strip()

    def validate_authorization_group_ids(self, value):
        if not value:
            return value
        existing = AuthorizationGroup.objects.filter(
            pk__in=value, status=True
        ).count()
        if existing != len(value):
            raise serializers.ValidationError(
                'Satu atau lebih Authorization Group tidak valid.'
            )
        return value


class EmployeeListSerializer(serializers.ModelSerializer):
    """Untuk list view."""
    position_name   = serializers.CharField(source='position.name',            read_only=True)
    department_name = serializers.CharField(source='position.department.name', read_only=True)
    username        = serializers.CharField(source='user.username',            read_only=True, default=None)
    has_signature   = serializers.BooleanField(read_only=True)
    groups          = serializers.SerializerMethodField()

    class Meta:
        model  = Employee
        fields = [
            'id', 'employee_id', 'full_name', 'email', 'phone',
            'position', 'position_name', 'department_name',
            'status', 'join_date', 'has_signature',
            'user', 'username', 'groups', 'created_at',
        ]

    def get_groups(self, obj):
        if not obj.user:
            return []
        return list(
            obj.user.user_auth_groups
               .filter(authorization_group__status=True)
               .values('authorization_group__id',
                       'authorization_group__group_name',
                       'authorization_group__description')
        )


class EmployeeDetailSerializer(EmployeeListSerializer):
    """Untuk detail view — tambah signature info."""
    signature_draw  = serializers.CharField(read_only=True)
    signature_image = serializers.ImageField(read_only=True)

    class Meta(EmployeeListSerializer.Meta):
        fields = EmployeeListSerializer.Meta.fields + [
            'signature_draw', 'signature_image',
        ]


class EmployeeUpdateSerializer(serializers.ModelSerializer):
    """Update data employee (tidak termasuk user/password)."""
    authorization_group_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        write_only=True,
    )
    signature_draw = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model  = Employee
        fields = [
            'position', 'full_name', 'email', 'phone',
            'join_date', 'status', 'signature_draw',
            'authorization_group_ids',
        ]