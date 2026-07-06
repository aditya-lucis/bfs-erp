from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from django.db.models import F

from apps.approval.models import ApprovalRequest
from apps.approval.constants import ApprovalStatus
from apps.inventory.models import ReceiptReport, AccountPurpose
from apps.accounting.models import JournalHeader, JournalDetail


@receiver(post_save, sender=ApprovalRequest)
def on_receipt_report_approved(sender, instance, **kwargs):
    if instance.document_code == 'RECEIPT_REPORT':
        try:
            with transaction.atomic():
                rr = ReceiptReport.objects.get(pk=int(instance.document_id))
                
                if instance.status == ApprovalStatus.APPROVED:
                    rr.approval_status = ReceiptReport.ApprovalStatus.APPROVED
                    rr.document_status = ReceiptReport.DocumentStatus.CLOSE
                    rr.save(update_fields=['approval_status', 'document_status'])
                    
                    po = rr.po

                    # Generate Journal if not already exists
                    if not JournalHeader.objects.filter(journal_number=rr.receipt_number).exists():
                        journal_header = None
                        
                        for item in rr.items.all():
                            # Increment PO Detail received_qty
                            if item.po_item:
                                po_item = item.po_item
                                po_item.received_qty = F('received_qty') + item.receive_qty
                                po_item.save(update_fields=['received_qty'])
                                
                                # Note: the user explicitly requested NOT to modify the 
                                # PurchaseOrder DocumentStatus here. We ONLY update received_qty.
                            
                            # Conditionally generate GL Journal
                            if item.item.view_inventory:
                                asset_link = item.item.account_links.filter(
                                    purpose=AccountPurpose.INVENTORY,
                                    currency__in=['ALL', po.po_currency if po else 'IDR']
                                ).first()
                                
                                purchase_link = item.item.account_links.filter(
                                    purpose=AccountPurpose.PURCHASE,
                                    currency__in=['ALL', po.po_currency if po else 'IDR']
                                ).first()
                                
                                if asset_link and purchase_link:
                                    if not journal_header:
                                        journal_header = JournalHeader.objects.create(
                                            journal_number=rr.receipt_number,
                                            company=rr.company,
                                            date=rr.receive_date,
                                            memo=f"Receipt Report: {rr.receipt_number}",
                                            project=po.project if po else None,
                                            created_by=rr.created_by,
                                            type='INV'
                                        )
                                        
                                    amount = item.receive_qty * (item.po_item.unit_price if item.po_item else 0)
                                    
                                    # Currency logic
                                    asset_curr = asset_link.currency if asset_link.currency != 'ALL' else (po.po_currency if po else 'IDR')
                                    pur_curr = purchase_link.currency if purchase_link.currency != 'ALL' else (po.po_currency if po else 'IDR')
                                    
                                    # Debit Asset
                                    JournalDetail.objects.create(
                                        journal_header=journal_header,
                                        account=asset_link.account,
                                        currency=asset_curr,
                                        base_debet=amount,
                                        base_kredit=0
                                    )
                                    
                                    # Credit Purchase (Liability)
                                    JournalDetail.objects.create(
                                        journal_header=journal_header,
                                        account=purchase_link.account,
                                        currency=pur_curr,
                                        base_debet=0,
                                        base_kredit=amount
                                    )
                                    
                                    # Update Account Balances
                                    asset_account = asset_link.account
                                    asset_account.month_debet = F('month_debet') + amount
                                    if asset_account.default_position == 'DEBET':
                                        asset_account.amount = F('amount') + amount
                                    else:
                                        asset_account.amount = F('amount') - amount
                                    asset_account.save(update_fields=['month_debet', 'amount'])
                                    
                                    pur_account = purchase_link.account
                                    pur_account.month_kredit = F('month_kredit') + amount
                                    if pur_account.default_position == 'DEBET':
                                        pur_account.amount = F('amount') - amount
                                    else:
                                        pur_account.amount = F('amount') + amount
                                    pur_account.save(update_fields=['month_kredit', 'amount'])

                elif instance.status == ApprovalStatus.REJECTED:
                    rr.approval_status = ReceiptReport.ApprovalStatus.REJECTED
                    rr.document_status = ReceiptReport.DocumentStatus.CLOSE
                    rr.save(update_fields=['approval_status', 'document_status'])
                    
                elif instance.status == ApprovalStatus.CANCELLED:
                    rr.approval_status = ReceiptReport.ApprovalStatus.REVISED
                    rr.document_status = ReceiptReport.DocumentStatus.DRAFT
                    rr.save(update_fields=['approval_status', 'document_status'])
                    
        except (ReceiptReport.DoesNotExist, ValueError):
            pass
