<template>
  <Panel title="Monthly Period" subtitle="Setting | Accounting Setting | Monthly Accounting Period">
    <!-- Unified Tabs Navigation -->
    <div class="flex border-b border-gray-200 mb-6 shrink-0 flex-wrap">
      <router-link to="/settings/accounting-period" class="px-5 py-3 text-xs font-semibold text-gray-500 hover:text-bfs-gold border-b-2 border-transparent transition-all flex items-center gap-1.5" active-class="!text-bfs-gold !border-bfs-gold bg-gray-50/50">
        <CalendarRange class="w-4 h-4"/> Accounting Period
      </router-link>
      <router-link to="/settings/annual-period" class="px-5 py-3 text-xs font-semibold text-gray-500 hover:text-bfs-gold border-b-2 border-transparent transition-all flex items-center gap-1.5" active-class="!text-bfs-gold !border-bfs-gold bg-gray-50/50">
        <CalendarDays class="w-4 h-4"/> Annual Period
      </router-link>
      <router-link to="/settings/quarter-period" class="px-5 py-3 text-xs font-semibold text-gray-500 hover:text-bfs-gold border-b-2 border-transparent transition-all flex items-center gap-1.5" active-class="!text-bfs-gold !border-bfs-gold bg-gray-50/50">
        <PieChart class="w-4 h-4"/> Quarter Period
      </router-link>
      <router-link to="/settings/monthly-period" class="px-5 py-3 text-xs font-semibold text-gray-500 hover:text-bfs-gold border-b-2 border-transparent transition-all flex items-center gap-1.5" active-class="!text-bfs-gold !border-bfs-gold bg-gray-50/50">
        <Calendar class="w-4 h-4"/> Monthly Period
      </router-link>
      <router-link to="/settings/period-activity-log" class="px-5 py-3 text-xs font-semibold text-gray-500 hover:text-bfs-gold border-b-2 border-transparent transition-all flex items-center gap-1.5" active-class="!text-bfs-gold !border-bfs-gold bg-gray-50/50">
        <History class="w-4 h-4"/> Period Activity Log
      </router-link>
    </div>

    <!-- Summary KPI Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
      <div class="bg-gradient-to-br from-blue-50 to-white border border-blue-150 p-5 rounded-2xl flex items-center justify-between shadow-xs hover:shadow-md transition-all">
        <div>
          <span class="text-xs font-semibold text-blue-600 uppercase tracking-wider">Total Months</span>
          <h3 class="text-2xl font-bold text-blue-850 mt-1 font-mono">{{ totalMonthsCount }}</h3>
        </div>
        <div class="w-12 h-12 rounded-xl bg-blue-500/10 flex items-center justify-center text-blue-600">
          <Calendar class="w-6 h-6"/>
        </div>
      </div>
      <div class="bg-gradient-to-br from-emerald-50 to-white border border-emerald-150 p-5 rounded-2xl flex items-center justify-between shadow-xs hover:shadow-md transition-all">
        <div>
          <span class="text-xs font-semibold text-emerald-600 uppercase tracking-wider">Open Months</span>
          <h3 class="text-2xl font-bold text-emerald-850 mt-1 font-mono">{{ openMonthsCount }}</h3>
        </div>
        <div class="w-12 h-12 rounded-xl bg-emerald-500/10 flex items-center justify-center text-emerald-600">
          <Unlock class="w-6 h-6 animate-pulse"/>
        </div>
      </div>
      <div class="bg-gradient-to-br from-rose-50 to-white border border-rose-150 p-5 rounded-2xl flex items-center justify-between shadow-xs hover:shadow-md transition-all">
        <div>
          <span class="text-xs font-semibold text-rose-600 uppercase tracking-wider">Closed Months</span>
          <h3 class="text-2xl font-bold text-rose-850 mt-1 font-mono">{{ closedMonthsCount }}</h3>
        </div>
        <div class="w-12 h-12 rounded-xl bg-rose-500/10 flex items-center justify-center text-rose-600">
          <Lock class="w-6 h-6"/>
        </div>
      </div>
    </div>

    <!-- Header Actions and Paging -->
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-2">
        <button class="px-4 py-2 bg-bfs-gold hover:bg-bfs-gold-dark text-white text-xs font-semibold rounded-lg transition-all flex items-center gap-1.5 cursor-pointer shadow-xs disabled:opacity-60" @click="goToAnnual" :disabled="adding">
          <Loader2 v-if="adding" class="w-4 h-4 animate-spin"/>
          <Plus v-else class="w-4 h-4"/> Add New
        </button>
        <button class="px-4 py-2 border border-gray-200 text-gray-700 bg-white hover:bg-gray-50 text-xs font-semibold rounded-lg transition-all flex items-center gap-1.5 cursor-pointer" @click="openGlobalLog">
          <History class="w-4 h-4 text-gray-500"/> Audit Logs
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

    <!-- Table -->
    <div class="border border-gray-200 rounded-2xl overflow-hidden bg-white shadow-xs max-w-4xl">
      <div v-if="store.isLoading" class="flex flex-col items-center justify-center py-20 text-gray-400 gap-2">
        <Loader2 class="w-8 h-8 animate-spin text-bfs-gold"/>
        <span class="text-xs font-medium">Fetching monthly periods...</span>
      </div>
      <div v-else class="overflow-x-auto">
        <table class="w-full text-left text-xs border-collapse">
          <thead>
            <tr class="bg-gray-50 border-b border-gray-200 text-[11px] font-semibold text-gray-500 uppercase tracking-wider">
              <th class="px-6 py-4 w-16 text-center">No.</th>
              <th class="px-6 py-4">Year</th>
              <th class="px-6 py-4 min-w-[320px] text-center">Months</th>
              <th class="px-6 py-4 w-44 text-center">Status</th>
              <th class="px-6 py-4 w-44 text-right">Action</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-150">
            <tr v-if="pagedData.length === 0">
              <td colspan="5" class="px-6 py-10 text-center text-gray-400 font-medium">No monthly periods created yet.</td>
            </tr>
            <tr v-for="(row, i) in pagedData" :key="row.id" class="hover:bg-blue-50/25 transition-colors">
              <td class="px-6 py-3.5 text-center text-gray-400 font-mono">{{ (currentPage - 1) * perPage + i + 1 }}.</td>
              <td class="px-6 py-3.5 text-bfs-navy font-bold text-sm font-mono tracking-wide">{{ row.year }}</td>
              <td class="px-6 py-3.5 text-center">
                <div class="grid grid-cols-6 gap-1 w-fit mx-auto">
                  <template v-for="m in MONTHS" :key="m.num">
                    <button v-if="getMonth(row, m.num)"
                      class="inline-flex items-center justify-center px-1.5 py-1 rounded-md text-[10px] font-bold border cursor-pointer hover:shadow-xs transition-all w-11"
                      :class="getMonth(row, m.num).status === 'OPEN'
                        ? 'bg-emerald-50 border-emerald-200 text-emerald-700 hover:bg-emerald-100 hover:border-emerald-300'
                        : 'bg-rose-50 border-rose-200 text-rose-700 hover:bg-rose-100 hover:border-rose-300'"
                      @click="openToggle(getMonth(row, m.num), row.year, m)"
                      :title="`${m.name} ${row.year}: ${getMonth(row, m.num).status}`"
                    >
                      {{ m.abbr }}
                    </button>
                    <span v-else class="text-gray-300 font-medium w-11 text-center">—</span>
                  </template>
                </div>
              </td>
              <td class="px-6 py-3.5 text-center">
                <span class="inline-flex px-2.5 py-0.5 rounded-full text-[10px] font-bold border"
                  :class="row.status === 'OPEN' ? 'bg-emerald-50 border-emerald-200 text-emerald-700' : 'bg-rose-50 border-rose-200 text-rose-700'">
                  {{ row.status === 'OPEN' ? 'Open' : 'Close' }}
                </span>
              </td>
              <td class="px-6 py-3.5 text-right">
                <div class="flex justify-end gap-1.5">
                  <button class="px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1 cursor-pointer transition-colors shadow-xs"
                    :class="row.status === 'OPEN' ? 'bg-rose-50 border border-rose-200 hover:bg-rose-100 text-rose-700' : 'bg-emerald-50 border border-emerald-200 hover:bg-emerald-100 text-emerald-700'"
                    @click="openAnnualToggle(row)">
                    <Lock v-if="row.status === 'OPEN'" class="w-3.5 h-3.5"/>
                    <Unlock v-else class="w-3.5 h-3.5"/>
                    {{ row.status === 'OPEN' ? 'Close' : 'Open' }}
                  </button>
                  <button class="p-1.5 border border-gray-200 hover:bg-gray-50 text-gray-500 rounded-lg cursor-pointer transition-colors" @click="openLog(row)" title="Log Activity">
                    <History class="w-4 h-4"/>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modals -->
    <PeriodReasonModal :show="showToggleModal" :is-closing="toggleTarget?.status === 'OPEN'" :period-label="toggleLabel" :loading="toggling" @confirm="handleToggleConfirm" @cancel="showToggleModal = false"/>
    <PeriodLogModal :show="showLogModal" :logs="currentLogs" :period-label="logTarget ? `Year ${logTarget.year}` : 'All Monthly Periods'" :loading="logLoading" @close="showLogModal = false"/>
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
import { CalendarRange, CalendarDays, Calendar, PieChart, History, Lock, Unlock, Plus, Loader2 } from 'lucide-vue-next'

