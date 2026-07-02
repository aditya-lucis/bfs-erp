<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 overflow-y-auto">
    <div class="bg-white rounded-2xl shadow-2xl w-full max-w-5xl my-8 flex flex-col max-h-[90vh]">
      <!-- Header -->
      <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between shrink-0">
        <h3 class="text-lg font-semibold text-bfs-dark">
          {{ isEdit ? 'Edit' : 'Create' }} Good Receipt Note
        </h3>
        <button @click="$emit('close')" class="p-2 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100 cursor-not-allowed transition-colors">
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- Body -->
      <div class="p-6 overflow-y-auto flex-1">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 bg-white p-4 rounded-xl border border-gray-200 shadow-sm items-start">
          
          <!-- Left Column -->
          <div class="space-y-4">
            <!-- GRN Number -->
            <div class="form-group" v-if="isEdit">
              <label class="text-xs font-bold text-gray-700 uppercase tracking-wider mb-1 block">Good Receipt Note Number <span class="text-red-500">*</span></label>
              <input type="text" :value="form.grn_number" class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg bg-gray-100 cursor-not-allowed text-gray-700 font-semibold" disabled />
            </div>

            <!-- Acceptance Date -->
            <div class="form-group">
              <label class="text-xs font-bold text-gray-700 uppercase tracking-wider mb-1 block">Acceptance Date <span class="text-red-500">*</span></label>
              <input type="date" v-model="form.acceptance_date" class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-1 focus:ring-bfs-navy focus:border-bfs-navy bg-white text-gray-900 disabled:bg-gray-100 cursor-not-allowed disabled:text-gray-500" required />
            </div>

            <!-- Document Date -->
            <div class="form-group">
              <label class="text-xs font-bold text-gray-700 uppercase tracking-wider mb-1 block">Document Date <span class="text-red-500">*</span></label>
              <input type="date" v-model="form.document_date" class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-1 focus:ring-bfs-navy focus:border-bfs-navy bg-white text-gray-900 disabled:bg-gray-100 cursor-not-allowed disabled:text-gray-500" required />
              <p v-if="!isPeriodOpen" class="text-red-500 text-sm mt-1">{{ periodMessage }}</p>
            </div>

            <!-- Vendor -->
            <div class="form-group">
              <label class="text-xs font-bold text-gray-700 uppercase tracking-wider mb-1 block">Vendor <span class="text-red-500">*</span></label>
              <SearchableSelect
                v-model="form.vendor"
                :options="store.validVendors"
                value-key="id"
                label-key="name"
                placeholder="Select Vendor"
                @change="onVendorChange"
                :disabled="isEdit"
              />
            </div>

            <!-- Purchase Order No -->
            <div class="form-group">
              <label class="text-xs font-bold text-gray-700 uppercase tracking-wider mb-1 block">Purchase Order No <span class="text-red-500">*</span></label>
              <SearchableSelect
                v-model="form.po"
                :options="poOptions"
                value-key="id"
                label-key="label"
                placeholder="Select PO"
                @change="onPOChange"
                :disabled="isEdit || !form.vendor"
              />
            </div>

            <!-- RAP Name -->
            <div class="form-group">
              <label class="text-xs font-bold text-gray-700 uppercase tracking-wider mb-1 block">RAP Name / Activity Code</label>
              <input type="text" class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-1 focus:ring-bfs-navy focus:border-bfs-navy bg-gray-100 text-gray-900 cursor-not-allowed disabled:text-gray-500" :value="selectedRAPName" disabled />
            </div>

            <!-- CC No -->
            <div class="form-group">
              <label class="text-xs font-bold text-gray-700 uppercase tracking-wider mb-1 block">Completion Certificate No <span class="text-red-500">*</span></label>
              <SearchableSelect
                v-model="form.cc"
                :options="ccOptions"
                value-key="id"
                label-key="label"
                placeholder="Select CC"
                @change="onCCChange"
                :disabled="isEdit || !form.po"
              />
            </div>

            <!-- Type -->
            <div class="form-group">
              <label class="text-xs font-bold text-gray-700 uppercase tracking-wider mb-1 block">Type</label>
              <select v-model="form.type" class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-1 focus:ring-bfs-navy focus:border-bfs-navy bg-gray-100 text-gray-900 cursor-not-allowed disabled:text-gray-500" disabled>
                <option value="GRN">GRN</option>
                <option value="SES">SES</option>
              </select>
            </div>
          </div>

          <!-- Right Column -->
          <div class="space-y-4">
            <!-- Description -->
            <div class="form-group">
              <label class="text-xs font-bold text-gray-700 uppercase tracking-wider mb-1 block">Description <span class="text-red-500">*</span></label>
              <textarea v-model="form.description" class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-1 focus:ring-bfs-navy focus:border-bfs-navy bg-white text-gray-900 disabled:bg-gray-100 cursor-not-allowed disabled:text-gray-500 resize-none" rows="4" required></textarea>
            </div>

            <!-- Currency -->
            <div class="form-group">
              <label class="text-xs font-bold text-gray-700 uppercase tracking-wider mb-1 block">Currency</label>
              <input type="text" class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-1 focus:ring-bfs-navy focus:border-bfs-navy bg-gray-100 text-gray-900 cursor-not-allowed disabled:text-gray-500" v-model="form.currency" disabled />
            </div>
          </div>

        </div>

        <hr class="my-6 border-gray-200" />

        <!-- Documents Table -->
        <h4 class="font-semibold text-bfs-dark mb-4">GRN-SES Documents Checklist</h4>
        <div class="table-container mb-6 overflow-x-auto">
          <table class="w-full text-left border-collapse min-w-[800px]">
            <thead>
              <tr class="bg-gray-50 border-b border-t border-gray-200 text-[11px] font-semibold text-gray-600 uppercase tracking-wider">
                <th class="py-3 px-4 w-12 text-center">CHK</th>
                <th class="py-3 px-4">DOCUMENT NAME</th>
                <th class="py-3 px-4 w-32 text-center">ADA/TIDAK</th>
                <th class="py-3 px-4">FILE (MAX 2MB)</th>
                <th class="py-3 px-4">DOCUMENT NUMBER</th>
                <th class="py-3 px-4">KETERANGAN</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loadingDocs" class="border-b border-gray-100">
                <td colspan="6" class="text-center py-4 text-gray-500">Loading documents...</td>
              </tr>
              <tr v-else-if="!displayedDocs.length" class="border-b border-gray-100">
                <td colspan="6" class="text-center py-4 text-gray-500">No active documents found.</td>
              </tr>
              <tr v-else v-for="(doc, idx) in displayedDocs" :key="doc.id" class="border-b border-gray-100 hover:bg-yellow-50/20 text-xs">
                <td class="py-2 px-4 text-center">
                  <input type="checkbox" v-model="doc.checked" class="w-4 h-4 text-bfs-gold border-gray-300 rounded" />
                </td>
                <td class="py-2 px-4 text-sm font-medium text-gray-700">
                  {{ doc.document_name }}
                  <span v-if="doc.type" class="text-xs text-gray-400 font-normal">({{ doc.type }})</span>
                </td>
                <td class="py-2 px-4 text-center">
                  <select v-model="doc.is_available" class="px-2 py-1 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-bfs-navy bg-white" :disabled="!doc.checked">
                    <option :value="true">Ada</option>
                    <option :value="false">Tidak</option>
                  </select>
                </td>
                <td class="py-2 px-4">
                  <div class="flex items-center gap-2">
                    <button 
                      type="button"
                      v-if="doc.is_available && (doc.fileData || doc.fileUrl)" 
                      @click="previewFile(doc)" 
                      class="text-xs text-blue-600 hover:text-blue-800 font-medium whitespace-nowrap cursor-pointer"
                    >
                      Show
                    </button>
                    <div class="flex flex-col gap-1">
                      <input 
                        type="file" 
                        @change="handleFileUpload($event, doc)" 
                        class="text-sm file:mr-2 file:py-1 file:px-2 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-yellow-50 file:text-bfs-gold hover:file:bg-yellow-100 disabled:opacity-50 max-w-[200px]"
                        :disabled="!doc.checked || !doc.is_available"
                      />
                      <p v-if="doc.fileError" class="text-red-500 text-xs">{{ doc.fileError }}</p>
                      <p v-else-if="doc.existingFile" class="text-blue-500 text-xs truncate max-w-[150px]">Current: {{ doc.existingFile }}</p>
                    </div>
                  </div>
                </td>
                <td class="py-2 px-4">
                  <input type="text" v-model="doc.document_number" class="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-bfs-navy bg-white" placeholder="No. Dok" :disabled="!doc.checked" />
                </td>
                <td class="py-2 px-4">
                  <input type="text" v-model="doc.keterangan" class="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-bfs-navy bg-white" placeholder="Ket..." :disabled="!doc.checked" />
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Termin / Amount Calculation -->
        <h4 class="font-semibold text-bfs-dark mb-4">Payment Calculation</h4>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 p-4 bg-gray-50 rounded-lg">
          <div class="space-y-4">
            <div class="flex justify-between border-b pb-2">
              <span class="text-sm font-medium text-gray-600">PO Amount:</span>
              <span class="font-semibold">{{ formatCurrency(selectedPOObj?.total_amount) }}</span>
            </div>
            <div class="flex justify-between border-b pb-2">
              <span class="text-sm font-medium text-gray-600">Discount:</span>
              <span class="font-semibold text-red-500">-{{ formatCurrency(selectedPOObj?.total_discount) }}</span>
            </div>
            <div class="flex justify-between border-b pb-2">
              <span class="text-sm font-medium text-gray-600">PPN {{ selectedPOObj?.ppn ? '(Inclusive)' : '' }}:</span>
              <span class="font-semibold">{{ formatCurrency(selectedPOObj?.total_tax) }}</span>
            </div>
            <div class="flex justify-between border-b pb-2">
              <span class="text-sm font-bold text-gray-800">Net PO Amount:</span>
              <span class="font-bold text-bfs-dark">{{ formatCurrency(selectedPOObj?.grand_total) }}</span>
            </div>
            <div class="flex justify-between pb-2 bg-yellow-50 p-2 rounded border border-yellow-100">
              <span class="text-sm font-bold text-gray-800">Total Invoice yg Sudah Diinput:</span>
              <span class="font-bold text-bfs-gold">{{ formatCurrency(totalInvoiced) }}</span>
            </div>
          </div>

          <div class="space-y-4 border-l pl-6 border-gray-200">
            <div class="form-group">
              <label class="text-xs font-bold text-gray-700 uppercase tracking-wider mb-1 block">Term Purchase Order</label>
              <input type="text" class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg bg-gray-100 cursor-not-allowed text-gray-700 font-semibold" :value="selectedTermDesc" disabled />
            </div>
            <div class="flex justify-between items-center border-t pt-4">
              <span class="text-sm font-bold text-gray-800">Term Percentage:</span>
              <span class="font-bold text-blue-600 text-lg">{{ form.term_percentage || 0 }} %</span>
            </div>
            <div class="flex justify-between items-center bg-blue-50 p-3 rounded border border-blue-100">
              <span class="text-sm font-bold text-bfs-dark">GRN / SES AMOUNT:</span>
              <span class="font-bold text-xl text-bfs-gold">{{ formatCurrency(form.amount) }}</span>
            </div>
          </div>
        </div>

      </div>

      <!-- Footer -->
      <div class="px-6 py-4 bg-gray-50 border-t border-gray-100 flex items-center justify-end gap-3 sticky bottom-0 rounded-b-2xl shadow-[0_-4px_10px_-4px_rgba(0,0,0,0.05)]">
        <button 
          @click="emit('close')"
          class="px-5 py-2 text-sm font-semibold text-gray-600 hover:text-gray-900 bg-white border border-gray-200 hover:bg-gray-50 rounded-xl transition-colors shadow-sm"
        >
          Cancel
        </button>
        <div class="flex gap-2">
          <button
            v-if="(!isEdit && canCreate) || (isEdit && canUpdate && ['draft', 'revised'].includes(form.approval_status))"
            @click="submitForm(true)" 
            class="px-6 py-2 text-sm font-bold text-bfs-navy border border-bfs-navy hover:bg-gray-50 rounded-xl shadow-sm transition-all flex items-center justify-center gap-2"
            :disabled="isSubmitting || !isFormValid"
          >
            <Loader2 v-if="isSubmitting" class="w-4 h-4 animate-spin" />
            <Save v-else class="w-4 h-4" />
            <span>Save Document</span>
          </button>
          <button
            v-if="isEdit && ['draft', 'revised'].includes(form.approval_status) && canUpdate"
            @click="submitForm(false)" 
            class="px-6 py-2 text-sm font-bold text-white bg-bfs-navy hover:bg-bfs-navy-dark rounded-xl shadow-md transition-all flex items-center justify-center gap-2"
            :disabled="isSubmitting || !isFormValid"
          >
            <Loader2 v-if="isSubmitting" class="w-4 h-4 animate-spin" />
            <Send v-else class="w-4 h-4" />
            <span>Submit to Approval</span>
          </button>
        </div>
      </div></div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { X, Loader2, Save, Send } from 'lucide-vue-next'
