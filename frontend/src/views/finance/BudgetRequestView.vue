<template>
  <Panel title="Budget Request" subtitle="Finance | Budget Request">
    <div class="space-y-6">
      
      <!-- Toolbar/Search/Filter (Premium Look) -->
      <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-100 flex flex-col gap-5">
        <div class="flex flex-wrap items-center gap-4">
          
          <div class="flex items-center gap-2 text-sm bg-gray-50 px-3 py-1.5 rounded-lg border border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors">
            <input type="checkbox" v-model="filterShowAll" id="showAll" class="cursor-pointer w-4 h-4 text-bfs-navy rounded border-gray-300 focus:ring-bfs-navy" />
            <label for="showAll" class="text-gray-700 font-medium cursor-pointer">Show All</label>
          </div>

          <!-- Date Range -->
          <div class="flex items-center gap-3 text-sm">
            <span class="text-gray-500 font-semibold uppercase tracking-wide text-xs">Date Range:</span>
            <div class="flex items-center bg-gray-50 border border-gray-200 rounded-lg overflow-hidden focus-within:ring-2 focus-within:ring-bfs-navy focus-within:border-transparent transition-all shadow-sm">
              <span class="pl-3 pr-2 text-gray-400">From</span>
              <input v-model="filterDateFrom" type="date" class="bg-transparent px-2 py-1.5 text-sm focus:outline-none text-gray-700" />
              <span class="px-2 text-gray-400 border-l border-gray-200">To</span>
              <input v-model="filterDateTo" type="date" class="bg-transparent px-2 py-1.5 text-sm focus:outline-none text-gray-700" />
            </div>
          </div>

          <!-- Status Filter -->
          <div class="flex items-center gap-3 text-sm">
            <span class="text-gray-500 font-semibold uppercase tracking-wide text-xs">Status:</span>
            <select v-model="filterStatus" class="border border-gray-200 bg-gray-50 text-gray-700 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-bfs-navy transition-all shadow-sm w-48 appearance-none cursor-pointer">
              <option value="All">All</option>
              <option value="Not Paid">Not Paid</option>
              <option value="Half Paid">Half Paid</option>
              <option value="Full Paid">Full Paid</option>
              <option value="Ready To Process">Ready To Process</option>
              <option value="Ready To Pay">Ready To Pay</option>
              <option value="Approve for Payment">Approve for Payment</option>
              <option value="Close">Close</option>
            </select>
          </div>

          <!-- Due Date -->
          <div class="flex items-center gap-3 text-sm">
            <span class="text-gray-500 font-semibold uppercase tracking-wide text-xs">Due Date:</span>
            <div class="bg-gray-50 border border-gray-200 rounded-lg overflow-hidden focus-within:ring-2 focus-within:ring-bfs-navy shadow-sm transition-all">
               <input v-model="filterDueDate" type="date" class="bg-transparent px-3 py-1.5 text-sm focus:outline-none text-gray-700" />
            </div>
          </div>
        </div>

        <div class="flex flex-wrap items-center justify-between border-t border-gray-100 pt-5">
           <div class="text-sm text-gray-500">
             Manage and track your budget requests below.
           </div>
           <div class="flex items-center gap-3">
            <button
              @click="handleSearch"
              class="px-4 py-2 bg-white border border-gray-300 hover:bg-gray-50 hover:border-gray-400 hover:shadow-md text-gray-700 text-sm font-medium rounded-lg transition-all flex items-center gap-2 cursor-pointer active:scale-95"
            >
              <Search class="w-4 h-4 text-gray-500" /> Search
            </button>
            <button
              class="px-4 py-2 bg-white border border-gray-300 hover:bg-gray-50 hover:border-gray-400 hover:shadow-md text-gray-700 text-sm font-medium rounded-lg transition-all flex items-center gap-2 cursor-pointer active:scale-95"
            >
              <FileText class="w-4 h-4 text-gray-500" /> Report
            </button>
            <button
              class="px-4 py-2 bg-white border border-gray-300 hover:bg-gray-50 hover:border-gray-400 hover:shadow-md text-green-700 text-sm font-medium rounded-lg transition-all flex items-center gap-2 cursor-pointer active:scale-95"
            >
              <Download class="w-4 h-4 text-green-600" /> Export Excel
            </button>
            <button
              @click="handleSave"
              class="px-5 py-2 bg-bfs-navy hover:bg-[#1a2b4b] hover:shadow-lg hover:-translate-y-0.5 text-white text-sm font-medium rounded-lg transition-all flex items-center gap-2 cursor-pointer active:scale-95 ml-2"
            >
              <Save class="w-4 h-4" /> Save Changes
            </button>
          </div>
        </div>
      </div>

      <!-- Data Table (Premium Sleek Design) -->
      <div class="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm">
        <div class="overflow-x-auto custom-scrollbar">
          <table class="w-full text-left text-xs whitespace-nowrap min-w-max">
            <thead class="bg-gradient-to-r from-gray-50 to-gray-100 text-gray-600 font-semibold border-b border-gray-200 shadow-sm sticky top-0 z-10">
              <tr>
                <th class="px-3 py-3 border-r border-gray-200 w-12 text-center">No</th>
                <th class="px-3 py-3 border-r border-gray-200">Date</th>
                <th class="px-3 py-3 border-r border-gray-200">Payment Request No</th>
                <th class="px-3 py-3 border-r border-gray-200">Reference Number</th>
                <th class="px-3 py-3 border-r border-gray-200">Bouwheer</th>
                <th class="px-3 py-3 border-r border-gray-200">Area</th>
                <th class="px-3 py-3 border-r border-gray-200">Site</th>
                <th class="px-3 py-3 border-r border-gray-200">Category</th>
                <th class="px-3 py-3 border-r border-gray-200">Description</th>
                <th class="px-3 py-3 border-r border-gray-200 text-right">Amount In Document</th>
                <th class="px-3 py-3 border-r border-gray-200 text-right">VAT</th>
                <th class="px-3 py-3 border-r border-gray-200 text-right">Discount</th>
                <th class="px-3 py-3 border-r border-gray-200 text-center w-36">WHT</th>
                <th class="px-3 py-3 border-r border-gray-200 text-right">Total Amount</th>
                <th class="px-3 py-3 border-r border-gray-200">Payment Type</th>
                <th class="px-3 py-3 border-r border-gray-200">Term Of</th>
                <th class="px-3 py-3 border-r border-gray-200">Remark</th>
                <th class="px-3 py-3 border-r border-gray-200">PIC</th>
                <th class="px-3 py-3 border-r border-gray-200 text-right">Paid Amount</th>
                <th class="px-3 py-3 border-r border-gray-200 text-center">Currency</th>
                <th class="px-3 py-3 border-r border-gray-200 text-right bg-blue-50/50">Actual Payment</th>
                <th class="px-3 py-3 border-r border-gray-200 text-right">Remaining Unpaid</th>
                <th class="px-3 py-3 border-r border-gray-200">Due Date</th>
                <th class="px-3 py-3 border-r border-gray-200">Comment</th>
                <th class="px-3 py-3 border-r border-gray-200 text-right">Aging</th>
                <th class="px-3 py-3 border-r border-gray-200">Paid Status</th>
                <th class="px-3 py-3 border-r border-gray-200 text-center w-40">Action</th>
                <th class="px-3 py-3 text-center">Close Doc</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <template v-for="(item, index) in tableData" :key="item.id || index">
                <tr class="hover:bg-blue-50/30 transition-colors align-top group">
                  <td class="px-3 py-3 border-r border-gray-100 text-center text-gray-500 font-medium">{{ index + 1 }}</td>
                  <td class="px-3 py-3 border-r border-gray-100 text-gray-700">{{ formatDate(item.date) || '-' }}</td>
                  <td class="px-3 py-3 border-r border-gray-100 font-medium text-bfs-navy">{{ item.document_number || '-' }}</td>
                  <td class="px-3 py-3 border-r border-gray-100 text-gray-600">{{ item.po_number || item.reference_number || '-' }}</td>
                  <td class="px-3 py-3 border-r border-gray-100 text-gray-600">{{ item.vendor_display || item.payment_to_display || '-' }}</td>
                  <td class="px-3 py-3 border-r border-gray-100 text-gray-600">{{ item.project_display || item.budget_component_name || '-' }}</td>
                  <td class="px-3 py-3 border-r border-gray-100 text-gray-600">{{ item.site_name || '-' }}</td>
                  <td class="px-3 py-3 border-r border-gray-100">
                    <span class="px-2 py-1 bg-purple-100 text-purple-700 rounded-md text-[10px] font-bold tracking-wide uppercase">{{ item.transaction_type_display || item.category || '-' }}</span>
                  </td>
                  <td class="px-3 py-3 border-r border-gray-100 text-gray-600 truncate max-w-[200px]" :title="item.remarks || item.description">{{ item.remarks || item.description || '-' }}</td>
                  <td class="px-3 py-3 border-r border-gray-100 text-right font-medium text-gray-700">{{ formatNumber(item.amount) }}</td>
                  <td class="px-3 py-3 border-r border-gray-100 text-right text-gray-500">{{ formatNumber(item.vat || 0) }}</td>
                  <td class="px-3 py-3 border-r border-gray-100 text-right text-gray-500">{{ formatNumber(item.discount || 0) }}</td>
                  
                  <td class="px-2 py-2 border-r border-gray-100 align-middle">
                    <div class="flex flex-col gap-1.5 items-end bg-gray-50 p-1.5 rounded-lg border border-gray-100 group-hover:border-gray-200 transition-colors">
                      <input type="text" v-model="item.wht_amount" class="w-full bg-white border border-gray-200 rounded px-2 py-1 text-right text-xs focus:ring-1 focus:ring-bfs-navy focus:border-bfs-navy focus:outline-none transition-all shadow-sm" />
                      <select v-model="item.wht_type" class="w-full bg-white border border-gray-200 rounded px-2 py-1 text-xs focus:ring-1 focus:ring-bfs-navy focus:border-bfs-navy focus:outline-none transition-all shadow-sm text-gray-600">
                        <option value="PPh 21">PPh 21</option>
                        <option value="PPh 23">PPh 23</option>
                        <option value="PPh 4 (2) PPh Final">PPh 4 (2) PPh Final</option>
                      </select>
                    </div>
                  </td>
                  
                  <td class="px-3 py-3 border-r border-gray-100 text-right font-bold text-gray-800">{{ formatNumber(item.total_amount || item.amount) }}</td>
                  <td class="px-3 py-3 border-r border-gray-100 text-gray-600">{{ item.payment_type || '-' }}</td>
                  <td class="px-3 py-3 border-r border-gray-100 text-gray-600">
                    <span class="flex items-center gap-1 text-amber-600 bg-amber-50 px-1.5 py-0.5 rounded" v-if="item.term_duration || item.term_of"><Clock class="w-3 h-3" /> {{ item.term_duration || item.term_of }}</span>
                    <span v-else>-</span>
                  </td>
                  <td class="px-3 py-3 border-r border-gray-100 text-gray-600 whitespace-pre-line text-[11px] leading-tight">{{ item.remark || item.remarks || '-' }}</td>
                  <td class="px-3 py-3 border-r border-gray-100 text-gray-600 font-medium">{{ item.created_by_name || '-' }}</td>
                  <td class="px-3 py-3 border-r border-gray-100 text-right text-green-600 font-medium">{{ formatNumber(item.paid_amount || 0) }}</td>
                  <td class="px-3 py-3 border-r border-gray-100 text-center font-semibold text-gray-500">{{ item.currency || 'IDR' }}</td>
                  
                  <!-- Actual Payment Amount Input -->
                  <td class="px-2 py-2 border-r border-gray-100 align-middle bg-blue-50/20 group-hover:bg-blue-50/50 transition-colors">
                    <input type="text" v-model="item.actual_payment_amount" class="w-24 bg-white border border-blue-200 rounded px-2 py-1.5 text-right font-semibold text-blue-800 focus:ring-2 focus:ring-blue-400 focus:border-transparent focus:outline-none transition-all shadow-sm" />
                  </td>
                  
                  <td class="px-3 py-3 border-r border-gray-100 text-right font-bold text-red-600">{{ formatNumber(item.remaining_unpaid || item.amount) }}</td>
                  <td class="px-3 py-3 border-r border-gray-100 text-gray-700">
                    <span class="px-2 py-1 bg-gray-100 rounded text-[11px] font-medium border border-gray-200" v-if="item.due_date">{{ formatDate(item.due_date) }}</span>
                    <span v-else>-</span>
                  </td>
                  <td class="px-3 py-3 border-r border-gray-100 text-gray-600">{{ item.comment || '-' }}</td>
                  <td class="px-3 py-3 border-r border-gray-100 text-right font-medium" :class="item.aging && item.aging.includes('-') ? 'text-red-500' : 'text-green-500'">{{ item.aging || '-' }}</td>
                  
                  <td class="px-3 py-3 border-r border-gray-100">
                    <span class="px-2 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider" 
                          :class="(item.paid_status || item.document_status) === 'Not Paid' ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'">
                      {{ item.paid_status || item.document_status || 'Not Paid' }}
                    </span>
                  </td>
                  
                  <td class="px-2 py-2 border-r border-gray-100 align-middle">
                    <select v-model="item.action_status" class="w-full bg-white border border-gray-200 rounded-lg px-2 py-1.5 text-xs focus:ring-2 focus:ring-bfs-navy focus:border-transparent focus:outline-none transition-all shadow-sm text-gray-700 cursor-pointer hover:border-gray-300">
                      <option value="None">None</option>
                      <option value="Ready To Process">Ready To Process</option>
                      <option value="Ready To Pay">Ready To Pay</option>
                      <option value="Approve for Payment">Approve for Payment</option>
                    </select>
                  </td>
                  <td class="px-3 py-3 text-center align-middle">
                    <button class="px-2 py-1.5 bg-white border border-gray-300 hover:bg-red-50 hover:border-red-300 hover:text-red-600 text-gray-600 text-[10px] font-semibold rounded transition-colors shadow-sm cursor-pointer flex items-center justify-center mx-auto" title="Close Document">
                      <XCircle class="w-4 h-4" />
                    </button>
                  </td>
                </tr>
                
                <!-- Sub Total Row (Premium Look) -->
                <tr class="bg-gradient-to-r from-gray-50 to-gray-100 border-b border-gray-200">
                  <td colspan="16" class="border-r border-gray-100"></td>
                  <td class="px-3 py-2 border-r border-gray-100 bg-amber-100/50 text-amber-900 font-semibold whitespace-pre-line text-[10px] leading-tight flex items-center justify-between">
                    <span>Sub Total<br/>CHEQUE/CASH</span>
                    <CornerDownRight class="w-3 h-3 text-amber-500 opacity-50" />
                  </td>
                  <td colspan="2" class="border-r border-gray-100"></td>
                  <td class="px-3 py-2 border-r border-gray-100 bg-amber-100/50 text-center text-amber-900 font-bold">{{ item.currency || 'IDR' }}</td>
                  <td class="px-3 py-2 border-r border-gray-100 bg-amber-200/50 text-right text-amber-900 font-bold shadow-inner">{{ formatNumber(item.actual_payment_amount || 0) }}</td>
                  <td class="px-3 py-2 border-r border-gray-100 bg-amber-100/50 text-right text-red-700 font-bold">{{ formatNumber(item.remaining_unpaid || item.amount) }}</td>
                  <td colspan="6"></td>
                </tr>
              </template>
              
              <!-- Empty State -->
              <tr v-if="tableData.length === 0">
                <td colspan="28" class="px-6 py-16 text-center">
                  <div class="flex flex-col items-center justify-center gap-3">
                    <div class="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center">
                      <Inbox class="w-8 h-8 text-gray-300" />
                    </div>
                    <p class="text-gray-500 text-sm font-medium">No budget requests found for the selected criteria</p>
                    <button @click="handleSearch" class="mt-2 text-bfs-navy text-xs font-semibold hover:underline cursor-pointer">Clear filters & search again</button>
                  </div>
                </td>
              </tr>
            </tbody>
            
            <!-- Grand Total Row (Sticky Bottom) -->
            <tfoot v-if="tableData.length > 0" class="bg-white border-t-2 border-gray-200 sticky bottom-0 z-10 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)]">
              <tr>
                <td colspan="18" class="px-3 py-4 border-r border-gray-100 text-right text-gray-500 font-bold uppercase tracking-widest text-[10px]">Grand Total</td>
                <td class="px-3 py-4 border-r border-gray-100 text-right font-bold text-green-700 text-sm">{{ formatNumber(grandTotalPaidAmount) }}</td>
                <td class="px-3 py-4 border-r border-gray-100 text-center font-bold text-gray-700">IDR</td>
                <td class="px-3 py-4 border-r border-gray-100 text-right font-bold text-blue-800 text-sm bg-blue-50/30">{{ formatNumber(0) }}</td>
                <td class="px-3 py-4 border-r border-gray-100 text-right font-bold text-red-700 text-sm">{{ formatNumber(grandTotalRemainingUnpaid) }}</td>
                <td colspan="6"></td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>
    </div>
  </Panel>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import Panel from '../../components/Panel.vue'
