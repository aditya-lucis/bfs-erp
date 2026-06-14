"""
Reusable approval matrix library.

Call `resolve_approval_steps()` from any document module (RAP, PR, PO, etc.)
using the document transaction code as the trigger.
"""

from decimal import Decimal
from typing import Optional

from django.db.models import Prefetch

from django.db import transaction
from django.utils import timezone

from apps.organization.models import Company, Employee, Position
from .constants import ApprovalBasis, DocumentType, ApprovalStatus, StepStatus
from .models import (
    ApprovalMatrix, ApprovalMatrixRange, ApprovalMatrixStep,
    ApprovalRequest, ApprovalRequestStep, DocumentSignature
)


class ApprovalMatrixError(Exception):
    """Raised when no matching matrix or range is found."""


def get_document_types():
    """Return registered document types for settings UI."""
    return [
        {'code': choice.value, 'name': choice.label}
        for choice in DocumentType
    ]


def get_approval_roles():
    """Return available approval step roles."""
    from .constants import ApprovalRole
    return [
        {'code': choice.value, 'name': choice.label}
        for choice in ApprovalRole
    ]


def validate_ranges(ranges_data, basis=ApprovalBasis.AMOUNT):
    """
    Validate range blocks: non-empty, from <= to, no overlapping tiers.
    `ranges_data` is a list of dicts with `from_value` and `to_value`.
    """
    if not ranges_data:
        raise ApprovalMatrixError('Minimal satu range approval harus diisi.')

    parsed = []
    for idx, block in enumerate(ranges_data):
        from_val = Decimal(str(block.get('from_value', 0)))
        to_val = Decimal(str(block.get('to_value', 0)))
        if from_val > to_val:
            raise ApprovalMatrixError(
                f'Range #{idx + 1}: nilai To harus >= From.'
            )
        parsed.append((from_val, to_val, idx))

    parsed.sort(key=lambda x: x[0])
    for i in range(1, len(parsed)):
        prev_to = parsed[i - 1][1]
        curr_from = parsed[i][0]
        if curr_from <= prev_to:
            raise ApprovalMatrixError(
                f'Range #{parsed[i][2] + 1} overlap dengan range sebelumnya.'
            )

    return True


def get_matrix_queryset(company=None):
    """Optimized queryset with nested ranges and steps."""
    company = company or Company.get_default()
    return ApprovalMatrix.objects.filter(
        company=company,
        is_active=True,
    ).select_related(
        'creator_position__department',
    ).prefetch_related(
        Prefetch(
            'ranges',
            queryset=ApprovalMatrixRange.objects.prefetch_related(
                Prefetch(
                    'steps',
                    queryset=ApprovalMatrixStep.objects.select_related(
                        'position__department',
                    ).order_by('step_number'),
                ),
            ).order_by('order_no', 'from_value'),
        ),
    )


def find_matrix(
    document_code: str,
    creator_position_id: int,
    company=None,
) -> Optional[ApprovalMatrix]:
    """Find active matrix for document + creator position."""
    company = company or Company.get_default()
    return get_matrix_queryset(company).filter(
        document_code=document_code,
        creator_position_id=creator_position_id,
    ).first()


def _match_range(
    matrix: ApprovalMatrix,
    value: Decimal,
) -> Optional[ApprovalMatrixRange]:
    """Pick the range tier that contains `value`."""
    for block in matrix.ranges.all():
        if block.from_value <= value <= block.to_value:
            return block
    return None


def resolve_approval_steps(
    document_code: str,
    creator_position_id: int,
    *,
    amount: Optional[Decimal] = None,
    quantity: Optional[Decimal] = None,
    company=None,
) -> dict:
    """
    Resolve approval workflow for a document submission.

    Returns dict with matrix info and ordered steps including position details.
    Raises ApprovalMatrixError if matrix or matching range not found.
    """
    matrix = find_matrix(document_code, creator_position_id, company)
    if not matrix:
        raise ApprovalMatrixError(
            f'Matrix approval untuk dokumen {document_code} '
            f'dan posisi creator tidak ditemukan.'
        )

    if matrix.basis == ApprovalBasis.AMOUNT:
        if amount is None:
            raise ApprovalMatrixError('Parameter amount wajib diisi untuk basis AMOUNT.')
        lookup_value = Decimal(str(amount))
    else:
        if quantity is None:
            raise ApprovalMatrixError('Parameter quantity wajib diisi untuk basis QUANTITY.')
        lookup_value = Decimal(str(quantity))

    matched = _match_range(matrix, lookup_value)
    if not matched:
        raise ApprovalMatrixError(
            f'Nilai {lookup_value} tidak masuk dalam range approval manapun.'
        )

    steps = []
    for step in matched.steps.all():
        steps.append(_serialize_step(step))

    return {
        'matrix_id': matrix.id,
        'document_code': matrix.document_code,
        'document_name': matrix.document_name,
        'creator_position_id': matrix.creator_position_id,
        'creator_position_name': matrix.creator_position.name,
        'basis': matrix.basis,
        'lookup_value': str(lookup_value),
        'matched_range': {
            'id': matched.id,
            'from_value': str(matched.from_value),
            'to_value': str(matched.to_value),
        },
        'steps': steps,
    }


