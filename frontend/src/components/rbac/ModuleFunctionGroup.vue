<template>
  <div>
    <!-- Module header row -->
    <div
      class="flex items-center gap-3 px-4 py-3 bg-gray-50 cursor-pointer hover:bg-gray-100 transition-colors border-b border-gray-200"
      @click="isOpen = !isOpen"
    >
      <input
        type="checkbox"
        :checked="isModuleChecked"
        :indeterminate.prop="isModuleIndeterminate"
        @change.stop="$emit('toggle-module', module.id)"
        @click.stop
        class="w-4 h-4 rounded"
      />
      <component :is="isOpen ? ChevronDown : ChevronRight" class="w-4 h-4 text-gray-400 flex-shrink-0" />
      <span class="text-sm font-semibold text-bfs-navy">{{ module.name }}</span>
      <span class="ml-auto text-xs text-gray-400 flex-shrink-0">
        {{ checkedCount }} / {{ module.functions.length }}
      </span>
    </div>

    <!-- Function rows — TANPA header legend (sudah di modal) -->
    <Transition name="slide">
      <div v-if="isOpen" class="divide-y divide-gray-100 bg-white">
        <div
          v-for="fn in module.functions"
          :key="fn.id"
          class="grid grid-cols-12 px-4 py-2.5 items-center hover:bg-gray-50 transition-colors"
          :class="{ 'opacity-40': !selections[fn.id]?.checked }"
        >
          <!-- Function name -->
          <div class="col-span-4 flex items-center gap-2.5">
            <input
              type="checkbox"
              :checked="selections[fn.id]?.checked"
              @change="$emit('toggle-function', fn.id)"
              class="w-4 h-4 rounded border-gray-300 text-bfs-gold focus:ring-bfs-gold"
            />
            <span class="text-sm text-gray-700 truncate">{{ fn.name }}</span>
          </div>

          <!-- Actions -->
          <div
            v-for="action in ACTIONS"
            :key="action.key"
            class="col-span-1 flex justify-center"
          >
            <input
              type="checkbox"
              :checked="selections[fn.id]?.[action.key]"
              :disabled="!selections[fn.id]?.checked"
              @change="$emit('toggle-action', fn.id, action.key)"
              class="w-3.5 h-3.5 rounded border-gray-300 text-bfs-gold focus:ring-bfs-gold disabled:opacity-25 cursor-pointer disabled:cursor-not-allowed"
            />
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ChevronRight, ChevronDown } from 'lucide-vue-next'

const props = defineProps({
  module:     { type: Object, required: true },
  selections: { type: Object, required: true },
})
defineEmits(['toggle-module', 'toggle-function', 'toggle-action'])

const isOpen = ref(false)

const ACTIONS = [
  { key: 'can_read'    },
  { key: 'can_create'  },
  { key: 'can_update'  },
  { key: 'can_delete'  },
  { key: 'can_approve' },
  { key: 'can_print'   },
  { key: 'can_export'  },
]

const checkedCount = computed(() =>
  props.module.functions.filter(fn => props.selections[fn.id]?.checked).length
)
const isModuleChecked = computed(() =>
  props.module.functions.length > 0 &&
  checkedCount.value === props.module.functions.length
)
const isModuleIndeterminate = computed(() =>
  checkedCount.value > 0 &&
  checkedCount.value < props.module.functions.length
)
</script>

<style scoped>
.slide-enter-active, .slide-leave-active { transition: all 0.15s ease; overflow: hidden; }
.slide-enter-from, .slide-leave-to { max-height: 0; opacity: 0; }
.slide-enter-to, .slide-leave-from { max-height: 9999px; opacity: 1; }
</style>