<template>
  <div class="px-6 py-4 space-y-6">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 bg-gray-50/50 p-4 rounded-xl border border-gray-100">
      <!-- Left Column -->
      <div class="space-y-4">
        <FormField label="Document Number">
          <input :value="form.document_number || ''" type="text" class="form-input bg-gray-100 cursor-not-allowed" placeholder="Auto Generated" disabled />
        </FormField>

        <FormField label="Date" required>
          <input v-model="form.date" type="date" class="form-input" />
        </FormField>

        <FormField label="Transaction Type" required>
          <SearchableSelect
            v-model="form.transaction_type"
            :options="transactionTypeOptions"
            placeholder="----- None -----"
            searchPlaceholder="Search transaction type..."
          />
        </FormField>

        <FormField label="Cashflow Type">
          <input :value="cashflowTypeDisplay" type="text" class="form-input bg-gray-100 cursor-not-allowed" disabled />
        </FormField>

        <FormField label="Component Budget">
          <input :value="budgetComponentDisplay" type="text" class="form-input bg-gray-100 cursor-not-allowed" disabled />
        </FormField>

        <FormField label="Due Date" required>
          <input v-model="form.due_date" type="date" class="form-input" />
        </FormField>

        <FormField label="Description">
          <textarea v-model="form.description" class="form-input h-20 resize-none" placeholder="Description..."></textarea>
        </FormField>
      </div>

      <!-- Right Column -->
      <div class="space-y-4">
        <FormField label="Currency">
          <select v-model="form.currency" class="form-input" disabled>
            <option value="IDR">IDR</option>
            <option value="USD">USD</option>
            <option value="EUR">EUR</option>
            <option value="SGD">SGD</option>
          </select>
        </FormField>

        <FormField label="Payment To">
          <SearchableSelect
            v-model="form.payment_to"
            :options="paymentToOptions"
            placeholder="----- None -----"
            searchPlaceholder="Search payment to..."
          />
        </FormField>

        <FormField label="Notes / Payment To">
          <textarea v-model="form.notes_payment_to" class="form-input h-14 resize-none bg-gray-100 cursor-not-allowed" disabled></textarea>
        </FormField>

        <FormField label="Notes">
          <textarea v-model="form.notes" class="form-input h-14 resize-none" placeholder="Notes..."></textarea>
        </FormField>

        <FormField label="Requestor Department">
          <SearchableSelect
            v-model="form.requestor_department"
            :options="departmentOptions"
            placeholder="----- None -----"
            searchPlaceholder="Search department..."
            :disabled="true"
          />
        </FormField>

        <FormField label="Choose Obligation" required>
          <SearchableSelect
            v-model="form.bank_obligation"
            :options="bankObligationOptions"
            placeholder="----- Select Obligation -----"
            searchPlaceholder="Search obligation..."
          />
        </FormField>

        <!-- Amount Summary -->
        <div class="grid grid-cols-1 gap-2 mt-4">
          <div class="bg-white border border-gray-200 rounded-lg px-3 py-2 text-xs">
            <p class="text-gray-400 uppercase tracking-wide mb-1">Total Amount</p>
            <p class="font-bold text-bfs-navy text-lg">{{ formatNumber(totalAmount) }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Input Detail Table -->
    <div class="bg-white border border-gray-200 rounded-xl overflow-hidden">
      <div class="flex items-center justify-between px-4 py-3 border-b border-gray-100 bg-gray-50">
        <h4 class="text-sm font-bold text-gray-700">Input Detail</h4>
      </div>
      
      <div class="overflow-x-auto">
        <table class="w-full text-sm text-left">
          <thead class="bg-gray-50/50 text-gray-600 font-medium border-b border-gray-200">
            <tr>
              <th class="px-4 py-3 w-12 text-center">
                <input type="checkbox" @change="toggleAllDetails" :checked="allDetailsSelected" class="w-4 h-4 rounded accent-bfs-navy" />
              </th>
              <th class="px-4 py-3">Description</th>
              <th class="px-4 py-3">Account (COA)</th>
              <th class="px-4 py-3 text-right">Amount</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-if="outstandingDetails.length === 0" class="bg-white">
              <td colspan="4" class="px-4 py-8 text-center text-gray-500">
                <div class="flex flex-col items-center justify-center space-y-2">
                  <div class="w-12 h-12 bg-gray-50 rounded-full flex items-center justify-center mb-2">
                    <span class="text-2xl text-gray-400">📄</span>
                  </div>
                  <p class="font-medium text-gray-600">No Details Available</p>
                  <p class="text-xs text-gray-400">Please select an obligation with outstanding installments.</p>
                </div>
              </td>
            </tr>
            <tr v-for="(detail, index) in outstandingDetails" :key="index" class="bg-white hover:bg-gray-50/50 transition-colors">
              <td class="px-4 py-3 text-center">
                <input type="checkbox" v-model="detail.selected" class="w-4 h-4 rounded accent-bfs-navy" />
              </td>
              <td class="px-4 py-3">
                <div class="font-medium text-gray-800">{{ detail.description }}</div>
                <div class="text-xs text-gray-500">Cicilan Ke-{{ detail.no }} / Bln {{ detail.bulan }}</div>
              </td>
              <td class="px-4 py-3">
                <div class="text-gray-700">{{ accountDisplay }}</div>
              </td>
              <td class="px-4 py-3 text-right font-medium text-gray-800">
                {{ formatNumber(detail.amount) }}
              </td>
            </tr>
          </tbody>
          <tfoot v-if="outstandingDetails.length > 0" class="bg-gray-50 border-t border-gray-200">
            <tr>
              <td colspan="3" class="px-4 py-3 text-right font-bold text-gray-700">Total Selected:</td>
              <td class="px-4 py-3 text-right font-bold text-bfs-navy">{{ formatNumber(totalAmount) }}</td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import FormField from '../../components/FormField.vue'
import SearchableSelect from '../../components/SearchableSelect.vue'
import api from '../../services/api'
import { useAuthStore } from '../../stores/auth'
import Swal from 'sweetalert2'

const props = defineProps({
  form: { type: Object, required: true },
  usageFor: { type: String, required: true } // 'Bank Obligation Principal' or 'Bank Obligation Interest'
})

const authStore = useAuthStore()

// ── Options ───────────────────────────────────────────────────────────────────
const transactionTypeOptions = ref([])
const paymentToOptions = ref([])
const bankObligationOptions = ref([])
const departmentOptions = ref([])

const flattenDepartments = (depts) => {
  let flat = []
  depts.forEach(d => {
    flat.push(d)
    if (d.children?.length) flat = flat.concat(flattenDepartments(d.children))
  })
  return flat
}

// ── States ────────────────────────────────────────────────────────────────────
const outstandingDetails = ref([])
const settings = ref(null)
const selectedBankObligation = ref(null)



const cashflowTypeDisplay = computed(() => {
  if (!settings.value) return '-'
  return props.usageFor === 'Bank Obligation Principal' ? (settings.value.pokok_cost_category_name || '-') : (settings.value.bunga_cost_category_name || '-')
})

const budgetComponentDisplay = computed(() => {
  if (!settings.value) return '-'
  return props.usageFor === 'Bank Obligation Principal' ? (settings.value.pokok_budget_component_name || '-') : (settings.value.bunga_budget_component_name || '-')
})

const accountDisplay = computed(() => {
  if (!selectedBankObligation.value) return '-'
  if (props.usageFor === 'Bank Obligation Principal') {
    return selectedBankObligation.value.account_pokok_name || '-'
  } else {
    return selectedBankObligation.value.account_bunga_name || '-'
  }
})

const totalAmount = computed(() => {
  return outstandingDetails.value.filter(d => d.selected).reduce((sum, d) => sum + Number(d.amount), 0)
})

const allDetailsSelected = computed(() => {
  if (outstandingDetails.value.length === 0) return false
  return outstandingDetails.value.every(d => d.selected)
})

const toggleAllDetails = (e) => {
  const checked = e.target.checked
  outstandingDetails.value.forEach(d => {
    d.selected = checked
  })
}

const formatNumber = (value) => {
  if (!value) return '0.00'
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value)
}

