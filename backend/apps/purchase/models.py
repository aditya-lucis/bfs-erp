from decimal import Decimal
from django.db import models
from django.conf import settings
from apps.accounting.models import Account
from apps.organization.models import Company, Department
from apps.projects.models import Project, RAP, RAPDetail
from apps.inventory.models import Item, UnitMeasurement
from apps.budget_component.models import BudgetComponent


# ─────────────────────────────────────────────────────────────────────────────
# Master kecil
# ─────────────────────────────────────────────────────────────────────────────

class VendorCategory(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'purchases_vendor_category'
        verbose_name_plural = 'Vendor Categories'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"


class VendorGroup(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'purchases_vendor_group'
        ordering = ['name']

    def __str__(self):
        return self.name


# ─────────────────────────────────────────────────────────────────────────────
# Vendor
# ─────────────────────────────────────────────────────────────────────────────

class Vendor(models.Model):

    class Status(models.TextChoices):
        OPEN   = 'open',   'Open'
        CLOSED = 'closed', 'Closed'
        HOLD   = 'hold',   'Hold'

    class Currency(models.TextChoices):
        IDR = 'IDR', 'IDR'
        USD = 'USD', 'USD'
        EUR = 'EUR', 'EUR'
        SGD = 'SGD', 'SGD'

    class AreaCode(models.TextChoices):
        OTHER    = 'other',    '[Other] Other'
        JAKARTA  = 'jakarta',  'Jakarta'
        BANDUNG  = 'bandung',  'Bandung'
        SURABAYA = 'surabaya', 'Surabaya'

    class KriteriaUsaha(models.TextChoices):
        USAHA_KECIL    = 'usaha_kecil',    'Usaha Kecil'
        USAHA_MENENGAH = 'usaha_menengah', 'Usaha Menengah'
        USAHA_BESAR    = 'usaha_besar',    'Usaha Besar'

    # ── Identity ──────────────────────────────────────────────────────────────
    company    = models.ForeignKey(Company, on_delete=models.PROTECT, related_name='vendors')
    code       = models.CharField(max_length=20, unique=True, editable=False)
    title      = models.CharField(max_length=20, blank=True, default='')
    name       = models.CharField(max_length=200)
    category   = models.ForeignKey(VendorCategory, on_delete=models.PROTECT, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    variety    = models.CharField(max_length=100, blank=True, default='')   # jenis usaha / speciality
    tax_number = models.CharField(max_length=50, blank=True, default='')
    nppkp      = models.CharField(max_length=50, blank=True, default='')
    is_leasing = models.BooleanField(default=False)

    # ── Contact ───────────────────────────────────────────────────────────────
    email           = models.EmailField()
    alternative_email = models.EmailField(blank=True, default='')
    website         = models.CharField(max_length=200, blank=True, default='')
    address_1       = models.TextField()
    address_2       = models.TextField(blank=True, default='')
    country         = models.CharField(max_length=100, default='Indonesia')
    state           = models.CharField(max_length=100, blank=True, default='')
    city            = models.CharField(max_length=100)
    zip_code        = models.CharField(max_length=20, blank=True, default='')
    area_code       = models.CharField(max_length=20, choices=AreaCode.choices, default=AreaCode.OTHER)
    phone_1         = models.CharField(max_length=30)
    phone_2         = models.CharField(max_length=30, blank=True, default='')
    fax             = models.CharField(max_length=30, blank=True, default='')

    # ── Financial ─────────────────────────────────────────────────────────────
    currency             = models.CharField(max_length=5, choices=Currency.choices, default=Currency.IDR)
    tolerance_difference = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    deposit              = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    # ── Bank Account ──────────────────────────────────────────────────────────
    bank_name       = models.CharField(max_length=100, blank=True, default='')
    bank_branch     = models.CharField(max_length=100, blank=True, default='')
    bank_city       = models.CharField(max_length=100, blank=True, default='')
    bank_account_number = models.CharField(max_length=50, blank=True, default='')
    bank_account_name   = models.CharField(max_length=200, blank=True, default='')
    term_and_condition  = models.TextField(blank=True, default='')

    # ── Legalitas ─────────────────────────────────────────────────────────────
    company_financial_capability = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    notary_name          = models.CharField(max_length=200, blank=True, default='')
    letter_no_date       = models.CharField(max_length=200, blank=True, default='')
    notary_name_2        = models.CharField(max_length=200, blank=True, default='')
    letter_no_date_2     = models.CharField(max_length=200, blank=True, default='')
    letter_of_endorsement = models.CharField(max_length=200, blank=True, default='')
    no_siup              = models.CharField(max_length=100, blank=True, default='')
    expired_date_siup    = models.DateField(null=True, blank=True)
    no_tdp               = models.CharField(max_length=100, blank=True, default='')
    expired_date_tdp     = models.DateField(null=True, blank=True)
    no_sk_domisili       = models.CharField(max_length=100, blank=True, default='')
    expired_date_sk_domisili = models.DateField(null=True, blank=True)
    no_siujk             = models.CharField(max_length=100, blank=True, default='')
    expired_date_siujk   = models.DateField(null=True, blank=True)
    kriteria_usaha       = models.CharField(
        max_length=20,
        choices=KriteriaUsaha.choices,
        default=KriteriaUsaha.USAHA_KECIL,
        blank=True,
    )

    # ── Item Type Flags ───────────────────────────────────────────────────────
    item_type_asset       = models.BooleanField(default=True)
    item_type_fg          = models.BooleanField(default=True)   # Finished Goods
    item_type_rm          = models.BooleanField(default=True)   # Raw Material
    item_type_supplies    = models.BooleanField(default=True)
    item_type_wip         = models.BooleanField(default=True)
    item_type_maintenance = models.BooleanField(default=True)
    item_type_subcont     = models.BooleanField(default=True)   # Sub-Contractor

    # ── Relations & Status ────────────────────────────────────────────────────
    group       = models.ForeignKey(VendorGroup, on_delete=models.SET_NULL, null=True, blank=True)
    is_sister_company = models.BooleanField(default=False)
    status      = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'purchases_vendor'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.title} {self.name}".strip()

    def save(self, *args, **kwargs):
        if not self.code:
            category = self.category
            if not category and self.category_id:
                category = VendorCategory.objects.filter(pk=self.category_id).first()
            self.code = self._generate_code(category)
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_code(category=None):
        """Generate kode vendor: {CATEGORY_CODE}-{SEQ:03d}, contoh SB-029."""
        if category:
            prefix = category.code.upper()
            last = (
                Vendor.objects
                .filter(code__startswith=f"{prefix}-")
                .order_by('-code')
                .first()
            )
            if last:
                try:
                    num = int(last.code.rsplit('-', 1)[-1]) + 1
                except ValueError:
                    num = 1
            else:
                num = 1
            return f"{prefix}-{num:03d}"

        last = Vendor.objects.order_by('id').last()
        next_num = (last.id + 1) if last else 1
        return f"VND-{next_num:03d}"


# ─────────────────────────────────────────────────────────────────────────────
# Linked Accounts (AP, Deposit, Down Payment)
# ─────────────────────────────────────────────────────────────────────────────

class VendorLinkedAccount(models.Model):

    class AccountType(models.TextChoices):
        AP           = 'ap',           'Account Payable (A/P)'
        DEPOSIT      = 'deposit',      'Vendor Deposit'
        DOWN_PAYMENT = 'down_payment', 'Vendor Down Payment'

    class CurrencyScope(models.TextChoices):
        ALL = 'all', 'All'
        IDR = 'IDR', 'IDR'
        USD = 'USD', 'USD'
        EUR = 'EUR', 'EUR'
        SGD = 'SGD', 'SGD'

    vendor         = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='linked_accounts')
    account_type   = models.CharField(max_length=30, choices=AccountType.choices)
    currency_scope = models.CharField(max_length=5, choices=CurrencyScope.choices, default=CurrencyScope.ALL)
    account        = models.ForeignKey(Account, on_delete=models.PROTECT, null=True, blank=True)

    class Meta:
        db_table = 'purchases_vendor_linked_account'
        unique_together = ('vendor', 'account_type', 'currency_scope')

    def __str__(self):
        return f"{self.vendor.code} | {self.account_type} | {self.currency_scope}"


# ─────────────────────────────────────────────────────────────────────────────
# Terms
# ─────────────────────────────────────────────────────────────────────────────

class VendorTerms(models.Model):

    class PaymentDue(models.TextChoices):
        TANPA_CICILAN = 'tanpa_cicilan', 'Tanpa Cicilan'
        NET_30        = 'net_30',        'Net 30'
        NET_60        = 'net_60',        'Net 60'
        COD           = 'cod',           'COD'

    class TaxCode(models.TextChoices):
        NONE             = 'none',             'None'
        PPH_23_RATE_15   = 'pph_23_rate_15',   'PPH 23 RATE 15 %'
        PPH_23_RATE_2    = 'pph_23_rate_2',    'PPH 23 RATE 2 %'
        PPH_23_RATE_4    = 'pph_23_rate_4',    'PPH 23 RATE 4%'
        PPH_23_RATE_4_5  = 'pph_23_rate_4_5',  'PPh 23 RATE 4.5 %'
        PPH_23_RATE_7_5  = 'pph_23_rate_7_5',  'PPH 23 RATE 7.5 %'
        PPH_4_2_RATE_10  = 'pph_4_2_rate_10',  'PPH 4(2) RATE 10%'
        PPH_4_2_RATE_2   = 'pph_4_2_rate_2',   'PPH 4(2) RATE 2%'
        PPH_4_2_RATE_3   = 'pph_4_2_rate_3',   'PPH 4(2) RATE 3%'
        PPH_4_2_RATE_4   = 'pph_4_2_rate_4',   'PPH 4(2) RATE 4%'
        PPN_01           = 'ppn_01',           'PPN 01 %'
        PPN_10           = 'ppn_10',           'PPN 10 %'
        PPN_10_EURO      = 'ppn_10_euro',      'PPN 10% (EURO)'
        PPN_11           = 'ppn_11',           'PPN 11 %'
        PPN_15           = 'ppn_15',           'PPN 15%'
        NON              = 'non',              'Non PPh'

    vendor                = models.OneToOneField(Vendor, on_delete=models.CASCADE, related_name='terms')
    payment_due           = models.CharField(max_length=20, choices=PaymentDue.choices, default=PaymentDue.TANPA_CICILAN)
    balance_due_days      = models.PositiveIntegerField(default=0)
    tax_code              = models.CharField(max_length=20, choices=TaxCode.choices, default=TaxCode.NON)
    use_vendor_tax_code   = models.BooleanField(default=False)
    credit_limit          = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    class Meta:
        db_table = 'purchases_vendor_terms'

    def __str__(self):
        return f"Terms - {self.vendor.code}"


# ─────────────────────────────────────────────────────────────────────────────
# Contact Person (lebih detail dari Customer)
# ─────────────────────────────────────────────────────────────────────────────

class VendorContactPerson(models.Model):

    class Title(models.TextChoices):
        MR   = 'mr',   'Mr'
        MRS  = 'mrs',  'Mrs'
        MS   = 'ms',   'Ms'
        DR   = 'dr',   'Dr'
        PROF = 'prof', 'Prof'

    class Gender(models.TextChoices):
        MALE   = 'male',   'Male'
        FEMALE = 'female', 'Female'

    class Area(models.TextChoices):
        OTHER    = 'other',    'O - Other'
        JAKARTA  = 'jakarta',  'Jakarta'
        BANDUNG  = 'bandung',  'Bandung'
        SURABAYA = 'surabaya', 'Surabaya'

    vendor       = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='contact_persons')
    first_name   = models.CharField(max_length=100)
    middle_name  = models.CharField(max_length=100, blank=True, default='')
    last_name    = models.CharField(max_length=100, blank=True, default='')
    nickname     = models.CharField(max_length=100, blank=True, default='')
    title        = models.CharField(max_length=10, choices=Title.choices, blank=True, default='')
    job_title    = models.CharField(max_length=100, blank=True, default='')
    gender       = models.CharField(max_length=10, choices=Gender.choices, blank=True, default='')
    spouse       = models.CharField(max_length=200, blank=True, default='')
    birthday     = models.DateField(null=True, blank=True)
    email        = models.EmailField(blank=True, default='')
    country      = models.CharField(max_length=100, default='Indonesia')
    city         = models.CharField(max_length=100, blank=True, default='')
    area         = models.CharField(max_length=20, choices=Area.choices, default=Area.OTHER)
    home_address = models.TextField(blank=True, default='')
    zip_code     = models.CharField(max_length=20, blank=True, default='')
    phone        = models.CharField(max_length=30, blank=True, default='')
    mobile_phone = models.CharField(max_length=30, blank=True, default='')
    fax          = models.CharField(max_length=30, blank=True, default='')
    notes        = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'purchases_vendor_contact_person'
        ordering = ['id']

    def __str__(self):
        full = f"{self.first_name} {self.last_name}".strip()
        return f"{full} ({self.vendor.code})"

    @property
    def full_name(self):
        parts = [self.first_name, self.middle_name, self.last_name]
        return ' '.join(p for p in parts if p).strip()


