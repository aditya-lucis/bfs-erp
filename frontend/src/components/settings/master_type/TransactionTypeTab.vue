<template>
  <div class="space-y-4">
    <!-- Header & Actions -->
    <div class="flex flex-col sm:flex-row items-center justify-between gap-4 border-b border-gray-100 pb-4">
      <div>
        <h2 class="text-lg font-bold text-gray-800">Transaction Type</h2>
        <p class="text-xs text-gray-500 mt-0.5">Manage and configure all transaction types in the system.</p>
      </div>
      
      <div class="flex items-center gap-3 w-full sm:w-auto">
        <!-- Search Input -->
        <div class="relative w-full sm:w-64 group">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search class="h-4 w-4 text-gray-400 group-focus-within:text-bfs-navy transition-colors" />
          </div>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search types..."
            class="block w-full pl-9 pr-3 py-2 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-bfs-navy/20 focus:border-bfs-navy bg-gray-50/50 focus:bg-white transition-all duration-300"
          />
        </div>

        <button
          @click="openAddModal"
          class="bg-bfs-navy text-white hover:bg-blue-900 text-sm font-semibold flex items-center gap-2 px-5 py-2.5 rounded-xl shadow-md shadow-bfs-navy/20 hover:shadow-lg hover:shadow-bfs-navy/30 transition-all duration-300 transform hover:-translate-y-0.5"
        >
          <Plus class="w-4 h-4" /> Add New
        </button>
      </div>
    </div>

    <!-- Data Table -->
    <div class="relative rounded-2xl border border-gray-100 bg-white overflow-hidden shadow-sm">
      <div v-if="loading" class="absolute inset-0 bg-white/60 backdrop-blur-sm flex items-center justify-center z-10">
        <div class="flex flex-col items-center gap-2">
          <div class="w-6 h-6 border-2 border-bfs-gold border-t-transparent rounded-full animate-spin"></div>
          <span class="text-xs font-semibold text-gray-600">Loading data...</span>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse whitespace-nowrap">
          <thead>
            <tr class="bg-gray-50/80 border-b border-gray-100">
              <th class="py-3.5 px-4 text-[11px] font-bold text-gray-500 uppercase tracking-wider w-16 text-center">No</th>
              <th class="py-3.5 px-4 text-[11px] font-bold text-gray-500 uppercase tracking-wider">Type Code</th>
              <th class="py-3.5 px-4 text-[11px] font-bold text-gray-500 uppercase tracking-wider">Name (EN)</th>
              <th class="py-3.5 px-4 text-[11px] font-bold text-gray-500 uppercase tracking-wider">Name (ID)</th>
              <th class="py-3.5 px-4 text-[11px] font-bold text-gray-500 uppercase tracking-wider">Company</th>
              <th class="py-3.5 px-4 text-[11px] font-bold text-gray-500 uppercase tracking-wider text-center">Status</th>
              <th class="py-3.5 px-4 text-[11px] font-bold text-gray-500 uppercase tracking-wider text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr
              v-for="item in paginatedData"
              :key="item.id"
              class="hover:bg-bfs-navy/5 transition-colors duration-200 group"
            >
              <td class="py-3 px-4 text-center text-xs font-medium text-gray-400">{{ item.order_no }}</td>
              <td class="py-3 px-4 text-xs font-mono font-semibold text-bfs-navy">{{ item.type_code }}</td>
              <td class="py-3 px-4 text-sm font-semibold text-gray-800">{{ item.type_name_en }}</td>
              <td class="py-3 px-4 text-sm text-gray-600">{{ item.type_name_id }}</td>
              <td class="py-3 px-4 text-xs text-gray-500">
                <div class="flex items-center gap-1.5">
                  <div class="w-2 h-2 rounded-full bg-blue-400"></div>
                  {{ item.company_name }}
                </div>
              </td>
              <td class="py-3 px-4 text-center">
                <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold tracking-wide"
                  :class="!item.is_not_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'"
                >
                  {{ !item.is_not_active ? 'ACTIVE' : 'INACTIVE' }}
                </span>
              </td>
              <td class="py-3 px-4 text-right">
                <div class="flex justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                  <button @click="openEditModal(item)" class="p-1.5 bg-gray-100 hover:bg-bfs-gold hover:text-white text-gray-500 rounded-lg transition-colors shadow-sm" title="Edit">
                    <Pencil class="w-3.5 h-3.5" />
                  </button>
                  <button @click="handleDelete(item.id)" class="p-1.5 bg-gray-100 hover:bg-red-500 hover:text-white text-gray-500 rounded-lg transition-colors shadow-sm" title="Delete">
                    <Trash2 class="w-3.5 h-3.5" />
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="filteredData.length === 0 && !loading">
              <td colspan="7" class="py-12 text-center">
                <div class="flex flex-col items-center justify-center">
                  <div class="w-12 h-12 bg-gray-50 rounded-full flex items-center justify-center mb-3">
                    <Search class="w-6 h-6 text-gray-300" />
                  </div>
                  <p class="text-sm font-medium text-gray-600">No transaction types found</p>
                  <p class="text-xs text-gray-400 mt-1">Try adjusting your search criteria.</p>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- Frontend Pagination -->
      <div v-if="filteredData.length > 0" class="border-t border-gray-100 px-4 py-3 flex items-center justify-between bg-gray-50/50">
        <div class="text-xs text-gray-500">
          Showing <span class="font-semibold text-gray-700">{{ paginationStart + 1 }}</span> to 
          <span class="font-semibold text-gray-700">{{ Math.min(paginationEnd, filteredData.length) }}</span> of 
          <span class="font-semibold text-gray-700">{{ filteredData.length }}</span> entries
        </div>
        <div class="flex items-center gap-1.5">
          <button 
            @click="currentPage--" 
            :disabled="currentPage === 1"
            class="px-2.5 py-1.5 rounded-lg border border-gray-200 text-xs font-medium hover:bg-white hover:text-bfs-navy disabled:opacity-40 disabled:hover:bg-transparent transition-colors flex items-center gap-1"
          >
            <ChevronLeft class="w-3 h-3" /> Prev
          </button>
          
          <div class="flex items-center gap-1 px-2">
            <button 
              v-for="page in totalPages" :key="page"
              @click="currentPage = page"
              class="w-7 h-7 flex items-center justify-center rounded-lg text-xs font-bold transition-colors"
              :class="currentPage === page ? 'bg-bfs-navy text-white shadow-md' : 'text-gray-500 hover:bg-gray-200'"
            >
              {{ page }}
            </button>
          </div>

          <button 
            @click="currentPage++" 
            :disabled="currentPage === totalPages"
            class="px-2.5 py-1.5 rounded-lg border border-gray-200 text-xs font-medium hover:bg-white hover:text-bfs-navy disabled:opacity-40 disabled:hover:bg-transparent transition-colors flex items-center gap-1"
          >
            Next <ChevronRight class="w-3 h-3" />
          </button>
        </div>
      </div>
    </div>

    <!-- Add/Edit Modal (Glassmorphism design) -->
    <Teleport to="body">
      <Transition name="modal-scale">
        <div v-if="modal.show" class="fixed inset-0 z-50 overflow-y-auto">
          <div class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm transition-opacity" @click="closeModal" />
          <div class="flex min-h-full items-center justify-center p-4">
            <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-lg z-10 overflow-hidden" @click.stop>
              
              <!-- Decoration -->
              <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-bfs-navy via-bfs-gold to-bfs-navy"></div>

              <!-- Header -->
              <div class="flex items-center justify-between px-6 py-5 border-b border-gray-100">
                <div class="flex items-center gap-3">
                  <div class="w-8 h-8 rounded-full bg-bfs-navy/10 flex items-center justify-center">
                    <FileText class="w-4 h-4 text-bfs-navy" />
                  </div>
                  <h3 class="text-base font-bold text-gray-800">
                    {{ modal.mode === 'add' ? 'Create New Type' : 'Edit Type' }}
                  </h3>
                </div>
                <button @click="closeModal" class="p-1.5 rounded-full text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors">
                  <X class="w-4 h-4" />
                </button>
              </div>

              <!-- Form -->
              <form @submit.prevent="saveTransactionType">
                <div class="px-6 py-6 space-y-5">
                  
                  <div v-if="modal.mode === 'edit'" class="bg-gray-50 rounded-xl p-3 border border-gray-100 flex items-center justify-between">
                    <span class="text-xs text-gray-500 font-medium">Type Code</span>
                    <span class="text-sm font-mono font-bold text-bfs-navy">{{ form.type_code }}</span>
                  </div>

                  <div class="grid grid-cols-2 gap-4">
                    <FormField label="Name (EN)" required>
                      <input v-model="form.type_name_en" type="text" class="form-input transition-colors focus:ring-bfs-navy" placeholder="e.g. HPP Farmasi" required />
                    </FormField>
                    
                    <FormField label="Name (ID)" required>
                      <input v-model="form.type_name_id" type="text" class="form-input transition-colors focus:ring-bfs-navy" placeholder="e.g. HPP Farmasi" required />
                    </FormField>
                  </div>

                  <div class="grid grid-cols-1 gap-4">
                    <FormField label="Order No" required>
                      <input v-model="form.order_no" type="number" class="form-input transition-colors focus:ring-bfs-navy" placeholder="0" required />
                    </FormField>
                  </div>
                  
                  <div class="flex items-center p-3 mt-2 bg-gray-50 rounded-xl border border-gray-100 cursor-pointer hover:bg-gray-100 transition-colors" @click="form.is_not_active = !form.is_not_active">
                    <div class="flex-1">
                      <p class="text-sm font-semibold text-gray-700">Status Inactive</p>
                      <p class="text-[10px] text-gray-500 mt-0.5">Toggle to deactivate this transaction type.</p>
                    </div>
                    <!-- Toggle Switch -->
                    <div class="relative inline-flex h-5 w-9 items-center rounded-full transition-colors duration-300" :class="form.is_not_active ? 'bg-red-500' : 'bg-gray-300'">
                      <span class="inline-block h-3.5 w-3.5 transform rounded-full bg-white transition duration-300 shadow-sm" :class="form.is_not_active ? 'translate-x-4.5' : 'translate-x-1'" />
                    </div>
                  </div>
                </div>

                <!-- Actions -->
                <div class="flex justify-end gap-3 px-6 py-5 bg-gray-50/80 border-t border-gray-100">
                  <button type="button" @click="closeModal" class="bg-white border border-gray-200 text-gray-700 hover:bg-gray-50 text-sm font-semibold px-5 py-2.5 rounded-xl transition-colors shadow-sm">
                    Cancel
                  </button>
                  <button type="submit" class="bg-bfs-navy text-white hover:bg-blue-900 text-sm font-semibold flex items-center gap-2 px-6 py-2.5 rounded-xl shadow-md shadow-bfs-navy/20 hover:shadow-lg hover:shadow-bfs-navy/30 transition-all duration-300 transform hover:-translate-y-0.5" :disabled="saving">
                    <Save v-if="!saving" class="w-4 h-4" />
                    <div v-else class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    {{ saving ? 'Saving...' : 'Save Changes' }}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive, watch } from 'vue'
