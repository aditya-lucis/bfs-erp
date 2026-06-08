<template>
  <Panel title="Unit Measurement" subtitle="Inventory | Unit Measurement">

    <!-- Toolbar -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
      <!-- Filter tabs: All / RM / SP -->
      <div class="flex items-center gap-1 bg-gray-100 rounded-lg p-1">
        <button
          v-for="tab in tabs"
          :key="tab.value"
          @click="activeTab = tab.value"
          class="px-3 py-1.5 text-xs font-medium rounded-md transition-colors"
          :class="activeTab === tab.value
            ? 'bg-white text-gray-800 shadow-sm'
            : 'text-gray-500 hover:text-gray-700'"
        >
          {{ tab.label }}
        </button>
      </div>

      <div class="flex items-center gap-2">
        <!-- Search -->
        <div class="relative">
          <Search class="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-400" />
          <input
            v-model="search"
            type="text"
            placeholder="Cari unit..."
            class="pl-8 pr-3 py-1.5 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-bfs-gold/40 focus:border-bfs-gold w-48"
          />
        </div>
        <button
          v-if="canCreate"
          @click="openAddModal"
          class="btn-primary text-xs flex items-center gap-1.5"
        >
          <Plus class="w-3.5 h-3.5" /> Add Unit
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="store.isLoading" class="flex justify-center py-16">
      <Loader2 class="w-6 h-6 animate-spin text-bfs-gold" />
    </div>

    <!-- Table -->
    <div v-else-if="filteredUnits.length" class="border border-gray-200 rounded-xl overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 border-b border-gray-200">
          <tr>
            <th class="text-left px-4 py-2.5 text-[11px] font-semibold text-gray-500 uppercase tracking-wide">Unit Name</th>
            <th class="text-left px-4 py-2.5 text-[11px] font-semibold text-gray-500 uppercase tracking-wide">Description</th>
            <th class="text-left px-4 py-2.5 text-[11px] font-semibold text-gray-500 uppercase tracking-wide">Type</th>
            <th class="text-left px-4 py-2.5 text-[11px] font-semibold text-gray-500 uppercase tracking-wide">Status</th>
            <th class="px-4 py-2.5 text-right text-[11px] font-semibold text-gray-500 uppercase tracking-wide">Action</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr
            v-for="unit in filteredUnits"
            :key="unit.id"
            class="hover:bg-gray-50 transition-colors"
          >
            <td class="px-4 py-2.5 font-medium text-gray-800">{{ unit.unit_name }}</td>
            <td class="px-4 py-2.5 text-gray-500">{{ unit.unit_description || '—' }}</td>
            <td class="px-4 py-2.5">
              <span
                class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold"
                :class="unit.item_type === 'RM'
                  ? 'bg-blue-50 text-blue-700'
                  : 'bg-purple-50 text-purple-700'"
              >
                {{ unit.item_type_label }}
              </span>
            </td>
            <td class="px-4 py-2.5">
              <span
                class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold"
                :class="unit.is_active ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-500'"
              >
                {{ unit.is_active ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td class="px-4 py-2.5">
              <div class="flex items-center justify-end gap-1">
                <button
                  v-if="canUpdate"
                  @click="openEditModal(unit)"
                  class="p-1.5 text-gray-400 hover:text-blue-500 hover:bg-blue-50 rounded transition-colors"
                  title="Edit"
                >
                  <Pencil class="w-3.5 h-3.5" />
                </button>
                <button
                  v-if="canDelete"
                  @click="confirmDelete(unit)"
                  class="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded transition-colors"
                  title="Hapus"
                >
                  <Trash2 class="w-3.5 h-3.5" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Empty state -->
    <div v-else class="flex flex-col items-center justify-center py-20 text-gray-400">
      <Ruler class="w-10 h-10 mb-3" />
      <p class="text-sm">Belum ada unit measurement.</p>
      <button v-if="canCreate" @click="openAddModal" class="mt-3 text-sm text-bfs-gold hover:underline">
        Tambah sekarang
      </button>
    </div>

    <!-- ── Form Modal ── -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="modal.show" class="fixed inset-0 z-50 overflow-y-auto" @click.self="modal.show = false">
          <div class="fixed inset-0 bg-black/40" @click="modal.show = false" />
          <div class="flex min-h-full items-start justify-center p-4 py-8">
            <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-sm z-10" @click.stop>

              <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
                <h3 class="text-base font-semibold text-gray-800">
                  {{ modal.mode === 'add' ? 'Add Unit Measurement' : 'Edit Unit Measurement' }}
                </h3>
                <button @click="modal.show = false" class="text-gray-400 hover:text-gray-600">
                  <X class="w-5 h-5" />
                </button>
              </div>

              <!-- Server error banner -->
              <div v-if="formError.serverError.value" class="mx-6 mt-4 px-4 py-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
                <AlertCircle class="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
                <p class="text-sm text-red-600">{{ formError.serverError.value }}</p>
              </div>

              <div class="px-6 py-4 space-y-3">
                <FormField label="Unit Name" required :error="formError.fieldErrors.unit_name">
                  <input
                    v-model="form.unit_name"
                    class="form-input"
                    :class="{ 'border-red-300': formError.fieldErrors.unit_name }"
                    placeholder="e.g. Pcs, Kg, Ltr"
                    @input="delete formError.fieldErrors.unit_name"
                  />
                </FormField>

                <FormField label="Description" :error="formError.fieldErrors.unit_description">
                  <input
                    v-model="form.unit_description"
                    class="form-input"
                    placeholder="e.g. Pieces"
                  />
                </FormField>

                <FormField label="Item Type" required :error="formError.fieldErrors.item_type">
                  <div class="flex gap-3">
                    <label
                      v-for="t in itemTypes"
                      :key="t.value"
                      class="flex items-center gap-2 cursor-pointer px-3 py-2 border rounded-lg flex-1 transition-colors"
                      :class="form.item_type === t.value
                        ? 'border-bfs-gold bg-yellow-50'
                        : 'border-gray-200 hover:border-gray-300'"
                    >
                      <input
                        type="radio"
                        :value="t.value"
                        v-model="form.item_type"
                        class="accent-yellow-500"
                      />
                      <span class="text-sm font-medium">{{ t.label }}</span>
                    </label>
                  </div>
                </FormField>

                <FormField label="Status">
                  <label class="flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" v-model="form.is_active" class="w-4 h-4 rounded accent-yellow-500" />
                    <span class="text-sm text-gray-700">Active</span>
                  </label>
                </FormField>
              </div>

              <div class="flex justify-end gap-2 px-6 py-4 border-t border-gray-100 bg-gray-50 rounded-b-2xl">
                <button @click="modal.show = false" class="btn-secondary text-sm">Cancel</button>
                <button @click="handleSubmit" :disabled="isSaving" class="btn-primary text-sm flex items-center gap-1.5">
                  <Loader2 v-if="isSaving" class="w-3.5 h-3.5 animate-spin" />
                  <Save v-else class="w-3.5 h-3.5" />
                  {{ modal.mode === 'add' ? 'Save' : 'Update' }}
                </button>
              </div>

            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- ── Delete Confirm Modal ── -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="deleteModal.show" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-black/40" @click="deleteModal.show = false" />
          <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6 z-10">
            <div class="flex flex-col items-center text-center gap-3">
              <div class="w-12 h-12 rounded-full bg-red-100 flex items-center justify-center">
                <Trash2 class="w-6 h-6 text-red-500" />
              </div>
              <h3 class="text-base font-semibold text-gray-800">Hapus Unit?</h3>
              <p class="text-sm text-gray-500">
                Unit <span class="font-semibold text-gray-700">{{ deleteModal.target?.unit_name }}</span>
                akan dinonaktifkan. Unit yang masih dipakai item aktif tidak bisa dihapus.
              </p>
            </div>
            <div v-if="deleteModal.error" class="mt-3 px-4 py-2 bg-red-50 border border-red-200 rounded-lg">
              <p class="text-sm text-red-600 text-center">{{ deleteModal.error }}</p>
            </div>
            <div class="flex gap-2 mt-5">
              <button @click="deleteModal.show = false" class="btn-secondary text-sm flex-1">Batal</button>
              <button
                @click="handleDelete"
                :disabled="isSaving"
                class="flex-1 text-sm py-2 px-4 bg-red-500 hover:bg-red-600 text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-1.5 disabled:opacity-60"
              >
                <Loader2 v-if="isSaving" class="w-3.5 h-3.5 animate-spin" />
                <Trash2 v-else class="w-3.5 h-3.5" />
                Hapus
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

  </Panel>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useInventoryStore } from '../../stores/inventory.js'
import { usePermission } from '../../composables/usePermission.js'
import { useFormError } from '../../composables/useFormError.js'
import Panel from '../../components/Panel.vue'
import FormField from '../../components/FormField.vue'
import { useToast } from '../../composables/useToast.js'
import { Plus, Pencil, Trash2, Save, X, Loader2, Search, Ruler, AlertCircle } from 'lucide-vue-next'

const store = useInventoryStore()
const { canCreate, canUpdate, canDelete } = usePermission('INV-UNIT-MEASUREMENT')
const formError = useFormError()
const isSaving  = ref(false)
const toast = useToast()

// ── Filter & Search ────────────────────────────────────────────────────────
const activeTab = ref('ALL')
const search    = ref('')

const tabs = [
  { value: 'ALL', label: 'All' },
  { value: 'RM',  label: 'Raw Material' },
  { value: 'SP',  label: 'Supplies' },
]

const itemTypes = [
  { value: 'RM', label: 'Raw Material' },
  { value: 'SP', label: 'Supplies' },
]

const filteredUnits = computed(() => {
  let list = store.units
  if (activeTab.value !== 'ALL') list = list.filter(u => u.item_type === activeTab.value)
  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    list = list.filter(u =>
      u.unit_name.toLowerCase().includes(q) ||
      (u.unit_description || '').toLowerCase().includes(q)
    )
  }
  return list
})

