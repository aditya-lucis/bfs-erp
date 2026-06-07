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
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'INV-UNIT-MEASUREMENT'
    serializer_class   = UnitMeasurementSerializer
    pagination_class   = None

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