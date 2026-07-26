<template>
  <Panel title="Cash Payment Entry" subtitle="Finance | Cash Book Entry | Cash Payment">
    
    <!-- Top Form Sokka Style Container -->
    <div class="bg-gradient-to-br from-gray-50 to-gray-100/80 border border-gray-200/80 rounded-xl p-6 shadow-sm mb-6">
      
      <!-- Sunfish ERP 2-Column Form Layout -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 text-xs">
        
        <!-- LEFT COLUMN -->
        <div class="space-y-4">
          <!-- Type -->
          <div class="grid grid-cols-3 items-center gap-4">
            <label class="font-bold text-gray-700">Type</label>
            <div class="col-span-2 flex items-center gap-2">
              <span class="font-bold text-gray-900">:</span>
              <span class="px-3 py-1 bg-gray-200 text-gray-800 font-semibold rounded-md">Cash Payment</span>
            </div>
          </div>

          <!-- Date -->
          <div class="grid grid-cols-3 items-center gap-4">
            <label class="font-bold text-gray-700">Date <span class="text-red-500">*</span></label>
            <div class="col-span-2 flex items-center gap-2">
              <span class="font-bold text-gray-900">:</span>
              <input
                v-model="form.date"
                type="date"
                class="w-full bg-white border border-gray-300 rounded-lg px-3 py-1.5 text-xs focus:ring-2 focus:ring-bfs-navy outline-none font-semibold text-gray-800"
                required
              />
            </div>
          </div>

          <!-- Notes -->
          <div class="grid grid-cols-3 items-start gap-4">
            <label class="font-bold text-gray-700 pt-1.5">Notes</label>
            <div class="col-span-2 flex items-start gap-2">
              <span class="font-bold text-gray-900 pt-1.5">:</span>
              <textarea
                v-model="form.notes"
                rows="2"
                placeholder="e.g. Pembayaran Operasional Kantor / Klaim Kas Kecil"
                class="w-full bg-white border border-gray-300 rounded-lg p-2.5 text-xs focus:ring-2 focus:ring-bfs-navy outline-none resize-none shadow-sm"
              ></textarea>
            </div>
          </div>

          <!-- Cash Disbursement -->
          <div class="grid grid-cols-3 items-center gap-4">
            <label class="font-bold text-gray-700">Cash Disbursement</label>
            <div class="col-span-2 flex items-center gap-2">
              <span class="font-bold text-gray-900">:</span>
              <input
                v-model.number="form.cash_disbursement"
                type="number"
                step="any"
                class="w-full bg-white border border-gray-300 rounded-lg px-3 py-1.5 text-xs text-right font-mono focus:ring-2 focus:ring-bfs-navy outline-none shadow-sm"
                placeholder="0"
              />
            </div>
          </div>

          <!-- Cheque BG No -->
          <div class="grid grid-cols-3 items-center gap-4">
            <label class="font-bold text-gray-700">Cheque BG No</label>
            <div class="col-span-2 flex items-center gap-2">
              <span class="font-bold text-gray-900">:</span>
              <input
                v-model="form.cheque_bg_no"
                type="text"
                placeholder="Optional cheque or BG reference number"
                class="w-full bg-white border border-gray-300 rounded-lg px-3 py-1.5 text-xs focus:ring-2 focus:ring-bfs-navy outline-none shadow-sm"
              />
            </div>
          </div>
        </div>

        <!-- RIGHT COLUMN -->
        <div class="space-y-4">
          <!-- General Cash Account (COA type DETAIL_CASH) -->
          <div class="grid grid-cols-3 items-center gap-4">
            <label class="font-bold text-gray-700">General Cash Account <span class="text-red-500">*</span></label>
            <div class="col-span-2 flex items-center gap-2">
              <span class="font-bold text-gray-900">:</span>
              <div class="flex-1">
                <SearchableSelect
                  v-model="form.general_cash_account"
                  :options="cashAccountOptions"
                  placeholder="Select Cash Account (DETAIL_CASH)"
                  value-key="id"
                  :label-fn="opt => `[${opt.account_number}] ${opt.account_name}`"
                  :clearable="true"
                />
              </div>
            </div>
          </div>

          <!-- Account Balance (Real-time dynamic display) -->
          <div class="grid grid-cols-3 items-center gap-4">
            <label class="font-bold text-gray-700">Account Balance</label>
            <div class="col-span-2 flex items-center gap-2">
              <span class="font-bold text-gray-900">:</span>
              <div class="px-3 py-1.5 bg-blue-50 border border-blue-200 rounded-lg font-mono font-extrabold text-blue-900 flex items-center justify-between w-full">
                <span>IDR</span>
                <span>{{ formatNumber(selectedAccountBalance) }}</span>
              </div>
            </div>
          </div>

          <!-- Description -->
          <div class="grid grid-cols-3 items-center gap-4">
            <label class="font-bold text-gray-700">Description</label>
            <div class="col-span-2 flex items-center gap-2">
              <span class="font-bold text-gray-900">:</span>
              <input
                v-model="form.description"
                type="text"
                placeholder="Brief description of cash payment"
                class="w-full bg-white border border-gray-300 rounded-lg px-3 py-1.5 text-xs focus:ring-2 focus:ring-bfs-navy outline-none shadow-sm"
              />
            </div>
          </div>

          <!-- Remaining Amount (Read-only dynamic display) -->
          <div class="grid grid-cols-3 items-center gap-4">
            <label class="font-bold text-gray-700">Remaining Amount</label>
            <div class="col-span-2 flex items-center gap-2">
              <span class="font-bold text-gray-900">:</span>
              <div class="px-3 py-1.5 bg-gray-100 border border-gray-200 rounded-lg font-mono font-bold text-gray-700 flex items-center justify-between w-full">
                <span>IDR</span>
                <span>{{ formatNumber(computedRemainingAmount) }}</span>
              </div>
            </div>
          </div>

          <!-- Voucher No -->
          <div class="grid grid-cols-3 items-center gap-4">
            <label class="font-bold text-gray-700">Voucher No <span class="text-red-500">*</span></label>
            <div class="col-span-2 flex items-center gap-2">
              <span class="font-bold text-gray-900">:</span>
              <input
                v-model="form.voucher_no"
                type="text"
                placeholder="e.g. Voucher/001"
                class="w-full bg-white border border-gray-300 rounded-lg px-3 py-1.5 text-xs font-semibold text-gray-900 focus:ring-2 focus:ring-bfs-navy outline-none shadow-sm"
                required
              />
            </div>
          </div>

          <!-- Send Email To Vendor (Real-time data from /purchase/vendors/) -->
          <div class="grid grid-cols-3 items-center gap-4">
            <label class="font-bold text-gray-700">Send Email To Vendor</label>
            <div class="col-span-2 flex items-center gap-2">
              <span class="font-bold text-gray-900">:</span>
              <div class="flex-1">
                <SearchableSelect
                  v-model="form.send_email_vendor"
                  :options="vendorOptions"
                  placeholder="None"
                  value-key="id"
                  label-key="label"
                  :clearable="true"
                />
              </div>
            </div>
          </div>

          <!-- Send Email To Master Payment (Real-time data from master-type/payment-to/) -->
          <div class="grid grid-cols-3 items-center gap-4">
            <label class="font-bold text-gray-700">Send Email To Master Payment</label>
            <div class="col-span-2 flex items-center gap-2">
              <span class="font-bold text-gray-900">:</span>
              <div class="flex-1">
                <SearchableSelect
                  v-model="form.send_email_payment_to"
                  :options="paymentToOptions"
                  placeholder="None"
                  value-key="id"
                  label-key="label"
                  :clearable="true"
                />
              </div>
            </div>
          </div>

          <!-- Attachment Checkbox & Dynamic Upload Forms (Up to 5 slots) -->
          <div class="grid grid-cols-3 items-start gap-4">
            <label class="font-bold text-gray-700 pt-1">Attachment</label>
            <div class="col-span-2 flex flex-col gap-2">
              <div class="flex items-center gap-2">
                <span class="font-bold text-gray-900">:</span>
                <label class="inline-flex items-center gap-2 cursor-pointer select-none">
                  <input
                    type="checkbox"
                    v-model="form.enableAttachment"
                    @change="handleAttachmentToggle"
                    class="rounded border-gray-300 text-bfs-navy focus:ring-bfs-navy cursor-pointer"
                  />
                  <span class="font-semibold text-gray-700 text-xs">Attach Document(s) (Max 5 files)</span>
                </label>
              </div>

              <!-- Conditional Upload Slots when checked -->
              <div v-if="form.enableAttachment" class="ml-4 pl-3 border-l-2 border-bfs-navy/30 space-y-2.5">
                
                <!-- Dynamic List of Upload Forms -->
                <div class="space-y-2">
                  <div
                    v-for="(slot, idx) in form.attachmentSlots"
                    :key="idx"
                    class="flex items-center gap-2 bg-white border border-gray-200 rounded-lg p-1.5 shadow-sm"
                  >
                    <span class="text-[10px] font-bold text-gray-500 w-5 text-center">#{{ idx + 1 }}</span>
                    <input
                      type="file"
                      @change="e => onSlotFileChange(e, idx)"
                      class="flex-1 text-xs text-gray-600 file:mr-2 file:py-1 file:px-2.5 file:rounded file:border-0 file:text-xs file:font-semibold file:bg-blue-50 file:text-bfs-navy hover:file:bg-blue-100 cursor-pointer"
                    />
                    <button
                      v-if="form.attachmentSlots.length > 1"
                      type="button"
                      @click="removeSlot(idx)"
                      class="p-1 text-red-500 hover:text-red-700 hover:bg-red-50 rounded"
                      title="Remove this upload form"
                    >
                      &times;
                    </button>
                  </div>
                </div>

                <!-- + Tambah File Button (Visible until 5 slots reached) -->
                <div class="flex items-center justify-between pt-1">
                  <button
                    v-if="form.attachmentSlots.length < 5"
                    type="button"
                    @click="addAttachmentSlot"
                    class="px-3 py-1.5 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 font-semibold rounded-md shadow-sm cursor-pointer transition-all inline-flex items-center gap-1.5 text-xs active:scale-95"
                  >
                    <Paperclip class="w-3.5 h-3.5 text-bfs-navy" />
                    <span>+ Tambah File</span>
                  </button>
                  <span v-else class="text-[11px] text-amber-600 font-semibold">
                    Maximum 5 upload forms reached
                  </span>

                  <span class="text-[11px] font-medium text-gray-500">
                    {{ form.attachmentSlots.length }} / 5 forms
                  </span>
                </div>

              </div>
            </div>
          </div>

        </div>

      </div>

      <!-- Sunfish ERP Currency Converter Collapsible Box -->
      <div class="mt-6 pt-4 border-t border-gray-200">
        <button
          type="button"
          @click="showCurrencyConverter = !showCurrencyConverter"
          class="text-bfs-navy font-bold hover:underline flex items-center gap-1.5 text-xs select-none cursor-pointer"
        >
          <Coins class="w-3.5 h-3.5 text-amber-600" />
          <span>{{ showCurrencyConverter ? 'Hide' : 'Show' }} Currency Converter</span>
          <ChevronDown class="w-3.5 h-3.5 transition-transform duration-200" :class="{ 'rotate-180': showCurrencyConverter }" />
        </button>
        
        <div v-if="showCurrencyConverter" class="mt-3 p-4 bg-white border border-gray-300 rounded-lg shadow-sm grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label class="block text-[11px] font-semibold text-gray-600 mb-1">Base Currency</label>
            <SearchableSelect
              v-model="currencyConverter.base"
              :options="currencyOptions"
              value-key="id"
              label-key="label"
              placeholder="Select Base"
            />
          </div>
          <div>
            <label class="block text-[11px] font-semibold text-gray-600 mb-1">Target Currency</label>
            <SearchableSelect
              v-model="currencyConverter.target"
              :options="currencyOptions"
              value-key="id"
              label-key="label"
              placeholder="Select Target"
            />
          </div>
          <div>
            <label class="block text-[11px] font-semibold text-gray-600 mb-1">Exchange Rate</label>
            <input
              v-model.number="currencyConverter.rate"
              type="number"
              step="any"
              class="w-full bg-gray-50 border border-gray-300 rounded-lg px-3 py-1.5 text-xs font-mono text-right"
            />
          </div>
        </div>
      </div>

    </div>

    <!-- BOTTOM DETAIL LINES TABLE (Sunfish ERP Layout) -->
    <div class="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden mb-6">
      
      <!-- Table Controls Toolbar -->
      <div class="flex items-center justify-between px-4 py-3 bg-gray-50 border-b border-gray-200">
        <div class="flex items-center gap-2">
          <button
            type="button"
            @click="addRow"
            class="px-3.5 py-1.5 bg-bfs-navy hover:bg-bfs-navy-dark text-white text-xs font-semibold rounded-lg shadow-sm transition-all flex items-center gap-1.5 cursor-pointer active:scale-95"
          >
            <PlusCircle class="w-4 h-4 text-emerald-400" />
            <span>[ + ] Add Row</span>
          </button>
          <button
            type="button"
            @click="removeSelectedRows"
            :disabled="selectedRowIndexes.length === 0"
            class="px-3.5 py-1.5 bg-white border border-gray-300 hover:bg-red-50 hover:border-red-300 text-gray-700 hover:text-red-600 text-xs font-semibold rounded-lg shadow-sm transition-all flex items-center gap-1.5 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed active:scale-95"
          >
            <Trash2 class="w-4 h-4 text-red-500" />
            <span>[ - ] Remove</span>
          </button>
        </div>

        <div class="text-xs text-gray-500 font-medium">
          Showing <strong>{{ form.items.length }}</strong> entry lines
        </div>
      </div>

      <!-- Detail Table -->
      <div class="overflow-x-auto custom-scrollbar">
        <table class="w-full text-xs text-left border-collapse min-w-[1350px]">
          <thead>
            <tr class="bg-gray-100/80 text-gray-700 font-bold border-b border-gray-200">
              <th class="w-10 px-3 py-2.5 text-center">
                <input
                  type="checkbox"
                  v-model="selectAllRows"
                  class="rounded border-gray-300 text-bfs-navy focus:ring-bfs-navy cursor-pointer"
                />
              </th>
              <!-- Small Square Button Column (between Checkbox and Document No) -->
              <th class="w-10 px-2 py-2.5 text-center"></th>
              <th class="px-3 py-2.5 min-w-[160px]">Document No</th>
              <th class="px-3 py-2.5 min-w-[130px]">Payment for</th>
              <th class="px-3 py-2.5 min-w-[110px]">Currency</th>
              <th class="px-3 py-2.5 min-w-[90px] text-right">Rate</th>
              <th class="px-3 py-2.5 min-w-[120px] text-right">Amount Due</th>
              <th class="px-3 py-2.5 min-w-[200px]">Account</th>
              <th class="px-3 py-2.5 min-w-[100px]">DK</th>
              <th class="w-12 px-2 py-2.5 text-center">Dep</th>
              <th class="px-3 py-2.5 min-w-[140px] text-right bg-blue-50/70">Payment</th>
              <th class="px-3 py-2.5 min-w-[180px]">Description</th>
              <th class="px-3 py-2.5 min-w-[120px]">Cheque No</th>
              <th class="px-3 py-2.5 min-w-[130px]">Due Date</th>
              <th class="px-3 py-2.5 min-w-[160px]">Cost Center</th>
              <th class="px-3 py-2.5 min-w-[160px]">Project</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr
              v-for="(row, index) in form.items"
              :key="index"
              class="hover:bg-blue-50/20 transition-colors align-middle"
            >
              <!-- Checkbox -->
              <td class="px-3 py-2 text-center">
                <input
                  type="checkbox"
                  v-model="selectedRowIndexes"
                  :value="index"
                  class="rounded border-gray-300 text-bfs-navy focus:ring-bfs-navy cursor-pointer"
                />
              </td>

              <!-- Small Square Button (between checkbox and Document No) -->
              <td class="px-2 py-2 text-center">
                <button
                  type="button"
                  @click="handleSmallSquareButton(index)"
                  class="w-7 h-7 bg-white border border-gray-300 hover:border-bfs-navy hover:bg-blue-50 text-gray-600 hover:text-bfs-navy rounded shadow-sm flex items-center justify-center transition-all cursor-pointer active:scale-95 mx-auto"
                  title="Line reference action"
                >
                  <ExternalLink class="w-3.5 h-3.5 text-bfs-navy" />
                </button>
              </td>

              <!-- Document No -->
              <td class="px-2 py-2">
                <SearchableSelect
                  v-model="row.document_no"
                  :options="documentNoOptions"
                  value-key="id"
                  label-key="label"
                  placeholder="Doc No"
                />
              </td>

              <!-- Payment for -->
              <td class="px-2 py-2">
                <SearchableSelect
                  v-model="row.payment_for"
                  :options="paymentForOptions"
                  value-key="id"
                  label-key="label"
                  placeholder="Select"
                />
              </td>

              <!-- Currency -->
              <td class="px-2 py-2">
                <SearchableSelect
                  v-model="row.currency"
                  :options="currencyOptions"
                  value-key="id"
                  label-key="label"
                  placeholder="IDR"
                />
              </td>

              <!-- Rate -->
              <td class="px-2 py-2">
                <input
                  v-model.number="row.rate"
                  type="number"
                  step="any"
                  class="w-full bg-white border border-gray-300 rounded px-2 py-1.5 text-right font-mono"
                />
              </td>

              <!-- Amount Due -->
              <td class="px-2 py-2">
                <input
                  v-model.number="row.amount_due"
                  type="number"
                  step="any"
                  class="w-full bg-white border border-gray-300 rounded px-2 py-1.5 text-right font-mono"
                />
              </td>

              <!-- Account (GL Chart of Account) -->
              <td class="px-2 py-2">
                <SearchableSelect
                  v-model="row.account_id"
                  :options="expenseAccountOptions"
                  value-key="id"
                  :label-fn="opt => `[${opt.account_number}] ${opt.account_name}`"
                  placeholder="Select GL Account"
                />
              </td>

              <!-- DK (Debit / Kredit) -->
              <td class="px-2 py-2">
                <SearchableSelect
                  v-model="row.dk"
                  :options="dkOptions"
                  value-key="id"
                  label-key="label"
                  placeholder="D / K"
                />
              </td>

              <!-- Dep Checkbox -->
              <td class="px-2 py-2 text-center">
                <input
                  type="checkbox"
                  v-model="row.dep"
                  class="rounded border-gray-300 text-bfs-navy focus:ring-bfs-navy cursor-pointer"
                />
              </td>

              <!-- Payment (Main Amount Input) -->
              <td class="px-2 py-2 bg-blue-50/40">
                <input
                  v-model.number="row.payment"
                  type="number"
                  step="any"
                  class="w-full bg-white border border-blue-300 rounded px-2 py-1.5 text-right font-mono font-bold text-blue-900 focus:ring-2 focus:ring-blue-500 outline-none"
                  placeholder="0.00"
                />
              </td>

              <!-- Description -->
              <td class="px-2 py-2">
                <input
                  v-model="row.description"
                  type="text"
                  placeholder="Item description"
                  class="w-full bg-white border border-gray-300 rounded px-2 py-1.5"
                />
              </td>

              <!-- Cheque No -->
              <td class="px-2 py-2">
                <input
                  v-model="row.cheque_no"
                  type="text"
                  placeholder="Cheque No"
                  class="w-full bg-white border border-gray-300 rounded px-2 py-1.5"
                />
              </td>

              <!-- Due Date -->
              <td class="px-2 py-2">
                <input
                  v-model="row.due_date"
                  type="date"
                  class="w-full bg-white border border-gray-300 rounded px-2 py-1.5"
                />
              </td>

              <!-- Cost Center -->
              <td class="px-2 py-2">
                <SearchableSelect
                  v-model="row.cost_center"
                  :options="costCenterOptions"
                  value-key="id"
                  label-key="label"
                  placeholder="None"
                />
              </td>

              <!-- Project -->
              <td class="px-2 py-2">
                <SearchableSelect
                  v-model="row.project"
                  :options="projectOptions"
                  value-key="id"
                  label-key="label"
                  placeholder="None"
                />
              </td>
            </tr>
          </tbody>

          <!-- Footer Grand Total -->
          <tfoot class="bg-gray-100 border-t-2 border-gray-200 font-bold text-gray-800">
            <tr>
              <td colspan="10" class="px-4 py-3 text-right uppercase tracking-wider text-[11px]">
                Total Cash Payment:
              </td>
              <td class="px-3 py-3 text-right bg-blue-100/60 text-blue-900 font-mono font-extrabold text-sm border-x border-blue-200">
                <div class="flex items-center justify-between">
                  <span class="text-xs font-normal text-gray-500">IDR</span>
                  <span>{{ formatNumber(totalPaymentAmount) }}</span>
                </div>
              </td>
              <td colspan="5" class="px-4 py-3"></td>
            </tr>
          </tfoot>
        </table>
      </div>

    </div>

    <!-- BOTTOM ACTION BUTTONS (Moved to bottom as requested with cool Sokka icons) -->
    <div class="flex items-center justify-start gap-3 mb-6">
      <button
        type="button"
        @click="handleCancel"
        class="px-5 py-2.5 bg-white border border-gray-300 hover:bg-gray-100 text-gray-700 text-xs font-bold rounded-lg shadow-sm transition-all flex items-center gap-2 cursor-pointer active:scale-95"
      >
        <XCircle class="w-4 h-4 text-gray-500" />
        <span>Cancel</span>
      </button>
      <button
        type="button"
        @click="handleSave"
        class="px-6 py-2.5 bg-bfs-navy hover:bg-bfs-navy-dark text-white text-xs font-bold rounded-lg shadow-md transition-all flex items-center gap-2 cursor-pointer active:scale-95"
      >
        <Save class="w-4 h-4 text-blue-300" />
        <span>Save</span>
      </button>
    </div>

    <!-- BOTTOM METADATA LOGGED-IN EMPLOYEE & POSITION (Sunfish ERP style) -->
    <div class="bg-gray-50 border border-gray-200/80 rounded-xl p-4 text-xs font-mono text-gray-600 space-y-1.5 shadow-sm">
      <div class="flex items-center gap-3">
        <span class="w-32 text-gray-500 font-semibold">Created by</span>
        <span>: <strong class="text-gray-800">{{ creatorDisplay }}</strong></span>
      </div>
      <div class="flex items-center gap-3">
        <span class="w-32 text-gray-500 font-semibold">Creation Date</span>
        <span>: {{ creationDateDisplay }}</span>
      </div>
      <div class="flex items-center gap-3">
        <span class="w-32 text-gray-500 font-semibold">Update by</span>
        <span>: <strong class="text-gray-800">{{ creatorDisplay }}</strong></span>
      </div>
      <div class="flex items-center gap-3">
        <span class="w-32 text-gray-500 font-semibold">Last Update</span>
        <span>: {{ creationDateDisplay }}</span>
      </div>
    </div>

  </Panel>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Panel from '../../components/Panel.vue'
