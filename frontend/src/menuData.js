export const menuData = {
  commercial: [
    { name: 'Customers', url: '/commercial/customers' },
    {
      name: 'Work Order', url: '', children: [
        { name: 'Work Order', url: '' },
        { name: 'Work Order Inbox', url: '' },
      ]
    },
    { name: 'Region', url: '' },
    { name: 'Province', url: '' },
    { name: 'Area', url: '' },
    { name: 'List of Projects', url: '' },
    { name: 'Review Contract', url: '' },
    { name: 'Submit ESR Document', url: '' },
    { name: 'Submit RFI Document', url: '' },
    { name: 'Submit BAUF BAPS BAK RE', url: '' },
    { name: 'Site Monitoring', url: '' },
    { name: 'Print Document', url: '' },
    {
      name: 'Commercial Report', url: '', children: [
        { name: 'Summary of Tower', url: '' },
        { name: 'List Of Tower', url: '' },
        { name: 'Summary of Commercial', url: '' },
      ]
    },
    {
      name: 'Sales Report', url: '', children: [
        { name: 'Sales Order Report', url: '' },
        { name: 'Customer Sales Report', url: '' },
        { name: 'Item Sales Report', url: '' },
        { name: 'Link Account Report', url: '' },
        { name: 'Sales Return Report', url: '' },
        { name: 'Customers Transaction Report', url: '' },
        { name: 'Item Transaction Report', url: '' },
        { name: 'Sales Document Flow', url: '' },
        { name: 'Customer Rank Report', url: '' },
        { name: 'Sales Contract Report', url: '' },
        { name: 'Sales Contract Balance', url: '' },
        { name: 'Sales Invoice Schedule Report', url: '' },
        { name: 'Credit Limit Usage', url: '' },
        { name: 'Company Sales', url: '' },
      ]
    },
  ],

  gl: [
    { name: 'Chart of Accounts', url: '/gl/chart-of-accounts' },
    { name: 'Cost Center', url: '' },
    {
      name: 'Budget', url: '', children: [
        { name: 'Set COA Budget', url: '' },
        { name: 'Set CC-PC Budget', url: '' },
        { name: 'Set Activity Budget', url: '' },
        { name: 'Set Project Budget', url: '' },
        { name: 'Set Matrix Budget', url: '' },
      ]
    },
    { name: 'Profit Center', url: '' },
    {
      name: 'General Journal', url: '', children: [
        { name: 'General Journal Template', url: '' },
        { name: 'General Journal', url: '' },
        { name: 'General Journal Transaction', url: '/gl/general-journal-transaction' },
        { name: 'General Journal Inbox', url: '/gl/general-journal-inbox' },
      ]
    },
    { name: 'Job List', url: '' },
    { name: 'Reversable Journal', url: '' },
    { name: 'Budget Entry', url: '' },
    { name: 'Audit Trail', url: '' },
    { name: 'Defferal Journal', url: '' },
    { name: 'Amortization Journal', url: '' },
    {
      name: 'Accrual & Reverse Journal', url: '', children: [
        { name: 'Accrual Journal', url: '' },
        { name: 'Accrual Journal Inbox', url: '' },
        { name: 'Reverse Journal', url: '' },
        { name: 'Reverse Journal Inbox', url: '' },
      ]
    },
    { name: 'Reversable Journals', url: '' },
    { name: 'Journal Verification', url: '' },
    { name: 'Transaction Journal', url: '' },
    {
      name: 'Report', url: '', children: [
        { name: 'Accrual Journal Report', url: '' },
        { name: 'Reverse Journal Report', url: '' },
        { name: 'Balance Sheet', url: '' },
        { name: 'Profit & Loss', url: '' },
        { name: 'Profit Loss by Cost Center', url: '' },
        { name: 'Chart of Account Report', url: '' },
        { name: 'Trial Balance', url: '' },
        { name: 'Tax Code', url: '' },
        { name: 'General Ledger', url: '' },
        { name: 'General Ledger Project Cost Center', url: '' },
        { name: 'Job Activity', url: '' },
        { name: 'Job List', url: '' },
        { name: 'Job Profit & Loss', url: '' },
        { name: 'Budget VS Actual', url: '' },
        { name: 'Cost Center Report', url: '' },
        { name: 'Inter Company Transaction Report', url: '' },
        { name: 'COGS Report', url: '' },
        { name: 'List Of Sales', url: '' },
        { name: 'List Of Credit', url: '' },
        { name: 'Rental Calculation', url: '' },
        { name: 'Amortization Journal', url: '' },
      ]
    },
    {
      name: 'Multi Company Report', url: '', children: [
        { name: 'Balance Sheet', url: '' },
        { name: 'Profit & Loss', url: '' },
        { name: 'Chart of Accounts', url: '' },
        { name: 'Trial Balance', url: '' },
      ]
    },
  ],

  ar: [
    { name: 'Debtor Enquiry', url: '' },
    { name: 'List of Outstanding Receivables', url: '' },
    { name: 'Refunds', url: '' },
    { name: 'Tax Form', url: '' },
    { name: 'Customer Payments', url: '' },
    { name: 'PPh 23 Receipt List', url: '' },
    { name: 'Invoice Book', url: '' },
    { name: 'SPT', url: '' },
    {
      name: 'Debit Notes', url: '', children: [
        { name: 'Debit Notes', url: '' },
        { name: 'Debit Notes Inbox', url: '' },
      ]
    },
    {
      name: 'Credit Notes', url: '', children: [
        { name: 'Credit Notes', url: '' },
        { name: 'Credit Notes Inbox', url: '' },
      ]
    },
    { name: 'Transaction Journal', url: '' },
    {
      name: 'Report', url: '', children: [
        { name: 'AR', url: '' },
        { name: 'Account Receivable Card', url: '' },
        { name: 'Aged Receivables', url: '' },
        { name: 'Sales Invoice', url: '' },
        { name: 'Debtors Ledger', url: '' },
        { name: 'Customer Payment Report', url: '' },
        { name: 'Outstanding Debtors', url: '' },
        { name: 'Urn Receivables', url: '' },
        { name: 'AccountReceivableDetail', url: '' },
        { name: 'ARByCustomer', url: '' },
        { name: 'Debit Credit Notes Report', url: '' },
        { name: 'VAT', url: '' },
        { name: 'PPN Attachment', url: '' },
        { name: 'Tax In Report', url: '' },
        { name: 'Tax Out Report', url: '' },
      ]
    },
  ],

  sales: [
    { name: 'Customer Category', url: '' },
    { name: 'Customers Group', url: '' },
    { name: 'Customers', url: '/sales/customers' },
    {
      name: 'Introduction Letter', url: '', children: [
        { name: 'Introduction Letter', url: '' },
        { name: 'Introduction Letter Inbox', url: '' },
      ]
    },
    { name: 'Customer RFQ', url: '' },
    {
      name: 'Job Costing Sheet', url: '', children: [
        { name: 'Job Costing Sheet', url: '' },
        { name: 'Job Costing Sheet Inbox', url: '' },
      ]
    },
    {
      name: 'Quotation', url: '', children: [
        { name: 'Quotation', url: '' },
        { name: 'Quotation Inbox', url: '' },
      ]
    },
    {
      name: 'Sales Contract', url: '', children: [
        { name: 'Sales Contract', url: '' },
        { name: 'Sales Contract Inbox', url: '' },
      ]
    },
    {
      name: 'Proforma Invoice', url: '', children: [
        { name: 'Proforma Invoice', url: '' },
        { name: 'Proforma Invoice Inbox', url: '' },
      ]
    },
    {
      name: 'Work Order', url: '', children: [
        { name: 'Work Order', url: '' },
        { name: 'Work Order Inbox', url: '' },
        { name: 'Inter Company Sales', url: '' },
        { name: 'Retail Sales', url: '' },
        { name: 'Invoice', url: '' },
      ]
    },
    { name: 'Sales Invoice', url: '' },
    { name: 'Sales Invoice Schedule', url: '' },
    { name: 'Void Invoice', url: '' },
    { name: 'Inter Company Invoice', url: '' },
    {
      name: 'Sales Return', url: '', children: [
        { name: 'Sales Return', url: '' },
        { name: 'Sales Return Inbox', url: '' },
        { name: 'Retail Sales Return', url: '' },
      ]
    },
    {
      name: 'Commission', url: '', children: [
        { name: 'Commission', url: '' },
        { name: 'Commission Inbox', url: '' },
      ]
    },
    {
      name: 'Consignment Sales', url: '', children: [
        {
          name: 'Consignment Sales Order', url: '', children: [
            { name: 'Consignment Sales Order', url: '' },
            { name: 'Consignment Sales Order Inbox', url: '' },
          ]
        },
        {
          name: 'Consignment Item Transfer', url: '', children: [
            { name: 'Consignment Item Transfer', url: '' },
            { name: 'Consignment Item Transfer Inbox', url: '' },
          ]
        },
        { name: 'Consignment Report Entry', url: '' },
        { name: 'Consignment Sales Invoice', url: '' },
      ]
    },
    {
      name: 'Sales Forecast', url: '', children: [
        { name: 'Sales Forecast', url: '' },
        { name: 'Sales Forecast Inbox', url: '' },
      ]
    },
    { name: 'Customer Discount', url: '' },
    { name: 'Sales Price Group', url: '' },
    { name: 'Free Of Charge', url: '' },
    { name: 'Print Invoice', url: '' },
    { name: 'Sales Person', url: '' },
    { name: 'Transaction Journal', url: '' },
    {
      name: 'Sales Report', url: '', children: [
        { name: 'Sales Order Report', url: '' },
        { name: 'Customer Sales Report', url: '' },
        { name: 'Item Sales Report', url: '' },
        { name: 'Link Account Report', url: '' },
        { name: 'Commission Report', url: '' },
        { name: 'Sales Return Report', url: '' },
        { name: 'Free Of Charge Report', url: '' },
        { name: 'Customers Transaction Report', url: '' },
        { name: 'Custom Report', url: '' },
        { name: 'Item Transaction Report', url: '' },
        { name: 'Sales Quantity Analysis', url: '' },
        { name: 'Sales Document Flow', url: '' },
        { name: 'Customer Rank Report', url: '' },
        { name: 'SO Document', url: '' },
        { name: 'Sales Contract Report', url: '' },
        { name: 'Project Profit Loss Report', url: '' },
        { name: 'Sales Contract Balance', url: '' },
        { name: 'Sales Invoice Schedule Report', url: '' },
        { name: 'Credit Limit Usage', url: '' },
        { name: 'Company Sales', url: '' },
      ]
    },
  ],

  ap: [
    { name: 'Creditor Enquiry', url: '' },
    { name: 'List of Outstanding Payables', url: '' },
    {
      name: 'Debit Notes', url: '', children: [
        { name: 'Debit Notes', url: '' },
        { name: 'Debit Notes Inbox', url: '' },
      ]
    },
    { name: 'Vendor Payment', url: '' },
    {
      name: 'Credit Notes', url: '', children: [
        { name: 'Credit Notes', url: '' },
        { name: 'Credit Notes Inbox', url: '' },
      ]
    },
    { name: 'Tax Minus Summary', url: '' },
    { name: 'Transaction Journal', url: '' },
    {
      name: 'Report', url: '', children: [
        { name: 'Account Payable', url: '' },
        { name: 'Account Payable Card', url: '' },
        { name: 'Aged Payables', url: '' },
        { name: 'Vendor Invoice', url: '' },
        { name: 'Creditors Ledger', url: '' },
        { name: 'Vendor Payment Report', url: '' },
        { name: 'Debit Credit Notes Report', url: '' },
        { name: 'Invoice Payment', url: '' },
        { name: 'Tax In Report', url: '' },
      ]
    },
  ],

  purchases: [
    { name: 'Vendor Category', url: '/purchases/vendor-category' },
    { name: 'Vendor Group', url: '/purchases/vendor-group' },
    { name: 'Vendor', url: '/purchases/vendor' },
    { name: 'Term And Condition', url: '' },
    { name: 'Price List', url: '' },
    {
      name: 'Purchase Requisition', url: '', children: [
        { name: 'Purchase Requisition', url: '' },
        { name: 'Purchase Requisition Inbox', url: '' },
      ]
    },
    {
      name: 'Purchase RFQ', url: '', children: [
        { name: 'Purchase RFQ', url: '' },
        { name: 'RFQ Inbox', url: '' },
      ]
    },
    { name: 'Vendor Quotation', url: '' },
    {
      name: 'Purchase Order', url: '', children: [
        { name: 'Purchase Order Template', url: '' },
        { name: 'Purchase Order', url: '' },
        { name: 'Purchase Order Inbox', url: '' },
      ]
    },
    {
      name: 'Delivery Receipt', url: '', children: [
        { name: 'Delivery Receipt', url: '' },
        { name: 'Delivery Receipt Inbox', url: '' },
      ]
    },
    {
      name: 'Good Receipt Note', url: '', children: [
        { name: 'Good Receipt Note', url: '/purchases/good-receipt-note' },
        { name: 'Purchase Invoice', url: '/purchases/purchase-invoice' },
        { name: 'Good Receipt Note Inbox', url: '' },
        { name: 'GRN-SES Document', url: '/purchases/grnses-document' },
      ]
    },
    { name: 'Purchase Receipt', url: '' },
    { name: 'Purchase Invoice', url: '' },
    { name: 'Void Invoice', url: '' },
    {
      name: 'Vendor Evaluation', url: '', children: [
        { name: 'Vendor Evaluation', url: '' },
        { name: 'Vendor Evaluation Inbox', url: '' },
      ]
    },
    {
      name: 'Completion Certificate', url: '', children: [
        { name: 'Completion Certificate', url: '' },
        { name: 'Completion Certificate Inbox', url: '' },
      ]
    },
    {
      name: 'Purchase Return', url: '', children: [
        { name: 'Purchase Return', url: '' },
        { name: 'Purchase Return Inbox', url: '' },
      ]
    },
    {
      name: 'Purchase Return Requisition', url: '', children: [
        { name: 'Purchase Return Requisition', url: '' },
        { name: 'Purchase Return Requisition Inbox', url: '' },
      ]
    },
    { name: 'Purchase Costing Sheet', url: '' },
    {
      name: 'Letter of Credit', url: '', children: [
        { name: 'Letter of Credit', url: '' },
        { name: 'Letter of Credit Inbox', url: '' },
      ]
    },
    { name: 'Transaction Journal', url: '' },
    {
      name: 'Purchase Report', url: '', children: [
        { name: 'Purchase Order Report', url: '' },
        { name: 'Unmatch Purchase Order', url: '' },
        { name: 'Purchase Costing Sheet Report', url: '' },
        { name: 'Link Account Report', url: '' },
        { name: 'Pending Purchase Order', url: '' },
        { name: 'Price List Comparison', url: '' },
        { name: 'Purchase Payable Report', url: '' },
        { name: 'Credit Agenda', url: '' },
        { name: 'Vendors Transaction Report', url: '' },
        { name: 'Vendor Rank Report', url: '' },
        { name: 'Document Flow Report', url: '' },
        { name: 'List of Purchase Order', url: '' },
        { name: 'List of Purchase Invoice', url: '' },
        { name: 'Outstanding Purchase Order', url: '' },
        { name: 'List of Purchase Requisition', url: '' },
        { name: 'List Of Basic Calculation WHT', url: '' },
        { name: 'GRN-SES Report', url: '' },
        { name: 'Rekap SES GRN', url: '' },
        { name: 'Material Progress Report', url: '' },
      ]
    },
  ],

  finance: [
    { name: 'List of Cash Book Entry', url: '' },
    { name: 'Invoice Payment Selection', url: '' },
    {
      name: 'Payment Request', url: '', children: [
        { name: 'Payment Request', url: '/finance/payment-request' },
        { name: 'Payment Request Inbox', url: '' },
        { name: 'Petty Cash Usage', url: '' },
      ]
    },
    { name: 'Budget Request', url: '' },
    {
      name: 'Cash Book Entry', url: '', children: [
        { name: 'Bank Receipt', url: '' },
        { name: 'Bank Payment', url: '' },
        { name: 'Cash Receipt', url: '' },
        { name: 'Cash Payment', url: '' },
        { name: 'Cash Book Entry Inbox', url: '' },
      ]
    },
    { name: 'Cash Flow Projection', url: '' },
    { name: 'Budget Component', url: '/finance/budget-component' },
    { name: 'Annual Budget', url: '/finance/annual-budget' },
    { name: 'Company Loan Board', url: '' },
    { name: 'Banks', url: '' },
    { name: 'Bank Product', url: '' },
    {
      name: 'Bank Reconciliation', url: '', children: [
        { name: 'Bank Reconciliation', url: '' },
        { name: 'Bank Reconciliation Inbox', url: '' },
      ]
    },
    {
      name: 'Bank Obligation', url: '', children: [
        { name: 'Bank Obligation', url: '' },
        { name: 'Bank Obligation Report', url: '' },
      ]
    },
    { name: 'Cheque', url: '' },
    { name: 'Set Deposit to Income', url: '' },
    {
      name: 'Settlement', url: '', children: [
        { name: 'Settlement', url: '' },
        { name: 'Settlement Inbox', url: '' },
      ]
    },
    { name: 'Company Legality', url: '' },
    {
      name: 'Transaction Journal', url: '', children: [
        { name: 'Receipts Journal', url: '' },
        { name: 'Disbursement Journal', url: '' },
      ]
    },
    {
      name: 'Report', url: '', children: [
        { name: 'Bank Reconciliation Report', url: '' },
        { name: 'Cash Flow', url: '' },
        { name: 'Cash Flow Statement', url: '' },
        { name: 'Cash Flow Report', url: '' },
        { name: 'Recapitulation Cash Flow', url: '' },
        { name: 'Cash Balance Report', url: '' },
        { name: 'Daily Cash Report', url: '' },
        { name: 'Daily Bank Report', url: '' },
        { name: 'Cheque Report', url: '' },
        { name: 'Cash Count Report', url: '' },
        { name: 'Piutang', url: '' },
        { name: 'Hutang', url: '' },
        { name: 'Report Revenue', url: '' },
        { name: 'Bank Product Report', url: '' },
        { name: 'Cash Book Requisition Report', url: '' },
        { name: 'Company Loan Report', url: '' },
        { name: 'Finance Report', url: '' },
        { name: 'Financial Statement Ratio', url: '' },
        { name: 'Customer Deposit History', url: '' },
        { name: 'Payee Advice', url: '' },
        { name: 'List of Payment Request', url: '' },
        { name: 'List of Payment Request Accrual', url: '' },
        { name: 'Finance Control', url: '' },
        { name: 'Cash Book Entry Report', url: '' },
        { name: 'List Cash Book Entry', url: '' },
        { name: 'Tax Out & Tax In Recapitulation', url: '' },
        { name: 'Donation Report', url: '' },
        { name: 'Progress Report', url: '' },
      ]
    },
  ],

  assets: [
    { name: 'Asset Group', url: '' },
    { name: 'Assets', url: '' },
    {
      name: 'Asset New', url: '', children: [
        { name: 'Asset New', url: '' },
        { name: 'Asset New Inbox', url: '' },
      ]
    },
    { name: 'Asset Usage Planning', url: '' },
    {
      name: 'Asset Usage Request', url: '', children: [
        { name: 'Asset Usage Request', url: '' },
        { name: 'Asset Usage Request Inbox', url: '' },
      ]
    },
    { name: 'Asset Usage Metering', url: '' },
    {
      name: 'Asset Maintenance Scheduler', url: '', children: [
        { name: 'Asset Maintenance Scheduler', url: '' },
        { name: 'Asset Maintenance Scheduler Inbox', url: '' },
      ]
    },
    {
      name: 'Asset Maintenance Order', url: '', children: [
        { name: 'Asset Maintenance Order', url: '' },
        { name: 'Asset Maintenance Order Inbox', url: '' },
        { name: 'Asset Maintenance Order Transaction', url: '' },
      ]
    },
    { name: 'Depreciation Run', url: '' },
    {
      name: 'Asset Transactions', url: '', children: [
        { name: 'Asset Transaction', url: '' },
        { name: 'Asset Transaction Inbox', url: '' },
      ]
    },
    { name: 'Void Asset Transaction', url: '' },
    { name: 'Asset Monthly Depreciation', url: '' },
    { name: 'Transaction Journal', url: '' },
    {
      name: 'Report', url: '', children: [
        { name: 'Assets Listed by Location', url: '' },
        { name: 'Assets Listed by Group', url: '' },
        { name: 'Assets Listed by Acquired Date', url: '' },
        { name: 'Assets Listed by Acquired Period', url: '' },
        { name: 'Asset History Report', url: '' },
        { name: 'Asset Depreciation Report', url: '' },
        { name: 'Asset Depreciation History', url: '' },
        { name: 'Out Dated Assets', url: '' },
        { name: 'Asset Maintenance Report', url: '' },
        { name: 'Maintenance Report by Asset', url: '' },
        { name: 'Asset Meter', url: '' },
        { name: 'Capacity VS Planning VS Metering', url: '' },
        { name: 'Asset Usage Request Report', url: '' },
        { name: 'Asset Transaction Report', url: '' },
        { name: 'Spare Part Usage Report', url: '' },
        { name: 'Spare Part Usage Analysis Report', url: '' },
      ]
    },
  ],

  inventory: [
    {
      name: 'Item', url: '', children: [
        { name: 'Item Category', url: '/inventory/item-category' },
        { name: 'List of Items', url: '/inventory/items' },
        { name: 'Item Barcode', url: '' },
        { name: 'Item Label', url: '' },
        { name: 'Matrix Item', url: '' },
        { name: 'Count Item', url: '' },
        { name: 'Customer Item', url: '' },
        { name: 'Vendor Item', url: '' },
        { name: 'Reserve Item', url: '' },
        { name: 'Reserve Item By Document', url: '' },
        { name: 'Release Reserved Item', url: '' },
      ]
    },
    {
      name: 'Pricing', url: '', children: [
        { name: 'Price List', url: '' },
        {
          name: 'Customer Pricing', url: '', children: [
            { name: 'Customer Pricing Request', url: '' },
            { name: 'Customer Pricing Inbox', url: '' },
          ]
        },
        { name: 'Customer Price List', url: '' },
        {
          name: 'Vendor Pricing', url: '', children: [
            { name: 'Vendor Pricing Request', url: '' },
            { name: 'Vendor Pricing Inbox', url: '' },
          ]
        },
        { name: 'Vendor Price List', url: '' },
        { name: 'Event Pricing and Discount', url: '' },
      ]
    },
    { name: 'Set Minimum Stock', url: '' },
    { name: 'Set Item Price', url: '' },
    { name: 'CoGS History', url: '' },
    {
      name: 'Inventory Adjustment', url: '', children: [
        { name: 'Inventory Adjustment', url: '' },
        { name: 'Inventory Adjustment Inbox', url: '' },
      ]
    },
    {
      name: 'Warehouse Management', url: '', children: [
        { name: 'Warehouse Cost', url: '' },
        { name: 'Warehouse Current Usage', url: '' },
      ]
    },
    { name: 'Warehouse Transfer Requisition', url: '' },
    {
      name: 'Warehouse Transfer', url: '', children: [
        { name: 'Warehouse Transfer', url: '' },
        { name: 'Warehouse Transfer Inbox', url: '' },
        { name: 'Warehouse Transfer Acceptance', url: '' },
      ]
    },
    {
      name: 'Receipt Report', url: '', children: [
        { name: 'Receipt Report', url: '/inventory/receipt-report' },
        { name: 'Inter Company Receipt', url: '' },
        { name: 'Receipt Report Inbox', url: '/inventory/receipt-report-inbox' },
      ]
    },
    { name: 'Delivery Order', url: '' },
    { name: 'Trip Plan', url: '' },
    {
      name: 'Shipment Notes', url: '', children: [
        { name: 'Shipment Notes', url: '' },
        { name: 'Shipment Notes Inbox', url: '' },
      ]
    },
    {
      name: 'Internal Request Material', url: '', children: [
        { name: 'Internal Request Material', url: '' },
        { name: 'Internal Request Material Inbox', url: '' },
      ]
    },
    {
      name: 'Item Exchange', url: '', children: [
        { name: 'Item Exchange History', url: '' },
        { name: 'Item Exchange Inbox', url: '' },
      ]
    },
    { name: 'Inter Company Transaction', url: '' },
    { name: 'Lead Time', url: '' },
    { name: 'Serial Number Tracking', url: '' },
    { name: 'Material Requirement Planning', url: '' },
    { name: 'Transaction Journal', url: '' },
    {
      name: 'Report', url: '', children: [
        { name: 'Analyse Inventory', url: '' },
        { name: 'Stock', url: '' },
        { name: 'Stock Position', url: '' },
        { name: 'Stock Card', url: '' },
        { name: 'Stock Balance', url: '' },
        { name: 'Incoming Stock', url: '' },
        { name: 'Outgoing Stock', url: '' },
        { name: 'Available Item', url: '' },
        { name: 'List of Items', url: '' },
        { name: 'List of Items per Warehouse', url: '' },
        { name: 'Item History', url: '' },
        { name: 'List of Receipt Report', url: '' },
        { name: 'List of Shipment Note', url: '' },
        { name: 'Best Seller Item', url: '' },
        { name: 'Slow Moving Item', url: '' },
        { name: 'Expired Item', url: '' },
        { name: 'Lead Time Report', url: '' },
        { name: 'History Item Price', url: '' },
        { name: 'Pricing History Report', url: '' },
        { name: 'Pricing Compare Report', url: '' },
        { name: 'Borrow Vs Return Item', url: '' },
        { name: 'Trip Plan Report', url: '' },
        { name: 'Link Account Report', url: '' },
        { name: 'SN Report Based On User', url: '' },
        { name: 'Outstanding SN Report', url: '' },
        { name: 'Holding Report', url: '' },
        { name: 'ROQ', url: '' },
        { name: 'Warehouse Report', url: '' },
        { name: 'Virtual Warehouse', url: '' },
      ]
    },
  ],

  projects: [
    { name: 'Region', url: '' },
    { name: 'Area', url: '' },
    { name: 'Tower Type', url: '' },
    { name: 'Project Template', url: '' },
    { name: 'List of Projects', url: '' },
    { name: 'Project Cost Calculation', url: '' },
    { name: 'Project Activity Detail', url: '' },
    { name: 'Project Cost Allocation', url: '' },
    {
      name: 'RAP', url: '', children: [
        { name: 'RAP Type', url: '' },
        { name: 'RAP', url: '' },
        { name: 'RAP Inbox', url: '' },
      ]
    },
    {
      name: 'Sales Order Project', url: '', children: [
        { name: 'Sales Order Project', url: '' },
        { name: 'Sales Order Project Inbox', url: '' },
      ]
    },
    {
      name: 'Material Requisition', url: '', children: [
        { name: 'Material Requisition', url: '' },
        { name: 'Material Requisition Inbox', url: '' },
        { name: 'Material Requisition Delivery', url: '' },
      ]
    },
    {
      name: 'Material Return Project', url: '', children: [
        { name: 'Material Return Project', url: '' },
        { name: 'Material Return Project Inbox', url: '' },
      ]
    },
    {
      name: 'Shipment Notes Project', url: '', children: [
        { name: 'Shipment Notes Project', url: '' },
        { name: 'Shipment Notes Project Inbox', url: '' },
      ]
    },
    {
      name: 'Project Activity Completion', url: '', children: [
        { name: 'Project Activity Completion', url: '' },
        { name: 'Project Activity Completion Inbox', url: '' },
      ]
    },
    { name: 'Project Invoice', url: '' },
    { name: 'Void Invoice', url: '' },
    { name: 'Transaction Journal', url: '' },
    {
      name: 'Report', url: '', children: [
        { name: 'Project Material Usage Report', url: '' },
        { name: 'Project Activity', url: '' },
        { name: 'Project List', url: '' },
        { name: 'Project Profit Loss', url: '' },
        { name: 'Project Profit Loss Per AO', url: '' },
        { name: 'Project Profit Loss Per Customer', url: '' },
        { name: 'Project Profit Loss Per COA', url: '' },
        { name: 'Project Activity Detail', url: '' },
        { name: 'Report Detail COA Per Project', url: '' },
        { name: 'Project Journal Report', url: '' },
        { name: 'Shopping Budget Planning', url: '' },
        { name: 'Project Performance Report', url: '' },
        { name: 'Project Progress Report', url: '' },
        { name: 'Report Summary of Tower', url: '' },
        { name: 'Report List of Tower', url: '' },
        { name: 'Project Capitalize Report', url: '' },
      ]
    },
  ],

  settings: [
    {
      name: 'Document Setting', url: '', children: [
        { name: 'Item Inspection Template', url: '' },
        { name: 'Request Approval Setting', url: '/settings/request-approval-setting' },
        { name: 'Document Pattern', url: '' },
        { name: 'Letter Template', url: '' },
        { name: 'Close Open Document', url: '' },
      ]
    },
    {
      name: 'Tax', url: '', children: [
        { name: 'Tax Code', url: '' },
        { name: 'Tax Converter', url: '' },
      ]
    },
    {
      name: 'Accounting Setting', url: '', children: [
        { name: 'Linked Accounts', url: '' },
        { name: 'Link Account Template', url: '' },
        { name: 'Link Account Board', url: '' },
        {
          name: 'Closing', url: '', children: [
            { name: 'Closing Module', url: '' },
            { name: 'Closing Balance', url: '' },
            { name: 'Start New Financial Year Balance', url: '' },
            { name: 'Closing Adjustment Period', url: '' },
          ]
        },
        {
          name: 'Financial Period Open Close', url: '', children: [
            { name: 'Accounting Period', url: '/settings/accounting-period' },
            { name: 'Annual Accounting Period', url: '/settings/annual-period' },
            { name: 'Quarter Accounting Period', url: '/settings/quarter-period' },
            { name: 'Monthly Accounting Period', url: '/settings/monthly-period' },
            { name: 'Period Activity Log', url: '/settings/period-activity-log' },
          ]
        },
        { name: 'Consolidation Worksheet', url: '' },
        {
          name: 'Account Match', url: '', children: [
            { name: 'Match Template', url: '' },
            { name: 'Account Match', url: '' },
          ]
        },
        { name: 'COA Segmentation', url: '' },
        { name: 'Terms', url: '' },
        { name: 'Terms Of Payment', url: '' },
        { name: 'Payment Schedule', url: '' },
        { name: 'Currency Converter', url: '' },
        { name: 'Inter Company', url: '' },
        { name: 'Consolidation Report', url: '' },
        { name: 'Extra Cost', url: '' },
        { name: 'Financial Ratio Setting', url: '' },
        { name: 'Manage Verification', url: '' },
        { name: 'Verification Approval', url: '' },
      ]
    },
    {
      name: 'Budget Setting', url: '', children: [
        { name: 'Budget Version', url: '' },
        { name: 'Budget Period', url: '' },
        { name: 'Budget Module', url: '' },
        { name: 'Budget Global Setting', url: '' },
      ]
    },
    {
      name: 'Organizational Structure', url: '/settings/organizational-level', children: [
        { name: 'Organizational Level', url: '' },
        { name: 'Company Information', url: '/settings/company-information' },
        { name: 'Position', url: '' },
        { name: 'Employee Data', url: '/settings/employee-data' },
        { name: 'Company Share Setting', url: '' },
        { name: 'Career History', url: '' },
        { name: 'Master Payment To', url: '/settings/payment-to' },
        { name: 'ISO Document', url: '' },
      ]
    },
    {
      name: 'Function Authorization', url: '', children: [
        { name: 'User Group Data', url: '' },
        { name: 'User Member', url: '' },
        { name: 'User Authorization Group', url: '' },
      ]
    },
    {
      name: 'System Setting', url: '', children: [
        { name: 'Global Setting', url: '' },
        { name: 'Application Parameter', url: '' },
        { name: 'Master Type', url: '/settings/master-type' },
        { name: 'Dashboard Setting', url: '' },
        { name: 'B2B Setting', url: '' },
        { name: 'Business Type Setting', url: '' },
        { name: 'Personal Preference', url: '' },
        { name: 'Multi Language Text', url: '' },
        { name: 'Notification Management', url: '' },
        {
          name: 'Licensing', url: '', children: [
            { name: 'License Agreement', url: '' },
            { name: 'Update License', url: '' },
          ]
        },
      ]
    },
    {
      name: 'Inventory', url: '', children: [
        { name: 'Unit Measurement Group', url: '' },
        { name: 'Unit Measurement', url: '/inventory/unit-measurement' },
        { name: 'Unit Measurement Converter', url: '' },
        { name: 'Linked Account Alias', url: '' },
        { name: 'Master Color', url: '' },
        { name: 'Master Size', url: '' },
        { name: 'Master Configuration', url: '' },
        { name: 'Master Dimension', url: '' },
        { name: 'Item Dimension Setting', url: '' },
      ]
    },
    {
      name: 'Production', url: '', children: [
        { name: 'Machine Type', url: '' },
        { name: 'Master Machine', url: '' },
        { name: 'Master Factory Labour', url: '' },
        { name: 'Master Workgroup', url: '' },
        { name: 'Master Section', url: '' },
        { name: 'Master Division', url: '' },
        { name: 'Standard Cost Setting', url: '' },
        { name: 'Standard Cost', url: '' },
        { name: 'Section QC', url: '' },
        { name: 'Holiday Setting', url: '' },
        { name: 'Visual Factory', url: '' },
        { name: 'Machine Usage Template', url: '' },
        { name: 'Waste Dump Location', url: '' },
        { name: 'Item Waste Transform Matrix', url: '' },
        { name: 'Sales Forecast Setting', url: '' },
      ]
    },
    {
      name: 'Project Settings', url: '', children: [
        { name: 'Project Resource', url: '' },
        { name: 'Project Activity', url: '' },
        { name: 'Project Stage', url: '' },
        { name: 'Payment Terms', url: '' },
        { name: 'Project Component', url: '' },
        { name: 'Project Category', url: '/settings/project-category' },
      ]
    },
    {
      name: 'Maintenance - Fixed Assets', url: '', children: [
        { name: 'Asset Usage Period', url: '' },
        { name: 'Maintenance Periode', url: '' },
        { name: 'Maintenance Category', url: '' },
        { name: 'Maintenance Type', url: '' },
      ]
    },
    {
      name: 'Shipping', url: '', children: [
        { name: 'Vehicle Setting', url: '' },
        { name: 'Area Setting', url: '' },
        { name: 'Driver Setting', url: '' },
        { name: 'Carrier Setting', url: '' },
        { name: 'Region Setting', url: '' },
      ]
    },
    {
      name: 'CRM', url: '', children: [
        { name: 'Sales Stage', url: '' },
        { name: 'Activity Type', url: '' },
        { name: 'Activity Status', url: '' },
        { name: 'Activity Priority', url: '' },
        { name: 'Activity Color Legend', url: '' },
        { name: 'CRM Settings', url: '' },
        { name: 'Sales Period', url: '' },
        { name: 'Commission Category', url: '' },
        { name: 'Complain Category', url: '' },
      ]
    },
    {
      name: 'Purchase Settings', url: '', children: [
        { name: 'LC-Purchasing Step', url: '' },
        { name: 'LC-Document Checklist', url: '' },
        { name: 'Vendor Evaluation', url: '' },
        { name: 'PO Approval Setting', url: '' },
      ]
    },
    {
      name: 'QC', url: '', children: [
        { name: 'Score Mask', url: '' },
        { name: 'Parameter', url: '' },
      ]
    },
    {
      name: 'Warehouse', url: '', children: [
        { name: 'Warehouse Capacity', url: '' },
        { name: 'Warehouse Cost Component', url: '' },
      ]
    },
    {
      name: 'Data Migration', url: '', children: [
        { name: 'Send Data', url: '' },
        { name: 'Receive & Process Data', url: '' },
        { name: 'Log Migration Report', url: '' },
        { name: 'Data Migration Setting', url: '' },
        { name: 'Transaction Data Upload', url: '' },
      ]
    },
    {
      name: 'Tools', url: '', children: [
        { name: 'Data Checking', url: '' },
        { name: 'Bugs Report', url: '' },
        { name: 'Recount', url: '' },
      ]
    },
    { name: 'Product Type', url: '' },
    { name: 'Material Category', url: '' },
    { name: 'Price Category', url: '' },
    { name: 'Payment Method', url: '' },
    { name: 'Sales Target', url: '' },
    { name: 'Leather Type', url: '' },
    { name: 'Item Option', url: '' },
  ],
}