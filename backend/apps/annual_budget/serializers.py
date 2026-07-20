"""
BFS ERP — Annual Budget Serializers
"""
from decimal import Decimal
from rest_framework import serializers
from .models import AnnualBudgetHeader, AnnualBudgetLine, AnnualBudgetLog
from apps.budget_component.models import BudgetComponent


MONTH_FIELDS = ['jan', 'feb', 'mar', 'apr', 'may', 'jun',
                'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
RELOC_FIELDS = ['jan_reloc', 'feb_reloc', 'mar_reloc', 'apr_reloc',
                'may_reloc', 'jun_reloc', 'jul_reloc', 'aug_reloc',
                'sep_reloc', 'oct_reloc', 'nov_reloc', 'dec_reloc']
MONTH_NAMES  = ['', 'January', 'February', 'March', 'April',
                'May', 'June', 'July', 'August',
                'September', 'October', 'November', 'December']


# ── Log ──────────────────────────────────────────────────────────────────────

class AnnualBudgetLogSerializer(serializers.ModelSerializer):
    changed_by_name = serializers.SerializerMethodField()
    month_name      = serializers.SerializerMethodField()

    class Meta:
        model  = AnnualBudgetLog
        fields = [
            'id', 'month', 'month_name',
            'old_value', 'new_value',
            'changed_by', 'changed_by_name',
            'changed_at', 'note',
        ]

    def get_changed_by_name(self, obj):
        if obj.changed_by:
            return obj.changed_by.full_name or obj.changed_by.username
        return None

    def get_month_name(self, obj):
        return MONTH_NAMES[obj.month] if 1 <= obj.month <= 12 else ''


# ── Line ─────────────────────────────────────────────────────────────────────

class AnnualBudgetLineSerializer(serializers.ModelSerializer):
    budget_component_name     = serializers.SerializerMethodField()
    budget_component_category = serializers.CharField(source='cost_category', read_only=True)
    total_annual              = serializers.DecimalField(
                                    max_digits=18, decimal_places=2, read_only=True)
    total_reloc               = serializers.DecimalField(
                                    max_digits=18, decimal_places=2, read_only=True)
    total_budget              = serializers.DecimalField(
                                    max_digits=18, decimal_places=2, read_only=True)

    # Monthly breakdown as structured list (for frontend table)
    months = serializers.SerializerMethodField()

    class Meta:
        model  = AnnualBudgetLine
        fields = [
            'id', 'header', 'cost_category', 'budget_component',
            'budget_component_name', 'budget_component_category',
            'order_no',
            # raw month fields
            'jan', 'feb', 'mar', 'apr', 'may', 'jun',
            'jul', 'aug', 'sep', 'oct', 'nov', 'dec',
            'jan_reloc', 'feb_reloc', 'mar_reloc', 'apr_reloc',
            'may_reloc', 'jun_reloc', 'jul_reloc', 'aug_reloc',
            'sep_reloc', 'oct_reloc', 'nov_reloc', 'dec_reloc',
            # computed
            'total_annual', 'total_reloc', 'total_budget',
            'months',
            'created_at', 'updated_at',
        ]

    def get_budget_component_name(self, obj):
        if obj.header.budget_type == obj.header.BudgetType.BANK_OBLIGATION:
            return obj.budget_component.custom_name if obj.budget_component else 'BANK OBLIGATION'
            
        dept_name = obj.header.department.name.upper() if obj.header.department else 'GLOBAL'
        cat_name = obj.get_cost_category_display().upper()
        return f"{cat_name} - {dept_name}"

    def get_months(self, obj):
        result = []
        for i, (mf, rf) in enumerate(zip(MONTH_FIELDS, RELOC_FIELDS), start=1):
            budget = getattr(obj, mf) or Decimal('0')
            reloc  = getattr(obj, rf) or Decimal('0')
            result.append({
                'month':      i,
                'month_name': MONTH_NAMES[i],
                'budget':     budget,
                'reloc':      reloc,
                'total':      budget + reloc,
            })
        return result


class AnnualBudgetLineWriteSerializer(serializers.ModelSerializer):
    budget_component = serializers.CharField(write_only=True, required=False)

    class Meta:
        model  = AnnualBudgetLine
        fields = [
            'id', 'header', 'cost_category', 'budget_component', 'order_no',
            'jan', 'feb', 'mar', 'apr', 'may', 'jun',
            'jul', 'aug', 'sep', 'oct', 'nov', 'dec',
        ]

    def validate(self, data):
        bc = data.pop('budget_component', None)
        if bc and not data.get('cost_category'):
            data['cost_category'] = bc
        return data


# ── Bulk month update (PATCH per bulan) ──────────────────────────────────────

class MonthlyBudgetUpdateSerializer(serializers.Serializer):
    """
    Used for PATCH /lines/<id>/update-month/
    Body: { "month": 6, "budget": 20000000.00, "note": "..." }
    """
    month  = serializers.IntegerField(min_value=1, max_value=12)
    budget = serializers.DecimalField(max_digits=18, decimal_places=2, min_value=Decimal('0'))
    note   = serializers.CharField(max_length=500, required=False, allow_blank=True)


# ── Header ───────────────────────────────────────────────────────────────────

class AnnualBudgetHeaderSerializer(serializers.ModelSerializer):
    department_name = serializers.SerializerMethodField()
    department_code = serializers.CharField(source='department.code', read_only=True, default='')
    total_annual    = serializers.SerializerMethodField()
    line_count      = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model  = AnnualBudgetHeader
        fields = [
            'id', 'company', 'budget_type', 'department', 'department_name', 'department_code',
            'year', 'notes', 'is_locked',
            'total_annual', 'line_count',
            'created_by', 'created_by_name',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['created_by']

    def get_department_name(self, obj):
        if obj.budget_type == obj.BudgetType.BANK_OBLIGATION:
            return 'Bank Obligation'
        return obj.department.name if obj.department else 'Global'

    def get_total_annual(self, obj):
        return sum(
            sum((getattr(line, f) or Decimal('0')) for f in MONTH_FIELDS)
            for line in obj.lines.all()
        )

    def get_line_count(self, obj):
        return obj.lines.count()

    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.full_name or obj.created_by.username
        return None


class AnnualBudgetHeaderDetailSerializer(AnnualBudgetHeaderSerializer):
    """Detail serializer yang menyertakan semua lines."""
    lines = AnnualBudgetLineSerializer(many=True, read_only=True)

    class Meta(AnnualBudgetHeaderSerializer.Meta):
        fields = AnnualBudgetHeaderSerializer.Meta.fields + ['lines']


from apps.organization.models import Company

class AnnualBudgetHeaderWriteSerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(),
        required=False,
        allow_null=True,
        default=None
    )

    class Meta:
        model  = AnnualBudgetHeader
        fields = ['id', 'company', 'budget_type', 'department', 'year', 'notes', 'is_locked']

    def validate(self, data):
        # Check if is_locked is being changed
        if 'is_locked' in data:
            request = self.context.get('request')
            if request and request.user:
                from apps.rbac.permissions import user_has_permission
                if not user_has_permission(request.user, 'FINANCE-ANNUAL-BUDGET', 'can_approve'):
                    raise serializers.ValidationError({
                        'is_locked': 'Anda tidak memiliki izin (Approve) untuk mengunci/membuka budget.'
                    })

        department = data.get('department')
        company    = data.get('company')

        if not company and department:
            company = department.company
            data['company'] = company

        if not company:
            company = Company.get_default()
            data['company'] = company

        if department and company:
            if department.company_id != company.id:
                raise serializers.ValidationError({
                    'department': 'Department tidak berasal dari company yang dipilih.'
                })

        # Check unique constraint manually to return a clean 400 Bad Request
        year = data.get('year')
        budget_type = data.get('budget_type')
        if year is None and self.instance:
            year = self.instance.year
        if budget_type is None and self.instance:
            budget_type = self.instance.budget_type
            
        if department is None and self.instance:
            department = self.instance.department

        if company and year:
            instance_id = self.instance.id if self.instance else None
            qs = AnnualBudgetHeader.objects.filter(
                company=company,
                year=year,
                budget_type=budget_type
            )
            if budget_type == 'STANDARD':
                if not department:
                    raise serializers.ValidationError({'department': 'Department wajib diisi untuk tipe budget Standard.'})
                qs = qs.filter(department=department)
                
            if instance_id:
                qs = qs.exclude(id=instance_id)
                
            if qs.exists():
                if budget_type == 'STANDARD':
                    raise serializers.ValidationError({
                        'non_field_errors': f'Annual budget untuk department {department.name} di tahun {year} sudah ada.'
                    })
                else:
                    raise serializers.ValidationError({
                        'non_field_errors': f'Annual budget Bank Obligation di tahun {year} sudah ada.'
                    })

        return data
