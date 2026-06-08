<template>
  <Panel title="Item Category" subtitle="Inventory | Item Category">

    <!-- Toolbar -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
      <div class="flex items-center gap-1 bg-gray-100 rounded-lg p-1">
        <button
          v-for="tab in tabs"
          :key="tab.value"
          @click="activeTab = tab.value"
          class="px-3 py-1.5 text-xs font-medium rounded-md transition-colors"
          :class="activeTab === tab.value ? 'bg-white text-gray-800 shadow-sm' : 'text-gray-500 hover:text-gray-700'"
        >
          {{ tab.label }}
        </button>
      </div>

      <div class="flex items-center gap-2">
        <div class="relative">
          <Search class="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-400" />
          <input
            v-model="search"
            type="text"
            placeholder="Cari category..."
            class="pl-8 pr-3 py-1.5 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-bfs-gold/40 focus:border-bfs-gold w-48"
          />
        </div>
        <button
          v-if="canCreate"
          @click="openAddModal"
          class="btn-primary text-xs flex items-center gap-1.5"
        >
          <Plus class="w-3.5 h-3.5" /> Add Group
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="store.isLoading" class="flex justify-center py-16">
      <Loader2 class="w-6 h-6 animate-spin text-bfs-gold" />
    </div>

    <!-- Grid directory — mirip tampilan folder di screenshot ERP lama -->
    <div v-else-if="filteredCategories.length" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
      <div
        v-for="cat in filteredCategories"
        :key="cat.id"
        class="group flex items-center gap-3 p-3 border border-gray-200 rounded-xl hover:border-bfs-gold/50 hover:bg-yellow-50/30 transition-all"
      >
        <!-- Folder icon -->
        <div class="shrink-0 w-9 h-9 rounded-lg flex items-center justify-center"
          :class="cat.item_type === 'RM' ? 'bg-blue-50' : 'bg-purple-50'">
          <FolderOpen class="w-5 h-5" :class="cat.item_type === 'RM' ? 'text-blue-500' : 'text-purple-500'" />
        </div>

        <!-- Info -->
        <div class="flex-1 min-w-0">
          <p class="text-sm font-mono font-semibold text-gray-800 truncate">{{ cat.name }}</p>
          <div class="flex items-center gap-2 mt-0.5">
            <span class="text-[10px] font-medium px-1.5 py-0.5 rounded"
              :class="cat.item_type === 'RM' ? 'bg-blue-50 text-blue-700' : 'bg-purple-50 text-purple-700'">
              {{ cat.item_type_label }}
            </span>
            <span class="text-[10px] text-gray-400">{{ cat.item_count }} item</span>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            v-if="canUpdate"
            @click="openEditModal(cat)"
            class="p-1.5 text-gray-400 hover:text-blue-500 hover:bg-blue-50 rounded transition-colors"
            title="Edit"
          >
            <Pencil class="w-3.5 h-3.5" />
          </button>
          <button
            v-if="canDelete"
            @click="confirmDelete(cat)"
            class="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded transition-colors"
            title="Hapus"
          >
            <Trash2 class="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>

    <!-- Empty -->
    <div v-else class="flex flex-col items-center justify-center py-20 text-gray-400">
      <FolderOpen class="w-10 h-10 mb-3" />
      <p class="text-sm">Belum ada item category.</p>
      <button v-if="canCreate" @click="openAddModal" class="mt-3 text-sm text-bfs-gold hover:underline">
        Buat group pertama
      </button>
    </div>

    <!-- ── Form Modal ── -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="modal.show" class="fixed inset-0 z-50 overflow-y-auto">
          <div class="fixed inset-0 bg-black/40" @click="modal.show = false" />
          <div class="flex min-h-full items-start justify-center p-4 py-8">
            <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-sm z-10" @click.stop>

              <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
                <h3 class="text-base font-semibold text-gray-800">
                  {{ modal.mode === 'add' ? 'Add Group' : 'Edit Group' }}
                </h3>
                <button @click="modal.show = false" class="text-gray-400 hover:text-gray-600">
                  <X class="w-5 h-5" />
                </button>
              </div>

              <div v-if="formError.serverError.value" class="mx-6 mt-4 px-4 py-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
                <AlertCircle class="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
                <p class="text-sm text-red-600">{{ formError.serverError.value }}</p>
              </div>

              <div class="px-6 py-4 space-y-3">
                <FormField label="Item Type" required :error="formError.fieldErrors.item_type">
                  <div class="flex gap-3">
                    <label
                      v-for="t in itemTypes"
                      :key="t.value"
                      class="flex items-center gap-2 cursor-pointer px-3 py-2 border rounded-lg flex-1 transition-colors"
                      :class="[
                        form.item_type === t.value ? 'border-bfs-gold bg-yellow-50' : 'border-gray-200 hover:border-gray-300',
                        modal.mode === 'edit' ? 'opacity-60 cursor-not-allowed' : ''
                      ]"
                    >
                      <input
                        type="radio"
                        :value="t.value"
                        v-model="form.item_type"
                        class="accent-yellow-500"
                        :disabled="modal.mode === 'edit'"
                      />
                      <span class="text-sm font-medium">{{ t.label }}</span>
                    </label>
                  </div>
                  <p v-if="modal.mode === 'edit'" class="mt-1 text-xs text-amber-600 flex items-center gap-1">
                    <AlertCircle class="w-3 h-3 shrink-0" />
                    Item type tidak bisa diubah setelah group dibuat.
                  </p>
                </FormField>

                <FormField label="Nama Group (Directory)" required :error="formError.fieldErrors.name">
                  <input
                    v-model="form.name"
                    class="form-input font-mono uppercase"
                    :class="{ 'border-red-300': formError.fieldErrors.name }"
                    placeholder="e.g. BHP_MEDIS"
                    @input="handleNameInput"
                  />
                  <p class="mt-1 text-xs text-gray-400">
                    Hanya huruf kapital, angka, dan underscore (_). Tanpa spasi.
                  </p>
                </FormField>

                <FormField label="Description" :error="formError.fieldErrors.description">
                  <input
                    v-model="form.description"
                    class="form-input"
                    placeholder="Deskripsi singkat (opsional)"
                  />
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

    <!-- ── Delete Modal ── -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="deleteModal.show" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-black/40" @click="deleteModal.show = false" />
          <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6 z-10">
            <div class="flex flex-col items-center text-center gap-3">
              <div class="w-12 h-12 rounded-full bg-red-100 flex items-center justify-center">
                <Trash2 class="w-6 h-6 text-red-500" />
              </div>
              <h3 class="text-base font-semibold text-gray-800">Hapus Group?</h3>
              <p class="text-sm text-gray-500">
                Group <span class="font-mono font-semibold text-gray-700">{{ deleteModal.target?.name }}</span>
                akan dinonaktifkan. Group yang masih memiliki item aktif tidak bisa dihapus.
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
import { Plus, Pencil, Trash2, Save, X, Loader2, Search, FolderOpen, AlertCircle } from 'lucide-vue-next'