# ─────────────────────────────────────────────────────────────────────────────
# Purchase Requisition (PR)
# ─────────────────────────────────────────────────────────────────────────────

class PurchaseRequisition(models.Model):
    class DocumentStatus(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        READY_TO_PROCESS = 'ready_to_process', 'Ready to Process'
        CLOSE = 'close', 'Close'

    class ApprovalStatus(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        AWAITING = 'awaiting', 'Awaiting'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Reject'
        REVISED = 'revised', 'Revised'

    class PRType(models.TextChoices):
        RAW_MATERIAL = 'RM', 'Raw Material'
        SUPPLIES = 'SP', 'Supplies'
        ASSET = 'AST', 'Asset'

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='purchase_requisitions')
    pr_number = models.CharField(max_length=100, unique=True, editable=False)
    pr_date = models.DateField()
    pr_type = models.CharField(max_length=5, choices=PRType.choices, default=PRType.RAW_MATERIAL)
    
    # New fields based on requirements
    request_type = models.CharField(max_length=50, default='Normal')
    pr_class = models.CharField(max_length=50, default='Common')
    repetition = models.CharField(max_length=50, default='None')
    
    project = models.ForeignKey(Project, on_delete=models.PROTECT, null=True, blank=True, related_name='purchase_requisitions')
    rap = models.ForeignKey(RAP, on_delete=models.PROTECT, null=True, blank=True, related_name='purchase_requisitions')
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='purchase_requisitions')
    budget_component = models.ForeignKey(BudgetComponent, on_delete=models.PROTECT, null=True, blank=True, related_name='purchase_requisitions')
    
    cost_category = models.CharField(max_length=50, blank=True, default='')
    currency = models.CharField(max_length=10, default='IDR')
    
    etd = models.DateField(null=True, blank=True, verbose_name='Estimated Time Delivery')
    delivery_point = models.TextField(blank=True, default='')
    notes = models.TextField(blank=True, default='')
    
    document_status = models.CharField(max_length=20, choices=DocumentStatus.choices, default=DocumentStatus.DRAFT)
    approval_status = models.CharField(max_length=20, choices=ApprovalStatus.choices, default=ApprovalStatus.DRAFT)
    
    total_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='created_prs'
    )

    class Meta:
        db_table = 'purchases_pr_header'
        ordering = ['-created_at']
        verbose_name = 'Purchase Requisition'
        verbose_name_plural = 'Purchase Requisitions'

    def __str__(self):
        return f"{self.pr_number} - {self.get_pr_type_display()}"

    def save(self, *args, **kwargs):
        if not self.pr_number:
            self.pr_number = self._generate_pr_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_pr_number():
        from django.utils import timezone
        timestamp = timezone.localtime().strftime('%Y%m%d%H%M%S')
        prefix = f"PRN{timestamp}"
        last = PurchaseRequisition.objects.filter(pr_number__startswith=prefix).order_by('id').last()
        if last:
            # PRN<timestamp> -> len(prefix) is 3 + 14 = 17
            try:
                seq_str = last.pr_number[len(prefix):]
                next_seq = int(seq_str) + 1
            except ValueError:
                next_seq = 1
        else:
            next_seq = 1
        return f"{prefix}{next_seq:05d}"


