from django.conf import settings
from django.db import models


# ─── Company ─────────────────────────────────────────────────────────────────

class Company(models.Model):
    """
    Single-tenant — hanya 1 row aktif.
    Dari screenshot Edit Company.
    """
    BUSINESS_TYPE_CHOICES = [
        ('trading',      'Trading'),
        ('manufacturing','Manufacturing'),
        ('service',      'Service'),
        ('medical',      'Medical'),
    ]

    logo                = models.ImageField(
                              upload_to='company/logo/',
                              null=True, blank=True,
                          )
    company_code        = models.CharField(max_length=20, unique=True)
    company_type        = models.CharField(max_length=50, blank=True)
    company_name        = models.CharField(max_length=200)
    company_tax_number  = models.CharField(max_length=50, blank=True)
    company_tax_date    = models.DateField(null=True, blank=True)
    opening_balance_date= models.DateField(null=True, blank=True)
    tax_serial_number   = models.CharField(max_length=50, blank=True)
    company_address     = models.TextField(blank=True)
    company_address2    = models.TextField(blank=True)
    bank                = models.CharField(max_length=100, blank=True)
    account_number      = models.CharField(max_length=50, blank=True)
    country             = models.CharField(max_length=100, default='Indonesia')
    state               = models.CharField(max_length=100, blank=True)
    postal_code         = models.CharField(max_length=10, blank=True)
    phone               = models.CharField(max_length=30, blank=True)
    fax                 = models.CharField(max_length=30, blank=True)
    email               = models.EmailField(blank=True)
    business_template   = models.CharField(
                              max_length=20,
                              choices=BUSINESS_TYPE_CHOICES,
                              default='trading',
                          )
    is_holding          = models.BooleanField(default=False)
    rap_tolerance       = models.PositiveSmallIntegerField(
                              default=100,
                              help_text='RAP Tolerance in percent',
                          )
    period_frequency    = models.PositiveSmallIntegerField(default=12)
    currency_id         = models.CharField(max_length=10, default='IDR')

    is_active           = models.BooleanField(default=True)
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)

    class Meta:
        db_table     = 'org_company'
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'

    def __str__(self):
        return f"[{self.company_code}] {self.company_name}"

    @classmethod
    def get_default(cls):
        """Ambil company aktif (single-tenant)."""
        return cls.objects.filter(is_active=True).first()


# ─── Department ───────────────────────────────────────────────────────────────

class Department(models.Model):
    """
    Self-referential tree — dari screenshot Organizational Structure.
    Contoh:
        bod (Board Of Director)
          └── dir (Direktur)
          └── non_medis (Non-Medis)
                └── fat (Finance, Akutansi & Tax)
                      └── akutansi (Akuntansi)
    """
    company     = models.ForeignKey(
                      Company,
                      on_delete=models.CASCADE,
                      related_name='departments',
                  )
    parent      = models.ForeignKey(
                      'self',
                      null=True, blank=True,
                      on_delete=models.CASCADE,
                      related_name='children',
                  )
    code        = models.CharField(max_length=50)
    name        = models.CharField(max_length=150)
    order       = models.PositiveSmallIntegerField(default=0)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table        = 'org_department'
        unique_together = ('company', 'code')
        ordering        = ['order', 'name']
        verbose_name    = 'Department'
        verbose_name_plural = 'Departments'

    def __str__(self):
        return f"{self.code}. {self.name}"

    def get_ancestors(self):
        """Return list of ancestors from root to self."""
        ancestors = []
        node = self.parent
        while node:
            ancestors.insert(0, node)
            node = node.parent
        return ancestors

    @property
    def level(self):
        return len(self.get_ancestors())


# ─── Position ─────────────────────────────────────────────────────────────────

class Position(models.Model):
    """
    Jabatan di dalam sebuah Department.
    Banyak Employee bisa pegang 1 Position.
    Contoh: Department=akutansi → Position='Accounting Manager'
    """
    department  = models.ForeignKey(
                      Department,
                      on_delete=models.CASCADE,
                      related_name='positions',
                  )
    code        = models.CharField(max_length=50)
    name        = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table        = 'org_position'
        unique_together = ('department', 'code')
        ordering        = ['department__name', 'name']
        verbose_name    = 'Position'
        verbose_name_plural = 'Positions'

    def __str__(self):
        return f"{self.department.code} › {self.name}"


# ─── Employee ─────────────────────────────────────────────────────────────────

class Employee(models.Model):
    """
    Data karyawan perusahaan.
    - Satu Position bisa dipegang banyak Employee.
    - Satu Employee hanya punya satu User (one-to-one).
    """
    STATUS_CHOICES = [
        ('active',      'Active'),
        ('inactive',    'Inactive'),
        ('resigned',    'Resigned'),
        ('terminated',  'Terminated'),
    ]

    # Link ke User (nullable dulu biar bisa ada employee tanpa akun sistem)
    user        = models.OneToOneField(
                      settings.AUTH_USER_MODEL,
                      null=True, blank=True,
                      on_delete=models.SET_NULL,
                      related_name='employee_profile',
                  )
    position    = models.ForeignKey(
                      Position,
                      on_delete=models.PROTECT,
                      related_name='employees',
                  )
    employee_id = models.CharField(max_length=30, unique=True)
    full_name   = models.CharField(max_length=150)
    email       = models.EmailField(blank=True)
    phone       = models.CharField(max_length=30, blank=True)
    status      = models.CharField(
                      max_length=20,
                      choices=STATUS_CHOICES,
                      default='active',
                  )
    join_date   = models.DateField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table     = 'org_employee'
        ordering     = ['employee_id']
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'

    def __str__(self):
        return f"[{self.employee_id}] {self.full_name} — {self.position}"

    @property
    def department(self):
        return self.position.department

    @property
    def company(self):
        return self.position.department.company