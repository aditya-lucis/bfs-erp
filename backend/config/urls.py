from django.contrib import admin
from django.urls import path, include
from config import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),

    # API v1
    path('api/v1/auth/', include('apps.authentication.urls')),
    path('api/v1/rbac/', include('apps.rbac.urls')),
    path('api/v1/org/',  include('apps.organization.urls')),
    path('api/v1/accounting/', include('apps.accounting.urls')),
    path('api/v1/accounting/periods/', include('apps.accounting_period.urls')),
    path('api/v1/inventory/', include('apps.inventory.urls')),
    path('api/v1/sales/', include('apps.sales.urls')),
    path('api/v1/purchase/', include('apps.purchase.urls')),
    path('api/v1/budget-components/', include('apps.budget_component.urls')),
    path('api/v1/annual-budget/', include('apps.annual_budget.urls')),
    path('api/v1/approval/', include('apps.approval.urls')),
    path('api/v1/projects/', include('apps.projects.urls')),
    path('api/v1/master-type/', include('apps.master_type.urls')),

    # API Docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)