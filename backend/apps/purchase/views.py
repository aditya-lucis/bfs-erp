from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from django.core.exceptions import ValidationError
from email.mime.image import MIMEImage
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

        project_id = self.request.query_params.get('project')
        if project_id:
            qs = qs.filter(project_id=project_id)

        rap_id = self.request.query_params.get('rap')
        if rap_id:
            qs = qs.filter(rap_id=rap_id)

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

# ─────────────────────────────────────────────────────────────────────────────
# Purchase Order (PO)
# ─────────────────────────────────────────────────────────────────────────────

from .models import PurchaseOrder
from .serializers import PurchaseOrderListSerializer, PurchaseOrderSerializer, POInboxSerializer

class PurchaseOrderListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'PURCHASES-PURCHASE-ORDER'

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PurchaseOrderListSerializer
        return PurchaseOrderSerializer

    def get_queryset(self):
        company = Company.get_default()
        qs = PurchaseOrder.objects.filter(company=company).select_related(
            'vendor', 'project', 'rap', 'requestor_department', 'created_by'
        )
        
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(Q(po_number__icontains=search) | Q(vendor__name__icontains=search))
            
        doc_status = self.request.query_params.get('document_status')
        if doc_status:
            qs = qs.filter(document_status=doc_status)
            
        app_status = self.request.query_params.get('approval_status')
        if app_status:
            qs = qs.filter(approval_status=app_status)
            
        po_type = self.request.query_params.get('po_type')
        if po_type:
            qs = qs.filter(po_type=po_type)

        start_date = self.request.query_params.get('start_date')
        if start_date:
            qs = qs.filter(po_date__gte=start_date)

        end_date = self.request.query_params.get('end_date')
        if end_date:
            qs = qs.filter(po_date__lte=end_date)

        return qs

    def perform_create(self, serializer):
        company = Company.get_default()
        serializer.save(company=company, created_by=self.request.user)


class PurchaseOrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'PURCHASES-PURCHASE-ORDER'

    def perform_destroy(self, instance):
        if instance.approval_status in [PurchaseOrder.ApprovalStatus.AWAITING, PurchaseOrder.ApprovalStatus.APPROVED]:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'detail': 'Purchase Order yang sedang diajukan atau sudah disetujui tidak dapat dihapus.'})
        instance.delete()



class PurchaseOrderManualCloseView(APIView):
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'PURCHASES-PURCHASE-ORDER'

    def post(self, request, pk):
        from rest_framework.exceptions import ValidationError
        from rest_framework.response import Response
        
        try:
            po = PurchaseOrder.objects.get(pk=pk)
        except PurchaseOrder.DoesNotExist:
            raise ValidationError({'detail': 'Purchase Order tidak ditemukan.'})
            
        action_type = request.data.get('action', 'toggle')
        close_reason_val = request.data.get('close_reason', 'Manual Close')

        if po.is_close:
            # Check if it was auto-closed due to expiration
            if po.close_reason and ('kadaluarsa' in po.close_reason.lower() or 'expired' in po.close_reason.lower()):
                raise ValidationError({'detail': 'PO ini ditutup otomatis karena sudah kadaluarsa dan tidak bisa dibuka kembali.'})
            
            # Re-open the PO
            po.is_close = False
            po.close_reason = ''
            po.save()
            return Response({'message': 'Purchase Order berhasil dibuka kembali.'})
        else:
            # Close the PO
            po.is_close = True
            po.close_reason = close_reason_val
            po.save()
            return Response({'message': 'Purchase Order berhasil ditutup manual.'})

