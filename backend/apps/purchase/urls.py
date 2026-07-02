from django.urls import path
from . import views

urlpatterns = [

    # ── Master kecil ──────────────────────────────────────────────
    path('vendor-categories/',
         views.VendorCategoryListView.as_view(),
         name='vendor-category-list'),
    path('vendor-categories/<int:pk>/',
         views.VendorCategoryDetailView.as_view(),
         name='vendor-category-detail'),

    path('vendor-groups/',
         views.VendorGroupListView.as_view(),
         name='vendor-group-list'),
    path('vendor-groups/<int:pk>/',
         views.VendorGroupDetailView.as_view(),
         name='vendor-group-detail'),

    # ── Vendor CRUD ─────────────────────────────────────────────
    path('vendors/',
         views.VendorListView.as_view(),
         name='vendor-list'),
    path('vendors/create/',
         views.VendorCreateView.as_view(),
         name='vendor-create'),
    path('vendors/<int:pk>/',
         views.VendorDetailView.as_view(),
         name='vendor-detail'),
    path('vendors/<int:pk>/update/',
         views.VendorUpdateView.as_view(),
         name='vendor-update'),
    path('vendors/<int:pk>/delete/',
         views.VendorDeleteView.as_view(),
         name='vendor-delete'),
    path('vendors/<int:pk>/activate/',
         views.VendorActivateView.as_view(),
         name='vendor-activate'),

    # ── Linked Accounts ───────────────────────────────────────────
    path('vendors/<int:pk>/linked-accounts/',
         views.VendorLinkedAccountListView.as_view(),
         name='vendor-linked-account-list'),
    path('vendors/<int:pk>/linked-accounts/save/',
         views.VendorLinkedAccountBulkSaveView.as_view(),
         name='vendor-linked-account-save'),

    # ── Terms ─────────────────────────────────────────────────────
    path('vendors/<int:pk>/terms/',
         views.VendorTermsView.as_view(),
         name='vendor-terms'),

    # ── Contact Person ────────────────────────────────────────────
    path('vendors/<int:pk>/contact-persons/',
         views.VendorContactPersonListView.as_view(),
         name='vendor-contact-person-list'),
    path('vendors/<int:vendor_pk>/contact-persons/<int:pk>/',
         views.VendorContactPersonDetailView.as_view(),
         name='vendor-contact-person-detail'),

    # ── Purchase Requisition (PR) ─────────────────────────────────
    path('pr/',
         views.PurchaseRequisitionListView.as_view(),
         name='pr-list'),
    path('pr/<int:pk>/',
         views.PurchaseRequisitionDetailView.as_view(),
         name='pr-detail'),
    path('pr/<int:pk>/submit/',
         views.PurchaseRequisitionSubmitView.as_view(),
         name='pr-submit'),

    # ── Purchase Requisition Inbox ────────────────────────────────
    path('pr-inbox/',
         views.PurchaseRequisitionInboxListView.as_view(),
         name='pr-inbox-list'),
    path('pr-inbox/<int:pk>/approve/',
         views.PurchaseRequisitionApproveView.as_view(),
         name='pr-inbox-approve'),

    # ── Purchase Order (PO) ───────────────────────────────────────
    path('po/',
         views.PurchaseOrderListView.as_view(),
         name='po-list'),
    path('po/<int:pk>/',
         views.PurchaseOrderDetailView.as_view(),
         name='po-detail'),
    path('po/<int:pk>/submit/',
         views.PurchaseOrderSubmitView.as_view(),
         name='po-submit'),
    path('po/<int:pk>/allow-previous-year/',
         views.POInboxViewSet.as_view({'post': 'allow_previous_year_budget'}),
         name='po-allow-previous-year'),

    # ─── Purchase Order Inbox ──────────────────────────────────────────────────
    path('po-inbox/',
         views.POInboxViewSet.as_view({'get': 'list'}),
         name='po-inbox-list'),
    path('po-inbox/<int:pk>/',
         views.POInboxViewSet.as_view({'get': 'retrieve'}),
         name='po-inbox-detail'),
    path('po-inbox/<int:pk>/approve/',
         views.POInboxViewSet.as_view({'post': 'approve'}),
         name='po-inbox-approve'),
    path('po-inbox/<int:pk>/reject/',
         views.POInboxViewSet.as_view({'post': 'reject'}),
         name='po-inbox-reject'),

    # GRN-SES Documents
    path('grn-ses-documents/', views.GrnSesDocumentViewSet.as_view({'get': 'list', 'post': 'create'}), name='grn-ses-document-list'),
    path('grn-ses-documents/<int:pk>/', views.GrnSesDocumentViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='grn-ses-document-detail'),

    path('completion-certificates/', views.CompletionCertificateViewSet.as_view({'get': 'list', 'post': 'create'}), name='completion-certificate-list'),
    path('completion-certificates/<int:pk>/', views.CompletionCertificateViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='completion-certificate-detail'),
    path('completion-certificates/<int:pk>/void_cc/', views.CompletionCertificateViewSet.as_view({'post': 'void_cc'}), name='cc-void'),
    path('completion-certificates/get_valid_vendors/', views.CompletionCertificateViewSet.as_view({'get': 'get_valid_vendors'}), name='cc-valid-vendors'),
    path('completion-certificates/get_valid_pos/', views.CompletionCertificateViewSet.as_view({'get': 'get_valid_pos'}), name='cc-valid-pos'),
    path('completion-certificates/<int:pk>/submit/', views.CompletionCertificateSubmitApprovalView.as_view(), name='cc-submit'),

    # Good Receipt Note
    path('good-receipt-notes/', views.GoodReceiptNoteViewSet.as_view({'get': 'list', 'post': 'create'}), name='grn-list'),
    path('good-receipt-notes/<int:pk>/', views.GoodReceiptNoteViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='grn-detail'),
    path('good-receipt-notes/<int:pk>/approve/', views.GoodReceiptNoteViewSet.as_view({'post': 'approve'}), name='grn-approve'),
    path('good-receipt-notes/<int:pk>/void_grn/', views.GoodReceiptNoteViewSet.as_view({'post': 'void_grn'}), name='grn-void'),
    path('good-receipt-notes/get_valid_vendors/', views.GoodReceiptNoteViewSet.as_view({'get': 'get_valid_vendors'}), name='grn-valid-vendors'),
    path('good-receipt-notes/get_valid_pos/', views.GoodReceiptNoteViewSet.as_view({'get': 'get_valid_pos'}), name='grn-valid-pos'),
    path('good-receipt-notes/get_valid_ccs/', views.GoodReceiptNoteViewSet.as_view({'get': 'get_valid_ccs'}), name='grn-valid-ccs'),
    path('good-receipt-notes/<int:pk>/submit/', views.GoodReceiptNoteSubmitApprovalView.as_view(), name='grn-submit'),
]
