<template>
  <div class="fixed inset-0 z-50 flex items-start justify-center bg-black/40 overflow-y-auto py-8">
    <div class="bg-white rounded-lg shadow-xl w-full max-w-4xl mx-4">

      <!-- Header -->
      <div class="bg-blue-700 text-white px-6 py-3 rounded-t-lg flex justify-between items-center">
        <span class="font-semibold text-sm">
          Sales | Customer | {{ isEdit ? 'Update Customer' : 'Add Customer' }}
        </span>
        <button @click="$emit('close')" class="text-white hover:text-gray-200 text-lg">✕</button>
      </div>

      <!-- Tabs -->
      <div class="flex border-b border-gray-200 px-6 pt-4 gap-4">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          @click="switchTab(tab.key)"
          :disabled="tab.requiresEdit && !isEdit"
          :class="[
            'pb-2 text-sm font-medium border-b-2 transition-colors',
            activeTab === tab.key
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700',
            tab.requiresEdit && !isEdit ? 'opacity-40 cursor-not-allowed' : '',
          ]"
        >
          {{ tab.label }}
        </button>
      </div>

      <p
        v-if="!isEdit && activeTab !== 'main'"
        class="mx-6 mt-4 text-sm text-amber-700 bg-amber-50 border border-amber-200 rounded-lg px-4 py-2"
      >
        Simpan data utama customer terlebih dahulu sebelum mengatur tab ini.
      </p>

      <!-- Tab: Data Utama -->
      <div v-show="activeTab === 'main'" class="p-6 grid grid-cols-2 gap-x-8 gap-y-4">

        <div v-if="isEdit">
          <label class="form-label">Code</label>
          <input :value="form.code" disabled class="form-input bg-gray-50" />
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
          <label class="form-label">Customer Category</label>
          <select v-model="form.category" class="form-input">
            <option :value="null">--- Pilih ---</option>
            <option v-for="c in store.categories" :key="c.id" :value="c.id">
              {{ c.code }} - {{ c.name }}
            </option>
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
          <label class="form-label">Website</label>
          <input v-model="form.website" class="form-input" />
        </div>

        <div class="col-span-2">
          <label class="form-label">Address 1 <span class="text-red-500">*</span></label>
          <textarea v-model="form.address_1" rows="3" class="form-input" />
        </div>

        <div class="col-span-2">
          <label class="form-label">Address 2</label>
          <textarea v-model="form.address_2" rows="3" class="form-input" />
        </div>

        <div>
          <label class="form-label">Country</label>
          <input v-model="form.country" class="form-input" />
        </div>

        <div>
          <label class="form-label">State</label>
          <input v-model="form.state" class="form-input" />
        </div>

        <div>
          <label class="form-label">City <span class="text-red-500">*</span></label>
          <input v-model="form.city" class="form-input" />
          <p v-if="errors.city" class="form-error">{{ errors.city }}</p>
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
          <p v-if="errors.phone_1" class="form-error">{{ errors.phone_1 }}</p>
        </div>

        <div>
          <label class="form-label">Phone 2</label>
          <input v-model="form.phone_2" class="form-input" />
        </div>

        <div>
          <label class="form-label">Fax</label>
          <input v-model="form.fax" class="form-input" />
        </div>

        <div>
          <label class="form-label">Currency <span class="text-red-500">*</span></label>
          <select v-model="form.currency" class="form-input">
            <option value="IDR">IDR</option>
            <option value="USD">USD</option>
            <option value="EUR">EUR</option>
            <option value="SGD">SGD</option>
          </select>
        </div>

        <div>
          <label class="form-label">Tolerance Difference (%)</label>
          <input v-model="form.tolerance_difference" type="number" step="0.01" class="form-input" />
        </div>

        <div>
          <label class="form-label">Credit Limit (IDR)</label>
          <input v-model="form.credit_limit" type="number" step="0.01" class="form-input" />
        </div>

        <div>
          <label class="form-label">Group</label>
          <select v-model="form.group" class="form-input">
            <option :value="null">None</option>
            <option v-for="g in store.groups" :key="g.id" :value="g.id">{{ g.name }}</option>
          </select>
        </div>

        <div>
          <label class="form-label">Customer Status</label>
          <select v-model="form.status" class="form-input">
            <option value="open">Open</option>
            <option value="closed">Closed</option>
            <option value="hold">Hold</option>
          </select>
        </div>

        <!-- Flags -->
        <div class="col-span-2 border-t pt-4">
          <p class="text-xs text-gray-500 mb-2 font-medium uppercase">Item Type Flags</p>
          <div class="flex flex-wrap gap-4">
            <label v-for="flag in itemFlags" :key="flag.key" class="flex items-center gap-2 text-sm">
              <input type="checkbox" v-model="form[flag.key]" class="rounded" />
              {{ flag.label }}
            </label>
          </div>
        </div>

        <div class="col-span-2 flex gap-6">
          <label class="flex items-center gap-2 text-sm">
            <input type="checkbox" v-model="form.is_kawasan_berikat" class="rounded" />
            Kawasan Berikat
          </label>
          <label class="flex items-center gap-2 text-sm">
            <input type="checkbox" v-model="form.is_sister_company" class="rounded" />
            Is Sister Company
          </label>
        </div>

      </div>

      <!-- Tab: Linked Accounts -->
      <div v-show="activeTab === 'linked' && isEdit" class="p-6 space-y-6">
        <div
          v-for="acct in linkedAccountTypes"
          :key="acct.key"
          class="border border-gray-200 rounded p-4"
        >
          <p class="text-sm font-semibold text-gray-700 mb-3">{{ acct.label }}</p>
          <div class="flex items-center gap-4 flex-wrap">
            <div class="flex items-center gap-2">
              <span class="text-xs text-gray-500">Currency:</span>
              <label v-for="cur in currencies" :key="cur" class="flex items-center gap-1 text-sm">
                <input
                  type="radio"
                  :name="`cur_${acct.key}`"
                  :value="cur"
                  v-model="linkedForms[acct.key].currency_scope"
                />
                {{ cur }}
              </label>
            </div>
            <div class="flex-1 min-w-48">
              <SearchableSelect
                v-model="linkedForms[acct.key].account"
                :groups="coaGrouped"
                value-key="id"
                label-key="account_name"
                :search-keys="['account_number', 'account_name']"
                placeholder="— Cari account... —"
                search-placeholder="Ketik nomor atau nama akun..."
              />
            </div>
          </div>
        </div>

        <div class="flex justify-end">
          <button
            @click="saveLinkedAccounts"
            :disabled="savingLinked"
            class="bg-blue-600 text-white text-sm px-5 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
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
            <option value="ppn_11">PPN 11 %</option>
            <option value="ppn_0">PPN 0 %</option>
            <option value="non">Non PPN</option>
          </select>
        </div>
        <label class="flex items-center gap-2 text-sm">
          <input type="checkbox" v-model="termsForm.use_customer_tax_code" />
          Use Customer Tax's Code
        </label>
        <div class="flex justify-end pt-2">
          <button
            @click="saveTerms"
            :disabled="savingTerms"
            class="bg-blue-600 text-white text-sm px-5 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {{ savingTerms ? 'Menyimpan...' : 'Save Terms' }}
          </button>
        </div>
      </div>

      <!-- Tab: Contact Person -->
      <div v-show="activeTab === 'contacts' && isEdit" class="p-6">
        <div class="flex justify-end mb-3">
          <button
            @click="addContactRow"
            class="bg-green-600 text-white text-xs px-4 py-1.5 rounded hover:bg-green-700"
          >
            + Add Contact Person
          </button>
        </div>
        <table class="min-w-full text-sm border border-gray-200 rounded">
          <thead class="bg-gray-100 text-xs text-gray-600 uppercase">
            <tr>
              <th class="px-3 py-2 text-left">Name</th>
              <th class="px-3 py-2 text-left">Home Address</th>
              <th class="px-3 py-2 text-left">Email</th>
              <th class="px-3 py-2 text-left">Phone</th>
              <th class="px-3 py-2"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="!contacts.length">
              <td colspan="5" class="text-center py-4 text-gray-400">Belum ada contact person</td>
            </tr>
            <tr
              v-for="(c, i) in contacts"
              :key="i"
              class="border-t border-gray-100"
            >
              <td class="px-3 py-2">
                <input v-model="c.name" class="form-input text-xs" />
              </td>
              <td class="px-3 py-2">
                <input v-model="c.home_address" class="form-input text-xs" />
              </td>
              <td class="px-3 py-2">
                <input v-model="c.email" class="form-input text-xs" />
              </td>
              <td class="px-3 py-2">
                <input v-model="c.home_phone" class="form-input text-xs" />
              </td>
              <td class="px-3 py-2">
                <button @click="removeContact(i, c)" class="text-red-500 text-xs hover:underline">
                  Delete
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        <div class="flex justify-end mt-3">
          <button
            @click="saveContacts"
            :disabled="savingContacts"
            class="bg-blue-600 text-white text-sm px-5 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {{ savingContacts ? 'Menyimpan...' : 'Save Contacts' }}
          </button>
        </div>
      </div>

      <!-- Footer actions (tab main) -->
      <div v-if="activeTab === 'main'" class="px-6 py-4 border-t flex justify-end gap-3">
        <button
          @click="$emit('close')"
          class="text-sm px-4 py-2 rounded border border-gray-300 hover:bg-gray-50"
        >
          Close
        </button>
        <button
          @click="submit"
          :disabled="saving"
          class="bg-blue-600 text-white text-sm px-5 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {{ saving ? 'Menyimpan...' : (isEdit ? 'Update' : 'Save') }}
        </button>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import Swal from 'sweetalert2'
