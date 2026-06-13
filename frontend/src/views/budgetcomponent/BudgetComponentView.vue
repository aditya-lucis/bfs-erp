<template>
  <Panel title="Budget Component" subtitle="Finance | Budget Component">

    <!-- Toolbar -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
      <div class="flex items-center gap-2 flex-wrap">
        <!-- Filter Cost Category -->
        <select v-model="filterCostCategory" @change="load" class="text-sm border border-gray-200 rounded-lg px-3 py-1.5">
          <option value="">All Cost Category</option>
          <option value="hpp">HPP</option>
          <option value="revenue">REVENUE</option>
          <option value="target_hpp">TARGET_HPP</option>
          <option value="target_opex">TARGET_OPEX</option>
          <option value="opex">OPEX</option>
          <option value="capex">CAPEX</option>
          <option value="tax">TAX</option>
        </select>
        <!-- Filter Department -->
        <select v-model="filterDepartment" @change="load" class="text-sm border border-gray-200 rounded-lg px-3 py-1.5">
          <option value="">All Department</option>
          <option v-for="d in orgStore.departmentList" :key="d.id" :value="d.id">{{ d.name }}</option>
        </select>
        <!-- Filter Active -->
        <select v-model="filterActive" @change="load" class="text-sm border border-gray-200 rounded-lg px-3 py-1.5">
          <option value="">All Status</option>
          <option value="true">Active</option>
          <option value="false">Inactive</option>
        </select>
      </div>
      <button v-if="canCreate" @click="openAddModal" class="btn-primary text-xs flex items-center gap-1.5">
        <Plus class="w-3.5 h-3.5" /> Add Budget Component
      </button>
    </div>

    <!-- Loading -->
    <div v-if="store.loading" class="flex justify-center py-16">
      <Loader2 class="w-6 h-6 animate-spin text-bfs-gold" />
    </div>

    <!-- Table -->
    <div v-else-if="store.budgetComponents.length" class="border border-gray-200 rounded-xl overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm min-w-[800px]">
          <thead class="bg-gray-50 border-b border-gray-200">
            <tr>
              <th class="text-left px-4 py-2.5 text-[11px] font-semibold text-gray-500 uppercase w-12">No</th>
              <th class="text-left px-4 py-2.5 text-[11px] font-semibold text-gray-500 uppercase">Budget Component</th>
              <th class="text-left px-4 py-2.5 text-[11px] font-semibold text-gray-500 uppercase">Cost Category</th>
              <th class="text-left px-4 py-2.5 text-[11px] font-semibold text-gray-500 uppercase">Department</th>
              <th class="text-left px-4 py-2.5 text-[11px] font-semibold text-gray-500 uppercase">Cost of Unit</th>
              <th class="text-left px-4 py-2.5 text-[11px] font-semibold text-gray-500 uppercase w-20">Order No</th>
              <th class="text-left px-4 py-2.5 text-[11px] font-semibold text-gray-500 uppercase w-16">Active</th>
              <th class="text-left px-4 py-2.5 text-[11px] font-semibold text-gray-500 uppercase w-20">Template RAP</th>
              <th class="px-4 py-2.5 text-right text-[11px] font-semibold text-gray-500 uppercase w-28">Action</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-if="!store.budgetComponents.length">
              <td colspan="9" class="text-center py-10 text-gray-400">Tidak ada data</td>
            </tr>
            <tr v-for="(row, i) in store.budgetComponents" :key="row.id" class="hover:bg-gray-50/80">
              <td class="px-4 py-2.5 text-gray-500">{{ i + 1 }}</td>
              <td class="px-4 py-2.5 font-medium text-gray-800">{{ row.name }}</td>
              <td class="px-4 py-2.5">
                <span class="inline-flex px-2 py-0.5 rounded-full text-xs font-medium" :class="costCategoryClass(row.cost_category)">
                  {{ row.cost_category.toUpperCase() }}
                </span>
              </td>
              <td class="px-4 py-2.5 text-gray-600">{{ row.department_name }}</td>
              <td class="px-4 py-2.5 text-gray-600">{{ row.position_name || '—' }}</td>
              <td class="px-4 py-2.5 text-gray-600 font-mono text-xs">{{ row.order_no }}</td>
              <td class="px-4 py-2.5">
                <span v-if="row.is_active" class="text-green-600">✓</span>
                <span v-else class="text-red-500">✗</span>
              </td>
              <td class="px-4 py-2.5 text-gray-600 text-xs">
                <button
                  v-if="canAccessTemplateRAP"
                  @click="openTemplateRAP(row)"
                  class="inline-flex items-center justify-center w-8 h-8 rounded-lg transition-colors"
                  :class="row.template_rap === 'added' 
                    ? 'bg-green-100 text-green-600 hover:bg-green-200' 
                    : 'bg-gray-100 text-gray-400 hover:bg-gray-200'"
                  :title="row.template_rap === 'added' ? 'Edit Template RAP' : 'Add Template RAP'"
                >
                  <FileText v-if="row.template_rap === 'added'" class="w-4 h-4" />
                  <Plus v-else class="w-4 h-4" />
                </button>
                <span v-else class="text-gray-300">—</span>
              </td>
              <td class="px-4 py-2.5 text-right">
                <div class="flex justify-end gap-1">
                  <button v-if="canUpdate" @click="openEditModal(row)" class="p-1.5 text-gray-400 hover:text-bfs-gold rounded transition-colors" title="Edit">
                    <Pencil class="w-3.5 h-3.5" />
                  </button>
                  <button v-if="canDelete" @click="confirmDelete(row)" class="p-1.5 text-gray-400 hover:text-red-500 rounded transition-colors" title="Hapus">
                    <Trash2 class="w-3.5 h-3.5" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Empty -->
    <div v-else class="flex flex-col items-center justify-center py-20 text-gray-400">
      <Calculator class="w-10 h-10 mb-3" />
      <p class="text-sm">Belum ada budget component.</p>
    </div>

    <!-- ── Form Modal ── -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="modal.show" class="fixed inset-0 z-50 overflow-y-auto">
          <div class="fixed inset-0 bg-black/45" @click="modal.show = false" />
          <div class="flex min-h-full items-start justify-center p-4 py-8">
            <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-md z-10" @click.stop>

              <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
                <h3 class="text-base font-semibold text-gray-800">
                  {{ modal.mode === 'add' ? 'Add Budget Component' : 'Edit Budget Component' }}
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
                <!-- Preview: Auto-generated Name -->
                <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
                  <label class="text-xs text-gray-500 uppercase font-semibold">Component Budget (Auto)</label>
                  <p class="text-sm font-mono text-gray-800 mt-1">{{ previewName }}</p>
                </div>

                <!-- Cost Category -->
                <FormField label="Cost Category" required :error="formError.fieldErrors.cost_category">
                  <select v-model="form.cost_category" class="form-input" :class="{ 'border-red-300': formError.fieldErrors.cost_category }">
                    <option value="">— Pilih —</option>
                    <option value="hpp">HPP</option>
                    <option value="revenue">REVENUE</option>
                    <option value="target_hpp">TARGET_HPP</option>
                    <option value="target_opex">TARGET_OPEX</option>
                    <option value="opex">OPEX</option>
                    <option value="capex">CAPEX</option>
                    <option value="tax">TAX</option>
                  </select>
                </FormField>

                <!-- Department -->
                <FormField label="Department" required :error="formError.fieldErrors.department">
                  <select v-model="form.department" @change="onDepartmentChange" class="form-input" :class="{ 'border-red-300': formError.fieldErrors.department }">
                    <option :value="null">— Pilih —</option>
                    <option v-for="d in orgStore.departmentList" :key="d.id" :value="d.id">{{ d.name }}</option>
                  </select>
                </FormField>

                <!-- Cost of Unit (Position) -->
                <FormField label="Cost of Unit" required :error="formError.fieldErrors.position">
                  <select 
                    v-model="form.position" 
                    :disabled="!form.department || loadingPositions" 
                    class="form-input" 
                    :class="{ 'border-red-300': formError.fieldErrors.position }"
                  >
                    <option :value="null">— Pilih —</option>
                    <option 
                      v-for="p in availablePositions" 
                      :key="p.id" 
                      :value="p.id"
                    >
                      {{ p.name }}
                    </option>
                  </select>
                  <p v-if="loadingPositions" class="text-xs text-gray-400 mt-1">Loading positions...</p>
                  <p v-else-if="form.department && !availablePositions.length && !loadingPositions" class="text-xs text-amber-600 mt-1">
                    Department ini tidak memiliki position.
                  </p>
                </FormField>

                <!-- Order No -->
                <FormField label="Order No" required :error="formError.fieldErrors.order_no">
                  <input v-model.number="form.order_no" type="number" class="form-input" :class="{ 'border-red-300': formError.fieldErrors.order_no }" />
                </FormField>

                <!-- Active -->
                <div class="flex items-center gap-2">
                  <input type="checkbox" v-model="form.is_active" id="is_active" class="rounded" />
                  <label for="is_active" class="text-sm text-gray-700">Active</label>
                </div>
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
              <h3 class="text-base font-semibold text-gray-800">Hapus Budget Component?</h3>
              <p class="text-sm text-gray-500">
                <span class="font-mono font-semibold text-gray-700">{{ deleteModal.target?.name }}</span>
                akan dihapus permanen.
              </p>
            </div>
            <div v-if="deleteModal.error" class="mt-3 px-4 py-2 bg-red-50 border border-red-200 rounded-lg">
              <p class="text-sm text-red-600 text-center">{{ deleteModal.error }}</p>
            </div>
            <div class="flex gap-2 mt-5">
              <button @click="deleteModal.show = false" class="btn-secondary text-sm flex-1">Batal</button>
              <button @click="handleDelete" :disabled="isSaving" class="flex-1 text-sm py-2 px-4 bg-red-500 hover:bg-red-600 text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-1.5 disabled:opacity-60">
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

  <TemplateRAPView
    v-if="templateRAPModal.show"
    :budget-component="templateRAPModal.component"
    @close="templateRAPModal.show = false"
  />
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useBudgetComponentStore } from '../../stores/budgetComponent.js'
import { useOrganizationStore } from '../../stores/organization.js'
import { usePermission } from '../../composables/usePermission.js'
import { useFormError } from '../../composables/useFormError.js'
import { useToast } from '../../composables/useToast.js'
import TemplateRAPView from './TemplateRAPView.vue'
import Panel from '../../components/Panel.vue'
import FormField from '../../components/FormField.vue'
import { useAuthStore } from '../../stores/auth.js'
import { Plus, Pencil, Trash2, Save, X, Loader2, Calculator, AlertCircle, FileText } from 'lucide-vue-next'

