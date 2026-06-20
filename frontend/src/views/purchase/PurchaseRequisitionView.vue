<template>
  <Panel title="Purchase Requisition (PR)" subtitle="Purchase | Purchase Requisition">
    
    <!-- Toolbar/Search/Filter -->
    <div class="flex flex-col gap-4 mb-6">
      <div class="flex flex-wrap items-center gap-4">
        <!-- Search -->
        <div class="flex items-center border border-gray-200 rounded-lg overflow-hidden bg-white">
          <span class="px-3 py-1.5 bg-gray-50 text-xs text-gray-500 border-r border-gray-200">Search</span>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Type PR Number or Project..."
            class="px-3 py-1.5 text-xs focus:outline-none w-48 sm:w-64"
            @keyup.enter="handleSearch"
          />
        </div>

        <!-- Date Range -->
        <div class="flex items-center gap-2 text-xs">
          <span class="text-gray-500 font-semibold uppercase">Date From:</span>
          <input v-model="filterDateFrom" type="date" class="border border-gray-200 rounded px-2 py-1 bg-white text-xs focus:outline-none" />
          <span class="text-gray-500 font-semibold uppercase">To:</span>
          <input v-model="filterDateTo" type="date" class="border border-gray-200 rounded px-2 py-1 bg-white text-xs focus:outline-none" />
        </div>

        <button
          @click="handleSearch"
          class="px-3 py-1.5 bg-bfs-navy hover:bg-bfs-navy-dark text-white text-xs font-medium rounded-lg transition-colors flex items-center gap-1.5 cursor-pointer"
        >
          <Search class="w-3.5 h-3.5" /> Search
        </button>
        <button
          @click="handleResetFilters"
          class="btn-secondary text-xs px-3 py-1.5 flex items-center gap-1.5"
        >
          Reset
        </button>
      </div>

      <div class="flex flex-wrap items-center justify-between gap-4 border-t border-gray-100 pt-4">
        <div class="flex flex-wrap items-center gap-4 text-xs">
          <!-- Item Category Dropdown -->
          <div class="flex items-center gap-2">
            <span class="text-gray-500 font-semibold">Item Category:</span>
            <select v-model="filterItemCategory" class="border border-gray-200 rounded px-2 py-1 bg-white focus:outline-none h-[34px]" @change="handleSearch">
              <option value="">All</option>
              <option value="RM">Raw Material</option>
              <option value="SP">Supplies</option>
              <option value="AST">Asset</option>
            </select>
          </div>

          <!-- Filter Status (Sokka Style) -->
          <div class="border border-gray-200 rounded-lg px-3 py-1.5 relative bg-white flex items-center gap-2 shadow-sm min-h-[38px]">
            <span class="absolute -top-2 left-2 bg-white px-1 text-[9px] font-bold text-gray-500 uppercase tracking-wider">Filter Status</span>
            <button 
              @click="filterDocStatus = ''; handleSearch()" 
              class="px-1.5 py-0.5 rounded text-[10px] font-bold transition-colors cursor-pointer"
              :class="filterDocStatus === '' ? 'bg-bfs-navy text-white' : 'hover:bg-gray-100 text-gray-400'"
              title="All Status"
            >
              ALL
            </button>
            <button 
              @click="filterDocStatus = 'draft'; handleSearch()" 
              class="p-0.5 rounded transition-all cursor-pointer"
              :class="filterDocStatus === 'draft' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"
              title="Draft (Editable)"
            >
              <Folder class="w-4 h-4 text-amber-500 fill-amber-500/10" />
            </button>
            <button 
              @click="filterDocStatus = 'ready_to_process'; handleSearch()" 
              class="p-0.5 rounded transition-all cursor-pointer"
              :class="filterDocStatus === 'ready_to_process' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"
              title="Ready to Process (Submitted)"
            >
              <FolderOpen class="w-4 h-4 text-blue-500 fill-blue-500/10" />
            </button>
            <button 
              @click="filterDocStatus = 'close'; handleSearch()" 
              class="p-0.5 rounded transition-all cursor-pointer"
              :class="filterDocStatus === 'close' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"
              title="Close (Finalized)"
            >
              <FolderCheck class="w-4 h-4 text-green-500 fill-green-500/10" />
            </button>
          </div>

          <!-- Approval Filter Status (Sokka Style) -->
          <div class="border border-gray-200 rounded-lg px-3 py-1.5 relative bg-white flex items-center gap-2 shadow-sm min-h-[38px]">
            <span class="absolute -top-2 left-2 bg-white px-1 text-[9px] font-bold text-gray-500 uppercase tracking-wider">Approval Filter Status</span>
            <button 
              @click="filterAppStatus = ''; handleSearch()" 
              class="px-1.5 py-0.5 rounded text-[10px] font-bold transition-colors cursor-pointer"
              :class="filterAppStatus === '' ? 'bg-bfs-navy text-white' : 'hover:bg-gray-100 text-gray-400'"
              title="All Approval"
            >
              ALL
            </button>
            <button 
              @click="filterAppStatus = 'draft'; handleSearch()" 
              class="p-0.5 rounded transition-all cursor-pointer"
              :class="filterAppStatus === 'draft' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"
              title="Draft"
            >
              <FileText class="w-4 h-4 text-gray-400" />
            </button>
            <button 
              @click="filterAppStatus = 'awaiting'; handleSearch()" 
              class="p-0.5 rounded transition-all cursor-pointer"
              :class="filterAppStatus === 'awaiting' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"
              title="Awaiting Approval"
            >
              <FileClock class="w-4 h-4 text-bfs-gold animate-pulse" />
            </button>
            <button 
              @click="filterAppStatus = 'approved'; handleSearch()" 
              class="p-0.5 rounded transition-all cursor-pointer"
              :class="filterAppStatus === 'approved' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"
              title="Approved"
            >
              <FileCheck class="w-4 h-4 text-green-500" />
            </button>
            <button 
              @click="filterAppStatus = 'rejected'; handleSearch()" 
              class="p-0.5 rounded transition-all cursor-pointer"
              :class="filterAppStatus === 'rejected' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"
              title="Rejected"
            >
              <FileX class="w-4 h-4 text-red-500" />
            </button>
            <button 
              @click="filterAppStatus = 'revised'; handleSearch()" 
              class="p-0.5 rounded transition-all cursor-pointer"
              :class="filterAppStatus === 'revised' ? 'ring-2 ring-bfs-gold ring-offset-1 scale-110' : 'hover:bg-gray-100'"
              title="Revised"
            >
              <FileWarning class="w-4 h-4 text-orange-500" />
            </button>
          </div>
        </div>

        <button
          @click="openAddModal"
          class="px-4 py-2 bg-bfs-gold text-white text-xs font-semibold rounded-lg hover:bg-[#C2A05B] transition-colors shadow-sm flex items-center gap-1.5 ml-auto"
        >
          <Plus class="w-3.5 h-3.5" /> New PR
        </button>
      </div>
    </div>
    
    <!-- Loading -->
    <div v-if="store.loading && !store.prs.length" class="flex justify-center py-16">
      <Loader2 class="w-6 h-6 animate-spin text-bfs-gold" />
    </div>
    
    <!-- Table List -->
    <div v-else-if="store.prs.length" class="border border-gray-200 rounded-xl overflow-hidden bg-white shadow-sm">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-gray-50 border-b border-gray-200 text-[11px] font-semibold text-gray-600 uppercase tracking-wider">
              <th class="py-3 px-4 w-12 text-center">No.</th>
              <th class="py-3 px-4">Purchase Requisition Code</th>
              <th class="py-3 px-4">Purchase Request Date</th>
              <th class="py-3 px-4">RAP Name</th>
              <th class="py-3 px-4">Requestor</th>
              <th class="py-3 px-4">Notes</th>
              <th class="py-3 px-4 text-center">Status</th>
              <th class="py-3 px-4 text-center">Approval</th>
              <th class="py-3 px-4 text-center">PO Created</th>
              <th class="py-3 px-4 text-center">Close PR</th>
              <th class="py-3 px-4 w-20 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="(pr, idx) in store.prs" :key="pr.id" class="hover:bg-yellow-50/20 transition-colors text-xs text-gray-700">
              <td class="py-3 px-4 text-center font-medium text-gray-400">{{ idx + 1 }}.</td>
              <td class="py-3 px-4 font-mono text-gray-600 cursor-pointer hover:text-bfs-navy font-semibold" @click="openEditModal(pr)">{{ pr.pr_number }}</td>
              <td class="py-3 px-4">{{ formatDate(pr.pr_date) }}</td>
              <td class="py-3 px-4 truncate max-w-[200px]" :title="pr.rap_name">{{ pr.rap_name || '-' }}</td>
              <td class="py-3 px-4 font-semibold text-gray-800">{{ pr.department_name }}</td>
              <td class="py-3 px-4 truncate max-w-[150px]">{{ pr.notes || '-' }}</td>
              <td class="py-3 px-4 text-center">
                <div class="inline-flex items-center justify-center p-1 rounded-md" :title="pr.document_status">
                  <Folder v-if="pr.document_status === 'draft'" class="w-4.5 h-4.5 text-amber-500 fill-amber-500/10" />
                  <FolderOpen v-else-if="pr.document_status === 'ready_to_process'" class="w-4.5 h-4.5 text-blue-500 fill-blue-500/10" />
                  <FolderCheck v-else-if="pr.document_status === 'close'" class="w-4.5 h-4.5 text-green-500 fill-green-500/10" />
                </div>
              </td>
              <td class="py-3 px-4 text-center">
                <div class="inline-flex items-center justify-center p-1 rounded-md" :title="pr.approval_status">
                  <FileText v-if="pr.approval_status === 'draft'" class="w-4.5 h-4.5 text-gray-400" />
                  <FileClock v-else-if="pr.approval_status === 'awaiting'" class="w-4.5 h-4.5 text-bfs-gold animate-pulse" />
                  <FileCheck v-else-if="pr.approval_status === 'approved'" class="w-4.5 h-4.5 text-green-500" />
                  <FileX v-else-if="pr.approval_status === 'rejected'" class="w-4.5 h-4.5 text-red-500" />
                  <FileWarning v-else-if="pr.approval_status === 'revised'" class="w-4.5 h-4.5 text-orange-500" />
                </div>
              </td>
              <td class="py-3 px-4 text-center">
                <span v-if="pr.po_created" class="text-green-500 font-bold text-base">✓</span>
                <span v-else class="text-gray-300 font-bold text-base">-</span>
              </td>
              <td class="py-3 px-4 text-center">
                <span v-if="pr.document_status === 'close'" class="text-green-500 font-bold text-base">✓</span>
                <span v-else class="text-gray-300 font-bold text-base">-</span>
              </td>
              <td class="py-3 px-4 text-right">
                <div class="flex justify-end gap-1.5">
                  <button @click="openPrintPreview(pr)" class="p-1 text-gray-400 hover:text-bfs-navy transition-colors" title="Print">
                    <Printer class="w-3.5 h-3.5" />
                  </button>
                  <button @click="openEditModal(pr)" class="p-1 text-gray-400 hover:text-bfs-gold transition-colors" title="Edit">
                    <Pencil class="w-3.5 h-3.5" />
                  </button>
                  <button v-if="pr.document_status === 'draft'" @click="deletePR(pr.id)" class="p-1 text-gray-400 hover:text-red-500 transition-colors" title="Delete">
                    <Trash2 class="w-3.5 h-3.5" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <div v-else class="py-16 text-center text-gray-400">
      <div class="flex flex-col items-center justify-center">
        <FileText class="w-12 h-12 text-gray-200 mb-2" />
        <p>No records found.</p>
      </div>
    </div>

    <!-- Add/Edit PR Form Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="modal.show" class="fixed inset-0 z-50 overflow-y-auto">
          <div class="fixed inset-0 bg-black/40" @click="closeModal" />
          <div class="flex min-h-full items-start justify-center p-4 py-8">
            <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-6xl z-10" @click.stop>
              
              <!-- Modal Header -->
              <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
                <div>
                  <h3 class="text-base font-bold text-gray-800">
                    {{ modal.mode === 'add' ? 'Purchase Requisition | Add' : 'Purchase Requisition | Edit' }}
                  </h3>
                  <p v-if="modal.mode === 'edit'" class="text-xs text-gray-500 font-mono">
                    PR Number: {{ form.pr_number }}
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

              <!-- Modal Form Content -->
              <div class="px-6 py-4 space-y-6">
                <!-- Header Fields (2-col grid) -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 bg-gray-50/50 p-4 rounded-xl border border-gray-100">
                  <!-- PR Type -->
                  <FormField label="PR Type" required>
                    <SearchableSelect
                      v-model="form.pr_type"
                      :options="prTypeChoices"
                      value-key="value"
                      label-key="label"
                      placeholder="— Select Type —"
                      @change="onPrTypeChange"
                      :disabled="modal.mode === 'edit'"
                    />
                  </FormField>

                  <!-- Requestor Department -->
                  <FormField label="Requestor Department" required>
                    <SearchableSelect
                      v-model="form.department"
                      :options="availableDepartments"
                      value-key="id"
                      label-key="name"
                      placeholder="— Select Department —"
                      :disabled="modal.mode === 'edit' || (!authStore.isSuperuser && availableDepartments.length === 1)"
                    />
                  </FormField>

                  <!-- Project (Filtered status=start) -->
                  <FormField label="Project" required>
                    <SearchableSelect
                      v-model="form.project"
                      :options="availableProjects"
                      value-key="id"
                      label-key="project_name"
                      placeholder="— Select Project —"
                      @change="onProjectChange"
                      :disabled="modal.mode === 'edit'"
                    />
                  </FormField>

                  <!-- PR Date -->
                  <FormField label="PR Date" required>
                    <input v-model="form.pr_date" type="date" class="form-input text-xs" />
                  </FormField>

                  <!-- Request Type -->
                  <FormField label="Request Type">
                    <SearchableSelect
                      v-model="form.request_type"
                      :options="requestTypeChoices"
                      value-key="value"
                      label-key="label"
                      placeholder="— Select Request Type —"
                    />
                  </FormField>

                  <!-- PR Class -->
                  <FormField label="Purchase Requisition Class">
                    <SearchableSelect
                      v-model="form.pr_class"
                      :options="prClassChoices"
                      value-key="value"
                      label-key="label"
                      placeholder="— Select PR Class —"
                    />
                  </FormField>

                  <!-- Repetition -->
                  <FormField label="Repetition">
                    <SearchableSelect
                      v-model="form.repetition"
                      :options="repetitionChoices"
                      value-key="value"
                      label-key="label"
                      placeholder="— Select Repetition —"
                    />
                  </FormField>

                  <!-- Estimated Time Delivery (ETD) -->
                  <FormField label="Estimated Date (ETD)">
                    <input v-model="form.etd" type="date" class="form-input text-xs" />
                  </FormField>

                  <!-- Delivery Point -->
                  <FormField label="Delivery Point" class="md:col-span-2">
                    <input v-model="form.delivery_point" type="text" class="form-input text-xs" placeholder="Delivery Point (e.g. pop b)" />
                  </FormField>

                  <!-- Notes -->
                  <FormField label="Notes" class="md:col-span-2">
                    <input v-model="form.notes" type="text" class="form-input text-xs" placeholder="Optional notes..." />
                  </FormField>
                </div>

                <!-- Template / Table Controls -->
                <div class="flex items-center justify-between pb-2 border-b border-gray-100">
                  <h4 class="text-sm font-semibold text-gray-700 flex items-center gap-2">
                    <CheckSquare class="w-4 h-4 text-bfs-gold" />
                    PR Details
                  </h4>
                  <button
                    v-if="form.pr_type !== 'AST'"
                    type="button"
                    @click="addDetailRow"
                    :disabled="!form.project || isFetchingRap"
                    class="btn-secondary text-xs px-3 py-1.5 flex items-center gap-1.5"
                  >
                    <Plus class="w-3.5 h-3.5" /> Add Item
                  </button>
                  <div v-else class="text-xs text-orange-500 italic">
                    Asset Module coming soon.
                  </div>
                </div>

                <!-- Detail Table -->
                <div v-if="form.details.length" class="border border-gray-200 rounded-xl overflow-hidden bg-white shadow-sm">
                  <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse">
                      <thead>
                        <tr class="bg-gray-50 border-b border-gray-200 text-[11px] font-semibold text-gray-600 uppercase tracking-wider">
                          <th class="py-2.5 px-3 w-10 text-center">No.</th>
                          <th class="py-2.5 px-3">Item Selection</th>
                          <th class="py-2.5 px-3 w-32">Notes</th>
                          <th class="py-2.5 px-3 w-28 text-right">Quantity</th>
                          <th class="py-2.5 px-3 w-36 text-right">Unit Price</th>
                          <th class="py-2.5 px-3 w-36 text-right">Total Price</th>
                          <th class="py-2.5 px-3 w-12 text-center">Del</th>
                        </tr>
                      </thead>
                      <tbody class="divide-y divide-gray-100 text-xs">
                        <tr v-for="(row, idx) in form.details" :key="idx" class="hover:bg-yellow-50/20">
                          <td class="py-2 px-3 text-center font-mono text-gray-400">{{ idx + 1 }}</td>
                          
                          <!-- Item Selection -->
                          <td class="py-2 px-3">
                            <SearchableSelect
                              v-model="row.rap_detail_id"
                              :options="getAvailableItemsForRow(row)"
                              value-key="id"
                              :label-fn="opt => `${opt.item_name} (Avail: ${opt.remaining_volume})`"
                              placeholder="— Select RAP Item —"
                              @change="onItemSelect(row)"
                            />
                          </td>

                          <!-- Notes -->
                          <td class="py-2 px-3">
                            <input v-model="row.notes" type="text" class="w-full border border-gray-200 rounded px-2 py-1 text-xs focus:outline-none" placeholder="Item note" />
                          </td>

                          <!-- Quantity -->
                          <td class="py-2 px-3 text-right">
                            <input 
                              v-model.number="row.quantity" 
                              type="number" 
                              min="0" 
                              :max="row.max_quantity"
                              step="0.01"
                              class="w-full border border-gray-200 rounded px-2 py-1 text-xs text-right focus:outline-none" 
                              @input="calculateRowTotal(row)"
                            />
                            <div v-if="row.max_quantity !== null" class="text-[9px] text-gray-400 mt-1 text-right">Max: {{ row.max_quantity }}</div>
                          </td>

                          <!-- Unit Price (Readonly from RAP) -->
                          <td class="py-2 px-3 text-right">
                            <div class="w-full border border-gray-100 bg-gray-50 rounded px-2 py-1 text-xs text-right text-gray-500 cursor-not-allowed">
                              {{ formatCurrency(row.unit_price) }}
                            </div>
                          </td>

                          <!-- Total Price (Calculated) -->
                          <td class="py-2 px-3 text-right font-mono font-semibold text-bfs-navy">
                            {{ formatCurrency(row.total_price) }}
                          </td>

                          <!-- Delete -->
                          <td class="py-2 px-3 text-center">
                            <button @click="removeDetailRow(idx)" class="text-gray-400 hover:text-red-500 p-1">
                              <X class="w-4 h-4" />
                            </button>
                          </td>
                        </tr>
                        
                        <!-- Grand Total Footer -->
                        <tr class="bg-gray-50 border-t-2 border-gray-200 font-bold">
                          <td colspan="5" class="py-3 px-4 text-right uppercase tracking-wider text-gray-600 text-[10px]">
                            Grand Total
                          </td>
                          <td class="py-3 px-4 text-right text-bfs-gold font-mono text-sm">
                            {{ formatCurrency(formGrandTotal) }}
                          </td>
                          <td></td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
                
                <div v-else-if="form.pr_type === 'AST'" class="text-center py-8 text-gray-400 border border-dashed border-gray-300 rounded-xl">
                  Asset requisition items will be added here once Asset module is integrated.
                </div>
                <div v-else class="text-center py-8 text-gray-400 border border-dashed border-gray-300 rounded-xl">
                  Click 'Add Item' to insert request items based on selected Project RAP.
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
                    @click="savePR(false)" 
                    :disabled="store.loading"
                    class="btn-secondary text-sm px-5 flex items-center gap-2"
                  >
                    <Save class="w-4 h-4" /> Save as Draft
                  </button>
                  <button 
                    v-if="!['ready_to_process', 'close'].includes(form.document_status)"
                    @click="savePR(true)" 
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
    </Teleport>


    <!-- Print Preview Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="printModal.show" class="fixed inset-0 z-50 overflow-y-auto print-modal-overlay">
          <div class="fixed inset-0 bg-black/40 print:hidden" @click="printModal.show = false" />
          
          <div class="flex min-h-full items-start justify-center p-4 py-8 print:p-0">
            <div class="relative bg-white shadow-2xl w-full max-w-[210mm] min-h-[297mm] z-10 print-modal-container" @click.stop>
              
              <!-- Web-only Header -->
              <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100 print:hidden sticky top-0 bg-white z-20 shadow-sm">
                <h3 class="text-base font-bold text-gray-800 flex items-center gap-2">
                  <Printer class="w-5 h-5 text-bfs-gold" />
                  Print Preview: {{ printModal.pr?.pr_number }}
                </h3>
                <div class="flex gap-2">
                  <button @click="printDocument" class="btn-primary text-sm px-4 flex items-center gap-2 shadow-md">
                    <Printer class="w-4 h-4" /> Print Document
                  </button>
                  <button @click="printModal.show = false" class="text-gray-400 hover:text-gray-600 bg-gray-100 hover:bg-gray-200 p-2 rounded-lg transition-colors">
                    <X class="w-5 h-5" />
                  </button>
                </div>
              </div>

              <!-- Print Document Content -->
              <div class="p-[10mm] text-[11px] text-black bg-white print:p-0 font-sans">
                
                <!-- Company Header -->
                <div class="flex justify-between items-start mb-6">
                  <div class="leading-tight">
                    <div class="font-bold text-sm">{{ orgStore.company?.company_name || 'PT. Rumah Sakit Jati Rahayu' }}</div>
                    <div class="whitespace-pre-line">{{ printAddress }}</div>
                    <div v-if="orgStore.company?.country || orgStore.company?.state">{{ orgStore.company?.state || '' }} - {{ orgStore.company?.country || 'Indonesia' }}</div>
                    <div>Phone : {{ orgStore.company?.phone || '-' }}</div>
                    <div>Fax : {{ orgStore.company?.fax || '-' }}</div>
                  </div>
                  <div class="flex flex-col items-end">
                    <!-- Right Logo -->
                    <img :src="orgStore.company?.logo || '/bfs-logo.png'" alt="Logo" class="h-16 object-contain" />
                  </div>
                </div>

                <!-- Title Block -->
                <div class="bg-[#b4c6e7] text-black text-center font-bold text-sm py-1 mb-4">
                  Purchase Requisition (ORIGINAL)
                </div>

                <!-- Meta Info Grid -->
                <div class="grid grid-cols-2 gap-x-8 gap-y-1 mb-6">
                  <div>
                    <table class="w-full">
                      <tr><td class="w-36 py-0.5 align-top">PR Number</td><td class="w-4 align-top">:</td><td class="font-medium align-top">{{ printModal.pr?.pr_number }}</td></tr>
                      <tr><td class="py-0.5 align-top">Project Name</td><td class="align-top">:</td><td class="align-top">{{ printModal.pr?.project_name || '-' }}</td></tr>
                      <tr><td class="py-0.5 align-top">RAP Number</td><td class="align-top">:</td><td class="align-top">{{ printModal.pr?.rap_number || printModal.pr?.rap_name || '-' }}</td></tr>
                      <tr><td class="py-0.5 align-top">Purchase Request Date</td><td class="align-top">:</td><td class="align-top">{{ formatDatePrint(printModal.pr?.pr_date) }}</td></tr>
                      <tr><td class="py-0.5 align-top">ETD</td><td class="align-top">:</td><td class="align-top">{{ formatDatePrint(printModal.pr?.etd) }}</td></tr>
                    </table>
                  </div>
                  <div>
                    <table class="w-full">
                      <tr><td class="w-24 py-0.5 align-top">Delivery Point</td><td class="w-4 align-top">:</td><td class="align-top">{{ printModal.pr?.delivery_point || '-' }}</td></tr>
                    </table>
                  </div>
                </div>

                <!-- Details Table -->
                <table class="w-full border-collapse border border-black mb-6">
                  <thead>
                    <tr class="bg-[#b4c6e7] text-black font-bold">
                      <th class="border border-black py-1 px-2 text-center w-8">No.</th>
                      <th class="border border-black py-1 px-2 text-left">Item Name</th>
                      <th class="border border-black py-1 px-2 text-left">Description</th>
                      <th class="border border-black py-1 px-2 text-center">Request quantity</th>
                      <th class="border border-black py-1 px-2 text-center">Unit</th>
                      <th class="border border-black py-1 px-2 text-right">Unit Price</th>
                      <th class="border border-black py-1 px-2 text-right">Final Unit Price</th>
                      <th class="border border-black py-1 px-2 text-right">Amount</th>
                      <th class="border border-black py-1 px-2 text-center">Department</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(item, idx) in printDetails" :key="idx">
                      <td class="border border-black py-1 px-2 text-center align-top">{{ idx + 1 }}.</td>
                      <td class="border border-black py-1 px-2 align-top">{{ item.item_name || item.asset_name }}</td>
                      <td class="border border-black py-1 px-2 align-top">{{ item.notes }}</td>
                      <td class="border border-black py-1 px-2 text-center align-top">{{ item.quantity }}</td>
                      <td class="border border-black py-1 px-2 text-center align-top">{{ item.unit_name || 'Unit' }}</td>
                      <td class="border border-black py-1 px-2 text-right align-top">{{ formatCurrencyRaw(item.unit_price) }}</td>
                      <td class="border border-black py-1 px-2 text-right align-top">{{ formatCurrencyRaw(item.final_unit_price || item.unit_price) }}</td>
                      <td class="border border-black py-1 px-2 text-right align-top">{{ formatCurrencyRaw(item.amount || (item.quantity * item.unit_price)) }}</td>
                      <td class="border border-black py-1 px-2 text-center align-top">{{ printModal.pr?.department_name || 'IT' }}</td>
                    </tr>
                    <tr>
                      <td colspan="7" class="border border-black py-1 px-2 text-right font-bold text-sm">Total</td>
                      <td colspan="2" class="border border-black py-1 px-2 text-left font-bold text-sm">{{ formatCurrencyRaw(printGrandTotal) }}</td>
                    </tr>
                  </tbody>
                </table>

                <!-- Notes -->
                <div class="mb-12">
                  <span class="font-bold text-sm">Notes:</span> <span class="font-bold text-sm ml-2">{{ printModal.pr?.notes || '-' }}</span>
                </div>

                <!-- Signatures -->
                <div class="flex justify-end mt-16 pb-8">
                  <table class="border-collapse border border-black text-center text-xs ml-auto">
                    <tr>
                      <td v-for="sig in printModal.signatures" :key="'pos-'+sig.id" class="border border-black px-2 py-1.5 font-medium w-36 bg-white min-h-[30px] align-middle">
                        {{ sig.position_name }}
                      </td>
                    </tr>
                    <tr>
                      <td v-for="sig in printModal.signatures" :key="'img-'+sig.id" class="border border-black h-24 align-middle bg-white relative p-1">
                        <template v-if="printModal.pr?.document_status === 'close' && sig.is_signed">
                          <img 
                            v-if="sig.signature_draw && sig.signature_draw.startsWith('data:image')" 
                            :src="sig.signature_draw" 
                            alt="Signature" 
                            class="max-h-20 object-contain mx-auto" 
                          />
                          <img 
                            v-else-if="sig.signature_image" 
                            :src="sig.signature_image" 
                            alt="Signature" 
                            class="max-h-20 object-contain mx-auto" 
                          />
                          <div 
                            v-else 
                            class="px-2 py-0.5 border border-green-500 rounded text-[8px] text-green-600 font-serif italic font-bold border-double inline-block"
                          >
                            SIGNED DIGITALLY
                          </div>
                        </template>
                        <template v-else-if="printModal.pr?.document_status === 'ready_to_process'">
                          <div class="text-[8px] text-gray-300 italic">
                            (Wet Signature Area)
                          </div>
                        </template>
                        <span v-else class="text-[9px] text-gray-400 italic">No Signature</span>
                      </td>
                    </tr>
                    <tr>
                      <td v-for="sig in printModal.signatures" :key="'name-'+sig.id" class="border border-black px-2 py-1.5 bg-white font-medium">
                        {{ sig.signer_employee_name || sig.signer_name || '(Pending)' }}
                      </td>
                    </tr>
                  </table>
                </div>

              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </Panel>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { 
  Search, Plus, Loader2, Edit3, Trash2, Send, Pencil, Printer, CheckSquare,
  Folder, FolderOpen, FolderCheck,
  FileText, FileClock, FileCheck, FileX, FileWarning, X, AlertCircle, Save
} from 'lucide-vue-next'
import api from '../../services/api'
import { useAuthStore } from '../../stores/auth'
import { usePurchaseRequisitionStore } from '../../stores/purchaseRequisition'
import { useProjectsStore } from '../../stores/projects'
import { useOrganizationStore } from '../../stores/organization'
import { useApprovalRequestStore } from '../../stores/approvalRequest'
import Panel from '../../components/Panel.vue'
import FormField from '../../components/FormField.vue'
import SearchableSelect from '../../components/SearchableSelect.vue'

