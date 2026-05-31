"""
python manage.py seed_organization

Seed:
1. Company  → PT. HashMicro (single-tenant)
2. Department tree → dari screenshot (skip yang berbau medis)
3. Position per department
4. 3 sample employees (Aditya, Suyono, Ikbal) sebagai Programmer
"""
from datetime import date
from django.core.management.base import BaseCommand
from apps.organization.models import Company, Department, Position, Employee


# ─── Company Data ─────────────────────────────────────────────────────────────

COMPANY = {
    'company_code':         'BFS',
    'company_type':         'Software House',
    'company_name':         'PT. HashMicro',
    'company_tax_number':   '',
    'company_tax_date':     date(1997, 6, 7),
    'opening_balance_date': date(2008, 12, 1),
    'tax_serial_number':    '',
    'company_address':      (
        'Jl. Raya Hankam No. 17 RT. 003 RW. 008 '
        'Kel. Jatirahayu Kec. Pondok Melati Kab. Bekasi Jawa Barat.'
    ),
    'country':              'Indonesia',
    'business_template':    'trading',
    'is_holding':           False,
    'rap_tolerance':        100,
    'period_frequency':     12,
    'currency_id':          'IDR',
}


# ─── Department Tree ──────────────────────────────────────────────────────────
# Format: (code, name, parent_code atau None, order)
# Kita skip semua yang berbau medis (yanmed, igada, iokvk, irajal, iranap, medis)

DEPARTMENTS = [
    # Level 0 — root
    ('bod',             'Board Of Director',            None,           0),

    # Level 1 — direct under BOD
    ('dir',             'Direktur',                     'bod',          0),
    ('marketing.utama', 'Marketing Utama',              'bod',          1),
    ('non_medis',       'Non-Medis',                    'bod',          2),
    ('it',              'IT',                           'bod',          3),

    # Level 2 — under Marketing Utama
    ('kepala.marketing','Kepala Marketing',             'marketing.utama', 0),
    ('marketing',       'Marketing',                    'marketing.utama', 1),
    ('regist.custcare', 'Pendaftaraan & Customer Care', 'marketing.utama', 2),

    # Level 2 — under Non-Medis
    ('cost.control',    'Cost Control',                 'non_medis',    0),
    ('hr.umum',         'HR & Umum',                    'non_medis',    1),
    ('purchasing',      'Purchasing',                   'non_medis',    2),
    ('fat',             'Finance, Akutansi & Tax',      'non_medis',    3),

    # Level 3 — under HR & Umum
    ('hr',              'Kepegawaian',                  'hr.umum',      0),
    ('umum',            'Umum',                         'hr.umum',      1),

    # Level 3 — under FAT
    ('akutansi',        'Akuntansi',                    'fat',          0),
    ('kepala.fat',      'Kepala FAT',                   'fat',          1),
    ('keuangan',        'Keuangan',                     'fat',          2),
    ('pajak',           'Pajak',                        'fat',          3),

    # Level 2 — under IT
    ('it.supp',         'IT Support',                   'it',           0),
]


# ─── Positions per Department ─────────────────────────────────────────────────
# Format: (dept_code, position_code, position_name)

POSITIONS = [
    # BOD / Direktur
    ('bod',             'BOD',          'Board of Director'),
    ('dir',             'DIR',          'Direktur'),

    # Marketing
    ('marketing.utama', 'MKT-MGR',      'Marketing Manager'),
    ('kepala.marketing','MKT-HEAD',     'Kepala Marketing'),
    ('marketing',       'MKT-STAFF',    'Marketing Staff'),
    ('regist.custcare', 'CC-STAFF',     'Customer Care Staff'),

    # Cost Control
    ('cost.control',    'CC-MGR',       'Cost Control Manager'),
    ('cost.control',    'CC-STAFF',     'Cost Control Staff'),

    # HR & Umum
    ('hr.umum',         'HRUM-MGR',     'HR & Umum Manager'),
    ('hr',              'HR-STAFF',     'HR Staff'),
    ('umum',            'UMUM-STAFF',   'Staff Umum'),

    # Purchasing
    ('purchasing',      'PUR-MGR',      'Purchasing Manager'),
    ('purchasing',      'PUR-STAFF',    'Purchasing Staff'),

    # FAT
    ('fat',             'FAT-MGR',      'FAT Manager'),
    ('kepala.fat',      'FAT-HEAD',     'Kepala FAT'),
    ('akutansi',        'ACC-MGR',      'Accounting Manager'),   # ← superuser akan ditempatkan di sini
    ('akutansi',        'ACC-STAFF',    'Accounting Staff'),
    ('keuangan',        'FIN-STAFF',    'Finance Staff'),
    ('pajak',           'TAX-STAFF',    'Tax Staff'),

    # IT
    ('it',              'IT-MGR',       'IT Manager'),
    ('it.supp',         'IT-PROG',      'Programmer'),           # ← Aditya, Suyono, Ikbal
    ('it.supp',         'IT-SUPP',      'IT Support Staff'),
]


