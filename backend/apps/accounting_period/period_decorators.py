"""
BFS ERP — Period Decorators & Mixins
apps/accounting/period_decorators.py

Provides decorators and mixins to enforce period validation
on Django REST Framework views and serializers.

Usage — View Decorator:
    from apps.accounting.period_decorators import period_required

    class JournalCreateView(generics.CreateAPIView):
        @period_required(date_field='journal_date')
        def create(self, request, *args, **kwargs):
            ...

Usage — Mixin (recommended for class-based views):
    from apps.accounting.period_decorators import PeriodCheckMixin

    class JournalCreateView(PeriodCheckMixin, generics.CreateAPIView):
        period_date_field = 'journal_date'   # field name in request.data
        period_levels     = None             # None = all levels

Usage — Serializer Mixin:
    from apps.accounting.period_decorators import PeriodCheckSerializerMixin

    class JournalSerializer(PeriodCheckSerializerMixin, serializers.ModelSerializer):
        period_date_field = 'journal_date'
        ...

Usage — Manual in view:
    from apps.accounting.period_decorators import check_period_or_400

    def create(self, request, *args, **kwargs):
        check_period_or_400(request.data.get('journal_date'))
        ...
"""

import functools
import logging
from datetime import date, datetime

from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status as http_status

from .period_checker import PeriodChecker, PeriodClosedException, PeriodNotFoundException

logger = logging.getLogger(__name__)


# ── Utility: get date from request data ───────────────────────────────────────

def _extract_date(source, field_name: str):
    """Extract date value from dict-like or object."""
    if isinstance(source, dict):
        return source.get(field_name)
    return getattr(source, field_name, None)


# ── Simple helper function ─────────────────────────────────────────────────────

def check_period_or_400(
    transaction_date,
    company=None,
    levels=None,
    field_name: str = 'non_field_errors',
):
    """
    Validate period and raise DRF ValidationError (HTTP 400) if closed.
    Use this inside serializer.validate() or view methods.

    Args:
        transaction_date : Date to check
        company          : Company instance (None = default)
        levels           : List of levels to check (None = all)
        field_name       : Error dict key for DRF ValidationError

    Raises:
        serializers.ValidationError with HTTP 400 if period is closed
    """
    if not transaction_date:
        return  # No date provided — skip check

    result = PeriodChecker.check(
        transaction_date,
        company=company,
        levels=levels,
        raise_exception=False,
    )

    if result.is_closed:
        raise serializers.ValidationError({
            field_name: result.message,
            'period_closed': True,
            'blocked_level': result.level,
            'period_label':  result.period_label,
        })


def check_period_response(
    transaction_date,
    company=None,
    levels=None,
):
    """
    Validate period and return a DRF Response (HTTP 403) if closed, else None.
    Use this inside view methods:

        error = check_period_response(request.data.get('journal_date'))
        if error:
            return error

    Returns:
        Response with 403 if closed, None if open
    """
    if not transaction_date:
        return None

    result = PeriodChecker.check(
        transaction_date,
        company=company,
        levels=levels,
        raise_exception=False,
    )

    if result.is_closed:
        return Response(
            {
                'detail':        result.message,
                'period_closed': True,
                'blocked_level': result.level,
                'period_label':  result.period_label,
            },
            status=http_status.HTTP_403_FORBIDDEN,
        )
    return None


# ── Function Decorator ─────────────────────────────────────────────────────────