import { useSalesStore } from '../../stores/sales.js'
import { useAccountingStore } from '../../stores/accounting.js'
import SearchableSelect from '../../components/SearchableSelect.vue'

const props = defineProps({
  customer: { type: Object, default: null },
})
const emit = defineEmits(['close', 'saved'])

const store      = useSalesStore()
const accStore   = useAccountingStore()

const activeTab  = ref('main')
const saving     = ref(false)
const savingLinked   = ref(false)
const savingTerms    = ref(false)
const savingContacts = ref(false)
const errors     = ref({})

const isEdit = computed(() => !!props.customer?.id)

const tabs = [
  { key: 'main',     label: 'Data Utama',      requiresEdit: false },
  { key: 'linked',   label: 'Linked Accounts', requiresEdit: true },
  { key: 'terms',    label: 'Terms',           requiresEdit: true },
  { key: 'contacts', label: 'Contact Person',  requiresEdit: true },
]

const titles = ['PT', 'CV', 'KAP', 'KJPP', 'FIRMA', 'PD', 'RS', 'RSU', 'TK', 'TOKO', 'UD', 'Yayasan', 'Appraisal']

const itemFlags = [
  { key: 'item_type_asset',    label: 'Asset' },
  { key: 'item_type_fg',       label: 'Finished Goods' },
  { key: 'item_type_rm',       label: 'Raw Material' },
  { key: 'item_type_supplies', label: 'Supplies' },
  { key: 'item_type_wip',      label: 'WIP' },
]

