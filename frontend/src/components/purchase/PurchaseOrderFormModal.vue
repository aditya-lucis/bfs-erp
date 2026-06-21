<template>

      <Transition name="modal">
        <div v-if="props.show" class="fixed inset-0 z-50 overflow-y-auto">
          <div class="fixed inset-0 bg-black/40" @click="closeModal" />
          <div class="flex min-h-full items-start justify-center p-4 py-8">
            <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-6xl z-10" @click.stop>
              
              <!-- Modal Header -->
              <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
                <div>
                  <h3 class="text-base font-bold text-gray-800">
                    {{ props.mode === 'add' ? 'Purchase Order | Add' : 'Purchase Order | Edit' }}
                  </h3>
                  <p v-if="props.mode === 'edit'" class="text-xs text-gray-500 font-mono">
                    PO Number: {{ form.po_number }}
                  </p>
                </div>
                <button @click="closeModal" class="text-gray-400 hover:text-gray-600">
                  <X class="w-5 h-5" />
                </button>
              </div>

              <!-- Form Error Alert -->
              <div v-if="formError" class="mx-6 mt-4 px-4 py-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
                <AlertCircle class="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
                <p class="text-sm text-red-600">{{ formError }}</p>
              </div>

              
              <div class="px-6 py-4 space-y-6">
                <!-- Header Fields Grid -->
                  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 bg-white p-4 rounded-xl border border-gray-200 shadow-sm mb-6">
                    <!-- Row 1: Project, RAP, Requestor Department -->
                    <FormField label="Project" required>
                      <SearchableSelect
                        v-model="form.project"
                        :options="availableProjects"
                        value-key="id"
                        label-key="project_name"
                        placeholder="— Select Project —"
                        @change="onProjectChange"
                        :disabled="props.mode === 'edit'"
                      />
                    </FormField>
                    
                    <FormField label="RAP" required>
                      <SearchableSelect
                        v-model="form.rap"
                        :options="availableRaps"
                        value-key="id"
                        label-key="rap_number"
                        placeholder="— Select RAP —"
                        :disabled="props.mode === 'edit' || !form.project"
                      />
                    </FormField>

                    <FormField label="Requestor Department" required>
                      <SearchableSelect
                        v-model="form.department"
                        :options="availableDepartments"
                        value-key="id"
                        label-key="name"
                        placeholder="— Select Department —"
                        :disabled="props.mode === 'edit' || !authStore.isSuperuser"
                      />
                    </FormField>

                    <!-- Row 2: Vendor, ETD, PO Date -->
                    <FormField label="Vendor" required>
                      <SearchableSelect
                        v-model="form.vendor"
                        :options="availableVendors"
                        value-key="id"
                        label-key="name"
                        placeholder="— Select Vendor —"
                        :disabled="props.mode === 'edit'"
                      />
                    </FormField>

                    <FormField label="Estimated Date (ETD)">
                      <input v-model="form.etd" type="date" class="w-full px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-1 focus:ring-bfs-navy focus:border-bfs-navy bg-white text-gray-900" />
                    </FormField>
                    
                    <FormField label="PO Date" required>
                      <input v-model="form.po_date" type="date" required class="w-full px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-1 focus:ring-bfs-navy focus:border-bfs-navy bg-white text-gray-900" />
                    </FormField>

                    <!-- Row 3: Purchase Requisition [Pick] -->
                    <div class="col-span-1 lg:col-span-3 border border-yellow-400 bg-yellow-50 p-3 rounded-lg shadow-sm">
                      <FormField label="Purchase Requisition [ Pick ]">
                        <div class="flex gap-2">
                          <input
                            type="text"
                            v-model="form.pr_number"
                            readonly
                            placeholder="Select PR after choosing Project, RAP, and Vendor..."
                            class="w-full px-3 py-1.5 text-sm border border-gray-300 rounded-lg bg-gray-100 cursor-not-allowed text-gray-600 font-mono"
                          />
                          <button
                            type="button"
                            @click="openPRPicker"
                            class="px-5 py-1.5 bg-yellow-400 hover:bg-yellow-500 text-yellow-900 font-bold rounded-lg text-sm transition-colors shadow-sm"
                          >
                            Pick
                          </button>
                        </div>
                      </FormField>
                    </div>

                    <!-- Row 4: PO Item Type, Print Out Type, Repetition -->
                    <FormField label="PO Item Type" required class="col-span-1">
                      <div class="flex items-center gap-6 mt-2">
                        <label class="flex items-center gap-2 cursor-pointer">
                          <input type="radio" v-model="form.po_type" value="RM" @change="onPrTypeChange" class="w-4 h-4 text-bfs-navy border-gray-300 focus:ring-bfs-navy" />
                          <span class="text-sm font-medium text-gray-700">Raw Material</span>
                        </label>
                        <label class="flex items-center gap-2 cursor-pointer">
                          <input type="radio" v-model="form.po_type" value="SP" @change="onPrTypeChange" class="w-4 h-4 text-bfs-navy border-gray-300 focus:ring-bfs-navy" />
                          <span class="text-sm font-medium text-gray-700">Supplies</span>
                        </label>
                      </div>
                    </FormField>

                    <FormField label="Print Out Type" required class="col-span-1">
                      <div class="flex items-center gap-6 mt-2">
                        <label class="flex items-center gap-2 cursor-pointer">
                          <input type="radio" v-model="form.print_out_type" value="po" class="w-4 h-4 text-bfs-navy border-gray-300 focus:ring-bfs-navy" />
                          <span class="text-sm font-medium text-gray-700">Purchase Order</span>
                        </label>
                        <label class="flex items-center gap-2 cursor-pointer">
                          <input type="radio" v-model="form.print_out_type" value="spk" class="w-4 h-4 text-bfs-navy border-gray-300 focus:ring-bfs-navy" />
                          <span class="text-sm font-medium text-gray-700">Surat Perintah Kerja</span>
                        </label>
                      </div>
                    </FormField>

                    <FormField label="Repetition">
                      <SearchableSelect
                        v-model="form.repetition"
                        :options="repetitionChoices"
                        value-key="value"
                        label-key="label"
                        placeholder="— Select Repetition —"
                      />
                    </FormField>
                    
                    <!-- Row 5: Delivery Point & Notes -->
                    <FormField label="Delivery Point" class="lg:col-span-3">
                      <input v-model="form.delivery_point" type="text" class="w-full px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-1 focus:ring-bfs-navy focus:border-bfs-navy bg-white text-gray-900" placeholder="Delivery Point (e.g. pop b)" />
                    </FormField>
                    
                    <FormField label="Notes" class="lg:col-span-3">
                      <textarea v-model="form.notes" rows="2" class="w-full px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-1 focus:ring-bfs-navy focus:border-bfs-navy bg-white text-gray-900 resize-none" placeholder="Optional notes..."></textarea>
                    </FormField>
                  </div>

                <!-- Template / Table Controls -->
                <div class="flex items-center justify-between pb-2 border-b border-gray-100">
                  <h4 class="text-sm font-semibold text-gray-700 flex items-center gap-2">
                    <CheckSquare class="w-4 h-4 text-bfs-gold" />
                    PO Details
                  </h4>
                  <button
                    type="button"
                    @click="addDetailRow"
                    :disabled="!form.project || isFetchingRap"
                    class="btn-secondary text-xs px-3 py-1.5 flex items-center gap-1.5"
                  >
                    <Plus class="w-3.5 h-3.5" /> Add Item
                  </button>
                </div>

                <!-- Detail Table -->
                  <div v-if="form.details.length" class="border border-gray-200 rounded-xl overflow-hidden bg-white shadow-sm mt-6">
                    <div class="p-3 border-b border-gray-100 bg-gray-50 flex justify-between items-center">
                      <h4 class="text-sm font-semibold text-gray-700 flex items-center gap-2">
                        <CheckSquare class="w-4 h-4 text-bfs-gold" />
                        PO Details
                      </h4>
                      <button type="button" class="text-xs text-bfs-navy hover:underline flex items-center gap-1">
                        <Plus class="w-3 h-3" /> Add Custom Item
                      </button>
                    </div>
                    <div class="overflow-x-auto">
                      <table class="w-full text-left border-collapse">
                        <thead>
                          <tr class="bg-gray-50 border-b border-gray-200 text-[10px] font-semibold text-gray-600 uppercase tracking-wider">
                            <th class="py-2.5 px-3 w-10 text-center">No.</th>
                            <th class="py-2.5 px-3">Item Name</th>
                            <th class="py-2.5 px-3 w-32">Notes</th>
                            <th class="py-2.5 px-3 w-24 text-right">Qty</th>
                            <th class="py-2.5 px-3 w-32 text-right">Unit Price</th>
                            <th class="py-2.5 px-3 w-32 text-right">Total Price</th>
                            <th class="py-2.5 px-3 w-10 text-center">Del</th>
                          </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-100 text-xs">
                          <tr v-for="(row, idx) in form.details" :key="idx" class="hover:bg-yellow-50/20">
                            <td class="py-2 px-3 text-center font-mono text-gray-400">{{ idx + 1 }}</td>
                            <td class="py-2 px-3 font-medium text-gray-700">{{ row.item_name || 'Selected Item' }}</td>
                            <td class="py-2 px-3">
                              <input v-model="row.notes" type="text" class="w-full border border-gray-200 rounded px-2 py-1 text-xs focus:outline-none" placeholder="Note" />
                            </td>
                            <td class="py-2 px-3 text-right">
                              <input 
                                v-model.number="row.quantity" 
                                type="number" 
                                min="0" 
                                step="0.01"
                                class="w-full border border-gray-200 rounded px-2 py-1 text-xs text-right focus:outline-none" 
                                @input="calculateSummary"
                              />
                            </td>
                            <td class="py-2 px-3 text-right">
                              <input 
                                v-model.number="row.unit_price" 
                                type="number" 
                                class="w-full border border-gray-200 rounded px-2 py-1 text-xs text-right bg-gray-50 focus:outline-none" 
                                readonly
                              />
                            </td>
                            <td class="py-2 px-3 text-right font-mono text-gray-600">
                              {{ formatCurrency(row.quantity * row.unit_price) }}
                            </td>
                            <td class="py-2 px-3 text-center">
                              <button @click="removeDetailRow(idx)" type="button" class="text-red-400 hover:text-red-600">
                                <X class="w-4 h-4" />
                              </button>
                            </td>
                          </tr>
                        </tbody>
                        <tfoot class="bg-gray-50 border-t border-gray-200">
                          <tr>
                            <td colspan="5" class="py-2.5 px-4 text-right text-xs font-bold text-gray-700 uppercase">Subtotal</td>
                            <td class="py-2.5 px-4 text-right font-mono font-bold text-bfs-gold">{{ formatCurrency(summary.total_amount) }}</td>
                            <td></td>
                          </tr>
                        </tfoot>
                      </table>
                    </div>
                  </div>
                  
                  <!-- PAYMENT TERMS & SUMMARY -->
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 pt-4 border-t border-gray-100">
                  <!-- Left: Payment Terms -->
                  <div>
                    <div class="flex items-center justify-between pb-2 mb-2 border-b border-gray-100">
                      <h4 class="text-sm font-semibold text-gray-700 flex items-center gap-2">
                        <CheckSquare class="w-4 h-4 text-bfs-gold" />
                        Payment Terms
                      </h4>
                      <button type="button" @click="addPaymentTerm" class="text-xs text-bfs-navy hover:underline flex items-center gap-1">
                        <Plus class="w-3 h-3" /> Add Term
                      </button>
                    </div>
                    
                    <table class="w-full text-left border-collapse border border-gray-200">
                      <thead>
                        <tr class="bg-gray-100 text-[10px] uppercase text-gray-600">
                          <th class="p-1.5 border border-gray-200 w-6 text-center"></th>
                          <th class="p-1.5 border border-gray-200">Term Desc</th>
                          <th class="p-1.5 border border-gray-200">Duration Due</th>
                          <th class="p-1.5 border border-gray-200 w-16">%</th>
                          <th class="p-1.5 border border-gray-200">Amount</th>
                          <th class="p-1.5 border border-gray-200">Due Date</th>
                          <th class="p-1.5 border border-gray-200">Doc Reff</th>
                        </tr>
                      </thead>
                      <tbody class="text-xs">
                        <tr v-for="(term, idx) in form.payment_terms" :key="idx">
                          <td class="p-1 border border-gray-200 text-center">
                            <button @click="removePaymentTerm(idx)" class="text-red-400 hover:text-red-600"><Trash2 class="w-3 h-3" /></button>
                          </td>
                          <td class="p-1 border border-gray-200">
                            <input v-model="term.term_desc" type="text" class="w-full p-1 bg-gray-50 border border-gray-300 rounded text-xs" />
                          </td>
                          <td class="p-1 border border-gray-200">
                            <select v-model="term.duration_due" class="w-full p-1 bg-gray-50 border border-gray-300 rounded text-xs">
                              <option value="none">None</option>
                              <option value="14">14 HARI</option>
                              <option value="21">21 HARI</option>
                              <option value="30">30 HARI</option>
                              <option value="45">45 HARI</option>
                              <option value="60">60 HARI</option>
                            </select>
                          </td>
                          <td class="p-1 border border-gray-200">
                            <input v-model.number="term.duration_due_percent" @input="calculatePaymentTerms" type="number" step="0.1" class="w-full p-1 bg-gray-50 border border-gray-300 rounded text-xs text-right" />
                          </td>
                          <td class="p-1 border border-gray-200">
                            <input v-model.number="term.amount" type="number" readonly class="w-full p-1 bg-gray-100 text-gray-500 rounded text-xs text-right" />
                          </td>
                          <td class="p-1 border border-gray-200">
                            <input v-model="term.due_date" type="date" class="w-full p-1 bg-gray-50 border border-gray-300 rounded text-xs" />
                          </td>
                          <td class="p-1 border border-gray-200">
                            <input v-model="term.doc_reff" type="text" class="w-full p-1 bg-gray-50 border border-gray-300 rounded text-xs" />
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>

                  <!-- Right: Summary Totals -->
                  <div class="flex flex-col gap-1.5 text-xs">
                    <div class="flex justify-between items-center px-2 py-1 bg-gray-50 rounded">
                      <span class="text-gray-600">Total Amount (IDR)</span>
                      <span class="font-mono font-semibold">{{ formatCurrency(summary.total_amount) }}</span>
                    </div>
                    <div class="flex justify-between items-center px-2 py-1 bg-gray-50 rounded">
                      <div class="flex items-center gap-2">
                        <span class="text-gray-600">Disc.</span>
                        <input v-model.number="form.discount_percent" @input="calculateSummary" type="number" step="0.1" class="w-16 p-0.5 border border-gray-300 rounded text-right" />
                        <span class="text-gray-600">%</span>
                      </div>
                      <span class="font-mono">{{ formatCurrency(summary.discount_amount) }}</span>
                    </div>
                    <div class="flex justify-between items-center px-2 py-1 bg-gray-50 rounded">
                      <span class="text-gray-600">Total Tax (IDR)</span>
                      <span class="font-mono">{{ formatCurrency(summary.total_tax) }}</span>
                    </div>
                    <div class="flex justify-between items-center px-2 py-1 bg-gray-50 rounded">
                      <span class="text-gray-600">Total Deduction (IDR)</span>
                      <span class="font-mono">{{ formatCurrency(summary.total_deduction) }}</span>
                    </div>
                    <div class="flex justify-between items-center px-2 py-1.5 bg-gray-200 rounded font-bold border-t border-b border-gray-300 my-1">
                      <span class="text-gray-800">Grand Total (IDR)</span>
                      <span class="font-mono text-bfs-navy">{{ formatCurrency(summary.grand_total) }}</span>
                    </div>
                    
                    <div class="flex justify-between items-center px-2 py-1 bg-gray-50 rounded">
                      <span class="text-gray-600">Payment ({{ paymentPercent }}%)</span>
                      <span class="font-mono">{{ formatCurrency(summary.payment_amount) }}</span>
                    </div>
                    <div class="flex justify-between items-center px-2 py-1 bg-gray-50 rounded">
                      <span class="text-gray-600">Selisih</span>
                      <span class="font-mono">{{ formatCurrency(summary.selisih) }}</span>
                    </div>
                    <div class="flex justify-between items-center px-2 py-1 bg-gray-50 rounded">
                      <span class="text-gray-600">Partial Cancelation PO</span>
                      <input v-model.number="form.partial_cancellation" @input="calculateSummary" type="number" class="w-32 p-0.5 border border-gray-300 rounded text-right" />
                    </div>
                    <div class="flex justify-between items-center px-2 py-1 bg-gray-50 rounded font-bold">
                      <span class="text-gray-800">Balance</span>
                      <span class="font-mono text-red-600">{{ formatCurrency(summary.balance) }}</span>
                    </div>
                  </div>
                </div>

              </div>

              <!-- Modal Footer -->
              <div class="px-6 py-4 border-t border-gray-100 bg-gray-50 rounded-b-2xl flex justify-between items-center">
                <button @click="closeModal" class="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 transition-colors font-semibold">
                  Cancel
                </button>
                <div class="flex gap-2">
                  <button 
                    v-if="!['ready_to_process', 'close'].includes(form.document_status)"
                    @click="savePO(false)" 
                    :disabled="store.loading"
                    class="btn-secondary text-sm px-5 flex items-center gap-2"
                  >
                    <Save class="w-4 h-4" /> Save as Draft
                  </button>
                  <button 
                    v-if="!['ready_to_process', 'close'].includes(form.document_status)"
                    @click="savePO(true)" 
                    :disabled="store.loading || !form.details.length"
                    class="bg-bfs-navy hover:bg-bfs-navy-dark text-white text-sm font-bold px-6 py-2 rounded-lg transition-colors flex items-center gap-2 cursor-pointer shadow-md shadow-bfs-navy/20"
                  >
                    <Send class="w-4 h-4" /> Submit to Approval
                  </button>
                </div>
              </div>

            </div>
          </div>
        </div>
      </Transition>
      <PRPickerModal 
        v-model:show="showPRPicker"
        :project-id="form.project"
        :rap-id="form.rap"
        :po-type="form.po_type"
        @select="handlePRSelected"
      />