const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
const formatPeriod = (dateStr) => {
  if (!dateStr) return ''
  const [year, month] = dateStr.split('-')
  return `${monthNames[parseInt(month, 10) - 1]}-${year}`
}

const getBankShortName = (name) => {
  if (!name) return ''
  const match = name.match(/\(([^)]+)\)/)
  return match ? match[1] : name
}

const updateDescription = () => {
  const selected = outstandingDetails.value.filter(d => d.selected)
  if (selected.length === 0) {
    props.form.description = ''
    return
  }

  const typeStr = props.usageFor === 'Bank Obligation Principal' ? 'Pokok' : 'Bunga'
  const bankName = getBankShortName(selectedBankObligation.value?.bank_name)
  const contractNumber = selectedBankObligation.value?.contract_number || selectedBankObligation.value?.loan_no || ''
  
  const periods = selected.map(d => formatPeriod(d.bulan))
  const periodStr = periods.join(' & ')

  const contractPart = contractNumber ? `. ${contractNumber}` : ''
  props.form.description = `Pembayaran ${typeStr} Pinjaman ${bankName} Periode ${periodStr}${contractPart}`
}

// ── Data Fetching ─────────────────────────────────────────────────────────────
const loadOptions = async () => {
  try {
    const [transRes, payToRes, boRes, setRes, deptRes] = await Promise.all([
      api.get('master-type/transaction-type/'),
      api.get('master-type/payment-to/'),
      api.get('accounting/bank-obligation/active_bank_obligations/'),
      api.get('accounting/bank-obligation-setting/'),
      api.get('org/departments/')
    ])

    departmentOptions.value = flattenDepartments(deptRes.data.results || deptRes.data).map(d => ({
      id: d.id, label: `${d.code} - ${d.name}`
    }))

    transactionTypeOptions.value = (transRes.data.results || transRes.data).map(t => ({
      id: t.id, label: `${t.type_code} - ${t.type_name_en || t.type_name_id || ''}`
    }))
    paymentToOptions.value = (payToRes.data.results || payToRes.data)
      .filter(p => !p.is_hide)
      .map(p => ({
        id: p.id, label: `${p.name} - ${p.bank?.bank_name || ''}`, description: p.description
    }))
    bankObligationOptions.value = (boRes.data.results || boRes.data).map(b => ({
      id: b.id, label: `${b.loan_no} - ${b.bank_name}`, original: b
    }))
    
    settings.value = setRes.data
    
    // Set default requestor department
    if (!props.form.requestor_department) {
      try {
        const userRes = await api.get('auth/me/')
        const empRes = await api.get(`org/employees/?user=${userRes.data.id}`)
        const emp = (empRes.data.results || empRes.data)[0]
        if (emp?.department) props.form.requestor_department = emp.department
      } catch { /* silently skip */ }
    }
    
    if (props.form.bank_obligation) {
      loadOutstandingDetails(props.form.bank_obligation)
    }
  } catch (error) {
    console.error('Error loading options:', error)
  }
}

