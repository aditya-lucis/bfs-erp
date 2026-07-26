<template>
  <Panel title="List of Cash Book Entry" subtitle="Finance | List of Cash Book Entry">
    
    <!-- Top Filter Section (Sokka ERP Style) -->
    <div class="bg-gradient-to-br from-gray-50 to-gray-100/80 border border-gray-200/80 rounded-xl p-4 mb-6 shadow-sm">
      
      <!-- Row 1: Cash Book Type & Status -->
      <div class="flex flex-wrap items-center gap-6 pb-3 border-b border-gray-200/60 mb-3">
        <div class="flex items-center gap-2">
          <label class="text-xs font-bold text-gray-700">Cash Book Type :</label>
          <select 
            v-model="filterType" 
            @change="handleTypeChange"
            class="border border-gray-300 rounded-lg px-3 py-1.5 bg-white text-xs font-semibold text-bfs-navy shadow-sm focus:ring-2 focus:ring-bfs-navy focus:border-transparent outline-none cursor-pointer min-w-[150px]"
          >
            <option value="Cash Receipt">Cash Receipt</option>
            <option value="Bank Receipt">Bank Receipt</option>
            <option value="Cash Payment">Cash Payment</option>
            <option value="Bank Payment">Bank Payment</option>
          </select>
        </div>

        <div class="flex items-center gap-2">
          <label class="text-xs font-bold text-gray-700">Status :</label>
          <select 
            v-model="filterStatus" 
            @change="handleSearch"
            class="border border-gray-300 rounded-lg px-3 py-1.5 bg-white text-xs font-medium text-gray-700 shadow-sm focus:ring-2 focus:ring-bfs-navy focus:border-transparent outline-none cursor-pointer"
          >
            <option value="Active">Active</option>
            <option value="All">All</option>
            <option value="Void">Void</option>
          </select>
        </div>
      </div>

      <!-- Row 2: Field Search & Show All -->
      <div class="flex flex-wrap items-center gap-3 pb-3 border-b border-gray-200/60 mb-3">
        <select 
          v-model="searchField"
          class="border border-gray-300 rounded-lg px-2.5 py-1.5 bg-white text-xs font-medium text-gray-700 shadow-sm focus:ring-2 focus:ring-bfs-navy outline-none"
        >
          <option value="Document No">Document No</option>
          <option value="Voucher No">Voucher No</option>
          <option value="Payee">Payee / Payer</option>
          <option value="Description">Description</option>
          <option value="Invoice No">Invoice No</option>
          <option value="Payment Request">Payment Request</option>
        </select>

        <select 
          v-model="searchCondition"
          class="border border-gray-300 rounded-lg px-2.5 py-1.5 bg-white text-xs font-medium text-gray-700 shadow-sm focus:ring-2 focus:ring-bfs-navy outline-none"
        >
          <option value="Any Part of Field">Any Part of Field</option>
          <option value="Exact Match">Exact Match</option>
          <option value="Starts With">Starts With</option>
        </select>

        <div class="relative flex-1 min-w-[200px] max-w-md">
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Search keyword..." 
            class="w-full border border-gray-300 rounded-lg px-3 py-1.5 text-xs bg-white shadow-sm focus:ring-2 focus:ring-bfs-navy focus:border-transparent outline-none"
            @keyup.enter="handleSearch"
          />
        </div>

        <select 
          v-model="searchCategory"
          class="border border-gray-300 rounded-lg px-2.5 py-1.5 bg-white text-xs font-medium text-gray-700 shadow-sm focus:ring-2 focus:ring-bfs-navy outline-none"
        >
          <option value="NONE">NONE</option>
        </select>

        <button 
          @click="handleSearch"
          class="px-3.5 py-1.5 bg-bfs-navy hover:bg-bfs-navy-dark text-white text-xs font-semibold rounded-lg shadow-sm transition-all flex items-center gap-1.5 cursor-pointer"
        >
          <Search class="w-3.5 h-3.5" /> Search
        </button>

        <button 
          @click="handleShowAll"
          class="px-3.5 py-1.5 bg-white border border-gray-300 hover:bg-gray-100 text-gray-700 text-xs font-semibold rounded-lg shadow-sm transition-all cursor-pointer"
        >
          Show All
        </button>
      </div>

      <!-- Row 3: Date Filter & Sokka Icon Status Filters -->
      <div class="flex flex-wrap items-center justify-between gap-4">
        <div class="flex flex-wrap items-center gap-3">
          <label class="text-xs font-bold text-gray-700">Date From</label>
          <input 
            v-model="filterDateFrom" 
            type="date" 
            class="border border-gray-300 rounded-lg px-2.5 py-1 text-xs bg-white shadow-sm font-medium focus:ring-2 focus:ring-bfs-navy outline-none" 
          />
          <label class="text-xs font-bold text-gray-700">Date To</label>
          <input 
            v-model="filterDateTo" 
            type="date" 
            class="border border-gray-300 rounded-lg px-2.5 py-1 text-xs bg-white shadow-sm font-medium focus:ring-2 focus:ring-bfs-navy outline-none" 
          />
          <button 
            @click="handleSearch" 
            class="px-3 py-1.5 bg-bfs-navy hover:bg-bfs-navy-dark text-white text-xs font-semibold rounded-lg shadow-sm transition-all flex items-center gap-1.5 cursor-pointer"
          >
            <Search class="w-3.5 h-3.5" /> Search
          </button>
        </div>

        <!-- Sokka Style Right Status Icons -->
        <div class="flex flex-wrap items-center gap-4">
          <!-- Document Filter Status (Sokka Style) -->
          <div class="border border-gray-200 rounded-lg px-3 py-1.5 relative bg-white flex items-center gap-2 shadow-sm min-h-[38px]">
            <span class="absolute -top-2 left-2 bg-white px-1 text-[9px] font-bold text-gray-500 uppercase tracking-wider whitespace-nowrap">Document Filter Status</span>
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
            <span class="absolute -top-2 left-2 bg-white px-1 text-[9px] font-bold text-gray-500 uppercase tracking-wider whitespace-nowrap">Approval Filter Status</span>
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
              <FileText class="w-4 h-4 text-gray-500 fill-gray-500/10" />
            </button>
            <button 
              @click="filterAppStatus = 'awaiting'; handleSearch()" 
              class="p-0.5 rounded transition-all cursor-pointer"
              :class="filterAppStatus === 'awaiting' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"
              title="In Review / Awaiting"
            >
              <FileClock class="w-4 h-4 text-amber-500 fill-amber-500/10" />
            </button>
            <button 
              @click="filterAppStatus = 'approved'; handleSearch()" 
              class="p-0.5 rounded transition-all cursor-pointer"
              :class="filterAppStatus === 'approved' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"
              title="Approved"
            >
              <FileCheck class="w-4 h-4 text-green-500 fill-green-500/10" />
            </button>
            <button 
              @click="filterAppStatus = 'rejected'; handleSearch()" 
              class="p-0.5 rounded transition-all cursor-pointer"
              :class="filterAppStatus === 'rejected' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"
              title="Rejected"
            >
              <FileX class="w-4 h-4 text-red-500 fill-red-500/10" />
            </button>
            <button 
              @click="filterAppStatus = 'revised'; handleSearch()" 
              class="p-0.5 rounded transition-all cursor-pointer"
              :class="filterAppStatus === 'revised' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"
              title="Revised"
            >
              <FileWarning class="w-4 h-4 text-orange-500 fill-orange-500/10" />
            </button>
          </div>

          <div class="flex items-center gap-1.5 text-xs text-gray-600 font-medium">
            <span>Page:</span>
            <select v-model="currentPage" class="border border-gray-300 rounded px-1.5 py-0.5 bg-white text-xs font-semibold">
              <option :value="1">1</option>
            </select>
            <span>of 1</span>
          </div>
        </div>
      </div>

    </div>

    <!-- Data Table Section (Sokka ERP Layout with Sleek Aesthetics) -->
    <div class="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm mb-6">
      <div class="overflow-x-auto custom-scrollbar">
        <table class="w-full text-left text-xs whitespace-nowrap min-w-max">
          <!-- Table Header -->
          <thead class="bg-gradient-to-r from-gray-50 to-gray-100 text-gray-700 font-bold border-b border-gray-200 shadow-sm">
            <tr>
              <th class="px-3 py-3 border-r border-gray-200 text-center w-14">
                <div class="flex flex-col items-center gap-1">
                  <span>Print</span>
                  <input 
                    type="checkbox" 
                    :checked="isAllSelected" 
                    @change="toggleSelectAll"
                    class="rounded border-gray-300 text-bfs-navy focus:ring-bfs-navy cursor-pointer" 
                  />
                </div>
              </th>
              <th class="px-3 py-3 border-r border-gray-200 text-center w-12">No.</th>
              <th class="px-4 py-3 border-r border-gray-200">
                <div class="flex items-center gap-1 cursor-pointer hover:text-bfs-navy">
                  <span>Document No</span>
                  <span class="text-[10px] text-amber-600">▲</span>
                </div>
              </th>
              <th class="px-3 py-3 border-r border-gray-200">Voucher No</th>
              <th class="px-4 py-3 border-r border-gray-200">
                {{ filterType.includes('Receipt') ? 'Payer' : 'Payee' }}
              </th>
              <th class="px-3 py-3 border-r border-gray-200">
                <div class="flex items-center gap-1 cursor-pointer hover:text-bfs-navy">
                  <span>Date</span>
                  <span class="text-[10px] text-amber-600">▲</span>
                </div>
              </th>
              <th class="px-3 py-3 border-r border-gray-200">Account</th>
              <th class="px-4 py-3 border-r border-gray-200 text-right bg-blue-50/60 text-blue-900">
                {{ filterType }}
              </th>
              <th class="px-4 py-3 border-r border-gray-200">Description</th>
              <th class="px-3 py-3 border-r border-gray-200 text-center">Status</th>
              <th class="px-3 py-3 border-r border-gray-200 text-center">Approval Status</th>
              <th class="px-3 py-3 border-r border-gray-200">Invoice No</th>
              <th class="px-3 py-3 border-r border-gray-200">Payment Request</th>
              <th class="px-3 py-3 text-center">Is Void</th>
            </tr>
          </thead>

          <!-- Table Body -->
          <tbody class="divide-y divide-gray-100">
            <template v-if="filteredData.length > 0">
              <tr 
                v-for="(item, idx) in filteredData" 
                :key="item.id || idx"
                class="hover:bg-blue-50/40 transition-colors align-top group"
                :class="{'bg-red-50/30': item.is_void}"
              >
                <!-- Print Checkbox -->
                <td class="px-3 py-3 border-r border-gray-100 text-center align-middle">
                  <input 
                    type="checkbox" 
                    v-model="selectedItems" 
                    :value="item.id"
                    class="rounded border-gray-300 text-bfs-navy focus:ring-bfs-navy cursor-pointer w-4 h-4" 
                  />
                </td>

                <!-- Number -->
                <td class="px-3 py-3 border-r border-gray-100 text-center font-semibold text-gray-500 align-middle">
                  {{ idx + 1 }}.
                </td>

                <!-- Document No -->
                <td class="px-4 py-3 border-r border-gray-100 align-middle">
                  <a 
                    href="javascript:void(0)" 
                    @click="handleViewDetail(item)"
                    class="font-bold text-blue-600 hover:text-blue-800 hover:underline transition-colors"
                  >
                    {{ item.document_number }}
                  </a>
                </td>

                <!-- Voucher No -->
                <td class="px-3 py-3 border-r border-gray-100 font-medium text-gray-700 align-middle">
                  {{ item.voucher_number || '-' }}
                </td>

                <!-- Payee/Payer (Multiline details) -->
                <td class="px-4 py-3 border-r border-gray-100 align-middle whitespace-pre-line text-gray-700 font-medium leading-relaxed max-w-[220px]">
                  {{ item.payee_display || item.payer_display || '-' }}
                </td>

                <!-- Date -->
                <td class="px-3 py-3 border-r border-gray-100 text-gray-700 align-middle font-medium">
                  {{ formatDate(item.date) }}
                </td>

                <!-- Account -->
                <td class="px-3 py-3 border-r border-gray-100 text-gray-800 font-semibold align-middle">
                  {{ item.account_name || '-' }}
                </td>

                <!-- Amount Column (Cash/Bank Payment or Receipt) -->
                <td class="px-4 py-3 border-r border-gray-100 text-right align-middle bg-blue-50/30 group-hover:bg-blue-50/60 transition-colors">
                  <div class="flex items-center justify-end gap-1.5 font-bold text-gray-900">
                    <span class="text-gray-500 font-semibold text-[10px]">{{ item.currency || 'IDR' }}</span>
                    <span>{{ formatNumber(item.amount) }}</span>
                  </div>
                </td>

                <!-- Description -->
                <td class="px-4 py-3 border-r border-gray-100 text-gray-600 align-middle truncate max-w-[200px]" :title="item.description">
                  {{ item.description || '-' }}
                </td>

                <!-- Document Status (Sokka Icon) -->
                <td class="px-3 py-3 border-r border-gray-100 text-center align-middle">
                  <div class="inline-flex items-center justify-center p-1 rounded hover:bg-gray-100 transition-colors" :title="item.document_status_display || 'Draft'">
                    <Folder v-if="item.document_status === 'draft'" class="w-4 h-4 text-amber-500 fill-amber-500/20" />
                    <FolderOpen v-else-if="item.document_status === 'ready_to_process'" class="w-4 h-4 text-blue-500 fill-blue-500/20" />
                    <FolderCheck v-else-if="item.document_status === 'close'" class="w-4 h-4 text-green-500 fill-green-500/20" />
                    <Folder class="w-4 h-4 text-gray-400 fill-gray-400/20" v-else />
                  </div>
                </td>

                <!-- Approval Status (Sokka Icon) -->
                <td class="px-3 py-3 border-r border-gray-100 text-center align-middle">
                  <div class="inline-flex items-center justify-center p-1 rounded hover:bg-gray-100 transition-colors" :title="item.approval_status_display || 'Approved'">
                    <FileCheck v-if="item.approval_status === 'approved'" class="w-4 h-4 text-green-500 fill-green-500/20" />
                    <FileClock v-else-if="item.approval_status === 'awaiting'" class="w-4 h-4 text-amber-500 fill-amber-500/20" />
                    <FileText v-else-if="item.approval_status === 'draft'" class="w-4 h-4 text-gray-500 fill-gray-500/20" />
                    <FileX v-else-if="item.approval_status === 'rejected'" class="w-4 h-4 text-red-500 fill-red-500/20" />
                    <FileWarning v-else-if="item.approval_status === 'revised'" class="w-4 h-4 text-orange-500 fill-orange-500/20" />
                    <FileCheck class="w-4 h-4 text-green-500 fill-green-500/20" v-else />
                  </div>
                </td>

                <!-- Invoice No -->
                <td class="px-3 py-3 border-r border-gray-100 text-gray-700 font-medium align-middle">
                  {{ item.invoice_number || '-' }}
                </td>

                <!-- Payment Request -->
                <td class="px-3 py-3 border-r border-gray-100 font-semibold text-bfs-navy align-middle">
                  {{ item.payment_request_number || '-' }}
                </td>

                <!-- Is Void -->
                <td class="px-3 py-3 text-center align-middle">
                  <span v-if="item.is_void" class="inline-flex items-center justify-center text-red-600 font-extrabold text-sm" title="Voided">✔</span>
                  <button 
                    v-else 
                    @click="handleToggleVoid(item)" 
                    class="text-red-500 hover:text-red-700 hover:scale-125 transition-all font-extrabold text-base cursor-pointer inline-block" 
                    title="Click to Void"
                  >
                    ✕
                  </button>
                </td>
              </tr>
            </template>

            <!-- Empty State -->
            <tr v-else>
              <td colspan="14" class="px-6 py-16 text-center">
                <div class="flex flex-col items-center justify-center gap-3">
                  <div class="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center border border-gray-200">
                    <Inbox class="w-8 h-8 text-gray-300" />
                  </div>
                  <p class="text-gray-500 text-sm font-semibold">.:: No Record ::.</p>
                  <p class="text-gray-400 text-xs">No {{ filterType }} documents found matching your filter criteria.</p>
                </div>
              </td>
            </tr>
          </tbody>

          <!-- Table Footer Total -->
          <tfoot v-if="filteredData.length > 0" class="bg-gray-50 border-t-2 border-gray-200 font-bold text-gray-700">
            <tr>
              <td colspan="7" class="px-4 py-3 text-right uppercase tracking-wider text-[11px]">Total {{ filterType }}:</td>
              <td class="px-4 py-3 text-right text-blue-900 bg-blue-100/50">
                <div class="flex items-center justify-end gap-1.5 font-extrabold">
                  <span class="text-gray-500 text-[10px]">IDR</span>
                  <span>{{ formatNumber(totalAmount) }}</span>
                </div>
              </td>
              <td colspan="6"></td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>

    <!-- Bottom Actions Toolbar (Sokka ERP Buttons) -->
    <div class="flex flex-wrap items-center justify-between gap-4 pt-2 border-t border-gray-200/60">
      <div class="flex flex-wrap items-center gap-3">
        <button 
          @click="handlePrintToVoucher"
          class="px-4 py-2 bg-white border border-gray-300 hover:bg-gray-100 text-gray-800 text-xs font-bold rounded-lg shadow-sm transition-all cursor-pointer flex items-center gap-1.5"
        >
          <Printer class="w-4 h-4 text-gray-600" />
          Print to Voucher
        </button>

        <button 
          @click="handlePrintThisDocument"
          class="px-4 py-2 bg-white border border-gray-300 hover:bg-gray-100 text-gray-800 text-xs font-bold rounded-lg shadow-sm transition-all cursor-pointer flex items-center gap-1.5"
        >
          <FileText class="w-4 h-4 text-blue-600" />
          Print This Document
        </button>

        <button 
          @click="handleVoidCashBook"
          class="px-4 py-2 bg-white border border-red-300 hover:bg-red-50 text-red-700 text-xs font-bold rounded-lg shadow-sm transition-all cursor-pointer flex items-center gap-1.5"
        >
          <XCircle class="w-4 h-4 text-red-600" />
          Void Cash Book
        </button>
      </div>

      <div>
        <button 
          @click="handleCreateNew"
          class="px-5 py-2 bg-bfs-navy hover:bg-bfs-navy-dark text-white text-xs font-bold rounded-lg shadow-md transition-all cursor-pointer flex items-center gap-1.5"
        >
          + New {{ filterType }}
        </button>
      </div>
    </div>

  </Panel>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Panel from '../../components/Panel.vue'
