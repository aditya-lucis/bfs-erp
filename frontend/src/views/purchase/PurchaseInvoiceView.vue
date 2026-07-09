<template>
  <Panel title="Purchase Invoice" subtitle="Purchase | Purchase Invoice">
    
    <!-- Toolbar/Search/Filter -->
    <div class="flex flex-col gap-4 mb-6">
      <div class="flex flex-wrap items-center gap-4">
        <div class="flex items-center border border-gray-200 rounded-lg overflow-hidden bg-white">
          <span class="px-3 py-1.5 bg-gray-50 text-xs text-gray-500 border-r border-gray-200">Search</span>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Type Invoice Number or Vendor..."
            class="px-3 py-1.5 text-xs focus:outline-none w-48 sm:w-64"
          />
        </div>
      </div>

      <div class="flex flex-wrap items-center justify-between gap-4 border-t border-gray-100 pt-4">
        <div class="flex flex-wrap items-center gap-4 text-xs">
          <!-- Filter Status -->
          <div class="border border-gray-200 rounded-lg px-3 py-1.5 relative bg-white flex items-center gap-2 shadow-sm min-h-[38px]">
            <span class="absolute -top-2 left-2 bg-white px-1 text-[9px] font-bold text-gray-500 uppercase tracking-wider">Status</span>
            <button @click="filterStatus = ''" class="px-1.5 py-0.5 rounded text-[10px] font-bold transition-colors cursor-pointer" :class="filterStatus === '' ? 'bg-bfs-navy text-white' : 'hover:bg-gray-100 text-gray-400'">ALL</button>
            <button @click="filterStatus = 'draft'" class="px-1.5 py-0.5 rounded text-[10px] font-bold transition-colors cursor-pointer" :class="filterStatus === 'draft' ? 'bg-amber-500 text-white' : 'hover:bg-gray-100 text-gray-400'">DRAFT</button>
            <button @click="filterStatus = 'open'" class="px-1.5 py-0.5 rounded text-[10px] font-bold transition-colors cursor-pointer" :class="filterStatus === 'open' ? 'bg-blue-500 text-white' : 'hover:bg-gray-100 text-gray-400'">OPEN</button>
            <button @click="filterStatus = 'paid'" class="px-1.5 py-0.5 rounded text-[10px] font-bold transition-colors cursor-pointer" :class="filterStatus === 'paid' ? 'bg-green-500 text-white' : 'hover:bg-gray-100 text-gray-400'">PAID</button>
          </div>
        </div>

        <div class="flex gap-2">
          <button @click="openModal('add')" class="btn-primary text-xs px-3 py-1.5 flex items-center gap-1.5 shadow-sm shadow-bfs-gold/30">
            <Plus class="w-3.5 h-3.5" /> Add Invoice
          </button>
        </div>
      </div>
    </div>

    <!-- Table -->
    <div class="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm shadow-bfs-navy/5">
      <div class="overflow-x-auto">
        <table class="w-full text-xs text-left">
          <thead class="bg-bfs-navy text-white text-[11px] uppercase tracking-wider">
            <tr>
              <th class="px-4 py-3 font-medium rounded-tl-lg">Action</th>
              <th class="px-4 py-3 font-medium">Invoice No</th>
              <th class="px-4 py-3 font-medium">Date</th>
              <th class="px-4 py-3 font-medium">Vendor</th>
              <th class="px-4 py-3 font-medium">PO Ref</th>
              <th class="px-4 py-3 font-medium">GRN Ref</th>
              <th class="px-4 py-3 font-medium text-right">Total Amount</th>
              <th class="px-4 py-3 font-medium text-center rounded-tr-lg">Status</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-if="loading" class="animate-pulse">
              <td colspan="8" class="px-4 py-8 text-center text-gray-400">Loading data...</td>
            </tr>
            <tr v-else-if="filteredInvoices.length === 0">
              <td colspan="8" class="px-4 py-8 text-center text-gray-500 flex flex-col items-center justify-center gap-2">
                <FileX class="w-8 h-8 text-gray-300" />
                <p>No Purchase Invoice found.</p>
              </td>
            </tr>
            <tr
              v-for="item in filteredInvoices"
              :key="item.id"
              class="hover:bg-bfs-navy/5 transition-colors group"
            >
              <td class="px-4 py-2">
                <div class="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button @click="openModal('view', item)" class="p-1 text-gray-400 hover:text-bfs-navy rounded cursor-pointer" title="View">
                    <Eye class="w-4 h-4" />
                  </button>
                  <button @click="openModal('edit', item)" class="p-1 text-gray-400 hover:text-bfs-gold rounded cursor-pointer" title="Edit">
                    <Edit class="w-4 h-4" />
                  </button>
                </div>
              </td>
              <td class="px-4 py-2 font-medium text-bfs-navy">{{ item.invoice_number }}</td>
              <td class="px-4 py-2 text-gray-600">{{ item.invoice_date }}</td>
              <td class="px-4 py-2 text-gray-600">{{ item.vendor_name || item.vendor }}</td>
              <td class="px-4 py-2 text-gray-600">{{ item.po_number || item.po }}</td>
              <td class="px-4 py-2 text-gray-600">{{ item.grn_number || item.grn }}</td>
              <td class="px-4 py-2 font-semibold text-right">{{ formatNumber(item.grand_total, item.currency) }}</td>
              <td class="px-4 py-2 text-center">
                <span class="px-2 py-0.5 rounded text-[10px] font-bold"
                  :class="{
                    'bg-amber-100 text-amber-700': item.status === 'draft',
                    'bg-blue-100 text-blue-700': item.status === 'open',
                    'bg-green-100 text-green-700': item.status === 'full_paid',
                    'bg-gray-100 text-gray-700': item.status === 'void',
                  }">
                  {{ item.status ? item.status.toUpperCase() : 'DRAFT' }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

<!-- Modal Form -->
    <Modal
      :isOpen="isModalOpen"
      :title="modalMode === 'add' ? '✨ Create Purchase Invoice' : modalMode === 'edit' ? '📝 Edit Purchase Invoice' : '👁️ View Purchase Invoice'"
      @close="closeModal"
      size="5xl"
    >
      <div class="space-y-6 text-sm text-gray-800 bg-gray-50/50 p-2 rounded-xl">
        
        <!-- Top Section: 3 Columns -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          
          <!-- Column 1: Vendor & Document Reference -->
          <div class="bg-white p-5 rounded-2xl shadow-sm border border-gray-100 space-y-4">
            <h3 class="font-bold text-bfs-navy flex items-center gap-2 mb-4 border-b pb-2">
              <span class="w-6 h-6 rounded bg-bfs-navy/10 flex items-center justify-center">🏢</span>
              Vendor Details
            </h3>
            
            <div>
              <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Invoice No</label>
              <div class="font-mono text-green-600 bg-green-50 px-3 py-2 rounded-lg border border-green-100 font-semibold w-full">
                {{ formData.invoice_number || '[Auto Generated]' }}
              </div>
            </div>

            <div>
              <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">
                Vendor <span class="italic text-[10px] lowercase text-gray-400 font-normal">(only with outstanding RR)</span>
              </label>
              <SearchableSelect
                v-model="formData.vendor"
                :options="vendors"
                :disabled="modalMode === 'view' || modalMode === 'edit'"
                placeholder="Select Vendor"
                :label-fn="(v) => `${v.name}`"
                value-key="id"
                @change="onVendorChange"
                class="w-full"
              />
            </div>

            <div v-if="formData.vendor">
              <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Address</label>
              <div class="text-gray-600 bg-gray-50 px-3 py-2 rounded-lg border border-gray-100 text-xs min-h-[42px]">
                {{ selectedVendorAddress || '-' }}
              </div>
            </div>

            <div v-if="formData.vendor">
              <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">PO Number</label>
              <SearchableSelect
                v-model="formData.po"
                :options="pos"
                :disabled="!formData.vendor || modalMode === 'view' || modalMode === 'edit'"
                placeholder="Select PO"
                :label-fn="(p) => p.po_number"
                value-key="id"
                @change="onPOChange"
                class="w-full"
              />
            </div>
            
            <div v-if="formData.po">
              <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Receipt Report (RR)</label>
              <SearchableSelect
                v-model="formData.receipt_report"
                :options="receiptReports"
                :disabled="!formData.po || modalMode === 'view' || modalMode === 'edit'"
                placeholder="Select RR"
                :label-fn="(r) => `${r.receipt_number}`"
                value-key="id"
                @change="onReceiptReportChange"
                class="w-full"
              />
            </div>
            
            <div v-if="formData.po">
              <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Good Receipt Note (GRN)</label>
              <SearchableSelect
                v-model="formData.grn"
                :options="grns"
                :disabled="!formData.po || modalMode === 'view' || modalMode === 'edit'"
                placeholder="Select GRN"
                :label-fn="(g) => `${g.grn_number} - ${g.document_date}`"
                value-key="id"
                @change="onReceiptReportChange"
                class="w-full"
              />
            </div>
          </div>

          <!-- Column 2: Dates & Terms -->
          <div class="bg-white p-5 rounded-2xl shadow-sm border border-gray-100 space-y-4">
            <h3 class="font-bold text-bfs-navy flex items-center gap-2 mb-4 border-b pb-2">
              <span class="w-6 h-6 rounded bg-bfs-navy/10 flex items-center justify-center">📅</span>
              Dates & Timeline
            </h3>

            <div>
              <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Invoice Date <span class="text-red-500">*</span></label>
              <input v-model="formData.invoice_date" @change="calculateDueDate" type="date" :readonly="modalMode === 'view'" class="form-input text-sm w-full rounded-lg border-gray-300 focus:border-bfs-navy focus:ring-1 focus:ring-bfs-navy" />
            </div>

            <div>
              <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Duration Due Date</label>
              <select v-model="formData.duration_due_date" @change="calculateDueDate" :disabled="modalMode === 'view'" class="form-input text-sm w-full rounded-lg border-gray-300 focus:border-bfs-navy focus:ring-1 focus:ring-bfs-navy">
                <option value="">----- None -----</option>
                <option value="15">15 Days</option>
                <option value="30">30 Days</option>
                <option value="45">45 Days</option>
                <option value="60">60 Days</option>
              </select>
            </div>

            <div>
              <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Due Date <span class="text-red-500">*</span></label>
              <input v-model="formData.due_date" type="date" :readonly="modalMode === 'view'" class="form-input text-sm w-full rounded-lg border-gray-300 focus:border-bfs-navy focus:ring-1 focus:ring-bfs-navy" />
            </div>

            <div>
              <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Tax Date</label>
              <input v-model="formData.tax_date" type="date" :readonly="modalMode === 'view'" class="form-input text-sm w-full rounded-lg border-gray-300 focus:border-bfs-navy focus:ring-1 focus:ring-bfs-navy" />
            </div>
            
            <div class="mt-6 pt-4 border-t">
              <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Status</label>
              <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold"
                :class="{
                  'bg-amber-100 text-amber-700': formData.status === 'draft',
                  'bg-blue-100 text-blue-700': formData.status === 'open' || !formData.status,
                  'bg-green-100 text-green-700': formData.status === 'full_paid',
                  'bg-gray-100 text-gray-700': formData.status === 'void',
                }">
                {{ formData.status === 'full_paid' ? 'Full Paid' : formData.status === 'half_paid' ? 'Half Paid' : formData.status ? formData.status.toUpperCase() : 'OPEN' }}
              </span>
            </div>
          </div>

          <!-- Column 3: Tax & References -->
          <div class="bg-white p-5 rounded-2xl shadow-sm border border-gray-100 space-y-4">
            <h3 class="font-bold text-bfs-navy flex items-center gap-2 mb-4 border-b pb-2">
              <span class="w-6 h-6 rounded bg-bfs-navy/10 flex items-center justify-center">🧾</span>
              Tax & References
            </h3>

            <div>
              <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Vendor Invoice Number <span class="text-red-500">*</span></label>
              <input v-model="formData.vendor_invoice_number" type="text" :readonly="modalMode === 'view'" placeholder="Enter vendor invoice no..." class="form-input text-sm w-full rounded-lg border-gray-300 focus:border-bfs-navy focus:ring-1 focus:ring-bfs-navy" />
            </div>

            <div>
              <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Tax Number (PPN)</label>
              <input v-model="formData.tax_number_ppn" type="text" :readonly="modalMode === 'view'" placeholder="Enter PPN number..." class="form-input text-sm w-full rounded-lg border-gray-300 focus:border-bfs-navy focus:ring-1 focus:ring-bfs-navy" />
            </div>

            <div>
              <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Tax Number (PPH)</label>
              <input v-model="formData.tax_number_pph" type="text" :readonly="modalMode === 'view'" placeholder="Enter PPH number..." class="form-input text-sm w-full rounded-lg border-gray-300 focus:border-bfs-navy focus:ring-1 focus:ring-bfs-navy" />
            </div>
            
            <div class="flex items-center gap-3 pt-2">
              <label class="text-xs font-semibold text-gray-500 uppercase tracking-wider">TickMark PPN</label>
              <label class="relative inline-flex items-center cursor-pointer">
                <input v-model="formData.tickmark_ppn" type="checkbox" :disabled="modalMode === 'view'" class="sr-only peer" @change="calculateTotals">
                <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-bfs-navy"></div>
                <span class="ml-3 text-sm font-medium text-gray-700">{{ formData.tickmark_ppn ? 'Yes' : 'No' }}</span>
              </label>
            </div>
          </div>
        </div>

        <!-- Notes (Full Width) -->
        <div class="bg-white p-5 rounded-2xl shadow-sm border border-gray-100">
          <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Notes & Remarks</label>
          <textarea v-model="formData.notes" :readonly="modalMode === 'view'" rows="2" placeholder="Add any additional notes here..." class="form-input text-sm w-full rounded-lg border-gray-300 focus:border-bfs-navy focus:ring-1 focus:ring-bfs-navy resize-none"></textarea>
        </div>
        
        <div v-if="formData.details.length > 0" class="bg-white p-5 rounded-2xl shadow-sm border border-gray-100 flex flex-col md:flex-row gap-6 justify-between items-start">
          <div class="w-full md:w-1/2">
            <h3 class="font-bold text-bfs-navy flex items-center gap-2 mb-4 border-b pb-2">
              <span class="w-6 h-6 rounded bg-bfs-navy/10 flex items-center justify-center">📊</span>
              Invoice Percentage Setting
            </h3>
            <div class="flex items-center gap-4 bg-gray-50 p-4 rounded-xl border border-gray-100">
              <div class="w-32">
                <label class="block text-xs text-gray-500 mb-1">Percentage (%)</label>
                <input v-model.number="formData.invoice_percentage" type="number" step="0.01" :readonly="modalMode === 'view'" class="form-input text-sm w-full rounded-lg border-gray-300 font-bold text-right" @input="calculateTotals" />
              </div>
              <div class="flex-1">
                <label class="block text-xs text-gray-500 mb-1">Calculated Amount</label>
                <input :value="formatNumber(formData.invoice_rcv_amount)" type="text" readonly class="form-input text-sm w-full rounded-lg border-transparent bg-gray-200 text-gray-700 font-mono text-right" />
              </div>
            </div>
          </div>
          
          <div class="w-full md:w-1/2 bg-blue-50/50 p-4 rounded-xl border border-blue-100 font-mono text-xs text-gray-600">
            <div class="flex justify-between py-1 border-b border-blue-100">
              <span>Amount PO</span>
              <span class="font-bold text-bfs-navy">{{ formatNumber(totalPOAmount) }}</span>
            </div>
            <div class="flex justify-between py-1 border-b border-blue-100">
              <span>Total Invoiced (%)</span>
              <span class="font-bold text-bfs-navy">{{ formatNumber(totalInvoicedPercentage) }} %</span>
            </div>
            <div class="flex justify-between py-1 border-b border-blue-100">
              <span>Total Invoiced (Amount)</span>
              <span class="font-bold text-bfs-navy">{{ formatNumber((totalPOAmount * totalInvoicedPercentage) / 100) }}</span>
            </div>
            <div class="flex justify-between py-1 mt-1 font-bold">
              <span class="text-blue-800">Selisih (Variance)</span>
              <span :class="selisih < 0 ? 'text-red-600' : 'text-green-600'">{{ formatNumber(selisih) }}</span>
            </div>
          </div>
        </div>

        <!-- Items Table -->
        <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          <div class="bg-bfs-navy px-5 py-3 flex items-center justify-between text-white">
            <div class="flex items-center gap-2 font-semibold">
              <List class="w-4 h-4" />
              Invoice Item Details
            </div>
            <div class="w-5 h-5 bg-white/20 rounded-full flex items-center justify-center text-[11px] font-bold cursor-help" title="These items are populated from the selected RR/GRN">?</div>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-xs text-left">
              <thead class="bg-gray-50 text-gray-500 uppercase tracking-wider text-[10px]">
                <tr>
                  <th class="px-4 py-3 font-semibold text-center border-b">No.</th>
                  <th class="px-4 py-3 font-semibold border-b">Item Details</th>
                  <th class="px-4 py-3 font-semibold text-center border-b">Qty</th>
                  <th class="px-4 py-3 font-semibold text-right border-b">Unit Price (IDR)</th>
                  <th class="px-4 py-3 font-semibold text-center border-b">Disc (%)</th>
                  <th class="px-4 py-3 font-semibold text-right border-b">Amount (IDR)</th>
                  <th class="px-4 py-3 font-semibold text-center border-b">Tax</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-100">
                <tr v-if="formData.details.length === 0">
                  <td colspan="7" class="px-4 py-8 text-center text-gray-400">
                    <div class="flex flex-col items-center gap-2">
                      <FolderOpen class="w-8 h-8 text-gray-300" />
                      <span>No items available. Select a PO and RR/GRN first.</span>
                    </div>
                  </td>
                </tr>
                <tr v-for="(detail, index) in formData.details" :key="index" class="hover:bg-blue-50/30 transition-colors">
                  <td class="px-4 py-3 text-center text-gray-500">{{ index + 1 }}</td>
                  <td class="px-4 py-3">
                    <div class="font-semibold text-bfs-navy">{{ detail.item_name }}</div>
                    <div class="text-[10px] text-gray-400 mt-0.5">Code: {{ detail.item_code || '-' }} | Dim: {{ detail.dimension || '-' }}</div>
                  </td>
                  <td class="px-4 py-3 text-center font-medium">
                    <div class="bg-gray-100 px-2 py-1 rounded inline-block">{{ detail.quantity }}</div>
                  </td>
                  <td class="px-4 py-3 text-right">
                    <input v-model.number="detail.unit_price" type="number" step="0.01" @input="calculateTotals" :readonly="modalMode === 'view'" class="w-24 form-input text-xs border-gray-300 rounded focus:border-bfs-navy text-right" />
                  </td>
                  <td class="px-4 py-3 text-center">
                    <span class="text-gray-500">{{ detail.discount_percent || 0 }}%</span>
                  </td>
                  <td class="px-4 py-3 text-right font-mono font-semibold text-gray-700">
                    {{ formatNumber(detail.total_amount) }}
                  </td>
                  <td class="px-4 py-3 text-center">
                    <span v-if="formData.tickmark_ppn" class="bg-blue-100 text-blue-700 px-2 py-0.5 rounded text-[10px] font-bold">PPN</span>
                    <span v-else class="text-gray-400">-</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Totals & Payment Terms -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
          
          <!-- Payment Terms -->
          <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden flex flex-col">
            <div class="bg-gray-50 px-4 py-3 border-b flex items-center justify-between">
              <h3 class="font-bold text-gray-700 flex items-center gap-2">
                <FileText class="w-4 h-4 text-gray-400" />
                Terms of Payment
              </h3>
              <button v-if="modalMode !== 'view'" @click="addPaymentTerm" class="text-bfs-navy hover:text-blue-700 text-xs font-semibold flex items-center gap-1">
                <Plus class="w-3 h-3" /> Add Term
              </button>
            </div>
            <div class="p-4 overflow-x-auto flex-1">
              <table class="w-full text-[11px] text-left border-collapse">
                <thead class="bg-gray-100 text-gray-600">
                  <tr>
                    <th class="px-2 py-2 font-semibold text-center rounded-tl">#</th>
                    <th class="px-2 py-2 font-semibold text-center">Due Date</th>
                    <th class="px-2 py-2 font-semibold">Description</th>
                    <th class="px-2 py-2 font-semibold text-center">%</th>
                    <th class="px-2 py-2 font-semibold text-right">Amount (IDR)</th>
                    <th class="px-2 py-2 text-center rounded-tr"></th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-if="formData.payment_terms.length === 0">
                    <td colspan="6" class="px-2 py-4 text-center text-gray-400 italic border-b">No payment terms defined.</td>
                  </tr>
                  <tr v-for="(term, index) in formData.payment_terms" :key="index" class="border-b border-gray-50">
                    <td class="px-2 py-2 text-center text-gray-400">{{ index + 1 }}</td>
                    <td class="px-1 py-1 w-28">
                      <input v-model="term.due_date" type="date" :readonly="modalMode === 'view'" class="w-full form-input text-[10px] py-1 border-gray-300 rounded" />
                    </td>
                    <td class="px-1 py-1">
                      <input v-model="term.description" type="text" :readonly="modalMode === 'view'" class="w-full form-input text-[10px] py-1 border-gray-300 rounded" placeholder="Desc..." />
                    </td>
                    <td class="px-1 py-1 w-16">
                      <input v-model.number="term.percentage" type="number" step="0.01" @input="onTermPercentChange(term)" :readonly="modalMode === 'view'" class="w-full form-input text-[10px] py-1 border-gray-300 rounded text-center" />
                    </td>
                    <td class="px-1 py-1 w-28">
                      <input v-model.number="term.amount" type="number" step="0.01" @input="onTermAmountChange(term)" :readonly="modalMode === 'view'" class="w-full form-input text-[10px] py-1 border-gray-300 rounded text-right font-mono" />
                    </td>
                    <td class="px-1 py-1 text-center w-8">
                      <button v-if="modalMode !== 'view'" @click="removePaymentTerm(index)" class="text-red-400 hover:text-red-600 p-1 rounded-full hover:bg-red-50 transition-colors" title="Remove Term">
                        <Trash2 class="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Totals Summary -->
          <div class="bg-bfs-navy text-white rounded-2xl shadow-lg overflow-hidden flex flex-col font-mono text-xs">
            <div class="px-5 py-4 border-b border-white/10 flex items-center justify-between">
              <span class="font-semibold text-white/80 tracking-wider">SUMMARY (IDR)</span>
              <div class="text-[10px] text-white/50">Total Qty: {{ formData.details.reduce((sum, d) => sum + (parseFloat(d.quantity) || 0), 0) }}</div>
            </div>
            <div class="p-5 space-y-3 flex-1">
              <div class="flex justify-between items-center text-white/80">
                <span>Subtotal</span>
                <span>{{ formatNumber(formData.subtotal_amount) }}</span>
              </div>
              <div class="flex justify-between items-center text-white/80">
                <span>Discount</span>
                <span class="text-red-300">- {{ formatNumber(formData.discount_amount) }}</span>
              </div>
              <div class="flex justify-between items-center text-white/80">
                <span>Tax (PPN)</span>
                <span class="text-green-300">+ {{ formatNumber(formData.tax_amount) }}</span>
              </div>
              <div class="flex justify-between items-center pt-3 border-t border-white/20 mt-3 font-bold text-sm">
                <span>GRAND TOTAL</span>
                <span class="text-bfs-gold">{{ formatNumber(formData.grand_total) }}</span>
              </div>
              
              <!-- Advance Payment Placeholder -->
              <div class="mt-6 p-3 bg-black/20 rounded-lg border border-white/10">
                <div class="flex justify-between items-center text-white/70 mb-2 text-[10px] uppercase tracking-wider">
                  <span>Advance Payment (DP)</span>
                  <a href="#" class="text-blue-300 hover:text-blue-200 underline lowercase">Select doc</a>
                </div>
                <div class="flex justify-between items-center text-white/90">
                  <span>Total DP</span>
                  <span class="text-white">0.00</span>
                </div>
                <div class="flex justify-between items-center pt-2 border-t border-white/10 mt-2 font-bold text-white">
                  <span>NET PAYABLE</span>
                  <span class="text-xl">{{ formatNumber(formData.grand_total) }}</span>
                </div>
              </div>
            </div>
          </div>

        </div>

      </div>

      <!-- Action Buttons -->
      <template #footer>
        <div class="flex justify-end gap-3 w-full mt-4 pt-2">
          <button @click="closeModal" class="px-6 py-2.5 rounded-xl font-bold text-gray-500 bg-gray-100 hover:bg-gray-200 transition-colors text-sm">
            {{ modalMode === 'view' ? 'Close' : 'Cancel' }}
          </button>
          <button
            v-if="modalMode !== 'view'"
            @click="saveInvoice"
            :disabled="isSaving"
            class="px-8 py-2.5 rounded-xl font-bold text-white bg-bfs-navy hover:bg-bfs-navy-light transition-all shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 text-sm"
          >
            <span v-if="isSaving" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
            <Save v-else class="w-4 h-4" />
            {{ isSaving ? 'Saving...' : 'Save Invoice' }}
          </button>
        </div>
      </template>
    </Modal>
  </Panel>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import Swal from 'sweetalert2'
import api from '../../services/api'
import Panel from '../../components/Panel.vue'
import Modal from '../../components/Modal.vue'
import SearchableSelect from '../../components/SearchableSelect.vue'
import {
  Plus, Search, Edit, Eye, Trash2, FileText, List, Save, FileX, Folder, FolderOpen, FolderCheck
} from 'lucide-vue-next'

const invoices = ref([])


const loading = ref(false)
const isSaving = ref(false)
const searchQuery = ref('')
const filterStatus = ref('')

const isModalOpen = ref(false)
const modalMode = ref('add') // add, edit, view

const initialFormState = {
  id: null,
  vendor: '',
  po: '',
  receipt_report: '',
  grn: '',
  invoice_date: new Date().toISOString().split('T')[0],
  duration_due_date: '',
  due_date: new Date().toISOString().split('T')[0],
  tax_date: new Date().toISOString().split('T')[0],
  tax_number: '',
  tax_number_ppn: '',
  tax_number_pph: '',
  vendor_invoice_number: '',
  notes: '',
  currency: 'IDR',
  subtotal_amount: 0,
  discount_amount: 0,
  tax_amount: 0,
  grand_total: 0,
  invoice_percentage: 100.00,
  invoice_rcv_amount: 0,
  details: [],
  payment_terms: []
}

