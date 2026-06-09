<template>
  <div class="fixed inset-0 z-50 flex items-start justify-center bg-black/40 overflow-y-auto py-6">
    <div class="bg-white rounded-xl shadow-2xl w-full max-w-5xl mx-4 my-4">

      <div class="bg-bfs-navy text-white px-6 py-3 rounded-t-xl flex justify-between items-center">
        <span class="font-semibold text-sm">
          Purchases | Vendor | {{ isEdit ? 'Edit Vendor' : 'Add Vendor' }}
        </span>
        <button @click="$emit('close')" class="text-white/80 hover:text-white text-lg">✕</button>
      </div>

      <!-- Tabs -->
      <div class="flex border-b border-gray-200 px-6 pt-3 gap-4 overflow-x-auto">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          @click="switchTab(tab.key)"
          :disabled="tab.requiresEdit && !isEdit"
          :class="[
            'pb-2 text-sm font-medium border-b-2 whitespace-nowrap transition-colors',
            activeTab === tab.key ? 'border-bfs-gold text-bfs-navy' : 'border-transparent text-gray-500',
            tab.requiresEdit && !isEdit ? 'opacity-40 cursor-not-allowed' : '',
          ]"
        >{{ tab.label }}</button>
      </div>

      <!-- Tab: Data Utama -->
      <div v-show="activeTab === 'main'" class="p-6 grid grid-cols-2 gap-x-6 gap-y-4">
        <div v-if="isEdit" class="col-span-2 sm:col-span-1">
          <label class="form-label">Code</label>
          <input :value="form.code" disabled class="form-input bg-gray-50 font-mono" />
        </div>
        <div class="flex items-center gap-2">
          <input type="checkbox" v-model="form.is_leasing" id="is_leasing" class="rounded" />
          <label for="is_leasing" class="text-sm text-gray-700">Is Leasing</label>
        </div>

        <div>
          <label class="form-label">Department</label>
          <select v-model="form.department" class="form-input">
            <option :value="null">None</option>
            <option v-for="d in deptList" :key="d.id" :value="d.id">{{ '—'.repeat(d.level) }} {{ d.name }}</option>
          </select>
        </div>
        <div>
          <label class="form-label">Variety</label>
          <input v-model="form.variety" class="form-input" placeholder="Jenis usaha / speciality" />
        </div>

        <div class="col-span-2 grid grid-cols-3 gap-3">
          <div>
            <label class="form-label">Title</label>
            <select v-model="form.title" class="form-input">
              <option value="">None</option>
              <option v-for="t in titles" :key="t" :value="t">{{ t }}</option>
            </select>
          </div>
          <div class="col-span-2">
            <label class="form-label">Name <span class="text-red-500">*</span></label>
            <input v-model="form.name" class="form-input" />
            <p v-if="errors.name" class="form-error">{{ errors.name }}</p>
          </div>
        </div>

        <div>
          <label class="form-label">Vendor Category</label>
          <select v-model="form.category" class="form-input" :disabled="isEdit">
            <option :value="null">— Pilih —</option>
            <option v-for="c in store.categories" :key="c.id" :value="c.id">{{ c.code }} - {{ c.name }}</option>
          </select>
        </div>
        <div>
          <label class="form-label">Tax Number</label>
          <input v-model="form.tax_number" class="form-input" />
        </div>
        <div>
          <label class="form-label">NPPKP</label>
          <input v-model="form.nppkp" class="form-input" />
        </div>
        <div>
          <label class="form-label">Email <span class="text-red-500">*</span></label>
          <input v-model="form.email" type="email" class="form-input" />
          <p v-if="errors.email" class="form-error">{{ errors.email }}</p>
        </div>
        <div>
          <label class="form-label">Alternative Email</label>
          <input v-model="form.alternative_email" type="email" class="form-input" />
        </div>
        <div>
          <label class="form-label">Website</label>
          <input v-model="form.website" class="form-input" placeholder="http://" />
        </div>
        <div class="col-span-2">
          <label class="form-label">Address 1 <span class="text-red-500">*</span></label>
          <textarea v-model="form.address_1" rows="2" class="form-input" />
        </div>
        <div class="col-span-2">
          <label class="form-label">Address 2</label>
          <textarea v-model="form.address_2" rows="2" class="form-input" />
        </div>
        <div>
          <label class="form-label">Country <span class="text-red-500">*</span></label>
          <input v-model="form.country" class="form-input" />
        </div>
        <div>
          <label class="form-label">State</label>
          <input v-model="form.state" class="form-input" />
        </div>
        <div>
          <label class="form-label">City <span class="text-red-500">*</span></label>
          <input v-model="form.city" class="form-input" />
        </div>
        <div>
          <label class="form-label">Zip Code</label>
          <input v-model="form.zip_code" class="form-input" />
        </div>
        <div>
          <label class="form-label">Area Code</label>
          <select v-model="form.area_code" class="form-input">
            <option value="other">[Other] Other</option>
            <option value="jakarta">Jakarta</option>
            <option value="bandung">Bandung</option>
            <option value="surabaya">Surabaya</option>
          </select>
        </div>
        <div>
          <label class="form-label">Phone 1 <span class="text-red-500">*</span></label>
          <input v-model="form.phone_1" class="form-input" />
        </div>
        <div>
          <label class="form-label">Phone 2</label>
          <input v-model="form.phone_2" class="form-input" />
        </div>
        <div>
          <label class="form-label">Fax</label>
          <input v-model="form.fax" class="form-input" />
        </div>

        <!-- Item type flags -->
        <div class="col-span-2 border-t pt-4">
          <p class="text-xs text-gray-500 mb-2 font-semibold uppercase">Company Type</p>
          <div class="flex flex-wrap gap-3">
            <label v-for="f in companyFlags" :key="f.key" class="flex items-center gap-1.5 text-sm">
              <input type="checkbox" v-model="form[f.key]" class="rounded" /> {{ f.label }}
            </label>
          </div>
        </div>
        <div class="col-span-2">
          <p class="text-xs text-gray-500 mb-2 font-semibold uppercase">Vendor Type</p>
          <div class="flex flex-wrap gap-3">
            <label v-for="f in vendorFlags" :key="f.key" class="flex items-center gap-1.5 text-sm">
              <input type="checkbox" v-model="form[f.key]" class="rounded" /> {{ f.label }}
            </label>
          </div>
        </div>
      </div>

      <!-- Tab: Financial & Bank -->
      <div v-show="activeTab === 'financial'" class="p-6 grid grid-cols-2 gap-x-6 gap-y-4">
        <div>
          <label class="form-label">Currency <span class="text-red-500">*</span></label>
          <select v-model="form.currency" class="form-input">
            <option value="IDR">IDR</option><option value="USD">USD</option>
            <option value="EUR">EUR</option><option value="SGD">SGD</option>
          </select>
        </div>
        <div>
          <label class="form-label">Tolerance Difference (%)</label>
          <input v-model="form.tolerance_difference" type="number" step="0.01" class="form-input" />
        </div>
        <div>
          <label class="form-label">Deposit</label>
          <input v-model="form.deposit" type="number" step="0.01" class="form-input" />
        </div>
        <div>
          <label class="form-label">Group</label>
          <select v-model="form.group" class="form-input">
            <option :value="null">None</option>
            <option v-for="g in store.groups" :key="g.id" :value="g.id">{{ g.name }}</option>
          </select>
        </div>
        <div>
          <label class="form-label">Vendor Status</label>
          <select v-model="form.status" class="form-input">
            <option value="open">Open</option><option value="closed">Closed</option><option value="hold">Hold</option>
          </select>
        </div>
        <div class="flex items-center gap-2 pt-6">
          <input type="checkbox" v-model="form.is_sister_company" class="rounded" />
          <label class="text-sm">Is Sister Company</label>
        </div>

        <div class="col-span-2 border-t pt-4">
          <p class="text-sm font-semibold text-gray-700 mb-3">Bank Account</p>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="form-label">Bank Name</label>
              <select v-model="form.bank_name" class="form-input">
                <option value="">— Pilih —</option>
                <option v-for="b in banks" :key="b" :value="b">{{ b }}</option>
              </select>
            </div>
            <div><label class="form-label">Bank Branch</label><input v-model="form.bank_branch" class="form-input" /></div>
            <div><label class="form-label">Bank City</label><input v-model="form.bank_city" class="form-input" /></div>
            <div><label class="form-label">Account Number</label><input v-model="form.bank_account_number" class="form-input" /></div>
            <div class="col-span-2"><label class="form-label">Account Name</label><input v-model="form.bank_account_name" class="form-input" /></div>
          </div>
        </div>
        <div class="col-span-2">
          <label class="form-label">Term and Condition</label>
          <textarea v-model="form.term_and_condition" rows="4" class="form-input" />
        </div>
      </div>

      <!-- Tab: Legal -->
      <div v-show="activeTab === 'legal'" class="p-6 grid grid-cols-2 gap-x-6 gap-y-4">
        <div>
          <label class="form-label">Company Financial Capability</label>
          <input v-model="form.company_financial_capability" type="number" step="0.01" class="form-input" />
        </div>
        <div>
          <label class="form-label">Kriteria Usaha</label>
          <select v-model="form.kriteria_usaha" class="form-input">
            <option value="usaha_kecil">Usaha Kecil</option>
            <option value="usaha_menengah">Usaha Menengah</option>
            <option value="usaha_besar">Usaha Besar</option>
          </select>
        </div>
        <div><label class="form-label">Notary Name</label><input v-model="form.notary_name" class="form-input" /></div>
        <div><label class="form-label">Letter No & Date</label><input v-model="form.letter_no_date" class="form-input" /></div>
        <div><label class="form-label">Notary Name 2</label><input v-model="form.notary_name_2" class="form-input" /></div>
        <div><label class="form-label">Letter No & Date 2</label><input v-model="form.letter_no_date_2" class="form-input" /></div>
        <div class="col-span-2"><label class="form-label">Letter Of Endorsement</label><input v-model="form.letter_of_endorsement" class="form-input" /></div>
        <div><label class="form-label">No SIUP</label><input v-model="form.no_siup" class="form-input" /></div>
        <div><label class="form-label">Expired Date SIUP</label><input v-model="form.expired_date_siup" type="date" class="form-input" /></div>
        <div><label class="form-label">No TDP</label><input v-model="form.no_tdp" class="form-input" /></div>
        <div><label class="form-label">Expired Date TDP</label><input v-model="form.expired_date_tdp" type="date" class="form-input" /></div>
        <div><label class="form-label">No SK Domisili</label><input v-model="form.no_sk_domisili" class="form-input" /></div>
        <div><label class="form-label">Expired Date SK Domisili</label><input v-model="form.expired_date_sk_domisili" type="date" class="form-input" /></div>
        <div><label class="form-label">No SIUJK</label><input v-model="form.no_siujk" class="form-input" /></div>
        <div><label class="form-label">Expired Date SIUJK</label><input v-model="form.expired_date_siujk" type="date" class="form-input" /></div>
      </div>

      <!-- Tab: Linked Accounts -->
      <div v-show="activeTab === 'linked' && isEdit" class="p-6 space-y-5">
        <div v-for="acct in linkedTypes" :key="acct.key" class="border border-gray-200 rounded-lg p-4">
          <p class="text-sm font-semibold text-gray-700 mb-3">{{ acct.label }}</p>
          <div class="flex flex-wrap items-center gap-4">
            <div class="flex items-center gap-2">
              <span class="text-xs text-gray-500">Currency:</span>
              <label v-for="cur in currencies" :key="cur" class="flex items-center gap-1 text-sm">
                <input type="radio" :name="`cur_${acct.key}`" :value="cur" v-model="linkedForms[acct.key].currency_scope" />
                {{ cur === 'all' ? 'All' : cur }}
              </label>
            </div>
            <div class="flex-1 min-w-56">
              <SearchableSelect
                v-model="linkedForms[acct.key].account"
                :groups="coaGrouped"
                value-key="id"
                label-key="account_name"
                :search-keys="['account_number', 'account_name']"
                placeholder="— Pilih akun —"
              />
            </div>
          </div>
        </div>
        <div class="flex justify-end">
          <button @click="saveLinked" :disabled="savingLinked" class="btn-primary text-sm">
            {{ savingLinked ? 'Menyimpan...' : 'Save Linked Accounts' }}
          </button>
        </div>
      </div>

      <!-- Tab: Terms -->
      <div v-show="activeTab === 'terms' && isEdit" class="p-6 max-w-md space-y-4">
        <div>
          <label class="form-label">Payment is Due</label>
          <select v-model="termsForm.payment_due" class="form-input">
            <option value="tanpa_cicilan">Tanpa Cicilan</option>
            <option value="net_30">Net 30</option>
            <option value="net_60">Net 60</option>
            <option value="cod">COD</option>
          </select>
        </div>
        <div>
          <label class="form-label">Balance Due Days</label>
          <input v-model="termsForm.balance_due_days" type="number" class="form-input" />
        </div>
        <div>
          <label class="form-label">Tax Code</label>
          <select v-model="termsForm.tax_code" class="form-input">
            <option value="pph_23_45">PPh 23 Rate 4.5 %</option>
            <option value="pph_23_2">PPh 23 Rate 2 %</option>
            <option value="pph_23_15">PPh 23 Rate 1.5 %</option>
            <option value="non">Non PPh</option>
          </select>
        </div>
        <div>
          <label class="form-label">Credit Limit (IDR)</label>
          <input v-model="termsForm.credit_limit" type="number" step="0.01" class="form-input" />
        </div>
        <label class="flex items-center gap-2 text-sm">
          <input type="checkbox" v-model="termsForm.use_vendor_tax_code" /> Use Vendor Tax Code
        </label>
        <div class="flex justify-end">
          <button @click="saveTerms" :disabled="savingTerms" class="btn-primary text-sm">
            {{ savingTerms ? 'Menyimpan...' : 'Save Terms' }}
          </button>
        </div>
      </div>

      <!-- Tab: Contact Person -->
      <div v-show="activeTab === 'contacts' && isEdit" class="p-6">
        <div class="flex justify-end mb-3">
          <button @click="openContactModal(null)" class="text-xs bg-green-600 text-white px-3 py-1.5 rounded-lg">+ Add Contact</button>
        </div>
        <table class="w-full text-sm border border-gray-200 rounded-lg overflow-hidden">
          <thead class="bg-gray-50 text-xs text-gray-500 uppercase">
            <tr>
              <th class="px-3 py-2 text-left">Name</th>
              <th class="px-3 py-2 text-left">Job Title</th>
              <th class="px-3 py-2 text-left">Email</th>
              <th class="px-3 py-2 text-left">Phone</th>
              <th class="px-3 py-2"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="!contacts.length">
              <td colspan="5" class="text-center py-6 text-gray-400">Belum ada contact person</td>
            </tr>
            <tr v-for="c in contacts" :key="c.id || c._tmp" class="border-t border-gray-100">
              <td class="px-3 py-2">{{ c.full_name || `${c.first_name} ${c.last_name}`.trim() }}</td>
              <td class="px-3 py-2">{{ c.job_title }}</td>
              <td class="px-3 py-2">{{ c.email }}</td>
              <td class="px-3 py-2">{{ c.phone || c.mobile_phone }}</td>
              <td class="px-3 py-2 text-right">
                <button @click="openContactModal(c)" class="text-blue-600 text-xs mr-2">Edit</button>
                <button @click="removeContact(c)" class="text-red-500 text-xs">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Footer (main/financial/legal tabs) -->
      <div v-if="['main','financial','legal'].includes(activeTab)" class="px-6 py-4 border-t flex justify-end gap-3 bg-gray-50 rounded-b-xl">
        <button @click="$emit('close')" class="btn-secondary text-sm">Close</button>
        <button @click="submit" :disabled="saving" class="btn-primary text-sm">
          {{ saving ? 'Menyimpan...' : (isEdit ? 'Update' : 'Save') }}
        </button>
      </div>
    </div>

    <!-- Contact sub-modal -->
    <VendorContactFormModal
      v-if="contactModal.show"
      :contact="contactModal.data"
      @close="contactModal.show = false"
      @save="saveContact"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import Swal from 'sweetalert2'
