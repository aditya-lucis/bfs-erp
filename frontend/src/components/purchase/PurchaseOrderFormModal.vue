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
                    <div class="col-span-1">
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

                      <!-- Vendor Info -->
                      <div v-if="selectedVendorData" class="mt-2 mb-4 p-3 bg-gray-50 rounded-lg text-xs font-mono text-gray-700">
                        <div class="grid grid-cols-[120px_1fr] gap-2">
                          <div>Vendor Address</div>
                          <div>: {{ selectedVendorData.address_1 }}</div>
                          <div>NPWP</div>
                          <div>: {{ selectedVendorData.tax_number || '-' }}</div>
                        </div>
                      </div>
                    </div>

                    <FormField label="Estimated Date (ETD)">
                      <input v-model="form.etd" type="date" class="w-full px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-1 focus:ring-bfs-navy focus:border-bfs-navy bg-white text-gray-900" />
                    </FormField>
                    
                    <FormField label="PO Date" required>
                      <input v-model="form.po_date" @change="updateAllDueDates" type="date" required class="w-full px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-1 focus:ring-bfs-navy focus:border-bfs-navy bg-white text-gray-900" />
                    </FormField>



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

                    <!-- Row 5: Delivery Point & Notes -->
                    <FormField label="Delivery Point" class="lg:col-span-3">
                      <input v-model="form.delivery_point" type="text" class="w-full px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-1 focus:ring-bfs-navy focus:border-bfs-navy bg-white text-gray-900" placeholder="Delivery Point (e.g. pop b)" />
                    </FormField>
                    
                    <FormField label="Notes" class="lg:col-span-3">
                      <textarea v-model="form.notes" rows="2" class="w-full px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-1 focus:ring-bfs-navy focus:border-bfs-navy bg-white text-gray-900 resize-none" placeholder="Optional notes..."></textarea>
                    </FormField>

                    <!-- Additional Requested Fields -->
                    <div class="col-span-1 lg:col-span-3 grid grid-cols-1 md:grid-cols-2 gap-6 mt-4 pt-4 border-t border-gray-100">
                      <FormField label="Term and Condition" required>
                        <textarea v-model="form.term_and_condition" rows="2" class="w-full px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-1 focus:ring-bfs-navy focus:border-bfs-navy bg-white text-gray-900 resize-none"></textarea>
                      </FormField>
                      
                      <div class="flex flex-col">
                        <label class="flex items-center gap-2 cursor-pointer mb-2">
                          <input type="checkbox" v-model="form.is_subcontract" class="w-4 h-4 text-bfs-navy border-gray-300 rounded focus:ring-bfs-navy" @change="!form.is_subcontract ? form.subcontract_notes = '' : null" />
                          <span class="text-xs font-semibold text-gray-700 uppercase tracking-wider">Is Sub Contract</span>
                        </label>
                        <textarea v-model="form.subcontract_notes" :disabled="!form.is_subcontract" rows="2" class="w-full px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-1 focus:ring-bfs-navy focus:border-bfs-navy bg-white text-gray-900 resize-none disabled:bg-gray-100 disabled:text-gray-500" placeholder="Sub contract notes..."></textarea>
                      </div>

                      <FormField label="Vendor SO Number">
                        <input v-model="form.vendor_so_number" type="text" class="w-full px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-1 focus:ring-bfs-navy focus:border-bfs-navy bg-white text-gray-900" />
                      </FormField>

                      <div class="flex flex-col gap-3 mt-1">
                        <label class="flex items-center gap-2 cursor-pointer">
                          <input type="checkbox" v-model="form.mandatory_update_material" class="w-4 h-4 text-bfs-navy border-gray-300 rounded focus:ring-bfs-navy" />
                          <span class="text-sm font-medium text-gray-700">Mandatory Update Material</span>
                        </label>
                        <label class="flex items-center gap-2 cursor-pointer">
                          <input type="checkbox" v-model="form.is_sister_company" class="w-4 h-4 text-bfs-navy border-gray-300 rounded focus:ring-bfs-navy" />
                          <span class="text-sm font-medium text-gray-700">Is Sister Company</span>
                        </label>
                      </div>
                    </div>
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
                            <th class="py-2.5 px-3 w-28 text-left">Tax 1</th>
                            <th class="py-2.5 px-3 w-28 text-left">Tax 2</th>
                            <th class="py-2.5 px-3 w-32 text-right">Total Price</th>
                            <th class="py-2.5 px-3 w-10 text-center">Del</th>
                          </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-100 text-xs">
                          <tr v-for="(row, idx) in form.details" :key="idx" class="hover:bg-yellow-50/20">
                            <td class="py-2 px-3 text-center font-mono text-gray-400">{{ idx + 1 }}</td>
                            <td class="py-2 px-3 font-medium text-gray-700">
                              <span v-if="row.item_code" class="text-gray-500 mr-1">[{{ row.item_code }}]</span>
                              {{ row.item_name || 'Selected Item' }}
                            </td>
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
                            <td class="py-2 px-3">
                              <select v-model="row.tax1" @change="calculateSummary" class="w-full border border-gray-200 rounded px-2 py-1 text-xs focus:outline-none bg-white">
                                <option v-for="t in taxChoices" :key="'1'+t.value" :value="t.value">{{ t.label }}</option>
                              </select>
                            </td>
                            <td class="py-2 px-3">
                              <select v-model="row.tax2" @change="calculateSummary" class="w-full border border-gray-200 rounded px-2 py-1 text-xs focus:outline-none bg-white">
                                <option v-for="t in taxChoices" :key="'2'+t.value" :value="t.value">{{ t.label }}</option>
                              </select>
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
                            <td colspan="7" class="py-2.5 px-4 text-right text-xs font-bold text-gray-700 uppercase">Subtotal</td>
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
                            <select v-model="term.duration_due" @change="updateDueDate(idx)" class="w-full p-1 bg-gray-50 border border-gray-300 rounded text-xs">
                              <option value="none">None</option>
                              <option value="14">14 HARI</option>
                              <option value="21">21 HARI</option>
                              <option value="30">30 HARI</option>
                              <option value="45">45 HARI</option>
                              <option value="60">60 HARI</option>
                            </select>
                          </td>
                          <td class="p-1 border border-gray-200">
                            <input v-model.number="term.percentage" @input="calculatePaymentTerms" type="number" step="0.1" class="w-full p-1 bg-gray-50 border border-gray-300 rounded text-xs text-right" />
                          </td>
                          <td class="p-1 border border-gray-200">
                            <input v-model.number="term.amount" type="number" @input="calculateSummary" class="w-full p-1 bg-white border border-gray-300 rounded text-xs text-right" />
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
                    <button 
                      v-if="form.approval_status === 'approved'"
                      @click="updatePaymentTerms" 
                      :disabled="store.loading"
                      class="bg-bfs-navy text-white font-medium text-[11px] px-4 py-1.5 rounded hover:bg-bfs-navy-dark transition-colors mt-3 shadow-sm shadow-bfs-navy/20"
                    >
                      Update Payment Term
                    </button>
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
                    <div class="flex justify-between items-center px-3 py-2 bg-gray-100 rounded text-base font-bold border-t border-gray-300 mt-2">
                      <span class="text-gray-800">Grand Total (IDR)</span>
                      <span class="font-mono text-bfs-navy">{{ formatCurrency(summary.display_total) }}</span>
                    </div>
                        <div class="flex justify-between items-center px-2 py-1 bg-gray-50 rounded">
                          <span class="text-gray-600">Payment</span>
                          <span class="font-mono">{{ formatCurrency(form.paid_amount || 0) }}</span>
                        </div>
                    <div class="flex justify-between items-center px-2 py-1 bg-gray-50 rounded">
                      <span class="text-gray-600">Selisih</span>
                      <span class="font-mono" :class="summary.selisih < 0 ? 'text-red-500' : ''">
                        {{ summary.selisih < 0 ? '- ' : '' }}{{ formatCurrency(Math.abs(summary.selisih)) }}
                      </span>
                    </div>
                    <template v-if="canPartialCancel">
                      <div class="flex justify-between items-center px-2 py-1 bg-gray-50 rounded">
                        <span class="text-gray-600">Partial Cancelation PO</span>
                        <input
                          v-model.number="form.partial_cancellation"
                          @input="calculateSummary"
                          type="number"
                          class="w-32 px-2 py-1 border border-gray-300 rounded text-right text-xs focus:ring-bfs-navy"
                        />
                      </div>
                      <div class="flex justify-between items-center px-3 py-2 bg-gray-100 rounded text-base font-bold border-t border-gray-300 mt-2">
                        <span class="text-gray-800">Balance</span>
                        <span class="font-mono text-red-600">{{ formatCurrency(summary.balance) }}</span>
                      </div>
                      <button 
                        v-if="form.approval_status === 'approved'"
                        @click="updatePartialCancelation" 
                        :disabled="store.loading"
                        class="bg-bfs-navy text-white font-medium text-[11px] px-4 py-1.5 rounded hover:bg-bfs-navy-dark transition-colors mt-3 ml-auto block shadow-sm shadow-bfs-navy/20"
                      >
                        Update PO Cancelation
                      </button>
                    </template>
                  </div>
                </div>

              </div>

              <!-- Modal Footer -->
              <div class="px-6 py-4 border-t border-gray-100 bg-gray-50 rounded-b-2xl flex justify-between items-center">
                <div class="flex justify-end gap-3 px-6 py-4 bg-gray-50 border-t border-gray-100">
                  <button type="button" @click="closeModal" class="btn-ghost text-sm px-5">Cancel</button>
                  <button 
                    v-if="!['ready_to_process', 'close'].includes(form.document_status) && !['awaiting', 'approved'].includes(form.approval_status)"
                    @click="savePO(true)" 
                    :disabled="store.loading"
                    class="btn-secondary text-sm px-5 flex items-center gap-2"
                  >
                  <Save class="w-4 h-4" /> Save as Draft
                  </button>
                  <button 
                    v-if="!['ready_to_process', 'close'].includes(form.document_status) && !['awaiting', 'approved'].includes(form.approval_status)"
                    @click="savePO(false)" 
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
import { Plus, Trash2, Save, X, Search, FileText, AlertCircle, CheckSquare, Send } from 'lucide-vue-next'
import Swal from 'sweetalert2'
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
  ppn: false,
  is_subcontract: false,
  subcontract_notes: '',
  term_and_condition: '',
  mandatory_update_material: false,
  vendor_so_number: '',
  is_sister_company: false,
  paid_amount: 0,
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

const selectedVendorData = computed(() => {
  return availableVendors.value.find(v => v.id === form.value.vendor)
})

const prTypeChoices = [
  { value: 'RM', label: 'Raw Material' },
  { value: 'SP', label: 'Supplies' },
  { value: 'AST', label: 'Asset' }
]

const taxMap = {
  'none': { rate: 0, type: 'none' },
  'non': { rate: 0, type: 'none' },
  'pph_23_rate_15': { rate: 15, type: 'deduction' },
  'pph_23_rate_2': { rate: 2, type: 'deduction' },
  'pph_23_rate_4': { rate: 4, type: 'deduction' },
  'pph_23_rate_4_5': { rate: 4.5, type: 'deduction' },
  'pph_23_rate_7_5': { rate: 7.5, type: 'deduction' },
  'pph_4_2_rate_10': { rate: 10, type: 'deduction' },
  'pph_4_2_rate_2': { rate: 2, type: 'deduction' },
  'pph_4_2_rate_3': { rate: 3, type: 'deduction' },
  'pph_4_2_rate_4': { rate: 4, type: 'deduction' },
  'ppn_01': { rate: 1, type: 'addition' },
  'ppn_10': { rate: 10, type: 'addition' },
  'ppn_10_euro': { rate: 10, type: 'addition' },
  'ppn_11': { rate: 11, type: 'addition' },
  'ppn_15': { rate: 15, type: 'addition' }
}