</template>

<script setup>

import { ref, computed, watch, onMounted } from 'vue'
import { Plus, Trash2, Save, X, Search, FileText } from 'lucide-vue-next'
import api from '../../services/api'
import { useAuthStore } from '../../stores/auth'
import { usePurchaseOrderStore } from '../../stores/purchaseOrder'
import { usePurchaseStore } from '../../stores/purchase'
import { useProjectsStore } from '../../stores/projects'
import FormField from '../../components/FormField.vue'
import SearchableSelect from '../../components/SearchableSelect.vue'
import PRPickerModal from './PRPickerModal.vue'
import { usePurchaseRequisitionStore } from '../../stores/purchaseRequisition'

const props = defineProps({
  show: Boolean,
  mode: String,
  editId: Number
})

const emit = defineEmits(['update:show', 'saved'])

const authStore = useAuthStore()
const store = usePurchaseOrderStore()
const purchaseStore = usePurchaseStore()
const projectStore = useProjectsStore()
const prStore = usePurchaseRequisitionStore()

const showPRPicker = ref(false)

const availableProjects = computed(() => projectStore.projects)

// We use local form state
const formError = ref(null)
const isFetchingRap = ref(false)

const form = ref({
  po_number: '',
  pr_number: '',
  po_type: 'RM',
  print_out_type: 'po',
  project: null,
  department: (!authStore.isSuperuser && authStore.employee) ? authStore.employee.department_id : null,
  po_date: new Date().toISOString().split('T')[0],
  rap: null,
  vendor: null,
  pr_class: 'None',
  repetition: 'None',
  etd: new Date().toISOString().split('T')[0],
  delivery_point: '',
  notes: '',
  details: [],
  payment_terms: []
})

