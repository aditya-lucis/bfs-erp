<template>
  <Panel title="List of Projects" subtitle="Project | List of Project">

    <!-- Search / Filter Toolbar (Sokka ERP style) -->
    <div class="bg-gray-50 border border-gray-200 rounded-xl p-4 mb-6 space-y-4">
      <div class="flex flex-wrap items-center gap-3">
        <span class="text-xs font-semibold text-gray-500 uppercase tracking-wider">Search by:</span>
        <div class="flex items-center border border-gray-200 rounded-lg overflow-hidden bg-white">
          <span class="px-3 py-1.5 bg-gray-50 text-xs text-gray-500 border-r border-gray-200">Project Name/Code</span>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Type Project Name or Code..."
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

      <!-- Action & Workflow Buttons -->
      <div class="flex flex-wrap items-center gap-2 pt-2 border-t border-gray-200">
        <button
          v-if="canCreate"
          @click="openAddModal"
          class="px-3 py-1.5 bg-bfs-gold hover:bg-bfs-gold-dark text-white text-xs font-medium rounded-lg transition-colors flex items-center gap-1.5 cursor-pointer"
        >
          <Plus class="w-3.5 h-3.5" /> New Project
        </button>

        <button
          @click="handleActionSelected('start')"
          :disabled="!selectedProject"
          class="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-medium rounded-lg transition-colors disabled:opacity-50 cursor-pointer disabled:cursor-not-allowed"
        >
          Start Project
        </button>

        <button
          @click="handleActionSelected('cancel')"
          :disabled="!selectedProject"
          class="px-3 py-1.5 bg-red-600 hover:bg-red-700 text-white text-xs font-medium rounded-lg transition-colors disabled:opacity-50 cursor-pointer disabled:cursor-not-allowed"
        >
          Cancel Project
        </button>

        <div class="relative inline-block">
          <select
            @change="handleStatusChange"
            :disabled="!selectedProject"
            class="px-3 py-1.5 border border-gray-200 text-xs font-medium rounded-lg bg-white hover:bg-gray-50 focus:outline-none disabled:opacity-50 cursor-pointer disabled:cursor-not-allowed"
            v-model="changeStatusModel"
          >
            <option value="" disabled selected>Change Status Project</option>
            <option value="not_start">Not Start</option>
            <option value="start">Start</option>
            <option value="cancel">Cancel</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="store.loading" class="flex justify-center py-16">
      <Loader2 class="w-6 h-6 animate-spin text-bfs-gold" />
    </div>

    <!-- Data Table -->
    <div v-else-if="store.projects.length" class="border border-gray-200 rounded-xl overflow-hidden bg-white shadow-sm">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse min-w-[1200px]">
          <thead>
            <tr class="bg-gray-50 border-b border-gray-200 text-xs font-semibold text-gray-600 uppercase tracking-wider">
              <th class="py-3 px-4 w-12 text-center">Select</th>
              <th class="py-3 px-4 w-12 text-center">No.</th>
              <th class="py-3 px-4">Project Code</th>
              <th class="py-3 px-4">Project Name</th>
              <th class="py-3 px-4">RAP Name</th>
              <th class="py-3 px-4">Project Manager</th>
              <th class="py-3 px-4">Customer Name</th>
              <th class="py-3 px-4">Start Date</th>
              <th class="py-3 px-4">End Date</th>
              <th class="py-3 px-4">Project Type</th>
              <th class="py-3 px-4 text-right">Amount</th>
              <th class="py-3 px-4 text-center">Project Status</th>
              <th class="py-3 px-4 w-20 text-center">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr
              v-for="(proj, idx) in store.projects"
              :key="proj.id"
              class="hover:bg-yellow-50/20 transition-colors text-sm text-gray-700"
              :class="{ 'bg-yellow-50/40': selectedProjectId === proj.id }"
              @click="selectedProjectId = proj.id"
            >
              <td class="py-3 px-4 text-center" @click.stop>
                <input
                  type="radio"
                  name="selected_project"
                  :value="proj.id"
                  v-model="selectedProjectId"
                  class="rounded-full border-gray-300 text-bfs-gold focus:ring-bfs-gold"
                />
              </td>
              <td class="py-3 px-4 text-center font-medium text-gray-400">{{ idx + 1 }}</td>
              <td class="py-3 px-4 font-mono text-xs font-semibold text-gray-900">{{ proj.project_code }}</td>
              <td class="py-3 px-4 font-medium text-gray-800">{{ proj.project_name }}</td>
              <td class="py-3 px-4 text-gray-500">{{ proj.project_name }}(-)</td>
              <td class="py-3 px-4 text-xs">{{ proj.project_manager_name }}</td>
              <td class="py-3 px-4 text-xs font-medium text-gray-800">{{ proj.customer_name }}</td>
              <td class="py-3 px-4 text-xs">{{ formatDate(proj.start_date) }}</td>
              <td class="py-3 px-4 text-xs">{{ proj.end_date ? formatDate(proj.end_date) : '-' }}</td>
              <td class="py-3 px-4 text-xs">{{ proj.project_type_name }}</td>
              <td class="py-3 px-4 text-right font-mono text-xs font-semibold text-gray-900">
                {{ formatCurrency(proj.amount, proj.currency_id) }}
              </td>
              <td class="py-3 px-4 text-center">
                <span
                  class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider"
                  :class="getStatusBadgeClass(proj.status)"
                >
                  {{ formatStatus(proj.status) }}
                </span>
              </td>
              <td class="py-3 px-4 text-center" @click.stop>
                <div class="flex justify-center gap-1.5">
                  <button
                    v-if="canUpdate"
                    @click="openEditModal(proj)"
                    class="p-1 text-gray-400 hover:text-bfs-gold transition-colors"
                    title="Edit"
                  >
                    <Pencil class="w-3.5 h-3.5" />
                  </button>
                  <button
                    v-if="canDelete"
                    @click="confirmDelete(proj)"
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
      <p class="text-sm">No project data found.</p>
      <button v-if="canCreate" @click="openAddModal" class="mt-3 text-sm text-bfs-gold hover:underline">
        Create the first Project
      </button>
    </div>

    <!-- Add/Edit Modal (Premium Drawer/Modal layout) -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="modal.show" class="fixed inset-0 z-50 overflow-y-auto">
          <div class="fixed inset-0 bg-black/40" @click="modal.show = false" />
          <div class="flex min-h-full items-start justify-center p-4 py-8">
            <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-lg z-10" @click.stop>
              
              <!-- Modal Header -->
              <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
                <h3 class="text-base font-semibold text-gray-800">
                  {{ modal.mode === 'add' ? 'Create Project' : 'Edit Project' }}
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
              <div class="px-6 py-4 space-y-4 max-h-[70vh] overflow-y-auto">
                <div class="grid grid-cols-2 gap-4">
                  <FormField label="Project Type *" required :error="formError.fieldErrors.project_type">
                    <SearchableSelect
                      v-model="form.project_type"
                      :options="store.projectTypes"
                      value-key="id"
                      label-key="name"
                      placeholder="-- Select Type --"
                      search-placeholder="Search project type..."
                    />
                  </FormField>

                  <FormField label="Project Category *" required :error="formError.fieldErrors.project_category">
                    <SearchableSelect
                      v-model="form.project_category"
                      :options="store.projectCategories"
                      value-key="id"
                      :label-fn="(cat) => `[${cat.code}] - ${cat.name}`"
                      placeholder="-- Select Category --"
                      search-placeholder="Search project category..."
                    />
                  </FormField>
                </div>

                <div class="grid grid-cols-3 gap-4">
                  <FormField label="Site Code *" required :error="formError.fieldErrors.site_code">
                    <input v-model="form.site_code" type="text" class="form-input" placeholder="." />
                  </FormField>
                  <FormField label="Site ID *" required :error="formError.fieldErrors.site_id">
                    <input v-model="form.site_id" type="text" class="form-input" placeholder="-" />
                  </FormField>
                  <FormField label="Site Name *" required :error="formError.fieldErrors.site_name">
                    <input v-model="form.site_name" type="text" class="form-input" placeholder="Site Name" />
                  </FormField>
                </div>

                <FormField label="Project Name *" required :error="formError.fieldErrors.project_name">
                  <input
                    v-model="form.project_name"
                    type="text"
                    class="form-input"
                    placeholder="e.g. OPEX-TAX/RSHJR/08/2026"
                  />
                </FormField>

                <FormField label="Customer *" required :error="formError.fieldErrors.customer">
                  <SearchableSelect
                    v-model="form.customer"
                    :options="salesStore.customers"
                    value-key="id"
                    :label-fn="(c) => `[${c.code}] - ${c.name}`"
                    placeholder="-- Select Customer --"
                    search-placeholder="Search customer..."
                  />
                </FormField>

                <div class="grid grid-cols-3 gap-4">
                  <FormField label="Currency" :error="formError.fieldErrors.currency_id">
                    <select v-model="form.currency_id" class="form-input">
                      <option value="IDR">IDR</option>
                      <option value="USD">USD</option>
                      <option value="EUR">EUR</option>
                      <option value="SGD">SGD</option>
                    </select>
                  </FormField>
                  <FormField label="Rate" :error="formError.fieldErrors.exchange_rate">
                    <input v-model="form.exchange_rate" type="number" step="0.01" class="form-input font-mono" />
                  </FormField>
                  <FormField label="Project Amount" :error="formError.fieldErrors.amount">
                    <input v-model="form.amount" type="number" step="1000" class="form-input font-mono" />
                  </FormField>
                </div>

                <div class="grid grid-cols-2 gap-4">
                  <FormField label="Start Date *" required :error="formError.fieldErrors.start_date">
                    <input v-model="form.start_date" type="date" class="form-input" />
                  </FormField>
                  <FormField label="End Date" :error="formError.fieldErrors.end_date">
                    <input v-model="form.end_date" type="date" class="form-input" />
                  </FormField>
                </div>

                <FormField label="Project Manager *" required :error="formError.fieldErrors.project_manager">
                  <SearchableSelect
                    v-model="form.project_manager"
                    :options="orgStore.employees"
                    value-key="id"
                    :label-fn="(emp) => `${emp.full_name} (${emp.position_name || 'No Position'})`"
                    placeholder="-- Select Project Manager --"
                    search-placeholder="Search project manager..."
                  />
                </FormField>
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
              <h3 class="text-base font-semibold text-gray-800">Delete Project?</h3>
              <p class="text-sm text-gray-500">
                Are you sure you want to delete Project <span class="font-semibold text-gray-700">"{{ deleteModal.target?.project_name }}"</span>? This action cannot be undone.
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
import { useRoute } from 'vue-router'
import { useProjectsStore } from '../../stores/projects.js'
import { useSalesStore } from '../../stores/sales.js'
import { useOrganizationStore } from '../../stores/organization.js'
import { usePermission } from '../../composables/usePermission.js'
import { useFormError } from '../../composables/useFormError.js'
import Panel from '../../components/Panel.vue'
import FormField from '../../components/FormField.vue'
import SearchableSelect from '../../components/SearchableSelect.vue'
import { useToast } from '../../composables/useToast.js'
import { Plus, Pencil, Trash2, Save, X, Loader2, Search, Briefcase, AlertCircle } from 'lucide-vue-next'

