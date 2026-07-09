"""
BFS ERP — Accounting: Chart of Account Serializers
"""

from rest_framework import serializers
from .models import Account, AccountGroup, AccountType, BankType, DefaultPosition


# ─── Account Group ────────────────────────────────────────────────────────────

class AccountGroupSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(source='total_amount', read_only=True, max_digits=18, decimal_places=2)

    class Meta:
        model  = AccountGroup
        fields = [
            'id', 'code', 'name', 'number_prefix',
            'default_position', 'order', 'is_active',
            'amount',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'amount', 'created_at', 'updated_at']

    def validate_code(self, value):
        qs = AccountGroup.objects.filter(
            company=self.context['company'],  
            code=value,
        )
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('Account group code already exists.')
        return value


# ─── Account (COA) ───────────────────────────────────────────────────────────

class AccountListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list view (flat, no children)."""
    account_group_name = serializers.CharField(source='account_group.name', read_only=True)
    account_group_code = serializers.CharField(source='account_group.code', read_only=True)
    parent_number      = serializers.CharField(source='parent.account_number', read_only=True)
    account_type_label = serializers.CharField(source='get_account_type_display', read_only=True)
    is_postable        = serializers.BooleanField(read_only=True)
    level              = serializers.IntegerField(read_only=True)
    amount             = serializers.DecimalField(source='computed_amount', read_only=True, max_digits=18, decimal_places=2)
    month_opening_balance = serializers.DecimalField(read_only=True, max_digits=18, decimal_places=2)
    month_debet        = serializers.DecimalField(source='computed_month_debet', read_only=True, max_digits=18, decimal_places=2)
    month_kredit       = serializers.DecimalField(source='computed_month_kredit', read_only=True, max_digits=18, decimal_places=2)

    class Meta:
        model  = Account
        fields = [
            'id', 'account_number', 'account_name',
            'account_type', 'account_type_label',
            'account_group', 'account_group_name', 'account_group_code',
            'parent', 'parent_number',
            'default_position', 'currency', 'amount',
            'month_opening_balance', 'month_debet', 'month_kredit',
            'is_postable', 'is_linked', 'is_active',
            'bank_type', 'level',
        ]


class AccountTreeSerializer(serializers.ModelSerializer):
    """Recursive serializer for tree view."""
    children           = serializers.SerializerMethodField()
    account_type_label = serializers.CharField(source='get_account_type_display', read_only=True)
    is_postable        = serializers.BooleanField(read_only=True)
    level              = serializers.IntegerField(read_only=True)
    amount             = serializers.DecimalField(source='computed_amount', read_only=True, max_digits=18, decimal_places=2)
    month_opening_balance = serializers.DecimalField(read_only=True, max_digits=18, decimal_places=2)
    month_debet        = serializers.DecimalField(source='computed_month_debet', read_only=True, max_digits=18, decimal_places=2)
    month_kredit       = serializers.DecimalField(source='computed_month_kredit', read_only=True, max_digits=18, decimal_places=2)

    class Meta:
        model  = Account
        fields = [
            'id', 'account_number', 'account_name',
            'account_type', 'account_type_label',
            'account_group', 'parent',
            'is_inter_company', 'is_cost_component', 'is_on_duty',
            'default_position', 'currency', 'amount',
            'month_opening_balance', 'month_debet', 'month_kredit',
            'is_postable', 'is_linked', 'is_active',
            'bank_type', 'level', 'children',
        ]

    def get_children(self, obj):
        qs = obj.children.filter(is_active=True).order_by('account_number')
        return AccountTreeSerializer(qs, many=True, context=self.context).data


class AccountDetailSerializer(serializers.ModelSerializer):
    """Full detail serializer (read)."""
    account_group_name = serializers.CharField(source='account_group.name', read_only=True)
    parent_number      = serializers.CharField(source='parent.account_number', read_only=True)
    parent_name        = serializers.CharField(source='parent.account_name', read_only=True)
    account_type_label = serializers.CharField(source='get_account_type_display', read_only=True)
    is_postable        = serializers.BooleanField(read_only=True)
    level              = serializers.IntegerField(read_only=True)
    has_children       = serializers.BooleanField(read_only=True)
    created_by_name    = serializers.CharField(source='created_by.full_name', read_only=True)
    amount             = serializers.DecimalField(source='computed_amount', read_only=True, max_digits=18, decimal_places=2)
    month_opening_balance = serializers.DecimalField(read_only=True, max_digits=18, decimal_places=2)
    month_debet        = serializers.DecimalField(source='computed_month_debet', read_only=True, max_digits=18, decimal_places=2)
    month_kredit       = serializers.DecimalField(source='computed_month_kredit', read_only=True, max_digits=18, decimal_places=2)

    class Meta:
        model  = Account
        fields = [
            'id', 'company',
            'account_number', 'account_name',
            'account_type', 'account_type_label',
            'account_group', 'account_group_name',
            'parent', 'parent_number', 'parent_name',
            'language', 'default_position', 'currency', 'amount',
            'month_opening_balance', 'month_debet', 'month_kredit',
            'is_inter_company', 'is_cost_component', 'is_on_duty',
            'bank_type',
            'is_linked', 'is_postable', 'has_children',
            'is_active', 'level',
            'created_at', 'updated_at', 'created_by', 'created_by_name',
        ]


class AccountCreateSerializer(serializers.ModelSerializer):
    """Create / Update serializer with full validation."""

    class Meta:
        model  = Account
        fields = [
            'account_number', 'account_name',
            'account_type',
            'account_group', 'parent',
            'language', 'default_position', 'currency', 'amount',
            'is_inter_company', 'is_cost_component', 'is_on_duty',
            'bank_type',
            'is_linked', 'is_active',
        ]

    # ── Field-level validations ───────────────────────────────────────────────

    def validate_account_number(self, value):
        company = self.context['company']
        qs = Account.objects.filter(company=company, account_number=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                f'Account number "{value}" already exists in this company.'
            )
        return value

    # ── Object-level validation ───────────────────────────────────────────────

    def validate(self, attrs):
        account_type = attrs.get('account_type', getattr(self.instance, 'account_type', None))
        bank_type    = attrs.get('bank_type',    getattr(self.instance, 'bank_type', None))
        parent       = attrs.get('parent',       getattr(self.instance, 'parent', None))
        account_group = attrs.get('account_group', getattr(self.instance, 'account_group', None))
        account_number = attrs.get('account_number', getattr(self.instance, 'account_number', ''))
        company      = self.context['company']

        # bank_type only for DETAIL_BANK
        if account_type != AccountType.DETAIL_BANK and bank_type:
            raise serializers.ValidationError({
                'bank_type': 'bank_type is only applicable for Detail Bank accounts.'
            })

        # DETAIL_BANK requires bank_type
        if account_type == AccountType.DETAIL_BANK and not bank_type:
            raise serializers.ValidationError({
                'bank_type': 'bank_type is required for Detail Bank accounts.'
            })

        # HEADER cannot have postable flags set
        if account_type == AccountType.HEADER:
            for flag in ('is_inter_company', 'is_cost_component', 'is_on_duty'):
                if attrs.get(flag, False):
                    raise serializers.ValidationError({
                        flag: 'Header accounts cannot have this flag enabled.'
                    })

        # Parent must belong to same company
        if parent and parent.company_id != company.id:
            raise serializers.ValidationError({
                'parent': 'Parent account must belong to the same company.'
            })

        # Parent must be a HEADER type (non-postable) — only headers can have children
        if parent and parent.account_type != AccountType.HEADER:
            raise serializers.ValidationError({
                'parent': 'Parent account must be a Header (non-postable) account.'
            })

        # Account number must start with group prefix
        if account_group and account_number:
            prefix = account_group.number_prefix
            if not account_number.startswith(prefix):
                raise serializers.ValidationError({
                    'account_number': f'Account number must start with group prefix "{prefix}".'
                })

        # account_group must belong to same company
        if account_group and account_group.company_id != company.id:
            raise serializers.ValidationError({
                'account_group': 'Account group must belong to the same company.'
            })

        return attrs

    def create(self, validated_data):
        company    = self.context['company']
        created_by = self.context['request'].user
        return Account.objects.create(
            company=company,
            created_by=created_by,
            **validated_data,
        )

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

# ─── General Journal Transaction ──────────────────────────────────────────────

from .models import GeneralJournalTransaction, GeneralJournalTransactionDetail, JournalHeader, JournalDetail

class GeneralJournalTransactionDetailSerializer(serializers.ModelSerializer):
    account_number = serializers.CharField(source='account.account_number', read_only=True)
    account_name = serializers.CharField(source='account.account_name', read_only=True)
    
    class Meta:
        model = GeneralJournalTransactionDetail
        fields = [
            'id', 'account', 'account_number', 'account_name', 
            'currency', 'debit', 'credit', 'period_from', 'period_to'
        ]

class GeneralJournalTransactionSerializer(serializers.ModelSerializer):
    details = GeneralJournalTransactionDetailSerializer(many=True, required=False)
    status_label = serializers.CharField(source='get_status_display', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)

    class Meta:
        model = GeneralJournalTransaction
        fields = [
            'id', 'transaction_number', 'date', 'memo', 'project', 'project_name',
            'vendor', 'vendor_name',
            'tax_rectification', 'is_adjustment_pph', 'status', 'status_label',
            'created_at', 'updated_at', 'details'
        ]
        read_only_fields = ['transaction_number', 'status', 'created_at', 'updated_at']

    def create(self, validated_data):
        details_data = validated_data.pop('details', [])
        company = self.context['company']
        user = self.context['request'].user
        
        transaction = GeneralJournalTransaction.objects.create(
            company=company,
            created_by=user,
            **validated_data
        )
        
        for detail_data in details_data:
            GeneralJournalTransactionDetail.objects.create(header=transaction, **detail_data)
            
        return transaction

    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if details_data is not None:
            # Delete existing details and recreate
            instance.details.all().delete()
            for detail_data in details_data:
                GeneralJournalTransactionDetail.objects.create(header=instance, **detail_data)
                
        return instance

from .models import GlobalLinkedAccount

class GlobalLinkedAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalLinkedAccount
        fields = '__all__'
        read_only_fields = ('company', 'created_at', 'updated_at', 'updated_by')

    def update(self, instance, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['updated_by'] = request.user
        return super().update(instance, validated_data)
