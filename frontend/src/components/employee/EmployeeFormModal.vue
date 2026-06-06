<!-- src/components/employee/EmployeeFormModal.vue -->
<template>
  <Teleport to="body">
    <Transition name="modal">
      <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="$emit('close')" />

        <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-2xl z-10 flex flex-col max-h-[92vh]">

          <!-- Header -->
          <div class="bg-bfs-navy px-6 py-4 rounded-t-2xl flex items-center justify-between flex-shrink-0">
            <div class="flex items-center gap-3">
              <div class="w-9 h-9 rounded-xl bg-bfs-gold/20 flex items-center justify-center">
                <UserCircle class="w-5 h-5 text-bfs-gold" />
              </div>
              <div>
                <h3 class="text-sm font-semibold text-white">
                  {{ isEdit ? 'Edit Employee' : 'Add Employee' }}
                </h3>
                <p v-if="isEdit" class="text-[11px] text-white/50">
                  {{ employee.employee_id }} — {{ employee.full_name }}
                </p>
                <p v-else class="text-[11px] text-white/50">
                  ID akan di-generate otomatis: {{ companyCode }}001, dst.
                </p>
              </div>
            </div>
            <button @click="$emit('close')" class="text-white/50 hover:text-white transition-colors">
              <X class="w-5 h-5" />
            </button>
          </div>

          <!-- Tabs -->
          <div class="flex border-b border-gray-100 flex-shrink-0 bg-white">
            <button
              v-for="tab in tabs" :key="tab.key"
              @click="handleTabClick(tab.key)"
              :class="activeTab === tab.key
                ? 'border-b-2 border-bfs-gold text-bfs-gold'
                : 'text-gray-500 hover:text-gray-700'"
              class="flex items-center gap-1.5 px-5 py-3 text-sm font-medium transition-colors"
            >
              <component :is="tab.icon" class="w-4 h-4" />
              {{ tab.label }}
            </button>
          </div>

          <!-- Scroll body -->
          <div class="flex-1 min-h-0 overflow-y-auto px-6 py-5">

            <!-- ── Tab: Info Employee ── -->
            <div v-show="activeTab === 'info'" class="space-y-4">

              <div class="grid grid-cols-2 gap-4">
                <FormField label="Full Name" required class="col-span-2">
                  <input v-model="form.full_name" type="text" class="form-input" placeholder="Nama lengkap" />
                </FormField>

                <FormField label="Email" required>
                  <input v-model="form.email" type="email" class="form-input" placeholder="email@company.com" />
                </FormField>

                <FormField label="Phone">
                  <input v-model="form.phone" type="text" class="form-input" placeholder="+62..." />
                </FormField>

                <FormField label="Position" required>
                  <select v-model="form.position" class="form-input">
                    <option value="">— Pilih Position —</option>
                    <optgroup
                      v-for="dept in groupedPositions"
                      :key="dept.dept_name"
                      :label="dept.dept_name"
                    >
                      <option v-for="pos in dept.positions" :key="pos.id" :value="pos.id">
                        {{ pos.name }}
                      </option>
                    </optgroup>
                  </select>
                </FormField>

                <FormField label="Join Date">
                  <input v-model="form.join_date" type="date" class="form-input" />
                </FormField>

                <FormField label="Status">
                  <select v-model="form.status" class="form-input">
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                    <option value="resigned">Resigned</option>
                    <option value="terminated">Terminated</option>
                  </select>
                </FormField>
              </div>

            </div>

            <!-- ── Tab: User & Groups ── -->
            <div v-show="activeTab === 'user'" class="space-y-4">

              <!-- ═══════════════════════════════════════════════
                   CASE A: ADD NEW EMPLOYEE → username + password
                   ═══════════════════════════════════════════════ -->
              <template v-if="!isEdit">
                <FormField label="Username" required>
                  <input
                    v-model="form.username"
                    type="text"
                    class="form-input font-mono"
                    placeholder="e.g. bfs001"
                    :class="errors.username ? 'border-red-300' : ''"
                  />
                  <p v-if="errors.username" class="mt-1 text-xs text-red-500">{{ errors.username }}</p>
                </FormField>

                <FormField label="Password" required>
                  <div class="relative">
                    <input
                      v-model="form.password"
                      :type="showPwd ? 'text' : 'password'"
                      class="form-input pr-10"
                      placeholder="Min. 8 karakter"
                    />
                    <button type="button" @click="showPwd = !showPwd"
                      class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                      <component :is="showPwd ? EyeOff : Eye" class="w-4 h-4" />
                    </button>
                  </div>
                </FormField>
              </template>

              <!-- ═══════════════════════════════════════════════
                   CASE B: EDIT — employee BELUM punya user (seed)
                   Superuser bisa buatkan user baru
                   ═══════════════════════════════════════════════ -->
              <template v-else-if="isEdit && !employee.username">
                <div v-if="!authStore.isSuperuser"
                  class="flex items-center gap-3 p-4 bg-amber-50 border border-amber-100 rounded-xl">
                  <Info class="w-4 h-4 text-amber-500 flex-shrink-0" />
                  <p class="text-xs text-amber-700">
                    Employee ini belum memiliki user account. Hubungi superuser untuk membuatkan akun.
                  </p>
                </div>

                <template v-else>
                  <div class="flex items-center gap-3 p-3 bg-blue-50 border border-blue-100 rounded-xl">
                    <Info class="w-4 h-4 text-blue-500 flex-shrink-0" />
                    <p class="text-xs text-blue-700">
                      Employee ini belum punya user account. Isi username & password untuk membuatkan akun login.
                    </p>
                  </div>

                  <FormField label="Username" required>
                    <input
                      v-model="newUser.username"
                      type="text"
                      class="form-input font-mono"
                      placeholder="e.g. bfs007"
                      :class="newUserErrors.username ? 'border-red-300' : ''"
                    />
                    <p v-if="newUserErrors.username" class="mt-1 text-xs text-red-500">{{ newUserErrors.username }}</p>
                  </FormField>

                  <FormField label="Password" required>
                    <div class="relative">
                      <input
                        v-model="newUser.password"
                        :type="showPwd ? 'text' : 'password'"
                        class="form-input pr-10"
                        placeholder="Min. 8 karakter"
                      />
                      <button type="button" @click="showPwd = !showPwd"
                        class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                        <component :is="showPwd ? EyeOff : Eye" class="w-4 h-4" />
                      </button>
                    </div>
                  </FormField>

                  <button
                    type="button"
                    @click="handleCreateUser"
                    :disabled="isCreatingUser"
                    class="w-full btn-primary flex items-center justify-center gap-2"
                  >
                    <Loader2 v-if="isCreatingUser" class="w-4 h-4 animate-spin" />
                    <UserPlus v-else class="w-4 h-4" />
                    {{ isCreatingUser ? 'Membuat akun...' : 'Buat User Account' }}
                  </button>

                  <p v-if="createUserSuccess" class="text-xs text-green-600 flex items-center gap-1.5">
                    <CheckCircle class="w-3.5 h-3.5" /> {{ createUserSuccess }}
                  </p>
                </template>
              </template>

              <!-- ═══════════════════════════════════════════════
                   CASE C: EDIT — employee SUDAH punya user
                   Tampilkan info + form reset password (superuser only)
                   ═══════════════════════════════════════════════ -->
              <template v-else-if="isEdit && employee.username">

                <!-- Info username -->
                <div class="flex items-center gap-3 p-3 bg-blue-50 border border-blue-100 rounded-xl">
                  <Info class="w-4 h-4 text-blue-500 flex-shrink-0" />
                  <p class="text-xs text-blue-700">
                    Username: <span class="font-mono font-bold">{{ employee.username }}</span>
                    — tidak bisa diubah.
                  </p>
                </div>

                <!-- Reset password — hanya superuser -->
                <div v-if="authStore.isSuperuser" class="border border-gray-200 rounded-xl overflow-hidden">
                  <button
                    type="button"
                    @click="showResetPwd = !showResetPwd"
                    class="w-full flex items-center justify-between px-4 py-3 bg-gray-50 hover:bg-gray-100 transition-colors text-sm font-medium text-gray-700"
                  >
                    <span class="flex items-center gap-2">
                      <KeyRound class="w-4 h-4 text-bfs-gold" />
                      Reset Password
                    </span>
                    <ChevronDown class="w-4 h-4 transition-transform" :class="showResetPwd ? 'rotate-180' : ''" />
                  </button>

                  <div v-if="showResetPwd" class="px-4 py-4 space-y-3 border-t border-gray-100">
                    <FormField label="Password Baru" required>
                      <div class="relative">
                        <input
                          v-model="resetPwd.new_password"
                          :type="showPwd ? 'text' : 'password'"
                          class="form-input pr-10"
                          placeholder="Min. 8 karakter"
                        />
                        <button type="button" @click="showPwd = !showPwd"
                          class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                          <component :is="showPwd ? EyeOff : Eye" class="w-4 h-4" />
                        </button>
                      </div>
                    </FormField>

                    <FormField label="Konfirmasi Password" required>
                      <input
                        v-model="resetPwd.new_password2"
                        type="password"
                        class="form-input"
                        placeholder="Ulangi password baru"
                      />
                    </FormField>

                    <button
                      type="button"
                      @click="handleResetPassword"
                      :disabled="isResettingPwd"
                      class="w-full btn-primary flex items-center justify-center gap-2 text-sm"
                    >
                      <Loader2 v-if="isResettingPwd" class="w-3.5 h-3.5 animate-spin" />
                      <KeyRound v-else class="w-3.5 h-3.5" />
                      {{ isResettingPwd ? 'Mereset...' : 'Reset Password' }}
                    </button>

                    <p v-if="resetPwdSuccess" class="text-xs text-green-600 flex items-center gap-1.5">
                      <CheckCircle class="w-3.5 h-3.5" /> {{ resetPwdSuccess }}
                    </p>
                    <p v-if="resetPwdError" class="text-xs text-red-500">{{ resetPwdError }}</p>
                  </div>
                </div>

                <div v-else class="p-3 bg-gray-50 border border-gray-100 rounded-xl">
                  <p class="text-xs text-gray-500">Reset password hanya bisa dilakukan oleh superuser.</p>
                </div>
              </template>

              <!-- Authorization Groups — tampil di semua case kecuali employee tanpa user & bukan superuser -->
              <FormField
                v-if="!isEdit || employee.username || authStore.isSuperuser"
                label="Authorization Groups"
              >
                <div class="border border-gray-200 rounded-xl overflow-hidden">
                  <div class="bg-gray-50 px-3 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wide">
                    Pilih Group User
                  </div>
                  <div class="max-h-52 overflow-y-auto divide-y divide-gray-100">
                    <label
                      v-for="group in availableGroups"
                      :key="group.id"
                      class="flex items-center gap-3 px-3 py-2.5 hover:bg-gray-50 cursor-pointer transition-colors"
                    >
                      <input
                        type="checkbox"
                        :value="group.id"
                        v-model="form.authorization_group_ids"
                        class="w-4 h-4 rounded border-gray-300 text-bfs-gold focus:ring-bfs-gold"
                      />
                      <div>
                        <p class="text-sm font-medium text-gray-800">{{ group.group_name }}</p>
                        <p class="text-xs text-gray-400">{{ group.description }}</p>
                      </div>
                    </label>
                  </div>
                </div>
                <p class="mt-1 text-xs text-gray-400">
                  {{ form.authorization_group_ids.length }} group dipilih
                </p>
              </FormField>

            </div>

            <!-- ── Tab: Signature ── -->
            <div v-show="activeTab === 'signature'" class="space-y-5">

              <!-- Toggle mode -->
              <div class="flex gap-2">
                <button
                  @click="sigMode = 'draw'"
                  :class="sigMode === 'draw' ? 'bg-bfs-gold text-white' : 'bg-gray-100 text-gray-600'"
                  class="flex-1 py-2 text-sm font-medium rounded-lg transition-colors flex items-center justify-center gap-1.5"
                >
                  <PenLine class="w-4 h-4" /> Draw
                </button>
                <button
                  @click="sigMode = 'upload'"
                  :class="sigMode === 'upload' ? 'bg-bfs-gold text-white' : 'bg-gray-100 text-gray-600'"
                  class="flex-1 py-2 text-sm font-medium rounded-lg transition-colors flex items-center justify-center gap-1.5"
                >
                  <Upload class="w-4 h-4" /> Upload
                </button>
              </div>

              <!-- Draw mode -->
              <div v-show="sigMode === 'draw'" class="space-y-3">
                <div class="border-2 border-dashed border-gray-200 rounded-xl overflow-hidden bg-gray-50">
                  <canvas
                    ref="canvasRef"
                    width="520"
                    height="200"
                    class="w-full touch-none cursor-crosshair"
                    @mousedown="startDraw"
                    @mousemove="draw"
                    @mouseup="stopDraw"
                    @mouseleave="stopDraw"
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
                  <p class="text-xs text-gray-400 self-center">
                    Tanda tangan menggunakan mouse atau touch
                  </p>
                </div>

                <!-- Preview kalau sudah ada -->
                <div v-if="currentSignature && !hasDrawn" class="p-3 bg-gray-50 rounded-xl border border-gray-100">
                  <p class="text-xs text-gray-400 mb-2">Signature saat ini:</p>
                  <img :src="currentSignature" class="max-h-20 object-contain" />
                </div>
              </div>

              <!-- Upload mode -->
              <div v-show="sigMode === 'upload'" class="space-y-3">
                <label class="block cursor-pointer">
                  <div :class="signatureFile
                    ? 'border-bfs-gold bg-bfs-gold/5'
                    : 'border-gray-200 hover:border-bfs-gold/50'"
                    class="border-2 border-dashed rounded-xl p-8 text-center transition-colors"
                  >
                    <Upload class="w-8 h-8 text-gray-300 mx-auto mb-2" />
                    <p class="text-sm text-gray-500">
                      {{ signatureFile ? signatureFile.name : 'Klik atau drag gambar tanda tangan' }}
                    </p>
                    <p class="text-xs text-gray-400 mt-1">PNG, JPG. Latar belakang putih/transparan.</p>
                  </div>
                  <input
                    type="file"
                    accept="image/*"
                    class="hidden"
                    @change="handleSignatureFile"
                  />
                </label>

                <!-- Preview upload -->
                <div v-if="signaturePreview || currentSignature"
                  class="p-3 bg-gray-50 rounded-xl border border-gray-100">
                  <p class="text-xs text-gray-400 mb-2">Preview:</p>
                  <img
                    :src="signaturePreview || currentSignature"
                    class="max-h-24 object-contain"
                  />
                </div>
              </div>

            </div>

          </div>

          <!-- Footer -->
          <div class="px-6 py-4 border-t border-gray-100 flex items-center justify-between flex-shrink-0">
            <div v-if="serverError" class="flex items-center gap-2 text-xs text-red-600">
              <AlertCircle class="w-4 h-4" />
              {{ serverError }}
            </div>
            <div v-else class="text-xs text-gray-400">*) Required</div>

            <div class="flex gap-2">
              <button @click="$emit('close')" class="btn-secondary text-sm">Cancel</button>
              <button
                @click="handleSave"
                :disabled="isSaving"
                class="btn-primary text-sm flex items-center gap-1.5"
              >
                <Loader2 v-if="isSaving" class="w-3.5 h-3.5 animate-spin" />
                <Save v-else class="w-3.5 h-3.5" />
                {{ isEdit ? 'Update' : 'Save Employee' }}
              </button>
            </div>
          </div>

        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick, watch } from 'vue'
