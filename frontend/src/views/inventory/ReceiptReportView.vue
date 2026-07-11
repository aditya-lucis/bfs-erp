<template>
  <Panel title="Receipt Report" subtitle="Inventory | Receipt Report">
    
    <!-- Toolbar/Search/Filter -->
    <div class="flex flex-col gap-4 mb-6">
      <div class="flex flex-wrap items-center gap-4">
        <!-- Search -->
        <div class="flex items-center gap-2">
          <div class="flex items-center border border-gray-200 rounded-lg overflow-hidden bg-white h-[34px]">
            <span class="px-3 py-1.5 bg-gray-50 text-xs text-gray-500 border-r border-gray-200 h-full flex items-center">Search</span>
            <input
              v-model="filters.po_number"
              type="text"
              placeholder="Type PO Number..."
              class="px-3 py-1.5 text-xs focus:outline-none w-48 sm:w-64 h-full"
              @keyup.enter="applyFilters"
            />
          </div>
          
          <div class="flex items-center border border-gray-200 rounded-lg overflow-hidden bg-white h-[34px] ml-2">
            <span class="px-3 py-1.5 bg-gray-50 text-xs text-gray-500 border-r border-gray-200 h-full flex items-center">Date</span>
            <input type="date" v-model="filters.start_date" @change="applyFilters" class="px-2 py-1 text-xs focus:outline-none h-full text-gray-600 border-r border-gray-100">
            <span class="px-2 py-1 text-xs text-gray-400 bg-gray-50 h-full flex items-center border-r border-gray-100">to</span>
            <input type="date" v-model="filters.end_date" @change="applyFilters" class="px-2 py-1 text-xs focus:outline-none h-full text-gray-600">
          </div>
        </div>

        <button
          @click="applyFilters"
          class="px-3 py-1.5 bg-bfs-navy hover:bg-bfs-navy-dark text-white text-xs font-medium rounded-lg transition-colors flex items-center gap-1.5 cursor-pointer"
        >
          <Search class="w-3.5 h-3.5" /> Search
        </button>
        <button
          @click="resetFilters"
          class="btn-secondary text-xs px-3 py-1.5 flex items-center gap-1.5"
        >
          Reset
        </button>
      </div>

      <div class="flex flex-wrap items-center justify-between gap-4 border-t border-gray-100 pt-4">
        <div class="flex flex-wrap items-center gap-4 text-xs">
          <!-- Receipt Report Type Dropdown -->
          <div class="flex items-center gap-2">
            <span class="text-gray-500 font-semibold">Receipt Report Type:</span>
            <select v-model="filters.receipt_type" class="border border-gray-200 rounded px-2 py-1 bg-white focus:outline-none h-[34px]" @change="applyFilters">
              <option value="RR_PUR">Receipt Report For Purchase</option>
              <option value="RR_SRT" disabled>Receipt Report For Sales Return</option>
              <option value="RR_INT" disabled>Receipt Report For Internal</option>
              <option value="RR_SRV" disabled>Receipt Report For Service Note</option>
              <option value="RR_REP" disabled>Receipt Report For Repair</option>
            </select>
          </div>

          <!-- Filter Status (Sokka Style) -->
          <div class="border border-gray-200 rounded-lg px-3 py-1.5 relative bg-white flex items-center gap-2 shadow-sm min-h-[38px]">
            <span class="absolute -top-2 left-2 bg-white px-1 text-[9px] font-bold text-gray-500 uppercase tracking-wider">Filter Status</span>
            <button 
              @click="filters.document_status = ''; applyFilters()" 
              class="px-1.5 py-0.5 rounded text-[10px] font-bold transition-colors cursor-pointer"
              :class="filters.document_status === '' ? 'bg-bfs-navy text-white' : 'hover:bg-gray-100 text-gray-400'"
              title="All Status"
            >
              ALL
            </button>
            <button 
              @click="filters.document_status = 'draft'; applyFilters()" 
              class="p-0.5 rounded transition-all cursor-pointer"
              :class="filters.document_status === 'draft' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"
              title="Draft (Editable)"
            >
              <Folder class="w-4 h-4 text-amber-500 fill-amber-500/10" />
            </button>
            <button 
              @click="filters.document_status = 'ready_to_process'; applyFilters()" 
              class="p-0.5 rounded transition-all cursor-pointer"
              :class="filters.document_status === 'ready_to_process' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"
              title="Ready to Process (Open)"
            >
              <FolderOpen class="w-4 h-4 text-blue-500 fill-blue-500/10" />
            </button>
            <button 
              @click="filters.document_status = 'close'; applyFilters()" 
              class="p-0.5 rounded transition-all cursor-pointer"
              :class="filters.document_status === 'close' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"
              title="Closed"
            >
              <FolderCheck class="w-4 h-4 text-emerald-500 fill-emerald-500/10" />
            </button>
          </div>

          <!-- Approval Filter Status (Sokka Style) -->
          <div class="border border-gray-200 rounded-lg px-3 py-1.5 relative bg-white flex items-center gap-2 shadow-sm min-h-[38px]">
            <span class="absolute -top-2 left-2 bg-white px-1 text-[9px] font-bold text-gray-500 uppercase tracking-wider">Approval Filter Status</span>
            <button 
              @click="filters.approval_status = ''; applyFilters()" 
              class="px-1.5 py-0.5 rounded text-[10px] font-bold transition-colors cursor-pointer"
              :class="filters.approval_status === '' ? 'bg-bfs-navy text-white' : 'hover:bg-gray-100 text-gray-400'"
              title="All Approval"
            >
              ALL
            </button>
            <button 
              @click="filters.approval_status = 'draft'; applyFilters()" 
              class="p-0.5 rounded transition-all cursor-pointer"
              :class="filters.approval_status === 'draft' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"
              title="Draft"
            >
              <FileText class="w-4 h-4 text-gray-400" />
            </button>
            <button 
              @click="filters.approval_status = 'awaiting'; applyFilters()" 
              class="p-0.5 rounded transition-all cursor-pointer"
              :class="filters.approval_status === 'awaiting' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"
              title="Awaiting Approval"
            >
              <FileClock class="w-4 h-4 text-bfs-gold animate-pulse" />
            </button>
            <button 
              @click="filters.approval_status = 'approved'; applyFilters()" 
              class="p-0.5 rounded transition-all cursor-pointer"
              :class="filters.approval_status === 'approved' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"
              title="Approved"
            >
              <FileCheck class="w-4 h-4 text-green-500" />
            </button>
            <button 
              @click="filters.approval_status = 'rejected'; applyFilters()" 
              class="p-0.5 rounded transition-all cursor-pointer"
              :class="filters.approval_status === 'rejected' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"
              title="Rejected"
            >
              <FileX class="w-4 h-4 text-red-500" />
            </button>
            <button 
              @click="filters.approval_status = 'revised'; applyFilters()" 
              class="p-0.5 rounded transition-all cursor-pointer"
              :class="filters.approval_status === 'revised' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"
              title="Revised"
            >
              <FileWarning class="w-4 h-4 text-orange-500" />
            </button>
          </div>
        </div>

        <button
          @click="showCreateModal = true"
          class="px-4 py-2 bg-bfs-gold text-white text-xs font-semibold rounded-lg hover:bg-[#C2A05B] transition-colors shadow-sm flex items-center gap-1.5 ml-auto cursor-pointer"
        >
          <Plus class="w-3.5 h-3.5" /> Add Receipt Report
        </button>
      </div>
    </div>
    
    <!-- Loading -->
    <div v-if="store.loading && !store.receiptReports.length" class="flex justify-center py-16">
      <Loader2 class="w-6 h-6 animate-spin text-bfs-gold" />
    </div>
    
    <!-- Table List -->
    <div v-else-if="store.receiptReports.length" class="border border-gray-200 rounded-xl overflow-hidden bg-white shadow-sm">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          
          <thead>
            <tr class="bg-gray-50 border-b border-gray-200 text-[11px] font-semibold text-gray-600 uppercase tracking-wider">
              <th class="py-3 px-4 w-12 text-center">No.</th>
              <th class="py-3 px-4">Receipt Report Number</th>
              <th class="py-3 px-4">Receive Date</th>
              <th class="py-3 px-4">PO Number</th>
              <th class="py-3 px-4">Vendor</th>
              <th class="py-3 px-4 text-center">Document Status</th>
              <th class="py-3 px-4 text-center">Approval</th>
              <th class="py-3 px-4 w-20 text-right">Actions</th>
            </tr>
          </thead>

          <tbody class="divide-y divide-gray-100">
            <tr v-for="(rr, idx) in store.receiptReports" :key="rr.id" class="hover:bg-yellow-50/20 transition-colors text-xs text-gray-700">
              <td class="py-3 px-4 text-center font-medium text-gray-400">{{ (store.pagination.page - 1) * store.pagination.limit + idx + 1 }}.</td>
              <td class="py-3 px-4 font-mono text-gray-600 font-semibold">{{ rr.receipt_number }}</td>
              <td class="py-3 px-4">{{ rr.receive_date }}</td>
              <td class="py-3 px-4 font-mono">{{ rr.po_number || '-' }}</td>
              <td class="py-3 px-4 truncate max-w-[150px]" :title="rr.vendor_name">{{ rr.vendor_name || '-' }}</td>
              
              <td class="py-3 px-4 text-center">
                  <div class="inline-flex items-center justify-center p-1 rounded-md" :title="rr.document_status">
                    <Folder v-if="rr.document_status === 'draft'" class="w-4.5 h-4.5 text-amber-500 fill-amber-500/10" />
                    <FolderOpen v-else-if="rr.document_status === 'ready_to_process'" class="w-4.5 h-4.5 text-blue-500 fill-blue-500/10" />
                    <FolderCheck v-else class="w-4.5 h-4.5 text-green-500 fill-green-500/10" />
                  </div>
                </td>
              <td class="py-3 px-4 text-center">
                <div class="inline-flex items-center justify-center p-1 rounded-md" :title="rr.approval_status">
                  <FileText v-if="rr.approval_status === 'draft'" class="w-4.5 h-4.5 text-gray-400" />
                  <FileClock v-else-if="rr.approval_status === 'awaiting'" class="w-4.5 h-4.5 text-bfs-gold animate-pulse" />
                  <FileCheck v-else-if="rr.approval_status === 'approved'" class="w-4.5 h-4.5 text-green-500" />
                  <FileX v-else-if="rr.approval_status === 'rejected'" class="w-4.5 h-4.5 text-red-500" />
                  <FileWarning v-else-if="rr.approval_status === 'revised'" class="w-4.5 h-4.5 text-orange-500" />
                </div>
              </td>
              <td class="py-3 px-4 text-right">
                  <div class="flex justify-end gap-1.5">
                    <button @click="openTrackingModal(rr)" class="p-1 text-gray-400 hover:text-indigo-500 transition-colors cursor-pointer" title="Tracking Info">
                      <MapPin class="w-3.5 h-3.5" />
                    </button>
                    <button @click="printRR(rr.id)" class="p-1 text-gray-400 hover:text-gray-900 transition-colors cursor-pointer" title="Print Document">
                      <Printer class="w-3.5 h-3.5" />
                    </button>
                    <button @click="openEditModal(rr)" class="p-1 text-gray-400 hover:text-bfs-gold transition-colors cursor-pointer" title="View/Edit">
                      <Pencil class="w-3.5 h-3.5" />
                    </button>
                    <button v-if="['draft', 'revised'].includes(rr.approval_status)" @click="submitRR(rr.id)" class="p-1 text-gray-400 hover:text-blue-500 transition-colors cursor-pointer" title="Submit">
                      <Send class="w-3.5 h-3.5" />
                    </button>
                    <button v-if="rr.approval_status === 'awaiting'" @click="approveRR(rr.id)" class="p-1 text-gray-400 hover:text-green-500 transition-colors cursor-pointer" title="Approve">
                      <FileCheck class="w-3.5 h-3.5" />
                    </button>
                    <button v-if="rr.approval_status === 'approved'" @click="voidRR(rr.id)" class="p-1 text-gray-400 hover:text-red-500 transition-colors cursor-pointer" title="Void Document">
                      <FileX class="w-3.5 h-3.5" />
                    </button>
                  </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <div v-else class="text-center py-16 text-gray-500 text-sm">
      ... NO RECORDS ...
    </div>
    
    <ReceiptReportFormModal v-if="showCreateModal" @close="showCreateModal = false; selectedRR = null" :editId="selectedRR" @success="handleSuccess" />

    <!-- Print Modal -->
    <ReceiptReportPrintTemplate
      :show="showPrintModal"
      :documentId="printRRId"
      @close="closePrintModal"
    />

    <!-- Tracking Modal -->
    <ReceiptReportTrackingModal
      :show="showTrackingModal"
      :documentId="trackingRRId"
      :receiptNumber="trackingRRNumber"
      @close="closeTrackingModal"
      @success="handleSuccess"
    />
  </Panel>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useReceiptReportStore } from '../../stores/inventory/receiptReportStore'
