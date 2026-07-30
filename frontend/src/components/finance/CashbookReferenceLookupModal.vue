<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 overflow-y-auto">
    <div class="bg-white rounded-2xl shadow-2xl border border-gray-200/80 w-full max-w-6xl max-h-[90vh] flex flex-col overflow-hidden animate-fade-in-up">
      
      <!-- MODAL HEADER (Sokka Premium Navy Gradient) -->
      <div class="bg-gradient-to-r from-bfs-navy via-[#1e293b] to-[#334155] px-6 py-4 flex items-center justify-between border-b border-gray-700/50 shadow-md">
        <div class="flex items-center gap-3">
          <div class="p-2 rounded-xl bg-white/10 text-white shadow-inner">
            <Layers class="w-6 h-6" />
          </div>
          <div>
            <h2 class="text-lg font-extrabold text-white tracking-wide">
              Reference Document Lookup
            </h2>
            <p class="text-xs text-blue-200/80">
              Sunfish ERP Style | Filtered by Approved Payment Requests & Documents
            </p>
          </div>
        </div>
        <div class="flex items-center gap-3">
          <button
            type="button"
            @click="closeModal"
            class="p-1.5 text-gray-400 hover:text-white rounded-lg hover:bg-white/10 transition-colors"
          >
            <X class="w-6 h-6" />
          </button>
        </div>
      </div>

      <!-- MODAL BODY (4 Accordion Groups / Tables - Sunfish ERP Style) -->
      <div class="flex-1 overflow-y-auto p-6 space-y-5 bg-gray-50/60">
        
        <!-- 1. LIST OF CASH BOOK REQUISITION (Default Open) -->
        <div class="bg-white border border-gray-200/90 rounded-xl shadow-sm overflow-hidden transition-all">
          
          <!-- Accordion Header -->
          <div
            @click="toggleSection('requisition')"
            class="w-full bg-gradient-to-r from-[#d5e2f1] to-[#e7eff8] px-4 py-3 flex items-center justify-between cursor-pointer select-none border-b border-blue-200/60 hover:from-[#c8dbf0] transition-colors"
          >
            <div class="flex items-center gap-2.5">
              <FileText class="w-5 h-5 text-bfs-navy" />
              <span class="font-extrabold text-sm text-gray-800">List Of Cash Book Requisition</span>
              <span class="px-2 py-0.5 text-xs font-bold bg-bfs-navy text-white rounded-full">
                {{ requisitions.length }}
              </span>
            </div>
            <ChevronDown
              class="w-5 h-5 text-gray-600 transition-transform duration-300"
              :class="{ 'rotate-180': openSections.requisition }"
            />
          </div>

          <!-- Section Content -->
          <div v-show="openSections.requisition" class="p-4 space-y-4">
            <!-- Filter Toolbar: Date From & Date To (Awal & Akhir Bulan) -->
            <div class="flex flex-wrap items-center justify-between gap-4 bg-gray-50/80 p-3 rounded-lg border border-gray-200/80">
              <div class="flex flex-wrap items-center gap-3">
                <div class="flex items-center gap-2">
                  <label class="text-xs font-bold text-gray-700">Date From</label>
                  <input
                    v-model="reqDateFrom"
                    type="date"
                    class="bg-white border border-gray-300 rounded-lg px-2.5 py-1 text-xs font-semibold text-gray-800 focus:ring-2 focus:ring-bfs-navy outline-none shadow-sm"
                  />
                </div>
                <div class="flex items-center gap-2">
                  <label class="text-xs font-bold text-gray-700">Date To</label>
                  <input
                    v-model="reqDateTo"
                    type="date"
                    class="bg-white border border-gray-300 rounded-lg px-2.5 py-1 text-xs font-semibold text-gray-800 focus:ring-2 focus:ring-bfs-navy outline-none shadow-sm"
                  />
                </div>
                <button
                  type="button"
                  @click="fetchRequisitions"
                  :disabled="loadingReq"
                  class="bg-bfs-navy hover:bg-slate-800 text-white text-xs font-bold px-4 py-1.5 rounded-lg shadow-sm flex items-center gap-1.5 transition-all active:scale-95 disabled:opacity-50"
                >
                  <Search class="w-3.5 h-3.5" />
                  <span>Search</span>
                </button>
              </div>

              <!-- Select Button for Requisitions -->
              <button
                type="button"
                @click="confirmSelection('requisition')"
                class="bg-gradient-to-r from-emerald-600 to-teal-700 hover:from-emerald-700 hover:to-teal-800 text-white text-xs font-bold px-4 py-1.5 rounded-lg shadow flex items-center gap-1.5 transition-all active:scale-95"
              >
                <CheckSquare class="w-4 h-4" />
                <span>Select ({{ selectedReqIds.length }})</span>
              </button>
            </div>

            <!-- Table 1: Requisition -->
            <div class="overflow-x-auto border border-gray-200/80 rounded-lg shadow-sm">
              <table class="w-full text-left border-collapse text-xs">
                <thead>
                  <tr class="bg-gray-100/90 text-gray-700 font-bold uppercase tracking-wider border-b border-gray-300">
                    <th class="py-2.5 px-3 w-12 text-center">No.</th>
                    <th class="py-2.5 px-3 min-w-[140px]">PIC</th>
                    <th class="py-2.5 px-3 min-w-[110px]">Document Date</th>
                    <th class="py-2.5 px-3 min-w-[150px]">Document No</th>
                    <th class="py-2.5 px-3 min-w-[220px]">Purchase Invoice / Cash Advanced Detail</th>
                    <th class="py-2.5 px-3 min-w-[250px]">Detail</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-200 bg-white">
                  <tr
                    v-for="(item, idx) in requisitions"
                    :key="item.id"
                    @click="toggleCheckbox('requisition', item.id)"
                    class="hover:bg-blue-50/50 transition-colors cursor-pointer"
                    :class="{ 'bg-blue-50/80 border-l-4 border-l-bfs-navy': isSelected('requisition', item.id) }"
                  >
                    <td class="py-3 px-3 text-center font-semibold text-gray-500">{{ idx + 1 }}</td>
                    <td class="py-3 px-3 font-bold text-gray-800">{{ item.pic || item.employee_name || 'Sokka Kreatif Teknologi' }}</td>
                    <td class="py-3 px-3 font-medium text-gray-600">{{ formatDate(item.date) }}</td>
                    <td class="py-3 px-3 font-mono font-bold text-bfs-navy">{{ item.document_number }}</td>
                    <td class="py-3 px-3">
                      <div class="flex items-start gap-2">
                        <div class="p-1 rounded-full bg-blue-100 text-blue-600 shrink-0 mt-0.5" title="Reference Info">
                          <Info class="w-3.5 h-3.5" />
                        </div>
                        <span class="text-gray-700 font-medium leading-relaxed">{{ item.reference_detail }}</span>
                      </div>
                    </td>
                    <td class="py-3 px-3" @click.stop>
                      <div class="space-y-2">
                        <p class="text-gray-700 font-medium leading-relaxed">{{ item.description }}</p>
                        <!-- Checkbox & Amount IDR (Sunfish ERP Style) -->
                        <label class="inline-flex items-center gap-2 cursor-pointer p-1 rounded hover:bg-gray-100/80 transition-colors">
                          <input
                            type="checkbox"
                            :checked="isSelected('requisition', item.id)"
                            @change="toggleCheckbox('requisition', item.id)"
                            class="rounded border-gray-300 text-bfs-navy focus:ring-bfs-navy w-4 h-4 cursor-pointer"
                          />
                          <span class="font-bold text-gray-900 text-xs">Amount IDR {{ formatNumber(item.amount) }}</span>
                        </label>
                      </div>
                    </td>
                  </tr>
                  <!-- Empty State -->
                  <tr v-if="requisitions.length === 0">
                    <td colspan="6" class="py-8 text-center text-gray-400 font-medium italic">
                      :: [No Record Found] ::
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- 2. LIST OF INVOICE(S) -->
        <div class="bg-white border border-gray-200/90 rounded-xl shadow-sm overflow-hidden transition-all">
          <!-- Accordion Header -->
          <div
            @click="toggleSection('invoices')"
            class="w-full bg-gradient-to-r from-[#d5e2f1] to-[#e7eff8] px-4 py-3 flex items-center justify-between cursor-pointer select-none border-b border-blue-200/60 hover:from-[#c8dbf0] transition-colors"
          >
            <div class="flex items-center gap-2.5">
              <Receipt class="w-5 h-5 text-bfs-navy" />
              <span class="font-extrabold text-sm text-gray-800">List of Invoice(s)</span>
              <span class="px-2 py-0.5 text-xs font-bold bg-gray-600 text-white rounded-full">
                {{ invoices.length }}
              </span>
            </div>
            <ChevronDown
              class="w-5 h-5 text-gray-600 transition-transform duration-300"
              :class="{ 'rotate-180': openSections.invoices }"
            />
          </div>

          <!-- Section Content -->
          <div v-show="openSections.invoices" class="p-4 space-y-4">
            <!-- Filter Toolbar -->
            <div class="flex flex-wrap items-center justify-between gap-4 bg-gray-50/80 p-3 rounded-lg border border-gray-200/80">
              <div class="flex flex-wrap items-center gap-2">
                <select v-model="invFilterField" class="bg-white border border-gray-300 rounded-lg px-2.5 py-1 text-xs font-semibold text-gray-800">
                  <option value="vendor_name">Vendor Name</option>
                  <option value="invoice_no">Invoice No</option>
                </select>
                <select v-model="invFilterMode" class="bg-white border border-gray-300 rounded-lg px-2.5 py-1 text-xs font-semibold text-gray-800">
                  <option value="any">Any Part of Field</option>
                  <option value="exact">Exact Match</option>
                </select>
                <input
                  v-model="invSearchQuery"
                  type="text"
                  placeholder="Search invoice..."
                  class="bg-white border border-gray-300 rounded-lg px-2.5 py-1 text-xs font-semibold text-gray-800 w-44 focus:ring-2 focus:ring-bfs-navy outline-none"
                />
                <button
                  type="button"
                  @click="fetchInvoices"
                  class="bg-bfs-navy hover:bg-slate-800 text-white text-xs font-bold px-3 py-1 rounded-lg shadow-sm flex items-center gap-1 transition-all"
                >
                  <Search class="w-3.5 h-3.5" />
                  <span>Search</span>
                </button>
                <button
                  type="button"
                  @click="showAllInvoices"
                  class="bg-white hover:bg-gray-100 border border-gray-300 text-gray-700 text-xs font-bold px-3 py-1 rounded-lg shadow-sm transition-all"
                >
                  Show All
                </button>
              </div>

              <!-- Select Button for Invoices -->
              <button
                type="button"
                @click="confirmSelection('invoices')"
                class="bg-gradient-to-r from-emerald-600 to-teal-700 hover:from-emerald-700 hover:to-teal-800 text-white text-xs font-bold px-4 py-1.5 rounded-lg shadow flex items-center gap-1.5 transition-all active:scale-95"
              >
                <CheckSquare class="w-4 h-4" />
                <span>Select ({{ selectedInvIds.length }})</span>
              </button>
            </div>

            <!-- Table 2: Invoices -->
            <div class="overflow-x-auto border border-gray-200/80 rounded-lg shadow-sm">
              <table class="w-full text-left border-collapse text-xs">
                <thead>
                  <tr class="bg-gray-100/90 text-gray-700 font-bold uppercase tracking-wider border-b border-gray-300">
                    <th class="py-2.5 px-3 w-12 text-center">No.</th>
                    <th class="py-2.5 px-3 min-w-[150px]">Vendor Name</th>
                    <th class="py-2.5 px-3 min-w-[110px]">Invoice Date</th>
                    <th class="py-2.5 px-3 min-w-[110px]">Invoice Due Date</th>
                    <th class="py-2.5 px-3 min-w-[140px]">Invoice No</th>
                    <th class="py-2.5 px-3 min-w-[220px]">Detail</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-200 bg-white">
                  <tr
                    v-for="(item, idx) in invoices"
                    :key="item.id"
                    @click="toggleCheckbox('invoices', item.id)"
                    class="hover:bg-blue-50/50 transition-colors cursor-pointer"
                    :class="{ 'bg-blue-50/80 border-l-4 border-l-bfs-navy': isSelected('invoices', item.id) }"
                  >
                    <td class="py-3 px-3 text-center font-semibold text-gray-500">{{ idx + 1 }}</td>
                    <td class="py-3 px-3 font-bold text-gray-800">{{ item.vendor_name }}</td>
                    <td class="py-3 px-3 font-medium text-gray-600">{{ formatDate(item.date) }}</td>
                    <td class="py-3 px-3 font-medium text-gray-600">{{ formatDate(item.due_date) }}</td>
                    <td class="py-3 px-3 font-mono font-bold text-bfs-navy">{{ item.invoice_number }}</td>
                    <td class="py-3 px-3" @click.stop>
                      <div class="space-y-2">
                        <p class="text-gray-700 font-medium">{{ item.description }}</p>
                        <label class="inline-flex items-center gap-2 cursor-pointer p-1 rounded hover:bg-gray-100/80 transition-colors">
                          <input
                            type="checkbox"
                            :checked="isSelected('invoices', item.id)"
                            @change="toggleCheckbox('invoices', item.id)"
                            class="rounded border-gray-300 text-bfs-navy focus:ring-bfs-navy w-4 h-4 cursor-pointer"
                          />
                          <span class="font-bold text-gray-900 text-xs">Amount IDR {{ formatNumber(item.amount) }}</span>
                        </label>
                      </div>
                    </td>
                  </tr>
                  <tr v-if="invoices.length === 0">
                    <td colspan="6" class="py-8 text-center text-gray-400 font-medium italic">
                      :: [No Record Found] ::
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- 3. LIST OF DEBIT NOTE(S) -->
        <div class="bg-white border border-gray-200/90 rounded-xl shadow-sm overflow-hidden transition-all">
          <div
            @click="toggleSection('debitNotes')"
            class="w-full bg-gradient-to-r from-[#d5e2f1] to-[#e7eff8] px-4 py-3 flex items-center justify-between cursor-pointer select-none border-b border-blue-200/60 hover:from-[#c8dbf0] transition-colors"
          >
            <div class="flex items-center gap-2.5">
              <FileMinus class="w-5 h-5 text-bfs-navy" />
              <span class="font-extrabold text-sm text-gray-800">List of Debit Note(s)</span>
              <span class="px-2 py-0.5 text-xs font-bold bg-gray-600 text-white rounded-full">
                {{ debitNotes.length }}
              </span>
            </div>
            <div class="flex items-center gap-4" @click.stop>
              <button
                type="button"
                @click="confirmSelection('debitNotes')"
                class="bg-gradient-to-r from-emerald-600 to-teal-700 hover:from-emerald-700 hover:to-teal-800 text-white text-xs font-bold px-3 py-1 rounded shadow flex items-center gap-1 transition-all"
              >
                <span>Select ({{ selectedDnIds.length }})</span>
              </button>
              <ChevronDown
                class="w-5 h-5 text-gray-600 transition-transform duration-300 cursor-pointer"
                :class="{ 'rotate-180': openSections.debitNotes }"
                @click="toggleSection('debitNotes')"
              />
            </div>
          </div>

          <div v-show="openSections.debitNotes" class="p-4">
            <div class="overflow-x-auto border border-gray-200/80 rounded-lg shadow-sm">
              <table class="w-full text-left border-collapse text-xs">
                <thead>
                  <tr class="bg-gray-100/90 text-gray-700 font-bold uppercase tracking-wider border-b border-gray-300">
                    <th class="py-2.5 px-3 w-12 text-center">No.</th>
                    <th class="py-2.5 px-3 min-w-[150px]">Vendor Name</th>
                    <th class="py-2.5 px-3 min-w-[110px]">Document Date</th>
                    <th class="py-2.5 px-3 min-w-[140px]">Document No</th>
                    <th class="py-2.5 px-3 min-w-[220px]">Detail</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-200 bg-white">
                  <tr v-if="debitNotes.length === 0">
                    <td colspan="5" class="py-8 text-center text-gray-400 font-medium italic">
                      :: [No Record Found] ::
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- 4. LIST OF CREDIT NOTE(S) -->
        <div class="bg-white border border-gray-200/90 rounded-xl shadow-sm overflow-hidden transition-all">
          <div
            @click="toggleSection('creditNotes')"
            class="w-full bg-gradient-to-r from-[#d5e2f1] to-[#e7eff8] px-4 py-3 flex items-center justify-between cursor-pointer select-none border-b border-blue-200/60 hover:from-[#c8dbf0] transition-colors"
          >
            <div class="flex items-center gap-2.5">
              <FilePlus class="w-5 h-5 text-bfs-navy" />
              <span class="font-extrabold text-sm text-gray-800">List of Credit Note(s)</span>
              <span class="px-2 py-0.5 text-xs font-bold bg-gray-600 text-white rounded-full">
                {{ creditNotes.length }}
              </span>
            </div>
            <div class="flex items-center gap-4" @click.stop>
              <button
                type="button"
                @click="confirmSelection('creditNotes')"
                class="bg-gradient-to-r from-emerald-600 to-teal-700 hover:from-emerald-700 hover:to-teal-800 text-white text-xs font-bold px-3 py-1 rounded shadow flex items-center gap-1 transition-all"
              >
                <span>Select ({{ selectedCnIds.length }})</span>
              </button>
              <ChevronDown
                class="w-5 h-5 text-gray-600 transition-transform duration-300 cursor-pointer"
                :class="{ 'rotate-180': openSections.creditNotes }"
                @click="toggleSection('creditNotes')"
              />
            </div>
          </div>

          <div v-show="openSections.creditNotes" class="p-4">
            <div class="overflow-x-auto border border-gray-200/80 rounded-lg shadow-sm">
              <table class="w-full text-left border-collapse text-xs">
                <thead>
                  <tr class="bg-gray-100/90 text-gray-700 font-bold uppercase tracking-wider border-b border-gray-300">
                    <th class="py-2.5 px-3 w-12 text-center">No.</th>
                    <th class="py-2.5 px-3 min-w-[150px]">Vendor Name</th>
                    <th class="py-2.5 px-3 min-w-[110px]">Document Date</th>
                    <th class="py-2.5 px-3 min-w-[140px]">Document No</th>
                    <th class="py-2.5 px-3 min-w-[220px]">Detail</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-200 bg-white">
                  <tr v-if="creditNotes.length === 0">
                    <td colspan="5" class="py-8 text-center text-gray-400 font-medium italic">
                      :: [No Record Found] ::
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

      </div>

      <!-- MODAL FOOTER -->
      <div class="bg-gray-100/90 px-6 py-4 flex items-center justify-between border-t border-gray-300">
        <div class="text-xs font-semibold text-gray-600">
          Showing approved documents available for payment allocation.
        </div>
        <div class="flex items-center gap-3">
          <button
            type="button"
            @click="closeModal"
            class="px-5 py-2 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 rounded-xl text-xs font-bold shadow-sm transition-all"
          >
            Cancel
          </button>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import api from '../../services/api'
