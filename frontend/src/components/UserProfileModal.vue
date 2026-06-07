<template>
  <Teleport to="body">
    <Transition name="modal">
      <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="$emit('close')" />

        <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-lg z-10 flex flex-col max-h-[92vh]">

          <!-- Header -->
          <div class="bg-bfs-navy px-6 py-4 rounded-t-2xl flex items-center justify-between flex-shrink-0">
            <div class="flex items-center gap-3">
              <!-- Avatar -->
              <div class="w-10 h-10 rounded-xl bg-bfs-gold/20 overflow-hidden flex items-center justify-center">
                <img v-if="photoPreview || me.profile_photo_url"
                  :src="photoPreview || me.profile_photo_url"
                  class="w-full h-full object-cover"
                />
                <UserCircle v-else class="w-6 h-6 text-bfs-gold" />
              </div>
              <div>
                <h3 class="text-sm font-semibold text-white">My Profile</h3>
                <p class="text-[11px] text-white/50">@{{ me.username }}</p>
              </div>
            </div>
            <button @click="$emit('close')" class="text-white/50 hover:text-white transition-colors">
              <X class="w-5 h-5" />
            </button>
          </div>

          <!-- Tabs -->
          <div class="flex border-b border-gray-100 flex-shrink-0">
            <button v-for="tab in tabs" :key="tab.key"
              @click="handleTabClick(tab.key)"
              :class="activeTab === tab.key ? 'border-b-2 border-bfs-gold text-bfs-gold' : 'text-gray-500 hover:text-gray-700'"
              class="flex items-center gap-1.5 px-5 py-3 text-sm font-medium transition-colors"
            >
              <component :is="tab.icon" class="w-4 h-4" />
              {{ tab.label }}
            </button>
          </div>

          <!-- Body -->
          <div class="flex-1 min-h-0 overflow-y-auto px-6 py-5">

            <!-- ── Tab: Profile ── -->
            <div v-show="activeTab === 'profile'" class="space-y-4">

              <!-- Photo upload -->
              <div class="flex items-center gap-4">
                <div class="w-20 h-20 rounded-2xl border-2 border-dashed border-gray-200 overflow-hidden flex items-center justify-center bg-gray-50 flex-shrink-0">
                  <img v-if="photoPreview || me.profile_photo_url"
                    :src="photoPreview || me.profile_photo_url"
                    class="w-full h-full object-cover"
                  />
                  <UserCircle v-else class="w-10 h-10 text-gray-300" />
                </div>
                <div class="space-y-1">
                  <p class="text-sm font-medium text-gray-700">Photo Profile</p>
                  <label class="cursor-pointer inline-flex items-center gap-2 px-3 py-1.5 bg-white border border-gray-200 rounded-lg text-xs text-gray-600 hover:bg-gray-50 transition-colors">
                    <Upload class="w-3.5 h-3.5" /> Upload Photo
                    <input type="file" accept="image/*" class="hidden" @change="handlePhotoChange" />
                  </label>
                  <p class="text-xs text-gray-400">PNG, JPG maks. 2MB</p>
                </div>
              </div>

              <FormField label="Full Name">
                <input v-model="form.full_name" type="text" class="form-input" />
              </FormField>

              <FormField label="Email">
                <input v-model="form.email" type="email" class="form-input" />
              </FormField>

              <p v-if="profileError" class="text-xs text-red-500">{{ profileError }}</p>
              <p v-if="profileSuccess" class="text-xs text-green-600 flex items-center gap-1.5">
                <CheckCircle class="w-3.5 h-3.5" /> {{ profileSuccess }}
              </p>

              <button @click="saveProfile" :disabled="isSavingProfile"
                class="w-full btn-primary flex items-center justify-center gap-2">
                <Loader2 v-if="isSavingProfile" class="w-4 h-4 animate-spin" />
                <Save v-else class="w-4 h-4" />
                {{ isSavingProfile ? 'Menyimpan...' : 'Simpan Profile' }}
              </button>
            </div>

            <!-- ── Tab: Password ── -->
            <div v-show="activeTab === 'password'" class="space-y-4">

              <FormField label="Password Lama" required>
                <div class="relative">
                  <input v-model="pwd.old_password" :type="showOldPwd ? 'text' : 'password'" class="form-input pr-10" />
                  <button type="button" @click="showOldPwd = !showOldPwd"
                    class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400">
                    <component :is="showOldPwd ? EyeOff : Eye" class="w-4 h-4" />
                  </button>
                </div>
              </FormField>

              <FormField label="Password Baru" required>
                <div class="relative">
                  <input v-model="pwd.new_password" :type="showNewPwd ? 'text' : 'password'" class="form-input pr-10" placeholder="Min. 8 karakter" />
                  <button type="button" @click="showNewPwd = !showNewPwd"
                    class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400">
                    <component :is="showNewPwd ? EyeOff : Eye" class="w-4 h-4" />
                  </button>
                </div>
              </FormField>

              <FormField label="Konfirmasi Password Baru" required>
                <input v-model="pwd.new_password2" type="password" class="form-input" placeholder="Ulangi password baru" />
              </FormField>

              <p v-if="pwdError" class="text-xs text-red-500">{{ pwdError }}</p>
              <p v-if="pwdSuccess" class="text-xs text-green-600 flex items-center gap-1.5">
                <CheckCircle class="w-3.5 h-3.5" /> {{ pwdSuccess }}
              </p>

              <button @click="savePassword" :disabled="isSavingPwd"
                class="w-full btn-primary flex items-center justify-center gap-2">
                <Loader2 v-if="isSavingPwd" class="w-4 h-4 animate-spin" />
                <KeyRound v-else class="w-4 h-4" />
                {{ isSavingPwd ? 'Menyimpan...' : 'Ganti Password' }}
              </button>
            </div>

            <!-- ── Tab: Signature ── -->
            <div v-show="activeTab === 'signature'" class="space-y-4">

              <div class="flex gap-2">
                <button @click="sigMode = 'draw'"
                  :class="sigMode === 'draw' ? 'bg-bfs-gold text-white' : 'bg-gray-100 text-gray-600'"
                  class="flex-1 py-2 text-sm font-medium rounded-lg transition-colors flex items-center justify-center gap-1.5">
                  <PenLine class="w-4 h-4" /> Draw
                </button>
                <button @click="sigMode = 'upload'"
                  :class="sigMode === 'upload' ? 'bg-bfs-gold text-white' : 'bg-gray-100 text-gray-600'"
                  class="flex-1 py-2 text-sm font-medium rounded-lg transition-colors flex items-center justify-center gap-1.5">
                  <Upload class="w-4 h-4" /> Upload
                </button>
              </div>

              <!-- Draw -->
              <div v-show="sigMode === 'draw'" class="space-y-3">
                <div class="border-2 border-dashed border-gray-200 rounded-xl overflow-hidden bg-gray-50">
                  <canvas ref="canvasRef" width="520" height="180"
                    class="w-full touch-none cursor-crosshair"
                    @mousedown="startDraw" @mousemove="draw"
                    @mouseup="stopDraw" @mouseleave="stopDraw"
                    @touchstart.prevent="startDrawTouch"
                    @touchmove.prevent="drawTouch"
                    @touchend="stopDraw"
                  />
                </div>
                <div class="flex gap-2">
                  <button @click="clearCanvas"
                    class="text-sm px-3 py-1.5 border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-50 flex items-center gap-1.5">
                    <Eraser class="w-3.5 h-3.5" /> Clear
                  </button>
                  <p class="text-xs text-gray-400 self-center">Gunakan mouse atau touch</p>
                </div>
                <!-- existing signature preview -->
                <div v-if="empSignatureDraw && !hasDrawn"
                  class="p-3 bg-gray-50 rounded-xl border border-gray-100">
                  <p class="text-xs text-gray-400 mb-2">Signature saat ini:</p>
                  <img :src="empSignatureDraw" class="max-h-16 object-contain" />
                </div>
              </div>

              <!-- Upload -->
              <div v-show="sigMode === 'upload'" class="space-y-3">
                <label class="block cursor-pointer">
                  <div :class="sigFile ? 'border-bfs-gold bg-bfs-gold/5' : 'border-gray-200 hover:border-bfs-gold/50'"
                    class="border-2 border-dashed rounded-xl p-8 text-center transition-colors">
                    <Upload class="w-8 h-8 text-gray-300 mx-auto mb-2" />
                    <p class="text-sm text-gray-500">{{ sigFile ? sigFile.name : 'Klik atau drag gambar tanda tangan' }}</p>
                  </div>
                  <input type="file" accept="image/*" class="hidden" @change="handleSigFile" />
                </label>
                <div v-if="sigPreview || empSignatureImgUrl"
                  class="p-3 bg-gray-50 rounded-xl border border-gray-100">
                  <p class="text-xs text-gray-400 mb-2">Preview:</p>
                  <img :src="sigPreview || empSignatureImgUrl" class="max-h-20 object-contain" />
                </div>
              </div>

              <p v-if="sigError" class="text-xs text-red-500">{{ sigError }}</p>
              <p v-if="sigSuccess" class="text-xs text-green-600 flex items-center gap-1.5">
                <CheckCircle class="w-3.5 h-3.5" /> {{ sigSuccess }}
              </p>

              <button @click="saveSignature" :disabled="isSavingSig"
                class="w-full btn-primary flex items-center justify-center gap-2">
                <Loader2 v-if="isSavingSig" class="w-4 h-4 animate-spin" />
                <Save v-else class="w-4 h-4" />
                {{ isSavingSig ? 'Menyimpan...' : 'Simpan Signature' }}
              </button>
            </div>

          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth.js'