import Swal from 'sweetalert2'
import { useGoodReceiptNoteStore } from '../../stores/goodReceiptNote'
import { useGrnSesDocumentStore } from '../../stores/grnSesDocument'
import { usePeriodCheck } from '../../composables/usePeriodCheck'
import { usePermission } from '../../composables/usePermission'
import api from '../../services/api.js'
import SearchableSelect from '../../components/SearchableSelect.vue'

const props = defineProps({
  isOpen: Boolean,
  editData: Object
})

const emit = defineEmits(['close'])

const store = useGoodReceiptNoteStore()
const grnStore = useGrnSesDocumentStore()
const { checkPeriod, isPeriodOpen, periodMessage } = usePeriodCheck()
const { canCreate, canUpdate } = usePermission('PURCHASES-GOOD-RECEIPT-NOTE')

const isSubmitting = ref(false)
const loadingDocs = ref(false)
const activeDocs = ref([])

const initialFormState = {
  vendor: '',
  po: '',
  cc: '',
  type: 'GRN',
  document_date: '',
  acceptance_date: new Date().toISOString().split('T')[0],
  currency: 'IDR',
  description: '',
  payment_term: '',
  amount: 0,
  term_percentage: 0,
  approval_status: 'draft',
}

const form = ref({ ...initialFormState, document_date: new Date().toISOString().split('T')[0] })

