"""
BFS ERP — Inventory: Unit Measurement, Item Category, Item

Struktur:
    UnitMeasurement  — satuan item, berlaku untuk RM dan/atau SP
    ItemCategory     — directory item (flat, uppercase + underscore only)
                       dipisah by item_type: RM | SP
    Item             — master item, relasi ke UnitMeasurement, ItemCategory, Account (COA)
    ItemAccountLink  — relasi item ke COA per tracking purpose
"""

import os
import re
from datetime import date

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


# ─── Choices ──────────────────────────────────────────────────────────────────

class ItemType(models.TextChoices):
    RAW_MATERIAL = 'RM', 'Raw Material'
    SUPPLIES     = 'SP', 'Supplies'


class CostingMethod(models.TextChoices):
    FIFO    = 'FIFO', 'First In First Out (FIFO)'
    FEFO    = 'FEFO', 'First Expired, First Out (FEFO)'
    LIFO    = 'LIFO', 'Last In First Out (LIFO)'
    AVERAGE = 'AVG',  'Weighted Average'


class PriceType(models.TextChoices):
    FIXED       = 'FIXED',       'Fixed'
    EDITABLE    = 'EDITABLE',    'Editable'
    USER_DEFINED = 'USER_DEFINED', 'User-Defined'


class AccountPurpose(models.TextChoices):
    PURCHASE          = 'PURCHASE',          'Account for tracking purchase'
    PURCHASE_DISCOUNT = 'PURCHASE_DISCOUNT', 'Account for tracking purchase discount'
    PURCHASE_RETURN   = 'PURCHASE_RETURN',   'Account for tracking purchase return'
    WIP               = 'WIP',               'Account for tracking WIP'
    UNBILL_REVENUE    = 'UNBILL_REVENUE',     'Account for tracking unbill revenue'
    SALES             = 'SALES',             'Account for tracking sales'
    SALES_DISCOUNT    = 'SALES_DISCOUNT',    'Account for tracking sales discount'
    SALES_RETURN      = 'SALES_RETURN',      'Account for tracking sales return'
    INVENTORY         = 'INVENTORY',         'Account for tracking inventory'


# ─── Validators ───────────────────────────────────────────────────────────────

def validate_directory_name(value):
    """
    Hanya boleh huruf kapital, angka, dan underscore.
    Tidak boleh diawali/diakhiri underscore.
    Tidak boleh spasi atau simbol lain.
    """
    if not re.match(r'^[A-Z0-9][A-Z0-9_]*[A-Z0-9]$|^[A-Z0-9]$', value):
        raise ValidationError(
            'Nama directory hanya boleh mengandung huruf kapital (A-Z), '
            'angka (0-9), dan underscore (_). '
            'Tidak boleh diawali atau diakhiri dengan underscore. '
            'Contoh: BHP_MEDIS, CAPEX_ALL'
        )


def validate_item_code(value):
    """Kode item: hanya huruf, angka, underscore."""
    if not re.match(r'^[A-Z0-9_]+$', value):
        raise ValidationError(
            'Kode item hanya boleh mengandung huruf kapital, angka, dan underscore.'
        )


def item_image_upload_path(instance, filename):
    """Upload path: media/items/{item_type}/{item_code}/{filename}"""
    ext      = os.path.splitext(filename)[1].lower()
    new_name = f"{instance.item_code}{ext}"
    return os.path.join('items', instance.item_type, instance.item_code, new_name)


# ─── Unit Measurement ─────────────────────────────────────────────────────────

class UnitMeasurement(models.Model):
    """
    Satuan item. Satu unit bisa berlaku untuk RM, SP, atau keduanya.
    Contoh: Pcs (RM), Pcs (SP) — bisa sama nama beda record per type,
    atau satu record berlaku untuk keduanya (is_rm + is_sp).
    Dari Excel: setiap row punya ItemCategoryType (RM/SP),
    jadi kita simpan per-type agar fleksibel.
    """
    unit_name        = models.CharField(max_length=50)
    unit_description = models.CharField(max_length=100, blank=True)
    item_type        = models.CharField(
                           max_length=2,
                           choices=ItemType.choices,
                           help_text='RM = Raw Material, SP = Supplies',
                       )
    is_active        = models.BooleanField(default=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)
    created_by       = models.ForeignKey(
                           settings.AUTH_USER_MODEL,
                           null=True, blank=True,
                           on_delete=models.SET_NULL,
                           related_name='created_units',
                       )

    class Meta:
        db_table        = 'inv_unit_measurement'
        # Satu unit_name bisa ada di RM dan SP sekaligus, tapi unik per type
        unique_together = ('unit_name', 'item_type')
        ordering        = ['item_type', 'unit_name']
        verbose_name    = 'Unit Measurement'
        verbose_name_plural = 'Unit Measurements'

    def __str__(self):
        return f"{self.unit_name} ({self.item_type})"


