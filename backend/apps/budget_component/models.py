from django.db import models
from django.conf import settings
from apps.inventory.models import Item
from apps.organization.models import Company, Department, Position


# ─── Budget Component ───────────────────────────────────────────────────────

class BudgetComponent(models.Model):
    """
    Budget Component — copycat dari Sokka ERP.
    Nama auto-generate dari: Cost Category + Department + Position.
    """

    class CostCategory(models.TextChoices):
        HPP          = 'hpp',          'HPP'
        REVENUE      = 'revenue',      'REVENUE'
        TARGET_HPP   = 'target_hpp',   'TARGET_HPP'
        TARGET_OPEX  = 'target_opex',  'TARGET_OPEX'
        OPEX         = 'opex',         'OPEX'
        CAPEX        = 'capex',        'CAPEX'
        TAX          = 'tax',          'TAX'

    class TemplateRap(models.TextChoices):
        NONE  = 'none',  'NONE'
        ADDED = 'added', 'ADDED'

    company       = models.ForeignKey(
                        Company,
                        on_delete=models.CASCADE,
                        related_name='budget_components',
                    )
    name          = models.CharField(max_length=200, blank=True, editable=False)
    cost_category = models.CharField(
                        max_length=20,
                        choices=CostCategory.choices,
                        default=CostCategory.OPEX,
                    )
    department    = models.ForeignKey(
                        Department,
                        on_delete=models.PROTECT,
                        related_name='budget_components',
                    )
    position      = models.ForeignKey(
                        Position,
                        on_delete=models.PROTECT,
                        related_name='budget_components',
                        null=True,
                        blank=True,
                    )
    order_no      = models.PositiveIntegerField(default=0)
    is_active     = models.BooleanField(default=True)
    template_rap  = models.CharField(
                        max_length=10,
                        choices=TemplateRap.choices,
                        default=TemplateRap.NONE,
                    )
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'budget_component'
        ordering = ['order_no', 'id']
        verbose_name = 'Budget Component'
        verbose_name_plural = 'Budget Components'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Auto-generate name: COST_CATEGORY - DEPARTMENT - POSITION
        dept_name = self.department.name if self.department else ''
        pos_name = self.position.name if self.position else ''

        parts = [self.cost_category.upper()]
        if dept_name:
            parts.append(dept_name.upper())
        if pos_name:
            parts.append(pos_name.upper())

        self.name = ' - '.join(parts)

        # Deactivate existing active budget components for the same position and cost category
        if self.is_active and self.position:
            from django.db import transaction
            with transaction.atomic():
                existing = BudgetComponent.objects.filter(
                    position=self.position,
                    cost_category=self.cost_category,
                    is_active=True
                )
                if self.pk:
                    existing = existing.exclude(pk=self.pk)
                
                # Deactivate their corresponding TemplateRAPHeaders if they exist
                TemplateRAPHeader.objects.filter(budget_component__in=existing).update(is_active=False)
                
                # Deactivate the budget components
                existing.update(is_active=False)

        super().save(*args, **kwargs)

    def update_template_rap_status(self):
        """Auto-update template_rap to ADDED if template exists with details."""
        if hasattr(self, 'template_rap_header') and self.template_rap_header:
            has_details = self.template_rap_header.details.exists()
            if has_details and self.template_rap == self.TemplateRap.NONE:
                self.template_rap = self.TemplateRap.ADDED
                self.save(update_fields=['template_rap'])
            elif not has_details and self.template_rap == self.TemplateRap.ADDED:
                self.template_rap = self.TemplateRap.NONE
                self.save(update_fields=['template_rap'])


# ─── Template RAP ───────────────────────────────────────────────────────────

class TemplateRAPHeader(models.Model):
    """
    Template RAP untuk 1 Budget Component.
    Contoh: "Template RAP of OPEX - Farmasi"
    """
    budget_component = models.OneToOneField(
        BudgetComponent,
        on_delete=models.CASCADE,
        related_name='template_rap_header',
    )
    template_name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'budget_component_template_rap'
        ordering = ['id']

    def __str__(self):
        return self.template_name

    def save(self, *args, **kwargs):
        if not self.template_name and self.budget_component:
            self.template_name = f"Template RAP of {self.budget_component.name}"
        super().save(*args, **kwargs)
        # Update parent budget_component's template_rap status
        self.budget_component.update_template_rap_status()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        # Reset to NONE when template deleted
        self.budget_component.update_template_rap_status()

