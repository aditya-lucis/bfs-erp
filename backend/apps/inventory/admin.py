from django.contrib import admin
from .models import UnitMeasurement, ItemCategory, Item, ItemAccountLink


@admin.register(UnitMeasurement)
class UnitMeasurementAdmin(admin.ModelAdmin):
    list_display  = ['unit_name', 'unit_description', 'item_type', 'is_active']
    list_filter   = ['item_type', 'is_active']
    search_fields = ['unit_name']


@admin.register(ItemCategory)
class ItemCategoryAdmin(admin.ModelAdmin):
    list_display  = ['name', 'item_type', 'description', 'is_active']
    list_filter   = ['item_type', 'is_active']
    search_fields = ['name']


class ItemAccountLinkInline(admin.TabularInline):
    model  = ItemAccountLink
    extra  = 0
    fields = ['purpose', 'currency', 'account']


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display  = ['item_code', 'item_name', 'item_type', 'category', 'unit', 'unit_price', 'is_active']
    list_filter   = ['item_type', 'is_active', 'is_service', 'is_new', 'costing_method']
    search_fields = ['item_code', 'item_name']
    readonly_fields = ['item_code', 'created_at', 'updated_at', 'created_by']
    inlines       = [ItemAccountLinkInline]