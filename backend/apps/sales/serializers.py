from rest_framework import serializers
from .models import (
    CustomerCategory,
    CustomerGroup,
    Customer,
    CustomerLinkedAccount,
    CustomerTerms,
    CustomerContactPerson,
)


class CustomerCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerCategory
        fields = '__all__'


class CustomerGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerGroup
        fields = '__all__'


class CustomerLinkedAccountSerializer(serializers.ModelSerializer):
    account_name = serializers.CharField(source='account.account_name', read_only=True)
    account_code = serializers.CharField(source='account.account_number', read_only=True)

    class Meta:
        model = CustomerLinkedAccount
        fields = [
            'id',
            'account_type',
            'currency_scope',
            'account',
            'account_name',
            'account_code',
        ]


class CustomerTermsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerTerms
        fields = [
            'id',
            'payment_due',
            'balance_due_days',
            'tax_code',
            'use_customer_tax_code',
        ]


class CustomerContactPersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerContactPerson
        fields = [
            'id',
            'name',
            'home_address',
            'email',
            'home_phone',
        ]


# --- Read (detail & list) ---

class CustomerDetailSerializer(serializers.ModelSerializer):
    linked_accounts  = CustomerLinkedAccountSerializer(many=True, read_only=True)
    terms            = CustomerTermsSerializer(read_only=True)
    contact_persons  = CustomerContactPersonSerializer(many=True, read_only=True)
    category_name    = serializers.CharField(source='category.name', read_only=True)
    group_name       = serializers.CharField(source='group.name', read_only=True)

    class Meta:
        model = Customer
        fields = [
            'id', 'code',
            'title', 'name',
            'category', 'category_name',
            'tax_number', 'nppkp',
            'email', 'website',
            'address_1', 'address_2',
            'country', 'state', 'city', 'zip_code', 'area_code',
            'phone_1', 'phone_2', 'fax',
            'currency', 'default_price_group',
            'tolerance_difference', 'deposit', 'credit_limit',
            'is_kawasan_berikat', 'is_sister_company',
            'item_type_asset', 'item_type_fg', 'item_type_rm',
            'item_type_supplies', 'item_type_wip',
            'group', 'group_name',
            'status',
            'created_at', 'updated_at',
            'linked_accounts', 'terms', 'contact_persons',
        ]


class CustomerListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Customer
        fields = [
            'id', 'code',
            'title', 'name',
            'category', 'category_name',
            'city', 'phone_1', 'fax',
            'currency', 'status',
        ]


# --- Write ---

class CustomerWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        exclude = ['code', 'created_at', 'updated_at', 'company']

    def validate_email(self, value):
        qs = Customer.objects.filter(email=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Email sudah digunakan customer lain.")
        return value