// ── Form ───────────────────────────────────────────────────────────────────
const modal = reactive({ show: false, mode: 'add', editId: null })
const form  = reactive({ unit_name: '', unit_description: '', item_type: 'RM', is_active: true })

function openAddModal() {
  modal.show   = true
  modal.mode   = 'add'
  modal.editId = null
  formError.clearErrors()
  Object.assign(form, { unit_name: '', unit_description: '', item_type: 'RM', is_active: true })
}

function openEditModal(unit) {
  modal.show   = true
  modal.mode   = 'edit'
  modal.editId = unit.id
  formError.clearErrors()
  Object.assign(form, {
    unit_name:        unit.unit_name,
    unit_description: unit.unit_description || '',
    item_type:        unit.item_type,
    is_active:        unit.is_active,
  })
}

function validate() {
  formError.clearErrors()
  let valid = true
  if (!form.unit_name.trim()) {
    formError.fieldErrors.unit_name = 'Unit name wajib diisi.'
    valid = false
  }
  if (!form.item_type) {
    formError.fieldErrors.item_type = 'Item type wajib dipilih.'
    valid = false
  }
  return valid
}

async function handleSubmit() {
  if (!validate()) return
  isSaving.value = true
  try {
    if (modal.mode === 'add') {
      await store.createUnit({ ...form })
      toast.success('Unit berhasil ditambahkan.')
    } else {
      await store.updateUnit(modal.editId, { ...form })
      toast.success('Unit berhasil diperbarui.')
    }
    modal.show = false
    await store.fetchUnits()
  } catch (err) {
    formError.parseApiError(err)
    toast.error('Gagal menyimpan unit.')
  } finally {
    isSaving.value = false
  }
}

