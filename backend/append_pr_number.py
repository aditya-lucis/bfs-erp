
with open(r'C:\Traine\bfs-erp\backend\apps\purchase\serializers.py', 'r') as f:
    content = f.read()

replacement = '''
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
'''

import re
content = re.sub(r'class PurchaseOrderSerializer\(serializers\.ModelSerializer\):.*?(?=    def _calculate_totals)', replacement, content, flags=re.DOTALL)

with open(r'C:\Traine\bfs-erp\backend\apps\purchase\serializers.py', 'w') as f:
    f.write(content)

