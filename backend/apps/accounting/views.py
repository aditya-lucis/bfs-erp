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
from rest_framework import generics, status, permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.organization.models import Company
from apps.rbac.permissions import HasFunctionPermission

from .models import (
    Account, AccountGroup, AccountType, BankType, DefaultPosition,
    BankObligation, BankObligationDetail
)
from .serializers import (
    AccountGroupSerializer,
    AccountListSerializer,
    AccountTreeSerializer,
    AccountDetailSerializer,
    AccountCreateSerializer,
    BankObligationSerializer,
    BankObligationDetailSerializer
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
from .models import CashbookReqHeader, CashbookReqDetail
from .serializers import CashbookReqHeaderSerializer
from rest_framework.decorators import action
from apps.accounting_period.period_decorators import PeriodCheckMixin

class CashbookReqViewSet(PeriodCheckMixin, viewsets.ModelViewSet):
    serializer_class = CashbookReqHeaderSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'FINANCE-PAYMENT-REQUEST'
    period_date_field = 'date'
    
    def get_queryset(self):
        qs = CashbookReqHeader.objects.all().order_by('-date', '-id')
        usage_for = self.request.query_params.get('usage_for', None)
        document_status = self.request.query_params.get('document_status', None)
        approval_status = self.request.query_params.get('approval_status', None)
        
        if usage_for:
            qs = qs.filter(usage_for=usage_for)
        if document_status:
            qs = qs.filter(document_status=document_status)
        if approval_status:
            qs = qs.filter(approval_status=approval_status)
            
        return qs

    @action(detail=True, methods=['post'])
    def submit_approval(self, request, pk=None):
        """Submit Payment Request for approval."""
        transaction = self.get_object()
        
        if transaction.approval_status not in [CashbookReqHeader.ApprovalStatus.DRAFT, CashbookReqHeader.ApprovalStatus.REVISED]:
            return Response({'detail': 'Only draft or revised transactions can be submitted.'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            from apps.approval.services import create_approval_request
            from apps.projects.models import RAP
            from django.utils import timezone
            
            today = timezone.localtime().date()
            if transaction.date and transaction.date.year != today.year and not transaction.allow_previous_year_budget:
                return Response({'detail': 'Payment request from a previous year cannot be submitted unless explicitly allowed (Allow Previous Year Budget).'}, status=status.HTTP_400_BAD_REQUEST)

            if transaction.due_date and today > transaction.due_date:
                return Response({'detail': 'Cannot submit to approval. The due date has already passed.'}, status=status.HTTP_400_BAD_REQUEST)
                
            if transaction.project:
                active_rap = RAP.objects.filter(project=transaction.project, is_active=True).first()
                if active_rap and transaction.amount > active_rap.total_cost:
                    return Response({'detail': 'Total amount exceeds the active RAP total cost.'}, status=status.HTTP_400_BAD_REQUEST)
                    
            # Determine document code dynamically based on usage_for
            if transaction.usage_for == CashbookReqHeader.UsageFor.PURCHASE_INVOICE_PAYMENT:
                doc_code = 'CBR_PI'
            elif transaction.usage_for == CashbookReqHeader.UsageFor.PROJECT_CASH_ADVANCED:
                # Advance if Is LPJ OR Is Reimbursement is checked
                if transaction.is_pr_for_lpj or transaction.is_reimbursement:
                    doc_code = 'CBR_PCA_UM'
                else:
                    doc_code = 'CBR_PCA_NON'
            elif transaction.usage_for == CashbookReqHeader.UsageFor.BANK_OBLIGATION_PRINCIPAL:
                doc_code = 'CBR_BRC_POKOK'
            elif transaction.usage_for == CashbookReqHeader.UsageFor.BANK_OBLIGATION_INTEREST:
                doc_code = 'CBR_BRC_BUNGA'
            else:
                return Response({'detail': f'Approval for usage {transaction.usage_for} is not configured yet.'}, status=status.HTTP_400_BAD_REQUEST)
                
            emp_profile = getattr(request.user, 'employee_profile', None)
            emp_pos = getattr(emp_profile, 'position', None)
            fallback_company = emp_pos.department.company if emp_pos and emp_pos.department else None

            create_approval_request(
                document_code=doc_code,
                document_id=str(transaction.id),
                document_number=transaction.document_number,
                creator_user=request.user,
                amount=transaction.amount,
                company=transaction.project.company if transaction.project else fallback_company
            )
            
            transaction.document_status = CashbookReqHeader.DocumentStatus.READY_TO_PROCESS
            transaction.approval_status = CashbookReqHeader.ApprovalStatus.AWAITING
            transaction.save()
            
            return Response({'status': 'Submitted for approval'})
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def available_rap_details(self, request):
        """Return RAP detail items available for selection in PCA form."""
        project_id = request.query_params.get('project_id')
        header_id = request.query_params.get('header_id')

        if not project_id:
            return Response([])

        from apps.projects.models import RAP
        from django.db.models import Q

        active_rap = RAP.objects.filter(project_id=project_id, is_active=True).first()
        if not active_rap:
            return Response([])

        rap_items = active_rap.details.filter(item_type='item')

        current_detail_rap_ids = []
        if header_id:
            header = CashbookReqHeader.objects.filter(id=header_id).first()
            if header:
                current_detail_rap_ids = list(header.details.values_list('rap_detail_id', flat=True))

        used_in_other_pca = CashbookReqDetail.objects.filter(
            header__project_id=project_id,
            header__usage_for=CashbookReqHeader.UsageFor.PROJECT_CASH_ADVANCED,
            rap_detail__isnull=False
        )
        if header_id:
            used_in_other_pca = used_in_other_pca.exclude(header__id=header_id)
            
        used_in_other_pca = used_in_other_pca.exclude(
            Q(header__is_close=True) | Q(header__approval_status=CashbookReqHeader.ApprovalStatus.REJECTED)
        ).values_list('rap_detail_id', flat=True)

        try:
            from apps.purchase.models import PurchaseRequisition, PurchaseRequisitionDetail
            used_in_purchasing = PurchaseRequisitionDetail.objects.filter(
                rap_detail__rap=active_rap
            ).exclude(
                pr__approval_status=PurchaseRequisition.ApprovalStatus.REJECTED
            ).values_list('rap_detail_id', flat=True)
        except Exception as e:
            print(f"Error checking used_in_purchasing: {e}")
            used_in_purchasing = []

        exclude_ids = set(list(current_detail_rap_ids) + list(used_in_other_pca) + list(used_in_purchasing))
        available = rap_items.exclude(id__in=exclude_ids)

        from apps.projects.serializers import RAPDetailSerializer
        serializer = RAPDetailSerializer(available, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def toggle_inactive(self, request):
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'detail': 'No IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
            
        from django.db import transaction
        with transaction.atomic():
            headers = CashbookReqHeader.objects.filter(id__in=ids)
            
            # Validation: Only APPROVED and NOT_PAID CBRs can be toggled
            invalid_docs = []
            for h in headers:
                if h.approval_status != CashbookReqHeader.ApprovalStatus.APPROVED:
                    invalid_docs.append(f"{h.document_number} (Bukan Approved)")
                elif h.paid_status != CashbookReqHeader.PaidStatus.NOT_PAID:
                    invalid_docs.append(f"{h.document_number} (Sudah/Sebagian Dibayar)")
                    
            if invalid_docs:
                return Response({'detail': f'Gagal! Dokumen berikut tidak memenuhi syarat Inactive: {", ".join(invalid_docs)}'}, status=status.HTTP_400_BAD_REQUEST)
                
            for header in headers:
                if header.is_close:
                    from django.db.models import Sum
                    from apps.projects.models import RAP
                    active_rap = RAP.objects.filter(project=header.project, is_active=True).first()
                    if active_rap:
                        active_cbrs = CashbookReqHeader.objects.filter(
                            project=header.project,
                            is_close=False
                        ).exclude(
                            approval_status=CashbookReqHeader.ApprovalStatus.REJECTED
                        )
                        current_total = active_cbrs.aggregate(total=Sum('amount'))['total'] or 0
                        if current_total + header.amount > active_rap.total_cost:
                            return Response({
                                'detail': f'Gagal! Dokumen {header.document_number} tidak dapat diaktifkan kembali karena akan melebihi budget RAP.'
                            }, status=status.HTTP_400_BAD_REQUEST)

                header.is_close = not header.is_close
                header.save(update_fields=['is_close'])
                
        return Response({'status': 'success', 'message': f'Updated {len(ids)} records.'})

    @action(detail=False, methods=['post'])
    def allow_previous_year(self, request):
        ids = request.data.get('ids', [])
        reason = request.data.get('reason', '')
        if not ids:
            return Response({'detail': 'No IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        if not reason:
            return Response({'detail': 'Reason is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        from django.db import transaction
        from django.utils import timezone
        
        today = timezone.localtime().date()
        with transaction.atomic():
            headers = CashbookReqHeader.objects.filter(id__in=ids)
            invalid_docs = []
            for header in headers:
                if header.date and header.date.year >= today.year:
                    invalid_docs.append(f"{header.document_number} (Bukan tahun sebelumnya)")
                elif header.approval_status != CashbookReqHeader.ApprovalStatus.DRAFT:
                    invalid_docs.append(f"{header.document_number} (Bukan Draft)")
            
            if invalid_docs:
                return Response({'detail': f'Gagal! Dokumen berikut tidak memenuhi syarat: {", ".join(invalid_docs)}'}, status=status.HTTP_400_BAD_REQUEST)

            for header in headers:
                header.allow_previous_year_budget = True
                header.reason_allow_previous_year_budget = reason
                header.save(update_fields=['allow_previous_year_budget', 'reason_allow_previous_year_budget'])
                
        return Response({'status': 'success', 'message': f'Allowed previous year budget for {len(ids)} records.'})

# ─── Bank Obligation ──────────────────────────────────────────────────────────

class BankObligationViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, HasFunctionPermission]
    rbac_function_code = 'FINANCE-BANK-OBLIGATION'
    serializer_class = BankObligationSerializer
    queryset = BankObligation.objects.all().order_by('-created_at')
    pagination_class = None

    def get_queryset(self):
        qs = super().get_queryset()
        company_id = self.request.query_params.get('company_id')
        if company_id and company_id != 'undefined':
            qs = qs.filter(company_id=company_id)
        return qs

    def get_permissions(self):
        if self.action in ['active_bank_obligations', 'outstanding_details']:
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    @action(detail=False, methods=['get'])
    def active_bank_obligations(self, request):
        company = get_company(request)
        qs = self.get_queryset().filter(company=company, is_closed=False)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def outstanding_details(self, request, pk=None):
        usage_for = request.query_params.get('usage_for')
        exclude_cbr_id = request.query_params.get('exclude_cbr_id')
        bank_obligation = self.get_object()
        details = bank_obligation.details.all().order_by('no')
        
        # Filter based on whether they have already been requested in CBR
        from django.db.models import Q
        if usage_for == CashbookReqHeader.UsageFor.BANK_OBLIGATION_PRINCIPAL:
            q_filter = Q(is_cbr_pokok=False)
            if exclude_cbr_id:
                q_filter = q_filter | Q(cashbook_details__header_id=exclude_cbr_id, cashbook_details__header__usage_for=usage_for)
            details = details.filter(q_filter).distinct()
        elif usage_for == CashbookReqHeader.UsageFor.BANK_OBLIGATION_INTEREST:
            q_filter = Q(is_cbr_bunga=False)
            if exclude_cbr_id:
                q_filter = q_filter | Q(cashbook_details__header_id=exclude_cbr_id, cashbook_details__header__usage_for=usage_for)
            details = details.filter(q_filter).distinct()
            
        from .serializers import BankObligationDetailSerializer
        serializer = BankObligationDetailSerializer(details, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        company = get_company(self.request)
        serializer.save(company=company)

from .models import BankObligationSetting
from .serializers import BankObligationSettingSerializer
from rest_framework.views import APIView
from rest_framework.response import Response

class BankObligationSettingView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        company = get_company(request)
        setting, created = BankObligationSetting.objects.get_or_create(company=company)
        serializer = BankObligationSettingSerializer(setting)
        return Response(serializer.data)

    def put(self, request):
        company = get_company(request)
        setting, created = BankObligationSetting.objects.get_or_create(company=company)
        serializer = BankObligationSettingSerializer(setting, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(company=company)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
