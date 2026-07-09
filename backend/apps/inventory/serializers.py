"""
BFS ERP — Inventory: Serializers

Unit Measurement, Item Category, Item, ItemAccountLink
"""

import re
from rest_framework import serializers
from .models import (
    UnitMeasurement, ItemCategory, Item, ItemAccountLink,
    ItemType, CostingMethod, PriceType, AccountPurpose,
    Warehouse, WarehouseBin, ItemBinAllocation,
    validate_directory_name,
)


# ─── Unit Measurement ─────────────────────────────────────────────────────────

class WarehouseBinSerializer(serializers.ModelSerializer):
    class Meta:
        model = WarehouseBin
        fields = '__all__'

class WarehouseSerializer(serializers.ModelSerializer):
    bins = WarehouseBinSerializer(many=True, read_only=True)
    class Meta:
        model = Warehouse
        fields = '__all__'

class UnitMeasurementSerializer(serializers.ModelSerializer):
    item_type_label = serializers.CharField(source='get_item_type_display', read_only=True)

    class Meta:
        model  = UnitMeasurement
        fields = [
            'id', 'unit_name', 'unit_description',
            'item_type', 'item_type_label',
            'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        unit_name = attrs.get('unit_name', getattr(self.instance, 'unit_name', ''))
        item_type = attrs.get('item_type', getattr(self.instance, 'item_type', ''))

        qs = UnitMeasurement.objects.filter(
            unit_name__iexact=unit_name,
            item_type=item_type,
        )
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError({
                'unit_name': f'Unit "{unit_name}" sudah ada untuk tipe {item_type}.'
            })
        return attrs

    def create(self, validated_data):
        return UnitMeasurement.objects.create(
            created_by=self.context['request'].user,
            **validated_data,
        )


# ─── Item Category ────────────────────────────────────────────────────────────

class ItemCategorySerializer(serializers.ModelSerializer):
    item_type_label = serializers.CharField(source='get_item_type_display', read_only=True)
    item_count      = serializers.SerializerMethodField()

    class Meta:
        model  = ItemCategory
        fields = [
            'id', 'name', 'description',
            'item_type', 'item_type_label',
            'item_count', 'is_active',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_item_count(self, obj):
        return obj.items.filter(is_active=True).count()

    def validate_name(self, value):
        # Force uppercase
        value = value.upper()
        # Validasi format directory
        validate_directory_name(value)
        return value

    def validate(self, attrs):
        name      = attrs.get('name', getattr(self.instance, 'name', ''))
        item_type = attrs.get('item_type', getattr(self.instance, 'item_type', ''))

        qs = ItemCategory.objects.filter(name=name.upper(), item_type=item_type)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError({
                'name': f'Directory "{name}" sudah ada untuk tipe {item_type}.'
            })
        return attrs

    def create(self, validated_data):
        return ItemCategory.objects.create(
            created_by=self.context['request'].user,
            **validated_data,
        )


# ─── Item Account Link ────────────────────────────────────────────────────────

class ItemAccountLinkSerializer(serializers.ModelSerializer):
    purpose_label  = serializers.CharField(source='get_purpose_display',  read_only=True)
    currency_label = serializers.CharField(source='get_currency_display', read_only=True)
    account_number = serializers.CharField(source='account.account_number', read_only=True)
    account_name   = serializers.CharField(source='account.account_name',   read_only=True)

    class Meta:
        model  = ItemAccountLink
        fields = [
            'id', 'purpose', 'purpose_label',
            'currency', 'currency_label',
            'account', 'account_number', 'account_name',
        ]

    def validate(self, attrs):
        item    = self.context.get('item')
        purpose  = attrs.get('purpose',  getattr(self.instance, 'purpose',  None))
        currency = attrs.get('currency', getattr(self.instance, 'currency', None))

        if item:
            qs = ItemAccountLink.objects.filter(item=item, purpose=purpose, currency=currency)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    f'Account link untuk purpose "{purpose}" dengan currency "{currency}" sudah ada.'
                )
        return attrs


# ─── Item ─────────────────────────────────────────────────────────────────────

class ItemListSerializer(serializers.ModelSerializer):
    """Lightweight — untuk list view."""
    category_name   = serializers.CharField(source='category.name',     read_only=True)
    item_type_label = serializers.CharField(source='get_item_type_display', read_only=True)
    unit_name       = serializers.CharField(source='unit.unit_name',    read_only=True)
    image_url       = serializers.SerializerMethodField()

    class Meta:
        model  = Item
        fields = [
            'id', 'item_code', 'item_name',
            'item_type', 'item_type_label',
            'category', 'category_name',
            'unit', 'unit_name',
            'unit_price', 'is_active', 'is_service', 'is_new',
            'image_url',
        ]

    def get_image_url(self, obj):
        if not obj.image:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url


class ItemDetailSerializer(serializers.ModelSerializer):
    """Full detail — untuk retrieve & response setelah create/update."""
    category_name              = serializers.CharField(source='category.name',                    read_only=True)
    item_type_label            = serializers.CharField(source='get_item_type_display',            read_only=True)
    unit_name                  = serializers.CharField(source='unit.unit_name',                   read_only=True)
    secondary_rr_unit_name     = serializers.CharField(source='secondary_rr_unit.unit_name',      read_only=True)
    secondary_sndo_unit_name   = serializers.CharField(source='secondary_sndo_unit.unit_name',    read_only=True)
    secondary_production_unit_name = serializers.CharField(source='secondary_production_unit.unit_name', read_only=True)
    costing_method_label       = serializers.CharField(source='get_costing_method_display',       read_only=True)
    price_type_label           = serializers.CharField(source='get_price_type_display',           read_only=True)
    account_links              = ItemAccountLinkSerializer(many=True, read_only=True)
    image_url                  = serializers.SerializerMethodField()
    created_by_name            = serializers.CharField(source='created_by.full_name', read_only=True)

    class Meta:
        model  = Item
        fields = [
            'id', 'item_code', 'item_name',
            'item_type', 'item_type_label',
            'category', 'category_name',

            'unit', 'unit_name',
            'secondary_rr_unit', 'secondary_rr_unit_name',
            'secondary_sndo_unit', 'secondary_sndo_unit_name',
            'secondary_production_unit', 'secondary_production_unit_name',

            'is_production', 'is_purchase',
            'price_type', 'price_type_label',
            'unit_price', 'is_last_purchase_price',

            'costing_method', 'costing_method_label',
            'default_currency', 'is_automatic_pr',

            'view_buy', 'view_sell', 'view_inventory',
            'is_active', 'is_service', 'is_new',

            'image_url',
            'account_links',

            'created_at', 'updated_at', 'created_by', 'created_by_name',
        ]

    def get_image_url(self, obj):
        if not obj.image:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url


class ItemCreateSerializer(serializers.ModelSerializer):
    """Create & Update item."""

    class Meta:
        model  = Item
        fields = [
            'item_name', 'item_type', 'category',
            'unit', 'secondary_rr_unit', 'secondary_sndo_unit', 'secondary_production_unit',
            'is_production', 'is_purchase',
            'price_type', 'unit_price', 'is_last_purchase_price',
            'costing_method', 'default_currency', 'is_automatic_pr',
            'view_buy', 'view_sell', 'view_inventory',
            'is_active', 'is_service', 'is_new',
            'image',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter unit choices sesuai item_type yang dikirim
        # (akan di-override di validate)

    def validate(self, attrs):
        item_type = attrs.get('item_type', getattr(self.instance, 'item_type', None))
        category  = attrs.get('category',  getattr(self.instance, 'category',  None))

        # category item_type harus sama dengan item item_type
        if category and item_type and category.item_type != item_type:
            raise serializers.ValidationError({
                'category': f'Category "{category.name}" bertipe {category.item_type}, '
                            f'bukan {item_type}.'
            })

        # Validasi semua unit sesuai item_type
        unit_fields = ['unit', 'secondary_rr_unit', 'secondary_sndo_unit', 'secondary_production_unit']
        for field in unit_fields:
            unit = attrs.get(field, getattr(self.instance, field, None) if self.instance else None)
            if unit and item_type and unit.item_type != item_type:
                raise serializers.ValidationError({
                    field: f'Unit "{unit.unit_name}" bertipe {unit.item_type}, '
                           f'bukan {item_type}. Pilih unit yang sesuai.'
                })

        # Minimal satu source
        is_production = attrs.get('is_production', getattr(self.instance, 'is_production', False))
        is_purchase   = attrs.get('is_purchase',   getattr(self.instance, 'is_purchase',   False))
        if not is_production and not is_purchase:
            raise serializers.ValidationError(
                'Item harus memiliki minimal satu source: Production atau Purchase.'
            )

        return attrs

    def create(self, validated_data):
        return Item.objects.create(
            created_by=self.context['request'].user,
            **validated_data,
        )

    def update(self, instance, validated_data):
        # Jangan izinkan ganti item_type atau category setelah create
        validated_data.pop('item_type', None)
        validated_data.pop('category',  None)

        # Handle image — kalau tidak dikirim, jangan hapus yang lama
        image = validated_data.get('image')
        if image is None and 'image' not in self.context['request'].FILES:
            validated_data.pop('image', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


# ─── Choices Serializer ───────────────────────────────────────────────────────

def get_inventory_choices():
    return {
        'item_types': [
            {'value': v, 'label': l} for v, l in ItemType.choices
        ],
        'costing_methods': [
            {'value': v, 'label': l} for v, l in CostingMethod.choices
        ],
        'price_types': [
            {'value': v, 'label': l} for v, l in PriceType.choices
        ],
        'account_purposes': [
            {'value': v, 'label': l} for v, l in AccountPurpose.choices
        ],
        'currencies': [
            {'value': 'ALL', 'label': 'All Currency'},
            {'value': 'IDR', 'label': 'IDR'},
            {'value': 'USD', 'label': 'USD'},
            {'value': 'EUR', 'label': 'EUR'},
            {'value': 'SGD', 'label': 'SGD'},
        ],
    }
from .models import ReceiptReport, ReceiptReportItem

class ItemBinAllocationSerializer(serializers.ModelSerializer):
    bin_name = serializers.CharField(source='bin.bin_name', read_only=True)
    bin_code = serializers.CharField(source='bin.bin_code', read_only=True)

    class Meta:
        model = ItemBinAllocation
        fields = '__all__'
        read_only_fields = ('reference_number', 'document_type', 'item')

class ReceiptReportItemSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.item_name', read_only=True)
    item_code = serializers.CharField(source='item.item_code', read_only=True)
    unit_name = serializers.CharField(source='unit_type.unit_name', read_only=True)
    bins = serializers.ListField(child=serializers.DictField(), write_only=True, required=False)
    
    # From add.cfm: unit_price and disc come from TAccPO_Detail (joined via RR Item -> PO Detail)
    po_item_unit_price = serializers.DecimalField(
        source='po_item.unit_price', max_digits=18, decimal_places=2, read_only=True, default=0
    )
    po_item_discount_percent = serializers.DecimalField(
        source='po_item.discount_percent', max_digits=5, decimal_places=2, read_only=True, default=0
    )
    po_item_amount = serializers.DecimalField(
        source='po_item.amount', max_digits=18, decimal_places=2, read_only=True, default=0
    )
    po_item_tax1 = serializers.CharField(source='po_item.tax1', read_only=True, default='')
    po_item_tax2 = serializers.CharField(source='po_item.tax2', read_only=True, default='')
    # Dimension from po_item (budget_component or rap_detail name)
    dimension = serializers.SerializerMethodField()

    def get_dimension(self, obj):
        if obj.po_item:
            if obj.po_item.budget_component:
                return obj.po_item.budget_component.name if hasattr(obj.po_item.budget_component, 'name') else str(obj.po_item.budget_component)
            if obj.po_item.rap_detail:
                return str(obj.po_item.rap_detail)
        return ''

    class Meta:
        model = ReceiptReportItem
        fields = '__all__'
        read_only_fields = ('receipt_report',)
        
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        allocations = ItemBinAllocation.objects.filter(
            reference_number=instance.receipt_report.receipt_number,
            document_type='RECEIPT_REPORT',
            item=instance.item
        )
        ret['bins'] = ItemBinAllocationSerializer(allocations, many=True).data
        return ret

class ReceiptReportSerializer(serializers.ModelSerializer):
    items = ReceiptReportItemSerializer(many=True)
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)
    po_number = serializers.CharField(source='po.po_number', read_only=True)
    
    class Meta:
        model = ReceiptReport
        fields = '__all__'
        read_only_fields = ('receipt_number', 'created_at', 'updated_at', 'created_by', 'updated_by', 'approval_status', 'document_status')

    def validate(self, attrs):
        # We need to validate items against PO remaining quantities
        po = attrs.get('po')
        if po:
            # We must get the items data from initial_data because it's a writable nested serializer
            # or from attrs if it's already popped/present. Actually, nested serializer data is in attrs.
            items_data = attrs.get('items', [])
            
            # Map PO items to their current remaining quantities
            # We get all po details to also check for partial status
            po_details = po.details.all()
            po_item_map = {}
            for pd in po_details:
                # pd.received_qty is dynamically calculated, but let's query it explicitly to be safe
                from django.db.models import Sum
                from apps.inventory.models import ReceiptReportItem
                
                qs = ReceiptReportItem.objects.filter(receipt_report__po=po, po_item=pd)
                if self.instance:
                    qs = qs.exclude(receipt_report=self.instance)
                    
                received = qs.aggregate(Sum('receive_qty'))['receive_qty__sum'] or 0
                remaining = pd.quantity - received
                po_item_map[pd.id] = {
                    'quantity': pd.quantity,
                    'received': received,
                    'remaining': remaining,
                    'new_receive': 0
                }
            
            for item_data in items_data:
                po_item = item_data.get('po_item')
                receive_qty = item_data.get('receive_qty', 0)
                
                if po_item:
                    pd_info = po_item_map.get(po_item.id)
                    if pd_info:
                        if receive_qty > pd_info['remaining']:
                            raise serializers.ValidationError(
                                f"Cannot receive {receive_qty} for item {po_item.item.item_code}. Only {pd_info['remaining']} remaining."
                            )
                        pd_info['new_receive'] += receive_qty
            
            # Check if partial
            is_partial = False
            for pd_id, pd_info in po_item_map.items():
                total_after_this = pd_info['received'] + pd_info['new_receive']
                if total_after_this < pd_info['quantity']:
                    is_partial = True
                    break
            
            attrs['is_partial'] = is_partial
            
        vendor = attrs.get('vendor', getattr(self.instance, 'vendor', None))
        vendor_sn = attrs.get('vendor_sn', getattr(self.instance, 'vendor_sn', None))
        
        if vendor and vendor_sn:
            qs = ReceiptReport.objects.filter(vendor=vendor, vendor_sn=vendor_sn)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({
                    'vendor_sn': f'Vendor SN "{vendor_sn}" sudah pernah direcord untuk vendor ini. Harap gunakan DO / Vendor SN yang unik.'
                })
            
        return attrs

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        receipt_report = ReceiptReport.objects.create(**validated_data)
        
        for item_data in items_data:
            bins_data = item_data.pop('bins', [])
            rr_item = ReceiptReportItem.objects.create(receipt_report=receipt_report, **item_data)
            
            for bin_data in bins_data:
                ItemBinAllocation.objects.create(
                    reference_number=receipt_report.receipt_number,
                    document_type='RECEIPT_REPORT',
                    item=rr_item.item,
                    bin_id=bin_data.get('bin'),
                    qty=bin_data.get('qty')
                )
            
        return receipt_report

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if items_data is not None:
            instance.items.all().delete()
            ItemBinAllocation.objects.filter(
                reference_number=instance.receipt_number,
                document_type='RECEIPT_REPORT'
            ).delete()
            for item_data in items_data:
                bins_data = item_data.pop('bins', [])
                rr_item = ReceiptReportItem.objects.create(receipt_report=instance, **item_data)
                for bin_data in bins_data:
                    ItemBinAllocation.objects.create(
                        reference_number=instance.receipt_number,
                        document_type='RECEIPT_REPORT',
                        item=rr_item.item,
                        bin_id=bin_data.get('bin'),
                        qty=bin_data.get('qty')
                    )
                
        return instance
