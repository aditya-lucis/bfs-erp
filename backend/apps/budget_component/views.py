from django.db import models
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied

from apps.inventory.models import Item
from apps.inventory.serializers import ItemListSerializer
from apps.organization.models import Company
from apps.rbac.permissions import HasFunctionPermission
from .models import BudgetComponent, TemplateRAPHeader, TemplateRAPDetail
from .permissions import CanManageTemplateRAP
from .serializers import (
    BudgetComponentSerializer,
    BudgetComponentWriteSerializer,
    DepartmentPositionSerializer,
    TemplateRAPSerializer,
    TemplateRAPWriteSerializer,
    TemplateRAPDetailSerializer,
    TemplateRAPDetailWriteSerializer,
)


# ── Budget Component CRUD ───────────────────────────────────────────────────

class BudgetComponentListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'FINANCE-BUDGET-COMPONENT'

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BudgetComponentWriteSerializer
        return BudgetComponentSerializer

    def get_queryset(self):
        qs = BudgetComponent.objects.select_related(
            'department', 'position'
        ).order_by('order_no', 'id')
        cost_cat = self.request.query_params.get('cost_category')
        if cost_cat:
            qs = qs.filter(cost_category=cost_cat)

        dept_id = self.request.query_params.get('department')
        if dept_id:
            qs = qs.filter(department_id=dept_id)

        active = self.request.query_params.get('active')
        if active is not None:
            qs = qs.filter(is_active=(active.lower() == 'true'))

        comp_type = self.request.query_params.get('component_type')
        if comp_type:
            qs = qs.filter(component_type=comp_type)

        return qs

    def perform_create(self, serializer):
        company = Company.get_default()
        if not company:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'detail': 'Company belum dikonfigurasi.'})
        serializer.save(company=company)


class BudgetComponentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BudgetComponent.objects.select_related('department', 'position')
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'FINANCE-BUDGET-COMPONENT'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return BudgetComponentWriteSerializer
        return BudgetComponentSerializer


# ── Helper: Positions by Department ─────────────────────────────────────────

class DepartmentPositionListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, dept_id):
        from apps.organization.models import Position
        positions = Position.objects.filter(
            department_id=dept_id,
            is_active=True,
        ).order_by('name')
        serializer = DepartmentPositionSerializer(positions, many=True)
        return Response(serializer.data)


# ── Template RAP ────────────────────────────────────────────────────────────

class TemplateRAPListView(generics.ListCreateAPIView):
    """
    GET  → list templates (filter by budget_component)
    POST → create template for a budget component
    """
    permission_classes = [
        permissions.IsAuthenticated,
        HasFunctionPermission,
        CanManageTemplateRAP,
    ]
    rbac_function_code = 'FINANCE-BUDGET-COMPONENT'

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TemplateRAPWriteSerializer
        return TemplateRAPSerializer

    def get_queryset(self):
        qs = TemplateRAPHeader.objects.select_related(
            'budget_component', 'budget_component__department', 'budget_component__position'
        ).prefetch_related('details')

        budget_component = self.request.query_params.get('budget_component')
        if budget_component:
            qs = qs.filter(budget_component_id=budget_component)

        # Filter by position for non-superuser
        if not self.request.user.is_superuser:
            if hasattr(self.request.user, 'employee_profile') and self.request.user.employee_profile:
                emp_pos = self.request.user.employee_profile.position
                qs = qs.filter(budget_component__position=emp_pos)

        return qs

    def perform_create(self, serializer):
        budget_component = serializer.validated_data.get('budget_component')

        # Check permission
        if not self.request.user.is_superuser:
            if not hasattr(self.request.user, 'employee_profile') or not self.request.user.employee_profile:
                raise PermissionDenied('Employee profile tidak ditemukan.')
            emp_pos = self.request.user.employee_profile.position
            if budget_component.position != emp_pos:
                raise PermissionDenied(
                    'Anda hanya boleh membuat Template RAP untuk posisi Anda sendiri.'
                )

        serializer.save()


class TemplateRAPDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TemplateRAPHeader.objects.prefetch_related('details')
    permission_classes = [
        permissions.IsAuthenticated,
        HasFunctionPermission,
        CanManageTemplateRAP,
    ]
    rbac_function_code = 'FINANCE-BUDGET-COMPONENT'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return TemplateRAPWriteSerializer
        return TemplateRAPSerializer

    def get_object(self):
        obj = super().get_object()
        # Check object-level permission
        if not self.request.user.is_superuser:
            if not hasattr(self.request.user, 'employee_profile') or not self.request.user.employee_profile:
                raise PermissionDenied('Employee profile tidak ditemukan.')
            emp_pos = self.request.user.employee_profile.position
            if obj.budget_component.position != emp_pos:
                raise PermissionDenied(
                    'Anda hanya boleh mengakses Template RAP untuk posisi Anda sendiri.'
                )
        return obj


# ── Template RAP Detail (Tree Nodes) ───────────────────────────────────────
class TemplateRAPDetailListView(generics.ListCreateAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
        HasFunctionPermission,
        CanManageTemplateRAP,
    ]
    rbac_function_code = 'FINANCE-BUDGET-COMPONENT'

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TemplateRAPDetailWriteSerializer
        return TemplateRAPDetailSerializer

    def get_queryset(self):
        qs = TemplateRAPDetail.objects.select_related(
            'item', 'item__unit'
        ).prefetch_related('children')

        template = self.request.query_params.get('template')
        if template:
            qs = qs.filter(template_id=template)

        # Return ALL details for this template (flat), frontend yang build tree
        # Jangan filter by parent — return semua biar frontend bisa build tree

        return qs.order_by('order_no', 'id')

    def perform_create(self, serializer):
        template = serializer.validated_data.get('template')

        # Check permission
        if not self.request.user.is_superuser:
            if not hasattr(self.request.user, 'employee_profile') or not self.request.user.employee_profile:
                raise PermissionDenied('Employee profile tidak ditemukan.')
            emp_pos = self.request.user.employee_profile.position
            if template.budget_component.position != emp_pos:
                raise PermissionDenied(
                    'Anda hanya boleh menambah detail untuk posisi Anda sendiri.'
                )

        serializer.save()

class TemplateRAPDetailDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TemplateRAPDetail.objects.select_related('item', 'item__unit')
    permission_classes = [
        permissions.IsAuthenticated,
        HasFunctionPermission,
        CanManageTemplateRAP,
    ]
    rbac_function_code = 'FINANCE-BUDGET-COMPONENT'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return TemplateRAPDetailWriteSerializer
        return TemplateRAPDetailSerializer

    def get_object(self):
        obj = super().get_object()
        # Check object-level permission
        if not self.request.user.is_superuser:
            if not hasattr(self.request.user, 'employee_profile') or not self.request.user.employee_profile:
                raise PermissionDenied('Employee profile tidak ditemukan.')
            emp_pos = self.request.user.employee_profile.position
            if obj.template.budget_component.position != emp_pos:
                raise PermissionDenied(
                    'Anda hanya boleh mengakses detail untuk posisi Anda sendiri.'
                )
        return obj


# ── Item Picker ─────────────────────────────────────────────────────────────

class ItemPickerListView(generics.ListAPIView):
    serializer_class = ItemListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Item.objects.select_related('unit', 'category').filter(is_active=True)

        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(
                models.Q(item_name__icontains=search) |
                models.Q(item_code__icontains=search)
            )

        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category_id=category)

        return qs[:50]