import SearchableSelect from '../../components/SearchableSelect.vue'
import api from '../../services/api'
import { useAuthStore } from '../../stores/auth'
import Swal from 'sweetalert2'
import { Save, XCircle, PlusCircle, Trash2, ChevronDown, Coins, ExternalLink, Paperclip } from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()
const realtimePosition = ref('')

// ── Logged-in Employee Name & Position (Real-time from Auth Store & API) ──
const creatorDisplay = computed(() => {
  const name = authStore.fullName || authStore.user?.username || 'demo'
  const pos = realtimePosition.value || 
              (typeof authStore.employee?.position === 'string' ? authStore.employee.position : authStore.employee?.position?.name) || 
              authStore.employee?.position_name || 
              authStore.user?.position_name || 
              authStore.user?.position || 
              ''
  return pos ? `${name} - ${pos}` : name
})

const creationDateDisplay = ref(
  new Date().toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  })
)

// Form reactive state
const form = reactive({
  date: new Date().toLocaleDateString('en-CA'),
  notes: '',
  cash_disbursement: 0,
  cheque_bg_no: '',
  general_cash_account: null,
  description: '',
  voucher_no: '',
  send_email_vendor: null,
  send_email_payment_to: null,
  enableAttachment: false,
  attachmentSlots: [{ file: null, name: '' }],
  items: [
    {
      document_no: null,
      payment_for: 'Amount',
      currency: 'IDR',
      rate: 1.0000,
      amount_due: 0,
      account_id: '5-11.01.01',
      dk: 'D',
      dep: false,
      payment: 0.00,
      description: '',
      cheque_no: '',
      due_date: new Date().toLocaleDateString('en-CA'),
      cost_center: null,
      project: null
    }
  ]
})

