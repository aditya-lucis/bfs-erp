from django.db import models
from django.db import transaction
from apps.organization.models import Company

class TransactionType(models.Model):
    """
    Master data untuk Transaction Type.
    TYPE_CODE menggunakan format TrsType_X dengan auto-increment terpisah dari PK.
    """
    type_code = models.CharField(max_length=50, unique=True, blank=True)
    type_name_en = models.CharField(max_length=150)
    type_name_id = models.CharField(max_length=150)
    table_name = models.CharField(max_length=50, default='TrsType')
    order_no = models.IntegerField(default=0)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='transaction_types')
    is_not_active = models.BooleanField(default=False)
    
    # Metadata fields (standard for the project but mostly skipped for brevity if not asked,
    # however created_at and updated_at are standard practice).
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'master_transaction_type'
        ordering = ['order_no', 'type_code']
        verbose_name = 'Transaction Type'
        verbose_name_plural = 'Transaction Types'

    def __str__(self):
        return f"{self.type_code} - {self.type_name_en}"

    def save(self, *args, **kwargs):
        if not self.type_code:
            # Auto-increment logic: TrsType_1, TrsType_2, etc.
            with transaction.atomic():
                # Lock the table to prevent race conditions when finding the max ID
                # Actually, filtering by prefix and extracting max integer is safer.
                last_trstype = (
                    TransactionType.objects.select_for_update()
                    .filter(type_code__startswith='TrsType_')
                    .order_by('-id')
                )
                
                max_num = 0
                for item in last_trstype:
                    try:
                        num = int(item.type_code.split('_')[1])
                        if num > max_num:
                            max_num = num
                    except (IndexError, ValueError):
                        continue
                        
                self.type_code = f"TrsType_{max_num + 1}"
        super().save(*args, **kwargs)
