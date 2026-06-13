"""
BFS ERP — Accounting: Financial Period Views

Endpoints:
    Annual:
        GET    /api/v1/accounting/periods/annual/              list
        POST   /api/v1/accounting/periods/annual/              add new year (auto-generates quarters + months)
        PATCH  /api/v1/accounting/periods/annual/<id>/toggle/  open/close (with reason)
        GET    /api/v1/accounting/periods/annual/<id>/logs/    activity log for this year

    Quarter:
        GET    /api/v1/accounting/periods/quarter/             list (grouped by year, Q1–Q4)
        PATCH  /api/v1/accounting/periods/quarter/<id>/toggle/ open/close (with reason)
        GET    /api/v1/accounting/periods/quarter/<id>/logs/   activity log

    Monthly:
        GET    /api/v1/accounting/periods/monthly/             list (grouped by year, 12 months)
        PATCH  /api/v1/accounting/periods/monthly/<id>/toggle/ open/close (with reason)
        GET    /api/v1/accounting/periods/monthly/<id>/logs/   activity log

    Accounting Period:
        GET    /api/v1/accounting/periods/accounting/          flat list (start_date, end_date, status)
        PATCH  /api/v1/accounting/periods/accounting/<id>/toggle/ open/close (with reason)
        GET    /api/v1/accounting/periods/accounting/<id>/logs/   activity log

    Global Log:
        GET    /api/v1/accounting/periods/logs/                all logs (filterable by period_type)
"""

import calendar
from datetime import date

from django.shortcuts import get_object_or_404
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.organization.models import Company
from apps.rbac.permissions import HasFunctionPermission

from .models import (
    AnnualPeriod, QuarterPeriod, MonthlyPeriod,
    AccountingPeriod, PeriodActivityLog, PeriodStatus,
    MONTH_CHOICES,
)
from .serielizers import (
    AnnualPeriodSerializer,
    AnnualPeriodWithQuartersSerializer,
    AnnualPeriodWithMonthsSerializer,
    QuarterPeriodSerializer,
    MonthlyPeriodSerializer,
    AccountingPeriodSerializer,
    PeriodActivityLogSerializer,
    PeriodToggleSerializer,
)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def get_company(request):
    return Company.get_default()


def _log(company, period_type, obj, action, reason, user, period_label):
    """Create a PeriodActivityLog entry."""
    kwargs = dict(
        company=company,
        period_type=period_type,
        action=action,
        reason=reason,
        period_label=period_label,
        period_status_after=action,
        actioned_by=user,
    )
    if period_type == 'ANNUAL':
        kwargs['annual_period'] = obj
    elif period_type == 'QUARTER':
        kwargs['quarter_period'] = obj
    elif period_type == 'MONTHLY':
        kwargs['monthly_period'] = obj
    elif period_type == 'ACCOUNTING':
        kwargs['accounting_period'] = obj

    PeriodActivityLog.objects.create(**kwargs)


def _generate_periods_for_year(company, annual, user):
    """
    Auto-generate QuarterPeriod, MonthlyPeriod, and AccountingPeriod
    records for a newly created AnnualPeriod.
    """
    year = annual.year

    # Quarter mapping: Q1=1-3, Q2=4-6, Q3=7-9, Q4=10-12
    quarter_map = {1: (1, 3), 2: (4, 6), 3: (7, 9), 4: (10, 12)}
    quarters = {}
    for q_num in range(1, 5):
        qp = QuarterPeriod.objects.create(
            company=company,
            annual_period=annual,
            year=year,
            quarter=q_num,
            status=PeriodStatus.OPEN,
            created_by=user,
        )
        quarters[q_num] = qp

    # Monthly periods
    for month_num in range(1, 13):
        q_num = (month_num - 1) // 3 + 1
        _, last_day = calendar.monthrange(year, month_num)
        start_dt = date(year, month_num, 1)
        end_dt   = date(year, month_num, last_day)

        mp = MonthlyPeriod.objects.create(
            company=company,
            annual_period=annual,
            quarter_period=quarters[q_num],
            year=year,
            month=month_num,
            status=PeriodStatus.OPEN,
            created_by=user,
        )

        AccountingPeriod.objects.create(
            company=company,
            monthly_period=mp,
            year=year,
            month=month_num,
            start_date=start_dt,
            end_date=end_dt,
            status=PeriodStatus.OPEN,
            created_by=user,
        )