const authStore = useAuthStore()
const orgStore = useOrganizationStore()
const approvalStore = useApprovalRequestStore()
const store = usePurchaseRequisitionStore()
const projectStore = useProjectsStore()



// --- PRINT PREVIEW ---
const printModal = ref({
  show: false,
  pr: null,
  signatures: [],
  isLoadingSignatures: false
})

const printDetails = ref([])

async function openPrintPreview(pr) {
  printModal.value.pr = pr
  printModal.value.show = true
  printModal.value.signatures = []
  printDetails.value = []
  
  if (!orgStore.company) {
    orgStore.fetchCompany()
  }
  
  // Fetch full details
  try {
    const fullPr = await store.fetchPRDetails(pr.id)
    printDetails.value = fullPr.details || []
  } catch (e) {
    console.error('Failed to fetch print details', e)
  }

  if (pr.document_status !== 'draft') {
    printModal.value.isLoadingSignatures = true
    try {
      const sigs = await approvalStore.fetchSignatures('PR', pr.id)
      printModal.value.signatures = sigs
    } catch (e) {
      console.error(e)
      printModal.value.signatures = []
    } finally {
      printModal.value.isLoadingSignatures = false
    }
  }
}

const printAddress = computed(() => {
  const addr1 = orgStore.company?.company_address || 'Jl. Raya Hankam No. 17 RT. 003 RW. 000 Kel. Jatirahayu Kec. Pondok Melati Kab. Bekasi Jawa Barat,'
  const addr2 = orgStore.company?.company_address2 || ''
  if (addr2 && addr2.trim().toLowerCase() !== addr1.trim().toLowerCase()) {
    return `${addr1}\n${addr2}`
  }
  return addr1
})

function printDocument() {
  window.print()
}

function formatDatePrint(dateStr) {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

function formatCurrencyRaw(value) {
  if (value == null) return '0.00'
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value)
}

const printGrandTotal = computed(() => {
  return printDetails.value.reduce((sum, item) => sum + (parseFloat(item.amount) || parseFloat(item.quantity) * parseFloat(item.unit_price) || 0), 0)
})

// --- END PRINT PREVIEW ---

// --- LIST STATE ---
const today = new Date()
const firstDay = new Date(today.getFullYear(), today.getMonth(), 1)
const lastDay = new Date(today.getFullYear(), today.getMonth() + 1, 0)

const formatDateStr = (d) => d.toISOString().split('T')[0]

const searchQuery = ref('')
const filterItemCategory = ref('')
const filterDateFrom = ref(formatDateStr(firstDay))
const filterDateTo = ref(formatDateStr(lastDay))

const filterDocStatus = ref('')
const filterAppStatus = ref('')

function handleSearch() {
  store.fetchPRs({
    search: searchQuery.value,
    pr_type: filterItemCategory.value,
    document_status: filterDocStatus.value,
    approval_status: filterAppStatus.value,
    start_date: filterDateFrom.value,
    end_date: filterDateTo.value,
  })
}

function handleResetFilters() {
  searchQuery.value = ''
  filterItemCategory.value = ''
  filterDateFrom.value = formatDateStr(firstDay)
  filterDateTo.value = formatDateStr(lastDay)
  filterDocStatus.value = ''
  filterAppStatus.value = ''
  handleSearch()
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' })
}

function formatCurrency(value) {
  if (value == null) return 'Rp 0'
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value)
}

async function deletePR(id) {
  if (confirm('Are you sure you want to delete this PR?')) {
    try {
      await store.deletePR(id)
      handleSearch()
    } catch (e) {
      alert(store.error || 'Delete failed')
    }
  }
}


// --- MODAL & FORM STATE ---
const modal = ref({
  show: false,
  mode: 'add',
  editId: null
})

const formError = ref(null)
const isFetchingRap = ref(false)

const form = ref({
  pr_number: '',
  pr_type: '',
  project: null,
  department: null,
  pr_date: new Date().toISOString().split('T')[0],
  request_type: 'Normal',
  pr_class: 'Common',
  repetition: 'None',
  etd: '',
  delivery_point: '',
  notes: '',
  document_status: 'draft',
  rap_id: null,
  details: []
})

const prTypeChoices = [
  { value: 'RM', label: 'Raw Material' },
  { value: 'SP', label: 'Supplies' },
  { value: 'AST', label: 'Asset' }
]

const requestTypeChoices = [
  { value: 'Normal', label: 'Normal' },
  { value: 'Urgent', label: 'Urgent' }
]

const prClassChoices = [
  { value: 'Normal', label: 'Normal' },
  { value: 'Sub Contract', label: 'Sub Contract' },
  { value: 'Common', label: 'Common' },
  { value: 'Urgent', label: 'Urgent' }
]

const repetitionChoices = [
  { value: 'None', label: 'None' },
  { value: 'Routine', label: 'Routine' },
  { value: 'Non Routine', label: 'Non Routine' }
]

const availableProjects = computed(() => projectStore.projects.filter(p => p.status === 'start'))
const availableDepartments = ref([])

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
        name: authStore.employee.department
      }]
    } else {
      availableDepartments.value = []
    }
  }
}

// Store extracted RAP items for dropdown
const availableRapItems = ref([])

function closeModal() {
  modal.value.show = false
  formError.value = null
  availableRapItems.value = []
}

function resetForm() {
  form.value = {
    pr_number: '',
    pr_type: '',
    project: null,
    department: (!authStore.isSuperuser && authStore.employee) ? authStore.employee.department_id : null,
    pr_date: new Date().toISOString().split('T')[0],
    request_type: 'Normal',
    pr_class: 'Common',
    repetition: 'None',
    etd: '',
    delivery_point: '',
    notes: '',
    details: []
  }
  availableRapItems.value = []
}

async function openAddModal() {
  resetForm()
  modal.value.mode = 'add'
  modal.value.editId = null
  modal.value.show = true
  
  if (!projectStore.projects.length) {
    await projectStore.fetchProjects()
  }
}

async function openEditModal(pr) {
  resetForm()
  modal.value.mode = 'edit'
  modal.value.editId = pr.id
  
  form.value.pr_number = pr.pr_number
  form.value.pr_type = pr.pr_type
  form.value.project = pr.project
  form.value.department = pr.department
  form.value.pr_date = pr.pr_date
  form.value.request_type = pr.request_type || 'Normal'
  form.value.pr_class = pr.pr_class || 'Common'
  form.value.repetition = pr.repetition || 'None'
  form.value.etd = pr.etd || ''
  form.value.delivery_point = pr.delivery_point || ''
  form.value.notes = pr.notes
  form.value.document_status = pr.document_status
  
  // We must fetch the RAP items first so we know their unit prices & max quantities
  await fetchProjectRAPItems(pr.project)
  
  // Now populate details
  // Note: GET /purchase/pr/{id}/ gives full details
  try {
    const prDetails = await store.fetchPRDetails(pr.id)
    form.value.details = prDetails.details.map(d => {
      // Find RAP item info
      const rapInfo = availableRapItems.value.find(ri => ri.id === d.rap_detail)
      const max_qty = rapInfo ? (rapInfo.remaining_volume + parseFloat(d.quantity)) : parseFloat(d.quantity)
      
      return {
        id: d.id,
        rap_detail_id: d.rap_detail,
        item: d.item,
        notes: d.notes,
        quantity: parseFloat(d.quantity),
        max_quantity: max_qty, // Since we are editing, max_quantity could be tricky if we don't have remaining budget endpoint
        unit_price: parseFloat(d.unit_price),
        total_price: parseFloat(d.amount) || (parseFloat(d.quantity) * parseFloat(d.unit_price))
      }
    })
    modal.value.show = true
  } catch (e) {
    alert('Failed to load PR details')
  }
}

// Fetch RAP when Project changes
async function onProjectChange() {
  form.value.details = [] // Reset details
  if (!form.value.project || form.value.pr_type === 'AST') {
    availableRapItems.value = []
    return
  }
  await fetchProjectRAPItems(form.value.project)
}

function onPrTypeChange() {
  form.value.details = []
  if (form.value.pr_type === 'AST') {
    availableRapItems.value = []
  } else if (form.value.project) {
    fetchProjectRAPItems(form.value.project)
  }
}

async function fetchProjectRAPItems(projectId) {
  isFetchingRap.value = true
  try {
    // We get approved RAPs for this project
    await projectStore.fetchRaps({ project: projectId, approval_status: 'approved', is_active: 'true' })
    if (projectStore.raps.length > 0) {
      // Assuming the API returns the first active approved RAP
      const rap = projectStore.raps[0]
      form.value.rap_id = rap.id
      // Filter only item_type === 'item' AND inventory_item_type matches PR Type
      availableRapItems.value = (rap.details || []).filter(d => 
        d.item_type === 'item' && d.inventory_item_type === form.value.pr_type
      )
    } else {
      form.value.rap_id = null
      availableRapItems.value = []
    }
  } catch (e) {
    console.error(e)
    availableRapItems.value = []
  } finally {
    isFetchingRap.value = false
  }
}

// Table logic
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

function removeDetailRow(idx) {
  form.value.details.splice(idx, 1)
}

function getAvailableItemsForRow(currentRow) {
  // If editing, they might have selected an item that's no longer 'available' in the general list? 
  // Let's just exclude items that are already selected in OTHER rows.
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
    row.item = selectedItem.item
    // Set max_quantity to remaining_volume + (the quantity already entered in this row if we are editing, though usually editing resets it or we handle it in openEditModal)
    // Wait, onItemSelect is triggered when the user picks an item. So current row.quantity is 0.
    row.max_quantity = selectedItem.remaining_volume
    row.unit_price = selectedItem.unit_price
    row.quantity = 0
    row.total_price = 0
  } else {
    row.item = null
    row.max_quantity = null
    row.unit_price = 0
    row.quantity = 0
    row.total_price = 0
  }
}

function calculateRowTotal(row) {
  if (row.max_quantity !== null && row.quantity > row.max_quantity) {
    row.quantity = row.max_quantity // Strict constraint
  }
  row.total_price = row.quantity * row.unit_price
}

const formGrandTotal = computed(() => {
  return form.value.details.reduce((sum, row) => sum + (parseFloat(row.total_price) || 0), 0)
})

async function savePR(submitImmediately = false) {
  formError.value = null
  
  if (!form.value.project || !form.value.pr_type || !form.value.pr_date || !form.value.department) {
    formError.value = "Please fill all required header fields."
    return
  }
  
  if (form.value.pr_type !== 'AST' && form.value.details.length === 0) {
    formError.value = "Please add at least one item."
    return
  }

  // Ensure items have values
  for (let row of form.value.details) {
    if (!row.rap_detail_id || row.quantity <= 0) {
      formError.value = "All items must be selected and have a quantity greater than 0."
      return
    }
  }

  const payload = {
    project: form.value.project,
    department: form.value.department,
    pr_type: form.value.pr_type,
    pr_date: form.value.pr_date,
    rap: form.value.rap_id,
    request_type: form.value.request_type,
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
    }))
  }

  try {
    let savedPrId = null
    if (modal.value.mode === 'add') {
      const res = await store.createPR(payload)
      savedPrId = res.id
    } else {
      await store.updatePR(modal.value.editId, payload)
      savedPrId = modal.value.editId
    }
    
    if (submitImmediately && savedPrId) {
      await store.submitPR(savedPrId)
    }
    
    closeModal()
    handleSearch()
  } catch (e) {
    formError.value = store.error || "Failed to save Purchase Requisition."
  }
}

onMounted(() => {
  projectStore.fetchProjects()
  fetchDepartments()
  handleSearch()
})
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
  body > * {
    display: none !important;
  }
  .print-modal-overlay {
    position: absolute !important;
    left: 0 !important;
    top: 0 !important;
    width: 100% !important;
    height: auto !important;
    background: transparent !important;
    display: block !important;
    z-index: 99999 !important;
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