import api from '../../services/api'
import Swal from 'sweetalert2'
import { 
  Search, 
  Folder, 
  FolderOpen, 
  FolderCheck, 
  FileCheck, 
  FileClock, 
  FileText, 
  FileX, 
  FileWarning, 
  Printer, 
  XCircle, 
  Inbox 
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

// Filter parameters
const filterType = ref(route.query.type || 'Cash Payment')
const filterStatus = ref('Active')
const searchField = ref('Document No')
const searchCondition = ref('Any Part of Field')
const searchQuery = ref('')
const searchCategory = ref('NONE')
const filterDateFrom = ref('2026-01-01')
const filterDateTo = ref('2026-07-31')
const filterDocStatus = ref('')
const filterAppStatus = ref('')
const currentPage = ref(1)

// Selection state
const selectedItems = ref([])

// Sample realistic Sokka legacy data for instant interactive demo
const sampleCashPayments = [
  {
    id: 1,
    document_number: 'CDJ583002601-0014262',
    voucher_number: 'Voucher/001',
    payee_display: 'BCA Kota Bekasi\nKota Bekasi a/c 123456789\na/n Arvi Ramadhan',
    date: '2026-01-13',
    account_name: 'Kas Kecil Pusat',
    amount: 11000000.00,
    currency: 'IDR',
    description: 'Test by Arvi',
    document_status: 'draft',
    approval_status: 'approved',
    invoice_number: 'VIN583002601-0022635',
    payment_request_number: 'CBR583002601-0050729',
    is_void: false
  },
  {
    id: 2,
    document_number: 'CDJ583002601-0014263',
    voucher_number: 'Voucher/001',
    payee_display: 'Tunas a/c . a/n .',
    date: '2026-01-13',
    account_name: 'Kas Kecil Pusat',
    amount: 2220000.00,
    currency: 'IDR',
    description: 'Test by Arvi',
    document_status: 'draft',
    approval_status: 'approved',
    invoice_number: '-',
    payment_request_number: 'CBR583002601-0050730',
    is_void: false
  }
]

const tableData = ref([...sampleCashPayments])

// Fetch from API or fallback to sample demo data
const fetchTableData = async () => {
  try {
    const response = await api.get('/accounting/cashbook-entry/', {
      params: {
        type: filterType.value,
        status: filterStatus.value,
        date_from: filterDateFrom.value,
        date_to: filterDateTo.value,
        doc_status: filterDocStatus.value,
        app_status: filterAppStatus.value,
        search_field: searchField.value,
        search_query: searchQuery.value
      }
    })
    const results = response.data.results || response.data
    if (results && results.length > 0) {
      tableData.value = results
    } else if (filterType.value === 'Cash Payment') {
      tableData.value = [...sampleCashPayments]
    } else {
      tableData.value = []
    }
  } catch (error) {
    // If backend endpoint is not yet created, display sample demo data when Cash Payment is selected
    if (filterType.value === 'Cash Payment') {
      tableData.value = [...sampleCashPayments]
    } else {
      tableData.value = []
    }
  }
}

// Filtered data based on search and status buttons
const filteredData = computed(() => {
  return tableData.value.filter(item => {
    // Document Filter Status
    if (filterDocStatus.value && item.document_status !== filterDocStatus.value) {
      return false
    }
    // Approval Filter Status
    if (filterAppStatus.value && item.approval_status !== filterAppStatus.value) {
      return false
    }
    // Keyword search
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      const docMatch = (item.document_number || '').toLowerCase().includes(query)
      const descMatch = (item.description || '').toLowerCase().includes(query)
      const payeeMatch = (item.payee_display || '').toLowerCase().includes(query)
      const invMatch = (item.invoice_number || '').toLowerCase().includes(query)
      const cbrMatch = (item.payment_request_number || '').toLowerCase().includes(query)
      if (!docMatch && !descMatch && !payeeMatch && !invMatch && !cbrMatch) {
        return false
      }
    }
    return true
  })
})

