from rest_framework import serializers
from .models import TransactionType

class TransactionTypeSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.company_name', read_only=True)

    class Meta:
        model = TransactionType
        fields = '__all__'
        read_only_fields = ('type_code', 'company')
