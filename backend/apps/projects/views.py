from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.organization.models import Company
from apps.rbac.permissions import HasFunctionPermission
from .models import RAPType, Project, ProjectType, ProjectCategory
from .serializers import RAPTypeSerializer, ProjectListSerializer, ProjectWriteSerializer, ProjectTypeSerializer, ProjectCategorySerializer

class RAPTypeListView(generics.ListCreateAPIView):
    serializer_class = RAPTypeSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'PROJECTS-RAP-TYPE'
    pagination_class = None

    def get_queryset(self):
        company = Company.get_default()
        qs = RAPType.objects.filter(company=company, is_active=True)
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(name__icontains=search)
        return qs.order_by('name')

    def perform_create(self, serializer):
        company = Company.get_default()
        serializer.save(company=company)

class RAPTypeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = RAPType.objects.all()
    serializer_class = RAPTypeSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'PROJECTS-RAP-TYPE'

    def perform_destroy(self, instance):
        # Soft delete by setting is_active=False
        instance.is_active = False
        instance.save()


class ProjectTypeListView(generics.ListCreateAPIView):
    serializer_class = ProjectTypeSerializer
    pagination_class = None

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), HasFunctionPermission()]

    def get_rbac_function_code(self):
        return 'SETTINGS-PROJECT-CATEGORY'

    def get_queryset(self):
        company = Company.get_default()
        qs = ProjectType.objects.filter(company=company, is_active=True)
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(name__icontains=search)
        return qs

    def perform_create(self, serializer):
        company = Company.get_default()
        serializer.save(company=company)


class ProjectTypeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProjectType.objects.all()
    serializer_class = ProjectTypeSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'SETTINGS-PROJECT-CATEGORY'

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()


class ProjectCategoryListView(generics.ListCreateAPIView):
    serializer_class = ProjectCategorySerializer
    pagination_class = None

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), HasFunctionPermission()]

    def get_rbac_function_code(self):
        return 'SETTINGS-PROJECT-CATEGORY'

    def get_queryset(self):
        company = Company.get_default()
        qs = ProjectCategory.objects.filter(company=company, is_active=True)
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(name__icontains=search) | qs.filter(code__icontains=search)
        return qs

    def perform_create(self, serializer):
        company = Company.get_default()
        serializer.save(company=company)


class ProjectCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProjectCategory.objects.all()
    serializer_class = ProjectCategorySerializer
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'SETTINGS-PROJECT-CATEGORY'

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()



class ProjectListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    pagination_class = None

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProjectWriteSerializer
        return ProjectListSerializer

    def get_queryset(self):
        company = Company.get_default()
        qs = Project.objects.filter(company=company, is_active=True).select_related('customer', 'project_manager__position')
        
        search = self.request.query_params.get('search')
        if search:
            from django.db.models import Q
            qs = qs.filter(Q(project_name__icontains=search) | Q(project_code__icontains=search))
            
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
            
        return qs

    def perform_create(self, serializer):
        company = Company.get_default()
        serializer.save(company=company)

    def get_rbac_function_code(self):
        if 'commercial' in self.request.path:
            return 'COMMERCIAL-LIST-OF-PROJECTS'
        return 'PROJECTS-LIST-OF-PROJECTS'


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ProjectWriteSerializer
        return ProjectListSerializer

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()

    def get_rbac_function_code(self):
        if 'commercial' in self.request.path:
            return 'COMMERCIAL-LIST-OF-PROJECTS'
        return 'PROJECTS-LIST-OF-PROJECTS'


class ProjectActionView(APIView):
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]

    def post(self, request, pk):
        project = generics.get_object_or_404(Project, pk=pk)
        action = request.data.get('action') # 'start', 'cancel', 'change_status'
        new_status = request.data.get('status')

        if action == 'start':
            # project ini baru bisa di start ketika dia sudah punya RAP (nanti)
            # Karena modul RAP belum diimplementasikan, kita return validation error
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'detail': 'Project tidak dapat dimulai karena Rencana Anggaran Pelaksana (RAP) belum dibuat.'})
        elif action == 'cancel':
            project.status = Project.Status.CANCEL
        elif action == 'change_status' and new_status:
            if new_status == Project.Status.START:
                from rest_framework.exceptions import ValidationError
                raise ValidationError({'detail': 'Project tidak dapat dimulai karena Rencana Anggaran Pelaksana (RAP) belum dibuat.'})
            project.status = new_status
        else:
            return Response({'detail': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

        project.save()
        return Response(ProjectListSerializer(project).data)

    def get_rbac_function_code(self):
        if 'commercial' in self.request.path:
            return 'COMMERCIAL-LIST-OF-PROJECTS'
        return 'PROJECTS-LIST-OF-PROJECTS'

