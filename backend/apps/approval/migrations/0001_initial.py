# Generated manually for approval app

import decimal
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('organization', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ApprovalMatrix',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document_code', models.CharField(choices=[('RAP', 'Rencana Anggaran Pelaksana (RAP)')], help_text='Kode transaksi/dokumen, e.g. RAP, PR, PO', max_length=20)),
                ('basis', models.CharField(choices=[('AMOUNT', 'Total Amount (After Disc & Tax)'), ('QUANTITY', 'Total Quantity')], default='AMOUNT', max_length=10)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='approval_matrices', to='organization.company')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_approval_matrices', to=settings.AUTH_USER_MODEL)),
                ('creator_position', models.ForeignKey(help_text='Posisi employee yang membuat dokumen', on_delete=django.db.models.deletion.PROTECT, related_name='approval_matrices_as_creator', to='organization.position')),
            ],
            options={
                'verbose_name': 'Approval Matrix',
                'verbose_name_plural': 'Approval Matrices',
                'db_table': 'approval_matrix',
                'ordering': ['document_code', 'creator_position__name'],
                'unique_together': {('company', 'document_code', 'creator_position')},
            },
        ),
        migrations.CreateModel(
            name='ApprovalMatrixRange',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_value', models.DecimalField(decimal_places=2, default=decimal.Decimal('0'), max_digits=18)),
                ('to_value', models.DecimalField(decimal_places=2, default=decimal.Decimal('0'), max_digits=18)),
                ('order_no', models.PositiveSmallIntegerField(default=0)),
                ('matrix', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ranges', to='approval.approvalmatrix')),
            ],
            options={
                'verbose_name': 'Approval Matrix Range',
                'verbose_name_plural': 'Approval Matrix Ranges',
                'db_table': 'approval_matrix_range',
                'ordering': ['order_no', 'from_value'],
            },
        ),
        migrations.CreateModel(
            name='ApprovalMatrixStep',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('step_number', models.PositiveSmallIntegerField()),
                ('role', models.CharField(choices=[('PREPARED_BY', 'Prepared By'), ('APPROVED_BY', 'Approved By'), ('ACKNOWLEDGE_BY', 'Acknowledge By'), ('ACCOUNTING_DEPT', 'Accounting Dept'), ('CHECKED_BY', 'Checked By'), ('VERIFIED_BY', 'Verified By'), ('ACCEPTED_BY', 'Accepted By')], max_length=20)),
                ('position', models.ForeignKey(help_text='Posisi yang bertanggung jawab pada step ini', on_delete=django.db.models.deletion.PROTECT, related_name='approval_matrix_steps', to='organization.position')),
                ('range', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='steps', to='approval.approvalmatrixrange')),
            ],
            options={
                'verbose_name': 'Approval Matrix Step',
                'verbose_name_plural': 'Approval Matrix Steps',
                'db_table': 'approval_matrix_step',
                'ordering': ['step_number'],
                'unique_together': {('range', 'step_number')},
            },
        ),
    ]
