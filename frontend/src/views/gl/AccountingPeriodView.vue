<template>
  <Panel title="Accounting Period" subtitle="Setting | Accounting Setting | Accounting Period">
    
    <!-- Unified Tabs Navigation -->
    <div class="flex border-b border-gray-200 mb-6 shrink-0 flex-wrap">
      <router-link to="/settings/accounting-period" class="px-5 py-3 text-xs font-semibold text-gray-500 hover:text-bfs-gold border-b-2 border-transparent transition-all flex items-center gap-1.5" active-class="!text-bfs-gold !border-bfs-gold bg-gray-50/50">
        <CalendarRange class="w-4 h-4" /> Accounting Period
      </router-link>
      <router-link to="/settings/annual-period" class="px-5 py-3 text-xs font-semibold text-gray-500 hover:text-bfs-gold border-b-2 border-transparent transition-all flex items-center gap-1.5" active-class="!text-bfs-gold !border-bfs-gold bg-gray-50/50">
        <CalendarDays class="w-4 h-4" /> Annual Period
      </router-link>
      <router-link to="/settings/quarter-period" class="px-5 py-3 text-xs font-semibold text-gray-500 hover:text-bfs-gold border-b-2 border-transparent transition-all flex items-center gap-1.5" active-class="!text-bfs-gold !border-bfs-gold bg-gray-50/50">
        <PieChart class="w-4 h-4" /> Quarter Period
      </router-link>
      <router-link to="/settings/monthly-period" class="px-5 py-3 text-xs font-semibold text-gray-500 hover:text-bfs-gold border-b-2 border-transparent transition-all flex items-center gap-1.5" active-class="!text-bfs-gold !border-bfs-gold bg-gray-50/50">
        <Calendar class="w-4 h-4" /> Monthly Period
      </router-link>
      <router-link to="/settings/period-activity-log" class="px-5 py-3 text-xs font-semibold text-gray-500 hover:text-bfs-gold border-b-2 border-transparent transition-all flex items-center gap-1.5" active-class="!text-bfs-gold !border-bfs-gold bg-gray-50/50">
        <History class="w-4 h-4" /> Period Activity Log
      </router-link>
    </div>

    <!-- Summary KPI Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
      <div class="bg-gradient-to-br from-emerald-50 to-white border border-emerald-150 p-5 rounded-2xl flex items-center justify-between shadow-xs hover:shadow-md transition-all">
        <div>
          <span class="text-xs font-semibold text-emerald-600 uppercase tracking-wider">Open Periods</span>
          <h3 class="text-2xl font-bold text-emerald-850 mt-1 font-mono">{{ openPeriodsCount }}</h3>
        </div>
        <div class="w-12 h-12 rounded-xl bg-emerald-500/10 flex items-center justify-center text-emerald-600">
          <Unlock class="w-6 h-6 animate-pulse" />
        </div>
      </div>
      <div class="bg-gradient-to-br from-rose-50 to-white border border-rose-150 p-5 rounded-2xl flex items-center justify-between shadow-xs hover:shadow-md transition-all">
        <div>
          <span class="text-xs font-semibold text-rose-600 uppercase tracking-wider">Closed Periods</span>
          <h3 class="text-2xl font-bold text-rose-850 mt-1 font-mono">{{ closedPeriodsCount }}</h3>
        </div>
        <div class="w-12 h-12 rounded-xl bg-rose-500/10 flex items-center justify-center text-rose-600">
          <Lock class="w-6 h-6" />
        </div>
      </div>
      <div class="bg-gradient-to-br from-blue-50 to-white border border-blue-150 p-5 rounded-2xl flex items-center justify-between shadow-xs hover:shadow-md transition-all">
        <div>
          <span class="text-xs font-semibold text-blue-600 uppercase tracking-wider">Active Year</span>
          <h3 class="text-2xl font-bold text-blue-850 mt-1 font-mono">{{ currentFiscalYear }}</h3>
        </div>
        <div class="w-12 h-12 rounded-xl bg-blue-500/10 flex items-center justify-center text-blue-600">
          <CalendarRange class="w-6 h-6" />
        </div>
      </div>
    </div>

    <!-- Filter Bar Component -->
    <div class="bg-gray-50 border border-gray-150 rounded-2xl p-5 mb-6 flex flex-col md:flex-row md:items-end justify-between gap-4">
      <div class="flex flex-wrap items-center gap-3 flex-1">
        <div class="space-y-1">
          <label class="block text-[10px] font-bold text-gray-500 uppercase tracking-wider">Field</label>
          <select v-model="filterField" class="px-3 py-1.5 text-xs border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-bfs-gold/30 focus:border-bfs-gold bg-white min-w-28">
            <option value="close">Close Status</option>
            <option value="month">Month</option>
            <option value="year">Year</option>
          </select>
        </div>

        <div class="space-y-1">
          <label class="block text-[10px] font-bold text-gray-500 uppercase tracking-wider">Operator</label>
          <select v-model="filterOp" class="px-3 py-1.5 text-xs border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-bfs-gold/30 focus:border-bfs-gold bg-white w-20">
            <option value="=">=</option>
            <option value="contains">Contains</option>
          </select>
        </div>

        <div class="space-y-1 flex-1 min-w-36">
          <label class="block text-[10px] font-bold text-gray-500 uppercase tracking-wider">Value</label>
          <input v-model="filterValue" type="text" class="w-full px-3 py-1.5 text-xs border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-bfs-gold/30 focus:border-bfs-gold bg-white" placeholder="Type filters..." />
        </div>

        <div class="space-y-1">
          <label class="block text-[10px] font-bold text-gray-500 uppercase tracking-wider">Open/Close</label>
          <select v-model="filterStatus" class="px-3 py-1.5 text-xs border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-bfs-gold/30 focus:border-bfs-gold bg-white">
            <option value="">ALL STATUS</option>
            <option value="OPEN">Open</option>
            <option value="CLOSE">Close</option>
          </select>
        </div>
      </div>
      
      <div class="flex items-center gap-2">
        <button class="px-5 py-2 bg-bfs-navy hover:bg-bfs-navy-light text-white text-xs font-semibold rounded-lg transition-all flex items-center gap-1.5 cursor-pointer shadow-xs" @click="applyFilter">
          <Search class="w-3.5 h-3.5" /> Search
        </button>
        <button class="px-5 py-2 border border-gray-200 text-gray-700 bg-white hover:bg-gray-50 text-xs font-semibold rounded-lg transition-all flex items-center gap-1.5 cursor-pointer" @click="resetFilter">
          <RefreshCw class="w-3.5 h-3.5 text-gray-500" /> Reset
        </button>
      </div>
    </div>

    <!-- Header Actions and Local Paging info -->
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-2">
        <button class="px-4 py-2 bg-bfs-gold hover:bg-bfs-gold-dark text-white text-xs font-semibold rounded-lg transition-all flex items-center gap-1.5 cursor-pointer shadow-xs" @click="handleAddNew">
          <Plus class="w-4 h-4" /> Add New Period
        </button>
        <button class="px-4 py-2 border border-gray-200 text-gray-700 bg-white hover:bg-gray-50 text-xs font-semibold rounded-lg transition-all flex items-center gap-1.5 cursor-pointer" @click="openGlobalLog">
          <History class="w-4 h-4 text-gray-500" /> Audit Logs
        </button>
      </div>
      
      <div class="flex items-center gap-1.5 text-xs text-gray-500 font-medium">
        <span>Page:</span>
        <select v-model="currentPage" class="px-2 py-1 border border-gray-200 rounded-md bg-white text-gray-700">
          <option v-for="p in totalPages" :key="p" :value="p">{{ p }}</option>
        </select>
        <span>of {{ totalPages }}</span>
      </div>
    </div>

    <!-- Table Container -->
    <div class="border border-gray-200 rounded-2xl overflow-hidden bg-white shadow-xs">
      <div v-if="store.isLoading" class="flex flex-col items-center justify-center py-20 text-gray-400 gap-2">
        <Loader2 class="w-8 h-8 animate-spin text-bfs-gold" />
        <span class="text-xs font-medium">Fetching accounting periods...</span>
      </div>
      
      <div v-else-if="store.error" class="flex flex-col items-center justify-center py-20 text-red-500 gap-2 font-medium">
        <AlertCircle class="w-8 h-8" />
        <span>{{ store.error }}</span>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full text-left text-xs border-collapse">
          <thead>
            <tr class="bg-gray-50 border-b border-gray-200 text-[11px] font-semibold text-gray-500 uppercase tracking-wider">
              <th class="px-6 py-4 w-16 text-center">No.</th>
              <th class="px-6 py-4 w-44">Start date</th>
              <th class="px-6 py-4 w-44">End Date</th>
              <th class="px-6 py-4">Current/Active Period</th>
              <th class="px-6 py-4 w-28 text-center">Year</th>
              <th class="px-6 py-4 w-32 text-center">Is Closed?</th>
              <th class="px-6 py-4 w-44 text-right">Action</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-150">
            <tr v-if="pagedData.length === 0">
              <td colspan="7" class="px-6 py-10 text-center text-gray-400 font-medium">
                No matching accounting periods found.
              </td>
            </tr>
            <tr
              v-for="(item, i) in pagedData"
              :key="item.id"
              class="hover:bg-blue-50/25 transition-colors"
            >
              <td class="px-6 py-3.5 text-center text-gray-400 font-mono">{{ (currentPage - 1) * perPage + i + 1 }}.</td>
              <td class="px-6 py-3.5 text-gray-650 font-medium font-mono">{{ formatDate(item.start_date) }}</td>
              <td class="px-6 py-3.5 text-gray-650 font-medium font-mono">{{ formatDate(item.end_date) }}</td>
              <td class="px-6 py-3.5 text-bfs-navy font-semibold text-sm">{{ item.month_name }}</td>
              <td class="px-6 py-3.5 text-center text-gray-600 font-mono font-medium">{{ item.year }}</td>
              <td class="px-6 py-3.5 text-center">
                <span class="inline-flex px-2.5 py-0.5 rounded-full text-[10px] font-bold border" :class="item.status === 'CLOSE' ? 'bg-red-50 border-red-200 text-red-700' : 'bg-emerald-50 border-emerald-200 text-emerald-700'">
                  {{ item.status === 'CLOSE' ? 'Yes' : 'No' }}
                </span>
              </td>
              <td class="px-6 py-3.5 text-right">
                <div class="flex justify-end gap-1.5">
                  <button
                    class="px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1 cursor-pointer transition-colors shadow-xs"
                    :class="item.status === 'OPEN'
                      ? 'bg-rose-50 border border-rose-200 hover:bg-rose-100 text-rose-700'
                      : 'bg-emerald-50 border border-emerald-200 hover:bg-emerald-100 text-emerald-700'"
                    @click="openToggle(item)"
                    :title="item.status === 'OPEN' ? 'Tutup Period' : 'Buka Period'"
                  >
                    <Lock v-if="item.status === 'OPEN'" class="w-3.5 h-3.5" />
                    <Unlock v-else class="w-3.5 h-3.5" />
                    {{ item.status === 'OPEN' ? 'Close' : 'Open' }}
                  </button>
                  <button class="p-1.5 border border-gray-200 hover:bg-gray-50 text-gray-500 rounded-lg cursor-pointer transition-colors" @click="openLog(item)" title="Log Activity">
                    <History class="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Reason Modal -->
    <PeriodReasonModal
      :show="showToggleModal"
      :is-closing="toggleTarget?.status === 'OPEN'"
      :period-label="toggleTarget ? `${toggleTarget.month_name} ${toggleTarget.year}` : ''"
      :loading="toggling"
      @confirm="handleToggleConfirm"
      @cancel="showToggleModal = false"
    />

    <!-- Log Modal -->
    <PeriodLogModal
      :show="showLogModal"
      :logs="currentLogs"
      :period-label="logTarget ? `${logTarget.month_name} ${logTarget.year}` : 'All Periods'"
      :loading="logLoading"
      @close="showLogModal = false"
    />
  </Panel>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import Swal from 'sweetalert2'