const totalAmount = computed(() => {
  return filteredData.value.reduce((sum, item) => sum + (parseFloat(item.amount) || 0), 0)
})

const isAllSelected = computed(() => {
  return filteredData.value.length > 0 && selectedItems.value.length === filteredData.value.length
})

const toggleSelectAll = (event) => {
  if (event.target.checked) {
    selectedItems.value = filteredData.value.map(item => item.id)
  } else {
    selectedItems.value = []
  }
}

const handleTypeChange = () => {
  router.replace({ query: { ...route.query, type: filterType.value } })
  handleSearch()
}

const handleSearch = () => {
  selectedItems.value = []
  fetchTableData()
}

const handleShowAll = () => {
  searchQuery.value = ''
  filterDocStatus.value = ''
  filterAppStatus.value = ''
  fetchTableData()
}

const handleViewDetail = (item) => {
  Swal.fire({
    title: item.document_number,
    html: `
      <div class="text-left text-xs space-y-2">
        <p><strong>Voucher No:</strong> ${item.voucher_number || '-'}</p>
        <p><strong>Account:</strong> ${item.account_name}</p>
        <p><strong>Amount:</strong> IDR ${formatNumber(item.amount)}</p>
        <p><strong>Description:</strong> ${item.description}</p>
        <p><strong>Payment Request:</strong> ${item.payment_request_number}</p>
      </div>
    `,
    icon: 'info',
    confirmButtonColor: '#1e293b'
  })
}

