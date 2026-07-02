import sys

file_path = 'c:/Traine/bfs-erp/frontend/src/views/purchase/GRNInboxView.vue'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('Tampilkan semua riwayat pengajuan CC', 'Tampilkan semua riwayat pengajuan GRN')
content = content.replace('Pilih dokumen CC dari panel kiri', 'Pilih dokumen GRN dari panel kiri')
content = content.replace('Total Nilai (CC)', 'Total Nilai (GRN)')
content = content.replace('Klik untuk melihat detail CC', 'Klik untuk melihat detail GRN')
content = content.replace('Tanda Tangan Dokumen CC', 'Tanda Tangan Dokumen GRN')
content = content.replace('Detail CC', 'Detail GRN')
content = content.replace('CC / BAST Amount', 'GRN Amount')
content = content.replace(':cc="documentDetail"', ':grn="documentDetail"')
content = content.replace("const filters = { document_code: 'CC' }", "const filters = { document_code: 'GRN' }")
content = content.replace('/purchase/completion-certificates//', '/purchase/good-receipt-notes//')
content = content.replace("requestStore.fetchSignatures('CC'", "requestStore.fetchSignatures('GRN'")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('Replaced successfully')