def _serialize_step(step: ApprovalMatrixStep) -> dict:
    pos = step.position
    return {
        'step_number': step.step_number,
        'role': step.role,
        'role_display': step.get_role_display(),
        'position_id': pos.id,
        'position_code': pos.code,
        'position_name': pos.name,
        'department_id': pos.department_id,
        'department_name': pos.department.name if pos.department else '',
    }


def get_approver_employees(position_id: int, active_only=True):
    """
    Return employees at a position — used when routing to inbox/approver.
    """
    qs = Employee.objects.filter(position_id=position_id).select_related(
        'position__department', 'user',
    )
    if active_only:
        qs = qs.filter(status='active')
    return qs


def get_approver_users(position_id: int):
    """Return user IDs eligible to act on a step (employees with linked users)."""
    employees = get_approver_employees(position_id)
    return [
        emp.user_id
        for emp in employees
        if emp.user_id
    ]


@transaction.atomic
def create_approval_request(
    document_code: str,
    document_id: str,
    document_number: str,
    creator_user,
    amount: Optional[Decimal] = None,
    quantity: Optional[Decimal] = None,
    company=None,
) -> ApprovalRequest:
    """
    Initiate an approval request for a document transaction.
    Resolves matrix steps and creates request steps and signature blocks.
    """
    company = company or Company.get_default()
    
    # Get creator employee and position
    employee = getattr(creator_user, 'employee_profile', None)
    if not employee:
        raise ApprovalMatrixError("User tidak memiliki profile Employee yang valid.")
    
    creator_position = employee.position
    
    # Resolve steps
    resolved = resolve_approval_steps(
        document_code=document_code,
        creator_position_id=creator_position.id,
        amount=amount,
        quantity=quantity,
        company=company,
    )
    
    # If there is already an existing PENDING/APPROVED request for this document, delete or deactivate it
    ApprovalRequest.objects.filter(
        company=company,
        document_code=document_code,
        document_id=document_id
    ).delete()
    
    DocumentSignature.objects.filter(
        company=company,
        document_code=document_code,
        document_id=document_id
    ).delete()
    
    # Create request header
    request = ApprovalRequest.objects.create(
        company=company,
        document_code=document_code,
        document_id=document_id,
        document_number=document_number,
        creator=creator_user,
        creator_position=creator_position,
        basis=resolved['basis'],
        amount=amount,
        quantity=quantity,
        status=ApprovalStatus.PENDING,
        current_step_number=1,
    )
    
    # Create steps & signature placeholders
    for step_data in resolved['steps']:
        # Create transaction step
        ApprovalRequestStep.objects.create(
            approval_request=request,
            step_number=step_data['step_number'],
            role=step_data['role'],
            position_id=step_data['position_id'],
            status=StepStatus.PENDING,
        )
        
        # Create signature placeholder
        DocumentSignature.objects.create(
            company=company,
            document_code=document_code,
            document_id=document_id,
            document_number=document_number,
            step_number=step_data['step_number'],
            role=step_data['role'],
            position_id=step_data['position_id'],
            is_signed=False,
        )
        
    return request