import { usePeriodStore } from '../../stores/period.js'
import Panel from '../../components/Panel.vue'
import PeriodReasonModal from '../../components/period/PeriodReasonModal.vue'
import PeriodLogModal from '../../components/period/PeriodLogModal.vue'
import {
  CalendarRange,
  CalendarDays,
  PieChart,
  Calendar,
  History,
  Lock,
  Unlock,
  Plus,
  Search,
  RefreshCw,
  Loader2,
  AlertCircle
} from 'lucide-vue-next'

const store = usePeriodStore()

// ── Filters ──────────────────────────────────────────────────────────────────
const filterField  = ref('close')
const filterOp     = ref('=')
const filterValue  = ref('')
const filterStatus = ref('')
const activeStatus = ref('')
const activeField  = ref('close')
const activeOp      = ref('=')
const activeValue   = ref('')

function applyFilter() {
  activeStatus.value = filterStatus.value
  activeField.value  = filterField.value
  activeOp.value     = filterOp.value
  activeValue.value  = filterValue.value
  currentPage.value  = 1
}
function resetFilter() {
  filterField.value  = 'close'
  filterOp.value     = '='
  filterValue.value  = ''
  filterStatus.value = ''
  activeStatus.value = ''
  activeField.value  = 'close'
  activeOp.value     = '='
  activeValue.value  = ''
  currentPage.value  = 1
}

