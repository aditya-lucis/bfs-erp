<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="show" class="fixed inset-0 z-50 overflow-y-auto">
        <div class="fixed inset-0 bg-black/40" @click="$emit('close')" />
        <div class="flex min-h-full items-start justify-center p-4 py-8">
          <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-2xl z-10" @click.stop>

            <!-- Header -->
            <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
              <div>
                <h3 class="text-base font-semibold text-gray-800">
                  {{ mode === 'add' ? 'New Item' : 'Edit Item' }}
                </h3>
                <p v-if="mode === 'edit' && initialData" class="text-xs text-gray-400 font-mono mt-0.5">
                  {{ initialData.item_code }}
                </p>
              </div>
              <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600">
                <X class="w-5 h-5" />
              </button>
            </div>

            <!-- Server error banner -->
            <div v-if="serverError" class="mx-6 mt-4 px-4 py-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
              <AlertCircle class="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
              <p class="text-sm text-red-600">{{ serverError }}</p>
            </div>

            <!-- Tabs -->
            <div class="flex border-b border-gray-100 px-6 pt-3 gap-1">
              <button
                v-for="tab in tabs"
                :key="tab.value"
                @click="activeTab = tab.value"
                class="px-4 py-2 text-xs font-semibold rounded-t-lg transition-colors border-b-2 -mb-px"
                :class="activeTab === tab.value
                  ? 'border-bfs-gold text-bfs-gold'
                  : 'border-transparent text-gray-500 hover:text-gray-700'"
              >
                {{ tab.label }}
              </button>
            </div>

            <!-- ── Tab: Item Info ── -->
            <div v-show="activeTab === 'info'" class="px-6 py-4 space-y-4">

              <!-- Item Type + Category (2 col) -->
              <div class="grid grid-cols-2 gap-3">
                <FormField label="Item Type" required :error="errors.item_type">
                  <div class="flex gap-2">
                    <label
                      v-for="t in itemTypes"
                      :key="t.value"
                      class="flex items-center gap-1.5 cursor-pointer px-3 py-2 border rounded-lg flex-1 transition-colors text-xs"
                      :class="[
                        form.item_type === t.value ? 'border-bfs-gold bg-yellow-50' : 'border-gray-200 hover:border-gray-300',
                        mode === 'edit' ? 'opacity-60 cursor-not-allowed' : ''
                      ]"
                    >
                      <input
                        type="radio"
                        :value="t.value"
                        v-model="form.item_type"
                        class="accent-yellow-500"
                        :disabled="mode === 'edit'"
                      />
                      <span class="font-medium">{{ t.label }}</span>
                    </label>
                  </div>
                  <p v-if="mode === 'edit'" class="mt-1 text-[10px] text-amber-600">
                    Item type tidak bisa diubah.
                  </p>
                </FormField>

                <FormField label="Category" required :error="errors.category">
                  <select
                    v-model="form.category"
                    class="form-input"
                    :class="{ 'border-red-300': errors.category }"
                    :disabled="mode === 'edit'"
                    @change="delete errors.category"
                  >
                    <option :value="null">— Pilih Category —</option>
                    <option
                      v-for="cat in filteredCategories"
                      :key="cat.id"
                      :value="cat.id"
                    >
                      {{ cat.name }}
                    </option>
                  </select>
                  <p v-if="mode === 'add' && form.item_type && filteredCategories.length === 0"
                    class="mt-1 text-[10px] text-amber-600">
                    Belum ada category untuk tipe ini.
                  </p>
                  <p v-if="mode === 'edit'" class="mt-1 text-[10px] text-amber-600">
                    Category tidak bisa diubah.
                  </p>
                </FormField>
              </div>

              <!-- Item Name -->
              <FormField label="Item Name" required :error="errors.item_name">
                <input
                  v-model="form.item_name"
                  class="form-input"
                  :class="{ 'border-red-300': errors.item_name }"
                  placeholder="e.g. ATS INJ 1.500 UI (BIOSAT)"
                  @input="delete errors.item_name"
                />
              </FormField>

              <!-- Item Code preview (add mode only) -->
              <div v-if="mode === 'add' && form.category" class="px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg">
                <p class="text-[11px] text-gray-500 uppercase font-semibold tracking-wide">Preview Kode Item</p>
                <p class="text-sm font-mono font-semibold text-gray-700 mt-0.5">
                  {{ codePreview }}
                </p>
              </div>

              <!-- Units — 2x2 grid -->
              <div class="grid grid-cols-2 gap-3">
                <FormField label="Item Unit" required :error="errors.unit">
                  <select v-model="form.unit" class="form-input" :class="{ 'border-red-300': errors.unit }" @change="delete errors.unit">
                    <option :value="null">— Pilih Unit —</option>
                    <option v-for="u in filteredUnits" :key="u.id" :value="u.id">{{ u.unit_name }}</option>
                  </select>
                </FormField>
                <FormField label="Secondary RR Unit" required :error="errors.secondary_rr_unit">
                  <select v-model="form.secondary_rr_unit" class="form-input" @change="delete errors.secondary_rr_unit">
                    <option :value="null">— Pilih Unit —</option>
                    <option v-for="u in filteredUnits" :key="u.id" :value="u.id">{{ u.unit_name }}</option>
                  </select>
                </FormField>
                <FormField label="Secondary SN/DO Unit" required :error="errors.secondary_sndo_unit">
                  <select v-model="form.secondary_sndo_unit" class="form-input" @change="delete errors.secondary_sndo_unit">
                    <option :value="null">— Pilih Unit —</option>
                    <option v-for="u in filteredUnits" :key="u.id" :value="u.id">{{ u.unit_name }}</option>
                  </select>
                </FormField>
                <FormField label="Secondary Production Unit" required :error="errors.secondary_production_unit">
                  <select v-model="form.secondary_production_unit" class="form-input" @change="delete errors.secondary_production_unit">
                    <option :value="null">— Pilih Unit —</option>
                    <option v-for="u in filteredUnits" :key="u.id" :value="u.id">{{ u.unit_name }}</option>
                  </select>
                </FormField>
              </div>

              <!-- Item Source -->
              <FormField label="Item Source" :error="errors.source">
                <div class="flex gap-4">
                  <label class="flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" v-model="form.is_production" class="w-4 h-4 rounded accent-yellow-500" />
                    <span class="text-sm">Production</span>
                  </label>
                  <label class="flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" v-model="form.is_purchase" class="w-4 h-4 rounded accent-yellow-500" />
                    <span class="text-sm">Purchase</span>
                  </label>
                </div>
                <p v-if="errors.source" class="mt-1 text-xs text-red-500 flex items-center gap-1">
                  <AlertCircle class="w-3 h-3" />{{ errors.source }}
                </p>
              </FormField>

              <!-- Price Type + Unit Price -->
              <div class="grid grid-cols-2 gap-3">
                <FormField label="Price Type" required>
                  <div class="space-y-1.5">
                    <label
                      v-for="p in priceTypes"
                      :key="p.value"
                      class="flex items-center gap-2 cursor-pointer"
                    >
                      <input type="radio" :value="p.value" v-model="form.price_type" class="accent-yellow-500" />
                      <span class="text-sm">{{ p.label }}</span>
                    </label>
                  </div>
                </FormField>

                <div class="space-y-3">
                  <FormField label="Unit Price" :error="errors.unit_price">
                    <div class="flex items-center border border-gray-200 rounded-lg overflow-hidden focus-within:ring-2 focus-within:ring-bfs-gold/40 focus-within:border-bfs-gold">
                      <span class="px-3 py-2 bg-gray-50 text-xs text-gray-500 border-r border-gray-200 shrink-0">IDR</span>
                      <input
                        v-model.number="form.unit_price"
                        type="number"
                        min="0"
                        class="flex-1 px-3 py-2 text-sm outline-none"
                        placeholder="0"
                      />
                    </div>
                  </FormField>
                  <label class="flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" v-model="form.is_last_purchase_price" class="w-4 h-4 rounded accent-yellow-500" />
                    <span class="text-xs text-gray-600">Use Last Purchase Price</span>
                  </label>
                </div>
              </div>

              <!-- Costing + Currency -->
              <div class="grid grid-cols-2 gap-3">
                <FormField label="Costing Method">
                  <select v-model="form.costing_method" class="form-input">
                    <option v-for="c in costingMethods" :key="c.value" :value="c.value">{{ c.label }}</option>
                  </select>
                </FormField>
                <FormField label="Default Currency">
                  <select v-model="form.default_currency" class="form-input">
                    <option value="IDR">IDR</option>
                    <option value="USD">USD</option>
                    <option value="EUR">EUR</option>
                    <option value="SGD">SGD</option>
                  </select>
                </FormField>
              </div>

              <!-- View Category + Flags -->
              <div class="grid grid-cols-2 gap-3">
                <FormField label="View Category">
                  <div class="space-y-1.5">
                    <label class="flex items-center gap-2 cursor-pointer">
                      <input type="checkbox" v-model="form.view_buy"       class="w-4 h-4 rounded accent-yellow-500" />
                      <span class="text-sm">Buy</span>
                    </label>
                    <label class="flex items-center gap-2 cursor-pointer">
                      <input type="checkbox" v-model="form.view_sell"      class="w-4 h-4 rounded accent-yellow-500" />
                      <span class="text-sm">Sell</span>
                    </label>
                    <label class="flex items-center gap-2 cursor-pointer">
                      <input type="checkbox" v-model="form.view_inventory" class="w-4 h-4 rounded accent-yellow-500" />
                      <span class="text-sm">Inventory</span>
                    </label>
                  </div>
                </FormField>

                <FormField label="Status & Flags">
                  <div class="space-y-1.5">
                    <label class="flex items-center gap-2 cursor-pointer">
                      <input type="checkbox" v-model="form.is_active"       class="w-4 h-4 rounded accent-yellow-500" />
                      <span class="text-sm">Active</span>
                    </label>
                    <label class="flex items-center gap-2 cursor-pointer">
                      <input type="checkbox" v-model="form.is_service"      class="w-4 h-4 rounded accent-yellow-500" />
                      <span class="text-sm">Service</span>
                    </label>
                    <label class="flex items-center gap-2 cursor-pointer">
                      <input type="checkbox" v-model="form.is_new"          class="w-4 h-4 rounded accent-yellow-500" />
                      <span class="text-sm">New Item</span>
                    </label>
                    <label class="flex items-center gap-2 cursor-pointer">
                      <input type="checkbox" v-model="form.is_automatic_pr" class="w-4 h-4 rounded accent-yellow-500" />
                      <span class="text-sm">Automatic PR</span>
                    </label>
                  </div>
                </FormField>
              </div>
            </div>

            <!-- ── Tab: Photo ── -->
            <div v-show="activeTab === 'photo'" class="px-6 py-4">
              <div class="flex flex-col items-center gap-4">
                <!-- Preview -->
                <div class="w-48 h-48 border-2 border-dashed border-gray-200 rounded-xl overflow-hidden flex items-center justify-center bg-gray-50">
                  <img
                    v-if="imagePreview"
                    :src="imagePreview"
                    class="w-full h-full object-contain"
                    alt="Item preview"
                  />
                  <div v-else class="text-center text-gray-400">
                    <ImageIcon class="w-10 h-10 mx-auto mb-2" />
                    <p class="text-xs">Belum ada foto</p>
                  </div>
                </div>

                <!-- Upload -->
                <div class="w-full">
                  <label class="block w-full cursor-pointer">
                    <div class="flex items-center justify-center gap-2 px-4 py-3 border border-gray-200 rounded-lg hover:border-bfs-gold hover:bg-yellow-50 transition-colors">
                      <Upload class="w-4 h-4 text-gray-500" />
                      <span class="text-sm text-gray-600">
                        {{ selectedFile ? selectedFile.name : 'Pilih foto item' }}
                      </span>
                    </div>
                    <input
                      type="file"
                      accept="image/*"
                      class="hidden"
                      @change="handleFileSelect"
                    />
                  </label>
                  <p class="mt-2 text-xs text-gray-400 text-center">
                    Format: JPG, PNG, WEBP. Maks 5MB.
                  </p>
                  <p v-if="errors.image" class="mt-1 text-xs text-red-500 text-center">{{ errors.image }}</p>
                </div>

                <!-- Remove photo button -->
                <button
                  v-if="imagePreview"
                  @click="removeImage"
                  class="text-xs text-red-500 hover:underline flex items-center gap-1"
                >
                  <Trash2 class="w-3 h-3" /> Hapus foto
                </button>
              </div>
            </div>

            <!-- Footer -->
            <div class="flex justify-between items-center px-6 py-4 border-t border-gray-100 bg-gray-50 rounded-b-2xl">
              <p v-if="activeTab === 'photo' && mode === 'add'" class="text-xs text-gray-400">
                Foto bisa diupload setelah item disimpan.
              </p>
              <div class="flex gap-2 ml-auto">
                <button @click="$emit('close')" class="btn-secondary text-sm">Cancel</button>
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
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, reactive, computed, watch, nextTick } from 'vue'
import { X, Save, Loader2, AlertCircle, Upload, Trash2, Image as ImageIcon } from 'lucide-vue-next'
import FormField from '../FormField.vue'

