"""
BFS ERP — Accounting: Financial Period Data Seeder

Usage:
    python manage.py seed_financial_periods
    python manage.py seed_financial_periods --years 2023 2024 2025 2026
    python manage.py seed_financial_periods --years 2026 --company-id 1

What it does:
    For each requested year:
      1. Creates AnnualPeriod (OPEN for current/future, CLOSE for past)
      2. Creates 4 QuarterPeriods (Q1–Q4)
      3. Creates 12 MonthlyPeriods (Jan–Dec)
      4. Creates 12 AccountingPeriods with exact start_date / end_date
      5. Logs a creation entry in PeriodActivityLog

    Safe to run multiple times — skips existing records.
"""

import calendar
from datetime import date, datetime

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed Financial Period data (Annual → Quarter → Monthly → Accounting Period)'

    def add_arguments(self, parser):
        current_year = datetime.now().year
        parser.add_argument(
            '--years',
            nargs='+',
            type=int,
            default=list(range(current_year - 3, current_year + 2)),
            help='List of years to seed. Default: last 3 years + current + next year.',
        )
        parser.add_argument(
            '--company-id',
            type=int,
            default=None,
            help='Company ID to seed for. Default: first company found.',
        )
        parser.add_argument(
            '--user-id',
            type=int,
            default=None,
            help='User ID for created_by. Default: first superuser found.',
        )

    def handle(self, *args, **options):
        from apps.organization.models import Company
        from apps.accounting.models_period import (
            AnnualPeriod, QuarterPeriod, MonthlyPeriod,
            AccountingPeriod, PeriodActivityLog, PeriodStatus,
        )

        years      = sorted(options['years'])
        company_id = options['company_id']
        user_id    = options['user_id']

        # ── Resolve company ───────────────────────────────────────────────────
        if company_id:
            try:
                company = Company.objects.get(pk=company_id)
            except Company.DoesNotExist:
                raise CommandError(f'Company with ID {company_id} not found.')
        else:
            company = Company.objects.first()
            if not company:
                raise CommandError('No company found. Please create a company first.')

        # ── Resolve user ──────────────────────────────────────────────────────
        if user_id:
            try:
                user = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                raise CommandError(f'User with ID {user_id} not found.')
        else:
            user = User.objects.filter(is_superuser=True).first()
            if not user:
                user = User.objects.first()

        current_year = datetime.now().year
        current_month = datetime.now().month

        self.stdout.write(self.style.NOTICE(
            f'\n🚀 Seeding Financial Periods for company: [{company.id}] {company.name}'
        ))
        self.stdout.write(self.style.NOTICE(f'   Years: {years}'))
        self.stdout.write(self.style.NOTICE(f'   User:  {user}\n'))

        # Quarter month mapping
        quarter_months = {
            1: (1, 2, 3),
            2: (4, 5, 6),
            3: (7, 8, 9),
            4: (10, 11, 12),
        }

        total_created = 0
        total_skipped = 0

        for year in years:
            self.stdout.write(f'  📅 Year {year} ...', ending=' ')

            # Determine default status
            if year < current_year:
                year_status = PeriodStatus.CLOSE
            else:
                year_status = PeriodStatus.OPEN

            with transaction.atomic():
                # ── Annual Period ─────────────────────────────────────────────
                annual, annual_created = AnnualPeriod.objects.get_or_create(
                    company=company,
                    year=year,
                    defaults={
                        'status': year_status,
                        'created_by': user,
                    },
                )
                if annual_created:
                    total_created += 1
                    PeriodActivityLog.objects.create(
                        company=company,
                        period_type='ANNUAL',
                        annual_period=annual,
                        action=year_status,
                        reason=f'[SEEDER] Annual period {year} initialized.',
                        period_label=str(year),
                        period_status_after=year_status,
                        actioned_by=user,
                    )
                else:
                    total_skipped += 1

                # ── Quarter Periods ───────────────────────────────────────────
                quarters = {}
                for q_num in range(1, 5):
                    # Quarter is OPEN only if year is current/future
                    # For current year, close past quarters
                    if year < current_year:
                        q_status = PeriodStatus.CLOSE
                    elif year == current_year:
                        current_quarter = (current_month - 1) // 3 + 1
                        q_status = PeriodStatus.OPEN if q_num >= current_quarter else PeriodStatus.CLOSE
                    else:
                        q_status = PeriodStatus.OPEN

                    qp, qp_created = QuarterPeriod.objects.get_or_create(
                        company=company,
                        year=year,
                        quarter=q_num,
                        defaults={
                            'annual_period': annual,
                            'status': q_status,
                            'created_by': user,
                        },
                    )
                    quarters[q_num] = qp
                    if qp_created:
                        total_created += 1
                        PeriodActivityLog.objects.create(
                            company=company,
                            period_type='QUARTER',
                            quarter_period=qp,
                            action=q_status,
                            reason=f'[SEEDER] Quarter Q{q_num} {year} initialized.',
                            period_label=f'{year} Q{q_num}',
                            period_status_after=q_status,
                            actioned_by=user,
                        )
                    else:
                        total_skipped += 1

                # ── Monthly + Accounting Periods ──────────────────────────────
                month_names = [
                    '', 'January', 'February', 'March', 'April',
                    'May', 'June', 'July', 'August',
                    'September', 'October', 'November', 'December',
                ]

                for month_num in range(1, 13):
                    q_num    = (month_num - 1) // 3 + 1
                    quarter  = quarters[q_num]
                    _, last  = calendar.monthrange(year, month_num)
                    start_dt = date(year, month_num, 1)
                    end_dt   = date(year, month_num, last)

                    # Month status logic
                    if year < current_year:
                        m_status = PeriodStatus.CLOSE
                    elif year == current_year:
                        m_status = PeriodStatus.OPEN if month_num >= current_month else PeriodStatus.CLOSE
                    else:
                        m_status = PeriodStatus.OPEN

                    mp, mp_created = MonthlyPeriod.objects.get_or_create(
                        company=company,
                        year=year,
                        month=month_num,
                        defaults={
                            'annual_period': annual,
                            'quarter_period': quarter,
                            'status': m_status,
                            'created_by': user,
                        },
                    )
                    if mp_created:
                        total_created += 1
                        PeriodActivityLog.objects.create(
                            company=company,
                            period_type='MONTHLY',
                            monthly_period=mp,
                            action=m_status,
                            reason=f'[SEEDER] Monthly period {month_names[month_num]} {year} initialized.',
                            period_label=f'{month_names[month_num]} {year}',
                            period_status_after=m_status,
                            actioned_by=user,
                        )
                    else:
                        total_skipped += 1

                    ap, ap_created = AccountingPeriod.objects.get_or_create(
                        company=company,
                        year=year,
                        month=month_num,
                        defaults={
                            'monthly_period': mp,
                            'start_date': start_dt,
                            'end_date': end_dt,
                            'status': m_status,
                            'created_by': user,
                        },
                    )
                    if ap_created:
                        total_created += 1
                        PeriodActivityLog.objects.create(
                            company=company,
                            period_type='ACCOUNTING',
                            accounting_period=ap,
                            action=m_status,
                            reason=f'[SEEDER] Accounting period {month_names[month_num]} {year} initialized.',
                            period_label=f'{month_names[month_num]} {year}',
                            period_status_after=m_status,
                            actioned_by=user,
                        )
                    else:
                        total_skipped += 1

            self.stdout.write(self.style.SUCCESS('✓'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'✅ Done! Created: {total_created} records | Skipped (already exist): {total_skipped} records'
        ))