// Store extracted RAP items for dropdown
const availableRaps = computed(() => projectStore.raps)
const availableRapItems = ref([])
const availableVendors = computed(() => purchaseStore.vendors)
const availableDepartments = ref([])

const prTypeChoices = [
  { value: 'RM', label: 'Raw Material' },
  { value: 'SP', label: 'Supplies' },
  { value: 'AST', label: 'Asset' }
]

const requestTypeChoices = [
  { value: 'Normal', label: 'Normal' },
  { value: 'Urgent', label: 'Urgent' }
]

const repetitionChoices = [
  { value: 'None', label: 'None' },
  { value: 'Daily', label: 'Daily' },
  { value: 'Weekly', label: 'Weekly' },
  { value: 'Monthly', label: 'Monthly' },
  { value: 'Yearly', label: 'Yearly' }
]

const formatCurrency = (val) => {
  if (!val) return 'Rp 0'
  return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR' }).format(val)
}

function resetForm() {
  formError.value = null
  form.value = {
    po_number: '',
    pr_number: '',
    po_type: 'RM',
    print_out_type: 'po',
    project: null,
    department: (!authStore.isSuperuser && authStore.employee) ? authStore.employee.department_id : null,
    po_date: new Date().toISOString().split('T')[0],
    rap: null,
    vendor: null,
    pr_class: 'None',
    repetition: 'None',
    etd: new Date().toISOString().split('T')[0],
    delivery_point: '',
    notes: '',
    details: [],
    payment_terms: []
  }
  availableRapItems.value = []
}