const handleToggleVoid = (item) => {
  Swal.fire({
    title: 'Void Cash Book Entry?',
    text: `Are you sure you want to void document ${item.document_number}?`,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#dc2626',
    cancelButtonColor: '#64748b',
    confirmButtonText: 'Yes, Void Document!'
  }).then((result) => {
    if (result.isConfirmed) {
      item.is_void = true
      Swal.fire('Voided!', 'Document has been marked as void.', 'success')
    }
  })
}

const handlePrintToVoucher = () => {
  if (selectedItems.value.length === 0) {
    Swal.fire({
      icon: 'warning',
      title: 'No Selection',
      text: 'Please select at least one document to print voucher.'
    })
    return
  }
  Swal.fire({
    icon: 'success',
    title: 'Print to Voucher',
    text: `Generating voucher for ${selectedItems.value.length} selected document(s)...`,
    timer: 2000,
    showConfirmButton: false
  })
}

const handlePrintThisDocument = () => {
  if (selectedItems.value.length === 0) {
    Swal.fire({
      icon: 'warning',
      title: 'No Selection',
      text: 'Please select at least one document to print.'
    })
    return
  }
  Swal.fire({
    icon: 'success',
    title: 'Print Document',
    text: `Printing ${selectedItems.value.length} selected document(s)...`,
    timer: 2000,
    showConfirmButton: false
  })
}

