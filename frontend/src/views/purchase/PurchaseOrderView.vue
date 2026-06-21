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
                <span v-if="po.document_status !== 'close'" class="text-green-500 font-bold text-base">✓</span>
                <span v-else class="text-red-500 font-bold text-base">✗</span>
              </td>
              <td class="py-3 px-4 text-center">
                <span v-if="po.document_status === 'close'" class="text-green-500 font-bold text-base">✓</span>
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
                  <button v-if="po.document_status === 'draft'" @click="deletePO(po.id)" class="p-1 text-gray-400 hover:text-red-500 transition-colors" title="Delete">
                    <Trash2 class="w-3.5 h-3.5" />
                  </button>
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
              <div class="p-8 print:p-0 print:pt-4">
                <!-- Meta Info Grid -->
                <div class="grid grid-cols-2 gap-x-8 gap-y-1 mb-6">
                  <div>
                    <table class="w-full">
                      <tr><td class="w-36 py-0.5 align-top">PO Number</td><td class="w-4 align-top">:</td><td class="font-medium align-top">{{ printModal.po?.po_number }}</td></tr>
                      <tr><td class="py-0.5 align-top">Project Name</td><td class="align-top">:</td><td class="align-top">{{ printModal.po?.project_name || '-' }}</td></tr>
                      <tr><td class="py-0.5 align-top">RAP Number</td><td class="align-top">:</td><td class="align-top">{{ printModal.po?.rap_number || printModal.po?.rap_name || '-' }}</td></tr>
                      <tr><td class="py-0.5 align-top">PO Date</td><td class="align-top">:</td><td class="align-top">{{ formatDatePrint(printModal.po?.po_date) }}</td></tr>
                      <tr><td class="py-0.5 align-top">ETD</td><td class="align-top">:</td><td class="align-top">{{ formatDatePrint(printModal.po?.etd) }}</td></tr>
                    </table>
                  </div>
                  <div>
                    <table class="w-full">
                      <tr><td class="w-24 py-0.5 align-top">Delivery Point</td><td class="w-4 align-top">:</td><td class="align-top">{{ printModal.po?.delivery_point || '-' }}</td></tr>
                      <tr><td class="py-0.5 align-top">Vendor</td><td class="align-top">:</td><td class="align-top">{{ printModal.po?.vendor_name || '-' }}</td></tr>
                    </table>
                  </div>
                </div>

                <!-- Details Table -->
                <div class="mb-6">
                  <table class="w-full border-collapse border border-black text-xs">
                    <thead>
                      <tr class="bg-gray-100 text-center">
                        <th class="border border-black py-1.5 px-2 w-10">No</th>
                        <th class="border border-black py-1.5 px-2">Item Name</th>
                        <th class="border border-black py-1.5 px-2">Notes</th>
                        <th class="border border-black py-1.5 px-2 w-16">Qty</th>
                        <th class="border border-black py-1.5 px-2 w-20">Unit</th>
                        <th class="border border-black py-1.5 px-2 w-28">Unit Price</th>
                        <th class="border border-black py-1.5 px-2 w-28">Total Price</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(item, idx) in printDetails" :key="idx">
                        <td class="border border-black py-1 px-2 text-center align-top">{{ idx + 1 }}.</td>
                        <td class="border border-black py-1 px-2 align-top">{{ item.item_name || item.item || '-' }}</td>
                        <td class="border border-black py-1 px-2 align-top">{{ item.notes || '-' }}</td>
                        <td class="border border-black py-1 px-2 text-center align-top">{{ item.quantity }}</td>
                        <td class="border border-black py-1 px-2 text-center align-top">{{ item.unit_name || 'Unit' }}</td>
                        <td class="border border-black py-1 px-2 text-right align-top">{{ formatCurrencyRaw(item.unit_price) }}</td>
                        <td class="border border-black py-1 px-2 text-right align-top">{{ formatCurrencyRaw(item.quantity * item.unit_price) }}</td>
                      </tr>
                      <tr>
                        <td colspan="6" class="border border-black py-1 px-2 text-right font-bold text-sm">Grand Total</td>
                        <td class="border border-black py-1 px-2 text-right font-bold text-sm">{{ formatCurrencyRaw(printGrandTotal) }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                <!-- Notes -->
                <div class="mb-12">
                  <span class="font-bold text-sm">Notes:</span> <span class="font-bold text-sm ml-2">{{ printModal.po?.notes || '-' }}</span>
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
import { 
  Search, Plus, Loader2, Edit3, Trash2, Send, Pencil, Printer, CheckSquare,
  Folder, FolderOpen, FolderCheck,
  FileText, FileClock, FileCheck, FileX, FileWarning, X, AlertCircle, Save
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
  printModal.value.po = pr
  printModal.value.show = true
  printModal.value.signatures = []
  printDetails.value = []
  
  if (!orgStore.company) {
    orgStore.fetchCompany()
  }
  
  // Fetch full details
  try {
    const fullPo = await store.fetchPODetails(po.id)
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

const printGrandTotal = computed(() => {
  return printDetails.value.reduce((sum, item) => sum + (parseFloat(item.amount) || parseFloat(item.quantity) * parseFloat(item.unit_price) || 0), 0)
})

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
  store.fetchPOs({
    search: searchQuery.value,
    po_type: filterItemCategory.value,
    document_status: filterDocStatus.value,
    approval_status: filterAppStatus.value,
    start_date: filterDateFrom.value,
    end_date: filterDateTo.value,
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

async function deletePO(id) {
  if (confirm('Are you sure you want to delete this PO?')) {
    try {
      await store.deletePO(id)
      handleSearch()
    } catch (e) {
      alert(store.error || 'Delete failed')
    }
  }
}


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

function openEditModal(po) {
  modal.value.mode = 'edit'
  modal.value.editId = po.id
  modal.value.show = true
}
</script>
<style scoped>
@media print {
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