const formData = ref({ ...initialFormState })






const vendors = ref([])
const pos = ref([])
const receiptReports = ref([])
const grns = ref([])

const fetchVendors = async () => {
  try {
    const res = await api.get('/purchase/purchase-invoices/get_valid_vendors/')
    vendors.value = res.data.results || res.data
  } catch (error) {
    console.error('Error fetching vendors', error)
  }
}

const onVendorChange = async () => {
  formData.value.po = ''
  formData.value.receipt_report = ''
  formData.value.grn = ''
  pos.value = []
  receiptReports.value = []
  grns.value = []
  
  if (!formData.value.vendor) return

  try {
    const res = await api.get(`/purchase/purchase-invoices/get_valid_pos/?vendor_id=${formData.value.vendor}`)
    pos.value = res.data.results || res.data
  } catch (error) {
    console.error('Error fetching POs', error)
  }
}

const onPOChange = async () => {
  formData.value.receipt_report = ''
  formData.value.grn = ''
  receiptReports.value = []
  grns.value = []
  
  if (!formData.value.po) return

  try {
    const resRR = await api.get(`/inventory/receipt-reports/?po=${formData.value.po}&approval_status=approved`)
    receiptReports.value = resRR.data.results || resRR.data

    const resGRN = await api.get(`/purchase/good-receipt-notes/?po=${formData.value.po}&un_invoiced=true`)
    grns.value = resGRN.data.results || resGRN.data
  } catch (error) {
    console.error('Error fetching RRs and GRNs', error)
  }
}

const selectedVendorInfo = computed(() => {
  return vendors.value.find(v => v.id === formData.value.vendor) || {}
})

const selectedVendorName = computed(() => {
  return selectedVendorInfo.value.name || ''
})

const selectedVendorAddress = computed(() => {
  return selectedVendorInfo.value.address || selectedVendorInfo.value.address_1 || selectedVendorInfo.value.address1 || ''
})

const selectedGRN = computed(() => {
  return grns.value.find(g => g.id === formData.value.grn) || {}
})

const selectedGRNNumber = computed(() => {
  return selectedGRN.value.grn_number || ''
})

const onReceiptReportChange = async () => {
  formData.value.details = []
  if (!formData.value.receipt_report) return

  try {
    const res = await api.get(`/inventory/receipt-reports/${formData.value.receipt_report}/`)
    const rr = res.data
    
    if (rr && rr.items) {
      // From add.cfm (line 761-824): items come from PO Detail joined with RR Item.
      // Unit price = TAccPO_Detail.UnitPrice (po_item_unit_price)
      // Disc = TAccPO_Detail.Disc_Percentage (po_item_discount_percent)
      // Tax from TAccPO_Detail.Tax_Code1 (po_item_tax1)
      formData.value.details = rr.items.map((d, index) => {
        const qty = parseFloat(d.receive_qty) || 0
        const unitPrice = parseFloat(d.po_item_unit_price) || 0
        const discPercent = parseFloat(d.po_item_discount_percent) || 0
        const baseAmount = qty * unitPrice
        const discAmount = baseAmount * (discPercent / 100)
        const netAmount = baseAmount - discAmount
        // Tax: ppn_11 = 11%, ppn_10 = 10%, none = 0
        let taxRate = 0
        const tax1 = (d.po_item_tax1 || '').toLowerCase()
        if (tax1.includes('ppn_11') || tax1.includes('ppn11')) taxRate = 0.11
        else if (tax1.includes('ppn_10') || tax1.includes('ppn10')) taxRate = 0.10
        const taxAmount = formData.value.tickmark_ppn ? netAmount * taxRate : 0

        return {
          item: d.item,
          item_code: d.item_code || '',
          item_name: d.item_name || 'Item',
          dimension: d.dimension || '',
          quantity: qty,
          unit_price: unitPrice,
          discount_percent: discPercent,
          discount_amount: discAmount,
          po_item_tax1: d.po_item_tax1 || '',
          tax_rate: taxRate,
          tax_amount: taxAmount,
          total_amount: netAmount + taxAmount,
          order_no: index + 1
        }
      })
      calculateTotals()
    }
  } catch (error) {
    console.error('Error fetching RR items', error)
  }
}

const calculateDueDate = () => {
  if (!formData.value.invoice_date || !formData.value.duration_due_date) return
  const date = new Date(formData.value.invoice_date)
  date.setDate(date.getDate() + parseInt(formData.value.duration_due_date))
  formData.value.due_date = date.toISOString().split('T')[0]
}

const blastGRN = () => {
  if (!formData.value.grn) return
  const selectedGRN = grns.value.find(g => g.id === formData.value.grn)
  if (selectedGRN) {
    formData.value.invoice_percentage = selectedGRN.term_percentage || 100
    formData.value.invoice_rcv_amount = selectedGRN.amount || 0
  }
}

// Reactively recalculate due_date whenever invoice_date or duration_due_date changes
watch(
  () => [formData.value.invoice_date, formData.value.duration_due_date],
  ([invoiceDate, duration]) => {
    if (!invoiceDate || !duration) return
    const date = new Date(invoiceDate)
    date.setDate(date.getDate() + parseInt(duration))
    formData.value.due_date = date.toISOString().split('T')[0]
  }
)

// Payment Terms functions
const addPaymentTerm = () => {
  formData.value.payment_terms.push({
    due_date: formData.value.due_date || formData.value.invoice_date,
    description: 'Full Pembayaran',
    percentage: 100.00,
    amount: formData.value.grand_total || 0,
    term_number: formData.value.payment_terms.length + 1
  })
}

