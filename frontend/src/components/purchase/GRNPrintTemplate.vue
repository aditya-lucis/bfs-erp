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
                Print Preview: {{ grn?.grn_number || 'GRN' }}
              </h3>
              <div class="flex gap-2">
                <button @click="printDocument" class="btn-primary text-sm px-4 py-2 flex items-center gap-2 shadow-md bg-bfs-navy text-white rounded-lg hover:bg-opacity-90">
                  <Printer class="w-4 h-4" /> Print Document
                </button>
                <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600 bg-gray-100 hover:bg-gray-200 p-2 rounded-lg transition-colors">
                  <X class="w-5 h-5" />
                </button>
              </div>
            </div>

            <!-- Print Page Content -->
            <div class="p-8 lg:p-12 bg-white text-[11px] leading-relaxed relative">
              
              <!-- HEADER -->
              <div class="flex justify-between items-start border-b-2 border-bfs-navy pb-6 mb-6">
                <!-- Company Logo & Details -->
                <div class="flex items-center gap-4">
                  <img v-if="orgStore.company?.logo_url" :src="orgStore.company.logo_url" alt="Company Logo" class="h-16 object-contain" />
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
                  <h1 class="text-2xl font-black text-bfs-navy tracking-tighter uppercase mb-2">Good Receipt Note</h1>
                  <div class="inline-block bg-gray-50 border border-gray-200 rounded px-3 py-1">
                    <p class="text-sm font-bold text-gray-800">No: {{ grn?.grn_number || '-' }}</p>
                  </div>
                </div>
              </div>

              <!-- INFO SECTION -->
              <div class="grid grid-cols-2 gap-x-12 gap-y-4 mb-8">
                <!-- Left Info -->
                <div class="space-y-3">
                  <div class="flex">
                    <span class="w-24 text-gray-500 font-semibold uppercase tracking-wider text-[10px]">Date</span>
                    <span class="font-medium text-gray-900">: {{ formatDatePrint(grn?.document_date) }}</span>
                  </div>
                  <div class="flex">
                    <span class="w-24 text-gray-500 font-semibold uppercase tracking-wider text-[10px]">Company</span>
                    <span class="font-bold text-gray-900">: {{ grn?.vendor_name || '-' }}</span>
                  </div>
                  <div class="flex">
                    <span class="w-24 text-gray-500 font-semibold uppercase tracking-wider text-[10px]">Description</span>
                    <span class="flex-1 font-medium text-gray-900 leading-snug whitespace-pre-wrap">: {{ grn?.description || '-' }}</span>
                  </div>
                </div>

                <!-- Right Info -->
                <div class="space-y-3">
                  <div class="flex">
                    <span class="w-32 text-gray-500 font-semibold uppercase tracking-wider text-[10px]">RAP / Activity Code</span>
                    <span class="font-medium text-gray-900">: {{ grn?.po_detail?.rap_name || '-' }}</span>
                  </div>
                  <div class="flex">
                    <span class="w-32 text-gray-500 font-semibold uppercase tracking-wider text-[10px]">Purchase Order No</span>
                    <span class="font-bold text-gray-900">: {{ grn?.po_number || '-' }}</span>
                  </div>
                  <div class="flex">
                    <span class="w-32 text-gray-500 font-semibold uppercase tracking-wider text-[10px]">Project / Site ID</span>
                    <span class="font-medium text-gray-900">: {{ grn?.site_name || '-' }}</span>
                  </div>
                </div>
              </div>

              <!-- DOCUMENTS CHECKLIST -->
              <div class="mb-8">
                <div class="text-xs font-bold text-bfs-navy uppercase tracking-wider mb-2 border-b border-bfs-navy pb-1">Check List for Document</div>
                <table class="w-full text-left border-collapse">
                  <thead>
                    <tr class="bg-gray-50 text-gray-500 uppercase tracking-wider text-[9px]">
                      <th class="py-2 px-3 border-y border-gray-200 font-bold w-12 text-center">No</th>
                      <th class="py-2 px-3 border-y border-gray-200 font-bold">Item Description</th>
                      <th class="py-2 px-3 border-y border-gray-200 font-bold w-16 text-center">Tick</th>
                      <th class="py-2 px-3 border-y border-gray-200 font-bold">Document Number</th>
                      <th class="py-2 px-3 border-y border-gray-200 font-bold">Remarks / Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(doc, idx) in grn?.documents" :key="idx" class="border-b border-gray-100 last:border-b-0">
                      <td class="py-2 px-3 text-center text-gray-500">{{ idx + 1 }}</td>
                      <td class="py-2 px-3 font-medium text-gray-800">{{ doc.document_name || '-' }}</td>
                      <td class="py-2 px-3 text-center">
                        <div v-if="doc.is_available" class="inline-flex items-center justify-center w-4 h-4 rounded bg-green-50 text-green-600 font-bold">✓</div>
                        <div v-else class="inline-flex items-center justify-center w-4 h-4 rounded bg-gray-50 text-gray-300 font-bold">-</div>
                      </td>
                      <td class="py-2 px-3 text-gray-700">{{ doc.document_number || '-' }}</td>
                      <td class="py-2 px-3 text-gray-700">{{ doc.keterangan || '-' }}</td>
                    </tr>
                    <tr v-if="!grn?.documents?.length">
                      <td colspan="5" class="py-4 text-center text-gray-400 font-medium">No documents available</td>
                    </tr>
                  </tbody>
                </table>
                <div class="mt-4 p-3 bg-gray-50 rounded border border-gray-100">
                  <span class="font-bold text-gray-600 uppercase tracking-wider text-[9px]">Notes :</span>
                  <p class="text-gray-800 mt-1 min-h-[20px]">{{ grn?.void_reason || '-' }}</p>
                </div>
              </div>

              <!-- CALCULATIONS / SUMMARY -->
              <div class="flex justify-end mb-10">
                <div class="w-72">
                  <div class="space-y-2 border-b border-gray-200 pb-3 mb-3">
                    <div class="flex justify-between text-gray-600">
                      <span class="font-medium">PO Amount</span>
                      <span class="font-bold text-gray-900">{{ formatCurrencyRaw(grn?.po_detail?.total_amount) }}</span>
                    </div>
                    <div class="flex justify-between text-gray-600">
                      <span class="font-medium">PPN</span>
                      <span class="font-bold text-gray-900">{{ formatCurrencyRaw(grn?.po_detail?.total_tax) }}</span>
                    </div>
                    <div class="flex justify-between text-gray-600">
                      <span class="font-medium">Discount</span>
                      <span class="font-bold text-gray-900">{{ formatCurrencyRaw(grn?.po_detail?.total_discount) }}</span>
                    </div>
                  </div>
                  <div class="space-y-2">
                    <div class="flex justify-between text-bfs-navy text-[13px]">
                      <span class="font-black">Net PO Amount</span>
                      <span class="font-black">{{ formatCurrencyRaw(grn?.po_detail?.grand_total) }}</span>
                    </div>
                    <div class="flex justify-between items-end mt-2">
                      <span class="font-bold text-gray-700">Term Percentage</span>
                      <div class="text-right">
                        <span class="text-[10px] text-gray-500 block mb-0.5">{{ grn?.term_percentage || 0 }}% =</span>
                        <span class="font-black text-bfs-gold text-[13px]">{{ formatCurrencyRaw(grn?.amount) }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- SIGNATURES -->
              <div v-if="grn?.approval_status && grn.approval_status !== 'draft'" class="mt-8">
                <div class="flex w-full border border-gray-200 rounded-lg overflow-hidden">
                  <div 
                    v-for="(sig, index) in signatures" 
                    :key="sig.id"
                    class="flex-1 flex flex-col items-center justify-between min-h-[140px] border-r border-gray-200 last:border-r-0 bg-white"
                  >
                    <!-- Header Position -->
                    <div class="w-full text-center py-2 bg-gray-50 border-b border-gray-200">
                      <div class="text-[9px] uppercase font-bold text-gray-700 tracking-wider">
                        {{ sig.role_display }}
                      </div>
                    </div>

                    <!-- Signature Area -->
                    <div class="flex-1 flex items-center justify-center p-2 relative w-full">
                      <template v-if="sig.is_signed">
                        <img v-if="sig.signature_draw && sig.signature_draw.startsWith('data:image')" :src="sig.signature_draw" alt="Signature" class="max-h-14 max-w-full object-contain" />
                        <img v-else-if="sig.signature_image" :src="sig.signature_image" alt="Signature" class="max-h-14 max-w-full object-contain" />
                        <div v-else class="px-2 py-1 border-2 border-green-500 rounded-md text-[10px] text-green-600 font-serif italic font-black -rotate-6">APPROVED</div>
                        <div class="absolute bottom-2 right-2 text-[7px] text-gray-400 font-medium">
                          {{ sig.signed_at ? new Date(sig.signed_at).toLocaleDateString() : '' }}
                        </div>
                      </template>
                      <div v-else class="text-[10px] italic text-gray-300 font-medium">Pending Signature</div>
                    </div>

                    <!-- Footer Name & Date -->
                    <div class="w-full text-center py-2 border-t border-gray-200 px-2">
                      <div class="font-bold text-gray-900 truncate" :title="sig.signer_employee_name">
                        {{ sig.signer_employee_name || sig.signer_name || '(Pending)' }}
                      </div>
                      <div class="text-[8px] text-gray-500 mt-0.5 truncate">{{ sig.position_name || '-' }}</div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- FOOTER / META -->
              <div class="flex justify-between items-center mt-12 pt-4 border-t border-gray-200 text-gray-400 text-[9px] font-medium uppercase tracking-wider">
                <span>REV#01</span>
                <span>{{ formatDatePrint(new Date()) }}</span>
                <span>FRM-GRND-02-01</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { Printer, X } from 'lucide-vue-next'
import { useOrganizationStore } from '../../stores/organization'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  grn: {
    type: Object,
    default: () => null
  },
  signatures: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['close'])

const orgStore = useOrganizationStore()

onMounted(async () => {
  if (!orgStore.company) {
    await orgStore.fetchCompany()
  }
})

const printAddress = computed(() => {
  if (!orgStore.company) return '-'
  return orgStore.company.company_address || '-'
})

function formatCurrencyRaw(val) {
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
