from django.core.management.base import BaseCommand
from apps.master_type.models import TransactionType
from apps.organization.models import Company
from apps.rbac.models import Module, Function

class Command(BaseCommand):
    help = 'Seeds initial Transaction Type data'

    def handle(self, *args, **options):
        # 1. Pastikan RBAC Function untuk SETTINGS-MASTER-TYPE ada
        settings_module, _ = Module.objects.get_or_create(
            name='Settings',
            defaults={
                'is_active': True,
                'description': 'System Settings'
            }
        )
        
        func, created = Function.objects.get_or_create(
            code='SETTINGS-MASTER-TYPE',
            defaults={
                'module': settings_module,
                'name': 'Master Type Management',
                'description': 'Manage Master Types like Transaction Types',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Created RBAC Function SETTINGS-MASTER-TYPE'))

        # 2. Ambil Company (Default company, assuming ID=51 from screenshot or just first active)
        company = Company.objects.filter(is_active=True).first()
        if not company:
            self.stdout.write(self.style.ERROR('No active Company found. Please seed organization first.'))
            return
            
        # 3. Data Transaction Type sesuai screenshot
        data = [
            {'name_id': 'HPP Farmasi', 'name_en': 'HPP Farmasi'},
            {'name_id': 'HPP Penunjang', 'name_en': 'HPP Penunjang'},
            {'name_id': 'HPP Lab & Radiologi', 'name_en': 'HPP Lab & Radiologi'},
            {'name_id': 'HPP - Gizi', 'name_en': 'HPP - Gizi'},
            {'name_id': 'HPP - Jasa Medis', 'name_en': 'HPP - Jasa Medis'},
            {'name_id': 'OPEX - Kepegawaian', 'name_en': 'OPEX - Kepegawaian'},
            {'name_id': 'Opex - Umum', 'name_en': 'Opex - Umum'},
            {'name_id': 'Opex - Marketing', 'name_en': 'Opex - Marketing'},
            {'name_id': 'BANK LOAN - Pokok', 'name_en': 'BANK LOAN - Pokok'},
            {'name_id': 'BANK LOAN - Bunga', 'name_en': 'BANK LOAN - Bunga'},
            {'name_id': 'CAPEX - Bangunan', 'name_en': 'CAPEX - Bangunan'},
            {'name_id': 'CAPEX - Kendaraan', 'name_en': 'CAPEX - Kendaraan'},
            {'name_id': 'CAPEX - Peralatan Medis', 'name_en': 'CAPEX - Peralatan Medis'},
            {'name_id': 'CAPEX - Peralatan Non Medis', 'name_en': 'CAPEX - Peralatan Non Medis'},
        ]
        
        count = 0
        for i, item in enumerate(data, start=1):
            type_code = f'TrsType_{i}'
            obj, created = TransactionType.objects.get_or_create(
                type_code=type_code,
                defaults={
                    'type_name_id': item['name_id'],
                    'type_name_en': item['name_en'],
                    'table_name': 'TrsType',
                    'order_no': i,
                    'company': company,
                    'is_not_active': False
                }
            )
            if created:
                count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {count} Transaction Types.'))
