from django.db import models

from config import settings

class AccountGroup(models.Model):
    """
    Top-level grouping visible as column headers in the COA list.
    e.g. AKTIVA, LIABILITAS, MODAL, PENDAPATAN, PENDAPATAN LAINNYA,
         BIAYA OPERASIONAL, HARGA POKOK PENDAPATAN (HPP), BEBAN LAINNYA.
    Users with proper authorization can add groups dynamically.
    """
    company         = models.ForeignKey(
                          'organization.Company',
                          on_delete=models.CASCADE,
                          related_name='account_groups',
                      )
    code            = models.CharField(max_length=20)
    name            = models.CharField(max_length=100)
    number_prefix   = models.CharField(
                          max_length=10,
                          help_text='Prefix for account numbers in this group, e.g. "1" for AKTIVA',
                      )
    default_position = models.CharField(
                          max_length=6,
                          choices=[('DEBET', 'Debet'), ('KREDIT', 'Kredit')],
                          default='DEBET',
                      )
    order           = models.PositiveSmallIntegerField(default=0)
    is_active       = models.BooleanField(default=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)
    created_by      = models.ForeignKey(
                          settings.AUTH_USER_MODEL,
                          null=True, blank=True,
                          on_delete=models.SET_NULL,
                          related_name='created_account_groups',
                      )
 
    class Meta:
        db_table        = 'acc_account_group'
        unique_together = ('company', 'code')
        ordering        = ['order', 'code']
        verbose_name    = 'Account Group'
        verbose_name_plural = 'Account Groups'
 
    def __str__(self):
        return f"[{self.code}] {self.name}"

    @property
    def total_amount(self):
        from django.db.models import Sum
        total = self.accounts.filter(
            is_active=True
        ).exclude(account_type=AccountType.HEADER).aggregate(total=Sum('amount'))['total']
        return float(total or 0.00)

# ─── Account (COA) ────────────────────────────────────────────────────────────
 
class AccountType(models.TextChoices):
    HEADER        = 'HEADER',        'Header Account [Non Postable]'
    DETAIL        = 'DETAIL',        'Detail Account [Postable]'
    DETAIL_BANK   = 'DETAIL_BANK',   'Detail Bank [Postable]'
    DETAIL_CASH   = 'DETAIL_CASH',   'Detail Cash [Postable]'
    DETAIL_CHEQUE = 'DETAIL_CHEQUE', 'Detail Cheque Account [Postable]'
 
 
class BankType(models.TextChoices):
    OPERATIONAL = 'OPERATIONAL', 'Operational'
    INVESTMENT  = 'INVESTMENT',  'Investment'
    LOAN        = 'LOAN',        'Loan'
    PAYROLL     = 'PAYROLL',     'Payroll'
    PETTY_CASH  = 'PETTY_CASH',  'Petty Cash'
 
 
class DefaultPosition(models.TextChoices):
    DEBET  = 'DEBET',  'Debet'
    KREDIT = 'KREDIT', 'Kredit'
 
 
