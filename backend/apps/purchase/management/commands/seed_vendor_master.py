from django.core.management.base import BaseCommand
from apps.purchase.models import VendorCategory

DEFAULT_CATEGORIES = [
    ('EXP', 'EXP'),
    ('LS',  'LS'),
    ('SB',  'SB'),
    ('SP',  'SP'),
]


class Command(BaseCommand):
    help = 'Seed vendor categories default (EXP, LS, SB, SP)'

    def handle(self, *args, **options):
        for code, name in DEFAULT_CATEGORIES:
            obj, created = VendorCategory.objects.get_or_create(
                code=code,
                defaults={'name': name},
            )
            self.stdout.write(f'  {"✨" if created else "🔄"} {obj.code} - {obj.name}')
        self.stdout.write(self.style.SUCCESS(f'\n✅ {len(DEFAULT_CATEGORIES)} vendor categories ready'))
