from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.approval.models import ApprovalRequest
from apps.approval.constants import ApprovalStatus
from apps.purchase.models import PurchaseRequisition, PurchaseOrder

@receiver(post_save, sender=ApprovalRequest)
def sync_purchase_approval_status(sender, instance, **kwargs):
    if instance.document_code == 'PR':
        try:
            pr = PurchaseRequisition.objects.get(pk=int(instance.document_id))
            if instance.status == ApprovalStatus.APPROVED:
                pr.approval_status = PurchaseRequisition.ApprovalStatus.APPROVED
                pr.document_status = PurchaseRequisition.DocumentStatus.DRAFT
                pr.save()
            elif instance.status == ApprovalStatus.REJECTED:
                pr.approval_status = PurchaseRequisition.ApprovalStatus.REJECTED
                pr.document_status = PurchaseRequisition.DocumentStatus.DRAFT
                pr.save()
            elif instance.status == ApprovalStatus.CANCELLED:
                # Cancelled maps to revised/draft in this workflow
                pr.approval_status = PurchaseRequisition.ApprovalStatus.REVISED
                pr.document_status = PurchaseRequisition.DocumentStatus.DRAFT
                pr.save()
        except (PurchaseRequisition.DoesNotExist, ValueError):
            pass
    elif instance.document_code == 'PO':
        try:
            from apps.purchase.services.po_approval_service import POApprovalService
            po = PurchaseOrder.objects.get(pk=int(instance.document_id))
            if instance.status == ApprovalStatus.APPROVED:
                POApprovalService.approve_po(po.id, instance.creator)
            elif instance.status == ApprovalStatus.REJECTED:
                # Instead of closing, set to draft/revised so it can be edited
                po.approval_status = PurchaseOrder.ApprovalStatus.REVISED
                po.document_status = PurchaseOrder.DocumentStatus.DRAFT
                po.save()
            elif instance.status == ApprovalStatus.CANCELLED:
                po.approval_status = PurchaseOrder.ApprovalStatus.REVISED
                po.document_status = PurchaseOrder.DocumentStatus.DRAFT
                po.save()
        except (PurchaseOrder.DoesNotExist, ValueError):
            pass
    elif instance.document_code == 'CC':
        try:
            from apps.purchase.models import CompletionCertificate
            cc = CompletionCertificate.objects.get(pk=int(instance.document_id))
            if instance.status == ApprovalStatus.APPROVED:
                cc.approval_status = 'approved'
                cc.is_active = True
                cc.save()
            elif instance.status == ApprovalStatus.REJECTED:
                cc.approval_status = 'rejected'
                cc.save()
            elif instance.status == ApprovalStatus.CANCELLED:
                cc.approval_status = 'revised'
                cc.save()
        except (CompletionCertificate.DoesNotExist, ValueError, ImportError):
            pass