async function fetchDepartments() {
  if (authStore.isSuperuser) {
    try {
      const res = await api.get('/org/departments/')
      const flatten = (nodes) => {
        let result = []
        for (const node of nodes) {
          result.push({ id: node.id, name: node.name })
          if (node.children && node.children.length) {
            result = result.concat(flatten(node.children))
          }
        }
        return result
      }
      availableDepartments.value = flatten(res.data)
    } catch (e) {
      console.error('Failed to fetch departments', e)
    }
  } else {
    if (authStore.employee && authStore.employee.department_id) {
      availableDepartments.value = [{
        id: authStore.employee.department_id,
        name: typeof authStore.employee.department === 'object' ? authStore.employee.department.name : (authStore.employee.department_name || authStore.employee.department || 'My Department')
      }]
    } else {
      availableDepartments.value = []
    }
  }
}

async function fetchProjectRAPItems(projectId) {
  isFetchingRap.value = true
  try {
    await projectStore.fetchRaps({ project: projectId, approval_status: 'approved' })
    if (projectStore.raps.length > 0) {
      const rap = projectStore.raps[0]
      form.value.rap = rap.id
      availableRapItems.value = (rap.details || []).filter(d => 
        d.item_type === 'item'
      )
    } else {
      form.value.rap = null
      availableRapItems.value = []
    }
  } catch (e) {
    console.error(e)
    availableRapItems.value = []
  } finally {
    isFetchingRap.value = false
  }
}

