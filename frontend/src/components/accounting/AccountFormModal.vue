<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="show"
        class="fixed inset-0 z-50 overflow-y-auto"
        @click.self="$emit('close')"
      >
        <!-- Overlay -->
        <div class="fixed inset-0 bg-black/40" @click="$emit('close')" />

        <!-- Scroll container — padding atas bawah biar ada ruang -->
        <div class="flex min-h-full items-start justify-center p-4 py-8">
          <div
            class="relative bg-white rounded-2xl shadow-2xl w-full max-w-lg z-10"
            @click.stop
          >

            <!-- Header -->
            <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
              <div>
                <h3 class="text-base font-semibold text-gray-800">
                  {{ mode === 'add' ? 'New Account' : 'Edit Account' }}
                </h3>
                <p v-if="parentAccount" class="text-xs text-gray-400 mt-0.5">
                  Parent: {{ parentAccount.account_number }} {{ parentAccount.account_name }}
                </p>
              </div>
              <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600 transition-colors">
                <X class="w-5 h-5" />
              </button>
            </div>

            <!-- Alert error dari backend -->
            <div v-if="serverError" class="mx-6 mt-4 px-4 py-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
              <AlertCircle class="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
              <p class="text-sm text-red-600">{{ serverError }}</p>
            </div>

            <!-- Account Type Selector -->
            <div class="px-6 pt-4 pb-3 border-b border-gray-100 space-y-1.5">
              <label
                v-for="t in accountTypes"
                :key="t.value"
                class="flex items-center gap-2.5 cursor-pointer"
              >
                <input
                  type="radio"
                  :value="t.value"
                  v-model="form.account_type"
                  class="w-3.5 h-3.5 accent-yellow-500"
                />
                <span class="text-sm" :class="form.account_type === t.value ? 'text-gray-800 font-medium' : 'text-gray-500'">
                  {{ t.label }}
                </span>
              </label>
            </div>

            <!-- Form Fields — tidak ada max-h, biarkan konten natural -->
            <div class="px-6 py-4 space-y-3">

              <!-- Language -->
              <FormField label="Language">
                <select v-model="form.language" class="form-input">
                  <option v-for="l in choices?.languages" :key="l.value" :value="l.value">
                    {{ l.label }}
                  </option>
                </select>
              </FormField>

              <!-- Account Group -->
              <FormField label="Account Group" required>
                <select
                  v-model="form.account_group"
                  class="form-input"
                  :class="{ 'border-red-300': errors.account_group }"
                >
                  <option :value="null">— Pilih Group —</option>
                  <option v-for="g in accountGroups" :key="g.id" :value="g.id">
                    [{{ g.number_prefix }}] {{ g.name }}
                  </option>
                </select>
                <p v-if="errors.account_group" class="mt-1 text-xs text-red-500 flex items-center gap-1">
                  <AlertCircle class="w-3 h-3 shrink-0" />{{ errors.account_group }}
                </p>
              </FormField>

              <!-- Account Number -->
              <FormField label="Account Number" required>
                <div class="flex items-center">
                  <span
                    class="px-3 py-2 text-sm border border-gray-200 border-r-0 rounded-l-lg font-mono shrink-0"
                    :class="selectedGroup ? 'bg-gray-100 text-gray-700' : 'bg-gray-50 text-gray-400'"
                  >
                    {{ selectedGroup?.number_prefix ?? '—' }}
                  </span>
                  <input
                    v-model="accountSuffix"
                    type="text"
                    class="form-input rounded-l-none font-mono"
                    :class="{ 'border-red-300': errors.account_number }"
                    :placeholder="suffixPlaceholder"
                    :disabled="!form.account_group"
                  />
                </div>
                <p class="mt-1 text-xs text-gray-400">
                  Nomor lengkap:
                  <span class="font-mono font-semibold text-gray-700">{{ fullAccountNumber || '—' }}</span>
                </p>
                <p v-if="errors.account_number" class="mt-1 text-xs text-red-500 flex items-center gap-1">
                  <AlertCircle class="w-3 h-3 shrink-0" />{{ errors.account_number }}
                </p>
              </FormField>

              <!-- Account Name -->
              <FormField label="Account Name" required>
                <input
                  v-model="form.account_name"
                  type="text"
                  class="form-input"
                  :class="{ 'border-red-300': errors.account_name }"
                  placeholder="e.g. Kas Besar"
                />
                <p v-if="errors.account_name" class="mt-1 text-xs text-red-500 flex items-center gap-1">
                  <AlertCircle class="w-3 h-3 shrink-0" />{{ errors.account_name }}
                </p>
              </FormField>

              <!-- Parent Account — custom dropdown -->
              <FormField label="Parent Account">
                <div class="relative" ref="parentDropdownRef">
                  <button
                    type="button"
                    @click="parentDropdownOpen = !parentDropdownOpen"
                    class="form-input text-left flex items-center justify-between"
                    :disabled="!form.account_group"
                  >
                    <span :class="selectedParentLabel ? 'text-gray-800' : 'text-gray-400'">
                      {{ selectedParentLabel || (form.account_group ? '— Root (tanpa parent) —' : 'Pilih group dulu') }}
                    </span>
                    <ChevronDown class="w-4 h-4 text-gray-400 shrink-0" />
                  </button>

                  <div
                    v-if="parentDropdownOpen && form.account_group"
                    class="absolute z-50 mt-1 w-full bg-white border border-gray-200 rounded-lg shadow-lg max-h-48 overflow-y-auto"
                  >
                    <div
                      @click="selectParent(null)"
                      class="px-3 py-2 text-sm cursor-pointer hover:bg-gray-50"
                      :class="form.parent === null ? 'text-bfs-gold font-medium bg-yellow-50' : 'text-gray-600'"
                    >
                      — Root (tanpa parent) —
                    </div>
                    <div
                      v-for="acc in filteredHeaderAccounts"
                      :key="acc.id"
                      @click="acc.id !== editId && selectParent(acc.id)"
                      class="px-3 py-2 text-sm cursor-pointer hover:bg-gray-50"
                      :class="{
                        'text-bfs-gold font-medium bg-yellow-50': form.parent === acc.id,
                        'text-gray-400 cursor-not-allowed': acc.id === editId,
                        'text-gray-700': acc.id !== editId && form.parent !== acc.id,
                      }"
                      :style="{ paddingLeft: `${12 + acc.level * 16}px` }"
                    >
                      {{ acc.account_number }} {{ acc.account_name }}
                    </div>
                    <div v-if="filteredHeaderAccounts.length === 0" class="px-3 py-4 text-sm text-gray-400 text-center">
                      Tidak ada header account di group ini.
                    </div>
                  </div>
                </div>
                <p class="mt-1 text-xs text-gray-400">
                  {{ form.account_group ? 'Opsional. Hanya header accounts dalam group yang dipilih.' : 'Pilih group terlebih dahulu.' }}
                </p>
              </FormField>

              <!-- Default Position -->
              <FormField label="Default Position">
                <select v-model="form.default_position" class="form-input">
                  <option v-for="p in choices?.default_positions" :key="p.value" :value="p.value">
                    {{ p.label }}
                  </option>
                </select>
              </FormField>

              <!-- Currency -->
              <FormField label="Currency">
                <select v-model="form.currency" class="form-input">
                  <option v-for="c in choices?.currencies" :key="c.value" :value="c.value">
                    {{ c.label }}
                  </option>
                </select>
              </FormField>

              <!-- Bank Type -->
              <FormField v-if="form.account_type === 'DETAIL_BANK'" label="Bank Type" required>
                <select
                  v-model="form.bank_type"
                  class="form-input"
                  :class="{ 'border-red-300': errors.bank_type }"
                >
                  <option :value="null">— Pilih Bank Type —</option>
                  <option v-for="b in choices?.bank_types" :key="b.value" :value="b.value">
                    {{ b.label }}
                  </option>
                </select>
                <p v-if="errors.bank_type" class="mt-1 text-xs text-red-500 flex items-center gap-1">
                  <AlertCircle class="w-3 h-3 shrink-0" />{{ errors.bank_type }}
                </p>
              </FormField>

              <!-- Flags -->
              <template v-if="form.account_type !== 'HEADER'">
                <div class="pt-2 space-y-2 border-t border-gray-100">
                  <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide pt-1">Flags</p>
                  <label class="flex items-center gap-2.5 cursor-pointer">
                    <input type="checkbox" v-model="form.is_inter_company" class="w-4 h-4 rounded accent-yellow-500" />
                    <span class="text-sm text-gray-700">Is Inter Company</span>
                  </label>
                  <label class="flex items-center gap-2.5 cursor-pointer">
                    <input type="checkbox" v-model="form.is_cost_component" class="w-4 h-4 rounded accent-yellow-500" />
                    <span class="text-sm text-gray-700">Is Cost Component</span>
                  </label>
                  <label class="flex items-center gap-2.5 cursor-pointer">
                    <input type="checkbox" v-model="form.is_on_duty" class="w-4 h-4 rounded accent-yellow-500" />
                    <span class="text-sm text-gray-700">Is On Duty</span>
                  </label>
                  <label class="flex items-center gap-2.5" :class="isTaxInDisabled ? 'cursor-not-allowed opacity-60' : 'cursor-pointer'">
                    <input type="checkbox" v-model="form.is_tax_in" :disabled="isTaxInDisabled" class="w-4 h-4 rounded accent-yellow-500 disabled:bg-gray-200" />
                    <span class="text-sm text-gray-700">Is Tax In (PPN Masukan)</span>
                  </label>
                </div>
              </template>

            </div>

            <!-- Footer — sticky di bawah konten, bukan fixed -->
            <div class="flex justify-end gap-2 px-6 py-4 border-t border-gray-100 bg-gray-50 rounded-b-2xl">
              <button @click="$emit('close')" class="btn-secondary text-sm">
                Cancel
              </button>
              <button
                @click="handleSubmit"
                :disabled="isSaving"
                class="btn-primary text-sm flex items-center gap-1.5"
              >
                <Loader2 v-if="isSaving" class="w-3.5 h-3.5 animate-spin" />
                <Save v-else class="w-3.5 h-3.5" />
                {{ mode === 'add' ? 'Save' : 'Update' }}
              </button>
            </div>

          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, reactive, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { X, Save, Loader2, AlertCircle, ChevronDown } from 'lucide-vue-next'