import { useOrganizationStore } from '../../stores/organization.js'
import { useRbacStore } from '../../stores/rbac.js'
import { useAuthStore } from '../../stores/auth.js'
import FormField from '../FormField.vue'
import {
  X, UserCircle, Save, Loader2, Eye, EyeOff,
  PenLine, Upload, Eraser, Info, AlertCircle,
  User, Shield, Pen, KeyRound, ChevronDown, UserPlus, CheckCircle,
} from 'lucide-vue-next'

const props  = defineProps({ employee: { type: Object, default: null } })
const emit   = defineEmits(['close', 'saved'])

const orgStore  = useOrganizationStore()
const rbacStore = useRbacStore()
const authStore = useAuthStore()

const isEdit      = computed(() => !!props.employee)
const companyCode = computed(() => orgStore.companyCode || 'BFS')
const isSaving    = ref(false)
const serverError = ref('')
const showPwd     = ref(false)
const activeTab   = ref('info')
const sigMode     = ref('draw')

const tabs = [
  { key: 'info',      label: 'Employee Info', icon: User   },
  { key: 'user',      label: 'User & Groups',  icon: Shield },
  { key: 'signature', label: 'Signature',      icon: Pen    },
]

// ── Form state ─────────────────────────────────────────────────────────────
const form = reactive({
  full_name:               props.employee?.full_name  || '',
  email:                   props.employee?.email       || '',
  phone:                   props.employee?.phone       || '',
  position:                props.employee?.position    || '',
  join_date:               props.employee?.join_date   || '',
  status:                  props.employee?.status      || 'active',
  username:                '',
  password:                '',
  authorization_group_ids: props.employee?.groups?.map(g => g.authorization_group__id) || [],
})