const removePaymentTerm = (index) => {
  formData.value.payment_terms.splice(index, 1)
  // recalculate percentages or amounts if necessary
}

const onTermPercentChange = (term) => {
  const gt = parseFloat(formData.value.grand_total) || 0
  term.amount = (parseFloat(term.percentage) / 100) * gt
}

const onTermAmountChange = (term) => {
  const gt = parseFloat(formData.value.grand_total) || 0
  if (gt > 0) {
    term.percentage = (parseFloat(term.amount) / gt) * 100
  }
}


const selectedPOInfo = computed(() => {
  return pos.value.find(p => String(p.id) === String(formData.value.po)) || {}
})

const totalPOAmount = computed(() => {
  return selectedPOInfo.value.grand_total || 0
})

const totalInvoicedPercentage = computed(() => {
  return selectedPOInfo.value.total_invoiced_percentage || 0
})

const selisih = computed(() => {
  const currentInvoiceValue = (totalPOAmount.value * parseFloat(formData.value.invoice_percentage)) / 100
  return totalPOAmount.value - ((totalPOAmount.value * totalInvoicedPercentage.value) / 100) - currentInvoiceValue
})

const calculateTotals = () => {
  let sub = 0
  let disc = 0
  let tax = 0
  
  formData.value.details.forEach(d => {
    const qty = parseFloat(d.quantity) || 0
    const price = parseFloat(d.unit_price) || 0
    const discPercent = parseFloat(d.discount_percent) || 0
    const base = qty * price
    const itemDisc = base * (discPercent / 100)
    const net = base - itemDisc
    // Recalculate tax based on tickmark_ppn toggle
    const taxRate = parseFloat(d.tax_rate) || 0
    const itemTax = formData.value.tickmark_ppn ? net * taxRate : 0
    d.discount_amount = itemDisc
    d.tax_amount = itemTax
    d.total_amount = net + itemTax
    
    sub += base
    disc += itemDisc
    tax += itemTax
  })
  
  // Apply invoice_percentage from GRN (add.cfm: invoice_percentage = portion of PO to invoice)
  const pct = parseFloat(formData.value.invoice_percentage) || 100
  const factor = pct / 100

  formData.value.subtotal_amount = sub * factor
  formData.value.discount_amount = disc * factor
  formData.value.tax_amount = tax * factor
  formData.value.grand_total = (sub - disc + tax) * factor
  
  // Update invoice_rcv_amount
  formData.value.invoice_rcv_amount = formData.value.grand_total

  // Auto update payment term amounts based on percentage (matching add.cfm logic)
  if (formData.value.payment_terms && formData.value.payment_terms.length > 0) {
    formData.value.payment_terms.forEach(term => {
      const pct = parseFloat(term.percentage) || 0
      term.amount = (pct / 100) * formData.value.grand_total
    })
  }
}