import FormField from '../FormField.vue'
import { useAccountingStore } from '../../stores/accounting.js'

const store = useAccountingStore()

const props = defineProps({
  show:           { type: Boolean, required: true },
  mode:           { type: String,  default: 'add' },
  editId:         { type: Number,  default: null },
  initialData:    { type: Object,  default: null },
  parentAccount:  { type: Object,  default: null },
  accountGroups:  { type: Array,   default: () => [] },
  headerAccounts: { type: Array,   default: () => [] },
  choices:        { type: Object,  default: null },
})

const emit = defineEmits(['close', 'saved'])

const accountTypes = [
  { value: 'HEADER',        label: 'Header Account [Non Postable]' },
  { value: 'DETAIL',        label: 'Detail Account [Postable]' },
  { value: 'DETAIL_BANK',   label: 'Detail Bank [Postable]' },
  { value: 'DETAIL_CASH',   label: 'Detail Cash [Postable]' },
  { value: 'DETAIL_CHEQUE', label: 'Detail Cheque Account [Postable]' },
]

// ── State ──────────────────────────────────────────────────────────────────
const isSaving      = ref(false)
const serverError   = ref('')
const errors        = reactive({})
const accountSuffix = ref('')
const isPopulating  = ref(false)
const parentDropdownOpen  = ref(false)
const parentDropdownRef   = ref(null)

