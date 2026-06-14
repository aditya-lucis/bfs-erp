from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.approval.models import ApprovalRequest
from apps.approval.constants import ApprovalStatus
from apps.projects.models import RAP

@receiver(post_save, sender=ApprovalRequest)
def sync_rap_approval_status(sender, instance, **kwargs):
    if instance.document_code == 'RAP':
        try:
            rap = RAP.objects.get(pk=int(instance.document_id))
            if instance.status == ApprovalStatus.APPROVED:
                rap.approval_status = 'approved'
                rap.document_status = 'close'
                rap.is_active = True
                rap.save()
            elif instance.status == ApprovalStatus.REJECTED:
                rap.approval_status = 'rejected'
                rap.document_status = 'close'
                rap.is_active = False
                rap.save()
            elif instance.status == ApprovalStatus.CANCELLED:
                rap.approval_status = 'revised'
                rap.document_status = 'draft'
                rap.is_active = False
                rap.save()
        except (RAP.DoesNotExist, ValueError):
            pass
