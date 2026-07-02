import sys
import os

files = [
    'c:/Traine/bfs-erp/frontend/src/views/purchase/GoodReceiptNoteView.vue',
    'c:/Traine/bfs-erp/frontend/src/components/purchase/GoodReceiptNoteFormModal.vue',
    'c:/Traine/bfs-erp/frontend/src/views/purchase/GRNInboxView.vue'
]

for file_path in files:
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        content = content.replace('sugrness', 'success')
        content = content.replace('agrnpt', 'accept')
        content = content.replace('acgrnss', 'access')
        content = content.replace('occurrgrnce', 'occurrence')
        content = content.replace('agrnss', 'access')
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

print('Typos fixed')
