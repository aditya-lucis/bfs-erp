<template>
  <Panel title="Purchase Order (PR)" subtitle="Purchase | Purchase Order">
    
    <!-- Toolbar/Search/Filter -->
    <div class="flex flex-col gap-4 mb-6">
      <div class="flex flex-wrap items-center gap-4">
        <!-- Search -->
        <div class="flex items-center border border-gray-200 rounded-lg overflow-hidden bg-white">
          <span class="px-3 py-1.5 bg-gray-50 text-xs text-gray-500 border-r border-gray-200">Search</span>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Type PO Number or Project..."
            class="px-3 py-1.5 text-xs focus:outline-none w-48 sm:w-64"
            @keyup.enter="handleSearch"
          />
        </div>

        <!-- Date Range -->
        <div class="flex items-center gap-2 text-xs">
          <span class="text-gray-500 font-semibold uppercase">Date From:</span>
          <input v-model="filterDateFrom" type="date" class="border border-gray-200 rounded px-2 py-1 bg-white text-xs focus:outline-none" />
          <span class="text-gray-500 font-semibold uppercase">To:</span>
          <input v-model="filterDateTo" type="date" class="border border-gray-200 rounded px-2 py-1 bg-white text-xs focus:outline-none" />
        </div>

        <button
          @click="handleSearch"
          class="px-3 py-1.5 bg-bfs-navy hover:bg-bfs-navy-dark text-white text-xs font-medium rounded-lg transition-colors flex items-center gap-1.5 cursor-pointer"
        >
          <Search class="w-3.5 h-3.5" /> Search
        </button>
        <button
          @click="handleResetFilters"
          class="btn-secondary text-xs px-3 py-1.5 flex items-center gap-1.5"
        >
          Reset
        </button>
      </div>

      <div class="flex flex-wrap items-center justify-between gap-4 border-t border-gray-100 pt-4">
        <div class="flex flex-wrap items-center gap-4 text-xs">
          <!-- Item Category Dropdown -->
          <div class="flex items-center gap-2">
            <span class="text-gray-500 font-semibold">Item Category:</span>
            <select v-model="filterItemCategory" class="border border-gray-200 rounded px-2 py-1 bg-white focus:outline-none h-[34px]" @change="handleSearch">
              <option value="">All</option>
              <option value="RM">Raw Material</option>
              <option value="SP">Supplies</option>
              <option value="AST">Asset</option>
            </select>
          </div>

          <!-- Filter Status (Sokka Style) -->
          <div class="border border-gray-200 rounded-lg px-3 py-1.5 relative bg-white flex items-center gap-2 shadow-sm min-h-[38px]">
            <span class="absolute -top-2 left-2 bg-white px-1 text-[9px] font-bold text-gray-500 uppercase tracking-wider">Filter Status</span>
            <button 
              @click="filterDocStatus = ''; handleSearch()" 
              class="px-1.5 py-0.5 rounded text-[10px] font-bold transition-colors cursor-pointer"
              :class="filterDocStatus === '' ? 'bg-bfs-navy text-white' : 'hover:bg-gray-100 text-gray-400'"
              title="All Status"
            >
              ALL
            </button>
            <button 
              @click="filterDocStatus = 'draft'; handleSearch()" 
              class="p-0.5 rounded transition-all cursor-pointer"
              :class="filterDocStatus === 'draft' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"
              title="Draft (Editable)"
            >
              <Folder class="w-4 h-4 text-amber-500 fill-amber-500/10" />
            </button>
            <button 
              @click="filterDocStatus = 'ready_to_process'; handleSearch()" 
              class="p-0.5 rounded transition-all cursor-pointer"
              :class="filterDocStatus === 'ready_to_process' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"
              title="Ready to Process (Submitted)"
            >
              <FolderOpen class="w-4 h-4 text-blue-500 fill-blue-500/10" />
            </button>
            <button 
              @click="filterDocStatus = 'close'; handleSearch()" 
              class="p-0.5 rounded transition-all cursor-pointer"
              :class="filterDocStatus === 'close' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"
              title="Close (Finalized)"
            >
              <FolderCheck class="w-4 h-4 text-green-500 fill-green-500/10" />
            </button>
          </div>

          <!-- Approval Filter Status (Sokka Style) -->
          <div class="border border-gray-200 rounded-lg px-3 py-1.5 relative bg-white flex items-center gap-2 shadow-sm min-h-[38px]">
            <span class="absolute -top-2 left-2 bg-white px-1 text-[9px] font-bold text-gray-500 uppercase tracking-wider">Approval Filter Status</span>
            <button 
              @click="filterAppStatus = ''; handleSearch()" 
              class="px-1.5 py-0.5 rounded text-[10px] font-bold transition-colors cursor-pointer"
              :class="filterAppStatus === '' ? 'bg-bfs-navy text-white' : 'hover:bg-gray-100 text-gray-400'"
              title="All Approval"
            >
              ALL
            </button>
            <button 
              @click="filterAppStatus = 'draft'; handleSearch()" 
              class="p-0.5 rounded transition-all cursor-pointer"
              :class="filterAppStatus === 'draft' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"
              title="Draft"
            >
              <FileText class="w-4 h-4 text-gray-400" />
            </button>
            <button 
              @click="filterAppStatus = 'awaiting'; handleSearch()" 
              class="p-0.5 rounded transition-all cursor-pointer"
              :class="filterAppStatus === 'awaiting' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"
              title="Awaiting Approval"
            >
              <FileClock class="w-4 h-4 text-bfs-gold animate-pulse" />
            </button>
            <button 
              @click="filterAppStatus = 'approved'; handleSearch()" 
              class="p-0.5 rounded transition-all cursor-pointer"
              :class="filterAppStatus === 'approved' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"
              title="Approved"
            >
              <FileCheck class="w-4 h-4 text-green-500" />
            </button>
            <button 
              @click="filterAppStatus = 'rejected'; handleSearch()" 
              class="p-0.5 rounded transition-all cursor-pointer"
              :class="filterAppStatus === 'rejected' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"
              title="Rejected"
            >
              <FileX class="w-4 h-4 text-red-500" />
            </button>
            <button 
              @click="filterAppStatus = 'revised'; handleSearch()" 
              class="p-0.5 rounded transition-all cursor-pointer"
              :class="filterAppStatus === 'revised' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"
              title="Revised"
            >
              <FileWarning class="w-4 h-4 text-orange-500" />
            </button>
          </div>
        </div>

        <button
          @click="openAddModal"
          class="px-4 py-2 bg-bfs-gold text-white text-xs font-semibold rounded-lg hover:bg-[#C2A05B] transition-colors shadow-sm flex items-center gap-1.5 ml-auto"
        >
          <Plus class="w-3.5 h-3.5" /> New PO
        </button>
      </div>
    </div>
    
    <!-- Loading -->
    <div v-if="store.loading && !store.pos.length" class="flex justify-center py-16">
      <Loader2 class="w-6 h-6 animate-spin text-bfs-gold" />
    </div>
    
    <!-- Table List -->
    <div v-else-if="store.pos.length" class="border border-gray-200 rounded-xl overflow-hidden bg-white shadow-sm">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          
          <thead>
            <tr class="bg-gray-50 border-b border-gray-200 text-[11px] font-semibold text-gray-600 uppercase tracking-wider">
              <th class="py-3 px-4 w-12 text-center">No.</th>
              <th class="py-3 px-4">PO Number</th>
              <th class="py-3 px-4">Vendor</th>
              <th class="py-3 px-4">RAP Name</th>
              <th class="py-3 px-4">PO Date</th>
              <th class="py-3 px-4">Pick Up Date</th>
              <th class="py-3 px-4">Notes</th>
              <th class="py-3 px-4 text-center">Document Status</th>
              <th class="py-3 px-4 text-center">Approval</th>
              <th class="py-3 px-4 text-center">Invoiced</th>
              <th class="py-3 px-4 text-center">Active</th>
              <th class="py-3 px-4 text-center">Close</th>
              <th class="py-3 px-4 text-center">Allow Pre Year</th>
              <th class="py-3 px-4 text-right">PO Amount</th>
              <th class="py-3 px-4 w-20 text-right">Actions</th>
            </tr>
          </thead>

          
          <tbody class="divide-y divide-gray-100">
            <tr v-for="(po, idx) in store.pos" :key="po.id" class="hover:bg-yellow-50/20 transition-colors text-xs text-gray-700">
              <td class="py-3 px-4 text-center font-medium text-gray-400">{{ idx + 1 }}.</td>
              <td class="py-3 px-4 font-mono text-gray-600 cursor-pointer hover:text-bfs-navy font-semibold" @click="openEditModal(po)">{{ po.po_number }}</td>
              <td class="py-3 px-4 truncate max-w-[150px]" :title="po.vendor_name">{{ po.vendor_name || '-' }}</td>
              <td class="py-3 px-4 truncate max-w-[150px]" :title="po.rap_name">{{ po.rap_name || '-' }}</td>
              <td class="py-3 px-4">{{ formatDate(po.po_date) }}</td>
              <td class="py-3 px-4">{{ formatDate(po.etd) }}</td>
              <td class="py-3 px-4 truncate max-w-[150px]" :title="po.notes">{{ po.notes || '-' }}</td>
              
              <td class="py-3 px-4 text-center">
                <div class="inline-flex items-center justify-center p-1 rounded-md" :title="po.document_status">
                  <Folder v-if="po.document_status === 'draft'" class="w-4.5 h-4.5 text-amber-500 fill-amber-500/10" />
                  <FolderOpen v-else-if="po.document_status === 'open'" class="w-4.5 h-4.5 text-blue-500 fill-blue-500/10" />
                  <FolderCheck v-else-if="po.document_status === 'close'" class="w-4.5 h-4.5 text-green-500 fill-green-500/10" />
                  <Folder v-else class="w-4.5 h-4.5 text-gray-500 fill-gray-500/10" />
                </div>
              </td>
              <td class="py-3 px-4 text-center">
                <div class="inline-flex items-center justify-center p-1 rounded-md" :title="po.approval_status">
                  <FileText v-if="po.approval_status === 'draft'" class="w-4.5 h-4.5 text-gray-400" />
                  <FileClock v-else-if="po.approval_status === 'awaiting'" class="w-4.5 h-4.5 text-bfs-gold animate-pulse" />
                  <FileCheck v-else-if="po.approval_status === 'approved'" class="w-4.5 h-4.5 text-green-500" />
                  <FileX v-else-if="po.approval_status === 'rejected'" class="w-4.5 h-4.5 text-red-500" />
                  <FileWarning v-else-if="po.approval_status === 'revised'" class="w-4.5 h-4.5 text-orange-500" />
                </div>
              </td>
              <td class="py-3 px-4 text-center">
                <span v-if="po.document_status === 'invoiced'" class="text-green-500 font-bold text-base">✓</span>
                <span v-else class="text-red-500 font-bold text-base">✗</span>
              </td>
              <td class="py-3 px-4 text-center">
                <span v-if="po.is_active" class="text-green-500 font-bold text-base">✓</span>
                <span v-else class="text-red-500 font-bold text-base">✗</span>
              </td>
              <td class="py-3 px-4 text-center">
                <div class="flex items-center justify-center gap-1">
                  <span v-if="po.is_close" class="text-green-500 font-bold text-base">&#10003;</span>
                  <span v-else class="text-red-500 font-bold text-base">&#10007;</span>
                  <div v-if="po.is_close && po.close_reason" class="relative group flex items-center justify-center">
                    <AlertCircle class="w-4 h-4 text-pink-500 cursor-help" />
                    <div class="absolute bottom-full mb-1 hidden group-hover:block w-max max-w-xs bg-pink-500 text-white text-xs px-2 py-1 rounded shadow-lg z-50">
                      {{ po.close_reason }}
                      <div class="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-pink-500"></div>
                    </div>
                  </div>
                </div>
              </td>
              <td class="py-3 px-4 text-center">
                <span v-if="po.allow_previous_year_budget" class="text-green-500 font-bold text-base">✓</span>
                <span v-else class="text-red-500 font-bold text-base">✗</span>
              </td>
              <td class="py-3 px-4 text-right font-semibold text-bfs-navy">
                IDR. {{ formatCurrency(po.grand_total) }}
              </td>
              <td class="py-3 px-4 text-right">
                <div class="flex justify-end gap-1.5">
                  <button @click="openPrintPreview(po)" class="p-1 text-gray-400 hover:text-bfs-navy transition-colors" title="Print">
                    <Printer class="w-3.5 h-3.5" />
                  </button>
                  <button @click="openEditModal(po)" class="p-1 text-gray-400 hover:text-bfs-gold transition-colors" title="Edit">
                    <Pencil class="w-3.5 h-3.5" />
                  </button>
                  <button v-if="po.document_status === 'draft' && !po.allow_previous_year_budget" @click="allowPreviousYearBudget(po)" class="p-1 text-gray-400 hover:text-green-500 transition-colors" title="Allow Previous Year Budget RAP">
                    <Unlock class="w-3.5 h-3.5" />
                  </button>
                  <button v-if="po.document_status === 'draft'" @click="deletePO(po.id)" class="p-1 text-gray-400 hover:text-red-500 transition-colors" title="Delete">
                    <Trash2 class="w-3.5 h-3.5" />
                  </button>
                  <template v-if="po.approval_status === 'approved'">
                    <button v-if="!po.is_close" @click="manualClose(po)" class="p-1 text-gray-400 hover:text-pink-500 transition-colors" title="Manual Close">
                      <FileX class="w-3.5 h-3.5" />
                    </button>
                    <button v-else-if="!(po.close_reason && (po.close_reason.toLowerCase().includes('kadaluarsa') || po.close_reason.toLowerCase().includes('expired')))" @click="manualClose(po)" class="p-1 text-gray-400 hover:text-green-500 transition-colors" title="Open PO">
                      <FileCheck class="w-3.5 h-3.5" />
                    </button>
                  </template>
                </div>
              </td>
            </tr>
          </tbody>

        </table>
      </div>
    </div>
    
    <div v-else class="py-16 text-center text-gray-400">
      <div class="flex flex-col items-center justify-center">
        <FileText class="w-12 h-12 text-gray-200 mb-2" />
        <p>No records found.</p>
      </div>
    </div>

    <!-- Add/Edit PO Form Modal -->
    <Teleport to="body">
      <PurchaseOrderFormModal 
        v-model:show="modal.show" 
        :mode="modal.mode" 
        :edit-id="modal.editId" 
        @saved="handleSearch" 
      />
    </Teleport>


    <!-- Print Preview Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="printModal.show" class="fixed inset-0 z-50 overflow-y-auto print-modal-overlay">
          <div class="fixed inset-0 bg-black/40 print:hidden" @click="printModal.show = false" />
          
          <div class="flex min-h-full items-start justify-center p-4 py-8 print:p-0">
            <div class="relative bg-white shadow-2xl w-full max-w-[210mm] min-h-[297mm] z-10 print-modal-container" @click.stop>
              
              <!-- Web-only Header -->
              <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100 print:hidden sticky top-0 bg-white z-20 shadow-sm">
                <h3 class="text-base font-bold text-gray-800 flex items-center gap-2">
                  <Printer class="w-5 h-5 text-bfs-gold" />
                  Print Preview: {{ printModal.po?.po_number }}
                </h3>
                <div class="flex gap-2">
                  <button @click="printDocument" class="btn-primary text-sm px-4 flex items-center gap-2 shadow-md">
                    <Printer class="w-4 h-4" /> Print Document
                  </button>
                  <button @click="printModal.show = false" class="text-gray-400 hover:text-gray-600 bg-gray-100 hover:bg-gray-200 p-2 rounded-lg transition-colors">
                    <X class="w-5 h-5" />
                  </button>
                </div>
              </div>

              <!-- Print Content -->
              <div class="p-[10mm] print:p-0 text-black bg-white font-sans text-[11px] relative">
                <!-- Header: Company Info and Logo -->
                <div class="flex justify-between items-start mb-4 border-b-2 border-black pb-4">
                  <div class="flex-1 pr-4">
                    <h1 class="text-base font-black uppercase mb-1">{{ orgStore.company?.company_name || 'Company Name' }}</h1>
                    <div class="text-[10px] leading-snug whitespace-pre-line max-w-sm">{{ printAddress }}</div>
                    <div class="text-[10px] mt-1">
                      <span v-if="orgStore.company?.phone">Phone: {{ orgStore.company.phone }}<br/></span>
                      <span v-if="orgStore.company?.fax">Fax: {{ orgStore.company.fax }}<br/></span>
                      <span v-if="orgStore.company?.email">Email: {{ orgStore.company.email }}<br/></span>
                    </div>
                  </div>
                  <div class="w-28 h-16 ml-4 flex items-start justify-end">
                    <img v-if="orgStore.company?.logo_url" :src="orgStore.company.logo_url" alt="Logo" class="max-w-full max-h-full object-contain" />
                  </div>
                </div>

                <!-- PO Title -->
                <div class="text-center mb-6">
                  <h2 class="text-lg font-extrabold uppercase underline tracking-wider">Purchase Order</h2>
                  <p class="text-[11px] mt-1">{{ printModal.po?.po_number }}</p>
                </div>

                <!-- PO Meta Info -->
                <div class="flex justify-between text-[11px] mb-6">
                  <!-- Vendor Info -->
                  <div class="w-1/2 pr-4">
                    <p class="font-bold underline mb-1">Order To:</p>
                    <table class="w-full">
                      <tr><td class="w-16 align-top">Name</td><td class="w-3 align-top">:</td><td class="align-top">{{ printModal.po?.vendor_name || '-' }}</td></tr>
                      <tr><td class="w-16 align-top">Company</td><td class="w-3 align-top">:</td><td class="align-top">{{ printModal.po?.vendor_name || '-' }}</td></tr>
                      <tr><td class="w-16 align-top">Telp</td><td class="w-3 align-top">:</td><td class="align-top">{{ printModal.po?.vendor_phone || '-' }}</td></tr>
                      <tr><td class="w-16 align-top">Alamat</td><td class="w-3 align-top">:</td><td class="align-top">{{ printModal.po?.vendor_address || '-' }}</td></tr>
                    </table>
                  </div>
                  <!-- PO Details -->
                  <div class="w-1/2 pl-4">
                    <table class="w-full">
                      <tr><td class="w-24 align-top">Date</td><td class="w-3 align-top">:</td><td class="align-top">{{ formatDatePrint(printModal.po?.po_date) }}</td></tr>
                      <tr><td class="w-24 align-top">Currency</td><td class="w-3 align-top">:</td><td class="align-top">{{ printModal.po?.po_currency || 'IDR' }}</td></tr>
                      <tr><td class="w-24 align-top">Amount</td><td class="w-3 align-top">:</td><td class="align-top">{{ formatCurrencyRaw(printGrandTotal) }}</td></tr>
                      <tr><td colspan="3" class="h-2"></td></tr>
                      <tr><td class="w-24 align-top">RAP / Project</td><td class="w-3 align-top">:</td><td class="align-top">{{ printModal.po?.rap_number || printModal.po?.project_name || '-' }}</td></tr>
                      <tr><td class="w-24 align-top">Dept / SBU</td><td class="w-3 align-top">:</td><td class="align-top">{{ printModal.po?.department_name || '-' }}</td></tr>
                    </table>
                  </div>
                </div>

                <!-- Items Table -->
                <div class="mb-4">
                  <table class="w-full border-collapse border-t-[2px] border-b-[2px] border-black text-[11px]">
                    <thead>
                      <tr class="border-b-[2px] border-black">
                        <th class="py-1 px-1 w-8 text-center font-bold">NO</th>
                        <th class="py-1 px-2 text-left font-bold">Description</th>
                        <th class="py-1 px-2 w-12 text-center font-bold">Qty</th>
                        <th class="py-1 px-2 w-12 text-center font-bold">Unit</th>
                        <th class="py-1 px-2 w-20 text-right font-bold">Unit Price</th>
                        <th class="py-1 px-2 w-16 text-right font-bold">Tax %</th>
                        <th class="py-1 px-2 w-16 text-right font-bold">Discount</th>
                        <th class="py-1 px-2 w-24 text-right font-bold">Amount</th>
                      </tr>
                    </thead>
                    <tbody class="align-top">
                      <tr v-for="(item, idx) in printDetails" :key="idx" class="border-b border-gray-200 last:border-0">
                        <td class="py-1.5 px-1 text-center">{{ idx + 1 }}</td>
                        <td class="py-1.5 px-2">
                          <div class="font-medium">{{ item.item_name || item.item || '-' }}</div>
                          <div class="text-[9px] text-gray-500 mt-0.5" v-if="item.notes">{{ item.notes }}</div>
                        </td>
                        <td class="py-1.5 px-2 text-center">{{ item.quantity }}</td>
                        <td class="py-1.5 px-2 text-center">{{ item.unit_name || 'Unit' }}</td>
                        <td class="py-1.5 px-2 text-right">{{ formatCurrencyRaw(item.unit_price) }}</td>
                        <td class="py-1.5 px-2 text-right">{{ parseFloat(getItemTaxRate(item)).toFixed(2) }}%</td>
                        <td class="py-1.5 px-2 text-right">{{ formatCurrencyRaw(item.discount_amount || 0) }}</td>
                        <td class="py-1.5 px-2 text-right">{{ formatCurrencyRaw(getLineTotal(item)) }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                <!-- Term and Condition, Term of Payment, Notes -->
                <div class="flex justify-between text-[11px] mb-8">
                  <div class="w-7/12 pr-4 space-y-4">
                    <div>
                      <p class="font-medium">Term and Condition :</p>
                      <p class="whitespace-pre-line text-[10px]">{{ printModal.po?.term_and_condition || '-' }}</p>
                    </div>
                    <div>
                      <p class="font-medium">Term of Payment :</p>
                      <p class="whitespace-pre-line text-[10px]">{{ printModal.po?.payment_terms?.length ? printModal.po.payment_terms.map(t => `- ${t.term_desc} (${t.duration_due || '0 HARI'}) ${t.duration_due_percent}%`).join('\n') : '- (30 days) full 100.00 %' }}</p>
                    </div>
                    <div>
                      <p class="font-medium text-[10px]">Payment To :</p>
                      <p class="whitespace-pre-line text-[11px]">{{ printModal.po?.vendor_bank || '-' }} {{ printModal.po?.vendor_account_number || '-' }} an. {{ printModal.po?.vendor_name || '-' }}</p>
                    </div>
                    <div>
                      <p class="font-medium">Notes :</p>
                      <p class="whitespace-pre-line text-[10px]">{{ printModal.po?.notes || '-' }}</p>
                    </div>
                    <div class="mt-4 pt-4">
                      <span class="font-medium text-[10px]">In Word : </span> <span class="capitalize italic text-[10px]">{{ numberToWordsEn(printGrandTotal) }} {{ printModal.po?.po_currency || 'Rupiahs' }}</span>
                    </div>
                  </div>
                  
                  <div class="w-5/12 pl-4 flex flex-col justify-end pb-4">
                    <table class="w-full text-right">
                      <tr><td class="py-0.5">Subtotal</td><td class="w-4">:</td><td class="py-0.5 w-24">{{ formatCurrencyRaw(printDetails.reduce((sum, item) => sum + (parseFloat(item.quantity) * parseFloat(item.unit_price) || 0), 0)) }}</td></tr>
                      <tr><td class="py-0.5">Disc</td><td class="w-4">:</td><td class="py-0.5 w-24">{{ formatCurrencyRaw(printModal.po?.total_discount || 0) }}</td></tr>
                      <tr><td class="py-0.5">Total Tax</td><td class="w-4">:</td><td class="py-0.5 w-24">{{ formatCurrencyRaw(printModal.po?.total_tax || 0) }}</td></tr>
                      <tr><td class="py-1 font-bold text-[13px] pt-2">Total Amount</td><td class="w-4 font-bold pt-2">:</td><td class="py-1 font-bold text-[13px] pt-2">{{ formatCurrencyRaw(printGrandTotal) }}</td></tr>
                    </table>
                  </div>
                </div>

                <!-- Signatures -->
                <div class="flex justify-between text-[10px] mt-12 mb-8">
                  <div class="w-56 text-center">
                    <table class="w-full border border-black">
                      <tbody>
                        <tr class="border-b border-black"><td class="py-1 text-[9px]">Accepted By</td></tr>
                        <tr class="border-b border-black"><td class="py-1">Supplier</td></tr>
                        <tr><td class="h-20 align-middle p-1"></td></tr>
                        <tr class="border-t border-black"><td class="py-1">{{ printModal.po?.vendor_name || '-' }}</td></tr>
                      </tbody>
                    </table>
                  </div>
                  <div class="w-56 text-center">
                    <table class="w-full border border-black">
                      <tbody>
                        <tr class="border-b border-black"><td class="py-1 text-[9px]">Approved By</td></tr>
                        <tr class="border-b border-black"><td class="py-1">Direktur</td></tr>
                        <tr>
                          <td class="h-20 align-middle p-1 relative">
                            <template v-for="sig in printModal.signatures" :key="sig.id">
                              <img v-if="sig.is_signed" :src="sig.signature_image" class="max-h-16 max-w-full mx-auto object-contain" />
                            </template>
                          </td>
                        </tr>
                        <tr class="border-t border-black"><td class="py-1 font-medium">
                          <span v-for="(sig, i) in printModal.signatures" :key="'name-'+sig.id">
                            {{ sig.user_name }}<span v-if="i < printModal.signatures.length - 1">, </span>
                          </span>
                        </td></tr>
                      </tbody>
                    </table>
                  </div>
                </div>

                <!-- Footer -->
                <div class="text-[8px] flex justify-between">
                  <span>REV#03</span>
                  <span>{{ formatDatePrint(new Date()) }}</span>
                  <span>FRM-PRC-02-01</span>
                </div>
                <div class="text-[8px] mt-1 font-bold leading-tight pt-2">
                  *Dilarang keras menyebarluaskan sebagian atau seluruh konten dari dokumen ini untuk kepentingan apapun, tanpa seijin penerbit dokumen ini, informasi yang terdapat didalamnya sangat rahasia dan atau dilindungi oleh hukum.
                </div>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </Panel>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import Swal from 'sweetalert2'
import { 
  Search, Plus, Loader2, Edit3, Trash2, Send, Pencil, Printer, CheckSquare,
  Folder, FolderOpen, FolderCheck,
  FileText, FileClock, FileCheck, FileX, FileWarning, X, AlertCircle, Save, Unlock
} from 'lucide-vue-next'
import api from '../../services/api'
import { useAuthStore } from '../../stores/auth'
import { usePurchaseOrderStore } from '../../stores/purchaseOrder'
import { usePurchaseStore } from '../../stores/purchase'
import { useProjectsStore } from '../../stores/projects'
import { useOrganizationStore } from '../../stores/organization'
import { useApprovalRequestStore } from '../../stores/approvalRequest'
import PurchaseOrderFormModal from '../../components/purchase/PurchaseOrderFormModal.vue'
import Panel from '../../components/Panel.vue'
import FormField from '../../components/FormField.vue'
import SearchableSelect from '../../components/SearchableSelect.vue'

const authStore = useAuthStore()
const orgStore = useOrganizationStore()
const approvalStore = useApprovalRequestStore()
const store = usePurchaseOrderStore()
const purchaseStore = usePurchaseStore()
const projectStore = useProjectsStore()



// --- POINT POEVIEW ---
const printModal = ref({
  show: false,
  pr: null,
  signatures: [],
  isLoadingSignatures: false
})

const printDetails = ref([])

async function openPrintPreview(po) {
  printModal.value.po = po
  printModal.value.show = true
  printModal.value.signatures = []
  printDetails.value = []
  
  if (!orgStore.company) {
    orgStore.fetchCompany()
  }
  
  // Fetch full details
  try {
    const fullPo = await store.fetchPODetails(po.id)
    printModal.value.po = fullPo
    printDetails.value = fullPo.details || []
  } catch (e) {
    console.error('Failed to fetch print details', e)
  }

  if (po.document_status !== 'draft') {
    printModal.value.isLoadingSignatures = true
    try {
      const sigs = await approvalStore.fetchSignatures('PR', po.id)
      printModal.value.signatures = sigs
    } catch (e) {
      console.error(e)
      printModal.value.signatures = []
    } finally {
      printModal.value.isLoadingSignatures = false
    }
  }
}

const printAddress = computed(() => {
  const addr1 = orgStore.company?.company_address || 'Jl. Raya Hankam No. 17 RT. 003 RW. 000 Kel. Jatirahayu Kec. Pondok Melati Kab. Bekasi Jawa Barat,'
  const addr2 = orgStore.company?.company_address2 || ''
  if (addr2 && addr2.trim().toLowerCase() !== addr1.trim().toLowerCase()) {
    return `${addr1}
${addr2}`
  }
  return addr1
})

function printDocument() {
  window.print()
}

function formatDatePrint(dateStr) {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

function formatCurrencyRaw(value) {
  if (value == null) return '0.00'
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value)
}

const taxMap = {
  'none': { rate: 0, type: 'none' },
  'non': { rate: 0, type: 'none' },
  'pph_23_rate_15': { rate: 15, type: 'deduction' },
  'pph_23_rate_2': { rate: 2, type: 'deduction' },
  'pph_23_rate_4': { rate: 4, type: 'deduction' },
  'pph_23_rate_4_5': { rate: 4.5, type: 'deduction' },
  'pph_23_rate_7_5': { rate: 7.5, type: 'deduction' },
  'pph_4_2_rate_10': { rate: 10, type: 'deduction' },
  'pph_4_2_rate_2': { rate: 2, type: 'deduction' },
  'pph_4_2_rate_3': { rate: 3, type: 'deduction' },
  'pph_4_2_rate_4': { rate: 4, type: 'deduction' },
  'ppn_01': { rate: 1, type: 'addition' },
  'ppn_10': { rate: 10, type: 'addition' },
  'ppn_10_euro': { rate: 10, type: 'addition' },
  'ppn_11': { rate: 11, type: 'addition' },
  'ppn_15': { rate: 15, type: 'addition' }
}

function getItemTaxRate(item) {
  let rate = 0
  const t1 = taxMap[item.tax1] || { rate: 0, type: 'none' }
  const t2 = taxMap[item.tax2] || { rate: 0, type: 'none' }
  if (t1.type === 'addition') rate += t1.rate
  if (t2.type === 'addition') rate += t2.rate
  return rate
}

function getLineTotal(item) {
  const baseAmount = parseFloat(item.amount) || ((parseFloat(item.quantity) * parseFloat(item.unit_price)) - parseFloat(item.discount_amount || 0)) || 0
  if (printModal.value.po?.ppn) return baseAmount
  return baseAmount + parseFloat(item.tax_amount || 0)
}

const printGrandTotal = computed(() => {
  const po = printModal.value.po
  if (po) {
    return parseFloat(po.grand_total || 0) + parseFloat(po.total_tax || 0) - parseFloat(po.total_deduction || 0)
  }
  return printDetails.value.reduce((sum, item) => sum + (parseFloat(item.amount) || parseFloat(item.quantity) * parseFloat(item.unit_price) || 0), 0)
})

function numberToWordsEn(n) {
  if (n === 0) return 'Zero';
  if (typeof n === 'string') n = parseFloat(n);
  n = Math.floor(n);
  
  const a = ['','One','Two','Three','Four','Five','Six','Seven','Eight','Nine','Ten','Eleven','Twelve','Thirteen','Fourteen','Fifteen','Sixteen','Seventeen','Eighteen','Nineteen'];
  const b = ['','','Twenty','Thirty','Forty','Fifty','Sixty','Seventy','Eighty','Ninety'];
  
  function convertToWords(num) {
    if (num < 20) return a[num];
    if (num < 100) return b[Math.floor(num / 10)] + (num % 10 ? ' ' + a[num % 10] : '');
    if (num < 1000) return a[Math.floor(num / 100)] + ' Hundred' + (num % 100 ? ' ' + convertToWords(num % 100) : '');
    if (num < 1000000) return convertToWords(Math.floor(num / 1000)) + ' Thousand' + (num % 1000 ? ' ' + convertToWords(num % 1000) : '');
    if (num < 1000000000) return convertToWords(Math.floor(num / 1000000)) + ' Million' + (num % 1000000 ? ' ' + convertToWords(num % 1000000) : '');
    return convertToWords(Math.floor(num / 1000000000)) + ' Billion' + (num % 1000000000 ? ' ' + convertToWords(num % 1000000000) : '');
  }
  
  return convertToWords(n);
}

// --- END POINT POEVIEW ---

// --- LIST STATE ---
const today = new Date()
const firstDay = new Date(today.getFullYear(), today.getMonth(), 1)
const lastDay = new Date(today.getFullYear(), today.getMonth() + 1, 0)

const formatDateStr = (d) => d.toISOString().split('T')[0]

const searchQuery = ref('')
const filterItemCategory = ref('')
const filterDateFrom = ref(formatDateStr(firstDay))
const filterDateTo = ref(formatDateStr(lastDay))

const filterDocStatus = ref('')
const filterAppStatus = ref('')

function handleSearch() {
  console.log("handleSearch called with filters:", {
    search: searchQuery.value,
    po_type: filterItemCategory.value,
    document_status: filterDocStatus.value,
    approval_status: filterAppStatus.value,
    start_date: filterDateFrom.value,
    end_date: filterDateTo.value,
  });
  store.fetchPOs({
    search: searchQuery.value,
    po_type: filterItemCategory.value,
    document_status: filterDocStatus.value,
    approval_status: filterAppStatus.value,
    start_date: filterDateFrom.value,
    end_date: filterDateTo.value,
  }).then(res => {
    console.log("fetchPOs success. store.pos:", store.pos);
  }).catch(err => {
    console.error("fetchPOs error:", err);
  })
}

function handleResetFilters() {
  searchQuery.value = ''
  filterItemCategory.value = ''
  filterDateFrom.value = formatDateStr(firstDay)
  filterDateTo.value = formatDateStr(lastDay)
  filterDocStatus.value = ''
  filterAppStatus.value = ''
  handleSearch()
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' })
}

function formatCurrency(value) {
  if (value == null) return 'Rp 0'
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value)
}