@transaction.atomic
def approve_step(
    approval_request_id: int,
    user,
    remarks: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> ApprovalRequest:
    """
    Approve the current active step in an approval request.
    Stamps the corresponding DocumentSignature block with user signature.
    """
    request = ApprovalRequest.objects.select_for_update().get(id=approval_request_id)
    if request.status != ApprovalStatus.PENDING:
        raise ApprovalMatrixError("Request approval tidak dalam status PENDING.")
        
    current_step = request.steps.filter(
        step_number=request.current_step_number,
        status=StepStatus.PENDING
    ).first()
    
    if not current_step:
        raise ApprovalMatrixError("Step pending saat ini tidak ditemukan.")
        
    # Check authorization (user position must match or user is superuser)
    employee = getattr(user, 'employee_profile', None)
    if not employee and not user.is_superuser:
        raise ApprovalMatrixError("User tidak memiliki profile Employee.")
        
    if not user.is_superuser and employee.position_id != current_step.position_id:
        raise ApprovalMatrixError("Posisi Anda tidak berwenang menyetujui step ini.")
        
    # Mark step as approved
    current_step.status = StepStatus.APPROVED
    current_step.approved_by = user
    current_step.approved_at = timezone.now()
    current_step.remarks = remarks or ''
    current_step.save()
    
    # Stamp DocumentSignature
    sig = DocumentSignature.objects.filter(
        company=request.company,
        document_code=request.document_code,
        document_id=request.document_id,
        step_number=request.current_step_number,
    ).first()
    
    if sig:
        sig.user = user
        sig.is_signed = True
        sig.signed_at = current_step.approved_at
        sig.ip_address = ip_address
        sig.user_agent = user_agent or ''
        
        # Copy signature graphics from employee profile if available
        if employee:
            sig.signature_draw = employee.signature_draw or ''
            if employee.signature_image:
                sig.signature_image = employee.signature_image.url
        sig.save()
        
    # Advance step or finish approval
    next_step = request.steps.filter(
        step_number=request.current_step_number + 1
    ).first()
    
    if next_step:
        request.current_step_number += 1
    else:
        request.status = ApprovalStatus.APPROVED
        
    request.save()
    return request


@transaction.atomic
def reject_request(
    approval_request_id: int,
    user,
    remarks: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> ApprovalRequest:
    """
    Reject the approval request at the current step.
    Skips all remaining steps.
    """
    if not remarks:
        raise ApprovalMatrixError("Alasan penolakan (remarks) wajib diisi.")
        
    request = ApprovalRequest.objects.select_for_update().get(id=approval_request_id)
    if request.status != ApprovalStatus.PENDING:
        raise ApprovalMatrixError("Request approval tidak dalam status PENDING.")
        
    current_step = request.steps.filter(
        step_number=request.current_step_number,
        status=StepStatus.PENDING
    ).first()
    
    if not current_step:
        raise ApprovalMatrixError("Step pending saat ini tidak ditemukan.")
        
    # Check authorization
    employee = getattr(user, 'employee_profile', None)
    if not employee and not user.is_superuser:
        raise ApprovalMatrixError("User tidak memiliki profile Employee.")
        
    if not user.is_superuser and employee.position_id != current_step.position_id:
        raise ApprovalMatrixError("Posisi Anda tidak berwenang menolak step ini.")
        
    # Mark step as rejected
    current_step.status = StepStatus.REJECTED
    current_step.approved_by = user
    current_step.approved_at = timezone.now()
    current_step.remarks = remarks
    current_step.save()
    
    # Skip remaining steps
    request.steps.filter(step_number__gt=request.current_step_number).update(
        status=StepStatus.SKIPPED
    )
    
    # Reject request
    request.status = ApprovalStatus.REJECTED
    request.save()
    
    return request


def get_document_signatures(document_code: str, document_id: str):
    """
    Retrieve all signature blocks for a document, ordered by step sequence.
    """
    return DocumentSignature.objects.filter(
        document_code=document_code,
        document_id=document_id
    ).select_related('position', 'user__employee_profile').order_by('step_number')


@transaction.atomic
def revise_request(
    approval_request_id: int,
    user,
    remarks: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> ApprovalRequest:
    """
    Request a revision at the current step. Skips remaining steps and sets request status to CANCELLED.
    """
    if not remarks:
        raise ApprovalMatrixError("Alasan revisi (remarks) wajib diisi.")
        
    request = ApprovalRequest.objects.select_for_update().get(id=approval_request_id)
    if request.status != ApprovalStatus.PENDING:
        raise ApprovalMatrixError("Request approval tidak dalam status PENDING.")
        
    current_step = request.steps.filter(
        step_number=request.current_step_number,
        status=StepStatus.PENDING
    ).first()
    
    if not current_step:
        raise ApprovalMatrixError("Step pending saat ini tidak ditemukan.")
        
    # Check authorization
    employee = getattr(user, 'employee_profile', None)
    if not employee and not user.is_superuser:
        raise ApprovalMatrixError("User tidak memiliki profile Employee.")
        
    if not user.is_superuser and employee.position_id != current_step.position_id:
        raise ApprovalMatrixError("Posisi Anda tidak berwenang meminta revisi step ini.")
        
    # Mark step as rejected with revision comment
    current_step.status = StepStatus.REJECTED
    current_step.approved_by = user
    current_step.approved_at = timezone.now()
    current_step.remarks = f"[REVISI] {remarks}"
    current_step.save()
    
    # Skip remaining steps
    request.steps.filter(step_number__gt=request.current_step_number).update(
        status=StepStatus.SKIPPED
    )
    
    # Cancel request (representing Revised)
    request.status = ApprovalStatus.CANCELLED
    request.save()
    
    return request