# ─── Item Category (Directory) ────────────────────────────────────────────────

class ItemCategory(models.Model):
    """
    Directory untuk grouping item. Flat (tidak nested).
    Nama = kode directory: uppercase + underscore only.
    Dipisah by item_type: RM atau SP.

    Kode item akan menggunakan nama directory ini sebagai bagian dari prefix.
    Contoh: directory 'BHP_MEDIS' → item code '2026_BHP_MEDIS_0001'
    """
    name        = models.CharField(
                      max_length=100,
                      validators=[validate_directory_name],
                      help_text='Uppercase + underscore only. Contoh: BHP_MEDIS',
                  )
    description = models.CharField(max_length=200, blank=True)
    item_type   = models.CharField(
                      max_length=2,
                      choices=ItemType.choices,
                  )
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    created_by  = models.ForeignKey(
                      settings.AUTH_USER_MODEL,
                      null=True, blank=True,
                      on_delete=models.SET_NULL,
                      related_name='created_item_categories',
                  )

    class Meta:
        db_table        = 'inv_item_category'
        unique_together = ('name', 'item_type')
        ordering        = ['item_type', 'name']
        verbose_name    = 'Item Category'
        verbose_name_plural = 'Item Categories'

    def __str__(self):
        return f"[{self.item_type}] {self.name}"


# ─── Item ─────────────────────────────────────────────────────────────────────

