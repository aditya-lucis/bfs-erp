<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'
import Panel from '../../components/Panel.vue'
import { useAuthStore } from '../../stores/auth'
import Swal from 'sweetalert2'

// Icons
import {
  Plus, Search, SearchX, FileText, CheckCircle, Clock, AlertCircle, FileCheck, FileX, FileWarning, FileClock, Folder, FolderOpen, FolderCheck, Pencil, Send, Trash2, Loader2
} from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()

const items = ref([])
const loading = ref(false)
const error = ref(null)

const canCreate = computed(() => authStore.hasPermission('GL-GENERAL-JOURNAL_CREATE'))
const canUpdate = computed(() => authStore.hasPermission('GL-GENERAL-JOURNAL_UPDATE'))
const canDelete = computed(() => authStore.hasPermission('GL-GENERAL-JOURNAL_DELETE'))

const today = new Date()
const firstDay = new Date(today.getFullYear(), today.getMonth(), 1)
const lastDay = new Date(today.getFullYear(), today.getMonth() + 1, 0)

// Filters
const filterDateFrom = ref(firstDay.toISOString().substring(0, 10))
const filterDateTo = ref(lastDay.toISOString().substring(0, 10))
const searchQuery = ref('')
const filterDocStatus = ref('')
const filterAppStatus = ref('')

