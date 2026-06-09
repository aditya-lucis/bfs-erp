<template>
  <Panel title="Vendor Category" subtitle="Purchases | Vendor Category">

    <!-- Toolbar -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
      <div class="relative">
        <Search class="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-400" />
        <input
          v-model="search"
          type="text"
          placeholder="Cari kategori..."
          class="pl-8 pr-3 py-1.5 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-bfs-gold/40 focus:border-bfs-gold w-56"
        />
      </div>
      <button
        v-if="canCreate"
        @click="openAddModal"
        class="btn-primary text-xs flex items-center gap-1.5"
      >
        <Plus class="w-3.5 h-3.5" /> Add Category
      </button>
    </div>

    <!-- Loading -->
    <div v-if="store.loading" class="flex justify-center py-16">
      <Loader2 class="w-6 h-6 animate-spin text-bfs-gold" />
    </div>

    <!-- Tree Category (mirip Sokka) -->
    <div v-else-if="filteredCategories.length" class="border border-gray-200 rounded-xl overflow-hidden bg-white max-w-md">
      <div class="flex items-center gap-2 px-4 py-2.5 bg-gray-50 border-b border-gray-200 text-sm font-semibold text-gray-700">
        <FolderOpen class="w-4 h-4 text-bfs-gold" />
        Category
      </div>
      <ul class="py-1">
        <li
          v-for="cat in filteredCategories"
          :key="cat.id"
          class="group flex items-center gap-2 px-4 py-2 hover:bg-yellow-50/40 transition-colors"
        >
          <FolderOpen class="w-4 h-4 text-gray-400 shrink-0" />
          <span class="text-sm text-gray-800 flex-1">
            <span class="font-mono text-gray-500">{{ cat.code }}</span>
            <span class="text-gray-400 mx-1">-</span>
            {{ cat.name }}
          </span>
          <div class="flex gap-1 opacity-0 group-hover:opacity-100">
            <button v-if="canUpdate" @click="openEditModal(cat)" class="p-1 text-gray-400 hover:text-bfs-gold" title="Edit">
              <Pencil class="w-3.5 h-3.5" />
            </button>
            <button v-if="canDelete" @click="confirmDelete(cat)" class="p-1 text-gray-400 hover:text-red-500" title="Hapus">
              <Trash2 class="w-3.5 h-3.5" />
            </button>
          </div>
        </li>
      </ul>
    </div>

    <!-- Empty -->
    <div v-else class="flex flex-col items-center justify-center py-20 text-gray-400">
      <FolderOpen class="w-10 h-10 mb-3" />
      <p class="text-sm">Belum ada vendor category.</p>
      <button v-if="canCreate" @click="openAddModal" class="mt-3 text-sm text-bfs-gold hover:underline">
        Buat kategori pertama
      </button>
    </div>

    <!-- ── Form Modal ── -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="modal.show" class="fixed inset-0 z-50 overflow-y-auto">
          <div class="fixed inset-0 bg-black/45" @click="modal.show = false" />
          <div class="flex min-h-full items-start justify-center p-4 py-8">
            <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-sm z-10" @click.stop>

              <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
                <h3 class="text-base font-semibold text-gray-800">
                  {{ modal.mode === 'add' ? 'Add Vendor Category' : 'Edit Vendor Category' }}
                </h3>
                <button @click="modal.show = false" class="text-gray-400 hover:text-gray-600">
                  <X class="w-5 h-5" />
                </button>
              </div>

              <div v-if="formError.serverError.value" class="mx-6 mt-4 px-4 py-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
                <AlertCircle class="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
                <p class="text-sm text-red-600">{{ formError.serverError.value }}</p>
              </div>

              <div class="px-6 py-4 space-y-4">
                <FormField label="Kategori Code" required :error="formError.fieldErrors.code">
                  <input
                    v-model="form.code"
                    class="form-input font-mono uppercase"
                    :class="{ 'border-red-300': formError.fieldErrors.code }"
                    placeholder="e.g. EXP"
                    :disabled="modal.mode === 'edit'"
                    @input="handleCodeInput"
                  />
                  <p v-if="modal.mode === 'add'" class="mt-1 text-xs text-gray-400">
                    Kode unik. Hanya huruf kapital dan angka.
                  </p>
                </FormField>

                <FormField label="Nama Kategori" required :error="formError.fieldErrors.name">
                  <input
                    v-model="form.name"
                    class="form-input"
                    :class="{ 'border-red-300': formError.fieldErrors.name }"
                    placeholder="e.g. Export / Import"
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
          <div class="absolute inset-0 bg-black/45" @click="deleteModal.show = false" />
          <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6 z-10">
            <div class="flex flex-col items-center text-center gap-3">
              <div class="w-12 h-12 rounded-full bg-red-100 flex items-center justify-center">
                <Trash2 class="w-6 h-6 text-red-500" />
              </div>
              <h3 class="text-base font-semibold text-gray-800">Hapus Kategori?</h3>
              <p class="text-sm text-gray-500">
                Kategori <span class="font-mono font-semibold text-gray-700">{{ deleteModal.target?.name }}</span>
                akan dihapus permanen. Kategori yang masih terikat dengan vendor tidak dapat dihapus.
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
import { usePurchaseStore } from '../../stores/purchase.js'
import { usePermission } from '../../composables/usePermission.js'
import { useFormError } from '../../composables/useFormError.js'
import Panel from '../../components/Panel.vue'
import FormField from '../../components/FormField.vue'
import { useToast } from '../../composables/useToast.js'
import { Plus, Pencil, Trash2, Save, X, Loader2, Search, FolderOpen, AlertCircle } from 'lucide-vue-next'

