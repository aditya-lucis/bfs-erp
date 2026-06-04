<template>
  <aside class="fixed top-14 left-0 z-40 h-[calc(100vh-3.5rem)] w-64 bg-white border-r border-gray-200 shadow-lg flex flex-col transition-all">

    <!-- Header module name — sama persis dengan asli -->
    <div class="flex items-center justify-between px-4 py-3 bg-bfs-navy text-white">
      <span class="text-sm font-semibold truncate">{{ activeModuleName }}</span>
    </div>

    <!-- Loading skeleton -->
    <div v-if="menuStore.isLoading" class="flex-1 px-4 py-4 space-y-2">
      <div class="h-3 bg-gray-200 rounded animate-pulse w-3/4" />
      <div class="h-3 bg-gray-200 rounded animate-pulse w-1/2" />
      <div class="h-3 bg-gray-200 rounded animate-pulse w-2/3" />
      <div class="h-3 bg-gray-200 rounded animate-pulse w-4/5" />
    </div>

    <!-- Menu nav -->
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

const props = defineProps(['activeModule', 'activeModuleName'])
defineEmits(['navigate'])

const menuStore = useMenuStore()

// Cari items untuk module yang aktif dari backend tree
// Fallback ke array kosong kalau module belum ada di tree
const currentMenuItems = computed(() => {
  if (!menuStore.tree.length) return []

  const module = menuStore.tree.find(
    m => m.module_code === props.activeModule
  )
  return module?.children ?? []
})
</script>