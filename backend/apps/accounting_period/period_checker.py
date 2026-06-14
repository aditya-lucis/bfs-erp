"""
BFS ERP — Period Checker Library
apps/accounting/period_checker.py

Central library untuk validasi apakah transaksi boleh diposting
berdasarkan status Financial Period (Annual → Quarter → Monthly → Accounting).

Usage:
    from apps.accounting.period_checker import PeriodChecker

    # Raise exception jika closed (default)
    PeriodChecker.check(transaction_date)

    # Return False jika closed (no exception)
    result = PeriodChecker.check(transaction_date, raise_exception=False)
    if not result.is_open:
        print(result.message)

    # Cek spesifik level
    PeriodChecker.check(transaction_date, levels=['MONTHLY', 'ACCOUNTING'])

    # Cek dengan company eksplisit
    PeriodChecker.check(transaction_date, company=company)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional

from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


# ── Constants ──────────────────────────────────────────────────────────────────

ALL_LEVELS   = ['ANNUAL', 'QUARTER', 'MONTHLY', 'ACCOUNTING']
MONTH_NAMES  = [
    '', 'January', 'February', 'March', 'April',
    'May', 'June', 'July', 'August',
    'September', 'October', 'November', 'December',
]
QUARTER_MAP  = {1: 1, 2: 1, 3: 1, 4: 2, 5: 2, 6: 2,
                7: 3, 8: 3, 9: 3, 10: 4, 11: 4, 12: 4}


# ── Exceptions ─────────────────────────────────────────────────────────────────

class PeriodClosedException(Exception):
    """
    Raised when a transaction date falls in a closed period.

    Attributes:
        level        : Which level is closed (ANNUAL/QUARTER/MONTHLY/ACCOUNTING)
        period_label : Human-readable period description e.g. "June 2026"
        message      : Full error message for display
    """
    def __init__(self, level: str, period_label: str, message: str):
        self.level        = level
        self.period_label = period_label
        self.message      = message
        super().__init__(message)


class PeriodNotFoundException(Exception):
    """Raised when no period record exists for the given date."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


# ── Result Object ──────────────────────────────────────────────────────────────

@dataclass
class PeriodCheckResult:
    """
    Result of a period check when raise_exception=False.

    Attributes:
        is_open        : True = transaction allowed, False = blocked
        level          : Blocking level (None if open)
        period_label   : Which period is blocking (None if open)
        message        : Human-readable message
        checked_levels : All levels that were checked
        details        : Dict of each level's result
    """
    is_open        : bool
    level          : Optional[str]        = None
    period_label   : Optional[str]        = None
    message        : str                  = ''
    checked_levels : list                 = field(default_factory=list)
    details        : dict                 = field(default_factory=dict)

    @property
    def is_closed(self) -> bool:
        return not self.is_open

    def to_dict(self) -> dict:
        return {
            'is_open':        self.is_open,
            'level':          self.level,
            'period_label':   self.period_label,
            'message':        self.message,
            'checked_levels': self.checked_levels,
            'details':        self.details,
        }


# ── Main Checker ───────────────────────────────────────────────────────────────

