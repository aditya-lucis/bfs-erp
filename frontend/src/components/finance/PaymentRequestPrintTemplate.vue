<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="show" class="fixed inset-0 z-50 overflow-y-auto print-modal-overlay">
        <!-- Backdrop -->
        <div class="fixed inset-0 bg-black/40 print:hidden" @click="$emit('close')" />
        
        <div class="flex min-h-full items-start justify-center p-4 py-8 print:p-0">
          <div class="relative bg-white shadow-2xl w-full max-w-[210mm] min-h-[297mm] z-10 print-modal-container" @click.stop>
            
            <!-- Web-only Header -->
            <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100 print:hidden sticky top-0 bg-white z-20 shadow-sm">
              <h3 class="text-base font-bold text-gray-800 flex items-center gap-2">
                <Printer class="w-5 h-5 text-bfs-gold" />
                Print Preview: {{ document?.document_number || 'PAYMENT REQUEST' }}
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

            <div class="p-4 lg:p-8 bg-white text-black text-[11px] font-sans">
              <!-- Header: Company Info -->
              <div class="flex justify-between items-start border-b-2 border-black pb-2 mb-4">
                <div class="flex items-center space-x-4">
                  <img v-if="orgStore.company?.logo_url" :src="orgStore.company.logo_url" alt="Company Logo" class="h-16 object-contain" />
                  <div v-else class="h-16 w-16 bg-gray-200 flex items-center justify-center rounded">
                    <span class="text-[10px] text-gray-500 font-bold">LOGO</span>
                  </div>
                  <div class="text-[10px] leading-tight max-w-xs">
                    <p class="font-bold text-sm">{{ orgStore.company?.company_name || 'PT. BUMI FINANSIAL SOLUSI' }}</p>
                    <p>{{ printAddress }}</p>
                    <p>Phone: {{ orgStore.company?.company_phone || '-' }}</p>
                    <p>Email: {{ orgStore.company?.company_email || '-' }}</p>
                  </div>
                </div>
                <div class="text-right">
                  <h1 class="text-xl font-bold tracking-tight uppercase">Payment Request</h1>
                  <p class="text-base font-bold mt-1 border border-black px-2 py-1 inline-block">No: {{ document?.document_number || '-' }}</p>
                  <p v-if="document?.approval_status === 'approved'" class="text-xs text-black font-bold tracking-widest mt-1">(DUPLICATE)</p>
                </div>
              </div>

              <!-- Document Info Table -->
              <div class="mb-4">
                <table class="w-full border-collapse border border-black text-[11px]">
                  <tbody>
                    <tr>
                      <td class="border border-black px-2 py-1 font-semibold w-1/4 bg-gray-100">Date</td>
                      <td class="border border-black px-2 py-1 w-1/4">{{ formatDatePrint(document?.date) }}</td>
                      <td class="border border-black px-2 py-1 font-semibold w-1/4 bg-gray-100">Department</td>
                      <td class="border border-black px-2 py-1 w-1/4">{{ document?.requestor_department_display || '-' }}</td>
                    </tr>
                    <tr>
                      <td class="border border-black px-2 py-1 font-semibold bg-gray-100">Currency</td>
                      <td class="border border-black px-2 py-1">{{ document?.currency_id || 'IDR' }}</td>
                      <td class="border border-black px-2 py-1 font-semibold bg-gray-100">Amount</td>
                      <td class="border border-black px-2 py-1 font-bold">{{ formatCurrencyRaw(document?.amount || 0) }}</td>
                    </tr>
                    <tr>
                      <td class="border border-black px-2 py-1 font-semibold bg-gray-100">Due Date</td>
                      <td class="border border-black px-2 py-1">{{ formatDatePrint(document?.due_date) }}</td>
                      <td class="border border-black px-2 py-1 font-semibold bg-gray-100">Flow Type</td>
                      <td class="border border-black px-2 py-1">{{ document?.cash_flow_code || '-' }}</td>
                    </tr>
                    <tr>
                      <td class="border border-black px-2 py-1 font-semibold bg-gray-100">Termin</td>
                      <td class="border border-black px-2 py-1">{{ document?.usage_for === 'Project Cash Advanced' ? (document?.duration_due_date || '-') : (document?.term_duration || '-') }}</td>
                      <td class="border border-black px-2 py-1 font-semibold bg-gray-100">Transaction</td>
                      <td class="border border-black px-2 py-1">{{ document?.transaction_type_display || '-' }}</td>
                    </tr>
                    <tr>
                      <td class="border border-black px-2 py-1 font-semibold bg-gray-100 text-black">Usage For</td>
                      <td class="border border-black px-2 py-1 text-black font-semibold" colspan="3">{{ document?.usage_for || '-' }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- Item Details Table -->
              <div class="mb-4">
                <table class="w-full border-collapse border border-black text-[11px]">
                  <thead>
                    <tr class="bg-gray-100">
                      <th class="border border-black px-2 py-1 w-10 text-center">NO</th>
                      <th class="border border-black px-2 py-1">PROJECT NAME / SITE NAME</th>
                      <th class="border border-black px-2 py-1">DESCRIPTION & SPECIFICATION</th>
                      <th class="border border-black px-2 py-1 w-20 text-center">QUANTITY</th>
                      <th class="border border-black px-2 py-1 w-32 text-right">AMOUNT</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td class="border border-black px-2 py-1 text-center">1</td>
                      <td class="border border-black px-2 py-1 font-semibold">
                        {{ document?.project_display || '-' }}
                        <div v-if="document?.site_name" class="font-normal">{{ document.site_name }}</div>
                      </td>
                      <td class="border border-black px-2 py-1">
                        {{ document?.description || '-' }}
                        <div v-if="document?.po_number" class="mt-1 text-[10px]">Purchase Order: {{ document.po_number }}</div>
                      </td>
                      <td class="border border-black px-2 py-1 text-center">{{ document?.total_quantity || '0' }}</td>
                      <td class="border border-black px-2 py-1 text-right font-semibold">{{ document?.currency_id || 'IDR' }} {{ formatCurrencyRaw(document?.amount || 0) }}</td>
                    </tr>
                    <tr v-if="parseFloat(document?.tax_amount || 0) > 0">
                      <td colspan="4" class="border border-black px-2 py-1 text-right font-semibold">Tax Amount</td>
                      <td class="border border-black px-2 py-1 text-right font-semibold">{{ document?.currency_id || 'IDR' }} {{ formatCurrencyRaw(document?.tax_amount || 0) }}</td>
                    </tr>
                    <tr v-if="parseFloat(document?.tax_amount || 0) > 0">
                      <td colspan="4" class="border border-black px-2 py-1 text-right font-bold bg-gray-100">Grand Total</td>
                      <td class="border border-black px-2 py-1 text-right font-bold bg-gray-100">{{ document?.currency_id || 'IDR' }} {{ formatCurrencyRaw((parseFloat(document?.amount || 0) + parseFloat(document?.tax_amount || 0)).toFixed(2)) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- Notes, In Words, and RAP -->
              <div class="mb-4 grid grid-cols-2 gap-4">
                <div>
                  <div class="border border-black min-h-[60px] p-2 h-full flex flex-col">
                    <p class="font-semibold bg-gray-100 border-b border-black -mx-2 -mt-2 px-2 py-1 mb-2">Note / Payment To :</p>
                    <p class="font-bold flex-1 whitespace-pre-wrap">{{ document?.payment_to_bank_details || 'Bank details not specified' }}</p>
                    <p class="font-bold uppercase mt-2">{{ document?.payment_to_display || '-' }}</p>
                  </div>
                </div>
                
                <div class="space-y-4">
                  <div class="border border-black p-2 min-h-[40px]">
                    <p class="font-semibold bg-gray-100 border-b border-black -mx-2 -mt-2 px-2 py-1 mb-2">In Word :</p>
                    <p class="font-bold italic text-black">{{ terbilangEnglish(parseFloat(document?.amount || 0) + parseFloat(document?.tax_amount || 0)) }} Rupiahs</p>
                  </div>
                  
                  <div class="border border-black p-2 min-h-[40px]">
                    <p class="font-semibold bg-gray-100 border-b border-black -mx-2 -mt-2 px-2 py-1 mb-2">RAP Comparation :</p>
                    <div class="flex flex-col gap-1 mt-1">
                      <div class="flex items-center gap-2">
                        <div class="w-3 h-3 border border-black flex items-center justify-center font-bold text-[9px]" :class="isRapGreater ? 'text-black' : 'text-transparent'">✓</div>
                        <span>Lebih Besar dari RAP</span>
                      </div>
                      <div class="flex items-center gap-2">
                        <div class="w-3 h-3 border border-black flex items-center justify-center font-bold text-[9px]" :class="isRapSmaller ? 'text-black' : 'text-transparent'">✓</div>
                        <span>Lebih Kecil dari RAP</span>
                      </div>
                      <div class="flex items-center gap-2">
                        <div class="w-3 h-3 border border-black flex items-center justify-center font-bold text-[9px]" :class="isRapEqual ? 'text-black' : 'text-transparent'">✓</div>
                        <span>Sama dengan RAP</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Document Signatures Box -->
              <div class="mt-6 border border-black bg-white p-2">
                <div class="text-[10px] uppercase font-bold text-black mb-2 border-b border-black pb-1">Document Signatures</div>
                <div class="flex flex-wrap gap-2 justify-start">
                  
                  <!-- Approvals -->
                  <div 
                    v-for="sig in signatures" 
                    :key="sig.id"
                    class="border border-black p-2 text-center w-[140px] flex flex-col justify-between h-[120px]"
                  >
                    <div>
                      <div class="text-[9px] uppercase font-bold text-black">{{ sig.role_display || 'Approved By' }}</div>
                      <div class="text-[9px] font-semibold text-gray-700">{{ sig.position_name }}</div>
                    </div>
                    <div class="flex-1 flex items-center justify-center py-1 h-12">
                      <template v-if="sig.is_signed">
                        <img v-if="sig.signature_draw && sig.signature_draw.startsWith('data:image')" :src="sig.signature_draw" alt="Signature" class="max-h-10 max-w-full object-contain" />
                        <img v-else-if="sig.signature_image" :src="sig.signature_image" alt="Signature" class="max-h-10 max-w-full object-contain" />
                        <div v-else class="px-1 py-0.5 border border-black rounded text-[7px] text-black font-serif italic font-bold">SIGNED DIGITALLY</div>
                      </template>
                      <div v-else class="text-[9px] italic text-gray-400">Pending</div>
                    </div>
                    <div class="border-t border-black pt-1 text-[8px] text-black mt-1">
                      <div class="font-bold truncate" :title="sig.signer_employee_name">{{ sig.signer_employee_name || sig.signer_name || '(Pending)' }}</div>
                      <div class="text-[7px] text-gray-500 mt-0.5">{{ sig.signed_at ? new Date(sig.signed_at).toLocaleString('en-GB') : 'Not signed' }}</div>
                    </div>
                  </div>

                </div>
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
  show: Boolean,
  document: {
    type: Object,
    default: () => ({})
  },
  signatures: {
    type: Array,
    default: () => []
  }
})

defineEmits(['close'])

const orgStore = useOrganizationStore()

onMounted(() => {
  if (!orgStore.company) {
    orgStore.fetchCompany()
  }
})

const printAddress = computed(() => {
  const comp = orgStore.company
  if (!comp) return ''
  let addr = comp.company_address || ''
  if (comp.company_city) addr += `, ${comp.company_city}`
  if (comp.company_postal_code) addr += ` ${comp.company_postal_code}`
  return addr
})

const formatDatePrint = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }).replace(/ /g, '-')
}

