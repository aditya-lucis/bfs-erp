from django.core.management.base import BaseCommand
from apps.master_type.models import MasterBank
from apps.organization.models import Company
from django.db import transaction

class Command(BaseCommand):
    help = 'Seeds initial Master Bank data for Indonesian Banks'

    def handle(self, *args, **options):
        # Ambil Company (Default company, assuming first active)
        company = Company.objects.filter(is_active=True).first()
        if not company:
            self.stdout.write(self.style.ERROR('No active Company found. Please seed organization first.'))
            return
            
        # Data Bank di Indonesia
        banks_data = [
            {'name_id': 'Bank Mandiri', 'name_en': 'Bank Mandiri'},
            {'name_id': 'Bank Rakyat Indonesia (BRI)', 'name_en': 'Bank Rakyat Indonesia (BRI)'},
            {'name_id': 'Bank Central Asia (BCA)', 'name_en': 'Bank Central Asia (BCA)'},
            {'name_id': 'Bank Negara Indonesia (BNI)', 'name_en': 'Bank Negara Indonesia (BNI)'},
            {'name_id': 'Bank Tabungan Negara (BTN)', 'name_en': 'Bank Tabungan Negara (BTN)'},
            {'name_id': 'Bank Syariah Indonesia (BSI)', 'name_en': 'Bank Syariah Indonesia (BSI)'},
            {'name_id': 'Bank CIMB Niaga', 'name_en': 'Bank CIMB Niaga'},
            {'name_id': 'Bank Danamon', 'name_en': 'Bank Danamon'},
            {'name_id': 'Bank Permata', 'name_en': 'Bank Permata'},
            {'name_id': 'Bank Panin', 'name_en': 'Bank Panin'},
            {'name_id': 'Bank Mega', 'name_en': 'Bank Mega'},
            {'name_id': 'Bank Jabar Banten (BJB)', 'name_en': 'Bank Jabar Banten (BJB)'},
            {'name_id': 'Bank OCBC NISP', 'name_en': 'Bank OCBC NISP'},
            {'name_id': 'Bank Maybank Indonesia', 'name_en': 'Bank Maybank Indonesia'},
            {'name_id': 'Bank Muamalat', 'name_en': 'Bank Muamalat'},
            {'name_id': 'Bank DKI', 'name_en': 'Bank DKI'},
            {'name_id': 'Bank UOB Indonesia', 'name_en': 'Bank UOB Indonesia'},
            {'name_id': 'Bank Bukopin', 'name_en': 'Bank Bukopin'},
            {'name_id': 'Bank Sinarmas', 'name_en': 'Bank Sinarmas'},
            {'name_id': 'Bank INA Perdana', 'name_en': 'Bank INA Perdana'}
        ]
        
        count = 0
        with transaction.atomic():
            for i, item in enumerate(banks_data, start=1):
                # The auto-increment is handled by the model's save method.
                # Since the prompt said to use TAccBank_0 (auto increment), the model handles TAccBank_1, etc.
                # But to avoid re-seeding if we run multiple times, we should check by name.
                obj, created = MasterBank.objects.get_or_create(
                    bank_name_id=item['name_id'],
                    defaults={
                        'bank_name': item['name_en'],
                        'order_no': i,
                        'company': company,
                        'is_not_active': False
                    }
                )
                if created:
                    count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {count} Master Banks.'))