class PurchaseRequisitionDetail(models.Model):
    pr = models.ForeignKey(PurchaseRequisition, on_delete=models.CASCADE, related_name='details')
    rap_detail = models.ForeignKey(RAPDetail, on_delete=models.SET_NULL, null=True, blank=True, related_name='pr_details')
    item = models.ForeignKey(Item, on_delete=models.PROTECT, null=True, blank=True, related_name='pr_details')
    
    asset_name = models.CharField(max_length=255, blank=True, default='')
    
    quantity = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    unit = models.ForeignKey(UnitMeasurement, on_delete=models.SET_NULL, null=True, blank=True, related_name='pr_details')
    
    unit_price = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    final_unit_price = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    amount = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    
    notes = models.CharField(max_length=500, blank=True, default='')
    order_no = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'purchases_pr_detail'
        ordering = ['pr', 'order_no', 'id']

    def __str__(self):
        return f"{self.pr.pr_number} - {self.item.item_name if self.item else self.asset_name}"

    def save(self, *args, **kwargs):
        # Auto calculate amount
        qty = Decimal(str(self.quantity or 0))
        price = Decimal(str(self.final_unit_price or 0))
        self.amount = qty * price
        super().save(*args, **kwargs)

# ─────────────────────────────────────────────────────────────────────────────
# Purchase Order (PO)
# ─────────────────────────────────────────────────────────────────────────────

