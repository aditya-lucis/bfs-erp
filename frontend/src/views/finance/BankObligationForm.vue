
<template>
  <div class="p-4 bg-slate-50 min-h-screen">
    <!-- Header Title -->
    <div class="flex items-center gap-2 text-xs text-slate-500 font-medium mb-4 uppercase tracking-wider">
      <Banknote class="w-4 h-4 text-bfs-navy" />
      <span>Finance</span>
      <ChevronRight class="w-3 h-3" />
      <span>Bank Obligation</span>
      <ChevronRight class="w-3 h-3" />
      <span class="text-slate-800">{{ isEdit ? 'Edit' : 'Add' }}</span>
    </div>

    <div class="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden mb-6">
      <div class="bg-bfs-navy/5 border-b border-slate-200 px-5 py-3 flex items-center justify-between">
        <h2 class="font-bold text-slate-800 flex items-center gap-2">
          <Banknote class="w-5 h-5 text-bfs-navy" />
          Bank Obligation Header
        </h2>
      </div>
      
      <div class="p-6">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <!-- Left Column -->
          <div class="space-y-4">
            <div class="grid grid-cols-3 items-center gap-2">
              <label class="text-sm font-medium text-slate-700">Loan No</label>
              <div class="col-span-2">
                <input v-model="form.loan_no" type="text" class="w-full bg-white border border-slate-300 text-slate-700 text-sm rounded-lg focus:ring-2 focus:ring-bfs-navy/20 focus:border-bfs-navy block p-2 transition-all" placeholder="Enter loan no" />
              </div>
            </div>

            <div class="grid grid-cols-3 items-center gap-2">
              <label class="text-sm font-medium text-slate-700">Transaction Date</label>
              <div class="col-span-2 relative">
                <input v-model="form.transaction_date" type="date" class="w-full bg-white border border-slate-300 text-slate-700 text-sm rounded-lg focus:ring-2 focus:ring-bfs-navy/20 focus:border-bfs-navy block p-2 transition-all" />
              </div>
            </div>

            <div class="grid grid-cols-3 items-center gap-2">
              <label class="text-sm font-medium text-slate-700">Contract Number</label>
              <div class="col-span-2">
                <input v-model="form.contract_number" type="text" class="w-full bg-white border border-slate-300 text-slate-700 text-sm rounded-lg focus:ring-2 focus:ring-bfs-navy/20 focus:border-bfs-navy block p-2 transition-all" placeholder="Enter contract no" />
              </div>
            </div>

            <div class="grid grid-cols-3 items-center gap-2">
              <label class="text-sm font-medium text-slate-700">Bank Name</label>
              <div class="col-span-2">
                <SearchSelect 
                  v-model="form.bank"
                  :options="masterBankOpts"
                  placeholder="Select bank..."
                  class="w-full"
                />
              </div>
            </div>

            <div class="grid grid-cols-3 items-center gap-2">
              <label class="text-sm font-medium text-slate-700">Due Date</label>
              <div class="col-span-2">
                <input v-model="calculatedDueDate" type="date" readonly class="w-full bg-slate-100 border border-slate-300 text-slate-600 text-sm rounded-lg focus:ring-0 block p-2 cursor-not-allowed" />
              </div>
            </div>

            <div class="grid grid-cols-3 items-center gap-2">
              <label class="text-sm font-medium text-slate-700">Plafond</label>
              <div class="col-span-2 relative">
                <input v-model.number="form.plafond" type="number" step="0.01" class="w-full bg-white border border-slate-300 text-slate-700 text-sm rounded-lg focus:ring-2 focus:ring-bfs-navy/20 focus:border-bfs-navy block p-2 transition-all text-right font-mono" placeholder="0.00" />
              </div>
            </div>

            <div class="grid grid-cols-3 items-center gap-2">
              <label class="text-sm font-medium text-slate-700">Jangka Waktu (Bulan)</label>
              <div class="col-span-2">
                <input v-model.number="form.jangka_waktu" type="number" class="w-full bg-white border border-slate-300 text-slate-700 text-sm rounded-lg focus:ring-2 focus:ring-bfs-navy/20 focus:border-bfs-navy block p-2 transition-all text-right" placeholder="0" />
              </div>
            </div>

            <div class="grid grid-cols-3 items-center gap-2">
              <label class="text-sm font-medium text-slate-700">Bunga / Margin (%)</label>
              <div class="col-span-2">
                <input v-model.number="form.bunga_margin" type="number" step="0.01" class="w-full bg-white border border-slate-300 text-slate-700 text-sm rounded-lg focus:ring-2 focus:ring-bfs-navy/20 focus:border-bfs-navy block p-2 transition-all text-right" placeholder="0.00" />
              </div>
            </div>

            <div class="grid grid-cols-3 items-center gap-2">
              <label class="text-sm font-medium text-slate-700">Angsuran Pokok</label>
              <div class="col-span-2 relative">
                <input :value="formatNumber(calculatedAngsuranPokok)" type="text" readonly class="w-full bg-slate-100 border border-slate-300 text-slate-600 text-sm rounded-lg block p-2 text-right font-mono cursor-not-allowed" />
              </div>
            </div>

            <div class="grid grid-cols-3 items-center gap-2">
              <label class="text-sm font-medium text-slate-700">Loan Type</label>
              <div class="col-span-2">
                <select v-model="form.loan_type" class="w-full bg-white border border-slate-300 text-slate-700 text-sm rounded-lg focus:ring-2 focus:ring-bfs-navy/20 focus:border-bfs-navy block p-2 transition-all cursor-pointer">
                  <option v-for="opt in loanTypeOpts" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
                </select>
              </div>
            </div>
          </div>

          <!-- Right Column -->
          <div class="space-y-4">
            <h3 class="text-sm font-bold text-slate-700 mb-2 pb-2 border-b border-slate-100">Additional Settings</h3>
            
            <div class="grid grid-cols-3 items-center gap-2">
              <label class="text-sm font-medium text-slate-700">Account Pokok</label>
              <div class="col-span-2">
                <SearchSelect 
                  v-model="form.account_pokok"
                  :options="coaOpts"
                  placeholder="Select Account Pokok..."
                  class="w-full"
                />
              </div>
            </div>

            <div class="grid grid-cols-3 items-center gap-2">
              <label class="text-sm font-medium text-slate-700">Account Bunga</label>
              <div class="col-span-2">
                <SearchSelect 
                  v-model="form.account_bunga"
                  :options="coaOpts"
                  placeholder="Select Account Bunga..."
                  class="w-full"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Detail Section -->
    <div v-if="details.length > 0" class="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden mb-6 transition-all duration-500">
      <div class="bg-slate-50 border-b border-slate-200 px-5 py-3 flex items-center justify-between">
        <h2 class="font-bold text-slate-800 flex items-center gap-2">
          <ListIcon class="w-4 h-4 text-slate-500" />
          Input Detail
        </h2>
      </div>
      
      <div class="overflow-x-auto">
        <table class="w-full text-sm text-left">
          <thead class="bg-slate-100 text-slate-600 font-semibold text-xs tracking-wider border-b border-slate-200">
            <tr>
              <th class="px-4 py-3 text-center w-12">No</th>
              <th class="px-4 py-3">Bulan</th>
              <th class="px-4 py-3">Tanggal Pencairan</th>
              <th class="px-4 py-3 text-right">Sisa Pokok</th>
              <th class="px-4 py-3 text-right">Pokok</th>
              <th class="px-4 py-3 text-right">Margin</th>
              <th class="px-4 py-3 text-right">Diskon Margin</th>
              <th class="px-4 py-3 text-right">Total Angsuran</th>
              <th class="px-4 py-3 text-center">CBR Pokok</th>
              <th class="px-4 py-3 text-center">CBR Bunga</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="(row, idx) in details" :key="idx" class="hover:bg-slate-50 transition-colors">
              <td class="px-4 py-2 text-center text-slate-500 font-medium">{{ row.no }}</td>
              <td class="px-4 py-2">
                <input v-model="row.bulan" type="date" class="w-full bg-white border border-slate-300 text-slate-700 text-xs rounded focus:ring-1 focus:ring-bfs-navy/20 p-1.5" />
              </td>
              <td class="px-4 py-2">
                <input v-model="row.tanggal_pencairan" type="date" class="w-full bg-white border border-slate-300 text-slate-700 text-xs rounded focus:ring-1 focus:ring-bfs-navy/20 p-1.5" />
              </td>
              <td class="px-4 py-2 text-right font-mono text-slate-700">
                {{ formatNumber(row.sisa_pokok) }}
              </td>
              <td class="px-4 py-2 text-right font-mono text-slate-700">
                {{ formatNumber(row.pokok) }}
              </td>
              <td class="px-4 py-2 text-right font-mono text-slate-700">
                {{ formatNumber(row.margin) }}
              </td>
              <td class="px-4 py-2">
                <input v-model.number="row.diskon_margin" @input="recalcRow(idx)" type="number" step="0.01" class="w-full bg-white border border-slate-300 text-slate-700 text-xs rounded focus:ring-1 focus:ring-bfs-navy/20 p-1.5 text-right font-mono" />
              </td>
              <td class="px-4 py-2 text-right font-mono font-medium text-slate-700 bg-slate-50">
                {{ formatNumber(row.total_angsuran) }}
              </td>
              <td class="px-4 py-2 text-center">
                <div v-if="row.is_cbr_pokok" class="w-5 h-5 mx-auto rounded-full bg-emerald-50 flex items-center justify-center"><Check class="w-3 h-3 text-emerald-500" /></div>
                <div v-else class="w-5 h-5 mx-auto rounded-full bg-rose-50 flex items-center justify-center"><X class="w-3 h-3 text-rose-500" /></div>
              </td>
              <td class="px-4 py-2 text-center">
                <div v-if="row.is_cbr_bunga" class="w-5 h-5 mx-auto rounded-full bg-emerald-50 flex items-center justify-center"><Check class="w-3 h-3 text-emerald-500" /></div>
                <div v-else class="w-5 h-5 mx-auto rounded-full bg-rose-50 flex items-center justify-center"><X class="w-3 h-3 text-rose-500" /></div>
              </td>
            </tr>
          </tbody>
          <tfoot class="bg-slate-50 font-bold text-slate-700 text-sm">
            <tr>
              <td colspan="4" class="px-4 py-3 text-right uppercase tracking-wider text-xs">Total</td>
              <td class="px-4 py-3 text-right font-mono">{{ formatNumber(totalPokok) }}</td>
              <td class="px-4 py-3 text-right font-mono">{{ formatNumber(totalMargin) }}</td>
              <td class="px-4 py-3 text-right font-mono">{{ formatNumber(totalDiskonMargin) }}</td>
              <td class="px-4 py-3 text-right font-mono">{{ formatNumber(totalAll) }}</td>
              <td colspan="2"></td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>

    <!-- Actions -->
    <div class="flex items-center gap-3">
      <button v-if="canSave" @click="save" :disabled="loading" class="flex items-center gap-2 px-6 py-2.5 bg-bfs-navy text-white text-sm font-semibold rounded-lg hover:bg-bfs-navy/90 focus:ring-4 focus:ring-bfs-navy/30 transition-all shadow-sm active:scale-95 disabled:opacity-50">
        <Save class="w-4 h-4" />
        {{ loading ? 'Saving...' : 'Save' }}
      </button>
      <button @click="router.push('/finance/bank-obligation')" class="flex items-center gap-2 px-6 py-2.5 bg-white text-slate-700 border border-slate-300 text-sm font-semibold rounded-lg hover:bg-slate-50 focus:ring-4 focus:ring-slate-100 transition-all shadow-sm active:scale-95">
        <X class="w-4 h-4" />
        Cancel
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { usePermission } from '../../composables/usePermission'
import { Banknote, ChevronRight, Save, X, List as ListIcon, Check } from 'lucide-vue-next'
import SearchSelect from '../../components/SearchableSelect.vue'
import Swal from 'sweetalert2'
import api from '../../services/api'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const { canCreate, canUpdate } = usePermission('FINANCE-BANK-OBLIGATION')

