from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import (
    Module, Function, AuthorizationGroup,
    GroupFunction, UserAuthorizationGroup,
)
from .serializers import (
    ModuleSerializer, FunctionSerializer,
    AuthorizationGroupListSerializer, AuthorizationGroupDetailSerializer,
    AuthorizationGroupWriteSerializer,
    GroupFunctionSerializer, GroupFunctionBulkSerializer,
    UserAuthGroupSerializer, AssignUsersToGroupSerializer,
    PermissionCheckSerializer,
)
from .permissions import IsAdminGroupMember, get_user_permissions, invalidate_permission_cache


# ─── Module ─────────────────────────────────────────────────────────────────

class ModuleListCreateView(generics.ListCreateAPIView):
    """GET /api/v1/rbac/modules/  |  POST /api/v1/rbac/modules/"""
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminGroupMember]
    filterset_fields = ['is_active']
    search_fields = ['code', 'name']


class ModuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PATCH/DELETE /api/v1/rbac/modules/<id>/"""
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminGroupMember]


# ─── Function ────────────────────────────────────────────────────────────────

class FunctionListCreateView(generics.ListCreateAPIView):
    """GET /api/v1/rbac/functions/  |  POST /api/v1/rbac/functions/"""
    queryset = Function.objects.select_related('module').all()
    serializer_class = FunctionSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminGroupMember]
    filterset_fields = ['module', 'is_active']
    search_fields = ['code', 'name']


class FunctionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PATCH/DELETE /api/v1/rbac/functions/<id>/"""
    queryset = Function.objects.select_related('module').all()
    serializer_class = FunctionSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminGroupMember]


# ─── Authorization Group ─────────────────────────────────────────────────────

class AuthGroupListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/rbac/groups/  → list (screenshot 1)
    POST /api/v1/rbac/groups/  → create new group (screenshot 2 form)
    """
    queryset = AuthorizationGroup.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAdminGroupMember]
    filterset_fields = ['status']
    search_fields = ['group_name', 'description']
    ordering_fields = ['id', 'group_name']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AuthorizationGroupWriteSerializer
        return AuthorizationGroupListSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class AuthGroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/v1/rbac/groups/<id>/  → detail with functions (screenshot 2)
    PATCH  /api/v1/rbac/groups/<id>/  → update (Update button)
    DELETE /api/v1/rbac/groups/<id>/  → delete (Delete button)
    """
    queryset = AuthorizationGroup.objects.prefetch_related(
        'group_functions__function__module'
    ).all()
    permission_classes = [permissions.IsAuthenticated, IsAdminGroupMember]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return AuthorizationGroupWriteSerializer
        return AuthorizationGroupDetailSerializer


# ─── Group Functions (Function List / Apply — screenshot 3) ─────────────────

class GroupFunctionListView(generics.ListAPIView):
    """
    GET /api/v1/rbac/groups/<group_id>/functions/
    Returns all functions currently assigned to the group.
    """
    serializer_class = GroupFunctionSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminGroupMember]

    def get_queryset(self):
        group_id = self.kwargs['group_id']
        get_object_or_404(AuthorizationGroup, pk=group_id)
        return GroupFunction.objects.filter(
            authorization_group_id=group_id
        ).select_related('function__module')


