
with open(r'C:\Traine\bfs-erp\backend\apps\purchase\serializers.py', 'a') as f:
    f.write('''

class POInboxSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source=\'vendor.name\', read_only=True)
    project_name = serializers.CharField(source=\'project.project_name\', read_only=True)
    requestor_department_name = serializers.CharField(source=\'requestor_department.name\', read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = [
            \'id\', \'po_number\', \'po_date\', \'vendor\', \'vendor_name\', 
            \'project\', \'project_name\', \'requestor_department_name\',
            \'grand_total\', \'document_status\', \'approval_status\', \'allow_previous_year_budget\'
        ]
''')