// ── Pagination ────────────────────────────────────────────────────────────────
const perPage     = 15
const currentPage = ref(1)

const filteredData = computed(() => {
  let list = store.accountingPeriods
  if (activeStatus.value) {
    list = list.filter(i => i.status === activeStatus.value)
  }
  
  if (activeValue.value !== null && activeValue.value !== undefined && activeValue.value.trim() !== '') {
    const val = activeValue.value.trim().toLowerCase()
    
    const indonesianMonths = {
      'januari': 'january', 'jan': 'january',
      'februari': 'february', 'feb': 'february',
      'maret': 'march', 'mar': 'march',
      'april': 'april', 'apr': 'april',
      'mei': 'may',
      'juni': 'june', 'jun': 'june',
      'juli': 'july', 'jul': 'july',
      'agustus': 'august', 'agu': 'august', 'agt': 'august', 'aug': 'august',
      'september': 'september', 'sep': 'september',
      'oktober': 'october', 'okt': 'october', 'oct': 'october',
      'november': 'november', 'nov': 'november',
      'desember': 'december', 'des': 'december', 'dec': 'december'
    }

    list = list.filter(item => {
      let fieldValue = ''
      
      if (activeField.value === 'year') {
        fieldValue = String(item.year).toLowerCase()
        if (activeOp.value === '=') {
          return fieldValue === val
        } else {
          return fieldValue.includes(val)
        }
      }
      
      if (activeField.value === 'month') {
        const englishMapped = indonesianMonths[val] || val
        const nameMatch = String(item.month_name).toLowerCase()
        const numMatch = String(item.month)
        const monthNum = parseInt(val)

        if (activeOp.value === '=') {
          return nameMatch === englishMapped || numMatch === String(monthNum)
        } else {
          return nameMatch.includes(englishMapped) || numMatch.includes(val)
        }
      }
      
      if (activeField.value === 'close') {
        const isClosed = item.status === 'CLOSE'
        if (val === 'yes' || val === 'ya' || val === 'y' || val === 'close' || val === 'closed') {
          return isClosed
        } else if (val === 'no' || val === 'tidak' || val === 't' || val === 'n' || val === 'open') {
          return !isClosed
        }
        
        fieldValue = String(item.status).toLowerCase()
        if (activeOp.value === '=') {
          return fieldValue === val
        } else {
          return fieldValue.includes(val)
        }
      }

      return true
    })
  }
  
  return list
})

