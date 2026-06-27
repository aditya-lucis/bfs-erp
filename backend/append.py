import os

content = """
from .models import CompletionCertificate, CompletionCertificateDocument

class CompletionCertificateDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompletionCertificateDocument
        fields = ['id', 'cc', 'master_document', 'is_available', 'file', 'document_number', 'keterangan']
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
            'vendor_name', 'po_number', 'site_name', 'rap_name'
        ]
        read_only_fields = ['cc_number', 'approval_status', 'created_at', 'updated_at']

    def create(self, validated_data):
        documents_data = validated_data.pop('documents', [])
        # Auto generate cc_number
        import datetime
        now = datetime.datetime.now()
        prefix = f"CC{now.strftime('%m%d%y')}-"
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
            instance.documents.all().delete()
            for doc_data in documents_data:
                CompletionCertificateDocument.objects.create(cc=instance, **doc_data)
                
        return instance
"""

with open('c:/Traine/bfs-erp/backend/apps/purchase/serializers.py', 'a', encoding='utf-8') as f:
    f.write(content)
