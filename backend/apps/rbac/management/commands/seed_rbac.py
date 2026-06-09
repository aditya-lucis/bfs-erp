import re
from django.core.management.base import BaseCommand
from apps.rbac.models import Module, Function, AuthorizationGroup


# ─── Helper ──────────────────────────────────────────────────────────────────

def slugify_code(module_code: str, name: str) -> str:
    """
    Bikin function code dari nama menu.
    Contoh: ('gl', 'Chart of Accounts') → 'GL-CHART-OF-ACCOUNTS'
    """
    clean = re.sub(r'[^a-zA-Z0-9\s]', '', name)
    slug  = re.sub(r'\s+', '-', clean.strip()).upper()
    return f"{module_code.upper()}-{slug}"


# ─── Menu Data (dari menuData.js lo) ─────────────────────────────────────────

MENU_DATA = {
    'commercial': {
        'name': 'Commercial', 'order': 1,
        'items': [
            {'name': 'Customers'},
            {'name': 'Work Order', 'children': [
                {'name': 'Work Order'},
                {'name': 'Work Order Inbox'},
            ]},
            {'name': 'Region'},
            {'name': 'Province'},
            {'name': 'Area'},
            {'name': 'List of Projects'},
            {'name': 'Review Contract'},
            {'name': 'Submit ESR Document'},
            {'name': 'Submit RFI Document'},
            {'name': 'Submit BAUF BAPS BAK RE'},
            {'name': 'Site Monitoring'},
            {'name': 'Print Document'},
            {'name': 'Sales Report', 'children': [
                {'name': 'Sales Order Report'},
                {'name': 'Customer Sales Report'},
                {'name': 'Item Sales Report'},
                {'name': 'Link Account Report'},
                {'name': 'Sales Return Report'},
                {'name': 'Customers Transaction Report'},
                {'name': 'Item Transaction Report'},
                {'name': 'Sales Document Flow'},
                {'name': 'Customer Rank Report'},
                {'name': 'Sales Contract Report'},
                {'name': 'Sales Contract Balance'},
                {'name': 'Sales Invoice Schedule Report'},
                {'name': 'Credit Limit Usage'},
                {'name': 'Company Sales'},
            ]},
        ],
    },

    'gl': {
        'name': 'General Ledger', 'order': 2,
        'items': [
            {'name': 'Chart of Accounts'},
            {'name': 'Cost Center'},
            {'name': 'Budget', 'children': [
                {'name': 'Set COA Budget'},
                {'name': 'Set CC-PC Budget'},
                {'name': 'Set Activity Budget'},
                {'name': 'Set Project Budget'},
                {'name': 'Set Matrix Budget'},
            ]},
            {'name': 'Profit Center'},
            {'name': 'General Journal', 'children': [
                {'name': 'General Journal Template'},
                {'name': 'General Journal'},
                {'name': 'General Journal Transaction'},
                {'name': 'General Journal Inbox'},
            ]},
            {'name': 'Job List'},
            {'name': 'Reversable Journal'},
            {'name': 'Budget Entry'},
            {'name': 'Audit Trail'},
            {'name': 'Defferal Journal'},
            {'name': 'Amortization Journal'},
            {'name': 'Accrual & Reverse Journal', 'children': [
                {'name': 'Accrual Journal'},
                {'name': 'Accrual Journal Inbox'},
                {'name': 'Reverse Journal'},
                {'name': 'Reverse Journal Inbox'},
            ]},
            {'name': 'Reversable Journals'},
            {'name': 'Journal Verification'},
            {'name': 'Transaction Journal'},
            {'name': 'Report', 'children': [
                {'name': 'Accrual Journal Report'},
                {'name': 'Reverse Journal Report'},
                {'name': 'Balance Sheet'},
                {'name': 'Profit & Loss'},
                {'name': 'Profit Loss by Cost Center'},
                {'name': 'Chart of Account Report'},
                {'name': 'Trial Balance'},
                {'name': 'Tax Code'},
                {'name': 'General Ledger'},
                {'name': 'General Ledger Project Cost Center'},
                {'name': 'Job Activity'},
                {'name': 'Job List'},
                {'name': 'Job Profit & Loss'},
                {'name': 'Budget VS Actual'},
                {'name': 'Cost Center Report'},
                {'name': 'Inter Company Transaction Report'},
                {'name': 'COGS Report'},
                {'name': 'List Of Sales'},
                {'name': 'List Of Credit'},
                {'name': 'Rental Calculation'},
                {'name': 'Amortization Journal'},
            ]},
            {'name': 'Multi Company Report', 'children': [
                {'name': 'Balance Sheet'},
                {'name': 'Profit & Loss'},
                {'name': 'Chart of Accounts'},
                {'name': 'Trial Balance'},
            ]},
        ],
    },

    'ar': {
        'name': 'AR', 'order': 3,
        'items': [
            {'name': 'Debtor Enquiry'},
            {'name': 'List of Outstanding Receivables'},
            {'name': 'Refunds'},
            {'name': 'Tax Form'},
            {'name': 'Customer Payments'},
            {'name': 'PPh 23 Receipt List'},
            {'name': 'Invoice Book'},
            {'name': 'SPT'},
            {'name': 'Debit Notes', 'children': [
                {'name': 'Debit Notes'},
                {'name': 'Debit Notes Inbox'},
            ]},
            {'name': 'Credit Notes', 'children': [
                {'name': 'Credit Notes'},
                {'name': 'Credit Notes Inbox'},
            ]},
            {'name': 'Transaction Journal'},
            {'name': 'Report', 'children': [
                {'name': 'AR'},
                {'name': 'Account Receivable Card'},
                {'name': 'Aged Receivables'},
                {'name': 'Sales Invoice'},
                {'name': 'Debtors Ledger'},
                {'name': 'Customer Payment Report'},
                {'name': 'Outstanding Debtors'},
                {'name': 'Urn Receivables'},
                {'name': 'AccountReceivableDetail'},
                {'name': 'ARByCustomer'},
                {'name': 'Debit Credit Notes Report'},
                {'name': 'VAT'},
                {'name': 'PPN Attachment'},
                {'name': 'Tax In Report'},
                {'name': 'Tax Out Report'},
            ]},
        ],
    },

    'sales': {
        'name': 'Sales', 'order': 4,
        'items': [
            {'name': 'Customer Category'},
            {'name': 'Customers Group'},
            {'name': 'Customers'},
            {'name': 'Introduction Letter', 'children': [
                {'name': 'Introduction Letter'},
                {'name': 'Introduction Letter Inbox'},
            ]},
            {'name': 'Customer RFQ'},
            {'name': 'Job Costing Sheet', 'children': [
                {'name': 'Job Costing Sheet'},
                {'name': 'Job Costing Sheet Inbox'},
            ]},
            {'name': 'Quotation', 'children': [
                {'name': 'Quotation'},
                {'name': 'Quotation Inbox'},
            ]},
            {'name': 'Sales Contract', 'children': [
                {'name': 'Sales Contract'},
                {'name': 'Sales Contract Inbox'},
            ]},
            {'name': 'Proforma Invoice', 'children': [
                {'name': 'Proforma Invoice'},
                {'name': 'Proforma Invoice Inbox'},
            ]},
            {'name': 'Work Order', 'children': [
                {'name': 'Work Order'},
                {'name': 'Work Order Inbox'},
                {'name': 'Inter Company Sales'},
                {'name': 'Retail Sales'},
                {'name': 'Invoice'},
            ]},
            {'name': 'Sales Invoice'},
            {'name': 'Sales Invoice Schedule'},
            {'name': 'Void Invoice'},
            {'name': 'Inter Company Invoice'},
            {'name': 'Sales Return', 'children': [
                {'name': 'Sales Return'},
                {'name': 'Sales Return Inbox'},
                {'name': 'Retail Sales Return'},
            ]},
            {'name': 'Commission', 'children': [
                {'name': 'Commission'},
                {'name': 'Commission Inbox'},
            ]},
            {'name': 'Consignment Sales', 'children': [
                {'name': 'Consignment Sales Order', 'children': [
                    {'name': 'Consignment Sales Order'},
                    {'name': 'Consignment Sales Order Inbox'},
                ]},
                {'name': 'Consignment Item Transfer', 'children': [
                    {'name': 'Consignment Item Transfer'},
                    {'name': 'Consignment Item Transfer Inbox'},
                ]},
                {'name': 'Consignment Report Entry'},
                {'name': 'Consignment Sales Invoice'},
            ]},
            {'name': 'Sales Forecast', 'children': [
                {'name': 'Sales Forecast'},
                {'name': 'Sales Forecast Inbox'},
            ]},
            {'name': 'Customer Discount'},
            {'name': 'Sales Price Group'},
            {'name': 'Free Of Charge'},
            {'name': 'Print Invoice'},
            {'name': 'Sales Person'},
            {'name': 'Transaction Journal'},
            {'name': 'Sales Report', 'children': [
                {'name': 'Sales Order Report'},
                {'name': 'Customer Sales Report'},
                {'name': 'Item Sales Report'},
                {'name': 'Link Account Report'},
                {'name': 'Commission Report'},
                {'name': 'Sales Return Report'},
                {'name': 'Free Of Charge Report'},
                {'name': 'Customers Transaction Report'},
                {'name': 'Custom Report'},
                {'name': 'Item Transaction Report'},
                {'name': 'Sales Quantity Analysis'},
                {'name': 'Sales Document Flow'},
                {'name': 'Customer Rank Report'},
                {'name': 'SO Document'},
                {'name': 'Sales Contract Report'},
                {'name': 'Project Profit Loss Report'},
                {'name': 'Sales Contract Balance'},
                {'name': 'Sales Invoice Schedule Report'},
                {'name': 'Credit Limit Usage'},
                {'name': 'Company Sales'},
            ]},
        ],
    },

    'ap': {
        'name': 'AP', 'order': 5,
        'items': [
            {'name': 'Creditor Enquiry'},
            {'name': 'List of Outstanding Payables'},
            {'name': 'Debit Notes', 'children': [
                {'name': 'Debit Notes'},
                {'name': 'Debit Notes Inbox'},
            ]},
            {'name': 'Vendor Payment'},
            {'name': 'Credit Notes', 'children': [
                {'name': 'Credit Notes'},
                {'name': 'Credit Notes Inbox'},
            ]},
            {'name': 'Tax Minus Summary'},
            {'name': 'Transaction Journal'},
            {'name': 'Report', 'children': [
                {'name': 'Account Payable'},
                {'name': 'Account Payable Card'},
                {'name': 'Aged Payables'},
                {'name': 'Vendor Invoice'},
                {'name': 'Creditors Ledger'},
                {'name': 'Vendor Payment Report'},
                {'name': 'Debit Credit Notes Report'},
                {'name': 'Invoice Payment'},
                {'name': 'Tax In Report'},
            ]},
        ],
    },

    'purchases': {
        'name': 'Purchases', 'order': 6,
        'items': [
            {'name': 'Vendor Category'},
            {'name': 'Vendor Group'},
            {'name': 'Vendor'},
            {'name': 'Term And Condition'},
            {'name': 'Price List'},
            {'name': 'Purchase Requisition', 'children': [
                {'name': 'Purchase Requisition'},
                {'name': 'Purchase Requisition Inbox'},
            ]},
            {'name': 'Purchase RFQ', 'children': [
                {'name': 'Purchase RFQ'},
                {'name': 'RFQ Inbox'},
            ]},
            {'name': 'Vendor Quotation'},
            {'name': 'Purchase Order', 'children': [
                {'name': 'Purchase Order Template'},
                {'name': 'Purchase Order'},
                {'name': 'Purchase Order Inbox'},
            ]},
            {'name': 'Delivery Receipt', 'children': [
                {'name': 'Delivery Receipt'},
                {'name': 'Delivery Receipt Inbox'},
            ]},
            {'name': 'Good Receipt Note', 'children': [
                {'name': 'Good Receipt Note'},
                {'name': 'Good Receipt Note Inbox'},
                {'name': 'GRN-SES Document'},
            ]},
            {'name': 'Purchase Receipt'},
            {'name': 'Purchase Invoice'},
            {'name': 'Void Invoice'},
            {'name': 'Vendor Evaluation', 'children': [
                {'name': 'Vendor Evaluation'},
                {'name': 'Vendor Evaluation Inbox'},
            ]},
            {'name': 'Completion Certificate', 'children': [
                {'name': 'Completion Certificate'},
                {'name': 'Completion Certificate Inbox'},
            ]},
            {'name': 'Purchase Return', 'children': [
                {'name': 'Purchase Return'},
                {'name': 'Purchase Return Inbox'},
            ]},
            {'name': 'Purchase Return Requisition', 'children': [
                {'name': 'Purchase Return Requisition'},
                {'name': 'Purchase Return Requisition Inbox'},
            ]},
            {'name': 'Purchase Costing Sheet'},
            {'name': 'Letter of Credit', 'children': [
                {'name': 'Letter of Credit'},
                {'name': 'Letter of Credit Inbox'},
            ]},
            {'name': 'Transaction Journal'},
            {'name': 'Purchase Report', 'children': [
                {'name': 'Purchase Order Report'},
                {'name': 'Unmatch Purchase Order'},
                {'name': 'Purchase Costing Sheet Report'},
                {'name': 'Link Account Report'},
                {'name': 'Pending Purchase Order'},
                {'name': 'Price List Comparison'},
                {'name': 'Purchase Payable Report'},
                {'name': 'Credit Agenda'},
                {'name': 'Vendors Transaction Report'},
                {'name': 'Vendor Rank Report'},
                {'name': 'Document Flow Report'},
                {'name': 'List of Purchase Order'},
                {'name': 'List of Purchase Invoice'},
                {'name': 'Outstanding Purchase Order'},
                {'name': 'List of Purchase Requisition'},
                {'name': 'List Of Basic Calculation WHT'},
                {'name': 'GRN-SES Report'},
                {'name': 'Rekap SES GRN'},
                {'name': 'Material Progress Report'},
            ]},
        ],
    },

    'finance': {
        'name': 'Finance', 'order': 7,
        'items': [
            {'name': 'List of Cash Book Entry'},
            {'name': 'Invoice Payment Selection'},
            {'name': 'Payment Request', 'children': [
                {'name': 'Payment Request'},
                {'name': 'Payment Request Inbox'},
                {'name': 'Petty Cash Usage'},
            ]},
            {'name': 'Budget Request'},
            {'name': 'Cash Book Entry', 'children': [
                {'name': 'Bank Receipt'},
                {'name': 'Bank Payment'},
                {'name': 'Cash Receipt'},
                {'name': 'Cash Payment'},
                {'name': 'Cash Book Entry Inbox'},
            ]},
            {'name': 'Cash Flow Projection'},
            {'name': 'Budget Component'},
            {'name': 'Annual Budget'},
            {'name': 'Company Loan Board'},
            {'name': 'Banks'},
            {'name': 'Bank Product'},
            {'name': 'Bank Reconciliation', 'children': [
                {'name': 'Bank Reconciliation'},
                {'name': 'Bank Reconciliation Inbox'},
            ]},
            {'name': 'Bank Obligation', 'children': [
                {'name': 'Bank Obligation'},
                {'name': 'Bank Obligation Report'},
            ]},
            {'name': 'Cheque'},
            {'name': 'Set Deposit to Income'},
            {'name': 'Settlement', 'children': [
                {'name': 'Settlement'},
                {'name': 'Settlement Inbox'},
            ]},
            {'name': 'Company Legality'},
            {'name': 'Transaction Journal', 'children': [
                {'name': 'Receipts Journal'},
                {'name': 'Disbursement Journal'},
            ]},
            {'name': 'Report', 'children': [
                {'name': 'Bank Reconciliation Report'},
                {'name': 'Cash Flow'},
                {'name': 'Cash Flow Statement'},
                {'name': 'Cash Flow Report'},
                {'name': 'Recapitulation Cash Flow'},
                {'name': 'Cash Balance Report'},
                {'name': 'Daily Cash Report'},
                {'name': 'Daily Bank Report'},
                {'name': 'Cheque Report'},
                {'name': 'Cash Count Report'},
                {'name': 'Piutang'},
                {'name': 'Hutang'},
                {'name': 'Report Revenue'},
                {'name': 'Bank Product Report'},
                {'name': 'Cash Book Requisition Report'},
                {'name': 'Company Loan Report'},
                {'name': 'Finance Report'},
                {'name': 'Financial Statement Ratio'},
                {'name': 'Customer Deposit History'},
                {'name': 'Payee Advice'},
                {'name': 'List of Payment Request'},
                {'name': 'List of Payment Request Accrual'},
                {'name': 'Finance Control'},
                {'name': 'Cash Book Entry Report'},
                {'name': 'List Cash Book Entry'},
                {'name': 'Tax Out & Tax In Recapitulation'},
                {'name': 'Donation Report'},
                {'name': 'Progress Report'},
            ]},
        ],
    },

    'assets': {
        'name': 'Fixed Assets', 'order': 8,
        'items': [
            {'name': 'Asset Group'},
            {'name': 'Assets'},
            {'name': 'Asset New', 'children': [
                {'name': 'Asset New'},
                {'name': 'Asset New Inbox'},
            ]},
            {'name': 'Asset Usage Planning'},
            {'name': 'Asset Usage Request', 'children': [
                {'name': 'Asset Usage Request'},
                {'name': 'Asset Usage Request Inbox'},
            ]},
            {'name': 'Asset Usage Metering'},
            {'name': 'Asset Maintenance Scheduler', 'children': [
                {'name': 'Asset Maintenance Scheduler'},
                {'name': 'Asset Maintenance Scheduler Inbox'},
            ]},
            {'name': 'Asset Maintenance Order', 'children': [
                {'name': 'Asset Maintenance Order'},
                {'name': 'Asset Maintenance Order Inbox'},
                {'name': 'Asset Maintenance Order Transaction'},
            ]},
            {'name': 'Depreciation Run'},
            {'name': 'Asset Transactions', 'children': [
                {'name': 'Asset Transaction'},
                {'name': 'Asset Transaction Inbox'},
            ]},
            {'name': 'Void Asset Transaction'},
            {'name': 'Asset Monthly Depreciation'},
            {'name': 'Transaction Journal'},
            {'name': 'Report', 'children': [
                {'name': 'Assets Listed by Location'},
                {'name': 'Assets Listed by Group'},
                {'name': 'Assets Listed by Acquired Date'},
                {'name': 'Assets Listed by Acquired Period'},
                {'name': 'Asset History Report'},
                {'name': 'Asset Depreciation Report'},
                {'name': 'Asset Depreciation History'},
                {'name': 'Out Dated Assets'},
                {'name': 'Asset Maintenance Report'},
                {'name': 'Maintenance Report by Asset'},
                {'name': 'Asset Meter'},
                {'name': 'Capacity VS Planning VS Metering'},
                {'name': 'Asset Usage Request Report'},
                {'name': 'Asset Transaction Report'},
                {'name': 'Spare Part Usage Report'},
                {'name': 'Spare Part Usage Analysis Report'},
            ]},
        ],
    },

    'inventory': {
        'name': 'Inventory', 'order': 9,
        'items': [
            {'name': 'Item', 'children': [
                {'name': 'Item Category'},
                {'name': 'List of Items'},
                {'name': 'Item Barcode'},
                {'name': 'Item Label'},
                {'name': 'Matrix Item'},
                {'name': 'Count Item'},
                {'name': 'Customer Item'},
                {'name': 'Vendor Item'},
                {'name': 'Reserve Item'},
                {'name': 'Reserve Item By Document'},
                {'name': 'Release Reserved Item'},
            ]},
            {'name': 'Pricing', 'children': [
                {'name': 'Price List'},
                {'name': 'Customer Pricing', 'children': [
                    {'name': 'Customer Pricing Request'},
                    {'name': 'Customer Pricing Inbox'},
                ]},
                {'name': 'Customer Price List'},
                {'name': 'Vendor Pricing', 'children': [
                    {'name': 'Vendor Pricing Request'},
                    {'name': 'Vendor Pricing Inbox'},
                ]},
                {'name': 'Vendor Price List'},
                {'name': 'Event Pricing and Discount'},
            ]},
            {'name': 'Set Minimum Stock'},
            {'name': 'Set Item Price'},
            {'name': 'CoGS History'},
            {'name': 'Inventory Adjustment', 'children': [
                {'name': 'Inventory Adjustment'},
                {'name': 'Inventory Adjustment Inbox'},
            ]},
            {'name': 'Warehouse Management', 'children': [
                {'name': 'Warehouse Cost'},
                {'name': 'Warehouse Current Usage'},
            ]},
            {'name': 'Warehouse Transfer Requisition'},
            {'name': 'Warehouse Transfer', 'children': [
                {'name': 'Warehouse Transfer'},
                {'name': 'Warehouse Transfer Inbox'},
                {'name': 'Warehouse Transfer Acceptance'},
            ]},
            {'name': 'Receipt Report', 'children': [
                {'name': 'Receipt Report'},
                {'name': 'Inter Company Receipt'},
                {'name': 'Receipt Report Inbox'},
            ]},
            {'name': 'Delivery Order'},
            {'name': 'Trip Plan'},
            {'name': 'Shipment Notes', 'children': [
                {'name': 'Shipment Notes'},
                {'name': 'Shipment Notes Inbox'},
            ]},
            {'name': 'Internal Request Material', 'children': [
                {'name': 'Internal Request Material'},
                {'name': 'Internal Request Material Inbox'},
            ]},
            {'name': 'Item Exchange', 'children': [
                {'name': 'Item Exchange History'},
                {'name': 'Item Exchange Inbox'},
            ]},
            {'name': 'Inter Company Transaction'},
            {'name': 'Lead Time'},
            {'name': 'Serial Number Tracking'},
            {'name': 'Material Requirement Planning'},
            {'name': 'Transaction Journal'},
            {'name': 'Report', 'children': [
                {'name': 'Analyse Inventory'},
                {'name': 'Stock'},
                {'name': 'Stock Position'},
                {'name': 'Stock Card'},
                {'name': 'Stock Balance'},
                {'name': 'Incoming Stock'},
                {'name': 'Outgoing Stock'},
                {'name': 'Available Item'},
                {'name': 'List of Items'},
                {'name': 'List of Items per Warehouse'},
                {'name': 'Item History'},
                {'name': 'List of Receipt Report'},
                {'name': 'List of Shipment Note'},
                {'name': 'Best Seller Item'},
                {'name': 'Slow Moving Item'},
                {'name': 'Expired Item'},
                {'name': 'Lead Time Report'},
                {'name': 'History Item Price'},
                {'name': 'Pricing History Report'},
                {'name': 'Pricing Compare Report'},
                {'name': 'Borrow Vs Return Item'},
                {'name': 'Trip Plan Report'},
                {'name': 'Link Account Report'},
                {'name': 'SN Report Based On User'},
                {'name': 'Outstanding SN Report'},
                {'name': 'Holding Report'},
                {'name': 'ROQ'},
                {'name': 'Warehouse Report'},
                {'name': 'Virtual Warehouse'},
            ]},
        ],
    },

    'projects': {
        'name': 'Projects', 'order': 10,
        'items': [
            {'name': 'Region'},
            {'name': 'Area'},
            {'name': 'Project Template'},
            {'name': 'List of Projects'},
            {'name': 'Project Cost Calculation'},
            {'name': 'Project Activity Detail'},
            {'name': 'Project Cost Allocation'},
            {'name': 'RAP', 'children': [
                {'name': 'RAP Type'},
                {'name': 'RAP'},
                {'name': 'RAP Inbox'},
            ]},
            {'name': 'Sales Order Project', 'children': [
                {'name': 'Sales Order Project'},
                {'name': 'Sales Order Project Inbox'},
            ]},
            {'name': 'Material Requisition', 'children': [
                {'name': 'Material Requisition'},
                {'name': 'Material Requisition Inbox'},
                {'name': 'Material Requisition Delivery'},
            ]},
            {'name': 'Material Return Project', 'children': [
                {'name': 'Material Return Project'},
                {'name': 'Material Return Project Inbox'},
            ]},
            {'name': 'Shipment Notes Project', 'children': [
                {'name': 'Shipment Notes Project'},
                {'name': 'Shipment Notes Project Inbox'},
            ]},
            {'name': 'Project Activity Completion', 'children': [
                {'name': 'Project Activity Completion'},
                {'name': 'Project Activity Completion Inbox'},
            ]},
            {'name': 'Project Invoice'},
            {'name': 'Void Invoice'},
            {'name': 'Transaction Journal'},
            {'name': 'Report', 'children': [
                {'name': 'Project Material Usage Report'},
                {'name': 'Project Activity'},
                {'name': 'Project List'},
                {'name': 'Project Profit Loss'},
                {'name': 'Project Profit Loss Per AO'},
                {'name': 'Project Profit Loss Per Customer'},
                {'name': 'Project Profit Loss Per COA'},
                {'name': 'Project Activity Detail'},
                {'name': 'Report Detail COA Per Project'},
                {'name': 'Project Journal Report'},
                {'name': 'Shopping Budget Planning'},
                {'name': 'Project Performance Report'},
                {'name': 'Project Progress Report'},
                {'name': 'Project Capitalize Report'},
            ]},
        ],
    },

    'settings': {
        'name': 'Setting', 'order': 11,
        'items': [
            {'name': 'Document Setting', 'children': [
                {'name': 'Item Inspection Template'},
                {'name': 'Request Approval Setting'},
                {'name': 'Document Pattern'},
                {'name': 'Letter Template'},
                {'name': 'Close Open Document'},
            ]},
            {'name': 'Tax', 'children': [
                {'name': 'Tax Code'},
                {'name': 'Tax Converter'},
            ]},
            {'name': 'Accounting Setting', 'children': [
                {'name': 'Linked Accounts'},
                {'name': 'Link Account Template'},
                {'name': 'Link Account Board'},
                {'name': 'Closing', 'children': [
                    {'name': 'Closing Module'},
                    {'name': 'Closing Balance'},
                    {'name': 'Start New Financial Year Balance'},
                    {'name': 'Closing Adjustment Period'},
                ]},
                {'name': 'Annual Accounting Period'},
                {'name': 'Quarter Accounting Period'},
                {'name': 'Accounting Period'},
                {'name': 'Consolidation Worksheet'},
                {'name': 'Account Match', 'children': [
                    {'name': 'Match Template'},
                    {'name': 'Account Match'},
                ]},
                {'name': 'COA Segmentation'},
                {'name': 'Terms'},
                {'name': 'Terms Of Payment'},
                {'name': 'Payment Schedule'},
                {'name': 'Currency Converter'},
                {'name': 'Inter Company'},
                {'name': 'Consolidation Report'},
                {'name': 'Extra Cost'},
                {'name': 'Financial Ratio Setting'},
                {'name': 'Manage Verification'},
                {'name': 'Verification Approval'},
            ]},
            {'name': 'Budget Setting', 'children': [
                {'name': 'Budget Version'},
                {'name': 'Budget Period'},
                {'name': 'Budget Module'},
                {'name': 'Budget Global Setting'},
            ]},
            {'name': 'Organizational Structure', 'children': [
                {'name': 'Organizational Level'},
                {'name': 'Company Information'},
                {'name': 'Position'},
                {'name': 'Employee Data'},
                {'name': 'Company Share Setting'},
                {'name': 'Career History'},
                {'name': 'Master Payment To'},
                {'name': 'ISO Document'},
            ]},
            {'name': 'Function Authorization', 'children': [
                {'name': 'User Group Data'},
                {'name': 'User Member'},
                {'name': 'User Authorization Group'},
            ]},
            {'name': 'System Setting', 'children': [
                {'name': 'Global Setting'},
                {'name': 'Application Parameter'},
                {'name': 'Master Type'},
                {'name': 'Dashboard Setting'},
                {'name': 'B2B Setting'},
                {'name': 'Business Type Setting'},
                {'name': 'Personal Preference'},
                {'name': 'Multi Language Text'},
                {'name': 'Notification Management'},
                {'name': 'Licensing', 'children': [
                    {'name': 'License Agreement'},
                    {'name': 'Update License'},
                ]},
            ]},
            {'name': 'Inventory', 'children': [
                {'name': 'Unit Measurement Group'},
                {'name': 'Unit Measurement'},
                {'name': 'Unit Measurement Converter'},
                {'name': 'Linked Account Alias'},
                {'name': 'Master Color'},
                {'name': 'Master Size'},
                {'name': 'Master Configuration'},
                {'name': 'Master Dimension'},
                {'name': 'Item Dimension Setting'},
            ]},
            {'name': 'Production', 'children': [
                {'name': 'Machine Type'},
                {'name': 'Master Machine'},
                {'name': 'Master Factory Labour'},
                {'name': 'Master Workgroup'},
                {'name': 'Master Section'},
                {'name': 'Master Division'},
                {'name': 'Standard Cost Setting'},
                {'name': 'Standard Cost'},
                {'name': 'Section QC'},
                {'name': 'Holiday Setting'},
                {'name': 'Visual Factory'},
                {'name': 'Machine Usage Template'},
                {'name': 'Waste Dump Location'},
                {'name': 'Item Waste Transform Matrix'},
                {'name': 'Sales Forecast Setting'},
            ]},
            {'name': 'Project Settings', 'children': [
                {'name': 'Project Resource'},
                {'name': 'Project Activity'},
                {'name': 'Project Stage'},
                {'name': 'Payment Terms'},
                {'name': 'Project Component'},
                {'name': 'Project Category'},
            ]},
            {'name': 'Maintenance - Fixed Assets', 'children': [
                {'name': 'Asset Usage Period'},
                {'name': 'Maintenance Periode'},
                {'name': 'Maintenance Category'},
                {'name': 'Maintenance Type'},
            ]},
            {'name': 'Shipping', 'children': [
                {'name': 'Vehicle Setting'},
                {'name': 'Area Setting'},
                {'name': 'Driver Setting'},
                {'name': 'Carrier Setting'},
                {'name': 'Region Setting'},
            ]},
            {'name': 'CRM', 'children': [
                {'name': 'Sales Stage'},
                {'name': 'Activity Type'},
                {'name': 'Activity Status'},
                {'name': 'Activity Priority'},
                {'name': 'Activity Color Legend'},
                {'name': 'CRM Settings'},
                {'name': 'Sales Period'},
                {'name': 'Commission Category'},
                {'name': 'Complain Category'},
            ]},
            {'name': 'Purchase Settings', 'children': [
                {'name': 'LC-Purchasing Step'},
                {'name': 'LC-Document Checklist'},
                {'name': 'Vendor Evaluation'},
                {'name': 'PO Approval Setting'},
            ]},
            {'name': 'QC', 'children': [
                {'name': 'Score Mask'},
                {'name': 'Parameter'},
            ]},
            {'name': 'Warehouse', 'children': [
                {'name': 'Warehouse Capacity'},
                {'name': 'Warehouse Cost Component'},
            ]},
            {'name': 'Data Migration', 'children': [
                {'name': 'Send Data'},
                {'name': 'Receive & Process Data'},
                {'name': 'Log Migration Report'},
                {'name': 'Data Migration Setting'},
                {'name': 'Transaction Data Upload'},
            ]},
            {'name': 'Tools', 'children': [
                {'name': 'Data Checking'},
                {'name': 'Bugs Report'},
                {'name': 'Recount'},
            ]},
            {'name': 'Product Type'},
            {'name': 'Material Category'},
            {'name': 'Price Category'},
            {'name': 'Payment Method'},
            {'name': 'Sales Target'},
            {'name': 'Leather Type'},
            {'name': 'Item Option'},
        ],
    },
}

