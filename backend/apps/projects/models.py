from django.db import models
from django.conf import settings
from apps.organization.models import Company, Employee
from apps.sales.models import Customer

class RAPType(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='rap_types'
    )
    name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_rap_type'
        ordering = ['name', 'id']
        verbose_name = 'RAP Type'
        verbose_name_plural = 'RAP Types'

    def __str__(self):
        return self.name


class ProjectType(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='project_types')
    name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_type'
        ordering = ['name']
        verbose_name = 'Project Type'
        verbose_name_plural = 'Project Types'

    def __str__(self):
        return self.name


class ProjectCategory(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='project_categories')
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=200)
    pattern_group_name = models.CharField(max_length=150, blank=True, default='')
    document_pattern = models.CharField(max_length=50, blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_category'
        ordering = ['code']
        verbose_name = 'Project Category'
        verbose_name_plural = 'Project Categories'

    def __str__(self):
        return f"[{self.code}] {self.name}"

    def save(self, *args, **kwargs):
        # Auto prefix code with company code
        if self.company and not self.code.startswith(self.company.company_code):
            self.code = f"{self.company.company_code}-{self.code}"
        super().save(*args, **kwargs)


class Project(models.Model):
    class Status(models.TextChoices):
        NOT_START = 'not_start', 'Not Start'
        START     = 'start',     'Start'
        CANCEL    = 'cancel',    'Cancel'

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='projects')
    project_code = models.CharField(max_length=50, unique=True, editable=False)
    project_name = models.CharField(max_length=250)
    project_type = models.ForeignKey(ProjectType, on_delete=models.PROTECT, related_name='projects')
    project_category = models.ForeignKey(ProjectCategory, on_delete=models.PROTECT, related_name='projects')
    site_code = models.CharField(max_length=100, blank=True, default='')
    site_id = models.CharField(max_length=100, blank=True, default='')
    site_name = models.CharField(max_length=200, blank=True, default='')
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='projects')
    currency_id = models.CharField(max_length=10, default='IDR')
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=2, default=1.00)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    project_manager = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name='managed_projects')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NOT_START)
    amount = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_list'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.project_code}] {self.project_name}"

    def save(self, *args, **kwargs):
        if not self.project_code:
            self.project_code = self._generate_project_code()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_project_code():
        from django.utils import timezone
        today = timezone.localtime().strftime('%Y%m%d')
        prefix = f"PRJ-{today}"
        last = Project.objects.filter(project_code__startswith=prefix).order_by('id').last()
        next_seq = (int(last.project_code.split('-')[-1]) + 1) if last else 1
        return f"{prefix}-{next_seq:04d}"


# ─── RAP (Rencana Anggaran Pelaksana) ──────────────────────────────────────────

class RAP(models.Model):
    class DocumentStatus(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        READY_TO_PROCESS = 'ready_to_process', 'Ready to Process'
        CLOSE = 'close', 'Close'

    class ApprovalStatus(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        AWAITING = 'awaiting', 'Awaiting'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Reject'
        REVISED = 'revised', 'Revised'

    class ActivityChoices(models.TextChoices):
        NOT_SET = 'not_set', 'Not Set'
        INVESTASI = 'investasi', 'Investasi'
        OPERATING = 'operating', 'Operating'
        FINANCING = 'financing', 'Financing'

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='raps')
    rap_number = models.CharField(max_length=100, unique=True, editable=False)
    rap_type = models.ForeignKey(RAPType, on_delete=models.PROTECT, related_name='raps')
    rap_date = models.DateField()
    month_period = models.PositiveSmallIntegerField()  # 1-12
    year_period = models.PositiveSmallIntegerField()
    cost_category = models.CharField(
        max_length=20,
        choices=[
            ('hpp', 'HPP'),
            ('revenue', 'REVENUE'),
            ('target_hpp', 'TARGET_HPP'),
            ('target_opex', 'TARGET_OPEX'),
            ('opex', 'OPEX'),
            ('capex', 'CAPEX'),
            ('tax', 'TAX'),
        ]
    )
    department = models.ForeignKey('organization.Department', on_delete=models.PROTECT, related_name='raps')
    position = models.ForeignKey('organization.Position', on_delete=models.PROTECT, related_name='raps')  # Cost of Unit
    budget_component = models.ForeignKey('budget_component.BudgetComponent', on_delete=models.PROTECT, related_name='raps')
    activity = models.CharField(max_length=20, choices=ActivityChoices.choices, default=ActivityChoices.NOT_SET)
    project = models.ForeignKey(Project, on_delete=models.PROTECT, related_name='raps')

    is_active = models.BooleanField(default=False)
    document_status = models.CharField(max_length=20, choices=DocumentStatus.choices, default=DocumentStatus.DRAFT)
    approval_status = models.CharField(max_length=20, choices=ApprovalStatus.choices, default=ApprovalStatus.DRAFT)

    total_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='created_raps'
    )

    class Meta:
        db_table = 'project_rap'
        ordering = ['-created_at']
        verbose_name = 'RAP'
        verbose_name_plural = 'RAPs'

    def __str__(self):
        return f"{self.rap_number} - {self.project.project_name}"

    def save(self, *args, **kwargs):
        if not self.rap_number:
            self.rap_number = self._generate_rap_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_rap_number():
        from django.utils import timezone
        timestamp = timezone.localtime().strftime('%Y%m%d%H%M%S')
        prefix = f"RAP{timestamp}-"
        last = RAP.objects.order_by('id').last()
        next_seq = (int(last.rap_number.split('-')[-1]) + 1) if last and '-' in last.rap_number else 1
        return f"{prefix}{next_seq:05d}"