const isEdit = computed(() => !!route.params.id)
const canSave = computed(() => isEdit.value ? canUpdate.value : canCreate.value)
const loading = ref(false)

const getTodayDate = () => {
  return new Date().toLocaleDateString('en-CA')
}

const form = ref({
  company: authStore.activeCompanyId,
  loan_no: '',
  transaction_date: getTodayDate(),
  contract_number: '',
  bank: null,
  account_pokok: null,
  account_bunga: null,
  plafond: 0,
  jangka_waktu: 0,
  bunga_margin: 0,
  loan_type: 'NON_SINDIKASI'
})

const details = ref([])

const masterBankOpts = ref([])
const coaOpts = ref([])

const loanTypeOpts = [
  { value: 'NON_SINDIKASI', label: 'Non Sindikasi' },
  { value: 'SINDIKASI', label: 'Sindikasi' },
  { value: 'TRANCHE_1', label: 'Tranche 1' },
  { value: 'TRANCHE_2', label: 'Tranche 2' },
  { value: 'TRANCHE_3', label: 'Tranche 3' },
  { value: 'KREDIT_INVESTASI', label: 'Kredit Investasi' },
  { value: 'KREDIT_MODAL_KERJA', label: 'Kredit Modal Kerja' },
  { value: 'KREDIT_REKENING_KORAN', label: 'Kredit Rekening Koran' },
  { value: 'BACK_TO_BACK', label: 'Back To Back' },
  { value: 'CAPITAL_LEASE', label: 'Capital Lease' },
  { value: 'OPERATING_LEASE', label: 'Operating Lease' }
]