const displayedDocs = computed(() => {
  if (form.value.type === 'GRN') {
    return activeDocs.value.filter(d => d.type === 'GRN')
  } else if (form.value.type === 'SES') {
    return activeDocs.value.filter(d => d.type === 'SES')
  }
  return activeDocs.value
})

const isEdit = computed(() => !!props.editData)

// Computed for PO details
const selectedPOObj = computed(() => {
  if (!form.value.po) return null
  return store.validPOs.find(p => p.id === form.value.po)
})
const poOptions = computed(() => {
  return store.validPOs.map(po => ({
    id: po.id,
    label: `${po.po_number} - ${po.project?.site_name || ''}`
  }))
})

// CC Options
const ccOptions = computed(() => {
  return store.validCCs.map(cc => ({
    id: cc.id,
    label: `${cc.cc_number}`
  }))
})
const selectedCCObj = computed(() => {
  if (!form.value.cc) return null
  return store.validCCs.find(c => c.id === form.value.cc)
})

const selectedPOTerms = computed(() => {
  return selectedPOObj.value?.payment_terms || []
})
const selectedTermObj = computed(() => {
  if (!form.value.payment_term) return null
  return selectedPOTerms.value.find(t => t.id === form.value.payment_term)
})
const selectedTermDesc = computed(() => {
  if (!selectedTermObj.value) return '-'
  return `${selectedTermObj.value.term_desc} (${selectedTermObj.value.duration_due_percent}%)`
})