const totalPages = computed(() => Math.max(1, Math.ceil(filteredData.value.length / perPage)))

const pagedData = computed(() => {
  const s = (currentPage.value - 1) * perPage
  return filteredData.value.slice(s, s + perPage)
})

// ── KPI Summary Computeds ─────────────────────────────────────────────────────
const openPeriodsCount = computed(() => {
  return store.accountingPeriods.filter(p => p.status === 'OPEN').length
})

const closedPeriodsCount = computed(() => {
  return store.accountingPeriods.filter(p => p.status === 'CLOSE').length
})

const currentFiscalYear = computed(() => {
  const openPeriods = store.accountingPeriods.filter(p => p.status === 'OPEN')
  if (openPeriods.length) {
    const years = openPeriods.map(p => p.year)
    return Math.max(...years)
  }
  if (store.accountingPeriods.length) {
    const years = store.accountingPeriods.map(p => p.year)
    return Math.max(...years)
  }
  return new Date().getFullYear()
})

// ── Toggle ────────────────────────────────────────────────────────────────────
const showToggleModal = ref(false)
const toggleTarget    = ref(null)
const toggling        = ref(false)

function openToggle(item) {
  toggleTarget.value    = item
  showToggleModal.value = true
}

async function handleToggleConfirm(reason) {
  toggling.value = true
  try {
    await store.toggleAccountingPeriod(toggleTarget.value.id, reason)
    showToggleModal.value = false
    Swal.fire({
      icon: 'success',
      title: 'Success!',
      text: `Period ${toggleTarget.value.month_name} ${toggleTarget.value.year} has been ${toggleTarget.value.status === 'OPEN' ? 'closed' : 'opened'} successfully.`,
      timer: 2000,
      showConfirmButton: false,
    })
    // Refresh list
    await store.fetchAccountingPeriods()
  } catch (err) {
    Swal.fire({
      icon: 'error',
      title: 'Failed!',
      text: err?.response?.data?.detail || 'Something went wrong.',
    })
  } finally {
    toggling.value = false
  }
}

