<template>
  <Panel title="Master Payment To" subtitle="Setting | Master Payment To">
    <!-- Main Card Wrapper -->
    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden flex flex-col relative w-full">
      <!-- Glassmorphism header decoration -->
      <div class="absolute top-0 left-0 w-full h-32 bg-gradient-to-br from-bfs-navy/5 to-bfs-gold/5 pointer-events-none"></div>

      <div class="p-6 relative">
        <PaymentToTable />
      </div>
    </div>
  </Panel>
</template>

<script setup>
import Panel from '../../../components/Panel.vue'
import PaymentToTable from './PaymentToTable.vue'
</script>
