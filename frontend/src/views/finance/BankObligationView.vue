<template>
  <div class="p-6 bg-slate-50">
    <!-- Header removed as requested -->

    <!-- Main Card -->
    <div class="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden transition-all duration-300 hover:shadow-md">
      
      <!-- Filters Section -->
      <div class="p-5 border-b border-slate-100 bg-slate-50/50 flex flex-wrap items-center gap-4">
        
        <div class="relative flex-1 min-w-[250px] max-w-md">
          <div class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
            <Search class="w-4 h-4 text-slate-400" />
          </div>
          <input v-model="searchQuery" type="text" class="bg-white border border-slate-300 text-slate-700 text-sm rounded-lg focus:ring-2 focus:ring-bfs-navy/20 focus:border-bfs-navy block w-full pl-10 p-2.5 transition-all placeholder-slate-400" placeholder="Search loan no, amount, angsuran..." />
        </div>
        
        <div class="flex items-center gap-3 bg-white border border-slate-300 rounded-lg p-1 shadow-sm">
          <div class="flex items-center gap-2 pl-3 border-r border-slate-200 pr-3">
            <Calendar class="w-4 h-4 text-slate-500" />
            <span class="text-sm font-medium text-slate-600">From</span>
          </div>
          <input v-model="dateFrom" type="date" class="border-none text-sm text-slate-700 focus:ring-0 cursor-pointer bg-transparent py-1.5" />
        </div>
        
        <ArrowRight class="w-4 h-4 text-slate-400" />
        
        <div class="flex items-center gap-3 bg-white border border-slate-300 rounded-lg p-1 shadow-sm">
          <div class="flex items-center gap-2 pl-3 border-r border-slate-200 pr-3">
            <Calendar class="w-4 h-4 text-slate-500" />
            <span class="text-sm font-medium text-slate-600">To</span>
          </div>
          <input v-model="dateTo" type="date" class="border-none text-sm text-slate-700 focus:ring-0 cursor-pointer bg-transparent py-1.5" />
        </div>

        <button @click="applyFilters" class="flex items-center gap-2 px-5 py-2.5 bg-bfs-navy text-white text-sm font-medium rounded-lg hover:bg-bfs-navy/90 focus:ring-4 focus:ring-bfs-navy/30 transition-all shadow-sm hover:shadow active:scale-95">
          <Filter class="w-4 h-4" />
          Search
        </button>

      </div>

      <!-- Table Section -->
      <div class="overflow-x-auto">
        <table class="w-full text-sm text-left">
          <thead class="bg-slate-100 text-slate-600 font-semibold text-xs uppercase tracking-wider border-b border-slate-200">
            <tr>
              <th class="px-6 py-4 w-12 text-center">
                <div class="flex justify-center">
                  <input type="checkbox" class="w-4 h-4 rounded border-slate-300 text-bfs-navy focus:ring-bfs-navy transition-all cursor-pointer" />
                </div>
              </th>
              <th class="px-4 py-4 w-12 text-center">No</th>
              <th class="px-6 py-4">Loan No</th>
              <th class="px-6 py-4">Document Date</th>
              <th class="px-6 py-4">Due Date</th>
              <th class="px-6 py-4 text-right">Issued Amount</th>
              <th class="px-6 py-4 text-center">Angsuran</th>
              <th class="px-6 py-4 text-center">Sindikasi</th>
              <th class="px-6 py-4 text-center">Closed</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-if="paginatedData.length === 0">
              <td colspan="9" class="px-6 py-12 text-center">
                <div class="flex flex-col items-center justify-center text-slate-500">
                  <FolderSearch class="w-12 h-12 mb-3 text-slate-300" />
                  <p class="text-base font-medium">No records found</p>
                  <p class="text-sm mt-1">Try adjusting your search or filters to find what you're looking for.</p>
                </div>
              </td>
            </tr>
            <tr v-for="(item, idx) in paginatedData" :key="item.id" class="group hover:bg-blue-50/50 transition-colors duration-200">
              <td class="px-6 py-3.5 text-center">
                <div class="flex justify-center">
                  <input type="checkbox" class="w-4 h-4 rounded border-slate-300 text-bfs-navy focus:ring-bfs-navy transition-all cursor-pointer opacity-50 group-hover:opacity-100" />
                </div>
              </td>
              <td class="px-4 py-3.5 text-center text-slate-500 font-medium">{{ (currentPage - 1) * itemsPerPage + idx + 1 }}</td>
              <td class="px-6 py-3.5">
                <span v-if="canUpdate" @click="router.push(`/finance/bank-obligation/edit/${item.id}`)" class="font-semibold text-bfs-navy hover:text-blue-600 cursor-pointer transition-colors border-b border-transparent hover:border-blue-600 pb-0.5">
                  {{ item.loan_no }}
                </span>
                <span v-else class="font-semibold text-slate-700">
                  {{ item.loan_no }}
                </span>
              </td>
              <td class="px-6 py-3.5 text-slate-600">
                <div class="flex items-center gap-2">
                  <CalendarDays class="w-3.5 h-3.5 text-slate-400" />
                  {{ formatDate(item.transaction_date) }}
                </div>
              </td>
              <td class="px-6 py-3.5 text-slate-600">
                <div class="flex items-center gap-2">
                  <CalendarDays class="w-3.5 h-3.5 text-slate-400" />
                  {{ formatDate(item.due_date) }}
                </div>
              </td>
              <td class="px-6 py-3.5 text-right font-mono font-medium text-slate-700">
                {{ formatNumber(item.plafond) }}
              </td>
              <td class="px-6 py-3.5 text-center">
                <span class="inline-flex items-center justify-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-700">
                  {{ item.jangka_waktu }}
                </span>
              </td>
              <td class="px-6 py-3.5 text-center">
                <div class="flex justify-center">
                  <div v-if="item.loan_type === 'SINDIKASI'" class="w-6 h-6 rounded-full bg-emerald-50 flex items-center justify-center" title="Yes">
                    <Check class="w-4 h-4 text-emerald-500" />
                  </div>
                  <div v-else class="w-6 h-6 rounded-full bg-rose-50 flex items-center justify-center" title="No">
                    <X class="w-4 h-4 text-rose-500" />
                  </div>
                </div>
              </td>
              <td class="px-6 py-3.5 text-center">
                <div class="flex justify-center">
                  <div v-if="item.is_closed" class="w-6 h-6 rounded-full bg-slate-100 flex items-center justify-center" title="Closed">
                    <Lock class="w-3.5 h-3.5 text-slate-500" />
                  </div>
                  <div v-else class="w-6 h-6 rounded-full bg-blue-50 flex items-center justify-center" title="Open">
                    <Unlock class="w-3.5 h-3.5 text-blue-500" />
                  </div>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Footer / Paging -->
      <div class="p-4 border-t border-slate-200 bg-slate-50/50 flex flex-wrap items-center justify-between gap-4">
        <button v-if="canCreate" @click="router.push('/finance/bank-obligation/new')" class="group flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-bfs-navy to-blue-800 text-white text-sm font-semibold rounded-lg hover:from-blue-800 hover:to-bfs-navy focus:ring-4 focus:ring-bfs-navy/30 transition-all shadow-md hover:shadow-lg active:scale-95">
          <PlusCircle class="w-4 h-4 transition-transform group-hover:rotate-90" />
          Create New Loan
        </button>
        <!-- Placeholder if no create permission to maintain spacing -->
        <div v-else></div>
        
        <div class="flex items-center gap-4 bg-white px-4 py-2 rounded-lg border border-slate-200 shadow-sm">
          <span class="text-sm font-medium text-slate-500">Page</span>
          <div class="relative">
            <select v-model="currentPage" class="appearance-none bg-slate-50 border border-slate-300 text-slate-700 text-sm font-semibold rounded-md focus:ring-2 focus:ring-bfs-navy/20 focus:border-bfs-navy block w-16 px-3 py-1.5 pr-6 cursor-pointer">
              <option v-for="page in totalPages" :key="page" :value="page">{{ page }}</option>
            </select>
            <ChevronDown class="w-3.5 h-3.5 absolute right-2 top-2.5 text-slate-500 pointer-events-none" />
          </div>
          <span class="text-sm text-slate-500 font-medium">of <span class="text-slate-800">{{ totalPages }}</span></span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { usePermission } from '../../composables/usePermission'
