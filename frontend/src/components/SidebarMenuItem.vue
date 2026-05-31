<template>
  <div class="w-full">
    <button
      @click="toggle"
      class="w-full flex items-center justify-between py-2 px-4 text-xs hover:bg-gray-100 transition-colors text-gray-700"
      :style="{ paddingLeft: `${1 + depth * 1.5}rem` }"
    >
      <span class="truncate">{{ item.name }}</span>
      <span v-if="hasChildren" class="text-[10px] ml-2">{{ isOpen ? '▼' : '▶' }}</span>
    </button>

    <div v-if="hasChildren && isOpen" class="bg-gray-50 border-l border-gray-200">
      <SidebarMenuItem
        v-for="child in item.children"
        :key="child.name"
        :item="child"
        :depth="depth + 1"
        :moduleId="moduleId"
        @navigate="$emit('navigate', $event)"
      />
    </div>
  </div>
</template>

<script>
export default {
  name: 'SidebarMenuItem'
}
</script>

<script setup>
import { ref, computed } from 'vue'
const props = defineProps(['item', 'depth', 'moduleId'])
const emit = defineEmits(['navigate'])
const isOpen = ref(false)
const hasChildren = computed(() => props.item.children && props.item.children.length > 0)

const toggle = () => {
  if (hasChildren.value) {
    isOpen.value = !isOpen.value
  } else {
    emit('navigate', { 
      name: props.item.name, 
      moduleId: props.moduleId 
    })
  }
}
</script>