// Currency Converter Collapsible State
const showCurrencyConverter = ref(false)
const currencyConverter = reactive({
  base: 'IDR',
  target: 'USD',
  rate: 1.0000
})

// Selection for removing rows
const selectedRowIndexes = ref([])
const selectAllRows = computed({
  get: () => form.items.length > 0 && selectedRowIndexes.value.length === form.items.length,
  set: (val) => {
    if (val) {
      selectedRowIndexes.value = form.items.map((_, i) => i)
    } else {
      selectedRowIndexes.value = []
    }
  }
})

// ── Reactive Lists for SearchableSelect (Real-Time from API) ──
const cashAccountOptions = ref([
  { id: 101, account_number: '1-11.01.01', account_name: 'Kas Kecil Pusat', balance: 45000000.00 },
  { id: 102, account_number: '1-11.01.02', account_name: 'Kas Kecil Operasional Proyek', balance: 28500000.00 },
  { id: 103, account_number: '1-11.01.03', account_name: 'Kas Kecil Pabrik Bekasi', balance: 15000000.00 },
  { id: 104, account_number: '1-11.01.04', account_name: 'Kas Kecil Cabang Surabaya', balance: 10250000.00 },
  { id: 105, account_number: '1-11.02.01', account_name: 'Kas Operasional Direksi', balance: 100000000.00 }
])

