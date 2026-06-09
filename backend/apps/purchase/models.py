from django.db import models
from apps.accounting.models import Account
from apps.organization.models import Company, Department


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
        PPH_23_45  = 'pph_23_45',  'PPh 23 Rate 4.5 %'
        PPH_23_2   = 'pph_23_2',   'PPh 23 Rate 2 %'
        PPH_23_15  = 'pph_23_15',  'PPh 23 Rate 1.5 %'
        NON        = 'non',        'Non PPh'

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