const errors = reactive({ username: '', password: '' })

// ── State: buat user baru untuk employee seed ──────────────────────────────
const newUser = reactive({ username: '', password: '' })
const newUserErrors  = reactive({ username: '' })
const isCreatingUser = ref(false)
const createUserSuccess = ref('')

// ── State: reset password ─────────────────────────────────────────────────
const showResetPwd  = ref(false)
const isResettingPwd = ref(false)
const resetPwdSuccess = ref('')
const resetPwdError   = ref('')
const resetPwd = reactive({ new_password: '', new_password2: '' })

// ── Handler: buat user untuk employee seed ─────────────────────────────────
async function handleCreateUser() {
  newUserErrors.username = ''
  createUserSuccess.value = ''

  if (!newUser.username.trim()) {
    newUserErrors.username = 'Username wajib diisi.'
    return
  }
  if (!newUser.password || newUser.password.length < 8) {
    serverError.value = 'Password minimal 8 karakter.'
    return
  }

  isCreatingUser.value = true
  try {
    const res = await orgStore.createUserForEmployee(props.employee.id, {
      username:  newUser.username.trim(),
      password:  newUser.password,
      password2: newUser.password,
    })
    createUserSuccess.value = res.detail || 'User account berhasil dibuat!'
    // Refresh list setelah berhasil
    emit('saved')
  } catch (err) {
    const data = err.response?.data
    if (data?.username) {
      newUserErrors.username = data.username[0]
    } else {
      serverError.value = data?.detail || 'Gagal membuat user account.'
    }
  } finally {
    isCreatingUser.value = false
  }
}