const store = useBudgetComponentStore()
const orgStore = useOrganizationStore()
const { canCreate, canUpdate, canDelete } = usePermission('BUDGET-COMPONENT')
const formError = useFormError()
const isSaving = ref(false)
const toast = useToast()
const loadingPositions = ref(false)
const authStore = useAuthStore()

// ── Filters ──────────────────────────────────────────────────────────────────
const filterCostCategory = ref('')
const filterDepartment = ref('')
const filterActive = ref('')

// Check if user can manage template RAP for this budget component
function canManageTemplateRAP(row) {
  // Superuser can access all
  if (authStore.user?.is_superuser) return true
  
  // Check if user has employee profile and position matches
  const userPosition = authStore.user?.employee_profile?.position
  if (!userPosition) return false
  
  return userPosition === row.position
}

function load() {
  store.fetchBudgetComponents({
    cost_category: filterCostCategory.value || undefined,
    department: filterDepartment.value || undefined,
    active: filterActive.value || undefined,
  })
}

// ── Form ───────────────────────────────────────────────────────────────────
const modal = reactive({ show: false, mode: 'add', editId: null })
const form = reactive({
  cost_category: '',
  department: null,
  position: null,
  order_no: 0,
  is_active: true,
})

const availablePositions = ref([])

const previewName = computed(() => {
  const cat = form.cost_category.toUpperCase() || '???'
  const dept = orgStore.departmentList.find(d => d.id === form.department)?.name?.toUpperCase() || ''
  const pos = availablePositions.value.find(p => p.id === form.position)?.name?.toUpperCase() || ''
  const parts = [cat]
  if (dept) parts.push(dept)
  if (pos) parts.push(pos)
  return parts.join(' - ')
})

