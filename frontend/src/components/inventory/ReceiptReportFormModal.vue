<template>
  <div class="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 sm:p-6">
    <div class="bg-white rounded-xl shadow-2xl w-full max-w-7xl flex flex-col max-h-[95vh] overflow-hidden border border-gray-200">
      
      <!-- Header -->
      <div class="px-6 py-4 bg-slate-800 text-white flex justify-between items-center relative">
        <div class="flex items-center gap-3">
          <div class="bg-white/20 p-2 rounded-lg">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div>
            <h2 class="text-lg font-bold tracking-wide">New Receipt Report For Purchase</h2>
            <p class="text-xs text-slate-300">Inventory | Receipt Report | Add</p>
          </div>
        </div>

        <div class="absolute right-16 top-1/2 -translate-y-1/2 flex items-center gap-2">
          <label class="flex items-center gap-2 text-white font-semibold cursor-pointer bg-white/10 px-3 py-1.5 rounded-lg hover:bg-white/20 transition-colors">
            <input type="checkbox" v-model="isPartial" @change="onPartialChange" class="w-4 h-4 rounded text-bfs-gold focus:ring-bfs-gold cursor-pointer border-none">
            <span>Partial Receive</span>
          </label>
        </div>

        <button @click="$emit('close')" class="text-slate-300 hover:text-white transition-colors bg-white/10 hover:bg-white/20 p-1.5 rounded-lg cursor-pointer">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Body -->
      <div class="flex-1 overflow-y-auto bg-gray-50/50">
        
        <!-- Document Header Info -->
        <div class="p-6 border-b border-gray-200 bg-white">
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-x-8 gap-y-4">
            
            <!-- Left Column -->
            <div class="space-y-4">
              <div class="flex items-center text-sm">
                <label class="w-32 font-semibold text-gray-600 shrink-0">Vendor <span class="text-red-500">*</span></label>
                <div class="flex-1 flex gap-2">
                  <SearchableSelect 
                    v-model="formData.vendor" 
                    :options="availableVendors" 
                    labelKey="name" 
                    valueKey="id" 
                    placeholder="-- Select Vendor --" 
                    @update:modelValue="onVendorChange"
                    class="flex-1"
                  />
                </div>
              </div>

              <div class="flex items-center text-sm">
                <label class="w-32 font-semibold text-gray-600 shrink-0">Address</label>
                <div class="flex-1">
                  <textarea :value="selectedVendorDetails?.address_1 || '-'" disabled rows="2" class="w-full bg-gray-100 border-gray-300 rounded text-sm text-gray-600 font-medium resize-none"></textarea>
                </div>
              </div>

              <div class="flex items-center text-sm">
                <label class="w-32 font-semibold text-gray-600 shrink-0">PO Number <span class="text-red-500">*</span></label>
                <div class="flex-1 flex gap-2">
                  <SearchableSelect 
                    v-model="formData.po" 
                    :options="filteredPos" 
                    labelKey="po_number" 
                    valueKey="id" 
                    placeholder="-- Select PO --" 
                    :disabled="!formData.vendor"
                    @update:modelValue="onPoChange"
                    class="flex-1"
                  />
                </div>
              </div>

              <div class="flex items-center text-sm">
                <label class="w-32 font-semibold text-gray-600 shrink-0">Base Amount PO</label>
                <div class="flex-1">
                  <input type="text" :value="selectedPoDetails ? 'IDR ' + selectedPoDetails.grand_total.toLocaleString() : '-'" disabled class="w-full bg-gray-100 border-gray-300 rounded text-sm text-gray-600 font-mono">
                </div>
              </div>
            </div>

            <!-- Middle Column -->
            <div class="space-y-4">
              <div class="flex items-center text-sm">
                <label class="w-32 font-semibold text-gray-600 shrink-0">Receive Date <span class="text-red-500">*</span></label>
                <div class="flex-1">
                  <input type="date" v-model="formData.receive_date" class="w-full border-gray-300 rounded focus:ring-bfs-gold focus:border-bfs-gold text-sm shadow-sm bg-white">
                </div>
              </div>
              
              <div class="flex items-center text-sm">
                <label class="w-32 font-semibold text-gray-600 shrink-0">Vendor SN</label>
                <div class="flex-1">
                  <input type="text" v-model="formData.vendor_sn" placeholder="e.g. DO-12345" class="w-full border-gray-300 rounded focus:ring-bfs-gold focus:border-bfs-gold text-sm shadow-sm bg-white">
                </div>
              </div>

              <div class="flex items-center text-sm">
                <label class="w-32 font-semibold text-gray-600 shrink-0">Vendor SN Date</label>
                <div class="flex-1">
                  <input type="date" v-model="formData.vendor_sn_date" class="w-full border-gray-300 rounded focus:ring-bfs-gold focus:border-bfs-gold text-sm shadow-sm bg-white">
                </div>
              </div>
            </div>

            <!-- Right Column -->
            <div class="space-y-4">
              <div class="flex items-center text-sm">
                <label class="w-32 font-semibold text-gray-600 shrink-0">PO Date</label>
                <div class="flex-1">
                  <input type="text" :value="selectedPoDetails?.po_date || '-'" disabled class="w-full bg-gray-100 border-gray-300 rounded text-sm text-gray-600">
                </div>
              </div>

              <div class="flex items-start text-sm h-full">
                <label class="w-32 font-semibold text-gray-600 shrink-0 mt-2">Memo</label>
                <div class="flex-1">
                  <textarea v-model="formData.memo" rows="3" placeholder="Optional remarks..." class="w-full border-gray-300 rounded focus:ring-bfs-gold focus:border-bfs-gold text-sm shadow-sm resize-none bg-white"></textarea>
                </div>
              </div>
            </div>

          </div>
        </div>

        <!-- Items Table -->
        <div class="p-6">
          <div class="border border-gray-200 rounded-lg overflow-hidden bg-white shadow-sm">
            <div class="bg-slate-100 px-4 py-3 border-b border-gray-200 flex justify-between items-center">
              <h3 class="font-bold text-slate-700 text-sm flex items-center gap-2">
                <svg class="w-4 h-4 text-bfs-gold" fill="currentColor" viewBox="0 0 20 20"><path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z"/></svg>
                Items to Receive
              </h3>
            </div>
            <div class="overflow-x-auto">
              <table class="w-full text-left border-collapse whitespace-nowrap">
                <thead>
                  <tr class="bg-gray-50 text-gray-600 text-xs uppercase tracking-wider border-b border-gray-200">
                    <th class="p-3 font-semibold text-center w-10">No</th>
                    <th class="p-3 font-semibold">Item Code</th>
                    <th class="p-3 font-semibold">Description</th>
                    <th class="p-3 font-semibold text-right">PO Qty</th>
                    <th class="p-3 font-semibold text-right">Others Doc</th>
                    <th class="p-3 font-semibold text-right text-orange-600">Remaining</th>
                    <th class="p-3 font-semibold text-right bg-blue-50/50 w-32 border-l border-blue-100">Receive Now</th>
                    <th class="p-3 font-semibold">Unit</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-if="loadingItems" class="bg-white">
                    <td colspan="8" class="p-8 text-center text-gray-500">
                      <div class="flex flex-col items-center justify-center gap-2">
                        <svg class="animate-spin h-6 w-6 text-bfs-gold" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        <span class="text-sm font-medium">Loading PO Details...</span>
                      </div>
                    </td>
                  </tr>
                  <tr v-else-if="!items.length" class="bg-white">
                    <td colspan="8" class="p-8 text-center text-gray-400 text-sm italic">Please select a PO to view items.</td>
                  </tr>
                  <tr v-else v-for="(item, index) in items" :key="item.id" class="border-b border-gray-100 hover:bg-yellow-50/30 transition-colors group">
                    <td class="p-3 text-center text-xs text-gray-400 font-medium">{{ index + 1 }}</td>
                    <td class="p-3 text-sm font-medium text-slate-700">{{ item.item_code }}</td>
                    <td class="p-3 text-xs text-gray-600 max-w-[200px] truncate" :title="item.item_name">{{ item.item_name }}</td>
                    <td class="p-3 text-right text-sm text-gray-600 font-mono">{{ parseFloat(item.quantity).toFixed(2) }}</td>
                    <td class="p-3 text-right text-sm text-gray-600 font-mono">{{ parseFloat(item.received_qty).toFixed(2) }}</td>
                    <td class="p-3 text-right text-sm font-bold text-orange-600 font-mono">{{ Math.max(0, item.quantity - item.received_qty).toFixed(2) }}</td>
                    <td class="p-2 bg-blue-50/30 border-l border-blue-50 group-hover:bg-blue-50 transition-colors">
                      <input type="number" 
                             v-model.number="item.current_receive" 
                             :max="item.quantity - item.received_qty"
                             min="0"
                             step="0.01"
                             :disabled="!isPartial"
                             class="w-full border-gray-300 rounded text-right text-sm font-mono focus:ring-blue-500 focus:border-blue-500 shadow-inner bg-white disabled:bg-gray-100 disabled:text-gray-500">
                    </td>
                    <td class="p-3 text-xs text-gray-500">{{ item.unit_name }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

      </div>

      <!-- Footer -->
      <div class="px-6 py-4 border-t border-gray-200 bg-white flex justify-end space-x-3 items-center shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)]">
        <button @click="$emit('close')" class="px-5 py-2.5 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors text-sm font-semibold cursor-pointer">
          Cancel
        </button>
        <button @click="save" :disabled="saving" class="px-6 py-2.5 bg-bfs-gold text-white rounded-lg hover:bg-[#C2A05B] transition-colors text-sm font-bold shadow-md disabled:opacity-70 disabled:cursor-not-allowed flex items-center cursor-pointer">
          <span v-if="saving" class="mr-2">
             <svg class="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
          </span>
          Save Draft Receipt
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useReceiptReportStore } from '../../stores/inventory/receiptReportStore'
import api from '../../services/api'
import Swal from 'sweetalert2'
import SearchableSelect from '../../components/SearchableSelect.vue'