const selectedRAPName = computed(() => {
  return selectedPOObj.value?.rap_number || '-'
})

const totalInvoiced = computed(() => {
  // Try to find if backend provides it in PO
  return selectedPOObj.value?.total_invoiced || 0
})

const isFormValid = computed(() => {
  const hasCheckedDocs = displayedDocs.value.some(d => d.checked)
  const hasFileErrors = displayedDocs.value.some(d => d.checked && d.fileError)
  return form.value.vendor && form.value.po && form.value.cc && form.value.payment_term && 
         form.value.document_date && form.value.acceptance_date && form.value.description && isPeriodOpen.value && hasCheckedDocs && !hasFileErrors
})

watch(() => form.value.document_date, async (newVal) => {
  if (newVal) {
    await checkPeriod(newVal)
  }
})

watch(() => props.isOpen, async (newVal) => {
  if (newVal) {
    loadingDocs.value = true
    await store.fetchValidVendors()
    await store.fetchValidPOs(0) // clear
    await grnStore.fetchDocuments()
    
    // Prepare base documents
    activeDocs.value = grnStore.documents
      .filter(d => d.is_active)
      .map(d => ({
        ...d,
        master_document: d.id,
        checked: false,
        is_available: true,
        fileData: null,
        existingFile: null,
        fileUrl: null,
        fileError: '',
        document_number: '',
        keterangan: ''
      }))
    loadingDocs.value = false

    if (isEdit.value) {
      const data = props.editData
      await store.fetchValidPOs(data.vendor)
      if (!store.validPOs.find(p => p.id === data.po)) {
        try {
          const res = await api.get('/purchase/po/' + data.po + '/')
          store.validPOs.push(res.data)
        } catch (e) {}
      }
      await store.fetchValidCCs(data.po)
      if (!store.validCCs.find(c => c.id === data.cc)) {
        try {
          const res = await api.get('/purchase/completion-certificates/' + data.cc + '/')
          store.validCCs.push(res.data)
        } catch (e) {}
      }
      
      const matchingCC = store.validCCs.find(c => c.id === data.cc)
      const ccPaymentTerm = matchingCC ? matchingCC.payment_term : data.payment_term

      form.value = {
        grn_number: data.grn_number,
        vendor: data.vendor,
        po: data.po,
        cc: data.cc,
        type: data.type,
        document_date: data.document_date,
        acceptance_date: data.acceptance_date,
        currency: data.currency || 'IDR',
        description: data.description || '',
        payment_term: ccPaymentTerm,
        amount: data.amount,
        term_percentage: data.term_percentage || 0,
        approval_status: data.approval_status || 'draft',
      }

      if (form.value.document_date) {
        await checkPeriod(form.value.document_date)
      }

      // Pre-fill checked docs from GRN saved docs
      if (data.documents && data.documents.length) {
        data.documents.forEach(savedDoc => {
          const match = activeDocs.value.find(d => d.id === savedDoc.master_document)
          if (match) {
            match.checked = true
            match.is_available = savedDoc.is_available
            match.document_number = savedDoc.document_number || ''
            match.keterangan = savedDoc.keterangan || ''
            match.existingFile = savedDoc.file ? savedDoc.file.split('/').pop() : null
            match.fileUrl = savedDoc.file || null
          }
        })
      }
      
      // Fallback to CC file if GRN file is missing
      if (data.cc) {
        try {
          const res = await api.get('/purchase/completion-certificates/' + data.cc + '/')
          const ccData = res.data
          if (ccData.documents && ccData.documents.length) {
            ccData.documents.forEach(ccDoc => {
              const match = activeDocs.value.find(d => d.id === ccDoc.master_document)
              if (match && match.checked && !match.fileUrl && ccDoc.file) {
                match.existingFile = ccDoc.file.split('/').pop()
                match.fileUrl = ccDoc.file
              }
            })
          }
        } catch (e) {
          console.error('Failed to fetch fallback CC docs', e)
        }
      }
    } else {
      form.value = { ...initialFormState, document_date: new Date().toISOString().split('T')[0] }
      await checkPeriod(form.value.document_date)
    }
  } else {
    activeDocs.value = []
    store.validPOs = []
    store.validCCs = []
  }
})