async function onDepartmentChange() {
  // Reset position tapi jangan langsung set null di form
  const oldPosition = form.position
  form.position = null
  await loadPositionsForDepartment(form.department)
}

function openAddModal() {
  modal.show = true; modal.mode = 'add'; modal.editId = null
  formError.clearErrors()
  Object.assign(form, {
    cost_category: '',
    department: null,
    position: null,
    order_no: 0,
    is_active: true,
  })
  availablePositions.value = []
}

function openEditModal(row) {
  modal.show = true
  modal.mode = 'edit'
  modal.editId = row.id
  formError.clearErrors()
  
  // Set form values
  form.cost_category = row.cost_category
  form.department = row.department
  form.order_no = row.order_no
  form.is_active = row.is_active
  form.template_rap = row.template_rap
  
  // FIX: Load positions DULU, baru set position
  loadPositionsForDepartment(row.department, row.position)
}


async function loadPositionsForDepartment(deptId, selectPositionId = null) {

  if (!deptId) {
    availablePositions.value = []
    return
  }
  
  loadingPositions.value = true
  try {
    const positions = await store.fetchPositionsByDepartment(deptId)
    availablePositions.value = positions || []
    
    // Kalau ada selectPositionId, pastikan position tetep ke-select
    if (selectPositionId && positions.find(p => p.id === selectPositionId)) {
      form.position = selectPositionId
    }
  } catch (e) {
    console.error('Failed to load positions:', e)
    toast.error('Gagal memuat positions.')
    availablePositions.value = []
  } finally {
    loadingPositions.value = false
  }
}