def _heal_periods(company):
    """
    Heal dirty database state: if an AnnualPeriod is closed, 
    all its sub-periods (quarters, months, accounting periods) must be CLOSE.
    If an AnnualPeriod is open, and is NOT the only open year (e.g. dirty data from before),
    we should keep only the latest year open and close the rest.
    """
    # 1. Enforce only one open annual period at a time
    open_years = AnnualPeriod.objects.filter(company=company, status=PeriodStatus.OPEN).order_by('-year')
    if open_years.count() > 1:
        active_year = open_years.first()
        other_years = open_years[1:]
        for yr in other_years:
            yr.status = PeriodStatus.CLOSE
            yr.save()
            
            # Cascade close
            yr.quarters.all().update(status=PeriodStatus.CLOSE)
            yr.months.all().update(status=PeriodStatus.CLOSE)
            AccountingPeriod.objects.filter(monthly_period__annual_period=yr).update(status=PeriodStatus.CLOSE)
            
            _log(company, 'ANNUAL', yr, PeriodStatus.CLOSE,
                 '[AUTO-HEAL] Closed to enforce single active year rule.',
                 None, str(yr.year))

    # 2. Cascade close to all sub-periods of CLOSED years
    closed_years = AnnualPeriod.objects.filter(company=company, status=PeriodStatus.CLOSE)
    for yr in closed_years:
        # Close any open quarters
        yr.quarters.filter(status=PeriodStatus.OPEN).update(status=PeriodStatus.CLOSE)
        # Close any open months
        yr.months.filter(status=PeriodStatus.OPEN).update(status=PeriodStatus.CLOSE)
        # Close any open accounting periods
        AccountingPeriod.objects.filter(monthly_period__annual_period=yr).exclude(status=PeriodStatus.CLOSE).update(status=PeriodStatus.CLOSE)


# ─── Annual Period Views ───────────────────────────────────────────────────────

