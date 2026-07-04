"""
BFS ERP — Inventory URL Configuration
Base: /api/v1/inventory/
"""
from django.urls import path
from .views import (
    UnitListCreateView, UnitDetailView,
    ItemCategoryListCreateView, ItemCategoryDetailView,
    ItemListCreateView, ItemDetailView, ItemImageUploadView,
    ItemAccountLinkListCreateView, ItemAccountLinkDeleteView,
    InventoryChoicesView,
)

urlpatterns = [
    # Unit Measurement
    path('units/',      UnitListCreateView.as_view(), name='unit-list'),
    path('units/<int:pk>/', UnitDetailView.as_view(), name='unit-detail'),

    # Item Category
    path('categories/',          ItemCategoryListCreateView.as_view(), name='category-list'),
    path('categories/<int:pk>/', ItemCategoryDetailView.as_view(),     name='category-detail'),

    # Item
    path('items/',          ItemListCreateView.as_view(), name='item-list'),
    path('items/<int:pk>/', ItemDetailView.as_view(),     name='item-detail'),

    # Upload image
    path('items/<int:pk>/upload-image/', ItemImageUploadView.as_view(), name='item-upload-image'),

    # Account Links
    path('items/<int:item_pk>/accounts/',          ItemAccountLinkListCreateView.as_view(), name='item-account-list'),
    path('items/<int:item_pk>/accounts/<int:pk>/', ItemAccountLinkDeleteView.as_view(),     name='item-account-delete'),

    # Choices
    path('choices/', InventoryChoicesView.as_view(), name='inventory-choices'),
]

from rest_framework.routers import DefaultRouter
from .views import ReceiptReportViewSet

router = DefaultRouter()
router.register(r'receipt-reports', ReceiptReportViewSet, basename='receipt-report')

urlpatterns += router.urls


from .views import ReceiptReportSubmitView, ReceiptReportApproveView

urlpatterns += [
    path('receipt-reports/<int:pk>/submit/', ReceiptReportSubmitView.as_view(), name='receipt-report-submit'),
    path('receipt-reports/<int:pk>/approve/', ReceiptReportApproveView.as_view(), name='receipt-report-approve'),
]
