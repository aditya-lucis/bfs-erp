from django.contrib import admin

from apps.organization.models import Company, Department, Employee, Position

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['company_code', 'company_name', 'currency_id', 'is_active']

class DepartmentInline(admin.TabularInline):
    model = Department
    extra = 0
    fields = ['code', 'name', 'parent', 'order', 'is_active']
    fk_name = 'parent'

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display  = ['code', 'name', 'parent', 'level', 'is_active']
    list_filter   = ['company', 'is_active']
    search_fields = ['code', 'name']

class PositionInline(admin.TabularInline):
    model = Position
    extra = 0
    fields = ['code', 'name', 'is_active']

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display  = ['code', 'name', 'department', 'is_active']
    list_filter   = ['department', 'is_active']
    search_fields = ['code', 'name']
    inlines       = []

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display  = ['employee_id', 'full_name', 'position', 'status', 'user']
    list_filter   = ['status', 'position__department']
    search_fields = ['employee_id', 'full_name', 'email']
    raw_id_fields = ['user']