class Account(models.Model):
    """
    Chart of Account entry.
    - Belongs to a Company and an AccountGroup.
    - Self-referential tree for Header → Detail hierarchy.
    - account_number is unique per company, prefixed by AccountGroup.number_prefix.
    - Postable types (DETAIL, DETAIL_BANK, DETAIL_CASH, DETAIL_CHEQUE) can receive journal postings.
    - HEADER type is non-postable, used only for grouping.
    """
    company         = models.ForeignKey(
                          'organization.Company',
                          on_delete=models.CASCADE,
                          related_name='accounts',
                      )
    account_group   = models.ForeignKey(
                          AccountGroup,
                          on_delete=models.PROTECT,
                          related_name='accounts',
                      )
    parent          = models.ForeignKey(
                          'self',
                          null=True, blank=True,
                          on_delete=models.CASCADE,
                          related_name='children',
                      )

    # ── Core fields ───────────────────────────────────────────────────────────
    account_number  = models.CharField(
                          max_length=50,
                          help_text='Unique account number, e.g. 51-1.1, 51-1.1.11, 51-1.11.01',
                      )
    account_name    = models.CharField(max_length=200)
    account_type    = models.CharField(
                          max_length=20,
                          choices=AccountType.choices,
                          default=AccountType.DETAIL,
                      )
 
    # ── Common postable fields ────────────────────────────────────────────────
    language        = models.CharField(max_length=10, default='EN',
                          choices=[('EN', 'English'), ('ID', 'Indonesian')])
    default_position = models.CharField(
                          max_length=6,
                          choices=DefaultPosition.choices,
                          default=DefaultPosition.DEBET,
                       )
    currency        = models.CharField(max_length=10, default='IDR')
    amount          = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    month_debet     = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    month_kredit    = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    month_opening_balance = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    
    path            = models.CharField(max_length=500, db_index=True, blank=True)
    # ── Flags — available for DETAIL / DETAIL_BANK / DETAIL_CASH / DETAIL_CHEQUE ─
    is_inter_company  = models.BooleanField(
                            default=False,
                            help_text='Intercompany account flag',
                        )
    is_cost_component = models.BooleanField(
                            default=False,
                            help_text='Used in cost component calculation',
                        )
    is_on_duty        = models.BooleanField(
                          default=False,
                          help_text='Indicates if this account is used for duty/tax logic in other modules.'
                      )
    is_tax_in         = models.BooleanField(
                          default=False,
                          help_text='Indicates if this account is the Input Tax (PPN Masukan) account.'
                      )
 
    # ── Bank-specific ─────────────────────────────────────────────────────────
    bank_type       = models.CharField(
                          max_length=20,
                          choices=BankType.choices,
                          null=True, blank=True,
                          help_text='Only used when account_type = DETAIL_BANK',
                      )
 
    # ── Linked flag (shown in COA list) ──────────────────────────────────────
    is_linked       = models.BooleanField(
                          default=False,
                          help_text='Linked to sub-ledger (AR/AP/Asset/etc.)',
                      )
 
    is_active       = models.BooleanField(default=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)
    created_by      = models.ForeignKey(
                          settings.AUTH_USER_MODEL,
                          null=True, blank=True,
                          on_delete=models.SET_NULL,
                          related_name='created_accounts',
                      )
 
    class Meta:
        db_table        = 'acc_account'
        unique_together = ('company', 'account_number')
        ordering        = ['account_number']
        verbose_name    = 'Account'
        verbose_name_plural = 'Accounts'
 
    def __str__(self):
        return f"{self.account_number} {self.account_name}"
 
    # ── Helpers ───────────────────────────────────────────────────────────────
 
    @property
    def computed_amount(self):
        if self.account_type != AccountType.HEADER:
            return float(self.amount)
        
        if not self.path:
            return 0.00
            
        # Rollup from detail descendants using Materialized Path
        from django.db.models import Sum
        total = Account.objects.filter(
            path__startswith=self.path,
            is_active=True
        ).exclude(account_type=AccountType.HEADER).aggregate(total=Sum('amount'))['total']
        
        return float(total or 0.00)

    @property
    def computed_month_debet(self):
        if self.account_type != AccountType.HEADER:
            return float(self.month_debet)
        
        if not self.path:
            return 0.00
            
        from django.db.models import Sum
        total = Account.objects.filter(
            path__startswith=self.path,
            is_active=True
        ).exclude(account_type=AccountType.HEADER).aggregate(total=Sum('month_debet'))['total']
        
        return float(total or 0.00)

    @property
    def computed_month_kredit(self):
        if self.account_type != AccountType.HEADER:
            return float(self.month_kredit)
        
        if not self.path:
            return 0.00
            
        from django.db.models import Sum
        total = Account.objects.filter(
            path__startswith=self.path,
            is_active=True
        ).exclude(account_type=AccountType.HEADER).aggregate(total=Sum('month_kredit'))['total']
        
        return float(total or 0.00)

    def get_descendants(self):
        descendants = []
        for child in self.children.filter(is_active=True):
            descendants.append(child)
            descendants.extend(child.get_descendants())
        return descendants

    @property
    def is_postable(self):
        return self.account_type != AccountType.HEADER
 
    @property
    def is_header(self):
        return self.account_type == AccountType.HEADER
 
    @property
    def has_children(self):
        return self.children.exists()
 
    @property
    def level(self):
        """Tree depth (0 = root)."""
        depth = 0
        node = self.parent
        while node:
            depth += 1
            node = node.parent
        return depth
 
    def get_ancestors(self):
        """Return list of ancestors from root to self (exclusive)."""
        ancestors = []
        node = self.parent
        while node:
            ancestors.insert(0, node)
            node = node.parent
        return ancestors

 
    @property
    def is_header(self):
        return self.account_type == AccountType.HEADER
 
    @property
    def has_children(self):
        return self.children.exists()
 
    @property
    def level(self):
        """Tree depth (0 = root)."""
        depth = 0
        node = self.parent
        while node:
            depth += 1
            node = node.parent
        return depth
 
    def get_ancestors(self):
        """Return list of ancestors from root to self (exclusive)."""
        ancestors = []
        node = self.parent
        while node:
            ancestors.insert(0, node)
            node = node.parent
        return ancestors
 
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if self.parent:
            new_path = self.parent.path + str(self.pk) + '.'
        else:
            new_path = str(self.pk) + '.'
            
        if self.path != new_path:
            self.path = new_path
            self.save(update_fields=['path'])

    def clean(self):
        from django.core.exceptions import ValidationError
 
        # HEADER cannot be postable — bank_type must be null
        if self.account_type == AccountType.HEADER:
            if self.bank_type:
                raise ValidationError('Header accounts cannot have a bank type.')
 
        # bank_type only for DETAIL_BANK
        if self.account_type != AccountType.DETAIL_BANK and self.bank_type:
            raise ValidationError('bank_type is only applicable for Detail Bank accounts.')
 
        # account_number must start with the group prefix
        if self.account_group_id:
            prefix = self.account_group.number_prefix
            if not self.account_number.startswith(prefix):
                raise ValidationError(
                    f'Account number must start with group prefix "{prefix}".'
                )
 
        # HEADER cannot have postable children — not enforceable here,
        # but children's parent must be same company
        if self.parent_id and self.parent.company_id != self.company_id:
            raise ValidationError('Parent account must belong to the same company.')


