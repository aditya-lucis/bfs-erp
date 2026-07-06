<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="show" class="fixed inset-0 z-50 overflow-y-auto print-modal-overlay">
        <!-- Backdrop -->
        <div class="fixed inset-0 bg-black/40 print:hidden" @click="$emit('close')" />
        
        <div class="flex min-h-full items-start justify-center p-4 py-8 print:p-0">
          <div class="relative bg-white shadow-2xl w-full max-w-[210mm] min-h-[297mm] z-10 print-modal-container font-sans text-gray-800" @click.stop>
            
            <!-- Web-only Header -->
            <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100 print:hidden sticky top-0 bg-white z-20 shadow-sm">
              <h3 class="text-base font-bold text-gray-800 flex items-center gap-2">
                <Printer class="w-5 h-5 text-bfs-navy" />
                Print Preview: {{ data?.receipt_number || 'Loading...' }}
              </h3>
              <div class="flex gap-2">
                <button :disabled="loading" @click="printDocument" class="btn-primary text-sm px-4 py-2 flex items-center gap-2 shadow-md bg-bfs-navy text-white rounded-lg hover:bg-opacity-90 disabled:opacity-50">
                  <Printer class="w-4 h-4" /> Print Document
                </button>
                <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600 bg-gray-100 hover:bg-gray-200 p-2 rounded-lg transition-colors">
                  <X class="w-5 h-5" />
                </button>
              </div>
            </div>

            <!-- Print Page Content -->
            <div id="print-area-wrapper" class="p-8 lg:p-12 bg-white text-[11px] leading-relaxed relative min-h-[280mm] flex flex-col">
              
              <div v-if="loading" class="flex-1 flex items-center justify-center text-gray-400">
                Loading document...
              </div>

              <template v-else-if="data">
                <!-- HEADER -->
                <div class="flex justify-between items-start border-b-2 border-bfs-navy pb-6 mb-6">
                  <!-- Company Logo & Details -->
                  <div class="flex items-center gap-4">
                    <img v-if="orgStore.company?.logo_url" :src="orgStore.company.logo_url" crossorigin="anonymous" alt="Company Logo" class="h-16 object-contain" />
                    <div v-else class="h-16 w-16 bg-gray-100 flex items-center justify-center rounded-lg border border-gray-200">
                      <span class="text-[10px] text-gray-400 font-bold tracking-widest">LOGO</span>
                    </div>
                    <div>
                      <h2 class="text-lg font-black text-bfs-navy tracking-tight uppercase">{{ orgStore.company?.company_name || 'BUMI FINANSIAL SOLUSI' }}</h2>
                      <p class="text-gray-500 mt-1 max-w-[250px]">{{ printAddress }}</p>
                      <div class="flex items-center gap-3 mt-1 text-gray-400 font-medium">
                        <span v-if="orgStore.company?.company_phone">P: {{ orgStore.company?.company_phone }}</span>
                        <span v-if="orgStore.company?.company_email">E: {{ orgStore.company?.company_email }}</span>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Document Title -->
                  <div class="text-right">
                    <h1 class="text-2xl font-black text-bfs-navy tracking-tighter uppercase mb-2">RECEIPT REPORT</h1>
                    <div class="inline-block bg-gray-50 border border-gray-200 rounded px-3 py-1">
                      <p class="text-sm font-bold text-gray-800">NO: {{ data.receipt_number || '-' }}</p>
                    </div>
                  </div>
                </div>

                <!-- INFO SECTION -->
                <div class="grid grid-cols-2 gap-x-12 gap-y-4 mb-8">
                  <!-- Left Info -->
                  <div class="space-y-3">
                    <div class="flex">
                      <span class="w-24 text-gray-500 font-semibold uppercase tracking-wider text-[10px]">TANGGAL</span>
                      <span class="font-medium text-gray-900">: {{ formatDatePrint(data.receive_date) }}</span>
                    </div>
                    <div class="flex">
                      <span class="w-24 text-gray-500 font-semibold uppercase tracking-wider text-[10px]">DITERIMA DARI</span>
                      <span class="font-bold text-gray-900">: {{ data.vendor_name || '-' }}</span>
                    </div>
                  </div>

                  <!-- Right Info -->
                  <div class="space-y-3">
                    <div class="flex">
                      <span class="w-32 text-gray-500 font-semibold uppercase tracking-wider text-[10px]">SURAT JALAN</span>
                      <span class="font-medium text-gray-900">: {{ data.delivery_note_number || '-' }}</span>
                    </div>
                    <div class="flex">
                      <span class="w-32 text-gray-500 font-semibold uppercase tracking-wider text-[10px]">NO. PO</span>
                      <span class="font-bold text-gray-900">: {{ data.po_number || '-' }}</span>
                    </div>
                    <div class="flex">
                      <span class="w-32 text-gray-500 font-semibold uppercase tracking-wider text-[10px]">NO. POLISI</span>
                      <span class="font-medium text-gray-900">: {{ data.vehicle_number || '-' }}</span>
                    </div>
                    <div class="flex">
                      <span class="w-32 text-gray-500 font-semibold uppercase tracking-wider text-[10px]">DIANGKUT OLEH</span>
                      <span class="font-medium text-gray-900">: {{ data.transport_with || '-' }}</span>
                    </div>
                  </div>
                </div>

                <!-- ITEMS TABLE -->
                <div class="mb-8">
                  <table class="w-full text-left border-collapse">
                    <thead>
                      <tr class="bg-gray-50 text-gray-500 uppercase tracking-wider text-[9px]">
                        <th class="py-2 px-3 border-y border-gray-200 font-bold w-12 text-center">No</th>
                        <th class="py-2 px-3 border-y border-gray-200 font-bold">Nama dan Uraian Barang</th>
                        <th class="py-2 px-3 border-y border-gray-200 font-bold w-20 text-center">Sat</th>
                        <th class="py-2 px-3 border-y border-gray-200 font-bold w-24 text-right">Kuantitas</th>
                        <th class="py-2 px-3 border-y border-gray-200 font-bold w-48 text-center">Keterangan</th>
                      </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-100 border-b border-gray-200">
                      <tr v-for="(item, index) in data.items" :key="index">
                        <td class="py-2 px-3 text-center text-gray-500">{{ index + 1 }}</td>
                        <td class="py-2 px-3">
                          <p class="font-bold text-gray-900">{{ item.item_name }}</p>
                          <p class="text-[9px] text-gray-500 mt-0.5">Code: {{ item.item_code }}</p>
                        </td>
                        <td class="py-2 px-3 text-center text-gray-700">{{ item.uom_name }}</td>
                        <td class="py-2 px-3 text-right font-bold text-gray-900">{{ formatNumber(item.qty_received) }}</td>
                        <td class="py-2 px-3 text-center text-gray-700">{{ item.notes || '-' }}</td>
                      </tr>
                      <tr v-if="!data.items?.length">
                        <td colspan="5" class="py-4 text-center text-gray-400 font-medium">No items available</td>
                      </tr>
                    </tbody>
                  </table>
                  
                  <div class="mt-4 p-3 bg-gray-50 rounded border border-gray-100">
                    <span class="font-bold text-gray-600 uppercase tracking-wider text-[9px]">Note :</span>
                    <p class="text-gray-800 mt-1 min-h-[20px]">{{ data.notes || 'Lembar ini harus disertakan pada saat melakukan penagihan.' }}</p>
                  </div>
                </div>

                <!-- SIGNATURES -->
                <div class="mt-auto pt-16 pb-8">
                  <div class="flex w-full justify-between items-end text-center">
                    <div class="flex-1">
                      <p class="text-sm font-bold text-gray-900 mb-20">Diketahui oleh</p>
                      <p class="text-sm font-bold text-gray-900">(__________________)</p>
                    </div>
                    <div class="flex-1">
                      <p class="text-sm font-bold text-gray-900 mb-20">Diperiksa oleh</p>
                      <p class="text-sm font-bold text-gray-900">(__________________)</p>
                    </div>
                    <div class="flex-1">
                      <p class="text-sm font-bold text-gray-900 mb-20">Diserahkan oleh</p>
                      <p class="text-sm font-bold text-gray-900">(__________________)</p>
                    </div>
                    <div class="flex-1">
                      <p class="text-sm font-bold text-gray-900 mb-20">Diterima oleh</p>
                      <p class="text-sm font-bold text-gray-900">(__________________)</p>
                    </div>
                  </div>
                </div>

                <!-- FOOTER / META -->
                <div class="flex justify-between items-center mt-12 pt-4 border-t border-gray-200 text-gray-400 text-[9px] font-medium uppercase tracking-wider">
                  <span>Rangkap 1 = Supplier, 2 = Accounting, 3 = Purchasing, 4 = Warehouse</span>
                  <span>{{ formatDatePrint(new Date()) }}</span>
                  <span>Doc No: 05/FRM/WRH | Rev: 00</span>
                </div>
              </template>
              
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, ref, watch, onMounted } from 'vue'
import { Printer, X } from 'lucide-vue-next'
import api from '../../services/api'
import { useOrganizationStore } from '../../stores/organization'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  documentId: {
    type: [Number, String],
    default: null
  }
})

