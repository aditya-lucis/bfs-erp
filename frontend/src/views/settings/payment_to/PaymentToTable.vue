<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h2 class="text-xl font-bold text-gray-800">Payment To Name</h2>
        <p class="text-sm text-gray-500 mt-1">Manage and configure payment to settings.</p>
      </div>

      <div class="flex items-center gap-3">
        <div class="relative w-full md:w-64">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search payment to..."
            class="w-full pl-9 pr-4 py-2 text-sm bg-white border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-bfs-gold/30 focus:border-bfs-gold transition-all"
          />
        </div>
        <button
          @click="openAddModal"
          class="flex items-center gap-2 px-4 py-2 bg-bfs-navy text-white text-sm font-semibold rounded-xl hover:bg-blue-900 shadow-md shadow-bfs-navy/20 hover:shadow-lg hover:shadow-bfs-navy/30 transition-all duration-300 transform hover:-translate-y-0.5"
        >
          <Plus class="w-4 h-4" />
          Add New
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex flex-col items-center justify-center h-64 bg-white rounded-2xl shadow-sm border border-gray-100">
      <div class="w-8 h-8 border-4 border-bfs-gold/30 border-t-bfs-gold rounded-full animate-spin mb-4"></div>
      <p class="text-sm text-gray-500 font-medium animate-pulse">Loading data...</p>
    </div>

    <!-- Main Content -->
    <div v-else class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden flex flex-col transition-all duration-300">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-gray-50/80 border-b border-gray-100">
              <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-wider w-16">No</th>
              <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-wider">Payment To Name</th>
              <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-wider hidden md:table-cell">Payment To Description</th>
              <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-wider">Email</th>
              <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-wider w-24">Hide</th>
              <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-wider w-24">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <template v-if="paginatedData.length > 0">
              <tr 
                v-for="(item, index) in paginatedData" 
                :key="item.id"
                class="hover:bg-blue-50/50 transition-colors group cursor-default"
              >
                <td class="px-6 py-4 text-sm text-gray-400 font-mono">{{ paginationStart + index + 1 }}</td>
                <td class="px-6 py-4">
                  <p class="text-sm font-semibold text-gray-800">{{ item.name }}</p>
                </td>
                <td class="px-6 py-4 hidden md:table-cell">
                  <p class="text-sm text-gray-500 line-clamp-1" :title="item.description">{{ item.description || '-' }}</p>
                </td>
                <td class="px-6 py-4">
                  <p class="text-sm text-gray-500">{{ item.email }}</p>
                </td>
                <td class="px-6 py-4">
                  <div class="flex items-center">
                    <span v-if="item.is_hide" class="px-2.5 py-1 bg-gray-100 text-gray-500 rounded-lg text-[11px] font-bold tracking-wide uppercase">Hidden</span>
                    <span v-else class="px-2.5 py-1 bg-green-50 text-green-600 rounded-lg text-[11px] font-bold tracking-wide uppercase">Visible</span>
                  </div>
                </td>
                <td class="px-6 py-4">
                  <div class="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button 
                      @click="openEditModal(item)"
                      class="p-1.5 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                      title="Edit"
                    >
                      <Pencil class="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            </template>
            <tr v-else>
              <td colspan="6" class="px-6 py-12 text-center text-gray-500">
                <div class="flex flex-col items-center justify-center">
                  <div class="w-12 h-12 bg-gray-50 rounded-full flex items-center justify-center mb-3">
                    <Search class="w-6 h-6 text-gray-400" />
                  </div>
                  <p class="font-medium text-gray-900">No data found</p>
                  <p class="text-sm text-gray-500 mt-1">Try adjusting your search query.</p>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination Footer -->
      <div class="px-6 py-4 bg-gray-50/50 border-t border-gray-100 flex items-center justify-between">
        <p class="text-xs text-gray-500 font-medium">
          Showing <span class="text-gray-900">{{ Math.min(paginationStart + 1, filteredData.length) }}</span> 
          to <span class="text-gray-900">{{ Math.min(paginationEnd, filteredData.length) }}</span> 
          of <span class="text-gray-900">{{ filteredData.length }}</span> entries
        </p>
        
        <div class="flex items-center gap-2">
          <button 
            @click="currentPage--" 
            :disabled="currentPage === 1"
            class="p-1.5 rounded-lg border border-gray-200 text-gray-600 hover:bg-white hover:border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-sm"
          >
            <ChevronLeft class="w-4 h-4" />
          </button>
          
          <div class="flex items-center gap-1">
            <button 
              v-for="page in displayedPages" 
              :key="page"
              @click="currentPage = page"
              class="w-8 h-8 rounded-lg text-sm font-semibold transition-colors shadow-sm"
              :class="currentPage === page ? 'bg-bfs-navy text-white' : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-50'"
            >
              {{ page }}
            </button>
          </div>

          <button 
            @click="currentPage++" 
            :disabled="currentPage >= totalPages"
            class="p-1.5 rounded-lg border border-gray-200 text-gray-600 hover:bg-white hover:border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-sm"
          >
            <ChevronRight class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>

    <!-- Modal Form -->
    <PaymentToFormModal
      :show="modal.show"
      :mode="modal.mode"
      :initialData="modal.selectedData"
      @close="closeModal"
      @saved="fetchData"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive, watch } from 'vue'
import { Plus, Pencil, Trash2, Search, ChevronLeft, ChevronRight, Check, X } from 'lucide-vue-next'
import api from '../../../services/api'
import Swal from 'sweetalert2'
import PaymentToFormModal from './PaymentToFormModal.vue'

const loading = ref(false)
const searchQuery = ref('')
const allData = ref([])

const currentPage = ref(1)
const itemsPerPage = 15

const filteredData = computed(() => {
  if (!searchQuery.value) return allData.value
  const q = searchQuery.value.toLowerCase()
  return allData.value.filter(item => 
    item.name?.toLowerCase().includes(q) || 
    item.description?.toLowerCase().includes(q) ||
    item.email?.toLowerCase().includes(q)
  )
})

const totalPages = computed(() => Math.ceil(filteredData.value.length / itemsPerPage) || 1)
const paginationStart = computed(() => (currentPage.value - 1) * itemsPerPage)
const paginationEnd = computed(() => paginationStart.value + itemsPerPage)

const paginatedData = computed(() => {
  return filteredData.value.slice(paginationStart.value, paginationEnd.value)
})

const displayedPages = computed(() => {
  const pages = []
  let start = Math.max(1, currentPage.value - 2)
  let end = Math.min(totalPages.value, currentPage.value + 2)
  
  if (end - start < 4) {
    if (start === 1) {
      end = Math.min(totalPages.value, 5)
    } else {
      start = Math.max(1, end - 4)
    }
  }
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  return pages
})

watch(searchQuery, () => {
  currentPage.value = 1
})

const modal = reactive({
  show: false,
  mode: 'add',
  selectedData: null
})

const fetchData = async () => {
  loading.value = true
  try {
    const response = await api.get('master-type/payment-to/')
    allData.value = response.data.results || response.data
  } catch (error) {
    console.error('Failed to fetch payment to data:', error)
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: 'Error fetching data. Check your permissions or network.',
      confirmButtonColor: '#1e3a8a'
    })
  } finally {
    loading.value = false
  }
}

const openAddModal = () => {
  modal.mode = 'add'
  modal.selectedData = null
  modal.show = true
}

const openEditModal = (item) => {
  modal.mode = 'edit'
  modal.selectedData = item
  modal.show = true
}

const closeModal = () => {
  modal.show = false
}

const handleDelete = async (id) => {
  const result = await Swal.fire({
    title: 'Are you sure?',
    text: 'You want to delete this Payment To record?',
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#ef4444',
    cancelButtonColor: '#9ca3af',
    confirmButtonText: 'Yes, delete it!'
  })
  
  if (result.isConfirmed) {
    try {
      await api.delete(`master-type/payment-to/${id}/`)
      Swal.fire({
        icon: 'success',
        title: 'Deleted!',
        text: 'Record has been deleted.',
        confirmButtonColor: '#1e3a8a',
        timer: 1500,
        showConfirmButton: false
      })
      fetchData()
    } catch (error) {
      console.error('Error deleting:', error)
      Swal.fire({
        icon: 'error',
        title: 'Failed',
        text: 'Failed to delete data.',
        confirmButtonColor: '#1e3a8a'
      })
    }
  }
}

onMounted(() => {
  fetchData()
})
</script>