import {
  Layers, FileText, Receipt, FileMinus, FilePlus, ChevronDown,
  Search, CheckSquare, Info, X
} from 'lucide-vue-next'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  activeRowIndex: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['close', 'select'])

// ── Accordion Toggle State ──
const openSections = reactive({
  requisition: true,
  invoices: false,
  debitNotes: false,
  creditNotes: false
})

const toggleSection = (key) => {
  openSections[key] = !openSections[key]
}

// ── Default Dates: Awal dan Akhir Bulan (Start & End of Current Month) ──
const getDefaultStartOfMonth = () => {
  const now = new Date()
  const firstDay = new Date(now.getFullYear(), now.getMonth(), 1)
  return firstDay.toISOString().split('T')[0]
}

const getDefaultEndOfMonth = () => {
  const now = new Date()
  const lastDay = new Date(now.getFullYear(), now.getMonth() + 1, 0)
  return lastDay.toISOString().split('T')[0]
}

const reqDateFrom = ref(getDefaultStartOfMonth())
const reqDateTo = ref(getDefaultEndOfMonth())
const loadingReq = ref(false)

// ── Data Arrays ──
const requisitions = ref([])
const invoices = ref([])
const debitNotes = ref([])
const creditNotes = ref([])

// ── Selection Arrays ──
const selectedReqIds = ref([])
const selectedInvIds = ref([])
const selectedDnIds = ref([])
const selectedCnIds = ref([])

