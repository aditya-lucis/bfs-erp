<template>
  <Panel title="Annual Budget" subtitle="Finance | Annual Budget">

    <!-- ── Toolbar ─────────────────────────────────────────────────────── -->
    <div class="toolbar">
      <div class="toolbar-left">
        <!-- Year Selector -->
        <div class="year-selector">
          <button class="year-nav" @click="changeYear(-1)">
            <ChevronLeft class="w-4 h-4" />
          </button>
          <span class="year-label">{{ selectedYear }}</span>
          <button class="year-nav" @click="changeYear(1)">
            <ChevronRight class="w-4 h-4" />
          </button>
        </div>

        <!-- Department Filter -->
        <div class="filter-select-wrap">
          <Building2 class="filter-icon" />
          <select v-model="filterDept" @change="loadHeaders" class="filter-select">
            <option value="">All Departments</option>
            <option v-for="d in orgStore.departmentList" :key="d.id" :value="d.id">
              {{ d.name }}
            </option>
          </select>
        </div>
      </div>

      <div class="toolbar-right">
        <button class="btn-secondary" @click="loadSummary">
          <BarChart3 class="w-4 h-4" />
          Summary
        </button>
        <button v-if="canCreate" class="btn-primary" @click="openCreateModal">
          <Plus class="w-4 h-4" />
          New Budget
        </button>
      </div>
    </div>

    <!-- ── Summary Bar ─────────────────────────────────────────────────── -->
    <div v-if="summary" class="summary-bar">
      <div class="summary-card">
        <span class="summary-label">Total Departments</span>
        <span class="summary-value">{{ summary.results?.length ?? 0 }}</span>
      </div>
      <div class="summary-card highlight">
        <span class="summary-label">Grand Total Budget {{ selectedYear }}</span>
        <span class="summary-value">{{ formatCurrency(summary.grand_total) }}</span>
      </div>
      <div class="summary-card">
        <span class="summary-label">Locked</span>
        <span class="summary-value text-amber-500">
          {{ summary.results?.filter(r => r.is_locked).length ?? 0 }}
        </span>
      </div>
    </div>

    <!-- ── Loading ─────────────────────────────────────────────────────── -->
    <div v-if="store.loading" class="loading-state">
      <Loader2 class="w-8 h-8 animate-spin text-bfs-gold" />
      <p class="text-sm text-gray-400 mt-2">Memuat data budget...</p>
    </div>

    <!-- ── Empty ───────────────────────────────────────────────────────── -->
    <div v-else-if="!store.headers.length" class="empty-state">
      <div class="empty-icon">
        <Wallet class="w-10 h-10 text-gray-300" />
      </div>
      <p class="text-gray-500 font-medium">Belum ada Annual Budget untuk {{ selectedYear }}</p>
      <p class="text-gray-400 text-sm mt-1">Klik "New Budget" untuk membuat budget baru per departemen.</p>
      <button v-if="canCreate" class="btn-primary mt-4" @click="openCreateModal">
        <Plus class="w-4 h-4" /> Buat Budget Pertama
      </button>
    </div>

    <!-- ── Budget Cards Grid ────────────────────────────────────────────── -->
    <div v-else class="budget-grid">
      <div
        v-for="header in store.headers"
        :key="header.id"
        class="budget-card"
        :class="{ 'card-locked': header.is_locked }"
        @click="openProcessView(header)"
      >
        <!-- Card Header -->
        <div class="card-top">
          <div class="card-dept-badge">
            <Building2 class="w-3.5 h-3.5" />
            {{ header.department_code }}
          </div>
          <div class="card-status">
            <span v-if="header.is_locked" class="status-locked">
              <Lock class="w-3 h-3" /> Locked
            </span>
            <span v-else class="status-open">
              <Unlock class="w-3 h-3" /> Open
            </span>
          </div>
        </div>

        <!-- Dept Name -->
        <h3 class="card-dept-name">{{ header.department_name }}</h3>
        <p class="card-year">Budget {{ header.year }}</p>

        <!-- Total -->
        <div class="card-total">
          <span class="card-total-label">Total Budget</span>
          <span class="card-total-value">{{ formatCurrency(header.total_annual) }}</span>
        </div>

        <!-- Progress bar: visual fill (normalized) -->
        <div class="card-progress">
          <div class="card-progress-track">
            <div
              class="card-progress-fill"
              :style="{ width: progressWidth(header.total_annual) }"
            />
          </div>
        </div>

        <!-- Meta -->
        <div class="card-meta">
          <span class="card-meta-item">
            <FileText class="w-3 h-3" />
            {{ header.line_count }} components
          </span>
          <button
            class="card-action-btn"
            @click.stop="openProcessView(header)"
          >
            {{ canUpdate && !header.is_locked ? 'Edit' : 'View' }} <ArrowRight class="w-3 h-3" />
          </button>
        </div>
      </div>
    </div>

    <!-- ── Create Header Modal ─────────────────────────────────────────── -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="createModal.show" class="modal-overlay">
          <div class="modal-backdrop" @click="createModal.show = false" />
          <div class="modal-container">
            <div class="modal-box">

              <!-- Modal Header -->
              <div class="modal-header">
                <div class="modal-title-group">
                  <div class="modal-icon-wrap">
                    <Wallet class="w-5 h-5 text-bfs-gold" />
                  </div>
                  <div>
                    <h3 class="modal-title">New Annual Budget</h3>
                    <p class="modal-subtitle">Buat budget per departemen untuk satu tahun</p>
                  </div>
                </div>
                <button class="modal-close" @click="createModal.show = false">
                  <X class="w-5 h-5" />
                </button>
              </div>

              <!-- Error Banner -->
              <div v-if="createModal.error" class="error-banner">
                <AlertCircle class="w-4 h-4 shrink-0" />
                <span>{{ createModal.error }}</span>
              </div>

              <!-- Form -->
              <div class="modal-body">
                <FormField label="Year" required>
                  <input
                    v-model.number="createForm.year"
                    type="number"
                    class="form-input"
                    :min="2020" :max="2099"
                    placeholder="e.g. 2026"
                  />
                </FormField>

                <FormField label="Department" required>
                  <div class="select-wrap">
                    <Building2 class="select-icon" />
                    <select v-model="createForm.department" class="form-input pl-8" :disabled="isFetchingExistingHeaders">
                      <option :value="null">
                        {{ isFetchingExistingHeaders ? 'Loading departments...' : '— Pilih Department —' }}
                      </option>
                      <option v-for="d in availableDepartments" :key="d.id" :value="d.id">
                        {{ d.name }}
                      </option>
                    </select>
                  </div>
                </FormField>

                <FormField label="Notes">
                  <textarea
                    v-model="createForm.notes"
                    class="form-input resize-none"
                    rows="2"
                    placeholder="Keterangan (opsional)..."
                  />
                </FormField>
              </div>

              <!-- Footer -->
              <div class="modal-footer">
                <button class="btn-secondary" @click="createModal.show = false">Cancel</button>
                <button class="btn-primary" @click="handleCreate" :disabled="store.saving">
                  <Loader2 v-if="store.saving" class="w-4 h-4 animate-spin" />
                  <Save v-else class="w-4 h-4" />
                  Create Budget
                </button>
              </div>

            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

  </Panel>

  <!-- ── Process View (slide-over) ─────────────────────────────────────── -->
  <AnnualBudgetProcess
    v-if="processView.show"
    :header="processView.header"
    @close="processView.show = false"
    @saved="onProcessSaved"
  />
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import {
  Plus, X, Save, Loader2, Building2, Wallet, Lock, Unlock,
  FileText, ArrowRight, BarChart3, ChevronLeft, ChevronRight, AlertCircle
} from 'lucide-vue-next'
import { useAnnualBudgetStore } from '../../stores/annualBudget.js'
import { useOrganizationStore } from '../../stores/organization.js'
import { useToast } from '../../composables/useToast.js'
import { usePermission } from '../../composables/usePermission.js'
import api from '../../services/api.js'
import Panel from '../../components/Panel.vue'
import FormField from '../../components/FormField.vue'
import AnnualBudgetProcess from './AnnualBudgetProcess.vue'