GROUPS = [
    ('ACC-ACCMGR',    'ACCOUNTING MANAGER'),
    ('ACC-ACCSTF1',   'ACCOUNTING STAFF'),
    ('ACC-CC',        'COST CONTROL'),
    ('ADM',           'ADM'),
    ('ADM-SUPPORTIT', 'SUPPORT IT'),
    ('BUDGETING',     'BUDGETING'),
    ('BUSPRODDEV',    'Business Product Development'),
    ('BUSPRODDEVSTF', 'Staff Business Product Development'),
    ('CCICT',         'Cost Control Adm'),
    ('CONS_IMP',      'Construction & Implementation'),
    ('CONS_IMPSTAFF', 'Staff Construction & Implementation'),
    ('DIR-DIR',       'DIRECTOR'),
    ('ENG-ENGMGR',    'ENGINEERING MANAGER'),
    ('ENG-ENGSTF',    'ENGINEERING STAFF'),
]


# apps/rbac/management/commands/seed_rbac.py
# Update url_path untuk function yang sudah ada halaman

URL_MAP = {
    'SETTINGS-COMPANY-INFORMATION':       '/settings/company-information',
    'SETTINGS-ORGANIZATIONAL-STRUCTURE':  '/settings/organizational-level',
    'SETTINGS-USER-AUTHORIZATION-GROUP':  '/settings/user-authorization-group',
    'SETTINGS-EMPLOYEE-DATA':             '/settings/employee-data',
    'GL-CHART-OF-ACCOUNTS':               '/gl/chart-of-accounts',
    'INV-UNIT-MEASUREMENT':               '/inventory/unit-measurement',
    'INV-ITEM-CATEGORY':                  '/inventory/item-category',
    'INV-ITEM':                           '/inventory/items',
    'COMMERCIAL-CUSTOMERS':               '/commercial/customers',
    'SALES-CUSTOMERS':                    '/sales/customers',
    'PURCHASES-VENDOR-CATEGORY':          '/purchases/vendor-category',
    'PURCHASES-VENDOR-GROUP':             '/purchases/vendor-group',
    'PURCHASES-VENDOR':                   '/purchases/vendor',
}