import { usePurchaseStore } from '../../stores/purchase.js'
import { useAccountingStore } from '../../stores/accounting.js'
import { useOrganizationStore } from '../../stores/organization.js'
import SearchableSelect from '../SearchableSelect.vue'
import VendorContactFormModal from './VendorContactFormModal.vue'

const props = defineProps({ vendor: { type: Object, default: null } })
const emit = defineEmits(['close', 'saved'])

const store = usePurchaseStore()
const accStore = useAccountingStore()
const orgStore = useOrganizationStore()

const activeTab = ref('main')
const saving = ref(false)
const savingLinked = ref(false)
const savingTerms = ref(false)
const errors = ref({})

const isEdit = computed(() => !!props.vendor?.id)
const deptList = computed(() => orgStore.departmentList)

const tabs = [
  { key: 'main', label: 'Data Utama', requiresEdit: false },
  { key: 'financial', label: 'Financial & Bank', requiresEdit: false },
  { key: 'legal', label: 'Legalitas', requiresEdit: false },
  { key: 'linked', label: 'Linked Accounts', requiresEdit: true },
  { key: 'terms', label: 'Terms', requiresEdit: true },
  { key: 'contacts', label: 'Contact Person', requiresEdit: true },
]

const titles = ['PT', 'CV', 'UD', 'Firma', 'Mr', 'Mrs']
const banks = ['BCA', 'Mandiri', 'BNI', 'BRI', 'CIMB Niaga', 'Permata', 'Danamon', 'Lainnya']
const currencies = ['all', 'IDR', 'USD', 'EUR', 'SGD']

