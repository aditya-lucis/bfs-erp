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
    {
        'code':     'FINANCE-PAYMENT-REQUEST-2',
        'name':     'Payment Request',
        'url_path': '/finance/payment-request',
        'order':    2,
        'module_code': 'finance',
    },
]


class Command(BaseCommand):
    help = 'Seed RBAC Module & Functions untuk modul Accounting (GL)'

    def handle(self, *args, **options):
        # Pastikan module GL sudah ada (dibuat oleh seed_rbac)
        module_gl, _ = Module.objects.get_or_create(
            code='gl',
            defaults={
                'name':      'General Ledger',
                'order':     2,
                'is_active': True,
            },
        )
        
        module_finance, _ = Module.objects.get_or_create(
            code='finance',
            defaults={
                'name':      'Finance',
                'order':     3,
                'is_active': True,
            },
        )

        # Seed functions
        for fn_data in ACCOUNTING_FUNCTIONS:
            target_module = module_finance if fn_data.get('module_code') == 'finance' else module_gl
            
            # Use update to only update url_path instead of update_or_create
            # so we don't accidentally overwrite parent relations set by seed_rbac
            Function.objects.filter(code=fn_data['code']).update(
                url_path=fn_data['url_path'],
                module=target_module
            )
            self.stdout.write(f"  🔄 Updated URL for: [{fn_data['code']}] {fn_data['name']}")

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ {len(ACCOUNTING_FUNCTIONS)} accounting functions seeded ke module GL'
        ))