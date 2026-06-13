from django.contrib import admin
from .models import AnnualBudgetHeader, AnnualBudgetLine, AnnualBudgetLog


class AnnualBudgetLineInline(admin.TabularInline):
    model  = AnnualBudgetLine
    extra  = 0
    fields = ['cost_category', 'order_no',
              'jan', 'feb', 'mar', 'apr', 'may', 'jun',
              'jul', 'aug', 'sep', 'oct', 'nov', 'dec']


@admin.register(AnnualBudgetHeader)
class AnnualBudgetHeaderAdmin(admin.ModelAdmin):
    list_display  = ['__str__', 'year', 'department', 'is_locked', 'created_at']
    list_filter   = ['year', 'is_locked']
    search_fields = ['department__name']
    inlines       = [AnnualBudgetLineInline]


@admin.register(AnnualBudgetLine)
class AnnualBudgetLineAdmin(admin.ModelAdmin):
    list_display  = ['__str__', 'header', 'cost_category', 'order_no']
    list_filter   = ['header__year']
    search_fields = ['cost_category']


@admin.register(AnnualBudgetLog)
class AnnualBudgetLogAdmin(admin.ModelAdmin):
    list_display  = ['line', 'month', 'old_value', 'new_value', 'changed_by', 'changed_at']
    list_filter   = ['month', 'changed_at']
    readonly_fields = ['line', 'month', 'old_value', 'new_value', 'changed_by', 'changed_at']
