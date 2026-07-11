<template>
  <div class="bg-white rounded-lg shadow-sm border border-erp-border">
    <!-- Header -->
    <div 
      v-if="title"
      class="flex items-center gap-2 px-4 py-3 bg-gradient-to-r from-gray-50 to-white border-b border-erp-border rounded-t-lg"
    >
      <component 
        v-if="icon" 
        :is="icons[icon]" 
        class="w-5 h-5 text-bfs-gold" 
      />
      <h3 class="font-semibold text-erp-text">{{ title }}</h3>
      <div class="ml-auto flex items-center gap-2">
        <slot name="actions" />
      </div>
    </div>
    
    <!-- Content -->
    <div class="p-4">
      <slot />
    </div>
  </div>
</template>

<script setup>
import { Filter, Table, Settings, FileText } from 'lucide-vue-next'

defineProps({
  title: String,
  icon: String,
})

const icons = {
  Filter,
  Table,
  Settings,
  FileText,
}
</script>