class PurchaseOrder(models.Model):
    class DocumentStatus(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        OPEN = 'open', 'Open'
        CONFIRMED = 'confirmed', 'Confirmed'
        DELIVERED = 'delivered', 'Delivered'
        INVOICED = 'invoiced', 'Invoiced'
        CLOSE = 'close', 'Close'
        CANCELLED = 'cancelled', 'Cancelled'

    class ApprovalStatus(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        AWAITING = 'awaiting', 'Awaiting'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Reject'
        REVISED = 'revised', 'Revised'

    class POType(models.TextChoices):
        RAW_MATERIAL = 'RM', 'Raw Material'
        SUPPLIES = 'SP', 'Supplies'
        ASSET = 'AST', 'Asset'

    class PrintOutType(models.TextChoices):
        PO = 'po', 'Purchase Order'
        SPK = 'spk', 'Surat Perintah Kerja'

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='purchase_orders')
    po_number = models.CharField(max_length=100, unique=True, editable=False)
    po_date = models.DateField()
    
    # Core Relations
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, related_name='purchase_orders')
    project = models.ForeignKey(Project, on_delete=models.PROTECT, null=True, blank=True, related_name='purchase_orders')
    rap = models.ForeignKey(RAP, on_delete=models.PROTECT, null=True, blank=True, related_name='purchase_orders')
    
    # Financial Settings
    po_type = models.CharField(max_length=20, choices=POType.choices, default=POType.RAW_MATERIAL)
    po_currency = models.CharField(max_length=10, default='IDR')
    tax_currency = models.CharField(max_length=10, default='IDR')
    freight_currency = models.CharField(max_length=10, default='IDR')
    
    # Vendor Accounts (RR/VI represent vendors responsible for Receipt Report and Vendor Invoice)
    rr_account = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True, related_name='rr_purchase_orders')
    vi_account = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True, related_name='vi_purchase_orders')
    
    # Totals
    total_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    total_discount = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    total_tax = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    total_deduction = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    grand_total = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    partial_cancellation = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    payment_balance = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    paid_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)

    # Additional Flags & Fields
    is_sister_company = models.BooleanField(default=False)
    vendor_so_number = models.CharField(max_length=100, blank=True, default='')
    is_import = models.BooleanField(default=False)
    print_out_type = models.CharField(max_length=10, choices=PrintOutType.choices, default=PrintOutType.PO)
    requestor_department = models.ForeignKey(Department, on_delete=models.PROTECT, null=True, blank=True, related_name='purchase_orders')
    
    term_and_condition = models.TextField(blank=True, default='')
    mandatory_update_material = models.BooleanField(default=False)
    not_regular = models.BooleanField(default=False)
    
    ppn = models.BooleanField(default=False, verbose_name="PPN")
    is_subcontract = models.BooleanField(default=False)
    subcontract_notes = models.TextField(blank=True, default='')
    
    stock_tower = models.BooleanField(default=False)
    stock_besi = models.BooleanField(default=False)
    po_approval = models.CharField(max_length=100, blank=True, default='')
    
    pr_class = models.CharField(max_length=50, default='Common')
    repetition = models.CharField(max_length=50, default='None')
    delivery_point = models.CharField(max_length=255, blank=True, default='')
    
    etd = models.DateField(null=True, blank=True, verbose_name='Estimated Time Delivery')
    notes = models.TextField(blank=True, default='')

    # State tracking
    document_status = models.CharField(max_length=20, choices=DocumentStatus.choices, default=DocumentStatus.DRAFT)
    approval_status = models.CharField(max_length=20, choices=ApprovalStatus.choices, default=ApprovalStatus.DRAFT)
    
    # Active status & Budget Validation
    is_active = models.BooleanField(default=False, verbose_name="Active")
    allow_previous_year_budget = models.BooleanField(default=False, verbose_name="Allow Previous Year Budget RAP")

    # Auditing
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='created_pos'
    )

    class Meta:
        db_table = 'purchases_po_header'
        ordering = ['-created_at']
        verbose_name = 'Purchase Order'
        verbose_name_plural = 'Purchase Orders'

    def __str__(self):
        return f"{self.po_number} - {self.vendor.code}"

    def save(self, *args, **kwargs):
        if not self.po_number:
            self.po_number = self._generate_po_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_po_number():
        from django.utils import timezone
        timestamp = timezone.localtime().strftime('%Y%m%d%H%M%S')
        prefix = f"PO{timestamp}"
        last = PurchaseOrder.objects.filter(po_number__startswith=prefix).order_by('id').last()
        if last:
            try:
                seq_str = last.po_number.split('-')[-1]
                next_seq = int(seq_str) + 1
            except ValueError:
                next_seq = 1
        else:
            next_seq = 1
        return f"{prefix}-{next_seq:05d}"