// ── Handler: reset password ────────────────────────────────────────────────
async function handleResetPassword() {
  resetPwdSuccess.value = ''
  resetPwdError.value   = ''

  if (!resetPwd.new_password || resetPwd.new_password.length < 8) {
    resetPwdError.value = 'Password baru minimal 8 karakter.'
    return
  }
  if (resetPwd.new_password !== resetPwd.new_password2) {
    resetPwdError.value = 'Konfirmasi password tidak cocok.'
    return
  }

  // Dapatkan user_id dari employee — backend serializer expose field 'user' sebagai FK integer
  const userId = props.employee?.user
  if (!userId) {
    resetPwdError.value = 'User ID tidak ditemukan.'
    return
  }

  isResettingPwd.value = true
  try {
    const res = await orgStore.adminResetPassword(userId, {
      new_password:  resetPwd.new_password,
      new_password2: resetPwd.new_password2,
    })
    resetPwdSuccess.value = res.detail || 'Password berhasil direset!'
    resetPwd.new_password  = ''
    resetPwd.new_password2 = ''
    showResetPwd.value = false
  } catch (err) {
    resetPwdError.value = err.response?.data?.detail || 'Gagal mereset password.'
  } finally {
    isResettingPwd.value = false
  }
}

// ── Positions grouped by department ────────────────────────────────────────
const groupedPositions = computed(() => {
  const map = {}
  orgStore.positions.forEach(pos => {
    const dept = pos.department_name || 'Other'
    if (!map[dept]) map[dept] = { dept_name: dept, positions: [] }
    map[dept].positions.push(pos)
  })
  return Object.values(map)
})

