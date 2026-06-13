"""
BFS ERP — Annual Budget Models
apps/annual_budget/models.py

Budget bulanan per Budget Component, dikelompokkan per Department.
Semua position di bawah department tersebut tercakup dalam budget ini.

Struktur:
    AnnualBudgetHeader  — Header: Year + Department
    AnnualBudgetLine    — Line: BudgetComponent + 12 kolom bulan
    AnnualBudgetLog     — History perubahan per baris per bulan
"""
from django.db import models
from django.conf import settings
from apps.organization.models import Company, Department
from apps.budget_component.models import BudgetComponent


MONTH_NAMES = [
    '', 'January', 'February', 'March', 'April',
    'May', 'June', 'July', 'August',
    'September', 'October', 'November', 'December',
]


# ── Annual Budget Header ──────────────────────────────────────────────────────

class AnnualBudgetHeader(models.Model):
    """
    Satu header = satu kombinasi (company, department, year).
    Unique constraint mencegah duplikasi.
    """
    company    = models.ForeignKey(
                     Company,
                     on_delete=models.CASCADE,
                     related_name='annual_budgets',
                 )
    department = models.ForeignKey(
                     Department,
                     on_delete=models.CASCADE,
                     related_name='annual_budgets',
                 )
    year       = models.PositiveSmallIntegerField()
    notes      = models.TextField(blank=True)
    is_locked  = models.BooleanField(
                     default=False,
                     help_text='Locked = tidak bisa diedit lagi.',
                 )
    created_by = models.ForeignKey(
                     settings.AUTH_USER_MODEL,
                     null=True, blank=True,
                     on_delete=models.SET_NULL,
                     related_name='annual_budgets_created',
                 )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table        = 'annual_budget_header'
        unique_together = ('company', 'department', 'year')
        ordering        = ['-year', 'department__name']
        verbose_name    = 'Annual Budget Header'
        verbose_name_plural = 'Annual Budget Headers'

    def __str__(self):
        return f'[{self.year}] {self.department.name}'

    @property
    def total_annual(self):
        """Total seluruh budget component untuk tahun ini."""
        return sum(line.total_annual for line in self.lines.all())


# ── Annual Budget Line ────────────────────────────────────────────────────────

class AnnualBudgetLine(models.Model):
    """
    Satu baris = satu Budget Component dengan 12 nilai budget per bulan.
    Budget component dipilih dari yang berada di department yg sama.
    """
    header          = models.ForeignKey(
                          AnnualBudgetHeader,
                          on_delete=models.CASCADE,
                          related_name='lines',
                      )
    cost_category   = models.CharField(
                          max_length=20,
                          choices=BudgetComponent.CostCategory.choices,
                          default=BudgetComponent.CostCategory.OPEX,
                      )
    order_no        = models.PositiveSmallIntegerField(default=0)

    # 12 bulan budget
    jan  = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    feb  = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    mar  = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    apr  = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    may  = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    jun  = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    jul  = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    aug  = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    sep  = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    oct  = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    nov  = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    dec  = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    # Relokasi budget (opsional, bisa dari RAP realloc)
    jan_reloc  = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    feb_reloc  = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    mar_reloc  = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    apr_reloc  = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    may_reloc  = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    jun_reloc  = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    jul_reloc  = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    aug_reloc  = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    sep_reloc  = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    oct_reloc  = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    nov_reloc  = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    dec_reloc  = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    MONTH_FIELDS = ['jan', 'feb', 'mar', 'apr', 'may', 'jun',
                    'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
    RELOC_FIELDS = ['jan_reloc', 'feb_reloc', 'mar_reloc', 'apr_reloc',
                    'may_reloc', 'jun_reloc', 'jul_reloc', 'aug_reloc',
                    'sep_reloc', 'oct_reloc', 'nov_reloc', 'dec_reloc']

    class Meta:
        db_table        = 'annual_budget_line'
        unique_together = ('header', 'cost_category')
        ordering        = ['order_no', 'id']
        verbose_name    = 'Annual Budget Line'
        verbose_name_plural = 'Annual Budget Lines'

    def __str__(self):
        return f'{self.header} — {self.get_cost_category_display()}'

    @property
    def total_annual(self):
        return sum(getattr(self, f) or 0 for f in self.MONTH_FIELDS)

    @property
    def total_reloc(self):
        return sum(getattr(self, f) or 0 for f in self.RELOC_FIELDS)

    @property
    def total_budget(self):
        """Total budget + relokasi per bulan digabung."""
        return self.total_annual + self.total_reloc

    def get_month_value(self, month: int) -> dict:
        """Return dict with budget, reloc, total for given month (1-12)."""
        field = self.MONTH_FIELDS[month - 1]
        reloc = self.RELOC_FIELDS[month - 1]
        budget = getattr(self, field) or 0
        relocation = getattr(self, reloc) or 0
        return {
            'budget':    budget,
            'reloc':     relocation,
            'total':     budget + relocation,
            'month':     month,
            'month_name': MONTH_NAMES[month],
        }


# ── Annual Budget Log ─────────────────────────────────────────────────────────

class AnnualBudgetLog(models.Model):
    """
    Audit trail setiap kali nilai budget berubah.
    """
    line       = models.ForeignKey(
                     AnnualBudgetLine,
                     on_delete=models.CASCADE,
                     related_name='logs',
                 )
    month      = models.PositiveSmallIntegerField()  # 1-12
    old_value  = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    new_value  = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    changed_by = models.ForeignKey(
                     settings.AUTH_USER_MODEL,
                     null=True, blank=True,
                     on_delete=models.SET_NULL,
                     related_name='annual_budget_logs',
                 )
    changed_at = models.DateTimeField(auto_now_add=True)
    note       = models.CharField(max_length=500, blank=True)

    class Meta:
        db_table = 'annual_budget_log'
        ordering = ['-changed_at']

    def __str__(self):
        return (
            f'{self.line} | Month {self.month} | '
            f'{self.old_value} → {self.new_value}'
        )
