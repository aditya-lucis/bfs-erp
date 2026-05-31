from rest_framework import generics, permissions
from .models import Company, Department, Position, Employee
from .serializers import (
    CompanySerializer, DepartmentSerializer,
    PositionSerializer, EmployeeSerializer,
)
from apps.rbac.permissions import IsAdminGroupMember


class CompanyDetailView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/v1/org/company/ — single-tenant, selalu 1 record."""
    serializer_class   = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        from .models import Company
        return Company.get_default()


class DepartmentTreeView(generics.ListAPIView):
    """GET /api/v1/org/departments/ — return root departments (level 0) dengan nested children."""
    serializer_class   = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Department.objects.filter(
            parent=None, is_active=True
        ).order_by('order')


class PositionListView(generics.ListCreateAPIView):
    """GET /api/v1/org/positions/"""
    queryset           = Position.objects.filter(is_active=True).select_related('department')
    serializer_class   = PositionSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminGroupMember]
    filterset_fields   = ['department']
    search_fields      = ['code', 'name']


class EmployeeListCreateView(generics.ListCreateAPIView):
    """GET/POST /api/v1/org/employees/"""
    queryset = Employee.objects.select_related(
        'position__department', 'user'
    ).all()
    serializer_class   = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminGroupMember]
    filterset_fields   = ['status', 'position__department']
    search_fields      = ['employee_id', 'full_name', 'email']


class EmployeeDetailView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/v1/org/employees/<id>/"""
    queryset           = Employee.objects.select_related('position__department', 'user')
    serializer_class   = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminGroupMember]