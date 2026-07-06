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
          <div class="flex items-center gap-2 text-white font-semibold bg-white/10 px-3 py-1.5 rounded-lg border-none">
            <span v-if="computedIsPartial" class="text-orange-300">Status: Partial Receive</span>
            <span v-else class="text-green-300">Status: Full Receive</span>
          </div>
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
                    <th class="p-3 font-semibold text-right bg-blue-50/50 w-48 border-l border-blue-100">Receive Now</th>
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
                  <tr v-else v-for="(item, index) in visibleItems" :key="item.id" class="border-b border-gray-100 hover:bg-yellow-50/30 transition-colors group">
                    <td class="p-3 text-center text-xs text-gray-400 font-medium">{{ index + 1 }}</td>
                    <td class="p-3 text-sm font-medium text-slate-700">{{ item.item_code }}</td>
                    <td class="p-3 text-xs text-gray-600 max-w-[200px] truncate" :title="item.item_name">{{ item.item_name }}</td>
                    <td class="p-3 text-right text-sm text-gray-600 font-mono">{{ parseFloat(item.quantity).toFixed(2) }}</td>
                    <td class="p-3 text-right text-sm text-gray-600 font-mono">{{ parseFloat(item.received_qty).toFixed(2) }}</td>
                    <td class="p-3 text-right text-sm font-bold text-orange-600 font-mono">{{ Math.max(0, item.quantity - item.received_qty).toFixed(2) }}</td>
                    <td class="p-2 bg-blue-50/30 border-l border-blue-50 group-hover:bg-blue-50 transition-colors">
                      <div class="flex flex-col gap-1.5">
                        <input type="number" 
                               v-model.number="item.current_receive" 
                               :max="item.quantity - item.received_qty"
                               min="0"
                               step="0.01"
                               class="w-full border-gray-300 rounded text-right text-sm font-mono focus:ring-blue-500 focus:border-blue-500 shadow-inner bg-white disabled:bg-gray-100 disabled:text-gray-500">
                        <select v-model="item.selected_bin_id" class="w-full border-gray-300 rounded text-xs py-1 focus:ring-blue-500 focus:border-blue-500 bg-white truncate">
                          <option :value="null" disabled>Select Bin</option>
                          <optgroup v-for="wh in warehouses" :key="wh.id" :label="wh.name">
                            <option v-for="bin in wh.bins" :key="bin.id" :value="bin.id">{{ bin.bin_name }}</option>
                          </optgroup>
                        </select>
                      </div>
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
      <div class="px-6 py-4 border-t border-gray-200 bg-white">
        <div class="flex justify-end gap-3">
          <button @click="$emit('close')" type="button" class="px-5 py-2.5 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors text-sm font-semibold cursor-pointer">
            Cancel
          </button>
          <div v-if="!formData.id || ['draft', 'revised'].includes(formData.approval_status)" class="flex gap-3">
            <button @click="save(false)" :disabled="saving" class="px-6 py-2.5 border-2 border-bfs-gold text-bfs-gold rounded-lg hover:bg-yellow-50 transition-colors text-sm font-bold disabled:opacity-70 disabled:cursor-not-allowed flex items-center gap-2 cursor-pointer">
              <span v-if="saving" class="w-4 h-4 mr-1">
                 <svg class="animate-spin h-4 w-4 text-bfs-gold" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
              </span>
              <Save v-else class="w-4 h-4" />
              Save Draft
            </button>
            <button @click="save(true)" :disabled="saving" class="px-6 py-2.5 bg-bfs-gold text-white rounded-lg hover:bg-[#C2A05B] transition-colors text-sm font-bold shadow-md disabled:opacity-70 disabled:cursor-not-allowed flex items-center gap-2 cursor-pointer">
              <Send class="w-4 h-4" />
              Submit to Approval
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useReceiptReportStore } from '../../stores/inventory/receiptReportStore'
import api from '../../services/api'
import Swal from 'sweetalert2'
import SearchableSelect from '../../components/SearchableSelect.vue'
import { Save, Send, X } from 'lucide-vue-next'

const props = defineProps({
  editId: {
    type: [Number, String],
    default: null
  }
})

const emit = defineEmits(['close', 'success'])
const store = useReceiptReportStore()

const availableVendors = ref([])
const allPos = ref([])
const items = ref([])
const warehouses = ref([])
const defaultBinId = ref(null)

const visibleItems = computed(() => {
  return items.value.filter(item => {
    // Show if there is still remaining quantity
    if ((item.quantity - item.received_qty) > 0) return true;
    // Show if it's currently being received (editing mode)
    if (item.current_receive > 0) return true;
    return false;
  })
})

const loadingItems = ref(false)
const saving = ref(false)