// ── Available groups ────────────────────────────────────────────────────────
const availableGroups = computed(() => rbacStore.groups)

// ── Canvas signature ────────────────────────────────────────────────────────
const canvasRef    = ref(null)
const isDrawing    = ref(false)
const hasDrawn     = ref(false)
const signatureFile    = ref(null)
const signaturePreview = ref(null)

const currentSignature = ref(null)

// Watch employee prop — bisa datang telat karena parent fetch dulu
watch(() => props.employee, (emp) => {
  if (!emp) return
  currentSignature.value = emp.signature_draw || emp.signature_image_url || null
  console.log('✅ employee prop arrived:', emp.signature_draw?.slice(0, 30))
}, { immediate: true })

function getCanvasPos(e) {
  const rect = canvasRef.value.getBoundingClientRect()
  const scaleX = canvasRef.value.width / rect.width
  const scaleY = canvasRef.value.height / rect.height
  return {
    x: (e.clientX - rect.left) * scaleX,
    y: (e.clientY - rect.top)  * scaleY,
  }
}

function startDraw(e) {
  isDrawing.value = true
  const ctx = canvasRef.value.getContext('2d')
  const pos = getCanvasPos(e)
  ctx.beginPath()
  ctx.moveTo(pos.x, pos.y)
}

function draw(e) {
  if (!isDrawing.value) return
  const ctx = canvasRef.value.getContext('2d')
  const pos = getCanvasPos(e)
  ctx.lineWidth   = 2
  ctx.lineCap     = 'round'
  ctx.strokeStyle = '#1A2744'
  ctx.lineTo(pos.x, pos.y)
  ctx.stroke()
  hasDrawn.value = true
}

