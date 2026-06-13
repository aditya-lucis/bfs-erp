"""
BFS ERP — Accounting: Django Admin Registration
Covers: AccountGroup, Account (COA), AnnualPeriod, QuarterPeriod,
        MonthlyPeriod, AccountingPeriod, PeriodActivityLog
"""
from django.contrib import admin
from django.utils.html import format_html

from .models import AccountingPeriod
from .models import (
    AnnualPeriod, QuarterPeriod, MonthlyPeriod,
    AccountingPeriod, PeriodActivityLog,
)

@admin.register(AnnualPeriod)
class AnnualPeriodAdmin(admin.ModelAdmin):
    list_display    = ['year', 'status_badge', 'quarter_summary', 'company', 'created_at', 'created_by']
    list_filter     = ['status', 'company']
    search_fields   = ['year']
    ordering        = ['-year']
    readonly_fields = ['created_at', 'updated_at', 'created_by']

    fieldsets = (
        ('Period', {
            'fields': ('company', 'year', 'status'),
        }),
        ('Audit', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Status')
    def status_badge(self, obj):
        color = '#16a34a' if obj.status == 'OPEN' else '#dc2626'
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;border-radius:20px;font-size:11px;font-weight:600">{}</span>',
            color, obj.status,
        )

    @admin.display(description='Quarters')
    def quarter_summary(self, obj):
        quarters = obj.quarters.order_by('quarter')
        parts = []
        for q in quarters:
            color = '#16a34a' if q.status == 'OPEN' else '#dc2626'
            parts.append(
                f'<span style="color:{color};font-weight:600">Q{q.quarter}:{q.status}</span>'
            )
        return format_html(' | '.join(parts)) if parts else '-'


@admin.register(QuarterPeriod)
class QuarterPeriodAdmin(admin.ModelAdmin):
    list_display    = ['year', 'quarter_label', 'status_badge', 'annual_period', 'company', 'created_at']
    list_filter     = ['status', 'year', 'quarter', 'company']
    search_fields   = ['year']
    ordering        = ['-year', 'quarter']
    readonly_fields = ['created_at', 'updated_at', 'created_by']

    fieldsets = (
        ('Period', {
            'fields': ('company', 'annual_period', 'year', 'quarter', 'status'),
        }),
        ('Audit', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Quarter')
    def quarter_label(self, obj):
        return f'Q{obj.quarter}'

    @admin.display(description='Status')
    def status_badge(self, obj):
        color = '#16a34a' if obj.status == 'OPEN' else '#dc2626'
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;border-radius:20px;font-size:11px;font-weight:600">{}</span>',
            color, obj.status,
        )


@admin.register(MonthlyPeriod)
class MonthlyPeriodAdmin(admin.ModelAdmin):
    list_display    = ['year', 'month_name', 'status_badge', 'quarter_period', 'company', 'created_at']
    list_filter     = ['status', 'year', 'month', 'company']
    search_fields   = ['year']
    ordering        = ['-year', 'month']
    readonly_fields = ['created_at', 'updated_at', 'created_by']

    fieldsets = (
        ('Period', {
            'fields': ('company', 'annual_period', 'quarter_period', 'year', 'month', 'status'),
        }),
        ('Audit', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Month')
    def month_name(self, obj):
        return obj.month_name

    @admin.display(description='Status')
    def status_badge(self, obj):
        color = '#16a34a' if obj.status == 'OPEN' else '#dc2626'
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;border-radius:20px;font-size:11px;font-weight:600">{}</span>',
            color, obj.status,
        )


@admin.register(AccountingPeriod)
class AccountingPeriodAdmin(admin.ModelAdmin):
    list_display    = [
        'year', 'month_name', 'start_date', 'end_date',
        'status_badge', 'is_closed_display', 'company',
    ]
    list_filter     = ['status', 'year', 'month', 'company']
    search_fields   = ['year']
    ordering        = ['-year', '-month']
    readonly_fields = ['created_at', 'updated_at', 'created_by']

    fieldsets = (
        ('Period', {
            'fields': ('company', 'monthly_period', 'year', 'month', 'start_date', 'end_date', 'status'),
        }),
        ('Audit', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Month')
    def month_name(self, obj):
        return obj.month_name

    @admin.display(description='Status')
    def status_badge(self, obj):
        color = '#16a34a' if obj.status == 'OPEN' else '#dc2626'
        label = 'No (Open)' if obj.status == 'OPEN' else 'Yes (Closed)'
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;border-radius:20px;font-size:11px;font-weight:600">{}</span>',
            color, label,
        )

    @admin.display(boolean=True, description='Is Closed')
    def is_closed_display(self, obj):
        return obj.is_closed


@admin.register(PeriodActivityLog)
class PeriodActivityLogAdmin(admin.ModelAdmin):
    list_display  = [
        'period_type', 'period_label', 'action_badge',
        'reason_short', 'actioned_by', 'actioned_at',
    ]
    list_filter   = ['period_type', 'action', 'company']
    search_fields = ['period_label', 'reason', 'actioned_by__username']
    ordering      = ['-actioned_at']
    readonly_fields = [
        'company', 'period_type', 'period_label',
        'action', 'reason', 'period_status_after',
        'actioned_by', 'actioned_at',
        'annual_period', 'quarter_period',
        'monthly_period', 'accounting_period',
    ]
    date_hierarchy = 'actioned_at'

    fieldsets = (
        ('Log Detail', {
            'fields': (
                'company', 'period_type', 'period_label',
                'action', 'period_status_after', 'reason',
            ),
        }),
        ('References', {
            'fields': (
                'annual_period', 'quarter_period',
                'monthly_period', 'accounting_period',
            ),
            'classes': ('collapse',),
        }),
        ('Who & When', {
            'fields': ('actioned_by', 'actioned_at'),
        }),
    )

    @admin.display(description='Action')
    def action_badge(self, obj):
        color = '#16a34a' if obj.action == 'OPEN' else '#dc2626'
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;border-radius:20px;font-size:11px;font-weight:600">{}</span>',
            color, obj.action,
        )

    @admin.display(description='Reason')
    def reason_short(self, obj):
        return obj.reason[:60] + '...' if len(obj.reason) > 60 else obj.reason

    # Immutable log — no add/change/delete
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False