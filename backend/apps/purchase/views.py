from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.organization.models import Company
from apps.rbac.permissions import HasFunctionPermission
from .models import (
    VendorCategory,
    VendorGroup,
    Vendor,
    VendorLinkedAccount,
    VendorTerms,
    VendorContactPerson,
)
from .serializers import (
    VendorCategorySerializer,
    VendorGroupSerializer,
    VendorListSerializer,
    VendorDetailSerializer,
    VendorWriteSerializer,
    VendorLinkedAccountSerializer,
    VendorTermsSerializer,
    VendorContactPersonSerializer,
    PurchaseRequisitionListSerializer,
    PurchaseRequisitionSerializer,
)


# ── Master kecil ────────────────────────────────────────────────

class VendorCategoryListView(generics.ListCreateAPIView):
    queryset           = VendorCategory.objects.all().order_by('code')
    serializer_class   = VendorCategorySerializer
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'PURCHASES-VENDOR-CATEGORY'
    pagination_class   = None


class VendorCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset           = VendorCategory.objects.all()
    serializer_class   = VendorCategorySerializer
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'PURCHASES-VENDOR-CATEGORY'


class VendorGroupListView(generics.ListCreateAPIView):
    queryset           = VendorGroup.objects.all().order_by('name')
    serializer_class   = VendorGroupSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'PURCHASES-VENDOR-GROUP'
    pagination_class   = None


class VendorGroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset           = VendorGroup.objects.all()
    serializer_class   = VendorGroupSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'PURCHASES-VENDOR-GROUP'


# ── Vendor CRUD ────────────────────────────────────────────────

class VendorListView(generics.ListAPIView):
    serializer_class   = VendorListSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'PURCHASES-VENDOR'
    pagination_class   = None

    def get_queryset(self):
        qs = Vendor.objects.select_related('category', 'group').order_by('code')

        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)

        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(name__icontains=search) | Q(code__icontains=search)
            )

        return qs


class VendorCreateView(generics.CreateAPIView):
    serializer_class   = VendorWriteSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'PURCHASES-VENDOR'

    def perform_create(self, serializer):
        company = Company.get_default()
        if not company:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'detail': 'Company belum dikonfigurasi.'})
        vendor = serializer.save(company=company)
        VendorTerms.objects.create(vendor=vendor)


class VendorDetailView(generics.RetrieveAPIView):
    queryset = Vendor.objects.select_related(
        'category', 'group', 'department'
    ).prefetch_related(
        'linked_accounts__account',
        'terms',
        'contact_persons',
    )
    serializer_class   = VendorDetailSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'PURCHASES-VENDOR'


class VendorUpdateView(generics.UpdateAPIView):
    queryset           = Vendor.objects.all()
    serializer_class   = VendorWriteSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'PURCHASES-VENDOR'


class VendorDeleteView(generics.DestroyAPIView):
    queryset           = Vendor.objects.all()
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'PURCHASES-VENDOR'

    def destroy(self, request, *args, **kwargs):
        vendor = self.get_object()
        vendor.status = Vendor.Status.CLOSED
        vendor.save()
        return Response({'detail': 'Vendor berhasil dinonaktifkan.'}, status=status.HTTP_200_OK)


