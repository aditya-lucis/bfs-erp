from rest_framework import serializers
from .models import (
    Module, Function, AuthorizationGroup,
    GroupFunction, UserAuthorizationGroup,
)


# ─── Module ─────────────────────────────────────────────────────────────────

class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['id', 'code', 'name', 'description', 'order', 'is_active']


# ─── Function ────────────────────────────────────────────────────────────────

class FunctionSerializer(serializers.ModelSerializer):
    module_name = serializers.CharField(source='module.name', read_only=True)
    module_code = serializers.CharField(source='module.code', read_only=True)
    children    = serializers.SerializerMethodField()
    is_parent   = serializers.BooleanField(read_only=True)

    class Meta:
        model = Function
        fields = [
            'id', 'module', 'module_code', 'module_name',
            'code', 'name', 'description', 'url_path', 'order', 'is_active','is_parent', 'children',
        ]

    def get_children(self, obj):
        # Hanya return 1 level anak langsung, recursive dihandle frontend
        kids = obj.children.filter(is_active=True).order_by('order')
        return FunctionSerializer(kids, many=True).data


# ─── GroupFunction ───────────────────────────────────────────────────────────

class GroupFunctionSerializer(serializers.ModelSerializer):
    function_code = serializers.CharField(source='function.code', read_only=True)
    function_name = serializers.CharField(source='function.name', read_only=True)
    module_name   = serializers.CharField(source='function.module.name', read_only=True)

    class Meta:
        model = GroupFunction
        fields = [
            'id', 'function', 'function_code', 'function_name', 'module_name',
            'can_create', 'can_read', 'can_update', 'can_delete',
            'can_approve', 'can_print', 'can_export',
        ]


class GroupFunctionBulkItemSerializer(serializers.Serializer):
    """Single item for bulk assign."""
    function_id = serializers.IntegerField()
    can_create  = serializers.BooleanField(default=False)
    can_read    = serializers.BooleanField(default=True)
    can_update  = serializers.BooleanField(default=False)
    can_delete  = serializers.BooleanField(default=False)
    can_approve = serializers.BooleanField(default=False)
    can_print   = serializers.BooleanField(default=False)
    can_export  = serializers.BooleanField(default=False)


class GroupFunctionBulkSerializer(serializers.Serializer):
    """
    Used for the 'Apply' button on screen 3 of the screenshot.
    Replaces all GroupFunction rows for a group in one shot.
    """
    functions = GroupFunctionBulkItemSerializer(many=True)


# ─── AuthorizationGroup ──────────────────────────────────────────────────────

class AuthorizationGroupListSerializer(serializers.ModelSerializer):
    """Lightweight — for the list view (screenshot 1)."""
    class Meta:
        model = AuthorizationGroup
        fields = ['id', 'group_name', 'description', 'status', 'created_at']


class AuthorizationGroupDetailSerializer(serializers.ModelSerializer):
    """Full detail including assigned functions."""
    group_functions = GroupFunctionSerializer(many=True, read_only=True)

    class Meta:
        model = AuthorizationGroup
        fields = [
            'id', 'group_name', 'description', 'status',
            'created_at', 'updated_at', 'group_functions',
        ]


class AuthorizationGroupWriteSerializer(serializers.ModelSerializer):
    """Create / Update (screenshot 2 form fields)."""
    class Meta:
        model = AuthorizationGroup
        fields = ['group_name', 'description', 'status']

    def validate_group_name(self, value):
        return value.upper().strip()


# ─── UserAuthorizationGroup ──────────────────────────────────────────────────

class UserAuthGroupSerializer(serializers.ModelSerializer):
    username    = serializers.CharField(source='user.username', read_only=True)
    full_name   = serializers.CharField(source='user.full_name', read_only=True)
    group_name  = serializers.CharField(source='authorization_group.group_name', read_only=True)

    class Meta:
        model = UserAuthorizationGroup
        fields = ['id', 'user', 'username', 'full_name',
                  'authorization_group', 'group_name', 'assigned_at']
        read_only_fields = ['assigned_at']


class AssignUsersToGroupSerializer(serializers.Serializer):
    """Bulk assign users to a group."""
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
    )


# ─── Permission Check (used by frontend/middleware) ─────────────────────────

class PermissionCheckSerializer(serializers.Serializer):
    """
    Request body for checking if the current user
    can perform an action on a function.
    """
    function_code = serializers.CharField()
    action        = serializers.ChoiceField(choices=[
        'can_create', 'can_read', 'can_update', 'can_delete',
        'can_approve', 'can_print', 'can_export',
    ])
