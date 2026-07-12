from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.approval.models import ApprovalRequest
from apps.approval.constants import ApprovalStatus
from apps.accounting.models import GeneralJournalTransaction, DocumentStatus, JournalHeader, JournalDetail

@receiver(post_save, sender=ApprovalRequest)
def sync_gej_approval_status(sender, instance, **kwargs):
    if instance.document_code == 'GEJ':
        try:
            transaction = GeneralJournalTransaction.objects.get(pk=int(instance.document_id))
            
            if instance.status == ApprovalStatus.APPROVED:
                transaction.status = DocumentStatus.APPROVED
                transaction.save()
                
                # Check if JournalHeader already exists for this transaction
                if not JournalHeader.objects.filter(journal_number=transaction.transaction_number).exists():
                    # Post to Journal
                    journal = JournalHeader.objects.create(
                        journal_number=transaction.transaction_number,
                        company=transaction.company,
                        date=transaction.date,
                        memo=transaction.memo,
                        project=transaction.project,
                        created_by=transaction.created_by,
                        type='GEN'
                    )
                    
                    for detail in transaction.details.all():
                        JournalDetail.objects.create(
                            journal_header=journal,
                            account=detail.account,
                            currency=detail.currency,
                            base_debet=detail.debit,
                            base_kredit=detail.credit
                        )
                        
                        # Update Account Balances
                        if detail.account:
                            # using F expression to prevent race conditions
                            from django.db.models import F
                            detail.account.month_debet = F('month_debet') + detail.debit
                            detail.account.month_kredit = F('month_kredit') + detail.credit
                            
                            if detail.account.default_position == 'DEBET':
                                detail.account.amount = F('amount') + detail.debit - detail.credit
                            else:
                                detail.account.amount = F('amount') + detail.credit - detail.debit
                                
                            detail.account.save(update_fields=['month_debet', 'month_kredit', 'amount'])
                            
            elif instance.status == ApprovalStatus.REJECTED:
                transaction.status = DocumentStatus.REJECTED
                transaction.save()
                
            elif instance.status == ApprovalStatus.CANCELLED:
                transaction.status = DocumentStatus.CANCELLED
                transaction.save()
                
        except (GeneralJournalTransaction.DoesNotExist, ValueError):
            pass

@receiver(post_save, sender=ApprovalRequest)
def sync_cashbook_req_approval_status(sender, instance, **kwargs):
    if instance.document_code and instance.document_code.startswith('CBR_'):
        try:
            from apps.accounting.models import CashbookReqHeader
            transaction = CashbookReqHeader.objects.get(pk=int(instance.document_id))
            
            if instance.status == ApprovalStatus.APPROVED:
                transaction.approval_status = CashbookReqHeader.ApprovalStatus.APPROVED
                transaction.document_status = CashbookReqHeader.DocumentStatus.CLOSE
                transaction.save()
            elif instance.status == ApprovalStatus.REJECTED:
                transaction.approval_status = CashbookReqHeader.ApprovalStatus.REJECTED
                transaction.document_status = CashbookReqHeader.DocumentStatus.CLOSE
                transaction.save()
            elif instance.status == ApprovalStatus.CANCELLED:
                transaction.approval_status = CashbookReqHeader.ApprovalStatus.REVISED
                transaction.document_status = CashbookReqHeader.DocumentStatus.DRAFT
                transaction.save()
        except (CashbookReqHeader.DoesNotExist, ValueError, ImportError):
            pass