const store = usePeriodStore()
const router = useRouter()

const MONTHS = [
  { num: 1,  abbr: 'Jan', name: 'January'   },
  { num: 2,  abbr: 'Feb', name: 'February'  },
  { num: 3,  abbr: 'Mar', name: 'March'     },
  { num: 4,  abbr: 'Apr', name: 'April'     },
  { num: 5,  abbr: 'May', name: 'May'       },
  { num: 6,  abbr: 'Jun', name: 'June'      },
  { num: 7,  abbr: 'Jul', name: 'July'      },
  { num: 8,  abbr: 'Aug', name: 'August'    },
  { num: 9,  abbr: 'Sep', name: 'September' },
  { num: 10, abbr: 'Oct', name: 'October'   },
  { num: 11, abbr: 'Nov', name: 'November'  },
  { num: 12, abbr: 'Dec', name: 'December'  },
]

const perPage = 15
const currentPage = ref(1)
const totalPages = computed(() => Math.max(1, Math.ceil(store.monthlyPeriods.length / perPage)))
const pagedData = computed(() => {
  const s = (currentPage.value - 1) * perPage
  return store.monthlyPeriods.slice(s, s + perPage)
})

function getMonth(row, mNum) {
  return row.months?.find(m => m.month === mNum) || null
}

