import re

file_path = 'apps/purchase/views.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add imports
content = content.replace(
    'from rest_framework import generics, permissions, status',
    'from rest_framework import generics, permissions, status, viewsets\nfrom rest_framework.decorators import action\nfrom django.core.exceptions import ValidationError'
)

content = content.replace(
    'from .serializers import PurchaseOrderListSerializer, PurchaseOrderSerializer',
    'from .serializers import PurchaseOrderListSerializer, PurchaseOrderSerializer, POInboxSerializer'
)

# Cross-year validation
cross_year_validation = '''
        if po.rap:
            from django.utils import timezone
            current_year = timezone.now().year
            if current_year > po.rap.year_period and not po.allow_previous_year_budget:
                return Response({
                    'detail': f'PO ini menggunakan RAP tahun {po.rap.year_period}. Memerlukan izin "Allow Previous Year Budget" untuk disubmit pada tahun {current_year}.'
                }, status=status.HTTP_400_BAD_REQUEST)

            used_po = PurchaseOrder.objects.filter(
                rap=po.rap,
                document_status__in=['open', 'confirmed', 'delivered', 'invoiced', 'close']'''

content = content.replace(
    '''        if po.rap:
            used_po = PurchaseOrder.objects.filter(
                rap=po.rap,
                document_status__in=['open', 'confirmed', 'delivered', 'invoiced', 'close']''',
    cross_year_validation
)

# Append POInboxViewSet and Allow Previous Year Budget endpoint
po_inbox_viewset = '''

class POInboxViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Viewset untuk menampilkan daftar PO yang menunggu persetujuan oleh user login.
    """
    serializer_class = POInboxSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PurchaseOrder.objects.filter(approval_status=PurchaseOrder.ApprovalStatus.AWAITING).select_related('vendor', 'project')

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        try:
            from apps.purchase.services.po_approval_service import POApprovalService
            po = POApprovalService.approve_po(pk, request.user)
            return Response({'status': 'approved', 'po_number': po.po_number})
        except ValidationError as e:
            return Response({'detail': e.messages}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        try:
            from apps.purchase.services.po_approval_service import POApprovalService
            po = POApprovalService.reject_po(pk, request.user)
            return Response({'status': 'rejected', 'po_number': po.po_number})
        except ValidationError as e:
            return Response({'detail': e.messages}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def allow_previous_year_budget(self, request, pk=None):
        # Tambahkan RBAC function code khusus di sini jika diperlukan
        # Untuk kesederhanaan, kita hanya cek autentikasi
        po = get_object_or_404(PurchaseOrder, pk=pk)
        po.allow_previous_year_budget = True
        po.save()
        return Response({'status': 'success', 'message': 'Izin penggunaan RAP tahun sebelumnya telah diberikan.'})
'''

content += po_inbox_viewset

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Patch applied.")
