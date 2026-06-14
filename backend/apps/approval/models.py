"""
BFS ERP — Matrix of Approval

Defines approval workflows per document type, creator position, and value range.
"""

from decimal import Decimal

from django.db import models
from django.core.exceptions import ValidationError

from config import settings
from .constants import DocumentType, ApprovalBasis, ApprovalRole, ApprovalStatus, StepStatus


class ApprovalMatrix(models.Model):
    """
    Header: one matrix per (company, document_code, creator_position).
    """
    company = models.ForeignKey(
        'organization.Company',
        on_delete=models.CASCADE,
        related_name='approval_matrices',
    )
    document_code = models.CharField(
        max_length=20,
        choices=DocumentType.choices,
        help_text='Kode transaksi/dokumen, e.g. RAP, PR, PO',
    )
    creator_position = models.ForeignKey(
        'organization.Position',
        on_delete=models.PROTECT,
        related_name='approval_matrices_as_creator',
        help_text='Posisi employee yang membuat dokumen',
    )
    basis = models.CharField(
        max_length=10,
        choices=ApprovalBasis.choices,
        default=ApprovalBasis.AMOUNT,
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='created_approval_matrices',
    )

    class Meta:
        db_table = 'approval_matrix'
        unique_together = ('company', 'document_code', 'creator_position')
        ordering = ['document_code', 'creator_position__name']
        verbose_name = 'Approval Matrix'
        verbose_name_plural = 'Approval Matrices'

    def __str__(self):
        return (
            f"{self.document_code} — "
            f"{self.creator_position.name} [{self.get_basis_display()}]"
        )

    @property
    def document_name(self):
        return DocumentType(self.document_code).label


class ApprovalMatrixRange(models.Model):
    """Value tier within a matrix (e.g. 0–15M, 15M–25M)."""
    matrix = models.ForeignKey(
        ApprovalMatrix,
        on_delete=models.CASCADE,
        related_name='ranges',
    )
    from_value = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal('0'))
    to_value = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal('0'))
    order_no = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = 'approval_matrix_range'
        ordering = ['order_no', 'from_value']
        verbose_name = 'Approval Matrix Range'
        verbose_name_plural = 'Approval Matrix Ranges'

    def __str__(self):
        return f"{self.from_value} – {self.to_value}"

    def clean(self):
        if self.from_value > self.to_value:
            raise ValidationError({'to_value': 'To value must be >= From value.'})


class ApprovalMatrixStep(models.Model):
    """Single approval step within a range tier."""
    range = models.ForeignKey(
        ApprovalMatrixRange,
        on_delete=models.CASCADE,
        related_name='steps',
    )
    step_number = models.PositiveSmallIntegerField()
    role = models.CharField(max_length=20, choices=ApprovalRole.choices)
    position = models.ForeignKey(
        'organization.Position',
        on_delete=models.PROTECT,
        related_name='approval_matrix_steps',
        help_text='Posisi yang bertanggung jawab pada step ini',
    )

    class Meta:
        db_table = 'approval_matrix_step'
        ordering = ['step_number']
        unique_together = ('range', 'step_number')
        verbose_name = 'Approval Matrix Step'
        verbose_name_plural = 'Approval Matrix Steps'

    def __str__(self):
        return f"Step {self.step_number}: {self.get_role_display()} — {self.position.name}"


class ApprovalRequest(models.Model):
    """
    Header of a document approval transaction.
    """
    company = models.ForeignKey(
        'organization.Company',
        on_delete=models.CASCADE,
        related_name='approval_requests',
    )
    document_code = models.CharField(
        max_length=20,
        choices=DocumentType.choices,
        help_text='Kode transaksi/dokumen, e.g. RAP, PR, PO',
    )
    document_id = models.CharField(
        max_length=50,
        help_text='ID of the target document instance'
    )
    document_number = models.CharField(
        max_length=100,
        help_text='Nomor dokumen/kode transaksi, e.g. RAP-2026-0001'
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='submitted_approval_requests',
    )
    creator_position = models.ForeignKey(
        'organization.Position',
        on_delete=models.PROTECT,
        related_name='creator_approval_requests',
    )
    basis = models.CharField(
        max_length=10,
        choices=ApprovalBasis.choices,
        default=ApprovalBasis.AMOUNT,
    )
    amount = models.DecimalField(
        max_digits=18, decimal_places=2, null=True, blank=True
    )
    quantity = models.DecimalField(
        max_digits=18, decimal_places=2, null=True, blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=ApprovalStatus.choices,
        default=ApprovalStatus.PENDING,
    )
    current_step_number = models.PositiveSmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'approval_request'
        ordering = ['-created_at']
        unique_together = ('company', 'document_code', 'document_id')
        verbose_name = 'Approval Request'
        verbose_name_plural = 'Approval Requests'

    def __str__(self):
        return f"{self.document_code} {self.document_number} — {self.get_status_display()}"


class ApprovalRequestStep(models.Model):
    """
    Individual step within an approval request transaction.
    """
    approval_request = models.ForeignKey(
        ApprovalRequest,
        on_delete=models.CASCADE,
        related_name='steps',
    )
    step_number = models.PositiveSmallIntegerField()
    role = models.CharField(max_length=20, choices=ApprovalRole.choices)
    position = models.ForeignKey(
        'organization.Position',
        on_delete=models.PROTECT,
        related_name='request_steps',
    )
    status = models.CharField(
        max_length=20,
        choices=StepStatus.choices,
        default=StepStatus.PENDING,
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='actioned_approval_steps',
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        db_table = 'approval_request_step'
        ordering = ['step_number']
        unique_together = ('approval_request', 'step_number')
        verbose_name = 'Approval Request Step'
        verbose_name_plural = 'Approval Request Steps'

    def __str__(self):
        return f"{self.approval_request.document_number} Step {self.step_number}: {self.role} ({self.position.name})"


class DocumentSignature(models.Model):
    """
    Signatures registry / blocks for documents.
    Generates footers/printed signature requirements and tracks signed states.
    """
    company = models.ForeignKey(
        'organization.Company',
        on_delete=models.CASCADE,
        related_name='document_signatures',
    )
    document_code = models.CharField(
        max_length=20,
        choices=DocumentType.choices,
    )
    document_id = models.CharField(
        max_length=50,
    )
    document_number = models.CharField(
        max_length=100,
    )
    step_number = models.PositiveSmallIntegerField()
    role = models.CharField(max_length=20, choices=ApprovalRole.choices)
    position = models.ForeignKey(
        'organization.Position',
        on_delete=models.PROTECT,
        related_name='document_signatures',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='document_signatures',
    )
    is_signed = models.BooleanField(default=False)
    signed_at = models.DateTimeField(null=True, blank=True)
    signature_draw = models.TextField(
        blank=True,
        help_text='Base64 canvas drawing snapshot at time of signing'
    )
    signature_image = models.CharField(
        max_length=500,
        blank=True,
        help_text='URL path to uploaded signature image snapshot at time of signing'
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'document_signature'
        ordering = ['document_code', 'document_id', 'step_number']
        unique_together = ('company', 'document_code', 'document_id', 'step_number')
        verbose_name = 'Document Signature'
        verbose_name_plural = 'Document Signatures'

    def __str__(self):
        status = "SIGNED" if self.is_signed else "PENDING"
        return f"{self.document_code} {self.document_number} — {self.role} ({status})"