const deletePO = async (id) => {
  const result = await Swal.fire({
    title: 'Are you sure?',
    text: "You won't be able to revert this!",
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#3085d6',
    cancelButtonColor: '#d33',
    confirmButtonText: 'Yes, delete it!'
  })
  if (!result.isConfirmed) return
  
  try {
    await store.deletePO(id)
    handleSearch()
    Swal.fire('Deleted!', 'PO has been deleted.', 'success')
  } catch (err) {
    Swal.fire('Error', store.error || 'Failed to delete PO', 'error')
  }
}

const allowPreviousYearBudget = async (po) => {
  const result = await Swal.fire({
    title: 'Are you sure?',
    text: `Allow PO ${po.po_number} to use previous year budget?`,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonText: 'Yes, allow it!'
  })
  if (!result.isConfirmed) return

  try {
    const response = await api.post(`/purchase/po/${po.id}/allow-previous-year/`)
    Swal.fire('Success', response.data.message || 'Permission granted', 'success')
    handleSearch()
  } catch (err) {
    Swal.fire('Error', err.response?.data?.detail || 'Failed to grant permission', 'error')
  }
}


onMounted(() => {
  handleSearch()
})

// --- MODAL & FORM STATE ---
const modal = ref({
  show: false,
  mode: 'add',
  editId: null
})

