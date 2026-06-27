import os

content_views = """
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
        from django.utils import timezone
        from datetime import timedelta
        
        three_months_ago = timezone.now().date() - timedelta(days=90)
        PurchaseOrder.objects.filter(
            is_active=True,
            po_date__lt=three_months_ago,
            completioncertificate__isnull=True
        ).update(is_active=False)

        pos = PurchaseOrder.objects.filter(is_active=True, approval_status='approved').values_list('vendor_id', flat=True)
        vendors = Vendor.objects.filter(id__in=pos).distinct()
        serializer = VendorSerializer(vendors, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def get_valid_pos(self, request):
        vendor_id = request.query_params.get('vendor_id')
        if not vendor_id:
            return Response([])
        from apps.purchase.serializers import PurchaseOrderSerializer
        from django.utils import timezone
        from datetime import timedelta
        
        three_months_ago = timezone.now().date() - timedelta(days=90)
        PurchaseOrder.objects.filter(
            is_active=True,
            vendor_id=vendor_id,
            po_date__lt=three_months_ago,
            completioncertificate__isnull=True
        ).update(is_active=False)
        
        pos = PurchaseOrder.objects.filter(vendor_id=vendor_id, is_active=True, approval_status='approved')
        serializer = PurchaseOrderSerializer(pos, many=True)
        return Response(serializer.data)
"""

with open('c:/Traine/bfs-erp/backend/apps/purchase/views.py', 'a', encoding='utf-8') as f:
    f.write(content_views)
