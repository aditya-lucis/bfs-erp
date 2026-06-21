<template>
  <Transition name="modal">
    <div v-if="show" class="fixed inset-0 z-[60] overflow-y-auto">
      <div class="fixed inset-0 bg-black/40" @click="$emit('update:show', false)" />
      <div class="flex min-h-full items-center justify-center p-4">
        <div class="relative bg-white rounded-xl shadow-2xl w-full max-w-3xl p-6 z-10 flex flex-col max-h-[80vh]">
          <div class="flex justify-between items-center mb-4 pb-4 border-b">
            <div>
              <h3 class="font-bold text-lg text-bfs-navy">Pick Purchase Requisition</h3>
              <p class="text-sm text-gray-500">Select an approved PR to populate your Purchase Order</p>
            </div>
            <button @click="$emit('update:show', false)" class="text-gray-400 hover:text-gray-600">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <div class="flex-1 overflow-y-auto">
            <div v-if="loading" class="py-10 text-center text-gray-500 flex flex-col items-center">
              <svg class="animate-spin h-8 w-8 text-bfs-navy mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Memuat data PR...
            </div>
            <div v-else-if="error" class="py-10 text-center text-red-500">
              {{ error }}
            </div>
            <div v-else-if="prs.length === 0" class="py-10 text-center text-gray-500 bg-gray-50 rounded-lg">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-gray-300 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
              </svg>
              <p>Tidak ada PR yang disetujui (Approved) untuk kombinasi Project & RAP ini.</p>
            </div>
            <div v-else class="grid gap-3">
              <div 
                v-for="pr in prs" 
                :key="pr.id"
                @click="selectPR(pr)"
                class="border border-gray-200 rounded-lg p-4 cursor-pointer hover:border-yellow-400 hover:bg-yellow-50 transition-colors"
              >
                <div class="flex justify-between items-start mb-2">
                  <div class="font-bold text-bfs-navy text-lg">{{ pr.pr_number }}</div>
                  <span class="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
                    {{ pr.document_status || 'Approved' }}
                  </span>
                </div>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600">
                  <div>
                    <span class="block text-xs text-gray-400">Date</span>
                    <span class="font-medium">{{ pr.pr_date }}</span>
                  </div>
                  <div>
                    <span class="block text-xs text-gray-400">Type</span>
                    <span class="font-medium">{{ pr.pr_type }}</span>
                  </div>
                  <div class="md:col-span-2">
                    <span class="block text-xs text-gray-400">Notes</span>
                    <span class="line-clamp-1" :title="pr.notes">{{ pr.notes || '-' }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, watch } from 'vue'
import { usePurchaseRequisitionStore } from '../../stores/purchaseRequisition'

const props = defineProps({
  show: Boolean,
  projectId: [Number, String],
  rapId: [Number, String],
  poType: String
})

const emit = defineEmits(['update:show', 'select'])
const prStore = usePurchaseRequisitionStore()

const loading = ref(false)
const error = ref(null)
const prs = ref([])

watch(() => props.show, async (newVal) => {
  if (newVal) {
    loading.value = true
    error.value = null
    try {
      // Fetch PRs matching project and rap, and only approved ones
      const params = {
        approval_status: 'approved'
      }
      if (props.projectId) params.project = props.projectId
      if (props.rapId) params.rap = props.rapId
      if (props.poType) params.pr_type = props.poType
      
      const response = await prStore.fetchPRs(params)
      prs.value = prStore.prs
    } catch (err) {
      console.error("Failed to fetch PRs:", err)
      error.value = "Gagal mengambil daftar PR."
    } finally {
      loading.value = false
    }
  }
})

function selectPR(pr) {
  emit('select', pr)
  emit('update:show', false)
}
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>