const loadOutstandingDetails = async (boId) => {
  if (!boId) {
    outstandingDetails.value = []
    selectedBankObligation.value = null
    return
  }

  try {
    const boOpt = bankObligationOptions.value.find(o => o.id === boId)
    if (boOpt) {
      selectedBankObligation.value = boOpt.original
    }

    let url = `/accounting/bank-obligation/${boId}/outstanding_details/?usage_for=${encodeURIComponent(props.usageFor)}`
    if (props.form.id) {
      url += `&exclude_cbr_id=${props.form.id}`
    }
    const res = await api.get(url)
    
    outstandingDetails.value = res.data.map(d => {
      const existingDetail = (props.form.details || []).find(fd => fd.bank_obligation_detail === d.id)
      return {
        id: d.id,
        detail_id: existingDetail ? existingDetail.id : undefined,
        no: d.no,
        bulan: d.bulan,
        description: props.usageFor === 'Bank Obligation Principal' ? `Angsuran Pokok Pinjaman ${selectedBankObligation.value?.loan_no}` : `Angsuran Bunga Pinjaman ${selectedBankObligation.value?.loan_no}`,
        amount: props.usageFor === 'Bank Obligation Principal' ? d.pokok : d.margin,
        selected: !!existingDetail
      }
    })
  } catch (error) {
    console.error('Error loading outstanding details:', error)
  }
}

// ── Watchers ──────────────────────────────────────────────────────────────────
watch(() => props.form.payment_to, async (newVal) => {
  if (!newVal) {
    props.form.notes_payment_to = ''
    return
  }
  try {
    const res = await api.get(`master-type/payment-to/${newVal}/`)
    const data = res.data
    const details = []
    if (data.bank?.bank_name) details.push(data.bank.bank_name)
    if (data.bank_city) details.push(data.bank_city)
    if (data.account_number) details.push(data.account_number)
    if (data.account_name) details.push(data.account_name)
    props.form.notes_payment_to = details.join('\n')
  } catch (error) {
    console.error('Error fetching payment to details:', error)
  }
})

watch(() => props.form.bank_obligation, (newVal) => {
  loadOutstandingDetails(newVal)
})

// Sync back to parent form when details change
watch(() => outstandingDetails.value, (newVal) => {
  const selected = newVal.filter(d => d.selected)
  props.form.details = selected.map(d => ({
    id: d.detail_id,
    bank_obligation_detail: d.id,
    quantity: 1,
    unit_price: d.amount,
    total_amount: d.amount
  }))
  props.form.amount = totalAmount.value
  updateDescription()
}, { deep: true })

onMounted(() => {
  if (!props.form.date) props.form.date = new Date().toISOString().split('T')[0]
  if (!props.form.due_date) props.form.due_date = new Date().toISOString().split('T')[0]
  if (!props.form.currency) props.form.currency = authStore.user?.company?.currency || 'IDR'
  
  loadOptions()
})
</script>
