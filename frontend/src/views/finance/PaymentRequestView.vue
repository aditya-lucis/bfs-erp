<template>
  <Panel title="Payment Request" subtitle="Finance | Payment Request | Payment Request">

    <!-- Toolbar/Search/Filter -->
    <div class="flex flex-col gap-4 mb-6">
      <div class="flex flex-wrap items-center gap-4">
        <!-- Search -->
        <div class="flex items-center border border-gray-200 rounded-lg overflow-hidden bg-white">
          <span class="px-3 py-1.5 bg-gray-50 text-xs text-gray-500 border-r border-gray-200">Search</span>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Type Document Number..."
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
        <div class="flex flex-col gap-3 w-full">
          <!-- Main Filters Row -->
          <div class="flex flex-wrap items-center justify-between gap-4">
            
            <!-- Dynamic Filters -->
            <div class="flex items-center gap-4 text-xs">
              <div class="flex items-center gap-2">
                <span class="text-gray-500 font-semibold">Type :</span>
                <select v-model="filterType" class="border border-gray-200 rounded px-2 py-1 bg-white focus:outline-none h-[34px]" @change="handleSearch">
                  <option value="Disbursement">Disbursement</option>
                </select>
              </div>

              <div class="flex items-center gap-2">
                <span class="text-gray-500 font-semibold">Usage For :</span>
                <select v-model="filterUsageFor" class="border border-gray-200 rounded px-2 py-1 bg-white focus:outline-none h-[34px]" @change="handleUsageForChange">
                  <option value="Purchase Invoice Payment">Purchase Invoice Payment</option>
                  <option value="Project Cash Advanced">Project Cash Advanced</option>
                  <option value="Purchase Order Down Payment">Purchase Order Down Payment</option>
                  <option value="Bank Obligation Principal">Bank Obligation Principal</option>
                  <option value="Bank Obligation Interest">Bank Obligation Interest</option>
                </select>
              </div>

              <div v-if="filterUsageFor === 'Project Cash Advanced'" class="flex items-center gap-2">
                <span class="text-gray-500 font-semibold">Declaration :</span>
                <select v-model="filterDeclaration" class="border border-gray-200 rounded px-2 py-1 bg-white focus:outline-none h-[34px]" @change="handleSearch">
                  <option value="">All</option>
                  <option value="Yes">Yes</option>
                  <option value="No">No</option>
                </select>
              </div>
            </div>

            <div class="flex items-center gap-4 text-xs">
              <!-- Filter Status (Sokka Style) -->
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
          </div>
        </div>
      </div>
    </div>

    <!-- Table List -->
    <div class="border border-gray-200 rounded-xl overflow-hidden bg-white shadow-sm">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse whitespace-nowrap">
          <thead>
            <tr class="bg-gray-200 border-b border-gray-300 text-[11px] font-bold text-gray-700 tracking-wider">
              <th class="py-2 px-2 text-center w-10">
                <input type="checkbox" class="rounded border-gray-300 text-bfs-gold focus:ring-bfs-gold cursor-pointer" />
              </th>
              <th class="py-2 px-2">No.</th>
              <th class="py-2 px-2">Document<br/>Number</th>
              <th class="py-2 px-2">Date</th>
              <th class="py-2 px-2">PIC</th>
              <th class="py-2 px-2">Vendor<br/>Name</th>
              <th class="py-2 px-2">Description</th>
              <th class="py-2 px-2 text-right">Amount</th>
              <th class="py-2 px-2 text-center">Status</th>
              <th class="py-2 px-2 text-center">Approval</th>
              <th class="py-2 px-2 text-center">Paid Status</th>
              <th class="py-2 px-2">Transaction<br/>Type</th>
              <th class="py-2 px-2">Project<br/>Name</th>
              <th class="py-2 px-2">RAP Name</th>
              <th v-if="filterUsageFor === 'Project Cash Advanced'" class="py-2 px-2 text-center">Declaration<br/>Letter</th>
              <th class="py-2 px-2 text-center">Is<br/>Close</th>
              <th class="py-2 px-2 text-center">Allow<br/>Pre Year</th>
              <th v-if="filterUsageFor === 'Purchase Invoice Payment'" class="py-2 px-2">Invoice</th>
              <th class="py-2 px-2 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr
              v-for="(item, idx) in tableData"
              :key="item.id || idx"
              class="hover:bg-yellow-50/20 transition-colors text-xs text-gray-700"
            >
              <td class="py-3 px-2 text-center">
                <input type="checkbox" class="rounded border-gray-300 text-bfs-gold focus:ring-bfs-gold cursor-pointer" />
              </td>
              <td class="py-3 px-2 text-gray-500">{{ idx + 1 }}.</td>
              <td class="py-3 px-2 font-mono text-gray-600 font-semibold">{{ item.document_number }}</td>
              <td class="py-3 px-2">{{ item.date }}</td>
              <td class="py-3 px-2">{{ item.created_by || 'N/A' }}</td>
              <td class="py-3 px-2">{{ item.payment_to_display || item.vendor_name || '-' }}</td>
              <td class="py-3 px-2 truncate max-w-[150px]" :title="item.description">{{ item.description }}</td>
              <td class="py-3 px-2 text-right font-semibold text-bfs-gold">{{ formatCurrency(item.unpaid_amount || item.amount) }}</td>
              <td class="py-3 px-2 text-center">
                <div class="inline-flex items-center justify-center p-1 rounded-md" :title="'Document Status: ' + item.document_status">
                  <Folder v-if="item.document_status === 'draft'" class="w-4 h-4 text-amber-500 fill-amber-500/10" />
                  <FolderOpen v-else-if="item.document_status === 'ready_to_process'" class="w-4 h-4 text-blue-500 fill-blue-500/10" />
                  <FolderCheck v-else-if="item.document_status === 'close'" class="w-4 h-4 text-green-500 fill-green-500/10" />
                </div>
              </td>
              <td class="py-3 px-2 text-center">
                <button
                  class="inline-flex items-center justify-center p-1 rounded-md hover:bg-gray-100 transition-colors cursor-pointer"
                  :title="'Approval Status: ' + item.approval_status"
                >
                  <FileText v-if="item.approval_status === 'draft'" class="w-4 h-4 text-gray-400" />
                  <FileClock v-else-if="item.approval_status === 'awaiting'" class="w-4 h-4 text-bfs-gold animate-pulse" />
                  <FileCheck v-else-if="item.approval_status === 'approved'" class="w-4 h-4 text-green-500" />
                  <FileX v-else-if="item.approval_status === 'rejected'" class="w-4 h-4 text-red-500" />
                  <FileWarning v-else-if="item.approval_status === 'revised'" class="w-4 h-4 text-orange-500" />
                </button>
              </td>
              <td class="py-3 px-2 text-center">
                <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider"
                  :class="{
                    'bg-amber-100 text-amber-700': item.paid_status === 'not_paid',
                    'bg-blue-100 text-blue-700': item.paid_status === 'half_paid',
                    'bg-green-100 text-green-700': item.paid_status === 'full_paid'
                  }"
                >
                  {{ (item.paid_status || '').replace('_', ' ') }}
                </span>
              </td>
              <td class="py-3 px-2">{{ item.transaction_type_display || '-' }}</td>
              <td class="py-3 px-2">{{ item.project_display || '-' }}</td>
              <td class="py-3 px-2">{{ item.rap_name || '-' }}</td>
              <td v-if="filterUsageFor === 'Project Cash Advanced'" class="py-3 px-2 text-center">
                <span v-if="item.declaration_letter" class="text-green-500 font-bold text-base">✓</span>
                <span v-else class="text-red-500 font-bold text-base">✗</span>
              </td>
              <td class="py-3 px-2 text-center">
                <span v-if="item.is_close" class="text-green-500 font-bold text-base">✓</span>
                <span v-else class="text-red-500 font-bold text-base">✗</span>
              </td>
              <td class="py-3 px-2 text-center">
                <span v-if="item.allow_previous_year_budget" class="text-green-500 font-bold text-base">✓</span>
                <span v-else class="text-red-500 font-bold text-base">✗</span>
              </td>
              <td v-if="filterUsageFor === 'Purchase Invoice Payment'" class="py-3 px-2">{{ item.purchase_invoice_display || item.vendor_invoice_number || '-' }}</td>
              <td class="py-3 px-2 text-right">
                <div class="flex justify-end gap-1.5">
                  <button @click="editData(item)" class="p-1 text-gray-400 hover:text-bfs-gold transition-colors" title="Edit">
                    <Pencil class="w-3.5 h-3.5" />
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="tableData.length === 0">
              <td colspan="19" class="text-center py-10 text-gray-400">
                <FileText class="w-12 h-12 mx-auto mb-3 text-gray-300" />
                <p class="text-sm">No Payment Request found for {{ filterUsageFor }}.</p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- Bulk Actions (Dynamic based on Usage For) -->
    <div class="flex flex-wrap items-center gap-2 mt-4" v-if="tableData.length > 0">
      <button @click="openAddModal" class="px-3 py-1.5 bg-gray-200 hover:bg-gray-300 text-gray-700 text-xs font-semibold rounded transition-colors shadow-sm border border-gray-300 cursor-pointer">
        New Cash Book
      </button>
      <button class="px-3 py-1.5 bg-gray-200 hover:bg-gray-300 text-gray-700 text-xs font-semibold rounded transition-colors shadow-sm border border-gray-300">
        Print This Document
      </button>
      
      <template v-if="filterUsageFor === 'Project Cash Advanced'">
        <button class="px-3 py-1.5 bg-gray-200 hover:bg-gray-300 text-gray-700 text-xs font-semibold rounded transition-colors shadow-sm border border-gray-300">
          Inactive
        </button>
        <button class="px-3 py-1.5 bg-gray-200 hover:bg-gray-300 text-gray-700 text-xs font-semibold rounded transition-colors shadow-sm border border-gray-300">
          Cost Control Check List Attachment
        </button>
        <button class="px-3 py-1.5 bg-gray-200 hover:bg-gray-300 text-gray-700 text-xs font-semibold rounded transition-colors shadow-sm border border-gray-300">
          Use LPJ
        </button>
      </template>

      <button class="px-3 py-1.5 bg-gray-200 hover:bg-gray-300 text-gray-700 text-xs font-semibold rounded transition-colors shadow-sm border border-gray-300">
        Print SLA
      </button>

      <template v-if="filterUsageFor === 'Project Cash Advanced'">
        <button class="px-3 py-1.5 bg-gray-200 hover:bg-gray-300 text-gray-700 text-xs font-semibold rounded transition-colors shadow-sm border border-gray-300">
          Yearly Budget
        </button>
        <button class="px-3 py-1.5 bg-gray-200 hover:bg-gray-300 text-gray-700 text-xs font-semibold rounded transition-colors shadow-sm border border-gray-300">
          Over Budget
        </button>
      </template>

      <button class="px-3 py-1.5 bg-gray-200 hover:bg-gray-300 text-gray-700 text-xs font-semibold rounded transition-colors shadow-sm border border-gray-300">
        Allow Previous year Budget RAP
      </button>
    </div>

    <!-- Add/Edit Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="modal.show" class="fixed inset-0 z-50 overflow-y-auto">
          <div class="fixed inset-0 bg-black/40" @click="closeModal" />
          <div class="flex min-h-full items-start justify-center p-4 py-8">
            <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-4xl z-10" @click.stop>
              
              <!-- Modal Header -->
              <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
                <div>
                  <h3 class="text-base font-bold text-gray-800">
                    {{ modal.mode === 'add' ? 'Finance | Payment Request | Add' : 'Finance | Payment Request | Edit' }}
                  </h3>
                </div>
                <button @click="closeModal" class="text-gray-400 hover:text-gray-600">
                  <X class="w-5 h-5" />
                </button>
              </div>

              <!-- Modal Form Content -->
              <div v-if="filterUsageFor === 'Purchase Invoice Payment'">
                <PurchaseInvoicePaymentForm :form="form" @update:form="form = $event" />
              </div>
              <div v-else class="px-6 py-4 space-y-6">
                <!-- Data is context dependent -->
                <div class="bg-blue-50 text-blue-800 text-xs px-4 py-3 rounded-lg border border-blue-200">
                  Form depends on the selected <strong>Usage For</strong>: {{ filterUsageFor }}
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 bg-gray-50/50 p-4 rounded-xl border border-gray-100">
                  <FormField label="Date" required>
                    <input v-model="form.date" type="date" class="form-input" />
                  </FormField>
                  
                  <FormField label="PIC" required>
                    <input v-model="form.pic" type="text" class="form-input" placeholder="Person in Charge" />
                  </FormField>
                  
                  <FormField label="Vendor Name">
                    <input v-model="form.vendor_name" type="text" class="form-input" placeholder="Vendor Name" />
                  </FormField>
                  
                  <FormField label="Amount" required>
                    <input v-model="form.amount" type="number" step="0.01" class="form-input" placeholder="0.00" />
                  </FormField>
                  
                  <FormField label="Description">
                    <textarea v-model="form.description" class="form-input h-20 resize-none" placeholder="Description..."></textarea>
                  </FormField>
                </div>
              </div>

              <div class="px-6 py-4 border-t border-gray-100 bg-gray-50 rounded-b-2xl flex justify-between items-center">
                <button @click="closeModal" class="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 transition-colors font-semibold">
                  Cancel
                </button>
                <div class="flex gap-2">
                  <button @click="saveData(false)" :disabled="isSaving" class="btn-secondary text-sm px-5 flex items-center gap-2">
                    <Save class="w-4 h-4" /> Save as Draft
                  </button>
                  <button @click="saveData(true)" :disabled="isSaving" class="bg-bfs-navy hover:bg-bfs-navy-dark text-white text-sm font-bold px-6 py-2 rounded-lg transition-colors flex items-center gap-2 cursor-pointer shadow-md shadow-bfs-navy/20">
                    <Send class="w-4 h-4" /> Submit to Approval
                  </button>
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
import { ref, onMounted, reactive, computed } from 'vue'
import Panel from '../../components/Panel.vue'
import FormField from '../../components/FormField.vue'
import PurchaseInvoicePaymentForm from './PurchaseInvoicePaymentForm.vue'
import { Plus, Pencil, Trash2, Save, X, Search, FileText, Folder, FolderOpen, FolderCheck, FileClock, FileCheck, FileX, FileWarning, Send } from 'lucide-vue-next'
import api from '../../services/api'
import Swal from 'sweetalert2'