class GroupFunctionBulkAssignView(APIView):
    """
    POST /api/v1/rbac/groups/<group_id>/functions/assign/

    Body:
    {
        "functions": [
            {"function_id": 1, "can_read": true, "can_create": true, ...},
            {"function_id": 3, "can_read": true},
            ...
        ]
    }

    This replaces ALL existing GroupFunction rows for the group
    (mirrors the 'Apply' button in screenshot 3).
    """
    
    permission_classes = [permissions.IsAuthenticated, IsAdminGroupMember]

    @extend_schema(request=GroupFunctionBulkSerializer, responses={200: GroupFunctionSerializer(many=True)})
    @transaction.atomic
    def post(self, request, group_id):
        group = get_object_or_404(AuthorizationGroup, pk=group_id)
        serializer = GroupFunctionBulkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        incoming = serializer.validated_data['functions']
        function_ids = [item['function_id'] for item in incoming]

        # Validate all function IDs exist
        existing_functions = Function.objects.filter(pk__in=function_ids, is_active=True)
        if existing_functions.count() != len(function_ids):
            return Response(
                {'detail': 'One or more function_id values are invalid or inactive.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        invalidate_permission_cache(request.user)
        # Delete existing assignments and recreate
        GroupFunction.objects.filter(authorization_group=group).delete()

        new_entries = [
            GroupFunction(
                authorization_group=group,
                function_id=item['function_id'],
                can_create=item.get('can_create', False),
                can_read=item.get('can_read', True),
                can_update=item.get('can_update', False),
                can_delete=item.get('can_delete', False),
                can_approve=item.get('can_approve', False),
                can_print=item.get('can_print', False),
                can_export=item.get('can_export', False),
            )
            for item in incoming
        ]
        GroupFunction.objects.bulk_create(new_entries)

        result = GroupFunction.objects.filter(
            authorization_group=group
        ).select_related('function__module')
        return Response(GroupFunctionSerializer(result, many=True).data)


# ─── User ↔ Group Assignments ────────────────────────────────────────────────

class GroupUsersView(APIView):
    """
    GET  /api/v1/rbac/groups/<group_id>/users/        → list users in group
    POST /api/v1/rbac/groups/<group_id>/users/assign/ → assign users to group
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminGroupMember]

    def get(self, request, group_id):
        group = get_object_or_404(AuthorizationGroup, pk=group_id)
        qs = UserAuthorizationGroup.objects.filter(
            authorization_group=group
        ).select_related('user', 'authorization_group')
        return Response(UserAuthGroupSerializer(qs, many=True).data)


class GroupAssignUsersView(APIView):
    """POST /api/v1/rbac/groups/<group_id>/users/assign/"""
    permission_classes = [permissions.IsAuthenticated, IsAdminGroupMember]

    @extend_schema(request=AssignUsersToGroupSerializer)
    @transaction.atomic
    def post(self, request, group_id):
        group = get_object_or_404(AuthorizationGroup, pk=group_id)
        serializer = AssignUsersToGroupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from apps.authentication.models import User
        user_ids = serializer.validated_data['user_ids']
        users = User.objects.filter(pk__in=user_ids, is_active=True)
        if users.count() != len(user_ids):
            return Response(
                {'detail': 'One or more user_ids are invalid or inactive.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        created, skipped = [], []
        for user in users:
            obj, was_created = UserAuthorizationGroup.objects.get_or_create(
                user=user,
                authorization_group=group,
                defaults={'assigned_by': request.user},
            )
            (created if was_created else skipped).append(user.username)
            
        invalidate_permission_cache(request.user)

        return Response({
            'detail': f'Assigned {len(created)} user(s). {len(skipped)} already assigned.',
            'assigned': created,
            'already_assigned': skipped,
        })


class GroupRemoveUserView(APIView):
    """DELETE /api/v1/rbac/groups/<group_id>/users/<user_id>/"""
    permission_classes = [permissions.IsAuthenticated, IsAdminGroupMember]

    def delete(self, request, group_id, user_id):
        uag = get_object_or_404(
            UserAuthorizationGroup,
            authorization_group_id=group_id,
            user_id=user_id,
        )
        uag.delete()
        invalidate_permission_cache(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


# ─── Permission Check ────────────────────────────────────────────────────────

class MyPermissionsView(APIView):
    """
    GET /api/v1/rbac/my-permissions/
    Returns the full permission map for the current user.
    Useful for Vue frontend to decide which buttons to show.
    """
    def get(self, request):
        perms = get_user_permissions(request.user)
        return Response(perms)


class CheckPermissionView(APIView):
    """
    POST /api/v1/rbac/check-permission/
    Body: { "function_code": "GL-JOURNAL", "action": "can_create" }
    Returns: { "allowed": true/false }
    """
    @extend_schema(request=PermissionCheckSerializer, responses={200: dict})
    def post(self, request):
        serializer = PermissionCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        from .permissions import user_has_permission
        allowed = user_has_permission(
            request.user,
            serializer.validated_data['function_code'],
            serializer.validated_data['action'],
        )
        return Response({'allowed': allowed})

class MenuTreeView(APIView):
    """
    GET /api/v1/rbac/menu-tree/

    Return menu tree yang boleh diakses user yang sedang login.
    Dipakai Vue buat render sidebar navigation.

    Response shape:
    [
      {
        "module_code": "gl",
        "module_name": "General Ledger",
        "children": [
          {
            "id": 1,
            "name": "Chart of Accounts",
            "code": "GL-CHART-OF-ACCOUNTS",
            "url_path": "/gl/chart-of-accounts",
            "children": []
          },
          ...
        ]
      },
      ...
    ]
    """
    def get(self, request):
        user = request.user

        # Superuser dapat semua
        if user.is_superuser:
            allowed_codes = None
        else:
            perms = get_user_permissions(user)
            # Filter hanya function yang punya can_read=True
            allowed_codes = {
                code for code, actions in perms.items()
                if actions.get('can_read', False)
            }

        modules = Module.objects.filter(is_active=True).order_by('order')
        result = []

        for module in modules:
            # Ambil hanya root functions (parent=None)
            root_functions = module.functions.filter(
                is_active=True,
                parent=None,
            ).order_by('order')

            module_tree = self._build_tree(root_functions, allowed_codes)
            if module_tree:
                result.append({
                    'module_code': module.code,
                    'module_name': module.name,
                    'children': module_tree,
                })

        return Response(result)

    def _build_tree(self, functions, allowed_codes):
        tree = []
        for fn in functions:
            children = self._build_tree(
                fn.children.filter(is_active=True).order_by('order'),
                allowed_codes,
            )
            # Tampilkan jika:
            # 1. Superuser (allowed_codes=None)
            # 2. Function ini sendiri boleh diakses
            # 3. Atau salah satu anaknya boleh diakses (parent menu tetap tampil)
            is_allowed = (
                allowed_codes is None
                or fn.code in allowed_codes
                or bool(children)
            )
            if is_allowed:
                tree.append({
                    'id':       fn.id,
                    'code':     fn.code,
                    'name':     fn.name,
                    'url_path': fn.url_path,
                    'children': children,
                })
        return tree