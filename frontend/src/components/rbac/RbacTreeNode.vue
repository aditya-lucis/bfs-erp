<template>
  <div class="select-none">
    <!-- Row content (Grid columns match headers) -->
    <div
      class="grid grid-cols-12 py-1.5 hover:bg-slate-50 transition-colors group relative items-center"
      :class="{ 'opacity-60': !isChecked && node.isLeaf }"
    >
      <!-- Function Name and Indentation (col-span-4) -->
      <div class="col-span-4 flex items-center relative py-1" :style="{ paddingLeft: `${level * 24}px` }">
        <!-- Tree Guide Lines -->
        <div v-if="level > 0" class="absolute top-0 bottom-0 flex items-center" :style="{ left: `${(level - 1) * 24 + 12}px` }">
          <div class="w-px h-full border-l border-dashed border-slate-300"></div>
          <div class="w-3 h-px border-t border-dashed border-slate-300"></div>
        </div>

        <div class="flex items-center gap-2 z-10 w-full">
          <!-- Collapse/Expand handle for parents -->
          <button
            v-if="!node.isLeaf"
            @click="isExpanded = !isExpanded"
            class="w-4 h-4 flex items-center justify-center text-slate-400 hover:text-slate-600 transition-colors flex-shrink-0"
          >
            <component :is="isExpanded ? ChevronDown : ChevronRight" class="w-3.5 h-3.5" />
          </button>
          <div v-else class="w-4 flex-shrink-0"></div>

          <!-- Left Checkbox -->
          <input
            type="checkbox"
            :checked="isChecked"
            :indeterminate.prop="isIndeterminate"
            @change="toggleChecked"
            class="w-4 h-4 rounded border-slate-300 text-bfs-gold focus:ring-bfs-gold cursor-pointer flex-shrink-0"
          />

          <!-- Node Icon -->
          <component
            :is="node.isModule ? Package : (node.isLeaf ? FileText : (isExpanded ? FolderOpen : Folder))"
            class="w-4 h-4 text-slate-400 flex-shrink-0"
            :class="{ 'text-bfs-navy': node.isModule, 'text-amber-500': !node.isLeaf && !node.isModule }"
          />

          <!-- Node Name -->
          <span
            class="text-sm text-slate-700 font-medium truncate"
            :class="{ 'font-semibold text-bfs-navy': node.isModule || !node.isLeaf }"
          >
            {{ node.name }}
          </span>
        </div>
      </div>

      <!-- Actions (col-span-8: 1, 1, 1, 1, 1, 1, 2) -->
      <template v-if="node.isLeaf">
        <div
          v-for="action in ACTIONS"
          :key="action.key"
          :class="action.key === 'can_export' ? 'col-span-2' : 'col-span-1'"
          class="flex justify-center z-10"
        >
          <input
            type="checkbox"
            :checked="selections[node.id]?.[action.key]"
            :disabled="!isChecked"
            @change="toggleAction(action.key)"
            class="w-3.5 h-3.5 rounded border-slate-300 text-bfs-gold focus:ring-bfs-gold disabled:opacity-25 cursor-pointer disabled:cursor-not-allowed"
          />
        </div>
      </template>
    </div>

    <!-- Children Nodes -->
    <div v-if="!node.isLeaf && isExpanded" class="relative">
      <RbacTreeNode
        v-for="child in node.children"
        :key="child.id"
        :node="child"
        :selections="selections"
        :level="level + 1"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ChevronRight, ChevronDown, Folder, FolderOpen, FileText, Package } from 'lucide-vue-next'

const props = defineProps({
  node:       { type: Object, required: true },
  selections: { type: Object, required: true },
  level:      { type: Number, default: 0 }
})

const isExpanded = ref(true)

const ACTIONS = [
  { key: 'can_read'    },
  { key: 'can_create'  },
  { key: 'can_update'  },
  { key: 'can_delete'  },
  { key: 'can_approve' },
  { key: 'can_print'   },
  { key: 'can_export'  },
]

// Helper: Traverse to get all leaf descendant nodes of the current node
const getLeafDescendants = (node) => {
  const leaves = []
  const traverse = (n) => {
    if (n.isLeaf) {
      leaves.push(n)
    } else if (n.children) {
      n.children.forEach(traverse)
    }
  }
  traverse(node)
  return leaves
}

const leaves = computed(() => getLeafDescendants(props.node))

const isChecked = computed(() => {
  if (props.node.isLeaf) {
    return props.selections[props.node.id]?.checked || false
  }
  return leaves.value.length > 0 && leaves.value.every(leaf => props.selections[leaf.id]?.checked)
})

const isIndeterminate = computed(() => {
  if (props.node.isLeaf) return false
  const checkedCount = leaves.value.filter(leaf => props.selections[leaf.id]?.checked).length
  return checkedCount > 0 && checkedCount < leaves.value.length
})

const toggleChecked = (e) => {
  const val = e.target.checked
  if (props.node.isLeaf) {
    if (props.selections[props.node.id]) {
      props.selections[props.node.id].checked = val
      if (val) {
        const s = props.selections[props.node.id]
        if (!s.can_read && !s.can_create && !s.can_update && !s.can_delete && !s.can_approve && !s.can_print && !s.can_export) {
          s.can_read = true
        }
      }
    }
  } else {
    leaves.value.forEach(leaf => {
      if (props.selections[leaf.id]) {
        props.selections[leaf.id].checked = val
        if (val) {
          const s = props.selections[leaf.id]
          if (!s.can_read && !s.can_create && !s.can_update && !s.can_delete && !s.can_approve && !s.can_print && !s.can_export) {
            s.can_read = true
          }
        }
      }
    })
  }
}

const toggleAction = (key) => {
  if (!props.node.isLeaf) return
  const s = props.selections[props.node.id]
  if (s) {
    s[key] = !s[key]
    // If any action is checked, automatically check the main function checkbox
    if (s[key]) {
      s.checked = true
    }
  }
}
</script>