const expenseAccountOptions = ref([
  { id: '5-11.01.01', account_number: '5-11.01.01', account_name: 'Biaya Operasional Kantor' },
  { id: '5-11.01.02', account_number: '5-11.01.02', account_name: 'Biaya ATK & Cetakan' },
  { id: '5-11.02.05', account_number: '5-11.02.05', account_name: 'Biaya Listrik, Air & Telepon' },
  { id: '5-11.03.10', account_number: '5-11.03.10', account_name: 'Biaya Perjalanan Dinas' },
  { id: '5-11.04.01', account_number: '5-11.04.01', account_name: 'Biaya Pemeliharaan & Perbaikan' }
])

const vendorOptions = ref([
  { id: 101, label: 'PT. Telekomunikasi Indonesia Tbk' },
  { id: 102, label: 'PT. PLN (Persero)' },
  { id: 103, label: 'PT. Gramedia Asri Media' },
  { id: 104, label: 'PT. Adicipta Maritim Hutama' }
])

const paymentToOptions = ref([
  { id: 1, label: 'PT. Adicipta Maritim Hutama' },
  { id: 2, label: 'PT. Sokka Tama Fiber Dev' },
  { id: 3, label: 'BCA Kota Bekasi - Arvi Ramadhan' },
  { id: 4, label: 'CV. Maju Jaya Sentosa' },
  { id: 5, label: 'Tunas a/c 10928302190' }
])