const route = useRoute()
const store = useProjectsStore()
const salesStore = useSalesStore()
const orgStore = useOrganizationStore()

// Determine function code dynamically based on active route path
const permissionCode = computed(() => {
  if (route.path.includes('commercial')) {
    return 'COMMERCIAL-LIST-OF-PROJECTS'
  }
  return 'PROJECTS-LIST-OF-PROJECTS'
})

const { canCreate, canUpdate, canDelete } = usePermission(permissionCode)
const formError = useFormError()
const isSaving = ref(false)
const toast = useToast()
const searchQuery = ref('')

// Selection & Actions
const selectedProjectId = ref(null)
const changeStatusModel = ref('')

const selectedProject = computed(() => {
  return store.projects.find(p => p.id === selectedProjectId.value) || null
})

function handleSearch() {
  store.fetchProjects({ search: searchQuery.value.trim() })
}

function handleShowAll() {
  searchQuery.value = ''
  store.fetchProjects()
}

async function handleActionSelected(action) {
  if (!selectedProjectId.value) return
  try {
    await store.actionProject(selectedProjectId.value, action)
    toast.success(`Project successfully updated to ${action} status.`)
    await store.fetchProjects()
  } catch (err) {
    const errorMsg = err?.response?.data?.detail || err?.response?.data?.[0] || 'Failed to update project status.'
    toast.error(errorMsg)
  }
}

