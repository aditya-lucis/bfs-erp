<template>
  <!-- Full-screen slide-over panel -->
  <Teleport to="body">
    <Transition name="slide">
      <div class="process-overlay" v-if="visible">
        <!-- Backdrop -->
        <div class="process-backdrop" @click="$emit('close')" />

        <!-- Panel -->
        <div class="process-panel">

          <!-- ── Panel Header ──────────────────────────────────────────── -->
          <div class="panel-header">
            <div class="panel-header-left">
              <button class="back-btn" @click="$emit('close')">
                <ArrowLeft class="w-4 h-4" />
              </button>
              <div>
                <div class="panel-breadcrumb">Finance › Annual Budget › Process</div>
                <h2 class="panel-title">{{ header.department_name }}</h2>
                <p class="panel-subtitle">
                  <CalendarDays class="w-3.5 h-3.5" />
                  Budget Tahun {{ header.year }}
                  <span class="ml-2" :class="header.is_locked ? 'badge-locked' : 'badge-open'">
                    <Lock v-if="header.is_locked" class="w-3 h-3" />
                    <Unlock v-else class="w-3 h-3" />
                    {{ header.is_locked ? 'Locked' : 'Open' }}
                  </span>
                </p>
              </div>
            </div>

            <div class="panel-header-right">
              <!-- Lock / Unlock Button -->
              <button
                v-if="canApprove"
                class="btn-outline flex items-center gap-1.5"
                @click="handleLockToggle"
                :disabled="isTogglingLock"
                title="Kunci / Buka Kunci Budget"
              >
                <Loader2 v-if="isTogglingLock" class="w-4 h-4 animate-spin" />
                <template v-else>
                  <Lock v-if="!header.is_locked" class="w-4 h-4 text-amber-400" />
                  <Unlock v-else class="w-4 h-4 text-emerald-400" />
                </template>
                {{ header.is_locked ? 'Unlock' : 'Lock' }}
              </button>

              <!-- Init Lines Button -->
              <button
                v-if="!header.is_locked && canCreate"
                class="btn-outline"
                @click="handleInitLines"
                :disabled="initLoading"
                title="Auto-create lines dari Budget Component aktif"
              >
                <Loader2 v-if="initLoading" class="w-4 h-4 animate-spin" />
                <Sparkles v-else class="w-4 h-4" />
                Auto Init Components
              </button>

              <!-- Add Component Button -->
              <button
                v-if="!header.is_locked && canCreate"
                class="btn-secondary"
                @click="openAddComponentModal"
              >
                <Plus class="w-4 h-4" />
                Add Component
              </button>

              <!-- Save All Button -->
              <button
                v-if="!header.is_locked && canUpdate && hasChanges"
                class="btn-primary"
                @click="handleSaveAll"
                :disabled="store.saving"
              >
                <Loader2 v-if="store.saving" class="w-4 h-4 animate-spin" />
                <Save v-else class="w-4 h-4" />
                Save All
              </button>

              <button class="panel-close" @click="$emit('close')">
                <X class="w-5 h-5" />
              </button>
            </div>
          </div>

          <!-- ── Totals Bar ────────────────────────────────────────────── -->
          <div class="totals-bar">
            <div class="total-item">
              <span class="total-label">Budget Tahunan</span>
              <span class="total-value primary">{{ formatCurrency(grandTotal) }}</span>
            </div>
            <div class="total-divider" />
            <div class="total-item" v-for="(sum, i) in monthTotals" :key="i">
              <span class="total-label text-[10px]">{{ MONTHS[i].short }}</span>
              <span class="total-value text-sm">{{ formatCompact(sum) }}</span>
            </div>
          </div>

          <!-- ── Loading ───────────────────────────────────────────────── -->
          <div v-if="loading" class="process-loading">
            <Loader2 class="w-8 h-8 animate-spin text-bfs-gold" />
            <p class="text-gray-400 text-sm mt-2">Memuat data komponen...</p>
          </div>

          <!-- ── Empty Lines ────────────────────────────────────────────── -->
          <div v-else-if="!lines.length" class="process-empty">
            <div class="empty-icon-wrap">
              <FileSpreadsheet class="w-10 h-10 text-gray-300" />
            </div>
            <p class="text-gray-500 font-medium">Belum ada komponen budget</p>
            <p class="text-gray-400 text-sm mt-1">
              Klik "Auto Init Components" untuk otomatis mengambil semua
              Budget Component dari departemen ini.
            </p>
            <button class="btn-primary mt-4" @click="handleInitLines" :disabled="initLoading">
              <Sparkles class="w-4 h-4" />
              Auto Init Components
            </button>
          </div>

          <!-- ── Main Budget Table ──────────────────────────────────────── -->
          <div v-else class="table-container">
            <div class="table-scroll">
              <table class="budget-table">
                <thead>
                  <tr>
                    <th class="th-no">No</th>
                    <th class="th-component">Budget Component</th>
                    <th class="th-category">Category</th>
                    <th v-for="m in MONTHS" :key="m.num" class="th-month">
                      <div>{{ m.short }}</div>
                    </th>
                    <th class="th-total">Total Annual</th>
                    <th class="th-action">Action</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="(line, idx) in lines"
                    :key="line.id"
                    class="budget-row"
                    :class="{ 'row-modified': modifiedLines.has(line.id) }"
                  >
                    <td class="td-no">{{ idx + 1 }}</td>

                    <td class="td-component">
                      <div class="component-name">{{ line.budget_component_name }}</div>
                    </td>

                    <td class="td-category">
                      <span class="category-badge" :class="categoryClass(line.budget_component_category)">
                        {{ line.budget_component_category?.toUpperCase() }}
                      </span>
                    </td>

                    <!-- 12 month inputs -->
                    <td v-for="m in MONTHS" :key="m.num" class="td-month">
                      <div class="month-cell">
                        <input
                          :value="getLineMonth(line, m.num)"
                          @change="onMonthInput(line, m.num, $event.target.value)"
                          @focus="$event.target.select()"
                          :disabled="header.is_locked || !canUpdate"
                          type="number"
                          min="0"
                          step="1000"
                          class="month-input"
                          :class="{
                            'input-has-value': getLineMonth(line, m.num) > 0,
                            'input-modified': isMonthModified(line.id, m.num),
                          }"
                        />
                      </div>
                    </td>

                    <!-- Row total -->
                    <td class="td-total">
                      <span class="row-total">{{ formatCurrency(getLineTotalAnnual(line)) }}</span>
                    </td>

                    <!-- Action -->
                    <td class="td-action">
                      <div class="action-group">
                        <button
                          class="action-btn log-btn"
                          @click="openLogModal(line)"
                          title="Lihat Log History"
                        >
                          <History class="w-3.5 h-3.5" />
                        </button>
                        <button
                          v-if="!header.is_locked && canDelete"
                          class="action-btn delete-btn"
                          @click="confirmDeleteLine(line)"
                          title="Hapus Component"
                        >
                          <Trash2 class="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>

                <!-- Totals Footer -->
                <tfoot>
                  <tr class="footer-row">
                    <td colspan="3" class="footer-label">Total</td>
                    <td v-for="(sum, i) in monthTotals" :key="i" class="footer-month">
                      {{ formatCompact(sum) }}
                    </td>
                    <td class="footer-grand">{{ formatCurrency(grandTotal) }}</td>
                    <td />
                  </tr>
                  <tr class="footer-annual">
                    <td colspan="14" class="footer-annual-cell">
                      <span class="footer-annual-label">Budget Tahunan :</span>
                      <span class="footer-annual-value">{{ formatCurrency(grandTotal) }}</span>
                    </td>
                    <td />
                  </tr>
                </tfoot>
              </table>
            </div>
          </div>

        </div><!-- end process-panel -->
      </div>
    </Transition>
  </Teleport>

  <!-- ── Log History Modal ───────────────────────────────────────────────── -->
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="logModal.show" class="modal-overlay" style="z-index:200">
        <div class="modal-backdrop" @click="logModal.show = false" />
        <div class="modal-container">
          <div class="modal-box max-w-lg">
            <div class="modal-header">
              <div class="modal-title-group">
                <div class="modal-icon-wrap">
                  <History class="w-5 h-5 text-bfs-gold" />
                </div>
                <div>
                  <h3 class="modal-title">Log History</h3>
                  <p class="modal-subtitle">{{ logModal.lineName }}</p>
                </div>
              </div>
              <button class="modal-close" @click="logModal.show = false">
                <X class="w-5 h-5" />
              </button>
            </div>

            <div class="modal-body max-h-80 overflow-y-auto">
              <div v-if="logModal.loading" class="flex justify-center py-8">
                <Loader2 class="w-6 h-6 animate-spin text-bfs-gold" />
              </div>
              <div v-else-if="!logModal.logs.length" class="text-center py-8 text-gray-400 text-sm">
                Belum ada riwayat perubahan.
              </div>
              <div v-else class="space-y-2">
                <div
                  v-for="log in logModal.logs"
                  :key="log.id"
                  class="log-item"
                >
                  <div class="log-month-badge">{{ log.month_name?.slice(0, 3) }}</div>
                  <div class="log-detail">
                    <div class="log-change">
                      <span class="log-old">{{ formatCurrency(log.old_value) }}</span>
                      <ArrowRight class="w-3 h-3 text-gray-400" />
                      <span class="log-new">{{ formatCurrency(log.new_value) }}</span>
                    </div>
                    <div class="log-meta">
                      {{ log.changed_by_name || 'System' }} · {{ formatDate(log.changed_at) }}
                      <span v-if="log.note" class="log-note">· {{ log.note }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="modal-footer">
              <button class="btn-secondary" @click="logModal.show = false">Tutup</button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>

  <!-- ── Add Component Modal ─────────────────────────────────────────────── -->
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="addComponentModal.show" class="modal-overlay" style="z-index:200">
        <div class="modal-backdrop" @click="addComponentModal.show = false" />
        <div class="modal-container">
          <div class="modal-box">
            <div class="modal-header">
              <div class="modal-title-group">
                <div class="modal-icon-wrap">
                  <Plus class="w-5 h-5 text-bfs-gold" />
                </div>
                <div>
                  <h3 class="modal-title">Add Budget Component</h3>
                  <p class="modal-subtitle">Pilih komponen dari {{ header.department_name }}</p>
                </div>
              </div>
              <button class="modal-close" @click="addComponentModal.show = false">
                <X class="w-5 h-5" />
              </button>
            </div>

            <div class="modal-body">
              <div v-if="addComponentModal.loading" class="flex justify-center py-6">
                <Loader2 class="w-6 h-6 animate-spin text-bfs-gold" />
              </div>
              <div v-else-if="!addComponentModal.components.length" class="text-center py-6 text-gray-400 text-sm">
                Semua komponen sudah ditambahkan.
              </div>
              <div v-else class="space-y-2 max-h-72 overflow-y-auto">
                <label
                  v-for="comp in addComponentModal.components"
                  :key="comp.id"
                  class="comp-pick-row"
                  :class="{ 'comp-selected': addComponentModal.selected.includes(comp.id) }"
                >
                  <input
                    type="checkbox"
                    :value="comp.id"
                    v-model="addComponentModal.selected"
                    class="rounded"
                  />
                  <div>
                    <div class="text-sm font-medium text-gray-700">{{ comp.name }}</div>
                    <div class="text-[11px] text-gray-400 uppercase">{{ comp.cost_category }}</div>
                  </div>
                </label>
              </div>
            </div>

            <div class="modal-footer">
              <button class="btn-secondary" @click="addComponentModal.show = false">Cancel</button>
              <button
                class="btn-primary"
                @click="handleAddComponents"
                :disabled="!addComponentModal.selected.length || store.saving"
              >
                <Loader2 v-if="store.saving" class="w-4 h-4 animate-spin" />
                <Plus v-else class="w-4 h-4" />
                Add {{ addComponentModal.selected.length || '' }} Component
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>

  <!-- ── Delete Line Modal ────────────────────────────────────────────────── -->
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="deleteLineModal.show" class="modal-overlay" style="z-index:200">
        <div class="modal-backdrop" @click="deleteLineModal.show = false" />
        <div class="modal-container">
          <div class="modal-box max-w-sm">
            <div class="flex flex-col items-center text-center p-6 gap-3">
              <div class="w-14 h-14 rounded-full bg-red-100 flex items-center justify-center">
                <Trash2 class="w-7 h-7 text-red-500" />
              </div>
              <h3 class="text-base font-semibold text-gray-800">Hapus Komponen?</h3>
              <p class="text-sm text-gray-500">
                <strong>{{ deleteLineModal.line?.budget_component_name }}</strong>
                akan dihapus dari budget ini. Data budget bulanan ikut terhapus.
              </p>
              <div v-if="deleteLineModal.error" class="w-full px-3 py-2 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
                {{ deleteLineModal.error }}
              </div>
              <div class="flex gap-2 w-full mt-2">
                <button class="btn-secondary flex-1" @click="deleteLineModal.show = false">Batal</button>
                <button
                  class="btn-danger flex-1"
                  @click="handleDeleteLine"
                  :disabled="store.saving"
                >
                  <Loader2 v-if="store.saving" class="w-4 h-4 animate-spin" />
                  <Trash2 v-else class="w-4 h-4" />
                  Hapus
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import {
  ArrowLeft, X, Save, Loader2, Plus, Trash2, History,
  Lock, Unlock, CalendarDays, Sparkles, FileSpreadsheet,
  ArrowRight
} from 'lucide-vue-next'
import { useAnnualBudgetStore } from '../../stores/annualBudget.js'
import { useToast } from '../../composables/useToast.js'
import { usePermission } from '../../composables/usePermission.js'

const props  = defineProps({ header: { type: Object, required: true } })
const emit   = defineEmits(['close', 'saved'])

const budgetStore = useAnnualBudgetStore()
const store       = budgetStore   // alias used in template :disabled="store.saving"
const toast  = useToast()
const { canCreate, canUpdate, canDelete, canApprove } = usePermission('FINANCE-ANNUAL-BUDGET')

const visible = ref(true)
const isTogglingLock = ref(false)

async function handleLockToggle() {
  isTogglingLock.value = true
  const newLockState = !props.header.is_locked
  try {
    const updated = await budgetStore.updateHeader(props.header.id, {
      is_locked: newLockState
    })
    props.header.is_locked = updated.is_locked
    toast.success(newLockState ? 'Budget berhasil dikunci.' : 'Budget berhasil dibuka kunci.')
    emit('saved')
  } catch (err) {
    toast.error(err?.response?.data?.is_locked?.[0] || err?.response?.data?.detail || 'Gagal mengubah status kunci.')
  } finally {
    isTogglingLock.value = false
  }
}

// ── Month config ─────────────────────────────────────────────────────────────
const MONTHS = [
  { num: 1,  short: 'Jan', label: 'January'   },
  { num: 2,  short: 'Feb', label: 'February'  },
  { num: 3,  short: 'Mar', label: 'March'     },
  { num: 4,  short: 'Apr', label: 'April'     },
  { num: 5,  short: 'May', label: 'May'       },
  { num: 6,  short: 'Jun', label: 'June'      },
  { num: 7,  short: 'Jul', label: 'July'      },
  { num: 8,  short: 'Aug', label: 'August'    },
  { num: 9,  short: 'Sep', label: 'September' },
  { num: 10, short: 'Oct', label: 'October'   },
  { num: 11, short: 'Nov', label: 'November'  },
  { num: 12, short: 'Dec', label: 'December'  },
]
const MONTH_FIELDS = ['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec']

// ── State ─────────────────────────────────────────────────────────────────────
const loading    = ref(false)
const initLoading = ref(false)
const lines      = ref([])

// Tracks edited values: { [lineId]: { [month]: newValue } }
const editedValues  = ref({})
const modifiedLines = computed(() => new Set(Object.keys(editedValues.value).map(Number)))

const hasChanges = computed(() => Object.keys(editedValues.value).length > 0)

// ── Load Lines ────────────────────────────────────────────────────────────────
async function loadLines() {
  loading.value = true
  try {
    lines.value = await budgetStore.fetchLines(props.header.id)
  } finally {
    loading.value = false
  }
}

onMounted(loadLines)

// ── Month Input Helpers ───────────────────────────────────────────────────────
function getLineMonth(line, month) {
  const edited = editedValues.value[line.id]?.[month]
  if (edited !== undefined) return edited
  return Number(line[MONTH_FIELDS[month - 1]]) || 0
}

function onMonthInput(line, month, rawVal) {
  const val = parseFloat(rawVal) || 0
  if (!editedValues.value[line.id]) {
    editedValues.value[line.id] = {}
  }
  editedValues.value[line.id][month] = val
}

function isMonthModified(lineId, month) {
  return editedValues.value[lineId]?.[month] !== undefined
}

function getLineTotalAnnual(line) {
  let total = 0
  for (let m = 1; m <= 12; m++) {
    total += getLineMonth(line, m)
  }
  return total
}

const monthTotals = computed(() => {
  return MONTHS.map(m => {
    return lines.value.reduce((sum, line) => sum + getLineMonth(line, m.num), 0)
  })
})

const grandTotal = computed(() => monthTotals.value.reduce((a, b) => a + b, 0))

// ── Save All ─────────────────────────────────────────────────────────────────
async function handleSaveAll() {
  const lineIds = Object.keys(editedValues.value)
  if (!lineIds.length) return

  try {
    for (const lineId of lineIds) {
      const monthData = editedValues.value[lineId]
      const months = Object.entries(monthData).map(([month, budget]) => ({
        month: Number(month),
        budget,
      }))
      await budgetStore.bulkUpdateMonths(Number(lineId), months, 'Manual input')
    }
    editedValues.value = {}
    await loadLines()
    toast.success('Budget berhasil disimpan.')
    emit('saved')
  } catch (err) {
    toast.error('Gagal menyimpan budget.')
  }
}

// ── Init Lines ────────────────────────────────────────────────────────────────
async function handleInitLines() {
  initLoading.value = true
  try {
    const res = await budgetStore.initLines(props.header.id)
    toast.success(res.detail || 'Lines berhasil diinisialisasi.')
    await loadLines()
    emit('saved')
  } catch (err) {
    toast.error(err?.response?.data?.detail || 'Gagal init lines.')
  } finally {
    initLoading.value = false
  }
}

// ── Add Component Modal ───────────────────────────────────────────────────────
const addComponentModal = reactive({
  show:       false,
  loading:    false,
  components: [],
  selected:   [],
})

async function openAddComponentModal() {
  addComponentModal.show     = true
  addComponentModal.selected = []
  addComponentModal.loading  = true
  try {
    addComponentModal.components = await budgetStore.fetchBudgetComponents(
      props.header.department, props.header.id
    )
  } finally {
    addComponentModal.loading = false
  }
}

async function handleAddComponents() {
  for (const compId of addComponentModal.selected) {
    try {
      await budgetStore.createLine({
        header:           props.header.id,
        budget_component: compId,
        order_no:         lines.value.length + 1,
      })
    } catch {}
  }
  addComponentModal.show = false
  await loadLines()
  toast.success(`${addComponentModal.selected.length} komponen ditambahkan.`)
  emit('saved')
}

// ── Log History Modal ─────────────────────────────────────────────────────────
const logModal = reactive({
  show:     false,
  loading:  false,
  lineName: '',
  logs:     [],
})

async function openLogModal(line) {
  logModal.show     = true
  logModal.lineName = line.budget_component_name
  logModal.loading  = true
  logModal.logs     = []
  try {
    logModal.logs = await budgetStore.fetchLineLogs(line.id)
  } finally {
    logModal.loading = false
  }
}

// ── Delete Line Modal ─────────────────────────────────────────────────────────
const deleteLineModal = reactive({ show: false, line: null, error: '' })

function confirmDeleteLine(line) {
  deleteLineModal.line  = line
  deleteLineModal.error = ''
  deleteLineModal.show  = true
}

async function handleDeleteLine() {
  deleteLineModal.error = ''
  try {
    await budgetStore.deleteLine(deleteLineModal.line.id)
    deleteLineModal.show = false
    lines.value = lines.value.filter(l => l.id !== deleteLineModal.line.id)
    // Remove from editedValues
    delete editedValues.value[deleteLineModal.line.id]
    toast.success('Komponen berhasil dihapus.')
    emit('saved')
  } catch (err) {
    deleteLineModal.error = err?.response?.data?.detail || 'Gagal menghapus.'
  }
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function formatCurrency(val) {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency', currency: 'IDR', maximumFractionDigits: 0,
  }).format(Number(val) || 0)
}

