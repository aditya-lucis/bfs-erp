from django.contrib import admin
from .models import ApprovalMatrix, ApprovalMatrixRange, ApprovalMatrixStep


class ApprovalMatrixStepInline(admin.TabularInline):
    model = ApprovalMatrixStep
    extra = 0


class ApprovalMatrixRangeInline(admin.TabularInline):
    model = ApprovalMatrixRange
    extra = 0
    show_change_link = True


@admin.register(ApprovalMatrix)
class ApprovalMatrixAdmin(admin.ModelAdmin):
    list_display = ['document_code', 'creator_position', 'basis', 'is_active', 'company']
    list_filter = ['document_code', 'basis', 'is_active']
    inlines = [ApprovalMatrixRangeInline]


@admin.register(ApprovalMatrixRange)
class ApprovalMatrixRangeAdmin(admin.ModelAdmin):
    list_display = ['matrix', 'from_value', 'to_value', 'order_no']
    inlines = [ApprovalMatrixStepInline]
