"""
BFS ERP — Inventory: Views

Endpoints:
    Unit Measurement:
        GET/POST        /api/v1/inventory/units/
        GET/PATCH/DELETE /api/v1/inventory/units/<id>/

    Item Category:
        GET/POST        /api/v1/inventory/categories/
        GET/PATCH/DELETE /api/v1/inventory/categories/<id>/

    Item:
        GET/POST        /api/v1/inventory/items/
        GET/PATCH/DELETE /api/v1/inventory/items/<id>/
        POST            /api/v1/inventory/items/<id>/upload-image/
        GET/POST        /api/v1/inventory/items/<id>/accounts/
        DELETE          /api/v1/inventory/items/<id>/accounts/<link_id>/

    Choices:
        GET             /api/v1/inventory/choices/
"""

from django.db.models import Q
from rest_framework import generics, status, permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from apps.rbac.permissions import HasFunctionPermission
from .models import (
    UnitMeasurement, ItemCategory, Item, ItemAccountLink,
    ReceiptReport, Warehouse, WarehouseBin
)
from .serializers import (
    UnitMeasurementSerializer,
    ItemCategorySerializer,
    ItemListSerializer,
    ItemDetailSerializer,
    ItemCreateSerializer,
    ItemAccountLinkSerializer,
    WarehouseSerializer,
    WarehouseBinSerializer,
    ReceiptReportSerializer,
    get_inventory_choices,
)


# ─── Warehouse ────────────────────────────────────────────────────────────────

class WarehouseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Warehouse.objects.filter(is_active=True).prefetch_related('bins')
    serializer_class = WarehouseSerializer


class WarehouseBinViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WarehouseBin.objects.filter(is_active=True)
    serializer_class = WarehouseBinSerializer


# ─── Unit Measurement ─────────────────────────────────────────────────────────

class UnitListCreateView(generics.ListCreateAPIView):
    serializer_class   = UnitMeasurementSerializer
    pagination_class   = None

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), HasFunctionPermission()]

    def get_rbac_function_code(self):
        return 'INV-UNIT-MEASUREMENT'

    def get_queryset(self):
        qs     = UnitMeasurement.objects.all()
        params = self.request.query_params

        item_type = params.get('item_type')
        if item_type:
            qs = qs.filter(item_type=item_type.upper())

        active = params.get('active', 'true').lower()
        if active != 'all':
            qs = qs.filter(is_active=(active == 'true'))

        search = params.get('search')
        if search:
            qs = qs.filter(unit_name__icontains=search)

        return qs.order_by('item_type', 'unit_name')


class UnitDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'INV-UNIT-MEASUREMENT'
    serializer_class   = UnitMeasurementSerializer
    queryset           = UnitMeasurement.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.items_main.filter(is_active=True).exists():
            return Response(
                {'detail': 'Unit tidak bisa dihapus karena masih digunakan oleh item aktif.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ─── Item Category ────────────────────────────────────────────────────────────

class ItemCategoryListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'INV-ITEM-CATEGORY'
    serializer_class   = ItemCategorySerializer
    pagination_class   = None

    def get_queryset(self):
        qs     = ItemCategory.objects.all()
        params = self.request.query_params

        item_type = params.get('item_type')
        if item_type:
            qs = qs.filter(item_type=item_type.upper())

        active = params.get('active', 'true').lower()
        if active != 'all':
            qs = qs.filter(is_active=(active == 'true'))

        search = params.get('search')
        if search:
            qs = qs.filter(name__icontains=search)

        return qs.order_by('item_type', 'name')


class ItemCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'INV-ITEM-CATEGORY'
    serializer_class   = ItemCategorySerializer
    queryset           = ItemCategory.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.items.filter(is_active=True).exists():
            return Response(
                {'detail': 'Category tidak bisa dihapus karena masih memiliki item aktif.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ─── Item ─────────────────────────────────────────────────────────────────────

class ItemListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'INV-ITEM'
    parser_classes     = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        return ItemCreateSerializer if self.request.method == 'POST' else ItemListSerializer

    def get_queryset(self):
        qs     = Item.objects.select_related('category', 'unit', 'created_by')
        params = self.request.query_params

        item_type = params.get('item_type')
        if item_type:
            qs = qs.filter(item_type=item_type.upper())

        category = params.get('category')
        if category:
            qs = qs.filter(category_id=category)

        active = params.get('active', 'true').lower()
        if active == 'all':
            pass
        else:
            qs = qs.filter(is_active=(active == 'true'))

        is_new = params.get('is_new')
        if is_new is not None:
            qs = qs.filter(is_new=(is_new.lower() == 'true'))

        search = params.get('search')
        if search:
            qs = qs.filter(
                Q(item_code__icontains=search) | Q(item_name__icontains=search)
            )

        return qs.order_by('item_code')

    def create(self, request, *args, **kwargs):
        serializer = ItemCreateSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        item = serializer.save()
        return Response(
            ItemDetailSerializer(item, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


class ItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'INV-ITEM'
    parser_classes     = [MultiPartParser, FormParser, JSONParser]
    queryset           = Item.objects.select_related(
                             'category', 'unit',
                             'secondary_rr_unit', 'secondary_sndo_unit',
                             'secondary_production_unit', 'created_by',
                         ).prefetch_related('account_links__account')

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return ItemCreateSerializer
        return ItemDetailSerializer

    def update(self, request, *args, **kwargs):
        partial    = kwargs.pop('partial', False)
        instance   = self.get_object()
        serializer = ItemCreateSerializer(
            instance,
            data=request.data,
            partial=partial,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        item = serializer.save()
        return Response(
            ItemDetailSerializer(item, context={'request': request}).data
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ItemImageUploadView(APIView):
    """
    POST /api/v1/inventory/items/<id>/upload-image/
    Upload atau replace gambar item.
    """
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'INV-ITEM'
    parser_classes     = [MultiPartParser, FormParser]

    def post(self, request, pk):
        item = Item.objects.get(pk=pk)

        if 'image' not in request.FILES:
            return Response(
                {'detail': 'File gambar tidak ditemukan. Gunakan key "image".'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Hapus gambar lama kalau ada
        if item.image:
            item.image.delete(save=False)

        item.image = request.FILES['image']
        item.save()

        return Response(
            ItemDetailSerializer(item, context={'request': request}).data
        )


# ─── Item Account Links ───────────────────────────────────────────────────────

class ItemAccountLinkListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/inventory/items/<item_pk>/accounts/
    POST /api/v1/inventory/items/<item_pk>/accounts/
    """
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'INV-ITEM'
    serializer_class   = ItemAccountLinkSerializer
    pagination_class   = None

    def get_item(self):
        return Item.objects.get(pk=self.kwargs['item_pk'])

    def get_queryset(self):
        return ItemAccountLink.objects.filter(
            item_id=self.kwargs['item_pk']
        ).select_related('account').order_by('purpose', 'currency')

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['item'] = self.get_item()
        return ctx

    def perform_create(self, serializer):
        serializer.save(item=self.get_item())


class ItemAccountLinkDeleteView(generics.DestroyAPIView):
    """
    DELETE /api/v1/inventory/items/<item_pk>/accounts/<pk>/
    """
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'INV-ITEM'

    def get_queryset(self):
        return ItemAccountLink.objects.filter(item_id=self.kwargs['item_pk'])


# ─── Choices ──────────────────────────────────────────────────────────────────

class InventoryChoicesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(get_inventory_choices())
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ReceiptReport, ReceiptReportItem
from .serializers import ReceiptReportSerializer, ReceiptReportItemSerializer
from apps.purchase.models import PurchaseOrder

class ReceiptReportViewSet(viewsets.ModelViewSet):
    queryset = ReceiptReport.objects.all().select_related('company', 'vendor', 'po', 'created_by')
    serializer_class = ReceiptReportSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'INV-RECEIPT-REPORT'

    def get_queryset(self):
        qs = super().get_queryset()
        
        receipt_type = self.request.query_params.get('receipt_type')
        if receipt_type:
            qs = qs.filter(receipt_type=receipt_type)
            
        po_number = self.request.query_params.get('po_number')
        if po_number:
            qs = qs.filter(po__po_number__icontains=po_number)
            
        po_id = self.request.query_params.get('po')
        if po_id:
            qs = qs.filter(po_id=po_id)
            
        start_date = self.request.query_params.get('start_date')
        if start_date:
            qs = qs.filter(receive_date__gte=start_date)
            
        end_date = self.request.query_params.get('end_date')
        if end_date:
            qs = qs.filter(receive_date__lte=end_date)
            
        document_status = self.request.query_params.get('document_status')
        if document_status:
            qs = qs.filter(document_status=document_status)
            
        approval_status = self.request.query_params.get('approval_status')
        if approval_status:
            qs = qs.filter(approval_status=approval_status)
            
        return qs

    def perform_create(self, serializer):
        from datetime import datetime
        user = self.request.user
        
        # Determine company from PO if available, otherwise fallback to user's company
        po = serializer.validated_data.get('po')
        company = None
        if po and hasattr(po, 'company'):
            company = po.company
        elif hasattr(user, 'employee') and user.employee:
            company = user.employee.company
            
        rr = serializer.save(created_by=user, updated_by=user, company=company)
        # Generate receipt_number
        date_str = datetime.now().strftime('%Y%m%d%H%M%S')
        rr.receipt_number = f"RR{date_str}-{rr.id:04d}"
        rr.save()

    @action(detail=True, methods=['post', 'patch'])
    def update_tracking(self, request, pk=None):
        from django.utils import timezone
        instance = self.get_object()
        tracking_status = request.data.get('tracking_status', '')
        
        instance.tracking_status = tracking_status
        instance.tracking_last_update = timezone.now()
        instance.save(update_fields=['tracking_status', 'tracking_last_update'])
        
        return Response({'status': 'Tracking updated successfully'})

    @action(detail=True, methods=['get'])
    def print_data(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        # Add company data
        if instance.company:
            from apps.organization.serializers import CompanySerializer
            company_data = CompanySerializer(instance.company).data
            # Adjust logo url if needed
            if instance.company.logo:
                company_data['logo_url'] = request.build_absolute_uri(instance.company.logo.url)
            data['company_detail'] = company_data
        else:
            data['company_detail'] = None

        # Add created_by detail
        if instance.created_by:
            data['created_by_name'] = getattr(instance.created_by, 'get_full_name', lambda: instance.created_by.username)()
            
        # Add approval signatures
        from apps.approval.models import ApprovalRequest
        approval_req = ApprovalRequest.objects.filter(document_code='RECEIPT_REPORT', document_id=str(instance.id)).order_by('-created_at').first()
        
        signatures = []
        if approval_req:
            for step in approval_req.steps.all().order_by('step_number'):
                signer_name = step.position.employee.full_name if (hasattr(step.position, 'employee') and step.position.employee) else step.position.name
                signatures.append({
                    'role': step.get_role_display(),
                    'name': signer_name,
                    'status': step.status,
                    'date': step.updated_at if step.status == 'approved' else None
                })
                
        data['signatures'] = signatures

        return Response(data)

    @action(detail=False, methods=['get'])
    def get_valid_vendors(self, request):
        from apps.purchase.serializers import VendorListSerializer
        from apps.purchase.models import Vendor, PurchaseOrder
        
        # Valid vendors for Receipt Report are those that have a PO with a GRN (and CC) that are approved and not void
        pos = PurchaseOrder.objects.filter(
            is_active=True, 
            approval_status='approved',
            goodreceiptnote__approval_status='approved',
            goodreceiptnote__is_active=True,
            goodreceiptnote__void_reason__isnull=True,
            goodreceiptnote__cc__approval_status='approved',
            goodreceiptnote__cc__is_active=True,
            goodreceiptnote__cc__void_reason__isnull=True
        ).values_list('vendor_id', flat=True)
        
        vendors = Vendor.objects.filter(id__in=pos).distinct()
        serializer = VendorListSerializer(vendors, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def get_valid_pos(self, request):
        from apps.purchase.serializers import PurchaseOrderListSerializer
        from apps.purchase.models import PurchaseOrder
        vendor_id = request.query_params.get('vendor_id')
        if not vendor_id:
            return Response({'detail': 'vendor_id is required'}, status=400)
            
        pos = PurchaseOrder.objects.filter(
            vendor_id=vendor_id,
            is_active=True,
            approval_status='approved',
            goodreceiptnote__approval_status='approved',
            goodreceiptnote__is_active=True,
            goodreceiptnote__void_reason__isnull=True,
            goodreceiptnote__cc__approval_status='approved',
            goodreceiptnote__cc__is_active=True,
            goodreceiptnote__cc__void_reason__isnull=True
        ).distinct()
        
        serializer = PurchaseOrderListSerializer(pos, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        rr = self.get_object()
        
        if rr.approval_status != ReceiptReport.ApprovalStatus.DRAFT:
            return Response({'detail': 'Hanya Receipt Report berstatus Draft yang dapat disetujui.'}, status=status.HTTP_400_BAD_REQUEST)
            
        rr.approval_status = ReceiptReport.ApprovalStatus.APPROVED
        rr.save()
        
        # 1. Menambah saldo stok barang di Inventory
        # TODO: integrate with actual inventory balance logic once available, for now skip.
        
        # 2. Menambahkan receive_qty ke po_item.received_qty
        all_po_items = list(rr.po.details.all()) if rr.po else []
        for item in rr.items.all():
            po_item = item.po_item
            if po_item:
                po_item.received_qty += item.receive_qty
                po_item.save()
                
        # 3. Mengecek apakah semua item di PO tersebut received_qty >= quantity
        if rr.po and rr.po.status != PurchaseOrder.Status.CLOSED:
            po = rr.po
            po_items = po.details.all()
            all_received = True
            for p_item in po_items:
                if p_item.received_qty < p_item.quantity:
                    all_received = False
                    break
                    
            if all_received:
                po.status = PurchaseOrder.Status.CLOSED
                po.close_reason = 'Auto-closed: Semua barang telah diterima'
                po.save()
                
        return Response({'message': 'Receipt Report berhasil disetujui.'})

    @action(detail=True, methods=['post'])
    def void(self, request, pk=None):
        from django.utils import timezone
        from django.db import transaction
        from django.db.models import F
        from apps.purchase.models import PurchaseInvoice, PurchaseOrder
        from apps.accounting.models import JournalHeader, JournalDetail
        
        rr = self.get_object()
        
        # 1. Validation
        if rr.approval_status != ReceiptReport.ApprovalStatus.APPROVED:
            return Response({'detail': 'Hanya Receipt Report berstatus Approved yang dapat di-void.'}, status=status.HTTP_400_BAD_REQUEST)
            
        if PurchaseInvoice.objects.filter(receipt_report=rr).exists():
            return Response({'detail': 'Tidak dapat melakukan void karena Receipt Report ini sudah digunakan pada Purchase Invoice.'}, status=status.HTTP_400_BAD_REQUEST)
            
        void_reason = request.data.get('void_reason')
        if not void_reason:
            return Response({'detail': 'Alasan void wajib diisi.'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            with transaction.atomic():
                # 2. Update status of Receipt Report
                rr.approval_status = ReceiptReport.ApprovalStatus.VOID
                rr.void_reason = void_reason
                rr.void_date = timezone.now()
                rr.void_by = request.user
                rr.save(update_fields=['approval_status', 'void_reason', 'void_date', 'void_by'])
                
                # 3. Revert po_item.received_qty
                for item in rr.items.all():
                    if item.po_item:
                        po_item = item.po_item
                        # Revert received_qty using F expression safely
                        po_item.received_qty = F('received_qty') - item.receive_qty
                        po_item.save(update_fields=['received_qty'])
                        
                # 4. Reopen PO if it was auto-closed
                if rr.po and rr.po.status == PurchaseOrder.Status.CLOSED:
                    po = rr.po
                    po.status = PurchaseOrder.Status.OPEN # Reopen it
                    po.close_reason = ''
                    po.save(update_fields=['status', 'close_reason'])
                    
                # 5. Reverse accounting journal details if any
                original_journal = JournalHeader.objects.filter(journal_number=rr.receipt_number).first()
                if original_journal:
                    void_journal_number = f"VOID-{rr.receipt_number}"
                    if not JournalHeader.objects.filter(journal_number=void_journal_number).exists():
                        void_journal = JournalHeader.objects.create(
                            journal_number=void_journal_number,
                            company=rr.company,
                            date=timezone.now().date(),
                            memo=f"Void Receipt Report: {rr.receipt_number} - Reason: {void_reason}",
                            project=rr.po.project if rr.po else None,
                            created_by=request.user,
                            type='INV'
                        )
                        
                        # Loop through original details and reverse debits/credits
                        for detail in original_journal.details.all():
                            debet_amount = detail.base_kredit
                            kredit_amount = detail.base_debet
                            
                            JournalDetail.objects.create(
                                journal_header=void_journal,
                                account=detail.account,
                                currency=detail.currency,
                                base_debet=debet_amount,
                                base_kredit=kredit_amount
                            )
                            
                            # Update account balance
                            account = detail.account
                            
                            if detail.base_debet > 0:
                                # Reversing debet: we add to month_kredit, and subtract/add from amount
                                account.month_kredit = F('month_kredit') + detail.base_debet
                                if account.default_position == 'DEBET':
                                    account.amount = F('amount') - detail.base_debet
                                else:
                                    account.amount = F('amount') + detail.base_debet
                                    
                            if detail.base_kredit > 0:
                                # Reversing kredit: we add to month_debet, and add/subtract from amount
                                account.month_debet = F('month_debet') + detail.base_kredit
                                if account.default_position == 'DEBET':
                                    account.amount = F('amount') + detail.base_kredit
                                else:
                                    account.amount = F('amount') - detail.base_kredit
                                    
                            account.save(update_fields=['month_debet', 'month_kredit', 'amount'])
                            
            return Response({'status': 'success', 'message': 'Receipt Report berhasil di-void'})
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


from datetime import datetime
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from .models import ReceiptReport, ReceiptReportItem
from .serializers import ReceiptReportSerializer
from apps.purchase.models import PurchaseOrder
from apps.rbac.permissions import HasFunctionPermission
from apps.approval.services import create_approval_request, approve_step, reject_request

class ReceiptReportSubmitView(APIView):
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'INV-RECEIPT-REPORT'

    def post(self, request, pk):
        from apps.accounting_period.period_checker import PeriodChecker
        
        rr = get_object_or_404(ReceiptReport, pk=pk)
        if rr.approval_status not in ['draft', 'revised']:
            return Response({'detail': 'Receipt Report ini sudah diajukan.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate Accounting Period
        period_result = PeriodChecker.check(rr.receive_date, raise_exception=False)
        if not period_result.is_open:
            return Response({'detail': period_result.message}, status=status.HTTP_400_BAD_REQUEST)

        try:
            total_quantity = sum(item.receive_qty for item in rr.items.all())
            total_amount = sum(item.receive_qty * (item.po_item.unit_price if item.po_item else 0) for item in rr.items.all())
            
            req = create_approval_request(
                document_code='RECEIPT_REPORT',
                document_id=rr.id,
                document_number=rr.receipt_number,
                creator_user=request.user,
                quantity=total_quantity,
                amount=total_amount,
                company=rr.company
            )
            rr.approval_status = ReceiptReport.ApprovalStatus.AWAITING
            rr.document_status = ReceiptReport.DocumentStatus.READY_TO_PROCESS
            rr.save(update_fields=['approval_status', 'document_status'])
            return Response({'message': 'Receipt Report berhasil disubmit.', 'approval_id': req.id})
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ReceiptReportApproveView(APIView):
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'INV-RECEIPT-REPORT'

    def post(self, request, pk):
        rr = get_object_or_404(ReceiptReport, pk=pk)
        action = request.data.get('action') # approve, reject, revise
        remarks = request.data.get('remarks', '')
        
        if rr.approval_status != ReceiptReport.ApprovalStatus.AWAITING:
            return Response({'detail': 'RR tidak dalam status Awaiting.'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            if action == 'approve':
                is_final, next_user = approve_step('RR', rr.id, request.user, remarks)
                if is_final:
                    rr.approval_status = ReceiptReport.ApprovalStatus.APPROVED
                    rr.save()
                    
                    # Auto-close PO logic for RR_PUR
                    if rr.receipt_type == 'RR_PUR' and rr.po:
                        po = rr.po
                        all_items_received = True
                        for po_item in po.details.all():
                            total_received = ReceiptReportItem.objects.filter(
                                po_item=po_item,
                                receipt_report__po=po,
                                receipt_report__receipt_type='RR_PUR',
                                receipt_report__approval_status='approved'
                            ).aggregate(Sum('receive_qty'))['receive_qty__sum'] or 0
                            
                            if total_received < po_item.quantity:
                                all_items_received = False
                                break
                                
                        if all_items_received:
                            po.is_close = True
                            po.close_reason = 'Fully Received'
                            po.save()
                            
                return Response({'message': 'RR Approved'})
            elif action == 'reject':
                reject_request('RR', rr.id, request.user, remarks)
                rr.approval_status = ReceiptReport.ApprovalStatus.REJECTED
                rr.save()
                return Response({'message': 'RR Rejected'})
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
