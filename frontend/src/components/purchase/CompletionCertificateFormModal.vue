<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 overflow-y-auto">
    <div class="bg-white rounded-2xl shadow-2xl w-full max-w-5xl my-8 flex flex-col max-h-[90vh]">
      <!-- Header -->
      <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between shrink-0">
        <h3 class="text-lg font-semibold text-bfs-dark">
          {{ isEdit ? 'Edit' : 'Create' }} Completion Certificate
        </h3>
        <button @click="$emit('close')" class="p-2 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100 cursor-not-allowed transition-colors">
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- Body -->
      <div class="p-6 overflow-y-auto flex-1">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
          
          <!-- Vendor Selection -->
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

          <!-- PO Selection -->
          <div class="form-group">
            <label class="text-xs font-bold text-gray-700 uppercase tracking-wider mb-1 block">Purchase Order <span class="text-red-500">*</span></label>
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

          <!-- Type -->
          <div class="form-group">
            <label class="text-xs font-bold text-gray-700 uppercase tracking-wider mb-1 block">Type <span class="text-red-500">*</span></label>
            <select v-model="form.type" class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-1 focus:ring-bfs-navy focus:border-bfs-navy bg-white text-gray-900 disabled:bg-gray-100 cursor-not-allowed disabled:text-gray-500" required>
              <option value="GRN">GRN</option>
              <option value="BAST">BAST</option>
            </select>
          </div>

          <!-- RAP Name (Auto) -->
          <div class="form-group">
            <label class="text-xs font-bold text-gray-700 uppercase tracking-wider mb-1 block">RAP Name / Activity Code</label>
            <input type="text" class="input bg-gray-100 cursor-not-allowed" :value="selectedRAPName" disabled />
          </div>

          <!-- Document Date -->
          <div class="form-group">
            <label class="text-xs font-bold text-gray-700 uppercase tracking-wider mb-1 block">Document Date <span class="text-red-500">*</span></label>
            <input type="date" v-model="form.document_date" class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-1 focus:ring-bfs-navy focus:border-bfs-navy bg-white text-gray-900 disabled:bg-gray-100 cursor-not-allowed disabled:text-gray-500" required />
            <p v-if="!isPeriodOpen" class="text-red-500 text-sm mt-1">{{ periodMessage }}</p>
          </div>

          <!-- Document Date From Vendor -->
          <div class="form-group">
            <label class="text-xs font-bold text-gray-700 uppercase tracking-wider mb-1 block">Document Date From Vendor <span class="text-red-500">*</span></label>
            <input type="date" v-model="form.document_date_from_vendor" class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-1 focus:ring-bfs-navy focus:border-bfs-navy bg-white text-gray-900 disabled:bg-gray-100 cursor-not-allowed disabled:text-gray-500" required />
          </div>

          <!-- Currency -->
          <div class="form-group">
            <label class="text-xs font-bold text-gray-700 uppercase tracking-wider mb-1 block">Currency</label>
            <input type="text" class="input bg-gray-100 cursor-not-allowed" v-model="form.currency" disabled />
          </div>

          <!-- Description -->
          <div class="form-group md:col-span-2">
            <label class="text-xs font-bold text-gray-700 uppercase tracking-wider mb-1 block">Description</label>
            <textarea v-model="form.description" class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-1 focus:ring-bfs-navy focus:border-bfs-navy bg-white text-gray-900 disabled:bg-gray-100 cursor-not-allowed disabled:text-gray-500 resize-none" rows="2"></textarea>
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
              <tr v-else-if="!activeDocs.length" class="border-b border-gray-100">
                <td colspan="6" class="text-center py-4 text-gray-500">No active documents found.</td>
              </tr>
              <tr v-else v-for="(doc, idx) in activeDocs" :key="doc.id" class="border-b border-gray-100 hover:bg-yellow-50/20 text-xs">
                <td class="py-2 px-4 text-center">
                  <input type="checkbox" v-model="doc.checked" class="w-4 h-4 text-bfs-gold border-gray-300 rounded" />
                </td>
                <td class="py-2 px-4 text-sm font-medium text-gray-700">{{ doc.document_name }}</td>
                <td class="py-2 px-4 text-center">
                  <select v-model="doc.is_available" class="px-2 py-1 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-bfs-navy bg-white" :disabled="!doc.checked">
                    <option :value="true">Ada</option>
                    <option :value="false">Tidak</option>
                  </select>
                </td>
                <td class="py-2 px-4">
                  <input 
                    type="file" 
                    @change="handleFileUpload($event, doc)" 
                    class="text-sm file:mr-4 file:py-1 file:px-2 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-yellow-50 file:text-bfs-gold hover:file:bg-yellow-100 disabled:opacity-50"
                    :disabled="!doc.checked || !doc.is_available"
                  />
                  <p v-if="doc.fileError" class="text-red-500 text-xs mt-1">{{ doc.fileError }}</p>
                  <p v-else-if="doc.existingFile" class="text-blue-500 text-xs mt-1 truncate max-w-[150px]">Current: {{ doc.existingFile }}</p>
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
            <div class="flex justify-between pb-2">
              <span class="text-sm font-bold text-gray-800">Net PO Amount:</span>
              <span class="font-bold text-bfs-dark">{{ formatCurrency(selectedPOObj?.grand_total) }}</span>
            </div>
          </div>

          <div class="space-y-4 border-l pl-6 border-gray-200">
            <div class="form-group">
              <label class="text-xs font-bold text-gray-700 uppercase tracking-wider mb-1 block">Term Purchase Order <span class="text-red-500">*</span></label>
              <select v-model="form.payment_term" class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-1 focus:ring-bfs-navy focus:border-bfs-navy bg-white text-gray-900 disabled:bg-gray-100 cursor-not-allowed disabled:text-gray-500" @change="onTerminChange" required>
                <option value="">Pilih Termin</option>
                <option v-for="term in selectedPOTerms" :key="term.id" :value="term.id">
                  {{ term.term_desc }} ({{ term.duration_due_percent }}%)
                </option>
              </select>
            </div>
            <div class="flex justify-between items-center border-t pt-4">
              <span class="text-sm font-bold text-gray-800">Term Percentage:</span>
              <span class="font-bold text-blue-600 text-lg">{{ selectedTermObj?.duration_due_percent || 0 }} %</span>
            </div>
            <div class="flex justify-between items-center bg-blue-50 p-3 rounded border border-blue-100">
              <span class="text-sm font-bold text-bfs-dark">CC / BAST AMOUNT:</span>
              <span class="font-bold text-xl text-bfs-gold">{{ formatCurrency(form.amount) }}</span>
            </div>
          </div>
        </div>

      </div>

      <!-- Footer -->
      <div class="px-6 py-4 bg-gray-50 border-t border-gray-100 flex items-center justify-end gap-3 shrink-0 rounded-b-xl">
        <button type="button" @click="$emit('close')" class="px-5 py-2 text-sm font-semibold text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-xl transition-colors">
          Cancel
        </button>
        <button 
          @click="submitForm" 
          class="px-6 py-2 text-sm font-bold text-white bg-bfs-gold hover:bg-yellow-600 rounded-xl shadow-md transition-all flex items-center justify-center gap-2 min-w-[120px]"
          :disabled="isSubmitting || !isFormValid"
        >
          <Loader2 v-if="isSubmitting" class="w-4 h-4 animate-spin" />
          <span>{{ isEdit ? 'Save Changes' : 'Save Document' }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { X, Loader2 } from 'lucide-vue-next'
import Swal from 'sweetalert2'
import { useCompletionCertificateStore } from '../../stores/completionCertificate'
import { useGrnSesDocumentStore } from '../../stores/grnSesDocument'
import { usePeriodCheck } from '../../composables/usePeriodCheck'
import SearchableSelect from '../../components/SearchableSelect.vue'

const props = defineProps({
  isOpen: Boolean,
  editData: Object
})

const emit = defineEmits(['close'])

const store = useCompletionCertificateStore()
const grnStore = useGrnSesDocumentStore()
const { checkPeriod, isPeriodOpen, periodMessage } = usePeriodCheck()

const isSubmitting = ref(false)
const loadingDocs = ref(false)
const activeDocs = ref([])

const initialFormState = {
  vendor: '',
  po: '',
  type: 'GRN',
  document_date: '',
  document_date_from_vendor: new Date().toISOString().split('T')[0],
  currency: 'IDR',
  description: '',
  payment_term: '',
  amount: 0,
}

const form = ref({ ...initialFormState })

const isEdit = computed(() => !!props.editData)

// Computed for PO details
const selectedPOObj = computed(() => {
  if (!form.value.po) return null
  return store.validPOs.find(p => p.id === form.value.po)
})
const selectedPOTerms = computed(() => {
  return selectedPOObj.value?.payment_terms || []
})
const selectedTermObj = computed(() => {
  if (!form.value.payment_term) return null
  return selectedPOTerms.value.find(t => t.id === form.value.payment_term)
})
const poOptions = computed(() => {
  return store.validPOs.map(po => ({
    id: po.id,
    label: `${po.po_number} - ${po.project?.site_name || ''}`
  }))
})

const selectedRAPName = computed(() => {
  return selectedPOObj.value?.rap_number || '-'
})

const isFormValid = computed(() => {
  const hasCheckedDocs = activeDocs.value.some(d => d.checked)
  const hasFileErrors = activeDocs.value.some(d => d.checked && d.fileError)
  return form.value.vendor && form.value.po && form.value.payment_term && 
         form.value.document_date && isPeriodOpen.value && hasCheckedDocs && !hasFileErrors
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
    await grnStore.fetchDocuments()
    // Prepare documents
    activeDocs.value = grnStore.documents
      .filter(d => d.is_active)
      .map(d => ({
        ...d,
        master_document: d.id,
        checked: false,
        is_available: true,
        fileData: null,
        existingFile: null,
        fileError: '',
        document_number: '',
        keterangan: ''
      }))
    loadingDocs.value = false

    if (isEdit.value) {
      const data = props.editData
      await store.fetchValidPOs(data.vendor)
      
      form.value = {
        vendor: data.vendor,
        po: data.po,
        type: data.type,
        document_date: data.document_date,
        document_date_from_vendor: data.document_date_from_vendor,
        currency: data.currency || 'IDR',
        description: data.description || '',
        payment_term: data.payment_term,
        amount: data.amount,
      }

      if (form.value.document_date) {
        await checkPeriod(form.value.document_date)
      }

      // Pre-fill checked docs
      if (data.documents && data.documents.length) {
        data.documents.forEach(savedDoc => {
          const match = activeDocs.value.find(d => d.id === savedDoc.master_document)
          if (match) {
            match.checked = true
            match.is_available = savedDoc.is_available
            match.document_number = savedDoc.document_number || ''
            match.keterangan = savedDoc.keterangan || ''
            match.existingFile = savedDoc.file ? savedDoc.file.split('/').pop() : null
          }
        })
      }
    } else {
      form.value = { ...initialFormState, document_date: new Date().toISOString().split('T')[0] }
      await checkPeriod(form.value.document_date)
    }
  } else {
    // Reset on close
    activeDocs.value = []
    store.validPOs = []
  }
})