const store    = useAnnualBudgetStore()
const orgStore = useOrganizationStore()
const toast    = useToast()
const { canCreate, canUpdate } = usePermission('FINANCE-ANNUAL-BUDGET')

// ── Filters ─────────────────────────────────────────────────────────────────
const selectedYear = ref(new Date().getFullYear())
const filterDept   = ref('')
const summary      = ref(null)

function changeYear(delta) {
  selectedYear.value += delta
  loadHeaders()
  loadSummary()
}

async function loadHeaders() {
  const params = { year: selectedYear.value }
  if (filterDept.value) params.department = filterDept.value
  await store.fetchHeaders(params)
}

async function loadSummary() {
  try {
    summary.value = await store.fetchSummary(selectedYear.value)
  } catch {}
}

// ── Helpers ──────────────────────────────────────────────────────────────────
function formatCurrency(val) {
  if (!val && val !== 0) return 'Rp 0'
  return new Intl.NumberFormat('id-ID', {
    style: 'currency', currency: 'IDR',
    maximumFractionDigits: 0,
  }).format(Number(val))
}

const maxTotal = computed(() => {
  const vals = store.headers.map(h => Number(h.total_annual) || 0)
  return Math.max(...vals, 1)
})

function progressWidth(total) {
  const pct = (Number(total) / maxTotal.value) * 100
  return `${Math.min(pct, 100)}%`
}

