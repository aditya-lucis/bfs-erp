from rest_framework import serializers
from apps.organization.models import Department, Position
from .models import BudgetComponent
from apps.inventory.models import Item
from apps.inventory.serializers import ItemListSerializer
from .models import TemplateRAPHeader, TemplateRAPDetail



class BudgetComponentSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    department_code = serializers.CharField(source='department.code', read_only=True)
    position_name   = serializers.CharField(source='position.name', read_only=True)
    position_code   = serializers.CharField(source='position.code', read_only=True)

    class Meta:
        model = BudgetComponent
        fields = [
            'id', 'name', 'component_type', 'custom_name',
            'cost_category', 'department', 'department_name', 'department_code',
            'position', 'position_name', 'position_code',
            'order_no', 'is_active', 'template_rap',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['name']


class BudgetComponentWriteSerializer(serializers.ModelSerializer):
    """
    Write serializer — validasi position harus dari department yang sama.
    """
    class Meta:
        model = BudgetComponent
        fields = [
            'id', 'component_type', 'custom_name', 'cost_category', 
            'department', 'position', 'order_no', 'is_active',
        ]

    def validate(self, data):
        dept = data.get('department')
        pos = data.get('position')
        c_type = data.get('component_type', 'standard')

        if c_type == 'standard':
            if not dept:
                raise serializers.ValidationError({
                    'department': 'Department is required for standard components.'
                })
        
        if pos and dept and pos.department_id != dept.id:
            raise serializers.ValidationError({
                'position': 'Position harus berasal dari Department yang dipilih.'
            })
        return data
        
class DepartmentPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ['id', 'code', 'name', 'department']

class TemplateRAPDetailSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    item_name = serializers.CharField(source='item.item_name', read_only=True)
    item_code = serializers.CharField(source='item.item_code', read_only=True)
    unit_name = serializers.CharField(source='item.unit.unit_name', read_only=True)
    unit_price = serializers.DecimalField(source='item.unit_price', read_only=True, max_digits=18, decimal_places=2, allow_null=True)
    # parent harus return ID (integer) bukan object
    parent = serializers.IntegerField(source='parent_id', read_only=True, allow_null=True)

    class Meta:
        model = TemplateRAPDetail
        fields = [
            'id', 'template', 'parent', 'item_type',
            'description', 'item', 'item_name', 'item_code', 'unit_name', 'unit_price',
            'remarks', 'order_no', 'display_number',
            'children', 'created_at',
        ]

    def get_children(self, obj):
        # Jangan return children di sini — frontend yang handle tree build
        # Atau kalau mau, bisa tapi hati-hati infinite recursion
        return []

class TemplateRAPDetailWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateRAPDetail
        fields = [
            'id', 'template', 'parent', 'item_type',
            'description', 'item', 'remarks', 'order_no',
        ]

    def validate(self, data):
        item_type = data.get('item_type')
        item = data.get('item')

        # Item type 'item' must have item FK
        if item_type == 'item' and not item:
            raise serializers.ValidationError({
                'item': 'Item harus dipilih untuk tipe Item.'
            })

        # Header/Sub Header should NOT have item
        if item_type in ('header', 'sub_header') and item:
            raise serializers.ValidationError({
                'item': 'Header/Sub Header tidak boleh memiliki Item.'
            })

        # Parent validation
        parent = data.get('parent')
        if parent:
            if parent.template != data.get('template'):
                raise serializers.ValidationError({
                    'parent': 'Parent harus dari template yang sama.'
                })
            # Validate hierarchy depth (max 3 levels: header → sub_header → item)
            depth = 1
            current = parent
            while current.parent:
                depth += 1
                current = current.parent
            if depth >= 3:
                raise serializers.ValidationError({
                    'parent': 'Maksimal 3 level: Header → Sub Header → Item.'
                })
            # Item cannot have children
            if parent.item_type == 'item':
                raise serializers.ValidationError({
                    'parent': 'Item tidak boleh memiliki child.'
                })

        return data


class TemplateRAPSerializer(serializers.ModelSerializer):
    details = TemplateRAPDetailSerializer(many=True, read_only=True)
    budget_component_name = serializers.CharField(source='budget_component.name', read_only=True)

    class Meta:
        model = TemplateRAPHeader
        fields = [
            'id', 'budget_component', 'budget_component_name',
            'template_name', 'is_active', 'details',
            'created_at', 'updated_at',
        ]


class TemplateRAPWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateRAPHeader
        fields = ['id', 'budget_component', 'template_name', 'is_active']