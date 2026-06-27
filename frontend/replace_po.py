import re

file_path = 'src/views/purchase/POInboxView.vue'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replacements
content = content.replace('Purchase Requisition (PR) Inbox', 'Purchase Order (PO) Inbox')
content = content.replace('PR Inbox', 'PO Inbox')
content = content.replace('pr-inbox', 'po-inbox')
content = content.replace('pr_number', 'po_number')
content = content.replace('pr_date', 'po_date')
content = content.replace('pr_class', 'po_type')
content = content.replace('pr.pr_number', 'po.po_number')
content = content.replace('pr.pr_date', 'po.po_date')
content = content.replace('selectedPR', 'selectedPO')
content = content.replace('prStore', 'poStore')
content = content.replace('usePurchaseRequisitionStore', 'usePurchaseOrderStore')
content = content.replace('fetchPRInbox', 'fetchPOInbox')
content = content.replace('approvePR', 'approvePO')
content = content.replace('rejectPR', 'rejectPO')
content = content.replace('fetchPRDetail', 'fetchPODetail')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
