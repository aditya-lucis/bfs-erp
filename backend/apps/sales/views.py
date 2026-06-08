from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.organization.models import Company
from apps.rbac.permissions import HasFunctionPermission
from .models import (
    CustomerCategory,
    CustomerGroup,
    Customer,
    CustomerLinkedAccount,
    CustomerTerms,
    CustomerContactPerson,
)
from .serializers import (
    CustomerCategorySerializer,
    CustomerGroupSerializer,
    CustomerListSerializer,
    CustomerDetailSerializer,
    CustomerWriteSerializer,
    CustomerLinkedAccountSerializer,
    CustomerTermsSerializer,
    CustomerContactPersonSerializer,
)


# ── Master kecil ────────────────────────────────────────────────

class CustomerCategoryListView(generics.ListCreateAPIView):
    queryset           = CustomerCategory.objects.all().order_by('code')
    serializer_class   = CustomerCategorySerializer
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'SALES-CUSTOMER'
    pagination_class   = None


class CustomerCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset           = CustomerCategory.objects.all()
    serializer_class   = CustomerCategorySerializer
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'SALES-CUSTOMER'


class CustomerGroupListView(generics.ListCreateAPIView):
    queryset           = CustomerGroup.objects.all().order_by('name')
    serializer_class   = CustomerGroupSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'SALES-CUSTOMER'
    pagination_class   = None


class CustomerGroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset           = CustomerGroup.objects.all()
    serializer_class   = CustomerGroupSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'SALES-CUSTOMER'


# ── Customer CRUD ────────────────────────────────────────────────

class CustomerListView(generics.ListAPIView):
    serializer_class   = CustomerListSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'SALES-CUSTOMER'
    pagination_class   = None

    def get_queryset(self):
        qs = Customer.objects.select_related('category', 'group').order_by('code')

        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)

        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(name__icontains=search) | Q(code__icontains=search)
            )

        return qs


class CustomerCreateView(generics.CreateAPIView):
    serializer_class   = CustomerWriteSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'SALES-CUSTOMER'

    def perform_create(self, serializer):
        company = Company.get_default()
        if not company:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'detail': 'Company belum dikonfigurasi.'})
        customer = serializer.save(company=company)
        CustomerTerms.objects.create(customer=customer)


class CustomerDetailView(generics.RetrieveAPIView):
    queryset = Customer.objects.select_related(
        'category', 'group'
    ).prefetch_related(
        'linked_accounts__account',
        'terms',
        'contact_persons',
    )
    serializer_class   = CustomerDetailSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'SALES-CUSTOMER'


class CustomerUpdateView(generics.UpdateAPIView):
    queryset           = Customer.objects.all()
    serializer_class   = CustomerWriteSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'SALES-CUSTOMER'


class CustomerDeleteView(generics.DestroyAPIView):
    queryset           = Customer.objects.all()
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'SALES-CUSTOMER'

    def destroy(self, request, *args, **kwargs):
        customer = self.get_object()
        customer.status = Customer.Status.CLOSED
        customer.save()
        return Response({'detail': 'Customer berhasil dinonaktifkan.'}, status=status.HTTP_200_OK)


# ── Linked Accounts ──────────────────────────────────────────────

class CustomerLinkedAccountListView(generics.ListAPIView):
    serializer_class   = CustomerLinkedAccountSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'SALES-CUSTOMER'
    pagination_class   = None

    def get_queryset(self):
        return CustomerLinkedAccount.objects.filter(
            customer_id=self.kwargs['pk']
        ).select_related('account')


class CustomerLinkedAccountBulkSaveView(APIView):
    """
    Terima array linked accounts, replace semua milik customer ini.
    Sesuai perilaku tombol Save di modal Setting Linked Accounts Sunfish.
    """
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'SALES-CUSTOMER'

    def post(self, request, pk):
        customer = get_object_or_404(Customer, pk=pk)
        serializer = CustomerLinkedAccountSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        CustomerLinkedAccount.objects.filter(customer=customer).delete()
        CustomerLinkedAccount.objects.bulk_create([
            CustomerLinkedAccount(customer=customer, **item)
            for item in serializer.validated_data
        ])

        result = CustomerLinkedAccountSerializer(
            CustomerLinkedAccount.objects.filter(customer=customer).select_related('account'),
            many=True
        )
        return Response(result.data, status=status.HTTP_200_OK)


# ── Terms ─────────────────────────────────────────────────────────

class CustomerTermsView(APIView):
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'SALES-CUSTOMER'

    def get(self, request, pk):
        terms = get_object_or_404(CustomerTerms, customer_id=pk)
        return Response(CustomerTermsSerializer(terms).data)

    def put(self, request, pk):
        terms = get_object_or_404(CustomerTerms, customer_id=pk)
        serializer = CustomerTermsSerializer(terms, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request, pk):
        terms = get_object_or_404(CustomerTerms, customer_id=pk)
        serializer = CustomerTermsSerializer(terms, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# ── Contact Person ────────────────────────────────────────────────

class CustomerContactPersonListView(generics.ListCreateAPIView):
    serializer_class   = CustomerContactPersonSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'SALES-CUSTOMER'
    pagination_class   = None

    def get_queryset(self):
        return CustomerContactPerson.objects.filter(
            customer_id=self.kwargs['pk']
        ).order_by('id')

    def perform_create(self, serializer):
        customer = get_object_or_404(Customer, pk=self.kwargs['pk'])
        serializer.save(customer=customer)


class CustomerContactPersonDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = CustomerContactPersonSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'SALES-CUSTOMER'

    def get_queryset(self):
        return CustomerContactPerson.objects.filter(
            customer_id=self.kwargs['customer_pk']
        )
