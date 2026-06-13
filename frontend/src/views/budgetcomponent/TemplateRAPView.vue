<template>
  <div class="fixed inset-0 z-50 flex items-start justify-center bg-black/50 backdrop-blur-sm overflow-y-auto py-6">
    <div class="bg-white rounded-2xl shadow-2xl w-full max-w-6xl mx-4 flex flex-col max-h-[92vh] border border-gray-100">

      <!-- Header -->
      <div class="rap-header px-6 py-4 rounded-t-2xl flex justify-between items-center shrink-0">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-lg bg-white/15 flex items-center justify-center backdrop-blur-sm">
            <FileText class="w-5 h-5 text-white/90" />
          </div>
          <div>
            <h2 class="font-semibold text-white text-sm tracking-wide">Template RAP</h2>
            <p class="text-white/60 text-[11px] mt-0.5">Finance › Component Budget › {{ isEdit ? 'Edit' : 'Create' }}</p>
          </div>
        </div>
        <button @click="$emit('close')" class="w-8 h-8 rounded-lg bg-white/10 hover:bg-white/20 flex items-center justify-center transition-colors">
          <X class="w-4 h-4 text-white/80" />
        </button>
      </div>

      <!-- Info Cards -->
      <div class="px-6 py-4 bg-gradient-to-b from-gray-50/80 to-white border-b border-gray-100 shrink-0">
        <!-- Template Name (full width card) -->
        <div class="bg-white rounded-xl border border-gray-100 shadow-sm px-5 py-3 mb-3">
          <div class="flex items-center gap-2 mb-1">
            <div class="w-1.5 h-1.5 rounded-full bg-bfs-gold"></div>
            <span class="text-[10px] font-semibold text-gray-400 uppercase tracking-wider">Template Name</span>
          </div>
          <p class="text-sm font-semibold text-gray-800 pl-3.5">{{ templateName }}</p>
        </div>

        <!-- Info grid -->
        <div class="grid grid-cols-4 gap-3">
          <div class="info-card">
            <span class="info-label">Cost Category</span>
            <span class="info-value">
              <span class="inline-flex px-2 py-0.5 rounded-full text-[11px] font-semibold bg-blue-50 text-blue-700">
                {{ budgetComponent?.cost_category?.toUpperCase() }}
              </span>
            </span>
          </div>
          <div class="info-card">
            <span class="info-label">Department</span>
            <span class="info-value">{{ budgetComponent?.department_name }}</span>
          </div>
          <div class="info-card">
            <span class="info-label">Cost of Unit</span>
            <span class="info-value">{{ budgetComponent?.position_name || '—' }}</span>
          </div>
          <div class="info-card">
            <span class="info-label">Budget Component</span>
            <span class="info-value text-xs">{{ budgetComponent?.name }}</span>
          </div>
        </div>
      </div>

      <!-- Toolbar -->
      <div class="px-6 py-3 flex justify-between items-center border-b border-gray-100 shrink-0 bg-white">
        <button 
          v-if="canCreate"
          @click="addRootHeader" 
          class="btn-primary text-xs"
        >
          <Plus class="w-3.5 h-3.5" /> Add Header
        </button>
        <div v-else></div>
        <div class="flex gap-2">
          <button @click="exportToExcel" class="btn-secondary text-xs">
            <Download class="w-3.5 h-3.5" /> Export
          </button>
          <button @click="$emit('close')" class="btn-secondary text-xs">Close</button>
        </div>
      </div>

      <!-- Tree Content (scrollable) -->
      <div class="flex-1 overflow-auto">
        <!-- Table -->
        <table v-if="treeData.length" class="w-full text-sm tree-table">
          <thead class="bg-gray-50/80 sticky top-0 z-10">
            <tr>
              <th class="th-cell w-[60px] text-center">No</th>
              <th class="th-cell text-left">COA Header / Item</th>
              <th class="th-cell w-[180px] text-left">Item Code</th>
              <th class="th-cell w-[200px] text-left">Remarks</th>
              <th class="th-cell w-[70px] text-center">Unit</th>
              <th class="th-cell w-[100px] text-right pr-6">Action</th>
            </tr>
          </thead>
          <tbody>
            <TreeNode
              v-for="node in treeData"
              :key="node.id"
              :node="node"
              :level="0"
              @add-child="onAddChild"
              @edit="onEditNode"
              @delete="onDeleteNode"
            />
          </tbody>
        </table>

        <!-- Empty State -->
        <div v-else class="flex flex-col items-center justify-center py-20 text-gray-400">
          <div class="w-16 h-16 rounded-2xl bg-gray-50 flex items-center justify-center mb-4">
            <FolderOpen class="w-8 h-8 text-gray-300" />
          </div>
          <p class="text-sm font-medium text-gray-500">Belum ada data template</p>
          <p class="text-xs text-gray-400 mt-1">Klik "Add Header" untuk membuat header pertama</p>
        </div>
      </div>

    </div>

    <!-- ── Add/Edit Header Modal ── -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="headerModal.show" class="fixed inset-0 z-[60] flex items-center justify-center bg-black/50 p-4">
          <div class="bg-white rounded-2xl shadow-2xl w-full max-w-sm" @click.stop>
            <div class="px-6 py-4 border-b border-gray-100">
              <h3 class="text-base font-semibold text-gray-800">
                {{ headerModal.mode === 'add' ? 'Add' : 'Edit' }} 
                {{ headerModal.itemType === 'header' ? 'Header' : 'Sub Header' }}
              </h3>
            </div>
            <div class="px-6 py-5">
              <FormField label="Description" required :error="headerModal.error">
                <input 
                  v-model="headerModal.description" 
                  class="form-input" 
                  placeholder="e.g. Marketing Event"
                  @keyup.enter="saveHeader"
                />
              </FormField>
            </div>
            <div class="flex justify-end gap-2 px-6 py-4 border-t border-gray-100 bg-gray-50/50 rounded-b-2xl">
              <button @click="headerModal.show = false" class="btn-secondary text-sm">Cancel</button>
              <button 
                @click="saveHeader" 
                :disabled="saving" 
                class="btn-primary text-sm"
              >
                <Loader2 v-if="saving" class="w-3.5 h-3.5 animate-spin" />
                <Save v-else class="w-3.5 h-3.5" />
                {{ saving ? 'Saving...' : 'Save' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- ── Item Picker Modal ── -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="itemPicker.show" class="fixed inset-0 z-[60] flex items-center justify-center bg-black/50 p-4">
          <div class="bg-white rounded-2xl shadow-2xl w-full max-w-3xl max-h-[80vh] flex flex-col" @click.stop>
            <!-- Header -->
            <div class="px-6 py-4 border-b border-gray-100 flex justify-between items-center">
              <div>
                <h3 class="text-base font-semibold text-gray-800">Select Item</h3>
                <p class="text-xs text-gray-400 mt-0.5">Pick an item from inventory</p>
              </div>
              <button @click="itemPicker.show = false" class="w-8 h-8 rounded-lg hover:bg-gray-100 flex items-center justify-center transition-colors">
                <X class="w-4 h-4 text-gray-400" />
              </button>
            </div>

            <!-- Search -->
            <div class="px-6 py-3 border-b border-gray-100">
              <div class="relative">
                <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input 
                  v-model="itemPicker.search" 
                  @input="debounceSearch"
                  placeholder="Search item code or name..."
                  class="form-input pl-10"
                />
              </div>
            </div>

            <!-- Item List -->
            <div class="flex-1 overflow-auto">
              <table class="w-full text-sm">
                <thead class="bg-gray-50/80 sticky top-0">
                  <tr>
                    <th class="th-cell text-left">Item Code</th>
                    <th class="th-cell text-left">Item Name</th>
                    <th class="th-cell text-left">Category</th>
                    <th class="th-cell text-right">Price</th>
                    <th class="th-cell w-20 text-center"></th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-50">
                  <tr 
                    v-for="item in store.itemsForPicker" 
                    :key="item.id" 
                    class="hover:bg-yellow-50/40 transition-colors cursor-pointer"
                    @click="selectItem(item)"
                  >
                    <td class="px-4 py-3 font-mono text-xs text-gray-500">{{ item.item_code }}</td>
                    <td class="px-4 py-3 font-medium text-gray-800">{{ item.item_name }}</td>
                    <td class="px-4 py-3 text-gray-500 text-xs">{{ item.category_name }}</td>
                    <td class="px-4 py-3 text-right text-gray-600 font-mono text-xs">{{ formatPrice(item.unit_price) }}</td>
                    <td class="px-4 py-3 text-center">
                      <button 
                        class="text-xs font-semibold text-bfs-gold hover:text-bfs-gold-dark px-3 py-1 rounded-lg hover:bg-yellow-50 transition-colors"
                      >
                        Select
                      </button>
                    </td>
                  </tr>
                  <tr v-if="!store.itemsForPicker.length">
                    <td colspan="5" class="text-center py-12 text-gray-400 text-sm">
                      <Package class="w-8 h-8 mx-auto mb-2 text-gray-300" />
                      No items found
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- ── Add/Edit Item Detail Modal ── -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="itemDetailModal.show" class="fixed inset-0 z-[60] flex items-center justify-center bg-black/50 p-4">
          <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md" @click.stop>
            <div class="px-6 py-4 border-b border-gray-100">
              <h3 class="text-base font-semibold text-gray-800">
                {{ itemDetailModal.editId ? 'Edit' : 'Add' }} Item Detail
              </h3>
            </div>
            <div class="px-6 py-5 space-y-4">
              <!-- Selected Item Card -->
              <div class="bg-gradient-to-br from-gray-50 to-gray-50/50 rounded-xl p-4 border border-gray-100">
                <div class="flex items-start gap-3">
                  <div class="w-9 h-9 rounded-lg bg-white border border-gray-200 flex items-center justify-center shrink-0 shadow-sm">
                    <Package class="w-4 h-4 text-gray-400" />
                  </div>
                  <div class="min-w-0">
                    <p class="text-xs font-mono text-gray-400">{{ itemDetailModal.selectedItem?.item_code }}</p>
                    <p class="text-sm font-semibold text-gray-800 mt-0.5">{{ itemDetailModal.selectedItem?.item_name }}</p>
                    <p class="text-xs text-gray-500 mt-1">
                      UoM: <span class="font-medium text-gray-600">{{ itemDetailModal.selectedItem?.unit_name }}</span>
                    </p>
                  </div>
                </div>
              </div>
              <FormField label="Remarks">
                <input 
                  v-model="itemDetailModal.remarks" 
                  class="form-input" 
                  placeholder="Optional remarks..."
                />
              </FormField>
            </div>
            <div class="flex justify-end gap-2 px-6 py-4 border-t border-gray-100 bg-gray-50/50 rounded-b-2xl">
              <button @click="itemDetailModal.show = false" class="btn-secondary text-sm">Cancel</button>
              <button 
                @click="saveItemDetail" 
                :disabled="saving" 
                class="btn-primary text-sm"
              >
                <Loader2 v-if="saving" class="w-3.5 h-3.5 animate-spin" />
                <Save v-else class="w-3.5 h-3.5" />
                {{ saving ? 'Saving...' : 'Save' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useBudgetComponentStore } from '../../stores/budgetComponent.js'
import { usePermission } from '../../composables/usePermission.js'
import { useToast } from '../../composables/useToast.js'
import FormField from '../../components/FormField.vue'
import TreeNode from '../../components/budget_component/TreeNode.vue'
import { Plus, X, Search, FolderOpen, FileText, Download, Package, Save, Loader2 } from 'lucide-vue-next'

const props = defineProps({
  budgetComponent: { type: Object, required: true }
})
const emit = defineEmits(['close', 'saved'])

const store = useBudgetComponentStore()
const { canCreate, canUpdate, canDelete } = usePermission('FINANCE-BUDGET-COMPONENT')
const toast = useToast()
const saving = ref(false)

// ── State ──────────────────────────────────────────────────────────────────
const template = ref(null)
const treeData = ref([])

const isEdit = computed(() => !!template.value?.id)
const templateName = computed(() => {
  if (template.value?.template_name) return template.value.template_name
  return `Template RAP of ${props.budgetComponent.name}`
})

// ── Modals ─────────────────────────────────────────────────────────────────
const headerModal = ref({
  show: false,
  mode: 'add',
  itemType: 'header',
  parentId: null,
  description: '',
  error: '',
  editId: null,
})

const itemPicker = ref({
  show: false,
  search: '',
  parentId: null,
})

const itemDetailModal = ref({
  show: false,
  selectedItem: null,
  parentId: null,
  remarks: '',
  editId: null,
})

// ── Load Data ──────────────────────────────────────────────────────────────
onMounted(async () => {
  await loadTemplate()
})

async function loadTemplate() {
  try {
    const templates = await store.fetchTemplates({ budget_component: props.budgetComponent.id })
    if (templates.length > 0) {
      template.value = templates[0]
      await loadTree()
    }
  } catch (e) {
    console.error('Failed to load template', e)
  }
}

async function loadTree() {
  if (!template.value) return
  try {
    const details = await store.fetchTemplateDetails(template.value.id)
    treeData.value = buildTree(details)
  } catch (e) {
    toast.error('Gagal memuat template details.')
  }
}

function buildTree(flatData) {
  if (!flatData || !flatData.length) return []
  
  const map = {}
  const roots = []

  flatData.forEach(node => {
    map[node.id] = { ...node, children: [] }
  })

  flatData.forEach(node => {
    const parentId = node.parent
    if (parentId && map[parentId]) {
      map[parentId].children.push(map[node.id])
    } else {
      roots.push(map[node.id])
    }
  })

  return roots
}

// ── Create Template ────────────────────────────────────────────────────────
async function ensureTemplate() {
  if (template.value) return template.value

  try {
    const created = await store.createTemplate({
      budget_component: props.budgetComponent.id,
      template_name: templateName.value,
      is_active: true,
    })
    template.value = created
    return created
  } catch (e) {
    toast.error('Gagal membuat template.')
    throw e
  }
}

// ── Add Root Header ────────────────────────────────────────────────────────
function addRootHeader() {
  headerModal.value = {
    show: true,
    mode: 'add',
    itemType: 'header',
    parentId: null,
    description: '',
    error: '',
    editId: null,
  }
}

// ── Add Child ──────────────────────────────────────────────────────────────
async function onAddChild(parentNode) {
  if (parentNode.item_type === 'item') {
    toast.error('Item tidak boleh memiliki child.')
    return
  }

  const depth = getNodeDepth(parentNode)
  
  if (depth >= 2) {
    toast.error('Maksimal 3 level.')
    return
  }

  if (parentNode.item_type === 'sub_header') {
    // Parent is sub_header, child must be item → open item picker
    itemPicker.value = {
      show: true,
      search: '',
      parentId: parentNode.id,
    }
    await store.searchItems()
  } else {
    // Parent is header, child is sub_header
    headerModal.value = {
      show: true,
      mode: 'add',
      itemType: 'sub_header',
      parentId: parentNode.id,
      description: '',
      error: '',
      editId: null,
    }
  }
}

function getNodeDepth(node, currentDepth = 0) {
  if (node.item_type === 'header') return 0
  if (node.item_type === 'sub_header') return 1
  if (node.item_type === 'item') return 2
  return currentDepth
}

// ── Save Header ────────────────────────────────────────────────────────────
async function saveHeader() {
  headerModal.value.error = ''
  
  if (!headerModal.value.description.trim()) {
    headerModal.value.error = 'Description wajib diisi.'
    return
  }

  saving.value = true
  try {
    await ensureTemplate()

    const payload = {
      template: template.value.id,
      item_type: headerModal.value.itemType,
      parent: headerModal.value.parentId,
      description: headerModal.value.description.trim(),
      order_no: 0,
    }

    if (headerModal.value.mode === 'add') {
      await store.createTemplateDetail(template.value.id, payload)
    } else {
      await store.updateTemplateDetail(headerModal.value.editId, payload)
    }

    headerModal.value.show = false
    toast.success('Berhasil disimpan.')
    await loadTree()
  } catch (e) {
    const msg = e?.response?.data?.detail || e?.response?.data?.position?.[0] || 'Gagal menyimpan.'
    headerModal.value.error = msg
    toast.error('Gagal menyimpan.')
  } finally {
    saving.value = false
  }
}

// ── Item Picker ────────────────────────────────────────────────────────────
let searchTimeout = null
function debounceSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    store.searchItems(itemPicker.value.search)
  }, 300)
}