# ─── General Journal Transaction (Approval Phase) ─────────────────────────────

class DocumentStatus(models.TextChoices):
    DRAFT = 'DRAFT', 'Draft'
    IN_REVIEW = 'IN_REVIEW', 'In Review'
    APPROVED = 'APPROVED', 'Approved'
    REJECTED = 'REJECTED', 'Rejected'
    CANCELLED = 'CANCELLED', 'Cancelled'


class GeneralJournalTransaction(models.Model):
    company = models.ForeignKey('organization.Company', on_delete=models.CASCADE)
    transaction_number = models.CharField(max_length=50, unique=True)
    date = models.DateField()
    memo = models.CharField(max_length=255)
    project = models.ForeignKey('projects.Project', null=True, blank=True, on_delete=models.SET_NULL)
    vendor = models.ForeignKey('purchase.Vendor', null=True, blank=True, on_delete=models.SET_NULL)
    
    # Header fields shown in UI
    tax_rectification = models.CharField(max_length=50, null=True, blank=True)
    is_adjustment_pph = models.BooleanField(default=False)
    
    status = models.CharField(max_length=20, choices=DocumentStatus.choices, default=DocumentStatus.DRAFT)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'acc_general_journal_transaction'
        ordering = ['-date', '-transaction_number']

    @staticmethod
    def _generate_transaction_number():
        from django.utils import timezone
        timestamp = timezone.localtime().strftime('%Y%m%d%H%M%S')
        prefix = f"GEJ{timestamp}-"
        last = GeneralJournalTransaction.objects.order_by('id').last()
        next_seq = (int(last.transaction_number.split('-')[-1]) + 1) if last and '-' in last.transaction_number else 1
        return f"{prefix}{next_seq:05d}"

    def save(self, *args, **kwargs):
        if not self.transaction_number:
            self.transaction_number = self._generate_transaction_number()
        super().save(*args, **kwargs)


