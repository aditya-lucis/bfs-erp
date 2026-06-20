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
]