function selectItem(item) {
  itemPicker.value.show = false
  itemDetailModal.value = {
    show: true,
    selectedItem: item,
    parentId: itemPicker.value.parentId,
    remarks: '',
    editId: null,
  }
}

async function saveItemDetail() {
  saving.value = true
  try {
    await ensureTemplate()

    const payload = {
      template: template.value.id,
      item_type: 'item',
      parent: itemDetailModal.value.parentId,
      item: itemDetailModal.value.selectedItem.id,
      description: itemDetailModal.value.selectedItem.item_name,
      remarks: itemDetailModal.value.remarks,
      order_no: 0,
    }

    if (itemDetailModal.value.editId) {
      await store.updateTemplateDetail(itemDetailModal.value.editId, payload)
    } else {
      await store.createTemplateDetail(template.value.id, payload)
    }

    itemDetailModal.value.show = false
    toast.success('Item berhasil disimpan.')
    await loadTree()
  } catch (e) {
    toast.error('Gagal menyimpan item.')
  } finally {
    saving.value = false
  }
}

// ── Edit / Delete ──────────────────────────────────────────────────────────
function onEditNode(node) {
  if (node.item_type === 'item') {
    itemDetailModal.value = {
      show: true,
      selectedItem: { 
        id: node.item, 
        item_name: node.item_name, 
        item_code: node.item_code, 
        unit_name: node.unit_name 
      },
      parentId: node.parent,
      remarks: node.remarks || '',
      editId: node.id,
    }
  } else {
    headerModal.value = {
      show: true,
      mode: 'edit',
      itemType: node.item_type,
      parentId: node.parent,
      description: node.description,
      error: '',
      editId: node.id,
    }
  }
}