import FormField from '../../../components/FormField.vue'
import { Plus, Pencil, Trash2, Save, X, Search, ChevronLeft, ChevronRight, FileText } from 'lucide-vue-next'
import api from '../../../services/api'

// State
const loading = ref(false)
const saving = ref(false)
const searchQuery = ref('')
const allData = ref([])

// Pagination (Frontend)
const currentPage = ref(1)
const itemsPerPage = 10

const filteredData = computed(() => {
  if (!searchQuery.value) return allData.value
  const q = searchQuery.value.toLowerCase()
  return allData.value.filter(item => 
    item.type_name_en.toLowerCase().includes(q) || 
    item.type_name_id.toLowerCase().includes(q) ||
    item.type_code.toLowerCase().includes(q)
  )
})

const totalPages = computed(() => Math.ceil(filteredData.value.length / itemsPerPage) || 1)

const paginationStart = computed(() => (currentPage.value - 1) * itemsPerPage)
const paginationEnd = computed(() => paginationStart.value + itemsPerPage)

const paginatedData = computed(() => {
  return filteredData.value.slice(paginationStart.value, paginationEnd.value)
})

// Reset to page 1 when searching
watch(searchQuery, () => {
  currentPage.value = 1
})

// Modal State
const modal = reactive({
  show: false,
  mode: 'add',
  selectedId: null
})