function goToAnnual() {
  router.push('/settings/annual-period')
}

// Toggle
const showToggleModal = ref(false)
const toggleTarget = ref(null)
const toggleLabel = ref('')
const toggling = ref(false)
const toggleType = ref('MONTH') // 'MONTH' or 'ANNUAL'

function openToggle(month, year, mObj) {
  toggleType.value = 'MONTH'
  toggleTarget.value = month
  toggleLabel.value = `${mObj.name} ${year}`
  showToggleModal.value = true
}

function openAnnualToggle(row) {
  toggleType.value = 'ANNUAL'
  toggleTarget.value = row
  toggleLabel.value = `Annual Period ${row.year}`
  showToggleModal.value = true
}

async function handleToggleConfirm(reason) {
  toggling.value = true
  try {
    if (toggleType.value === 'ANNUAL') {
      await store.toggleAnnualPeriod(toggleTarget.value.id, reason)
    } else {
      await store.toggleMonthlyPeriod(toggleTarget.value.id, reason)
    }
    showToggleModal.value = false
    await store.fetchMonthlyPeriods()
    Swal.fire({
      icon: 'success',
      title: 'Berhasil!',
      text: `${toggleLabel.value} berhasil ${toggleTarget.value.status === 'OPEN' ? 'ditutup' : 'dibuka'}.`,
      timer: 2000,
      showConfirmButton: false,
    })
  } catch (err) {
    Swal.fire({
      icon: 'error',
      title: 'Gagal!',
      text: err?.response?.data?.detail || 'Terjadi kesalahan.',
    })
  } finally {
    toggling.value = false
  }
}

// Log
const showLogModal = ref(false)
const logTarget = ref(null)
const currentLogs = ref([])
const logLoading = ref(false)

async function openLog(row) {
  logTarget.value = row
  showLogModal.value = true
  logLoading.value = true
  try {
    currentLogs.value = await store.fetchAnnualLogs(row.id)
  } catch {
    currentLogs.value = []
  } finally {
    logLoading.value = false
  }
}

async function openGlobalLog() {
  logTarget.value = null
  showLogModal.value = true
  logLoading.value = true
  try {
    await store.fetchAllLogs({ period_type: 'MONTHLY' })
    currentLogs.value = store.activityLogs
  } catch {
    currentLogs.value = []
  } finally {
    logLoading.value = false
  }
}

// KPI Computeds
const totalMonthsCount = computed(() => {
  return store.monthlyPeriods.reduce((sum, row) => sum + (row.months?.length || 0), 0)
})
const openMonthsCount = computed(() => {
  return store.monthlyPeriods.reduce((sum, row) => sum + (row.months?.filter(m => m.status === 'OPEN').length || 0), 0)
})
const closedMonthsCount = computed(() => {
  return store.monthlyPeriods.reduce((sum, row) => sum + (row.months?.filter(m => m.status === 'CLOSE').length || 0), 0)
})

onMounted(() => store.fetchMonthlyPeriods())
</script>

<style scoped>
@reference "../../style.css";
</style>