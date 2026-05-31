<template>
  <div>
    <!-- Row department — sama seperti sebelumnya -->
    <div
      class="grid grid-cols-12 px-4 py-2.5 items-center hover:bg-gray-50 transition-colors group"
      :style="{ paddingLeft: `${16 + node.level * 24}px` }"
    >
      <!-- Expand toggle + icon + name -->
      <div class="col-span-5 flex items-center gap-2 min-w-0">
        <button
          @click="toggleExpand"
          class="w-5 h-5 flex items-center justify-center text-gray-400 hover:text-gray-600 flex-shrink-0 transition-colors"
        >
          <component
            :is="hasChildren || hasPositions
              ? (isExpanded ? ChevronDown : ChevronRight)
              : 'span'"
            class="w-4 h-4"
          />
        </button>

        <component
          :is="hasChildren ? Folders : Folder"
          class="w-4 h-4 flex-shrink-0"
          :class="hasChildren ? 'text-bfs-gold' : 'text-gray-400'"
        />

        <span class="text-sm text-gray-800 truncate font-medium">
          {{ node.name }}
        </span>
      </div>

      <!-- Code -->
      <div class="col-span-3">
        <span class="text-xs font-mono text-gray-500 bg-gray-100 px-2 py-0.5 rounded">
          {{ node.code }}
        </span>
      </div>

      <!-- Status -->
      <div class="col-span-2">
        <span
          :class="node.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'"
          class="text-xs px-2 py-0.5 rounded-full font-medium"
        >
          {{ node.is_active ? 'Active' : 'Inactive' }}
        </span>
      </div>

      <!-- Actions -->
      <div class="col-span-2 flex justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
        <button
          @click="$emit('add-child', node.id)"
          class="p-1.5 text-gray-400 hover:text-bfs-gold hover:bg-bfs-gold/10 rounded-lg transition-colors"
          title="Tambah sub-department"
        >
          <Plus class="w-3.5 h-3.5" />
        </button>
        <button
          @click="togglePositions"
          class="p-1.5 rounded-lg transition-colors"
          :class="showPositions
            ? 'text-bfs-gold bg-bfs-gold/10'
            : 'text-gray-400 hover:text-bfs-gold hover:bg-bfs-gold/10'"
          title="Lihat positions"
        >
          <Briefcase class="w-3.5 h-3.5" />
        </button>
        <button
          @click="$emit('edit', node)"
          class="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
          title="Edit"
        >
          <Pencil class="w-3.5 h-3.5" />
        </button>
        <button
          @click="$emit('delete', node)"
          class="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
          title="Hapus"
        >
          <Trash2 class="w-3.5 h-3.5" />
        </button>
      </div>
    </div>

    <!-- ── Positions Panel (inline) ── -->
    <Transition name="slide">
      <div
        v-if="showPositions"
        :style="{ paddingLeft: `${16 + node.level * 24 + 40}px` }"
        class="pr-4 pb-3 bg-blue-50/40 border-b border-blue-100"
      >
        <!-- Loading positions -->
        <div v-if="posLoading" class="flex items-center gap-2 py-3 text-xs text-gray-400">
          <Loader2 class="w-3.5 h-3.5 animate-spin" />
          Memuat positions...
        </div>

        <template v-else>
          <!-- Header positions -->
          <div class="flex items-center justify-between py-2.5">
            <p class="text-xs font-semibold text-bfs-navy uppercase tracking-wide flex items-center gap-1.5">
              <Briefcase class="w-3.5 h-3.5" />
              Positions
              <span class="font-normal text-gray-400">({{ positions.length }})</span>
            </p>
            <button
              @click="openPositionForm(null)"
              class="text-xs text-bfs-gold hover:text-bfs-gold-dark flex items-center gap-1 font-medium"
            >
              <Plus class="w-3.5 h-3.5" />
              Add Position
            </button>
          </div>

          <!-- Position list -->
          <div v-if="positions.length" class="space-y-1.5 mb-2">
            <div
              v-for="pos in positions"
              :key="pos.id"
              class="flex items-center justify-between px-3 py-2 bg-white rounded-lg border border-gray-100 group/pos hover:border-bfs-gold/30 hover:shadow-sm transition-all"
            >
              <div class="flex items-center gap-2.5 min-w-0">
                <div class="w-6 h-6 rounded-full bg-bfs-navy/8 flex items-center justify-center flex-shrink-0">
                  <UserCircle class="w-3.5 h-3.5 text-bfs-navy/50" />
                </div>
                <div class="min-w-0">
                  <p class="text-sm font-medium text-gray-800 truncate">{{ pos.name }}</p>
                  <p class="text-[10px] text-gray-400 font-mono">{{ pos.code }}</p>
                </div>
              </div>

              <div class="flex items-center gap-3 flex-shrink-0">
                <!-- Employee count badge -->
                <span class="text-xs text-gray-400 flex items-center gap-1">
                  <Users class="w-3 h-3" />
                  {{ pos.employee_count || 0 }}
                </span>

                <!-- Active badge -->
                <span
                  :class="pos.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-400'"
                  class="text-[10px] px-1.5 py-0.5 rounded-full font-medium"
                >
                  {{ pos.is_active ? 'Active' : 'Inactive' }}
                </span>

                <!-- Actions -->
                <div class="flex gap-1 opacity-0 group-hover/pos:opacity-100 transition-opacity">
                  <button
                    @click="openPositionForm(pos)"
                    class="p-1 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
                  >
                    <Pencil class="w-3 h-3" />
                  </button>
                  <button
                    @click="confirmDeletePosition(pos)"
                    class="p-1 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded transition-colors"
                  >
                    <Trash2 class="w-3 h-3" />
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Empty positions -->
          <div v-else class="py-3 text-center text-xs text-gray-400">
            Belum ada position di department ini.
          </div>
        </template>
      </div>
    </Transition>

    <!-- ── Children departments ── -->
    <Transition name="slide">
      <div v-if="isExpanded && hasChildren">
        <DepartmentTreeNode
          v-for="child in node.children"
          :key="child.id"
          :node="child"
          :expanded-ids="expandedIds"
          @toggle="$emit('toggle', $event)"
          @edit="$emit('edit', $event)"
          @delete="$emit('delete', $event)"
          @add-child="$emit('add-child', $event)"
        />
      </div>
    </Transition>

    <!-- ── Position Form Modal ── -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="posModal.show" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-black/40" @click="posModal.show = false" />
          <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6 z-10">

            <div class="flex items-center justify-between mb-4">
              <h3 class="text-base font-semibold text-gray-800">
                {{ posModal.editId ? 'Edit Position' : 'Add Position' }}
              </h3>
              <button @click="posModal.show = false" class="text-gray-400 hover:text-gray-600">
                <X class="w-5 h-5" />
              </button>
            </div>

            <p class="text-xs text-gray-400 mb-4 -mt-2">
              Department: <span class="font-medium text-bfs-navy">{{ node.name }}</span>
            </p>

            <form @submit.prevent="handlePositionSubmit" class="space-y-3">

              <FormField label="Position Code" required>
                <input
                  v-model="posForm.code"
                  type="text"
                  class="form-input font-mono uppercase"
                  placeholder="e.g. ACC-MGR"
                  :class="{ 'border-red-300': posErrors.code }"
                />
                <p v-if="posErrors.code" class="mt-1 text-xs text-red-500">{{ posErrors.code }}</p>
              </FormField>

              <FormField label="Position Name" required>
                <input
                  v-model="posForm.name"
                  type="text"
                  class="form-input"
                  placeholder="e.g. Accounting Manager"
                  :class="{ 'border-red-300': posErrors.name }"
                />
                <p v-if="posErrors.name" class="mt-1 text-xs text-red-500">{{ posErrors.name }}</p>
              </FormField>

              <FormField label="Description">
                <textarea
                  v-model="posForm.description"
                  rows="2"
                  class="form-input resize-none"
                  placeholder="Deskripsi jabatan..."
                />
              </FormField>

              <div class="flex items-center gap-3">
                <input
                  v-model="posForm.is_active"
                  type="checkbox"
                  id="pos_active"
                  class="w-4 h-4 rounded border-gray-300 text-bfs-gold focus:ring-bfs-gold"
                />
                <label for="pos_active" class="text-sm text-gray-700">Active</label>
              </div>

              <!-- Error server -->
              <div v-if="posServerError" class="p-3 bg-red-50 border border-red-200 text-red-600 rounded-lg text-xs">
                {{ posServerError }}
              </div>

              <div class="flex justify-end gap-2 pt-2 border-t border-gray-100">
                <button
                  type="button"
                  @click="posModal.show = false"
                  class="btn-secondary text-sm"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  :disabled="posSaving"
                  class="btn-primary text-sm flex items-center gap-1.5"
                >
                  <Loader2 v-if="posSaving" class="w-3.5 h-3.5 animate-spin" />
                  <Save v-else class="w-3.5 h-3.5" />
                  {{ posModal.editId ? 'Update' : 'Simpan' }}
                </button>
              </div>

            </form>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- ── Delete Position Confirm ── -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="deletePosModal.show" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-black/40" @click="deletePosModal.show = false" />
          <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6 z-10 text-center">
            <div class="w-12 h-12 rounded-full bg-red-100 flex items-center justify-center mx-auto mb-3">
              <Trash2 class="w-6 h-6 text-red-500" />
            </div>
            <h3 class="font-semibold text-gray-800 mb-1">Hapus Position?</h3>
            <p class="text-sm text-gray-500 mb-4">
              <span class="font-medium">{{ deletePosModal.target?.name }}</span>
              akan dihapus. Position yang masih punya employee tidak bisa dihapus.
            </p>
            <div class="flex gap-2">
              <button @click="deletePosModal.show = false" class="btn-secondary text-sm flex-1">
                Batal
              </button>
              <button
                @click="handleDeletePosition"
                :disabled="posSaving"
                class="flex-1 text-sm py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg font-medium flex items-center justify-center gap-1.5 transition-colors"
              >
                <Loader2 v-if="posSaving" class="w-3.5 h-3.5 animate-spin" />
                <Trash2 v-else class="w-3.5 h-3.5" />
                Hapus
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useOrganizationStore } from '../stores/organization.js'
import FormField from './FormField.vue'
import {
  ChevronRight, ChevronDown, Folder, Folders,
  Plus, Pencil, Trash2, Briefcase,
  UserCircle, Users, Loader2, Save, X,
} from 'lucide-vue-next'

