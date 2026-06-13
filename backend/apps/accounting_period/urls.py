"""
BFS ERP — Accounting: Financial Period URL Configuration

Base: /api/v1/accounting/periods/
"""
from django.urls import path
from .views import (
    AnnualPeriodListCreateView,
    AnnualPeriodToggleView,
    AnnualPeriodLogsView,
    QuarterPeriodListView,
    QuarterPeriodToggleView,
    QuarterPeriodLogsView,
    MonthlyPeriodListView,
    MonthlyPeriodToggleView,
    MonthlyPeriodLogsView,
    AccountingPeriodListView,
    AccountingPeriodToggleView,
    AccountingPeriodLogsView,
    PeriodActivityLogListView,
)

from .views_period_status import PeriodStatusView, PeriodStatusBulkView

urlpatterns = [
    # ── Annual ────────────────────────────────────────────────────────────────
    path('annual/',
         AnnualPeriodListCreateView.as_view(),
         name='period-annual-list'),

    path('annual/<int:pk>/toggle/',
         AnnualPeriodToggleView.as_view(),
         name='period-annual-toggle'),

    path('annual/<int:pk>/logs/',
         AnnualPeriodLogsView.as_view(),
         name='period-annual-logs'),

    # ── Quarter ───────────────────────────────────────────────────────────────
    path('quarter/',
         QuarterPeriodListView.as_view(),
         name='period-quarter-list'),

    path('quarter/<int:pk>/toggle/',
         QuarterPeriodToggleView.as_view(),
         name='period-quarter-toggle'),

    path('quarter/<int:pk>/logs/',
         QuarterPeriodLogsView.as_view(),
         name='period-quarter-logs'),

    # ── Monthly ───────────────────────────────────────────────────────────────
    path('monthly/',
         MonthlyPeriodListView.as_view(),
         name='period-monthly-list'),

    path('monthly/<int:pk>/toggle/',
         MonthlyPeriodToggleView.as_view(),
         name='period-monthly-toggle'),

    path('monthly/<int:pk>/logs/',
         MonthlyPeriodLogsView.as_view(),
         name='period-monthly-logs'),

    # ── Accounting Period ─────────────────────────────────────────────────────
    path('accounting/',
         AccountingPeriodListView.as_view(),
         name='period-accounting-list'),

    path('accounting/<int:pk>/toggle/',
         AccountingPeriodToggleView.as_view(),
         name='period-accounting-toggle'),

    path('accounting/<int:pk>/logs/',
         AccountingPeriodLogsView.as_view(),
         name='period-accounting-logs'),

    # ── Global Logs ───────────────────────────────────────────────────────────
    path('logs/',
         PeriodActivityLogListView.as_view(),
         name='period-logs-global'),

   # ── Period Status Check (for frontend real-time validation) ───────────────
    path('periods/status/',
         PeriodStatusView.as_view(),      name='period-status'),
    path('periods/status/bulk/',
         PeriodStatusBulkView.as_view(),  name='period-status-bulk'),
]