"""
BFS ERP — Accounting: Chart of Account Views

Endpoints:
    AccountGroup:
        GET     /api/v1/accounting/account-groups/         list
        POST    /api/v1/accounting/account-groups/         create
        GET     /api/v1/accounting/account-groups/<id>/    retrieve
        PATCH   /api/v1/accounting/account-groups/<id>/    update
        DELETE  /api/v1/accounting/account-groups/<id>/    soft-delete

    Account (COA):
        GET     /api/v1/accounting/coa/                    flat list (filterable)
        POST    /api/v1/accounting/coa/                    create
        GET     /api/v1/accounting/coa/tree/               tree grouped by AccountGroup
        GET     /api/v1/accounting/coa/<id>/               retrieve
        PATCH   /api/v1/accounting/coa/<id>/               update
        DELETE  /api/v1/accounting/coa/<id>/               soft-delete
        GET     /api/v1/accounting/coa/types/              enum choices
"""

from django.shortcuts import get_object_or_404
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.organization.models import Company
from apps.rbac.permissions import HasFunctionPermission

from .models import Account, AccountGroup, AccountType, BankType, DefaultPosition
from .serializers import (
    AccountGroupSerializer,
    AccountListSerializer,
    AccountTreeSerializer,
    AccountDetailSerializer,
    AccountCreateSerializer,
)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def get_company(request):
    """Return the single Company record (single-tenant)."""
    return Company.get_default()


# ─── Account Group Views ──────────────────────────────────────────────────────

class AccountGroupListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/accounting/account-groups/  → list all active account groups
    POST /api/v1/accounting/account-groups/  → create new account group
    """
    permission_classes   = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code   = 'GL-ACCOUNT-GROUP'
    serializer_class     = AccountGroupSerializer
    pagination_class     = None

    def get_queryset(self):
        company = get_company(self.request)
        return AccountGroup.objects.filter(
            company=company, is_active=True
        ).order_by('order', 'code')

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['company'] = get_company(self.request)
        return ctx

    def perform_create(self, serializer):
        company = get_company(self.request)
        serializer.save(company=company, created_by=self.request.user)


class AccountGroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/v1/accounting/account-groups/<id>/
    PATCH  /api/v1/accounting/account-groups/<id>/
    DELETE /api/v1/accounting/account-groups/<id>/  → soft delete
    """
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'GL-ACCOUNT-GROUP'
    serializer_class   = AccountGroupSerializer

    def get_queryset(self):
        company = get_company(self.request)
        return AccountGroup.objects.filter(company=company)

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['company'] = get_company(self.request)
        return ctx

    def destroy(self, request, *args, **kwargs):
        """Soft delete — check if any accounts use this group first."""
        instance = self.get_object()
        if instance.accounts.filter(is_active=True).exists():
            return Response(
                {'detail': 'Cannot delete account group that has active accounts.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ─── COA (Account) Views ──────────────────────────────────────────────────────

class AccountListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/accounting/coa/
        ?group=<group_id>           filter by account group
        ?type=HEADER|DETAIL|...     filter by account type
        ?postable=true|false        filter postable only
        ?parent=<parent_id>         filter by parent
        ?search=<str>               search account_number / account_name
        ?active=true|false          default true

    POST /api/v1/accounting/coa/    create new account
    """
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AccountCreateSerializer
        return AccountListSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), HasFunctionPermission()]

    def get_rbac_function_code(self):
        return 'GL-CHART-OF-ACCOUNT'

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['company'] = get_company(self.request)
        return ctx

    def get_queryset(self):
        company = get_company(self.request)
        qs = Account.objects.filter(company=company).select_related(
            'account_group', 'parent', 'created_by'
        ).order_by('account_number')

        params = self.request.query_params

        # active filter (default: only active)
        active = params.get('active', 'true').lower()
        if active == 'false':
            qs = qs.filter(is_active=False)
        elif active == 'all':
            pass  # no filter
        else:
            qs = qs.filter(is_active=True)

        # group filter
        group_id = params.get('group')
        if group_id:
            qs = qs.filter(account_group_id=group_id)

        # type filter
        acc_type = params.get('type')
        if acc_type:
            qs = qs.filter(account_type=acc_type.upper())

        # postable filter
        postable = params.get('postable')
        if postable is not None:
            if postable.lower() == 'true':
                qs = qs.exclude(account_type=AccountType.HEADER)
            elif postable.lower() == 'false':
                qs = qs.filter(account_type=AccountType.HEADER)

        # parent filter
        parent_id = params.get('parent')
        if parent_id == 'null':
            qs = qs.filter(parent__isnull=True)
        elif parent_id:
            qs = qs.filter(parent_id=parent_id)

        # search
        search = params.get('search')
        if search:
            qs = qs.filter(
                models_Q(account_number__icontains=search) |
                models_Q(account_name__icontains=search)
            )

        return qs

    def create(self, request, *args, **kwargs):
        serializer = AccountCreateSerializer(
            data=request.data,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)
        account = serializer.save()
        return Response(
            AccountDetailSerializer(account, context=self.get_serializer_context()).data,
            status=status.HTTP_201_CREATED,
        )


class AccountTreeView(APIView):
    """
    GET /api/v1/accounting/coa/tree/
    Returns COA grouped by AccountGroup, each group with nested account tree.

    Response:
    [
      {
        "group": { id, code, name, number_prefix, default_position },
        "accounts": [ <tree> ]
      },
      ...
    ]
    """
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'GL-CHART-OF-ACCOUNT'

    def get(self, request):
        company = get_company(request)
        groups  = AccountGroup.objects.filter(
            company=company, is_active=True
        ).order_by('order', 'code')

        result = []
        for group in groups:
            # Root accounts (no parent) in this group
            roots = Account.objects.filter(
                company=company,
                account_group=group,
                parent__isnull=True,
                is_active=True,
            ).order_by('account_number')

            result.append({
                'group': AccountGroupSerializer(group, context={'request': request}).data,
                'accounts': AccountTreeSerializer(
                    roots, many=True, context={'request': request}
                ).data,
            })

        return Response(result)


class AccountDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/v1/accounting/coa/<id>/
    PATCH  /api/v1/accounting/coa/<id>/
    DELETE /api/v1/accounting/coa/<id>/  → soft delete
    """
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'GL-CHART-OF-ACCOUNT'

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return AccountCreateSerializer
        return AccountDetailSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['company'] = get_company(self.request)
        return ctx

    def get_queryset(self):
        company = get_company(self.request)
        return Account.objects.filter(company=company).select_related(
            'account_group', 'parent', 'created_by'
        )

    def update(self, request, *args, **kwargs):
        partial  = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = AccountCreateSerializer(
            instance,
            data=request.data,
            partial=partial,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)
        account = serializer.save()
        return Response(
            AccountDetailSerializer(account, context=self.get_serializer_context()).data
        )

    def destroy(self, request, *args, **kwargs):
        """Soft delete — block if account has active children."""
        instance = self.get_object()
        if instance.children.filter(is_active=True).exists():
            return Response(
                {'detail': 'Cannot delete account that has active child accounts.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AccountChoicesView(APIView):
    """
    GET /api/v1/accounting/coa/choices/
    Returns all enum choices for dropdowns in the frontend.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({
            'account_types': [
                {'value': v, 'label': l} for v, l in AccountType.choices
            ],
            'bank_types': [
                {'value': v, 'label': l} for v, l in BankType.choices
            ],
            'default_positions': [
                {'value': v, 'label': l} for v, l in DefaultPosition.choices
            ],
            'currencies': [
                {'value': 'IDR', 'label': 'IDR - Indonesian Rupiah'},
                {'value': 'USD', 'label': 'USD - US Dollar'},
                {'value': 'EUR', 'label': 'EUR - Euro'},
                {'value': 'SGD', 'label': 'SGD - Singapore Dollar'},
            ],
            'languages': [
                {'value': 'EN', 'label': 'English'},
                {'value': 'ID', 'label': 'Indonesian'},
            ],
        })


# ─── Fix missing import ───────────────────────────────────────────────────────
from django.db.models import Q as models_Q