const emit = defineEmits(['close', 'success'])
const store = useReceiptReportStore()

const availableVendors = ref([])
const allPos = ref([])
const items = ref([])
const loadingItems = ref(false)
const saving = ref(false)
const isPartial = ref(false)

const formData = reactive({
  receipt_type: 'RR_PUR',
  vendor: '',
  po: '',
  receive_date: new Date().toISOString().split('T')[0],
  vendor_sn: '',
  vendor_sn_date: new Date().toISOString().split('T')[0],
  memo: ''
})

const selectedVendorDetails = computed(() => {
  return availableVendors.value.find(v => v.id === formData.vendor) || null
})

const filteredPos = computed(() => {
  if (!formData.vendor) return []
  return allPos.value.filter(po => po.vendor === formData.vendor)
})

const selectedPoDetails = computed(() => {
  return allPos.value.find(p => p.id === formData.po) || null
})

onMounted(() => {
  fetchData()
})

async function fetchData() {
  try {
    const { data } = await api.get('/inventory/receipt-reports/get_valid_vendors/')
    availableVendors.value = data.results || data
  } catch (error) {
    console.error('Failed to fetch initial data', error)
  }
}

function onVendorChange() {
  formData.po = ''
  items.value = []
  allPos.value = []
  if (formData.vendor) {
    fetchPOs()
  }
}