// Computed calculations
const calculatedDueDate = computed(() => {
  if (!form.value.transaction_date || !form.value.jangka_waktu) return ''
  const d = new Date(form.value.transaction_date)
  d.setMonth(d.getMonth() + parseInt(form.value.jangka_waktu))
  return d.toLocaleDateString('en-CA')
})

const calculatedAngsuranPokok = computed(() => {
  if (!form.value.plafond || !form.value.jangka_waktu) return 0
  return form.value.plafond / form.value.jangka_waktu
})

// Auto-generate details watcher
watch([() => form.value.plafond, () => form.value.jangka_waktu, () => form.value.bunga_margin], () => {
  // Only auto-generate if we are not editing (or if explicitly triggered)
  if (isEdit.value && details.value.length > 0) {
    // If editing and details exist, we shouldn't wipe them randomly, 
    // but if the user clears and re-enters, we might. For now, let's just generate if empty.
    if (details.value.length === parseInt(form.value.jangka_waktu)) return
  }

  const p = parseFloat(form.value.plafond) || 0
  const jw = parseInt(form.value.jangka_waktu) || 0
  const bunga = parseFloat(form.value.bunga_margin) || 0

  if (p > 0 && jw > 0) {
    const angsuranPokok = Math.round((p / jw) * 100) / 100
    const angsuranBunga = Math.round((p * (bunga / 100 / 12)) * 100) / 100
    
    let currentSisa = p
    let totalPokokDihitung = 0
    const newDetails = []
    
    for (let i = 1; i <= jw; i++) {
      let d = new Date(form.value.transaction_date || getTodayDate())
      d.setMonth(d.getMonth() + i)
      const bulanStr = d.toLocaleDateString('en-CA')
      
      // Bulan terakhir menampung sisa rounding
      let pokokBulanIni = (i === jw) ? (Math.round((p - totalPokokDihitung) * 100) / 100) : angsuranPokok
      
      newDetails.push({
        no: i,
        bulan: bulanStr,
        tanggal_pencairan: form.value.transaction_date || getTodayDate(),
        sisa_pokok: currentSisa,
        pokok: pokokBulanIni,
        margin: angsuranBunga,
        diskon_margin: 0,
        total_angsuran: Math.round((pokokBulanIni + angsuranBunga) * 100) / 100,
        is_cbr_pokok: false,
        is_cbr_bunga: false
      })
      currentSisa = Math.round((currentSisa - pokokBulanIni) * 100) / 100
      totalPokokDihitung += pokokBulanIni
    }
    details.value = newDetails
  } else {
    details.value = []
  }
}, { deep: true })