import api from '../../services/api'
import { 
  Banknote, ChevronRight, ChevronDown, Search, 
  Filter, RotateCcw, Calendar, ArrowRight, 
  FolderSearch, CalendarDays, Check, X, 
  Lock, Unlock, PlusCircle 
} from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)

const { canCreate, canUpdate, canDelete } = usePermission('FINANCE-BANK-OBLIGATION')

const bankObligations = ref([])

onMounted(async () => {
  await fetchData()
})

const fetchData = async () => {
  try {
    loading.value = true
    const res = await api.get(`accounting/bank-obligation/?company_id=${authStore.activeCompanyId}`)
    bankObligations.value = res.data.results || res.data
  } catch (err) {
    console.error('Failed to fetch bank obligations:', err)
  } finally {
    loading.value = false
  }
}

// -- Filters --
const searchQuery = ref('')

// Default date from 1st day of month to last day of month
const getFirstDayOfMonth = () => {
  const d = new Date()
  return new Date(d.getFullYear(), d.getMonth(), 1).toLocaleDateString('en-CA')
}
const getLastDayOfMonth = () => {
  const d = new Date()
  return new Date(d.getFullYear(), d.getMonth() + 1, 0).toLocaleDateString('en-CA')
}

const dateFrom = ref(getFirstDayOfMonth())
const dateTo = ref(getLastDayOfMonth())