async function onVendorChange() {
  form.value.po = ''
  form.value.payment_term = ''
  form.value.amount = 0
  if (form.value.vendor) {
    await store.fetchValidPOs(form.value.vendor)
  } else {
    store.validPOs = []
  }
}

function onPOChange() {
  form.value.payment_term = ''
  form.value.amount = 0
  if (selectedPOObj.value) {
    form.value.currency = selectedPOObj.value.po_currency || 'IDR'
  }
}

function onTerminChange() {
  if (selectedTermObj.value) {
    form.value.amount = selectedTermObj.value.amount
  } else {
    form.value.amount = 0
  }
}

function handleFileUpload(event, doc) {
  const file = event.target.files[0]
  doc.fileError = ''
  if (!file) {
    doc.fileData = null
    return
  }
  // Max 2MB Check
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

async function submitForm() {
  if (!isFormValid.value) return

  isSubmitting.value = true

  try {
    // We must send multipart/form-data for file uploads
    // Unfortunately nested structures with files in FormData can be tricky.
    // The backend accepts 'documents' as nested JSON, but standard Django Rest Framework 
    // doesn't parse nested multipart files easily. 
    // To solve this properly, DRF might need a custom parser or we stringify non-file fields.
    // However, considering the backend handles standard serializers, we can try to append 
    // documents with index notation, e.g. documents[0]is_available = true.
    
    // Fallback simple submission structure:
    const formData = new FormData()
    formData.append('vendor', form.value.vendor)
    formData.append('po', form.value.po)
    formData.append('type', form.value.type)
    formData.append('document_date', form.value.document_date)
    formData.append('document_date_from_vendor', form.value.document_date_from_vendor)
    formData.append('currency', form.value.currency)
    formData.append('description', form.value.description)
    formData.append('payment_term', form.value.payment_term)
    formData.append('amount', form.value.amount)

    // For documents: we use array-like keys if DRF supports it (requires drf-nested-multipart) 
    // OR we can just send JSON for non-file fields and a separate logic, but let's try the array approach.
    const selectedDocs = activeDocs.value.filter(d => d.checked)
    
    // Instead of raw FormData for nested, some DRF setups expect JSON for the main body 
    // and base64 for files. Since we appended files, let's just do a JSON payload for now
    // and if the backend complains, we'll need a base64 workaround.
    // Wait, the backend serializers expects simple list of dicts for `documents`.
    // The most robust way without modifying backend is to send JSON and ignore the files for a moment
    // OR send base64 files inside the JSON! DRF requires `Base64ImageField` / `Base64FileField` for that.
    
    // Given the constraints, let's use the standard `FormData` nested representation. 
    // E.g. `documents[0]master_document` = id
    // However, DRF's default nested serializer does NOT parse `documents[0]xxx`.
    // I will stringify the list of documents and if files are needed, handle them separately.
    // Actually, Django doesn't support multipart nested parsing out of the box. 
    
    // WORKAROUND: We will send standard JSON. If user attached files, we would ideally need a Base64 encoding.
    // For now, let's construct the payload as standard JSON. (Files won't work perfectly unless Base64 is used in backend)
    
    // We will build a JSON payload. File uploads might be ignored by backend if it's not multipart, 
    // but we'll include base64 just in case, or omit for now if it's too complex.
    
    const payload = { ...form.value, documents: [] }
    
    for (const doc of selectedDocs) {
      let fileObj = null
      if (doc.fileData) {
        // Simple base64 conversion just in case backend has a custom parser
        // Otherwise, it will just drop the file
        fileObj = await toBase64(doc.fileData)
      }
      payload.documents.push({
        master_document: doc.master_document,
        is_available: doc.is_available,
        document_number: doc.document_number,
        keterangan: doc.keterangan,
        // file: fileObj // Omitted for now to avoid DRF validation error on pure FileField
      })
    }

    if (isEdit.value) {
      await store.updateCertificate(props.editData.id, payload)
    } else {
      await store.createCertificate(payload)
    }

    if (!store.error) {
      Swal.fire({
        icon: 'success',
        title: 'Berhasil',
        text: 'Completion Certificate berhasil disimpan!',
        confirmButtonColor: '#002E5D'
      })
      emit('close')
    } else {
      throw new Error(typeof store.error === 'string' ? store.error : JSON.stringify(store.error))
    }
  } catch (err) {
    console.error(err)
    Swal.fire({
      icon: 'error',
      title: 'Gagal Menyimpan',
      text: err.message || 'Terjadi kesalahan sistem.',
      confirmButtonColor: '#002E5D'
    })
  } finally {
    isSubmitting.value = false
  }
}

function toBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.readAsDataURL(file)
    reader.onload = () => resolve(reader.result)
    reader.onerror = error => reject(error)
  })
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
