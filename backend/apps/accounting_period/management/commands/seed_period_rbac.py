"""
BFS ERP — RBAC Seeder: Financial Period Functions & Permissions

Usage:
    python manage.py seed_period_rbac
    python manage.py seed_period_rbac --group-name "ACC-ACCMGR"
    python manage.py seed_period_rbac --group-name "ACC-ACCMGR" --all-permissions

What it does:
    1. Creates Module entry for 'Settings' if not exists
    2. Creates Function tree under: Accounting Setting → Financial Period Open Close
       - Matches menuData.js structure exactly
       - Override function codes to GL-PERIOD-xxx for API permission alignment
    3. Creates/updates API Function entries (GL-PERIOD-xxx) under GL Module
    4. Optionally assigns all permissions to a target AuthorizationGroup

Menu Tree Structure (matches menuData.js):
    SETTINGS
    └── Accounting Setting
        └── Financial Period Open Close
            ├── Accounting Period            → code: GL-PERIOD-ACCOUNTING
            ├── Annual Accounting Period     → code: GL-PERIOD-ANNUAL
            ├── Quarter Accounting Period    → code: GL-PERIOD-QUARTER
            ├── Monthly Accounting Period    → code: GL-PERIOD-MONTHLY
            └── Period Activity Log          → code: GL-PERIOD-LOG

Function Code Design (matches rbac_function_code in views):
    GL-PERIOD-ANNUAL      → Annual Period management
    GL-PERIOD-QUARTER     → Quarter Period management
    GL-PERIOD-MONTHLY     → Monthly Period management
    GL-PERIOD-ACCOUNTING  → Accounting Period management
    GL-PERIOD-LOG         → Period Activity Log (read-only)
"""

import re
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

# ── Import RBAC models at module level ──────────────────────────────────────
from apps.rbac.models import Module, Function, AuthorizationGroup, GroupFunction


# ─── Helper ──────────────────────────────────────────────────────────────────

def slugify_code(module_code: str, name: str) -> str:
    """
    Generate function code from menu name.
    Example: ('gl', 'Chart of Accounts') → 'GL-CHART-OF-ACCOUNTS'
    """
    clean = re.sub(r'[^a-zA-Z0-9\s]', '', name)
    slug = re.sub(r'\s+', '-', clean.strip()).upper()
    return f"{module_code.upper()}-{slug}"


# ─── Menu Tree Data (Settings → Accounting Setting → Financial Period Open Close) ──
# Matches menuData.js exactly

PERIOD_MENU_TREE = {
    'name': 'Financial Period Open Close',
    'code_override': None,  # auto-generated: SETTINGS-FINANCIAL-PERIOD-OPEN-CLOSE
    'url_path': '',
    'children': [
        {
            'name': 'Accounting Period',
            'code_override': 'GL-PERIOD-ACCOUNTING',
            'url_path': '/settings/accounting-period',
        },
        {
            'name': 'Annual Accounting Period',
            'code_override': 'GL-PERIOD-ANNUAL',
            'url_path': '/settings/annual-period',
        },
        {
            'name': 'Quarter Accounting Period',
            'code_override': 'GL-PERIOD-QUARTER',
            'url_path': '/settings/quarter-period',
        },
        {
            'name': 'Monthly Accounting Period',
            'code_override': 'GL-PERIOD-MONTHLY',
            'url_path': '/settings/monthly-period',
        },
        {
            'name': 'Period Activity Log',
            'code_override': 'GL-PERIOD-LOG',
            'url_path': '/settings/period-activity-log',
        },
    ],
}


# ─── API Function Definitions (for GL Module) ────────────────────────────────

PERIOD_API_FUNCTIONS = [
    {
        'code':        'GL-PERIOD-ANNUAL',
        'name':        'Annual Accounting Period',
        'description': 'Manage annual fiscal year periods — open, close, and view history.',
        'url_pattern': '/api/v1/accounting/periods/annual/',
        'order':       10,
    },
    {
        'code':        'GL-PERIOD-QUARTER',
        'name':        'Quarter Accounting Period',
        'description': 'Manage quarterly periods (Q1–Q4) — open and close per quarter.',
        'url_pattern': '/api/v1/accounting/periods/quarter/',
        'order':       11,
    },
    {
        'code':        'GL-PERIOD-MONTHLY',
        'name':        'Monthly Accounting Period',
        'description': 'Manage monthly periods (Jan–Dec) — open and close per month.',
        'url_pattern': '/api/v1/accounting/periods/monthly/',
        'order':       12,
    },
    {
        'code':        'GL-PERIOD-ACCOUNTING',
        'name':        'Accounting Period',
        'description': 'Manage detailed accounting periods with start/end dates.',
        'url_pattern': '/api/v1/accounting/periods/accounting/',
        'order':       13,
    },
    {
        'code':        'GL-PERIOD-LOG',
        'name':        'Period Activity Log',
        'description': 'View audit trail of all period open/close actions.',
        'url_pattern': '/api/v1/accounting/periods/logs/',
        'order':       14,
    },
]


