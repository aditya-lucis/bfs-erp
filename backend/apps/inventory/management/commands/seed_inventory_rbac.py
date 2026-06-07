# apps/inventory/management/commands/seed_inventory_rbac.py
from django.core.management.base import BaseCommand
from apps.rbac.models import Module, Function

INVENTORY_FUNCTIONS = [
    {'code': 'INV-UNIT-MEASUREMENT', 'name': 'Unit Measurement', 'url_path': '/inventory/unit-measurement', 'order': 0},
    {'code': 'INV-ITEM-CATEGORY',    'name': 'Item Category',    'url_path': '/inventory/item-category',    'order': 1},
    {'code': 'INV-ITEM',             'name': 'List of Items',    'url_path': '/inventory/items',            'order': 2},
]

class Command(BaseCommand):
    help = 'Seed RBAC untuk modul Inventory'

    def handle(self, *args, **options):
        module, created = Module.objects.get_or_create(
            code='inventory',
            defaults={'name': 'Inventory', 'order': 3, 'is_active': True},
        )
        self.stdout.write(f'  📦 Module Inventory {"dibuat" if created else "sudah ada"}')

        for fn_data in INVENTORY_FUNCTIONS:
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
            f'\n✅ {len(INVENTORY_FUNCTIONS)} inventory functions seeded'
        ))