import api from '../../services/api'
import { Search, FileText, Download, Save, Clock, CornerDownRight, XCircle, Inbox } from 'lucide-vue-next'

const getFirstDayOfMonth = () => {
  const date = new Date()
  const y = date.getFullYear()
  const m = date.getMonth()
  return new Date(y, m, 1).toLocaleDateString('en-CA')
}

const getLastDayOfMonth = () => {
  const date = new Date()
  const y = date.getFullYear()
  const m = date.getMonth()
  return new Date(y, m + 1, 0).toLocaleDateString('en-CA')
}

// Filter state
const filterShowAll = ref(false)
const filterDateFrom = ref(getFirstDayOfMonth())
const filterDateTo = ref(getLastDayOfMonth())
const filterStatus = ref('Not Paid')
const filterDueDate = ref(getLastDayOfMonth())

const tableData = ref([])

const fetchTableData = async () => {
  try {
    const response = await api.get('/accounting/cashbook-request/')
    let results = response.data.results || response.data
    
    tableData.value = results.map(item => ({
      ...item,
      wht_amount: '0.0000',
      wht_type: 'PPh 21',
      actual_payment_amount: '0.0000',
      action_status: 'None'
    }))
  } catch (error) {
    console.error('Error fetching data:', error)
  }
}

const handleSearch = () => {
  fetchTableData()
}