class AnnualPeriodListCreateView(APIView):
    """
    GET  → list all annual periods for this company
    POST → add a new fiscal year (auto-generates quarters + months)
    """
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'GL-PERIOD-ANNUAL'

    def get(self, request):
        company = get_company(request)
        _heal_periods(company)
        qs = AnnualPeriod.objects.filter(company=company).prefetch_related(
            'quarters', 'months'
        ).order_by('-year')
        serializer = AnnualPeriodSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        company = get_company(request)
        serializer = AnnualPeriodSerializer(
            data=request.data,
            context={'request': request, 'company': company},
        )
        serializer.is_valid(raise_exception=True)
        year = serializer.validated_data['year']

        # Check duplicate
        if AnnualPeriod.objects.filter(company=company, year=year).exists():
            return Response(
                {'detail': f'Annual period for year {year} already exists.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        annual = AnnualPeriod.objects.create(
            company=company,
            year=year,
            status=PeriodStatus.OPEN,
            created_by=request.user,
        )
        _generate_periods_for_year(company, annual, request.user)

        # Log creation
        _log(company, 'ANNUAL', annual, PeriodStatus.OPEN,
             f'New annual period {year} created.', request.user, str(year))

        return Response(
            AnnualPeriodSerializer(annual, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


class AnnualPeriodToggleView(APIView):
    """
    PATCH /api/v1/accounting/periods/annual/<id>/toggle/
    Toggle open ↔ close with a required reason.
    """
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'GL-PERIOD-ANNUAL'

    def patch(self, request, pk):
        from django.db import transaction
        company = get_company(request)
        annual  = get_object_or_404(AnnualPeriod, pk=pk, company=company)

        ser = PeriodToggleSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        reason = ser.validated_data['reason']

        new_status = (
            PeriodStatus.CLOSE if annual.status == PeriodStatus.OPEN else PeriodStatus.OPEN
        )

        with transaction.atomic():
            if new_status == PeriodStatus.OPEN:
                # Close all other annual periods and their sub-periods
                other_open_years = AnnualPeriod.objects.filter(company=company, status=PeriodStatus.OPEN).exclude(pk=annual.pk)
                for other_yr in other_open_years:
                    other_yr.status = PeriodStatus.CLOSE
                    other_yr.save()
                    
                    # Cascade close to sub-periods
                    other_yr.quarters.all().update(status=PeriodStatus.CLOSE)
                    other_yr.months.all().update(status=PeriodStatus.CLOSE)
                    AccountingPeriod.objects.filter(monthly_period__annual_period=other_yr).update(status=PeriodStatus.CLOSE)
                    
                    _log(company, 'ANNUAL', other_yr, PeriodStatus.CLOSE, 
                         f'[AUTO-CLOSE] Closed because year {annual.year} was activated.', 
                         request.user, str(other_yr.year))
                
                # Open this annual period and all of its sub-periods
                annual.status = PeriodStatus.OPEN
                annual.save()
                
                annual.quarters.all().update(status=PeriodStatus.OPEN)
                annual.months.all().update(status=PeriodStatus.OPEN)
                AccountingPeriod.objects.filter(monthly_period__annual_period=annual).update(status=PeriodStatus.OPEN)
                
                _log(company, 'ANNUAL', annual, PeriodStatus.OPEN, reason, request.user, str(annual.year))
            else:
                # Close this annual period and all of its sub-periods
                annual.status = PeriodStatus.CLOSE
                annual.save()
                
                annual.quarters.all().update(status=PeriodStatus.CLOSE)
                annual.months.all().update(status=PeriodStatus.CLOSE)
                AccountingPeriod.objects.filter(monthly_period__annual_period=annual).update(status=PeriodStatus.CLOSE)
                
                _log(company, 'ANNUAL', annual, PeriodStatus.CLOSE, reason, request.user, str(annual.year))

        return Response(
            AnnualPeriodSerializer(annual, context={'request': request}).data
        )


class AnnualPeriodLogsView(generics.ListAPIView):
    """GET /api/v1/accounting/periods/annual/<id>/logs/"""
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'GL-PERIOD-ANNUAL'
    serializer_class   = PeriodActivityLogSerializer
    pagination_class   = None

    def get_queryset(self):
        company = get_company(self.request)
        return PeriodActivityLog.objects.filter(
            company=company,
            period_type='ANNUAL',
            annual_period_id=self.kwargs['pk'],
        ).select_related('actioned_by').order_by('-actioned_at')


# ─── Quarter Period Views ──────────────────────────────────────────────────────

class QuarterPeriodListView(APIView):
    """
    GET /api/v1/accounting/periods/quarter/
    Returns list grouped by year with Q1-Q4 status per row.
    """
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'GL-PERIOD-QUARTER'

    def get(self, request):
        company = get_company(request)
        _heal_periods(company)
        annuals = AnnualPeriod.objects.filter(company=company).prefetch_related(
            'quarters'
        ).order_by('-year')
        serializer = AnnualPeriodWithQuartersSerializer(annuals, many=True)
        return Response(serializer.data)


class QuarterPeriodToggleView(APIView):
    """
    PATCH /api/v1/accounting/periods/quarter/<id>/toggle/
    """
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'GL-PERIOD-QUARTER'

    def patch(self, request, pk):
        company = get_company(request)
        quarter = get_object_or_404(QuarterPeriod, pk=pk, company=company)

        ser = PeriodToggleSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        reason = ser.validated_data['reason']

        new_status = (
            PeriodStatus.CLOSE if quarter.status == PeriodStatus.OPEN else PeriodStatus.OPEN
        )

        if new_status == PeriodStatus.OPEN and quarter.annual_period.status == PeriodStatus.CLOSE:
            return Response(
                {'detail': f'Cannot open quarter period because the fiscal year {quarter.year} is closed. Please open the annual period first.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        quarter.status = new_status
        quarter.save()

        label = f'{quarter.year} Q{quarter.quarter}'
        _log(company, 'QUARTER', quarter, new_status, reason, request.user, label)

        return Response(QuarterPeriodSerializer(quarter).data)


class QuarterPeriodLogsView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'GL-PERIOD-QUARTER'
    serializer_class   = PeriodActivityLogSerializer
    pagination_class   = None

    def get_queryset(self):
        company = get_company(self.request)
        return PeriodActivityLog.objects.filter(
            company=company,
            period_type='QUARTER',
            quarter_period_id=self.kwargs['pk'],
        ).select_related('actioned_by').order_by('-actioned_at')


# ─── Monthly Period Views ──────────────────────────────────────────────────────

class MonthlyPeriodListView(APIView):
    """
    GET /api/v1/accounting/periods/monthly/
    Returns list grouped by year with Jan-Dec status columns.
    """
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'GL-PERIOD-MONTHLY'

    def get(self, request):
        company = get_company(request)
        _heal_periods(company)
        annuals = AnnualPeriod.objects.filter(company=company).prefetch_related(
            'months'
        ).order_by('-year')
        serializer = AnnualPeriodWithMonthsSerializer(annuals, many=True)
        return Response(serializer.data)


class MonthlyPeriodToggleView(APIView):
    """
    PATCH /api/v1/accounting/periods/monthly/<id>/toggle/
    """
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'GL-PERIOD-MONTHLY'

    def patch(self, request, pk):
        company = get_company(request)
        monthly = get_object_or_404(MonthlyPeriod, pk=pk, company=company)

        ser = PeriodToggleSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        reason = ser.validated_data['reason']

        new_status = (
            PeriodStatus.CLOSE if monthly.status == PeriodStatus.OPEN else PeriodStatus.OPEN
        )

        if new_status == PeriodStatus.OPEN and monthly.annual_period.status == PeriodStatus.CLOSE:
            return Response(
                {'detail': f'Cannot open monthly period because the fiscal year {monthly.year} is closed. Please open the annual period first.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        monthly.status = new_status
        monthly.save()

        # Sync AccountingPeriod
        try:
            ap = monthly.accounting_period
            ap.status = new_status
            ap.save()
        except AccountingPeriod.DoesNotExist:
            pass

        label = f'{monthly.month_name} {monthly.year}'
        _log(company, 'MONTHLY', monthly, new_status, reason, request.user, label)

        return Response(MonthlyPeriodSerializer(monthly).data)


class MonthlyPeriodLogsView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'GL-PERIOD-MONTHLY'
    serializer_class   = PeriodActivityLogSerializer
    pagination_class   = None

    def get_queryset(self):
        company = get_company(self.request)
        return PeriodActivityLog.objects.filter(
            company=company,
            period_type='MONTHLY',
            monthly_period_id=self.kwargs['pk'],
        ).select_related('actioned_by').order_by('-actioned_at')


# ─── Accounting Period Views ───────────────────────────────────────────────────

class AccountingPeriodListView(generics.ListAPIView):
    """
    GET /api/v1/accounting/periods/accounting/
    Flat list — start_date, end_date, month name, year, status (close = Yes / No).
    Supports ?search=, ?year=, ?status=OPEN|CLOSE
    """
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'GL-PERIOD-ACCOUNTING'
    serializer_class   = AccountingPeriodSerializer
    pagination_class   = None

    def get_queryset(self):
        company = get_company(self.request)
        _heal_periods(company)
        qs = AccountingPeriod.objects.filter(company=company).select_related(
            'monthly_period'
        ).order_by('-year', '-month')

        params = self.request.query_params
        if year := params.get('year'):
            qs = qs.filter(year=year)
        if s := params.get('status'):
            qs = qs.filter(status=s.upper())

        return qs


class AccountingPeriodToggleView(APIView):
    """
    PATCH /api/v1/accounting/periods/accounting/<id>/toggle/
    """
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'GL-PERIOD-ACCOUNTING'

    def patch(self, request, pk):
        company = get_company(request)
        ap = get_object_or_404(AccountingPeriod, pk=pk, company=company)

        ser = PeriodToggleSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        reason = ser.validated_data['reason']

        new_status = (
            PeriodStatus.CLOSE if ap.status == PeriodStatus.OPEN else PeriodStatus.OPEN
        )

        if new_status == PeriodStatus.OPEN and ap.monthly_period.annual_period.status == PeriodStatus.CLOSE:
            return Response(
                {'detail': f'Cannot open accounting period because the fiscal year {ap.year} is closed. Please open the annual period first.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ap.status = new_status
        ap.save()

        # Sync MonthlyPeriod
        ap.monthly_period.status = new_status
        ap.monthly_period.save()

        label = f'{ap.month_name} {ap.year}'
        _log(company, 'ACCOUNTING', ap, new_status, reason, request.user, label)

        return Response(AccountingPeriodSerializer(ap).data)


class AccountingPeriodLogsView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'GL-PERIOD-ACCOUNTING'
    serializer_class   = PeriodActivityLogSerializer
    pagination_class   = None

    def get_queryset(self):
        company = get_company(self.request)
        return PeriodActivityLog.objects.filter(
            company=company,
            period_type='ACCOUNTING',
            accounting_period_id=self.kwargs['pk'],
        ).select_related('actioned_by').order_by('-actioned_at')


# ─── Global Log View ───────────────────────────────────────────────────────────

class PeriodActivityLogListView(generics.ListAPIView):
    """
    GET /api/v1/accounting/periods/logs/
    All logs for this company. Filter by ?period_type=ANNUAL|QUARTER|MONTHLY|ACCOUNTING
    """
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'GL-PERIOD-LOG'
    serializer_class   = PeriodActivityLogSerializer
    pagination_class   = None

    def get_queryset(self):
        company = get_company(self.request)
        qs = PeriodActivityLog.objects.filter(company=company).select_related(
            'actioned_by'
        ).order_by('-actioned_at')

        if pt := self.request.query_params.get('period_type'):
            qs = qs.filter(period_type=pt.upper())

        return qs