// ── Create Modal ─────────────────────────────────────────────────────────────
const createModal = reactive({ show: false, error: '' })
const createForm  = reactive({ year: new Date().getFullYear(), department: null, notes: '' })
const existingHeadersForYear = ref([])
const isFetchingExistingHeaders = ref(false)

async function fetchExistingHeadersForYear(year) {
  if (!year || year < 2020 || year > 2099) {
    existingHeadersForYear.value = []
    return
  }
  isFetchingExistingHeaders.value = true
  try {
    const res = await api.get('/annual-budget/headers/', { params: { year } })
    existingHeadersForYear.value = res.data.results ?? res.data
    // Reset selected department if it is no longer available in the new list
    const existingDeptIds = existingHeadersForYear.value.map(h => h.department)
    if (createForm.department && existingDeptIds.includes(createForm.department)) {
      createForm.department = null
    }
  } catch (err) {
    console.error(err)
  } finally {
    isFetchingExistingHeaders.value = false
  }
}

// Watch createForm.year to fetch list of existing budgets for that year
watch(() => createForm.year, (newYear) => {
  fetchExistingHeadersForYear(newYear)
})

// Filter department list to exclude departments that already have a budget for this year
const availableDepartments = computed(() => {
  if (!orgStore.departmentList) return []
  const existingDeptIds = existingHeadersForYear.value.map(h => h.department)
  return orgStore.departmentList.filter(d => !existingDeptIds.includes(d.id))
})

async function openCreateModal() {
  createModal.show  = true
  createModal.error = ''
  createForm.year   = selectedYear.value
  createForm.department = null
  createForm.notes  = ''
  await fetchExistingHeadersForYear(createForm.year)
}

async function handleCreate() {
  if (!createForm.department) {
    createModal.error = 'Department wajib dipilih.'
    return
  }
  createModal.error = ''
  try {
    await store.createHeader({
      department: createForm.department,
      year:       createForm.year,
      notes:      createForm.notes,
    })
    createModal.show = false
    toast.success('Annual Budget berhasil dibuat.')
    await loadHeaders()
    await loadSummary()
  } catch (err) {
    const data = err?.response?.data
    createModal.error = data?.detail
      || data?.department?.[0]
      || data?.year?.[0]
      || data?.non_field_errors?.[0]
      || 'Gagal membuat budget.'
  }
}