function stopDraw() { isDrawing.value = false }

function startDrawTouch(e) {
  const touch = e.touches[0]
  startDraw({ clientX: touch.clientX, clientY: touch.clientY })
}

function drawTouch(e) {
  const touch = e.touches[0]
  draw({ clientX: touch.clientX, clientY: touch.clientY })
}

function clearCanvas() {
  const ctx = canvasRef.value.getContext('2d')
  ctx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height)
  hasDrawn.value = false
}

function getCanvasDataUrl() {
  if (!hasDrawn.value) return null
  return canvasRef.value.toDataURL('image/png')
}

function handleSignatureFile(e) {
  const file = e.target.files[0]
  if (!file) return
  signatureFile.value    = file
  signaturePreview.value = URL.createObjectURL(file)
}

async function handleTabClick(key) {
  activeTab.value = key
  if (key === 'signature' && isEdit.value && currentSignature.value) {
    setTimeout(() => {
      if (!canvasRef.value) return
      const src = props.employee?.signature_draw || currentSignature.value
      if (!src || !src.startsWith('data:')) return  // skip kalau bukan base64 draw
      const img = new Image()
      img.onload = () => {
        if (!canvasRef.value) return
        const canvas = canvasRef.value
        const ctx = canvas.getContext('2d')
        ctx.clearRect(0, 0, canvas.width, canvas.height)
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height)
        hasDrawn.value = true
        console.log('✅ Signature drawn to canvas')
      }
      img.src = src
    }, 100)
  }
}

