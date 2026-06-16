import sys
import re

file_path = 'c:\\Traine\\bfs-erp\\frontend\\src\\views\\gl\\GeneralJournalListView.vue'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add Printer to lucide-vue-next import
content = re.sub(r'import\s+\{(.*?)\}\s+from\s+''lucide-vue-next''', lambda m: m.group(0) if 'Printer' in m.group(1) else m.group(0).replace(m.group(1), m.group(1) + ', Printer'), content)

# Add useApprovalRequestStore import
if 'useApprovalRequestStore' not in content:
    content = re.sub(r'(import \{ useAuthStore \} from ''../../stores/auth\.js'')', r'\1\nimport { useApprovalRequestStore } from ''../../stores/approvalRequest.js''', content)

# Initialize store
if 'approvalStore =' not in content:
    content = re.sub(r'(const authStore = useAuthStore\(\))', r'\1\nconst approvalStore = useApprovalRequestStore()', content)

# Add printModal state
print_logic = '''

const printModal = reactive({
  show: false,
  transaction: null,
  signatures: [],
  isLoadingSignatures: false
})

async function openPrintPreview(item) {
  printModal.transaction = item
  printModal.show = true
  printModal.signatures = []
  
  if (item.status !== 'DRAFT') {
    printModal.isLoadingSignatures = true
    try {
      const sigs = await approvalStore.fetchSignatures('GEJ', item.id)
      printModal.signatures = sigs || []
    } catch (e) {
      console.error('Failed to fetch signatures', e)
    } finally {
      printModal.isLoadingSignatures = false
    }
  }
}

function printDocument() {
  window.print()
}

const printTotalDebit = computed(() => {
  if (!printModal.transaction || !printModal.transaction.details) return 0
  return printModal.transaction.details.reduce((sum, d) => sum + parseFloat(d.debit || 0), 0)
})

const printTotalCredit = computed(() => {
  if (!printModal.transaction || !printModal.transaction.details) return 0
  return printModal.transaction.details.reduce((sum, d) => sum + parseFloat(d.credit || 0), 0)
})

const companyInfo = computed(() => authStore.user?.company || {})
'''
if 'const printModal =' not in content:
    content = re.sub(r'(const today = new Date\(\))', print_logic + r'\n\1', content)

# Add Print button to template action column
print_btn = '''
                    <button 
                      @click="openPrintPreview(item)" 
                      class="p-1.5 rounded-md hover:bg-slate-100 text-slate-500 hover:text-bfs-navy transition-colors"
                      title="Print Preview"
                    >
                      <Printer class="w-4 h-4" />
                    </button>
'''
if 'openPrintPreview(item)' not in content:
    content = re.sub(r'(<button\s+v-if="canUpdate"\s+@click="navigateToEntry\(item\.id\)")', print_btn + r'\1', content)