const props = defineProps({
  show:        { type: Boolean, required: true },
  mode:        { type: String,  default: 'add' },
  initialData: { type: Object,  default: null },
  categories:  { type: Array,   default: () => [] },
  units:       { type: Array,   default: () => [] },
  choices:     { type: Object,  default: null },
})

const emit = defineEmits(['close', 'saved'])

const itemTypes = [
  { value: 'RM', label: 'Raw Material' },
  { value: 'SP', label: 'Supplies' },
]
const tabs = [
  { value: 'info',  label: 'Item Info' },
  { value: 'photo', label: 'Photo' },
]
const priceTypes = computed(() =>
  props.choices?.price_types ?? [
    { value: 'FIXED',        label: 'Fixed' },
    { value: 'EDITABLE',     label: 'Editable' },
    { value: 'USER_DEFINED', label: 'User-Defined' },
  ]
)
const costingMethods = computed(() =>
  props.choices?.costing_methods ?? [
    { value: 'FIFO', label: 'First In First Out (FIFO)' },
    { value: 'LIFO', label: 'Last In First Out (LIFO)' },
    { value: 'AVG',  label: 'Weighted Average' },
  ]
)

// ── State ──────────────────────────────────────────────────────────────────
const activeTab    = ref('info')
const isSaving     = ref(false)
const serverError  = ref('')
const errors       = reactive({})
const selectedFile = ref(null)
const imagePreview = ref('')
const isPopulating = ref(false)  // ← flag untuk cegah race condition

