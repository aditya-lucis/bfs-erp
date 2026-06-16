<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../../services/api'
import SearchableSelect from '../../components/SearchableSelect.vue'
import { useAuthStore } from '../../stores/auth'
import Swal from 'sweetalert2'

import {
  Save, Plus, Trash2, ArrowLeft, Send, Loader2, AlertCircle
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const isEdit = computed(() => !!route.params.id)
const isSubmitting = ref(false)
const error = ref(null)

const canCreate = computed(() => authStore.hasPermission('GL-GENERAL-JOURNAL-TRANSACTION_CREATE'))
const canUpdate = computed(() => authStore.hasPermission('GL-GENERAL-JOURNAL-TRANSACTION_UPDATE'))

const form = ref({
  date: new Date().toISOString().substring(0, 10),
  memo: '',
  project: null,
  vendor: null,
  tax_rectification: '',
  has_tax_rectification: false,
  is_adjustment_pph: false,
  status: 'DRAFT',
  transaction_number: '',
  details: []
})

const options = ref({
  projects: [],
  accounts: [],
  vendors: []
})

const cbr_number = ref('')

// Currency Rates
const exchangeRates = ref({
  USD: null,
  EUR: null,
  SGD: null
})
const loadingRates = ref(false)

const fetchExchangeRates = async () => {
  loadingRates.value = true
  try {
    // Fetch rates base IDR
    const res = await fetch('https://open.er-api.com/v6/latest/USD')
    if (res.ok) {
      const data = await res.json()
      const rates = data.rates
      // Base is USD. We need to convert from X to IDR.
      // 1 USD = rates.IDR
      // 1 EUR = rates.IDR / rates.EUR
      const idr = rates.IDR
      exchangeRates.value = {
        USD: idr,
        EUR: idr / rates.EUR,
        SGD: idr / rates.SGD
      }
    }
  } catch (err) {
    console.error('Failed to fetch exchange rates', err)
  } finally {
    loadingRates.value = false
  }
}

const formatRate = (val) => {
  if (!val) return 'Loading...'
  return 'IDR ' + Number(val).toLocaleString('id-ID', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const fetchOptions = async () => {
  try {
    const [projectsRes, accountsRes, vendorsRes] = await Promise.all([
      api.get('/projects/projects/', { params: { is_active: true } }),
      api.get('/accounting/coa/', { params: { postable: true, limit: 1000 } }),
      api.get('/purchase/vendors/')
    ])
    options.value.projects = projectsRes.data.results || projectsRes.data
    const accountsData = accountsRes.data.results || accountsRes.data
    options.value.accounts = accountsData.map(a => ({
      ...a,
      display_name: `${a.account_number} - ${a.account_name}`
    }))
    options.value.vendors = vendorsRes.data.results || vendorsRes.data
  } catch (err) {
    console.error('Failed to fetch options', err)
  }
}

const fetchTransaction = async () => {
  if (!isEdit.value) return
  try {
    const { data } = await api.get(`/accounting/general-journals/${route.params.id}/`)
    form.value = {
      date: data.date,
      memo: data.memo,
      project: data.project,
      vendor: data.vendor,
      tax_rectification: data.tax_rectification || '',
      has_tax_rectification: !!data.tax_rectification,
      is_adjustment_pph: data.is_adjustment_pph,
      status: data.status,
      transaction_number: data.transaction_number,
      details: data.details.map(d => ({
        ...d,
        debit: Number(d.debit),
        credit: Number(d.credit)
      }))
    }
  } catch (err) {
    console.error('Failed to fetch transaction', err)
  }
}

onMounted(async () => {
  fetchExchangeRates()
  await fetchOptions()
  await fetchTransaction()
  if (!isEdit.value && form.value.details.length === 0) {
    addDetailRow()
  }
})

const addDetailRow = () => {
  form.value.details.push({
    account: null,
    currency: 'IDR',
    debit: 0,
    credit: 0,
    period_from: null,
    period_to: null
  })
}

const removeDetailRow = (index) => {
  form.value.details.splice(index, 1)
}

const totalDebit = computed(() => {
  return form.value.details.reduce((sum, item) => sum + (Number(item.debit) || 0), 0)
})

const totalCredit = computed(() => {
  return form.value.details.reduce((sum, item) => sum + (Number(item.credit) || 0), 0)
})

const isBalanced = computed(() => {
  return totalDebit.value === totalCredit.value && totalDebit.value > 0
})

const canEdit = computed(() => {
  const isDraftOrRejected = form.value.status === 'DRAFT' || form.value.status === 'REJECTED' || form.value.status === 'CANCELLED'
  if (isEdit.value) {
    return canUpdate.value && isDraftOrRejected
  } else {
    return canCreate.value
  }
})

const save = async () => {
  if (!isBalanced.value) {
    error.value = 'Debit and Credit must be balanced and greater than zero.'
    window.scrollTo(0, 0)
    return
  }
  isSubmitting.value = true
  error.value = null
  try {
    const payload = { ...form.value }
    if (!payload.has_tax_rectification) {
      payload.tax_rectification = ''
    }
    if (isEdit.value) {
      await api.put(`/accounting/general-journals/${route.params.id}/`, payload)
    } else {
      await api.post('/accounting/general-journals/', payload)
    }
    router.push('/gl/general-journal-transaction')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to save transaction.'
    window.scrollTo(0, 0)
  } finally {
    isSubmitting.value = false
  }
}

const submitApproval = async () => {
  // Save first
  await save()
  if (error.value) return // Don't submit if save failed
  if (!isEdit.value) return // Redirected to list already
  
  const result = await Swal.fire({
    title: 'Are you sure?',
    text: 'Submit this transaction for approval?',
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#1e3a8a',
    cancelButtonColor: '#d33',
    confirmButtonText: 'Yes, submit it!'
  })
  
  if (result.isConfirmed) {
    try {
      await api.post(`/accounting/general-journals/${route.params.id}/submit_approval/`)
      router.push('/gl/general-journal-transaction')
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to submit for approval.'
      window.scrollTo(0, 0)
    }
  }
}

</script>

<template>
  <div class="min-h-full bg-slate-50 flex flex-col pt-4 px-4 pb-12">
    <!-- Main Wrapper Card -->
    <div class="max-w-7xl mx-auto w-full bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden flex flex-col">
      
      <!-- Top Nav Header -->
      <div class="shrink-0 px-6 py-4 flex items-center justify-between border-b border-gray-100">
        <div class="flex items-center gap-4">
          <button
            @click="router.push('/gl/general-journal-transaction')"
            class="text-gray-400 hover:text-gray-600 transition-colors cursor-pointer"
          >
            <ArrowLeft class="w-5 h-5" />
          </button>
          <h1 class="text-[19px] font-extrabold text-bfs-navy tracking-tight flex items-center gap-2">
            {{ isEdit ? 'Edit General Journal Entry' : 'New General Journal Entry' }}
            <span v-if="isEdit" class="ml-2 px-2 py-0.5 text-[10px] font-bold uppercase rounded-md bg-gray-100 text-gray-500 tracking-wider">
              {{ form.status }}
            </span>
          </h1>
        </div>
        <div class="flex items-center gap-3">
          <button
            v-if="canEdit"
            @click="save"
            :disabled="isSubmitting"
            class="btn-secondary text-[13px] flex items-center gap-2 px-4 py-2 border border-gray-200 shadow-sm font-semibold rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
          >
            <Loader2 v-if="isSubmitting" class="w-4 h-4 animate-spin" />
            <Save v-else class="w-4 h-4" />
            Save
          </button>
          <button
            v-if="isEdit && form.status === 'DRAFT'"
            @click="submitApproval"
            :disabled="isSubmitting || !isBalanced"
            class="btn-primary text-[13px] flex items-center gap-2 px-5 py-2 shadow-sm font-semibold rounded-lg bg-bfs-navy text-white hover:bg-bfs-navy-dark transition-colors"
          >
            <Send class="w-4 h-4" /> Confirm
          </button>
        </div>
      </div>

      <!-- Error Alert -->
      <div v-if="error" class="px-6 pt-4">
        <div class="flex items-center gap-3 p-4 bg-red-50 text-red-700 rounded-xl border border-red-100 shadow-sm">
          <AlertCircle class="w-5 h-5 shrink-0 text-red-500" />
          <p class="text-sm font-medium">{{ error }}</p>
        </div>
      </div>

      <!-- Content Area -->
      <div class="p-8 space-y-10">
        
        <!-- Header Info Form (No internal borders, matching screenshot) -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-12">
          <!-- Left Column -->
          <div class="space-y-6">
            <div class="grid grid-cols-[140px_1fr] items-center gap-4">
              <label class="text-[11px] font-extrabold text-slate-700 uppercase tracking-wider">Date <span class="text-red-500">*</span></label>
              <div>
                <input type="date" v-model="form.date" :disabled="!canEdit" class="w-full px-4 py-2.5 bg-white border border-gray-200 rounded-xl text-[13px] font-medium text-slate-700 focus:ring-2 focus:ring-bfs-gold/30 focus:border-bfs-gold transition-colors" />
              </div>
            </div>
            
            <div class="grid grid-cols-[140px_1fr] items-start gap-4">
              <label class="text-[11px] font-extrabold text-slate-700 uppercase tracking-wider mt-3">Memo <span class="text-red-500">*</span></label>
              <div>
                <textarea v-model="form.memo" rows="3" :disabled="!canEdit" class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-[13px] font-medium text-slate-700 focus:ring-2 focus:ring-bfs-gold/30 focus:border-bfs-gold transition-colors resize-none placeholder-gray-400 shadow-sm" placeholder="Enter journal description..."></textarea>
              </div>
            </div>
            
            <div class="grid grid-cols-[140px_1fr] items-center gap-4">
              <label class="text-[11px] font-extrabold text-slate-700 uppercase tracking-wider">Project</label>
              <div>
                <SearchableSelect
                  v-model="form.project"
                  :options="options.projects"
                  labelKey="project_name"
                  valueKey="id"
                  placeholder="None"
                  :clearable="true"
                  :disabled="!canEdit"
                />
              </div>
            </div>
          </div>
          
          <!-- Right Column -->
          <div class="space-y-6">
            <div class="grid grid-cols-[160px_1fr] items-center gap-4">
              <label class="text-[11px] font-extrabold text-slate-700 uppercase tracking-wider">Taxrectification</label>
              <div class="flex items-center gap-3">
                <input type="checkbox" v-model="form.has_tax_rectification" @change="form.has_tax_rectification && !form.tax_rectification ? form.tax_rectification = 'LB' : null" :disabled="!canEdit" class="w-4 h-4 rounded border-gray-300 text-bfs-navy focus:ring-bfs-navy cursor-pointer transition-colors" />
                <select v-if="form.has_tax_rectification" v-model="form.tax_rectification" :disabled="!canEdit" class="px-3 py-1.5 bg-white border border-gray-200 rounded-lg text-[13px] text-slate-700 font-medium focus:ring-2 focus:ring-bfs-gold/30 focus:border-bfs-gold transition-colors">
                  <option value="LB">LB</option>
                  <option value="KB">KB</option>
                </select>
              </div>
            </div>
            
            <div class="grid grid-cols-[160px_1fr] items-center gap-4">
              <label class="text-[11px] font-extrabold text-slate-700 uppercase tracking-wider">Is Adjustment Pph</label>
              <div class="flex items-center gap-2">
                <input type="checkbox" v-model="form.is_adjustment_pph" :disabled="!canEdit" class="w-4 h-4 rounded border-gray-300 text-bfs-navy focus:ring-bfs-navy cursor-pointer" />
                <span class="text-[13px] font-medium text-slate-700">Yes</span>
              </div>
            </div>
            
            <div class="grid grid-cols-[160px_1fr] items-center gap-4">
              <label class="text-[11px] font-extrabold text-slate-700 uppercase tracking-wider">Vendor</label>
              <div>
                <SearchableSelect
                  v-model="form.vendor"
                  :options="options.vendors"
                  labelKey="name"
                  valueKey="id"
                  placeholder="None"
                  :clearable="true"
                  :disabled="!canEdit"
                />
              </div>
            </div>
            
            <div class="grid grid-cols-[160px_1fr] items-center gap-4">
              <label class="text-[11px] font-extrabold text-slate-700 uppercase tracking-wider">Cbr Number</label>
              <div>
                 <input type="text" v-model="cbr_number" disabled placeholder="None" class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-[13px] cursor-not-allowed text-gray-400 font-medium shadow-sm" />
              </div>
            </div>
            
            <!-- Live Currency Converter Box (Matching Screenshot) -->
            <div class="mt-4 p-5 border border-blue-100 rounded-2xl bg-[#f8fbff] relative overflow-hidden shadow-sm">
              <div class="absolute top-0 left-0 w-1.5 h-full bg-blue-500 rounded-l-2xl"></div>
              <div class="flex items-center justify-between mb-4">
                <p class="text-[11px] font-extrabold text-bfs-navy uppercase tracking-widest">Live Currency Rates</p>
                <Loader2 v-if="loadingRates" class="w-3.5 h-3.5 animate-spin text-blue-500" />
              </div>
              <div class="grid grid-cols-2 gap-x-4 gap-y-3 text-[12px] font-semibold">
                <div class="flex justify-between items-center bg-white px-3 py-2 rounded-xl border border-blue-50 shadow-sm">
                  <span class="text-bfs-navy font-bold">1 EUR</span> 
                  <span class="font-mono text-gray-500">{{ formatRate(exchangeRates.EUR) }}</span>
                </div>
                <div class="flex justify-between items-center bg-white px-3 py-2 rounded-xl border border-blue-50 shadow-sm">
                  <span class="text-bfs-navy font-bold">1 SGD</span> 
                  <span class="font-mono text-gray-500">{{ formatRate(exchangeRates.SGD) }}</span>
                </div>
                <div class="flex justify-between items-center bg-white px-3 py-2 rounded-xl border border-blue-50 shadow-sm">
                  <span class="text-bfs-navy font-bold">1 USD</span> 
                  <span class="font-mono text-gray-500">{{ formatRate(exchangeRates.USD) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Details Grid (Matching Screenshot) -->
        <div class="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
          <div class="px-6 py-5 bg-white border-b border-gray-100 flex justify-between items-center">
            <button 
              v-if="canEdit"
              @click="addDetailRow"
              class="text-[11px] font-extrabold text-bfs-navy hover:text-bfs-navy-dark flex items-center gap-2 uppercase tracking-wider transition-colors cursor-pointer"
            >
              <Plus class="w-4 h-4" /> Add Account
            </button>
            <span v-else class="text-[11px] font-extrabold text-gray-500 uppercase tracking-wider flex items-center gap-2">
              Account Details
            </span>
          </div>
          
          <div class="overflow-x-auto">
            <table class="w-full text-left border-collapse">
              <thead>
                <tr class="bg-gray-50/50 border-b border-gray-100 text-[10px] font-extrabold text-slate-500 uppercase tracking-widest">
                  <th class="px-6 py-4 min-w-[280px]">Account</th>
                  <th class="px-6 py-4 w-32">Currency</th>
                  <th class="px-6 py-4 w-44 text-right">Debit</th>
                  <th class="px-6 py-4 w-44 text-right">Credit</th>
                  <th class="px-6 py-4 w-40">Period From</th>
                  <th class="px-6 py-4 w-40">Period To</th>
                  <th class="px-6 py-4 w-20 text-center">Delete</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-50">
                <tr v-for="(row, idx) in form.details" :key="idx" class="hover:bg-slate-50/50 transition-colors group">
                  <td class="px-6 py-3">
                    <SearchableSelect
                      v-model="row.account"
                      :options="options.accounts"
                      labelKey="display_name"
                      valueKey="id"
                      placeholder="Select account"
                      :disabled="!canEdit"
                    />
                  </td>
                  <td class="px-6 py-3">
                    <select v-model="row.currency" :disabled="!canEdit" class="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg text-[13px] font-medium text-slate-700 focus:ring-2 focus:ring-bfs-gold/30 focus:border-bfs-gold transition-colors">
                      <option value="IDR">IDR</option>
                      <option value="USD">USD</option>
                      <option value="EUR">EUR</option>
                      <option value="SGD">SGD</option>
                    </select>
                  </td>
                  <td class="px-6 py-3">
                    <input type="number" v-model.number="row.debit" :disabled="!canEdit" class="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg text-[13px] text-right font-mono text-slate-700 focus:ring-2 focus:ring-bfs-gold/30 focus:border-bfs-gold transition-colors" min="0" step="any" placeholder="0" />
                  </td>
                  <td class="px-6 py-3">
                    <input type="number" v-model.number="row.credit" :disabled="!canEdit" class="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg text-[13px] text-right font-mono text-slate-700 focus:ring-2 focus:ring-bfs-gold/30 focus:border-bfs-gold transition-colors" min="0" step="any" placeholder="0" />
                  </td>
                  <td class="px-6 py-3">
                    <input type="date" v-model="row.period_from" :disabled="!canEdit" class="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg text-[13px] font-medium text-slate-600 focus:ring-2 focus:ring-bfs-gold/30 focus:border-bfs-gold transition-colors" />
                  </td>
                  <td class="px-6 py-3">
                    <input type="date" v-model="row.period_to" :disabled="!canEdit" class="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg text-[13px] font-medium text-slate-600 focus:ring-2 focus:ring-bfs-gold/30 focus:border-bfs-gold transition-colors" />
                  </td>
                  <td class="px-6 py-3 text-center">
                    <button v-if="canEdit" @click="removeDetailRow(idx)" class="text-red-400 hover:text-red-600 hover:bg-red-50 p-2 rounded-lg transition-all opacity-0 group-hover:opacity-100 cursor-pointer" title="Delete Row">
                      <Trash2 class="w-4 h-4" />
                    </button>
                  </td>
                </tr>
                <tr v-if="form.details.length === 0">
                  <td colspan="7" class="px-6 py-10 text-center text-[13px] font-medium text-gray-400 italic">No account entries added yet.</td>
                </tr>
              </tbody>
              <tfoot>
                <tr class="bg-gray-50/50 border-t border-gray-200">
                  <td colspan="2" class="px-6 py-5 text-right text-[11px] font-extrabold uppercase tracking-widest text-slate-700">
                    Total Debit / Credit :
                  </td>
                  <td class="px-6 py-5 text-right">
                    <div class="font-mono text-[14px] font-extrabold" :class="totalDebit === totalCredit && totalDebit > 0 ? 'text-green-600' : (totalDebit > 0 ? 'text-red-500' : 'text-slate-800')">
                      {{ Number(totalDebit).toLocaleString('id-ID', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
                    </div>
                  </td>
                  <td class="px-6 py-5 text-right">
                    <div class="font-mono text-[14px] font-extrabold" :class="totalDebit === totalCredit && totalCredit > 0 ? 'text-green-600' : (totalCredit > 0 ? 'text-red-500' : 'text-slate-800')">
                      {{ Number(totalCredit).toLocaleString('id-ID', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
                    </div>
                  </td>
                  <td colspan="3" class="px-6 py-5">
                    <div v-if="totalDebit > 0 && totalDebit === totalCredit" class="inline-flex items-center gap-1.5 px-2.5 py-1 bg-green-50 text-green-700 text-[10px] font-bold uppercase rounded-md tracking-wider border border-green-200">
                      Balanced ✓
                    </div>
                    <div v-else-if="totalDebit > 0 || totalCredit > 0" class="inline-flex items-center gap-1.5 px-2.5 py-1 bg-red-50 text-red-700 text-[10px] font-bold uppercase rounded-md tracking-wider border border-red-200">
                      Unbalanced ⚠
                    </div>
                  </td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>
        
      </div>
    </div>
  </div>
</template>
