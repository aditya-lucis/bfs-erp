<template>
  <div class="fixed inset-0 z-[110] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 sm:p-6" v-if="show">
    <div class="bg-white rounded-xl shadow-2xl w-full max-w-2xl flex flex-col overflow-hidden border border-gray-200">
      
      <!-- Header -->
      <div class="px-6 py-4 bg-slate-800 text-white flex justify-between items-center relative">
        <div class="flex items-center gap-3">
          <div class="bg-white/20 p-2 rounded-lg">
            <MapPin class="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 class="text-lg font-bold tracking-wide">Tracking Info</h2>
            <p class="text-xs text-slate-300">{{ receiptNumber }}</p>
          </div>
        </div>

        <button @click="$emit('close')" class="p-1 hover:bg-white/20 rounded-md transition-colors cursor-pointer text-white">
          <X class="w-6 h-6" />
        </button>
      </div>

      <!-- Body -->
      <div class="p-6 bg-gray-50 flex-1 overflow-y-auto">
        <div v-if="loading" class="flex justify-center items-center py-12">
          <svg class="animate-spin h-8 w-8 text-bfs-gold" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>
        <div v-else class="space-y-4">
          <div v-if="lastUpdate" class="text-xs text-gray-500 bg-blue-50 px-3 py-2 rounded-md border border-blue-100 flex items-center gap-2">
            <Clock class="w-4 h-4 text-blue-500" />
            <span>Last Update: <strong class="text-gray-700">{{ formatDateTime(lastUpdate) }}</strong></span>
          </div>

          <div>
            <label class="block font-semibold text-gray-700 mb-2">Tracking Status</label>
            <textarea 
              v-model="trackingStatus" 
              rows="6" 
              class="w-full border-gray-300 rounded-lg focus:ring-bfs-gold focus:border-bfs-gold text-sm shadow-sm bg-white resize-none"
              placeholder="Enter tracking information here..."
            ></textarea>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="px-6 py-4 border-t border-gray-100 bg-white flex justify-end gap-3 rounded-b-xl">
        <button @click="$emit('close')" type="button" class="px-5 py-2.5 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors text-sm font-semibold cursor-pointer">
          Cancel
        </button>
        <button @click="save" :disabled="saving || loading" class="px-6 py-2.5 bg-bfs-gold text-white rounded-lg hover:bg-[#C2A05B] transition-colors text-sm font-bold shadow-md disabled:opacity-70 disabled:cursor-not-allowed flex items-center gap-2 cursor-pointer">
          <span v-if="saving" class="w-4 h-4 mr-1">
             <svg class="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
             </svg>
          </span>
          <Save v-else class="w-4 h-4" />
          Save Tracking
        </button>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { MapPin, X, Save, Clock } from 'lucide-vue-next'
import api from '../../services/api'
import Swal from 'sweetalert2'

const props = defineProps({
  show: { type: Boolean, default: false },
  documentId: { type: [Number, String], default: null },
  receiptNumber: { type: String, default: '' }
})

const emit = defineEmits(['close', 'success'])

const loading = ref(false)
const saving = ref(false)
const trackingStatus = ref('')
const lastUpdate = ref(null)

watch(() => props.show, async (newVal) => {
  if (newVal && props.documentId) {
    await loadData()
  } else {
    trackingStatus.value = ''
    lastUpdate.value = null
  }
})

async function loadData() {
  loading.value = true
  try {
    const { data } = await api.get(`/inventory/receipt-reports/${props.documentId}/`)
    trackingStatus.value = data.tracking_status || ''
    lastUpdate.value = data.tracking_last_update
  } catch (error) {
    Swal.fire({ icon: 'error', title: 'Error', text: 'Failed to load tracking info.' })
    emit('close')
  } finally {
    loading.value = false
  }
}

async function save() {
  saving.value = true
  try {
    await api.patch(`/inventory/receipt-reports/${props.documentId}/update_tracking/`, {
      tracking_status: trackingStatus.value
    })
    Swal.fire({
      icon: 'success',
      title: 'Success',
      text: 'Data Updated Successfully',
      timer: 1500,
      showConfirmButton: false
    })
    emit('success')
    emit('close')
  } catch (error) {
    Swal.fire({ icon: 'error', title: 'Save Failed', text: 'An error occurred while saving tracking info.' })
  } finally {
    saving.value = false
  }
}

function formatDateTime(dateStr) {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return new Intl.DateTimeFormat('en-GB', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit', second: '2-digit'
  }).format(date)
}
</script>