<template>
  <div class="fixed top-14 z-30 w-full bg-white border-b border-erp-border px-4 py-2 flex items-center justify-between shadow-sm">
    <!-- Dynamic Breadcrumb -->
    <nav class="flex items-center gap-2 text-sm">
      <template v-for="(crumb, index) in breadcrumbs" :key="index">
        <router-link 
          v-if="crumb.path && !crumb.isLast" 
          :to="crumb.path"
          class="text-erp-text-light hover:text-bfs-navy transition-colors"
        >
          {{ crumb.label }}
        </router-link>
        <span 
          v-else-if="!crumb.isLast"
          class="text-erp-text-light"
        >
          {{ crumb.label }}
        </span>
        <span 
          v-else
          class="font-semibold text-bfs-navy"
        >
          {{ crumb.label }}
        </span>
        <ChevronRight 
          v-if="index < breadcrumbs.length - 1" 
          class="w-4 h-4 text-erp-text-light" 
        />
      </template>
    </nav>

    <!-- Location & Language -->
    <div class="flex items-center gap-4 text-sm">
      <div class="flex items-center gap-2">
        <span class="text-erp-text-light font-medium">Location :</span>
        <select class="border border-erp-border rounded px-2 py-1 text-sm bg-white">
          <option>BFS (Build Financial System)</option>
        </select>
      </div>
      <div class="flex items-center gap-2">
        <span class="text-erp-text-light font-medium">Language :</span>
        <select class="border border-erp-border rounded px-2 py-1 text-sm bg-white">
          <option>English</option>
          <option>Bahasa Indonesia</option>
        </select>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ChevronRight } from 'lucide-vue-next'
import { useBreadcrumb } from '../composables/useBreadcrumb.js'

const { breadcrumbs } = useBreadcrumb()
</script>