function openAddModal() {
  modal.value.mode = 'add'
  modal.value.editId = null
  modal.value.show = true
}

async function manualClose(po) {
  if (po.is_close) {
    const confirm = await Swal.fire({
      title: 'Open PO?',
      text: 'Anda akan membuka kembali PO ini.',
      icon: 'question',
      showCancelButton: true,
      confirmButtonColor: '#0f172a',
      cancelButtonColor: '#ef4444'
    })
    
    if (confirm.isConfirmed) {
      try {
        await store.manualClosePO(po.id, { action: 'open' })
        if (!store.error) {
          Swal.fire('Success', 'PO berhasil dibuka kembali.', 'success')
          handleSearch()
        } else {
          Swal.fire('Error', store.error, 'error')
        }
      } catch (err) {
        Swal.fire('Error', 'Gagal memproses aksi ini.', 'error')
      }
    }
    return
  }

  const { value: reason } = await Swal.fire({
    title: 'Manual Close PO',
    input: 'text',
    inputLabel: 'Alasan penutupan manual:',
    inputPlaceholder: 'Masukkan alasan...',
    showCancelButton: true,
    confirmButtonColor: '#0f172a',
    cancelButtonColor: '#ef4444',
    inputValidator: (value) => {
      if (!value) return 'Alasan harus diisi!'
    }
  })

  if (reason) {
    try {
      await store.manualClosePO(po.id, { close_reason: reason })
      if (!store.error) {
        Swal.fire('Success', 'PO berhasil diclose secara manual.', 'success')
        handleSearch()
      } else {
        Swal.fire('Error', store.error, 'error')
      }
    } catch (err) {
      Swal.fire('Error', 'Gagal memproses manual close.', 'error')
    }
  }
}

function openEditModal(po) {
  modal.value.mode = 'edit'
  modal.value.editId = po.id
  modal.value.show = true
}
</script>
<style scoped>
@media print {
  @page {
    size: A4;
    margin: 10mm;
  }
  .print-modal-overlay {
    position: static !important;
    background: none !important;
  }
  .print-modal-container {
    position: absolute !important;
    left: 0 !important;
    top: 0 !important;
    width: 210mm !important;
    max-width: 210mm !important;
    height: auto !important;
    max-height: none !important;
    border: none !important;
    box-shadow: none !important;
    background: white !important;
    display: flex !important;
    flex-direction: column !important;
    overflow: visible !important;
  }
}
</style>
