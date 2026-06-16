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
                            help_text='On-duty / operational flag',
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