const form = reactive({
  item_name:                 '',
  item_type:                 'RM',
  category:                  null,
  unit:                      null,
  secondary_rr_unit:         null,
  secondary_sndo_unit:       null,
  secondary_production_unit: null,
  is_production:             false,
  is_purchase:               true,
  price_type:                'EDITABLE',
  unit_price:                0,
  is_last_purchase_price:    false,
  costing_method:            'FIFO',
  default_currency:          'IDR',
  is_automatic_pr:           false,
  view_buy:                  true,
  view_sell:                 true,
  view_inventory:            false,
  is_active:                 true,
  is_service:                false,
  is_new:                    true,
})

// ── Computed ───────────────────────────────────────────────────────────────
const filteredCategories = computed(() =>
  props.categories.filter(c => c.item_type === form.item_type)
)

const filteredUnits = computed(() =>
  props.units.filter(u => u.item_type === form.item_type)
)

const codePreview = computed(() => {
  const cat = props.categories.find(c => c.id === form.category)
  if (!cat) return '—'
  return `${new Date().getFullYear()}_${cat.name}_XXXX`
})

// ── Watchers ───────────────────────────────────────────────────────────────

// Reset category & units saat item_type berubah — SKIP kalau lagi populate
watch(() => form.item_type, () => {
  if (isPopulating.value) return
  form.category                  = null
  form.unit                      = null
  form.secondary_rr_unit         = null
  form.secondary_sndo_unit       = null
  form.secondary_production_unit = null
})

