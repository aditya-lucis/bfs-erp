<template>
  <Panel title="Master Type" subtitle="Settings | Master Type">
    <div class="flex flex-col md:flex-row items-start gap-6">
      
      <!-- Sidebar Navigation for Master Types -->
      <div class="w-full md:w-64 flex-shrink-0 sticky top-6 self-start z-10">
        <div class="bg-white/80 backdrop-blur-xl border border-gray-100 rounded-2xl shadow-sm p-4">
          <h3 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-4 px-3">Categories</h3>
          <nav class="space-y-1.5">
            <button 
              v-for="tab in tabs" 
              :key="tab.id"
              @click="activeTab = tab.id"
              class="w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-300 relative group overflow-hidden"
              :class="activeTab === tab.id ? 'text-bfs-navy bg-bfs-navy/5 shadow-sm' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'"
            >
              <!-- Animated Background for Active State -->
              <div 
                v-if="activeTab === tab.id" 
                class="absolute left-0 top-0 bottom-0 w-1 bg-bfs-gold rounded-l-xl transition-all duration-300"
              ></div>
              
              <div class="flex items-center gap-3 relative z-10">
                <component :is="tab.icon" class="w-4 h-4 transition-transform group-hover:scale-110" 
                  :class="activeTab === tab.id ? 'text-bfs-gold' : 'text-gray-400'" />
                <span>{{ tab.name }}</span>
              </div>
              
              <ChevronRight v-if="activeTab === tab.id" class="w-4 h-4 text-bfs-gold opacity-100 transition-opacity" />
              <ChevronRight v-else class="w-4 h-4 text-gray-300 opacity-0 group-hover:opacity-100 transition-opacity transform -translate-x-2 group-hover:translate-x-0" />
            </button>
          </nav>
        </div>
      </div>

      <!-- Main Content Area with Transition -->
      <div class="flex-1 min-w-0">
        <div class="bg-white/90 backdrop-blur-xl border border-gray-100 rounded-2xl shadow-sm p-6 min-h-[500px]">
          <Transition name="fade-slide" mode="out-in">
            <KeepAlive>
              <component :is="currentTabComponent" :key="activeTab" />
            </KeepAlive>
          </Transition>
        </div>
      </div>

    </div>
  </Panel>
</template>

<script setup>
import { ref, computed } from 'vue'
import Panel from '../../../components/Panel.vue'
import { FileText, Building2, FileSignature, ChevronRight } from 'lucide-vue-next'
import MasterBankTab from '../../../components/settings/master_type/MasterBankTab.vue'
import TransactionTypeTab from '../../../components/settings/master_type/TransactionTypeTab.vue'

// Dummy component for upcoming tabs
const ComingSoonTab = {
  template: `
    <div class="flex flex-col items-center justify-center h-64 text-center">
      <div class="w-16 h-16 bg-gray-100 rounded-2xl flex items-center justify-center mb-4 shadow-inner">
        <svg class="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <h3 class="text-lg font-bold text-gray-700">Coming Soon</h3>
      <p class="text-sm text-gray-500 mt-2 max-w-xs">This master data module is currently under development.</p>
    </div>
  `
}

const tabs = [
  { id: 'transaction-type', name: 'Transaction Type', icon: FileText, component: TransactionTypeTab },
  { id: 'master-bank', name: 'Master Bank', icon: Building2, component: MasterBankTab },
  { id: 'master-amandement', name: 'Master Amandement', icon: FileSignature, component: ComingSoonTab },
]

const activeTab = ref('transaction-type')

const currentTabComponent = computed(() => {
  const tab = tabs.find(t => t.id === activeTab.value)
  return tab ? tab.component : null
})
</script>

<style scoped>
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(10px) scale(0.99);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px) scale(0.99);
}
</style>
