# apps/accounting/management/commands/seed_accounting_rbac.py
"""
Seed RBAC entries untuk modul Accounting.

Jalankan:
    python manage.py seed_accounting_rbac

Idempotent — aman dijalanin berkali-kali, pakai update_or_create.
"""
from django.core.management.base import BaseCommand
from apps.rbac.models import Module, Function


# Function code yang dipakai di views.py (rbac_function_code)
ACCOUNTING_FUNCTIONS = [
    {
        'code':     'GL-CHART-OF-ACCOUNTS',
        'name':     'Chart of Accounts',
        'url_path': '/gl/chart-of-accounts',
        'order':    0,
    },
    {
        'code':     'GL-ACCOUNT-GROUP',
        'name':     'Account Group',
        'url_path': '',   # dikelola dari halaman COA, bukan halaman sendiri
        'order':    1,
    },
]


class Command(BaseCommand):
    help = 'Seed RBAC Module & Functions untuk modul Accounting (GL)'

    def handle(self, *args, **options):
        # Pastikan module GL sudah ada (dibuat oleh seed_rbac)
        module, created = Module.objects.get_or_create(
            code='gl',
            defaults={
                'name':      'General Ledger',
                'order':     2,
                'is_active': True,
            },
        )

        if created:
            self.stdout.write('  📦 Module GL dibuat baru')
        else:
            self.stdout.write('  📦 Module GL sudah ada, skip')

        # Seed functions
        for fn_data in ACCOUNTING_FUNCTIONS:
            fn, created = Function.objects.update_or_create(
                code=fn_data['code'],
                defaults={
                    'module':    module,
                    'parent':    None,
                    'name':      fn_data['name'],
                    'url_path':  fn_data['url_path'],
                    'order':     fn_data['order'],
                    'is_active': True,
                },
            )
            status = '✨ Dibuat' if created else '🔄 Updated'
            self.stdout.write(f'  {status}: [{fn.code}] {fn.name}')

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ {len(ACCOUNTING_FUNCTIONS)} accounting functions seeded ke module GL'
        ))