const computedIsPartial = computed(() => {
  if (!items.value || items.value.length === 0) return false
  for (const item of items.value) {
    const qty = parseFloat(item.quantity) || 0
    const rQty = parseFloat(item.received_qty) || 0
    const cQty = parseFloat(item.current_receive) || 0
    const totalAfter = rQty + cQty
    // Fix JS precision issues with toFixed
    if (parseFloat(totalAfter.toFixed(2)) < parseFloat(qty.toFixed(2))) {
      return true
    }
  }
  return false
})

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

onMounted(async () => {
  await fetchWarehouses()
  fetchData()
  if (props.editId) {
    loadEditData()
  }
})

async function fetchWarehouses() {
  try {
    const { data } = await api.get('/inventory/warehouses/')
    warehouses.value = data.results || data
    
    // Find default bin
    const mainWh = warehouses.value.find(w => w.code === 'WH-MAIN') || warehouses.value[0]
    if (mainWh && mainWh.bins && mainWh.bins.length > 0) {
      const defaultBin = mainWh.bins.find(b => b.bin_code === 'BIN-RECV') || mainWh.bins[0]
      defaultBinId.value = defaultBin.id
    }
  } catch (error) {
    console.error('Failed to fetch warehouses', error)
  }
}

async function loadEditData() {
  try {
    const { data } = await api.get(`/inventory/receipt-reports/${props.editId}/`)
    formData.receipt_type = data.receipt_type
    formData.vendor = data.vendor
    formData.po = data.po
    formData.receive_date = data.receive_date
    formData.vendor_sn = data.vendor_sn
    formData.vendor_sn_date = data.vendor_sn_date || ''
    formData.memo = data.memo
    
    // We also need to fetch POs for the vendor
    await fetchPOs()
    
    // Then load PO items, and merge existing receive_qty
    await onPoChange(false)
    
    if (data.items) {
      items.value.forEach(item => {
        const matching = data.items.find(i => i.po_item === item.id)
        if (matching) {
          item.current_receive = matching.receive_qty
          if (matching.bins && matching.bins.length > 0) {
            item.selected_bin_id = matching.bins[0].bin
          }
        } else {
          item.current_receive = 0
        }
      })
    }
  } catch (error) {
    console.error('Failed to load edit data', error)
  }
}


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

async function onPoChange(resetItems = true) {
  if (!formData.po) return
  loadingItems.value = true
  if (resetItems) {
    items.value = []
  }
  try {
    const { data } = await api.get(`/purchase/po/${formData.po}/`)
    if (data.details) {
      // If we are editing, we don't want to reset current_receive immediately
      // it will be merged in loadEditData. But if changing PO manually, reset it.
      if (resetItems) {
        items.value = data.details.map(d => ({
          ...d,
          current_receive: Math.max(0, d.quantity - d.received_qty),
          selected_bin_id: defaultBinId.value
        }))
      } else {
        items.value = data.details.map(d => ({
          ...d,
          current_receive: 0,
          selected_bin_id: defaultBinId.value
        }))
      }
    }
  } catch (error) {
    console.error('Failed to fetch PO details', error)
  } finally {
    loadingItems.value = false
  }
}



async function save(submit = false) {
  if (!formData.po) {
    Swal.fire({ icon: 'warning', text: 'Please select a PO' })
    return
  }
  
  const itemsToReceive = items.value.filter(item => item.current_receive > 0)
  if (itemsToReceive.length === 0) {
    Swal.fire({ icon: 'warning', text: 'Please input receive quantity for at least one item' })
    return
  }

  const missingBin = itemsToReceive.find(i => !i.selected_bin_id)
  if (missingBin) {
    Swal.fire({ icon: 'warning', text: `Please select a Bin location for item ${missingBin.item_code}` })
    return
  }

  const invalid = itemsToReceive.find(i => i.current_receive > (i.quantity - i.received_qty))
  if (invalid) {
    Swal.fire({ icon: 'error', text: `Receive quantity for ${invalid.item_code} exceeds remaining quantity.` })
    return
  }

  if (submit) {
    const result = await Swal.fire({
      title: 'Are you sure?',
      text: "You want to save and submit this receipt report for approval?",
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#C2A05B',
      cancelButtonColor: '#d33',
      confirmButtonText: 'Yes, submit it!'
    })
    if (!result.isConfirmed) return
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
        receive_qty: item.current_receive,
        bins: item.selected_bin_id ? [{
          bin: item.selected_bin_id,
          qty: item.current_receive
        }] : []
      }))
    }

    if (!payload.vendor_sn_date) {
      delete payload.vendor_sn_date
    }

    let rrData = null
    if (props.editId) {
      rrData = await store.updateReceiptReport(props.editId, payload)
    } else {
      rrData = await store.createReceiptReport(payload)
    }

    if (submit && rrData && rrData.id) {
      await store.submitReceiptReport(rrData.id)
    }

    emit('success')
  } catch (error) {
    Swal.fire({ icon: 'error', title: 'Save Failed', text: error.detail || 'An error occurred' })
  } finally {
    saving.value = false
  }
}
</script>
