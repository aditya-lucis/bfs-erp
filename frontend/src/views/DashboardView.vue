<template>
  <div class="min-h-[60vh] flex flex-col items-center justify-center p-8">
    <div class="text-center mb-10">
      <h1 class="text-3xl font-bold text-bfs-navy mb-2">Select Dashboard</h1>
      <p class="text-erp-text-light">Choose a dashboard to view</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-4xl w-full">
      <!-- Penyerapan RAP Card -->
      <router-link 
        to="/finance/penyerapan-rap"
        class="group bg-white rounded-xl shadow-md border border-erp-border p-6 hover:shadow-lg hover:border-bfs-gold transition-all duration-300 cursor-pointer"
      >
        <div class="flex items-center gap-4 mb-4">
          <div class="w-12 h-12 bg-bfs-navy/10 rounded-lg flex items-center justify-center group-hover:bg-bfs-gold/20 transition-colors">
            <BarChart3 class="w-6 h-6 text-bfs-navy group-hover:text-bfs-gold" />
          </div>
          <div>
            <h3 class="font-semibold text-erp-text group-hover:text-bfs-navy">Penyerapan RAP</h3>
            <p class="text-xs text-erp-text-light">Finance Dashboard</p>
          </div>
        </div>
        <p class="text-sm text-erp-text-light">Monitor RAP absorption, PO, CBR, and payment realization.</p>
      </router-link>

      <!-- Placeholder for future dashboards -->
      <div class="bg-gray-50 rounded-xl border border-dashed border-gray-300 p-6 flex flex-col items-center justify-center text-gray-400">
        <Plus class="w-8 h-8 mb-2" />
        <p class="text-sm font-medium">More Dashboards</p>
        <p class="text-xs">Coming Soon</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { BarChart3, Plus } from 'lucide-vue-next'
</script>