const linkedAccountTypes = [
  { key: 'ar_invoice',    label: 'Account for Tracking Receivables that will be invoiced (A/R to be invoiced)' },
  { key: 'ar',            label: 'Account for Tracking Receivables (A/R)' },
  { key: 'deposit',       label: 'Account for Tracking Customer Deposit' },
  { key: 'down_payment',  label: 'Account for Tracking Customer Down Payment' },
]

const currencies = ['all', 'USD', 'IDR', 'EUR', 'SGD']

// ── Form state ─────────────────────────────────────────────────

const defaultForm = () => ({
  title: '', name: '', category: null,
  tax_number: '', nppkp: '',
  email: '', website: '',
  address_1: '', address_2: '',
  country: 'Indonesia', state: '', city: '', zip_code: '',
  area_code: 'other',
  phone_1: '', phone_2: '', fax: '',
  currency: 'IDR', default_price_group: '',
  tolerance_difference: 0, deposit: 0, credit_limit: 0,
  is_kawasan_berikat: false, is_sister_company: false,
  item_type_asset: true, item_type_fg: true,
  item_type_rm: true, item_type_supplies: true, item_type_wip: true,
  group: null, status: 'open',
})

const form = ref(defaultForm())

const defaultLinked = () => Object.fromEntries(
  linkedAccountTypes.map(t => [t.key, { currency_scope: 'all', account: null }])
)
const linkedForms = ref(defaultLinked())

const defaultTerms = () => ({
  payment_due: 'tanpa_cicilan',
  balance_due_days: 0,
  tax_code: 'ppn_11',
  use_customer_tax_code: false,
})
const termsForm = ref(defaultTerms())

const contacts = ref([])

const coaGrouped = computed(() => {
  const flat = (accStore.coaFlat || []).filter(a => a.is_postable && a.is_active)
  const groups = {}
  flat.forEach(acc => {
    const gname = acc.account_group_name || 'Lainnya'
    if (!groups[gname]) groups[gname] = []
    groups[gname].push(acc)
  })
  return Object.entries(groups).map(([label, options]) => ({ label, options }))
})

function switchTab(key) {
  const tab = tabs.find(t => t.key === key)
  if (tab?.requiresEdit && !isEdit.value) return
  activeTab.value = key
}

// ── Load data saat edit ────────────────────────────────────────