const form = reactive({
  account_type:      'DETAIL',
  account_number:    '',
  account_name:      '',
  account_group:     null,
  parent:            null,
  language:          'EN',
  default_position:  'DEBET',
  currency:          'IDR',
  bank_type:         null,
  is_inter_company:  false,
  is_cost_component: false,
  is_on_duty:        false,
  is_tax_in:         false,
  is_active:         true,
})

// ── Computed ───────────────────────────────────────────────────────────────
const selectedGroup = computed(() =>
  props.accountGroups.find(g => g.id === form.account_group) ?? null
)

// Filter header accounts berdasarkan group yang dipilih
const filteredHeaderAccounts = computed(() => {
  if (!form.account_group) return []
  return props.headerAccounts.filter(acc => acc.account_group === form.account_group)
})

const isTaxInDisabled = computed(() => {
  // if current account already has it, it's not disabled (can uncheck)
  if (props.mode === 'edit' && props.initialData?.is_tax_in) return false
  
  // check if any account in the tree has is_tax_in
  let found = false
  const checkNodes = (nodes) => {
    for (const node of nodes) {
      if (node.is_tax_in && node.id !== props.editId) {
        found = true
        return
      }
      if (node.children?.length) checkNodes(node.children)
    }
  }
  
  if (store.coaTree) {
    for (const group of store.coaTree) {
      checkNodes(group.accounts)
      if (found) break
    }
  }
  
  return found
})