// Date helpers for current month defaults
const getFirstDayOfMonth = () => {
  const date = new Date()
  const y = date.getFullYear()
  const m = date.getMonth()
  return new Date(y, m, 1).toLocaleDateString('en-CA') // YYYY-MM-DD
}

const getLastDayOfMonth = () => {
  const date = new Date()
  const y = date.getFullYear()
  const m = date.getMonth()
  return new Date(y, m + 1, 0).toLocaleDateString('en-CA') // YYYY-MM-DD
}

// Filter state
const searchQuery = ref('')
const filterDateFrom = ref(getFirstDayOfMonth())
const filterDateTo = ref(getLastDayOfMonth())

// New Main Filters
const filterType = ref('Disbursement')
const filterUsageFor = ref('Purchase Invoice Payment')
const filterDeclaration = ref('') // Only for Project Cash Advanced

const filterDocStatus = ref('')
const filterAppStatus = ref('')

const tableData = ref([])

const fetchTableData = async () => {
  try {
    const res = await api.get('accounting/cashbook-request/')
    tableData.value = res.data.results || res.data
  } catch (err) {
    console.error('Error fetching cashbook requests:', err)
  }
}

const handleSearch = () => {
  // To be implemented with backend integration
  console.log('Search triggered with:', {
    query: searchQuery.value,
    dateFrom: filterDateFrom.value,
    dateTo: filterDateTo.value,
    type: filterType.value,
    usageFor: filterUsageFor.value,
    declaration: filterDeclaration.value,
    docStatus: filterDocStatus.value,
    appStatus: filterAppStatus.value
  })
}

