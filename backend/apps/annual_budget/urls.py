"""
BFS ERP — Annual Budget URL Configuration
Base: /api/v1/annual-budget/
"""
from django.urls import path
from . import views

urlpatterns = [
    # ── Summary / Overview ────────────────────────────────────────────────────
    path('summary/',
         views.AnnualBudgetSummaryView.as_view(),
         name='annual-budget-summary'),

    # ── Budget Component Picker ───────────────────────────────────────────────
    path('budget-components/',
         views.BudgetComponentPickerView.as_view(),
         name='annual-budget-component-picker'),

    # ── Headers ───────────────────────────────────────────────────────────────
    path('headers/',
         views.AnnualBudgetHeaderListView.as_view(),
         name='annual-budget-header-list'),

    path('headers/<int:pk>/',
         views.AnnualBudgetHeaderDetailView.as_view(),
         name='annual-budget-header-detail'),

    path('headers/<int:pk>/init-lines/',
         views.InitBudgetLinesView.as_view(),
         name='annual-budget-init-lines'),

    # ── Lines ─────────────────────────────────────────────────────────────────
    path('lines/',
         views.AnnualBudgetLineListView.as_view(),
         name='annual-budget-line-list'),

    path('lines/<int:pk>/',
         views.AnnualBudgetLineDetailView.as_view(),
         name='annual-budget-line-detail'),

    path('lines/<int:pk>/update-month/',
         views.UpdateMonthBudgetView.as_view(),
         name='annual-budget-update-month'),

    path('lines/<int:pk>/bulk-update/',
         views.BulkUpdateMonthsView.as_view(),
         name='annual-budget-bulk-update'),

    path('lines/<int:pk>/logs/',
         views.AnnualBudgetLineLogsView.as_view(),
         name='annual-budget-line-logs'),
]
