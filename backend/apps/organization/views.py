from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, status, permissions
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from django.db import models as django_models

from apps.authentication.models import User
from apps.rbac.models import AuthorizationGroup, UserAuthorizationGroup
from apps.rbac.permissions import IsAdminGroupMember, HasFunctionPermission
from .models import Company, Department, Position, Employee
from .serializers import (
    CompanySerializer, DepartmentSerializer, PositionSerializer,
    EmployeeCreateSerializer, EmployeeListSerializer,
    EmployeeDetailSerializer, EmployeeUpdateSerializer,
)


class CompanyDetailView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/v1/org/company/ — single-tenant, selalu 1 record."""
    serializer_class   = CompanySerializer
    parser_classes     = [MultiPartParser, FormParser, JSONParser]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), HasFunctionPermission()]

    def get_rbac_function_code(self):
        return 'SETTINGS-COMPANY-INFORMATION'

    def get_object(self):
        from .models import Company
        return Company.get_default()


class DepartmentTreeView(generics.ListCreateAPIView):
    serializer_class   = DepartmentSerializer
    pagination_class   = None

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), HasFunctionPermission()]

    def get_rbac_function_code(self):
        return 'SETTINGS-ORGANIZATIONAL-STRUCTURE'

    def get_queryset(self):
        return Department.objects.filter(
            parent=None, is_active=True
        ).order_by('order')

    def perform_create(self, serializer):
        company = Company.get_default()
        if not company:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'detail': 'Company belum dikonfigurasi.'})
        serializer.save(company=company)


class PositionListView(generics.ListCreateAPIView):
    """GET /api/v1/org/positions/"""
    queryset           = Position.objects.filter(is_active=True).select_related('department')
    serializer_class   = PositionSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'SETTINGS-ORGANIZATIONAL-STRUCTURE'
    filterset_fields   = ['department']
    search_fields      = ['code', 'name']
    pagination_class   = None


class EmployeeListCreateView(APIView):
    """
    GET  /api/v1/org/employees/  → list
    POST /api/v1/org/employees/  → create employee + user sekaligus
    """
    rbac_function_code = 'SETTINGS-EMPLOYEE-DATA'
    parser_classes     = [MultiPartParser, FormParser, JSONParser]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), HasFunctionPermission()]

    def get(self, request):
        qs = Employee.objects.select_related(
            'position__department', 'user'
        ).prefetch_related('user__user_auth_groups__authorization_group')

        # Filter
        status_filter = request.query_params.get('status')
        dept_filter   = request.query_params.get('department')
        search        = request.query_params.get('search')

        if status_filter:
            qs = qs.filter(status=status_filter)
        if dept_filter:
            qs = qs.filter(position__department_id=dept_filter)
        if search:
            qs = qs.filter(
                django_models.Q(full_name__icontains=search) |
                django_models.Q(employee_id__icontains=search) |
                django_models.Q(email__icontains=search)
            )

        serializer = EmployeeListSerializer(qs, many=True)
        return Response(serializer.data)

    @transaction.atomic
    def post(self, request):
        print("REQUEST DATA:", request.data)
        serializer = EmployeeCreateSerializer(data=request.data)
        
        if not serializer.is_valid():
            print("SERIALIZER ERRORS:", serializer.errors)  # ← tambah ini
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data

        # 1. Generate employee ID
        company     = Company.get_default()
        employee_id = Employee.generate_employee_id(company.company_code)

        # 2. Buat User
        user = User.objects.create_user(
            username  = data['username'],
            email     = data['email'],
            full_name = data['full_name'],
            password  = data['password'],
        )

        # 3. Buat Employee
        employee = Employee.objects.create(
            user          = user,
            position      = data['position'],
            employee_id   = employee_id,
            full_name     = data['full_name'],
            email         = data['email'],
            phone         = data.get('phone', ''),
            join_date     = data.get('join_date'),
            status        = data.get('status', 'active'),
            signature_draw= data.get('signature_draw', ''),
        )

        # 4. Handle signature image kalau ada
        if 'signature_image' in request.FILES:
            employee.signature_image = request.FILES['signature_image']
            employee.save()

        # 5. Assign ke Authorization Groups
        group_ids = data.get('authorization_group_ids', [])
        for group_id in group_ids:
            group = AuthorizationGroup.objects.get(pk=group_id)
            UserAuthorizationGroup.objects.create(
                user                = user,
                authorization_group = group,
                assigned_by         = request.user,
            )

        if not serializer.is_valid():
            print("ERRORS:", serializer.errors)  # ← dan ini
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            EmployeeDetailSerializer(employee).data,
            status=status.HTTP_201_CREATED,
        )


class EmployeeDetailView(APIView):
    """
    GET    /api/v1/org/employees/<id>/
    PATCH  /api/v1/org/employees/<id>/
    DELETE /api/v1/org/employees/<id>/
    """
    rbac_function_code = 'SETTINGS-EMPLOYEE-DATA'
    parser_classes     = [MultiPartParser, FormParser, JSONParser]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), HasFunctionPermission()]

    def get_object(self, pk):
        return get_object_or_404(
            Employee.objects.select_related(
                'position__department', 'user'
            ).prefetch_related('user__user_auth_groups__authorization_group'),
            pk=pk
        )

    def get(self, request, pk):
        employee = self.get_object(pk)
        return Response(EmployeeDetailSerializer(employee).data)

    @transaction.atomic
    def patch(self, request, pk):
        employee   = self.get_object(pk)
        serializer = EmployeeUpdateSerializer(
            employee, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)

        # Update group assignments kalau ada
        group_ids = serializer.validated_data.pop('authorization_group_ids', None)
        if group_ids is not None and employee.user:
            # Replace semua group
            UserAuthorizationGroup.objects.filter(user=employee.user).delete()
            for group_id in group_ids:
                group = AuthorizationGroup.objects.get(pk=group_id)
                UserAuthorizationGroup.objects.create(
                    user                = employee.user,
                    authorization_group = group,
                    assigned_by         = request.user,
                )

        # Handle signature image
        if 'signature_image' in request.FILES:
            employee.signature_image = request.FILES['signature_image']

        serializer.save()
        return Response(EmployeeDetailSerializer(employee).data)

    def delete(self, request, pk):
        employee = self.get_object(pk)
        if employee.user:
            employee.user.is_active = False
            employee.user.save()
        employee.status = 'terminated'
        employee.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class DepartmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PATCH/DELETE /api/v1/org/departments/<id>/"""
    queryset           = Department.objects.all()
    serializer_class   = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'SETTINGS-ORGANIZATIONAL-STRUCTURE'

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