// ── Invoice Filter State ──
const invFilterField = ref('vendor_name')
const invFilterMode = ref('any')
const invSearchQuery = ref('')

// ── Formatting Helpers ──
const formatNumber = (val) => {
  const num = parseFloat(val) || 0
  return num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  try {
    const d = new Date(dateStr)
    if (isNaN(d.getTime())) return dateStr
    return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
  } catch {
    return dateStr
  }
}

// ── Fetch Approved Cash Book Requisitions (ApproveForPayment) ──
const fetchRequisitions = async () => {
  loadingReq.value = true
  try {
    const res = await api.get('/accounting/cashbook-request/', {
      params: {
        is_budget_request: 'true',
        budget_status: 'Approve for Payment',
        date_from: reqDateFrom.value,
        date_to: reqDateTo.value
      }
    })
    const list = res.data?.results || res.data
    if (Array.isArray(list) && list.length > 0) {
      requisitions.value = list.map(item => {
        const brPaymentAmt = parseFloat(item.budget_request?.payment_amount)
        const fallbackAmt = parseFloat(item.amount || item.total_amount || 0)
        const resolvedAmt = (!isNaN(brPaymentAmt) && brPaymentAmt > 0) ? brPaymentAmt : fallbackAmt

        return {
          id: item.id,
          document_number: item.document_number,
          date: item.date,
          pic: item.pic_name || item.employee_name || item.created_by_name || 'Sokka Kreatif Teknologi',
          reference_detail: item.purchase_invoice_display || item.usage_for || `CBR Reference (${item.document_number})`,
          description: item.description || item.usage_for || 'Payment Request allocation',
          amount: resolvedAmt
        }
      })
    } else {
      requisitions.value = []
    }
  } catch (e) {
    console.error('Error fetching approved payment requests:', e)
    requisitions.value = []
  } finally {
    loadingReq.value = false
  }
}