class Item(models.Model):
    """
    Master Item.

    Kode item di-generate otomatis:
        {YEAR}_{CATEGORY_NAME}_{INCREMENT:04d}
        Contoh: 2026_BHP_MEDIS_0162

    Increment adalah sequence per category (bukan global).
    """
    # ── Identity ──────────────────────────────────────────────────────────────
    item_code    = models.CharField(
                       max_length=100,
                       unique=True,
                       editable=False,       # read-only, auto-generated
                       validators=[validate_item_code],
                   )
    item_name    = models.CharField(max_length=500)
    item_type    = models.CharField(max_length=2, choices=ItemType.choices)
    category     = models.ForeignKey(
                       ItemCategory,
                       on_delete=models.PROTECT,
                       related_name='items',
                   )

    # ── Units ─────────────────────────────────────────────────────────────────
    unit                    = models.ForeignKey(
                                  UnitMeasurement,
                                  on_delete=models.PROTECT,
                                  related_name='items_main',
                                  verbose_name='Item Unit',
                              )
    secondary_rr_unit       = models.ForeignKey(
                                  UnitMeasurement,
                                  on_delete=models.PROTECT,
                                  related_name='items_rr',
                                  verbose_name='Secondary RR Unit',
                              )
    secondary_sndo_unit     = models.ForeignKey(
                                  UnitMeasurement,
                                  on_delete=models.PROTECT,
                                  related_name='items_sndo',
                                  verbose_name='Secondary SN/DO Unit',
                              )
    secondary_production_unit = models.ForeignKey(
                                  UnitMeasurement,
                                  on_delete=models.PROTECT,
                                  related_name='items_production',
                                  verbose_name='Secondary Production Unit',
                              )

    # ── Source ────────────────────────────────────────────────────────────────
    is_production = models.BooleanField(default=False, verbose_name='Production')
    is_purchase   = models.BooleanField(default=True,  verbose_name='Purchase')

    # ── Pricing ───────────────────────────────────────────────────────────────
    price_type          = models.CharField(
                              max_length=15,
                              choices=PriceType.choices,
                              default=PriceType.EDITABLE,
                          )
    unit_price          = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    is_last_purchase_price = models.BooleanField(
                              default=False,
                              verbose_name='Use Last Purchase Price',
                          )

    # ── Inventory settings ────────────────────────────────────────────────────
    costing_method   = models.CharField(
                           max_length=10,
                           choices=CostingMethod.choices,
                           default=CostingMethod.FIFO,
                       )
    default_currency = models.CharField(max_length=10, default='IDR')
    is_automatic_pr  = models.BooleanField(default=False, verbose_name='Is Automatic PR')

    # ── View Category ─────────────────────────────────────────────────────────
    view_buy       = models.BooleanField(default=True)
    view_sell      = models.BooleanField(default=True)
    view_inventory = models.BooleanField(default=False)

    # ── Status ────────────────────────────────────────────────────────────────
    is_active  = models.BooleanField(default=True)
    is_service = models.BooleanField(default=False)
    is_new     = models.BooleanField(default=True)

    # ── Image ─────────────────────────────────────────────────────────────────
    image = models.ImageField(
                upload_to=item_image_upload_path,
                null=True, blank=True,
            )

    # ── Audit ─────────────────────────────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
                     settings.AUTH_USER_MODEL,
                     null=True, blank=True,
                     on_delete=models.SET_NULL,
                     related_name='created_items',
                 )

    class Meta:
        db_table    = 'inv_item'
        ordering    = ['item_code']
        verbose_name = 'Item'
        verbose_name_plural = 'Items'

    def __str__(self):
        return f"{self.item_code} — {self.item_name}"

    # ── Auto-generate item_code ───────────────────────────────────────────────

    @classmethod
    def generate_item_code(cls, category):
        """
        Generate kode item unik:
            {YEAR}_{CATEGORY_NAME}_{INCREMENT:04d}
        Increment adalah sequence per category — cari yang terbesar lalu +1.
        """
        year   = date.today().year
        prefix = f"{year}_{category.name}_"

        # Ambil semua kode yang sudah ada dengan prefix ini, urutkan descending
        last = (
            cls.objects
            .filter(item_code__startswith=prefix)
            .order_by('-item_code')
            .values_list('item_code', flat=True)
            .first()
        )

        if last:
            # Ambil bagian increment (4 digit terakhir setelah prefix)
            try:
                last_num = int(last[len(prefix):])
            except ValueError:
                last_num = 0
            next_num = last_num + 1
        else:
            next_num = 1

        return f"{prefix}{next_num:04d}"

    def save(self, *args, **kwargs):
        # Auto-generate item_code hanya saat create (belum punya PK)
        if not self.pk:
            self.item_code = Item.generate_item_code(self.category)
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        # item_type harus sama dengan category item_type
        if self.category_id and self.item_type != self.category.item_type:
            raise ValidationError({
                'category': f'Category bertipe {self.category.item_type}, '
                            f'tapi item bertipe {self.item_type}.'
            })

        # Minimal satu source harus dipilih
        if not self.is_production and not self.is_purchase:
            raise ValidationError(
                'Item harus memiliki minimal satu source: Production atau Purchase.'
            )


# ─── Item Account Link (COA) ──────────────────────────────────────────────────

class ItemAccountLink(models.Model):
    """
    Relasi item ke COA per tujuan tracking.
    Satu item bisa punya banyak account link (purchase, sales, WIP, dll).
    Currency per link bisa All, IDR, USD, EUR, atau SGD.
    """
    CURRENCY_CHOICES = [
        ('ALL', 'All Currency'),
        ('IDR', 'IDR'),
        ('USD', 'USD'),
        ('EUR', 'EUR'),
        ('SGD', 'SGD'),
    ]

    item     = models.ForeignKey(
                   Item,
                   on_delete=models.CASCADE,
                   related_name='account_links',
               )
    purpose  = models.CharField(
                   max_length=30,
                   choices=AccountPurpose.choices,
               )
    currency = models.CharField(
                   max_length=5,
                   choices=CURRENCY_CHOICES,
                   default='ALL',
               )
    account  = models.ForeignKey(
                   'accounting.Account',
                   on_delete=models.PROTECT,
                   related_name='item_links',
                   limit_choices_to={'is_active': True},
               )

    class Meta:
        db_table        = 'inv_item_account_link'
        unique_together = ('item', 'purpose', 'currency')
        verbose_name    = 'Item Account Link'
        verbose_name_plural = 'Item Account Links'

    def __str__(self):
        return f"{self.item.item_code} | {self.purpose} | {self.currency}"

