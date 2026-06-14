import os
import sys
import django
from decimal import Decimal
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.organization.models import Company, Position, Employee
from apps.approval.models import (
    ApprovalMatrix, ApprovalMatrixRange, ApprovalMatrixStep,
    ApprovalRequest, ApprovalRequestStep, DocumentSignature
)
from apps.approval.constants import DocumentType, ApprovalBasis, ApprovalRole, ApprovalStatus, StepStatus

User = get_user_model()

def seed():
    company = Company.get_default()
    if not company:
        print("Company default tidak ditemukan. Silakan jalankan seed_organization terlebih dahulu.")
        return

    # Find roles
    it_prog_pos = Position.objects.filter(code='IT-PROG').first()
    acc_mgr_pos = Position.objects.filter(code='ACC-MGR').first()
    fat_mgr_pos = Position.objects.filter(code='FAT-MGR').first()
    dir_pos = Position.objects.filter(code='DIR').first()

    if not all([it_prog_pos, acc_mgr_pos, fat_mgr_pos, dir_pos]):
        print("Beberapa posisi (IT-PROG, ACC-MGR, FAT-MGR, DIR) tidak ditemukan.")
        return

    # 1. Create matrix settings for RAP creator = IT-PROG
    matrix, created = ApprovalMatrix.objects.update_or_create(
        company=company,
        document_code=DocumentType.RAP,
        creator_position=it_prog_pos,
        defaults={
            'basis': ApprovalBasis.AMOUNT,
            'is_active': True,
        }
    )
    print(f"{'Matrix dibuat' if created else 'Matrix diperbarui'}: {matrix}")

    # Clear old ranges
    matrix.ranges.all().delete()

    # Range 1: 0 - 10,000,000 (Checked by ACC-MGR, Approved by FAT-MGR)
    r1 = ApprovalMatrixRange.objects.create(
        matrix=matrix,
        from_value=Decimal('0'),
        to_value=Decimal('10000000'),
        order_no=0
    )
    ApprovalMatrixStep.objects.create(range=r1, step_number=1, role=ApprovalRole.CHECKED_BY, position=acc_mgr_pos)
    ApprovalMatrixStep.objects.create(range=r1, step_number=2, role=ApprovalRole.APPROVED_BY, position=fat_mgr_pos)

    # Range 2: 10,000,000.01 - 100,000,000 (Checked by ACC-MGR, Verified by FAT-MGR, Approved by DIR)
    r2 = ApprovalMatrixRange.objects.create(
        matrix=matrix,
        from_value=Decimal('10000000.01'),
        to_value=Decimal('100000000'),
        order_no=1
    )
    ApprovalMatrixStep.objects.create(range=r2, step_number=1, role=ApprovalRole.CHECKED_BY, position=acc_mgr_pos)
    ApprovalMatrixStep.objects.create(range=r2, step_number=2, role=ApprovalRole.VERIFIED_BY, position=fat_mgr_pos)
    ApprovalMatrixStep.objects.create(range=r2, step_number=3, role=ApprovalRole.APPROVED_BY, position=dir_pos)

    print("Ranges dan Steps Matrix berhasil dibuat.")

    # Find/Create a user to act as creator (e.g. Aditya)
    aditya_user = User.objects.filter(username='aditya').first()
    if not aditya_user:
        aditya_user = User.objects.filter(email='aditya@bfserp.com').first()
    if not aditya_user:
        aditya_user = User.objects.create_user(
            username='aditya',
            email='aditya@bfserp.com',
            password='password123',
            full_name='Aditya Lucis Caelum'
        )

    # Make sure Aditya user is linked to BFS001 employee profile
    aditya_emp = Employee.objects.filter(employee_id='BFS001').first()
    if aditya_emp:
        # Avoid duplicate key if aditya_user is already linked elsewhere
        Employee.objects.filter(user=aditya_user).update(user=None)
        aditya_emp.user = aditya_user
        aditya_emp.save()

    # Make sure we have a user for ACC-MGR, FAT-MGR, DIR to simulate signing
    # Let's check superuser
    superuser = User.objects.filter(is_superuser=True).first()
    if superuser:
        # Link superuser to an employee with ACC-MGR position so they can approve Step 1
        admin_emp = Employee.objects.filter(user=superuser).first()
        if not admin_emp:
            Employee.objects.create(
                user=superuser,
                position=acc_mgr_pos,
                employee_id='BFS999',
                full_name=superuser.full_name or superuser.username,
                email=superuser.email or 'admin@bfserp.com',
                status='active'
            )
        else:
            admin_emp.position = acc_mgr_pos
            admin_emp.save()

    # Clear old requests
    ApprovalRequest.objects.filter(document_code=DocumentType.RAP).delete()
    DocumentSignature.objects.filter(document_code=DocumentType.RAP).delete()

    # Request 1: 5,000,000 RAP (Pending Step 1 ACC-MGR)
    req1 = ApprovalRequest.objects.create(
        company=company,
        document_code=DocumentType.RAP,
        document_id='1',
        document_number='RAP-2026-0001',
        creator=aditya_user,
        creator_position=it_prog_pos,
        basis=ApprovalBasis.AMOUNT,
        amount=Decimal('5000000'),
        status=ApprovalStatus.PENDING,
        current_step_number=1,
    )
    ApprovalRequestStep.objects.create(
        approval_request=req1, step_number=1, role=ApprovalRole.CHECKED_BY, position=acc_mgr_pos, status=StepStatus.PENDING
    )
    ApprovalRequestStep.objects.create(
        approval_request=req1, step_number=2, role=ApprovalRole.APPROVED_BY, position=fat_mgr_pos, status=StepStatus.PENDING
    )

    DocumentSignature.objects.create(
        company=company, document_code=DocumentType.RAP, document_id='1', document_number='RAP-2026-0001',
        step_number=1, role=ApprovalRole.CHECKED_BY, position=acc_mgr_pos, is_signed=False
    )
    DocumentSignature.objects.create(
        company=company, document_code=DocumentType.RAP, document_id='1', document_number='RAP-2026-0001',
        step_number=2, role=ApprovalRole.APPROVED_BY, position=fat_mgr_pos, is_signed=False
    )

    # Request 2: 25,000,000 RAP (Pending Step 1 ACC-MGR)
    req2 = ApprovalRequest.objects.create(
        company=company,
        document_code=DocumentType.RAP,
        document_id='2',
        document_number='RAP-2026-0002',
        creator=aditya_user,
        creator_position=it_prog_pos,
        basis=ApprovalBasis.AMOUNT,
        amount=Decimal('25000000'),
        status=ApprovalStatus.PENDING,
        current_step_number=1,
    )
    ApprovalRequestStep.objects.create(
        approval_request=req2, step_number=1, role=ApprovalRole.CHECKED_BY, position=acc_mgr_pos, status=StepStatus.PENDING
    )
    ApprovalRequestStep.objects.create(
        approval_request=req2, step_number=2, role=ApprovalRole.VERIFIED_BY, position=fat_mgr_pos, status=StepStatus.PENDING
    )
    ApprovalRequestStep.objects.create(
        approval_request=req2, step_number=3, role=ApprovalRole.APPROVED_BY, position=dir_pos, status=StepStatus.PENDING
    )

    DocumentSignature.objects.create(
        company=company, document_code=DocumentType.RAP, document_id='2', document_number='RAP-2026-0002',
        step_number=1, role=ApprovalRole.CHECKED_BY, position=acc_mgr_pos, is_signed=False
    )
    DocumentSignature.objects.create(
        company=company, document_code=DocumentType.RAP, document_id='2', document_number='RAP-2026-0002',
        step_number=2, role=ApprovalRole.VERIFIED_BY, position=fat_mgr_pos, is_signed=False
    )
    DocumentSignature.objects.create(
        company=company, document_code=DocumentType.RAP, document_id='2', document_number='RAP-2026-0002',
        step_number=3, role=ApprovalRole.APPROVED_BY, position=dir_pos, is_signed=False
    )

    # Request 3: 2,000,000 RAP (APPROVED, signed by superuser as ACC-MGR, and auto-signed for step 2)
    req3 = ApprovalRequest.objects.create(
        company=company,
        document_code=DocumentType.RAP,
        document_id='3',
        document_number='RAP-2026-0003',
        creator=aditya_user,
        creator_position=it_prog_pos,
        basis=ApprovalBasis.AMOUNT,
        amount=Decimal('2000000'),
        status=ApprovalStatus.APPROVED,
        current_step_number=2,
    )
    
    # Step 1: Checked by ACC-MGR (Approved by superuser)
    ApprovalRequestStep.objects.create(
        approval_request=req3, step_number=1, role=ApprovalRole.CHECKED_BY, position=acc_mgr_pos,
        status=StepStatus.APPROVED, approved_by=superuser, approved_at=timezone.now(), remarks='Cocok, silakan diproses'
    )
    # Step 2: Approved by FAT-MGR (Approved by superuser to simulate completion)
    ApprovalRequestStep.objects.create(
        approval_request=req3, step_number=2, role=ApprovalRole.APPROVED_BY, position=fat_mgr_pos,
        status=StepStatus.APPROVED, approved_by=superuser, approved_at=timezone.now(), remarks='Approved'
    )

    DocumentSignature.objects.create(
        company=company, document_code=DocumentType.RAP, document_id='3', document_number='RAP-2026-0003',
        step_number=1, role=ApprovalRole.CHECKED_BY, position=acc_mgr_pos, is_signed=True,
        user=superuser, signed_at=timezone.now(), signature_draw='MOCK_SIGNATURE_DRAW_DATA_1',
        ip_address='127.0.0.1', user_agent='Mozilla/5.0'
    )
    DocumentSignature.objects.create(
        company=company, document_code=DocumentType.RAP, document_id='3', document_number='RAP-2026-0003',
        step_number=2, role=ApprovalRole.APPROVED_BY, position=fat_mgr_pos, is_signed=True,
        user=superuser, signed_at=timezone.now(), signature_draw='MOCK_SIGNATURE_DRAW_DATA_2',
        ip_address='127.0.0.1', user_agent='Mozilla/5.0'
    )

    print("Mock Approval Requests dan Document Signatures berhasil diseed!")

if __name__ == '__main__':
    seed()
