from rest_framework import serializers
from .models import (
    VendorCategory,
    VendorGroup,
    Vendor,
    VendorLinkedAccount,
    VendorTerms,
    VendorContactPerson,
    PurchaseRequisition,
    PurchaseRequisitionDetail,
)


class VendorCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorCategory
        fields = '__all__'


class VendorGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorGroup
        fields = '__all__'


class VendorLinkedAccountSerializer(serializers.ModelSerializer):
    account_name = serializers.CharField(source='account.account_name', read_only=True)
    account_code = serializers.CharField(source='account.account_number', read_only=True)

    class Meta:
        model = VendorLinkedAccount
        fields = [
            'id',
            'account_type',
            'currency_scope',
            'account',
            'account_name',
            'account_code',
        ]


class VendorTermsSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorTerms
        fields = [
            'id',
            'payment_due',
            'balance_due_days',
            'tax_code',
            'use_vendor_tax_code',
            'credit_limit',
        ]


class VendorContactPersonSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = VendorContactPerson
        fields = [
            'id',
            'first_name',
            'middle_name',
            'last_name',
            'nickname',
            'title',
            'job_title',
            'gender',
            'spouse',
            'birthday',
            'email',
            'country',
            'city',
            'area',
            'home_address',
            'zip_code',
            'phone',
            'mobile_phone',
            'fax',
            'notes',
            'full_name',
        ]


# --- Read (detail & list) ---

class VendorDetailSerializer(serializers.ModelSerializer):
    linked_accounts  = VendorLinkedAccountSerializer(many=True, read_only=True)
    terms            = VendorTermsSerializer(read_only=True)
    contact_persons  = VendorContactPersonSerializer(many=True, read_only=True)
    category_name    = serializers.CharField(source='category.name', read_only=True)
    group_name       = serializers.CharField(source='group.name', read_only=True)

    class Meta:
        model = Vendor
        fields = [
            'id', 'code',
            'title', 'name',
            'category', 'category_name',
            'department', 'variety',
            'tax_number', 'nppkp',
            'is_leasing',
            'email', 'alternative_email', 'website',
            'address_1', 'address_2',
            'country', 'state', 'city', 'zip_code', 'area_code',
            'phone_1', 'phone_2', 'fax',
            'currency', 'tolerance_difference', 'deposit',
            'bank_name', 'bank_branch', 'bank_city', 'bank_account_number', 'bank_account_name',
            'term_and_condition',
            'company_financial_capability',
            'notary_name', 'letter_no_date', 'notary_name_2', 'letter_no_date_2', 'letter_of_endorsement',
            'no_siup', 'expired_date_siup', 'no_tdp', 'expired_date_tdp',
            'no_sk_domisili', 'expired_date_sk_domisili', 'no_siujk', 'expired_date_siujk',
            'kriteria_usaha',
            'item_type_asset', 'item_type_fg', 'item_type_rm',
            'item_type_supplies', 'item_type_wip', 'item_type_maintenance', 'item_type_subcont',
            'group', 'group_name',
            'is_sister_company', 'status',
            'created_at', 'updated_at',
            'linked_accounts', 'terms', 'contact_persons',
        ]


class VendorListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Vendor
        fields = [
            'id', 'code',
            'title', 'name',
            'category', 'category_name',
            'address_1', 'city', 'phone_1', 'fax',
            'currency', 'status',
        ]


# --- Write ---

class VendorWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        exclude = ['code', 'created_at', 'updated_at', 'company']

    def validate_email(self, value):
        qs = Vendor.objects.filter(email=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Email sudah digunakan vendor lain.")
            
        return value

# ─────────────────────────────────────────────────────────────────────────────
# Purchase Requisition Serializers
# ─────────────────────────────────────────────────────────────────────────────

class PurchaseRequisitionDetailSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.item_name', read_only=True)
    item_code = serializers.CharField(source='item.item_code', read_only=True)
    unit_name = serializers.CharField(source='unit.unit_name', read_only=True)
    rap_budget_amount = serializers.DecimalField(source='rap_detail.amount', max_digits=18, decimal_places=2, read_only=True)

    class Meta:
        model = PurchaseRequisitionDetail
        fields = [
            'id', 'pr', 'rap_detail', 'item', 'item_code', 'item_name', 
            'asset_name', 'quantity', 'unit', 'unit_name', 
            'unit_price', 'final_unit_price', 'amount', 'notes', 'order_no',
            'rap_budget_amount'
        ]
        read_only_fields = ['amount']
        extra_kwargs = {
            'pr': {'required': False}
        }


class PurchaseRequisitionListSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    rap_name = serializers.CharField(source='rap.rap_name', read_only=True)
    pr_type_display = serializers.CharField(source='get_pr_type_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = PurchaseRequisition
        fields = [
            'id', 'pr_number', 'pr_date', 'pr_type', 'pr_type_display',
            'project', 'project_name', 'rap', 'rap_name', 
            'department', 'department_name', 'currency',
            'request_type', 'pr_class', 'repetition', 'etd', 'delivery_point',
            'total_amount', 'document_status', 'approval_status',
            'created_by_name'
        ]


class PurchaseRequisitionSerializer(serializers.ModelSerializer):
    details = PurchaseRequisitionDetailSerializer(many=True, required=False)
    department_name = serializers.CharField(source='department.name', read_only=True)
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    rap_name = serializers.CharField(source='rap.rap_name', read_only=True)
    rap_number = serializers.CharField(source='rap.rap_number', read_only=True)
    budget_component_name = serializers.CharField(source='budget_component.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = PurchaseRequisition
        fields = '__all__'
        read_only_fields = ['pr_number', 'document_status', 'approval_status', 'company', 'created_by']

    def create(self, validated_data):
        details_data = validated_data.pop('details', [])
        
        # Set final_unit_price and calculate total amount
        total_amount = 0
        for item in details_data:
            if 'final_unit_price' not in item:
                item['final_unit_price'] = item.get('unit_price', 0)
            total_amount += item.get('quantity', 0) * item['final_unit_price']
            
        validated_data['total_amount'] = total_amount
        
        pr = PurchaseRequisition.objects.create(**validated_data)
        
        for i, detail_data in enumerate(details_data):
            detail_data['order_no'] = i
            PurchaseRequisitionDetail.objects.create(pr=pr, **detail_data)
            
        return pr

    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        if details_data is not None:
            # Set final_unit_price and re-calculate total amount
            total_amount = 0
            for item in details_data:
                if 'final_unit_price' not in item:
                    item['final_unit_price'] = item.get('unit_price', 0)
                total_amount += item.get('quantity', 0) * item['final_unit_price']
                
            instance.total_amount = total_amount
            
            # Clear old details and create new ones
            instance.details.all().delete()
            for i, detail_data in enumerate(details_data):
                detail_data['order_no'] = i
                PurchaseRequisitionDetail.objects.create(pr=instance, **detail_data)
                
        instance.save()
        return instance
