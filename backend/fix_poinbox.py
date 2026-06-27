import os
import re

file_path = '../frontend/src/views/purchase/POInboxView.vue'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('nomor PR', 'nomor PO')
content = content.replace('ada PR yang', 'ada PO yang')
content = content.replace('pengajuan PR', 'pengajuan PO')
content = content.replace('dokumen PR dari', 'dokumen PO dari')
content = content.replace('Purchase Requisition (PR)', 'Purchase Order (PO)')
content = content.replace('Nilai (PR)', 'Nilai (PO)')
content = content.replace('detail PR', 'detail PO')
content = content.replace('Detail PR', 'Detail PO')
content = content.replace('Dokumen RAP', 'Dokumen PO')
content = content.replace('PR Type', 'PO Type')
content = content.replace('pr_type', 'po_type')
content = content.replace('/purchase/pr/${', '/purchase/po/${')
content = content.replace("document_code: 'PR'", "document_code: 'PO'")
content = content.replace('<!-- RAP Detail Modal -->', '<!-- PO Detail Modal -->')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
