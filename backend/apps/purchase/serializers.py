from rest_framework import serializers
from .models import (
    VendorCategory,
    VendorGroup,
    Vendor,
    VendorLinkedAccount,
    VendorTerms,
    VendorContactPerson,
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