class Command(BaseCommand):
    help = 'Seed RBAC menu tree (Settings) + API functions (GL) + permissions for Financial Period management'

    def add_arguments(self, parser):
        parser.add_argument(
            '--group-name',
            type=str,
            default=None,
            help='Name of the AuthorizationGroup to assign all period permissions to.',
        )
        parser.add_argument(
            '--all-permissions',
            action='store_true',
            default=False,
            help='Grant all CRUD permissions (can_create, can_read, can_update, can_delete) to the target group.',
        )

    def handle(self, *args, **options):
        group_name = options['group_name']
        all_permissions = options['all_permissions']

        self.stdout.write(self.style.MIGRATE_HEADING('🌱 Starting Financial Period RBAC Seeding...'))
        self.stdout.write('')

        with transaction.atomic():
            # ═══════════════════════════════════════════════════════════════
            # PART 1: Seed Menu Tree (Settings Module)
            # ═══════════════════════════════════════════════════════════════
            self.stdout.write(self.style.MIGRATE_HEADING('📁 Part 1: Menu Tree (Settings Module)'))

            # Ensure Settings Module exists
            settings_module, mod_created = Module.objects.update_or_create(
                code='settings',
                defaults={
                    'name': 'Setting',
                    'order': 11,
                    'is_active': True,
                },
            )
            if mod_created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created module: [{settings_module.code}] {settings_module.name}'))
            else:
                self.stdout.write(f'  · Module already exists: [{settings_module.code}] {settings_module.name}')

            # Find or create "Accounting Setting" parent function
            accounting_setting_code = 'SETTINGS-ACCOUNTING-SETTING'
            accounting_setting, acct_created = Function.objects.update_or_create(
                code=accounting_setting_code,
                defaults={
                    'module': settings_module,
                    'parent': None,
                    'name': 'Accounting Setting',
                    'url_path': '/settings/accounting-setting',
                    'order': 2,
                    'is_active': True,
                },
            )
            if acct_created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created parent: [{accounting_setting.code}] {accounting_setting.name}'))
            else:
                self.stdout.write(f'  · Parent exists: [{accounting_setting.code}] {accounting_setting.name}')

            # Seed "Financial Period Open Close" and its children
            count = self._seed_menu_tree(
                module=settings_module,
                parent=accounting_setting,
                menu_data=PERIOD_MENU_TREE,
                order_start=0,
            )
            self.stdout.write(f'  📦 {count} menu functions seeded under Financial Period Open Close')

            # ═══════════════════════════════════════════════════════════════
            # PART 2: Seed API Functions (GL Module)
            # ═══════════════════════════════════════════════════════════════
            self.stdout.write('')
            self.stdout.write(self.style.MIGRATE_HEADING('🔌 Part 2: API Functions (GL Module)'))

            gl_module, gl_created = Module.objects.update_or_create(
                code='gl',
                defaults={
                    'name': 'General Ledger',
                    'order': 2,
                    'is_active': True,
                },
            )
            if gl_created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created module: [{gl_module.code}] {gl_module.name}'))
            else:
                self.stdout.write(f'  · Module already exists: [{gl_module.code}] {gl_module.name}')

            created_api_functions = []
            for fn_data in PERIOD_API_FUNCTIONS:
                fn, fn_created = Function.objects.update_or_create(
                    code=fn_data['code'],
                    defaults={
                        'module': gl_module,
                        'name': fn_data['name'],
                        'description': fn_data['description'],
                        'url_path': fn_data['url_pattern'],
                        'order': fn_data['order'],
                        'is_active': True,
                    },
                )

                if fn_created:
                    created_api_functions.append(fn)
                    self.stdout.write(self.style.SUCCESS(f'    ✓ Created API: [{fn.code}] {fn.name}'))
                else:
                    self.stdout.write(f'    · Updated API: [{fn.code}] {fn.name}')

            # ═══════════════════════════════════════════════════════════════
            # PART 3: Assign Permissions to AuthorizationGroup
            # ═══════════════════════════════════════════════════════════════
            if group_name:
                self.stdout.write('')
                self.stdout.write(self.style.MIGRATE_HEADING('🔐 Part 3: Permission Assignment'))

                try:
                    group = AuthorizationGroup.objects.get(group_name=group_name)
                except AuthorizationGroup.DoesNotExist:
                    raise CommandError(
                        f'AuthorizationGroup "{group_name}" not found. '
                        f'Available groups: {list(AuthorizationGroup.objects.values_list("group_name", flat=True))}'
                    )

                self.stdout.write(f'  Target group: [{group.group_name}]')

                # Get all period functions (both menu tree + API — same codes)
                all_period_functions = Function.objects.filter(
                    code__in=[f['code'] for f in PERIOD_API_FUNCTIONS]
                )

                for fn in all_period_functions:
                    defaults = {
                        'can_read': True,  # Always grant read by default
                    }

                    if all_permissions:
                        defaults.update({
                            'can_create': True,
                            'can_update': True,
                            'can_delete': True,
                            'can_approve': True,
                            'can_print': True,
                            'can_export': True,
                        })

                    gf, gf_created = GroupFunction.objects.update_or_create(
                        authorization_group=group,
                        function=fn,
                        defaults=defaults,
                    )

                    if gf_created:
                        self.stdout.write(
                            self.style.SUCCESS(f'    ✓ Assigned: {group.group_name} → {fn.code}')
                        )
                    else:
                        self.stdout.write(f'    · Updated: {group.group_name} → {fn.code}')

        # ── Summary ───────────────────────────────────────────────────────
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✅ RBAC seeding complete!'))
        self.stdout.write('')
        self.stdout.write(self.style.MIGRATE_HEADING('📋 Summary:'))
        self.stdout.write('')
        self.stdout.write('  Menu Tree (Settings) — matches menuData.js:')
        self.stdout.write(f'    • SETTINGS → Accounting Setting → Financial Period Open Close')
        for child in PERIOD_MENU_TREE['children']:
            self.stdout.write(f'      → {child["name"]:30s} (code: {child["code_override"]})')
        self.stdout.write('')
        self.stdout.write('  API Functions (GL):')
        for fn_data in PERIOD_API_FUNCTIONS:
            self.stdout.write(f'    • {fn_data["code"]:30s} → {fn_data["name"]}')
        self.stdout.write('')
        self.stdout.write('  View mappings:')
        self.stdout.write('    AnnualPeriodListCreateView    → GL-PERIOD-ANNUAL')
        self.stdout.write('    AnnualPeriodToggleView         → GL-PERIOD-ANNUAL')
        self.stdout.write('    QuarterPeriodListView          → GL-PERIOD-QUARTER')
        self.stdout.write('    QuarterPeriodToggleView        → GL-PERIOD-QUARTER')
        self.stdout.write('    MonthlyPeriodListView          → GL-PERIOD-MONTHLY')
        self.stdout.write('    MonthlyPeriodToggleView        → GL-PERIOD-MONTHLY')
        self.stdout.write('    AccountingPeriodListView       → GL-PERIOD-ACCOUNTING')
        self.stdout.write('    AccountingPeriodToggleView     → GL-PERIOD-ACCOUNTING')
        self.stdout.write('    PeriodActivityLogListView      → GL-PERIOD-LOG')
        self.stdout.write('')

    def _seed_menu_tree(self, module, parent, menu_data, order_start):
        """Recursively seed menu tree with code override support."""
        count = 0

        # Determine function code (override or auto-generated)
        code = menu_data.get('code_override') or slugify_code(module.code, menu_data['name'])

        # Check for existing function with different code (to avoid duplicates)
        existing_by_name = Function.objects.filter(
            module=module,
            parent=parent,
            name=menu_data['name'],
        ).exclude(code=code).first()

        if existing_by_name:
            # Update existing function code to match override
            existing_by_name.code = code
            existing_by_name.save(update_fields=['code'])
            func = existing_by_name
            fn_created = False
            self.stdout.write(
                self.style.WARNING(f'    ⚠ Updated code: {existing_by_name.name} → {code}')
            )
        else:
            func, fn_created = Function.objects.update_or_create(
                code=code,
                defaults={
                    'module': module,
                    'parent': parent,
                    'name': menu_data['name'],
                    'url_path': menu_data.get('url_path', ''),
                    'order': order_start,
                    'is_active': True,
                },
            )

        if fn_created:
            self.stdout.write(self.style.SUCCESS(f'    ✓ Created: [{func.code}] {func.name}'))
        else:
            self.stdout.write(f'    · Updated: [{func.code}] {func.name}')

        count += 1

        # Seed children recursively
        children = menu_data.get('children', [])
        for child_order, child_data in enumerate(children, start=0):
            count += self._seed_menu_tree(
                module=module,
                parent=func,
                menu_data=child_data,
                order_start=child_order,
            )

        return count