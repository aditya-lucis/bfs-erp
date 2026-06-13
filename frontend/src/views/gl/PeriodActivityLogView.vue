<template>
  <Panel title="Period Activity Log" subtitle="Setting | Accounting Setting | Period Activity Log">
    
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

    <!-- Search & Filter Card -->
    <div class="bg-gray-50 rounded-2xl border border-gray-150 p-5 mb-6 space-y-4">
      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
        <div class="space-y-1">
          <label class="block text-[10px] font-bold text-gray-500 uppercase tracking-wider">Search Field</label>
          <select v-model="filterField" class="w-full px-3 py-2 text-xs border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-bfs-gold/30 focus:border-bfs-gold transition-all bg-white">
            <option value="period">Period Name / Label</option>
            <option value="action">Action</option>
            <option value="reason">Reason</option>
          </select>
        </div>

        <div class="space-y-1">
          <label class="block text-[10px] font-bold text-gray-500 uppercase tracking-wider">Operator</label>
          <select v-model="filterOp" class="w-full px-3 py-2 text-xs border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-bfs-gold/30 focus:border-bfs-gold transition-all bg-white">
            <option value="contains">Any Part of Field</option>
            <option value="starts">Starts With</option>
          </select>
        </div>

        <div class="space-y-1 md:col-span-2">
          <label class="block text-[10px] font-bold text-gray-500 uppercase tracking-wider">Search Query</label>
          <div class="relative">
            <input
              v-model="searchQuery"
              type="text"
              class="w-full pl-3 pr-10 py-2 text-xs border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-bfs-gold/30 focus:border-bfs-gold transition-all bg-white"
              placeholder="Filter by name, actions or comments..."
              @keyup.enter="applyFilter"
            />
            <Search class="absolute right-3 top-2.5 w-4 h-4 text-gray-400" />
          </div>
        </div>
      </div>

      <div class="flex flex-wrap items-center justify-between gap-3 pt-2">
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-2">
            <span class="text-[10px] font-bold text-gray-500 uppercase tracking-wider">Period Type:</span>
            <select v-model="filterPeriodType" class="px-3 py-1.5 text-xs border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-bfs-gold/30 focus:border-bfs-gold bg-white">
              <option value="">ALL TYPES</option>
              <option value="ANNUAL">Annual</option>
              <option value="QUARTER">Quarter</option>
              <option value="MONTHLY">Monthly</option>
              <option value="ACCOUNTING">Accounting</option>
            </select>
          </div>
          
          <div class="flex items-center gap-2">
            <span class="text-[10px] font-bold text-gray-500 uppercase tracking-wider">Status:</span>
            <select v-model="filterStatus" class="px-3 py-1.5 text-xs border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-bfs-gold/30 focus:border-bfs-gold bg-white">
              <option value="">ALL STATUS</option>
              <option value="OPEN">Open</option>
              <option value="CLOSE">Close</option>
            </select>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <button @click="applyFilter" class="px-5 py-2 bg-bfs-navy hover:bg-bfs-navy-light text-white text-xs font-semibold rounded-lg transition-all flex items-center gap-1.5 cursor-pointer shadow-xs">
            <Search class="w-3.5 h-3.5" /> Search
          </button>
          <button @click="resetFilter" class="px-5 py-2 border border-gray-200 text-gray-700 bg-white hover:bg-gray-50 text-xs font-semibold rounded-lg transition-all flex items-center gap-1.5 cursor-pointer">
            <RefreshCw class="w-3.5 h-3.5 text-gray-500" /> Reset All
          </button>
        </div>
      </div>
    </div>

    <!-- Table Container -->
    <div class="border border-gray-200 rounded-2xl overflow-hidden bg-white shadow-xs">
      <div v-if="store.isLoading" class="flex flex-col items-center justify-center py-20 text-gray-400 gap-2">
        <Loader2 class="w-8 h-8 animate-spin text-bfs-gold" />
        <span class="text-xs font-medium">Fetching period logs...</span>
      </div>

      <div v-else-if="filteredLogs.length === 0" class="flex flex-col items-center justify-center py-20 text-gray-400 gap-3">
        <div class="w-12 h-12 rounded-full bg-gray-50 flex items-center justify-center">
          <Inbox class="w-6 h-6 text-gray-400" />
        </div>
        <p class="text-xs font-medium">No activity log records found.</p>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full text-left text-xs border-collapse">
          <thead>
            <tr class="bg-gray-50 border-b border-gray-200 text-[11px] font-semibold text-gray-500 uppercase tracking-wider">
              <th class="px-6 py-4 w-16 text-center">No.</th>
              <th class="px-6 py-4 w-28">Period Type</th>
              <th class="px-6 py-4 w-40">Period Label</th>
              <th class="px-6 py-4">Action Reason</th>
              <th class="px-6 py-4 w-28 text-center">Status After</th>
              <th class="px-6 py-4 w-44">Actioned By</th>
              <th class="px-6 py-4 w-48">Timestamp</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-150">
            <tr v-for="(log, i) in pagedLogs" :key="log.id" class="hover:bg-blue-50/25 transition-colors">
              <td class="px-6 py-3.5 text-center text-gray-400 font-mono">{{ (currentPage - 1) * perPage + i + 1 }}.</td>
              <td class="px-6 py-3.5">
                <span class="px-2 py-0.5 rounded-full text-[10px] font-bold border" :class="periodTypeClass(log.period_type)">
                  {{ log.period_type }}
                </span>
              </td>
              <td class="px-6 py-3.5 text-bfs-navy font-semibold">{{ log.period_label }}</td>
              <td class="px-6 py-3.5 text-gray-650 font-sans leading-relaxed whitespace-pre-wrap">{{ log.reason }}</td>
              <td class="px-6 py-3.5 text-center">
                <span class="inline-flex px-2.5 py-0.5 rounded-full text-[10px] font-bold border" :class="log.period_status_after === 'OPEN' ? 'bg-emerald-50 border-emerald-200 text-emerald-700' : 'bg-rose-50 border-rose-200 text-rose-700'">
                  {{ log.period_status_after === 'OPEN' ? 'Open' : 'Close' }}
                </span>
              </td>
              <td class="px-6 py-3.5 text-gray-700 font-medium">{{ log.actioned_by_name || '-' }}</td>
              <td class="px-6 py-3.5 text-gray-500 font-mono">{{ formatDateTime(log.actioned_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination Footer -->
      <div v-if="filteredLogs.length > perPage" class="flex items-center justify-between px-6 py-4 bg-gray-50 border-t border-gray-150 shrink-0">
        <span class="text-xs text-gray-450 font-medium">
          Showing page {{ currentPage }} of {{ totalPages }}
        </span>
        
        <div class="flex items-center gap-2">
          <button
            class="w-8 h-8 rounded-lg border border-gray-200 bg-white hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-all flex items-center justify-center cursor-pointer text-gray-600"
            :disabled="currentPage === 1"
            @click="currentPage--"
          >
            <ChevronLeft class="w-4 h-4" />
          </button>
          <span class="text-xs font-semibold text-gray-700 px-2">{{ currentPage }}</span>
          <button
            class="w-8 h-8 rounded-lg border border-gray-200 bg-white hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-all flex items-center justify-center cursor-pointer text-gray-600"
            :disabled="currentPage === totalPages"
            @click="currentPage++"
          >
            <ChevronRight class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  </Panel>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { usePeriodStore } from '../../stores/period.js'
import Panel from '../../components/Panel.vue'
import {
  CalendarRange,
  CalendarDays,
  PieChart,
  Calendar,
  History,
  Search,
  RefreshCw,
  Loader2,
  Inbox,
  ChevronLeft,
  ChevronRight
} from 'lucide-vue-next'

const store = usePeriodStore()

const perPage = 15
const currentPage = ref(1)
const searchQuery = ref('')
const filterField = ref('period')
const filterOp = ref('contains')
const filterStatus = ref('')
const filterPeriodType = ref('')

const activeQuery = ref('')
const activeField = ref('period')
const activeStatus = ref('')
const activePeriodType = ref('')

function applyFilter() {
  activeQuery.value = searchQuery.value
  activeField.value = filterField.value
  activeStatus.value = filterStatus.value
  activePeriodType.value = filterPeriodType.value
  currentPage.value = 1
}

function resetFilter() {
  searchQuery.value = ''
  filterField.value = 'period'
  filterOp.value = 'contains'
  filterStatus.value = ''
  filterPeriodType.value = ''
  
  activeQuery.value = ''
  activeField.value = 'period'
  activeStatus.value = ''
  activePeriodType.value = ''
  currentPage.value = 1
}

const filteredLogs = computed(() => {
  let logs = store.activityLogs
  
  if (activeStatus.value) {
    logs = logs.filter(l => l.period_status_after === activeStatus.value)
  }
  
  if (activePeriodType.value) {
    logs = logs.filter(l => l.period_type === activePeriodType.value)
  }
  
  if (activeQuery.value) {
    const q = activeQuery.value.toLowerCase()
    logs = logs.filter(l => {
      const field = activeField.value === 'reason' ? l.reason
        : activeField.value === 'action' ? l.action
        : l.period_label
      return (field || '').toLowerCase().includes(q)
    })
  }
  
  return logs
})

const totalPages = computed(() => Math.max(1, Math.ceil(filteredLogs.value.length / perPage)))

const pagedLogs = computed(() => {
  const start = (currentPage.value - 1) * perPage
  return filteredLogs.value.slice(start, start + perPage)
})

function formatDateTime(dt) {
  if (!dt) return '-'
  const d = new Date(dt)
  const pad = n => String(n).padStart(2, '0')
  return `${pad(d.getDate())}-${d.toLocaleString('en', { month: 'short' })}-${d.getFullYear()} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
}

function periodTypeClass(type) {
  const map = {
    ANNUAL: 'bg-purple-50 text-purple-700 border-purple-200',
    QUARTER: 'bg-blue-50 text-blue-700 border-blue-200',
    MONTHLY: 'bg-orange-50 text-orange-700 border-orange-200',
    ACCOUNTING: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  }
  return map[type] || 'bg-gray-50 text-gray-700 border-gray-200'
}

onMounted(() => {
  store.fetchAllLogs()
})
</script>

<style scoped>
@reference "../../style.css";
</style>