const taxChoices = [
  { value: 'none', label: '-' },
  { value: 'pph_23_rate_15', label: 'PPH 23 RATE 15 %' },
  { value: 'pph_23_rate_2', label: 'PPH 23 RATE 2 %' },
  { value: 'pph_23_rate_4', label: 'PPH 23 RATE 4%' },
  { value: 'pph_23_rate_4_5', label: 'PPh 23 RATE 4.5 %' },
  { value: 'pph_23_rate_7_5', label: 'PPH 23 RATE 7.5 %' },
  { value: 'pph_4_2_rate_10', label: 'PPH 4(2) RATE 10%' },
  { value: 'pph_4_2_rate_2', label: 'PPH 4(2) RATE 2%' },
  { value: 'pph_4_2_rate_3', label: 'PPH 4(2) RATE 3%' },
  { value: 'pph_4_2_rate_4', label: 'PPH 4(2) RATE 4%' },
  { value: 'ppn_01', label: 'PPN 01 %' },
  { value: 'ppn_10', label: 'PPN 10 %' },
  { value: 'ppn_10_euro', label: 'PPN 10% (EURO)' },
  { value: 'ppn_11', label: 'PPN 11 %' },
  { value: 'ppn_15', label: 'PPN 15%' },
  { value: 'non', label: 'Non PPh' }
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
    ppn: false,
    is_subcontract: false,
    subcontract_notes: '',
    term_and_condition: '',
    mandatory_update_material: false,
    vendor_so_number: '',
    is_sister_company: false,
    paid_amount: 0,
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
    pr_detail_id: null,
    rap_detail_id: null,
    item: null,
    notes: '',
    quantity: 0,
    max_quantity: null,
    unit_price: 0,
    tax1: 'none',
    tax2: 'none',
    total_price: 0
  })
}

function removeDetailRow(index) {
  form.value.details.splice(index, 1)
  calculateSummary()
}

function openPRPicker() {
  if (!form.value.project || !form.value.rap || !form.value.vendor) {
    Swal.fire({
      icon: 'warning',
      title: 'Incomplete Selection',
      text: 'Please select Project, RAP, and Vendor first'
    })
    return
  }
  showPRPicker.value = true
}

async function handlePRSelected(pr) {
  try {
    const prData = await prStore.fetchPRDetails(pr.id)
    form.value.pr_number = pr.pr_number
    form.value.details = (prData.details || []).map(d => ({
      pr_detail_id: d.id,
      rap_detail_id: d.rap_detail?.id || d.rap_detail,
      item: d.item?.id || d.item,
      item_name: d.item_name || (d.item ? d.item.item_name : ''),
      item_code: d.item_code || (d.item ? d.item.item_code : ''),
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
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: 'Gagal memuat detail PR.'
    })
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
    row.tax1 = 'none'
    row.tax2 = 'none'
    row.max_quantity = selectedItem.remaining_volume || 0
    row.quantity = 0
    row.total_price = 0
  } else {
    row.item = null
    row.unit_price = 0
    row.tax1 = 'none'
    row.tax2 = 'none'
    row.max_quantity = null
    row.quantity = 0
    row.total_price = 0
  }
  calculateSummary()
}

function addPaymentTerm() {
  let remaining = 0
  if (summary.value && summary.value.display_total) {
    remaining = summary.value.display_total - summary.value.payment_amount
    if (remaining < 0) remaining = 0
  }
  form.value.payment_terms.push({
    term_desc: '',
    duration_due: 'none',
    percentage: 0,
    amount: remaining,
    due_date: null,
    doc_reff: ''
  })
  calculateSummary()
}

function removePaymentTerm(idx) {
  form.value.payment_terms.splice(idx, 1)
  calculateSummary()
}

function updateDueDate(idx) {
  const term = form.value.payment_terms[idx]
  if (term.duration_due !== 'none' && form.value.po_date) {
    const duration = parseInt(term.duration_due, 10)
    if (!isNaN(duration)) {
      const poDate = new Date(form.value.po_date)
      poDate.setDate(poDate.getDate() + duration)
      term.due_date = poDate.toISOString().split('T')[0]
    }
  } else if (term.duration_due === 'none') {
    term.due_date = null
  }
}

function updateAllDueDates() {
  if (form.value.payment_terms && form.value.payment_terms.length > 0) {
    form.value.payment_terms.forEach((_, idx) => updateDueDate(idx))
  }
}

const canPartialCancel = computed(() => {
  return props.mode === 'edit' && form.value.approval_status === 'approved'
})

const paymentPercent = computed(() => {
  return form.value.payment_terms.reduce((sum, t) => sum + (Number(t.percentage) || 0), 0)
})

const summary = computed(() => {
  let subtotal = 0
  let total_tax = 0
  let total_deduction = 0

  const discount_percent = form.value.discount_percent || 0
  const discountMultiplier = 1 - (discount_percent / 100)

  form.value.details.forEach(d => {
    const lineTotal = (d.quantity || 0) * (d.unit_price || 0)
    const discountedLineTotal = lineTotal * discountMultiplier
    
    const t1 = taxMap[d.tax1] || { rate: 0, type: 'none' }
    const t2 = taxMap[d.tax2] || { rate: 0, type: 'none' }
    
    let ppnRate = 0
    let pphRate = 0
    
    if (t1.type === 'addition') ppnRate += t1.rate
    if (t2.type === 'addition') ppnRate += t2.rate
    
    if (t1.type === 'deduction') pphRate += t1.rate
    if (t2.type === 'deduction') pphRate += t2.rate
    
    let baseAmount = discountedLineTotal
    let itemPPN = 0
    
    if (form.value.ppn) {
      baseAmount = discountedLineTotal / (1 + (ppnRate / 100))
      itemPPN = discountedLineTotal - baseAmount
    } else {
      itemPPN = baseAmount * (ppnRate / 100)
    }
    
    const itemPPh = baseAmount * (pphRate / 100)
    
    subtotal += baseAmount
    total_tax += itemPPN
    total_deduction += itemPPh
  })
  
  const rawSubtotal = form.value.details.reduce((sum, d) => sum + ((d.quantity || 0) * (d.unit_price || 0)), 0)
  const discount_amount = rawSubtotal * (discount_percent / 100)
  const after_discount = rawSubtotal - discount_amount
  
  const grand_total = after_discount
  const display_total = grand_total + total_tax - total_deduction
  
  const payment_amount = form.value.payment_terms.reduce((sum, t) => sum + (Number(t.amount) || 0), 0)
  const selisih = display_total - (form.value.paid_amount || 0)
  const partial_cancellation = form.value.partial_cancellation || 0
  const balance = display_total - partial_cancellation - (form.value.paid_amount || 0)
  
  return {
    total_amount: rawSubtotal,
    discount_amount,
    total_tax,
    total_deduction,
    grand_total,
    display_total,
    payment_amount,
    selisih,
    partial_cancellation,
    balance
  }
})

function calculateSummary() {
  for (let d of form.value.details) {
    d.total_price = (d.quantity || 0) * (d.unit_price || 0)
  }
  const total = summary.value.display_total || summary.value.total_amount || 0
  for (let t of form.value.payment_terms) {
    if (t.amount < 0) t.amount = 0
    if (total > 0) {
      t.percentage = (t.amount / total) * 100
    } else {
      t.percentage = 0
    }
  }
}

function calculatePaymentTerms() {
  const total = summary.value.display_total || summary.value.total_amount || 0
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

async function updatePaymentTerms() {
  formError.value = null
  const payload = {
    payment_terms: form.value.payment_terms.map(t => ({
      term_desc: t.term_desc || '',
      duration_due: (t.duration_due === 'none' || !t.duration_due) ? '' : t.duration_due,
      duration_due_percent: Number(t.percentage) || 0,
      amount: Number(t.amount) || 0,
      due_date: t.due_date || null
    }))
  }
  try {
    await store.patchPO(props.editId, payload)
    if (store.error) throw new Error()
    Swal.fire({
      icon: 'success',
      title: 'Success!',
      text: 'Payment Terms updated successfully.',
      showConfirmButton: false,
      timer: 1500
    })
    emit('saved')
    closeModal()
  } catch (err) {
    formError.value = store.error || 'Failed to update Payment Terms.'
  }
}

async function updatePartialCancelation() {
  formError.value = null
  const payload = {
    partial_cancellation: form.value.partial_cancellation
  }
  try {
    await store.patchPO(props.editId, payload)
    if (store.error) throw new Error()
    Swal.fire({
      icon: 'success',
      title: 'Success!',
      text: 'PO Cancelation updated successfully.',
      showConfirmButton: false,
      timer: 1500
    })
    emit('saved')
    closeModal()
  } catch (err) {
    formError.value = store.error || 'Failed to update Cancelation.'
  }
}

async function savePO(isDraft = false) {
  formError.value = null
  for (let row of form.value.details) {
    if (!row.item || row.quantity <= 0) {
      formError.value = "All items must be selected and have a quantity greater than 0."
      return
    }
  }

  const payload = {
    project: form.value.project,
    requestor_department: form.value.department,
    po_type: form.value.po_type,
    print_out_type: form.value.print_out_type,
    po_date: form.value.po_date,
    rap: form.value.rap,
    vendor: form.value.vendor,
    pr_class: form.value.pr_class,
    repetition: form.value.repetition,
    ppn: form.value.ppn,
    is_subcontract: form.value.is_subcontract,
    subcontract_notes: form.value.subcontract_notes,
    term_and_condition: form.value.term_and_condition,
    mandatory_update_material: form.value.mandatory_update_material,
    vendor_so_number: form.value.vendor_so_number,
    is_sister_company: form.value.is_sister_company,
    paid_amount: form.value.paid_amount,
    etd: form.value.etd || null,
    delivery_point: form.value.delivery_point,
    notes: form.value.notes,
    details: form.value.details.map(d => ({
      pr_detail: d.pr_detail_id || null,
      rap_detail: d.rap_detail_id || null,
      item: d.item,
      quantity: d.quantity,
      unit_price: d.unit_price,
      tax1: d.tax1 || 'none',
      tax2: d.tax2 || 'none',
      total_price: d.total_price,
      notes: d.notes
    })),
    payment_terms: form.value.payment_terms.map(t => ({
      term_desc: t.term_desc || '',
      duration_due: (t.duration_due === 'none' || !t.duration_due) ? '' : t.duration_due,
      duration_due_percent: Number(t.percentage) || 0,
      amount: Number(t.amount) || 0,
      due_date: t.due_date || null
    })),
    document_status: 'draft' // Always save as draft first before submitting
  }

  try {
    let savedPo;
    if (props.mode === 'add') {
      savedPo = await store.createPO(payload)
    } else {
      savedPo = await store.updatePO(props.editId, payload)
    }
    
    if (store.error) throw new Error()

    // If it's a submission (isDraft is false), call submitPO
    if (!isDraft) {
      await store.submitPO(savedPo.id || props.editId)
      if (store.error) {
        Swal.fire({
          icon: 'error',
          title: 'Submit Failed',
          text: typeof store.error === 'string' ? store.error : 'Gagal submit PO ke Approval.'
        })
        return // Stop closing the modal if submit fails, allow user to retry
      }
    }

    Swal.fire({
      icon: 'success',
      title: 'Success',
      text: isDraft ? 'PO saved as Draft' : 'PO Submitted to Approval successfully!',
    })
    closeModal()
    emit('saved')
  } catch (e) {
    console.error(e)
    if (store.error) {
      let errorMsg = typeof store.error === 'string' ? store.error : JSON.stringify(store.error)
      if (typeof store.error === 'object') {
        const errors = []
        for (const [key, val] of Object.entries(store.error)) {
          if (Array.isArray(val)) {
            errors.push(`${key}: ${val.join(', ')}`)
          } else {
            errors.push(`${key}: ${val}`)
          }
        }
        errorMsg = errors.join('\n')
      }
      Swal.fire({
        icon: 'error',
        title: 'Error Saving PO',
        text: errorMsg
      })
      formError.value = errorMsg
    } else {
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: e.response?.data ? JSON.stringify(e.response.data) : "Failed to save Purchase Order."
      })
      formError.value = "Failed to save Purchase Order."
    }
  }
}

watch(() => props.show, async (newVal) => {
  if (newVal) {
    if (props.mode === 'add') {
      if (!projectStore.projects.length) {
        await projectStore.fetchProjects().catch(() => {})
      }
      await purchaseStore.fetchVendors().catch(() => {})
      await fetchDepartments().catch(() => {})
      resetForm()
      if (authStore.employee && authStore.employee.department_id) {
        form.value.department = authStore.employee.department_id
      }
    } else if (props.mode === 'edit' && props.editId) {
      try {
        if (!projectStore.projects.length) {
          await projectStore.fetchProjects().catch(() => {})
        }
        await purchaseStore.fetchVendors().catch(() => {})
        await fetchDepartments().catch(() => {})
        const poDetails = await store.fetchPODetails(props.editId)
        
        if (!purchaseStore.vendors.find(v => v.id === (poDetails.vendor?.id || poDetails.vendor))) {
          purchaseStore.vendors.push({
            id: poDetails.vendor?.id || poDetails.vendor,
            name: poDetails.vendor_name || 'Selected Vendor'
          })
        }
        
        if (!availableDepartments.value.find(d => d.id === (poDetails.requestor_department?.id || poDetails.requestor_department))) {
          const deptId = poDetails.requestor_department?.id || poDetails.requestor_department;
          if (deptId) {
            availableDepartments.value.push({
              id: deptId,
              name: poDetails.department_name || 'Selected Department'
            })
          }
        }

        form.value.po_number = poDetails.po_number
        form.value.pr_number = poDetails.pr_number
        form.value.po_type = poDetails.po_type || 'RM'
        form.value.print_out_type = poDetails.print_out_type || 'po'
        form.value.project = poDetails.project?.id || poDetails.project
        
        let resolvedDept = poDetails.requestor_department?.id || poDetails.requestor_department;
        if (!resolvedDept && !authStore.isSuperuser && authStore.employee?.department_id) {
          resolvedDept = authStore.employee.department_id;
        }
        form.value.department = resolvedDept;
        
        form.value.po_date = poDetails.po_date
        form.value.rap = poDetails.rap?.id || poDetails.rap
        form.value.vendor = poDetails.vendor?.id || poDetails.vendor
        form.value.pr_class = poDetails.pr_class
        form.value.repetition = poDetails.repetition
        form.value.ppn = poDetails.ppn || false
        form.value.is_subcontract = poDetails.is_subcontract || false
        form.value.subcontract_notes = poDetails.subcontract_notes || ''
        form.value.term_and_condition = poDetails.term_and_condition || ''
        form.value.mandatory_update_material = poDetails.mandatory_update_material || false
        form.value.vendor_so_number = poDetails.vendor_so_number || ''
        form.value.is_sister_company = poDetails.is_sister_company || false
        form.value.paid_amount = Number(poDetails.paid_amount) || 0
        form.value.etd = poDetails.etd
        form.value.delivery_point = poDetails.delivery_point
        form.value.notes = poDetails.notes
        form.value.partial_cancellation = Number(poDetails.partial_cancellation) || 0
        form.value.approval_status = poDetails.approval_status || 'draft'
        form.value.details = poDetails.details.map(d => ({
          id: d.id,
          pr_detail_id: d.pr_detail?.id || d.pr_detail,
          rap_detail_id: d.rap_detail?.id || d.rap_detail,
          item: d.item?.id || d.item,
          item_name: d.item_name || (d.item ? d.item.item_name : ''),
          item_code: d.item_code || (d.item ? d.item.item_code : ''),
          quantity: d.quantity,
          unit_price: Number(d.unit_price),
          tax1: d.tax1 || 'none',
          tax2: d.tax2 || 'none',
          total_price: Number(d.total_price),
          notes: d.notes,
          max_quantity: d.rap_detail?.remaining_volume + d.quantity
        }))
        form.value.payment_terms = poDetails.payment_terms.map(t => ({
          term_desc: t.term_desc,
          duration_due: t.duration_due || 'none',
          percentage: Number(t.duration_due_percent),
          amount: Number(t.amount),
          due_date: t.due_date,
          doc_reff: t.doc_reff || ''
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
