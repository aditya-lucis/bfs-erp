<template>
  <!-- Node Row -->
  <tr 
    class="group transition-colors"
    :class="rowClass"
  >
    <!-- Display Number -->
    <td class="px-4 py-0 text-center">
      <span class="text-[11px] font-mono font-semibold" :class="numberClass">
        {{ node.display_number }}
      </span>
    </td>

    <!-- COA Header / Item Name -->
    <td class="px-4 py-0">
      <div 
        class="flex items-center py-2.5"
        :style="{ paddingLeft: `${level * 28}px` }"
      >
        <!-- Expand/Collapse Toggle -->
        <button 
          v-if="hasChildren && node.item_type !== 'item'"
          @click="toggleExpand"
          class="w-5 h-5 flex items-center justify-center text-gray-400 hover:text-gray-600 rounded transition-colors mr-1.5 shrink-0"
        >
          <ChevronDown 
            v-if="isExpanded" 
            class="w-3.5 h-3.5" 
          />
          <ChevronRight 
            v-else 
            class="w-3.5 h-3.5" 
          />
        </button>
        <div v-else class="w-5 mr-1.5 shrink-0"></div>

        <!-- Icon -->
        <div 
          class="w-7 h-7 rounded-lg flex items-center justify-center shrink-0 mr-2.5"
          :class="iconBgClass"
        >
          <component 
            :is="nodeIcon" 
            class="w-3.5 h-3.5"
            :class="iconColorClass"
          />
        </div>

        <!-- Name -->
        <div class="min-w-0 flex-1">
          <span 
            class="text-sm leading-tight"
            :class="nameClass"
          >
            {{ node.description || node.item_name }}
          </span>
        </div>
      </div>
    </td>

    <!-- Item Code -->
    <td class="px-4 py-2.5">
      <span v-if="node.item_type === 'item' && node.item_code" class="inline-flex items-center px-2 py-0.5 rounded-md bg-gray-50 border border-gray-100 text-[11px] font-mono text-gray-500">
        {{ node.item_code }}
      </span>
    </td>

    <!-- Remarks -->
    <td class="px-4 py-2.5">
      <span v-if="node.remarks" class="text-xs text-gray-500 line-clamp-1">{{ node.remarks }}</span>
    </td>

    <!-- Unit -->
    <td class="px-4 py-2.5 text-center">
      <span v-if="node.unit_name" class="text-[11px] font-medium text-gray-500 uppercase">{{ node.unit_name }}</span>
    </td>

    <!-- Actions -->
    <td class="px-4 py-2.5 pr-6">
      <div class="flex justify-end gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
        <!-- Add Child -->
        <button 
          v-if="canAddChild && canCreate"
          @click="$emit('add-child', node)"
          class="action-btn text-gray-400 hover:text-emerald-600 hover:bg-emerald-50"
          :title="addChildTitle"
        >
          <Plus class="w-3.5 h-3.5" />
        </button>
        <!-- Edit -->
        <button 
          v-if="canUpdate"
          @click="$emit('edit', node)"
          class="action-btn text-gray-400 hover:text-bfs-gold hover:bg-yellow-50"
          title="Edit"
        >
          <Pencil class="w-3.5 h-3.5" />
        </button>
        <!-- Delete -->
        <button 
          v-if="canDelete"
          @click="$emit('delete', node)"
          class="action-btn text-gray-400 hover:text-red-500 hover:bg-red-50"
          title="Delete"
        >
          <Trash2 class="w-3.5 h-3.5" />
        </button>
      </div>
    </td>
  </tr>

  <!-- Children (recursive) -->
  <template v-if="isExpanded && hasChildren">
    <TreeNode
      v-for="child in node.children"
      :key="child.id"
      :node="child"
      :level="level + 1"
      @add-child="$emit('add-child', $event)"
      @edit="$emit('edit', $event)"
      @delete="$emit('delete', $event)"
    />
  </template>
</template>

<script setup>
import { ref, computed } from 'vue'
import { 
  FolderOpen, 
  Folder, 
  Package, 
  ChevronRight, 
  ChevronDown,
  Plus, 
  Pencil, 
  Trash2 
} from 'lucide-vue-next'
import { usePermission } from '../../composables/usePermission.js'

const props = defineProps({
  node: { type: Object, required: true },
  level: { type: Number, default: 0 },
})

defineEmits(['add-child', 'edit', 'delete'])

const { canCreate, canUpdate, canDelete } = usePermission('FINANCE-BUDGET-COMPONENT')

const isExpanded = ref(true)

const hasChildren = computed(() => props.node.children?.length > 0)

const canAddChild = computed(() => {
  return props.node.item_type !== 'item'
})

const addChildTitle = computed(() => {
  if (props.node.item_type === 'header') return 'Add Sub Header'
  if (props.node.item_type === 'sub_header') return 'Add Item'
  return ''
})

const nodeIcon = computed(() => {
  switch (props.node.item_type) {
    case 'header': return FolderOpen
    case 'sub_header': return Folder
    case 'item': return Package
    default: return Folder
  }
})

// Row background based on type
const rowClass = computed(() => {
  switch (props.node.item_type) {
    case 'header': return 'bg-slate-50/60 hover:bg-slate-50 border-b border-gray-100'
    case 'sub_header': return 'bg-white hover:bg-gray-50/50 border-b border-gray-50'
    case 'item': return 'bg-white hover:bg-yellow-50/30 border-b border-gray-50'
    default: return 'bg-white hover:bg-gray-50/50 border-b border-gray-50'
  }
})

// Display number color
const numberClass = computed(() => {
  switch (props.node.item_type) {
    case 'header': return 'text-slate-500'
    case 'sub_header': return 'text-gray-400'
    case 'item': return 'text-gray-300'
    default: return 'text-gray-400'
  }
})

// Icon background
const iconBgClass = computed(() => {
  switch (props.node.item_type) {
    case 'header': return 'bg-amber-50 border border-amber-100'
    case 'sub_header': return 'bg-blue-50 border border-blue-100'
    case 'item': return 'bg-gray-50 border border-gray-100'
    default: return 'bg-gray-50 border border-gray-100'
  }
})

// Icon color
const iconColorClass = computed(() => {
  switch (props.node.item_type) {
    case 'header': return 'text-amber-500'
    case 'sub_header': return 'text-blue-400'
    case 'item': return 'text-gray-400'
    default: return 'text-gray-400'
  }
})

// Name text style
const nameClass = computed(() => {
  switch (props.node.item_type) {
    case 'header': return 'font-semibold text-gray-800'
    case 'sub_header': return 'font-medium text-gray-700'
    case 'item': return 'text-gray-600'
    default: return 'text-gray-600'
  }
})

function toggleExpand() {
  isExpanded.value = !isExpanded.value
}
</script>

<style scoped>
@reference "../../style.css";
.action-btn {
  @apply w-7 h-7 rounded-lg flex items-center justify-center transition-all;
}
</style>