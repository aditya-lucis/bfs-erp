<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-[60] flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/50" />

      <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-3xl z-10 flex flex-col max-h-[90vh]"
           style="isolation: isolate;">

        <!-- ── Header modal ── -->
        <div class="px-6 py-4 border-b border-gray-100 flex-shrink-0">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-base font-semibold text-gray-800">Function Authorization</h3>
              <p class="text-xs text-gray-400 mt-0.5">
                Group: <span class="font-medium text-bfs-navy">{{ group.group_name }}</span>
                — {{ group.description }}
              </p>
            </div>
            <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600">
              <X class="w-5 h-5" />
            </button>
          </div>

          <div class="mt-3 flex items-center gap-4">
            <label class="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                :checked="isAllSelected"
                :indeterminate.prop="isIndeterminate"
                @change="toggleSelectAll"
                class="w-4 h-4 rounded"
              />
              <span class="text-sm font-medium text-gray-700">Select All Modules</span>
            </label>
            <span class="text-xs text-gray-400">
              {{ selectedCount }} / {{ totalFunctions }} functions selected
            </span>
          </div>
        </div>

        <!-- ── Sticky column header — SELALU KELIHATAN ── -->
        <div class="flex-shrink-0 grid grid-cols-12 px-4 py-2.5
                    bg-slate-100 border-b-2 border-slate-300
                    text-[10px] font-bold text-gray-500 uppercase tracking-wider
                    shadow-sm z-10">
          <div class="col-span-4 pl-8">Function</div>
          <div class="col-span-1 text-center">Read</div>
          <div class="col-span-1 text-center">Create</div>
          <div class="col-span-1 text-center">Update</div>
          <div class="col-span-1 text-center">Delete</div>
          <div class="col-span-1 text-center">Approve</div>
          <div class="col-span-1 text-center">Print</div>
          <div class="col-span-2 text-center">Export</div>
        </div>

        <!-- ── Scroll area — konten module ── -->
        <div class="flex-1 min-h-0 overflow-y-auto">
          <div v-if="isLoading" class="flex justify-center items-center py-20">
            <Loader2 class="w-7 h-7 animate-spin text-bfs-gold" />
          </div>
          <div v-else class="divide-y divide-gray-100">
            <ModuleFunctionGroup
              v-for="module in moduleTree"
              :key="module.id"
              :module="module"
              :selections="selections"
              @toggle-module="toggleModule"
              @toggle-function="toggleFunction"
              @toggle-action="toggleAction"
            />
          </div>
        </div>

        <!-- ── Footer ── -->
        <div class="px-6 py-4 border-t border-gray-100 flex items-center justify-between flex-shrink-0 bg-bfs-navy/5">
          <p class="text-xs text-bfs-navy font-medium">Current Status: Edit Mode</p>
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
import ModuleFunctionGroup from './ModuleFunctionGroup.vue'
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

// ── Load data ──────────────────────────────────────────────────────────────
onMounted(async () => {
  isLoading.value = true
  try {
    const [modules, functions, assigned] = await Promise.all([
      rbacStore.fetchModules(),
      rbacStore.fetchFunctions(),
      rbacStore.fetchGroupFunctions(props.group.id),
    ])

    // Semua sudah array langsung — tidak perlu ?? lagi
    const assignedMap = {}
    assigned.forEach(gf => { assignedMap[gf.function] = gf })

    moduleTree.value = modules
      .filter(mod => mod.is_active)
      .map(mod => ({
        ...mod,
        functions: functions.filter(f => f.module === mod.id && !f.parent),
      }))
      .filter(mod => mod.functions.length > 0)

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

function toggleModule(moduleId) {
  // Cek apakah semua function di modul ini sudah checked
  const moduleFnIds = moduleTree.value
    .find(m => m.id === moduleId)
    ?.functions.map(f => f.id) || []

  const allChecked = moduleFnIds.every(id => selections[id]?.checked)
  moduleFnIds.forEach(id => {
    if (selections[id]) selections[id].checked = !allChecked
  })
}

function toggleFunction(fnId) {
  if (selections[fnId]) {
    selections[fnId].checked = !selections[fnId].checked
  }
}

function toggleAction(fnId, action) {
  if (selections[fnId]) {
    selections[fnId][action] = !selections[fnId][action]
    // Kalau ada action yang di-check → otomatis check functionnya
    if (selections[fnId][action]) {
      selections[fnId].checked = true
    }
  }
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