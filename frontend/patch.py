import re

with open('c:/Traine/bfs-erp/frontend/src/menuData.js', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    \"{ name: 'Good Receipt Note', url: '/purchases/good-receipt-note' },\",
    \"{ name: 'Good Receipt Note', url: '/purchases/good-receipt-note' },\\n      { name: 'GRN Inbox', url: '/purchases/grn-inbox' },\"
)

with open('c:/Traine/bfs-erp/frontend/src/menuData.js', 'w', encoding='utf-8') as f:
    f.write(content)
print('Patched menuData')