# ─── Sample Employees ─────────────────────────────────────────────────────────
# Format: (employee_id, full_name, email, position_code, dept_code)

SAMPLE_EMPLOYEES = [
    ('BFS001', 'Aditya Lucis Caelum',   'aditya@bfserp.com',   'IT-PROG',   'it.supp'),
    ('BFS002', 'Suyono',    'suyono@bfserp.com',   'IT-PROG',   'it.supp'),
    ('BFS003', 'Ikbal Yulianto',    'ikbal@bfserp.com',    'IT-PROG',   'it.supp'),
    ('BFS004', 'Muhammad Sutriadi',     'budi@bfserp.com',     'ACC-STAFF', 'akutansi'),
    ('BFS005', 'Bayinatul Rahmatullah',        'sari@bfserp.com',     'FIN-STAFF', 'keuangan'),
    ('BFS006', 'Valiani',   'valiani@bfserp.com',   'HR-STAFF',  'hr'),
]


class Command(BaseCommand):
    help = 'Seed Company, Department tree, Positions, and Sample Employees'

    def handle(self, *args, **options):
        company  = self._seed_company()
        dept_map = self._seed_departments(company)
        pos_map  = self._seed_positions(dept_map)
        self._seed_employees(pos_map)
        self._patch_existing_superusers(pos_map)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _seed_company(self):
        company, created = Company.objects.update_or_create(
            company_code=COMPANY['company_code'],
            defaults=COMPANY,
        )
        status = '🆕 Created' if created else '✅ Updated'
        self.stdout.write(f'{status} company: {company}')
        return company

    def _seed_departments(self, company):
        dept_map = {}   # code → Department instance

        for code, name, parent_code, order in DEPARTMENTS:
            parent = dept_map.get(parent_code) if parent_code else None
            dept, created = Department.objects.update_or_create(
                company=company,
                code=code,
                defaults={
                    'name':      name,
                    'parent':    parent,
                    'order':     order,
                    'is_active': True,
                },
            )
            dept_map[code] = dept
            marker = '🆕' if created else '  '
            indent = '  ' * (dept.level + 1)
            self.stdout.write(f'{marker}{indent}{dept}')

        self.stdout.write(self.style.SUCCESS(
            f'✅ {len(dept_map)} departments seeded'
        ))
        return dept_map

    def _seed_positions(self, dept_map):
        pos_map = {}   # (dept_code, pos_code) → Position instance

        for dept_code, pos_code, pos_name in POSITIONS:
            dept = dept_map.get(dept_code)
            if not dept:
                self.stdout.write(
                    self.style.WARNING(f'  ⚠️  Department {dept_code} not found, skipping {pos_name}')
                )
                continue

            pos, created = Position.objects.update_or_create(
                department=dept,
                code=pos_code,
                defaults={'name': pos_name, 'is_active': True},
            )
            pos_map[(dept_code, pos_code)] = pos

        self.stdout.write(self.style.SUCCESS(
            f'✅ {len(pos_map)} positions seeded'
        ))
        return pos_map

    def _seed_employees(self, pos_map):
        count = 0
        for emp_id, full_name, email, pos_code, dept_code in SAMPLE_EMPLOYEES:
            position = pos_map.get((dept_code, pos_code))
            if not position:
                self.stdout.write(
                    self.style.WARNING(f'  ⚠️  Position ({dept_code}, {pos_code}) not found, skip {full_name}')
                )
                continue

            emp, created = Employee.objects.update_or_create(
                employee_id=emp_id,
                defaults={
                    'position':  position,
                    'full_name': full_name,
                    'email':     email,
                    'status':    'active',
                },
            )
            marker = '🆕' if created else '  '
            self.stdout.write(f'{marker} Employee: {emp}')
            count += 1

        self.stdout.write(self.style.SUCCESS(f'✅ {count} sample employees seeded'))

    def _patch_existing_superusers(self, pos_map):
        """
        Kalau superuser sudah ada tapi belum punya Employee record
        (misalnya dibuat sebelum seed), buatkan sekarang.
        """
        from apps.authentication.models import User

        acc_mgr_pos = pos_map.get(('akutansi', 'ACC-MGR'))
        if not acc_mgr_pos:
            return

        superusers = User.objects.filter(is_superuser=True)
        patched = 0
        for user in superusers:
            if hasattr(user, 'employee_profile'):
                continue  # sudah punya

            employee_id = f"ADM{user.pk:04d}"
            Employee.objects.get_or_create(
                user=user,
                defaults={
                    'position':    acc_mgr_pos,
                    'employee_id': employee_id,
                    'full_name':   user.full_name or user.username,
                    'email':       user.email,
                    'status':      'active',
                },
            )
            self.stdout.write(f'  🔧 Patched superuser → employee: {user.username}')
            patched += 1

        if patched:
            self.stdout.write(self.style.SUCCESS(f'✅ {patched} superuser(s) patched'))