import ReceiptReportFormModal from '../../components/inventory/ReceiptReportFormModal.vue'
import ReceiptReportPrintTemplate from '../../components/inventory/ReceiptReportPrintTemplate.vue'
import ReceiptReportTrackingModal from '../../components/inventory/ReceiptReportTrackingModal.vue'
import Panel from '../../components/Panel.vue'
import Swal from 'sweetalert2'
import { 
  Folder, FolderOpen, FolderCheck, 
  FileText, FileClock, FileCheck, FileX, FileWarning, 
  Search, Plus, Send, Printer, Pencil, Unlock, Lock, AlertCircle, Loader2,
  CheckCircle, XCircle, Clock, MapPin
} from 'lucide-vue-next'

import { useRouter } from 'vue-router'

const store = useReceiptReportStore()
const router = useRouter()
const showCreateModal = ref(false)
const selectedRR = ref(null)

const showPrintModal = ref(false)
const printRRId = ref(null)

const showTrackingModal = ref(false)
const trackingRRId = ref(null)
const trackingRRNumber = ref('')

function getDefaultDates() {
  const today = new Date();
  const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
  const lastDay = new Date(today.getFullYear(), today.getMonth() + 1, 0);
  
  // Format to YYYY-MM-DD (handling local timezone appropriately by simple offset)
  const formatDate = (date) => {
    const d = new Date(date);
    d.setMinutes(d.getMinutes() - d.getTimezoneOffset());
    return d.toISOString().split('T')[0];
  };
  
  return {
    start: formatDate(firstDay),
    end: formatDate(lastDay)
  };
}