const fullAccountNumber = computed(() => {
  const prefix = selectedGroup.value?.number_prefix ?? ''
  const suffix = accountSuffix.value.trim()
  if (!prefix && !suffix) return ''
  if (!prefix) return suffix
  if (!suffix) return prefix
  const sep = suffix.startsWith('.') || suffix.startsWith('-') ? '' : '.'
  return `${prefix}${sep}${suffix}`
})

const suffixPlaceholder = computed(() => {
  const prefix = selectedGroup.value?.number_prefix
  if (!prefix) return 'Pilih group terlebih dahulu'
  return `Lanjutan setelah "${prefix}.", contoh: 11.01`
})

const selectedParentLabel = computed(() => {
  if (form.parent === null) return ''
  const acc = props.headerAccounts.find(a => a.id === form.parent)
  return acc ? `${acc.account_number} ${acc.account_name}` : ''
})

function selectParent(id) {
  form.parent          = id
  parentDropdownOpen.value = false
}

// Tutup dropdown kalau klik di luar
function handleClickOutside(e) {
  if (parentDropdownRef.value && !parentDropdownRef.value.contains(e.target)) {
    parentDropdownOpen.value = false
  }
}

onMounted(() => document.addEventListener('mousedown', handleClickOutside))
onUnmounted(() => document.removeEventListener('mousedown', handleClickOutside))

// ── Watchers ───────────────────────────────────────────────────────────────
watch(fullAccountNumber, (val) => {
  form.account_number = val
})

watch(() => form.account_group, () => {
  if (isPopulating.value) return
  accountSuffix.value = ''
  form.parent = null 
  delete errors.account_number
})

watch(() => form.account_type, (newType) => {
  if (isPopulating.value) return
  if (newType !== 'DETAIL_BANK') form.bank_type = null
  if (newType === 'HEADER') {
    form.is_inter_company  = false
    form.is_cost_component = false
    form.is_on_duty        = false
    form.is_tax_in         = false
  }
})

// Watch KEDUANYA: show DAN accountGroups
// Karena accountGroups bisa datang belakangan (async fetch di view)
watch(
  [() => props.show, () => props.accountGroups],
  ([show, groups]) => {
    if (!show) return
    if (!groups || groups.length === 0) return
    populateForm()
  }
)

