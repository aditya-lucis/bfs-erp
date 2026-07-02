<template>
  <Panel title="Good Receipt Note" subtitle="Purchase | Good Receipt Note">
    
    <!-- Toolbar/Search/Filter -->
    <div class="flex flex-col gap-4 mb-6">
      <div class="flex flex-wrap items-center gap-4">
        <!-- Search -->
        <div class="flex items-center border border-gray-200 rounded-lg overflow-hidden bg-white">
          <span class="px-3 py-1.5 bg-gray-50 text-xs text-gray-500 border-r border-gray-200">Search</span>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Type Good Receipt Note Number or Vendor..."
            class="px-3 py-1.5 text-xs focus:outline-none w-48 sm:w-64"
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
          
          <!-- Filter Status (Sokka Style) -->
          <div class="border border-gray-200 rounded-lg px-3 py-1.5 relative bg-white flex items-center gap-2 shadow-sm min-h-[38px]">
            <span class="absolute -top-2 left-2 bg-white px-1 text-[9px] font-bold text-gray-500 uppercase tracking-wider">Filter Status</span>
            <button @click="filterDocStatus = ''" class="px-1.5 py-0.5 rounded text-[10px] font-bold transition-colors cursor-pointer" :class="filterDocStatus === '' ? 'bg-bfs-navy text-white' : 'hover:bg-gray-100 text-gray-400'">ALL</button>
            <button @click="filterDocStatus = 'draft'" class="p-0.5 rounded transition-all cursor-pointer" :class="filterDocStatus === 'draft' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"><Folder class="w-4 h-4 text-amber-500 fill-amber-500/10" /></button>
            <button @click="filterDocStatus = 'ready'" class="p-0.5 rounded transition-all cursor-pointer" :class="filterDocStatus === 'ready' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"><FolderOpen class="w-4 h-4 text-blue-500 fill-blue-500/10" /></button>
            <button @click="filterDocStatus = 'close'" class="p-0.5 rounded transition-all cursor-pointer" :class="filterDocStatus === 'close' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"><FolderCheck class="w-4 h-4 text-green-500 fill-green-500/10" /></button>
          </div>

          <!-- Approval Filter Status (Sokka Style) -->
          <div class="border border-gray-200 rounded-lg px-3 py-1.5 relative bg-white flex items-center gap-2 shadow-sm min-h-[38px]">
            <span class="absolute -top-2 left-2 bg-white px-1 text-[9px] font-bold text-gray-500 uppercase tracking-wider">Approval Filter Status</span>
            <button @click="filterAppStatus = ''" class="px-1.5 py-0.5 rounded text-[10px] font-bold transition-colors cursor-pointer" :class="filterAppStatus === '' ? 'bg-bfs-navy text-white' : 'hover:bg-gray-100 text-gray-400'">ALL</button>
            <button @click="filterAppStatus = 'draft'" class="p-0.5 rounded transition-all cursor-pointer" :class="filterAppStatus === 'draft' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"><FileText class="w-4 h-4 text-gray-400" /></button>
            <button @click="filterAppStatus = 'awaiting'" class="p-0.5 rounded transition-all cursor-pointer" :class="filterAppStatus === 'awaiting' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"><FileClock class="w-4 h-4 text-bfs-gold animate-pulse" /></button>
            <button @click="filterAppStatus = 'approved'" class="p-0.5 rounded transition-all cursor-pointer" :class="filterAppStatus === 'approved' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"><FileCheck class="w-4 h-4 text-green-500" /></button>
            <button @click="filterAppStatus = 'rejected'" class="p-0.5 rounded transition-all cursor-pointer" :class="filterAppStatus === 'rejected' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"><FileX class="w-4 h-4 text-red-500" /></button>
            <button @click="filterAppStatus = 'revised'" class="p-0.5 rounded transition-all cursor-pointer" :class="filterAppStatus === 'revised' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"><FileWarning class="w-4 h-4 text-orange-500" /></button>
          </div>
        </div>

        <button
          v-if="canCreate"
          @click="openAddModal"
          class="px-4 py-2 bg-bfs-gold text-white text-xs font-semibold rounded-lg hover:bg-[#C2A05B] transition-colors shadow-sm flex items-center gap-1.5 ml-auto"
        >
          <Plus class="w-3.5 h-3.5" /> New GRN
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="store.loading && !filteredGRNs.length" class="flex justify-center py-16">
      <Loader2 class="w-6 h-6 animate-spin text-bfs-gold" />
    </div>

    <!-- Table -->
    <div v-else-if="filteredGRNs.length" class="border border-gray-200 rounded-xl overflow-hidden bg-white shadow-sm">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-gray-50 border-b border-gray-200 text-[11px] font-semibold text-gray-600 uppercase tracking-wider">
              <th class="py-3 px-4 w-12 text-center">NO.</th>
              <th class="py-3 px-4">GRN NUMBER</th>
              <th class="py-3 px-4">VENDOR</th>
              <th class="py-3 px-4">DOCUMENT DATE</th>
              <th class="py-3 px-4">PURCHASE ORDER NO</th>
              <th class="py-3 px-4 text-center">DOCUMENT STATUS</th>
              <th class="py-3 px-4 text-center">APPROVAL</th>
              <th class="py-3 px-4 text-center">IS ACTIVE</th>
              <th class="py-3 px-4 text-center">TYPE</th>
              <th class="py-3 px-4 text-right">AMOUNT</th>
              <th class="py-3 px-4">SITE NAME</th>
              <th class="py-3 px-4 text-center w-20">ACTIONS</th>
            </tr>
          </thead>
          
          <tbody class="divide-y divide-gray-100">
            <tr v-for="(grn, idx) in filteredGRNs" :key="grn.id" class="hover:bg-yellow-50/20 transition-colors text-xs text-gray-700">
              <td class="py-3 px-4 text-center font-medium text-gray-400">{{ idx + 1 }}.</td>
              <td class="py-3 px-4 font-mono text-gray-600 font-semibold cursor-pointer hover:text-bfs-navy" @click="openEditModal(grn)">
                {{ grn.grn_number }}
              </td>
              <td class="py-3 px-4 truncate max-w-[150px]" :title="grn.vendor_name">{{ grn.vendor_name || '-' }}</td>
              <td class="py-3 px-4">{{ grn.document_date }}</td>
              <td class="py-3 px-4 font-mono">{{ grn.po_number || '-' }}</td>
              
              <td class="py-3 px-4 text-center">
                <div class="inline-flex items-center justify-center p-1 rounded-md" :title="getDocStatus(grn.approval_status)">
                  <Folder v-if="getDocStatus(grn.approval_status) === 'draft'" class="w-4.5 h-4.5 text-amber-500 fill-amber-500/10" />
                  <FolderOpen v-else-if="getDocStatus(grn.approval_status) === 'ready'" class="w-4.5 h-4.5 text-blue-500 fill-blue-500/10" />
                  <FolderCheck v-else-if="getDocStatus(grn.approval_status) === 'close'" class="w-4.5 h-4.5 text-green-500 fill-green-500/10" />
                </div>
              </td>
              <td class="py-3 px-4 text-center">
                <div class="inline-flex items-center justify-center p-1 rounded-md" :title="grn.approval_status">
                  <FileText v-if="grn.approval_status?.toLowerCase() === 'draft'" class="w-4.5 h-4.5 text-gray-400" />
                  <FileClock v-else-if="grn.approval_status?.toLowerCase() === 'awaiting'" class="w-4.5 h-4.5 text-bfs-gold animate-pulse" />
                  <FileCheck v-else-if="grn.approval_status?.toLowerCase() === 'approved'" class="w-4.5 h-4.5 text-green-500" />
                  <FileX v-else-if="grn.approval_status?.toLowerCase() === 'rejected'" class="w-4.5 h-4.5 text-red-500" />
                  <FileWarning v-else-if="grn.approval_status?.toLowerCase() === 'revised'" class="w-4.5 h-4.5 text-orange-500" />
                </div>
              </td>
              
              <td class="py-3 px-4 text-center">
                <div v-if="grn.is_active" class="flex items-center justify-center">
                  <span class="text-green-500 font-bold text-base">✓</span>
                </div>
                <div v-else class="flex items-center justify-center gap-1">
                  <span class="text-red-500 font-bold text-base">✗</span>
                  <div v-if="grn.void_reason" class="relative group">
                    <AlertCircle class="w-4 h-4 text-pink-500 cursor-help" />
                    <div class="absolute left-1/2 -translate-x-1/2 bottom-full mb-1 hidden group-hover:block w-56 p-2 bg-pink-100 border border-pink-300 text-pink-800 text-[10px] rounded shadow-lg z-50 text-left">
                      <strong>Voided At:</strong> {{ grn.void_date ? new Date(grn.void_date).toLocaleDateString() : '-' }}<br/>
                      <strong>Reason:</strong> {{ grn.void_reason }}
                    </div>
                  </div>
                </div>
              </td>
              <td class="py-3 px-4 text-center font-semibold text-gray-600">{{ grn.type }}</td>
              <td class="py-3 px-4 text-right font-semibold text-bfs-navy whitespace-nowrap">
                IDR. {{ formatCurrency(grn.amount) }}
              </td>
              <td class="py-3 px-4 truncate max-w-[150px]" :title="grn.site_name">{{ grn.site_name || '-' }}</td>
              <td class="py-3 px-4 text-center">
                <div class="flex items-center justify-center gap-1.5">
                  <button
                    @click="openPrintPreview(grn)"
                    class="p-1 text-gray-400 hover:text-blue-500 transition-colors"
                    title="Print"
                  >
                    <Printer class="w-3.5 h-3.5" />
                  </button>
                  <button
                    v-if="canUpdate"
                    @click="openEditModal(grn)"
                    class="p-1 text-gray-400 hover:text-bfs-gold transition-colors"
                    title="Edit"
                  >
                    <Pencil class="w-3.5 h-3.5" />
                  </button>
                  <button
                    v-if="canUpdate && grn.is_active"
                    @click="voidGRN(grn)"
                    class="p-1 text-gray-400 hover:text-red-500 transition-colors"
                    title="Void"
                  >
                    <Ban class="w-3.5 h-3.5" />
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

    <GoodReceiptNoteFormModal
      :is-open="isModalOpen"
      :edit-data="selectedGRN"
      @close="closeModal"
    />
    
    <!-- Print Template -->
    <GRNPrintTemplate
      :show="showPrintPreview"
      :grn="printDetail"
      :signatures="printSignatures"
      @close="showPrintPreview = false"
    />
  </Panel>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import Panel from '../../components/Panel.vue'
