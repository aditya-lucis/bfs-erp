<template>
  <aside class="fixed top-14 left-0 z-40 h-[calc(100vh-3.5rem)] w-64 bg-white border-r border-gray-200 shadow-lg flex flex-col transition-all">
    <div class="flex items-center justify-between px-4 py-3 bg-bfs-navy text-white">
      <span class="text-sm font-semibold truncate">{{ activeModuleName }}</span>
    </div>

    <nav class="flex-1 overflow-y-auto py-2">
      <SidebarMenuItem
        v-for="item in currentMenuItems"
        :key="item.name"
        :item="item"
        :depth="0"
        :moduleId="activeModule"
        @navigate="$emit('navigate', $event)"
      />
    </nav>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { menuData } from '../menuData.js'
import SidebarMenuItem from './SidebarMenuItem.vue'

const props = defineProps(['activeModule', 'activeModuleName'])

const currentMenuItems = computed(() => {
  return menuData[props.activeModule] || []
})
</script>