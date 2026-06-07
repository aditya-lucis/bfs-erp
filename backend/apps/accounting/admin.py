"""
BFS ERP — Accounting: Django Admin Registration
"""
from django.contrib import admin
from .models import Account, AccountGroup


@admin.register(AccountGroup)
class AccountGroupAdmin(admin.ModelAdmin):
    list_display   = ['code', 'name', 'number_prefix', 'default_position', 'order', 'is_active', 'company']
    list_filter    = ['is_active', 'default_position', 'company']
    search_fields  = ['code', 'name', 'number_prefix']
    ordering       = ['order', 'code']
    readonly_fields = ['created_at', 'updated_at', 'created_by']

    fieldsets = (
        ('Identity', {
            'fields': ('company', 'code', 'name', 'number_prefix')
        }),
        ('Settings', {
            'fields': ('default_position', 'order', 'is_active')
        }),
        ('Audit', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display   = [
        'account_number', 'account_name', 'account_type',
        'account_group', 'parent', 'default_position',
        'currency', 'is_postable', 'is_linked', 'is_active',
    ]
    list_filter    = ['account_type', 'account_group', 'default_position', 'is_active', 'is_linked', 'company']
    search_fields  = ['account_number', 'account_name']
    ordering       = ['account_number']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'is_postable', 'level']
    raw_id_fields  = ['parent']

    fieldsets = (
        ('Identity', {
            'fields': ('company', 'account_group', 'parent', 'account_number', 'account_name', 'account_type')
        }),
        ('Settings', {
            'fields': ('language', 'default_position', 'currency')
        }),
        ('Flags', {
            'fields': ('is_inter_company', 'is_cost_component', 'is_on_duty', 'is_linked', 'is_active')
        }),
        ('Bank', {
            'fields': ('bank_type',),
            'classes': ('collapse',),
        }),
        ('Computed', {
            'fields': ('is_postable', 'level'),
            'classes': ('collapse',),
        }),
        ('Audit', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def is_postable(self, obj):
        return obj.is_postable
    is_postable.boolean = True
    is_postable.short_description = 'Postable'