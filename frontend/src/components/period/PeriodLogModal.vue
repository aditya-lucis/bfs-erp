<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/45 backdrop-blur-xs" @click.self="$emit('close')">
        <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[85vh] flex flex-col overflow-hidden transform transition-all animate-in fade-in zoom-in-95 duration-250">
          
          <!-- Header -->
          <div class="flex items-center justify-between px-6 py-4.5 bg-gradient-to-r from-bfs-navy to-bfs-navy-light text-white shrink-0">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 bg-white/10 rounded-full flex items-center justify-center">
                <History class="w-5 h-5 text-bfs-gold-light" />
              </div>
              <div>
                <h3 class="font-bold text-sm tracking-wide">Log Activity</h3>
                <p class="text-xs text-white/80 mt-0.5">{{ periodLabel }}</p>
              </div>
            </div>
            <button @click="$emit('close')" class="p-1.5 rounded-full hover:bg-white/10 text-white/80 hover:text-white transition-colors">
              <X class="w-4 h-4" />
            </button>
          </div>

          <!-- Search Bar Grid -->
          <div class="grid grid-cols-1 sm:grid-cols-4 gap-4 p-5 bg-gray-50 border-b border-gray-100 shrink-0">
            <div class="space-y-1">
              <label class="block text-[10px] font-semibold text-gray-500 uppercase tracking-wider">Search Field</label>
              <select v-model="filterField" class="w-full px-3 py-1.5 text-xs border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-bfs-gold/30 focus:border-bfs-gold transition-all bg-white">
                <option value="period">Period</option>
                <option value="action">Action</option>
                <option value="reason">Reason</option>
              </select>
            </div>
            <div class="space-y-1">
              <label class="block text-[10px] font-semibold text-gray-500 uppercase tracking-wider">Operator</label>
              <select v-model="filterOp" class="w-full px-3 py-1.5 text-xs border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-bfs-gold/30 focus:border-bfs-gold transition-all bg-white">
                <option value="contains">Any Part of Field</option>
                <option value="starts">Starts With</option>
              </select>
            </div>
            <div class="space-y-1 sm:col-span-2">
              <label class="block text-[10px] font-semibold text-gray-500 uppercase tracking-wider">Search Value</label>
              <div class="relative">
                <input
                  v-model="searchQuery"
                  type="text"
                  class="w-full pl-3 pr-8 py-1.5 text-xs border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-bfs-gold/30 focus:border-bfs-gold transition-all bg-white"
                  placeholder="Type to search..."
                  @keyup.enter="applyFilter"
                />
                <button @click="applyFilter" class="absolute right-2 top-1.5 text-gray-400 hover:text-bfs-gold">
                  <Search class="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>

          <!-- Filter / Action Row -->
          <div class="flex flex-wrap items-center justify-between gap-3 px-5 py-3 border-b border-gray-100 bg-gray-50/50 shrink-0">
            <div class="flex items-center gap-2">
              <select v-model="filterStatus" class="px-3 py-1.5 text-xs border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-bfs-gold/30 focus:border-bfs-gold bg-white">
                <option value="">ALL STATUS</option>
                <option value="OPEN">Open</option>
                <option value="CLOSE">Close</option>
              </select>
              <button class="px-4 py-1.5 bg-bfs-navy hover:bg-bfs-navy-light text-white rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5 cursor-pointer shadow-xs" @click="applyFilter">
                <Search class="w-3.5 h-3.5" /> Search
              </button>
              <button class="px-4 py-1.5 border border-gray-200 text-gray-700 bg-white hover:bg-gray-50 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5 cursor-pointer" @click="resetFilter">
                <RefreshCw class="w-3.5 h-3.5 text-gray-500" /> Reset
              </button>
            </div>
            <span class="text-xs text-gray-400 font-medium">
              Total: <span class="text-gray-700 font-bold">{{ filteredLogs.length }}</span> logs
            </span>
          </div>

          <!-- Table Content Area -->
          <div class="flex-1 overflow-auto">
            <div v-if="loading" class="flex flex-col items-center justify-center py-20 text-gray-400 gap-2">
              <Loader2 class="w-7 h-7 animate-spin text-bfs-gold" />
              <span class="text-xs font-medium">Loading log activities...</span>
            </div>
            
            <div v-else-if="filteredLogs.length === 0" class="flex flex-col items-center justify-center py-20 text-gray-400 gap-3">
              <div class="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center">
                <Inbox class="w-6 h-6 text-gray-400" />
              </div>
              <span class="text-xs font-medium">No activity logs found.</span>
            </div>

            <table v-else class="w-full text-left text-xs border-collapse">
              <thead>
                <tr class="bg-gray-100/75 border-b border-gray-200 sticky top-0 z-10">
                  <th class="px-4 py-3 font-semibold text-gray-500 uppercase tracking-wider text-[10px] w-12 text-center">No.</th>
                  <th class="px-4 py-3 font-semibold text-gray-500 uppercase tracking-wider text-[10px] w-44">Edit Date</th>
                  <th class="px-4 py-3 font-semibold text-gray-500 uppercase tracking-wider text-[10px]">Reason</th>
                  <th class="px-4 py-3 font-semibold text-gray-500 uppercase tracking-wider text-[10px] w-28 text-center">Month</th>
                  <th class="px-4 py-3 font-semibold text-gray-500 uppercase tracking-wider text-[10px] w-24 text-center">Year</th>
                  <th class="px-4 py-3 font-semibold text-gray-500 uppercase tracking-wider text-[10px] w-32 text-center">Status After</th>
                  <th class="px-4 py-3 font-semibold text-gray-500 uppercase tracking-wider text-[10px] w-36">User</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-150">
                <tr
                  v-for="(log, i) in pagedLogs"
                  :key="log.id"
                  class="hover:bg-blue-50/35 transition-colors"
                >
                  <td class="px-4 py-3.5 text-center text-gray-400 font-mono">{{ (currentPage - 1) * perPage + i + 1 }}.</td>
                  <td class="px-4 py-3.5 text-gray-600 font-medium">{{ formatDateTime(log.actioned_at) }}</td>
                  <td class="px-4 py-3.5 text-gray-700 whitespace-pre-wrap leading-relaxed font-sans">{{ log.reason }}</td>
                  <td class="px-4 py-3.5 text-center text-gray-600">{{ extractMonth(log.period_label) }}</td>
                  <td class="px-4 py-3.5 text-center text-gray-600 font-mono">{{ extractYear(log.period_label) }}</td>
                  <td class="px-4 py-3.5 text-center">
                    <span
                      class="inline-flex px-2.5 py-0.5 rounded-full text-[10px] font-bold border"
                      :class="log.period_status_after === 'OPEN'
                        ? 'bg-emerald-50 border-emerald-200 text-emerald-700'
                        : 'bg-rose-50 border-rose-200 text-rose-700'"
                    >
                      {{ log.period_status_after === 'OPEN' ? 'Open' : 'Close' }}
                    </span>
                  </td>
                  <td class="px-4 py-3.5 text-gray-700 font-medium">{{ log.actioned_by_name || '-' }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Footer pagination -->
          <div class="flex items-center justify-between px-6 py-4 bg-gray-50 border-t border-gray-150 shrink-0" v-if="filteredLogs.length > perPage">
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
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { History, X, Search, RefreshCw, Loader2, Inbox, ChevronLeft, ChevronRight } from 'lucide-vue-next'

const props = defineProps({
  show:        { type: Boolean, default: false },
  logs:        { type: Array, default: () => [] },
  periodLabel: { type: String, default: 'Period' },
  loading:     { type: Boolean, default: false },
})
defineEmits(['close'])

const perPage     = 10
const currentPage = ref(1)
const searchQuery = ref('')
const filterField = ref('period')
const filterOp    = ref('contains')
const filterStatus = ref('')
const activeQuery  = ref('')
const activeField  = ref('period')
const activeStatus = ref('')

function applyFilter() {
  activeQuery.value  = searchQuery.value
  activeField.value  = filterField.value
  activeStatus.value = filterStatus.value
  currentPage.value  = 1
}

function resetFilter() {
  searchQuery.value  = ''
  filterField.value  = 'period'
  filterOp.value     = 'contains'
  filterStatus.value = ''
  activeQuery.value  = ''
  activeField.value  = 'period'
  activeStatus.value = ''
  currentPage.value  = 1
}

watch(() => props.show, (val) => {
  if (val) resetFilter()
})

const filteredLogs = computed(() => {
  let logs = props.logs
  if (activeStatus.value) {
    logs = logs.filter(l => l.period_status_after === activeStatus.value)
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

function extractMonth(label) {
  if (!label) return '-'
  const parts = label.split(' ')
  if (parts.length >= 2 && isNaN(parts[0])) return parts[0]
  return '-'
}

function extractYear(label) {
  if (!label) return '-'
  const parts = label.split(' ')
  return parts[parts.length - 1] || '-'
}
</script>

<style scoped>
.modal-enter-active, .modal-leave-active { transition: opacity 0.2s; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
</style>