import GoodReceiptNoteFormModal from '../../components/purchase/GoodReceiptNoteFormModal.vue'
import GRNPrintTemplate from '../../components/purchase/GRNPrintTemplate.vue'
import { Plus, Search, Loader2, Pencil, FileText, Folder, FolderOpen, FolderCheck, FileCheck, FileX, FileClock, FileWarning, Printer, Ban, AlertCircle } from 'lucide-vue-next'
import { useGoodReceiptNoteStore } from '../../stores/goodReceiptNote'
import { usePermission } from '../../composables/usePermission.js'
import api from '../../services/api'
import { useApprovalRequestStore } from '../../stores/approvalRequest'
import Swal from 'sweetalert2'

const { canCreate, canUpdate } = usePermission('PURCHASES-GOOD-RECEIPT-NOTE')

const store = useGoodReceiptNoteStore()
const approvalStore = useApprovalRequestStore()

// Native JS Date helpers for Start/End of Month
const getStartOfMonth = () => {
  const d = new Date();
  return new Date(d.getFullYear(), d.getMonth(), 1).toISOString().split('T')[0];
}
const getEndOfMonth = () => {
  const d = new Date();
  return new Date(d.getFullYear(), d.getMonth() + 1, 0).toISOString().split('T')[0];
}

// State
const searchQuery = ref('')
const filterDateFrom = ref(getStartOfMonth())
const filterDateTo = ref(getEndOfMonth())
const filterAppStatus = ref('')
const filterDocStatus = ref('')

