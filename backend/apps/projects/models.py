from django.db import models
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


