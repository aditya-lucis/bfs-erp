import uuid
from django.db import models
from apps.accounting.models import Account
from apps.organization.models import Company


class CustomerCategory(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'sales_customer_category'
        verbose_name_plural = 'Customer Categories'

    def __str__(self):
        return f"{self.code} - {self.name}"


class CustomerGroup(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'sales_customer_group'

    def __str__(self):
        return self.name


class Customer(models.Model):

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

    # --- Identity ---
    company        = models.ForeignKey(Company, on_delete=models.PROTECT, related_name='customers')
    code           = models.CharField(max_length=20, unique=True, editable=False)
    title          = models.CharField(max_length=20, blank=True, default='')
    name           = models.CharField(max_length=200)
    category       = models.ForeignKey(CustomerCategory, on_delete=models.PROTECT, null=True, blank=True)
    tax_number     = models.CharField(max_length=50, blank=True, default='')
    nppkp          = models.CharField(max_length=50, blank=True, default='')

    # --- Contact ---
    email          = models.EmailField()
    website        = models.CharField(max_length=200, blank=True, default='')
    address_1      = models.TextField()
    address_2      = models.TextField(blank=True, default='')
    country        = models.CharField(max_length=100, default='Indonesia')
    state          = models.CharField(max_length=100, blank=True, default='')
    city           = models.CharField(max_length=100)
    zip_code       = models.CharField(max_length=20, blank=True, default='')
    area_code      = models.CharField(max_length=20, choices=AreaCode.choices, default=AreaCode.OTHER)
    phone_1        = models.CharField(max_length=30)
    phone_2        = models.CharField(max_length=30, blank=True, default='')
    fax            = models.CharField(max_length=30, blank=True, default='')

    # --- Financial ---
    currency               = models.CharField(max_length=5, choices=Currency.choices, default=Currency.IDR)
    default_price_group    = models.CharField(max_length=50, blank=True, default='')
    tolerance_difference   = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    deposit                = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    credit_limit           = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    # --- Flags ---
    is_kawasan_berikat = models.BooleanField(default=False)
    is_sister_company  = models.BooleanField(default=False)
    item_type_asset    = models.BooleanField(default=True)
    item_type_fg       = models.BooleanField(default=True)   # Finished Goods
    item_type_rm       = models.BooleanField(default=True)   # Raw Material
    item_type_supplies = models.BooleanField(default=True)
    item_type_wip      = models.BooleanField(default=True)

    # --- Relations ---
    group  = models.ForeignKey(CustomerGroup, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sales_customer'

    def __str__(self):
        return f"{self.code} - {self.title} {self.name}".strip()

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self._generate_code()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_code():
        last = Customer.objects.order_by('id').last()
        next_num = (last.id + 1) if last else 1
        return f"CUST-{next_num:03d}"


class CustomerLinkedAccount(models.Model):

    class AccountType(models.TextChoices):
        AR_INVOICE     = 'ar_invoice',      'A/R to be Invoiced'
        AR             = 'ar',              'A/R'
        DEPOSIT        = 'deposit',         'Customer Deposit'
        DOWN_PAYMENT   = 'down_payment',    'Customer Down Payment'

    class CurrencyScope(models.TextChoices):
        ALL = 'all', 'All'
        IDR = 'IDR', 'IDR'
        USD = 'USD', 'USD'
        EUR = 'EUR', 'EUR'
        SGD = 'SGD', 'SGD'

    customer         = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='linked_accounts')
    account_type     = models.CharField(max_length=30, choices=AccountType.choices)
    currency_scope   = models.CharField(max_length=5, choices=CurrencyScope.choices, default=CurrencyScope.ALL)
    account          = models.ForeignKey(Account, on_delete=models.PROTECT, null=True, blank=True)

    class Meta:
        db_table = 'sales_customer_linked_account'
        unique_together = ('customer', 'account_type', 'currency_scope')

    def __str__(self):
        return f"{self.customer.code} | {self.account_type} | {self.currency_scope}"


class CustomerTerms(models.Model):

    class PaymentDue(models.TextChoices):
        TANPA_CICILAN = 'tanpa_cicilan', 'Tanpa Cicilan'
        NET_30        = 'net_30',        'Net 30'
        NET_60        = 'net_60',        'Net 60'
        COD           = 'cod',           'COD'

    class TaxCode(models.TextChoices):
        PPN_11 = 'ppn_11', 'PPN 11 %'
        PPN_0  = 'ppn_0',  'PPN 0 %'
        NON    = 'non',    'Non PPN'

    customer              = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='terms')
    payment_due           = models.CharField(max_length=20, choices=PaymentDue.choices, default=PaymentDue.TANPA_CICILAN)
    balance_due_days      = models.PositiveIntegerField(default=0)
    tax_code              = models.CharField(max_length=20, choices=TaxCode.choices, default=TaxCode.PPN_11)
    use_customer_tax_code = models.BooleanField(default=False)

    class Meta:
        db_table = 'sales_customer_terms'

    def __str__(self):
        return f"Terms - {self.customer.code}"


class CustomerContactPerson(models.Model):
    customer      = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='contact_persons')
    name          = models.CharField(max_length=200)
    home_address  = models.TextField(blank=True, default='')
    email         = models.EmailField(blank=True, default='')
    home_phone    = models.CharField(max_length=30, blank=True, default='')

    class Meta:
        db_table = 'sales_customer_contact_person'

    def __str__(self):
        return f"{self.name} ({self.customer.code})"