import api from '../services/api.js'
import FormField from './FormField.vue'
import {
  X, UserCircle, Save, Loader2, Eye, EyeOff,
  Upload, PenLine, Eraser, KeyRound, CheckCircle, User, Lock, Pen,
} from 'lucide-vue-next'

const emit = defineEmits(['close'])
const authStore = useAuthStore()

const activeTab = ref('profile')
const tabs = [
  { key: 'profile',   label: 'Profile',    icon: User  },
  { key: 'password',  label: 'Password',   icon: Lock  },
  { key: 'signature', label: 'Signature',  icon: Pen   },
]

// ── Me data ────────────────────────────────────────────────────────────────
const me = reactive({
  username: '', email: '', full_name: '',
  profile_photo_url: null, signature_draw: null, signature_image_url: null,
})

const form = reactive({ full_name: '', email: '' })

async function fetchMe() {
  const res = await api.get('/auth/me/')
  Object.assign(me, res.data)
  form.full_name = res.data.full_name || ''
  form.email     = res.data.email     || ''
  console.log('me:', res.data) 
}

// ── Photo ──────────────────────────────────────────────────────────────────
const photoPreview   = ref(null)
const photoFile      = ref(null)
const isSavingProfile = ref(false)
const profileError   = ref('')
const profileSuccess = ref('')