const props = defineProps({
  node:        { type: Object, required: true },
  expandedIds: { type: Set,    required: true },
})

const orgStore = useOrganizationStore()

// ── Department expand ──────────────────────────────────────────────────────
const hasChildren = computed(() => props.node.children?.length > 0)
const isExpanded  = computed(() => props.expandedIds.has(props.node.id))

function toggleExpand() {
  // emit toggle ke parent (DepartmentView yang handle expandedIds)
  // tapi kalau leaf node → toggle positions
  if (hasChildren.value) {
    emit('toggle', props.node.id)
  } else {
    togglePositions()
  }
}

// ── Positions ──────────────────────────────────────────────────────────────
const showPositions = ref(false)
const posLoading    = ref(false)
const positions     = ref([])

const hasPositions  = computed(() => positions.value.length > 0)

async function togglePositions() {
  showPositions.value = !showPositions.value
  if (showPositions.value && positions.value.length === 0) {
    await loadPositions()
  }
}

async function loadPositions() {
  posLoading.value = true
  try {
    positions.value = await orgStore.fetchPositionsByDept(props.node.id)
  } finally {
    posLoading.value = false
  }
}

// ── Position Form ──────────────────────────────────────────────────────────
const posSaving     = ref(false)
const posServerError = ref('')

const posModal = reactive({
  show:   false,
  editId: null,
})