function formatCompact(val) {
  const n = Number(val) || 0
  if (n === 0) return '—'
  if (n >= 1_000_000_000) return `${(n / 1_000_000_000).toFixed(1)}B`
  if (n >= 1_000_000)     return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000)         return `${(n / 1_000).toFixed(0)}K`
  return n.toLocaleString('id-ID')
}

function formatDate(dt) {
  if (!dt) return ''
  return new Date(dt).toLocaleString('id-ID', {
    dateStyle: 'short', timeStyle: 'short',
  })
}

function categoryClass(cat) {
  const map = {
    hpp:        'cat-hpp',
    revenue:    'cat-revenue',
    target_hpp: 'cat-target-hpp',
    target_opex:'cat-target-opex',
    opex:       'cat-opex',
    capex:      'cat-capex',
    tax:        'cat-tax',
  }
  return map[cat?.toLowerCase()] || 'cat-default'
}
</script>

<style scoped>
@reference "../../style.css";

/* ── Overlay ─────────────────────────────────────────────────────────────── */
.process-overlay {
  @apply fixed inset-0 z-[100] flex;
}
.process-backdrop {
  @apply absolute inset-0 bg-black/40 backdrop-blur-sm;
}
.process-panel {
  @apply relative ml-auto h-full flex flex-col bg-white shadow-2xl
         w-full max-w-[98vw] xl:max-w-[96vw];
}