// ── Populate form ──────────────────────────────────────────────────────────
function populateForm() {
  parentDropdownOpen.value = false
  Object.keys(errors).forEach(k => delete errors[k])
  serverError.value  = ''
  isPopulating.value = true

  if (props.mode === 'edit' && props.initialData) {
    Object.assign(form, {
      account_type:      props.initialData.account_type      ?? 'DETAIL',
      account_number:    props.initialData.account_number    ?? '',
      account_name:      props.initialData.account_name      ?? '',
      account_group:     props.initialData.account_group     ?? null,
      parent:            props.initialData.parent            ?? null,
      language:          props.initialData.language          ?? 'EN',
      default_position:  props.initialData.default_position  ?? 'DEBET',
      currency:          props.initialData.currency          ?? 'IDR',
      bank_type:         props.initialData.bank_type         ?? null,
      is_inter_company:  props.initialData.is_inter_company  ?? false,
      is_cost_component: props.initialData.is_cost_component ?? false,
      is_on_duty:        props.initialData.is_on_duty        ?? false,
      is_tax_in:         props.initialData.is_tax_in         ?? false,
      is_active:         props.initialData.is_active         ?? true,
    })

    // Parse suffix dari account_number yang sudah ada
    const group   = props.accountGroups.find(g => g.id === props.initialData.account_group)
    const prefix  = group?.number_prefix ?? ''
    const fullNum = props.initialData.account_number ?? ''
    if (prefix && fullNum.startsWith(prefix)) {
      accountSuffix.value = fullNum.slice(prefix.length).replace(/^[.\-]/, '')
    } else {
      accountSuffix.value = fullNum
    }

  } else {
    Object.assign(form, {
      account_type:      'DETAIL',
      account_number:    '',
      account_name:      '',
      account_group:     props.parentAccount?.account_group ?? null,
      parent:            props.parentAccount?.id            ?? null,
      language:          'EN',
      default_position:  'DEBET',
      currency:          'IDR',
      bank_type:         null,
      is_inter_company:  false,
      is_cost_component: false,
      is_on_duty:        false,
      is_tax_in:         false,
      is_active:         true,
    })
    accountSuffix.value = ''
  }

  // Lepas flag setelah semua reactive update selesai
  nextTick(() => {
    isPopulating.value = false
  })
}

// ── Validasi client-side ───────────────────────────────────────────────────
function validate() {
  Object.keys(errors).forEach(k => delete errors[k])
  serverError.value = ''
  let valid = true

  if (!form.account_group) {
    errors.account_group = 'Account group wajib dipilih.'
    valid = false
  }
  if (!accountSuffix.value.trim()) {
    errors.account_number = 'Account number wajib diisi.'
    valid = false
  }
  if (!form.account_name.trim()) {
    errors.account_name = 'Account name wajib diisi.'
    valid = false
  }
  if (form.account_type === 'DETAIL_BANK' && !form.bank_type) {
    errors.bank_type = 'Bank type wajib dipilih untuk akun Bank.'
    valid = false
  }

  return valid
}

// ── Expose ke parent (ChartOfAccountView) ─────────────────────────────────
function setErrors(serverErr, fieldErrors = {}) {
  serverError.value = serverErr
  Object.keys(errors).forEach(k => delete errors[k])
  Object.assign(errors, fieldErrors)
}

function setLoading(val) {
  isSaving.value = val
}

defineExpose({ setErrors, setLoading })

// ── Submit ─────────────────────────────────────────────────────────────────
function handleSubmit() {
  if (!validate()) return
  emit('saved', { ...form })
}
</script>

<style scoped>
@reference "../../style.css";

.form-input {
  @apply w-full px-3 py-2 text-sm border border-gray-200 rounded-lg
         focus:outline-none focus:ring-2 focus:ring-bfs-gold/40 focus:border-bfs-gold
         transition-all bg-white disabled:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed;
}
.btn-primary {
  @apply px-4 py-2 bg-bfs-gold hover:bg-bfs-gold-dark text-white font-medium rounded-lg transition-colors disabled:opacity-60;
}
.btn-secondary {
  @apply px-4 py-2 border border-gray-200 text-gray-600 hover:bg-gray-50 rounded-lg transition-colors;
}
.modal-enter-active, .modal-leave-active { transition: opacity 0.2s; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
</style>