async function onVendorChange() {
  form.value.po = ''
  form.value.cc = ''
  form.value.payment_term = ''
  form.value.amount = 0
  form.value.term_percentage = 0
  if (form.value.vendor) {
    await store.fetchValidPOs(form.value.vendor)
  } else {
    store.validPOs = []
    store.validCCs = []
  }
}

async function onPOChange() {
  form.value.cc = ''
  form.value.payment_term = ''
  form.value.amount = 0
  form.value.term_percentage = 0
  if (selectedPOObj.value) {
    form.value.currency = selectedPOObj.value.po_currency || 'IDR'
    await store.fetchValidCCs(form.value.po)
  } else {
    store.validCCs = []
  }
}

async function onCCChange() {
  // Clear docs check
  activeDocs.value.forEach(d => {
    d.checked = false
    d.is_available = true
    d.fileData = null
    d.existingFile = null
    d.fileUrl = null
    d.document_number = ''
    d.keterangan = ''
  })
  
  if (selectedCCObj.value) {
    const cc = selectedCCObj.value
    // CC BAST -> GRN SES, CC GRN -> GRN GRN
    form.value.type = (cc.type === 'BAST') ? 'SES' : 'GRN'
    
    // Copy amount, term, percentage
    form.value.amount = cc.amount
    form.value.payment_term = cc.payment_term
    const pTerm = selectedPOTerms.value.find(t => t.id === cc.payment_term)
    form.value.term_percentage = pTerm ? pTerm.duration_due_percent : 0
    
    // Copy description
    form.value.description = cc.description || ''

    // Fetch CC documents and prefill activeDocs
    try {
      const res = await api.get('/purchase/completion-certificates/' + cc.id + '/')
      const ccData = res.data
      if (ccData.documents && ccData.documents.length) {
        ccData.documents.forEach(ccDoc => {
          const match = activeDocs.value.find(d => d.id === ccDoc.master_document)
          if (match) {
            match.checked = true
            match.is_available = ccDoc.is_available
            match.document_number = ccDoc.document_number || ''
            match.keterangan = ccDoc.keterangan || ''
            match.existingFile = ccDoc.file ? ccDoc.file.split('/').pop() : null
            match.fileUrl = ccDoc.file || null
          }
        })
      }
    } catch (e) {
      console.error('Failed to fetch CC docs', e)
    }
  }
}

