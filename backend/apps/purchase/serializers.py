from rest_framework import serializers
from decimal import Decimal
from .models import (
    VendorCategory,
    VendorGroup,
    Vendor,
    VendorLinkedAccount,
    VendorTerms,
    VendorContactPerson,
    PurchaseRequisition,
    PurchaseRequisitionDetail,
)


class VendorCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorCategory
        fields = '__all__'


class VendorGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorGroup
        fields = '__all__'


class VendorLinkedAccountSerializer(serializers.ModelSerializer):
    account_name = serializers.CharField(source='account.account_name', read_only=True)
    account_code = serializers.CharField(source='account.account_number', read_only=True)

    class Meta:
        model = VendorLinkedAccount
        fields = [
            'id',
            'account_type',
            'currency_scope',
            'account',
            'account_name',
            'account_code',
        ]


class VendorTermsSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorTerms
        fields = [
            'id',
            'payment_due',
            'balance_due_days',
            'tax_code',
            'use_vendor_tax_code',
            'credit_limit',
        ]


class VendorContactPersonSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = VendorContactPerson
        fields = [
            'id',
            'first_name',
            'middle_name',
            'last_name',
            'nickname',
            'title',
            'job_title',
            'gender',
            'spouse',
            'birthday',
            'email',
            'country',
            'city',
            'area',
            'home_address',
            'zip_code',
            'phone',
            'mobile_phone',
            'fax',
            'notes',
            'full_name',
        ]


# --- Read (detail & list) ---

class VendorDetailSerializer(serializers.ModelSerializer):
    linked_accounts  = VendorLinkedAccountSerializer(many=True, read_only=True)
    terms            = VendorTermsSerializer(read_only=True)
    contact_persons  = VendorContactPersonSerializer(many=True, read_only=True)
    category_name    = serializers.CharField(source='category.name', read_only=True)
    group_name       = serializers.CharField(source='group.name', read_only=True)

    class Meta:
        model = Vendor
        fields = [
            'id', 'code',
            'title', 'name',
            'category', 'category_name',
            'department', 'variety',
            'tax_number', 'nppkp',
            'is_leasing',
            'email', 'alternative_email', 'website',
            'address_1', 'address_2',
            'country', 'state', 'city', 'zip_code', 'area_code',
            'phone_1', 'phone_2', 'fax',
            'currency', 'tolerance_difference', 'deposit',
            'bank_name', 'bank_branch', 'bank_city', 'bank_account_number', 'bank_account_name',
            'term_and_condition',
            'company_financial_capability',
            'notary_name', 'letter_no_date', 'notary_name_2', 'letter_no_date_2', 'letter_of_endorsement',
            'no_siup', 'expired_date_siup', 'no_tdp', 'expired_date_tdp',
            'no_sk_domisili', 'expired_date_sk_domisili', 'no_siujk', 'expired_date_siujk',
            'kriteria_usaha',
            'item_type_asset', 'item_type_fg', 'item_type_rm',
            'item_type_supplies', 'item_type_wip', 'item_type_maintenance', 'item_type_subcont',
            'group', 'group_name',
            'is_sister_company', 'status',
            'created_at', 'updated_at',
            'linked_accounts', 'terms', 'contact_persons',
        ]


class VendorListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Vendor
        fields = [
            'id', 'code',
            'title', 'name',
            'category', 'category_name',
            'address_1', 'city', 'phone_1', 'fax',
            'currency', 'status',
        ]


# --- Write ---

class VendorWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        exclude = ['code', 'created_at', 'updated_at', 'company']

    def validate_email(self, value):
        qs = Vendor.objects.filter(email=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Email sudah digunakan vendor lain.")
            
        return value

# ─────────────────────────────────────────────────────────────────────────────
# Purchase Requisition Serializers
# ─────────────────────────────────────────────────────────────────────────────

class PurchaseRequisitionDetailSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.item_name', read_only=True)
    item_code = serializers.CharField(source='item.item_code', read_only=True)
    unit_name = serializers.CharField(source='unit.unit_name', read_only=True)
    rap_budget_amount = serializers.DecimalField(source='rap_detail.amount', max_digits=18, decimal_places=2, read_only=True)

    class Meta:
        model = PurchaseRequisitionDetail
        fields = [
            'id', 'pr', 'rap_detail', 'item', 'item_code', 'item_name', 
            'asset_name', 'quantity', 'unit', 'unit_name', 
            'unit_price', 'final_unit_price', 'amount', 'notes', 'order_no',
            'rap_budget_amount'
        ]
        read_only_fields = ['amount']
        extra_kwargs = {
            'pr': {'required': False}
        }


class PurchaseRequisitionListSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    rap_name = serializers.CharField(source='rap.rap_name', read_only=True)
    pr_type_display = serializers.CharField(source='get_pr_type_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = PurchaseRequisition
        fields = [
            'id', 'pr_number', 'pr_date', 'pr_type', 'pr_type_display',
            'project', 'project_name', 'rap', 'rap_name', 
            'department', 'department_name', 'currency',
            'request_type', 'pr_class', 'repetition', 'etd', 'delivery_point',
            'total_amount', 'document_status', 'approval_status',
            'created_by_name'
        ]


class PurchaseRequisitionSerializer(serializers.ModelSerializer):
    details = PurchaseRequisitionDetailSerializer(many=True, required=False)
    department_name = serializers.CharField(source='department.name', read_only=True)
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    rap_name = serializers.CharField(source='rap.rap_name', read_only=True)
    rap_number = serializers.CharField(source='rap.rap_number', read_only=True)
    budget_component_name = serializers.CharField(source='budget_component.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = PurchaseRequisition
        fields = '__all__'
        read_only_fields = ['pr_number', 'document_status', 'approval_status', 'company', 'created_by']

    def create(self, validated_data):
        details_data = validated_data.pop('details', [])
        
        # Set final_unit_price and calculate total amount
        total_amount = 0
        for item in details_data:
            if 'final_unit_price' not in item:
                item['final_unit_price'] = item.get('unit_price', 0)
            total_amount += item.get('quantity', 0) * item['final_unit_price']
            
        validated_data['total_amount'] = total_amount
        
        pr = PurchaseRequisition.objects.create(**validated_data)
        
        for i, detail_data in enumerate(details_data):
            detail_data['order_no'] = i
            PurchaseRequisitionDetail.objects.create(pr=pr, **detail_data)
            
        return pr

    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        if details_data is not None:
            # Set final_unit_price and re-calculate total amount
            total_amount = 0
            for item in details_data:
                if 'final_unit_price' not in item:
                    item['final_unit_price'] = item.get('unit_price', 0)
                total_amount += item.get('quantity', 0) * item['final_unit_price']
                
            instance.total_amount = total_amount
            
            # Clear old details and create new ones
            instance.details.all().delete()
            for i, detail_data in enumerate(details_data):
                detail_data['order_no'] = i
                PurchaseRequisitionDetail.objects.create(pr=instance, **detail_data)
                
        instance.save()
        return instance

# ─────────────────────────────────────────────────────────────────────────────
# Purchase Order Serializers
# ─────────────────────────────────────────────────────────────────────────────

from .models import PurchaseOrder, PurchaseOrderDetail, PurchaseOrderPaymentTerm

class PurchaseOrderDetailSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.item_name', read_only=True)
    item_code = serializers.CharField(source='item.item_code', read_only=True)
    unit_name = serializers.CharField(source='unit.unit_name', read_only=True)
    budget_component_name = serializers.CharField(source='budget_component.name', read_only=True)

    class Meta:
        model = PurchaseOrderDetail
        fields = [
            'id', 'po', 'pr_detail', 'item', 'item_code', 'item_name',
            'rap_detail', 'budget_component', 'budget_component_name',
            'quantity', 'unit', 'unit_name', 'unit_price',
            'discount_percent', 'discount_amount', 'amount',
            'tax_amount', 'deduction_amount',
            'paid_amount', 'paid_tax_amount',
            'tax1', 'tax2', 'estimated_date', 'order_no'
        ]
        read_only_fields = ['amount', 'discount_amount', 'tax_amount', 'deduction_amount', 'paid_amount', 'paid_tax_amount']
        extra_kwargs = {
            'po': {'required': False}
        }


class PurchaseOrderPaymentTermSerializer(serializers.ModelSerializer):
    has_active_cc = serializers.SerializerMethodField()
    
    class Meta:
        model = PurchaseOrderPaymentTerm
        fields = [
            'id', 'po', 'term_desc', 'duration_due', 'duration_due_percent',
            'amount', 'due_date', 'doc_reff', 'order_no', 'has_active_cc'
        ]
        extra_kwargs = {
            'po': {'required': False}
        }
        
    def get_has_active_cc(self, obj):
        return obj.completioncertificate_set.filter(is_active=True).exists()


class PurchaseOrderListSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)
    vendor_code = serializers.CharField(source='vendor.code', read_only=True)
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    department_name = serializers.CharField(source='requestor_department.name', read_only=True)
    po_type_display = serializers.CharField(source='get_po_type_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = [
            'id', 'po_number', 'po_date', 'vendor', 'vendor_name', 'vendor_code',
            'po_type', 'po_type_display', 'project', 'project_name',
            'requestor_department', 'department_name', 'po_currency',
            'document_status', 'approval_status', 'grand_total', 'created_by_name',
            'allow_previous_year_budget', 'is_active'
        ]



class PurchaseOrderSerializer(serializers.ModelSerializer):
    details = PurchaseOrderDetailSerializer(many=True, required=False)
    payment_terms = PurchaseOrderPaymentTermSerializer(many=True, required=False)
    
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)
    vendor_code = serializers.CharField(source='vendor.code', read_only=True)
    vendor_address = serializers.CharField(source='vendor.address_1', read_only=True)
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    rap_name = serializers.CharField(source='rap.rap_name', read_only=True)
    rap_number = serializers.CharField(source='rap.rap_number', read_only=True)
    department_name = serializers.CharField(source='requestor_department.name', read_only=True)
    rr_account_name = serializers.CharField(source='rr_account.name', read_only=True)
    vi_account_name = serializers.CharField(source='vi_account.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    pr_number = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrder
        fields = '__all__'
        read_only_fields = [
            'po_number', 'document_status', 'approval_status', 
            'company', 'created_by', 'total_amount', 'total_discount',
            'total_tax', 'total_deduction', 'grand_total', 'payment_balance'
        ]

    def get_pr_number(self, obj):
        first_detail = obj.details.first()
        if first_detail and first_detail.pr_detail:
            return first_detail.pr_detail.pr.pr_number
        return None
    def _calculate_totals(self, validated_data, details_data):
        total_amount = Decimal('0')
        total_discount = Decimal('0')
        total_tax = Decimal('0')
        total_deduction = Decimal('0')
        
        tax_map = {
            'none': (Decimal('0'), 'none'),
            'non': (Decimal('0'), 'none'),
            'pph_23_rate_15': (Decimal('15'), 'deduction'),
            'pph_23_rate_2': (Decimal('2'), 'deduction'),
            'pph_23_rate_4': (Decimal('4'), 'deduction'),
            'pph_23_rate_4_5': (Decimal('4.5'), 'deduction'),
            'pph_23_rate_7_5': (Decimal('7.5'), 'deduction'),
            'pph_4_2_rate_10': (Decimal('10'), 'deduction'),
            'pph_4_2_rate_2': (Decimal('2'), 'deduction'),
            'pph_4_2_rate_3': (Decimal('3'), 'deduction'),
            'pph_4_2_rate_4': (Decimal('4'), 'deduction'),
            'ppn_01': (Decimal('1'), 'addition'),
            'ppn_10': (Decimal('10'), 'addition'),
            'ppn_10_euro': (Decimal('10'), 'addition'),
            'ppn_11': (Decimal('11'), 'addition'),
            'ppn_15': (Decimal('15'), 'addition'),
        }
        
        is_ppn_inclusive = validated_data.get('ppn', False)
        
        for item in details_data:
            qty = Decimal(str(item.get('quantity') or 0))
            price = Decimal(str(item.get('final_unit_price', item.get('unit_price', 0))))
            disc_pct = Decimal(str(item.get('discount_percent') or 0))
            
            base_amount = qty * price
            disc_amt = base_amount * (disc_pct / Decimal('100'))
            discounted_amount = base_amount - disc_amt
            
            total_amount += base_amount
            total_discount += disc_amt
            
            t1 = tax_map.get(item.get('tax1', 'none'), (Decimal('0'), 'none'))
            t2 = tax_map.get(item.get('tax2', 'none'), (Decimal('0'), 'none'))
            
            ppn_rate = Decimal('0')
            pph_rate = Decimal('0')
            
            if t1[1] == 'addition': ppn_rate += t1[0]
            if t2[1] == 'addition': ppn_rate += t2[0]
            if t1[1] == 'deduction': pph_rate += t1[0]
            if t2[1] == 'deduction': pph_rate += t2[0]
            
            baseAmount = discounted_amount
            itemPPN = Decimal('0')
            
            if is_ppn_inclusive:
                baseAmount = discounted_amount / (Decimal('1') + (ppn_rate / Decimal('100')))
                itemPPN = discounted_amount - baseAmount
            else:
                itemPPN = baseAmount * (ppn_rate / Decimal('100'))
                
            itemPPh = baseAmount * (pph_rate / Decimal('100'))
            
            total_tax += itemPPN
            total_deduction += itemPPh
            
        grand_total = total_amount - total_discount
        
        validated_data['total_amount'] = total_amount
        validated_data['total_discount'] = total_discount
        validated_data['total_tax'] = total_tax
        validated_data['total_deduction'] = total_deduction
        validated_data['grand_total'] = grand_total
        validated_data['payment_balance'] = grand_total

    def create(self, validated_data):
        details_data = validated_data.pop('details', [])
        payment_terms_data = validated_data.pop('payment_terms', [])
        
        self._calculate_totals(validated_data, details_data)
        
        po = PurchaseOrder.objects.create(**validated_data)
        
        for i, detail_data in enumerate(details_data):
            detail_data['order_no'] = i
            PurchaseOrderDetail.objects.create(po=po, **detail_data)
            
        for i, pt_data in enumerate(payment_terms_data):
            pt_data['order_no'] = i
            PurchaseOrderPaymentTerm.objects.create(po=po, **pt_data)
            
        return po

    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', None)
        payment_terms_data = validated_data.pop('payment_terms', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        if details_data is not None:
            self._calculate_totals(validated_data, details_data)
            instance.total_amount = validated_data.get('total_amount', 0)
            instance.total_discount = validated_data.get('total_discount', 0)
            instance.grand_total = validated_data.get('grand_total', 0)
            instance.payment_balance = validated_data.get('payment_balance', 0)
            
            instance.details.all().delete()
            for i, detail_data in enumerate(details_data):
                detail_data['order_no'] = i
                PurchaseOrderDetail.objects.create(po=instance, **detail_data)
                
        if payment_terms_data is not None:
            instance.payment_terms.all().delete()
            for i, pt_data in enumerate(payment_terms_data):
                pt_data['order_no'] = i
                PurchaseOrderPaymentTerm.objects.create(po=instance, **pt_data)
                
        instance.save()
        return instance


class POInboxSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    requestor_department_name = serializers.CharField(source='requestor_department.name', read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = [
            'id', 'po_number', 'po_date', 'vendor', 'vendor_name', 
            'project', 'project_name', 'requestor_department_name',
            'grand_total', 'document_status', 'approval_status', 'allow_previous_year_budget'
        ]

from .models import GrnSesDocument
class GrnSesDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrnSesDocument
        fields = '__all__'

from .models import CompletionCertificate, CompletionCertificateDocument

import base64
import uuid
import mimetypes
from django.core.files.base import ContentFile

class Base64FileField(serializers.FileField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:'):
            # Format: data:image/png;base64,<base64 data>
            format, imgstr = data.split(';base64,')
            mime_type = format.split(':')[1] if ':' in format else ''
            ext = mimetypes.guess_extension(mime_type) or '.bin'
            
            # Use a dummy name, we will rename it during save
            name = str(uuid.uuid4()) + ext
            data = ContentFile(base64.b64decode(imgstr), name=name)
        return super().to_internal_value(data)

class CompletionCertificateDocumentSerializer(serializers.ModelSerializer):
    file = Base64FileField(required=False, allow_null=True)
    document_name = serializers.CharField(source='master_document.document_name', read_only=True)

    class Meta:
        model = CompletionCertificateDocument
        fields = ['id', 'cc', 'master_document', 'document_name', 'is_available', 'file', 'document_number', 'keterangan']
        extra_kwargs = {
            'cc': {'read_only': True}
        }

class CompletionCertificateSerializer(serializers.ModelSerializer):
    documents = CompletionCertificateDocumentSerializer(many=True, read_only=False)
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)
    po_number = serializers.CharField(source='po.po_number', read_only=True)
    site_name = serializers.CharField(source='po.project.site_name', read_only=True)
    rap_name = serializers.CharField(source='po.project.rap.document_name', read_only=True, default='None')

    class Meta:
        model = CompletionCertificate
        fields = [
            'id', 'cc_number', 'document_date', 'vendor', 'po', 'description', 
            'type', 'document_date_from_vendor', 'currency', 'payment_term', 
            'amount', 'approval_status', 'is_active', 'documents',
            'vendor_name', 'po_number', 'site_name', 'rap_name',
            'void_reason', 'void_date'
        ]
        read_only_fields = ['cc_number', 'approval_status', 'created_at', 'updated_at']

    def create(self, validated_data):
        documents_data = validated_data.pop('documents', [])
        # Auto generate cc_number
        import datetime
        now = datetime.datetime.now()
        prefix = f"CC{now.strftime('%Y%m%d%H%M%S')}-"
        last_cc = CompletionCertificate.objects.filter(cc_number__startswith=prefix).order_by('id').last()
        if last_cc:
            last_seq = int(last_cc.cc_number.split('-')[1])
            new_seq = last_seq + 1
        else:
            new_seq = 1
        validated_data['cc_number'] = f"{prefix}{new_seq:07d}"
        
        cc = CompletionCertificate.objects.create(**validated_data)
        
        for doc_data in documents_data:
            CompletionCertificateDocument.objects.create(cc=cc, **doc_data)
        
        return cc

    def update(self, instance, validated_data):
        documents_data = validated_data.pop('documents', [])
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if documents_data:
            # Update or create documents based on master_document
            existing_docs = {doc.master_document_id: doc for doc in instance.documents.all()}
            for doc_data in documents_data:
                master_document = doc_data.get('master_document')
                file = doc_data.get('file', None)
                
                if master_document.id in existing_docs:
                    doc = existing_docs.pop(master_document.id)
                    doc.is_available = doc_data.get('is_available', doc.is_available)
                    doc.document_number = doc_data.get('document_number', doc.document_number)
                    doc.keterangan = doc_data.get('keterangan', doc.keterangan)
                    if file is not None:
                        doc.file = file
                    doc.save()
                else:
                    CompletionCertificateDocument.objects.create(cc=instance, **doc_data)
            
            # Delete any that were not in the payload
            for doc in existing_docs.values():
                doc.delete()
                
        return instance

from .models import GoodReceiptNote, GoodReceiptNoteDocument

class GoodReceiptNoteDocumentSerializer(serializers.ModelSerializer):
    document_name = serializers.CharField(source='master_document.document_name', read_only=True)
    type = serializers.CharField(source='master_document.type', read_only=True)

    class Meta:
        model = GoodReceiptNoteDocument
        fields = ['id', 'grn', 'master_document', 'is_available', 'file', 'document_number', 'keterangan', 'document_name', 'type']
        extra_kwargs = {
            'grn': {'read_only': True}
        }

class GoodReceiptNoteSerializer(serializers.ModelSerializer):
    documents = GoodReceiptNoteDocumentSerializer(many=True, read_only=False)
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)
    po_number = serializers.CharField(source='po.po_number', read_only=True)
    cc_number = serializers.CharField(source='cc.cc_number', read_only=True)
    site_name = serializers.CharField(source='po.project.site_name', read_only=True)
    rap_name = serializers.CharField(source='po.project.rap.document_name', read_only=True, default='None')

    class Meta:
        model = GoodReceiptNote
        fields = [
            'id', 'grn_number', 'vendor', 'po', 'cc', 'document_date', 'acceptance_date',
            'description', 'type', 'currency', 'amount', 'term_percentage',
            'approval_status', 'is_active', 'documents',
            'vendor_name', 'po_number', 'cc_number', 'site_name', 'rap_name',
            'void_reason', 'void_date'
        ]
        read_only_fields = ['grn_number', 'approval_status', 'created_at', 'updated_at']

    def create(self, validated_data):
        documents_data = validated_data.pop('documents', [])
        import datetime
        now = datetime.datetime.now()
        prefix = f"GRN{now.strftime('%Y%m%d%H%M%S')}-"
        last_grn = GoodReceiptNote.objects.filter(grn_number__startswith=prefix).order_by('id').last()
        if last_grn:
            last_seq = int(last_grn.grn_number.split('-')[1])
            new_seq = last_seq + 1
        else:
            new_seq = 1
        validated_data['grn_number'] = f"{prefix}{new_seq:07d}"
        
        grn = GoodReceiptNote.objects.create(**validated_data)
        
        for doc_data in documents_data:
            if doc_data.get('file') is None and grn.cc:
                from apps.purchase.models import CompletionCertificateDocument
                cc_doc = CompletionCertificateDocument.objects.filter(
                    cc=grn.cc, master_document=doc_data.get('master_document')
                ).first()
                if cc_doc and cc_doc.file:
                    doc_data['file'] = cc_doc.file
            GoodReceiptNoteDocument.objects.create(grn=grn, **doc_data)
        
        return grn

    def update(self, instance, validated_data):
        documents_data = validated_data.pop('documents', [])
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if documents_data:
            existing_docs = {doc.master_document_id: doc for doc in instance.documents.all()}
            for doc_data in documents_data:
                master_document = doc_data.get('master_document')
                file = doc_data.get('file', None)
                
                if master_document.id in existing_docs:
                    doc = existing_docs.pop(master_document.id)
                    doc.is_available = doc_data.get('is_available', doc.is_available)
                    doc.document_number = doc_data.get('document_number', doc.document_number)
                    doc.keterangan = doc_data.get('keterangan', doc.keterangan)
                    if file is not None:
                        doc.file = file
                    elif not doc.file and instance.cc:
                        from apps.purchase.models import CompletionCertificateDocument
                        cc_doc = CompletionCertificateDocument.objects.filter(
                            cc=instance.cc, master_document=master_document
                        ).first()
                        if cc_doc and cc_doc.file:
                            doc.file = cc_doc.file
                    doc.save()
                else:
                    if file is None and instance.cc:
                        from apps.purchase.models import CompletionCertificateDocument
                        cc_doc = CompletionCertificateDocument.objects.filter(
                            cc=instance.cc, master_document=master_document
                        ).first()
                        if cc_doc and cc_doc.file:
                            doc_data['file'] = cc_doc.file
                    GoodReceiptNoteDocument.objects.create(grn=instance, **doc_data)
            
            for doc in existing_docs.values():
                doc.delete()
                
        return instance