class VendorActivateView(APIView):
    """POST /api/v1/purchase/vendors/<pk>/activate/ — set status kembali ke Open."""
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'PURCHASES-VENDOR'
    rbac_action_map = {'POST': 'can_update'}

    def post(self, request, pk):
        vendor = get_object_or_404(Vendor, pk=pk)
        if vendor.status == Vendor.Status.OPEN:
            return Response(
                {'detail': 'Vendor sudah aktif.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        vendor.status = Vendor.Status.OPEN
        vendor.save(update_fields=['status', 'updated_at'])
        return Response({'detail': 'Vendor berhasil diaktifkan kembali.'})


# ── Linked Accounts ──────────────────────────────────────────────

class VendorLinkedAccountListView(generics.ListAPIView):
    serializer_class   = VendorLinkedAccountSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'PURCHASES-VENDOR'
    pagination_class   = None

    def get_queryset(self):
        return VendorLinkedAccount.objects.filter(
            vendor_id=self.kwargs['pk']
        ).select_related('account')


class VendorLinkedAccountBulkSaveView(APIView):
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'PURCHASES-VENDOR'

    def post(self, request, pk):
        vendor = get_object_or_404(Vendor, pk=pk)
        serializer = VendorLinkedAccountSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        VendorLinkedAccount.objects.filter(vendor=vendor).delete()
        VendorLinkedAccount.objects.bulk_create([
            VendorLinkedAccount(vendor=vendor, **item)
            for item in serializer.validated_data
        ])

        result = VendorLinkedAccountSerializer(
            VendorLinkedAccount.objects.filter(vendor=vendor).select_related('account'),
            many=True
        )
        return Response(result.data, status=status.HTTP_200_OK)


# ── Terms ─────────────────────────────────────────────────────────

class VendorTermsView(APIView):
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'PURCHASES-VENDOR'

    def get(self, request, pk):
        terms = get_object_or_404(VendorTerms, vendor_id=pk)
        return Response(VendorTermsSerializer(terms).data)

    def put(self, request, pk):
        terms = get_object_or_404(VendorTerms, vendor_id=pk)
        serializer = VendorTermsSerializer(terms, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request, pk):
        terms = get_object_or_404(VendorTerms, vendor_id=pk)
        serializer = VendorTermsSerializer(terms, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# ── Contact Person ────────────────────────────────────────────────

class VendorContactPersonListView(generics.ListCreateAPIView):
    serializer_class   = VendorContactPersonSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'PURCHASES-VENDOR'
    pagination_class   = None

    def get_queryset(self):
        return VendorContactPerson.objects.filter(
            vendor_id=self.kwargs['pk']
        ).order_by('id')

    def perform_create(self, serializer):
        vendor = get_object_or_404(Vendor, pk=self.kwargs['pk'])
        serializer.save(vendor=vendor)


class VendorContactPersonDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = VendorContactPersonSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'PURCHASES-VENDOR'

    def get_queryset(self):
        return VendorContactPerson.objects.filter(
            vendor_id=self.kwargs['vendor_pk']
        )


# ─────────────────────────────────────────────────────────────────────────────
# Purchase Requisition (PR)
# ─────────────────────────────────────────────────────────────────────────────

from .models import PurchaseRequisition
from apps.approval.models import ApprovalRequest, ApprovalStatus, StepStatus

class PurchaseRequisitionListView(generics.ListCreateAPIView):
    serializer_class = PurchaseRequisitionSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'PURCHASES-PURCHASE-REQUISITION'

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PurchaseRequisitionListSerializer
        return PurchaseRequisitionSerializer

    def get_queryset(self):
        company = Company.get_default()
        qs = PurchaseRequisition.objects.filter(company=company).select_related(
            'project', 'rap', 'department', 'budget_component', 'created_by'
        )
        
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(Q(pr_number__icontains=search) | Q(project__project_name__icontains=search))
            
        doc_status = self.request.query_params.get('document_status')
        if doc_status:
            qs = qs.filter(document_status=doc_status)
            
        app_status = self.request.query_params.get('approval_status')
        if app_status:
            qs = qs.filter(approval_status=app_status)
            
        pr_type = self.request.query_params.get('pr_type')
        if pr_type:
            qs = qs.filter(pr_type=pr_type)

        start_date = self.request.query_params.get('start_date')
        if start_date:
            qs = qs.filter(pr_date__gte=start_date)

        end_date = self.request.query_params.get('end_date')
        if end_date:
            qs = qs.filter(pr_date__lte=end_date)

        return qs

    def perform_create(self, serializer):
        company = Company.get_default()
        serializer.save(company=company, created_by=self.request.user)


class PurchaseRequisitionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PurchaseRequisition.objects.all()
    serializer_class = PurchaseRequisitionSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'PURCHASES-PURCHASE-REQUISITION'

    def perform_destroy(self, instance):
        if instance.approval_status in [PurchaseRequisition.ApprovalStatus.AWAITING, PurchaseRequisition.ApprovalStatus.APPROVED]:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'detail': 'Purchase Requisition yang sedang diajukan atau sudah disetujui tidak dapat dihapus.'})
        instance.delete()


class PurchaseRequisitionSubmitView(APIView):
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'PURCHASES-PURCHASE-REQUISITION'

    def post(self, request, pk):
        from django.db.models import Sum
        from apps.accounting_period.period_checker import PeriodChecker
        from apps.annual_budget.models import AnnualBudgetHeader
        from apps.approval.services import create_approval_request, ApprovalMatrixError

        pr = get_object_or_404(PurchaseRequisition, pk=pk)

        if pr.document_status not in ['draft', 'ready_to_process']:
            return Response({'detail': 'PR ini sudah ditutup dan tidak dapat diajukan lagi.'}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Validate Financial Period
        period_result = PeriodChecker.check(pr.pr_date, raise_exception=False)
        if not period_result.is_open:
            return Response({'detail': period_result.message}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Validate Budget Constraint (Strict validation)
        # If RM/SP, it must be validated against RAP
        if pr.pr_type in [PurchaseRequisition.PRType.RAW_MATERIAL, PurchaseRequisition.PRType.SUPPLIES]:
            if not pr.rap:
                return Response({'detail': 'PR tipe RM/SP harus merujuk pada RAP.'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if total amount of PR exceeds RAP remaining budget for the selected cost category or items.
            # Simplified for now: PR total_amount must not exceed RAP total_cost remaining (or we check item by item).
            # Here we just check total_amount against RAP's total cost
            used_rap = PurchaseRequisition.objects.filter(
                rap=pr.rap,
                document_status__in=['ready_to_process', 'close']
            ).exclude(pk=pr.pk).aggregate(total=Sum('total_amount'))['total'] or 0
            
            remaining_rap = pr.rap.total_cost - used_rap
            if pr.total_amount > remaining_rap:
                return Response({
                    'detail': f'Total PR ({pr.total_amount}) melebihi sisa anggaran RAP ({remaining_rap}).'
                }, status=status.HTTP_400_BAD_REQUEST)

        # 3. Create Approval Request
        try:
            create_approval_request(
                document_code='PR',
                document_id=str(pr.id),
                document_number=pr.pr_number,
                creator_user=request.user,
                amount=pr.total_amount,
            )
        except ApprovalMatrixError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        pr.document_status = 'ready_to_process'
        pr.approval_status = 'awaiting'
        pr.save()

        return Response(PurchaseRequisitionSerializer(pr).data)


# ─────────────────────────────────────────────────────────────────────────────
# PR Inbox
# ─────────────────────────────────────────────────────────────────────────────

class PurchaseRequisitionInboxListView(generics.ListAPIView):
    serializer_class = PurchaseRequisitionListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        employee = getattr(user, 'employee_profile', None)
        if not employee:
            return PurchaseRequisition.objects.none()
            
        # Get pending steps for user's position
        pending_requests = ApprovalRequest.objects.filter(
            document_code='PR',
            status=ApprovalStatus.PENDING,
            steps__position_id=employee.position_id,
            steps__status=StepStatus.PENDING,
            steps__step_number=models.F('current_step_number')
        ).values_list('document_id', flat=True)
        
        qs = PurchaseRequisition.objects.filter(id__in=pending_requests).select_related(
            'project', 'rap', 'department', 'budget_component', 'created_by'
        )
        return qs


class PurchaseRequisitionApproveView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        from apps.approval.services import approve_step, reject_request, revise_request, ApprovalMatrixError
        
        pr = get_object_or_404(PurchaseRequisition, pk=pk)
        action = request.data.get('action') # 'approve', 'reject', 'revise'
        remarks = request.data.get('remarks', '')
        
        # Approver can change final_unit_price before approving
        details_data = request.data.get('details', [])
        if details_data and action == 'approve':
            # Update final unit prices and recalculate
            total = 0
            for item_data in details_data:
                detail_id = item_data.get('id')
                final_price = item_data.get('final_unit_price')
                if detail_id and final_price is not None:
                    detail = pr.details.filter(id=detail_id).first()
                    if detail:
                        detail.final_unit_price = final_price
                        detail.amount = detail.quantity * detail.final_unit_price
                        detail.save()
                        total += detail.amount
            
            pr.total_amount = total
            pr.save()
        
        # Get active approval request
        approval_request = ApprovalRequest.objects.filter(
            document_code='PR',
            document_id=str(pr.id),
            status=ApprovalStatus.PENDING
        ).first()
        
        if not approval_request:
            return Response({'detail': 'Approval request tidak ditemukan atau sudah diproses.'}, status=status.HTTP_400_BAD_REQUEST)
            
        ip_address = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT')
        
        try:
            if action == 'approve':
                result = approve_step(approval_request.id, request.user, remarks, ip_address, user_agent)
                if result.status == ApprovalStatus.APPROVED:
                    pr.approval_status = 'approved'
            elif action == 'reject':
                result = reject_request(approval_request.id, request.user, remarks, ip_address, user_agent)
                pr.approval_status = 'rejected'
                pr.document_status = 'close'
            elif action == 'revise':
                result = revise_request(approval_request.id, request.user, remarks, ip_address, user_agent)
                pr.approval_status = 'revised'
                pr.document_status = 'draft'
            else:
                return Response({'detail': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
                
            pr.save()
            return Response({'detail': f'PR berhasil di-{action}.'})
            
        except ApprovalMatrixError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
