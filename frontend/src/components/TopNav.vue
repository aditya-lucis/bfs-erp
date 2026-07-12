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

        <!-- Notification Bell -->
        <div class="relative">
          <button 
            @click="isNotificationModalOpen = !isNotificationModalOpen"
            class="p-2 rounded-lg transition-colors flex items-center gap-1.5 relative"
            :class="isNotificationModalOpen ? 'bg-white/20' : 'hover:bg-white/10'"
            title="Notification Inbox"
          >
            <Bell class="w-5 h-5 text-white" />
            <span 
              v-if="pendingCount > 0" 
              class="absolute -top-1 -right-1 bg-red-500 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full min-w-4 h-4 flex items-center justify-center animate-bounce"
            >
              {{ pendingCount }}
            </span>
          </button>
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

    <!-- Active Request Available Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="isNotificationModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-black/55 backdrop-blur-sm" @click="isNotificationModalOpen = false" />
          <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-lg z-10 border border-gray-100 flex flex-col max-h-[85vh]">
            
            <!-- Modal Header -->
            <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between bg-bfs-navy text-white rounded-t-2xl">
              <h3 class="text-base font-bold flex items-center gap-2 uppercase tracking-wide">
                <Bell class="w-5 h-5 text-bfs-gold" />
                Active Request Available
              </h3>
              <button @click="isNotificationModalOpen = false" class="text-white/80 hover:text-white transition-colors">
                <X class="w-5 h-5" />
              </button>
            </div>

            <!-- Modal Body -->
            <div class="p-6 overflow-y-auto flex-1 space-y-4">
              <div v-if="pendingCount === 0" class="text-center py-10 text-gray-400 text-sm">
                <CheckCircle class="w-12 h-12 text-green-400 mx-auto mb-3" />
                <span>Tidak ada request pending di inbox Anda.</span>
              </div>
              <div v-else class="space-y-4">
                <div 
                  v-for="group in groupedRequests" 
                  :key="group.name" 
                  class="border border-gray-100 rounded-xl p-3 bg-gray-50/50"
                >
                  <div class="flex items-center justify-between">
                    <span class="text-sm font-bold text-gray-700">
                      {{ group.items.length }} {{ group.name }}
                    </span>
                    <button 
                      @click="toggleGroupDetails(group.name)"
                      class="text-xs text-bfs-gold-dark hover:text-bfs-gold font-semibold transition-colors cursor-pointer"
                    >
                      {{ expandedGroups[group.name] ? '-- hide details --' : '-- show details --' }}
                    </button>
                  </div>

                  <!-- Details Table (expanded) -->
                  <div v-if="expandedGroups[group.name]" class="mt-3 overflow-x-auto border-t border-gray-100 pt-3">
                    <table class="w-full text-left border-collapse text-xs">
                      <thead>
                        <tr class="bg-gray-100/80 text-gray-600 font-semibold uppercase tracking-wider">
                          <th class="py-1.5 px-3 border border-gray-200 w-16 text-center">No</th>
                          <th class="py-1.5 px-3 border border-gray-200">Document No</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr 
                          v-for="(item, idx) in group.items" 
                          :key="item.id"
                          class="hover:bg-bfs-gold/5 transition-colors"
                        >
                          <td class="py-1.5 px-3 border border-gray-200 text-center font-mono text-gray-500">
                            {{ idx + 1 }}
                          </td>
                          <td class="py-1.5 px-3 border border-gray-200">
                            <a 
                              href="#"
                              @click.prevent="handleNotificationClick(item)"
                              class="text-bfs-gold-dark hover:text-bfs-gold hover:underline font-semibold font-mono"
                            >
                              {{ item.document_number }}
                            </a>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>

            <!-- Modal Footer -->
            <div class="px-6 py-4 border-t border-gray-100 bg-gray-50 rounded-b-2xl flex justify-end">
              <button 
                @click="isNotificationModalOpen = false" 
                class="px-5 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold rounded-xl text-sm transition-colors cursor-pointer"
              >
                Close
              </button>
            </div>

          </div>
        </div>
      </Transition>
    </Teleport>

  </header>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Home, User, LogOut, Settings, ChevronDown, LayoutDashboard, Bell, X, CheckCircle } from 'lucide-vue-next'
import { useAuthStore } from '../stores/auth.js'
import { useApprovalRequestStore } from '../stores/approvalRequest.js'
import UserProfileModal from './UserProfileModal.vue'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const approvalStore = useApprovalRequestStore()
const router    = useRouter()
const showProfileModal = ref(false)
const isNotificationModalOpen = ref(false)
const expandedGroups = ref({})

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

// Notifications logic
const pendingCount = computed(() => {
  return approvalStore.requests.length
})

const groupedRequests = computed(() => {
  const groups = {}
  approvalStore.requests.forEach(req => {
    const docName = req.document_name || req.document_code
    if (!groups[docName]) {
      groups[docName] = {
        name: docName,
        code: req.document_code,
        items: []
      }
    }
    groups[docName].items.push(req)
  })
  return Object.values(groups)
})

const toggleGroupDetails = (groupName) => {
  expandedGroups.value[groupName] = !expandedGroups.value[groupName]
}

const handleNotificationClick = (item) => {
  isNotificationModalOpen.value = false
  approvalStore.currentRequest = item
  if (item.document_code === 'GEJ') {
    router.push('/gl/general-journal-inbox')
  } else if (item.document_code === 'PR') {
    router.push('/purchases/purchase-requisition-inbox')
  } else if (item.document_code === 'PO') {
    router.push('/purchases/purchase-order-inbox')
  } else if (item.document_code === 'CC') {
    router.push('/purchases/completion-certificate-inbox')
  } else if (item.document_code === 'GRN') {
    router.push('/purchases/good-receipt-note-inbox')
  } else if (item.document_code === 'RECEIPT_REPORT') {
    router.push('/inventory/receipt-report-inbox')
  } else if (item.document_code === 'CBR_PI') {
    router.push('/finance/payment-request-inbox')
  } else {
    router.push('/projects/rap-inbox')
  }
}

let fetchInterval = null
onMounted(() => {
  if (authStore.isLoggedIn) {
    approvalStore.fetchRequests({ inbox: 'true' }).catch(() => {})
  }
  fetchInterval = setInterval(() => {
    if (authStore.isLoggedIn) {
      approvalStore.fetchRequests({ inbox: 'true' }).catch(() => {})
    }
  }, 30000)
})

onUnmounted(() => {
  if (fetchInterval) clearInterval(fetchInterval)
})
</script>