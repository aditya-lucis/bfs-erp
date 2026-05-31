from rest_framework import generics, permissions
from .models import Company, Department, Position, Employee
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
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
    serializer_class   = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    # ← Matiin pagination untuk tree view
    pagination_class   = None

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

class DepartmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PATCH/DELETE /api/v1/org/departments/<id>/"""
    queryset           = Department.objects.all()
    serializer_class   = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminGroupMember]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Cegah hapus kalau masih punya children
        if instance.children.exists():
            return Response(
                {'detail': 'Tidak bisa menghapus department yang masih punya sub-department.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

class DepartmentPositionListView(generics.ListCreateAPIView):
    """
    GET  /api/v1/org/departments/<dept_id>/positions/
    POST /api/v1/org/departments/<dept_id>/positions/
    """
    serializer_class   = PositionSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminGroupMember]

    def get_queryset(self):
        dept_id = self.kwargs['dept_id']
        get_object_or_404(Department, pk=dept_id)
        return Position.objects.filter(
            department_id=dept_id
        ).annotate(
            employee_count=Count('employees', filter=Q(employees__status='active'))
        )

    def perform_create(self, serializer):
        dept_id = self.kwargs['dept_id']
        dept    = get_object_or_404(Department, pk=dept_id)
        serializer.save(department=dept)


class DepartmentPositionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET/PATCH/DELETE /api/v1/org/departments/<dept_id>/positions/<pk>/
    """
    serializer_class   = PositionSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminGroupMember]

    def get_queryset(self):
        return Position.objects.filter(
            department_id=self.kwargs['dept_id']
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.employees.exists():
            return Response(
                {'detail': 'Tidak bisa menghapus posisi yang masih punya employee.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)