async function handleStatusChange(e) {
  const statusVal = e.target.value
  if (!selectedProjectId.value || !statusVal) return
  try {
    await store.actionProject(selectedProjectId.value, 'change_status', statusVal)
    toast.success(`Project status successfully changed.`)
    changeStatusModel.value = ''
    await store.fetchProjects()
  } catch (err) {
    const errorMsg = err?.response?.data?.detail || err?.response?.data?.[0] || 'Failed to change status.'
    toast.error(errorMsg)
  }
}

// Helpers for default dates
const getTodayStr = (offset = 0) => {
  const d = new Date()
  d.setDate(d.getDate() + offset)
  const yyyy = d.getFullYear()
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${yyyy}-${mm}-${dd}`
}

// ── Modal & Form ──
const modal = reactive({ show: false, mode: 'add', editId: null })
const form = reactive({
  project_type: '',
  project_category: '',
  site_code: '.',
  site_id: '-',
  site_name: '',
  project_name: '',
  customer: '',
  currency_id: 'IDR',
  exchange_rate: 1.00,
  start_date: getTodayStr(0),
  end_date: getTodayStr(1),
  project_manager: '',
  amount: 0.00
})

function openAddModal() {
  modal.show = true
  modal.mode = 'add'
  modal.editId = null
  formError.clearErrors()
  Object.assign(form, {
    project_type: '',
    project_category: '',
    site_code: '.',
    site_id: '-',
    site_name: '',
    project_name: '',
    customer: '',
    currency_id: 'IDR',
    exchange_rate: 1.00,
    start_date: getTodayStr(0),
    end_date: getTodayStr(1),
    project_manager: '',
    amount: 0.00
  })
}

function openEditModal(proj) {
  modal.show = true
  modal.mode = 'edit'
  modal.editId = proj.id
  formError.clearErrors()
  Object.assign(form, {
    project_type: proj.project_type,
    project_category: proj.project_category,
    site_code: proj.site_code,
    site_id: proj.site_id,
    site_name: proj.site_name,
    project_name: proj.project_name,
    customer: proj.customer,
    currency_id: proj.currency_id,
    exchange_rate: parseFloat(proj.exchange_rate),
    start_date: proj.start_date,
    end_date: proj.end_date || '',
    project_manager: proj.project_manager,
    amount: parseFloat(proj.amount)
  })
}

function validate() {
  formError.clearErrors()
  let valid = true
  if (!form.project_name.trim()) {
    formError.fieldErrors.project_name = 'Project name is required.'
    valid = false
  }
  if (!form.customer) {
    formError.fieldErrors.customer = 'Customer is required.'
    valid = false
  }
  if (!form.start_date) {
    formError.fieldErrors.start_date = 'Start date is required.'
    valid = false
  }
  if (!form.project_manager) {
    formError.fieldErrors.project_manager = 'Project manager is required.'
    valid = false
  }
  return valid
}

async function handleSubmit() {
  if (!validate()) return
  isSaving.value = true
  try {
    const payload = { ...form }
    if (!payload.end_date) delete payload.end_date
    if (modal.mode === 'add') {
      await store.createProject(payload)
      toast.success('Project successfully created.')
    } else {
      await store.updateProject(modal.editId, payload)
      toast.success('Project successfully updated.')
    }
    modal.show = false
    await store.fetchProjects()
  } catch (err) {
    formError.parseApiError(err)
    toast.error('Failed to save project.')
  } finally {
    isSaving.value = false
  }
}

// ── Delete ──
const deleteModal = reactive({ show: false, target: null, error: '' })

function confirmDelete(proj) {
  deleteModal.target = proj
  deleteModal.error = ''
  deleteModal.show = true
}

async function handleDelete() {
  isSaving.value = true
  deleteModal.error = ''
  try {
    await store.deleteProject(deleteModal.target.id)
    deleteModal.show = false
    toast.success('Project successfully deleted.')
    await store.fetchProjects()
  } catch (err) {
    deleteModal.error = err?.response?.data?.detail || 'Failed to delete project.'
    toast.error('Failed to delete project.')
  } finally {
    isSaving.value = false
  }
}

// Helpers
function formatDate(val) {
  if (!val) return ''
  const d = new Date(val)
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  return `${d.getDate().toString().padStart(2, '0')} ${months[d.getMonth()]} ${d.getFullYear()}`
}

function formatCurrency(val, currency = 'IDR') {
  return new Intl.NumberFormat('id-ID', { style: 'currency', currency }).format(val)
}

function formatStatus(status) {
  if (status === 'not_start') return 'Not Start'
  if (status === 'start') return 'Start'
  if (status === 'cancel') return 'Cancel'
  return status
}

function getStatusBadgeClass(status) {
  if (status === 'not_start') return 'bg-gray-100 text-gray-700'
  if (status === 'start') return 'bg-emerald-100 text-emerald-700'
  if (status === 'cancel') return 'bg-red-100 text-red-700'
  return 'bg-blue-100 text-blue-700'
}

onMounted(() => {
  store.fetchProjects()
  store.fetchProjectTypes()
  store.fetchProjectCategories()
  salesStore.fetchCustomers()
  orgStore.fetchEmployees()
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
