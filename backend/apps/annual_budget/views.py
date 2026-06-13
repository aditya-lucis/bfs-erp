"""
BFS ERP — Annual Budget Views
apps/annual_budget/views.py

Endpoints:
    GET/POST   /api/v1/annual-budget/headers/
    GET/PUT    /api/v1/annual-budget/headers/<pk>/
    GET        /api/v1/annual-budget/headers/<pk>/detail/   (with lines)
    GET/POST   /api/v1/annual-budget/lines/
    GET/PUT    /api/v1/annual-budget/lines/<pk>/
    PATCH      /api/v1/annual-budget/lines/<pk>/update-month/
    GET        /api/v1/annual-budget/lines/<pk>/logs/
    POST       /api/v1/annual-budget/headers/<pk>/init-lines/
    GET        /api/v1/annual-budget/budget-components/?department=<id>&year=<year>
"""
import logging
from decimal import Decimal

from django.db import transaction
from rest_framework import generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.rbac.permissions import HasFunctionPermission

from apps.organization.models import Company
from apps.budget_component.models import BudgetComponent

from .models import AnnualBudgetHeader, AnnualBudgetLine, AnnualBudgetLog
from .serializers import (
    AnnualBudgetHeaderSerializer,
    AnnualBudgetHeaderDetailSerializer,
    AnnualBudgetHeaderWriteSerializer,
    AnnualBudgetLineSerializer,
    AnnualBudgetLineWriteSerializer,
    AnnualBudgetLogSerializer,
    MonthlyBudgetUpdateSerializer,
)

logger = logging.getLogger(__name__)

MONTH_FIELDS = ['jan', 'feb', 'mar', 'apr', 'may', 'jun',
                'jul', 'aug', 'sep', 'oct', 'nov', 'dec']


# ── Header List / Create ──────────────────────────────────────────────────────

class AnnualBudgetHeaderListView(generics.ListCreateAPIView):
    """
    GET  /annual-budget/headers/?year=2026&department=5
    POST /annual-budget/headers/
    """
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'FINANCE-ANNUAL-BUDGET'

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AnnualBudgetHeaderWriteSerializer
        return AnnualBudgetHeaderSerializer

    def get_queryset(self):
        qs = AnnualBudgetHeader.objects.select_related(
            'company', 'department', 'created_by'
        ).prefetch_related('lines')

        year = self.request.query_params.get('year')
        dept = self.request.query_params.get('department')

        if year:
            qs = qs.filter(year=year)
        if dept:
            qs = qs.filter(department_id=dept)

        return qs

    def perform_create(self, serializer):
        # Auto-set company to default if not provided
        company = serializer.validated_data.get('company') or Company.get_default()
        serializer.save(created_by=self.request.user, company=company)


# ── Header Retrieve / Update / Delete ────────────────────────────────────────

class AnnualBudgetHeaderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET/PUT/PATCH/DELETE /annual-budget/headers/<pk>/
    """
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'FINANCE-ANNUAL-BUDGET'
    queryset           = AnnualBudgetHeader.objects.select_related(
                             'company', 'department', 'created_by'
                         ).prefetch_related('lines')

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return AnnualBudgetHeaderWriteSerializer
        return AnnualBudgetHeaderDetailSerializer

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.is_locked:
            return Response(
                {'detail': 'Budget sudah dikunci, tidak bisa dihapus.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)


# ── Init Lines from BudgetComponents ─────────────────────────────────────────

class InitBudgetLinesView(APIView):
    """
    POST /annual-budget/headers/<pk>/init-lines/

    Auto-create AnnualBudgetLine untuk setiap active CostCategory.
    Idempotent (skip jika sudah ada).
    """
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'FINANCE-ANNUAL-BUDGET'

    def post(self, request, pk):
        try:
            header = AnnualBudgetHeader.objects.get(pk=pk)
        except AnnualBudgetHeader.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        if header.is_locked:
            return Response(
                {'detail': 'Budget sudah dikunci.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        created_count  = 0
        skipped_count  = 0

        with transaction.atomic():
            for i, (cat_val, cat_label) in enumerate(BudgetComponent.CostCategory.choices):
                line, created = AnnualBudgetLine.objects.get_or_create(
                    header=header,
                    cost_category=cat_val,
                    defaults={'order_no': i + 1},
                )
                if created:
                    created_count += 1
                else:
                    skipped_count += 1

        return Response({
            'detail': f'{created_count} baris ditambahkan, {skipped_count} sudah ada.',
            'created': created_count,
            'skipped': skipped_count,
        })


# ── Budget Component Picker ───────────────────────────────────────────────────

class BudgetComponentPickerView(APIView):
    """
    GET /annual-budget/budget-components/?department=<id>&header=<header_id>
    """
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'FINANCE-ANNUAL-BUDGET'

    def get(self, request):
        header_id = request.query_params.get('header')

        if not header_id:
            return Response(
                {'detail': 'Query param "header" diperlukan.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            header = AnnualBudgetHeader.objects.select_related('department').get(id=header_id)
        except AnnualBudgetHeader.DoesNotExist:
            return Response({'detail': 'Header not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Exclude yang sudah ada di header
        existing = AnnualBudgetLine.objects.filter(
            header=header
        ).values_list('cost_category', flat=True)

        data = []
        for cat_val, cat_label in BudgetComponent.CostCategory.choices:
            if cat_val not in existing:
                data.append({
                    'id':            cat_val,
                    'name':          f"{cat_label.upper()} - {header.department.name.upper()}",
                    'cost_category': cat_val,
                    'order_no':      0,
                })

        return Response(data)


# ── Line List / Create ────────────────────────────────────────────────────────

class AnnualBudgetLineListView(generics.ListCreateAPIView):
    """
    GET  /annual-budget/lines/?header=<id>
    POST /annual-budget/lines/
    """
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'FINANCE-ANNUAL-BUDGET'

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AnnualBudgetLineWriteSerializer
        return AnnualBudgetLineSerializer

    def get_queryset(self):
        qs = AnnualBudgetLine.objects.select_related(
            'header__department'
        )
        header_id = self.request.query_params.get('header')
        if header_id:
            qs = qs.filter(header_id=header_id)
        return qs.order_by('order_no', 'id')

    def perform_create(self, serializer):
        header = serializer.validated_data.get('header')
        if header and header.is_locked:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'header': 'Budget sudah dikunci.'})
        serializer.save()


# ── Line Retrieve / Update / Delete ──────────────────────────────────────────

class AnnualBudgetLineDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET/PUT/PATCH/DELETE /annual-budget/lines/<pk>/
    """
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'FINANCE-ANNUAL-BUDGET'
    queryset           = AnnualBudgetLine.objects.select_related(
                             'header__department'
                         )

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return AnnualBudgetLineWriteSerializer
        return AnnualBudgetLineSerializer

    def destroy(self, request, *args, **kwargs):
        line = self.get_object()
        if line.header.is_locked:
            return Response(
                {'detail': 'Budget sudah dikunci.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)


# ── Update Single Month Value ─────────────────────────────────────────────────

class UpdateMonthBudgetView(APIView):
    """
    PATCH /annual-budget/lines/<pk>/update-month/

    Body: { "month": 6, "budget": 20000000.00, "note": "Revisi" }
    Updates one month's budget and creates an audit log entry.
    """
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'FINANCE-ANNUAL-BUDGET'

    def patch(self, request, pk):
        try:
            line = AnnualBudgetLine.objects.select_related('header').get(pk=pk)
        except AnnualBudgetLine.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        if line.header.is_locked:
            return Response(
                {'detail': 'Budget sudah dikunci.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = MonthlyBudgetUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        month      = serializer.validated_data['month']
        new_value  = serializer.validated_data['budget']
        note       = serializer.validated_data.get('note', '')
        field_name = MONTH_FIELDS[month - 1]

        old_value = getattr(line, field_name) or Decimal('0')

        with transaction.atomic():
            setattr(line, field_name, new_value)
            line.save(update_fields=[field_name, 'updated_at'])

            # Log the change
            AnnualBudgetLog.objects.create(
                line=line,
                month=month,
                old_value=old_value,
                new_value=new_value,
                changed_by=request.user,
                note=note,
            )

        logger.info(
            '[AnnualBudget] Line %s month %s: %s → %s by %s',
            line.id, month, old_value, new_value, request.user,
        )

        return Response(AnnualBudgetLineSerializer(line).data)


# ── Bulk Update All Months for a Line ────────────────────────────────────────

class BulkUpdateMonthsView(APIView):
    """
    PATCH /annual-budget/lines/<pk>/bulk-update/

    Body: {
        "months": [
            { "month": 1, "budget": 5000000 },
            { "month": 2, "budget": 6000000 },
            ...
        ],
        "note": "Input awal"
    }
    """
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'FINANCE-ANNUAL-BUDGET'

    def patch(self, request, pk):
        try:
            line = AnnualBudgetLine.objects.select_related('header').get(pk=pk)
        except AnnualBudgetLine.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        if line.header.is_locked:
            return Response(
                {'detail': 'Budget sudah dikunci.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        months_data = request.data.get('months', [])
        note        = request.data.get('note', '')

        if not months_data or not isinstance(months_data, list):
            return Response(
                {'detail': '"months" harus berupa list.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        update_fields = ['updated_at']
        logs_to_create = []

        with transaction.atomic():
            for item in months_data:
                month = item.get('month')
                budget_val = item.get('budget', 0)

                if not isinstance(month, int) or not (1 <= month <= 12):
                    continue

                field_name = MONTH_FIELDS[month - 1]
                try:
                    new_value = Decimal(str(budget_val))
                except Exception:
                    continue

                old_value = getattr(line, field_name) or Decimal('0')
                setattr(line, field_name, new_value)
                update_fields.append(field_name)

                logs_to_create.append(AnnualBudgetLog(
                    line=line,
                    month=month,
                    old_value=old_value,
                    new_value=new_value,
                    changed_by=request.user,
                    note=note,
                ))

            line.save(update_fields=list(set(update_fields)))
            AnnualBudgetLog.objects.bulk_create(logs_to_create)

        return Response(AnnualBudgetLineSerializer(line).data)


# ── Line Logs ─────────────────────────────────────────────────────────────────

class AnnualBudgetLineLogsView(generics.ListAPIView):
    """
    GET /annual-budget/lines/<pk>/logs/
    """
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'FINANCE-ANNUAL-BUDGET'
    serializer_class   = AnnualBudgetLogSerializer

    def get_queryset(self):
        return AnnualBudgetLog.objects.filter(
            line_id=self.kwargs['pk']
        ).select_related('changed_by').order_by('-changed_at')


# ── Summary / Overview ────────────────────────────────────────────────────────

class AnnualBudgetSummaryView(APIView):
    """
    GET /annual-budget/summary/?year=2026

    Returns per-department budget totals for a given year.
    """
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'FINANCE-ANNUAL-BUDGET'

    def get(self, request):
        year = request.query_params.get('year')
        if not year:
            from datetime import date
            year = date.today().year

        try:
            year = int(year)
        except (ValueError, TypeError):
            return Response({'detail': 'Invalid year.'}, status=status.HTTP_400_BAD_REQUEST)

        headers = AnnualBudgetHeader.objects.filter(
            year=year
        ).select_related('department').prefetch_related(
            'lines'
        ).order_by('department__name')

        data = []
        for h in headers:
            total = sum(
                sum((getattr(line, f) or Decimal('0')) for f in MONTH_FIELDS)
                for line in h.lines.all()
            )
            data.append({
                'id':              h.id,
                'department':      h.department_id,
                'department_name': h.department.name,
                'department_code': h.department.code,
                'year':            h.year,
                'total_annual':    total,
                'line_count':      h.lines.count(),
                'is_locked':       h.is_locked,
            })

        return Response({
            'year':       year,
            'results':    data,
            'grand_total': sum(d['total_annual'] for d in data),
        })