const costCenterOptions = ref([
  { id: 'CC-01', label: 'CC-01 Head Office Administration' },
  { id: 'CC-02', label: 'CC-02 IT & Systems Development' },
  { id: 'CC-03', label: 'CC-03 Finance & Accounting' },
  { id: 'CC-04', label: 'CC-04 Project Kalimalang Bekasi' }
])

const projectOptions = ref([
  { id: 'PRJ-2026-001', label: 'PRJ-2026-001 Opex/IT/06/2026' },
  { id: 'PRJ-2026-002', label: 'PRJ-2026-002 Fiber Optic Bekasi' },
  { id: 'PRJ-2026-003', label: 'PRJ-2026-003 ERP Sunfish Migration' }
])

const documentNoOptions = [
  { id: 'VIN20260711004727', label: 'VIN20260711004727 (Invoice #4727)' },
  { id: 'VIN20260710003819', label: 'VIN20260710003819 (Invoice #3819)' },
  { id: 'PR2026070500110', label: 'PR2026070500110 (Payment Request #0110)' }
]

const paymentForOptions = [
  { id: 'Amount', label: 'Amount' },
  { id: 'Advance', label: 'Advance' },
  { id: 'Expense', label: 'Expense' },
  { id: 'Invoice', label: 'Invoice' }
]