const fetchJournals = async () => {
  loading.value = true
  error.value = null
  try {
    const params = {}
    if (searchQuery.value) params.search = searchQuery.value
    if (filterDateFrom.value) params.date_from = filterDateFrom.value
    if (filterDateTo.value) params.date_to = filterDateTo.value
    if (filterDocStatus.value) params.document_status = filterDocStatus.value
    if (filterAppStatus.value) params.approval_status = filterAppStatus.value
    
    const response = await api.get('/accounting/general-journals/', { params })
    items.value = response.data.results || response.data
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to fetch general journals'
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  fetchJournals()
}

const handleResetFilters = () => {
  searchQuery.value = ''
  filterDateFrom.value = ''
  filterDateTo.value = ''
  filterDocStatus.value = ''
  filterAppStatus.value = ''
  fetchJournals()
}

const submitApproval = async (item) => {
  const result = await Swal.fire({
    title: 'Are you sure?',
    text: `You want to submit journal ${item.transaction_number} for approval?`,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#1e3a8a',
    cancelButtonColor: '#d33',
    confirmButtonText: 'Yes, submit it!'
  })
  
  if (!result.isConfirmed) return
  
  loading.value = true
  try {
    await api.post(`/accounting/general-journals/${item.id}/submit_approval/`)
    fetchJournals()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to submit for approval'
  } finally {
    loading.value = false
  }
}

const deleteItem = async (item) => {
  const result = await Swal.fire({
    title: 'Are you sure?',
    text: `You want to delete journal ${item.transaction_number}?`,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#1e3a8a',
    cancelButtonColor: '#d33',
    confirmButtonText: 'Yes, delete it!'
  })
  
  if (!result.isConfirmed) return
  
  loading.value = true
  try {
    await api.delete(`/accounting/general-journals/${item.id}/`)
    fetchJournals()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to delete journal'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchJournals()
})

const navigateToEntry = (id = null) => {
  if (id) {
    router.push(`/gl/general-journal-transaction/entry/${id}`)
  } else {
    router.push('/gl/general-journal-transaction/entry')
  }
}

const formatDocStatusText = (status) => {
  return status || 'Draft'
}

const formatAppStatusText = (status) => {
  return status || 'Draft'
}

</script>

<template>
  <Panel title="General Journal Transactions" subtitle="General Ledger | General Journal | General Journal Transaction">
    
    <!-- Toolbar/Search/Filter -->
    <div class="flex flex-col gap-4 mb-6">
      <div class="flex flex-wrap items-center gap-4">
        <!-- Search -->
        <div class="flex items-center border border-gray-200 rounded-lg overflow-hidden bg-white">
          <span class="px-3 py-1.5 bg-gray-50 text-xs text-gray-500 border-r border-gray-200">Search</span>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Type Journal Number or Memo..."
            class="px-3 py-1.5 text-xs focus:outline-none w-48 sm:w-64"
            @keyup.enter="handleSearch"
          />
        </div>

        <!-- Date Range -->
        <div class="flex items-center gap-2 text-xs">
          <span class="text-gray-500 font-semibold uppercase">Date From:</span>
          <input v-model="filterDateFrom" type="date" class="border border-gray-200 rounded px-2 py-1 bg-white text-xs focus:outline-none" />
          <span class="text-gray-500 font-semibold uppercase">To:</span>
          <input v-model="filterDateTo" type="date" class="border border-gray-200 rounded px-2 py-1 bg-white text-xs focus:outline-none" />
        </div>

        <button
          @click="handleSearch"
          class="px-3 py-1.5 bg-bfs-navy hover:bg-bfs-navy-dark text-white text-xs font-medium rounded-lg transition-colors flex items-center gap-1.5 cursor-pointer"
        >
          <Search class="w-3.5 h-3.5" /> Search
        </button>
        <button
          @click="handleResetFilters"
          class="btn-secondary text-xs px-3 py-1.5 flex items-center gap-1.5"
        >
          Reset
        </button>
      </div>

      <div class="flex flex-wrap items-center justify-between gap-4 border-t border-gray-100 pt-4">
        <div class="flex flex-wrap items-center gap-4 text-xs">
          
          <!-- Filter Status -->
          <div class="border border-gray-200 rounded-lg px-3 py-1.5 relative bg-white flex items-center gap-2 shadow-sm min-h-[38px]">
            <span class="absolute -top-2 left-2 bg-white px-1 text-[9px] font-bold text-gray-500 uppercase tracking-wider">Filter Status</span>
            <button 
              @click="filterDocStatus = ''; handleSearch()" 
              class="px-1.5 py-0.5 rounded text-[10px] font-bold transition-colors cursor-pointer"
              :class="filterDocStatus === '' ? 'bg-bfs-navy text-white' : 'hover:bg-gray-100 text-gray-400'"
            >
              ALL
            </button>
            <button 
              @click="filterDocStatus = 'DRAFT'; handleSearch()" 
              class="p-0.5 rounded transition-all cursor-pointer"
              :class="filterDocStatus === 'DRAFT' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"
            >
              <Folder class="w-4 h-4 text-amber-500 fill-amber-500/10" />
            </button>
            <button 
              @click="filterDocStatus = 'IN_REVIEW'; handleSearch()" 
              class="p-0.5 rounded transition-all cursor-pointer"
              :class="filterDocStatus === 'IN_REVIEW' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"
            >
              <FolderOpen class="w-4 h-4 text-blue-500 fill-blue-500/10" />
            </button>
            <button 
              @click="filterDocStatus = 'APPROVED'; handleSearch()" 
              class="p-0.5 rounded transition-all cursor-pointer"
              :class="filterDocStatus === 'APPROVED' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"
            >
              <FolderCheck class="w-4 h-4 text-green-500 fill-green-500/10" />
            </button>
          </div>

          <!-- Approval Filter Status -->
          <div class="border border-gray-200 rounded-lg px-3 py-1.5 relative bg-white flex items-center gap-2 shadow-sm min-h-[38px]">
            <span class="absolute -top-2 left-2 bg-white px-1 text-[9px] font-bold text-gray-500 uppercase tracking-wider">Approval Filter Status</span>
            <button 
              @click="filterAppStatus = ''; handleSearch()" 
              class="px-1.5 py-0.5 rounded text-[10px] font-bold transition-colors cursor-pointer"
              :class="filterAppStatus === '' ? 'bg-bfs-navy text-white' : 'hover:bg-gray-100 text-gray-400'"
            >
              ALL
            </button>
            <button 
              @click="filterAppStatus = 'DRAFT'; handleSearch()" 
              class="p-0.5 rounded transition-all cursor-pointer"
              :class="filterAppStatus === 'DRAFT' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"
            >
              <FileText class="w-4 h-4 text-gray-400" />
            </button>
            <button 
              @click="filterAppStatus = 'IN_REVIEW'; handleSearch()" 
              class="p-0.5 rounded transition-all cursor-pointer"
              :class="filterAppStatus === 'IN_REVIEW' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"
            >
              <FileClock class="w-4 h-4 text-bfs-gold animate-pulse" />
            </button>
            <button 
              @click="filterAppStatus = 'APPROVED'; handleSearch()" 
              class="p-0.5 rounded transition-all cursor-pointer"
              :class="filterAppStatus === 'APPROVED' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"
            >
              <FileCheck class="w-4 h-4 text-green-500" />
            </button>
            <button 
              @click="filterAppStatus = 'REJECTED'; handleSearch()" 
              class="p-0.5 rounded transition-all cursor-pointer"
              :class="filterAppStatus === 'REJECTED' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"
            >
              <FileX class="w-4 h-4 text-red-500" />
            </button>
            <button 
              @click="filterAppStatus = 'CANCELLED'; handleSearch()" 
              class="p-0.5 rounded transition-all cursor-pointer"
              :class="filterAppStatus === 'CANCELLED' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"
            >
              <FileWarning class="w-4 h-4 text-orange-500" />
            </button>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex items-center justify-between gap-3 bg-slate-50/50 p-2 rounded-lg border border-slate-200">
          <div class="flex items-center gap-2">
            <button 
              v-if="canCreate"
              @click="navigateToEntry()"
              class="btn-primary text-sm flex items-center gap-2 px-3 py-1.5 shadow-sm"
            >
              <Plus class="w-4 h-4" /> Add General Journal
            </button>
          </div>
          <div class="flex items-center gap-2">
          </div>
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="error" class="mb-4">
      <div class="flex items-center gap-3 p-4 bg-red-50 text-red-700 rounded-lg border border-red-100">
        <AlertCircle class="w-5 h-5 shrink-0" />
        <p class="text-sm font-medium">{{ error }}</p>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-16">
      <Loader2 class="w-6 h-6 animate-spin text-bfs-gold" />
    </div>

    <!-- Table List -->
    <div v-else-if="items.length" class="border border-gray-200 rounded-xl overflow-hidden bg-white shadow-sm">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-gray-50 border-b border-gray-200 text-[11px] font-semibold text-gray-600 uppercase tracking-wider">
              <th class="py-3 px-4 w-12 text-center">No.</th>
              <th class="py-3 px-4">General Journal Number</th>
              <th class="py-3 px-4">General Journal Date</th>
              <th class="py-3 px-4">General Journal Description</th>
              <th class="py-3 px-4 text-center">Document Status</th>
              <th class="py-3 px-4 text-center">Approval</th>
              <th class="py-3 px-4 w-20 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr
              v-for="(item, idx) in items"
              :key="item.id"
              class="hover:bg-yellow-50/20 transition-colors text-xs text-gray-700"
            >
              <td class="py-3 px-4 text-center font-medium text-gray-400">{{ idx + 1 }}.</td>
              <td class="py-3 px-4 font-mono text-gray-600 font-semibold">{{ item.transaction_number }}</td>
              <td class="py-3 px-4">{{ item.date }}</td>
              <td class="py-3 px-4 truncate max-w-[200px]" :title="item.memo">{{ item.memo }}</td>
              <td class="py-3 px-4 text-center">
                <div
                  class="inline-flex items-center justify-center p-1 rounded-md"
                  :title="'Document Status: ' + formatDocStatusText(item.status)"
                >
                  <Folder v-if="item.status === 'DRAFT' || item.status === 'REJECTED' || item.status === 'CANCELLED'" class="w-4.5 h-4.5 text-amber-500 fill-amber-500/10" />
                  <FolderOpen v-else-if="item.status === 'IN_REVIEW'" class="w-4.5 h-4.5 text-blue-500 fill-blue-500/10" />
                  <FolderCheck v-else-if="item.status === 'APPROVED'" class="w-4.5 h-4.5 text-green-500 fill-green-500/10" />
                </div>
              </td>
              <td class="py-3 px-4 text-center">
                <div
                  class="inline-flex items-center justify-center p-1 rounded-md"
                  :title="'Approval Status: ' + formatAppStatusText(item.status)"
                >
                  <FileText v-if="item.status === 'DRAFT'" class="w-4.5 h-4.5 text-gray-400" />
                  <FileClock v-else-if="item.status === 'IN_REVIEW'" class="w-4.5 h-4.5 text-bfs-gold animate-pulse" />
                  <FileCheck v-else-if="item.status === 'APPROVED'" class="w-4.5 h-4.5 text-green-500" />
                  <FileX v-else-if="item.status === 'REJECTED'" class="w-4.5 h-4.5 text-red-500" />
                  <FileWarning v-else-if="item.status === 'CANCELLED'" class="w-4.5 h-4.5 text-orange-500" />
                </div>
              </td>
              <td class="py-2.5 px-4 text-center">
                <div class="flex justify-center gap-2">
                  <button 
                    v-if="canUpdate"
                    @click="navigateToEntry(item.id)" 
                    class="p-1.5 rounded-md hover:bg-slate-100 text-slate-500 hover:text-bfs-navy transition-colors"
                    title="Edit / View"
                  >
                    <Pencil class="w-4 h-4" />
                  </button>
                  <button 
                    v-else
                    @click="navigateToEntry(item.id)" 
                    class="p-1.5 rounded-md hover:bg-slate-100 text-slate-500 hover:text-bfs-navy transition-colors"
                    title="View"
                  >
                    <FileText class="w-4 h-4" />
                  </button>
                  
                  <button 
                    v-if="(item.status === 'DRAFT' || item.status === 'CANCELLED') && canUpdate"
                    @click="submitApproval(item)"
                    class="p-1.5 rounded-md hover:bg-green-50 text-slate-500 hover:text-green-600 transition-colors"
                    title="Submit for Approval"
                  >
                    <Send class="w-4 h-4" />
                  </button>
                  <button 
                    v-if="(item.status === 'DRAFT' || item.status === 'REJECTED' || item.status === 'CANCELLED') && canDelete"
                    @click="deleteItem(item)"
                    class="p-1.5 rounded-md hover:bg-red-50 text-slate-500 hover:text-red-600 transition-colors"
                    title="Delete"
                  >
                    <Trash2 class="w-4 h-4" />
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
      <FileText class="w-12 h-12 mb-3 text-gray-300" />
      <p class="text-sm">No general journals found.</p>
    </div>

  </Panel>
</template>
