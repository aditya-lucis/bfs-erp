"""
Document types and approval roles for Matrix of Approval.

Add new document codes here as modules (PR, PO, etc.) are implemented.
"""

from django.db import models


class DocumentType(models.TextChoices):
    RAP = 'RAP', 'Rencana Anggaran Pelaksana (RAP)'
    GENERAL_JOURNAL = 'GEJ', 'General Journal (GEJ)'
    PURCHASE_REQUISITION = 'PR', 'Purchase Requisition (PR)'
    PURCHASE_ORDER = 'PO', 'Purchase Order (PO)'
    COMPLETION_CERTIFICATE = 'CC', 'Completion Certificate (CC)'
    GOOD_RECEIPT_NOTE = 'GRN', 'Good Receipt Note (GRN)'
    RECEIPT_REPORT = 'RECEIPT_REPORT', 'Receipt Report (RR)'
    PAYMENT_REQUEST_PI = 'CBR_PI', 'Payment Request (Purchase Invoice)'
    PAYMENT_REQUEST_PCA_UM = 'CBR_PCA_UM', 'Payment Request (PCA - Uang Muka)'
    PAYMENT_REQUEST_PCA_NON_UM = 'CBR_PCA_NON', 'Payment Request (PCA - Non Uang Muka)'
    PAYMENT_REQUEST_BRC_PRINCIPAL = 'CBR_BRC_POKOK', 'Payment Request (Bank Obligation - Principal)'
    PAYMENT_REQUEST_BRC_INTEREST = 'CBR_BRC_BUNGA', 'Payment Request (Bank Obligation - Interest)'

class ApprovalBasis(models.TextChoices):
    AMOUNT   = 'AMOUNT',   'Total Amount (After Disc & Tax)'
    QUANTITY = 'QUANTITY', 'Total Quantity'


class ApprovalRole(models.TextChoices):
    PREPARED_BY    = 'PREPARED_BY',    'Prepared By'
    APPROVED_BY    = 'APPROVED_BY',    'Approved By'
    ACKNOWLEDGE_BY = 'ACKNOWLEDGE_BY', 'Acknowledge By'
    ACCOUNTING_DEPT = 'ACCOUNTING_DEPT', 'Accounting Dept'
    CHECKED_BY     = 'CHECKED_BY',     'Checked By'
    VERIFIED_BY    = 'VERIFIED_BY',    'Verified By'
    ACCEPTED_BY    = 'ACCEPTED_BY',    'Accepted By'


class ApprovalStatus(models.TextChoices):
    DRAFT = 'DRAFT', 'Draft'
    PENDING = 'PENDING', 'Pending'
    APPROVED = 'APPROVED', 'Approved'
    REJECTED = 'REJECTED', 'Rejected'
    CANCELLED = 'CANCELLED', 'Cancelled'


class StepStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    APPROVED = 'APPROVED', 'Approved'
    REJECTED = 'REJECTED', 'Rejected'
    SKIPPED = 'SKIPPED', 'Skipped'