async function onDeleteNode(node) {
  if (!confirm(`Hapus "${node.display_number} ${node.description || node.item_name}"?\n\nSemua child akan ikut terhapus.`)) {
    return
  }

  try {
    await store.deleteTemplateDetail(node.id)
    toast.success('Berhasil dihapus.')
    await loadTree()
  } catch (e) {
    toast.error('Gagal menghapus.')
  }
}

// ── Helpers ────────────────────────────────────────────────────────────────
function exportToExcel() {
  toast.info('Export to Excel — coming soon.')
}

function formatPrice(price) {
  return new Intl.NumberFormat('id-ID', { 
    style: 'currency', 
    currency: 'IDR',
    minimumFractionDigits: 0 
  }).format(price || 0)
}
</script>

<style scoped>
@reference "../../style.css";

/* Header gradient */
.rap-header {
  background: linear-gradient(135deg, #1e293b 0%, #334155 50%, #475569 100%);
}

/* Info cards */
.info-card {
  @apply bg-white rounded-xl border border-gray-100 shadow-sm px-4 py-3 flex flex-col gap-1;
}
.info-label {
  @apply text-[10px] font-semibold text-gray-400 uppercase tracking-wider;
}
.info-value {
  @apply text-sm font-medium text-gray-800;
}

/* Table */
.tree-table {
  border-collapse: separate;
  border-spacing: 0;
}
.th-cell {
  @apply px-4 py-3 text-[10px] font-bold text-gray-400 uppercase tracking-wider
         border-b-2 border-gray-100;
}

/* Form elements */
.form-input {
  @apply w-full px-3 py-2.5 text-sm border border-gray-200 rounded-xl
         focus:outline-none focus:ring-2 focus:ring-bfs-gold/30 focus:border-bfs-gold
         transition-all bg-white placeholder:text-gray-300;
}
.btn-primary {
  @apply px-4 py-2 bg-bfs-gold hover:bg-bfs-gold-dark text-white font-medium rounded-xl 
         transition-all disabled:opacity-60 cursor-pointer text-sm flex items-center gap-1.5
         shadow-sm hover:shadow-md active:scale-[0.98];
}
.btn-secondary {
  @apply px-4 py-2 border border-gray-200 text-gray-600 hover:bg-gray-50 rounded-xl 
         transition-all cursor-pointer text-sm flex items-center gap-1.5
         active:scale-[0.98];
}

/* Modal transitions */
.modal-enter-active, .modal-leave-active { 
  transition: opacity 0.2s ease, transform 0.2s ease; 
}
.modal-enter-from, .modal-leave-to { 
  opacity: 0; 
  transform: scale(0.95); 
}
</style>