/* ── Panel Header ────────────────────────────────────────────────────────── */
.panel-header {
  @apply flex items-center justify-between px-6 py-4
         bg-gradient-to-r from-gray-900 to-gray-800 text-white shrink-0;
}
.panel-header-left  { @apply flex items-center gap-4; }
.panel-header-right { @apply flex items-center gap-2; }

.back-btn {
  @apply p-2 rounded-xl bg-white/10 hover:bg-white/20 text-white transition-colors;
}
.panel-breadcrumb { @apply text-xs text-gray-400; }
.panel-title      { @apply text-xl font-bold text-white; }
.panel-subtitle {
  @apply text-xs text-gray-300 flex items-center gap-1.5 mt-0.5;
}
.panel-close {
  @apply p-2 rounded-xl bg-white/10 hover:bg-white/20 text-white transition-colors;
}

.badge-locked {
  @apply inline-flex items-center gap-1 px-2 py-0.5
         bg-amber-500/20 text-amber-400 rounded-full text-[11px] font-medium;
}
.badge-open {
  @apply inline-flex items-center gap-1 px-2 py-0.5
         bg-emerald-500/20 text-emerald-400 rounded-full text-[11px] font-medium;
}

/* ── Totals Bar ──────────────────────────────────────────────────────────── */
.totals-bar {
  @apply flex items-center gap-0 px-4 py-2.5 bg-gray-50 border-b border-gray-200
         overflow-x-auto shrink-0;
}
.total-item   { @apply flex flex-col items-center px-3 min-w-[70px]; }
.total-divider { @apply w-px h-8 bg-gray-200 mx-1; }
.total-label  { @apply text-[10px] text-gray-400 uppercase font-semibold tracking-wide whitespace-nowrap; }
.total-value  { @apply text-sm font-bold text-gray-700 whitespace-nowrap; }
.total-value.primary { @apply text-base text-bfs-gold; }