class PurchaseOrderDetail(models.Model):
    po = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='details')
    pr_detail = models.ForeignKey(PurchaseRequisitionDetail, on_delete=models.SET_NULL, null=True, blank=True, related_name='po_details')
    
    item = models.ForeignKey(Item, on_delete=models.PROTECT, null=True, blank=True, related_name='po_details')
    rap_detail = models.ForeignKey(RAPDetail, on_delete=models.SET_NULL, null=True, blank=True, related_name='po_details')
    budget_component = models.ForeignKey(BudgetComponent, on_delete=models.SET_NULL, null=True, blank=True)
    
    quantity = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    unit = models.ForeignKey(UnitMeasurement, on_delete=models.SET_NULL, null=True, blank=True, related_name='po_details')
    
    unit_price = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    
    amount = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    deduction_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    
    paid_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    paid_tax_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    
    tax1 = models.CharField(max_length=30, choices=VendorTerms.TaxCode.choices, default=VendorTerms.TaxCode.NONE)
    tax2 = models.CharField(max_length=30, choices=VendorTerms.TaxCode.choices, default=VendorTerms.TaxCode.NONE)
    
    estimated_date = models.DateField(null=True, blank=True)
    
    order_no = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'purchases_po_detail'
        ordering = ['po', 'order_no', 'id']

    def __str__(self):
        return f"{self.po.po_number} - {self.item.item_name if self.item else 'Item'}"

    def save(self, *args, **kwargs):
        # Auto calculate amount
        qty = Decimal(str(self.quantity or 0))
        price = Decimal(str(self.unit_price or 0))
        disc_pct = Decimal(str(self.discount_percent or 0))
        
        base_amount = qty * price
        if disc_pct > 0:
            self.discount_amount = base_amount * (disc_pct / Decimal('100'))
        else:
            self.discount_amount = Decimal('0')
            
        discounted_amount = base_amount - self.discount_amount
        
        tax_map = {
            'none': (Decimal('0'), 'none'),
            'non': (Decimal('0'), 'none'),
            'pph_23_rate_15': (Decimal('15'), 'deduction'),
            'pph_23_rate_2': (Decimal('2'), 'deduction'),
            'pph_23_rate_4': (Decimal('4'), 'deduction'),
            'pph_23_rate_4_5': (Decimal('4.5'), 'deduction'),
            'pph_23_rate_7_5': (Decimal('7.5'), 'deduction'),
            'pph_4_2_rate_10': (Decimal('10'), 'deduction'),
            'pph_4_2_rate_2': (Decimal('2'), 'deduction'),
            'pph_4_2_rate_3': (Decimal('3'), 'deduction'),
            'pph_4_2_rate_4': (Decimal('4'), 'deduction'),
            'ppn_01': (Decimal('1'), 'addition'),
            'ppn_10': (Decimal('10'), 'addition'),
            'ppn_10_euro': (Decimal('10'), 'addition'),
            'ppn_11': (Decimal('11'), 'addition'),
            'ppn_15': (Decimal('15'), 'addition'),
        }
        
        ppn_rate = Decimal('0')
        pph_rate = Decimal('0')
        
        t1 = tax_map.get(self.tax1, (Decimal('0'), 'none'))
        t2 = tax_map.get(self.tax2, (Decimal('0'), 'none'))
        
        if t1[1] == 'addition': ppn_rate += t1[0]
        if t2[1] == 'addition': ppn_rate += t2[0]
        if t1[1] == 'deduction': pph_rate += t1[0]
        if t2[1] == 'deduction': pph_rate += t2[0]
            
        baseAmount = discounted_amount
        itemPPN = Decimal('0')
        
        if hasattr(self, 'po') and self.po and getattr(self.po, 'ppn', False):
            baseAmount = discounted_amount / (Decimal('1') + (ppn_rate / Decimal('100')))
            itemPPN = discounted_amount - baseAmount
        else:
            itemPPN = baseAmount * (ppn_rate / Decimal('100'))
            
        itemPPh = baseAmount * (pph_rate / Decimal('100'))
        
        self.amount = discounted_amount
        self.tax_amount = itemPPN
        self.deduction_amount = itemPPh
            
        super().save(*args, **kwargs)