const emit = defineEmits(['close'])

const orgStore = useOrganizationStore()
const loading = ref(false)
const data = ref(null)

onMounted(async () => {
  if (!orgStore.company) {
    await orgStore.fetchCompany()
  }
})

const printAddress = computed(() => {
  if (!orgStore.company) return '-'
  return orgStore.company.company_address || '-'
})

watch(() => props.show, async (newVal) => {
  if (newVal && props.documentId) {
    await loadData()
  }
})

async function loadData() {
  loading.value = true
  try {
    const response = await api.get(`/inventory/receipt-reports/${props.documentId}/print_data/`)
    data.value = response.data
  } catch (error) {
    console.error('Failed to load print data', error)
  } finally {
    loading.value = false
  }
}

function formatNumber(val) {
  if (val === undefined || val === null) return '0.00'
  const num = Number(val)
  return num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function formatDatePrint(dateStr) {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  if (isNaN(d.getTime())) return dateStr
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const day = d.getDate().toString().padStart(2, '0')
  const month = months[d.getMonth()]
  const year = d.getFullYear().toString().slice(-2)
  return `${day}-${month}-${year}`
}

function printDocument() {
  window.print()
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

@media print {
  @page {
    size: A4 portrait;
    margin: 0;
  }
  body * {
    visibility: hidden;
  }
  .print-modal-overlay {
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
    margin: 0;
    padding: 0;
    background: white;
    overflow: visible;
  }
  .print-modal-container,
  .print-modal-container * {
    visibility: visible;
  }
  .print-modal-container {
    position: absolute;
    left: 0;
    top: 0;
    width: 210mm !important;
    max-width: 210mm !important;
    min-height: 297mm !important;
    margin: 0 !important;
    padding: 0 !important;
    box-shadow: none !important;
  }
}
</style>
