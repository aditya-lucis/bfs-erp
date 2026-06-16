<script setup>
import { ref,reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'
import Panel from '../../components/Panel.vue'
import { useAuthStore } from '../../stores/auth'
import { useApprovalRequestStore } from '../../stores/approvalRequest'
import { useOrganizationStore } from '../../stores/organization'
import Swal from 'sweetalert2'

// Icons
import {
  Plus, Search, SearchX, FileText, CheckCircle, Clock, AlertCircle, FileCheck, FileX, FileWarning, FileClock, Folder, FolderOpen, FolderCheck, Pencil, Send, Trash2, Loader2, Printer
} from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()
const approvalStore = useApprovalRequestStore()
const orgStore = useOrganizationStore()

const items = ref([])
const loading = ref(false)
const error = ref(null)

const canCreate = computed(() => authStore.hasPermission('GL-GENERAL-JOURNAL-TRANSACTION_CREATE'))
const canUpdate = computed(() => authStore.hasPermission('GL-GENERAL-JOURNAL-TRANSACTION_UPDATE'))
const canDelete = computed(() => authStore.hasPermission('GL-GENERAL-JOURNAL-TRANSACTION_DELETE'))



const printModal = reactive({
  show: false,
  transaction: null,
  signatures: [],
  isLoadingSignatures: false
})

async function openPrintPreview(item) {
  printModal.transaction = item
  printModal.show = true
  printModal.signatures = []
  
  if (item.status !== 'DRAFT') {
    printModal.isLoadingSignatures = true
    try {
      const sigs = await approvalStore.fetchSignatures('GEJ', item.id)
      printModal.signatures = sigs || []
    } catch (e) {
      console.error('Failed to fetch signatures', e)
    } finally {
      printModal.isLoadingSignatures = false
    }
  }
}

function printDocument() {
  window.print()
}

function formatCurrency(val) {
  if (val === undefined || val === null) return '0'
  const parsed = typeof val === 'string' ? parseFloat(val) : val
  return new Intl.NumberFormat('id-ID', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(parsed)
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric'
  }).replace(/ /g, '-')
}

const printTotalDebit = computed(() => {
  if (!printModal.transaction || !printModal.transaction.details) return 0
  return printModal.transaction.details.reduce((sum, d) => sum + parseFloat(d.debit || 0), 0)
})

const printTotalCredit = computed(() => {
  if (!printModal.transaction || !printModal.transaction.details) return 0
  return printModal.transaction.details.reduce((sum, d) => sum + parseFloat(d.credit || 0), 0)
})

const companyInfo = computed(() => orgStore.company || {})

const today = new Date()
const firstDay = new Date(today.getFullYear(), today.getMonth(), 1)
const lastDay = new Date(today.getFullYear(), today.getMonth() + 1, 0)

// Filters
const filterDateFrom = ref(firstDay.toISOString().substring(0, 10))
const filterDateTo = ref(lastDay.toISOString().substring(0, 10))
const searchQuery = ref('')
const filterDocStatus = ref('')
const filterAppStatus = ref('')

