<template>
  <Panel title="RAP Type" subtitle="Project | RAP | RAP Type">

    <!-- Toolbar/Search (mirip Sokka ERP) -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
      <div class="flex flex-wrap items-center gap-2">
        <span class="text-xs font-semibold text-gray-500 uppercase tracking-wider">Search by Name:</span>
        <div class="flex items-center border border-gray-200 rounded-lg overflow-hidden bg-white">
          <span class="px-3 py-1.5 bg-gray-50 text-xs text-gray-500 border-r border-gray-200">Any Part of Field</span>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Type RAP Type Name..."
            class="px-3 py-1.5 text-xs focus:outline-none w-48 sm:w-64"
            @keyup.enter="handleSearch"
          />
        </div>
        <button
          @click="handleSearch"
          class="px-3 py-1.5 bg-bfs-navy hover:bg-bfs-navy-dark text-white text-xs font-medium rounded-lg transition-colors flex items-center gap-1.5 cursor-pointer"
        >
          <Search class="w-3.5 h-3.5" /> Search
        </button>
        <button
          @click="handleShowAll"
          class="btn-secondary text-xs px-3 py-1.5 flex items-center gap-1.5"
        >
          Show All
        </button>
      </div>

      <button
        v-if="canCreate"
        @click="openAddModal"
        class="btn-primary text-xs flex items-center gap-1.5 self-start md:self-auto"
      >
        <Plus class="w-3.5 h-3.5" /> Add RAP Type
      </button>
    </div>

    <!-- Loading -->
    <div v-if="store.loading" class="flex justify-center py-16">
      <Loader2 class="w-6 h-6 animate-spin text-bfs-gold" />
    </div>

    <!-- Table List -->
    <div v-else-if="store.rapTypes.length" class="border border-gray-200 rounded-xl overflow-hidden bg-white shadow-sm">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-gray-50 border-b border-gray-200 text-xs font-semibold text-gray-600 uppercase tracking-wider">
              <th class="py-3 px-4 w-12 text-center">
                <input type="checkbox" class="rounded border-gray-300 text-bfs-gold focus:ring-bfs-gold" />
              </th>
              <th class="py-3 px-4 w-16 text-center">No.</th>
              <th class="py-3 px-4">Name</th>
              <th class="py-3 px-4 w-24 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr
              v-for="(type, idx) in store.rapTypes"
              :key="type.id"
              class="hover:bg-yellow-50/20 transition-colors text-sm text-gray-700"
            >
              <td class="py-3 px-4 text-center">
                <input type="checkbox" class="rounded border-gray-300 text-bfs-gold focus:ring-bfs-gold" />
              </td>
              <td class="py-3 px-4 text-center font-medium text-gray-400">{{ idx + 1 }}.</td>
              <td class="py-3 px-4 font-medium text-gray-800">{{ type.name }}</td>
              <td class="py-3 px-4 text-right">
                <div class="flex justify-end gap-1.5">
                  <button
                    v-if="canUpdate"
                    @click="openEditModal(type)"
                    class="p-1 text-gray-400 hover:text-bfs-gold transition-colors"
                    title="Edit"
                  >
                    <Pencil class="w-3.5 h-3.5" />
                  </button>
                  <button
                    v-if="canDelete"
                    @click="confirmDelete(type)"
                    class="p-1 text-gray-400 hover:text-red-500 transition-colors"
                    title="Delete"
                  >
                    <Trash2 class="w-3.5 h-3.5" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="flex flex-col items-center justify-center py-20 text-gray-400">
      <FileText class="w-12 h-12 mb-3 text-gray-300" />
      <p class="text-sm">No RAP Type data found.</p>
      <button v-if="canCreate" @click="openAddModal" class="mt-3 text-sm text-bfs-gold hover:underline">
        Create the first RAP Type
      </button>
    </div>

    <!-- Add/Edit Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="modal.show" class="fixed inset-0 z-50 overflow-y-auto">
          <div class="fixed inset-0 bg-black/40" @click="modal.show = false" />
          <div class="flex min-h-full items-start justify-center p-4 py-12">
            <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-md z-10" @click.stop>
              
              <!-- Modal Header -->
              <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
                <h3 class="text-base font-semibold text-gray-800">
                  {{ modal.mode === 'add' ? 'Create RAP Type' : 'Edit RAP Type' }}
                </h3>
                <button @click="modal.show = false" class="text-gray-400 hover:text-gray-600">
                  <X class="w-5 h-5" />
                </button>
              </div>

              <!-- Form Error Alert -->
              <div v-if="formError.serverError.value" class="mx-6 mt-4 px-4 py-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
                <AlertCircle class="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
                <p class="text-sm text-red-600">{{ formError.serverError.value }}</p>
              </div>

              <!-- Modal Form Content -->
              <div class="px-6 py-4 space-y-4">
                <FormField label="RAP Type Name" required :error="formError.fieldErrors.name">
                  <input
                    v-model="form.name"
                    type="text"
                    class="form-input"
                    :class="{ 'border-red-300': formError.fieldErrors.name }"
                    placeholder="e.g. Sarana Pendukung Rumah Sakit"
                    @input="delete formError.fieldErrors.name"
                  />
                </FormField>
              </div>

              <!-- Modal Actions -->
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

    <!-- Delete Confirmation Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="deleteModal.show" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-black/40" @click="deleteModal.show = false" />
          <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6 z-10">
            <div class="flex flex-col items-center text-center gap-3">
              <div class="w-12 h-12 rounded-full bg-red-100 flex items-center justify-center">
                <Trash2 class="w-6 h-6 text-red-500" />
              </div>
              <h3 class="text-base font-semibold text-gray-800">Delete RAP Type?</h3>
              <p class="text-sm text-gray-500">
                Are you sure you want to delete RAP Type <span class="font-semibold text-gray-700">"{{ deleteModal.target?.name }}"</span>? This action cannot be undone.
              </p>
            </div>
            <div v-if="deleteModal.error" class="mt-3 px-4 py-2 bg-red-50 border border-red-200 rounded-lg">
              <p class="text-sm text-red-600 text-center">{{ deleteModal.error }}</p>
            </div>
            <div class="flex gap-2 mt-5">
              <button @click="deleteModal.show = false" class="btn-secondary text-sm flex-1">Cancel</button>
              <button
                @click="handleDelete"
                :disabled="isSaving"
                class="flex-1 text-sm py-2 px-4 bg-red-500 hover:bg-red-600 text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-1.5 disabled:opacity-60 cursor-pointer"
              >
                <Loader2 v-if="isSaving" class="w-3.5 h-3.5 animate-spin" />
                <Trash2 v-else class="w-3.5 h-3.5" />
                Delete
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

  </Panel>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useProjectsStore } from '../../stores/projects.js'