const handleUsageForChange = () => {
  // Reset declaration when usage for changes
  filterDeclaration.value = ''
  handleSearch()
}

const handleResetFilters = () => {
  searchQuery.value = ''
  filterDateFrom.value = getFirstDayOfMonth()
  filterDateTo.value = getLastDayOfMonth()
  filterType.value = 'Disbursement'
  filterUsageFor.value = 'Purchase Invoice Payment'
  filterDeclaration.value = ''
  filterDocStatus.value = ''
  filterAppStatus.value = ''
  handleSearch()
}

const formatCurrency = (value) => {
  if (!value) return '0.00'
  return new Intl.NumberFormat('en-US', { minimumFractionDigits: 2 }).format(value)
}

// Modal State
const modal = reactive({
  show: false,
  mode: 'add'
})

const form = reactive({
  id: null,
  document_number: '',
  date: '',
  pic: '',
  vendor_name: '',
  amount: null,
  description: '',
  // Purchase Invoice Payment specific fields
  transaction_type: null,
  duration_due_date: '',
  invoice_date: '',
  due_date: '',
  currency: 'IDR',
  project: null,
  payment_to: null,
  notes_payment_to: '',
  notes: '',
  requestor_department: null,
  purchase_invoice: null,
  purchase_invoice_display: '',
  vendor_invoice_number: '',
  unpaid_amount: '0.00',
  is_sumbangan: false,
  budget_component: null,
  budget_component_name: ''
})