class RAPDetail(models.Model):
    class ItemType(models.TextChoices):
        HEADER = 'header', 'Header'
        SUB_HEADER = 'sub_header', 'Sub Header'
        ITEM = 'item', 'Item'

    rap = models.ForeignKey(RAP, on_delete=models.CASCADE, related_name='details')
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='children'
    )
    item_type = models.CharField(max_length=15, choices=ItemType.choices, default=ItemType.HEADER)

    # For Header / Sub Header
    description = models.CharField(max_length=500, blank=True)

    # For Item
    item = models.ForeignKey(
        'inventory.Item',
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name='rap_details'
    )
    remarks = models.CharField(max_length=500, blank=True)

    # Volume & Price
    volume = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    unit_price = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    total_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)

    order_no = models.PositiveIntegerField(default=0)
    display_number = models.CharField(max_length=20, blank=True, editable=False)

    class Meta:
        db_table = 'project_rap_detail'
        ordering = ['rap', 'order_no', 'id']

    def __str__(self):
        return f"{self.display_number} {self.description or (self.item.item_name if self.item else '')}"

    def save(self, *args, **kwargs):
        # Auto calculate total cost for the line only if it is an item
        if self.item_type == self.ItemType.ITEM:
            self.total_cost = self.volume * self.unit_price
        
        # Auto generate display number
        self.display_number = self._generate_display_number()
        
        super().save(*args, **kwargs)

    def _generate_display_number(self):
        if not self.parent:
            siblings = RAPDetail.objects.filter(
                rap=self.rap,
                parent__isnull=True,
            ).exclude(pk=self.pk if self.pk else None)
            count = siblings.count() + 1
            return str(count)

        parent_num = self.parent.display_number
        siblings = RAPDetail.objects.filter(
            rap=self.rap,
            parent=self.parent,
        ).exclude(pk=self.pk if self.pk else None)
        count = siblings.count() + 1
        return f"{parent_num}.{count}"

# ─── Project Budget (Commitment & Actual Tracking) ──────────────────────────

class ProjectBudgetHeader(models.Model):
    """
    Menyimpan total akumulasi budget commit dan actual per Project.
    """
    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name='budget_header'
    )
    commit_amount_total = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    actual_amount_total = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, blank=True,
        related_name='created_project_budgets'
    )

    class Meta:
        db_table = 'project_budget_header'

    def __str__(self):
        return f"Budget for {self.project.project_name}"


class ProjectBudgetDetail(models.Model):
    """
    Menyimpan akumulasi commit dan actual per Item dan RAPDetail.
    """
    budget_header = models.ForeignKey(
        ProjectBudgetHeader,
        on_delete=models.CASCADE,
        related_name='details'
    )
    rap_detail = models.OneToOneField(
        RAPDetail,
        on_delete=models.CASCADE,
        related_name='budget_detail'
    )
    item = models.ForeignKey(
        'inventory.Item',
        on_delete=models.PROTECT,
        related_name='project_budget_details'
    )
    commit_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    actual_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    class Meta:
        db_table = 'project_budget_detail'

    def __str__(self):
        return f"Budget Detail for {self.item.item_name}"