async function onProjectChange() {
  form.value.details = []
  if (!form.value.project) {
    availableRapItems.value = []
    return
  }
  await fetchProjectRAPItems(form.value.project)
}

function onPrTypeChange() {
  form.value.details = []
  if (form.value.project) {
    fetchProjectRAPItems(form.value.project)
  }
}

function addDetailRow() {
  form.value.details.push({
    rap_detail_id: null,
    item: null,
    notes: '',
    quantity: 0,
    max_quantity: null,
    unit_price: 0,
    total_price: 0
  })
}

function removeDetailRow(index) {
  form.value.details.splice(index, 1)
  calculateSummary()
}

function openPRPicker() {
  if (!form.value.project || !form.value.rap || !form.value.vendor) {
    alert('Please select Project, RAP, and Vendor first')
    return
  }
  showPRPicker.value = true
}

async function handlePRSelected(pr) {
  try {
    const prData = await prStore.fetchPRDetails(pr.id)
    form.value.pr_number = pr.pr_number
    form.value.details = (prData.details || []).map(d => ({
      pr_detail: d.id,
      item: d.item?.id || d.item,
      item_name: d.item_name || (d.item ? d.item.item_name : ''),
      item_type: 'item',
      quantity: d.quantity,
      unit: d.unit?.id || d.unit,
      unit_name: d.unit_name || (d.unit ? d.unit.unit_name : ''),
      unit_price: d.unit_price || 0,
      discount_percent: 0,
      tax1: 'none',
      tax2: 'none',
      amount: d.quantity * (d.unit_price || 0),
      estimated_date: form.value.etd
    }))
    calculateSummary()
  } catch (err) {
    console.error("Failed to fetch PR details", err)
    alert("Gagal memuat detail PR.")
  }
}