# Add the Modal HTML before </Panel>
modal_html = '''
    <!-- Print Preview Modal -->
    <Teleport to="body">
      <Transition 
        enter-active-class="transition duration-300 ease-out"
        enter-from-class="opacity-0 scale-95"
        enter-to-class="opacity-100 scale-100"
        leave-active-class="transition duration-200 ease-in"
        leave-from-class="opacity-100 scale-100"
        leave-to-class="opacity-0 scale-95"
      >
        <div v-if="printModal.show" class="fixed inset-0 z-50 flex items-center justify-center p-4 print-modal-overlay">
          <div class="absolute inset-0 bg-black/60 print:hidden" @click="printModal.show = false" />
          
          <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-[210mm] max-h-[95vh] overflow-y-auto z-10 border border-gray-100 flex flex-col print-modal-container">
            
            <!-- Toolbar (Hidden on print) -->
            <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between bg-bfs-navy text-white rounded-t-2xl print:hidden">
              <div class="flex items-center gap-3">
                <Printer class="w-4 h-4 text-bfs-gold" />
                <h3 class="font-bold text-lg tracking-wide">Print Preview General Journal</h3>
              </div>
              <div class="flex items-center gap-3">
                <button 
                  @click="printDocument" 
                  class="flex items-center gap-2 px-4 py-1.5 bg-bfs-gold hover:bg-yellow-500 text-bfs-navy font-bold rounded-lg transition-colors cursor-pointer"
                >
                  <Printer class="w-3.5 h-3.5" />
                  Print A4
                </button>
                <div class="w-px h-6 bg-white/20 mx-1"></div>
                <button @click="printModal.show = false" class="text-white/80 hover:text-white transition-colors">
                  <X class="w-6 h-6" />
                </button>
              </div>
            </div>

            <!-- Print Document Area (A4 layout styling) -->
            <div id="print-area" class="p-8 bg-white flex-1 text-xs text-gray-800 space-y-6 select-text overflow-y-auto">
              
              <!-- HEADER: Company Profile -->
              <div class="flex justify-between items-start border-b-2 border-gray-800 pb-4">
                <div class="flex flex-col text-[10px] leading-tight">
                  <h1 class="font-extrabold text-sm mb-1 uppercase tracking-wider">{{ companyInfo.name || 'PT. Bfs ERP' }}</h1>
                  <p>{{ companyInfo.address || 'Alamat Perusahaan' }}</p>
                  <p v-if="companyInfo.phone">Phone : {{ companyInfo.phone }}</p>
                  <p v-if="companyInfo.email">Email : {{ companyInfo.email }}</p>
                </div>
                <!-- Logo Company -->
                <div v-if="companyInfo.logo" class="h-16 w-48 flex items-start justify-end">
                  <img :src="companyInfo.logo" alt="Company Logo" class="max-h-full max-w-full object-contain" />
                </div>
              </div>

              <!-- TITLE -->
              <div class="text-center">
                <h2 class="text-lg font-black uppercase tracking-widest border-b border-gray-300 inline-block pb-1">General Journal Transaction</h2>
              </div>

              <!-- TRANSACTION INFO -->
              <div class="flex justify-center">
                <div class="grid grid-cols-[auto_auto_1fr] gap-x-2 gap-y-1 text-[11px] max-w-2xl">
                  <div class="text-right text-gray-500">Number</div>
                  <div>:</div>
                  <div class="font-bold">{{ printModal.transaction?.transaction_number }}</div>

                  <div class="text-right text-gray-500">Date</div>
                  <div>:</div>
                  <div>{{ formatDate(printModal.transaction?.date) }}</div>

                  <div class="text-right text-gray-500">Memo</div>
                  <div>:</div>
                  <div class="whitespace-pre-wrap">{{ printModal.transaction?.memo }}</div>

                  <div class="text-right text-gray-500">Project</div>
                  <div>:</div>
                  <div>{{ printModal.transaction?.project_name || '-' }}</div>

                  <div class="text-right text-gray-500">TaxRectification</div>
                  <div>:</div>
                  <div>{{ printModal.transaction?.tax_rectification || '-' }}</div>

                  <div class="text-right text-gray-500">Is Adjustment PPh</div>
                  <div>:</div>
                  <div>{{ printModal.transaction?.is_adjustment_pph ? 'Yes' : 'No' }}</div>
                </div>
              </div>

              <!-- DETAILS TABLE -->
              <div class="mt-4">
                <table class="w-full border-collapse border border-gray-800 text-[9px] mb-4">
                  <thead>
                    <tr class="bg-gray-100/50">
                      <th class="border border-gray-800 p-1.5 text-center w-8">No</th>
                      <th class="border border-gray-800 p-1.5 text-left">Account</th>
                      <th class="border border-gray-800 p-1.5 text-center">Currency</th>
                      <th class="border border-gray-800 p-1.5 text-right">Debit</th>
                      <th class="border border-gray-800 p-1.5 text-right">Credit</th>
                      <th class="border border-gray-800 p-1.5 text-center">Period From</th>
                      <th class="border border-gray-800 p-1.5 text-center">Period To</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(detail, idx) in printModal.transaction?.details || []" :key="idx">
                      <td class="border border-gray-800 p-1.5 text-center">{{ idx + 1 }}</td>
                      <td class="border border-gray-800 p-1.5">
                        <div class="font-bold">{{ detail.account_number || detail.account }}</div>
                        <div class="text-[8px] text-gray-600">{{ detail.account_name || '' }}</div>
                      </td>
                      <td class="border border-gray-800 p-1.5 text-center">{{ detail.currency }}</td>
                      <td class="border border-gray-800 p-1.5 text-right font-mono">{{ formatCurrency(detail.debit) }}</td>
                      <td class="border border-gray-800 p-1.5 text-right font-mono">{{ formatCurrency(detail.credit) }}</td>
                      <td class="border border-gray-800 p-1.5 text-center">{{ formatDate(detail.period_from) || '-' }}</td>
                      <td class="border border-gray-800 p-1.5 text-center">{{ formatDate(detail.period_to) || '-' }}</td>
                    </tr>
                    
                    <!-- TOTAL ROW -->
                    <tr class="bg-gray-100 font-bold border-t-2 border-gray-800">
                      <td colspan="3" class="border border-gray-800 p-1.5 text-right uppercase tracking-wider">Total</td>
                      <td class="border border-gray-800 p-1.5 text-right font-mono">{{ formatCurrency(printTotalDebit) }}</td>
                      <td class="border border-gray-800 p-1.5 text-right font-mono">{{ formatCurrency(printTotalCredit) }}</td>
                      <td colspan="2" class="border border-gray-800 p-1.5"></td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- SIGNATURES -->
              <div v-if="printModal.transaction && printModal.transaction.status !== 'DRAFT'" class="mt-8 border border-gray-800 p-2">
                <div class="text-[8px] uppercase font-bold text-gray-600 mb-2 tracking-wider">Document Signatures (Persetujuan Dokumen)</div>
                <div class="flex flex-wrap gap-2 justify-start">
                  <div 
                    v-for="sig in printModal.signatures" 
                    :key="sig.id"
                    class="border border-gray-800 p-1 text-center min-w-[120px] flex flex-col justify-between h-[100px] bg-white"
                  >
                    <div>
                      <div class="text-[7px] uppercase font-bold text-gray-500 tracking-wider">{{ sig.role_display }}</div>
                      <div class="text-[8px] font-semibold text-gray-800">{{ sig.position_name }}</div>
                    </div>
                    
                    <div class="flex-1 flex items-center justify-center py-1 h-10">
                      <template v-if="['APPROVED', 'CLOSE', 'IN_REVIEW'].includes(printModal.transaction.status) && sig.is_signed">
                        <img v-if="sig.signature_draw && sig.signature_draw.startsWith('data:image')" :src="sig.signature_draw" class="max-h-8 object-contain mx-auto" />
                        <img v-else-if="sig.signature_image" :src="sig.signature_image" class="max-h-8 object-contain mx-auto" />
                        <div v-else class="px-1 py-0 border border-green-600 rounded text-[6px] text-green-700 italic font-bold">SIGNED DIGITALLY</div>
                      </template>
                      <template v-else-if="['IN_REVIEW', 'READY_TO_PROCESS'].includes(printModal.transaction.status)">
                        <div class="text-[7px] text-gray-300 italic">(Wet Signature Area)</div>
                      </template>
                    </div>
                    
                    <div class="border-t border-gray-400 pt-0.5 text-[7px] text-gray-700">
                      <div class="font-bold truncate" :title="sig.signer_employee_name">{{ sig.signer_employee_name || sig.signer_name || '(Pending)' }}</div>
                    </div>
                  </div>
                </div>
              </div>

            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
'''
if '<!-- Print Preview Modal -->' not in content:
    content = re.sub(r'(</Panel>)', modal_html + r'\n  \1', content)

# Add CSS for print
css = '''
<style scoped>
@media print {
  body * {
    visibility: hidden;
  }
  .print-modal-overlay {
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
    background: transparent !important;
    padding: 0 !important;
    margin: 0 !important;
  }
  #print-area, #print-area * {
    visibility: visible;
  }
  #print-area {
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
    margin: 0;
    padding: 20px !important;
  }
  .print-modal-container {
    box-shadow: none !important;
    border: none !important;
    max-width: 100% !important;
    max-height: none !important;
    overflow: visible !important;
  }
  @page {
    size: A4 portrait;
    margin: 1cm;
  }
}
</style>
'''
if '@media print' not in content:
    content += css

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated GeneralJournalListView.vue")
