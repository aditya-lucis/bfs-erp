import os
import re

path = 'src/views/inventory/ReceiptReportInboxView.vue'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('Purchase Order (PO) Inbox', 'Receipt Report (RR) Inbox')
text = text.replace('Purchases | PO Inbox', 'Inventory | RR Inbox')
text = text.replace('Cari nomor PO...', 'Cari nomor RR...')
text = text.replace('Tidak ada PO yang', 'Tidak ada Receipt Report yang')
text = text.replace('riwayat pengajuan PO', 'riwayat pengajuan Receipt Report')
text = text.replace('Pilih dokumen PO', 'Pilih dokumen Receipt Report')
text = text.replace('Persetujuan untuk dokumen Purchase Order (PO)', 'Persetujuan untuk dokumen Receipt Report')
text = text.replace('Total Nilai (PO)', 'Jumlah Item')
text = text.replace('Detail PO', 'Detail Receipt Report')
text = text.replace("document_code: 'PO'", "document_code: 'RECEIPT_REPORT'")
text = text.replace("api.get(`/purchase/po/${selectedRequest.value.document_id}/`)", "api.get(`/inventory/receipt-reports/${selectedRequest.value.document_id}/`)")
text = text.replace('Total Amount', 'Status')
text = text.replace('formatCurrency(selectedRequest.amount)', "selectedRequest.amount ? selectedRequest.amount + ' item' : '-'")
text = text.replace('PO Type', 'Receipt Type')
text = text.replace('documentDetail.po_type', 'documentDetail.receipt_type')
text = text.replace('documentDetail.department_name', 'documentDetail.is_partial')
text = text.replace('documentDetail.project_name', 'documentDetail.po')
text = text.replace('formatCurrency(documentDetail.total_amount)', 'documentDetail.approval_status')

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
