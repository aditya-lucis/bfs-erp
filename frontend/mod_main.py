import os

path = 'src/main.js'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

import_statement = "import ReceiptReportInboxView from './views/inventory/ReceiptReportInboxView.vue'\n"
route_statement = "  { path: '/inventory/receipt-report-inbox', component: ReceiptReportInboxView, meta: { title: 'Receipt Report Inbox', moduleId: 'inventory', moduleName: 'Inventory', layout: 'default' } },\n"

if 'ReceiptReportInboxView.vue' not in text:
    text = text.replace("import ReceiptReportView from './views/inventory/ReceiptReportView.vue'", "import ReceiptReportView from './views/inventory/ReceiptReportView.vue'\n" + import_statement)
    text = text.replace("{ path: '/inventory/receipt-report', component: ReceiptReportView", route_statement + "  { path: '/inventory/receipt-report', component: ReceiptReportView")

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
