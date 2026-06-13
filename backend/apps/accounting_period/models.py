"""
BFS ERP — Accounting: Financial Period Models

Hierarchy:
    AnnualPeriod (Year)
        └── QuarterPeriod (Q1–Q4)
        └── MonthlyPeriod (Jan–Dec)
            └── AccountingPeriod (per-month detail: start_date, end_date)

Every open/close action is logged in PeriodActivityLog.
"""

from django.db import models
from config import settings


# ─── Choices ──────────────────────────────────────────────────────────────────

class PeriodStatus(models.TextChoices):
    OPEN  = 'OPEN',  'Open'
    CLOSE = 'CLOSE', 'Close'


MONTH_CHOICES = [
    (1, 'January'), (2, 'February'), (3, 'March'),
    (4, 'April'),   (5, 'May'),      (6, 'June'),
    (7, 'July'),    (8, 'August'),   (9, 'September'),
    (10, 'October'), (11, 'November'), (12, 'December'),
]

QUARTER_CHOICES = [
    (1, 'Q1'), (2, 'Q2'), (3, 'Q3'), (4, 'Q4'),
]

PERIOD_TYPE_CHOICES = [
    ('ANNUAL',   'Annual Period'),
    ('QUARTER',  'Quarter Period'),
    ('MONTHLY',  'Monthly Period'),
    ('ACCOUNTING', 'Accounting Period'),
]


# ─── Annual Period ─────────────────────────────────────────────────────────────

class AnnualPeriod(models.Model):
    """
    One record per fiscal year per company.
    e.g. Year 2025 → Open / Close
    Closing an annual period will also close all quarters and months within it.
    """
    company = models.ForeignKey(
        'organization.Company',
        on_delete=models.CASCADE,
        related_name='annual_periods',
    )
    year   = models.PositiveSmallIntegerField()
    status = models.CharField(
        max_length=5,
        choices=PeriodStatus.choices,
        default=PeriodStatus.OPEN,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='created_annual_periods',
    )

    class Meta:
        db_table        = 'acc_annual_period'
        unique_together = ('company', 'year')
        ordering        = ['-year']
        verbose_name    = 'Annual Period'
        verbose_name_plural = 'Annual Periods'

    def __str__(self):
        return f"{self.year} [{self.status}]"


# ─── Quarter Period ────────────────────────────────────────────────────────────

class QuarterPeriod(models.Model):
    """
    Four records per year (Q1–Q4) per company.
    Q1 = Jan–Mar, Q2 = Apr–Jun, Q3 = Jul–Sep, Q4 = Oct–Dec.
    """
    company       = models.ForeignKey(
        'organization.Company',
        on_delete=models.CASCADE,
        related_name='quarter_periods',
    )
    annual_period = models.ForeignKey(
        AnnualPeriod,
        on_delete=models.CASCADE,
        related_name='quarters',
    )
    year    = models.PositiveSmallIntegerField()
    quarter = models.PositiveSmallIntegerField(choices=QUARTER_CHOICES)  # 1–4
    status  = models.CharField(
        max_length=5,
        choices=PeriodStatus.choices,
        default=PeriodStatus.OPEN,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='created_quarter_periods',
    )

    class Meta:
        db_table        = 'acc_quarter_period'
        unique_together = ('company', 'year', 'quarter')
        ordering        = ['-year', 'quarter']
        verbose_name    = 'Quarter Period'
        verbose_name_plural = 'Quarter Periods'

    def __str__(self):
        return f"{self.year} Q{self.quarter} [{self.status}]"

    @property
    def quarter_label(self):
        return f"Q{self.quarter}"


# ─── Monthly Period ────────────────────────────────────────────────────────────