const openModal = async (mode, item = null) => {
  modalMode.value = mode
  if (mode === 'add') {
    formData.value = { ...initialFormState }
    formData.value.invoice_date = new Date().toISOString().split('T')[0]
    await fetchVendors()
  } else if (item) {
    let latestItem = { ...item }
    try {
      const invRes = await api.get(`/purchase/purchase-invoices/${item.id}/`)
      latestItem = invRes.data
    } catch (e) {
      console.error("Failed to fetch latest invoice", e)
    }
    
    formData.value = { ...latestItem }
    formData.value.tickmark_ppn = parseFloat(latestItem.tax_amount || 0) > 0
    await fetchVendors()
    if (latestItem.vendor) {
      try {
        const response = await api.get(`/purchase/purchase-orders/?vendor=${latestItem.vendor}`)
        let poList = response.data.results || response.data
        if (latestItem.po && !poList.find(p => String(p.id) === String(latestItem.po))) {
          try {
             const poRes = await api.get(`/purchase/purchase-orders/${latestItem.po}/`)
             if (poRes.data) {
                poList.push(poRes.data)
             }
          } catch(e) {}
        }
        pos.value = poList
      } catch (e) {}
    }
    if (latestItem.po) {
      try {
        const resRR = await api.get(`/inventory/receipt-reports/?po=${latestItem.po}`)
        let rrList = resRR.data.results || resRR.data
        if (latestItem.receipt_report && !rrList.find(r => String(r.id) === String(latestItem.receipt_report))) {
          try {
             const rr = await api.get(`/inventory/receipt-reports/${latestItem.receipt_report}/`)
             if (rr.data) rrList.push(rr.data)
          } catch(e) {}
        }
        receiptReports.value = rrList
        
        const resGRN = await api.get(`/purchase/good-receipt-notes/?po=${latestItem.po}`)
        let grnList = resGRN.data.results || resGRN.data
        if (latestItem.grn && !grnList.find(g => String(g.id) === String(latestItem.grn))) {
          try {
             const grn = await api.get(`/purchase/good-receipt-notes/${latestItem.grn}/`)
             if (grn.data) grnList.push(grn.data)
          } catch(e) {}
        }
        grns.value = grnList
      } catch (e) {}
    }
  }
  isModalOpen.value = true
}