const posForm = reactive({
  code:        '',
  name:        '',
  description: '',
  is_active:   true,
})

const posErrors = reactive({ code: '', name: '' })

function openPositionForm(pos) {
  posServerError.value = ''
  posErrors.code = ''
  posErrors.name = ''

  if (pos) {
    posModal.editId      = pos.id
    posForm.code        = pos.code
    posForm.name        = pos.name
    posForm.description = pos.description || ''
    posForm.is_active   = pos.is_active
  } else {
    posModal.editId      = null
    posForm.code        = ''
    posForm.name        = ''
    posForm.description = ''
    posForm.is_active   = true
  }
  posModal.show = true
}

function validatePosForm() {
  posErrors.code = ''
  posErrors.name = ''
  let valid = true
  if (!posForm.code.trim()) { posErrors.code = 'Code wajib diisi.'; valid = false }
  if (!posForm.name.trim()) { posErrors.name = 'Name wajib diisi.'; valid = false }
  return valid
}

async function handlePositionSubmit() {
  if (!validatePosForm()) return
  posSaving.value      = true
  posServerError.value = ''

  try {
    if (posModal.editId) {
      const updated = await orgStore.updatePosition(
        props.node.id, posModal.editId, { ...posForm }
      )
      // Update lokal
      const idx = positions.value.findIndex(p => p.id === posModal.editId)
      if (idx !== -1) positions.value[idx] = updated
    } else {
      const created = await orgStore.createPosition(props.node.id, { ...posForm })
      positions.value.push(created)
    }
    posModal.show = false
  } catch (err) {
    posServerError.value = err.response?.data?.code?.[0]
                        || err.response?.data?.detail
                        || 'Gagal menyimpan position.'
  } finally {
    posSaving.value = false
  }
}