async function fetchPOs() {
  try {
    const { data } = await api.get('/inventory/receipt-reports/get_valid_pos/', {
      params: { vendor_id: formData.vendor }
    })
    allPos.value = data.results || data
  } catch (error) {
    console.error('Failed to fetch POs', error)
  }
}

async function onPoChange() {
  if (!formData.po) return
  loadingItems.value = true
  items.value = []
  try {
    const { data } = await api.get(`/purchase/po/${formData.po}/`)
    if (data.details) {
      items.value = data.details.map(d => ({
        ...d,
        current_receive: Math.max(0, d.quantity - d.received_qty)
      }))
    }
  } catch (error) {
    console.error('Failed to fetch PO details', error)
  } finally {
    loadingItems.value = false
  }
}

function onPartialChange() {
  if (!isPartial.value) {
    items.value.forEach(item => {
      item.current_receive = Math.max(0, item.quantity - item.received_qty)
    })
  }
}

async function save() {
  if (!formData.po) {
    Swal.fire({ icon: 'warning', text: 'Please select a PO' })
    return
  }
  
  const itemsToReceive = items.value.filter(item => item.current_receive > 0)
  if (itemsToReceive.length === 0) {
    Swal.fire({ icon: 'warning', text: 'Please input receive quantity for at least one item' })
    return
  }

  const invalid = itemsToReceive.find(i => i.current_receive > (i.quantity - i.received_qty))
  if (invalid) {
    Swal.fire({ icon: 'error', text: `Receive quantity for ${invalid.item_code} exceeds remaining quantity.` })
    return
  }

  saving.value = true
  try {
    const payload = {
      ...formData,
      company: selectedPoDetails.value?.company,
      items: itemsToReceive.map(item => ({
        po_item: item.id,
        item: item.item,
        unit_type: item.unit,
        receive_qty: item.current_receive
      }))
    }

    if (!payload.vendor_sn_date) {
      delete payload.vendor_sn_date
    }

    await store.createReceiptReport(payload)
    emit('success')
  } catch (error) {
    Swal.fire({ icon: 'error', title: 'Save Failed', text: error.detail || 'An error occurred' })
  } finally {
    saving.value = false
  }
}
</script>
