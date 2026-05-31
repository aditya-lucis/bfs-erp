<template>
  <div class="h-screen w-screen flex overflow-hidden bg-[#F5F5F0]">
    <div 
      class="hidden lg:flex lg:w-1/2 relative flex-col justify-between p-8 lg:p-12 text-white h-screen overflow-hidden"
      style="background: linear-gradient(135deg, rgba(26,39,68,0.92) 0%, rgba(17,27,46,0.95) 100%), url('/login-bg.jpg') center/cover no-repeat;"
    >
      <div class="absolute inset-0 bg-bfs-navy/80"></div>

      <div class="relative z-10 flex flex-col gap-8 lg:gap-10">
        <div>
          <img 
            src="/bfs-logo.png" 
            alt="BFS ERP Logo"
            class="w-auto h-35 lg:h-43 object-contain drop-shadow-lg"
          />
        </div>

        <div class="space-y-4 lg:space-y-6">
          <h1 class="text-3xl lg:text-4xl font-bold leading-tight">
            Sistem Integrasi Mutakhir
          </h1>
          <p class="text-lg lg:text-xl text-bfs-gold font-medium">
            ERP dalam satu ekosistem
          </p>

          <div class="space-y-3 lg:space-y-4 mt-6">
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-full bg-bfs-gold/20 flex items-center justify-center flex-shrink-0">
                <Building2 class="w-4 h-4 text-bfs-gold" />
              </div>
              <span class="text-white/90 text-sm lg:text-base">Commercial, GL, AR, AP, Sales</span>
            </div>
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-full bg-bfs-gold/20 flex items-center justify-center flex-shrink-0">
                <Wallet class="w-4 h-4 text-bfs-gold" />
              </div>
              <span class="text-white/90 text-sm lg:text-base">Finance, Inventory, Assets, Projects</span>
            </div>
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-full bg-bfs-gold/20 flex items-center justify-center flex-shrink-0">
                <Zap class="w-4 h-4 text-bfs-gold" />
              </div>
              <span class="text-white/90 text-sm lg:text-base">Real-time sync antar modul</span>
            </div>
          </div>
        </div>
      </div>

      <div class="relative z-10 text-xs lg:text-sm text-white/60 flex-shrink-0">
        &copy; 2026 BFS ERP. Build Financial System.
      </div>
    </div>

    <div class="w-full lg:w-1/2 flex flex-col p-6 lg:p-8 h-screen overflow-hidden">
      
      <div class="lg:hidden flex-shrink-0 mb-4 flex justify-center">
        <img 
          src="/bfs-logo.png" 
          alt="BFS ERP Logo"
          class="h-16 w-auto object-contain"
        />
      </div>

      <div class="flex-1 flex flex-col justify-center items-center w-full min-h-0">
        <div class="w-full max-w-md">
          
          <div class="text-center mb-6">
            <img 
              src="/bfs-logo.png" 
              alt="BFS ERP Logo"
              class="h-16 lg:h-20 w-auto object-contain mx-auto mb-3 hidden lg:block"
            />
            <h2 class="text-2xl font-bold text-bfs-navy">BFS ERP</h2>
            <p class="text-[10px] lg:text-xs tracking-[0.3em] text-bfs-gold-dark uppercase font-medium">
              Build Financial System
            </p>
            <div class="pt-3">
              <h3 class="text-lg lg:text-xl font-semibold text-bfs-navy">Selamat Datang</h3>
              <p class="text-xs lg:text-sm text-gray-500 mt-1">AUTENTIKASI SISTEM</p>
            </div>
          </div>

          <form @submit.prevent="handleLogin" class="space-y-4">
            
            <div v-if="errorMessage" class="p-3 bg-red-50 border border-red-200 text-red-600 rounded-lg text-sm flex items-center gap-2">
              <AlertCircle class="w-4 h-4 flex-shrink-0" />
              <span>{{ errorMessage }}</span>
            </div>

            <div class="space-y-1.5">
              <label for="username" class="block text-[11px] font-semibold text-gray-600 tracking-wide uppercase">
                Username / NIP
              </label>
              <div class="relative">
                <User class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input 
                  id="username"
                  v-model="form.username"
                  type="text" 
                  :disabled="isLoading"
                  placeholder="Masukkan username atau NIP"
                  class="w-full pl-11 pr-4 py-2.5 bg-white border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-bfs-gold/50 focus:border-bfs-gold transition-all disabled:bg-gray-100 disabled:cursor-not-allowed"
                />
              </div>
            </div>

            <div class="space-y-1.5">
              <label for="password" class="block text-[11px] font-semibold text-gray-600 tracking-wide uppercase">
                Password
              </label>
              <div class="relative">
                <Lock class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input 
                  id="password"
                  v-model="form.password"
                  :type="showPassword ? 'text' : 'password'"
                  :disabled="isLoading"
                  placeholder="Masukkan password"
                  class="w-full pl-11 pr-11 py-2.5 bg-white border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-bfs-gold/50 focus:border-bfs-gold transition-all disabled:bg-gray-100 disabled:cursor-not-allowed"
                />
                <button 
                  type="button"
                  @click="showPassword = !showPassword"
                  :disabled="isLoading"
                  class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 disabled:opacity-50"
                >
                  <Eye v-if="!showPassword" class="w-4 h-4" />
                  <EyeOff v-else class="w-4 h-4" />
                </button>
              </div>
            </div>

            <div class="flex items-center justify-between pt-1">
              <label class="flex items-center gap-2 cursor-pointer">
                <input 
                  v-model="form.remember"
                  type="checkbox" 
                  :disabled="isLoading"
                  class="w-4 h-4 rounded border-gray-300 text-bfs-gold focus:ring-bfs-gold disabled:opacity-50"
                />
                <span class="text-xs lg:text-sm text-gray-600">Ingat saya</span>
              </label>
              <a href="#" class="text-xs lg:text-sm text-bfs-gold-dark hover:text-bfs-gold font-medium transition-colors">
                Lupa password?
              </a>
            </div>

            <button 
              type="submit"
              :disabled="isLoading"
              class="w-full py-2.5 bg-[#C9A96E] hover:bg-[#B8945A] text-white font-semibold rounded-xl transition-all duration-200 shadow-md hover:shadow-lg active:scale-[0.98] disabled:opacity-70 disabled:active:scale-100 flex items-center justify-center gap-2 mt-2"
            >
              <Loader2 v-if="isLoading" class="w-4 h-4 animate-spin" />
              <span>{{ isLoading ? 'MEMPROSES...' : 'MASUK SISTEM' }}</span>
            </button>
          </form>
        </div>
      </div>

      <div class="w-full text-center pt-3 border-t border-gray-200 flex-shrink-0 mt-4">
        <p class="text-xs lg:text-sm text-gray-500">
          Perusahaan: <span class="font-semibold text-bfs-navy">BFS MAIN BRANCH</span>
        </p>
        <p class="text-[10px] lg:text-xs text-gray-400 mt-1">
          v2.0.1-stable &bull; Secure Connection
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
// LoginView.vue — <script setup> section only
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'
import { 
  User, Lock, Eye, EyeOff, Building2, 
  Wallet, Zap, Loader2, AlertCircle 
} from 'lucide-vue-next'

const router      = useRouter()
const authStore   = useAuthStore()

const showPassword = ref(false)
const isLoading    = ref(false)
const errorMessage = ref('')

const form = reactive({
  username: '',
  password: '',
  remember: false
})

const handleLogin = async () => {
  errorMessage.value = ''

  if (!form.username.trim() || !form.password) {
    errorMessage.value = 'Username/NIP dan Password wajib diisi.'
    return
  }

  isLoading.value = true

  // ← Ganti fake logic dengan real API call
  const success = await authStore.login(form.username, form.password)

  if (success) {
    router.push('/')
  } else {
    // Error message sudah di-set oleh authStore.error
    errorMessage.value = authStore.error || 'Login gagal.'
  }

  isLoading.value = false
}
</script>