const isModalOpen = ref(false)
const selectedGRN = ref(null)

// --- Print Logic ---
const showPrintPreview = ref(false)
const printDetail = ref(null)
const printSignatures = ref([])

async function openPrintPreview(grnItem) {
  showPrintPreview.value = true
  try {
    const res = await api.get(`/purchase/good-receipt-notes/${grnItem.id}/`)
    const grnData = res.data
    
    if (grnData.po) {
      const poRes = await api.get(`/purchase/po/${grnData.po}/`)
      grnData.po_detail = poRes.data
    }
    printDetail.value = grnData

    const sigs = await approvalStore.fetchSignatures('GRN', grnItem.id)
    printSignatures.value = sigs
  } catch (e) {
    console.error('Failed to load print details', e)
    printSignatures.value = []
  }
}

async function voidGRN(grnItem) {
    const { value: reason } = await Swal.fire({
      title: 'Void Good Receipt Note?',
      text: "Anda yakin ingin melakukan void GRN ini? Silakan masukkan alasannya (Wajib):",
      input: 'textarea',
      inputPlaceholder: 'Masukkan alasan void...',
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#d33',
      cancelButtonColor: '#3085d6',
      confirmButtonText: 'Process Void',
      cancelButtonText: 'Batal',
      inputValidator: (value) => {
        if (!value || value.trim() === '') {
          return 'Alasan void wajib diisi!'
        }
      }
    })

    if (reason) {
      try {
        store.loading = true
        await api.post(`/purchase/good-receipt-notes/${grnItem.id}/void_grn/`, {
          void_reason: reason
        })
        await store.fetchGRNs()
        Swal.fire({
          icon: 'success',
          title: 'Berhasil',
          text: 'GRN berhasil di-void dan status tidak aktif.',
          confirmButtonColor: '#1e3a8a'
        })
      } catch (err) {
        Swal.fire({
          icon: 'error',
          title: 'Gagal',
          text: err.response?.data?.detail || 'Terjadi kesalahan saat memproses void GRN.',
          confirmButtonColor: '#1e3a8a'
        })
      } finally {
        store.loading = false
      }
    }
}

