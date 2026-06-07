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