class Command(BaseCommand):
    help = 'Seed Modules, Functions (full menu tree), and Authorization Groups'

    # Track codes yang sudah dipakai untuk hindari duplikat
    _used_codes = set()

    def handle(self, *args, **options):
        self._used_codes = set(
            Function.objects.values_list('code', flat=True)
        )
        total_modules = total_functions = 0

        for mod_key, mod_data in MENU_DATA.items():
            module, _ = Module.objects.update_or_create(
                code=mod_key,
                defaults={
                    'name':      mod_data['name'],
                    'order':     mod_data['order'],
                    'is_active': True,
                },
            )
            total_modules += 1
            count = self._seed_items(
                items=mod_data['items'],
                module=module,
                parent=None,
                order_start=0,
            )
            total_functions += count
            self.stdout.write(f'  📦 {module.name}: {count} functions')

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ {total_modules} modules, {total_functions} functions seeded'
        ))

        self.stdout.write('\n🌱 Seeding Authorization Groups...')
        for gname, gdesc in GROUPS:
            AuthorizationGroup.objects.update_or_create(
                group_name=gname,
                defaults={'description': gdesc, 'status': True},
            )
        self.stdout.write(self.style.SUCCESS(f'✅ {len(GROUPS)} groups seeded'))
        self.stdout.write(self.style.SUCCESS('\n🎉 Done!'))

    def _seed_items(self, items, module, parent, order_start):
        count = 0
        for order, item in enumerate(items, start=order_start):
            code = self._unique_code(module.code, item['name'])
            func, _ = Function.objects.update_or_create(
                code=code,
                defaults={
                    'module':    module,
                    'parent':    parent,
                    'name':      item['name'],
                    'url_path':  URL_MAP.get(code, ''),   # ← pakai URL_MAP
                    'order':     order,
                    'is_active': True,
                },
            )
            count += 1
            if item.get('children'):
                count += self._seed_items(
                    items=item['children'],
                    module=module,
                    parent=func,
                    order_start=0,
                )
        return count

    def _unique_code(self, module_code, name):
        """Generate unique code, append suffix kalau collision."""
        base = slugify_code(module_code, name)
        code = base
        suffix = 2
        while code in self._used_codes:
            code = f"{base}-{suffix}"
            suffix += 1
        self._used_codes.add(code)
        return code