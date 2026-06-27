import os

content_views = """
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import CompletionCertificate, PurchaseOrder, Vendor
from .serializers import CompletionCertificateSerializer

class CompletionCertificateViewSet(viewsets.ModelViewSet):
    queryset = CompletionCertificate.objects.all()
    serializer_class = CompletionCertificateSerializer

    @action(detail=False, methods=['get'])
    def get_valid_vendors(self, request):
        from apps.purchase.serializers import VendorSerializer
        pos = PurchaseOrder.objects.filter(is_active=True).values_list('vendor_id', flat=True)
        vendors = Vendor.objects.filter(id__in=pos).distinct()
        serializer = VendorSerializer(vendors, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def get_valid_pos(self, request):
        vendor_id = request.query_params.get('vendor_id')
        if not vendor_id:
            return Response([])
        from apps.purchase.serializers import PurchaseOrderSerializer
        pos = PurchaseOrder.objects.filter(vendor_id=vendor_id, is_active=True)
        serializer = PurchaseOrderSerializer(pos, many=True)
        return Response(serializer.data)
"""

with open('c:/Traine/bfs-erp/backend/apps/purchase/views.py', 'a', encoding='utf-8') as f:
    f.write(content_views)

content_urls = """
    path('completion-certificates/', views.CompletionCertificateViewSet.as_view({'get': 'list', 'post': 'create'}), name='completion-certificate-list'),
    path('completion-certificates/<int:pk>/', views.CompletionCertificateViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='completion-certificate-detail'),
    path('completion-certificates/get_valid_vendors/', views.CompletionCertificateViewSet.as_view({'get': 'get_valid_vendors'}), name='cc-valid-vendors'),
    path('completion-certificates/get_valid_pos/', views.CompletionCertificateViewSet.as_view({'get': 'get_valid_pos'}), name='cc-valid-pos'),
"""

with open('c:/Traine/bfs-erp/backend/apps/purchase/urls.py', 'r', encoding='utf-8') as f:
    urls_content = f.read()

if 'completion-certificates/' not in urls_content:
    urls_content = urls_content.replace(']', content_urls + ']')
    with open('c:/Traine/bfs-erp/backend/apps/purchase/urls.py', 'w', encoding='utf-8') as f:
        f.write(urls_content)
