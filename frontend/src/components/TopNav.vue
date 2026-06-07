<template>
  <header class="sticky top-0 z-50 bg-bfs-navy text-white shadow-lg w-full shrink-0">
    <div class="flex items-center justify-between px-4 h-14 border-b border-white/10 w-full gap-4">

      <div class="flex items-center shrink-0 pl-4 mr-8 lg:mr-16">
        <img 
          src="/bfs-logo.png" 
          alt="BFS ERP Logo" 
          class="h-14 w-auto object-contain drop-shadow-md cursor-pointer scale-[1.8] origin-left" 
        />
      </div>

      <nav class="hidden lg:flex items-center gap-1 flex-1 min-w-0 overflow-x-auto px-2 [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]">
        <button
          v-for="module in modules"
          :key="module.id"
          @click="selectModule(module.id)"
          :class="[
            'px-3 py-2 rounded-t-lg text-sm font-medium transition-all duration-200 flex items-center gap-1.5 shrink-0',
            activeModule === module.id
              ? 'bg-white text-bfs-navy shadow-sm'
              : 'text-white/80 hover:text-white hover:bg-white/10'
          ]"
        >
          <component :is="module.icon" class="w-4 h-4" />
          <span>{{ module.name }}</span>
        </button>
      </nav>

      <div class="flex items-center gap-3 shrink-0 ml-auto">
        <span class="text-sm text-bfs-silver hidden md:block whitespace-nowrap">
          Welcome, <span class="text-white font-medium">{{ authStore.fullName }}</span>
        </span>
        <div class="h-8 w-px bg-white/20"></div>

        <!-- Home Dropdown -->
        <div class="relative">
          <button 
            @click="isHomeMenuOpen = !isHomeMenuOpen"
            class="p-2 rounded-lg transition-colors flex items-center gap-1"
            :class="isHomeMenuOpen ? 'bg-white/20' : 'hover:bg-white/10'"
            title="Home Menu"
          >
            <Home class="w-5 h-5" />
            <ChevronDown class="w-3 h-3" />
          </button>

          <div v-if="isHomeMenuOpen" @click="isHomeMenuOpen = false" class="fixed inset-0 z-40"></div>

          <div v-if="isHomeMenuOpen" class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-xl border border-gray-100 py-1 z-50 overflow-hidden">
            <router-link 
              to="/" 
              @click="isHomeMenuOpen = false"
              class="w-full text-left px-4 py-2.5 text-sm text-erp-text hover:bg-gray-50 flex items-center gap-2 transition-colors"
            >
              <Home class="w-4 h-4 text-gray-500" /> Home
            </router-link>
            <div class="h-px bg-gray-200 my-1"></div>
            <router-link 
              to="/dashboard" 
              @click="isHomeMenuOpen = false"
              class="w-full text-left px-4 py-2.5 text-sm text-erp-text hover:bg-gray-50 flex items-center gap-2 transition-colors"
            >
              <LayoutDashboard class="w-4 h-4 text-gray-500" /> Dashboard
            </router-link>
          </div>
        </div>

        <!-- User Dropdown -->
        <div class="relative">
          <button 
            @click="isUserMenuOpen = !isUserMenuOpen"
            class="p-2 rounded-lg transition-colors flex items-center gap-2"
            :class="isUserMenuOpen ? 'bg-white/20' : 'hover:bg-white/10'"
          >
            <User class="w-5 h-5" />
          </button>

          <div v-if="isUserMenuOpen" @click="isUserMenuOpen = false" class="fixed inset-0 z-40"></div>

          <div v-if="isUserMenuOpen" class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-xl border border-gray-100 py-1 z-50 overflow-hidden">
            <button @click="goToSetting" class="w-full text-left px-4 py-2.5 text-sm text-erp-text hover:bg-gray-50 flex items-center gap-2 transition-colors">
              <Settings class="w-4 h-4 text-gray-500" /> Setting
            </button>
            <div class="h-px bg-gray-200 my-1"></div>
            <button @click="handleLogout" class="w-full text-left px-4 py-2.5 text-sm text-erp-red hover:bg-red-50 flex items-center gap-2 transition-colors">
              <LogOut class="w-4 h-4 text-erp-red" /> Logout
            </button>
          </div>
        </div>
      </div>
    </div>

    <UserProfileModal
      v-if="showProfileModal"
      @close="showProfileModal = false"
    />
    
  </header>
</template>

<script setup>
import { ref } from 'vue'
import { Home, User, LogOut, Settings, ChevronDown, LayoutDashboard } from 'lucide-vue-next'
import { useAuthStore } from '../stores/auth.js'
import UserProfileModal from './UserProfileModal.vue'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router    = useRouter()
const showProfileModal = ref(false)
const props = defineProps({
  activeModule: {
    type: String,
    required: true
  },
  modules: {
    type: Array,
    required: true,
    default: () => []
  }
})

const emit = defineEmits(['update:activeModule', 'toggle-sidebar'])

const selectModule = (id) => {
  emit('update:activeModule', id)
  emit('toggle-sidebar', id)
}

const isHomeMenuOpen = ref(false)
const isUserMenuOpen = ref(false)

const goToSetting = () => {
  isUserMenuOpen.value = false
  showProfileModal.value = true
}

const handleLogout = async () => {
  isUserMenuOpen.value = false
  await authStore.logout()
  router.push('/login')
}
</script>