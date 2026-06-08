from django.core.management.base import BaseCommand
from apps.rbac.models import Module, Function

SALES_FUNCTIONS = [
    {
        'code': 'SALES-CUSTOMER',
        'name': 'Customers',
        'url_path': '/sales/customers',
        'order': 0,
    },
]


class Command(BaseCommand):
    help = 'Seed RBAC untuk modul Sales'

    def handle(self, *args, **options):
        module, created = Module.objects.get_or_create(
            code='sales',
            defaults={'name': 'Sales', 'order': 4, 'is_active': True},
        )
        self.stdout.write(f'  📦 Module Sales {"dibuat" if created else "sudah ada"}')

        for fn_data in SALES_FUNCTIONS:
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
            self.stdout.write(f'  {"✨" if created else "🔄"} [{fn.code}] {fn.name}')

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ {len(SALES_FUNCTIONS)} sales functions seeded'
        ))