const form = reactive({
  type_code: '',
  type_name_en: '',
  type_name_id: '',
  table_name: 'TrsType',
  order_no: 0,
  is_not_active: false
})

// Fetch Data
const fetchTransactionTypes = async () => {
  loading.value = true
  try {
    // API should now return un-paginated array or a very large list
    const response = await api.get('master-type/transaction-type/')
    // Handle both wrapped and unwrapped DRF responses just in case
    allData.value = response.data.results || response.data
  } catch (error) {
    console.error('Failed to fetch transaction types:', error)
    alert('Error fetching data. Check your permissions or network.')
  } finally {
    loading.value = false
  }
}

// Modal Actions
const openAddModal = () => {
  modal.mode = 'add'
  modal.selectedId = null
  form.type_code = ''
  form.type_name_en = ''
  form.type_name_id = ''
  form.table_name = 'TrsType'
  form.order_no = (allData.value.length > 0 ? Math.max(...allData.value.map(t => t.order_no)) : 0) + 1
  form.is_not_active = false
  modal.show = true
}

const openEditModal = (item) => {
  modal.mode = 'edit'
  modal.selectedId = item.id
  form.type_code = item.type_code
  form.type_name_en = item.type_name_en
  form.type_name_id = item.type_name_id
  form.table_name = item.table_name
  form.order_no = item.order_no
  form.is_not_active = item.is_not_active
  modal.show = true
}

