from django.contrib import admin
from .models import (
    Vendor, VendorTerms, VendorLinkedAccount, VendorContactPerson,
    PurchaseRequisition, PurchaseRequisitionDetail,
    PurchaseOrder, PurchaseOrderDetail, PurchaseOrderPaymentTerm
)

class VendorTermsInline(admin.TabularInline):
    model = VendorTerms
    extra = 0

class VendorLinkedAccountInline(admin.TabularInline):
    model = VendorLinkedAccount
    extra = 0

class VendorContactPersonInline(admin.TabularInline):
    model = VendorContactPerson
    extra = 0

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'status', 'is_sister_company')
    search_fields = ('code', 'name')
    list_filter = ('status', 'is_sister_company')
    inlines = [
        VendorTermsInline, 
        VendorLinkedAccountInline, VendorContactPersonInline
    ]

class PurchaseRequisitionDetailInline(admin.TabularInline):
    model = PurchaseRequisitionDetail
    extra = 0

@admin.register(PurchaseRequisition)
class PurchaseRequisitionAdmin(admin.ModelAdmin):
    list_display = ('pr_number', 'pr_date', 'document_status', 'approval_status', 'company', 'department', 'total_amount')
    search_fields = ('pr_number',)
    list_filter = ('document_status', 'approval_status', 'pr_type')
    inlines = [PurchaseRequisitionDetailInline]

class PurchaseOrderDetailInline(admin.TabularInline):
    model = PurchaseOrderDetail
    extra = 0

class PurchaseOrderPaymentTermInline(admin.TabularInline):
    model = PurchaseOrderPaymentTerm
    extra = 0

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('po_number', 'po_date', 'vendor', 'document_status', 'approval_status', 'grand_total')
    search_fields = ('po_number', 'vendor__name')
    list_filter = ('document_status', 'approval_status', 'po_type')
    inlines = [PurchaseOrderDetailInline, PurchaseOrderPaymentTermInline]