/* ── Loading / Empty ─────────────────────────────────────────────────────── */
.process-loading {
  @apply flex flex-col items-center justify-center py-24 flex-1;
}
.process-empty {
  @apply flex flex-col items-center justify-center py-20 flex-1 text-center px-8;
}
.empty-icon-wrap {
  @apply w-20 h-20 rounded-full bg-gray-100 flex items-center justify-center mb-4;
}

/* ── Table Container ─────────────────────────────────────────────────────── */
.table-container {
  @apply flex-1 overflow-hidden flex flex-col;
}
.table-scroll {
  @apply flex-1 overflow-auto;
}

/* ── Budget Table ────────────────────────────────────────────────────────── */
.budget-table {
  @apply w-full border-collapse text-sm;
  min-width: 1800px;
}

.budget-table thead {
  @apply sticky top-0 z-10;
}
.budget-table thead tr {
  @apply bg-gradient-to-r from-gray-800 to-gray-700;
}

.th-no       { @apply px-3 py-3 text-left text-[11px] font-semibold text-gray-300 uppercase w-10 whitespace-nowrap; }
.th-component { @apply px-4 py-3 text-left text-[11px] font-semibold text-gray-300 uppercase min-w-[200px]; }
.th-category { @apply px-3 py-3 text-left text-[11px] font-semibold text-gray-300 uppercase w-28; }
.th-month    { @apply px-1 py-3 text-center text-[11px] font-semibold text-gray-300 uppercase w-[90px]; }
.th-total    { @apply px-4 py-3 text-right text-[11px] font-semibold text-gray-300 uppercase w-36 whitespace-nowrap; }
.th-action   { @apply px-3 py-3 text-center text-[11px] font-semibold text-gray-300 uppercase w-20; }