// ── Delete Position ────────────────────────────────────────────────────────
const deletePosModal = reactive({ show: false, target: null })

function confirmDeletePosition(pos) {
  deletePosModal.target = pos
  deletePosModal.show   = true
}

async function handleDeletePosition() {
  posSaving.value = true
  try {
    await orgStore.deletePosition(props.node.id, deletePosModal.target.id)
    positions.value     = positions.value.filter(p => p.id !== deletePosModal.target.id)
    deletePosModal.show = false
  } catch (err) {
    // Kalau masih ada employee → backend return 400
    posServerError.value = err.response?.data?.detail || 'Gagal menghapus.'
    deletePosModal.show  = false
    posModal.show        = false
  } finally {
    posSaving.value = false
  }
}

// expose emit (karena ada di dalam setup tapi dipanggil di toggleExpand)
const emit = defineEmits(['toggle', 'edit', 'delete', 'add-child'])
</script>

<script>
export default { name: 'DepartmentTreeNode' }
</script>

<style scoped>
@reference "../style.css";
.form-input {
  @apply w-full px-3 py-2 text-sm border border-gray-200 rounded-lg
         focus:outline-none focus:ring-2 focus:ring-bfs-gold/40 focus:border-bfs-gold
         transition-all bg-white;
}
.btn-primary   { @apply px-4 py-2 bg-bfs-gold hover:bg-bfs-gold-dark text-white font-medium rounded-lg transition-colors disabled:opacity-60; }
.btn-secondary { @apply px-4 py-2 border border-gray-200 text-gray-600 hover:bg-gray-50 rounded-lg transition-colors; }
.slide-enter-active, .slide-leave-active  { transition: all 0.2s ease; overflow: hidden; }
.slide-enter-from, .slide-leave-to        { max-height: 0; opacity: 0; }
.slide-enter-to, .slide-leave-from        { max-height: 2000px; opacity: 1; }
.modal-enter-active, .modal-leave-active  { transition: opacity 0.2s; }
.modal-enter-from, .modal-leave-to        { opacity: 0; }
</style>