const recalcRow = (idx) => {
  const row = details.value[idx]
  row.total_angsuran = (parseFloat(row.pokok) || 0) + (parseFloat(row.margin) || 0) - (parseFloat(row.diskon_margin) || 0)
}

// Totals
const totalPokok = computed(() => details.value.reduce((sum, r) => sum + (parseFloat(r.pokok) || 0), 0))
const totalMargin = computed(() => details.value.reduce((sum, r) => sum + (parseFloat(r.margin) || 0), 0))
const totalDiskonMargin = computed(() => details.value.reduce((sum, r) => sum + (parseFloat(r.diskon_margin) || 0), 0))
const totalAll = computed(() => details.value.reduce((sum, r) => sum + (parseFloat(r.total_angsuran) || 0), 0))

// Initial load
onMounted(async () => {
  await fetchMasterData()
  if (isEdit.value) {
    await loadData()
  }
})

const fetchMasterData = async () => {
  try {
    const [bankRes, coaRes] = await Promise.all([
      api.get('master-type/master-bank/'),
      api.get(`accounting/coa/?company_id=${authStore.activeCompanyId}&postable=true`)
    ])
    
    const bankData = bankRes.data.results || bankRes.data || []
    masterBankOpts.value = bankData.map(b => ({
      id: b.id, label: b.bank_name
    }))
    
    const coaData = coaRes.data.results || coaRes.data || []
    coaOpts.value = coaData.map(c => ({
      id: c.id, label: `${c.account_number} - ${c.account_name}`
    }))
  } catch (err) {
    console.error(err)
  }
}