class GeneralJournalTransactionDetail(models.Model):
    header = models.ForeignKey(GeneralJournalTransaction, related_name='details', on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    currency = models.CharField(max_length=10, default='IDR')
    debit = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    credit = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    period_from = models.DateField(null=True, blank=True)
    period_to = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'acc_general_journal_transaction_detail'


# ─── Journal (General Ledger - After Approval) ────────────────────────────────

class JournalHeader(models.Model):
    company = models.ForeignKey('organization.Company', on_delete=models.CASCADE)
    journal_number = models.CharField(max_length=50, unique=True)
    date = models.DateField() # mapped from general journal date
    memo = models.CharField(max_length=255)
    project = models.ForeignKey('projects.Project', null=True, blank=True, on_delete=models.SET_NULL)
    vendor = models.ForeignKey('purchase.Vendor', null=True, blank=True, on_delete=models.SET_NULL)
    type = models.CharField(max_length=10, default='GEN')
    
    is_verified = models.BooleanField(default=True)
    is_adjustment = models.BooleanField(default=False)
    pattern_type = models.CharField(max_length=50, default='STANDARD')

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'acc_journal_header'

class JournalDetail(models.Model):
    journal_header = models.ForeignKey(JournalHeader, related_name='details', on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    currency = models.CharField(max_length=10, default='IDR')
    base_debet = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    base_kredit = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)

    class Meta:
        db_table = 'acc_journal_detail'

# ─── Global Linked Accounts ───────────────────────────────────────────────────

class GlobalLinkedAccount(models.Model):
    company = models.OneToOneField(
        'organization.Company', 
        on_delete=models.CASCADE, 
        related_name='global_linked_accounts'
    )
    
    # General Ledger Linked Accounts
    current_earnings = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    retained_earnings = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    historical_balancing = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    
    # SO PO DISC Account
    sales_discount = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    purchase_discount = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    
    # PPIC Accounts
    wip_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    direct_labor_liability = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    
    # Revaluation Linked Accounts
    income_for_revaluation = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    expense_for_revaluation = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    
    # Sales Linked Accounts
    ar_trade = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    customer_deposit = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    ds_for_tracking_receivables = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    ds_for_tracking_sales_return = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')

    # Purchase Linked Accounts
    ap_trade = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    account_for_tracking_price_different = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    vendor_deposit = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    
    # Asset Management
    profit_on_selling_assets = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    loss_on_selling_assets = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    
    # Commission
    commission_amount = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    commission_amount_payable = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    commission_tax_payable = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    
    # Expense Kurs
    currency_gain = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    currency_loss = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    
    # Journal Difference Container Account
    journal_difference = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    
    # Waste Account
    waste_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    
    # Production Waste Account
    production_waste_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    
    # WHT Account
    wht_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'acc_global_linked_account'
        verbose_name = 'Global Linked Account'
        verbose_name_plural = 'Global Linked Accounts'

    def __str__(self):
        return f"Global Linked Accounts - {self.company.name}"

# ─── Cashbook Request (Payment Request) ─────────────────────────────────────────

class CashbookReqHeader(models.Model):
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

    class PaidStatus(models.TextChoices):
        NOT_PAID = 'not_paid', 'Not Paid'
        HALF_PAID = 'half_paid', 'Half Paid'
        FULL_PAID = 'full_paid', 'Full Paid'

    class UsageFor(models.TextChoices):
        PURCHASE_INVOICE_PAYMENT = 'Purchase Invoice Payment', 'Purchase Invoice Payment'
        PROJECT_CASH_ADVANCED = 'Project Cash Advanced', 'Project Cash Advanced'
        PO_DOWN_PAYMENT = 'Purchase Order Down Payment', 'Purchase Order Down Payment'
        BANK_OBLIGATION_PRINCIPAL = 'Bank Obligation Principal', 'Bank Obligation Principal'
        BANK_OBLIGATION_INTEREST = 'Bank Obligation Interest', 'Bank Obligation Interest'

    document_number = models.CharField(max_length=50, unique=True, editable=False)
    date = models.DateField()
    transaction_type = models.ForeignKey('master_type.TransactionType', on_delete=models.PROTECT)
    usage_for = models.CharField(max_length=50, choices=UsageFor.choices, default=UsageFor.PURCHASE_INVOICE_PAYMENT)
    duration_due_date = models.CharField(max_length=50, null=True, blank=True)
    invoice_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    currency = models.CharField(max_length=10, default='IDR')
    
    project = models.ForeignKey('projects.Project', on_delete=models.PROTECT)
    payment_to = models.ForeignKey('master_type.PaymentTo', on_delete=models.PROTECT)
    notes_payment_to = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    
    requestor_department = models.ForeignKey('organization.Department', on_delete=models.PROTECT, null=True, blank=True)
    purchase_invoice = models.ForeignKey('purchase.PurchaseInvoice', on_delete=models.PROTECT, null=True, blank=True)
    vendor_invoice_number = models.CharField(max_length=100, null=True, blank=True)
    unpaid_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    amount = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    unpaid_tax_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    is_sumbangan = models.BooleanField(default=False)
    
    document_status = models.CharField(max_length=20, choices=DocumentStatus.choices, default=DocumentStatus.DRAFT)
    approval_status = models.CharField(max_length=20, choices=ApprovalStatus.choices, default=ApprovalStatus.DRAFT)
    paid_status = models.CharField(max_length=20, choices=PaidStatus.choices, default=PaidStatus.NOT_PAID)
    
    is_close = models.BooleanField(default=False)
    allow_previous_year_budget = models.BooleanField(default=False)
    reason_allow_previous_year_budget = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('authentication.User', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'acc_cashbook_req_header'
        verbose_name = 'Cashbook Request Header'
        ordering = ['-date', '-id']

    def save(self, *args, **kwargs):
        if not self.document_number:
            from django.utils import timezone
            timestamp = timezone.localtime().strftime('%Y%m%d%H%M%S')
            prefix = f'CBR{timestamp}'
            last = CashbookReqHeader.objects.order_by('id').last()
            if last:
                try:
                    seq_str = last.document_number.split('-')[-1]
                    next_seq = int(seq_str) + 1
                except ValueError:
                    next_seq = 1
            else:
                next_seq = 1
            self.document_number = f'{prefix}-{next_seq:07d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.document_number


class CashbookReqDetail(models.Model):
    header = models.ForeignKey(CashbookReqHeader, on_delete=models.CASCADE, related_name='details')
    item = models.ForeignKey('inventory.Item', on_delete=models.PROTECT, null=True, blank=True)
    
    quantity = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    unit_price = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)

    class Meta:
        db_table = 'acc_cashbook_req_detail'
        verbose_name = 'Cashbook Request Detail'
