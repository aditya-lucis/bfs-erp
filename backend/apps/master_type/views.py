from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import TransactionType, MasterBank, PaymentTo
from .serializers import TransactionTypeSerializer, MasterBankSerializer, PaymentToSerializer
from apps.rbac.permissions import HasFunctionPermission

class MasterBankViewSet(viewsets.ModelViewSet):
    serializer_class = MasterBankSerializer
    permission_classes = [IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'SETTINGS-MASTER-BANK'
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return MasterBank.objects.all()
        try:
            if hasattr(user, 'employee_profile') and getattr(user, 'employee_profile', None):
                company = user.employee_profile.company
                if company:
                    return MasterBank.objects.filter(company=company)
        except Exception:
            pass
        return MasterBank.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        company = None
        try:
            if hasattr(user, 'employee_profile') and getattr(user, 'employee_profile', None):
                company = user.employee_profile.company
        except Exception:
            pass
        if not company and user.is_superuser:
            from apps.organization.models import Company
            company = Company.objects.filter(is_active=True).first()
        if not company:
            from django.core.exceptions import ValidationError
            raise ValidationError("User has no associated company.")
        serializer.save(company=company)

class TransactionTypeViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionTypeSerializer
    permission_classes = [IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'SETTINGS-MASTER-TYPE'
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return TransactionType.objects.all()
        try:
            if hasattr(user, 'employee_profile') and getattr(user, 'employee_profile', None):
                company = user.employee_profile.company
                if company:
                    return TransactionType.objects.filter(company=company)
        except Exception:
            pass
        return TransactionType.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        company = None
        try:
            if hasattr(user, 'employee_profile') and getattr(user, 'employee_profile', None):
                company = user.employee_profile.company
        except Exception:
            pass
            
        if not company and user.is_superuser:
            from apps.organization.models import Company
            company = Company.objects.filter(is_active=True).first()
            
        if not company:
            from django.core.exceptions import ValidationError
            raise ValidationError("User has no associated company.")

        serializer.save(company=company)

class PaymentToViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentToSerializer
    permission_classes = [IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'SETTINGS-PAYMENT-TO'
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return PaymentTo.objects.all()
        try:
            if hasattr(user, 'employee_profile') and getattr(user, 'employee_profile', None):
                company = user.employee_profile.company
                if company:
                    return PaymentTo.objects.filter(company=company)
        except Exception:
            pass
        return PaymentTo.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        company = None
        try:
            if hasattr(user, 'employee_profile') and getattr(user, 'employee_profile', None):
                company = user.employee_profile.company
        except Exception:
            pass
            
        if not company and user.is_superuser:
            from apps.organization.models import Company
            company = Company.objects.filter(is_active=True).first()
            
        if not company:
            from django.core.exceptions import ValidationError
            raise ValidationError("User has no associated company.")

        serializer.save(company=company)