const openAddModal = () => {
  modal.mode = 'add'
  // Reset form
  form.id = null
  form.document_number = ''
  form.date = new Date().toLocaleDateString('en-CA')
  form.pic = ''
  form.vendor_name = ''
  form.amount = null
  form.description = ''
  
  form.transaction_type = null
  form.duration_due_date = ''
  form.invoice_date = ''
  form.due_date = ''
  form.currency = 'IDR'
  form.project = null
  form.payment_to = null
  form.notes_payment_to = ''
  form.notes = ''
  form.requestor_department = null
  form.purchase_invoice = null
  form.purchase_invoice_display = ''
  form.vendor_invoice_number = ''
  form.unpaid_amount = '0.00'
  form.is_sumbangan = false
  form.budget_component = null
  form.budget_component_name = ''
  
  modal.show = true
}

const editData = (item) => {
  modal.mode = 'edit'
  // Populate form with existing data
  form.id = item.id
  form.document_number = item.document_number
  form.date = item.date
  form.pic = item.pic
  form.vendor_name = item.vendor_name
  form.amount = item.amount
  form.description = item.description
  
  form.transaction_type = item.transaction_type
  form.duration_due_date = item.duration_due_date
  form.invoice_date = item.invoice_date
  form.due_date = item.due_date
  form.currency = item.currency || 'IDR'
  form.project = item.project
  form.payment_to = item.payment_to
  form.notes_payment_to = item.notes_payment_to
  form.notes = item.notes
  form.requestor_department = item.requestor_department
  form.purchase_invoice = item.purchase_invoice
  form.purchase_invoice_display = item.purchase_invoice_display
  form.vendor_invoice_number = item.vendor_invoice_number
  form.unpaid_amount = item.unpaid_amount
  form.is_sumbangan = item.is_sumbangan
  
  // Try to load budget_component from item if available, though CashbookReqHeader might not have it natively.
  // It will be re-fetched by the form component watcher if needed.
  form.budget_component = item.budget_component || null
  form.budget_component_name = item.budget_component_name || ''
  
  modal.show = true
}

