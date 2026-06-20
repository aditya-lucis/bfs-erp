from django.core.management.base import BaseCommand
from apps.rbac.models import Module, Function

PURCHASE_FUNCTIONS = [
    {'code': 'PURCHASES-VENDOR-CATEGORY', 'name': 'Vendor Category', 'url_path': '/purchases/vendor-category', 'order': 0},
    {'code': 'PURCHASES-VENDOR-GROUP',    'name': 'Vendor Group',    'url_path': '/purchases/vendor-group',    'order': 1},
    {'code': 'PURCHASES-VENDOR',          'name': 'Vendor',          'url_path': '/purchases/vendor',          'order': 2},
    {'code': 'PURCHASES-PR',              'name': 'Purchase Requisition', 'url_path': '/purchases/pr',         'order': 3},
]


class Command(BaseCommand):
    help = 'Seed RBAC untuk modul Purchases (Vendor)'

    def handle(self, *args, **options):
        module, created = Module.objects.get_or_create(
            code='purchases',
            defaults={'name': 'Purchases', 'order': 6, 'is_active': True},
        )
        self.stdout.write(f'  📦 Module Purchases {"dibuat" if created else "sudah ada"}')

        for fn_data in PURCHASE_FUNCTIONS:
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
            f'\n✅ {len(PURCHASE_FUNCTIONS)} purchase functions seeded'
        ))