/* ── Rows ────────────────────────────────────────────────────────────────── */
.budget-row {
  @apply border-b border-gray-100 hover:bg-blue-50/30 transition-colors;
}
.budget-row.row-modified {
  @apply bg-amber-50/40;
}
.budget-row:nth-child(even) { @apply bg-gray-50/40; }
.budget-row:nth-child(even).row-modified { @apply bg-amber-50/60; }

.td-no        { @apply px-3 py-2 text-gray-400 text-xs; }
.td-component { @apply px-4 py-2; }
.td-category  { @apply px-3 py-2; }
.td-month     { @apply px-1 py-1.5; }
.td-total     { @apply px-4 py-2 text-right; }
.td-action    { @apply px-3 py-2 text-center; }

.component-name {
  @apply font-medium text-gray-800 text-xs leading-tight;
}

/* ── Month Input ─────────────────────────────────────────────────────────── */
.month-cell { @apply flex items-center justify-center; }
.month-input {
  @apply w-full text-right text-xs px-2 py-1.5
         border border-transparent rounded-lg bg-transparent
         focus:outline-none focus:ring-1 focus:ring-bfs-gold/50 focus:border-bfs-gold
         focus:bg-white transition-all
         disabled:opacity-50 disabled:cursor-not-allowed;
  min-width: 75px;
}
.month-input::-webkit-inner-spin-button,
.month-input::-webkit-outer-spin-button { -webkit-appearance: none; }
.month-input.input-has-value {
  @apply text-gray-800 font-medium;
}
.month-input.input-modified {
  @apply border-amber-300 bg-amber-50/80 text-amber-800 font-semibold;
}

