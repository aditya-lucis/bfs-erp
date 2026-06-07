"""
BFS ERP — Accounting URL Configuration

Base: /api/v1/accounting/
"""
from django.urls import path
from .views import (
    AccountGroupListCreateView,
    AccountGroupDetailView,
    AccountListCreateView,
    AccountTreeView,
    AccountDetailView,
    AccountChoicesView,
)

urlpatterns = [
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
]