// ── Delete ─────────────────────────────────────────────────────────────────
const deleteModal = reactive({ show: false, target: null, error: '' })

function confirmDelete(unit) {
  deleteModal.target = unit
  deleteModal.error  = ''
  deleteModal.show   = true
}

async function handleDelete() {
  isSaving.value    = true
  deleteModal.error = ''
  try {
    await store.deleteUnit(deleteModal.target.id)
    deleteModal.show = false
    toast.success('Unit berhasil dihapus.')
    await store.fetchUnits()
  } catch (err) {
    deleteModal.error = err?.response?.data?.detail || 'Gagal menghapus unit.'
    toast.error(deleteModal.error)
  } finally {
    isSaving.value = false
  }
}

onMounted(() => store.fetchUnits())
</script>

<style scoped>
@reference "../../style.css";
.form-input {
  @apply w-full px-3 py-2 text-sm border border-gray-200 rounded-lg
         focus:outline-none focus:ring-2 focus:ring-bfs-gold/40 focus:border-bfs-gold
         transition-all bg-white disabled:bg-gray-50 disabled:cursor-not-allowed;
}
.btn-primary  { @apply px-4 py-2 bg-bfs-gold hover:bg-bfs-gold-dark text-white font-medium rounded-lg transition-colors disabled:opacity-60; }
.btn-secondary { @apply px-4 py-2 border border-gray-200 text-gray-600 hover:bg-gray-50 rounded-lg transition-colors; }
.modal-enter-active, .modal-leave-active { transition: opacity 0.2s; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
</style>