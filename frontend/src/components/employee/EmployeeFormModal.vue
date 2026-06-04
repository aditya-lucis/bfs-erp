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
              @click="activeTab = tab.key"
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

              <!-- Info kalau edit — username tidak bisa diganti -->
              <div v-if="isEdit && employee.username"
                class="flex items-center gap-3 p-3 bg-blue-50 border border-blue-100 rounded-xl">
                <Info class="w-4 h-4 text-blue-500 flex-shrink-0" />
                <p class="text-xs text-blue-700">
                  Username: <span class="font-mono font-bold">{{ employee.username }}</span>
                  — tidak bisa diubah. Reset password dari menu terpisah.
                </p>
              </div>

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

              <!-- Authorization Groups -->
              <FormField label="Authorization Groups">
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
              <div v-if="sigMode === 'draw'" class="space-y-3">
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
                <div v-if="existingSignature && !hasDrawn" class="p-3 bg-gray-50 rounded-xl border border-gray-100">
                  <p class="text-xs text-gray-400 mb-2">Signature saat ini:</p>
                  <img :src="existingSignature" class="max-h-20 object-contain" />
                </div>
              </div>

              <!-- Upload mode -->
              <div v-else class="space-y-3">
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
                <div v-if="signaturePreview || (isEdit && employee.signature_image)"
                  class="p-3 bg-gray-50 rounded-xl border border-gray-100">
                  <p class="text-xs text-gray-400 mb-2">Preview:</p>
                  <img
                    :src="signaturePreview || employee.signature_image"
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
import FormField from '../FormField.vue'
import {
  X, UserCircle, Save, Loader2, Eye, EyeOff,
  PenLine, Upload, Eraser, Info, AlertCircle,
  User, Shield, Pen,
} from 'lucide-vue-next'

const props  = defineProps({ employee: { type: Object, default: null } })
const emit   = defineEmits(['close', 'saved'])

const orgStore  = useOrganizationStore()
const rbacStore = useRbacStore()

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

const existingSignature = computed(() =>
  props.employee?.signature_draw || props.employee?.signature_image || null
)

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

// ── Load existing signature ke canvas kalau edit ───────────────────────────
watch(activeTab, async (tab) => {
  if (tab === 'signature' && isEdit.value && props.employee.signature_draw) {
    await nextTick()
    sigMode.value = 'draw'
    const img = new Image()
    img.onload = () => {
      const ctx = canvasRef.value.getContext('2d')
      ctx.drawImage(img, 0, 0)
      hasDrawn.value = true
    }
    img.src = props.employee.signature_draw
  }
})

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
        await orgStore.uploadSignature(empId, { signature_draw: dataUrl })
      }
    } else if (sigMode.value === 'upload' && signatureFile.value) {
      const fd = new FormData()
      fd.append('signature_image', signatureFile.value)
      await orgStore.uploadSignature(empId, fd)
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