.row-total {
  @apply text-xs font-bold text-bfs-gold;
}

/* ── Category Badges ─────────────────────────────────────────────────────── */
.category-badge { @apply inline-flex px-2 py-0.5 rounded-md text-[10px] font-bold uppercase; }
.cat-hpp        { @apply bg-blue-100 text-blue-700; }
.cat-revenue    { @apply bg-green-100 text-green-700; }
.cat-target-hpp { @apply bg-purple-100 text-purple-700; }
.cat-target-opex{ @apply bg-indigo-100 text-indigo-700; }
.cat-opex       { @apply bg-orange-100 text-orange-700; }
.cat-capex      { @apply bg-amber-100 text-amber-700; }
.cat-tax        { @apply bg-red-100 text-red-700; }
.cat-default    { @apply bg-gray-100 text-gray-600; }

/* ── Action Buttons ──────────────────────────────────────────────────────── */
.action-group { @apply flex items-center justify-center gap-1; }
.action-btn   { @apply p-1.5 rounded-lg transition-colors; }
.log-btn      { @apply text-gray-400 hover:text-bfs-gold hover:bg-bfs-gold/10; }
.delete-btn   { @apply text-gray-400 hover:text-red-500 hover:bg-red-50; }

/* ── Table Footer ────────────────────────────────────────────────────────── */
.footer-row {
  @apply bg-gray-800 sticky bottom-10;
}
.footer-label {
  @apply px-4 py-2.5 text-right text-xs font-bold text-white uppercase;
}
.footer-month {
  @apply px-2 py-2.5 text-center text-xs font-bold text-bfs-gold whitespace-nowrap;
}
.footer-grand {
  @apply px-4 py-2.5 text-right text-sm font-bold text-bfs-gold whitespace-nowrap;
}