const companyFlags = [
  { key: 'item_type_asset', label: 'Asset' },
  { key: 'item_type_fg', label: 'Finished Goods' },
  { key: 'item_type_rm', label: 'Raw Material' },
  { key: 'item_type_supplies', label: 'Supplies' },
  { key: 'item_type_wip', label: 'WIP' },
]
const vendorFlags = [
  { key: 'item_type_maintenance', label: 'Maintenance' },
  { key: 'item_type_subcont', label: 'SubCont' },
]

const linkedTypes = [
  { key: 'ap', label: 'Account for Tracking Payables (A/P)' },
  { key: 'deposit', label: 'Account for Tracking Vendor Deposit' },
  { key: 'down_payment', label: 'Account for Tracking Vendor Down Payment' },
]

const defaultForm = () => ({
  title: '', name: '', category: null, department: null, variety: '',
  tax_number: '', nppkp: '', is_leasing: false,
  email: '', alternative_email: '', website: '',
  address_1: '', address_2: '', country: 'Indonesia', state: '', city: '', zip_code: '',
  area_code: 'other', phone_1: '', phone_2: '', fax: '',
  currency: 'IDR', tolerance_difference: 0, deposit: 0,
  bank_name: '', bank_branch: '', bank_city: '', bank_account_number: '', bank_account_name: '',
  term_and_condition: '',
  company_financial_capability: 0, kriteria_usaha: 'usaha_kecil',
  notary_name: '', letter_no_date: '', notary_name_2: '', letter_no_date_2: '', letter_of_endorsement: '',
  no_siup: '', expired_date_siup: null, no_tdp: '', expired_date_tdp: null,
  no_sk_domisili: '', expired_date_sk_domisili: null, no_siujk: '', expired_date_siujk: null,
  item_type_asset: true, item_type_fg: true, item_type_rm: true, item_type_supplies: true, item_type_wip: true,
  item_type_maintenance: true, item_type_subcont: true,
  group: null, is_sister_company: false, status: 'open',
})