const defaultDates = getDefaultDates();

const filters = reactive({
  po_number: '',
  receipt_type: 'RR_PUR',
  document_status: '',
  approval_status: '',
  start_date: defaultDates.start,
  end_date: defaultDates.end
})

onMounted(() => {
  store.fetchReceiptReports()
})

function applyFilters() {
  store.setFilters(filters)
}

function resetFilters() {
  const defaultDates = getDefaultDates();
  filters.po_number = ''
  filters.approval_status = ''
  filters.document_status = ''
  filters.start_date = defaultDates.start
  filters.end_date = defaultDates.end
  applyFilters()
}

function handleSuccess() {
  showCreateModal.value = false
  selectedRR.value = null
  store.fetchReceiptReports()
  Swal.fire({
    title: 'Success!',
    text: 'Receipt Report has been saved successfully.',
    icon: 'success',
    confirmButtonColor: '#C2A05B'
  })
}

function openEditModal(rr) {
  selectedRR.value = rr.id
  showCreateModal.value = true
}

function printRR(id) {
  printRRId.value = id
  showPrintModal.value = true
}

function closePrintModal() {
  showPrintModal.value = false
  printRRId.value = null
}

function openTrackingModal(rr) {
  trackingRRId.value = rr.id
  trackingRRNumber.value = rr.receipt_number
  showTrackingModal.value = true
}