const handleVoidCashBook = () => {
  if (selectedItems.value.length === 0) {
    Swal.fire({
      icon: 'warning',
      title: 'No Selection',
      text: 'Please check the box of the document you wish to void.'
    })
    return
  }
  Swal.fire({
    title: 'Void Selected Cash Book(s)?',
    text: `Are you sure you want to void ${selectedItems.value.length} selected document(s)?`,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#dc2626',
    cancelButtonColor: '#64748b',
    confirmButtonText: 'Yes, Void All!'
  }).then((result) => {
    if (result.isConfirmed) {
      filteredData.value.forEach(item => {
        if (selectedItems.value.includes(item.id)) {
          item.is_void = true
        }
      })
      Swal.fire('Voided!', 'Selected documents have been marked as void.', 'success')
    }
  })
}

const handleCreateNew = () => {
  Swal.fire({
    title: `Create New ${filterType.value}`,
    text: 'Form entry for ' + filterType.value + ' will open here.',
    icon: 'info',
    confirmButtonColor: '#1e293b'
  })
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }).replace(/ /g, '-')
}

const formatNumber = (num) => {
  if (num === null || num === undefined) return '0.00'
  return parseFloat(num).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

watch(() => route.query.type, (newType) => {
  if (newType) {
    filterType.value = newType
    fetchTableData()
  }
})

onMounted(() => {
  fetchTableData()
})
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  height: 8px;
  width: 8px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>