const form = ref(defaultForm())
const linkedForms = ref(Object.fromEntries(linkedTypes.map(t => [t.key, { currency_scope: 'all', account: null }])))
const termsForm = ref({ payment_due: 'tanpa_cicilan', balance_due_days: 0, tax_code: 'non', credit_limit: 0, use_vendor_tax_code: false })
const contacts = ref([])
const contactModal = ref({ show: false, data: null })

const coaGrouped = computed(() => {
  const flat = (accStore.coaFlat || []).filter(a => a.is_postable && a.is_active)
  const groups = {}
  flat.forEach(acc => {
    const g = acc.account_group_name || 'Lainnya'
    if (!groups[g]) groups[g] = []
    groups[g].push(acc)
  })
  return Object.entries(groups).map(([label, options]) => ({ label, options }))
})

function switchTab(key) {
  const tab = tabs.find(t => t.key === key)
  if (tab?.requiresEdit && !isEdit.value) return
  activeTab.value = key
}

function buildPayload() {
  const p = { ...form.value }
  if (!p.category) p.category = null
  if (!p.group) p.group = null
  if (!p.department) p.department = null
  ;['expired_date_siup','expired_date_tdp','expired_date_sk_domisili','expired_date_siujk'].forEach(k => {
    if (!p[k]) p[k] = null
  })
  return p
}

