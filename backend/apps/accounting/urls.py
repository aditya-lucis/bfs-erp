"""
BFS ERP — Accounting URL Configuration

Base: /api/v1/accounting/
"""
from django.urls import path, include
from .views import (
    GlobalLinkedAccountView,
    AccountGroupListCreateView,
    AccountGroupDetailView,
    AccountListCreateView,
    AccountTreeView,
    AccountDetailView,
    AccountRealtimeBalanceView,
    AccountChoicesView,
    GeneralJournalTransactionViewSet,
)

from rest_framework.routers import DefaultRouter
from .views import CashbookReqViewSet, BankObligationViewSet

router = DefaultRouter()
router.register(r'general-journals', GeneralJournalTransactionViewSet, basename='general-journal')
router.register(r'cashbook-request', CashbookReqViewSet, basename='cashbook-request')
router.register(r'bank-obligation', BankObligationViewSet, basename='bank-obligation')
urlpatterns = [
    path('global-linked-accounts/', GlobalLinkedAccountView.as_view(), name='global-linked-accounts'),
path('', include(router.urls)),
    # ── Account Groups ────────────────────────────────────────────────────────
    path('account-groups/',
         AccountGroupListCreateView.as_view(),
         name='account-group-list'),

    path('account-groups/<int:pk>/',
         AccountGroupDetailView.as_view(),
         name='account-group-detail'),

    # ── Chart of Accounts ────────────────────────────────────────────────────
    path('coa/',
         AccountListCreateView.as_view(),
         name='coa-list'),

    path('coa/tree/',
         AccountTreeView.as_view(),
         name='coa-tree'),

    path('coa/choices/',
         AccountChoicesView.as_view(),
         name='coa-choices'),

    path('coa/<int:pk>/',
         AccountDetailView.as_view(),
         name='coa-detail'),

    path('coa/<int:pk>/realtime_balance/',
         AccountRealtimeBalanceView.as_view(),
         name='coa-realtime-balance'),
]