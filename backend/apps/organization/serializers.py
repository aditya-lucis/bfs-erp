from rest_framework import serializers
from .models import Company, Department, Position, Employee

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Company
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class DepartmentSerializer(serializers.ModelSerializer):
    level       = serializers.SerializerMethodField()
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    children    = serializers.SerializerMethodField()

    class Meta:
        model  = Department
        fields = ['id', 'code', 'name', 'parent', 'parent_name',
                  'order', 'level', 'is_active', 'children']
        
    def get_level(self, obj):
        return obj.level
        
    def get_children(self, obj):
        kids = obj.children.filter(is_active=True).order_by('order')
        return DepartmentSerializer(kids, many=True).data

class PositionSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    employee_count  = serializers.SerializerMethodField()

    class Meta:
        model  = Position
        fields = ['id', 'code', 'name', 'description',
                  'department', 'department_name', 'is_active', 'employee_count']

    def get_employee_count(self, obj):
        return obj.employees.filter(status='active').count()
    
class EmployeeSerializer(serializers.ModelSerializer):
    position_name   = serializers.CharField(source='position.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    username        = serializers.CharField(source='user.username', read_only=True, default=None)

    class Meta:
        model  = Employee
        fields = [
            'id', 'employee_id', 'full_name', 'email', 'phone',
            'position', 'position_name', 'department_name',
            'status', 'join_date', 'user', 'username',
            'created_at',
        ]
        read_only_fields = ['created_at']