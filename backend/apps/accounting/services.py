from django.db import transaction
from django.utils import timezone
from .models import CashbookReqHeader, BudgetRequest
from rest_framework.exceptions import ValidationError

@transaction.atomic
def close_cashbook_request_service(request_id, reason, user=None):
    """
    Service to handle the complex logic of closing a Cashbook Request.
    This replaces the legacy qactive.cfm logic, minus the accrued expense reversal.
    """
    try:
        cashbook_req = CashbookReqHeader.objects.get(id=request_id)
    except CashbookReqHeader.DoesNotExist:
        raise ValidationError(f"Cashbook Request with ID {request_id} does not exist.")

    # 1. Validate Approval Status
    invalid_statuses = [
        CashbookReqHeader.ApprovalStatus.DRAFT,
        CashbookReqHeader.ApprovalStatus.REJECTED,
        CashbookReqHeader.ApprovalStatus.REVISED,
    ]
    if cashbook_req.approval_status in invalid_statuses:
        raise ValidationError(f"Please Reject or Revise this Document {cashbook_req.document_number} (Status: {cashbook_req.approval_status})")
        
    if cashbook_req.is_close:
        raise ValidationError(f"This Document {cashbook_req.document_number} is already closed.")
        
    if cashbook_req.paid_status in [CashbookReqHeader.PaidStatus.FULL_PAID, CashbookReqHeader.PaidStatus.HALF_PAID]:
        raise ValidationError(f"This Document {cashbook_req.document_number} is already {cashbook_req.paid_status}.")

    # 2. Check if there are any pending unapproved payments (Placeholder)
    # TODO: Implement check for unapproved GeneralJournalTransaction or CashbookHeader linked to this request
    # Example logic:
    # if has_unapproved_payment(cashbook_req):
    #     raise ValidationError(f"This Document {cashbook_req.document_number} already has a payment, but not approved yet.")

    # 3. Update CashbookReqHeader
    cashbook_req.is_close = True
    cashbook_req.close_reason = reason
    cashbook_req.close_date = timezone.now()
    if user:
        cashbook_req.updated_by = user
    cashbook_req.save()

    # 4. Reset BudgetRequest status if exists
    if hasattr(cashbook_req, 'budget_request'):
        budget_request = cashbook_req.budget_request
        budget_request.budgetrequest_status = BudgetRequest.ActionStatus.NONE
        if user:
            budget_request.updated_by = user
        budget_request.save()

    # 5. Delete ProjectCashAdvanced (Placeholder)
    # TODO: Implement logic to delete ProjectCashAdvanced when the model is available in apps.projects
    # Example:
    # ProjectCashAdvance.objects.filter(document_no=cashbook_req.document_number).delete()

    return cashbook_req