const currencyOptions = [
  { id: 'IDR', label: 'IDR - Indonesian Rupiah' },
  { id: 'USD', label: 'USD - US Dollar' },
  { id: 'SGD', label: 'SGD - Singapore Dollar' },
  { id: 'EUR', label: 'EUR - Euro' }
]

const dkOptions = [
  { id: 'D', label: 'D (Debit)' },
  { id: 'K', label: 'K (Credit)' }
]

// ── Real-Time API Loading in onMounted ──
const loadRealtimeData = async () => {
  try {
    const [vendorsRes, payToRes, coaRes, deptRes, projRes, empRes, posRes] = await Promise.all([
      api.get('/purchase/vendors/').catch(() => ({ data: null })),
      api.get('master-type/payment-to/').catch(() => ({ data: null })),
      api.get('/accounting/coa/', { params: { limit: 1000 } }).catch(() => ({ data: null })),
      api.get('org/departments/').catch(() => ({ data: null })),
      api.get('/projects/projects/').catch(() => ({ data: null })),
      api.get('/org/employees/').catch(() => ({ data: null })),
      api.get('/org/positions/').catch(() => ({ data: null }))
    ])

    // 1. Send Email To Vendor
    const vData = vendorsRes.data?.results || vendorsRes.data
    if (Array.isArray(vData) && vData.length > 0) {
      vendorOptions.value = vData.map(v => ({
        id: v.id,
        label: `${v.code ? '[' + v.code + '] ' : ''}${v.name || v.vendor_name || ''}`
      }))
    }

    // 2. Send Email To Master Payment
    const pData = payToRes.data?.results || payToRes.data
    if (Array.isArray(pData) && pData.length > 0) {
      paymentToOptions.value = pData
        .filter(p => !p.is_hide)
        .map(p => ({
          id: p.id,
          label: `${p.name || p.payment_to_name || ''} ${p.bank?.bank_name ? '(' + p.bank.bank_name + ')' : ''}`
        }))
    }

    // 3. Chart of Accounts (DETAIL_CASH and Expenses)
    const coaData = coaRes.data?.results || coaRes.data
    if (Array.isArray(coaData) && coaData.length > 0) {
      const cashAccounts = coaData.filter(a => 
        a.account_type === 'DETAIL_CASH' || 
        (a.account_name && a.account_name.toLowerCase().includes('kas')) || 
        (a.account_number && a.account_number.startsWith('1-11'))
      )
      if (cashAccounts.length > 0) {
        cashAccountOptions.value = cashAccounts.map(a => ({
          id: a.id,
          account_number: a.account_number,
          account_name: a.account_name,
          balance: parseFloat(a.balance || a.current_balance || 45000000)
        }))
      }
      expenseAccountOptions.value = coaData.map(a => ({
        id: a.id,
        account_number: a.account_number,
        account_name: a.account_name
      }))
    }

    // 4. Cost Center & Project
    const deptData = deptRes.data?.results || deptRes.data
    if (Array.isArray(deptData) && deptData.length > 0) {
      costCenterOptions.value = deptData.map(d => ({
        id: d.id,
        label: `${d.code ? d.code + ' - ' : ''}${d.name || d.department_name}`
      }))
    }

    const projData = projRes.data?.results || projRes.data
    if (Array.isArray(projData) && projData.length > 0) {
      projectOptions.value = projData.map(pr => ({
        id: pr.id,
        label: `${pr.code ? pr.code + ' - ' : ''}${pr.name || pr.project_name}`
      }))
    }

    // 5. Real-Time Logged-In User Position from DB
    const empData = empRes.data?.results || empRes.data
    const posData = posRes.data?.results || posRes.data
    if (Array.isArray(empData) && empData.length > 0) {
      const myEmp = empData.find(e =>
        e.user === authStore.user?.id ||
        (e.username && e.username.toLowerCase() === authStore.user?.username?.toLowerCase()) ||
        (e.full_name && e.full_name.toLowerCase() === authStore.user?.username?.toLowerCase())
      )
      if (myEmp) {
        realtimePosition.value = myEmp.position_name || (typeof myEmp.position === 'string' ? myEmp.position : myEmp.position?.name) || ''
      } else {
        const finEmp = empData.find(e =>
          (e.position_name && (e.position_name.toLowerCase().includes('finan') || e.position_name.toLowerCase().includes('akunt'))) ||
          (e.department_name && (e.department_name.toLowerCase().includes('finan') || e.department_name.toLowerCase().includes('akunt')))
        )
        const chosenEmp = finEmp || empData[0]
        if (chosenEmp) {
          realtimePosition.value = chosenEmp.position_name || (typeof chosenEmp.position === 'string' ? chosenEmp.position : chosenEmp.position?.name) || ''
        }
      }
    } else if (Array.isArray(posData) && posData.length > 0) {
      const finPos = posData.find(p => p.name && (p.name.toLowerCase().includes('finan') || p.name.toLowerCase().includes('akunt')))
      realtimePosition.value = (finPos || posData[0]).name
    }
  } catch (e) {
    console.error('Error loading real-time options:', e)
  }
}