// ── Log ───────────────────────────────────────────────────────────────────────
const showLogModal = ref(false)
const logTarget    = ref(null)
const currentLogs  = ref([])
const logLoading   = ref(false)

async function openLog(item) {
  logTarget.value    = item
  showLogModal.value = true
  logLoading.value   = true
  try {
    currentLogs.value = await store.fetchAccountingLogs(item.id)
  } catch {
    currentLogs.value = []
  } finally {
    logLoading.value = false
  }
}

async function openGlobalLog() {
  logTarget.value    = null
  showLogModal.value = true
  logLoading.value   = true
  try {
    await store.fetchAllLogs({ period_type: 'ACCOUNTING' })
    currentLogs.value = store.activityLogs
  } catch {
    currentLogs.value = []
  } finally {
    logLoading.value = false
  }
}

// ── Add New ───────────────────────────────────────────────────────────────────
async function handleAddNew() {
  Swal.fire({
    icon: 'info',
    title: 'Information',
    text: 'Accounting Periods are auto-generated when you add a new Annual Period. Please go to the Annual Period tab to add a new year.',
    confirmButtonText: 'OK',
    confirmButtonColor: '#1A2744',
  })
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function formatDate(d) {
  if (!d) return '-'
  const dt  = new Date(d)
  const day = String(dt.getDate()).padStart(2, '0')
  const mon = dt.toLocaleString('en', { month: 'short' })
  return `${day} ${mon} ${dt.getFullYear()}`
}

onMounted(() => store.fetchAccountingPeriods())
</script>

<style scoped>
@reference "../../style.css";
</style>