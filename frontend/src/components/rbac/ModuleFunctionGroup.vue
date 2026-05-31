<template>
  <div class="border border-gray-200 rounded-xl overflow-hidden">

    <!-- Module header -->
    <div
      class="flex items-center gap-3 px-4 py-3 bg-gray-50 cursor-pointer hover:bg-gray-100 transition-colors"
      @click="isOpen = !isOpen"
    >
      <input
        type="checkbox"
        :checked="isModuleChecked"
        :indeterminate="isModuleIndeterminate"
        @change.stop="$emit('toggle-module', module.id)"
        @click.stop
        class="w-4 h-4 rounded"
      />
      <component :is="isOpen ? ChevronDown : ChevronRight" class="w-4 h-4 text-gray-400" />
      <span class="text-sm font-semibold text-bfs-navy">{{ module.name }}</span>
      <span class="ml-auto text-xs text-gray-400">
        {{ checkedCount }} / {{ module.functions.length }}
      </span>
    </div>

    <!-- Functions list -->
    <Transition name="slide">
      <div v-if="isOpen" class="divide-y divide-gray-100">

        <!-- Action legend header -->
        <div class="grid grid-cols-12 px-4 py-2 bg-blue-50/50 text-[10px] font-semibold text-gray-500 uppercase tracking-wide">
          <div class="col-span-4">Function</div>
          <div class="col-span-1 text-center">Read</div>
          <div class="col-span-1 text-center">Create</div>
          <div class="col-span-1 text-center">Update</div>
          <div class="col-span-1 text-center">Delete</div>
          <div class="col-span-1 text-center">Approve</div>
          <div class="col-span-1 text-center">Print</div>
          <div class="col-span-2 text-center">Export</div>
        </div>

        <div
          v-for="fn in module.functions"
          :key="fn.id"
          class="grid grid-cols-12 px-4 py-2.5 items-center hover:bg-gray-50 transition-colors"
          :class="{ 'opacity-50': !selections[fn.id]?.checked }"
        >
          <!-- Function name + checkbox -->
          <div class="col-span-4 flex items-center gap-2.5">
            <input
              type="checkbox"
              :checked="selections[fn.id]?.checked"
              @change="$emit('toggle-function', fn.id)"
              class="w-4 h-4 rounded border-gray-300 text-bfs-gold focus:ring-bfs-gold"
            />
            <span class="text-sm text-gray-700 truncate">{{ fn.name }}</span>
          </div>

          <!-- Action flags — hanya aktif kalau function di-check -->
          <template v-for="action in ACTIONS" :key="action.key">
            <div class="col-span-1 flex justify-center">
              <input
                type="checkbox"
                :checked="selections[fn.id]?.[action.key]"
                :disabled="!selections[fn.id]?.checked"
                @change="$emit('toggle-action', fn.id, action.key)"
                class="w-3.5 h-3.5 rounded border-gray-300 text-bfs-gold focus:ring-bfs-gold disabled:opacity-30"
              />
            </div>
          </template>
        </div>

      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ChevronRight, ChevronDown } from 'lucide-vue-next'

const props = defineProps({
  module:     { type: Object,  required: true },
  selections: { type: Object,  required: true },
})
defineEmits(['toggle-module', 'toggle-function', 'toggle-action'])

const isOpen = ref(false)

const ACTIONS = [
  { key: 'can_read',    label: 'Read'    },
  { key: 'can_create',  label: 'Create'  },
  { key: 'can_update',  label: 'Update'  },
  { key: 'can_delete',  label: 'Delete'  },
  { key: 'can_approve', label: 'Approve' },
  { key: 'can_print',   label: 'Print'   },
  { key: 'can_export',  label: 'Export'  },
]

const checkedCount = computed(() =>
  props.module.functions.filter(fn => props.selections[fn.id]?.checked).length
)
const isModuleChecked = computed(() =>
  props.module.functions.length > 0 &&
  checkedCount.value === props.module.functions.length
)
const isModuleIndeterminate = computed(() =>
  checkedCount.value > 0 && checkedCount.value < props.module.functions.length
)
</script>

<style scoped>
.slide-enter-active, .slide-leave-active { transition: all 0.2s ease; overflow: hidden; }
.slide-enter-from, .slide-leave-to { max-height: 0; opacity: 0; }
.slide-enter-to, .slide-leave-from { max-height: 2000px; opacity: 1; }
</style>