.footer-annual {
  @apply bg-gray-900 sticky bottom-0;
}
.footer-annual-cell {
  @apply px-4 py-3 text-right;
}
.footer-annual-label {
  @apply text-xs text-gray-400 font-medium mr-4;
}
.footer-annual-value {
  @apply text-lg font-black text-bfs-gold;
}

/* ── Buttons ─────────────────────────────────────────────────────────────── */
.btn-primary {
  @apply inline-flex items-center gap-2 px-4 py-2
         bg-bfs-gold hover:bg-bfs-gold-dark text-white text-sm font-medium
         rounded-xl shadow-sm transition-all disabled:opacity-60 cursor-pointer;
}
.btn-secondary {
  @apply inline-flex items-center gap-2 px-4 py-2
         border border-white/20 text-white hover:bg-white/10 text-sm font-medium
         rounded-xl transition-all cursor-pointer;
}
.btn-outline {
  @apply inline-flex items-center gap-2 px-3 py-2
         border border-white/20 text-gray-300 hover:bg-white/10 text-sm
         rounded-xl transition-all cursor-pointer;
}
.btn-danger {
  @apply inline-flex items-center justify-center gap-2 px-4 py-2
         bg-red-500 hover:bg-red-600 text-white text-sm font-medium
         rounded-xl transition-all disabled:opacity-60 cursor-pointer;
}