# ─── Template RAP Detail (Tree) ─────────────────────────────────────────────
class TemplateRAPDetail(models.Model):
    """
    Tree structure: Header → Sub Header → Item
    """

    class ItemType(models.TextChoices):
        HEADER     = 'header',     'Header'
        SUB_HEADER = 'sub_header', 'Sub Header'
        ITEM       = 'item',       'Item'

    template = models.ForeignKey(
        TemplateRAPHeader,  # atau TemplateRAP kalau lo rename
        on_delete=models.CASCADE,
        related_name='details',
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='children',
    )
    item_type = models.CharField(
        max_length=15,
        choices=ItemType.choices,
        default=ItemType.HEADER,
    )

    # For Header / Sub Header
    description = models.CharField(max_length=500, blank=True)

    # For Item (leaf node)
    item = models.ForeignKey(
        Item,
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name='template_rap_details',
    )
    remarks = models.CharField(max_length=500, blank=True)

    # Display order within same parent
    order_no = models.PositiveIntegerField(default=0)

    # Auto-generated display number: 1, 1.1, 1.1.1, etc.
    display_number = models.CharField(max_length=20, blank=True, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'budget_component_template_rap_detail'
        ordering = ['template', 'order_no', 'id']

    def __str__(self):
        return f"{self.display_number} {self.description or (self.item.item_name if self.item else '')}"

    def save(self, *args, **kwargs):
        # Auto-generate display number
        self.display_number = self._generate_display_number()
        super().save(*args, **kwargs)
        # Update parent template status
        self.template.budget_component.update_template_rap_status()

    def delete(self, *args, **kwargs):
        template = self.template
        super().delete(*args, **kwargs)
        # Update parent template status
        template.budget_component.update_template_rap_status()

    def _generate_display_number(self):
        if not self.parent:
            # Root level: just sequential number
            siblings = TemplateRAPDetail.objects.filter(
                template=self.template,
                parent__isnull=True,
            ).exclude(pk=self.pk if self.pk else None)
            count = siblings.count() + 1
            return str(count)

        # Has parent: parent's number + . + sibling count + 1
        parent_num = self.parent.display_number
        siblings = TemplateRAPDetail.objects.filter(
            template=self.template,
            parent=self.parent,
        ).exclude(pk=self.pk if self.pk else None)
        count = siblings.count() + 1
        return f"{parent_num}.{count}"

# ─── Budget Commitment Log ──────────────────────────────────────────────────
class BudgetCommitmentLog(models.Model):
    """
    Tabel Historis (Log) untuk setiap transaksi yang memotong / menambah budget.
    Menggantikan TAccBudgetTransCommit dan TAccBudgetProject_Actual.
    """
    class DocumentType(models.TextChoices):
        PO  = 'PO',  'Purchase Order'
        RR  = 'RR',  'Receipt Report'
        CBR = 'CBR', 'Cashbook Request'
        MR  = 'MR',  'Material Requisition'

    document_type = models.CharField(max_length=5, choices=DocumentType.choices)
    document_no = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    department = models.ForeignKey(
        'organization.Department', 
        on_delete=models.PROTECT, 
        related_name='budget_commitments'
    )
    rap_detail = models.ForeignKey(
        'projects.RAPDetail', 
        on_delete=models.SET_NULL, 
        null=True, blank=True, 
        related_name='budget_commitments'
    )
    account = models.ForeignKey(
        'accounting.Account', 
        on_delete=models.SET_NULL, 
        null=True, blank=True, 
        related_name='budget_commitments'
    )
    month = models.PositiveSmallIntegerField()
    year = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, blank=True
    )

    class Meta:
        db_table = 'budget_commitment_log'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.document_type}] {self.document_no} - {self.amount}"