function closeTrackingModal() {
  showTrackingModal.value = false
  trackingRRId.value = null
  trackingRRNumber.value = ''
}

async function submitRR(id) {
  const result = await Swal.fire({
    title: 'Are you sure?',
    text: "You want to submit this receipt report for approval?",
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#C2A05B',
    cancelButtonColor: '#d33',
    confirmButtonText: 'Yes, submit it!'
  })
  
  if (result.isConfirmed) {
    try {
      await store.submitReceiptReport(id)
      Swal.fire('Submitted!', 'Receipt report has been submitted.', 'success')
    } catch (error) {
      Swal.fire('Error!', error.detail || 'Failed to submit', 'error')
    }
  }
}

async function approveRR(id) {
  const { isConfirmed } = await Swal.fire({
    title: 'Approve Receipt Report?',
    text: 'Do you want to approve this receipt?',
    icon: 'question',
    showCancelButton: true,
    confirmButtonText: 'Yes, approve it!'
  })

  if (isConfirmed) {
    try {
      await store.approveReceiptReport(id, { action: 'approve' })
      Swal.fire({ icon: 'success', title: 'Approved', text: 'Receipt Report has been approved.' })
    } catch (error) {
      Swal.fire({ icon: 'error', title: 'Error', text: error.detail || 'Failed to approve.' })
    }
  }
}

async function voidRR(id) {
  const { value: reason, isConfirmed } = await Swal.fire({
    title: 'Void Receipt Report?',
    text: 'Please enter the reason for voiding this Receipt Report:',
    input: 'text',
    inputPlaceholder: 'Reason for void...',
    icon: 'warning',
    showCancelButton: true,
    confirmButtonText: 'Yes, void it!',
    confirmButtonColor: '#d33',
    inputValidator: (value) => {
      if (!value) {
        return 'You need to write a reason!'
      }
    }
  })

  if (isConfirmed && reason) {
    try {
      await store.voidReceiptReport(id, { void_reason: reason })
      Swal.fire({ icon: 'success', title: 'Voided', text: 'Receipt Report has been voided.' })
    } catch (error) {
      Swal.fire({ icon: 'error', title: 'Error', text: error.detail || 'Failed to void.' })
    }
  }
}
</script>