def period_required(date_field: str, levels=None, company_resolver=None):
    """
    Decorator for view methods (create, update, partial_update).
    Extracts date from request.data[date_field] and validates period.

    Args:
        date_field       : Key in request.data containing the transaction date
        levels           : List of levels to check (None = all)
        company_resolver : Callable(request) → Company (None = default company)

    Usage:
        @period_required(date_field='journal_date')
        def create(self, request, *args, **kwargs):
            ...

        @period_required(date_field='invoice_date', levels=['MONTHLY', 'ACCOUNTING'])
        def create(self, request, *args, **kwargs):
            ...
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self_or_view, request, *args, **kwargs):
            txn_date = _extract_date(request.data, date_field)

            company = None
            if company_resolver:
                company = company_resolver(request)

            if txn_date:
                result = PeriodChecker.check(
                    txn_date,
                    company=company,
                    levels=levels,
                    raise_exception=False,
                )
                if result.is_closed:
                    return Response(
                        {
                            'detail':        result.message,
                            'period_closed': True,
                            'blocked_level': result.level,
                            'period_label':  result.period_label,
                        },
                        status=http_status.HTTP_403_FORBIDDEN,
                    )

            return func(self_or_view, request, *args, **kwargs)
        return wrapper
    return decorator


# ── Class-Based View Mixin ────────────────────────────────────────────────────

class PeriodCheckMixin:
    """
    Mixin for DRF class-based views.
    Override period_date_field with the field name in request.data.

    Intercepts create(), update(), partial_update() automatically.

    Class Attributes:
        period_date_field  : str  — field name in request.data (required)
        period_levels      : list — levels to check, None = all
        period_strict      : bool — True = 404 if period not found, False = allow

    Usage:
        class JournalCreateView(PeriodCheckMixin, generics.CreateAPIView):
            period_date_field = 'journal_date'

        class InvoiceView(PeriodCheckMixin, generics.CreateAPIView):
            period_date_field = 'invoice_date'
            period_levels     = ['MONTHLY', 'ACCOUNTING']
    """
    period_date_field : str        = 'transaction_date'
    period_levels     : list | None = None
    period_strict     : bool       = False

    def _get_period_company(self):
        """Override to return specific company. Default: system default."""
        return None

    def _validate_period(self, request):
        """
        Run period check against request.data[period_date_field].
        Returns Response(403) if closed, None if allowed.
        """
        txn_date = _extract_date(request.data, self.period_date_field)
        if not txn_date:
            return None  # No date in payload — skip (field validator will catch missing)

        company = self._get_period_company()
        result  = PeriodChecker.check(
            txn_date,
            company=company,
            levels=self.period_levels,
            raise_exception=False,
        )

        if result.is_closed:
            logger.warning(
                '[PeriodCheckMixin] Blocked %s | view=%s | date=%s | level=%s',
                request.method,
                self.__class__.__name__,
                txn_date,
                result.level,
            )
            return Response(
                {
                    'detail':        result.message,
                    'period_closed': True,
                    'blocked_level': result.level,
                    'period_label':  result.period_label,
                },
                status=http_status.HTTP_403_FORBIDDEN,
            )
        return None

    def create(self, request, *args, **kwargs):
        error = self._validate_period(request)
        if error:
            return error
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        error = self._validate_period(request)
        if error:
            return error
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        error = self._validate_period(request)
        if error:
            return error
        return super().partial_update(request, *args, **kwargs)


# ── Serializer Mixin ──────────────────────────────────────────────────────────

class PeriodCheckSerializerMixin:
    """
    Mixin for DRF Serializers.
    Validates period during serializer.validate().

    Class Attributes:
        period_date_field : str  — field name in validated_data (required)
        period_levels     : list — levels to check, None = all
        period_error_field: str  — key for error in ValidationError response

    Usage:
        class JournalSerializer(PeriodCheckSerializerMixin, serializers.ModelSerializer):
            period_date_field = 'journal_date'

            class Meta:
                model  = Journal
                fields = '__all__'
    """
    period_date_field  : str        = 'transaction_date'
    period_levels      : list | None = None
    period_error_field : str        = 'transaction_date'

    def _get_period_company(self):
        """Override to return specific company."""
        return self.context.get('company', None)

    def validate(self, attrs):
        # Call parent validate first
        attrs = super().validate(attrs)

        txn_date = attrs.get(self.period_date_field)
        if txn_date:
            company = self._get_period_company()
            check_period_or_400(
                txn_date,
                company=company,
                levels=self.period_levels,
                field_name=self.period_error_field,
            )
        return attrs