async function loadDetail() {
  if (!props.customer?.id) return
  await store.fetchCustomer(props.customer.id)
  const c = store.currentCustomer

  Object.keys(defaultForm()).forEach(k => {
    if (k in c) form.value[k] = c[k]
  })
  form.value.code = c.code

  // linked accounts
  if (c.linked_accounts?.length) {
    c.linked_accounts.forEach(la => {
      if (linkedForms.value[la.account_type]) {
        linkedForms.value[la.account_type] = {
          currency_scope: la.currency_scope,
          account: la.account,
        }
      }
    })
  }

  // terms
  if (c.terms) {
    Object.assign(termsForm.value, c.terms)
  }

  // contacts
  contacts.value = c.contact_persons
    ? c.contact_persons.map(cp => ({ ...cp }))
    : []
}

onMounted(async () => {
  await Promise.all([
    store.fetchCategories(),
    store.fetchGroups(),
    accStore.fetchCoaFlat({ postable: 'true', active: 'true' }),
  ])
  if (isEdit.value) await loadDetail()
})

// ── Submit main form ───────────────────────────────────────────

function buildPayload() {
  const payload = { ...form.value }
  // FK kosong → null (bukan string kosong)
  if (!payload.category) payload.category = null
  if (!payload.group) payload.group = null
  return payload
}

function formatApiErrors(data) {
  if (!data || typeof data !== 'object') return 'Gagal menyimpan data.'
  if (typeof data.detail === 'string') return data.detail
  return Object.entries(data)
    .map(([field, msgs]) => {
      const text = Array.isArray(msgs) ? msgs.join(', ') : String(msgs)
      return `${field}: ${text}`
    })
    .join('\n')
}

async function submit() {
  errors.value = {}
  saving.value = true
  try {
    const payload = buildPayload()
    if (isEdit.value) {
      await store.updateCustomer(props.customer.id, payload)
    } else {
      await store.createCustomer(payload)
    }
    await Swal.fire({ icon: 'success', title: 'Berhasil disimpan', timer: 1500, showConfirmButton: false })
    emit('saved')
  } catch (e) {
    if (e.response?.data) {
      errors.value = e.response.data
      Swal.fire({ icon: 'error', title: 'Gagal simpan', text: formatApiErrors(e.response.data) })
    } else {
      Swal.fire({ icon: 'error', title: 'Gagal simpan', text: e.message })
    }
  } finally {
    saving.value = false
  }
}

// ── Linked accounts ────────────────────────────────────────────

async function saveLinkedAccounts() {
  if (!isEdit.value) return
  savingLinked.value = true
  try {
    const payload = linkedAccountTypes
      .filter(t => linkedForms.value[t.key].account)
      .map(t => ({
        account_type:   t.key,
        currency_scope: linkedForms.value[t.key].currency_scope,
        account:        linkedForms.value[t.key].account,
      }))
    await store.saveLinkedAccounts(props.customer.id, payload)
    await Swal.fire({ icon: 'success', title: 'Linked accounts disimpan', timer: 1200, showConfirmButton: false })
  } catch (e) {
    Swal.fire({ icon: 'error', title: 'Gagal', text: e.message })
  } finally {
    savingLinked.value = false
  }
}

// ── Terms ──────────────────────────────────────────────────────

async function saveTerms() {
  if (!isEdit.value) return
  savingTerms.value = true
  try {
    await store.saveTerms(props.customer.id, termsForm.value)
    await Swal.fire({ icon: 'success', title: 'Terms disimpan', timer: 1200, showConfirmButton: false })
  } catch (e) {
    Swal.fire({ icon: 'error', title: 'Gagal', text: e.message })
  } finally {
    savingTerms.value = false
  }
}

// ── Contact persons ────────────────────────────────────────────

function addContactRow() {
  contacts.value.push({ name: '', home_address: '', email: '', home_phone: '' })
}

async function removeContact(index, contact) {
  if (contact.id) {
    await store.deleteContactPerson(props.customer.id, contact.id)
  }
  contacts.value.splice(index, 1)
}

async function saveContacts() {
  if (!isEdit.value) return
  savingContacts.value = true
  try {
    for (const c of contacts.value) {
      if (c.id) {
        await store.updateContactPerson(props.customer.id, c.id, c)
      } else {
        await store.createContactPerson(props.customer.id, c)
      }
    }
    await Swal.fire({ icon: 'success', title: 'Contact persons disimpan', timer: 1200, showConfirmButton: false })
    await loadDetail()
  } catch (e) {
    Swal.fire({ icon: 'error', title: 'Gagal', text: e.message })
  } finally {
    savingContacts.value = false
  }
}
</script>

<style scoped>
@reference "../../style.css";
.form-label {
  @apply block text-sm font-medium text-gray-700 mb-1;
}
.form-input {
  @apply w-full border border-gray-300 rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500;
}
.form-error {
  @apply text-red-500 text-xs mt-1;
}
</style>