const closeModal = () => {
  modal.show = false
}

// Save Data (Add/Edit)
const saveTransactionType = async () => {
  saving.value = true
  try {
    const payload = {
      type_name_en: form.type_name_en,
      type_name_id: form.type_name_id,
      table_name: form.table_name,
      order_no: form.order_no,
      is_not_active: form.is_not_active
    }

    if (modal.mode === 'add') {
      await api.post('master-type/transaction-type/', payload)
    } else {
      await api.patch(`master-type/transaction-type/${modal.selectedId}/`, payload)
    }
    
    closeModal()
    fetchTransactionTypes() // Refresh list
  } catch (error) {
    console.error('Error saving:', error)
    alert('Failed to save data. Please check the form and try again.')
  } finally {
    saving.value = false
  }
}

// Delete Data
const handleDelete = async (id) => {
  if (confirm('Are you sure you want to delete this Transaction Type?')) {
    try {
      await api.delete(`master-type/transaction-type/${id}/`)
      fetchTransactionTypes()
    } catch (error) {
      console.error('Error deleting:', error)
      alert('Failed to delete data.')
    }
  }
}

onMounted(() => {
  fetchTransactionTypes()
})
</script>

<style scoped>
.modal-scale-enter-active,
.modal-scale-leave-active {
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.modal-scale-enter-from,
.modal-scale-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(10px);
}

.modal-scale-enter-to,
.modal-scale-leave-from {
  opacity: 1;
  transform: scale(1) translateY(0);
}
</style>