const closeModal = () => {
  modal.show = false
}

const isSaving = ref(false)

const saveData = async (isSubmit) => {
  try {
    isSaving.value = true
    const payload = {
      ...form,
      document_status: isSubmit ? 'ready_to_process' : 'draft',
      approval_status: isSubmit ? 'awaiting' : 'draft'
    }
    
    // We only need to submit if we're adding for now
    if (modal.mode === 'add') {
      await api.post('accounting/cashbook-request/', payload)
      Swal.fire({
        icon: 'success',
        title: 'Success!',
        text: `Payment Request successfully ${isSubmit ? 'submitted' : 'saved as draft'}.`,
        confirmButtonColor: '#1d4ed8'
      })
      closeModal()
      fetchTableData()
    } else if (modal.mode === 'edit') {
      await api.put(`accounting/cashbook-request/${form.id}/`, payload)
      Swal.fire({
        icon: 'success',
        title: 'Success!',
        text: `Payment Request successfully ${isSubmit ? 'submitted' : 'updated'}.`,
        confirmButtonColor: '#1d4ed8'
      })
      closeModal()
      fetchTableData()
    }
  } catch (error) {
    console.error('Error saving Payment Request:', error)
    Swal.fire({
      icon: 'error',
      title: 'Oops...',
      text: 'Failed to save Payment Request: ' + (error.response?.data ? JSON.stringify(error.response.data) : error.message),
      confirmButtonColor: '#d33'
    })
  } finally {
    isSaving.value = false
  }
}

onMounted(() => {
  fetchTableData()
})
</script>
