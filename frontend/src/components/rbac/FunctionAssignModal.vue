<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-[60] flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/50" />

      <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-4xl z-10 flex flex-col max-h-[90vh]"
           style="isolation: isolate;">

        <!-- Title Bar (Sokka style) -->
        <div class="bg-slate-200 border-b border-slate-300 px-4 py-2 flex items-center justify-between text-sm font-semibold text-slate-800 rounded-t-2xl flex-shrink-0">
          <div class="flex items-center gap-2">
            <span class="text-base">📋</span>
            <span>Setting | Function Authorization | User Authorization Group</span>
          </div>
          <button @click="$emit('close')" class="text-slate-400 hover:text-slate-600 transition-colors">
            <X class="w-4 h-4" />
          </button>
        </div>

        <!-- ── Sub Header ── -->
        <div class="px-6 py-3 border-b border-slate-100 flex-shrink-0 bg-slate-50/50">
          <div>
            <h3 class="text-base font-bold text-slate-800">Function Authorization</h3>
            <p class="text-xs text-slate-400 mt-0.5">
              Group: <span class="font-semibold text-bfs-navy">{{ group.group_name }}</span>
              — {{ group.description }}
            </p>
          </div>
        </div>

        <!-- ── Sticky column header ── -->
        <div class="flex-shrink-0 grid grid-cols-12 px-4 py-2.5
                    bg-slate-100 border-b border-slate-300
                    text-[10px] font-bold text-slate-500 uppercase tracking-wider
                    shadow-sm z-10">
          <div class="col-span-4 pl-8">Function</div>
          <div class="col-span-1 text-center">Read</div>
          <div class="col-span-1 text-center">Create</div>
          <div class="col-span-1 text-center">Update</div>
          <div class="col-span-1 text-center">Delete</div>
          <div class="col-span-1 text-center">Approve</div>
          <div class="col-span-1 text-center">Print</div>
          <div class="col-span-2 text-center font-bold">Export</div>
        </div>

        <!-- ── Scroll area — recursive module tree ── -->
        <div class="flex-1 min-h-0 overflow-y-auto p-4 bg-slate-50/50">
          <div v-if="isLoading" class="flex justify-center items-center py-20">
            <Loader2 class="w-7 h-7 animate-spin text-bfs-gold" />
          </div>
          <div v-else class="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
            <!-- Master node: Function List -->
            <div>
              <div class="flex items-center gap-2 py-2 select-none">
                <input
                  type="checkbox"
                  :checked="isAllSelected"
                  :indeterminate.prop="isIndeterminate"
                  @change="toggleSelectAll"
                  class="w-4 h-4 rounded border-slate-300 text-bfs-gold focus:ring-bfs-gold cursor-pointer"
                />
                <span class="text-sm font-bold text-slate-800 flex items-center gap-1.5">
                  📁 Function List
                </span>
                <span class="text-xs text-slate-400 font-normal ml-2">
                  ({{ selectedCount }} / {{ totalFunctions }} functions selected)
                </span>
              </div>
              <div class="pl-4 relative">
                <!-- Vertical line connecting root modules -->
                <div class="absolute left-2.5 top-0 bottom-4 w-px border-l border-dashed border-slate-300"></div>
                <RbacTreeNode
                  v-for="module in moduleTree"
                  :key="module.id"
                  :node="module"
                  :selections="selections"
                  :level="0"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- ── Footer ── -->
        <div class="px-6 py-4 border-t border-slate-200 flex items-center justify-between flex-shrink-0 bg-bfs-navy/5 rounded-b-2xl">
          <p class="text-xs text-bfs-navy font-semibold">Current Status: Edit Mode</p>
          <div class="flex gap-2">
            <button @click="$emit('close')" class="btn-secondary text-sm">
              Back To Edit Admin Group
            </button>
            <button
              @click="handleApply"
              :disabled="isSaving"
              class="btn-primary text-sm flex items-center gap-1.5"
            >
              <Loader2 v-if="isSaving" class="w-3.5 h-3.5 animate-spin" />
              <Check v-else class="w-3.5 h-3.5" />
              Apply
            </button>
          </div>
        </div>

      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRbacStore } from '../../stores/rbac.js'
import RbacTreeNode from './RbacTreeNode.vue'
import { X, Loader2, Check } from 'lucide-vue-next'

const props = defineProps({ group: { type: Object, required: true } })
const emit  = defineEmits(['close'])

