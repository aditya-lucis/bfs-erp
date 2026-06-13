from django.contrib import admin
from .models import BudgetComponent


@admin.register(BudgetComponent)
class BudgetComponentAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'cost_category',
        'department',
        'position',
        'order_no',
        'is_active',
        'template_rap',
        'created_at',
    ]
    list_filter = [
        'cost_category',
        'is_active',
        'template_rap',
        'department',
        'created_at',
    ]
    search_fields = [
        'name',
        'department__name',
        'position__name',
    ]
    readonly_fields = ['name', 'created_at', 'updated_at']
    list_editable = ['order_no', 'is_active']
    ordering = ['order_no', 'id']

    fieldsets = (
        ('Component Info', {
            'fields': ('name', 'cost_category', 'order_no', 'is_active', 'template_rap')
        }),
        ('Organization', {
            'fields': ('department', 'position')
        }),
        ('System', {
            'fields': ('company', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('department', 'position', 'company')