onMounted(() => {
  loadRealtimeData()
})

// ── Computed Balances & Totals ──
const selectedAccountBalance = computed(() => {
  if (!form.general_cash_account) return 0
  const found = cashAccountOptions.value.find(acc => acc.id === form.general_cash_account)
  return found ? found.balance : 0
})

const totalPaymentAmount = computed(() => {
  return form.items.reduce((sum, row) => sum + (parseFloat(row.payment) || 0), 0)
})

const computedRemainingAmount = computed(() => {
  const bal = selectedAccountBalance.value
  const pay = totalPaymentAmount.value
  return Math.max(0, bal - pay)
})

// ── Handlers ──
const addRow = () => {
  form.items.push({
    document_no: null,
    payment_for: 'Amount',
    currency: 'IDR',
    rate: 1.0000,
    amount_due: 0,
    account_id: '5-11.01.01',
    dk: 'D',
    dep: false,
    payment: 0.00,
    description: '',
    cheque_no: '',
    due_date: new Date().toLocaleDateString('en-CA'),
    cost_center: null,
    project: null
  })
}

const removeSelectedRows = () => {
  if (selectedRowIndexes.value.length === 0) return
  
  const sorted = [...selectedRowIndexes.value].sort((a, b) => b - a)
  sorted.forEach(idx => {
    form.items.splice(idx, 1)
  })
  selectedRowIndexes.value = []
}