// ── Fetch Invoices ──
const fetchInvoices = async () => {
  try {
    const res = await api.get('/purchase/invoices/', {
      params: {
        search: invSearchQuery.value
      }
    }).catch(() => ({ data: [] }))
    const list = res.data?.results || res.data
    if (Array.isArray(list) && list.length > 0) {
      invoices.value = list.map(item => ({
        id: item.id,
        vendor_name: item.vendor?.name || item.vendor_name || '-',
        date: item.invoice_date || item.date,
        due_date: item.due_date,
        invoice_number: item.invoice_number || item.code,
        description: item.description || 'Purchase invoice settlement',
        amount: parseFloat(item.total_amount || item.amount || 0)
      }))
    } else {
      invoices.value = []
    }
  } catch (e) {
    invoices.value = []
  }
}

const showAllInvoices = () => {
  invSearchQuery.value = ''
  fetchInvoices()
}

// ── Checkbox Toggle Logic ──
const toggleCheckbox = (type, id) => {
  let arr
  if (type === 'requisition') arr = selectedReqIds
  else if (type === 'invoices') arr = selectedInvIds
  else if (type === 'debitNotes') arr = selectedDnIds
  else if (type === 'creditNotes') arr = selectedCnIds

  const idx = arr.value.indexOf(id)
  if (idx === -1) {
    arr.value.push(id)
  } else {
    arr.value.splice(idx, 1)
  }
}