const store = usePurchaseStore()
const { canCreate, canUpdate, canDelete } = usePermission('PURCHASES-VENDOR-CATEGORY')
const formError = useFormError()
const isSaving  = ref(false)
const toast = useToast()
const search    = ref('')

const filteredCategories = computed(() => {
  let list = store.categories
  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    list = list.filter(c => c.name.toLowerCase().includes(q) || c.code.toLowerCase().includes(q))
  }
  return list
})

// ── Form ───────────────────────────────────────────────────────────────────
const modal = reactive({ show: false, mode: 'add', editId: null })
const form  = reactive({ code: '', name: '' })

function openAddModal() {
  modal.show = true; modal.mode = 'add'; modal.editId = null
  formError.clearErrors()
  Object.assign(form, { code: '', name: '' })
}

function openEditModal(cat) {
  modal.show = true; modal.mode = 'edit'; modal.editId = cat.id
  formError.clearErrors()
  Object.assign(form, { code: cat.code, name: cat.name })
}

function handleCodeInput(e) {
  const cleaned = e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, '')
  form.code = cleaned
  delete formError.fieldErrors.code
}

function validate() {
  formError.clearErrors()
  let valid = true

  if (!form.code.trim()) {
    formError.fieldErrors.code = 'Kode kategori wajib diisi.'
    valid = false
  }
  if (!form.name.trim()) {
    formError.fieldErrors.name = 'Nama kategori wajib diisi.'
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
      await store.updateCategory(modal.editId, {
        code: form.code,
        name: form.name,
      })
    }
    modal.show = false
    toast.success('Kategori berhasil disimpan.')
    await store.fetchCategories()
  } catch (err) {
    formError.parseApiError(err)
    toast.error('Gagal menyimpan kategori.')
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
    toast.success('Kategori berhasil dihapus.')
    await store.fetchCategories()
  } catch (err) {
    deleteModal.error = err?.response?.data?.detail || 'Gagal menghapus kategori. Kategori ini mungkin masih terikat dengan data Vendor.'
    toast.error('Gagal menghapus kategori.')
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
.btn-primary   { @apply px-4 py-2 bg-bfs-gold hover:bg-bfs-gold-dark text-white font-medium rounded-lg transition-colors disabled:opacity-60 cursor-pointer; }
.btn-secondary { @apply px-4 py-2 border border-gray-200 text-gray-600 hover:bg-gray-50 rounded-lg transition-colors cursor-pointer; }
.modal-enter-active, .modal-leave-active { transition: opacity 0.2s; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
</style>
