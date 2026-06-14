from rest_framework import serializers
from .models import RAPType, Project, ProjectType, ProjectCategory

class RAPTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RAPType
        fields = ['id', 'name', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProjectTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectType
        fields = ['id', 'name', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProjectCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectCategory
        fields = ['id', 'code', 'name', 'pattern_group_name', 'document_pattern', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProjectListSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    project_manager_name = serializers.SerializerMethodField()
    project_type_name = serializers.CharField(source='project_type.name', read_only=True)
    project_category_name = serializers.CharField(source='project_category.name', read_only=True)

    class Meta:
        model = Project
        fields = '__all__'

    def get_project_manager_name(self, obj):
        emp = obj.project_manager
        if emp:
            # Check position name safely
            pos_name = emp.position.name if emp.position else ""
            return f"{emp.full_name} sebagai {pos_name}"
        return ""


class ProjectWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        exclude = ['company', 'project_code', 'is_active']


# ─── RAP Serializers ──────────────────────────────────────────────────────────

from .models import RAP, RAPDetail

class RAPDetailSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.item_name', read_only=True)
    item_code = serializers.CharField(source='item.item_code', read_only=True)
    unit_name = serializers.CharField(source='item.unit.unit_name', read_only=True)
    parent = serializers.IntegerField(source='parent_id', read_only=True, allow_null=True)

    class Meta:
        model = RAPDetail
        fields = [
            'id', 'parent', 'item_type',
            'description', 'item', 'item_name', 'item_code', 'unit_name',
            'remarks', 'volume', 'unit_price', 'total_cost',
            'order_no', 'display_number',
        ]


class RAPSerializer(serializers.ModelSerializer):
    details = RAPDetailSerializer(many=True, read_only=True)
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    project_code = serializers.CharField(source='project.project_code', read_only=True)
    rap_type_name = serializers.CharField(source='rap_type.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    position_name = serializers.CharField(source='position.name', read_only=True)
    budget_component_name = serializers.CharField(source='budget_component.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = RAP
        fields = [
            'id', 'company', 'rap_number', 'rap_type', 'rap_type_name',
            'rap_date', 'month_period', 'year_period', 'cost_category',
            'department', 'department_name', 'position', 'position_name',
            'budget_component', 'budget_component_name', 'activity',
            'project', 'project_name', 'project_code',
            'is_active', 'document_status', 'approval_status',
            'total_cost', 'details', 'created_at', 'updated_at', 'created_by_name'
        ]
        read_only_fields = ['id', 'company', 'rap_number', 'total_cost', 'created_at', 'updated_at', 'created_by_name']

    def create(self, validated_data):
        request = self.context.get('request')
        details_data = request.data.get('details', []) if request else []
        
        from django.db import transaction
        with transaction.atomic():
            rap = RAP.objects.create(**validated_data)
            
            saved_details = {}
            for d in details_data:
                temp_id = d.get('temp_id')
                parent_temp_id = d.get('parent_temp_id')
                
                parent_obj = None
                if parent_temp_id and parent_temp_id in saved_details:
                    parent_obj = saved_details[parent_temp_id]
                
                item_id = d.get('item')
                
                detail = RAPDetail.objects.create(
                    rap=rap,
                    parent=parent_obj,
                    item_type=d.get('item_type'),
                    description=d.get('description', ''),
                    item_id=item_id,
                    remarks=d.get('remarks', ''),
                    volume=d.get('volume', 0.00),
                    unit_price=d.get('unit_price', 0.00),
                    total_cost=d.get('total_cost', 0.00),
                    order_no=d.get('order_no', 0)
                )
                
                if temp_id is not None:
                    saved_details[temp_id] = detail
            
            # Calculate total_cost on RAP by summing only item-type details
            rap.total_cost = sum(d.total_cost for d in rap.details.filter(item_type='item'))
            rap.save()
            
            return rap

    def update(self, instance, validated_data):
        request = self.context.get('request')
        details_data = request.data.get('details', []) if request else []
        
        from django.db import transaction
        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            
            instance.details.all().delete()
            
            saved_details = {}
            for d in details_data:
                temp_id = d.get('temp_id')
                parent_temp_id = d.get('parent_temp_id')
                
                parent_obj = None
                if parent_temp_id and parent_temp_id in saved_details:
                    parent_obj = saved_details[parent_temp_id]
                
                item_id = d.get('item')
                
                detail = RAPDetail.objects.create(
                    rap=instance,
                    parent=parent_obj,
                    item_type=d.get('item_type'),
                    description=d.get('description', ''),
                    item_id=item_id,
                    remarks=d.get('remarks', ''),
                    volume=d.get('volume', 0.00),
                    unit_price=d.get('unit_price', 0.00),
                    total_cost=d.get('total_cost', 0.00),
                    order_no=d.get('order_no', 0)
                )
                
                if temp_id is not None:
                    saved_details[temp_id] = detail
            
            instance.total_cost = sum(d.total_cost for d in instance.details.filter(item_type='item'))
            instance.save()
            
            return instance