class PurchaseOrderPaymentTerm(models.Model):
    po = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='payment_terms')
    term_desc = models.CharField(max_length=200)
    duration_due = models.CharField(max_length=50, blank=True, default='') # E.g., '30 HARI'
    duration_due_percent = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)
    amount = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    due_date = models.DateField(null=True, blank=True)
    doc_reff = models.CharField(max_length=100, blank=True, default='')
    order_no = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'purchases_po_payment_term'
        ordering = ['po', 'order_no', 'id']

    def __str__(self):
        return f"{self.po.po_number} - {self.term_desc}"


class CompletionCertificate(models.Model):
    class TypeChoices(models.TextChoices):
        GRN = 'GRN', 'GRN'
        BAST = 'BAST', 'BAST'

    cc_number = models.CharField(max_length=100, unique=True)
    document_date = models.DateField()
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    po = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE)
    description = models.TextField()
    type = models.CharField(max_length=10, choices=TypeChoices.choices, default=TypeChoices.GRN)
    document_date_from_vendor = models.DateField()
    currency = models.CharField(max_length=10, default='IDR')
    payment_term = models.ForeignKey(PurchaseOrderPaymentTerm, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    approval_status = models.CharField(max_length=50, default='draft')
    is_active = models.BooleanField(default=False)
    
    # Void fields
    void_reason = models.TextField(null=True, blank=True)
    void_date = models.DateTimeField(null=True, blank=True)
    void_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='voided_ccs')
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'purchases_completion_certificate'
        ordering = ['-document_date', '-id']


