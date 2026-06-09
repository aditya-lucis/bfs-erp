from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.organization.models import Company
from apps.rbac.permissions import HasFunctionPermission
from .models import (
    VendorCategory,
    VendorGroup,
    Vendor,
    VendorLinkedAccount,
    VendorTerms,
    VendorContactPerson,
)
from .serializers import (
    VendorCategorySerializer,
    VendorGroupSerializer,
    VendorListSerializer,
    VendorDetailSerializer,
    VendorWriteSerializer,
    VendorLinkedAccountSerializer,
    VendorTermsSerializer,
    VendorContactPersonSerializer,
)


# ── Master kecil ────────────────────────────────────────────────

class VendorCategoryListView(generics.ListCreateAPIView):
    queryset           = VendorCategory.objects.all().order_by('code')
    serializer_class   = VendorCategorySerializer
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'PURCHASES-VENDOR-CATEGORY'
    pagination_class   = None


class VendorCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset           = VendorCategory.objects.all()
    serializer_class   = VendorCategorySerializer
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'PURCHASES-VENDOR-CATEGORY'


class VendorGroupListView(generics.ListCreateAPIView):
    queryset           = VendorGroup.objects.all().order_by('name')
    serializer_class   = VendorGroupSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'PURCHASES-VENDOR-GROUP'
    pagination_class   = None


class VendorGroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset           = VendorGroup.objects.all()
    serializer_class   = VendorGroupSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'PURCHASES-VENDOR-GROUP'


# ── Vendor CRUD ────────────────────────────────────────────────

class VendorListView(generics.ListAPIView):
    serializer_class   = VendorListSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'PURCHASES-VENDOR'
    pagination_class   = None

    def get_queryset(self):
        qs = Vendor.objects.select_related('category', 'group').order_by('code')

        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)

        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(name__icontains=search) | Q(code__icontains=search)
            )

        return qs


class VendorCreateView(generics.CreateAPIView):
    serializer_class   = VendorWriteSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'PURCHASES-VENDOR'

    def perform_create(self, serializer):
        company = Company.get_default()
        if not company:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'detail': 'Company belum dikonfigurasi.'})
        vendor = serializer.save(company=company)
        VendorTerms.objects.create(vendor=vendor)


class VendorDetailView(generics.RetrieveAPIView):
    queryset = Vendor.objects.select_related(
        'category', 'group', 'department'
    ).prefetch_related(
        'linked_accounts__account',
        'terms',
        'contact_persons',
    )
    serializer_class   = VendorDetailSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'PURCHASES-VENDOR'


class VendorUpdateView(generics.UpdateAPIView):
    queryset           = Vendor.objects.all()
    serializer_class   = VendorWriteSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'PURCHASES-VENDOR'


class VendorDeleteView(generics.DestroyAPIView):
    queryset           = Vendor.objects.all()
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'PURCHASES-VENDOR'

    def destroy(self, request, *args, **kwargs):
        vendor = self.get_object()
        vendor.status = Vendor.Status.CLOSED
        vendor.save()
        return Response({'detail': 'Vendor berhasil dinonaktifkan.'}, status=status.HTTP_200_OK)


# ── Linked Accounts ──────────────────────────────────────────────

class VendorLinkedAccountListView(generics.ListAPIView):
    serializer_class   = VendorLinkedAccountSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'PURCHASES-VENDOR'
    pagination_class   = None

    def get_queryset(self):
        return VendorLinkedAccount.objects.filter(
            vendor_id=self.kwargs['pk']
        ).select_related('account')


class VendorLinkedAccountBulkSaveView(APIView):
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'PURCHASES-VENDOR'

    def post(self, request, pk):
        vendor = get_object_or_404(Vendor, pk=pk)
        serializer = VendorLinkedAccountSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        VendorLinkedAccount.objects.filter(vendor=vendor).delete()
        VendorLinkedAccount.objects.bulk_create([
            VendorLinkedAccount(vendor=vendor, **item)
            for item in serializer.validated_data
        ])

        result = VendorLinkedAccountSerializer(
            VendorLinkedAccount.objects.filter(vendor=vendor).select_related('account'),
            many=True
        )
        return Response(result.data, status=status.HTTP_200_OK)


# ── Terms ─────────────────────────────────────────────────────────

class VendorTermsView(APIView):
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'PURCHASES-VENDOR'

    def get(self, request, pk):
        terms = get_object_or_404(VendorTerms, vendor_id=pk)
        return Response(VendorTermsSerializer(terms).data)

    def put(self, request, pk):
        terms = get_object_or_404(VendorTerms, vendor_id=pk)
        serializer = VendorTermsSerializer(terms, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request, pk):
        terms = get_object_or_404(VendorTerms, vendor_id=pk)
        serializer = VendorTermsSerializer(terms, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# ── Contact Person ────────────────────────────────────────────────

class VendorContactPersonListView(generics.ListCreateAPIView):
    serializer_class   = VendorContactPersonSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'PURCHASES-VENDOR'
    pagination_class   = None

    def get_queryset(self):
        return VendorContactPerson.objects.filter(
            vendor_id=self.kwargs['pk']
        ).order_by('id')

    def perform_create(self, serializer):
        vendor = get_object_or_404(Vendor, pk=self.kwargs['pk'])
        serializer.save(vendor=vendor)


class VendorContactPersonDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = VendorContactPersonSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'PURCHASES-VENDOR'

    def get_queryset(self):
        return VendorContactPerson.objects.filter(
            vendor_id=self.kwargs['vendor_pk']
        )
