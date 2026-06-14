from django.urls import path
from . import views

urlpatterns = [
    path('document-types/', views.DocumentTypeListView.as_view(), name='approval-document-types'),
    path('roles/', views.ApprovalRoleListView.as_view(), name='approval-roles'),
    path('matrix/', views.ApprovalMatrixListCreateView.as_view(), name='approval-matrix-list'),
    path('matrix/lookup/', views.ApprovalMatrixLookupView.as_view(), name='approval-matrix-lookup'),
    path('matrix/<int:pk>/', views.ApprovalMatrixDetailView.as_view(), name='approval-matrix-detail'),
    path('resolve/', views.ApprovalResolveView.as_view(), name='approval-resolve'),

    path('requests/', views.ApprovalRequestListCreateView.as_view(), name='approval-request-list'),
    path('requests/<int:pk>/', views.ApprovalRequestDetailView.as_view(), name='approval-request-detail'),
    path('requests/<int:pk>/approve/', views.ApprovalRequestApproveView.as_view(), name='approval-request-approve'),
    path('requests/<int:pk>/reject/', views.ApprovalRequestRejectView.as_view(), name='approval-request-reject'),
    path('requests/<int:pk>/revise/', views.ApprovalRequestReviseView.as_view(), name='approval-request-revise'),
    path('signatures/', views.DocumentSignatureListView.as_view(), name='document-signature-list'),
]