import { usePermission } from '../../composables/usePermission.js'
import { useFormError } from '../../composables/useFormError.js'
import Panel from '../../components/Panel.vue'
import FormField from '../../components/FormField.vue'
import { useToast } from '../../composables/useToast.js'
import { Plus, Pencil, Trash2, Save, X, Loader2, Search, FileText, AlertCircle } from 'lucide-vue-next'

const store = useProjectsStore()
const { canCreate, canUpdate, canDelete } = usePermission('PROJECTS-RAP-TYPE')
const formError = useFormError()
const isSaving = ref(false)
const toast = useToast()
const searchQuery = ref('')

function handleSearch() {
  store.fetchRapTypes({ search: searchQuery.value.trim() })
}

function handleShowAll() {
  searchQuery.value = ''
  store.fetchRapTypes()
}

// ── Modal & Form ──
const modal = reactive({ show: false, mode: 'add', editId: null })
const form = reactive({ name: '' })

function openAddModal() {
  modal.show = true
  modal.mode = 'add'
  modal.editId = null
  formError.clearErrors()
  form.name = ''
}

function openEditModal(type) {
  modal.show = true
  modal.mode = 'edit'
  modal.editId = type.id
  formError.clearErrors()
  form.name = type.name
}

function validate() {
  formError.clearErrors()
  let valid = true
  if (!form.name.trim()) {
    formError.fieldErrors.name = 'RAP Type name is required.'
    valid = false
  }
  return valid
}

async function handleSubmit() {
  if (!validate()) return
  isSaving.value = true
  try {
    if (modal.mode === 'add') {
      await store.createRapType({ name: form.name })
      toast.success('RAP Type successfully created.')
    } else {
      await store.updateRapType(modal.editId, { name: form.name })
      toast.success('RAP Type successfully updated.')
    }
    modal.show = false
    await store.fetchRapTypes()
  } catch (err) {
    formError.parseApiError(err)
    toast.error('Failed to save RAP Type.')
  } finally {
    isSaving.value = false
  }
}

// ── Delete ──
const deleteModal = reactive({ show: false, target: null, error: '' })

function confirmDelete(type) {
  deleteModal.target = type
  deleteModal.error = ''
  deleteModal.show = true
}

async function handleDelete() {
  isSaving.value = true
  deleteModal.error = ''
  try {
    await store.deleteRapType(deleteModal.target.id)
    deleteModal.show = false
    toast.success('RAP Type successfully deleted.')
    await store.fetchRapTypes()
  } catch (err) {
    deleteModal.error = err?.response?.data?.detail || 'Failed to delete RAP Type.'
    toast.error('Failed to delete RAP Type.')
  } finally {
    isSaving.value = false
  }
}

onMounted(() => {
  store.fetchRapTypes()
})
</script>

<style scoped>
@reference "../../style.css";
.form-input {
  @apply w-full px-3 py-2 text-sm border border-gray-200 rounded-lg
         focus:outline-none focus:ring-2 focus:ring-bfs-gold/40 focus:border-bfs-gold
         transition-all bg-white disabled:bg-gray-50 disabled:cursor-not-allowed;
}
.btn-primary {
  @apply px-4 py-2 bg-bfs-gold hover:bg-bfs-gold-dark text-white font-medium rounded-lg transition-colors disabled:opacity-60 cursor-pointer;
}
.btn-secondary {
  @apply px-4 py-2 border border-gray-200 text-gray-600 hover:bg-gray-50 rounded-lg transition-colors cursor-pointer;
}
.modal-enter-active, .modal-leave-active { transition: opacity 0.2s; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
</style>