const store = useInventoryStore()
const { canCreate, canUpdate, canDelete } = usePermission('INV-ITEM-CATEGORY')
const formError = useFormError()
const isSaving  = ref(false)
const toast = useToast()

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

const filteredCategories = computed(() => {
  let list = store.categories
  if (activeTab.value !== 'ALL') list = list.filter(c => c.item_type === activeTab.value)
  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    list = list.filter(c => c.name.toLowerCase().includes(q))
  }
  return list
})

// ── Form ───────────────────────────────────────────────────────────────────
const modal = reactive({ show: false, mode: 'add', editId: null })
const form  = reactive({ name: '', description: '', item_type: 'RM' })

function openAddModal() {
  modal.show = true; modal.mode = 'add'; modal.editId = null
  formError.clearErrors()
  Object.assign(form, { name: '', description: '', item_type: 'RM' })
}

function openEditModal(cat) {
  modal.show = true; modal.mode = 'edit'; modal.editId = cat.id
  formError.clearErrors()
  Object.assign(form, { name: cat.name, description: cat.description || '', item_type: cat.item_type })
}

// Force uppercase + strip invalid chars saat user mengetik
function handleNameInput(e) {
  // Ambil value, uppercase, hapus karakter selain A-Z 0-9 _
  const cleaned = e.target.value.toUpperCase().replace(/[^A-Z0-9_]/g, '')
  form.name = cleaned
  delete formError.fieldErrors.name
}

function validate() {
  formError.clearErrors()
  let valid = true

  if (!form.item_type) {
    formError.fieldErrors.item_type = 'Item type wajib dipilih.'
    valid = false
  }
  if (!form.name.trim()) {
    formError.fieldErrors.name = 'Nama group wajib diisi.'
    valid = false
  } else if (!/^[A-Z0-9][A-Z0-9_]*[A-Z0-9]$|^[A-Z0-9]$/.test(form.name)) {
    formError.fieldErrors.name = 'Format tidak valid. Gunakan huruf kapital, angka, dan underscore. Tidak boleh diawali/diakhiri underscore.'
    valid = false
  }
  return valid
}

async function handleSubmit() {
  if (!validate()) return
  isSaving.value = true
  try {
    if (modal.mode === 'add') {
      await store.createCategory({ ...form })
    } else {
      // item_type tidak boleh diubah
      await store.updateCategory(modal.editId, {
        name: form.name,
        description: form.description,
      })
    }
    modal.show = false
    await store.fetchCategories()
  } catch (err) {
    formError.parseApiError(err)
    toast.error('Gagal menyimpan group.')
  } finally {
    isSaving.value = false
  }
}

// ── Delete ─────────────────────────────────────────────────────────────────
const deleteModal = reactive({ show: false, target: null, error: '' })

function confirmDelete(cat) {
  deleteModal.target = cat
  deleteModal.error  = ''
  deleteModal.show   = true
}

async function handleDelete() {
  isSaving.value    = true
  deleteModal.error = ''
  try {
    await store.deleteCategory(deleteModal.target.id)
    deleteModal.show = false
    toast.success('Group berhasil dihapus.')
    await store.fetchCategories()
  } catch (err) {
    deleteModal.error = err?.response?.data?.detail || 'Gagal menghapus group.'
    toast.error(deleteModal.error)
  } finally {
    isSaving.value = false
  }
}

onMounted(() => store.fetchCategories())
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