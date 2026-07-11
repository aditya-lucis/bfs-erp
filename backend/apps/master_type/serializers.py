from rest_framework import serializers
from .models import TransactionType, MasterBank, PaymentTo

class TransactionTypeSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.company_name', read_only=True)

    class Meta:
        model = TransactionType
        fields = '__all__'
        read_only_fields = ('type_code', 'company')

class MasterBankSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.company_name', read_only=True)

    class Meta:
        model = MasterBank
        fields = '__all__'
        read_only_fields = ('bank_code', 'company')

class PaymentToSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.company_name', read_only=True)
    bank_name_display = serializers.CharField(source='bank.bank_name', read_only=True)
    department_name_display = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = PaymentTo
        fields = '__all__'
        read_only_fields = ('company',)