// Watch KEDUANYA: show + props data (units/categories bisa datang async)
watch(
  [() => props.show, () => props.units, () => props.categories],
  ([show, units, cats]) => {
    if (!show) return
    // Tunggu units dan categories tersedia
    if (!units?.length || !cats?.length) return
    populateForm()
  }
)

// ── Populate ───────────────────────────────────────────────────────────────
function populateForm() {
  activeTab.value   = 'info'
  serverError.value = ''
  Object.keys(errors).forEach(k => delete errors[k])
  selectedFile.value = null
  isPopulating.value = true

  if (props.mode === 'edit' && props.initialData) {
    Object.assign(form, {
      item_name:                 props.initialData.item_name                ?? '',
      item_type:                 props.initialData.item_type                ?? 'RM',
      category:                  props.initialData.category                 ?? null,
      unit:                      props.initialData.unit                     ?? null,
      secondary_rr_unit:         props.initialData.secondary_rr_unit        ?? null,
      secondary_sndo_unit:       props.initialData.secondary_sndo_unit      ?? null,
      secondary_production_unit: props.initialData.secondary_production_unit ?? null,
      is_production:             props.initialData.is_production             ?? false,
      is_purchase:               props.initialData.is_purchase               ?? true,
      price_type:                props.initialData.price_type                ?? 'EDITABLE',
      unit_price:                props.initialData.unit_price                ?? 0,
      is_last_purchase_price:    props.initialData.is_last_purchase_price    ?? false,
      costing_method:            props.initialData.costing_method            ?? 'FIFO',
      default_currency:          props.initialData.default_currency          ?? 'IDR',
      is_automatic_pr:           props.initialData.is_automatic_pr           ?? false,
      view_buy:                  props.initialData.view_buy                  ?? true,
      view_sell:                 props.initialData.view_sell                 ?? true,
      view_inventory:            props.initialData.view_inventory             ?? false,
      is_active:                 props.initialData.is_active                 ?? true,
      is_service:                props.initialData.is_service                ?? false,
      is_new:                    props.initialData.is_new                    ?? true,
    })
    imagePreview.value = props.initialData.image_url || ''
  } else {
    Object.assign(form, {
      item_name: '', item_type: 'RM', category: null,
      unit: null, secondary_rr_unit: null,
      secondary_sndo_unit: null, secondary_production_unit: null,
      is_production: false, is_purchase: true,
      price_type: 'EDITABLE', unit_price: 0,
      is_last_purchase_price: false, costing_method: 'FIFO',
      default_currency: 'IDR', is_automatic_pr: false,
      view_buy: true, view_sell: true, view_inventory: false,
      is_active: true, is_service: false, is_new: true,
    })
    imagePreview.value = ''
  }

  // Lepas flag setelah semua reactive selesai
  nextTick(() => { isPopulating.value = false })
}