function getAvailableItemsForRow(currentRow) {
  const otherSelectedIds = form.value.details
    .filter(r => r !== currentRow && r.rap_detail_id)
    .map(r => r.rap_detail_id)
    
  return availableRapItems.value.filter(item => {
    if (otherSelectedIds.includes(item.id)) return false
    if (item.id === currentRow.rap_detail_id) return true
    return item.remaining_volume > 0
  })
}

function onItemSelect(row) {
  const selectedItem = availableRapItems.value.find(ri => ri.id === row.rap_detail_id)
  if (selectedItem) {
    row.item = selectedItem.item?.id || null
    row.unit_price = selectedItem.unit_price || 0
    row.max_quantity = selectedItem.remaining_volume || 0
    row.quantity = 0
    row.total_price = 0
  } else {
    row.item = null
    row.unit_price = 0
    row.max_quantity = null
    row.quantity = 0
    row.total_price = 0
  }
  calculateSummary()
}

function addPaymentTerm() {
  form.value.payment_terms.push({
    term_name: '',
    percentage: 0,
    amount: 0,
    due_date: null
  })
}

function removePaymentTerm(idx) {
  form.value.payment_terms.splice(idx, 1)
}

const summary = computed(() => {
  const subtotal = form.value.details.reduce((sum, d) => sum + (d.total_price || 0), 0)
  return {
    total_amount: subtotal
  }
})

