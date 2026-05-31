<template>
  <div class="min-h-[60vh] flex items-center justify-center">
    <div class="text-center max-w-lg mx-auto p-8">
      <!-- Animated Construction Icon -->
      <div class="relative mb-8">
        <div class="absolute inset-0 bg-bfs-gold/10 rounded-full animate-ping"></div>
        <div class="relative bg-gradient-to-br from-bfs-navy to-bfs-navy-light rounded-2xl p-6 inline-block shadow-xl">
          <Construction class="w-16 h-16 text-bfs-gold animate-bounce" />
        </div>
      </div>

      <!-- Title -->
      <h1 class="text-3xl font-bold text-bfs-navy mb-3">
        {{ pageTitle }}
      </h1>

      <!-- Subtitle -->
      <p class="text-lg text-erp-text-light mb-2">
        Fitur ini sedang dalam pengembangan
      </p>
      <p class="text-sm text-erp-text-light/70 mb-8">
        This feature is currently under construction
      </p>

      <!-- Progress Indicator -->
      <div class="bg-white rounded-xl shadow-sm border border-erp-border p-6 mb-6">
        <div class="flex items-center justify-between mb-3">
          <span class="text-sm font-medium text-erp-text">Development Progress</span>
          <span class="text-sm font-bold text-bfs-gold">{{ progress }}%</span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
          <div 
            class="bg-gradient-to-r from-bfs-gold to-bfs-gold-light h-3 rounded-full transition-all duration-1000 ease-out"
            :style="{ width: progress + '%' }"
          ></div>
        </div>
        <div class="flex justify-between mt-2 text-xs text-erp-text-light">
          <span>Planning</span>
          <span>Development</span>
          <span>Testing</span>
          <span>Release</span>
        </div>
      </div>

      <!-- Module Badge -->
      <div class="flex items-center justify-center gap-2 mb-6">
        <span class="px-4 py-2 bg-bfs-navy/5 text-bfs-navy rounded-lg text-sm font-medium border border-bfs-navy/10">
          <component :is="currentModuleIcon" class="w-4 h-4 inline mr-1" />
          {{ currentModuleName }}
        </span>
        <span class="px-3 py-2 bg-amber-50 text-amber-700 rounded-lg text-sm font-medium border border-amber-200">
          <Clock class="w-4 h-4 inline mr-1" />
          Coming Soon
        </span>
      </div>

      <!-- Action Buttons -->
      <div class="flex gap-3 justify-center">
        <button 
          @click="goBack"
          class="px-5 py-2.5 bg-white border border-erp-border text-erp-text rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-2 text-sm font-medium"
        >
          <ArrowLeft class="w-4 h-4" />
          Kembali
        </button>
        <button 
          @click="goHome"
          class="px-5 py-2.5 bg-bfs-navy text-white rounded-lg hover:bg-bfs-navy-light transition-colors flex items-center gap-2 text-sm font-medium shadow-md"
        >
          <Home class="w-4 h-4" />
          Dashboard
        </button>
      </div>

      <!-- Decorative Elements -->
      <div class="mt-10 flex justify-center gap-4 opacity-30">
        <HardHat class="w-8 h-8 text-bfs-navy" />
        <Wrench class="w-8 h-8 text-bfs-gold" />
        <Hammer class="w-8 h-8 text-bfs-navy" />
        <Settings2 class="w-8 h-8 text-bfs-gold" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { 
  Construction, 
  Clock, 
  ArrowLeft, 
  Home,
  HardHat,
  Wrench,
  Hammer,
  Settings2,
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

const route = useRoute()
const router = useRouter()
const progress = ref(0)

const pageTitle = computed(() => {
  return route.meta?.title || 'Under Construction'
})

const currentModuleName = computed(() => {
  return route.meta?.moduleName || 'Unknown Module'
})

const moduleIcons = {
  commercial: ShoppingCart,
  gl: BookOpen,
  ar: Receipt,
  sales: TrendingUp,
  ap: CreditCard,
  purchases: Truck,
  finance: Landmark,
  assets: Package,
  inventory: Package,
  projects: FolderKanban,
  settings: Settings,
}

const currentModuleIcon = computed(() => {
  const moduleId = route.meta?.moduleId
  return moduleIcons[moduleId] || Construction
})

const goBack = () => router.back()
const goHome = () => router.push('/')

onMounted(() => {
  // Animate progress bar
  setTimeout(() => {
    progress.value = Math.floor(Math.random() * 30) + 40 // Random 40-70%
  }, 300)
})
</script>