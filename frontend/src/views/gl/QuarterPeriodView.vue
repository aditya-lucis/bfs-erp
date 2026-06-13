<template>
  <Panel title="Quarter Period" subtitle="Setting | Accounting Setting | Quarter Accounting Period">
    
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
      <div class="bg-gradient-to-br from-blue-50 to-white border border-blue-150 p-5 rounded-2xl flex items-center justify-between shadow-xs hover:shadow-md transition-all">
        <div>
          <span class="text-xs font-semibold text-blue-600 uppercase tracking-wider">Total Fiscal Years</span>
          <h3 class="text-2xl font-bold text-blue-850 mt-1 font-mono">{{ totalYearsCount }}</h3>
        </div>
        <div class="w-12 h-12 rounded-xl bg-blue-500/10 flex items-center justify-center text-blue-600">
          <CalendarDays class="w-6 h-6" />
        </div>
      </div>
      <div class="bg-gradient-to-br from-emerald-50 to-white border border-emerald-150 p-5 rounded-2xl flex items-center justify-between shadow-xs hover:shadow-md transition-all">
        <div>
          <span class="text-xs font-semibold text-emerald-600 uppercase tracking-wider">Total Quarters</span>
          <h3 class="text-2xl font-bold text-emerald-850 mt-1 font-mono">{{ totalQuartersCount }}</h3>
        </div>
        <div class="w-12 h-12 rounded-xl bg-emerald-500/10 flex items-center justify-center text-emerald-600">
          <PieChart class="w-6 h-6" />
        </div>
      </div>
      <div class="bg-gradient-to-br from-purple-50 to-white border border-purple-150 p-5 rounded-2xl flex items-center justify-between shadow-xs hover:shadow-md transition-all">
        <div>
          <span class="text-xs font-semibold text-purple-600 uppercase tracking-wider">Active Year</span>
          <h3 class="text-2xl font-bold text-purple-850 mt-1 font-mono">{{ activeYear }}</h3>
        </div>
        <div class="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center text-purple-600">
          <CalendarRange class="w-6 h-6" />
        </div>
      </div>
    </div>

    <!-- Header Actions and Local Paging info -->
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-2">
        <button class="px-4 py-2 bg-bfs-gold hover:bg-bfs-gold-dark text-white text-xs font-semibold rounded-lg transition-all flex items-center gap-1.5 cursor-pointer shadow-xs" @click="goToAnnual">
          <Plus class="w-4 h-4" /> Add Annual Period
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
    <div class="border border-gray-200 rounded-2xl overflow-hidden bg-white shadow-xs max-w-4xl">
      <div v-if="store.isLoading" class="flex flex-col items-center justify-center py-20 text-gray-400 gap-2">
        <Loader2 class="w-8 h-8 animate-spin text-bfs-gold" />
        <span class="text-xs font-medium">Fetching quarter periods...</span>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full text-left text-xs border-collapse">
          <thead>
            <tr class="bg-gray-50 border-b border-gray-200 text-[11px] font-semibold text-gray-500 uppercase tracking-wider">
              <th class="px-6 py-4 w-16 text-center">No.</th>
              <th class="px-6 py-4 w-44">Fiscal Year</th>
              <th v-for="q in [1,2,3,4]" :key="q" class="px-6 py-4 text-center">Q{{ q }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-150">
            <tr v-if="pagedData.length === 0">
              <td colspan="6" class="px-6 py-10 text-center text-gray-400 font-medium">
                No quarter periods created yet.
              </td>
            </tr>
            <tr
              v-for="(row, i) in pagedData"
              :key="row.id"
              class="hover:bg-blue-50/25 transition-colors animate-fade-in"
            >
              <td class="px-6 py-3.5 text-center text-gray-400 font-mono">{{ (currentPage - 1) * perPage + i + 1 }}.</td>
              <td class="px-6 py-3.5 text-bfs-navy font-bold text-sm font-mono tracking-wide">{{ row.year }}</td>
              <td v-for="q in [1,2,3,4]" :key="q" class="px-6 py-3.5 text-center">
                <template v-if="getQuarter(row, q)">
                  <button
                    class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-bold border cursor-pointer hover:shadow-xs transition-all"
                    :class="getQuarter(row, q).status === 'OPEN'
                      ? 'bg-emerald-50 border-emerald-250 text-emerald-700 hover:bg-emerald-100 hover:border-emerald-350'
                      : 'bg-rose-50 border-rose-250 text-rose-700 hover:bg-rose-100 hover:border-rose-350'"
                    @click="openToggle(getQuarter(row, q), row.year)"
                  >
                    <span class="w-1.5 h-1.5 rounded-full" :class="getQuarter(row, q).status === 'OPEN' ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'"></span>
                    {{ getQuarter(row, q).status === 'OPEN' ? 'Open' : 'Close' }}
                  </button>
                </template>
                <span v-else class="text-gray-300 font-medium">—</span>
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
      :period-label="toggleLabel"
      :loading="toggling"
      @confirm="handleToggleConfirm"
      @cancel="showToggleModal = false"
    />

    <!-- Log Modal -->
    <PeriodLogModal
      :show="showLogModal"
      :logs="currentLogs"
      :period-label="'Quarter Periods'"
      :loading="logLoading"
      @close="showLogModal = false"
    />
  </Panel>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import Swal from 'sweetalert2'
import { useRouter } from 'vue-router'
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
  Plus,
  Loader2
} from 'lucide-vue-next'