class EmployeeSignatureView(APIView):
    """
    POST /api/v1/org/employees/<id>/signature/
    Update signature saja — upload image atau save canvas draw.
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser, JSONParser]

    def post(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk)

        # Cek permission — hanya diri sendiri atau admin
        is_own = (
            hasattr(request.user, 'employee_profile') and
            request.user.employee_profile.pk == pk
        )

        has_employee_access = request.user.is_superuser or \
            request.user.user_auth_groups.filter(
                authorization_group__group_functions__function__function_code='SETTINGS-EMPLOYEE-DATA'
            ).exists()
        
        if not is_own and not has_employee_access:
            return Response(
                {'detail': 'Tidak diizinkan.'},
                status=status.HTTP_403_FORBIDDEN
            )

        if 'signature_image' in request.FILES:
            employee.signature_image = request.FILES['signature_image']
            employee.signature_draw  = ''

        elif 'signature_draw' in request.data:
            employee.signature_draw  = request.data['signature_draw']
            # Clear image kalau ada
            if employee.signature_image:
                employee.signature_image.delete(save=False)
                employee.signature_image = None

        else:
            return Response(
                {'detail': 'Kirim signature_image atau signature_draw.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        employee.save()
        return Response({
            'detail':          'Signature berhasil disimpan.',
            'has_signature':   employee.has_signature,
            'signature_draw':  employee.signature_draw,
            'signature_image': request.build_absolute_uri(employee.signature_image.url)
                               if employee.signature_image else None,
        })

class DepartmentPositionListView(generics.ListCreateAPIView):
    """
    GET  /api/v1/org/departments/<dept_id>/positions/
    POST /api/v1/org/departments/<dept_id>/positions/
    """
    serializer_class   = PositionSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'SETTINGS-ORGANIZATIONAL-STRUCTURE'

    def get_queryset(self):
        dept_id = self.kwargs['dept_id']
        get_object_or_404(Department, pk=dept_id)
        return Position.objects.filter(
            department_id=dept_id
        ).annotate(
            employee_count=django_models.Count('employees', filter=django_models.Q(employees__status='active'))
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
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'SETTINGS-ORGANIZATIONAL-STRUCTURE'

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