function formatErrors(data) {
  if (typeof data?.detail === 'string') return data.detail
  return Object.entries(data || {}).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`).join('\n')
}

async function loadDetail() {
  if (!props.vendor?.id) return
  await store.fetchVendor(props.vendor.id)
  const v = store.currentVendor
  Object.keys(defaultForm()).forEach(k => { if (k in v) form.value[k] = v[k] })
  form.value.code = v.code
  if (v.linked_accounts?.length) {
    v.linked_accounts.forEach(la => {
      if (linkedForms.value[la.account_type]) {
        linkedForms.value[la.account_type] = { currency_scope: la.currency_scope, account: la.account }
      }
    })
  }
  if (v.terms) Object.assign(termsForm.value, v.terms)
  contacts.value = v.contact_persons ? [...v.contact_persons] : []
}

onMounted(async () => {
  await Promise.all([
    store.fetchCategories(),
    store.fetchGroups(),
    orgStore.fetchDepartments(),
    accStore.fetchCoaFlat({ postable: 'true', active: 'true' }),
  ])
  if (isEdit.value) await loadDetail()
})

async function submit() {
  errors.value = {}
  saving.value = true
  try {
    if (isEdit.value) {
      await store.updateVendor(props.vendor.id, buildPayload())
    } else {
      if (!form.value.category) {
        Swal.fire({ icon: 'warning', title: 'Vendor Category wajib dipilih', text: 'Kode vendor di-generate dari kategori.' })
        saving.value = false
        return
      }
      await store.createVendor(buildPayload())
    }
    await Swal.fire({ icon: 'success', title: 'Berhasil disimpan', timer: 1500, showConfirmButton: false })
    emit('saved')
  } catch (e) {
    if (e.response?.data) errors.value = e.response.data
    Swal.fire({ icon: 'error', title: 'Gagal simpan', text: formatErrors(e.response?.data) || e.message })
  } finally {
    saving.value = false
  }
}

async function saveLinked() {
  savingLinked.value = true
  try {
    const payload = linkedTypes.filter(t => linkedForms.value[t.key].account).map(t => ({
      account_type: t.key,
      currency_scope: linkedForms.value[t.key].currency_scope,
      account: linkedForms.value[t.key].account,
    }))
    await store.saveLinkedAccounts(props.vendor.id, payload)
    await Swal.fire({ icon: 'success', title: 'Linked accounts disimpan', timer: 1200, showConfirmButton: false })
  } catch (e) {
    Swal.fire({ icon: 'error', title: 'Gagal', text: e.message })
  } finally {
    savingLinked.value = false
  }
}

async function saveTerms() {
  savingTerms.value = true
  try {
    await store.saveTerms(props.vendor.id, termsForm.value)
    await Swal.fire({ icon: 'success', title: 'Terms disimpan', timer: 1200, showConfirmButton: false })
  } catch (e) {
    Swal.fire({ icon: 'error', title: 'Gagal', text: e.message })
  } finally {
    savingTerms.value = false
  }
}

function openContactModal(contact) {
  contactModal.value = { show: true, data: contact ? { ...contact } : null }
}

async function saveContact(data) {
  try {
    if (data.id) {
      await store.updateContactPerson(props.vendor.id, data.id, data)
    } else {
      await store.createContactPerson(props.vendor.id, data)
    }
    contactModal.value.show = false
    await loadDetail()
  } catch (e) {
    Swal.fire({ icon: 'error', title: 'Gagal simpan contact', text: formatErrors(e.response?.data) })
  }
}

async function removeContact(c) {
  if (!c.id) return
  const r = await Swal.fire({ title: 'Hapus contact?', icon: 'warning', showCancelButton: true })
  if (!r.isConfirmed) return
  await store.deleteContactPerson(props.vendor.id, c.id)
  await loadDetail()
}
</script>

<style scoped>
@reference "../../style.css";
.form-label { @apply block text-sm font-medium text-gray-700 mb-1; }
.form-input { @apply w-full border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-bfs-gold; }
.form-error { @apply text-red-500 text-xs mt-1; }
.btn-primary { @apply px-4 py-2 bg-bfs-gold hover:bg-bfs-gold-dark text-white rounded-lg font-medium disabled:opacity-60; }
.btn-secondary { @apply px-4 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50; }
</style>