class PurchaseOrderSubmitView(APIView):
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'PURCHASES-PURCHASE-ORDER'

    def post(self, request, pk):
        from django.db.models import Sum
        from apps.accounting_period.period_checker import PeriodChecker
        from apps.approval.services import create_approval_request, ApprovalMatrixError

        po = get_object_or_404(PurchaseOrder, pk=pk)

        if po.document_status not in ['draft', 'open']:
            return Response({'detail': 'PO ini sudah diproses atau ditutup dan tidak dapat diajukan lagi.'}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Validate Financial Period
        period_result = PeriodChecker.check(po.po_date, raise_exception=False)
        if not period_result.is_open:
            return Response({'detail': period_result.message}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Check Budget (based on RAP tolerance in Company)
        # Assuming budget is checked here before submission or during approval.
        # Since BFS ERP relies on the AnnualBudget, we should ideally check AnnualBudget remaining
        # but for simplicity, we mirror PR behavior and assume PO budget follows RAP if linked.

        if po.rap:
            from django.utils import timezone
            from decimal import Decimal
            
            current_year = timezone.now().year
            if current_year > po.rap.year_period and not po.allow_previous_year_budget:
                return Response({
                    'detail': f'PO ini menggunakan RAP tahun {po.rap.year_period}. Memerlukan izin "Allow Previous Year Budget" untuk disubmit pada tahun {current_year}.'
                }, status=status.HTTP_400_BAD_REQUEST)

            used_po = PurchaseOrder.objects.filter(
                rap=po.rap,
                document_status__in=['open', 'confirmed', 'delivered', 'invoiced', 'close']
            ).exclude(pk=po.pk).aggregate(total=Sum('grand_total'))['total'] or 0
            
            # Using Company RAP tolerance if applicable
            tolerance_val = po.company.rap_tolerance if po.company.rap_tolerance else 100
            tolerance = Decimal(str(tolerance_val)) / Decimal('100')
            allowed_budget = po.rap.total_cost * tolerance
            remaining_rap = allowed_budget - Decimal(str(used_po))
            
            if po.grand_total > remaining_rap:
                return Response({
                    'detail': f'Total PO ({po.grand_total}) melebihi sisa anggaran RAP yang diizinkan ({remaining_rap}).'
                }, status=status.HTTP_400_BAD_REQUEST)

        # 3. Create Approval Request
        try:
            create_approval_request(
                document_code='PO',
                document_id=str(po.id),
                document_number=po.po_number,
                creator_user=request.user,
                amount=po.grand_total,
            )
        except ApprovalMatrixError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        po.document_status = 'open'
        po.approval_status = 'awaiting'
        po.save()

        return Response(PurchaseOrderSerializer(po).data)


class POInboxViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Viewset untuk menampilkan daftar PO yang menunggu persetujuan oleh user login.
    """
    serializer_class = POInboxSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PurchaseOrder.objects.filter(approval_status=PurchaseOrder.ApprovalStatus.AWAITING).select_related('vendor', 'project')

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        try:
            from apps.purchase.services.po_approval_service import POApprovalService
            po = POApprovalService.approve_po(pk, request.user)
            return Response({'status': 'approved', 'po_number': po.po_number})
        except ValidationError as e:
            return Response({'detail': e.messages}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        try:
            from apps.purchase.services.po_approval_service import POApprovalService
            po = POApprovalService.reject_po(pk, request.user)
            return Response({'status': 'rejected', 'po_number': po.po_number})
        except ValidationError as e:
            return Response({'detail': e.messages}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def allow_previous_year_budget(self, request, pk=None):
        # Tambahkan RBAC function code khusus di sini jika diperlukan
        # Untuk kesederhanaan, kita hanya cek autentikasi
        po = get_object_or_404(PurchaseOrder, pk=pk)
        po.allow_previous_year_budget = True
        po.save()
        return Response({'status': 'success', 'message': 'Izin penggunaan RAP tahun sebelumnya telah diberikan.'})

from rest_framework.decorators import action
from rest_framework.response import Response
from .models import CompletionCertificate, PurchaseOrder, Vendor
from .serializers import CompletionCertificateSerializer

class CompletionCertificateViewSet(viewsets.ModelViewSet):
    queryset = CompletionCertificate.objects.all()
    serializer_class = CompletionCertificateSerializer

    @action(detail=False, methods=['get'])
    def get_valid_vendors(self, request):
        from apps.purchase.serializers import VendorListSerializer
        from django.utils import timezone
        from datetime import timedelta
        
        three_months_ago = timezone.now().date() - timedelta(days=90)
        PurchaseOrder.objects.filter(
            is_active=True,
            po_date__lt=three_months_ago,
            completioncertificate__isnull=True
        ).update(is_active=False)

        pos = PurchaseOrder.objects.filter(is_active=True, approval_status='approved').values_list('vendor_id', flat=True)
        vendors = Vendor.objects.filter(id__in=pos).distinct()
        serializer = VendorListSerializer(vendors, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def get_valid_pos(self, request):
        vendor_id = request.query_params.get('vendor_id')
        if not vendor_id:
            return Response([])
        from apps.purchase.serializers import PurchaseOrderSerializer
        from django.utils import timezone
        from datetime import timedelta
        
        three_months_ago = timezone.now().date() - timedelta(days=90)
        PurchaseOrder.objects.filter(
            is_active=True,
            vendor_id=vendor_id,
            po_date__lt=three_months_ago,
            completioncertificate__isnull=True
        ).update(is_active=False)
        
        pos = PurchaseOrder.objects.filter(vendor_id=vendor_id, is_active=True, approval_status='approved')
        serializer = PurchaseOrderSerializer(pos, many=True)
        return Response(serializer.data)


from .models import GrnSesDocument
from .serializers import GrnSesDocumentSerializer
from rest_framework import viewsets

class GrnSesDocumentViewSet(viewsets.ModelViewSet):
    queryset = GrnSesDocument.objects.all()
    serializer_class = GrnSesDocumentSerializer

from rest_framework.decorators import action
from rest_framework.response import Response
from .models import CompletionCertificate, PurchaseOrder, Vendor
from .serializers import CompletionCertificateSerializer

class CompletionCertificateViewSet(viewsets.ModelViewSet):
    queryset = CompletionCertificate.objects.all()
    serializer_class = CompletionCertificateSerializer

    @action(detail=False, methods=['get'])
    def get_valid_vendors(self, request):
        from apps.purchase.serializers import VendorListSerializer
        from django.utils import timezone
        from datetime import timedelta
        
        three_months_ago = timezone.now().date() - timedelta(days=90)
        PurchaseOrder.objects.filter(
            is_active=True,
            po_date__lt=three_months_ago,
            completioncertificate__isnull=True
        ).update(is_active=False)

        pos = PurchaseOrder.objects.filter(is_active=True, approval_status='approved').values_list('vendor_id', flat=True)
        vendors = Vendor.objects.filter(id__in=pos).distinct()
        serializer = VendorListSerializer(vendors, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def get_valid_pos(self, request):
        vendor_id = request.query_params.get('vendor_id')
        if not vendor_id:
            return Response([])
        from apps.purchase.serializers import PurchaseOrderSerializer
        from django.utils import timezone
        from datetime import timedelta
        
        three_months_ago = timezone.now().date() - timedelta(days=90)
        PurchaseOrder.objects.filter(
            is_active=True,
            vendor_id=vendor_id,
            po_date__lt=three_months_ago,
            completioncertificate__isnull=True
        ).update(is_active=False)
        
        pos = PurchaseOrder.objects.filter(vendor_id=vendor_id, is_active=True, approval_status='approved')
        serializer = PurchaseOrderSerializer(pos, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def void_cc(self, request, pk=None):
        from django.utils import timezone
        cc = self.get_object()
        
        # Check if a non-void, non-rejected GRN exists for this CC
        from apps.purchase.models import GoodReceiptNote
        active_grn = GoodReceiptNote.objects.filter(
            cc=cc
        ).exclude(
            void_reason__isnull=False
        ).exclude(
            approval_status='rejected'
        ).first()
        
        if active_grn:
            return Response({'detail': f'Tidak dapat melakukan void karena CC ini sudah digunakan pada Good Receipt Note ({active_grn.grn_number}).'}, status=400)
            
        void_reason = request.data.get('void_reason')
        if not void_reason:
            return Response({'detail': 'Alasan void wajib diisi.'}, status=400)
            
        cc.is_active = False
        cc.void_reason = void_reason
        cc.void_date = timezone.now()
        cc.void_by = request.user
        cc.save()
        
        return Response({'status': 'success', 'message': 'CC berhasil di-void'})

class CompletionCertificateSubmitApprovalView(APIView):
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'PURCHASES-COMPLETION-CERTIFICATE'

    def post(self, request, pk):
        from apps.accounting_period.period_checker import PeriodChecker
        from apps.approval.services import create_approval_request, ApprovalMatrixError
        
        cc = get_object_or_404(CompletionCertificate, pk=pk)

        if cc.approval_status not in ['draft', 'revised']:
            return Response({'detail': 'Completion Certificate ini sudah diajukan atau diproses.'}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Validate Financial Period
        period_result = PeriodChecker.check(cc.document_date, raise_exception=False)
        if not period_result.is_open:
            return Response({'detail': period_result.message}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Check if at least one document is attached and available
        if not cc.documents.filter(is_available=True).exists():
            return Response({'detail': 'Minimal satu dokumen kelengkapan (GRN/SES) harus tersedia (is_available=True).'}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Create Approval Request
        try:
            employee = request.user.employee_profile
            req = create_approval_request(
                document_code='CC',
                document_id=str(cc.id),
                document_number=cc.cc_number,
                creator_user=request.user,
                amount=cc.amount
            )
            
            # Update CC status to awaiting
            cc.approval_status = 'awaiting'
            cc.save()

            return Response({'detail': 'CC berhasil diajukan untuk persetujuan.', 'request_id': req.id}, status=status.HTTP_201_CREATED)
        except ApprovalMatrixError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except AttributeError:
            return Response({'detail': 'User belum terhubung dengan data profil Karyawan/Posisi.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from .models import GoodReceiptNote, GoodReceiptNoteDocument
from .serializers import GoodReceiptNoteSerializer, GoodReceiptNoteDocumentSerializer

class GoodReceiptNoteViewSet(viewsets.ModelViewSet):
    queryset = GoodReceiptNote.objects.all()
    serializer_class = GoodReceiptNoteSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        vendor_id = self.request.query_params.get('vendor')

        if start_date:
            queryset = queryset.filter(document_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(document_date__lte=end_date)
        if vendor_id:
            queryset = queryset.filter(vendor_id=vendor_id)
            
        return queryset

    @action(detail=False, methods=['get'])
    def get_valid_vendors(self, request):
        from apps.purchase.serializers import VendorListSerializer
        from apps.purchase.models import Vendor, PurchaseOrder
        
        pos = PurchaseOrder.objects.filter(
            is_active=True, 
            approval_status='approved',
            completioncertificate__approval_status='approved',
            completioncertificate__is_active=True,
            completioncertificate__void_reason__isnull=True
        ).values_list('vendor_id', flat=True)
        
        vendors = Vendor.objects.filter(id__in=pos).distinct()
        serializer = VendorListSerializer(vendors, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def get_valid_pos(self, request):
        vendor_id = request.query_params.get('vendor_id')
        if not vendor_id:
            return Response({'detail': 'vendor_id is required'}, status=400)
            
        from apps.purchase.models import PurchaseOrder
        pos = PurchaseOrder.objects.filter(
            vendor_id=vendor_id,
            is_active=True,
            approval_status='approved',
            completioncertificate__approval_status='approved',
            completioncertificate__is_active=True,
            completioncertificate__void_reason__isnull=True
        ).distinct()
        
        serializer = PurchaseOrderSerializer(pos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def get_valid_ccs(self, request):
        po_id = request.query_params.get('po_id')
        if not po_id:
            return Response({'detail': 'po_id is required'}, status=400)
            
        from apps.purchase.models import CompletionCertificate, GoodReceiptNote
        
        ccs = CompletionCertificate.objects.filter(
            po_id=po_id,
            approval_status='approved',
            is_active=True,
            void_reason__isnull=True
        )
        
        used_cc_ids = GoodReceiptNote.objects.filter(
            po_id=po_id
        ).exclude(
            void_reason__isnull=False
        ).exclude(
            approval_status='rejected'
        ).values_list('cc_id', flat=True)
        
        ccs = ccs.exclude(id__in=used_cc_ids)
        
        from .serializers import CompletionCertificateSerializer
        serializer = CompletionCertificateSerializer(ccs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def void_grn(self, request, pk=None):
        from django.utils import timezone
        grn = self.get_object()
        
        void_reason = request.data.get('void_reason')
        if not void_reason:
            return Response({'detail': 'Alasan void wajib diisi.'}, status=400)
            
        grn.is_active = False
        grn.void_reason = void_reason
        grn.void_date = timezone.now()
        grn.void_by = request.user
        grn.save()
        
        return Response({'status': 'success', 'message': 'GRN berhasil di-void'})

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        grn = self.get_object()
        
        pdf_file = request.FILES.get('pdf_file')

        from apps.organization.models import Company
        company = Company.get_default()
        
        # Optional sending logic
        if not company or not company.smtp_host or not company.smtp_user:
            return Response({'status': 'approved_no_email', 'detail': 'GRN Approved successfully, but email not sent (SMTP not configured).'}, status=status.HTTP_200_OK)

        try:
            from django.core.mail import EmailMultiAlternatives
            from django.core.mail.backends.smtp import EmailBackend
            from django.template.loader import render_to_string

            backend = EmailBackend(
                host=company.smtp_host,
                port=company.smtp_port,
                username=company.smtp_user,
                password=company.smtp_password,
                use_tls=company.smtp_use_tls,
                fail_silently=False
            )

            subject = f'Approved Good Receipt Note: {grn.grn_number}'
            
            # Prepare context for the template
            logo_url = ''
            if company.logo:
                logo_url = request.build_absolute_uri(company.logo.url)
                
            site_name = ''
            if grn.po and getattr(grn.po, 'project', None):
                site_name = f'{grn.po.project.project_code} - {grn.po.project.project_name}'
                
            po_number = grn.po.po_number if grn.po else ''
            
            # Calculate total value
            total_value = grn.amount
            
            context = {
                'company': company,
                'logo_url': logo_url,
                'vendor_name': grn.vendor.name if grn.vendor else '',
                'site_name': site_name,
                'po_number': po_number,
                'grn_number': grn.grn_number,
                'currency': grn.currency,
                'total_value': '{:,.2f}'.format(total_value),
                'description': grn.description or 'Pembayaran Tagihan'
            }
            
            html_content = render_to_string('email/grn_notification.html', context)
            text_content = f'Dear {grn.vendor.name},\n\nBerikut adalah GRN yang sudah selesai diproses oleh {company.company_name}. Silakan untuk dapat melakukan Invoicing.\n\nRegards,\n{company.company_name}'
            
            from_email = company.smtp_from_email or company.smtp_user or 'noreply@example.com'
            to_email = [grn.vendor.email] if grn.vendor and grn.vendor.email else []
            
            cc_email = []
            if hasattr(grn, 'created_by') and grn.created_by and hasattr(grn.created_by, 'email') and grn.created_by.email:
                cc_email.append(grn.created_by.email)

            if not to_email:
                return Response({'status': 'approved_no_email', 'detail': 'Vendor does not have an email address.'}, status=status.HTTP_200_OK)

            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email,
                to=to_email,
                cc=cc_email,
                connection=backend
            )
            email.attach_alternative(html_content, "text/html")
            
            if company.logo:
                try:
                    with open(company.logo.path, 'rb') as f:
                        logo_image = MIMEImage(f.read())
                        logo_image.add_header('Content-ID', '<company_logo>')
                        email.attach(logo_image)
                except Exception as e:
                    pass

            pdf_attached = False
            pdf_size = 0
            if pdf_file and pdf_file.size > 0:
                email.attach(pdf_file.name, pdf_file.read(), pdf_file.content_type)
                pdf_attached = True
                pdf_size = pdf_file.size
            email.send()

            import traceback
            with open('c:/Traine/bfs-erp/backend/email_debug.log', 'a') as f:
                f.write(f'SUCCESS: Email sent to {to_email} at {grn.grn_number}. PDF attached: {pdf_attached} (size: {pdf_size})\n')

            return Response({'status': 'email_sent', 'detail': 'Approval email sent to vendor successfully.'}, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            with open('c:/Traine/bfs-erp/backend/email_debug.log', 'a') as f:
                f.write(f'EXCEPTION: {str(e)}\n')
                f.write(traceback.format_exc() + '\n')
            # If email fails for some reason (e.g. wrong credentials), we still return success for the approval
            # but notify the user that email failed.
            return Response({'status': 'approved_email_failed', 'detail': f'GRN Approved but failed to send email: {str(e)}'}, status=status.HTTP_200_OK)


class GoodReceiptNoteSubmitApprovalView(APIView):
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'PURCHASES-GOOD-RECEIPT-NOTE'

    def post(self, request, pk):
        from apps.accounting_period.period_checker import PeriodChecker
        from apps.approval.services import create_approval_request, ApprovalMatrixError
        
        grn = get_object_or_404(GoodReceiptNote, pk=pk)
        
        period_result = PeriodChecker.check(grn.document_date, raise_exception=False)
        if not period_result.is_open:
            return Response({'detail': f'Accounting period is closed or not configured for date {grn.document_date}.'}, status=400)
            
        has_docs = grn.documents.filter(is_available=True).exists()
        if not has_docs:
            return Response({'detail': 'Setidaknya ada satu dokumen kelengkapan yang tersedia.'}, status=400)

        try:
            req = create_approval_request(
                document_code='GRN',
                document_id=grn.id,
                document_number=grn.grn_number,
                creator_user=request.user,
                amount=grn.amount
            )
            grn.approval_status = 'awaiting'
            grn.save()
            return Response({'detail': 'GRN berhasil diajukan untuk persetujuan.', 'request_id': req.id}, status=status.HTTP_201_CREATED)
        except ApprovalMatrixError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except AttributeError:
            return Response({'detail': 'User belum terhubung dengan data profil Karyawan/Posisi.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