// ── Save ───────────────────────────────────────────────────────────────────
async function handleSave() {
  serverError.value = ''
  errors.username   = ''

  // Validasi basic
  if (!form.full_name.trim() || !form.email || !form.position) {
    serverError.value = 'Full name, email, dan position wajib diisi.'
    activeTab.value   = 'info'
    return
  }
  if (!isEdit.value && (!form.username.trim() || !form.password)) {
    serverError.value = 'Username dan password wajib diisi.'
    activeTab.value   = 'user'
    return
  }

  if (!isEdit.value) {
    if (!form.username.trim()) {
        serverError.value = 'Username wajib diisi.'
        activeTab.value   = 'user'
        return
    }
    if (!form.password || form.password.length < 8) {
        serverError.value = 'Password minimal 8 karakter!'  // ← ini yang catch
        activeTab.value   = 'user'
        return
    }
    }

  isSaving.value = true

  try {
    let result

    if (isEdit.value) {
      // Update
      const payload = {
        full_name:               form.full_name,
        email:                   form.email,
        phone:                   form.phone,
        position:                form.position,
        join_date:               form.join_date || null,
        status:                  form.status,
        authorization_group_ids: form.authorization_group_ids,
      }
      result = await orgStore.updateEmployee(props.employee.id, payload)
    } else {
      // Create
      const payload = {
        full_name:               form.full_name,
        email:                   form.email,
        phone:                   form.phone,
        position:                form.position,
        join_date:               form.join_date || null,
        status:                  form.status,
        username:                form.username,
        password:                form.password,
        authorization_group_ids: form.authorization_group_ids,
      }
      result = await orgStore.createEmployee(payload)
    }

    // Handle signature setelah employee tersimpan
    const empId = result.id
    if (sigMode.value === 'draw' && hasDrawn.value) {
      const dataUrl = getCanvasDataUrl()
      if (dataUrl) {
        const sigResult = await orgStore.uploadSignature(empId, { signature_draw: dataUrl })
        // Update currentSignature langsung dari response backend
        currentSignature.value = sigResult?.signature_draw || dataUrl
      }
    } else if (sigMode.value === 'upload' && signatureFile.value) {
      const fd = new FormData()
      fd.append('signature_image', signatureFile.value)
      const sigResult = await orgStore.uploadSignature(empId, fd)
      // Clear preview lama — biar tampil URL dari server
      signaturePreview.value = sigResult?.signature_image || signaturePreview.value
      signatureFile.value    = null
    }

    emit('saved')
  } catch (err) {
    const data = err.response?.data
    if (data?.username) {
      errors.username   = data.username[0]
      activeTab.value   = 'user'
      serverError.value = 'Username sudah digunakan.'
    } else {
      serverError.value = data?.detail
                       || data?.non_field_errors?.[0]
                       || 'Gagal menyimpan employee.'
    }
  } finally {
    isSaving.value = false
  }
}

// ── Load data saat mount ────────────────────────────────────────────────────
onMounted(async () => {
  console.log('MODAL MOUNTED, employee:', props.employee?.signature_draw?.slice(0, 30))
  await Promise.all([
    orgStore.fetchPositions(),
    rbacStore.fetchGroups({ page_size: 999 }),
  ])
})
</script>

<style scoped>
@reference "../../style.css";
.form-input {
  @apply w-full px-3.5 py-2.5 text-sm border border-gray-200 rounded-xl
         focus:outline-none focus:ring-2 focus:ring-bfs-gold/30 focus:border-bfs-gold
         transition-all bg-white;
}
.btn-primary   { @apply px-4 py-2 bg-bfs-gold hover:bg-bfs-gold-dark text-white font-medium rounded-lg transition-colors disabled:opacity-60; }
.btn-secondary { @apply px-4 py-2 border border-gray-200 text-gray-600 hover:bg-gray-50 rounded-lg transition-colors; }
.modal-enter-active, .modal-leave-active { transition: opacity 0.2s; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
</style>