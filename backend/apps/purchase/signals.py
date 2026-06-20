from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.approval.models import ApprovalRequest
from apps.approval.constants import ApprovalStatus
from apps.purchase.models import PurchaseRequisition

@receiver(post_save, sender=ApprovalRequest)
def sync_pr_approval_status(sender, instance, **kwargs):
    if instance.document_code == 'PR':
        try:
            pr = PurchaseRequisition.objects.get(pk=int(instance.document_id))
            if instance.status == ApprovalStatus.APPROVED:
                pr.approval_status = PurchaseRequisition.ApprovalStatus.APPROVED
                pr.document_status = PurchaseRequisition.DocumentStatus.CLOSE
                pr.save()
            elif instance.status == ApprovalStatus.REJECTED:
                pr.approval_status = PurchaseRequisition.ApprovalStatus.REJECTED
                pr.document_status = PurchaseRequisition.DocumentStatus.CLOSE
                pr.save()
            elif instance.status == ApprovalStatus.CANCELLED:
                # Cancelled maps to revised/draft in this workflow
                pr.approval_status = PurchaseRequisition.ApprovalStatus.REVISED
                pr.document_status = PurchaseRequisition.DocumentStatus.DRAFT
                pr.save()
        except (PurchaseRequisition.DoesNotExist, ValueError):
            pass