const handleResetFilters = () => {
  searchQuery.value = ''
  filterDateFrom.value = getStartOfMonth()
  filterDateTo.value = getEndOfMonth()
  filterAppStatus.value = ''
  filterDocStatus.value = ''
}

const getDocStatus = (approval_status) => {
  const status = (approval_status || '').toLowerCase()
  if (['draft', 'revised'].includes(status)) return 'draft'
  if (['awaiting'].includes(status)) return 'ready'
  if (['approved', 'rejected'].includes(status)) return 'close'
  return 'draft'
}

const filteredGRNs = computed(() => {
  return store.grns.filter(grn => {
    // Search
    let matchesSearch = true
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      const noMatch = grn.grn_number?.toLowerCase().includes(query)
      const vendorMatch = grn.vendor_name?.toLowerCase().includes(query)
      matchesSearch = noMatch || vendorMatch
    }
    
    // Date Range
    let matchesDate = true
    if (filterDateFrom.value && filterDateTo.value) {
      matchesDate = grn.document_date >= filterDateFrom.value && grn.document_date <= filterDateTo.value
    }

    // Document Status
    let matchesDocStatus = true
    if (filterDocStatus.value) {
      matchesDocStatus = getDocStatus(grn.approval_status) === filterDocStatus.value
    }
    
    // Approval Status
    let matchesApp = true
    if (filterAppStatus.value) {
      matchesApp = grn.approval_status?.toLowerCase() === filterAppStatus.value.toLowerCase()
    }
    
    return matchesSearch && matchesDate && matchesApp && matchesDocStatus
  })
})

onMounted(() => {
  store.fetchGRNs()
})

function openAddModal() {
  selectedGRN.value = null
  isModalOpen.value = true
}

function openEditModal(grn) {
  selectedGRN.value = grn
  isModalOpen.value = true
}

function closeModal() {
  isModalOpen.value = false
}

function formatCurrency(val) {
  if (!val) return '0.00'
  return Number(val).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}
</script>
