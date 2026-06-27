from decimal import Decimal
from django.db import transaction
from rest_framework.exceptions import ValidationError
from django.utils import timezone

from apps.purchase.models import PurchaseOrder, PurchaseOrderDetail, PurchaseRequisition
from apps.projects.models import RAPDetail, ProjectBudgetHeader, ProjectBudgetDetail
from apps.budget_component.models import BudgetCommitmentLog
from apps.inventory.models import ItemAccountLink, AccountPurpose

class POApprovalService:
    @staticmethod
    @transaction.atomic
    def approve_po(po_id, user):
        po = PurchaseOrder.objects.select_for_update().get(id=po_id)
        
        if po.approval_status in [PurchaseOrder.ApprovalStatus.APPROVED, PurchaseOrder.ApprovalStatus.REJECTED]:
            raise ValidationError(f"Cannot approve PO with status {po.approval_status}")
            
        details = po.details.select_related('item', 'rap_detail').all()
        
        # 1. Validate Budget (RAP) & COA Item mapping
        for detail in details:
            # Check Item COA mapping
            account = None
            if detail.item:
                account_link = ItemAccountLink.objects.filter(
                    item=detail.item,
                    purpose=AccountPurpose.PURCHASE
                ).first()
                if not account_link or not account_link.account:
                    raise ValidationError(f"Item {detail.item.item_code} tidak memiliki mapping akun Purchase (COA).")
                account = account_link.account

            if detail.rap_detail:
                rap_detail = RAPDetail.objects.select_for_update().get(id=detail.rap_detail_id)
                
                # Create or get ProjectBudgetHeader
                budget_header, _ = ProjectBudgetHeader.objects.get_or_create(
                    project=po.project,
                    defaults={'created_by': user}
                )
                
                # Create or get ProjectBudgetDetail
                try:
                    budget_detail = ProjectBudgetDetail.objects.select_for_update().get(rap_detail=rap_detail)
                except ProjectBudgetDetail.DoesNotExist:
                    budget_detail = ProjectBudgetDetail.objects.create(
                        budget_header=budget_header,
                        rap_detail=rap_detail,
                        item=detail.item
                    )

                # Validate Budget
                new_commit_total = budget_detail.commit_amount + detail.amount
                if new_commit_total > rap_detail.total_cost:
                    raise ValidationError(f"OverBudget: Item {detail.item.item_name} melebihi alokasi RAP. (RAP: {rap_detail.total_cost}, Commited + PO: {new_commit_total})")
                
                # 2. Insert BudgetCommitmentLog
                BudgetCommitmentLog.objects.create(
                    document_type=BudgetCommitmentLog.DocumentType.PO,
                    document_no=po.po_number,
                    amount=detail.amount,
                    department=rap_detail.rap.department,
                    rap_detail=rap_detail,
                    account=account,
                    month=po.po_date.month,
                    year=po.po_date.year,
                    created_by=user
                )

                # Update budget amounts
                budget_detail.commit_amount = new_commit_total
                budget_detail.save()

                budget_header.commit_amount_total += detail.amount
                budget_header.save()

        # Update PO Status
        po.approval_status = PurchaseOrder.ApprovalStatus.APPROVED
        po.document_status = PurchaseOrder.DocumentStatus.OPEN
        po.is_active = True
        po.save()

        # 3. PR Auto-Close Logic
        pr_ids = set([d.pr_detail.pr_id for d in details if d.pr_detail])
        for pr_id in pr_ids:
            pr = PurchaseRequisition.objects.get(id=pr_id)
            all_fulfilled = True
            for pr_detail in pr.details.all():
                ordered_qty = sum(pd.quantity for pd in pr_detail.po_details.filter(po__approval_status=PurchaseOrder.ApprovalStatus.APPROVED))
                if ordered_qty < pr_detail.quantity:
                    all_fulfilled = False
                    break
            if all_fulfilled:
                pr.document_status = PurchaseRequisition.DocumentStatus.CLOSE
                pr.save()

        return po
        
    @staticmethod
    @transaction.atomic
    def reject_po(po_id, user):
        po = PurchaseOrder.objects.select_for_update().get(id=po_id)
        
        if po.approval_status in [PurchaseOrder.ApprovalStatus.APPROVED, PurchaseOrder.ApprovalStatus.REJECTED]:
            raise ValidationError(f"Cannot reject PO with status {po.approval_status}")
            
        po.approval_status = PurchaseOrder.ApprovalStatus.REJECTED
        po.save()
        return po