const isSelected = (type, id) => {
  if (type === 'requisition') return selectedReqIds.value.includes(id)
  if (type === 'invoices') return selectedInvIds.value.includes(id)
  if (type === 'debitNotes') return selectedDnIds.value.includes(id)
  if (type === 'creditNotes') return selectedCnIds.value.includes(id)
  return false
}

// ── Confirm Selection & Emit to Parent Form ──
const confirmSelection = (type) => {
  let selectedItems = []
  if (type === 'requisition') {
    selectedItems = requisitions.value.filter(r => selectedReqIds.value.includes(r.id)).map(r => ({
      id: r.id,
      document_no: r.document_number,
      description: r.description,
      amount: r.amount,
      source: 'CASHBOOK_REQ'
    }))
  } else if (type === 'invoices') {
    selectedItems = invoices.value.filter(inv => selectedInvIds.value.includes(inv.id)).map(inv => ({
      id: inv.id,
      document_no: inv.invoice_number,
      description: inv.description,
      amount: inv.amount,
      source: 'INVOICE'
    }))
  }

  if (selectedItems.length === 0) return

  emit('select', {
    rowIndex: props.activeRowIndex,
    items: selectedItems
  })
  closeModal()
}

const closeModal = () => {
  emit('close')
}

// ── Watch open to fetch ──
watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    fetchRequisitions()
    fetchInvoices()
  }
})
</script>

<style scoped>
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(12px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.animate-fade-in-up {
  animation: fadeInUp 0.25s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
</style>