class PeriodChecker:
    """
    Main period validation class.

    All methods are class/static methods — no instantiation needed.
    The checker validates from highest level (ANNUAL) down to lowest (ACCOUNTING).
    The first closed level encountered immediately blocks the transaction.

    Examples:
        # Simple check — raises PeriodClosedException if closed
        PeriodChecker.check(date(2026, 6, 15))

        # Silent check — returns PeriodCheckResult
        result = PeriodChecker.check(date(2026, 6, 15), raise_exception=False)

        # Check specific levels only
        PeriodChecker.check(date(2026, 6, 15), levels=['MONTHLY'])

        # Check with explicit company (multi-company future support)
        PeriodChecker.check(date(2026, 6, 15), company=company_obj)
    """

    @classmethod
    def check(
        cls,
        transaction_date: date | datetime | str,
        company=None,
        levels: list[str] | None = None,
        raise_exception: bool = True,
    ) -> PeriodCheckResult:
        """
        Main entry point. Validates transaction_date against period status.

        Args:
            transaction_date : Date of the transaction (date, datetime, or ISO string)
            company          : Company instance. None = use default company.
            levels           : Which levels to check. None = all (ANNUAL→QUARTER→MONTHLY→ACCOUNTING)
            raise_exception  : True = raise PeriodClosedException on failure
                               False = return PeriodCheckResult

        Returns:
            PeriodCheckResult with is_open=True if allowed

        Raises:
            PeriodClosedException  : If period is closed and raise_exception=True
            PeriodNotFoundException : If no period record found for the date
        """
        # Normalize date
        txn_date = cls._normalize_date(transaction_date)
        levels   = cls._normalize_levels(levels)

        # Resolve company
        company  = cls._resolve_company(company)

        details        = {}
        checked_levels = []

        # Check each level in order: ANNUAL → QUARTER → MONTHLY → ACCOUNTING
        for level in ['ANNUAL', 'QUARTER', 'MONTHLY', 'ACCOUNTING']:
            if level not in levels:
                continue

            checked_levels.append(level)
            level_result = cls._check_level(level, txn_date, company)
            details[level] = level_result

            if not level_result['is_open']:
                # This level is closed — transaction blocked
                period_label = level_result['period_label']
                message      = cls._build_closed_message(level, period_label, txn_date)

                result = PeriodCheckResult(
                    is_open        = False,
                    level          = level,
                    period_label   = period_label,
                    message        = message,
                    checked_levels = checked_levels,
                    details        = details,
                )

                logger.warning(
                    '[PeriodChecker] BLOCKED | date=%s | level=%s | period=%s',
                    txn_date, level, period_label,
                )

                if raise_exception:
                    raise PeriodClosedException(level, period_label, message)
                return result

        # All checked levels are open
        result = PeriodCheckResult(
            is_open        = True,
            message        = f'Period {txn_date.strftime("%B %Y")} is open for transactions.',
            checked_levels = checked_levels,
            details        = details,
        )
        logger.debug('[PeriodChecker] ALLOWED | date=%s | levels=%s', txn_date, checked_levels)
        return result

    @classmethod
    def is_open(
        cls,
        transaction_date: date | datetime | str,
        company=None,
        levels: list[str] | None = None,
    ) -> bool:
        """
        Quick boolean check. Returns True if transaction is allowed.
        Never raises — always returns bool.

        Example:
            if not PeriodChecker.is_open(txn_date):
                return Response({'detail': 'Period closed.'}, status=400)
        """
        result = cls.check(transaction_date, company=company, levels=levels, raise_exception=False)
        return result.is_open

    @classmethod
    def get_status(
        cls,
        transaction_date: date | datetime | str,
        company=None,
        levels: list[str] | None = None,
    ) -> PeriodCheckResult:
        """
        Get full status result without raising exception.
        Alias for check(..., raise_exception=False).
        """
        return cls.check(transaction_date, company=company, levels=levels, raise_exception=False)

    # ── Level-specific checks ──────────────────────────────────────────────────

    @classmethod
    def check_annual(cls, year: int, company=None, raise_exception: bool = True) -> PeriodCheckResult:
        """Check only the annual period for a given year."""
        return cls.check(
            date(year, 1, 1),
            company=company,
            levels=['ANNUAL'],
            raise_exception=raise_exception,
        )

    @classmethod
    def check_quarter(cls, year: int, quarter: int, company=None, raise_exception: bool = True) -> PeriodCheckResult:
        """Check only the quarter period for a given year and quarter (1-4)."""
        month_start = (quarter - 1) * 3 + 1
        return cls.check(
            date(year, month_start, 1),
            company=company,
            levels=['QUARTER'],
            raise_exception=raise_exception,
        )

    @classmethod
    def check_month(cls, year: int, month: int, company=None, raise_exception: bool = True) -> PeriodCheckResult:
        """Check only the monthly period for a given year and month."""
        return cls.check(
            date(year, month, 1),
            company=company,
            levels=['MONTHLY'],
            raise_exception=raise_exception,
        )

    # ── Internal helpers ───────────────────────────────────────────────────────

    @classmethod
    def _check_level(cls, level: str, txn_date: date, company) -> dict:
        """
        Check a single level. Returns dict:
            { is_open: bool, period_label: str, status: str, exists: bool }
        """
        try:
            if level == 'ANNUAL':
                return cls._check_annual(txn_date, company)
            elif level == 'QUARTER':
                return cls._check_quarter(txn_date, company)
            elif level == 'MONTHLY':
                return cls._check_monthly(txn_date, company)
            elif level == 'ACCOUNTING':
                return cls._check_accounting(txn_date, company)
        except Exception as e:
            logger.error('[PeriodChecker] Error checking level %s: %s', level, e)
            # If period record doesn't exist, treat as open (lenient)
            # Change to False if you want strict mode
            return {
                'is_open':      True,
                'period_label': f'{level} period not found',
                'status':       'NOT_FOUND',
                'exists':       False,
                'error':        str(e),
            }

    @classmethod
    def _check_annual(cls, txn_date: date, company) -> dict:
        from .models import AnnualPeriod
        try:
            annual = AnnualPeriod.objects.get(company=company, year=txn_date.year)
            return {
                'is_open':      annual.status == 'OPEN',
                'period_label': str(txn_date.year),
                'status':       annual.status,
                'exists':       True,
            }
        except AnnualPeriod.DoesNotExist:
            return {'is_open': True, 'period_label': str(txn_date.year), 'status': 'NOT_FOUND', 'exists': False}

    @classmethod
    def _check_quarter(cls, txn_date: date, company) -> dict:
        from .models import QuarterPeriod
        quarter_num = QUARTER_MAP[txn_date.month]
        label       = f'{txn_date.year} Q{quarter_num}'
        try:
            qp = QuarterPeriod.objects.get(
                company=company, year=txn_date.year, quarter=quarter_num
            )
            return {
                'is_open':      qp.status == 'OPEN',
                'period_label': label,
                'status':       qp.status,
                'exists':       True,
            }
        except QuarterPeriod.DoesNotExist:
            return {'is_open': True, 'period_label': label, 'status': 'NOT_FOUND', 'exists': False}

    @classmethod
    def _check_monthly(cls, txn_date: date, company) -> dict:
        from .models import MonthlyPeriod
        label = f'{MONTH_NAMES[txn_date.month]} {txn_date.year}'
        try:
            mp = MonthlyPeriod.objects.get(
                company=company, year=txn_date.year, month=txn_date.month
            )
            return {
                'is_open':      mp.status == 'OPEN',
                'period_label': label,
                'status':       mp.status,
                'exists':       True,
            }
        except MonthlyPeriod.DoesNotExist:
            return {'is_open': True, 'period_label': label, 'status': 'NOT_FOUND', 'exists': False}

    @classmethod
    def _check_accounting(cls, txn_date: date, company) -> dict:
        from .models import AccountingPeriod
        label = f'{MONTH_NAMES[txn_date.month]} {txn_date.year}'
        try:
            ap = AccountingPeriod.objects.get(
                company=company, year=txn_date.year, month=txn_date.month
            )
            # Extra: ensure date falls within start_date–end_date
            if not (ap.start_date <= txn_date <= ap.end_date):
                return {
                    'is_open':      False,
                    'period_label': label,
                    'status':       'OUT_OF_RANGE',
                    'exists':       True,
                }
            return {
                'is_open':      ap.status == 'OPEN',
                'period_label': label,
                'status':       ap.status,
                'exists':       True,
            }
        except AccountingPeriod.DoesNotExist:
            return {'is_open': True, 'period_label': label, 'status': 'NOT_FOUND', 'exists': False}

    @classmethod
    def _normalize_date(cls, d) -> date:
        if isinstance(d, datetime):
            return d.date()
        if isinstance(d, date):
            return d
        if isinstance(d, str):
            for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y'):
                try:
                    return datetime.strptime(d, fmt).date()
                except ValueError:
                    continue
        raise ValueError(f'Cannot parse date: {d!r}')

    @classmethod
    def _normalize_levels(cls, levels) -> list[str]:
        if levels is None:
            return ALL_LEVELS
        return [l.upper() for l in levels if l.upper() in ALL_LEVELS]

    @classmethod
    def _resolve_company(cls, company):
        if company is not None:
            return company
        from apps.organization.models import Company
        return Company.get_default()

    @classmethod
    def _build_closed_message(cls, level: str, period_label: str, txn_date: date) -> str:
        level_display = {
            'ANNUAL':     'Annual',
            'QUARTER':    'Quarter',
            'MONTHLY':    'Monthly',
            'ACCOUNTING': 'Accounting',
        }.get(level, level)

        return (
            f'Transaksi tidak dapat diproses. '
            f'{level_display} period "{period_label}" sudah ditutup (CLOSED). '
            f'Hubungi Finance untuk membuka kembali periode ini.'
        )