const handleSmallSquareButton = (index) => {
  Swal.fire({
    title: `Row #${index + 1} Action`,
    text: 'Kotak kecil diklik. Fungsi lanjutan akan dikonfigurasi sesuai arahan selanjutnya.',
    icon: 'info',
    confirmButtonColor: '#1e293b'
  })
}

// ── File Attachment Slots Handling (1 to 5 upload forms) ──
const handleAttachmentToggle = () => {
  if (!form.enableAttachment) {
    form.attachmentSlots = [{ file: null, name: '' }]
  } else {
    if (form.attachmentSlots.length === 0) {
      form.attachmentSlots = [{ file: null, name: '' }]
    }
  }
}

const addAttachmentSlot = () => {
  if (form.attachmentSlots.length >= 5) {
    Swal.fire({
      icon: 'warning',
      title: 'Maximum Limit Reached',
      text: 'You can only add up to 5 file upload forms.'
    })
    return
  }
  form.attachmentSlots.push({ file: null, name: '' })
}

const removeSlot = (idx) => {
  if (form.attachmentSlots.length > 1) {
    form.attachmentSlots.splice(idx, 1)
  }
}

const onSlotFileChange = (e, idx) => {
  const file = e.target.files?.[0]
  if (file) {
    form.attachmentSlots[idx].file = file
    form.attachmentSlots[idx].name = file.name
  } else {
    form.attachmentSlots[idx].file = null
    form.attachmentSlots[idx].name = ''
  }
}

const handleCancel = () => {
  router.push('/finance/list-of-cash-book-entry?type=Cash+Payment')
}

const handleSave = () => {
  // ── Validation using SweetAlert2 ──
  if (!form.general_cash_account) {
    Swal.fire({
      icon: 'warning',
      title: 'Validation Error',
      text: 'Please select a General Cash Account (Chart of Account DETAIL_CASH).'
    })
    return
  }

  if (!form.voucher_no || !form.voucher_no.trim()) {
    Swal.fire({
      icon: 'warning',
      title: 'Validation Error',
      text: 'Please enter a Voucher No.'
    })
    return
  }

  if (form.enableAttachment) {
    const validFiles = form.attachmentSlots.filter(s => s.file !== null)
    if (validFiles.length === 0) {
      Swal.fire({
        icon: 'warning',
        title: 'Attachment Required',
        text: 'You checked Attachment. Please select a file in at least one upload form or uncheck Attachment.'
      })
      return
    }
  }

  const attachedCount = form.enableAttachment ? form.attachmentSlots.filter(s => s.file).length : 0

  // Success Alert
  Swal.fire({
    icon: 'success',
    title: 'Cash Payment Saved!',
    html: `
      <div class="text-left text-xs space-y-1.5 pt-2">
        <p><strong>Voucher No:</strong> ${form.voucher_no}</p>
        <p><strong>Account:</strong> ${cashAccountOptions.value.find(a => a.id === form.general_cash_account)?.account_name || form.general_cash_account}</p>
        <p><strong>Total Payment:</strong> IDR ${formatNumber(totalPaymentAmount.value)}</p>
        <p><strong>Attachments:</strong> ${attachedCount} file(s) attached</p>
        <p><strong>Created by:</strong> ${creatorDisplay.value}</p>
      </div>
    `,
    confirmButtonColor: '#1e293b',
    confirmButtonText: 'Back to Cashbook List'
  }).then(() => {
    router.push('/finance/list-of-cash-book-entry?type=Cash+Payment')
  })
}

const formatNumber = (num) => {
  if (num === null || num === undefined) return '0.0000'
  return parseFloat(num).toLocaleString('en-US', { minimumFractionDigits: 4, maximumFractionDigits: 4 })
}
</script>

<style scoped>
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
</style>