const fetchJournals = async () => {
  loading.value = true
  error.value = null
  try {
    const params = {}
    if (searchQuery.value) params.search = searchQuery.value
    if (filterDateFrom.value) params.date_from = filterDateFrom.value
    if (filterDateTo.value) params.date_to = filterDateTo.value
    if (filterDocStatus.value) params.document_status = filterDocStatus.value
    if (filterAppStatus.value) params.approval_status = filterAppStatus.value
    
    const response = await api.get('/accounting/general-journals/', { params })
    items.value = response.data.results || response.data
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to fetch general journals'
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  fetchJournals()
}

const handleResetFilters = () => {
  searchQuery.value = ''
  filterDateFrom.value = ''
  filterDateTo.value = ''
  filterDocStatus.value = ''
  filterAppStatus.value = ''
  fetchJournals()
}

const submitApproval = async (item) => {
  const result = await Swal.fire({
    title: 'Are you sure?',
    text: `You want to submit journal ${item.transaction_number} for approval?`,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#1e3a8a',
    cancelButtonColor: '#d33',
    confirmButtonText: 'Yes, submit it!'
  })
  
  if (!result.isConfirmed) return
  
  loading.value = true
  try {
    await api.post(`/accounting/general-journals/${item.id}/submit_approval/`)
    fetchJournals()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to submit for approval'
  } finally {
    loading.value = false
  }
}

const deleteItem = async (item) => {
  const result = await Swal.fire({
    title: 'Are you sure?',
    text: `You want to delete journal ${item.transaction_number}?`,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#1e3a8a',
    cancelButtonColor: '#d33',
    confirmButtonText: 'Yes, delete it!'
  })
  
  if (!result.isConfirmed) return
  
  loading.value = true
  try {
    await api.delete(`/accounting/general-journals/${item.id}/`)
    fetchJournals()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to delete journal'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchJournals()
  if (!orgStore.company) orgStore.fetchCompany()
})

const navigateToEntry = (id = null) => {
  if (id) {
    router.push(`/gl/general-journal-transaction/entry/${id}`)
  } else {
    router.push('/gl/general-journal-transaction/entry')
  }
}

const formatDocStatusText = (status) => {
  return status || 'Draft'
}

const formatAppStatusText = (status) => {
  return status || 'Draft'
}

</script>

<template>
  <Panel title="General Journal Transactions" subtitle="General Ledger | General Journal | General Journal Transaction">
    
    <!-- Toolbar/Search/Filter -->
    <div class="flex flex-col gap-4 mb-6">
      <div class="flex flex-wrap items-center gap-4">
        <!-- Search -->
        <div class="flex items-center border border-gray-200 rounded-lg overflow-hidden bg-white">
          <span class="px-3 py-1.5 bg-gray-50 text-xs text-gray-500 border-r border-gray-200">Search</span>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Type Journal Number or Memo..."
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
          
          <!-- Filter Status -->
          <div class="border border-gray-200 rounded-lg px-3 py-1.5 relative bg-white flex items-center gap-2 shadow-sm min-h-[38px]">
            <span class="absolute -top-2 left-2 bg-white px-1 text-[9px] font-bold text-gray-500 uppercase tracking-wider">Filter Status</span>
            <button 
              @click="filterDocStatus = ''; handleSearch()" 
              class="px-1.5 py-0.5 rounded text-[10px] font-bold transition-colors cursor-pointer"
              :class="filterDocStatus === '' ? 'bg-bfs-navy text-white' : 'hover:bg-gray-100 text-gray-400'"
            >
              ALL
            </button>
            <button 
              @click="filterDocStatus = 'DRAFT'; handleSearch()" 
              class="p-0.5 rounded transition-all cursor-pointer"
              :class="filterDocStatus === 'DRAFT' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"
            >
              <Folder class="w-4 h-4 text-amber-500 fill-amber-500/10" />
            </button>
            <button 
              @click="filterDocStatus = 'IN_REVIEW'; handleSearch()" 
              class="p-0.5 rounded transition-all cursor-pointer"
              :class="filterDocStatus === 'IN_REVIEW' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"
            >
              <FolderOpen class="w-4 h-4 text-blue-500 fill-blue-500/10" />
            </button>
            <button 
              @click="filterDocStatus = 'APPROVED'; handleSearch()" 
              class="p-0.5 rounded transition-all cursor-pointer"
              :class="filterDocStatus === 'APPROVED' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"
            >
              <FolderCheck class="w-4 h-4 text-green-500 fill-green-500/10" />
            </button>
          </div>

          <!-- Approval Filter Status -->
          <div class="border border-gray-200 rounded-lg px-3 py-1.5 relative bg-white flex items-center gap-2 shadow-sm min-h-[38px]">
            <span class="absolute -top-2 left-2 bg-white px-1 text-[9px] font-bold text-gray-500 uppercase tracking-wider">Approval Filter Status</span>
            <button 
              @click="filterAppStatus = ''; handleSearch()" 
              class="px-1.5 py-0.5 rounded text-[10px] font-bold transition-colors cursor-pointer"
              :class="filterAppStatus === '' ? 'bg-bfs-navy text-white' : 'hover:bg-gray-100 text-gray-400'"
            >
              ALL
            </button>
            <button 
              @click="filterAppStatus = 'DRAFT'; handleSearch()" 
              class="p-0.5 rounded transition-all cursor-pointer"
              :class="filterAppStatus === 'DRAFT' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"
            >
              <FileText class="w-4 h-4 text-gray-400" />
            </button>
            <button 
              @click="filterAppStatus = 'IN_REVIEW'; handleSearch()" 
              class="p-0.5 rounded transition-all cursor-pointer"
              :class="filterAppStatus === 'IN_REVIEW' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"
            >
              <FileClock class="w-4 h-4 text-bfs-gold animate-pulse" />
            </button>
            <button 
              @click="filterAppStatus = 'APPROVED'; handleSearch()" 
              class="p-0.5 rounded transition-all cursor-pointer"
              :class="filterAppStatus === 'APPROVED' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"
            >
              <FileCheck class="w-4 h-4 text-green-500" />
            </button>
            <button 
              @click="filterAppStatus = 'REJECTED'; handleSearch()" 
              class="p-0.5 rounded transition-all cursor-pointer"
              :class="filterAppStatus === 'REJECTED' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"
            >
              <FileX class="w-4 h-4 text-red-500" />
            </button>
            <button 
              @click="filterAppStatus = 'CANCELLED'; handleSearch()" 
              class="p-0.5 rounded transition-all cursor-pointer"
              :class="filterAppStatus === 'CANCELLED' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"
            >
              <FileWarning class="w-4 h-4 text-orange-500" />
            </button>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex items-center justify-between gap-3 bg-slate-50/50 p-2 rounded-lg border border-slate-200">
          <div class="flex items-center gap-2">
            <button 
              v-if="canCreate"
              @click="navigateToEntry()"
              class="btn-primary text-sm flex items-center gap-2 px-3 py-1.5 shadow-sm"
            >
              <Plus class="w-4 h-4" /> Add General Journal
            </button>
          </div>
          <div class="flex items-center gap-2">
          </div>
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="error" class="mb-4">
      <div class="flex items-center gap-3 p-4 bg-red-50 text-red-700 rounded-lg border border-red-100">
        <AlertCircle class="w-5 h-5 shrink-0" />
        <p class="text-sm font-medium">{{ error }}</p>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-16">
      <Loader2 class="w-6 h-6 animate-spin text-bfs-gold" />
    </div>

    <!-- Table List -->
    <div v-else-if="items.length" class="border border-gray-200 rounded-xl overflow-hidden bg-white shadow-sm">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-gray-50 border-b border-gray-200 text-[11px] font-semibold text-gray-600 uppercase tracking-wider">
              <th class="py-3 px-4 w-12 text-center">No.</th>
              <th class="py-3 px-4">General Journal Number</th>
              <th class="py-3 px-4">General Journal Date</th>
              <th class="py-3 px-4">General Journal Description</th>
              <th class="py-3 px-4 text-center">Document Status</th>
              <th class="py-3 px-4 text-center">Approval</th>
              <th class="py-3 px-4 w-20 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr
              v-for="(item, idx) in items"
              :key="item.id"
              class="hover:bg-yellow-50/20 transition-colors text-xs text-gray-700"
            >
              <td class="py-3 px-4 text-center font-medium text-gray-400">{{ idx + 1 }}.</td>
              <td class="py-3 px-4 font-mono text-gray-600 font-semibold">{{ item.transaction_number }}</td>
              <td class="py-3 px-4">{{ item.date }}</td>
              <td class="py-3 px-4 truncate max-w-[200px]" :title="item.memo">{{ item.memo }}</td>
              <td class="py-3 px-4 text-center">
                <div
                  class="inline-flex items-center justify-center p-1 rounded-md"
                  :title="'Document Status: ' + formatDocStatusText(item.status)"
                >
                  <Folder v-if="item.status === 'DRAFT' || item.status === 'REJECTED' || item.status === 'CANCELLED'" class="w-4.5 h-4.5 text-amber-500 fill-amber-500/10" />
                  <FolderOpen v-else-if="item.status === 'IN_REVIEW'" class="w-4.5 h-4.5 text-blue-500 fill-blue-500/10" />
                  <FolderCheck v-else-if="item.status === 'APPROVED'" class="w-4.5 h-4.5 text-green-500 fill-green-500/10" />
                </div>
              </td>
              <td class="py-3 px-4 text-center">
                <button
                  @click="openPrintPreview(item)"
                  class="inline-flex items-center justify-center p-1 rounded-md"
                  :title="'Approval Status: ' + formatAppStatusText(item.status)"
                >
                  <FileText v-if="item.status === 'DRAFT'" class="w-4.5 h-4.5 text-gray-400" />
                  <FileClock v-else-if="item.status === 'IN_REVIEW'" class="w-4.5 h-4.5 text-bfs-gold animate-pulse" />
                  <FileCheck v-else-if="item.status === 'APPROVED'" class="w-4.5 h-4.5 text-green-500" />
                  <FileX v-else-if="item.status === 'REJECTED'" class="w-4.5 h-4.5 text-red-500" />
                  <FileWarning v-else-if="item.status === 'CANCELLED'" class="w-4.5 h-4.5 text-orange-500" />
                </button>
              </td>
              <td class="py-2.5 px-4 text-center">
                <div class="flex justify-center gap-2">
                  <button 
                    v-if="canUpdate"
                    @click="navigateToEntry(item.id)" 
                    class="p-1.5 rounded-md hover:bg-slate-100 text-slate-500 hover:text-bfs-navy transition-colors"
                    title="Edit / View"
                  >
                    <Pencil class="w-4 h-4" />
                  </button>
                  <button 
                    v-else
                    @click="navigateToEntry(item.id)" 
                    class="p-1.5 rounded-md hover:bg-slate-100 text-slate-500 hover:text-bfs-navy transition-colors"
                    title="View"
                  >
                    <FileText class="w-4 h-4" />
                  </button>
                  
                  <button 
                    v-if="(item.status === 'DRAFT' || item.status === 'CANCELLED') && canUpdate"
                    @click="submitApproval(item)"
                    class="p-1.5 rounded-md hover:bg-green-50 text-slate-500 hover:text-green-600 transition-colors"
                    title="Submit for Approval"
                  >
                    <Send class="w-4 h-4" />
                  </button>
                  <button 
                    v-if="(item.status === 'DRAFT' || item.status === 'REJECTED' || item.status === 'CANCELLED') && canDelete"
                    @click="deleteItem(item)"
                    class="p-1.5 rounded-md hover:bg-red-50 text-slate-500 hover:text-red-600 transition-colors"
                    title="Delete"
                  >
                    <Trash2 class="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="flex flex-col items-center justify-center py-20 text-gray-400">
      <FileText class="w-12 h-12 mb-3 text-gray-300" />
      <p class="text-sm">No general journals found.</p>
    </div>

  
    <!-- Print Preview Modal -->
    <Teleport to="body">
      <Transition 
        enter-active-class="transition duration-300 ease-out"
        enter-from-class="opacity-0 scale-95"
        enter-to-class="opacity-100 scale-100"
        leave-active-class="transition duration-200 ease-in"
        leave-from-class="opacity-100 scale-100"
        leave-to-class="opacity-0 scale-95"
      >
        <div v-if="printModal.show" class="fixed inset-0 z-50 flex items-center justify-center p-4 print-modal-overlay">
          <div class="absolute inset-0 bg-black/60 print:hidden" @click="printModal.show = false" />
          
          <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-[210mm] max-h-[95vh] overflow-y-auto z-10 border border-gray-100 flex flex-col print-modal-container">
            
            <!-- Toolbar (Hidden on print) -->
            <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between bg-bfs-navy text-white rounded-t-2xl print:hidden">
              <div class="flex items-center gap-3">
                <Printer class="w-4 h-4 text-bfs-gold" />
                <h3 class="font-bold text-lg tracking-wide">Print Preview General Journal</h3>
              </div>
              <div class="flex items-center gap-3">
                <button 
                  @click="printDocument" 
                  class="flex items-center gap-2 px-4 py-1.5 bg-bfs-gold hover:bg-yellow-500 text-bfs-navy font-bold rounded-lg transition-colors cursor-pointer"
                >
                  <Printer class="w-3.5 h-3.5" />
                  Print A4
                </button>
                <div class="w-px h-6 bg-white/20 mx-1"></div>
                <button @click="printModal.show = false" class="text-white/80 hover:text-white transition-colors">
                  <X class="w-6 h-6" />
                </button>
              </div>
            </div>

            <!-- Print Document Area (A4 layout styling) -->
            <div id="print-area" class="p-8 bg-white flex-1 text-xs text-gray-800 space-y-6 select-text overflow-y-auto">
              
              <!-- HEADER: Company Profile -->
              <div class="flex justify-between items-start border-b-2 border-gray-800 pb-4">
                <div class="flex flex-col text-[10px] leading-tight">
                  <h1 class="font-extrabold text-sm mb-1 uppercase tracking-wider">{{ companyInfo.company_name || 'PT. BFS ERP' }}</h1>
                  <p>{{ companyInfo.company_address || 'Alamat Perusahaan' }}</p>
                  <p v-if="companyInfo.phone">Phone : {{ companyInfo.phone }}</p>
                  <p v-if="companyInfo.email">Email : {{ companyInfo.email }}</p>
                </div>
                <!-- Logo Company -->
                <div v-if="companyInfo.logo_url" class="h-16 w-48 flex items-start justify-end">
                  <img :src="companyInfo.logo_url" alt="Company Logo" class="max-h-full max-w-full object-contain" />
                </div>
              </div>

              <!-- TITLE -->
              <div class="text-center">
                <h2 class="text-lg font-black uppercase tracking-widest border-b border-gray-300 inline-block pb-1">General Journal Transaction</h2>
              </div>

              <!-- TRANSACTION INFO -->
              <div class="flex justify-center">
                <div class="grid grid-cols-[auto_auto_1fr] gap-x-2 gap-y-1 text-[11px] max-w-2xl">
                  <div class="text-right text-gray-500">Number</div>
                  <div>:</div>
                  <div class="font-bold">{{ printModal.transaction?.transaction_number }}</div>

                  <div class="text-right text-gray-500">Date</div>
                  <div>:</div>
                  <div>{{ formatDate(printModal.transaction?.date) }}</div>

                  <div class="text-right text-gray-500">Memo</div>
                  <div>:</div>
                  <div class="whitespace-pre-wrap">{{ printModal.transaction?.memo }}</div>

                  <div class="text-right text-gray-500">Project</div>
                  <div>:</div>
                  <div>{{ printModal.transaction?.project_name || '-' }}</div>

                  <div class="text-right text-gray-500">TaxRectification</div>
                  <div>:</div>
                  <div>{{ printModal.transaction?.tax_rectification || '-' }}</div>

                  <div class="text-right text-gray-500">Is Adjustment PPh</div>
                  <div>:</div>
                  <div>{{ printModal.transaction?.is_adjustment_pph ? 'Yes' : 'No' }}</div>
                </div>
              </div>

              <!-- DETAILS TABLE -->
              <div class="mt-4">
                <table class="w-full border-collapse border border-gray-800 text-[9px] mb-4">
                  <thead>
                    <tr class="bg-gray-100/50">
                      <th class="border border-gray-800 p-1.5 text-center w-8">No</th>
                      <th class="border border-gray-800 p-1.5 text-left">Account</th>
                      <th class="border border-gray-800 p-1.5 text-center">Currency</th>
                      <th class="border border-gray-800 p-1.5 text-right">Debit</th>
                      <th class="border border-gray-800 p-1.5 text-right">Credit</th>
                      <th class="border border-gray-800 p-1.5 text-center">Period From</th>
                      <th class="border border-gray-800 p-1.5 text-center">Period To</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(detail, idx) in printModal.transaction?.details || []" :key="idx">
                      <td class="border border-gray-800 p-1.5 text-center">{{ idx + 1 }}</td>
                      <td class="border border-gray-800 p-1.5">
                        <div class="font-bold">{{ detail.account_number || detail.account }}</div>
                        <div class="text-[8px] text-gray-600">{{ detail.account_name || '' }}</div>
                      </td>
                      <td class="border border-gray-800 p-1.5 text-center">{{ detail.currency }}</td>
                      <td class="border border-gray-800 p-1.5 text-right font-mono">{{ formatCurrency(detail.debit) }}</td>
                      <td class="border border-gray-800 p-1.5 text-right font-mono">{{ formatCurrency(detail.credit) }}</td>
                      <td class="border border-gray-800 p-1.5 text-center">{{ formatDate(detail.period_from) || '-' }}</td>
                      <td class="border border-gray-800 p-1.5 text-center">{{ formatDate(detail.period_to) || '-' }}</td>
                    </tr>
                    
                    <!-- TOTAL ROW -->
                    <tr class="bg-gray-100 font-bold border-t-2 border-gray-800">
                      <td colspan="3" class="border border-gray-800 p-1.5 text-right uppercase tracking-wider">Total</td>
                      <td class="border border-gray-800 p-1.5 text-right font-mono">{{ formatCurrency(printTotalDebit) }}</td>
                      <td class="border border-gray-800 p-1.5 text-right font-mono">{{ formatCurrency(printTotalCredit) }}</td>
                      <td colspan="2" class="border border-gray-800 p-1.5"></td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- SIGNATURES -->
              <div v-if="printModal.transaction && printModal.transaction.status !== 'DRAFT'" class="mt-8 border border-gray-800 p-2">
                <div class="text-[8px] uppercase font-bold text-gray-600 mb-2 tracking-wider">Document Signatures (Persetujuan Dokumen)</div>
                <div class="flex flex-wrap gap-2 justify-start">
                  <div 
                    v-for="sig in printModal.signatures" 
                    :key="sig.id"
                    class="border border-gray-800 p-1 text-center min-w-[120px] flex flex-col justify-between h-[100px] bg-white"
                  >
                    <div>
                      <div class="text-[7px] uppercase font-bold text-gray-500 tracking-wider">{{ sig.role_display }}</div>
                      <div class="text-[8px] font-semibold text-gray-800">{{ sig.position_name }}</div>
                    </div>
                    
                    <div class="flex-1 flex items-center justify-center py-1 h-10">
                      <template v-if="['APPROVED', 'CLOSE', 'IN_REVIEW'].includes(printModal.transaction.status) && sig.is_signed">
                        <img v-if="sig.signature_draw && sig.signature_draw.startsWith('data:image')" :src="sig.signature_draw" class="max-h-8 object-contain mx-auto" />
                        <img v-else-if="sig.signature_image" :src="sig.signature_image" class="max-h-8 object-contain mx-auto" />
                        <div v-else class="px-1 py-0 border border-green-600 rounded text-[6px] text-green-700 italic font-bold">SIGNED DIGITALLY</div>
                      </template>
                      <template v-else-if="['IN_REVIEW', 'READY_TO_PROCESS'].includes(printModal.transaction.status)">
                        <div class="text-[7px] text-gray-300 italic">(Wet Signature Area)</div>
                      </template>
                    </div>
                    
                    <div class="border-t border-gray-400 pt-0.5 text-[7px] text-gray-700">
                      <div class="font-bold truncate" :title="sig.signer_employee_name">{{ sig.signer_employee_name || sig.signer_name || '(Pending)' }}</div>
                    </div>
                  </div>
                </div>
              </div>

            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

  </Panel>
</template>

<style>
@media print {
  body > * {
    display: none !important;
  }
  .print-modal-overlay {
    position: absolute !important;
    left: 0 !important;
    top: 0 !important;
    width: 100% !important;
    height: auto !important;
    background: transparent !important;
    display: block !important;
    z-index: 99999 !important;
  }
  .print-modal-container {
    position: absolute !important;
    left: 0 !important;
    top: 0 !important;
    width: 210mm !important;
    max-width: 210mm !important;
    height: auto !important;
    box-shadow: none !important;
    border: none !important;
    overflow: visible !important;
  }
  #print-area, #print-area * {
    visibility: visible;
  }
  #print-area {
    padding: 20px !important;
  }
  @page {
    size: A4 portrait;
    margin: 1cm;
  }
}
</style>