const rbacStore = useRbacStore()
const isLoading = ref(true)
const isSaving  = ref(false)

// selections: { [function_id]: { checked, can_create, can_read, ... } }
const selections  = reactive({})
const moduleTree  = ref([])

// ── Computed ───────────────────────────────────────────────────────────────
const totalFunctions = computed(() => Object.keys(selections).length)
const selectedCount  = computed(() =>
  Object.values(selections).filter(s => s.checked).length
)
const isAllSelected  = computed(() =>
  totalFunctions.value > 0 && selectedCount.value === totalFunctions.value
)
const isIndeterminate = computed(() =>
  selectedCount.value > 0 && selectedCount.value < totalFunctions.value
)

// Helper: Recursively build the tree from flat modules & functions
const buildTree = (modules, functions) => {
  const functionsByParent = {}
  const rootFunctionsByModule = {}

  functions.forEach(f => {
    if (f.parent) {
      const parentId = typeof f.parent === 'object' ? f.parent.id : f.parent
      if (!functionsByParent[parentId]) {
        functionsByParent[parentId] = []
      }
      functionsByParent[parentId].push(f)
    } else {
      if (!rootFunctionsByModule[f.module]) {
        rootFunctionsByModule[f.module] = []
      }
      rootFunctionsByModule[f.module].push(f)
    }
  })

  const buildNode = (f) => {
    const children = (functionsByParent[f.id] || []).map(buildNode)
    children.sort((a, b) => a.order - b.order)
    return {
      ...f,
      children,
      isLeaf: children.length === 0
    }
  }

  return modules.map(m => {
    const rootFns = (rootFunctionsByModule[m.id] || []).map(buildNode)
    rootFns.sort((a, b) => a.order - b.order)
    return {
      id: `module-${m.id}`,
      isModule: true,
      name: m.name,
      code: m.code,
      children: rootFns,
      isLeaf: rootFns.length === 0
    }
  })
}

// ── Load data ──────────────────────────────────────────────────────────────
onMounted(async () => {
  isLoading.value = true
  try {
    const [modules, functions, assigned] = await Promise.all([
      rbacStore.fetchModules(),
      rbacStore.fetchFunctions(),
      rbacStore.fetchGroupFunctions(props.group.id),
    ])

    const assignedMap = {}
    assigned.forEach(gf => { assignedMap[gf.function] = gf })

    moduleTree.value = buildTree(
      modules.filter(mod => mod.is_active),
      functions.filter(fn => fn.is_active)
    ).filter(mod => mod.children.length > 0)

    functions.forEach(fn => {
      const gf = assignedMap[fn.id]
      selections[fn.id] = {
        checked:     !!gf,
        can_create:  gf?.can_create  || false,
        can_read:    gf?.can_read    ?? true,
        can_update:  gf?.can_update  || false,
        can_delete:  gf?.can_delete  || false,
        can_approve: gf?.can_approve || false,
        can_print:   gf?.can_print   || false,
        can_export:  gf?.can_export  || false,
      }
    })
  } catch (err) {
    console.error('FunctionAssign load error:', err)
  } finally {
    isLoading.value = false
  }
})

// ── Toggle helpers ─────────────────────────────────────────────────────────
function toggleSelectAll() {
  const newVal = !isAllSelected.value
  Object.keys(selections).forEach(id => {
    selections[id].checked = newVal
  })
}

// ── Apply ──────────────────────────────────────────────────────────────────
async function handleApply() {
  isSaving.value = true
  try {
    const functions = Object.entries(selections)
      .filter(([, s]) => s.checked)
      .map(([fnId, s]) => ({
        function_id: parseInt(fnId),
        can_create:  s.can_create,
        can_read:    s.can_read,
        can_update:  s.can_update,
        can_delete:  s.can_delete,
        can_approve: s.can_approve,
        can_print:   s.can_print,
        can_export:  s.can_export,
      }))

    await rbacStore.assignFunctions(props.group.id, functions)
    emit('close')
  } catch (err) {
    console.error('Failed to apply functions', err)
  } finally {
    isSaving.value = false
  }
}
</script>

<style scoped>
@reference "../../style.css";

.btn-primary   { @apply px-4 py-2 bg-bfs-gold hover:bg-bfs-gold-dark text-white font-medium rounded-lg transition-colors disabled:opacity-60; }
.btn-secondary { @apply px-4 py-2 border border-gray-200 text-gray-600 hover:bg-gray-50 rounded-lg transition-colors; }
</style>