// ── Process View ─────────────────────────────────────────────────────────────
const processView = reactive({ show: false, header: null })

function openProcessView(header) {
  processView.header = header
  processView.show   = true
}

async function onProcessSaved() {
  await loadHeaders()
  await loadSummary()
}

// ── Init ─────────────────────────────────────────────────────────────────────
onMounted(async () => {
  await Promise.all([
    orgStore.fetchDepartments(),
    loadHeaders(),
    loadSummary(),
  ])
})
</script>

<style scoped>
@reference "../../style.css";

/* ── Toolbar ─────────────────────────────────────────────────────────────── */
.toolbar {
  @apply flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6;
}
.toolbar-left  { @apply flex items-center gap-3 flex-wrap; }
.toolbar-right { @apply flex items-center gap-2; }

.year-selector {
  @apply flex items-center gap-1 bg-white border border-gray-200 rounded-xl px-1 py-1 shadow-sm;
}
.year-nav {
  @apply p-1.5 rounded-lg text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-colors;
}
.year-label {
  @apply px-3 text-base font-bold text-gray-800 min-w-[60px] text-center select-none;
}

.filter-select-wrap { @apply relative flex items-center; }
.filter-icon {
  @apply absolute left-2.5 w-4 h-4 text-gray-400 pointer-events-none;
}
.filter-select {
  @apply pl-8 pr-3 py-2 text-sm border border-gray-200 rounded-xl bg-white
         focus:outline-none focus:ring-2 focus:ring-bfs-gold/30 focus:border-bfs-gold
         shadow-sm cursor-pointer;
}

/* ── Summary Bar ─────────────────────────────────────────────────────────── */
.summary-bar {
  @apply grid grid-cols-3 gap-3 mb-6;
}
.summary-card {
  @apply bg-white border border-gray-100 rounded-xl p-4 shadow-sm
         flex flex-col gap-1 transition-all hover:shadow-md;
}
.summary-card.highlight {
  @apply bg-gradient-to-br from-bfs-gold/10 to-bfs-gold/5
         border-bfs-gold/30;
}
.summary-label { @apply text-xs text-gray-500 font-medium uppercase tracking-wide; }
.summary-value { @apply text-xl font-bold text-gray-800; }

/* ── Loading / Empty ─────────────────────────────────────────────────────── */
.loading-state {
  @apply flex flex-col items-center justify-center py-24;
}
.empty-state {
  @apply flex flex-col items-center justify-center py-20 text-center;
}
.empty-icon {
  @apply w-20 h-20 rounded-full bg-gray-100 flex items-center justify-center mb-4;
}

/* ── Budget Cards Grid ───────────────────────────────────────────────────── */
.budget-grid {
  @apply grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4;
}

.budget-card {
  @apply bg-white border border-gray-100 rounded-2xl p-5 shadow-sm
         cursor-pointer transition-all duration-200
         hover:shadow-lg hover:-translate-y-0.5 hover:border-bfs-gold/30
         flex flex-col gap-3;
}
.budget-card.card-locked {
  @apply bg-gray-50/60 border-gray-200;
}

.card-top {
  @apply flex items-center justify-between;
}
.card-dept-badge {
  @apply inline-flex items-center gap-1.5 px-2.5 py-1
         bg-bfs-gold/10 text-bfs-gold rounded-lg text-xs font-bold uppercase tracking-wide;
}
.status-locked {
  @apply inline-flex items-center gap-1 px-2 py-0.5
         bg-amber-100 text-amber-700 rounded-full text-xs font-medium;
}
.status-open {
  @apply inline-flex items-center gap-1 px-2 py-0.5
         bg-emerald-100 text-emerald-700 rounded-full text-xs font-medium;
}