# ─────────────────────────────────────────────────────────────────────────────
# Receipt Report
# ─────────────────────────────────────────────────────────────────────────────

class ReceiptReport(models.Model):
    class ReceiptType(models.TextChoices):
        PURCHASE = 'RR_PUR', 'Receipt Report For Purchase'
        SALES_RETURN = 'RR_SRT', 'Receipt Report For Sales Return'
        INTERNAL = 'RR_INT', 'Receipt Report For Internal'
        SERVICE_NOTE = 'RR_SRV', 'Receipt Report For Service Note'
        REPAIR = 'RR_REP', 'Receipt Report For Repair'

    class ApprovalStatus(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        AWAITING = 'awaiting', 'Awaiting'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Reject'
        REVISED = 'revised', 'Revised'
        VOID = 'void', 'Void'

    class DocumentStatus(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        READY_TO_PROCESS = 'ready_to_process', 'Ready to Process'
        CLOSE = 'close', 'Close'

    receipt_number = models.CharField(max_length=100, unique=True, editable=False)
    receipt_type = models.CharField(max_length=20, choices=ReceiptType.choices, default=ReceiptType.PURCHASE)
    
    # Core Relations
    company = models.ForeignKey('organization.Company', on_delete=models.CASCADE, related_name='receipt_reports', null=True)
    vendor = models.ForeignKey('purchase.Vendor', on_delete=models.PROTECT, related_name='receipt_reports', null=True, blank=True)
    po = models.ForeignKey('purchase.PurchaseOrder', on_delete=models.PROTECT, related_name='receipt_reports', null=True, blank=True)
    
    # Document Info
    receive_date = models.DateField()
    transport_with = models.CharField(max_length=255, blank=True, default='')
    vehicle_number = models.CharField(max_length=255, blank=True, default='')
    vendor_sn = models.CharField(max_length=100, blank=True, default='')
    vendor_sn_date = models.DateField(null=True, blank=True)
    memo = models.TextField(blank=True, default='')
    is_partial = models.BooleanField(default=False)
    
    # Tracking
    tracking_status = models.TextField(blank=True, default='')
    tracking_last_update = models.DateTimeField(null=True, blank=True)
    
    approval_status = models.CharField(max_length=50, choices=ApprovalStatus.choices, default=ApprovalStatus.DRAFT)
    document_status = models.CharField(max_length=50, choices=DocumentStatus.choices, default=DocumentStatus.DRAFT)
    
    # Void tracking fields
    void_reason = models.TextField(null=True, blank=True)
    void_date = models.DateTimeField(null=True, blank=True)
    void_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='voided_receipt_reports')
    
    # Auditing
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_receipt_reports')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_receipt_reports')

    class Meta:
        db_table = 'inv_receipt_report'
        ordering = ['-receive_date', '-id']

    def __str__(self):
        return self.receipt_number


class ReceiptReportItem(models.Model):
    receipt_report = models.ForeignKey(ReceiptReport, on_delete=models.CASCADE, related_name='items')
    po_item = models.ForeignKey('purchase.PurchaseOrderDetail', on_delete=models.PROTECT, null=True, blank=True, related_name='receipt_report_items')
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name='receipt_report_items')
    
    receive_qty = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    unit_type = models.ForeignKey('UnitMeasurement', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'inv_receipt_report_item'

    def __str__(self):
        return f"{self.receipt_report.receipt_number} - {self.item.item_name}"

class Warehouse(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'inv_warehouse'

    def __str__(self):
        return f"{self.code} - {self.name}"

class WarehouseBin(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='bins')
    bin_code = models.CharField(max_length=50)
    bin_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'inv_warehouse_bin'
        unique_together = ('warehouse', 'bin_code')

    def __str__(self):
        return f"{self.warehouse.code} / {self.bin_code}"

class ItemBinAllocation(models.Model):
    reference_number = models.CharField(max_length=50)
    document_type = models.CharField(max_length=50)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='bin_allocations')
    bin = models.ForeignKey(WarehouseBin, on_delete=models.PROTECT, related_name='allocations')
    qty = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)

    class Meta:
        db_table = 'inv_item_bin_allocation'

    def __str__(self):
        return f"{self.reference_number} | {self.item.item_code} -> {self.bin.bin_code}: {self.qty}"