function handlePhotoChange(e) {
  const file = e.target.files[0]
  if (!file) return
  photoFile.value    = file
  photoPreview.value = URL.createObjectURL(file)
}

async function saveProfile() {
  profileError.value   = ''
  profileSuccess.value = ''
  isSavingProfile.value = true
  try {
    const payload = new FormData()
    payload.append('full_name', form.full_name)
    payload.append('email', form.email)
    if (photoFile.value) payload.append('profile_photo', photoFile.value)

    const res = await api.patch('/auth/me/', payload, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    Object.assign(me, res.data)
    photoPreview.value   = null
    photoFile.value      = null
    profileSuccess.value = 'Profile berhasil disimpan!'
    setTimeout(() => profileSuccess.value = '', 3000)
  } catch (err) {
    profileError.value = err.response?.data?.detail || 'Gagal menyimpan profile.'
  } finally {
    isSavingProfile.value = false
  }
}

// ── Password ───────────────────────────────────────────────────────────────
const showOldPwd = ref(false)
const showNewPwd = ref(false)
const isSavingPwd = ref(false)
const pwdError   = ref('')
const pwdSuccess = ref('')
const pwd = reactive({ old_password: '', new_password: '', new_password2: '' })

async function savePassword() {
  pwdError.value   = ''
  pwdSuccess.value = ''
  if (pwd.new_password !== pwd.new_password2) {
    pwdError.value = 'Konfirmasi password tidak cocok.'
    return
  }
  if (pwd.new_password.length < 8) {
    pwdError.value = 'Password minimal 8 karakter.'
    return
  }
  isSavingPwd.value = true
  try {
    await api.post('/auth/change-password/', {
      old_password: pwd.old_password,
      new_password: pwd.new_password,
    })
    pwdSuccess.value   = 'Password berhasil diubah!'
    pwd.old_password   = ''
    pwd.new_password   = ''
    pwd.new_password2  = ''
    setTimeout(() => pwdSuccess.value = '', 3000)
  } catch (err) {
    pwdError.value = err.response?.data?.detail
                  || err.response?.data?.old_password?.[0]
                  || 'Gagal mengubah password.'
  } finally {
    isSavingPwd.value = false
  }
}

// ── Signature — via employee endpoint ─────────────────────────────────────
const canvasRef   = ref(null)
const isDrawing   = ref(false)
const hasDrawn    = ref(false)
const sigMode     = ref('draw')
const sigFile     = ref(null)
const sigPreview  = ref(null)
const isSavingSig = ref(false)
const sigError    = ref('')
const sigSuccess  = ref('')

// Data signature dari employee profile
const empSignatureDraw  = ref(null)
const empSignatureImgUrl = ref(null)

async function fetchEmployeeSignature() {
  if (!me.employee_pk) return
  try {
    const res = await api.get(`/org/employees/${me.employee_pk}/`)
    empSignatureDraw.value   = res.data.signature_draw   || null
    empSignatureImgUrl.value = res.data.signature_image_url || null
  } catch {}
}

function handleTabClick(key) {
  activeTab.value = key
  if (key === 'signature') {
    fetchEmployeeSignature().then(() => {
      if (!empSignatureDraw.value) return
      setTimeout(() => {
        if (!canvasRef.value) return
        const img = new Image()
        img.onload = () => {
          if (!canvasRef.value) return
          const canvas = canvasRef.value
          const ctx = canvas.getContext('2d')
          ctx.clearRect(0, 0, canvas.width, canvas.height)
          ctx.drawImage(img, 0, 0, canvas.width, canvas.height)
          hasDrawn.value = false
        }
        img.src = empSignatureDraw.value
      }, 100)
    })
  }
}

function startDraw(e) {
  if (!canvasRef.value) return
  isDrawing.value = true
  const ctx = canvasRef.value.getContext('2d')
  const pos = getCanvasPos(e)
  ctx.beginPath()
  ctx.moveTo(pos.x, pos.y)
}

function clearCanvas() {
  if (!canvasRef.value) return
  const ctx = canvasRef.value.getContext('2d')
  ctx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height)
  hasDrawn.value = false
}