const store  = usePeriodStore()
const router = useRouter()

const perPage     = 15
const currentPage = ref(1)
const totalPages  = computed(() => Math.max(1, Math.ceil(store.quarterPeriods.length / perPage)))
const pagedData   = computed(() => {
  const s = (currentPage.value - 1) * perPage
  return store.quarterPeriods.slice(s, s + perPage)
})

// KPI Computeds
const totalYearsCount = computed(() => store.quarterPeriods.length)

const totalQuartersCount = computed(() => {
  return store.quarterPeriods.reduce((acc, row) => acc + (row.quarters?.length || 0), 0)
})

const activeYear = computed(() => {
  const openYears = store.quarterPeriods.filter(p => p.status === 'OPEN')
  if (openYears.length) {
    const years = openYears.map(p => p.year)
    return Math.max(...years)
  }
  if (store.quarterPeriods.length) {
    const years = store.quarterPeriods.map(p => p.year)
    return Math.max(...years)
  }
  return new Date().getFullYear()
})

// Get specific quarter from row
function getQuarter(row, qNum) {
  return row.quarters?.find(q => q.quarter === qNum) || null
}

// Add New → redirect to annual period
function goToAnnual() {
  router.push('/settings/annual-period')
}

// Toggle
const showToggleModal = ref(false)
const toggleTarget    = ref(null)
const toggleLabel     = ref('')
const toggling        = ref(false)

function openToggle(quarter, year) {
  toggleTarget.value    = quarter
  toggleLabel.value     = `${year} Q${quarter.quarter}`
  showToggleModal.value = true
}

async function handleToggleConfirm(reason) {
  toggling.value = true
  try {
    await store.toggleQuarterPeriod(toggleTarget.value.id, reason)
    showToggleModal.value = false
    await store.fetchQuarterPeriods()
    Swal.fire({
      icon: 'success',
      title: 'Success!',
      text: `Quarter ${toggleLabel.value} has been ${toggleTarget.value.status === 'OPEN' ? 'closed' : 'opened'} successfully.`,
      timer: 2000,
      showConfirmButton: false,
    })
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

// Log
const showLogModal = ref(false)
const currentLogs  = ref([])
const logLoading   = ref(false)

async function openGlobalLog() {
  showLogModal.value = true
  logLoading.value   = true
  try {
    await store.fetchAllLogs({ period_type: 'QUARTER' })
    currentLogs.value = store.activityLogs
  } catch {
    currentLogs.value = []
  } finally {
    logLoading.value = false
  }
}

onMounted(() => store.fetchQuarterPeriods())
</script>

<style scoped>
@reference "../../style.css";
</style>