function calculateSummary() {
  for (let d of form.value.details) {
    d.total_price = (d.quantity || 0) * (d.unit_price || 0)
  }
  const total = summary.value.total_amount
  for (let t of form.value.payment_terms) {
    if (t.percentage) {
      t.amount = total * (t.percentage / 100)
    }
  }
}

function closeModal() {
  emit('update:show', false)
  formError.value = null
}

async function savePO(isDraft = false) {
  formError.value = null
  for (let row of form.value.details) {
    if (!row.rap_detail_id || row.quantity <= 0) {
      formError.value = "All items must be selected and have a quantity greater than 0."
      return
    }
  }

  const payload = {
    project: form.value.project,
    department: form.value.department,
    po_type: form.value.po_type,
    print_out_type: form.value.print_out_type,
    po_date: form.value.po_date,
    rap: form.value.rap,
    vendor: form.value.vendor,
    pr_class: form.value.pr_class,
    repetition: form.value.repetition,
    etd: form.value.etd || null,
    delivery_point: form.value.delivery_point,
    notes: form.value.notes,
    details: form.value.details.map(d => ({
      rap_detail: d.rap_detail_id,
      item: d.item,
      quantity: d.quantity,
      unit_price: d.unit_price,
      total_price: d.total_price,
      notes: d.notes
    })),
    payment_terms: form.value.payment_terms.map(t => ({
      term_name: t.term_name,
      percentage: t.percentage,
      amount: t.amount,
      due_date: t.due_date
    })),
    document_status: isDraft ? 'draft' : 'ready_to_process'
  }

  try {
    if (props.mode === 'add') {
      await store.createPO(payload)
    } else {
      await store.updatePO(props.editId, payload)
    }
    if (!store.error) {
      closeModal()
      emit('saved')
    } else {
      formError.value = store.error
    }
  } catch (e) {
    console.error(e)
    formError.value = "Failed to save Purchase Order."
  }
}

watch(() => props.show, async (newVal) => {
  if (newVal) {
    if (props.mode === 'add') {
      if (!projectStore.projects.length) {
        projectStore.fetchProjects()
      }
      purchaseStore.fetchVendors()
      fetchDepartments()
      resetForm()
      if (authStore.employee && authStore.employee.department_id) {
        form.value.department = authStore.employee.department_id
      }
    } else if (props.mode === 'edit' && props.editId) {
      try {
        if (!projectStore.projects.length) {
          projectStore.fetchProjects()
        }
        purchaseStore.fetchVendors()
        fetchDepartments()
        const poDetails = await store.fetchPODetails(props.editId)
        form.value.po_number = poDetails.po_number
        form.value.po_type = poDetails.po_type || 'RM'
        form.value.print_out_type = poDetails.print_out_type || 'po'
        form.value.project = poDetails.project?.id || poDetails.project
        form.value.department = poDetails.department?.id || poDetails.department
        form.value.po_date = poDetails.po_date
        form.value.rap = poDetails.rap?.id || poDetails.rap
        form.value.vendor = poDetails.vendor?.id || poDetails.vendor
        form.value.pr_class = poDetails.pr_class
        form.value.repetition = poDetails.repetition
        form.value.etd = poDetails.etd
        form.value.delivery_point = poDetails.delivery_point
        form.value.notes = poDetails.notes
        form.value.details = poDetails.details.map(d => ({
          id: d.id,
          rap_detail_id: d.rap_detail?.id || d.rap_detail,
          item: d.item?.id || d.item,
          quantity: d.quantity,
          unit_price: Number(d.unit_price),
          total_price: Number(d.total_price),
          notes: d.notes,
          max_quantity: d.rap_detail?.remaining_volume + d.quantity
        }))
        form.value.payment_terms = poDetails.payment_terms.map(t => ({
          term_name: t.term_name,
          percentage: Number(t.percentage),
          amount: Number(t.amount),
          due_date: t.due_date
        }))
        if (form.value.project) {
          await fetchProjectRAPItems(form.value.project)
        }
        calculateSummary()
      } catch (e) {
        console.error(e)
      }
    }
  }
})

onMounted(() => {
})

</script>