async function saveSignature() {
  sigError.value   = ''
  sigSuccess.value = ''
  if (!me.employee_pk) {
    sigError.value = 'Akun ini tidak terelasi dengan data employee.'
    return
  }
  isSavingSig.value = true
  try {
    if (sigMode.value === 'draw' && hasDrawn.value) {
      const dataUrl = canvasRef.value.toDataURL('image/png')
      await api.post(`/org/employees/${me.employee_pk}/signature/`, { signature_draw: dataUrl })
      empSignatureDraw.value = dataUrl
    } else if (sigMode.value === 'upload' && sigFile.value) {
      const fd = new FormData()
      fd.append('signature_image', sigFile.value)
      const res = await api.post(`/org/employees/${me.employee_pk}/signature/`, fd, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      empSignatureImgUrl.value = res.data.signature_image_url || sigPreview.value
      sigPreview.value = null
      sigFile.value    = null
    } else {
      sigError.value = 'Belum ada signature untuk disimpan.'
      return
    }
    sigSuccess.value = 'Signature berhasil disimpan!'
    setTimeout(() => sigSuccess.value = '', 3000)
  } catch (err) {
    sigError.value = err.response?.data?.detail || 'Gagal menyimpan signature.'
  } finally {
    isSavingSig.value = false
  }
}

onMounted(fetchMe)
</script>

<style scoped>
@reference "../style.css";
.form-input {
  @apply w-full px-3.5 py-2.5 text-sm border border-gray-200 rounded-xl
         focus:outline-none focus:ring-2 focus:ring-bfs-gold/30 focus:border-bfs-gold
         transition-all bg-white;
}
.btn-primary { @apply px-4 py-2 bg-bfs-gold hover:bg-bfs-gold-dark text-white font-medium rounded-lg transition-colors disabled:opacity-60; }
.modal-enter-active, .modal-leave-active { transition: opacity 0.2s; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
</style>