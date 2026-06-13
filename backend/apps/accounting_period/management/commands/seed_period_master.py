"""
BFS ERP — Master Seeder: Financial Open/Close

Usage:
    python manage.py seed_period_master
    python manage.py seed_period_master --years 2024 2025 2026
    python manage.py seed_period_master --years 2026 --company-id 1 --group-name "Finance Admin"
    python manage.py seed_period_master --dry-run

What it does in order:
    1. Validate company & user
    2. Seed AnnualPeriod
    3. Seed QuarterPeriod (Q1–Q4 per year)
    4. Seed MonthlyPeriod (Jan–Dec per year)
    5. Seed AccountingPeriod (with exact start/end dates)
    6. Log each creation to PeriodActivityLog
    7. Seed RBAC Module + Functions
    8. Assign permissions to group (if --group-name provided)
    9. Print full summary report
"""

import calendar
from datetime import date, datetime

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

MONTH_NAMES = [
    '', 'January', 'February', 'March', 'April',
    'May', 'June', 'July', 'August',
    'September', 'October', 'November', 'December',
]

PERIOD_RBAC_FUNCTIONS = [
    {
        'code':        'GL-PERIOD-ANNUAL',
        'name':        'Annual Accounting Period',
        'description': 'Manage annual fiscal year periods — open, close, view history.',
        'order':       10,
    },
    {
        'code':        'GL-PERIOD-QUARTER',
        'name':        'Quarter Accounting Period',
        'description': 'Manage quarterly periods (Q1–Q4) per year.',
        'order':       11,
    },
    {
        'code':        'GL-PERIOD-MONTHLY',
        'name':        'Monthly Accounting Period',
        'description': 'Manage monthly periods (Jan–Dec) per year.',
        'order':       12,
    },
    {
        'code':        'GL-PERIOD-ACCOUNTING',
        'name':        'Accounting Period',
        'description': 'Manage detailed accounting periods with start/end dates.',
        'order':       13,
    },
    {
        'code':        'GL-PERIOD-LOG',
        'name':        'Period Activity Log',
        'description': 'View audit trail of all period open/close actions.',
        'order':       14,
    },
]