const loadData = async () => {
  try {
    loading.value = true
    const res = await api.get(`accounting/bank-obligation/${route.params.id}/`)
    const data = res.data
    form.value = {
      company: data.company,
      loan_no: data.loan_no,
      transaction_date: data.transaction_date,
      contract_number: data.contract_number,
      bank: data.bank,
      account_pokok: data.account_pokok,
      account_bunga: data.account_bunga,
      plafond: data.plafond,
      jangka_waktu: data.jangka_waktu,
      bunga_margin: data.bunga_margin,
      loan_type: data.loan_type
    }
    details.value = data.details || []
  } catch (err) {
    Swal.fire('Error', 'Gagal memuat data', 'error')
  } finally {
    loading.value = false
  }
}

const save = async () => {
  try {
    if (!form.value.loan_no || !form.value.bank || !form.value.account_pokok || !form.value.account_bunga || !form.value.plafond || !form.value.jangka_waktu) {
      Swal.fire('Error', 'Mohon lengkapi semua data wajib!', 'error')
      return
    }

    loading.value = true
    const payload = {
      ...form.value,
      due_date: calculatedDueDate.value,
      details: details.value
    }
    
    if (isEdit.value) {
      await api.put(`accounting/bank-obligation/${route.params.id}/`, payload)
      Swal.fire({ icon: 'success', title: 'Success', text: 'Bank Obligation updated successfully', timer: 1500, showConfirmButton: false })
    } else {
      await api.post('accounting/bank-obligation/', payload)
      Swal.fire({ icon: 'success', title: 'Success', text: 'Bank Obligation created successfully', timer: 1500, showConfirmButton: false })
    }
    router.push('/finance/bank-obligation')
  } catch (err) {
    console.error(err)
    Swal.fire('Error', 'Gagal menyimpan data', 'error')
  } finally {
    loading.value = false
  }
}

const formatNumber = (val) => {
  if (!val) return '0.00'
  return new Intl.NumberFormat('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(val)
}
</script>
