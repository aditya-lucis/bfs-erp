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
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from apps.rbac.permissions import HasFunctionPermission
from .models import UnitMeasurement, ItemCategory, Item, ItemAccountLink
from .serializers import (
    UnitMeasurementSerializer,
    ItemCategorySerializer,
    ItemListSerializer,
    ItemDetailSerializer,
    ItemCreateSerializer,
    ItemAccountLinkSerializer,
    get_inventory_choices,
)


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
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        
        receipt_type = self.request.query_params.get('receipt_type')
        if receipt_type:
            qs = qs.filter(receipt_type=receipt_type)
            
        po_number = self.request.query_params.get('po_number')
        if po_number:
            qs = qs.filter(po__po_number__icontains=po_number)
            
        return qs

    def perform_create(self, serializer):
        from datetime import datetime
        user = self.request.user
        rr = serializer.save(created_by=user, updated_by=user)
        # Generate receipt_number
        date_str = datetime.now().strftime('%Y%m%d%H%M%S')
        rr.receipt_number = f"RR{date_str}-{rr.id:04d}"
        rr.save()

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
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        rr = get_object_or_404(ReceiptReport, pk=pk)
        if rr.approval_status not in ['draft', 'revised']:
            return Response({'detail': 'Receipt Report ini sudah diajukan.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            req = create_approval_request(
                document_code='RR',
                document_id=rr.id,
                document_number=rr.receipt_number,
                creator_user=request.user,
                amount=0,
                company=rr.company
            )
            rr.approval_status = ReceiptReport.ApprovalStatus.AWAITING
            rr.save()
            return Response({'message': 'Receipt Report berhasil disubmit.', 'approval_id': req.id})
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ReceiptReportApproveView(APIView):
    permission_classes = [permissions.IsAuthenticated]

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
