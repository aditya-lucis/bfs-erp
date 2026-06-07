<template>
  <!-- Baris akun -->
  <div
    class="grid grid-cols-12 items-center px-4 py-2.5 hover:bg-gray-50 transition-colors border-b border-gray-100 last:border-0"
    :style="{ paddingLeft: `${16 + node.level * 20}px` }"
  >
    <!-- Nama akun + toggle -->
    <div class="col-span-6 flex items-center gap-2 min-w-0">
      <!-- Toggle expand jika punya children -->
      <button
        v-if="node.children?.length"
        @click="$emit('toggle', node.id)"
        class="shrink-0 w-4 h-4 text-gray-400 hover:text-gray-600 transition-colors"
      >
        <ChevronRight
          class="w-4 h-4 transition-transform duration-200"
          :class="{ 'rotate-90': expandedIds.has(node.id) }"
        />
      </button>
      <span v-else class="shrink-0 w-4" />

      <!-- Ikon tipe akun -->
      <component :is="typeIcon" class="shrink-0 w-3.5 h-3.5" :class="typeColor" />

      <!-- Nomor + Nama -->
      <span class="text-sm font-mono text-gray-500 shrink-0">{{ node.account_number }}</span>
      <span
        class="text-sm truncate"
        :class="node.is_postable ? 'text-gray-800' : 'font-semibold text-gray-700'"
      >
        {{ node.account_name }}
      </span>
    </div>

    <!-- Tipe -->
    <div class="col-span-2">
      <span
        class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium"
        :class="typeBadgeClass"
      >
        {{ typeLabel }}
      </span>
    </div>

    <!-- Default Position -->
    <div class="col-span-1 text-xs text-gray-500">
      {{ node.default_position }}
    </div>

    <!-- Currency -->
    <div class="col-span-1 text-xs text-gray-500">
      {{ node.currency }}
    </div>

    <!-- Actions -->
    <div class="col-span-2 flex items-center justify-end gap-1">
      <button
        v-if="canCreate && node.is_header"
        @click="$emit('add-child', node)"
        class="p-1.5 text-gray-400 hover:text-bfs-gold hover:bg-yellow-50 rounded transition-colors"
        title="Add child account"
      >
        <Plus class="w-3.5 h-3.5" />
      </button>
      <button
        v-if="canUpdate"
        @click="$emit('edit', node)"
        class="p-1.5 text-gray-400 hover:text-blue-500 hover:bg-blue-50 rounded transition-colors"
        title="Edit"
      >
        <Pencil class="w-3.5 h-3.5" />
      </button>
      <button
        v-if="canDelete"
        @click="$emit('delete', node)"
        class="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded transition-colors"
        title="Delete"
      >
        <Trash2 class="w-3.5 h-3.5" />
      </button>
    </div>
  </div>

  <!-- Children (rekursif) -->
  <template v-if="node.children?.length && expandedIds.has(node.id)">
    <AccountTreeNode
      v-for="child in node.children"
      :key="child.id"
      :node="child"
      :expanded-ids="expandedIds"
      :can-create="canCreate"
      :can-update="canUpdate"
      :can-delete="canDelete"
      @toggle="$emit('toggle', $event)"
      @edit="$emit('edit', $event)"
      @delete="$emit('delete', $event)"
      @add-child="$emit('add-child', $event)"
    />
  </template>
</template>

<script setup>
import { computed } from 'vue'
import { ChevronRight, Plus, Pencil, Trash2, FolderOpen, Landmark, Coins, FileCheck, BookOpen } from 'lucide-vue-next'

const props = defineProps({
  node:        { type: Object,  required: true },
  expandedIds: { type: Object,  required: true }, // Set
  canCreate:   { type: Boolean, default: false },
  canUpdate:   { type: Boolean, default: false },
  canDelete:   { type: Boolean, default: false },
})

defineEmits(['toggle', 'edit', 'delete', 'add-child'])

// ── Ikon & badge per tipe akun ─────────────────────────────────────────────

const TYPE_CONFIG = {
  HEADER:        { icon: FolderOpen,  color: 'text-amber-500',  badge: 'bg-amber-50 text-amber-700',  label: 'Header'  },
  DETAIL:        { icon: BookOpen,    color: 'text-blue-500',   badge: 'bg-blue-50 text-blue-700',    label: 'Detail'  },
  DETAIL_BANK:   { icon: Landmark,    color: 'text-green-500',  badge: 'bg-green-50 text-green-700',  label: 'Bank'    },
  DETAIL_CASH:   { icon: Coins,       color: 'text-purple-500', badge: 'bg-purple-50 text-purple-700',label: 'Cash'    },
  DETAIL_CHEQUE: { icon: FileCheck,   color: 'text-rose-500',   badge: 'bg-rose-50 text-rose-700',    label: 'Cheque'  },
}

const config        = computed(() => TYPE_CONFIG[props.node.account_type] ?? TYPE_CONFIG.DETAIL)
const typeIcon      = computed(() => config.value.icon)
const typeColor     = computed(() => config.value.color)
const typeBadgeClass = computed(() => config.value.badge)
const typeLabel     = computed(() => config.value.label)
</script>