// ── Image ──────────────────────────────────────────────────────────────────
function handleFileSelect(e) {
  const file = e.target.files[0]
  if (!file) return
  if (file.size > 5 * 1024 * 1024) {
    errors.image = 'Ukuran file maksimal 5MB.'
    return
  }
  delete errors.image
  selectedFile.value = file
  imagePreview.value = URL.createObjectURL(file)
}

function removeImage() {
  selectedFile.value = null
  imagePreview.value = ''
}

// ── Validasi ───────────────────────────────────────────────────────────────
function validate() {
  Object.keys(errors).forEach(k => delete errors[k])
  serverError.value = ''
  let valid = true

  if (!form.item_type) { errors.item_type = 'Item type wajib dipilih.'; valid = false }
  if (!form.category)  { errors.category  = 'Category wajib dipilih.'; valid = false }
  if (!form.item_name.trim()) { errors.item_name = 'Item name wajib diisi.'; valid = false }
  if (!form.unit)                      { errors.unit                      = 'Item unit wajib dipilih.'; valid = false }
  if (!form.secondary_rr_unit)         { errors.secondary_rr_unit         = 'Wajib dipilih.'; valid = false }
  if (!form.secondary_sndo_unit)       { errors.secondary_sndo_unit       = 'Wajib dipilih.'; valid = false }
  if (!form.secondary_production_unit) { errors.secondary_production_unit = 'Wajib dipilih.'; valid = false }
  if (!form.is_production && !form.is_purchase) {
    errors.source = 'Minimal satu source harus dipilih.'
    valid = false
  }

  if (!valid) activeTab.value = 'info'
  return valid
}

// ── Expose ─────────────────────────────────────────────────────────────────
function setErrors(err) {
  const data = err?.response?.data
  if (!data) { serverError.value = 'Terjadi kesalahan server.'; return }

  if (typeof data === 'object' && !Array.isArray(data)) {
    let hasField = false
    for (const [field, messages] of Object.entries(data)) {
      const msg = Array.isArray(messages) ? messages[0] : String(messages)
      if (field === 'non_field_errors' || field === 'detail') {
        serverError.value = msg
      } else {
        errors[field] = msg
        hasField = true
      }
    }
    if (hasField && !serverError.value) serverError.value = 'Periksa kembali isian form.'
    if (hasField) activeTab.value = 'info'
  } else {
    serverError.value = String(data)
  }
}

function setLoading(val) { isSaving.value = val }

defineExpose({ setErrors, setLoading })

// ── Submit ─────────────────────────────────────────────────────────────────
function handleSubmit() {
  if (!validate()) return

  let payload
  if (selectedFile.value) {
    payload = new FormData()
    for (const [key, val] of Object.entries(form)) {
      if (val !== null && val !== undefined) payload.append(key, val)
    }
    payload.append('image', selectedFile.value)
  } else {
    payload = { ...form }
  }

  emit('saved', payload, selectedFile.value !== null)
}
</script>

<style scoped>
@reference "../../style.css";
.form-input {
  @apply w-full px-3 py-2 text-sm border border-gray-200 rounded-lg
         focus:outline-none focus:ring-2 focus:ring-bfs-gold/40 focus:border-bfs-gold
         transition-all bg-white disabled:bg-gray-50 disabled:cursor-not-allowed;
}
.btn-primary   { @apply px-4 py-2 bg-bfs-gold hover:bg-bfs-gold-dark text-white font-medium rounded-lg transition-colors disabled:opacity-60; }
.btn-secondary { @apply px-4 py-2 border border-gray-200 text-gray-600 hover:bg-gray-50 rounded-lg transition-colors; }
.modal-enter-active, .modal-leave-active { transition: opacity 0.2s; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
</style>