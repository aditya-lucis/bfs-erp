<template>
  <Panel title="Employee Data" subtitle="Setting | Organizational Structure">

    <!-- Toolbar -->
    <div class="flex items-center justify-between mb-4 gap-3">
      <div class="flex items-center gap-2 flex-1 max-w-lg">
        <div class="relative flex-1">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            v-model="search"
            type="text"
            placeholder="Cari nama, ID, email..."
            class="w-full pl-9 pr-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-bfs-gold/40 focus:border-bfs-gold"
            @input="onSearch"
          />
        </div>
        <select v-model="filterStatus" @change="onSearch"
          class="text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-bfs-gold/40">
          <option value="">All Status</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
          <option value="resigned">Resigned</option>
          <option value="terminated">Terminated</option>
        </select>
      </div>
      <button v-if="canCreate" @click="openForm(null)" class="btn-primary text-sm flex items-center gap-1.5">
        <UserPlus class="w-4 h-4" /> Add Employee
      </button>
    </div>

    <!-- Table -->
    <div class="border border-gray-200 rounded-xl overflow-hidden">
      <div class="bg-gray-50 border-b border-gray-200 grid grid-cols-12 px-4 py-2.5 text-[11px] font-semibold text-gray-500 uppercase tracking-wide">
        <div class="col-span-2">Employee ID</div>
        <div class="col-span-3">Name</div>
        <div class="col-span-2">Position</div>
        <div class="col-span-2">Department</div>
        <div class="col-span-1 text-center">Groups</div>
        <div class="col-span-1 text-center">Sign</div>
        <div class="col-span-1 text-center">Status</div>
      </div>

      <div v-if="orgStore.isLoading" class="flex justify-center py-12">
        <Loader2 class="w-6 h-6 animate-spin text-bfs-gold" />
      </div>

      <template v-else-if="orgStore.employees.length">
        <div
          v-for="emp in orgStore.employees"
          :key="emp.id"
          class="grid grid-cols-12 px-4 py-3 items-center border-b border-gray-100 last:border-0 hover:bg-gray-50/80 transition-colors group cursor-pointer"
          @click="openForm(emp)"
        >
          <!-- Employee ID -->
          <div class="col-span-2">
            <span class="text-xs font-mono font-bold text-bfs-navy bg-bfs-navy/8 px-2 py-1 rounded-lg">
              {{ emp.employee_id }}
            </span>
          </div>

          <!-- Name + username -->
          <div class="col-span-3">
            <p class="text-sm font-medium text-gray-800">{{ emp.full_name }}</p>
            <p class="text-xs text-gray-400">@{{ emp.username || '—' }}</p>
          </div>

          <!-- Position -->
          <div class="col-span-2 text-sm text-gray-600 truncate">{{ emp.position_name }}</div>

          <!-- Department -->
          <div class="col-span-2 text-sm text-gray-500 truncate">{{ emp.department_name }}</div>

          <!-- Groups count -->
          <div class="col-span-1 flex justify-center">
            <span v-if="emp.groups?.length"
              class="text-xs bg-bfs-gold/15 text-bfs-gold-dark font-medium px-2 py-0.5 rounded-full">
              {{ emp.groups.length }}
            </span>
            <span v-else class="text-xs text-gray-300">—</span>
          </div>

          <!-- Signature -->
          <div class="col-span-1 flex justify-center">
            <div :class="emp.has_signature
              ? 'bg-green-100 text-green-600'
              : 'bg-gray-100 text-gray-400'"
              class="w-7 h-7 rounded-full flex items-center justify-center"
              :title="emp.has_signature ? 'Signature tersedia' : 'Belum ada signature'"
            >
              <PenLine class="w-3.5 h-3.5" />
            </div>
          </div>

          <!-- Status -->
          <div class="col-span-1 flex justify-center">
            <span :class="statusBadge(emp.status)">{{ emp.status }}</span>
          </div>
        </div>
      </template>

      <div v-else class="flex flex-col items-center justify-center py-16 text-gray-400">
        <Users class="w-8 h-8 mb-2" />
        <p class="text-sm">Belum ada data employee.</p>
      </div>
    </div>

    <!-- Employee Form Modal -->
    <EmployeeFormModal
      v-if="formModal.show"
      :employee="formModal.employee"
      @close="formModal.show = false"
      @saved="onSaved"
    />

  </Panel>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useOrganizationStore } from '../../stores/organization.js'
import Panel from '../../components/Panel.vue'
import EmployeeFormModal from '../../components/employee/EmployeeFormModal.vue'
import { usePermission } from '../../composables/usePermission.js'
import { Search, UserPlus, Loader2, Users, PenLine } from 'lucide-vue-next'

const { canCreate, canUpdate, canDelete } = usePermission('SETTINGS-EMPLOYEE-DATA')

const orgStore = useOrganizationStore()

const search       = ref('')
const filterStatus = ref('')
let   searchTimer  = null

function onSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => loadEmployees(), 400)
}

function loadEmployees() {
  const params = {}
  if (search.value)       params.search = search.value
  if (filterStatus.value) params.status = filterStatus.value
  orgStore.fetchEmployees(params)
}

const statusBadge = (s) => ({
  'active':     'text-xs px-2 py-0.5 rounded-full bg-green-100 text-green-700 font-medium capitalize',
  'inactive':   'text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-500 font-medium capitalize',
  'resigned':   'text-xs px-2 py-0.5 rounded-full bg-orange-100 text-orange-600 font-medium capitalize',
  'terminated': 'text-xs px-2 py-0.5 rounded-full bg-red-100 text-red-600 font-medium capitalize',
}[s] || '')

const formModal = reactive({ show: false, employee: null })

async function openForm(emp) {
  if (emp) {
    // Fetch detail untuk dapat signature_draw, signature_image_url, dll
    const detail = await orgStore.fetchEmployeeDetail(emp.id)
    formModal.employee = detail
  } else {
    formModal.employee = null
  }
  formModal.show = true
}

function onSaved() {
  formModal.show = false
  loadEmployees()
}

onMounted(() => loadEmployees())
</script>

<style scoped>
@reference "../../style.css";
.btn-primary { @apply px-4 py-2 bg-bfs-gold hover:bg-bfs-gold-dark text-white font-medium rounded-lg transition-colors; }
</style>