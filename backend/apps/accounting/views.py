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


class AccountRealtimeBalanceView(APIView):
    """
    GET /api/v1/accounting/coa/<id>/realtime_balance/
    Placeholder for Real-Time Calculation (Cara 2) from journals.
    """
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'GL-CHART-OF-ACCOUNT'

    def get(self, request, pk=None):
        company = get_company(request)
        account = get_object_or_404(Account, pk=pk, company=company)
        
        # Placeholder logic: Since JournalHeader/JournalDetail models are not yet implemented,
        # we will just return the `computed_amount` property.
        # This endpoint should be updated when the journal models are ready.
        balance = account.computed_amount

        return Response({
            'account_id': account.id,
            'account_number': account.account_number,
            'balance': str(balance),
            'start_date': '2000-01-01',  # Placeholder
            'calculation_method': 'realtime (placeholder)'
        })


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

# ─── General Journal Transaction Views ────────────────────────────────────────

from rest_framework import viewsets
from .models import GeneralJournalTransaction, DocumentStatus
from .serializers import GeneralJournalTransactionSerializer
from apps.approval.services import create_approval_request
from apps.accounting_period.period_decorators import PeriodCheckMixin

class GeneralJournalTransactionViewSet(PeriodCheckMixin, viewsets.ModelViewSet):
    """
    CRUD for General Journal Transactions.
    """
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'GL-GENERAL-JOURNAL-TRANSACTION'
    serializer_class = GeneralJournalTransactionSerializer
    period_date_field = 'date'

    def get_queryset(self):
        company = get_company(self.request)
        qs = GeneralJournalTransaction.objects.filter(company=company).select_related('project')
        
        # Filtering
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        search = self.request.query_params.get('search')
        doc_status = self.request.query_params.get('document_status')
        app_status = self.request.query_params.get('approval_status')
        
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)
        if search:
            qs = qs.filter(models_Q(transaction_number__icontains=search) | models_Q(memo__icontains=search))
        if doc_status:
            qs = qs.filter(status=doc_status)
        if app_status:
            qs = qs.filter(status=app_status) # They share the same status field mapped to DocumentStatus
            
        return qs.order_by('-date', '-id')

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['company'] = get_company(self.request)
        return ctx

    from rest_framework.decorators import action

    @action(detail=True, methods=['post'])
    def submit_approval(self, request, pk=None):
        """Submit the transaction for approval."""
        transaction = self.get_object()
        
        if transaction.status not in [DocumentStatus.DRAFT, DocumentStatus.CANCELLED]:
            return Response({'detail': 'Only draft or revised transactions can be submitted.'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            # calculate total amount
            total_amount = sum([d.debit for d in transaction.details.all()])
            
            create_approval_request(
                document_code='GEJ',
                document_id=str(transaction.id),
                document_number=transaction.transaction_number,
                creator_user=request.user,
                amount=total_amount,
                company=transaction.company
            )
            
            transaction.status = DocumentStatus.IN_REVIEW
            transaction.save()
            return Response({'status': 'Submitted for approval'})
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

from .models import GlobalLinkedAccount
from .serializers import GlobalLinkedAccountSerializer
from rest_framework.views import APIView

class GlobalLinkedAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'GL-ACCOUNT'

    def get_queryset(self):
        return GlobalLinkedAccount.objects.none() # for HasFunctionPermission

    def get(self, request, *args, **kwargs):
        company = get_company(request)
        if not company:
            return Response({"detail": "No default company found."}, status=status.HTTP_400_BAD_REQUEST)
            
        gla, created = GlobalLinkedAccount.objects.get_or_create(company=company)
        serializer = GlobalLinkedAccountSerializer(gla)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        company = get_company(request)
        if not company:
            return Response({"detail": "No default company found."}, status=status.HTTP_400_BAD_REQUEST)
            
        gla, created = GlobalLinkedAccount.objects.get_or_create(company=company)
        serializer = GlobalLinkedAccountSerializer(gla, data=request.data, partial=True, context={'request': request})
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
