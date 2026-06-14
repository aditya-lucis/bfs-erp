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
        from apps.projects.models import RAP
        if instance.raps.filter(approval_status=RAP.ApprovalStatus.APPROVED).exists():
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'detail': 'Project tidak dapat dihapus karena memiliki Rencana Anggaran Pelaksana (RAP) yang sudah disetujui.'})
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
            from apps.projects.models import RAP
            if not project.raps.filter(approval_status=RAP.ApprovalStatus.APPROVED).exists():
                from rest_framework.exceptions import ValidationError
                raise ValidationError({'detail': 'Project tidak dapat dimulai karena Rencana Anggaran Pelaksana (RAP) belum disetujui.'})
            project.status = Project.Status.START
        elif action == 'cancel':
            project.status = Project.Status.CANCEL
        elif action == 'change_status' and new_status:
            if new_status == Project.Status.START:
                from apps.projects.models import RAP
                if not project.raps.filter(approval_status=RAP.ApprovalStatus.APPROVED).exists():
                    from rest_framework.exceptions import ValidationError
                    raise ValidationError({'detail': 'Project tidak dapat dimulai karena Rencana Anggaran Pelaksana (RAP) belum disetujui.'})
            project.status = new_status
        else:
            return Response({'detail': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

        project.save()
        return Response(ProjectListSerializer(project).data)

    def get_rbac_function_code(self):
        if 'commercial' in self.request.path:
            return 'COMMERCIAL-LIST-OF-PROJECTS'
        return 'PROJECTS-LIST-OF-PROJECTS'


# ─── RAP (Rencana Anggaran Pelaksana) Views ───────────────────────────────────

from .models import RAP
from .serializers import RAPSerializer
from apps.budget_component.models import TemplateRAPHeader
from apps.budget_component.serializers import TemplateRAPSerializer

class RAPListView(generics.ListCreateAPIView):
    serializer_class = RAPSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'PROJECTS-RAP'

    def get_queryset(self):
        company = Company.get_default()
        qs = RAP.objects.filter(company=company).select_related(
            'project', 'rap_type', 'department', 'position', 'budget_component', 'created_by'
        )
        
        # Search filter
        search = self.request.query_params.get('search')
        if search:
            from django.db.models import Q
            qs = qs.filter(Q(rap_number__icontains=search) | Q(project__project_name__icontains=search))
            
        # Project filter
        project_id = self.request.query_params.get('project')
        if project_id:
            qs = qs.filter(project_id=project_id)
            
        # Status filter (is_active)
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            val = is_active.lower() in ('true', '1')
            qs = qs.filter(is_active=val)
            
        # Document status filter
        doc_status = self.request.query_params.get('document_status')
        if doc_status:
            qs = qs.filter(document_status=doc_status)
            
        # Approval status filter
        app_status = self.request.query_params.get('approval_status')
        if app_status:
            qs = qs.filter(approval_status=app_status)
            
        # Date range filter
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            qs = qs.filter(rap_date__gte=date_from)
        if date_to:
            qs = qs.filter(rap_date__lte=date_to)
            
        return qs.order_by('-created_at')

    def perform_create(self, serializer):
        company = Company.get_default()
        serializer.save(company=company, created_by=self.request.user)


class RAPDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = RAP.objects.all()
    serializer_class = RAPSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'PROJECTS-RAP'


class RAPGetTemplateView(APIView):
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'PROJECTS-RAP'
    
    def get(self, request):
        budget_component_id = request.query_params.get('budget_component_id')
        if not budget_component_id:
            return Response({'detail': 'budget_component_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            template = TemplateRAPHeader.objects.get(
                budget_component_id=budget_component_id,
                is_active=True
            )
        except TemplateRAPHeader.DoesNotExist:
            return Response({'detail': 'Template RAP tidak ditemukan untuk Budget Component ini.'}, status=status.HTTP_404_NOT_FOUND)
            
        serializer = TemplateRAPSerializer(template)
        return Response(serializer.data)


class RAPSubmitView(APIView):
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'PROJECTS-RAP'

    def post(self, request, pk):
        from django.shortcuts import get_object_or_404
        from django.db.models import Sum
        from apps.accounting_period.period_checker import PeriodChecker
        from apps.annual_budget.models import AnnualBudgetHeader
        from apps.approval.services import create_approval_request, ApprovalMatrixError
        from .models import RAP
        from .serializers import RAPSerializer

        rap = get_object_or_404(RAP, pk=pk)

        # Only draft or revised RAP can be submitted
        if rap.document_status not in ('draft', 'ready_to_process'):
            # Allow resubmission if status was revised
            pass
        if rap.document_status == 'close':
            return Response({'detail': 'RAP ini sudah ditutup dan tidak dapat diajukan lagi.'}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Validate Financial Period is Open
        period_result = PeriodChecker.check(rap.rap_date, raise_exception=False)
        if not period_result.is_open:
            return Response({'detail': period_result.message}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Validate Budget Constraint
        header = AnnualBudgetHeader.objects.filter(
            company=rap.company,
            department=rap.department,
            year=rap.year_period
        ).first()
        if not header:
            return Response({
                'detail': f'Annual Budget belum di-set untuk Department {rap.department.name} di tahun {rap.year_period}.'
            }, status=status.HTTP_400_BAD_REQUEST)

        line = header.lines.filter(cost_category=rap.cost_category).first()
        budget_limit = 0
        if line:
            budget_limit = line.get_month_value(rap.month_period)['total']

        # Calculate already used budget by other finalized RAPs
        used_budget = RAP.objects.filter(
            company=rap.company,
            department=rap.department,
            year_period=rap.year_period,
            month_period=rap.month_period,
            cost_category=rap.cost_category,
            document_status__in=['ready_to_process', 'close']
        ).exclude(pk=rap.pk).aggregate(total=Sum('total_cost'))['total'] or 0

        remaining_budget = budget_limit - used_budget
        if rap.total_cost > remaining_budget:
            return Response({
                'detail': f'Total biaya RAP ({rap.total_cost}) melebihi sisa budget ({remaining_budget}) untuk Cost Category {rap.get_cost_category_display()} pada Department {rap.department.name} periode {rap.month_period}/{rap.year_period}.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 3. Create Approval Request
        try:
            create_approval_request(
                document_code='RAP',
                document_id=str(rap.id),
                document_number=rap.rap_number,
                creator_user=request.user,
                amount=rap.total_cost,
            )
        except ApprovalMatrixError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        # 4. Transition RAP Status
        rap.document_status = 'ready_to_process'
        rap.approval_status = 'awaiting'
        rap.save()

        return Response(RAPSerializer(rap).data)


