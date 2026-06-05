<template>
  <aside class="fixed top-14 left-0 z-40 h-[calc(100vh-3.5rem)] w-64 bg-white border-r border-gray-200 shadow-lg flex flex-col transition-all">
    <div class="flex items-center justify-between px-4 py-3 bg-bfs-navy text-white">
      <span class="text-sm font-semibold truncate">{{ activeModuleName }}</span>
    </div>

    <div v-if="menuStore.isLoading" class="flex-1 px-4 py-4 space-y-2">
      <div class="h-3 bg-gray-200 rounded animate-pulse w-3/4" />
      <div class="h-3 bg-gray-200 rounded animate-pulse w-1/2" />
      <div class="h-3 bg-gray-200 rounded animate-pulse w-2/3" />
    </div>

    <nav v-else class="flex-1 overflow-y-auto py-2">
      <SidebarMenuItem
        v-for="item in currentMenuItems"
        :key="item.id || item.name"
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
import { useMenuStore } from '../stores/menu.js'
import SidebarMenuItem from './SidebarMenuItem.vue'

const props = defineProps({
  activeModule: { type: String, default: '' },
  activeModuleName: { type: String, default: 'Menu' }
})

const menuStore = useMenuStore()

const currentMenuItems = computed(() => {
  if (!menuStore.tree?.length) return []

  // Cari berdasarkan module_code
  let module = menuStore.tree.find(m => m.module_code === props.activeModule)

  // Fallback: cari berdasarkan nama jika module_code belum benar
  if (!module && props.activeModule) {
    module = menuStore.tree.find(m => 
      m.module_name?.toLowerCase() === props.activeModule.toLowerCase()
    )
  }

  return module?.children ?? []
})
</script>