function validate() {
  formError.clearErrors()
  let valid = true

  if (!form.cost_category) {
    formError.fieldErrors.cost_category = 'Cost category wajib dipilih.'
    valid = false
  }
  if (!form.department) {
    formError.fieldErrors.department = 'Department wajib dipilih.'
    valid = false
  }
  if (!form.position) {
    formError.fieldErrors.position = 'Cost of unit (position) wajib dipilih.'
    valid = false
  }
  return valid
}

async function handleSubmit() {
  if (!validate()) return
  isSaving.value = true
  try {
    const payload = {
      cost_category: form.cost_category,
      department: form.department,
      position: form.position,
      order_no: form.order_no,
      is_active: form.is_active,
    }

    if (modal.mode === 'add') {
      await store.createBudgetComponent(payload)
    } else {
      await store.updateBudgetComponent(modal.editId, payload)
    }
    modal.show = false
    toast.success('Budget component berhasil disimpan.')
    await load()
  } catch (err) {
    formError.parseApiError(err)
    toast.error('Gagal menyimpan budget component.')
  } finally {
    isSaving.value = false
  }
}

// ── Delete ─────────────────────────────────────────────────────────────────
const deleteModal = reactive({ show: false, target: null, error: '' })

function confirmDelete(row) {
  deleteModal.target = row
  deleteModal.error = ''
  deleteModal.show = true
}

async function handleDelete() {
  isSaving.value = true
  deleteModal.error = ''
  try {
    await store.deleteBudgetComponent(deleteModal.target.id)
    deleteModal.show = false
    toast.success('Budget component berhasil dihapus.')
    await load()
  } catch (err) {
    deleteModal.error = err?.response?.data?.detail || 'Gagal menghapus.'
    toast.error('Gagal menghapus budget component.')
  } finally {
    isSaving.value = false
  }
}

// ── Helpers ────────────────────────────────────────────────────────────────
function costCategoryClass(cat) {
  const map = {
    hpp: 'bg-blue-100 text-blue-700',
    revenue: 'bg-green-100 text-green-700',
    target_hpp: 'bg-purple-100 text-purple-700',
    target_opex: 'bg-indigo-100 text-indigo-700',
    opex: 'bg-orange-100 text-orange-700',
    capex: 'bg-amber-100 text-amber-700',
    tax: 'bg-red-100 text-red-700',
  }
  return map[cat] || 'bg-gray-100 text-gray-700'
}

onMounted(async () => {
  await Promise.all([
    orgStore.fetchDepartments(),
    load(),
  ])
})

const templateRAPModal = ref({ show: false, component: null })

const canAccessTemplateRAP = computed(() => {
  // Superuser can access all
  if (authStore.user?.is_superuser) return true
  // Check if user's position matches
  const userPosition = authStore.user?.employee_profile?.position
  if (!userPosition) return false
  return true // Will be checked per-row in the view
})

function openTemplateRAP(component) {
  templateRAPModal.value = { show: true, component }
}
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