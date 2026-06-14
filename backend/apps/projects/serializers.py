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


