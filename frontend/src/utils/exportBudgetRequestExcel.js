/**
 * Export Budget Request Data to a Modern, Sleek Excel Spreadsheet (.xls)
 * Includes real-time company profile from store, full column mappings,
 * native numeric formatting, zebra striping, and clean Sub Total & Grand Total rows.
 */

export function exportBudgetRequestExcel(data, filterState = {}, company = null) {
  const now = new Date()
  const exportTimestamp = now.toLocaleDateString('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })

  // Dynamic Company Profile with fallback to PT. Sokka Tama Fiber Dev / PT. BFS ERP
  const compName = company?.company_name || company?.name || 'PT. Sokka Tama Fiber Dev'
  const compAddress = company?.address || company?.company_address || company?.street_address || 'Jl. Kyai Haji Noer Ali no. 3A Inspeksi Kalimalang - Bekasi'
  const compCountry = company?.country || '- Indonesia'
  const compPhone = company?.phone || company?.phone_number ? `Phone : ${company.phone || company.phone_number}` : 'Phone : 62.21.8896 0077(Hunting)'
  const compFax = company?.fax || company?.fax_number ? `Fax : ${company.fax || company.fax_number}` : 'Fax    : 62.21.8896 5147-48'

  // Calculate Sub Totals & Grand Totals
  let totalAmountInDoc = 0
  let totalVat = 0
  let totalWht = 0
  let totalNetAmount = 0
  let totalPaidAmount = 0
  let totalActualPayment = 0
  let totalRemainingUnpaid = 0

  const processedRows = data.map((item, idx) => {
    const amountDoc = parseFloat(item.amount) || 0
    const vat = parseFloat(item.vat || item.tax_amount) || 0
    const discount = parseFloat(item.discount) || 0
    const wht = parseFloat((item.wht_amount || item.budget_request?.wht || '0').toString().replace(/,/g, '')) || 0
    
    // Formula matching BudgetRequestView.vue
    const netAmount = amountDoc + vat - discount - wht
    const paid = parseFloat(item.paid_amount) || 0
    const actualPay = parseFloat((item.actual_payment_amount || 0).toString().replace(/,/g, '')) || 0
    const remaining = netAmount - paid

    totalAmountInDoc += amountDoc
    totalVat += vat
    totalWht += wht
    totalNetAmount += netAmount
    totalPaidAmount += paid
    totalActualPayment += actualPay
    totalRemainingUnpaid += remaining

    return {
      no: idx + 1,
      date: formatDate(item.date || item.created_at),
      paymentRequestNo: item.document_number || item.payment_request_number || item.cbr_no || '-',
      referenceNumber: item.po_number || item.reference_number || item.invoice_number || '-',
      bouwheer: item.vendor_display || item.payment_to_display || item.bouwheer || '-',
      area: item.area || '0',
      site: item.site_name || item.project_display || item.site || '-',
      category: item.transaction_type_display || item.category || item.usage_for || 'Invoice Payment',
      description: item.remarks || item.description || item.remark || '-',
      amountDoc,
      vat,
      wht,
      totalAmount: netAmount,
      termOf: item.term_duration || item.term_of || '30 days',
      remark: item.payment_to_display || item.vendor_display || item.remark || item.remarks || '-',
      pic: item.created_by_name || item.pic || item.vendor_display || '-',
      paidAmount: paid,
      currency: item.currency || 'IDR',
      actualPayment: actualPay,
      remainingUnpaid: remaining,
      dueDate: formatDate(item.due_date),
      comment: item.comment || '-',
      aging: item.aging || '-',
      paidStatus: item.paid_status || item.document_status || 'Not Paid',
      action: item.original_action_status || item.action_status || 'None',
      reason: item.reason || 'None',
      closeDate: formatDate(item.close_date)
    }
  })

  // Styling helpers for Excel HTML cells
  const numStyle = `style="mso-number-format:'\\#\\,\\#\\#0\\.00'; text-align: right; padding: 6px 8px; border: 1px solid #cbd5e1; font-family: 'Segoe UI', Calibri, Arial, sans-serif;"`
  const textStyle = `style="text-align: left; padding: 6px 8px; border: 1px solid #cbd5e1; font-family: 'Segoe UI', Calibri, Arial, sans-serif;"`
  const centerStyle = `style="text-align: center; padding: 6px 8px; border: 1px solid #cbd5e1; font-family: 'Segoe UI', Calibri, Arial, sans-serif;"`

  // 27 Columns matching Legacy ERP Report
  const headers = [
    'No', 'Date', 'Payment Request No', 'Reference Number', 'Bouwheer',
    'Area', 'Site', 'Category', 'Description', 'Amount In Document',
    'VAT', 'WHT', 'Total Amount', 'Term Of', 'Remark',
    'PIC', 'Paid Amount', 'Currency', 'Actual Payment Amount', 'Remaining Unpaid',
    'Due Date', 'Comment', 'Aging', 'Paid Status', 'Action', 'Reason', 'Close Date'
  ]

  const headerHtml = headers.map(th => `
    <th style="background-color: #1d4ed8; color: #ffffff; font-weight: bold; font-size: 10.5pt; text-align: center; padding: 10px 8px; border: 1px solid #1e40af; font-family: 'Segoe UI', Calibri, Arial, sans-serif; height: 32px;">
      ${th}
    </th>
  `).join('')

  // Build Data Rows
  const rowsHtml = processedRows.map((row, idx) => {
    const bg = idx % 2 === 0 ? '#ffffff' : '#f8fafc'
    const statusColor = (row.paidStatus || '').toLowerCase().includes('not') ? '#dc2626' : '#16a34a'

    return `
      <tr style="background-color: ${bg}; font-size: 10pt; height: 26px;">
        <td ${centerStyle}>${row.no}</td>
        <td ${centerStyle}>${row.date}</td>
        <td ${centerStyle} style="font-weight: 600; color: #1e3a8a; border: 1px solid #cbd5e1;">${row.paymentRequestNo}</td>
        <td ${centerStyle}>${row.referenceNumber}</td>
        <td ${textStyle}>${row.bouwheer}</td>
        <td ${centerStyle}>${row.area}</td>
        <td ${textStyle}>${row.site}</td>
        <td ${centerStyle}>${row.category}</td>
        <td ${textStyle}>${row.description}</td>
        <td ${numStyle}>${row.amountDoc}</td>
        <td ${numStyle}>${row.vat}</td>
        <td ${numStyle}>${row.wht}</td>
        <td ${numStyle} style="font-weight: bold; color: #0f172a; border: 1px solid #cbd5e1; background-color: #f1f5f9;">${row.totalAmount}</td>
        <td ${centerStyle}>${row.termOf}</td>
        <td ${textStyle}>${row.remark}</td>
        <td ${textStyle} style="font-weight: 500;">${row.pic}</td>
        <td ${numStyle} style="color: #15803d; font-weight: 600; border: 1px solid #cbd5e1;">${row.paidAmount}</td>
        <td ${centerStyle} style="font-weight: bold;">${row.currency}</td>
        <td ${numStyle} style="background-color: #eff6ff; color: #1e40af; font-weight: bold; border: 1px solid #cbd5e1;">${row.actualPayment}</td>
        <td ${numStyle} style="color: #dc2626; font-weight: bold; border: 1px solid #cbd5e1;">${row.remainingUnpaid}</td>
        <td ${centerStyle}>${row.dueDate}</td>
        <td ${textStyle}>${row.comment}</td>
        <td ${centerStyle}>${row.aging}</td>
        <td ${centerStyle} style="font-weight: bold; color: ${statusColor}; border: 1px solid #cbd5e1;">${row.paidStatus}</td>
        <td ${centerStyle}>${row.action}</td>
        <td ${textStyle}>${row.reason}</td>
        <td ${centerStyle}>${row.closeDate}</td>
      </tr>
    `
  }).join('')

  // Build Sub Total CHEQUE/CASH Row (Soft Yellow/Gold background, clean text)
  const subTotalHtml = `
    <tr style="background-color: #fef9c3; font-weight: bold; font-size: 10.5pt; height: 30px;">
      <td colspan="15" style="border: 1px solid #cbd5e1; text-align: right; color: #854d0e; padding: 6px 12px;">Sub Total CHEQUE/CASH</td>
      <td colspan="2" style="border: 1px solid #cbd5e1;"></td>
      <td style="border: 1px solid #cbd5e1; text-align: center; color: #854d0e;">IDR</td>
      <td style="mso-number-format:'\\#\\,\\#\\#0\\.00'; text-align: right; padding: 6px 8px; border: 1px solid #cbd5e1; color: #854d0e; background-color: #fde047;">${totalActualPayment}</td>
      <td style="mso-number-format:'\\#\\,\\#\\#0\\.00'; text-align: right; padding: 6px 8px; border: 1px solid #cbd5e1; color: #b91c1c;">${totalRemainingUnpaid}</td>
      <td colspan="7" style="border: 1px solid #cbd5e1;"></td>
    </tr>
  `

  // Build GRAND TOTAL Row (Soft Slate Blue background, professional double underline, clean text)
  const grandTotalHtml = `
    <tr style="background-color: #dbeafe; color: #1e3a8a; font-weight: bold; font-size: 11pt; height: 34px;">
      <td colspan="16" style="border-top: 2px solid #3b82f6; border-bottom: 3px double #1d4ed8; border-left: 1px solid #93c5fd; border-right: 1px solid #93c5fd; text-align: right; padding: 8px 12px; letter-spacing: 0.5px;">GRAND TOTAL</td>
      <td style="mso-number-format:'\\#\\,\\#\\#0\\.00'; text-align: right; padding: 8px; border-top: 2px solid #3b82f6; border-bottom: 3px double #1d4ed8; border-left: 1px solid #93c5fd; border-right: 1px solid #93c5fd; color: #15803d;">${totalPaidAmount}</td>
      <td style="border-top: 2px solid #3b82f6; border-bottom: 3px double #1d4ed8; border-left: 1px solid #93c5fd; border-right: 1px solid #93c5fd; text-align: center;">IDR</td>
      <td style="mso-number-format:'\\#\\,\\#\\#0\\.00'; text-align: right; padding: 8px; border-top: 2px solid #3b82f6; border-bottom: 3px double #1d4ed8; border-left: 1px solid #93c5fd; border-right: 1px solid #93c5fd; color: #1e40af; background-color: #bfdbfe;">${totalActualPayment}</td>
      <td style="mso-number-format:'\\#\\,\\#\\#0\\.00'; text-align: right; padding: 8px; border-top: 2px solid #3b82f6; border-bottom: 3px double #1d4ed8; border-left: 1px solid #93c5fd; border-right: 1px solid #93c5fd; color: #dc2626;">${totalRemainingUnpaid}</td>
      <td colspan="7" style="border-top: 2px solid #3b82f6; border-bottom: 3px double #1d4ed8; border-left: 1px solid #93c5fd; border-right: 1px solid #93c5fd;"></td>
    </tr>
  `

  // Filter Info text
  const filterInfoText = `Filter Status: ${filterState.status || 'Not Paid'} | Date Range: ${filterState.dateFrom || 'All'} to ${filterState.dateTo || 'All'} | Generated: ${exportTimestamp}`

  // Complete HTML Workbook Structure
  const htmlTemplate = `
    <html xmlns:o="urn:schemas-microsoft-com:office:office" 
          xmlns:x="urn:schemas-microsoft-com:office:excel" 
          xmlns="http://www.w3.org/TR/REC-html40">
      <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <!--[if gte mso 9]>
        <xml>
          <x:ExcelWorkbook>
            <x:ExcelWorksheets>
              <x:ExcelWorksheet>
                <x:Name>Budget Request Report</x:Name>
                <x:WorksheetOptions>
                  <x:DisplayGridlines/>
                  <x:FitToPage/>
                  <x:Print>
                    <x:ValidPrinterInfo/>
                    <x:HorizontalResolution>600</x:HorizontalResolution>
                    <x:VerticalResolution>600</x:VerticalResolution>
                  </x:Print>
                </x:WorksheetOptions>
              </x:ExcelWorksheet>
            </x:ExcelWorksheets>
          </x:ExcelWorkbook>
        </xml>
        <![endif]-->
        <style>
          table { border-collapse: collapse; width: 100%; font-family: 'Segoe UI', Calibri, Arial, sans-serif; }
          td, th { vertical-align: middle; }
          .company-name { font-size: 16pt; font-weight: bold; color: #0f172a; }
          .company-info { font-size: 11pt; color: #334155; }
          .banner-title { 
            font-size: 14pt; 
            font-weight: bold; 
            background-color: #1e3a8a; 
            color: #ffffff; 
            text-align: center; 
            padding: 8px 0;
          }
          .meta-info {
            font-size: 9.5pt;
            font-style: italic;
            color: #475569;
            background-color: #f8fafc;
            text-align: center;
            padding: 4px 0;
            border-bottom: 2px solid #cbd5e1;
          }
        </style>
      </head>
      <body>
        <table>
          <!-- Company Profile Header Block -->
          <tr>
            <td colspan="10" class="company-name">${compName}</td>
          </tr>
          <tr>
            <td colspan="10" class="company-info">${compAddress}</td>
          </tr>
          <tr>
            <td colspan="10" class="company-info">${compCountry}</td>
          </tr>
          <tr>
            <td colspan="10" class="company-info">${compPhone}</td>
          </tr>
          <tr>
            <td colspan="10" class="company-info">${compFax}</td>
          </tr>
          <tr><td colspan="27" style="height: 10px;"></td></tr>

          <!-- Modern Sleek Header Banner -->
          <tr>
            <td colspan="27" class="banner-title">BUDGET REQUEST REPORT</td>
          </tr>
          <tr>
            <td colspan="27" class="meta-info">${filterInfoText}</td>
          </tr>
          <tr><td colspan="27" style="height: 10px;"></td></tr>

          <!-- Table Header -->
          <thead>
            <tr>${headerHtml}</tr>
          </thead>

          <!-- Table Body -->
          <tbody>
            ${rowsHtml}
            ${subTotalHtml}
            ${grandTotalHtml}
          </tbody>
        </table>
      </body>
    </html>
  `

  // Create Blob and trigger download
  const blob = new Blob(['\ufeff', htmlTemplate], {
    type: 'application/vnd.ms-excel;charset=utf-8'
  })

  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  const dateStr = now.toISOString().slice(0, 10)
  link.setAttribute('href', url)
  link.setAttribute('download', `Budget_Request_Report_${dateStr}.xls`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

function formatDate(dateString) {
  if (!dateString) return '-'
  const date = new Date(dateString)
  if (isNaN(date.getTime())) return dateString
  return date.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }).replace(/ /g, '-')
}
