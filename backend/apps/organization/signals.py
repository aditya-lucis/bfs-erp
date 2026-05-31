"""
Signal: setiap kali User baru dibuat dengan is_superuser=True,
otomatis buatkan Employee record dengan posisi Accounting Manager.
"""
from django.conf import settings
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_employee_for_superuser(sender, instance, created, **kwargs):
    """
    Kalau user baru AND superuser → auto-create Employee
    sebagai Accounting Manager di perusahaan ini.
    """
    if not created or not instance.is_superuser:
        return

    # Import di dalam fungsi supaya hindari circular import
    from apps.organization.models import Company, Department, Position, Employee

    def _setup():
        company = Company.get_default()
        if not company:
            return  # Company belum di-seed, skip

        # Cari posisi Accounting Manager
        position = Position.objects.filter(
            code='ACC-MGR',
            department__company=company,
        ).first()
        if not position:
            return  # Posisi belum di-seed, skip

        # Jangan duplikat kalau sudah ada
        if Employee.objects.filter(user=instance).exists():
            return

        employee_id = f"ADM{instance.pk:04d}"
        Employee.objects.create(
            user=instance,
            position=position,
            employee_id=employee_id,
            full_name=instance.full_name or instance.username,
            email=instance.email,
            status='active',
        )

    # Jalankan setelah transaction commit supaya pk sudah tersedia
    transaction.on_commit(_setup)