class GrnSesDocument(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ('GRN', 'GRN'),
        ('SES', 'SES'),
    ]
    document_name = models.CharField(max_length=200)
    type = models.CharField(max_length=10, choices=DOCUMENT_TYPE_CHOICES, default='GRN')
    is_active = models.BooleanField(default=True, verbose_name='Is Active')

    class Meta:
        db_table = 'purchases_grn_ses_document'
        ordering = ['document_name']

def cc_document_upload_path(instance, filename):
    import os
    ext = os.path.splitext(filename)[1]
    # count existing documents for this CC to get an incremental number
    # instance.cc might not be saved yet, but if it is, we can query
    count = CompletionCertificateDocument.objects.filter(cc=instance.cc).count() + 1
    # fallback if cc_number is empty somehow
    cc_num = instance.cc.cc_number.replace('/', '_').replace(' ', '_') if instance.cc and instance.cc.cc_number else 'new_cc'
    new_filename = f'{cc_num}_{count}{ext}'
    return os.path.join('cc', new_filename)

class CompletionCertificateDocument(models.Model):
    cc = models.ForeignKey(CompletionCertificate, on_delete=models.CASCADE, related_name='documents')
    master_document = models.ForeignKey(GrnSesDocument, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=False)
    file = models.FileField(upload_to=cc_document_upload_path, null=True, blank=True)
    document_number = models.CharField(max_length=255, null=True, blank=True)
    keterangan = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'purchases_completion_certificate_document'
        unique_together = ('cc', 'master_document')


