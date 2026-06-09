from django.contrib import admin
from .models import (
    CustomerCategory,
    CustomerGroup,
    Customer,
    CustomerLinkedAccount,
    CustomerTerms,
    CustomerContactPerson,
)


@admin.register(CustomerCategory)
class CustomerCategoryAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')
    ordering = ('code',)


@admin.register(CustomerGroup)
class CustomerGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


class CustomerLinkedAccountInline(admin.TabularInline):
    model = CustomerLinkedAccount
    extra = 0
    fields = ('account_type', 'currency_scope', 'account')


class CustomerTermsInline(admin.StackedInline):
    model = CustomerTerms
    extra = 0
    can_delete = False


class CustomerContactPersonInline(admin.TabularInline):
    model = CustomerContactPerson
    extra = 0
    fields = ('name', 'email', 'home_phone', 'home_address')


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'name', 'city', 'phone_1', 'currency', 'status', 'created_at')
    list_filter = ('status', 'currency', 'area_code', 'is_kawasan_berikat', 'is_sister_company')
    search_fields = ('code', 'name', 'email', 'phone_1', 'city')
    readonly_fields = ('code', 'created_at', 'updated_at')
    ordering = ('code',)
    inlines = [CustomerTermsInline, CustomerLinkedAccountInline, CustomerContactPersonInline]

    fieldsets = (
        ('Identity', {
            'fields': ('code', 'company', 'title', 'name', 'category', 'tax_number', 'nppkp'),
        }),
        ('Contact', {
            'fields': (
                'email', 'website',
                'address_1', 'address_2',
                'country', 'state', 'city', 'zip_code', 'area_code',
                'phone_1', 'phone_2', 'fax',
            ),
        }),
        ('Financial', {
            'fields': (
                'currency', 'default_price_group',
                'tolerance_difference', 'deposit', 'credit_limit',
            ),
        }),
        ('Flags', {
            'fields': (
                'is_kawasan_berikat', 'is_sister_company',
                'item_type_asset', 'item_type_fg', 'item_type_rm',
                'item_type_supplies', 'item_type_wip',
            ),
        }),
        ('Relations & Status', {
            'fields': ('group', 'status'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )