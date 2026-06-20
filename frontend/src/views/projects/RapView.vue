<template>
  <Panel title="Rencana Anggaran Pelaksana (RAP)" subtitle="Project | RAP | List of RAP">

    <!-- Toolbar/Search/Filter -->
    <div class="flex flex-col gap-4 mb-6">
      <div class="flex flex-wrap items-center gap-4">
        <!-- Search -->
        <div class="flex items-center border border-gray-200 rounded-lg overflow-hidden bg-white">
          <span class="px-3 py-1.5 bg-gray-50 text-xs text-gray-500 border-r border-gray-200">Search</span>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Type RAP Number or Project..."
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
          <!-- RAP Status Dropdown -->
          <div class="flex items-center gap-2">
            <span class="text-gray-500 font-semibold">RAP Status:</span>
            <select v-model="filterIsActive" class="border border-gray-200 rounded px-2 py-1 bg-white focus:outline-none h-[34px]" @change="handleSearch">
              <option value="">All</option>
              <option value="true">Active</option>
              <option value="false">Not Active</option>
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
          v-if="canCreate"
          @click="openAddModal"
          class="btn-primary text-xs flex items-center gap-1.5"
        >
          <Plus class="w-3.5 h-3.5" /> Add RAP
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="store.loading" class="flex justify-center py-16">
      <Loader2 class="w-6 h-6 animate-spin text-bfs-gold" />
    </div>

    <!-- Table List -->
    <div v-else-if="store.raps.length" class="border border-gray-200 rounded-xl overflow-hidden bg-white shadow-sm">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-gray-50 border-b border-gray-200 text-[11px] font-semibold text-gray-600 uppercase tracking-wider">
              <th class="py-3 px-4 w-12 text-center">No.</th>
              <th class="py-3 px-4">Cost of Unit</th>
              <th class="py-3 px-4">RAP Number</th>
              <th class="py-3 px-4">Year Period</th>
              <th class="py-3 px-4">RAP Date</th>
              <th class="py-3 px-4">Project</th>
              <th class="py-3 px-4 text-right">Cost</th>
              <th class="py-3 px-4">RAP Type</th>
              <th class="py-3 px-4 text-center">Status</th>
              <th class="py-3 px-4 text-center">Approval</th>
              <th class="py-3 px-4 text-center">Is Active</th>
              <th class="py-3 px-4 w-20 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr
              v-for="(rap, idx) in store.raps"
              :key="rap.id"
              class="hover:bg-yellow-50/20 transition-colors text-xs text-gray-700"
            >
              <td class="py-3 px-4 text-center font-medium text-gray-400">{{ idx + 1 }}.</td>
              <td class="py-3 px-4 font-semibold text-gray-800">{{ rap.position_name }}</td>
              <td class="py-3 px-4 font-mono text-gray-600">{{ rap.rap_number }}</td>
              <td class="py-3 px-4">{{ rap.year_period }}</td>
              <td class="py-3 px-4">{{ formatDate(rap.rap_date) }}</td>
              <td class="py-3 px-4 truncate max-w-[200px]" :title="rap.project_name">
                <span class="font-semibold text-gray-700">[{{ rap.project_code }}]</span> {{ rap.project_name }}
              </td>
              <td class="py-3 px-4 text-right font-semibold text-bfs-gold">{{ formatCurrency(rap.total_cost) }}</td>
              <td class="py-3 px-4 truncate max-w-[120px]" :title="rap.rap_type_name">{{ rap.rap_type_name }}</td>
              <td class="py-3 px-4 text-center">
                <div
                  class="inline-flex items-center justify-center p-1 rounded-md"
                  :title="'Document Status: ' + formatDocStatusText(rap.document_status)"
                >
                  <Folder v-if="rap.document_status === 'draft'" class="w-4.5 h-4.5 text-amber-500 fill-amber-500/10" />
                  <FolderOpen v-else-if="rap.document_status === 'ready_to_process'" class="w-4.5 h-4.5 text-blue-500 fill-blue-500/10" />
                  <FolderCheck v-else-if="rap.document_status === 'close'" class="w-4.5 h-4.5 text-green-500 fill-green-500/10" />
                </div>
              </td>
              <td class="py-3 px-4 text-center">
                <button
                  @click="openPrintPreview(rap)"
                  class="inline-flex items-center justify-center p-1 rounded-md hover:bg-gray-100 transition-colors cursor-pointer"
                  :title="'Click to view Print Preview. Status: ' + formatAppStatusText(rap.approval_status)"
                >
                  <FileText v-if="rap.approval_status === 'draft'" class="w-4.5 h-4.5 text-gray-400" />
                  <FileClock v-else-if="rap.approval_status === 'awaiting'" class="w-4.5 h-4.5 text-bfs-gold animate-pulse" />
                  <FileCheck v-else-if="rap.approval_status === 'approved'" class="w-4.5 h-4.5 text-green-500" />
                  <FileX v-else-if="rap.approval_status === 'rejected'" class="w-4.5 h-4.5 text-red-500" />
                  <FileWarning v-else-if="rap.approval_status === 'revised'" class="w-4.5 h-4.5 text-orange-500" />
                </button>
              </td>
              <td class="py-3 px-4 text-center">
                <span v-if="rap.is_active" class="text-green-500 font-bold text-base">✓</span>
                <span v-else class="text-red-500 font-bold text-base">✗</span>
              </td>
              <td class="py-3 px-4 text-right">
                <div class="flex justify-end gap-1.5">
                  <button
                    v-if="canUpdate && rap.document_status === 'draft'"
                    @click="handleDirectSubmit(rap)"
                    class="p-1 text-gray-400 hover:text-green-600 transition-colors"
                    title="Submit RAP"
                  >
                    <Send class="w-3.5 h-3.5" />
                  </button>
                  <button
                    v-if="canUpdate && rap.document_status === 'draft'"
                    @click="openEditModal(rap)"
                    class="p-1 text-gray-400 hover:text-bfs-gold transition-colors"
                    title="Edit"
                  >
                    <Pencil class="w-3.5 h-3.5" />
                  </button>
                  <button
                    v-if="canDelete && rap.document_status === 'draft'"
                    @click="confirmDelete(rap)"
                    class="p-1 text-gray-400 hover:text-red-500 transition-colors"
                    title="Delete"
                  >
                    <Trash2 class="w-3.5 h-3.5" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="flex flex-col items-center justify-center py-20 text-gray-400">
      <FileText class="w-12 h-12 mb-3 text-gray-300" />
      <p class="text-sm">No RAP data found.</p>
      <button v-if="canCreate" @click="openAddModal" class="mt-3 text-sm text-bfs-gold hover:underline">
        Create the first RAP
      </button>
    </div>

    <!-- Add/Edit Modal (Large Modal for RAP Budgeting) -->
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
                    {{ modal.mode === 'add' ? 'Project | RAP | Add' : 'Project | RAP | Edit' }}
                  </h3>
                  <p v-if="modal.mode === 'edit'" class="text-xs text-gray-500 font-mono">
                    RAP Number: {{ form.rap_number }}
                  </p>
                </div>
                <button @click="closeModal" class="text-gray-400 hover:text-gray-600">
                  <X class="w-5 h-5" />
                </button>
              </div>

              <!-- Form Error Alert -->
              <div v-if="formError.serverError.value" class="mx-6 mt-4 px-4 py-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
                <AlertCircle class="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
                <p class="text-sm text-red-600">{{ formError.serverError.value }}</p>
              </div>

              <!-- Modal Form Content -->
              <div class="px-6 py-4 space-y-6">
                <!-- Header Fields (2-col grid) -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 bg-gray-50/50 p-4 rounded-xl border border-gray-100">
                  <!-- RAP Type -->
                  <FormField label="RAP Type" required :error="formError.fieldErrors.rap_type">
                    <SearchableSelect
                      v-model="form.rap_type"
                      :options="store.rapTypes"
                      label-key="name"
                      placeholder="— Pilih RAP Type —"
                    />
                  </FormField>

                  <!-- Date -->
                  <FormField label="RAP Date" required :error="formError.fieldErrors.rap_date">
                    <input v-model="form.rap_date" type="date" class="form-input" />
                  </FormField>

                  <!-- Month Period -->
                  <FormField label="Month Period" required :error="formError.fieldErrors.month_period">
                    <SearchableSelect
                      v-model="form.month_period"
                      :options="monthChoices"
                      value-key="value"
                      label-key="label"
                      placeholder="— Pilih Month Period —"
                    />
                  </FormField>

                  <!-- Year Period -->
                  <FormField label="Year Period" required :error="formError.fieldErrors.year_period">
                    <SearchableSelect
                      v-model="form.year_period"
                      :options="searchableYearChoices"
                      placeholder="— Pilih Year Period —"
                    />
                  </FormField>

                  <!-- Cost Category -->
                  <FormField label="Cost Category" required :error="formError.fieldErrors.cost_category">
                    <SearchableSelect
                      v-model="form.cost_category"
                      :options="costCategoryChoices"
                      placeholder="— Pilih Cost Category —"
                      @change="onCostCategoryChange"
                    />
                  </FormField>

                  <!-- Department -->
                  <FormField label="Department" required :error="formError.fieldErrors.department">
                    <SearchableSelect
                      v-model="form.department"
                      :options="departmentChoices"
                      label-key="name"
                      :label-fn="formatDeptLabel"
                      placeholder="— Pilih Department —"
                      :disabled="!authStore.isSuperuser"
                      @change="onDepartmentChange"
                    />
                  </FormField>

                  <!-- Cost of Unit (Position) -->
                  <FormField label="Cost of Unit" required :error="formError.fieldErrors.position">
                    <SearchableSelect
                      v-model="form.position"
                      :options="positionChoices"
                      label-key="name"
                      :disabled="!authStore.isSuperuser || !form.department"
                      placeholder="— Pilih Position —"
                      @change="onPositionChange"
                    />
                  </FormField>

                  <!-- Budget Component -->
                  <FormField label="Budget Component" required :error="formError.fieldErrors.budget_component">
                    <SearchableSelect
                      v-model="form.budget_component"
                      :options="activeBudgetComponents"
                      label-key="name"
                      :disabled="!activeBudgetComponents.length"
                      placeholder="— Pilih Budget Component —"
                      @change="onBudgetComponentChange"
                    />
                  </FormField>

                  <!-- Activity -->
                  <FormField label="Activity" required :error="formError.fieldErrors.activity">
                    <SearchableSelect
                      v-model="form.activity"
                      :options="activityChoices"
                      placeholder="— Pilih Activity —"
                    />
                  </FormField>

                  <!-- Project -->
                  <FormField label="Project" required :error="formError.fieldErrors.project">
                    <SearchableSelect
                      v-model="form.project"
                      :options="store.projects"
                      label-key="project_name"
                      :label-fn="formatProjectLabel"
                      placeholder="— Pilih Project —"
                    />
                  </FormField>
                </div>

                <!-- Template Trigger -->
                <div class="flex items-center justify-between pb-2 border-b border-gray-100">
                  <h4 class="text-sm font-semibold text-gray-700 flex items-center gap-2">
                    <Table2 class="w-4 h-4 text-bfs-gold" />
                    Anggaran Rencana RAP Detail
                  </h4>
                  <button
                    type="button"
                    @click="loadTemplateRAP"
                    :disabled="!form.budget_component || isFetchingTemplate"
                    class="px-4 py-2 bg-bfs-navy hover:bg-bfs-navy-dark text-white text-xs font-semibold rounded-lg disabled:opacity-50 flex items-center gap-1.5 cursor-pointer"
                  >
                    <Loader2 v-if="isFetchingTemplate" class="w-3.5 h-3.5 animate-spin" />
                    <DownloadCloud v-else class="w-3.5 h-3.5" />
                    Get Template RAP
                  </button>
                </div>

                <!-- Detail Table -->
                <div v-if="form.details.length" class="border border-gray-200 rounded-xl overflow-hidden bg-white shadow-sm">
                  <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse">
                      <thead>
                        <tr class="bg-gray-50 border-b border-gray-200 text-[11px] font-semibold text-gray-600 uppercase tracking-wider">
                          <th class="py-2.5 px-4 w-16 text-center">No.</th>
                          <th class="py-2.5 px-4 w-1/4">COA Header</th>
                          <th class="py-2.5 px-4 w-1/4">Item Category</th>
                          <th class="py-2.5 px-4">Description</th>
                          <th class="py-2.5 px-4 w-20">Unit</th>
                          <th class="py-2.5 px-4 w-28 text-right">Volume</th>
                          <th class="py-2.5 px-4 w-36 text-right">Unit Price</th>
                          <th class="py-2.5 px-4 w-36 text-right">Total Cost</th>
                        </tr>
                      </thead>
                      <tbody class="divide-y divide-gray-100 text-xs">
                        <tr
                          v-for="row in form.details"
                          :key="row.temp_id"
                          :class="{
                            'bg-gray-100/70 font-semibold text-gray-800': row.item_type === 'header',
                            'bg-gray-50/50 font-medium text-gray-700': row.item_type === 'sub_header',
                            'hover:bg-yellow-50/10 text-gray-600': row.item_type === 'item'
                          }"
                        >
                          <!-- No. -->
                          <td class="py-2 px-4 text-center font-mono text-gray-400">
                            {{ row.display_number }}
                          </td>
                          <!-- COA Header / Section Name -->
                          <td class="py-2 px-4">
                            <span v-if="row.item_type === 'header'" class="uppercase font-bold text-bfs-navy">
                              {{ row.description }}
                            </span>
                            <span v-else-if="row.item_type === 'sub_header'" class="pl-2 font-medium text-gray-600">
                              {{ row.description }}
                            </span>
                          </td>
                          <!-- Item Category / Name -->
                          <td class="py-2 px-4">
                            <span v-if="row.item_type === 'item'">
                              {{ row.item_name }} <span class="text-gray-400 font-mono">[{{ row.item_code }}]</span>
                            </span>
                          </td>
                          <!-- Description / Remarks -->
                          <td class="py-2 px-4">
                            <input
                              v-if="row.item_type === 'item'"
                              v-model="row.remarks"
                              type="text"
                              class="form-input-table"
                              placeholder="Keterangan item..."
                            />
                          </td>
                          <!-- Unit -->
                          <td class="py-2 px-4">
                            <span v-if="row.item_type === 'item'" class="font-semibold text-gray-500 uppercase">
                              {{ row.unit_name }}
                            </span>
                          </td>
                          <!-- Volume -->
                          <td class="py-2 px-4 text-right">
                            <input
                              v-if="row.item_type === 'item'"
                              v-model.number="row.volume"
                              type="number"
                              min="0"
                              step="any"
                              class="form-input-table text-right font-mono min-w-[80px]"
                              @input="calculateRowTotal(row)"
                            />
                          </td>
                          <!-- Unit Price -->
                          <td class="py-2 px-4 text-right">
                            <input
                              v-if="row.item_type === 'item'"
                              v-model="row.unit_price"
                              type="number"
                              min="0"
                              step="any"
                              class="form-input-table text-right font-mono min-w-[150px]"
                              @input="calculateRowTotal(row)"
                            />
                          </td>
                          <!-- Total Cost -->
                          <td class="py-2 px-4 text-right font-semibold font-mono text-gray-800">
                            {{ formatCurrency(row.total_cost) }}
                          </td>
                        </tr>
                        <!-- Grand Total Footer -->
                        <tr class="bg-gray-100/80 font-bold border-t-2 border-gray-200">
                          <td colspan="7" class="py-3 px-4 text-right uppercase text-xs tracking-wider">Grand Total:</td>
                          <td class="py-3 px-4 text-right text-sm font-extrabold text-bfs-gold font-mono">
                            {{ formatCurrency(calculatedGrandTotal) }}
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>

                <div v-else class="text-center py-10 bg-gray-50 rounded-xl border border-dashed border-gray-200 text-gray-400 text-xs">
                  Belum ada item anggaran. Silakan pilih Budget Component dan klik "Get Template RAP" di atas.
                </div>
              </div>

              <!-- Modal Actions -->
              <div class="flex justify-end gap-2 px-6 py-4 border-t border-gray-100 bg-gray-50 rounded-b-2xl">
                <button @click="closeModal" class="btn-secondary text-sm">Cancel</button>
                <button @click="handleSubmit('draft')" :disabled="isSaving" class="btn-secondary text-sm flex items-center gap-1.5 bg-white border border-gray-200 text-gray-700 hover:bg-gray-50">
                  <Loader2 v-if="isSaving" class="w-3.5 h-3.5 animate-spin" />
                  <Save v-else class="w-3.5 h-3.5" />
                  Save Draft
                </button>
                <button @click="handleSubmit('confirm')" :disabled="isSaving" class="btn-primary text-sm flex items-center gap-1.5">
                  <Loader2 v-if="isSaving" class="w-3.5 h-3.5 animate-spin" />
                  <Send v-else class="w-3.5 h-3.5" />
                  Save Confirm
                </button>
              </div>

            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Delete Confirmation Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="deleteModal.show" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-black/40" @click="deleteModal.show = false" />
          <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6 z-10">
            <div class="flex flex-col items-center text-center gap-3">
              <div class="w-12 h-12 rounded-full bg-red-100 flex items-center justify-center">
                <Trash2 class="w-6 h-6 text-red-500" />
              </div>
              <h3 class="text-base font-semibold text-gray-800">Delete RAP?</h3>
              <p class="text-sm text-gray-500">
                Are you sure you want to delete RAP <span class="font-mono font-semibold text-gray-700">"{{ deleteModal.target?.rap_number }}"</span>? This action cannot be undone.
              </p>
            </div>
            <div v-if="deleteModal.error" class="mt-3 px-4 py-2 bg-red-50 border border-red-200 rounded-lg">
              <p class="text-sm text-red-600 text-center">{{ deleteModal.error }}</p>
            </div>
            <div class="flex gap-2 mt-5">
              <button @click="deleteModal.show = false" class="btn-secondary text-sm flex-1">Cancel</button>
              <button
                @click="handleDelete"
                :disabled="isSaving"
                class="flex-1 text-sm py-2 px-4 bg-red-500 hover:bg-red-600 text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-1.5 disabled:opacity-60 cursor-pointer"
              >
                <Loader2 v-if="isSaving" class="w-3.5 h-3.5 animate-spin" />
                <Trash2 v-else class="w-3.5 h-3.5" />
                Delete
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Print Preview Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="printModal.show" class="fixed inset-0 z-50 flex items-center justify-center p-4 print-modal-overlay">
          <div class="absolute inset-0 bg-black/60 print:hidden" @click="printModal.show = false" />
          <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-[210mm] max-h-[95vh] overflow-y-auto z-10 border border-gray-100 flex flex-col print-modal-container">
            
            <!-- Toolbar (Hidden on print) -->
            <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between bg-bfs-navy text-white rounded-t-2xl print:hidden">
              <h3 class="text-sm font-bold flex items-center gap-2 uppercase tracking-wide">
                <Printer class="w-4 h-4 text-bfs-gold" />
                Print Preview RAP
              </h3>
              <div class="flex items-center gap-2">
                <button 
                  @click="printDocument" 
                  class="px-4 py-1.5 bg-bfs-gold hover:bg-bfs-gold/95 text-white text-xs font-semibold rounded-lg flex items-center gap-1.5 transition-colors cursor-pointer"
                >
                  <Printer class="w-3.5 h-3.5" />
                  Print A4
                </button>
                <button @click="printModal.show = false" class="text-white/80 hover:text-white transition-colors">
                  <X class="w-5 h-5" />
                </button>
              </div>
            </div>

            <!-- Print Document Area (A4 layout styling) -->
            <div id="print-area" class="p-8 bg-white flex-1 text-xs text-gray-800 space-y-6 select-text overflow-y-auto">
              
              <!-- Top Header & Logo -->
              <div class="flex items-start justify-between border border-gray-300 p-4 bg-white">
                <div class="space-y-1.5 flex-1 pr-4">
                  <h2 class="text-center font-bold text-base text-gray-900 border-b border-gray-300 pb-1 uppercase tracking-wide">
                    Rencana Anggaran Pelaksana (RAP)
                  </h2>
                  <div class="text-center font-mono font-bold text-sm tracking-widest text-gray-700">
                    {{ printModal.rap?.rap_number }}
                  </div>
                </div>
                <!-- Company Logo -->
                <div class="shrink-0 flex flex-col items-center">
                  <img v-if="orgStore.company?.logo_url" :src="orgStore.company.logo_url" alt="Company Logo" class="h-12 w-auto object-contain" />
                  <img v-else src="/bfs-logo.png" alt="Company Logo" class="h-12 w-auto object-contain" />
                  <span class="text-[8px] font-bold text-gray-400 mt-1 uppercase">{{ orgStore.company?.company_name || 'BFS ERP' }}</span>
                </div>
              </div>

              <!-- Metadata Table (Grid Layout) -->
              <div class="border border-gray-300 bg-white grid grid-cols-2 divide-x divide-gray-300 text-[10px]">
                <div class="p-3 space-y-1">
                  <div class="flex"><span class="w-32 text-gray-500">Departemen / Unit</span><span class="px-1">:</span><span class="font-bold flex-1">{{ printModal.rap?.department_name }}</span></div>
                  <div class="flex"><span class="w-32 text-gray-500">RAP Code</span><span class="px-1">:</span><span class="font-mono flex-1">{{ printModal.rap?.cost_category?.toUpperCase() }}/{{ printModal.rap?.month_period }}/{{ printModal.rap?.year_period }}</span></div>
                  <div class="flex"><span class="w-32 text-gray-500">Budget</span><span class="px-1">:</span><span class="font-bold uppercase flex-1">{{ printModal.rap?.cost_category }}</span></div>
                  <div class="flex"><span class="w-32 text-gray-500">Budget Component</span><span class="px-1">:</span><span class="flex-1">{{ printModal.rap?.budget_component_name }}</span></div>
                  <div class="flex"><span class="w-32 text-gray-500">Cost of Unit</span><span class="px-1">:</span><span class="flex-1">{{ printModal.rap?.position_name }}</span></div>
                </div>
                <div class="p-3 space-y-1">
                  <div class="flex"><span class="w-24 text-gray-500">RAP Name</span><span class="px-1">:</span><span class="flex-1 font-semibold">{{ printModal.rap?.rap_type_name }}</span></div>
                  <div class="flex"><span class="w-24 text-gray-500">Location</span><span class="px-1">:</span><span class="flex-1">BFS MAIN BRANCH</span></div>
                  <div class="flex"><span class="w-24 text-gray-500">RAP Date</span><span class="px-1">:</span><span class="flex-1">{{ formatDate(printModal.rap?.rap_date) }}</span></div>
                  <div class="flex"><span class="w-24 text-gray-500">Period</span><span class="px-1">:</span><span class="flex-1 font-semibold">{{ formatMonthName(printModal.rap?.month_period) }}</span></div>
                  <div class="flex"><span class="w-24 text-gray-500">Activity</span><span class="px-1">:</span><span class="flex-1 capitalize">{{ printModal.rap?.activity }}</span></div>
                </div>
              </div>

              <!-- Details Table -->
              <div class="border border-gray-300 rounded overflow-hidden">
                <table class="w-full text-left border-collapse text-[10px]">
                  <thead>
                    <tr class="bg-gray-100 text-gray-700 font-bold border-b border-gray-300 uppercase tracking-wider text-[9px]">
                      <th class="py-2 px-2 border border-gray-300 w-12 text-center">No</th>
                      <th class="py-2 px-2 border border-gray-300 w-1/4">COA Header</th>
                      <th class="py-2 px-2 border border-gray-300 w-1/4">Item Category</th>
                      <th class="py-2 px-2 border border-gray-300">Description</th>
                      <th class="py-2 px-2 border border-gray-300 w-14 text-center">UoM</th>
                      <th class="py-2 px-2 border border-gray-300 w-16 text-right">Quantity</th>
                      <th class="py-2 px-2 border border-gray-300 w-24 text-right">Unit Price</th>
                      <th class="py-2 px-2 border border-gray-300 w-24 text-right">Total Cost</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-gray-200">
                    <template v-for="header in structuredDetails" :key="header.id">
                      <!-- Header Row -->
                      <tr class="bg-gray-50 font-bold">
                        <td class="py-1.5 px-2 text-center border border-gray-300 font-mono">{{ header.display_number }}</td>
                        <td class="py-1.5 px-2 border border-gray-300 uppercase">{{ header.description }}</td>
                        <td class="py-1.5 px-2 border border-gray-300" colspan="5"></td>
                        <td class="py-1.5 px-2 text-right border border-gray-300 font-mono"></td>
                      </tr>
                      
                      <template v-for="sub in header.subheaders" :key="sub.id">
                        <!-- Subheader Row -->
                        <tr class="font-semibold text-gray-700 bg-gray-50/40">
                          <td class="py-1.5 px-2 text-center border border-gray-300 font-mono">{{ sub.display_number }}</td>
                          <td class="py-1.5 px-2 pl-4 border border-gray-300">{{ sub.description }}</td>
                          <td class="py-1.5 px-2 border border-gray-300" colspan="5"></td>
                          <td class="py-1.5 px-2 text-right border border-gray-300 font-mono"></td>
                        </tr>
                        
                        <!-- Item Rows -->
                        <tr v-for="item in sub.items" :key="item.id" class="text-gray-600 bg-white">
                          <td class="py-1.5 px-2 text-center border border-gray-300 font-mono">{{ item.display_number }}</td>
                          <td class="py-1.5 px-2 border border-gray-300"></td>
                          <td class="py-1.5 px-2 border border-gray-300">{{ item.item_name }} <span class="text-gray-400 font-mono">[{{ item.item_code }}]</span></td>
                          <td class="py-1.5 px-2 border border-gray-300">{{ item.remarks || '-' }}</td>
                          <td class="py-1.5 px-2 text-center border border-gray-300 uppercase">{{ item.unit_name || '-' }}</td>
                          <td class="py-1.5 px-2 text-right border border-gray-300 font-mono">{{ Number(item.volume) }}</td>
                          <td class="py-1.5 px-2 text-right border border-gray-300 font-mono">{{ formatCurrency(item.unit_price) }}</td>
                          <td class="py-1.5 px-2 text-right border border-gray-300 font-mono">{{ formatCurrency(item.total_cost) }}</td>
                        </tr>
                        
                        <!-- Sub Total Row (for subheader) -->
                        <tr class="font-bold text-gray-600 bg-gray-100/10">
                          <td class="py-1.5 px-2 border border-gray-300" colspan="2"></td>
                          <td class="py-1.5 px-2 text-right border border-gray-300 font-semibold uppercase tracking-wider" colspan="5">Sub Total</td>
                          <td class="py-1.5 px-2 text-right border border-gray-300 font-mono font-bold">{{ formatCurrency(sub.total_cost) }}</td>
                        </tr>
                      </template>
                      
                      <!-- Total [No] Row (for header) -->
                      <tr class="font-bold text-gray-700 bg-gray-100/20">
                        <td class="py-1.5 px-2 border border-gray-300" colspan="2"></td>
                        <td class="py-1.5 px-2 text-right border border-gray-300 font-bold uppercase tracking-wider" colspan="5">Total {{ header.display_number }}</td>
                        <td class="py-1.5 px-2 text-right border border-gray-300 font-mono font-extrabold">{{ formatCurrency(header.total_cost) }}</td>
                      </tr>
                    </template>
                    
                    <!-- Grand Total Row -->
                    <tr class="bg-gray-100 font-extrabold text-gray-900 border-t-2 border-gray-400">
                      <td class="py-2.5 px-2 border border-gray-300" colspan="2"></td>
                      <td class="py-2.5 px-2 text-right border border-gray-300 uppercase tracking-wide text-xs" colspan="5">
                        Total {{ structuredDetails.map(h => h.display_number).join(' + ') }}
                      </td>
                      <td class="py-2.5 px-2 text-right border border-gray-300 font-mono text-sm text-bfs-gold font-black">
                        {{ formatCurrency(printGrandTotal) }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- Document Signatures Box -->
              <div v-if="printModal.rap && printModal.rap.document_status !== 'draft'" class="mt-6 border border-gray-300 bg-white p-4">
                <div class="text-[9px] uppercase font-bold text-gray-400 mb-3 tracking-wider">Document Signatures (Persetujuan Dokumen)</div>
                <div class="flex flex-wrap gap-4 justify-start">
                  <div 
                    v-for="sig in printModal.signatures" 
                    :key="sig.id"
                    class="border border-gray-300 rounded p-3 text-center min-w-[150px] flex flex-col justify-between h-[130px] bg-white"
                  >
                    <!-- Header Position -->
                    <div>
                      <div class="text-[8px] uppercase font-bold text-gray-500 tracking-wider">
                        {{ sig.role_display }}
                      </div>
                      <div class="text-[9px] font-semibold text-gray-700">
                        {{ sig.position_name }}
                      </div>
                    </div>

                    <!-- Signature Area -->
                    <div class="flex-1 flex items-center justify-center py-1.5 h-12">
                      <!-- ONLY display signature if document is closed (approved) AND the step is signed -->
                      <template v-if="printModal.rap.document_status === 'close' && sig.is_signed">
                        <img 
                          v-if="sig.signature_draw && sig.signature_draw.startsWith('data:image')" 
                          :src="sig.signature_draw" 
                          alt="Signature" 
                          class="max-h-10 object-contain mx-auto" 
                        />
                        <img 
                          v-else-if="sig.signature_image" 
                          :src="sig.signature_image" 
                          alt="Signature" 
                          class="max-h-10 object-contain mx-auto" 
                        />
                        <div 
                          v-else 
                          class="px-2 py-0.5 border border-green-500 rounded text-[8px] text-green-600 font-serif italic font-bold border-double scale-95"
                        >
                          SIGNED DIGITALLY
                        </div>
                      </template>
                      <!-- Otherwise, if ready to process, keep it blank for wet signature -->
                      <template v-else-if="printModal.rap.document_status === 'ready_to_process'">
                        <div class="text-[8px] text-gray-300 italic">
                          (Wet Signature Area)
                        </div>
                      </template>
                    </div>

                    <!-- Signer Footer -->
                    <div class="border-t border-gray-100 pt-1 text-[8px] text-gray-600">
                      <div class="font-bold truncate" :title="sig.signer_employee_name">
                        {{ sig.signer_employee_name || sig.signer_name || '(Pending)' }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>

            </div>

            <!-- Footer (Hidden on print) -->
            <div class="px-6 py-4 border-t border-gray-100 bg-gray-50 rounded-b-2xl flex justify-end gap-2 print:hidden">
              <button 
                @click="printModal.show = false" 
                class="px-5 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold rounded-xl text-sm transition-colors cursor-pointer"
              >
                Close
              </button>
            </div>

          </div>
        </div>
      </Transition>
    </Teleport>

  </Panel>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useProjectsStore } from '../../stores/projects.js'
import { useOrganizationStore } from '../../stores/organization.js'
import { useBudgetComponentStore } from '../../stores/budgetComponent.js'
import { useApprovalRequestStore } from '../../stores/approvalRequest.js'
import { useAuthStore } from '../../stores/auth.js'
import { usePermission } from '../../composables/usePermission.js'
import { useFormError } from '../../composables/useFormError.js'
import Panel from '../../components/Panel.vue'
import FormField from '../../components/FormField.vue'
import { useToast } from '../../composables/useToast.js'
import { Plus, Pencil, Trash2, Save, X, Loader2, Search, FileText, AlertCircle, Table2, DownloadCloud, UserMinus, Folder, FolderOpen, FolderCheck, FileClock, FileCheck, FileX, FileWarning, Send, Printer } from 'lucide-vue-next'
import SearchableSelect from '../../components/SearchableSelect.vue'

const store = useProjectsStore()
const orgStore = useOrganizationStore()
const budgetStore = useBudgetComponentStore()
const approvalStore = useApprovalRequestStore()
const authStore = useAuthStore()

const { canCreate, canUpdate, canDelete } = usePermission('PROJECTS-RAP')
const formError = useFormError()
const isSaving = ref(false)
const isFetchingTemplate = ref(false)
const toast = useToast()

// Date helpers for current month defaults
const getFirstDayOfMonth = () => {
  const date = new Date()
  const y = date.getFullYear()
  const m = date.getMonth()
  return new Date(y, m, 1).toLocaleDateString('en-CA') // YYYY-MM-DD
}

const getLastDayOfMonth = () => {
  const date = new Date()
  const y = date.getFullYear()
  const m = date.getMonth()
  return new Date(y, m + 1, 0).toLocaleDateString('en-CA') // YYYY-MM-DD
}

// Filter state
const searchQuery = ref('')
const filterDateFrom = ref(getFirstDayOfMonth())
const filterDateTo = ref(getLastDayOfMonth())
const filterIsActive = ref('')
const filterDocStatus = ref('')
const filterAppStatus = ref('')

// Choices
const monthChoices = [
  { value: 1, label: 'January' }, { value: 2, label: 'February' }, { value: 3, label: 'March' },
  { value: 4, label: 'April' }, { value: 5, label: 'May' }, { value: 6, label: 'June' },
  { value: 7, label: 'July' }, { value: 8, label: 'August' }, { value: 9, label: 'September' },
  { value: 10, label: 'October' }, { value: 11, label: 'November' }, { value: 12, label: 'December' }
]

const yearChoices = computed(() => {
  const currentYear = new Date().getFullYear()
  const years = []
  for (let y = currentYear - 2; y <= currentYear + 5; y++) {
    years.push(y)
  }
  return years
})

const searchableYearChoices = computed(() => {
  return yearChoices.value.map(y => ({ id: y, label: String(y) }))
})

const costCategoryChoices = [
  { id: 'hpp', label: 'HPP' },
  { id: 'revenue', label: 'REVENUE' },
  { id: 'target_hpp', label: 'TARGET_HPP' },
  { id: 'target_opex', label: 'TARGET_OPEX' },
  { id: 'opex', label: 'OPEX' },
  { id: 'capex', label: 'CAPEX' },
  { id: 'tax', label: 'TAX' }
]

const activityChoices = [
  { id: 'not_set', label: 'Not Set' },
  { id: 'investasi', label: 'Investasi' },
  { id: 'operating', label: 'Operating' },
  { id: 'financing', label: 'Financing' }
]

const formatDeptLabel = (dept) => {
  return '\u00A0\u00A0'.repeat(dept.level || 0) + dept.name
}

const formatProjectLabel = (proj) => {
  return `[${proj.project_code}] ${proj.project_name}`
}

// Department and Positions
const positions = ref([])

const departmentChoices = computed(() => {
  if (authStore.isSuperuser) {
    return orgStore.departmentList
  }
  const userDeptId = authStore.user?.employee?.department_id
  if (userDeptId) {
    return orgStore.departmentList.filter(d => d.id === userDeptId)
  }
  return []
})

const positionChoices = computed(() => {
  if (authStore.isSuperuser) {
    return positions.value
  }
  const userPosId = authStore.user?.employee?.position_id
  if (userPosId) {
    return positions.value.filter(p => p.id === userPosId)
  }
  return []
})

async function onDepartmentChange() {
  form.position = ''
  form.budget_component = ''
  positions.value = []
  if (form.department) {
    try {
      positions.value = await budgetStore.fetchPositionsByDepartment(form.department)
    } catch (e) {
      toast.error('Failed to load positions.')
    }
  }
}

function onPositionChange() {
  form.budget_component = ''
}

function onCostCategoryChange() {
  form.budget_component = ''
}

// Active Budget Components matches current selections
const activeBudgetComponents = computed(() => {
  if (!form.cost_category || !form.department) return []
  return budgetStore.budgetComponents.filter(bc => {
    const ccMatch = bc.cost_category === form.cost_category
    const deptMatch = bc.department === form.department
    const posMatch = !form.position || bc.position === form.position
    return ccMatch && deptMatch && posMatch && bc.is_active
  })
})

function onBudgetComponentChange() {
  // Clear details if budget component changes
  form.details = []
}

function recalculateAllTotals() {
  // First, calculate all items
  form.details.forEach(row => {
    if (row.item_type === 'item') {
      const vol = typeof row.volume === 'string' ? parseFloat(row.volume) : (row.volume || 0)
      const price = typeof row.unit_price === 'string' ? parseFloat(row.unit_price) : (row.unit_price || 0)
      row.total_cost = (isNaN(vol) ? 0 : vol) * (isNaN(price) ? 0 : price)
    }
  })

  // Second, calculate all sub_headers from their items
  form.details.forEach(row => {
    if (row.item_type === 'sub_header') {
      const childItems = form.details.filter(r => r.parent_temp_id === row.temp_id && r.item_type === 'item')
      row.total_cost = childItems.reduce((sum, item) => sum + (item.total_cost || 0), 0)
    }
  })

  // Third, calculate all headers from their sub_headers
  form.details.forEach(row => {
    if (row.item_type === 'header') {
      const childSubHeaders = form.details.filter(r => r.parent_temp_id === row.temp_id && r.item_type === 'sub_header')
      row.total_cost = childSubHeaders.reduce((sum, sh) => sum + (sh.total_cost || 0), 0)
    }
  })
}

async function loadTemplateRAP() {
  if (!form.budget_component) return
  isFetchingTemplate.value = true
  try {
    const templateData = await store.fetchTemplateRap(form.budget_component)
    if (templateData && templateData.details) {
      // Map flat template details for UI editor
      form.details = templateData.details.map(d => ({
        temp_id: d.id, // we map id to temp_id to reconstruct parent-child links on save
        parent_temp_id: d.parent,
        item_type: d.item_type,
        description: d.description,
        item: d.item,
        item_name: d.item_name,
        item_code: d.item_code,
        unit_name: d.unit_name,
        remarks: d.remarks || '',
        volume: 0,
        unit_price: Number(d.unit_price) || 0,
        total_cost: 0,
        order_no: d.order_no,
        display_number: d.display_number
      }))
      recalculateAllTotals()
      toast.success('Template RAP successfully loaded.')
    } else {
      toast.warning('Template RAP details are empty.')
    }
  } catch (e) {
    console.error(e)
    toast.error(e.response?.data?.detail || 'Failed to load template RAP.')
  } finally {
    isFetchingTemplate.value = false
  }
}

function calculateRowTotal(row) {
  if (row.item_type === 'item') {
    recalculateAllTotals()
  }
}

const calculatedGrandTotal = computed(() => {
  return form.details.filter(row => row.item_type === 'item').reduce((sum, row) => sum + (row.total_cost || 0), 0)
})

function handleSearch() {
  const params = {}
  if (searchQuery.value.trim()) params.search = searchQuery.value.trim()
  if (filterDateFrom.value) params.date_from = filterDateFrom.value
  if (filterDateTo.value) params.date_to = filterDateTo.value
  if (filterIsActive.value) params.is_active = filterIsActive.value
  if (filterDocStatus.value) params.document_status = filterDocStatus.value
  if (filterAppStatus.value) params.approval_status = filterAppStatus.value

  store.fetchRaps(params)
}

function handleResetFilters() {
  searchQuery.value = ''
  filterDateFrom.value = getFirstDayOfMonth()
  filterDateTo.value = getLastDayOfMonth()
  filterIsActive.value = ''
  filterDocStatus.value = ''
  filterAppStatus.value = ''
  handleSearch()
}

// ── Modal & Form ──
const modal = reactive({ show: false, mode: 'add', editId: null })
const form = reactive({
  rap_number: '',
  rap_type: '',
  rap_date: new Date().toISOString().substring(0, 10),
  month_period: new Date().getMonth() + 1,
  year_period: new Date().getFullYear(),
  cost_category: '',
  department: '',
  position: '',
  budget_component: '',
  activity: 'not_set',
  project: '',
  details: []
})

function closeModal() {
  modal.show = false
  formError.clearErrors()
}

async function openAddModal() {
  await store.fetchProjects({ without_rap: true, status: 'not_start' })
  modal.show = true
  modal.mode = 'add'
  modal.editId = null
  formError.clearErrors()
  
  // Reset fields
  form.rap_number = ''
  form.rap_type = ''
  form.rap_date = new Date().toISOString().substring(0, 10)
  form.month_period = new Date().getMonth() + 1
  form.year_period = new Date().getFullYear()
  form.cost_category = ''
  form.department = ''
  form.position = ''
  form.budget_component = ''
  form.activity = 'not_set'
  form.project = ''
  form.details = []
  
  positions.value = []

  // Pre-fill if not superuser
  if (!authStore.isSuperuser && authStore.user?.employee) {
    const emp = authStore.user.employee
    form.department = emp.department_id
    if (emp.department_id) {
      try {
        positions.value = await budgetStore.fetchPositionsByDepartment(emp.department_id)
        form.position = emp.position_id
      } catch (e) {
        toast.error('Failed to load positions.')
      }
    }
  }
}

async function openEditModal(rap) {
  await store.fetchProjects({ without_rap: true, include_project: rap.project, status: 'not_start' })
  modal.show = true
  modal.mode = 'edit'
  modal.editId = rap.id
  formError.clearErrors()

  // Pre-load positions for selected department
  positions.value = []
  if (rap.department) {
    try {
      positions.value = await budgetStore.fetchPositionsByDepartment(rap.department)
    } catch (e) {
      console.error(e)
    }
  }

  form.rap_number = rap.rap_number
  form.rap_type = rap.rap_type
  form.rap_date = rap.rap_date
  form.month_period = rap.month_period
  form.year_period = rap.year_period
  form.cost_category = rap.cost_category
  form.department = rap.department
  form.position = rap.position
  form.budget_component = rap.budget_component
  form.activity = rap.activity
  form.project = rap.project
  
  // Map details for editor
  form.details = rap.details.map(d => ({
    id: d.id,
    temp_id: d.id, // keep it unique
    parent_temp_id: d.parent,
    item_type: d.item_type,
    description: d.description,
    item: d.item,
    item_name: d.item_name,
    item_code: d.item_code,
    unit_name: d.unit_name,
    remarks: d.remarks || '',
    volume: Number(d.volume),
    unit_price: Number(d.unit_price),
    total_cost: Number(d.total_cost),
    order_no: d.order_no,
    display_number: d.display_number
  }))
  recalculateAllTotals()
}

function validate() {
  formError.clearErrors()
  let valid = true
  
  if (!form.rap_type) {
    formError.fieldErrors.rap_type = 'RAP Type is required.'
    valid = false
  }
  if (!form.rap_date) {
    formError.fieldErrors.rap_date = 'RAP Date is required.'
    valid = false
  }
  if (!form.month_period) {
    formError.fieldErrors.month_period = 'Month Period is required.'
    valid = false
  }
  if (!form.year_period) {
    formError.fieldErrors.year_period = 'Year Period is required.'
    valid = false
  }
  if (!form.cost_category) {
    formError.fieldErrors.cost_category = 'Cost Category is required.'
    valid = false
  }
  if (!form.department) {
    formError.fieldErrors.department = 'Department is required.'
    valid = false
  }
  if (!form.position) {
    formError.fieldErrors.position = 'Cost of Unit is required.'
    valid = false
  }
  if (!form.budget_component) {
    formError.fieldErrors.budget_component = 'Budget Component is required.'
    valid = false
  }
  if (!form.project) {
    formError.fieldErrors.project = 'Project is required.'
    valid = false
  }
  if (form.details.length === 0) {
    toast.error('Details RAP cannot be empty. Please click Get Template RAP.')
    valid = false
  }

  return valid
}

async function handleSubmit(action = 'draft') {
  if (!validate()) return
  isSaving.value = true
  try {
    const payload = {
      rap_type: form.rap_type,
      rap_date: form.rap_date,
      month_period: form.month_period,
      year_period: form.year_period,
      cost_category: form.cost_category,
      department: form.department,
      position: form.position,
      budget_component: form.budget_component,
      activity: form.activity,
      project: form.project,
      details: form.details.map(row => ({
        temp_id: row.temp_id,
        parent_temp_id: row.parent_temp_id,
        item_type: row.item_type,
        description: row.description,
        item: row.item,
        remarks: row.remarks,
        volume: row.volume || 0,
        unit_price: row.unit_price || 0,
        order_no: row.order_no
      }))
    }

    let savedRap = null
    if (modal.mode === 'add') {
      savedRap = await store.createRap(payload)
      toast.success('RAP Draft successfully created.')
    } else {
      savedRap = await store.updateRap(modal.editId, payload)
      toast.success('RAP Draft successfully updated.')
    }

    if (action === 'confirm' && savedRap && savedRap.id) {
      toast.info('Submitting RAP for finalization...')
      await store.submitRap(savedRap.id)
      toast.success('RAP successfully submitted and finalized.')
    }

    modal.show = false
    await handleSearch()
  } catch (err) {
    formError.parseApiError(err)
    toast.error(err?.response?.data?.detail || 'Failed to save RAP.')
  } finally {
    isSaving.value = false
  }
}

// ── Delete ──
const deleteModal = reactive({ show: false, target: null, error: '' })

function confirmDelete(rap) {
  deleteModal.target = rap
  deleteModal.error = ''
  deleteModal.show = true
}

async function handleDelete() {
  isSaving.value = true
  deleteModal.error = ''
  try {
    await store.deleteRap(deleteModal.target.id)
    deleteModal.show = false
    toast.success('RAP successfully deleted.')
    await handleSearch()
  } catch (err) {
    deleteModal.error = err?.response?.data?.detail || 'Failed to delete RAP.'
    toast.error('Failed to delete RAP.')
  } finally {
    isSaving.value = false
  }
}

async function handleDirectSubmit(rap) {
  if (confirm(`Apakah Anda yakin ingin memfinalisasi RAP dengan nomor ${rap.rap_number}?`)) {
    isSaving.value = true
    try {
      await store.submitRap(rap.id)
      toast.success('RAP successfully submitted and finalized.')
      await handleSearch()
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Failed to submit RAP.')
    } finally {
      isSaving.value = false
    }
  }
}

const printModal = reactive({
  show: false,
  rap: null,
  signatures: [],
  isLoadingSignatures: false
})

async function openPrintPreview(rap) {
  printModal.rap = rap
  printModal.show = true
  printModal.signatures = []
  
  if (rap.document_status !== 'draft') {
    printModal.isLoadingSignatures = true
    try {
      const sigs = await approvalStore.fetchSignatures('RAP', rap.id)
      printModal.signatures = sigs
    } catch (e) {
      console.error(e)
    } finally {
      printModal.isLoadingSignatures = false
    }
  }
}

function printDocument() {
  window.print()
}

function formatMonthName(m) {
  const months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
  return months[m - 1] || m;
}

const structuredDetails = computed(() => {
  if (!printModal.rap || !printModal.rap.details) return []
  
  const headers = []
  const details = printModal.rap.details
  
  const headerRows = details.filter(d => d.item_type === 'header')
  headerRows.forEach(h => {
    const headerNode = {
      ...h,
      subheaders: []
    }
    
    const subheaderRows = details.filter(d => d.item_type === 'sub_header' && d.parent === h.id)
    subheaderRows.forEach(sh => {
      const rawItems = details.filter(d => d.item_type === 'item' && d.parent === sh.id)
      const filteredItems = rawItems.filter(item => {
        const qty = Number(item.volume || 0)
        const price = Number(item.unit_price || 0)
        return !(qty === 0 && price === 0)
      }).map(item => ({
        ...item,
        total_cost: Number(item.volume || 0) * Number(item.unit_price || 0)
      }))

      const subTotal = filteredItems.reduce((sum, item) => sum + item.total_cost, 0)
      
      const subheaderNode = {
        ...sh,
        items: filteredItems,
        total_cost: subTotal
      }
      headerNode.subheaders.push(subheaderNode)
    })
    
    const headerTotal = headerNode.subheaders.reduce((sum, sh) => sum + sh.total_cost, 0)
    headerNode.total_cost = headerTotal
    
    headers.push(headerNode)
  })
  
  return headers
})

const printGrandTotal = computed(() => {
  return structuredDetails.value.reduce((sum, h) => sum + h.total_cost, 0)
})

// Formatters & Badges
function formatCurrency(val) {
  if (val === undefined || val === null) return 'Rp 0'
  const parsed = typeof val === 'string' ? parseFloat(val) : val
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(parsed)
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return d.toLocaleDateString('id-ID', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  })
}

function getDocStatusClass(status) {
  switch (status) {
    case 'draft': return 'bg-gray-100 text-gray-700 border border-gray-200'
    case 'ready_to_process': return 'bg-blue-50 text-blue-700 border border-blue-200'
    case 'close': return 'bg-green-50 text-green-700 border border-green-200'
    default: return 'bg-gray-50 text-gray-500 border border-gray-200'
  }
}

function getAppStatusClass(status) {
  switch (status) {
    case 'draft': return 'bg-gray-100 text-gray-700 border border-gray-200'
    case 'awaiting': return 'bg-bfs-gold/10 text-bfs-gold border border-bfs-gold/20'
    case 'approved': return 'bg-green-50 text-green-700 border border-green-200'
    case 'rejected': return 'bg-red-50 text-red-700 border border-red-200'
    case 'revised': return 'bg-orange-50 text-orange-700 border border-orange-200'
    default: return 'bg-gray-50 text-gray-500 border border-gray-200'
  }
}

function formatDocStatusText(status) {
  switch (status) {
    case 'draft': return 'Draft'
    case 'ready_to_process': return 'Ready to Process'
    case 'close': return 'Close'
    default: return status
  }
}

function formatAppStatusText(status) {
  switch (status) {
    case 'draft': return 'Draft'
    case 'awaiting': return 'Awaiting Approval'
    case 'approved': return 'Approved'
    case 'rejected': return 'Rejected'
    case 'revised': return 'Revised'
    default: return status
  }
}

onMounted(() => {
  handleSearch()
  store.fetchRapTypes()
  store.fetchProjects({ without_rap: true, status: 'not_start' })
  orgStore.fetchDepartments()
  budgetStore.fetchBudgetComponents()
  if (!orgStore.company) orgStore.fetchCompany()
})
</script>

<style scoped>
@reference "../../style.css";
.form-input {
  @apply w-full px-3 py-2 text-xs border border-gray-200 rounded-lg
         focus:outline-none focus:ring-2 focus:ring-bfs-gold/40 focus:border-bfs-gold
         transition-all bg-white disabled:bg-gray-50 disabled:cursor-not-allowed;
}
.form-input-table {
  @apply w-full px-2 py-1 text-xs border border-gray-200 rounded
         focus:outline-none focus:ring-2 focus:ring-bfs-gold/40 focus:border-bfs-gold
         transition-all bg-white;
}
.btn-primary {
  @apply px-4 py-2 bg-bfs-gold hover:bg-bfs-gold-dark text-white font-medium rounded-lg transition-colors disabled:opacity-60 cursor-pointer;
}
.btn-secondary {
  @apply px-4 py-2 border border-gray-200 text-gray-600 hover:bg-gray-50 rounded-lg transition-colors cursor-pointer;
}
.modal-enter-active, .modal-leave-active { transition: opacity 0.2s; }
.modal-enter-from, .modal-leave-to { opacity: 0; }

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
