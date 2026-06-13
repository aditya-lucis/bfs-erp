"""
BFS ERP — Accounting: Financial Period Serializers
"""

import calendar
from rest_framework import serializers
from .models import (
    AnnualPeriod, QuarterPeriod, MonthlyPeriod,
    AccountingPeriod, PeriodActivityLog,
    PeriodStatus, MONTH_CHOICES, QUARTER_CHOICES,
)


# ─── Activity Log ─────────────────────────────────────────────────────────────

class PeriodActivityLogSerializer(serializers.ModelSerializer):
    actioned_by_name = serializers.SerializerMethodField()
    period_type_label = serializers.SerializerMethodField()
    action_label = serializers.SerializerMethodField()

    class Meta:
        model = PeriodActivityLog
        fields = [
            'id', 'period_type', 'period_type_label',
            'period_label', 'action', 'action_label',
            'reason', 'period_status_after',
            'actioned_by', 'actioned_by_name', 'actioned_at',
        ]

    def get_actioned_by_name(self, obj):
        if obj.actioned_by:
            return getattr(obj.actioned_by, 'full_name', None) or obj.actioned_by.username
        return None

    def get_period_type_label(self, obj):
        mapping = {
            'ANNUAL': 'Annual Period',
            'QUARTER': 'Quarter Period',
            'MONTHLY': 'Monthly Period',
            'ACCOUNTING': 'Accounting Period',
        }
        return mapping.get(obj.period_type, obj.period_type)

    def get_action_label(self, obj):
        return 'Open' if obj.action == PeriodStatus.OPEN else 'Close'


# ─── Toggle (Open/Close) Serializer ───────────────────────────────────────────

class PeriodToggleSerializer(serializers.Serializer):
    """Used for PATCH /toggle/ endpoint — requires a reason."""
    reason = serializers.CharField(min_length=3, max_length=500)


# ─── Annual Period ─────────────────────────────────────────────────────────────

class AnnualPeriodSerializer(serializers.ModelSerializer):
    status_label = serializers.SerializerMethodField()
    quarter_summary = serializers.SerializerMethodField()

    class Meta:
        model  = AnnualPeriod
        fields = ['id', 'year', 'status', 'status_label', 'quarter_summary', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_status_label(self, obj):
        return 'Open' if obj.status == PeriodStatus.OPEN else 'Close'

    def get_quarter_summary(self, obj):
        """Return Q1-Q4 status for this year."""
        quarters = {q.quarter: q.status for q in obj.quarters.all()}
        return {
            f'Q{i}': quarters.get(i, PeriodStatus.OPEN)
            for i in range(1, 5)
        }

    def validate_year(self, value):
        company = self.context['company']
        qs = AnnualPeriod.objects.filter(company=company, year=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(f'Annual period for year {value} already exists.')
        return value


# ─── Quarter Period ────────────────────────────────────────────────────────────

class QuarterPeriodSerializer(serializers.ModelSerializer):
    status_label   = serializers.SerializerMethodField()
    quarter_label  = serializers.CharField(read_only=True)
    month_statuses = serializers.SerializerMethodField()

    class Meta:
        model  = QuarterPeriod
        fields = [
            'id', 'year', 'quarter', 'quarter_label',
            'status', 'status_label', 'month_statuses',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'year', 'quarter', 'created_at', 'updated_at']

    def get_status_label(self, obj):
        return 'Open' if obj.status == PeriodStatus.OPEN else 'Close'

    def get_month_statuses(self, obj):
        return {
            m.month: m.status
            for m in obj.months.all()
        }


class AnnualPeriodWithQuartersSerializer(serializers.ModelSerializer):
    """For the Quarter Accounting Period view — one row per year, Q1–Q4 columns."""
    quarters = serializers.SerializerMethodField()
    status_label = serializers.SerializerMethodField()

    class Meta:
        model  = AnnualPeriod
        fields = ['id', 'year', 'status', 'status_label', 'quarters']

    def get_status_label(self, obj):
        return 'Open' if obj.status == PeriodStatus.OPEN else 'Close'

    def get_quarters(self, obj):
        qs = obj.quarters.order_by('quarter')
        return [
            {
                'id': q.id,
                'quarter': q.quarter,
                'quarter_label': f'Q{q.quarter}',
                'status': q.status,
                'status_label': 'Open' if q.status == PeriodStatus.OPEN else 'Close',
            }
            for q in qs
        ]


# ─── Monthly Period ────────────────────────────────────────────────────────────

class MonthlyPeriodSerializer(serializers.ModelSerializer):
    status_label = serializers.SerializerMethodField()
    month_name   = serializers.CharField(read_only=True)

    class Meta:
        model  = MonthlyPeriod
        fields = [
            'id', 'year', 'month', 'month_name',
            'status', 'status_label',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'year', 'month', 'created_at', 'updated_at']

    def get_status_label(self, obj):
        return 'Open' if obj.status == PeriodStatus.OPEN else 'Close'


class AnnualPeriodWithMonthsSerializer(serializers.ModelSerializer):
    """For the Monthly Accounting Period view — one row per year, 12 month columns."""
    months = serializers.SerializerMethodField()
    status_label = serializers.SerializerMethodField()

    class Meta:
        model  = AnnualPeriod
        fields = ['id', 'year', 'status', 'status_label', 'months']

    def get_status_label(self, obj):
        return 'Open' if obj.status == PeriodStatus.OPEN else 'Close'

    def get_months(self, obj):
        qs = {m.month: m for m in obj.months.order_by('month')}
        month_names = dict(MONTH_CHOICES)
        return [
            {
                'id': qs[i].id if i in qs else None,
                'month': i,
                'month_name': month_names[i],
                'month_abbr': month_names[i][:3],
                'status': qs[i].status if i in qs else None,
                'status_label': ('Open' if qs[i].status == PeriodStatus.OPEN else 'Close') if i in qs else '-',
            }
            for i in range(1, 13)
        ]


# ─── Accounting Period ─────────────────────────────────────────────────────────

class AccountingPeriodSerializer(serializers.ModelSerializer):
    month_name   = serializers.CharField(read_only=True)
    status_label = serializers.SerializerMethodField()

    class Meta:
        model  = AccountingPeriod
        fields = [
            'id', 'year', 'month', 'month_name',
            'start_date', 'end_date',
            'status', 'status_label',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'year', 'month', 'start_date', 'end_date',
            'created_at', 'updated_at',
        ]

    def get_status_label(self, obj):
        return 'No' if obj.status == PeriodStatus.CLOSE else 'Yes'