.card-dept-name {
  @apply text-base font-bold text-gray-800 leading-tight;
}
.card-year {
  @apply text-xs text-gray-400 -mt-1.5;
}

.card-total {
  @apply bg-gradient-to-br from-gray-50 to-gray-100/50 rounded-xl p-3 border border-gray-100;
}
.card-total-label { @apply text-[10px] text-gray-400 uppercase font-semibold tracking-wider; }
.card-total-value { @apply block text-lg font-bold text-gray-800 mt-0.5; }

.card-progress { @apply mt-1; }
.card-progress-track {
  @apply h-1.5 bg-gray-100 rounded-full overflow-hidden;
}
.card-progress-fill {
  @apply h-full bg-gradient-to-r from-bfs-gold to-bfs-gold/60 rounded-full
         transition-all duration-700;
}

.card-meta {
  @apply flex items-center justify-between mt-auto pt-2 border-t border-gray-100;
}
.card-meta-item {
  @apply inline-flex items-center gap-1 text-[11px] text-gray-400;
}
.card-action-btn {
  @apply inline-flex items-center gap-1 text-[11px] font-semibold
         text-bfs-gold hover:text-bfs-gold-dark transition-colors;
}

/* ── Buttons ─────────────────────────────────────────────────────────────── */
.btn-primary {
  @apply inline-flex items-center gap-2 px-4 py-2
         bg-bfs-gold hover:bg-bfs-gold-dark text-white text-sm font-medium
         rounded-xl shadow-sm transition-all disabled:opacity-60 cursor-pointer;
}
.btn-secondary {
  @apply inline-flex items-center gap-2 px-4 py-2
         border border-gray-200 text-gray-600 hover:bg-gray-50 text-sm font-medium
         rounded-xl transition-all cursor-pointer;
}

/* ── Modal ───────────────────────────────────────────────────────────────── */
.modal-overlay  { @apply fixed inset-0 z-50 overflow-y-auto; }
.modal-backdrop { @apply fixed inset-0 bg-black/50 backdrop-blur-sm; }
.modal-container {
  @apply relative flex min-h-full items-center justify-center p-4;
}
.modal-box {
  @apply relative bg-white rounded-2xl shadow-2xl w-full max-w-md
         ring-1 ring-black/5 z-10;
}
.modal-header {
  @apply flex items-start justify-between px-6 py-5
         border-b border-gray-100;
}
.modal-title-group { @apply flex items-center gap-3; }
.modal-icon-wrap {
  @apply w-10 h-10 rounded-xl bg-bfs-gold/10 flex items-center justify-center shrink-0;
}
.modal-title    { @apply text-base font-semibold text-gray-800; }
.modal-subtitle { @apply text-xs text-gray-400 mt-0.5; }
.modal-close {
  @apply p-1 text-gray-400 hover:text-gray-600 rounded-lg transition-colors;
}
.modal-body   { @apply px-6 py-5 space-y-4; }
.modal-footer {
  @apply flex justify-end gap-2 px-6 py-4
         border-t border-gray-100 bg-gray-50 rounded-b-2xl;
}

.error-banner {
  @apply mx-6 mt-4 flex items-start gap-2 px-4 py-3
         bg-red-50 border border-red-200 rounded-xl text-sm text-red-600;
}

.form-input {
  @apply w-full px-3 py-2.5 text-sm border border-gray-200 rounded-xl
         focus:outline-none focus:ring-2 focus:ring-bfs-gold/30 focus:border-bfs-gold
         bg-white transition-all;
}
.select-wrap  { @apply relative; }
.select-icon  { @apply absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none; }

/* ── Transitions ─────────────────────────────────────────────────────────── */
.modal-enter-active, .modal-leave-active { transition: opacity 0.2s ease; }
.modal-enter-from, .modal-leave-to       { opacity: 0; }
</style>
