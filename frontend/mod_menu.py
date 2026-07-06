import os

path = 'src/menuData.js'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace("{ name: 'Receipt Report', url: '' },", "{ name: 'Receipt Report', url: '/inventory/receipt-report' },")
text = text.replace("{ name: 'Receipt Report Inbox', url: '' },", "{ name: 'Receipt Report Inbox', url: '/inventory/receipt-report-inbox' },")

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