/* ── Modal ───────────────────────────────────────────────────────────────── */
.modal-overlay   { @apply fixed inset-0 z-[150] overflow-y-auto; }
.modal-backdrop  { @apply fixed inset-0 bg-black/50 backdrop-blur-sm; }
.modal-container { @apply relative flex min-h-full items-center justify-center p-4; }
.modal-box       { @apply relative bg-white rounded-2xl shadow-2xl w-full max-w-md ring-1 ring-black/5 z-10; }
.modal-header    { @apply flex items-start justify-between px-6 py-5 border-b border-gray-100; }
.modal-title-group { @apply flex items-center gap-3; }
.modal-icon-wrap { @apply w-10 h-10 rounded-xl bg-bfs-gold/10 flex items-center justify-center shrink-0; }
.modal-title     { @apply text-base font-semibold text-gray-800; }
.modal-subtitle  { @apply text-xs text-gray-400 mt-0.5; }
.modal-close     { @apply p-1 text-gray-400 hover:text-gray-600 rounded-lg transition-colors; }
.modal-body      { @apply px-6 py-5; }
.modal-footer    { @apply flex justify-end gap-2 px-6 py-4 border-t border-gray-100 bg-gray-50 rounded-b-2xl; }

/* ── Component Picker ────────────────────────────────────────────────────── */
.comp-pick-row {
  @apply flex items-center gap-3 px-3 py-2.5 rounded-xl border border-gray-100
         cursor-pointer hover:bg-bfs-gold/5 hover:border-bfs-gold/30 transition-all;
}
.comp-selected {
  @apply bg-bfs-gold/5 border-bfs-gold/40;
}

/* ── Log Items ───────────────────────────────────────────────────────────── */
.log-item {
  @apply flex items-start gap-3 py-2.5 border-b border-gray-50 last:border-0;
}
.log-month-badge {
  @apply w-10 h-10 rounded-lg bg-bfs-gold/10 text-bfs-gold text-xs font-bold
         flex items-center justify-center shrink-0;
}
.log-detail { @apply flex flex-col gap-0.5 flex-1; }
.log-change { @apply flex items-center gap-2 text-sm font-medium; }
.log-old    { @apply text-gray-400 line-through; }
.log-new    { @apply text-gray-800 font-semibold; }
.log-meta   { @apply text-[11px] text-gray-400 flex items-center gap-1; }
.log-note   { @apply italic text-gray-500; }

/* ── Transitions ─────────────────────────────────────────────────────────── */
.slide-enter-active { transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.2s ease; }
.slide-leave-active { transition: transform 0.25s ease, opacity 0.2s ease; }
.slide-enter-from   { transform: translateX(40px); opacity: 0; }
.slide-leave-to     { transform: translateX(40px); opacity: 0; }

.modal-enter-active, .modal-leave-active { transition: opacity 0.2s ease; }
.modal-enter-from, .modal-leave-to       { opacity: 0; }
</style>
