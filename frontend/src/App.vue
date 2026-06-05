<template>
  <!-- Auth Layout (Login) - No header, no sidebar -->
  <template v-if="isAuthPage">
    <router-view />
  </template>

  <!-- Default Layout (App with header + sidebar) -->
  <div v-else class="h-screen flex flex-col bg-erp-bg overflow-hidden">
    <TopNav 
      :activeModule="activeModule" 
      :modules="modules" 
      @update:activeModule="handleModuleChange"
      @toggle-sidebar="toggleSidebar"
    />

    <div class="flex-1 flex overflow-hidden">
      <AppSidebar 
        v-if="isSidebarVisible"
        :activeModule="activeModule"
        :activeModuleName="currentModule?.name"
        @navigate="handleNav"
      />

      <div 
          class="flex-1 overflow-auto transition-all duration-300 pt-10"
          :class="isSidebarVisible ? 'ml-64' : 'ml-0'"
        >
        <ToolBar />
        <main class="p-4">
          <router-view />
        </main>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import TopNav from './components/TopNav.vue'
import AppSidebar from './components/AppSidebar.vue'
import ToolBar from './components/ToolBar.vue'

import { 
  ShoppingCart, 
  BookOpen, 
  Receipt, 
  TrendingUp, 
  CreditCard, 
  Truck, 
  Landmark, 
  Package, 
  FolderKanban, 
  Settings 
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()

const isAuthPage = computed(() => route.meta?.layout === 'auth')

const modules = [
  { id: 'commercial', name: 'Commercial', icon: ShoppingCart },
  { id: 'gl', name: 'General Ledger', icon: BookOpen },
  { id: 'ar', name: 'Account Receivable', icon: Receipt },
  { id: 'sales', name: 'Sales', icon: TrendingUp },
  { id: 'ap', name: 'Account Payable', icon: CreditCard },
  { id: 'purchases', name: 'Purchases', icon: Truck },
  { id: 'finance', name: 'Finance', icon: Landmark },
  { id: 'assets', name: 'Assets', icon: Package },
  { id: 'inventory', name: 'Inventory', icon: Package },
  { id: 'projects', name: 'Projects', icon: FolderKanban },
  { id: 'settings', name: 'Settings', icon: Settings },
]

const isSidebarVisible = ref(false)
const activeModule = ref('finance')
const lastToggledModule = ref('')

const currentModule = computed(() => 
  modules.find(m => m.id === activeModule.value)
)

const handleModuleChange = (id) => {
  activeModule.value = id
}

const toggleSidebar = (id) => {
  if (lastToggledModule.value === id && isSidebarVisible.value) {
    isSidebarVisible.value = false
  } else {
    isSidebarVisible.value = true
    lastToggledModule.value = id
  }
}

const handleNav = (item) => {
  // Jika item punya url_path langsung, pakai itu
  const urlPath = item.url_path?.trim()
  if (urlPath && urlPath !== 'undefined') {
    router.push(urlPath)
    return
  }

  const mod = (item.module_code?.trim() && item.module_code !== 'undefined')
    ? item.module_code.trim()
    : activeModule.value

  const slug = (item.name || '')
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '')

  router.push(`/${mod}/${slug}`)
}
</script>