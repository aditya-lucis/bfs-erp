from django.urls import path
from . import views

urlpatterns = [

    # ── Master kecil ──────────────────────────────────────────────
    path('customer-categories/',
         views.CustomerCategoryListView.as_view(),
         name='customer-category-list'),
    path('customer-categories/<int:pk>/',
         views.CustomerCategoryDetailView.as_view(),
         name='customer-category-detail'),

    path('customer-groups/',
         views.CustomerGroupListView.as_view(),
         name='customer-group-list'),
    path('customer-groups/<int:pk>/',
         views.CustomerGroupDetailView.as_view(),
         name='customer-group-detail'),

    # ── Customer CRUD ─────────────────────────────────────────────
    path('customers/',
         views.CustomerListView.as_view(),
         name='customer-list'),
    path('customers/create/',
         views.CustomerCreateView.as_view(),
         name='customer-create'),
    path('customers/<int:pk>/',
         views.CustomerDetailView.as_view(),
         name='customer-detail'),
    path('customers/<int:pk>/update/',
         views.CustomerUpdateView.as_view(),
         name='customer-update'),
    path('customers/<int:pk>/delete/',
         views.CustomerDeleteView.as_view(),
         name='customer-delete'),

    # ── Linked Accounts ───────────────────────────────────────────
    path('customers/<int:pk>/linked-accounts/',
         views.CustomerLinkedAccountListView.as_view(),
         name='customer-linked-account-list'),
    path('customers/<int:pk>/linked-accounts/save/',
         views.CustomerLinkedAccountBulkSaveView.as_view(),
         name='customer-linked-account-save'),

    # ── Terms ─────────────────────────────────────────────────────
    path('customers/<int:pk>/terms/',
         views.CustomerTermsView.as_view(),
         name='customer-terms'),

    # ── Contact Person ────────────────────────────────────────────
    path('customers/<int:pk>/contact-persons/',
         views.CustomerContactPersonListView.as_view(),
         name='customer-contact-person-list'),
    path('customers/<int:customer_pk>/contact-persons/<int:pk>/',
         views.CustomerContactPersonDetailView.as_view(),
         name='customer-contact-person-detail'),
]