const handleSave = () => {
  alert('Changes saved successfully!')
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }).replace(/ /g, '-')
}

const formatNumber = (num) => {
  if (num === null || num === undefined) return '0.0000'
  return parseFloat(num).toLocaleString('en-US', { minimumFractionDigits: 4, maximumFractionDigits: 4 })
}

const grandTotalRemainingUnpaid = computed(() => {
  return tableData.value.reduce((sum, item) => sum + (parseFloat(item.remaining_unpaid || item.amount) || 0), 0)
})

const grandTotalPaidAmount = computed(() => {
  return tableData.value.reduce((sum, item) => sum + (parseFloat(item.paid_amount) || 0), 0)
})

onMounted(() => {
  fetchTableData()
})

</script>

<style scoped>
/* Custom Webkit Scrollbar for premium feel */
.custom-scrollbar::-webkit-scrollbar {
  height: 8px;
  width: 8px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: #f1f5f9; 
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #cbd5e1; 
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #94a3b8; 
}

/* Ensure date inputs look consistent across browsers */
input[type="date"]::-webkit-calendar-picker-indicator {
  cursor: pointer;
  opacity: 0.6;
  transition: 0.2s;
}
input[type="date"]::-webkit-calendar-picker-indicator:hover {
  opacity: 1;
}
</style>