class MonthlyPeriod(models.Model):
    """
    Twelve records per year (Jan–Dec) per company.
    Controls whether transactions can be posted for this month.
    """
    company       = models.ForeignKey(
        'organization.Company',
        on_delete=models.CASCADE,
        related_name='monthly_periods',
    )
    annual_period  = models.ForeignKey(
        AnnualPeriod,
        on_delete=models.CASCADE,
        related_name='months',
    )
    quarter_period = models.ForeignKey(
        QuarterPeriod,
        on_delete=models.CASCADE,
        related_name='months',
    )
    year   = models.PositiveSmallIntegerField()
    month  = models.PositiveSmallIntegerField(choices=MONTH_CHOICES)  # 1–12
    status = models.CharField(
        max_length=5,
        choices=PeriodStatus.choices,
        default=PeriodStatus.OPEN,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='created_monthly_periods',
    )

    class Meta:
        db_table        = 'acc_monthly_period'
        unique_together = ('company', 'year', 'month')
        ordering        = ['-year', 'month']
        verbose_name    = 'Monthly Period'
        verbose_name_plural = 'Monthly Periods'

    def __str__(self):
        month_name = dict(MONTH_CHOICES).get(self.month, '')
        return f"{month_name} {self.year} [{self.status}]"

    @property
    def month_name(self):
        return dict(MONTH_CHOICES).get(self.month, '')


# ─── Accounting Period (per-month detail) ─────────────────────────────────────

class AccountingPeriod(models.Model):
    """
    Detailed accounting period record with explicit start_date / end_date.
    One record = one calendar month, linked to MonthlyPeriod.
    This is the granular record shown in the 'Accounting Period' list.
    """
    company        = models.ForeignKey(
        'organization.Company',
        on_delete=models.CASCADE,
        related_name='accounting_periods',
    )
    monthly_period = models.OneToOneField(
        MonthlyPeriod,
        on_delete=models.CASCADE,
        related_name='accounting_period',
    )
    year       = models.PositiveSmallIntegerField()
    month      = models.PositiveSmallIntegerField(choices=MONTH_CHOICES)
    start_date = models.DateField()
    end_date   = models.DateField()
    status     = models.CharField(
        max_length=5,
        choices=PeriodStatus.choices,
        default=PeriodStatus.OPEN,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='created_accounting_periods',
    )

    class Meta:
        db_table        = 'acc_accounting_period'
        unique_together = ('company', 'year', 'month')
        ordering        = ['-year', '-month']
        verbose_name    = 'Accounting Period'
        verbose_name_plural = 'Accounting Periods'

    def __str__(self):
        month_name = dict(MONTH_CHOICES).get(self.month, '')
        return f"{month_name} {self.year} [{self.status}]"

    @property
    def month_name(self):
        return dict(MONTH_CHOICES).get(self.month, '')

    @property
    def is_closed(self):
        return self.status == PeriodStatus.CLOSE


# ─── Period Activity Log ───────────────────────────────────────────────────────

class PeriodActivityLog(models.Model):
    """
    Immutable audit log for every open/close action on any period type.
    Records: who, when, what period, what action, and the reason given.
    """
    company     = models.ForeignKey(
        'organization.Company',
        on_delete=models.CASCADE,
        related_name='period_activity_logs',
    )
    period_type = models.CharField(max_length=20, choices=PERIOD_TYPE_CHOICES)

    # Generic references — only one will be set per log entry
    annual_period  = models.ForeignKey(
        AnnualPeriod, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='activity_logs',
    )
    quarter_period = models.ForeignKey(
        QuarterPeriod, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='activity_logs',
    )
    monthly_period = models.ForeignKey(
        MonthlyPeriod, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='activity_logs',
    )
    accounting_period = models.ForeignKey(
        AccountingPeriod, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='activity_logs',
    )

    # What happened
    action         = models.CharField(
        max_length=5,
        choices=PeriodStatus.choices,
        help_text='The new status after this action (OPEN or CLOSE)',
    )
    reason         = models.TextField(help_text='Reason given by the user for this action')
    period_label   = models.CharField(
        max_length=100,
        help_text='Human-readable snapshot of the period at log time, e.g. "June 2026"',
    )
    period_status_after = models.CharField(
        max_length=5,
        choices=PeriodStatus.choices,
        help_text='Status of the period after the action',
    )

    # Who / when
    actioned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='period_activity_logs',
    )
    actioned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table  = 'acc_period_activity_log'
        ordering  = ['-actioned_at']
        verbose_name = 'Period Activity Log'
        verbose_name_plural = 'Period Activity Logs'

    def __str__(self):
        user = getattr(self.actioned_by, 'full_name', str(self.actioned_by))
        return f"[{self.period_type}] {self.period_label} → {self.action} by {user}"