const closeModal = () => {
  isModalOpen.value = false
  formData.value = { ...initialFormState }
}

const saveInvoice = async () => {
  isSaving.value = true
  try {
    if (modalMode.value === 'add') {
      await api.post('/purchase/purchase-invoices/', formData.value)
    } else {
      await api.put(`/purchase/purchase-invoices/${formData.value.id}/`, formData.value)
    }
    await fetchInvoices()
    closeModal()
    
    Swal.fire({
      icon: 'success',
      title: 'Success!',
      text: 'Purchase Invoice saved successfully.',
      confirmButtonColor: '#3b82f6', // Tailwind blue-500
      timer: 1500,
      showConfirmButton: false
    })
  } catch (error) {
    console.error('Error saving invoice', error)
    
    let errorMsg = 'Failed to save invoice. Please check your data and try again.'
    if (error.response && error.response.data) {
      if (typeof error.response.data === 'string') {
        // sometimes django backend returns an array wrapped in string or just string
        try {
          const parsed = JSON.parse(error.response.data)
          if (Array.isArray(parsed) && parsed.length > 0) errorMsg = parsed[0]
          else errorMsg = error.response.data
        } catch(e) {
          errorMsg = error.response.data
        }
      } else if (error.response.data.detail) {
        errorMsg = error.response.data.detail
      } else if (Array.isArray(error.response.data) && error.response.data.length > 0) {
        errorMsg = error.response.data[0]
      } else if (typeof error.response.data === 'object') {
        const firstKey = Object.keys(error.response.data)[0]
        if (firstKey) {
          const val = error.response.data[firstKey]
          errorMsg = `${firstKey}: ${Array.isArray(val) ? val[0] : val}`
        }
      }
    }
    
    Swal.fire({
      icon: 'error',
      title: 'Validation Error',
      text: errorMsg,
      confirmButtonColor: '#ef4444' // Tailwind red-500
    })
  } finally {
    isSaving.value = false
  }
}

const formatNumber = (value, currency = 'IDR') => {
  if (value === null || value === undefined) return '-'
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 2
  }).format(value)
}


const fetchInvoices = async () => {
  loading.value = true
  try {
    const res = await api.get('/purchase/purchase-invoices/')
    invoices.value = res.data.results || res.data
  } catch (error) {
    console.error('Error fetching invoices:', error)
  } finally {
    loading.value = false
  }
}

const filteredInvoices = computed(() => {
  let result = invoices.value || []
  
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(item => 
      (item.invoice_number && item.invoice_number.toLowerCase().includes(q)) ||
      (item.vendor_name && item.vendor_name.toLowerCase().includes(q)) ||
      (item.po_number && item.po_number.toLowerCase().includes(q)) ||
      (item.vendor && String(item.vendor).toLowerCase().includes(q))
    )
  }
  
  if (filterStatus.value) {
    result = result.filter(item => item.status === filterStatus.value)
  }
  
  return result
})

onMounted(() => {
  fetchInvoices()
})
</script>