function previewFile(doc) {
  if (doc.fileData) {
    const url = URL.createObjectURL(doc.fileData)
    window.open(url, '_blank')
  } else if (doc.fileUrl) {
    window.open(doc.fileUrl, '_blank')
  }
}

function handleFileUpload(event, doc) {
  const file = event.target.files[0]
  doc.fileError = ''
  if (!file) {
    doc.fileData = null
    return
  }
  if (file.size > 2 * 1024 * 1024) {
    doc.fileError = 'File size exceeds 2MB limit.'
    event.target.value = ''
    doc.fileData = null
    return
  }
  doc.fileData = file
}

function formatCurrency(val) {
  if (!val) return '0.00'
  return Number(val).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

async function submitForm(isDraft = true) {
  if (!isFormValid.value) return

  isSubmitting.value = true

  try {
    const payload = { ...form.value, documents: [] }
    const selectedDocs = displayedDocs.value.filter(d => d.checked)
    
    for (const doc of selectedDocs) {
      payload.documents.push({
        master_document: doc.master_document,
        is_available: doc.is_available,
        document_number: doc.document_number,
        keterangan: doc.keterangan,
        ...(doc.fileData && { file: doc.fileData }) // append File object directly if modified
      })
    }

    if (isEdit.value) {
      await store.updateGRN(props.editData.id, payload)
    } else {
      await store.createGRN(payload)
    }

    if (store.error) {
      throw new Error(typeof store.error === 'string' ? store.error : JSON.stringify(store.error))
    }

    if (!isDraft) {
      if (!isEdit.value) {
        throw new Error('Silakan Simpan Dokumen terlebih dahulu (Save Document) sebelum Submit ke Approval untuk dokumen baru.')
      }
      await store.submitGRN(props.editData.id)
    }

    Swal.fire({
      icon: 'success',
      title: 'Berhasil',
      text: isDraft ? 'Good Receipt Note berhasil disimpan!' : 'Good Receipt Note berhasil diajukan untuk persetujuan!',
      confirmButtonColor: '#002E5D'
    })
    emit('close')
  } catch (err) {
    console.error(err)
    const errorMsg = store.error 
      ? (typeof store.error === 'string' ? store.error : JSON.stringify(store.error))
      : (err.response?.data?.detail || err.message || 'Terjadi kesalahan sistem.')
      
    Swal.fire({
      icon: 'error',
      title: 'Gagal Menyimpan',
      text: errorMsg,
      confirmButtonColor: '#002E5D'
    })
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
@reference "../../style.css";
.form-group {
  @apply flex flex-col gap-1;
}
.form-label {
  @apply text-sm font-semibold text-gray-700;
}
</style>