// -- Paging --
const currentPage = ref(1)
const itemsPerPage = 10

// Filtered data computed property
const filteredData = computed(() => {
  let result = [...bankObligations.value]
  
  // Date filter
  if (dateFrom.value) {
    result = result.filter(item => item.transaction_date >= dateFrom.value)
  }
  if (dateTo.value) {
    result = result.filter(item => item.transaction_date <= dateTo.value)
  }
  
  // Search text filter across multiple fields
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(item => {
      const matchLoanNo = String(item.loan_no).toLowerCase().includes(query)
      const matchAmount = String(item.plafond).toLowerCase().includes(query)
      const matchAngsuran = String(item.jangka_waktu).toLowerCase().includes(query)
      
      let matchSindikasi = false
      if (query === 'yes' || query === 'y') matchSindikasi = item.loan_type === 'SINDIKASI'
      else if (query === 'no' || query === 'n') matchSindikasi = item.loan_type !== 'SINDIKASI'
      
      let matchClosed = false
      if (query === 'yes' || query === 'y') matchClosed = item.is_closed === true
      else if (query === 'no' || query === 'n') matchClosed = item.is_closed === false

      return matchLoanNo || matchAmount || matchAngsuran || matchSindikasi || matchClosed
    })
  }
  
  return result
})

// Paginated data computed property
const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredData.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredData.value.length / itemsPerPage) || 1
})

// -- Actions --
const applyFilters = () => {
  currentPage.value = 1 // Reset to first page
}

const resetFilters = () => {
  searchQuery.value = ''
  dateFrom.value = getFirstDayOfMonth()
  dateTo.value = getLastDayOfMonth()
  currentPage.value = 1
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }).replace(/ /g, '-')
}

const formatNumber = (val) => {
  if (!val) return '0.00'
  return new Intl.NumberFormat('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(val)
}
</script>