class Command(BaseCommand):
    help = 'Master seeder for Financial Open/Close — periods + RBAC in one shot'

    def add_arguments(self, parser):
        now = datetime.now()
        parser.add_argument(
            '--years',
            nargs='+',
            type=int,
            default=list(range(now.year - 3, now.year + 2)),
            help='Years to seed. Default: last 3 years + current + next.',
        )
        parser.add_argument(
            '--company-id',
            type=int,
            default=None,
            help='Company ID. Default: first company.',
        )
        parser.add_argument(
            '--user-id',
            type=int,
            default=None,
            help='User ID for created_by/actioned_by. Default: first superuser.',
        )
        parser.add_argument(
            '--group-name',
            type=str,
            default=None,
            help='AuthGroup name to assign period permissions to.',
        )
        parser.add_argument(
            '--skip-rbac',
            action='store_true',
            default=False,
            help='Skip RBAC seeding — seed period data only.',
        )
        parser.add_argument(
            '--skip-periods',
            action='store_true',
            default=False,
            help='Skip period data — seed RBAC only.',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            default=False,
            help='Show what would be created without actually creating.',
        )

    # ── Main ──────────────────────────────────────────────────────────────────

    def handle(self, *args, **options):
        self._options = options
        self._dry     = options['dry_run']
        self._now     = datetime.now()

        self._print_banner()

        # ── Resolve dependencies ──────────────────────────────────────────────
        company = self._resolve_company(options['company_id'])
        user    = self._resolve_user(options['user_id'])

        self.stdout.write(f'  Company : [{company.id}] {company.name}')
        self.stdout.write(f'  User    : [{user.id}] {user}')
        self.stdout.write(f'  Years   : {sorted(options["years"])}')
        self.stdout.write(f'  Dry Run : {"YES — nothing will be saved" if self._dry else "No"}')
        self.stdout.write('')

        stats = {
            'annual_created':     0,
            'annual_skipped':     0,
            'quarter_created':    0,
            'quarter_skipped':    0,
            'monthly_created':    0,
            'monthly_skipped':    0,
            'accounting_created': 0,
            'accounting_skipped': 0,
            'log_created':        0,
            'rbac_fn_created':    0,
            'rbac_fn_skipped':    0,
            'rbac_perm_created':  0,
        }

        # ── Seed Period Data ──────────────────────────────────────────────────
        if not options['skip_periods']:
            self._seed_periods(company, user, sorted(options['years']), stats)

        # ── Seed RBAC ─────────────────────────────────────────────────────────
        if not options['skip_rbac']:
            self._seed_rbac(options['group_name'], stats)

        # ── Summary Report ────────────────────────────────────────────────────
        self._print_summary(stats)

    # ── Period Seeding ────────────────────────────────────────────────────────

    def _seed_periods(self, company, user, years, stats):
        from apps.accounting.models_period import (
            AnnualPeriod, QuarterPeriod, MonthlyPeriod,
            AccountingPeriod, PeriodActivityLog, PeriodStatus,
        )

        self.stdout.write(self.style.HTTP_INFO('━━━ PERIOD DATA SEEDING ━━━'))

        current_year  = self._now.year
        current_month = self._now.month

        for year in years:
            self.stdout.write(f'\n  📅 {year}')

            # Determine statuses
            if year < current_year:
                year_status = PeriodStatus.CLOSE
            else:
                year_status = PeriodStatus.OPEN

            if self._dry:
                self.stdout.write(f'      [DRY] Would create AnnualPeriod {year} [{year_status}]')
                self.stdout.write(f'      [DRY] Would create 4 QuarterPeriods')
                self.stdout.write(f'      [DRY] Would create 12 MonthlyPeriods')
                self.stdout.write(f'      [DRY] Would create 12 AccountingPeriods')
                continue

            with transaction.atomic():
                # Annual
                annual, a_created = AnnualPeriod.objects.get_or_create(
                    company=company,
                    year=year,
                    defaults={'status': year_status, 'created_by': user},
                )
                if a_created:
                    stats['annual_created'] += 1
                    self._write_log(
                        company, 'ANNUAL', annual, year_status,
                        f'[SEEDER] Annual period {year} created.',
                        str(year), user,
                    )
                    stats['log_created'] += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'      ✓ AnnualPeriod {year} [{year_status}]')
                    )
                else:
                    stats['annual_skipped'] += 1
                    self.stdout.write(f'      · AnnualPeriod {year} — already exists [{annual.status}]')

                # Quarters
                quarters = {}
                for q in range(1, 5):
                    if year < current_year:
                        q_status = PeriodStatus.CLOSE
                    elif year == current_year:
                        cur_q    = (current_month - 1) // 3 + 1
                        q_status = PeriodStatus.OPEN if q >= cur_q else PeriodStatus.CLOSE
                    else:
                        q_status = PeriodStatus.OPEN

                    qp, q_created = QuarterPeriod.objects.get_or_create(
                        company=company, year=year, quarter=q,
                        defaults={
                            'annual_period': annual,
                            'status': q_status,
                            'created_by': user,
                        },
                    )
                    quarters[q] = qp
                    if q_created:
                        stats['quarter_created'] += 1
                        self._write_log(
                            company, 'QUARTER', qp, q_status,
                            f'[SEEDER] Q{q} {year} created.',
                            f'{year} Q{q}', user,
                        )
                        stats['log_created'] += 1
                    else:
                        stats['quarter_skipped'] += 1

                q_c = stats['quarter_created']
                q_s = stats['quarter_skipped']
                self.stdout.write(f'      ✓ QuarterPeriods: {q_c} created, {q_s} skipped')

                # Monthly + Accounting
                m_created_count = 0
                a_created_count = 0

                for m in range(1, 13):
                    q_num   = (m - 1) // 3 + 1
                    _, last = calendar.monthrange(year, m)
                    start   = date(year, m, 1)
                    end     = date(year, m, last)

                    if year < current_year:
                        m_status = PeriodStatus.CLOSE
                    elif year == current_year:
                        m_status = PeriodStatus.OPEN if m >= current_month else PeriodStatus.CLOSE
                    else:
                        m_status = PeriodStatus.OPEN

                    mp, mp_created = MonthlyPeriod.objects.get_or_create(
                        company=company, year=year, month=m,
                        defaults={
                            'annual_period':  annual,
                            'quarter_period': quarters[q_num],
                            'status':         m_status,
                            'created_by':     user,
                        },
                    )
                    if mp_created:
                        stats['monthly_created'] += 1
                        m_created_count += 1
                        self._write_log(
                            company, 'MONTHLY', mp, m_status,
                            f'[SEEDER] {MONTH_NAMES[m]} {year} created.',
                            f'{MONTH_NAMES[m]} {year}', user,
                        )
                        stats['log_created'] += 1
                    else:
                        stats['monthly_skipped'] += 1

                    ap, ap_created = AccountingPeriod.objects.get_or_create(
                        company=company, year=year, month=m,
                        defaults={
                            'monthly_period': mp,
                            'start_date':     start,
                            'end_date':       end,
                            'status':         m_status,
                            'created_by':     user,
                        },
                    )
                    if ap_created:
                        stats['accounting_created'] += 1
                        a_created_count += 1
                        self._write_log(
                            company, 'ACCOUNTING', ap, m_status,
                            f'[SEEDER] Accounting {MONTH_NAMES[m]} {year} created.',
                            f'{MONTH_NAMES[m]} {year}', user,
                        )
                        stats['log_created'] += 1
                    else:
                        stats['accounting_skipped'] += 1

                self.stdout.write(
                    f'      ✓ MonthlyPeriods:     {m_created_count} created'
                )
                self.stdout.write(
                    f'      ✓ AccountingPeriods:  {a_created_count} created'
                )

    def _write_log(self, company, period_type, obj, action, reason, label, user):
        from apps.accounting.models_period import PeriodActivityLog

        kwargs = dict(
            company=company,
            period_type=period_type,
            action=action,
            reason=reason,
            period_label=label,
            period_status_after=action,
            actioned_by=user,
        )
        if period_type == 'ANNUAL':
            kwargs['annual_period'] = obj
        elif period_type == 'QUARTER':
            kwargs['quarter_period'] = obj
        elif period_type == 'MONTHLY':
            kwargs['monthly_period'] = obj
        elif period_type == 'ACCOUNTING':
            kwargs['accounting_period'] = obj

        PeriodActivityLog.objects.create(**kwargs)

    # ── RBAC Seeding ──────────────────────────────────────────────────────────

    def _seed_rbac(self, group_name, stats):
        self.stdout.write('')
        self.stdout.write(self.style.HTTP_INFO('━━━ RBAC SEEDING ━━━'))

        try:
            from apps.rbac.models import Module, Function, AuthGroup, GroupFunction
        except ImportError:
            self.stdout.write(
                self.style.WARNING('  ⚠ RBAC models not found — skipping RBAC seeding.')
            )
            return

        if self._dry:
            self.stdout.write('  [DRY] Would seed Module: GL — General Ledger')
            for fn in PERIOD_RBAC_FUNCTIONS:
                self.stdout.write(f'  [DRY] Would seed Function: {fn["code"]} — {fn["name"]}')
            return

        with transaction.atomic():
            # Module
            module, mod_created = Module.objects.get_or_create(
                code='GL',
                defaults={
                    'name':        'General Ledger',
                    'description': 'General Ledger — COA, Journal, Period Management',
                    'icon':        'fas fa-book',
                    'order':       1,
                    'is_active':   True,
                },
            )
            status_str = '✓ Created' if mod_created else '· Exists'
            self.stdout.write(f'  {status_str}: Module [{module.code}] {module.name}')

            # Functions
            self.stdout.write('')
            seeded_functions = []
            for fn_data in PERIOD_RBAC_FUNCTIONS:
                fn_defaults = {
                    'name':        fn_data['name'],
                    'description': fn_data['description'],
                    'order':       fn_data['order'],
                    'is_active':   True,
                }
                # Try with module FK first
                try:
                    fn, fn_created = Function.objects.get_or_create(
                        code=fn_data['code'],
                        defaults={**fn_defaults, 'module': module},
                    )
                except Exception:
                    fn, fn_created = Function.objects.get_or_create(
                        code=fn_data['code'],
                        defaults=fn_defaults,
                    )

                seeded_functions.append(fn)
                if fn_created:
                    stats['rbac_fn_created'] += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✓ Created Function: [{fn.code}] {fn.name}')
                    )
                else:
                    stats['rbac_fn_skipped'] += 1
                    self.stdout.write(f'  · Exists  Function: [{fn.code}] {fn.name}')

            # Assign to group
            if group_name:
                self.stdout.write('')
                self.stdout.write(f'  Assigning to group: "{group_name}"')
                try:
                    group = AuthGroup.objects.get(name=group_name)
                except AuthGroup.DoesNotExist:
                    available = list(AuthGroup.objects.values_list('name', flat=True))
                    self.stdout.write(
                        self.style.ERROR(
                            f'  ✗ AuthGroup "{group_name}" not found.\n'
                            f'    Available: {available}'
                        )
                    )
                    return

                for fn in seeded_functions:
                    try:
                        gf, gf_created = GroupFunction.objects.get_or_create(
                            group=group,
                            function=fn,
                        )
                        if gf_created:
                            stats['rbac_perm_created'] += 1
                            self.stdout.write(
                                self.style.SUCCESS(f'    ✓ Assigned: {group.name} → {fn.code}')
                            )
                        else:
                            self.stdout.write(f'    · Already:  {group.name} → {fn.code}')
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f'    ⚠ Could not assign {fn.code}: {e}')
                        )

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _resolve_company(self, company_id):
        from apps.organization.models import Company
        if company_id:
            try:
                return Company.objects.get(pk=company_id)
            except Company.DoesNotExist:
                raise CommandError(f'Company with ID {company_id} not found.')
        company = Company.objects.first()
        if not company:
            raise CommandError('No company found. Create a company first.')
        return company

    def _resolve_user(self, user_id):
        if user_id:
            try:
                return User.objects.get(pk=user_id)
            except User.DoesNotExist:
                raise CommandError(f'User with ID {user_id} not found.')
        user = User.objects.filter(is_superuser=True).first() or User.objects.first()
        if not user:
            raise CommandError('No user found. Create a user first.')
        return user

    def _print_banner(self):
        self.stdout.write('')
        self.stdout.write(self.style.HTTP_INFO('╔══════════════════════════════════════════╗'))
        self.stdout.write(self.style.HTTP_INFO('║  BFS ERP — Financial Period Master Seed  ║'))
        self.stdout.write(self.style.HTTP_INFO('╚══════════════════════════════════════════╝'))
        self.stdout.write('')

    def _print_summary(self, stats):
        self.stdout.write('')
        self.stdout.write(self.style.HTTP_INFO('━━━ SUMMARY ━━━'))
        self.stdout.write('')

        rows = [
            ('Annual Periods',      stats['annual_created'],     stats['annual_skipped']),
            ('Quarter Periods',     stats['quarter_created'],    stats['quarter_skipped']),
            ('Monthly Periods',     stats['monthly_created'],    stats['monthly_skipped']),
            ('Accounting Periods',  stats['accounting_created'], stats['accounting_skipped']),
            ('Activity Logs',       stats['log_created'],        0),
            ('RBAC Functions',      stats['rbac_fn_created'],    stats['rbac_fn_skipped']),
            ('RBAC Assignments',    stats['rbac_perm_created'],  0),
        ]

        total_created = sum(r[1] for r in rows)
        total_skipped = sum(r[2] for r in rows)

        self.stdout.write(f'  {"Type":<25} {"Created":>8} {"Skipped":>8}')
        self.stdout.write(f'  {"─"*25} {"─"*8} {"─"*8}')
        for label, created, skipped in rows:
            c_str = self.style.SUCCESS(str(created)) if created else str(created)
            self.stdout.write(f'  {label:<25} {c_str:>8} {skipped:>8}')
        self.stdout.write(f'  {"─"*25} {"─"*8} {"─"*8}')
        self.stdout.write(
            f'  {"TOTAL":<25} '
            + self.style.SUCCESS(f'{total_created:>8}')
            + f' {total_skipped:>8}'
        )

        self.stdout.write('')
        if self._dry:
            self.stdout.write(self.style.WARNING('  ⚠ DRY RUN — no data was saved.'))
        else:
            self.stdout.write(self.style.SUCCESS('  ✅ Seeding completed successfully!'))
        self.stdout.write('')
        self.stdout.write('  Next steps:')
        self.stdout.write('    python manage.py migrate  (if not done yet)')
        self.stdout.write('    python manage.py seed_period_master --group-name "Finance Admin"')
        self.stdout.write('')