const formatCurrencyRaw = (val) => {
  if (!val) return '0.00'
  return parseFloat(val).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

// Terbilang English
const terbilangEnglish = (s) => {
  const th = ['', 'Thousand', 'Million', 'Billion', 'Trillion'];
  const dg = ['Zero', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine'];
  const tn = ['Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen'];
  const tw = ['Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety'];
  
  s = s.toString().split('.')[0]; // Only process integer part
  s = s.replace(/[\, ]/g, '');
  if (isNaN(parseFloat(s))) return 'not a number';
  var x = s.length;
  if (x > 15) return 'too big';
  var n = s.split('');
  var str = '';
  var sk = 0;
  for (var i = 0; i < x; i++) {
    if ((x - i) % 3 == 2) {
      if (n[i] == '1') {
        str += tn[Number(n[i + 1])] + ' ';
        i++;
        sk = 1;
      } else if (n[i] != 0) {
        str += tw[n[i] - 2] + ' ';
        sk = 1;
      }
    } else if (n[i] != 0) {
      str += dg[n[i]] + ' ';
      if ((x - i) % 3 == 0) str += 'Hundred ';
      sk = 1;
    }
    if ((x - i) % 3 == 1) {
      if (sk) str += th[(x - i - 1) / 3] + ' ';
      sk = 0;
    }
  }
  return str.replace(/\s+/g, ' ').trim() || 'Zero';
}

const isRapGreater = computed(() => {
  if (!props.document?.amount || !props.document?.rap_total_cost) return false
  const tax = parseFloat(props.document.tax_amount || 0)
  return (parseFloat(props.document.amount) - tax) > parseFloat(props.document.rap_total_cost)
})

const isRapSmaller = computed(() => {
  if (!props.document?.amount || !props.document?.rap_total_cost) return false
  const tax = parseFloat(props.document.tax_amount || 0)
  return (parseFloat(props.document.amount) - tax) < parseFloat(props.document.rap_total_cost)
})

const isRapEqual = computed(() => {
  if (!props.document?.amount || !props.document?.rap_total_cost) return false
  const tax = parseFloat(props.document.tax_amount || 0)
  return (parseFloat(props.document.amount) - tax) === parseFloat(props.document.rap_total_cost)
})

const printDocument = () => {
  setTimeout(() => {
    window.print()
  }, 100)
}
</script>

<style scoped>
@media print {
  @page {
    size: A4;
    margin: 10mm;
  }
  .print-modal-overlay {
    position: static !important;
    background: none !important;
  }
  .print-modal-container {
    position: absolute !important;
    left: 0 !important;
    top: 0 !important;
    width: 210mm !important;
    max-width: 210mm !important;
    height: auto !important;
    max-height: none !important;
    border: none !important;
    box-shadow: none !important;
    background: white !important;
    display: flex !important;
    flex-direction: column !important;
    overflow: visible !important;
  }
}
</style>
