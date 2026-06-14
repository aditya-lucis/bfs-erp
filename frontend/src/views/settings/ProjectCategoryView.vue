<template>
  <Panel title="Project Category" subtitle="Setting | Project Category">

    <!-- Toolbar -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
      <div class="relative">
        <Search class="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-400" />
        <input
          v-model="search"
          type="text"
          placeholder="Search category..."
          class="pl-8 pr-3 py-1.5 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-bfs-gold/40 focus:border-bfs-gold w-64 bg-white"
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
      <Loader2 class="w-7 h-7 animate-spin text-bfs-gold" />
    </div>

    <!-- Data Table -->
    <div v-else-if="filteredCategories.length" class="border border-gray-200 rounded-xl overflow-hidden bg-white shadow-sm">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse min-w-[800px]">
          <thead>
            <tr class="bg-gray-50 border-b border-gray-200 text-xs font-semibold text-gray-600 uppercase tracking-wider">
              <th class="py-3 px-4 w-12 text-center">No.</th>
              <th class="py-3 px-4">Code</th>
              <th class="py-3 px-4">Category Name</th>
              <th class="py-3 px-4">Pattern Group Name</th>
              <th class="py-3 px-4">Document Pattern</th>
              <th class="py-3 px-4 text-center">Status</th>
              <th class="py-3 px-4 w-24 text-center">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr
              v-for="(cat, idx) in filteredCategories"
              :key="cat.id"
              class="hover:bg-yellow-50/20 transition-colors text-sm text-gray-700"
            >
              <td class="py-3 px-4 text-center font-medium text-gray-400">{{ idx + 1 }}</td>
              <td class="py-3 px-4 font-mono text-xs font-semibold text-gray-900">{{ cat.code }}</td>
              <td class="py-3 px-4 font-medium text-gray-800">{{ cat.name }}</td>
              <td class="py-3 px-4 text-gray-500 text-xs">{{ cat.pattern_group_name || '-' }}</td>
              <td class="py-3 px-4 text-xs font-mono text-gray-600">{{ cat.document_pattern || '-' }}</td>
              <td class="py-3 px-4 text-center">
                <span
                  class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider"
                  :class="cat.is_active ? 'bg-emerald-100 text-emerald-700' : 'bg-gray-100 text-gray-700'"
                >
                  {{ cat.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td class="py-3 px-4 text-center">
                <div class="flex justify-center gap-1.5">
                  <button
                    v-if="canUpdate"
                    @click="openEditModal(cat)"
                    class="p-1 text-gray-400 hover:text-bfs-gold transition-colors"
                    title="Edit"
                  >
                    <Pencil class="w-3.5 h-3.5" />
                  </button>
                  <button
                    v-if="canDelete"
                    @click="confirmDelete(cat)"
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
      <Briefcase class="w-12 h-12 mb-3 text-gray-300" />
      <p class="text-sm">No project category data found.</p>
      <button v-if="canCreate" @click="openAddModal" class="mt-3 text-sm text-bfs-gold hover:underline">
        Create the first Category
      </button>
    </div>

    <!-- Add/Edit Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="modal.show" class="fixed inset-0 z-50 overflow-y-auto">
          <div class="fixed inset-0 bg-black/40" @click="modal.show = false" />
          <div class="flex min-h-full items-start justify-center p-4 py-8">
            <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-md z-10" @click.stop>
              
              <!-- Modal Header -->
              <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
                <h3 class="text-base font-semibold text-gray-800">
                  {{ modal.mode === 'add' ? 'Create Project Category' : 'Edit Project Category' }}
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
                <FormField label="Category Code *" required :error="formError.fieldErrors.code">
                  <input
                    v-model="form.code"
                    type="text"
                    class="form-input font-mono"
                    placeholder="e.g. PC005"
                    :disabled="modal.mode === 'edit'"
                  />
                  <p v-if="modal.mode === 'add'" class="mt-1 text-[11px] text-gray-400">
                    Will be auto-prefixed with your company code (e.g. RSHL-PC005).
                  </p>
                </FormField>

                <FormField label="Category Name *" required :error="formError.fieldErrors.name">
                  <input
                    v-model="form.name"
                    type="text"
                    class="form-input"
                    placeholder="e.g. Project Office"
                  />
                </FormField>

                <FormField label="Pattern Group Name" :error="formError.fieldErrors.pattern_group_name">
                  <input
                    v-model="form.pattern_group_name"
                    type="text"
                    class="form-input"
                    placeholder="e.g. Project Office Group"
                  />
                </FormField>

                <FormField label="Document Pattern" :error="formError.fieldErrors.document_pattern">
                  <input
                    v-model="form.document_pattern"
                    type="text"
                    class="form-input font-mono text-xs"
                    placeholder="e.g. PRJ-{YYYY}{MM}-{SEQ}"
                  />
                </FormField>

                <div class="flex items-center gap-3 pt-2">
                  <input
                    v-model="form.is_active"
                    type="checkbox"
                    id="cat_active"
                    class="w-4 h-4 rounded border-gray-300 text-bfs-gold focus:ring-bfs-gold"
                  />
                  <label for="cat_active" class="text-sm text-gray-700">Active</label>
                </div>
              </div>

              <!-- Modal Actions -->
              <div class="flex justify-end gap-2 px-6 py-4 border-t border-gray-100 bg-gray-50 rounded-b-2xl">
                <button @click="modal.show = false" class="btn-secondary text-sm">Cancel</button>
                <button @click="handleSubmit" :disabled="isSaving" class="btn-primary text-sm flex items-center gap-1.5">
                  <Loader2 v-if="isSaving" class="w-3.5 h-3.5 animate-spin" />
                  <Save v-else class="w-3.5 h-3.5" />
                  Save
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
              <h3 class="text-base font-semibold text-gray-800">Delete Category?</h3>
              <p class="text-sm text-gray-500">
                Are you sure you want to delete Project Category <span class="font-semibold text-gray-700">"{{ deleteModal.target?.name }}"</span>? This will make it inactive.
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
import { ref, reactive, computed, onMounted } from 'vue'
import { useProjectsStore } from '../../stores/projects.js'
import { usePermission } from '../../composables/usePermission.js'
import { useFormError } from '../../composables/useFormError.js'
import Panel from '../../components/Panel.vue'
import FormField from '../../components/FormField.vue'
import { useToast } from '../../composables/useToast.js'
import { Plus, Pencil, Trash2, Save, X, Loader2, Search, Briefcase, AlertCircle } from 'lucide-vue-next'

const store = useProjectsStore()
const { canCreate, canUpdate, canDelete } = usePermission('SETTINGS-PROJECT-CATEGORY')
const formError = useFormError()
const isSaving = ref(false)
const toast = useToast()
const search = ref('')

const filteredCategories = computed(() => {
  let list = store.projectCategories
  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    list = list.filter(c => 
      c.name.toLowerCase().includes(q) || 
      c.code.toLowerCase().includes(q) ||
      (c.pattern_group_name && c.pattern_group_name.toLowerCase().includes(q))
    )
  }
  return list
})

// Modal & Form State
const modal = reactive({ show: false, mode: 'add', editId: null })
const form = reactive({
  code: '',
  name: '',
  pattern_group_name: '',
  document_pattern: '',
  is_active: true
})

function openAddModal() {
  modal.show = true
  modal.mode = 'add'
  modal.editId = null
  formError.clearErrors()
  Object.assign(form, {
    code: '',
    name: '',
    pattern_group_name: '',
    document_pattern: '',
    is_active: true
  })
}

function openEditModal(cat) {
  modal.show = true
  modal.mode = 'edit'
  modal.editId = cat.id
  formError.clearErrors()
  // Clean prefix if any when editing? Actually the backend auto-prefixes or matches prefix on save.
  // We can just load the code as-is. Since edit code is disabled anyway, it's safe.
  Object.assign(form, {
    code: cat.code,
    name: cat.name,
    pattern_group_name: cat.pattern_group_name || '',
    document_pattern: cat.document_pattern || '',
    is_active: cat.is_active
  })
}

function validate() {
  formError.clearErrors()
  let valid = true
  if (!form.code.trim()) {
    formError.fieldErrors.code = 'Category code is required.'
    valid = false
  }
  if (!form.name.trim()) {
    formError.fieldErrors.name = 'Category name is required.'
    valid = false
  }
  return valid
}

async function handleSubmit() {
  if (!validate()) return
  isSaving.value = true
  try {
    const payload = { ...form }
    if (modal.mode === 'add') {
      await store.createProjectCategory(payload)
      toast.success('Project category successfully created.')
    } else {
      await store.updateProjectCategory(modal.editId, payload)
      toast.success('Project category successfully updated.')
    }
    modal.show = false
    await store.fetchProjectCategories()
  } catch (err) {
    formError.parseApiError(err)
    toast.error('Failed to save project category.')
  } finally {
    isSaving.value = false
  }
}

// Delete State
const deleteModal = reactive({ show: false, target: null, error: '' })

function confirmDelete(cat) {
  deleteModal.target = cat
  deleteModal.error = ''
  deleteModal.show = true
}

async function handleDelete() {
  isSaving.value = true
  deleteModal.error = ''
  try {
    await store.deleteProjectCategory(deleteModal.target.id)
    deleteModal.show = false
    toast.success('Project category successfully deleted (deactivated).')
    await store.fetchProjectCategories()
  } catch (err) {
    deleteModal.error = err?.response?.data?.detail || 'Failed to delete project category.'
    toast.error('Failed to delete project category.')
  } finally {
    isSaving.value = false
  }
}

onMounted(() => {
  store.fetchProjectCategories()
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
