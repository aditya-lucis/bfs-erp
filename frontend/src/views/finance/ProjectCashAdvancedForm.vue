<template>
  <div class="px-6 py-4 space-y-6">

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 bg-gray-50/50 p-4 rounded-xl border border-gray-100">
      <!-- Left Column -->
      <div class="space-y-4">
        <FormField label="Document Number">
          <input :value="form.document_number || ''" type="text" class="form-input bg-gray-100 cursor-not-allowed" placeholder="Auto Generated" disabled />
        </FormField>

        <FormField label="Date" required>
          <input v-model="form.date" type="date" class="form-input" @change="recalcDueDate" />
        </FormField>

        <FormField label="Budget Component">
          <input v-model="form.budget_component_name" type="text" class="form-input bg-gray-100 cursor-not-allowed" disabled />
        </FormField>

        <FormField label="Transaction Type" required>
          <SearchableSelect
            v-model="form.transaction_type"
            :options="transactionTypeOptions"
            placeholder="----- None -----"
            searchPlaceholder="Search transaction type..."
          />
        </FormField>

        <FormField label="Duration Due Date">
          <select v-model="form.duration_due_date" @change="recalcDueDate" class="form-input">
            <option value="">----- None -----</option>
            <option value="7">7 Hari</option>
            <option value="14">14 Hari</option>
            <option value="30">30 Hari</option>
            <option value="45">45 Hari</option>
            <option value="60">60 Hari</option>
          </select>
        </FormField>

        <FormField label="Due Date">
          <input v-model="form.due_date" type="date" class="form-input bg-gray-100 cursor-not-allowed" disabled />
        </FormField>

        <FormField label="Description">
          <textarea v-model="form.description" class="form-input h-20 resize-none" placeholder="Description..."></textarea>
        </FormField>
      </div>

      <!-- Right Column -->
      <div class="space-y-4">
        <FormField label="Currency">
          <select v-model="form.currency" class="form-input">
            <option value="IDR">IDR</option>
            <option value="USD">USD</option>
            <option value="EUR">EUR</option>
            <option value="SGD">SGD</option>
          </select>
        </FormField>

        <FormField label="Project" required>
          <SearchableSelect
            v-model="form.project"
            :options="projectOptions"
            placeholder="----- None -----"
            searchPlaceholder="Search project..."
          />
        </FormField>

        <FormField label="Account (COA)">
          <SearchableSelect
            v-model="form.account"
            :options="accountOptions"
            placeholder="----- None -----"
            searchPlaceholder="Search account..."
          />
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

        <!-- Amount Summary -->
        <div class="grid grid-cols-3 gap-2">
          <div class="bg-white border border-gray-200 rounded-lg px-3 py-2 text-xs">
            <p class="text-gray-400 uppercase tracking-wide mb-1">Net Amount</p>
            <p class="font-bold text-gray-800">{{ formatNumber(netAmount) }}</p>
          </div>
          <div class="bg-white border border-gray-200 rounded-lg px-3 py-2 text-xs">
            <p class="text-gray-400 uppercase tracking-wide mb-1">Tax In</p>
            <p class="font-bold text-gray-800">{{ formatNumber(taxInTotal) }}</p>
          </div>
          <div class="bg-white border border-gray-200 rounded-lg px-3 py-2 text-xs">
            <p class="text-gray-400 uppercase tracking-wide mb-1">Grand Total</p>
            <p class="font-bold text-bfs-navy">{{ formatNumber(netAmount + taxInTotal) }}</p>
          </div>
        </div>

        <!-- Checkboxes -->
        <div class="flex flex-col gap-2 pt-1">
          <label class="flex items-center gap-2 text-sm cursor-pointer select-none">
            <input v-model="form.is_pr_for_lpj" type="checkbox" class="w-4 h-4 rounded accent-bfs-navy" />
            <span>Is For LPJ</span>
            <span v-if="isUangMuka" class="ml-1 text-xs font-semibold text-amber-600 bg-amber-50 border border-amber-200 px-1.5 py-0.5 rounded">Uang Muka</span>
          </label>
          <label class="flex items-center gap-2 text-sm cursor-pointer select-none">
            <input v-model="form.is_reimbursement" type="checkbox" class="w-4 h-4 rounded accent-bfs-navy" />
            <span>Is Reimbursement</span>
          </label>
          <label class="flex items-center gap-2 text-sm cursor-pointer select-none">
            <input v-model="form.is_vendor" type="checkbox" class="w-4 h-4 rounded accent-bfs-navy" />
            <span>Is Vendor</span>
          </label>
          <div v-if="form.is_vendor" class="ml-6 mt-1">
            <SearchableSelect
              v-model="form.vendor"
              :options="vendorOptions"
              placeholder="----- Select Vendor -----"
              searchPlaceholder="Search vendor..."
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Item Detail Table -->
    <div class="bg-white border border-gray-200 rounded-xl overflow-hidden">
      <div class="flex items-center justify-between px-4 py-3 border-b border-gray-100 bg-gray-50">
        <h4 class="text-sm font-bold text-gray-700">Item Details</h4>
        <button
          @click="openRapPicker"
          :disabled="!form.project"
          class="px-3 py-1.5 text-xs font-semibold bg-bfs-navy text-white rounded-lg hover:bg-opacity-90 transition-colors disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-1.5"
        >
          <Plus class="w-3.5 h-3.5" />
          Multiple Item
        </button>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-xs min-w-[1400px]">
          <thead class="bg-gray-50 border-b border-gray-200">
            <tr>
              <th class="px-3 py-2 text-left text-gray-500 w-10">#</th>
              <th class="px-3 py-2 text-left text-gray-500 min-w-[140px]">Item Code</th>
              <th class="px-3 py-2 text-left text-gray-500 min-w-[180px]">Item Name</th>
              <th class="px-3 py-2 text-right text-gray-500 min-w-[100px]">Qty</th>
              <th class="px-3 py-2 text-right text-gray-500 min-w-[120px]">Unit Price</th>
              <th class="px-3 py-2 text-right text-gray-500 min-w-[120px]">Price</th>
              <th class="px-3 py-2 text-center text-gray-500 min-w-[70px]">Tax In</th>
              <th class="px-3 py-2 text-right text-gray-500 min-w-[120px]">Tax Amt</th>
              <th class="px-3 py-2 text-left text-gray-500 min-w-[130px]">No Faktur</th>
              <th class="px-3 py-2 text-left text-gray-500 min-w-[130px]">NPWP</th>
              <th class="px-3 py-2 text-left text-gray-500 min-w-[180px]">Account Tax</th>
              <th class="px-3 py-2 text-left text-gray-500 min-w-[130px]">Tax Date</th>
              <th class="px-3 py-2 w-12 text-center">Act</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="!form.details || form.details.length === 0">
              <td colspan="13" class="py-10 text-center text-gray-400">
                Belum ada item. Klik <strong>Multiple Item</strong> untuk memilih dari RAP.
              </td>
            </tr>
            <tr
              v-for="(row, idx) in form.details"
              :key="row.rap_detail || idx"
              class="border-b border-gray-100 hover:bg-gray-50/70 transition-colors"
            >
              <td class="px-3 py-1.5 text-gray-400">{{ idx + 1 }}</td>
              <td class="px-3 py-1.5 font-mono text-gray-600">{{ row.item_code || '-' }}</td>
              <td class="px-3 py-1.5 font-medium">{{ row.item_name || '-' }}</td>
              <td class="px-3 py-1.5">
                <input
                  v-model.number="row.quantity"
                  @change="onQtyChange(row)"
                  type="number"
                  step="0.01" min="0"
                  :max="row.rap_detail_volume || undefined"
                  class="form-input text-right text-xs py-1 px-2 w-full"
                />
              </td>
              <td class="px-3 py-1.5 text-right">{{ formatNumber(row.unit_price) }}</td>
              <td class="px-3 py-1.5 text-right font-semibold text-bfs-navy">{{ formatNumber((row.quantity || 0) * (row.unit_price || 0)) }}</td>
              <td class="px-3 py-1.5 text-center">
                <input v-model="row.is_tax_in" type="checkbox" class="w-3.5 h-3.5 accent-bfs-navy cursor-pointer" @change="onTaxInChange(row)" />
              </td>
              <td class="px-3 py-1.5">
                <input
                  v-if="row.is_tax_in"
                  :value="formatNumber(row.tax_amount)"
                  type="text"
                  readonly
                  class="form-input text-right text-xs py-1 px-2 w-full bg-gray-50 text-gray-500 cursor-not-allowed font-semibold"
                />
                <span v-else class="text-gray-300 block text-right">-</span>
              </td>
              <td class="px-3 py-1.5">
                <input v-if="row.is_tax_in" v-model="row.no_faktur" type="text" class="form-input text-xs py-1 px-2 w-full" placeholder="No Faktur" />
                <span v-else class="text-gray-300">-</span>
              </td>
              <td class="px-3 py-1.5">
                <input v-if="row.is_tax_in" v-model="row.npwp" type="text" class="form-input text-xs py-1 px-2 w-full" placeholder="NPWP" />
                <span v-else class="text-gray-300">-</span>
              </td>
              <td class="px-3 py-1.5">
                <SearchableSelect
                  v-if="row.is_tax_in"
                  v-model="row.tax_account"
                  :options="taxAccountOptions"
                  placeholder="Select..."
                  searchPlaceholder="Search..."
                />
                <span v-else class="text-gray-300">-</span>
              </td>
              <td class="px-3 py-1.5">
                <input v-if="row.is_tax_in" v-model="row.tax_date" type="date" class="form-input text-xs py-1 px-2 w-full" />
                <span v-else class="text-gray-300">-</span>
              </td>
              <td class="px-3 py-1.5">
                <button @click="removeDetail(idx)" class="p-1 text-red-400 hover:text-red-600 transition-colors rounded hover:bg-red-50">
                  <Trash2 class="w-3.5 h-3.5" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- RAP Picker Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="rapPicker.show" class="fixed inset-0 z-[70] overflow-y-auto">
          <div class="fixed inset-0 bg-black/40" @click="rapPicker.show = false" />
          <div class="flex min-h-full items-start justify-center p-4 py-10">
            <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-5xl z-10" @click.stop>
              <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
                <div>
                  <h3 class="text-base font-bold text-gray-800">Pilih Item dari RAP</h3>
                  <p class="text-xs text-gray-500 mt-0.5">Centang item yang ingin dimasukkan ke dalam PCA</p>
                </div>
                <button @click="rapPicker.show = false" class="text-gray-400 hover:text-gray-600">
                  <X class="w-5 h-5" />
                </button>
              </div>

              <div class="overflow-x-auto max-h-[55vh] overflow-y-auto p-2">
                <table class="w-full text-xs">
                  <thead class="bg-gray-50 sticky top-0 z-10">
                    <tr>
                      <th class="px-3 py-2 w-8">
                        <input
                          type="checkbox"
                          :checked="rapPicker.selected.length > 0 && rapPicker.selected.length === rapPicker.items.length"
                          :indeterminate="rapPicker.selected.length > 0 && rapPicker.selected.length < rapPicker.items.length"
                          @change="toggleSelectAllRap"
                          class="w-3.5 h-3.5 accent-bfs-navy cursor-pointer"
                        />
                      </th>
                      <th class="px-3 py-2 text-left text-gray-500">No</th>
                      <th class="px-3 py-2 text-left text-gray-500">Item Code</th>
                      <th class="px-3 py-2 text-left text-gray-500">Item Name</th>
                      <th class="px-3 py-2 text-left text-gray-500">Unit</th>
                      <th class="px-3 py-2 text-right text-gray-500">Volume</th>
                      <th class="px-3 py-2 text-right text-gray-500">Unit Price</th>
                      <th class="px-3 py-2 text-right text-gray-500">Price</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-if="rapPicker.loading">
                      <td colspan="8" class="py-10 text-center text-gray-400">Memuat item RAP...</td>
                    </tr>
                    <tr v-else-if="rapPicker.items.length === 0">
                      <td colspan="8" class="py-10 text-center text-gray-400">Tidak ada item RAP yang tersedia untuk dipilih.</td>
                    </tr>
                    <tr
                      v-for="(item, idx) in rapPicker.items"
                      :key="item.id"
                      class="border-b border-gray-100 hover:bg-blue-50 cursor-pointer transition-colors"
                      :class="{ 'bg-blue-50': rapPicker.selected.includes(item.id) }"
                      @click="toggleRapItem(item.id)"
                    >
                      <td class="px-3 py-2 text-center" @click.stop="toggleRapItem(item.id)">
                        <input type="checkbox" :checked="rapPicker.selected.includes(item.id)" class="w-3.5 h-3.5 accent-bfs-navy pointer-events-none" />
                      </td>
                      <td class="px-3 py-2 text-gray-500">{{ idx + 1 }}</td>
                      <td class="px-3 py-2 font-mono text-gray-600">{{ item.item_code || '-' }}</td>
                      <td class="px-3 py-2 font-medium">{{ item.item_name || item.description || '-' }}</td>
                      <td class="px-3 py-2 text-gray-500">{{ item.unit_name || '-' }}</td>
                      <td class="px-3 py-2 text-right">{{ formatNumber(item.volume) }}</td>
                      <td class="px-3 py-2 text-right">{{ formatNumber(item.unit_price) }}</td>
                      <td class="px-3 py-2 text-right font-semibold">{{ formatNumber((item.volume || 0) * (item.unit_price || 0)) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <div class="flex justify-between items-center px-6 py-4 border-t border-gray-100 bg-gray-50 rounded-b-2xl">
                <span class="text-xs text-gray-500 font-semibold">{{ rapPicker.selected.length }} item dipilih</span>
                <div class="flex gap-2">
                  <button @click="rapPicker.show = false" class="px-4 py-2 text-sm text-gray-600 font-semibold hover:text-gray-800 transition-colors">Batal</button>
                  <button
                    @click="confirmRapSelection"
                    :disabled="rapPicker.selected.length === 0"
                    class="px-5 py-2 text-sm font-bold bg-bfs-navy text-white rounded-lg hover:bg-opacity-90 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                  >
                    Tambahkan ({{ rapPicker.selected.length }})
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { Plus, Trash2, X } from 'lucide-vue-next'
import FormField from '../../components/FormField.vue'
import SearchableSelect from '../../components/SearchableSelect.vue'
import api from '../../services/api'
import Swal from 'sweetalert2'

const props = defineProps({
  form: { type: Object, required: true }
})

// ── Options ───────────────────────────────────────────────────────────────────
const transactionTypeOptions = ref([])
const projectOptions = ref([])
const paymentToOptions = ref([])
const departmentOptions = ref([])
const accountOptions = ref([])
const taxAccountOptions = ref([])
const vendorOptions = ref([])

const flattenDepartments = (depts) => {
  let flat = []
  depts.forEach(d => {
    flat.push(d)
    if (d.children?.length) flat = flat.concat(flattenDepartments(d.children))
  })
  return flat
}

const today = () => new Date().toLocaleDateString('en-CA')

const fetchOptions = async () => {
  try {
    const [trsTypeRes, projRes, paymentToRes, deptRes, coaRes, vendorRes] = await Promise.all([
      api.get('master-type/transaction-type/'),
      api.get(`projects/projects/?usage=project_cash_advanced${props.form.id ? '&exclude_cbr=' + props.form.id : ''}&_t=${Date.now()}`),
      api.get('master-type/payment-to/'),
      api.get('org/departments/'),
      api.get('accounting/coa/'),
      api.get('purchase/vendors/')
    ])

    transactionTypeOptions.value = (trsTypeRes.data.results || trsTypeRes.data).map(t => ({
      id: t.id, label: `${t.type_code} - ${t.type_name_en || t.type_name_id || ''}`
    }))

    projectOptions.value = (projRes.data.results || projRes.data).map(p => ({
      id: p.id, label: p.project_name
    }))

    paymentToOptions.value = (paymentToRes.data.results || paymentToRes.data)
      .filter(p => !p.is_hide)
      .map(p => ({ id: p.id, label: p.name, description: p.description }))

    departmentOptions.value = flattenDepartments(deptRes.data.results || deptRes.data)
      .map(d => ({ id: d.id, label: `${d.code} - ${d.name}` }))

    const allAccounts = coaRes.data.results || coaRes.data
    accountOptions.value = allAccounts.filter(a => a.is_postable).map(a => ({
      id: a.id, label: `${a.account_number} ${a.account_name}`
    }))
    taxAccountOptions.value = allAccounts.filter(a => a.is_tax_in).map(a => ({
      id: a.id, label: `${a.account_number} ${a.account_name}`
    }))

    vendorOptions.value = (vendorRes.data.results || vendorRes.data).map(v => ({
      id: v.id, label: v.name
    }))

    // Auto-fill requestor department
    await fetchUserDepartment()

    // Ensure project in list when editing
    if (props.form.id && props.form.project) {
      const exists = projectOptions.value.find(p => p.id === props.form.project)
      if (!exists) {
        projectOptions.value.push({ id: props.form.project, label: props.form.project_display || `Project ${props.form.project}` })
      }
    }
  } catch (error) {
    console.error('Error fetching options:', error)
    Swal.fire('Error', 'Gagal memuat data options.', 'error')
  }
}

const fetchUserDepartment = async () => {
  if (props.form.requestor_department) return // already set (edit mode)
  try {
    const userRes = await api.get('auth/me/')
    const empRes = await api.get(`org/employees/?user=${userRes.data.id}`)
    const emp = (empRes.data.results || empRes.data)[0]
    if (emp?.department) props.form.requestor_department = emp.department
  } catch { /* silently skip */ }
}

// ── Computed ──────────────────────────────────────────────────────────────────
const isUangMuka = computed(() => props.form.is_pr_for_lpj || props.form.is_reimbursement)

const netAmount = computed(() =>
  (props.form.details || []).reduce((s, d) => s + (parseFloat(d.quantity || 0) * parseFloat(d.unit_price || 0)), 0)
)

const taxInTotal = computed(() =>
  (props.form.details || []).filter(d => d.is_tax_in).reduce((s, d) => s + parseFloat(d.tax_amount || 0), 0)
)

// ── Watchers ──────────────────────────────────────────────────────────────────
watch([netAmount, taxInTotal], ([net, tax]) => {
  props.form.amount = net
  props.form.tax_amount = tax
}, { immediate: true })

watch(() => props.form.payment_to, (val) => {
  const sel = paymentToOptions.value.find(p => p.id === val)
  props.form.notes_payment_to = sel?.description || ''
})

watch(() => props.form.is_vendor, (val) => {
  if (!val) props.form.vendor = null
})

watch(() => props.form.project, async (val) => {
  if (val) {
    try {
      const rapRes = await api.get(`projects/raps/?project=${val}&is_active=true`)
      const raps = rapRes.data.results || rapRes.data
      if (raps?.length) {
        props.form.budget_component = raps[0].budget_component || null
        props.form.budget_component_name = raps[0].budget_component_name || ''
      } else {
        props.form.budget_component_name = ''
      }
    } catch (e) { console.error(e) }
  }
})

// ── Helpers ───────────────────────────────────────────────────────────────────
const formatNumber = (val) => {
  if (!val && val !== 0) return '0.00'
  return new Intl.NumberFormat('en-US', { minimumFractionDigits: 2 }).format(val)
}

const recalcDueDate = () => {
  if (!props.form.date || !props.form.duration_due_date) return
  const d = new Date(props.form.date)
  d.setDate(d.getDate() + parseInt(props.form.duration_due_date))
  props.form.due_date = d.toLocaleDateString('en-CA')
}

const onQtyChange = (row) => {
  const max = parseFloat(row.rap_detail_volume || 0)
  if (max > 0 && parseFloat(row.quantity || 0) > max) {
    Swal.fire({
      icon: 'warning',
      title: 'Melebihi Volume RAP',
      text: `Quantity tidak boleh melebihi volume RAP (max: ${max}).`,
      confirmButtonColor: '#1d3557'
    })
    row.quantity = max
  }
  if (row.is_tax_in) {
    row.tax_amount = (parseFloat(row.quantity || 0) * parseFloat(row.unit_price || 0)) * 0.11
  }
}

const onTaxInChange = (row) => {
  if (!row.is_tax_in) {
    row.tax_amount = 0; row.no_faktur = ''; row.npwp = ''; row.tax_account = null; row.tax_date = ''
  } else {
    if (!row.tax_date) row.tax_date = today()
    row.tax_amount = (parseFloat(row.quantity || 0) * parseFloat(row.unit_price || 0)) * 0.11
  }
}

const removeDetail = (idx) => props.form.details.splice(idx, 1)

// ── RAP Picker ────────────────────────────────────────────────────────────────
const rapPicker = ref({ show: false, loading: false, items: [], selected: [] })

const openRapPicker = async () => {
  if (!props.form.project) return
  rapPicker.value = { show: true, loading: true, items: [], selected: [] }

  try {
    let url = `accounting/cashbook-request/available_rap_details/?project_id=${props.form.project}`
    if (props.form.id) {
      url += `&header_id=${props.form.id}`
    }
    
    const res = await api.get(url)
    let items = res.data || []
    
    if (!items.length) {
      rapPicker.value.loading = false
      Swal.fire('Info', 'Tidak ada item RAP yang tersedia untuk project ini (mungkin sudah habis dipakai).', 'info')
      rapPicker.value.show = false
      return
    }
    
    // Filter out items that are already selected in the CURRENT frontend form state
    const alreadySelectedIds = (props.form.details || []).map(d => d.rap_detail).filter(Boolean)
    items = items.filter(d => !alreadySelectedIds.includes(d.id))
    rapPicker.value.items = items
  } catch (e) {
    console.error(e)
    Swal.fire('Error', 'Gagal memuat item RAP.', 'error')
    rapPicker.value.show = false
  } finally {
    rapPicker.value.loading = false
  }
}

const toggleRapItem = (id) => {
  const i = rapPicker.value.selected.indexOf(id)
  if (i === -1) rapPicker.value.selected.push(id)
  else rapPicker.value.selected.splice(i, 1)
}

const toggleSelectAllRap = () => {
  rapPicker.value.selected = rapPicker.value.selected.length === rapPicker.value.items.length
    ? [] : rapPicker.value.items.map(i => i.id)
}

const confirmRapSelection = () => {
  const todayStr = today()
  if (!props.form.details) props.form.details = []

  rapPicker.value.items
    .filter(i => rapPicker.value.selected.includes(i.id))
    .forEach(item => {
      if (props.form.details.find(d => d.rap_detail === item.id)) return
      props.form.details.push({
        id: null,
        rap_detail: item.id,
        item: item.item,
        item_code: item.item_code,
        item_name: item.item_name || item.description,
        unit_name: item.unit_name,
        rap_detail_volume: parseFloat(item.volume || 0),
        quantity: parseFloat(item.volume || 0),
        unit_price: parseFloat(item.unit_price || 0),
        total_amount: parseFloat(item.volume || 0) * parseFloat(item.unit_price || 0),
        is_tax_in: false,
        tax_amount: 0,
        no_faktur: '',
        npwp: '',
        tax_account: null,
        tax_date: todayStr
      })
    })

  rapPicker.value.show = false
}

onMounted(() => {
  if (!props.form.date) props.form.date = today()
  if (!props.form.details) props.form.details = []
  if (!props.form.currency) props.form.currency = 'IDR'
  fetchOptions()
})
</script>
