<template>
  <Panel title="Organizational Structure" subtitle="Setting | Organizational Level">

    <!-- Toolbar -->
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-2">
        <button @click="expandAll" class="btn-secondary text-xs flex items-center gap-1.5">
          <ChevronsDown class="w-3.5 h-3.5" /> Expand All
        </button>
        <button @click="collapseAll" class="btn-secondary text-xs flex items-center gap-1.5">
          <ChevronsUp class="w-3.5 h-3.5" /> Collapse All
        </button>
      </div>
      <button @click="openAddModal(null)" class="btn-primary text-xs flex items-center gap-1.5">
        <Plus class="w-3.5 h-3.5" /> Add Department
      </button>
    </div>

    <!-- Loading -->
    <div v-if="orgStore.isLoading" class="flex justify-center py-16">
      <Loader2 class="w-7 h-7 animate-spin text-bfs-gold" />
    </div>

    <!-- Tree -->
    <div v-else-if="orgStore.departments.length" class="border border-gray-200 rounded-xl overflow-hidden">
      <div class="bg-gray-50 border-b border-gray-200 px-4 py-2.5 grid grid-cols-12 text-[11px] font-semibold text-gray-500 uppercase tracking-wide">
        <div class="col-span-5">Department</div>
        <div class="col-span-3">Code</div>
        <div class="col-span-2">Status</div>
        <div class="col-span-2 text-right">Action</div>
      </div>

      <div class="divide-y divide-gray-100">
        <DepartmentTreeNode
          v-for="dept in orgStore.departments"
          :key="dept.id"
          :node="dept"
          :expanded-ids="expandedIds"
          @toggle="toggleNode"
          @edit="openEditModal"
          @delete="confirmDelete"
          @add-child="openAddModal"
        />
      </div>
    </div>

    <!-- Empty -->
    <div v-else class="flex flex-col items-center justify-center py-20 text-gray-400">
      <Network class="w-10 h-10 mb-3" />
      <p class="text-sm">Belum ada data department.</p>
      <button @click="openAddModal(null)" class="mt-3 text-sm text-bfs-gold hover:underline">
        Tambah sekarang
      </button>
    </div>

    <!-- ── Modal Add/Edit ── -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="modal.show" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-black/40" @click="closeModal" />
          <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-md p-6 z-10">

            <div class="flex items-center justify-between mb-5">
              <h3 class="text-base font-semibold text-gray-800">
                {{ modal.mode === 'add' ? 'Tambah Department' : 'Edit Department' }}
              </h3>
              <button @click="closeModal" class="text-gray-400 hover:text-gray-600 transition-colors">
                <X class="w-5 h-5" />
              </button>
            </div>

            <form @submit.prevent="handleSubmit" class="space-y-4">

              <FormField label="Parent Department">
                <select v-model="modalForm.parent" class="form-input">
                  <option :value="null">— Root (Tidak ada parent) —</option>
                  <option 
                    v-for="dept in flatDepartmentOptions" 
                    :key="dept.id" 
                    :value="dept.id"
                    :disabled="dept.id === modal.editId"
                  >
                    {{ '　'.repeat(dept.level) }}{{ dept.code }}. {{ dept.name }}
                  </option>
                </select>
              </FormField>

              <FormField label="Code" required>
                <input 
                  v-model="modalForm.code" 
                  type="text" 
                  class="form-input" 
                  placeholder="e.g. fat, hr.umum"
                  :class="{ 'border-red-300': formErrors.code }"
                />
                <p v-if="formErrors.code" class="mt-1 text-xs text-red-500">{{ formErrors.code }}</p>
              </FormField>

              <FormField label="Name" required>
                <input 
                  v-model="modalForm.name" 
                  type="text" 
                  class="form-input" 
                  placeholder="e.g. Finance, Akutansi & Tax"
                  :class="{ 'border-red-300': formErrors.name }"
                />
                <p v-if="formErrors.name" class="mt-1 text-xs text-red-500">{{ formErrors.name }}</p>
              </FormField>

              <FormField label="Order">
                <input v-model.number="modalForm.order" type="number" min="0" class="form-input" />
              </FormField>

              <div class="flex items-center gap-3">
                <input 
                  v-model="modalForm.is_active" 
                  type="checkbox" 
                  id="dept_active"
                  class="w-4 h-4 rounded border-gray-300 text-bfs-gold focus:ring-bfs-gold"
                />
                <label for="dept_active" class="text-sm text-gray-700">Active</label>
              </div>

              <div class="flex justify-end gap-2 pt-2 border-t border-gray-100">
                <button type="button" @click="closeModal" class="btn-secondary text-sm">
                  Cancel
                </button>
                <button 
                  type="submit" 
                  :disabled="isSaving"
                  class="btn-primary text-sm flex items-center gap-1.5"
                >
                  <Loader2 v-if="isSaving" class="w-3.5 h-3.5 animate-spin" />
                  <Save v-else class="w-3.5 h-3.5" />
                  {{ modal.mode === 'add' ? 'Simpan' : 'Update' }}
                </button>
              </div>

            </form>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- ── Confirm Delete Modal ── -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="deleteModal.show" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-black/40" @click="deleteModal.show = false" />
          <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6 z-10">
            <div class="flex flex-col items-center text-center gap-3">
              <div class="w-12 h-12 rounded-full bg-red-100 flex items-center justify-center">
                <Trash2 class="w-6 h-6 text-red-500" />
              </div>
              <h3 class="text-base font-semibold text-gray-800">Hapus Department?</h3>
              <p class="text-sm text-gray-500">
                <span class="font-medium text-gray-700">{{ deleteModal.target?.name }}</span> 
                akan dihapus permanen. Department yang masih punya anak tidak bisa dihapus.
              </p>
            </div>
            <div class="flex gap-2 mt-5">
              <button @click="deleteModal.show = false" class="btn-secondary text-sm flex-1">
                Batal
              </button>
              <button 
                @click="handleDelete" 
                :disabled="isSaving"
                class="flex-1 text-sm py-2 px-4 bg-red-500 hover:bg-red-600 text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-1.5"
              >
                <Loader2 v-if="isSaving" class="w-3.5 h-3.5 animate-spin" />
                <Trash2 v-else class="w-3.5 h-3.5" />
                Hapus
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

  </Panel>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useOrganizationStore } from '../../stores/organization.js'
import Panel from '../../components/Panel.vue'
import FormField from '../../components/FormField.vue'
import DepartmentTreeNode from '../../components/DepartmentTreeNode.vue'
import {
  Plus, Save, X, Loader2, Trash2, Network,
  ChevronsDown, ChevronsUp,
} from 'lucide-vue-next'

const orgStore = useOrganizationStore()
const isSaving = ref(false)

// ── Expand/Collapse ────────────────────────────────────────────────────────
const expandedIds = ref(new Set())

function toggleNode(id) {
  if (expandedIds.value.has(id)) {
    expandedIds.value.delete(id)
  } else {
    expandedIds.value.add(id)
  }
}

function expandAll() {
  const addAll = (nodes) => {
    nodes.forEach(n => {
      expandedIds.value.add(n.id)
      if (n.children?.length) addAll(n.children)
    })
  }
  addAll(orgStore.departments)
}

function collapseAll() {
  expandedIds.value.clear()
}

// ── Flat list untuk dropdown options ──────────────────────────────────────
const flatDepartmentOptions = computed(() => orgStore.departmentList)

// ── Modal Add/Edit ─────────────────────────────────────────────────────────
const modal = reactive({
  show:   false,
  mode:   'add',   // 'add' | 'edit'
  editId: null,
})

const modalForm = reactive({
  parent:    null,
  code:      '',
  name:      '',
  order:     0,
  is_active: true,
})

const formErrors = reactive({ code: '', name: '' })

function openAddModal(parentId) {
  modal.show   = true
  modal.mode   = 'add'
  modal.editId = null
  modalForm.parent    = parentId
  modalForm.code      = ''
  modalForm.name      = ''
  modalForm.order     = 0
  modalForm.is_active = true
  formErrors.code = ''
  formErrors.name = ''
}

function openEditModal(dept) {
  modal.show   = true
  modal.mode   = 'edit'
  modal.editId = dept.id
  modalForm.parent    = dept.parent
  modalForm.code      = dept.code
  modalForm.name      = dept.name
  modalForm.order     = dept.order
  modalForm.is_active = dept.is_active
  formErrors.code = ''
  formErrors.name = ''
}

function closeModal() {
  modal.show = false
}

function validateForm() {
  let valid = true
  formErrors.code = ''
  formErrors.name = ''
  if (!modalForm.code.trim()) { formErrors.code = 'Code wajib diisi.'; valid = false }
  if (!modalForm.name.trim()) { formErrors.name = 'Name wajib diisi.'; valid = false }
  return valid
}

async function handleSubmit() {
  if (!validateForm()) return
  isSaving.value = true
  try {
    const payload = { ...modalForm }
    if (modal.mode === 'add') {
      await orgStore.createDepartment(payload)
    } else {
      await orgStore.updateDepartment(modal.editId, payload)
    }
    closeModal()
    await orgStore.fetchDepartments()
  } catch (err) {
    console.error(err)
  } finally {
    isSaving.value = false
  }
}

// ── Delete ─────────────────────────────────────────────────────────────────
const deleteModal = reactive({ show: false, target: null })

function confirmDelete(dept) {
  deleteModal.target = dept
  deleteModal.show   = true
}

async function handleDelete() {
  isSaving.value = true
  try {
    await orgStore.deleteDepartment(deleteModal.target.id)
    deleteModal.show = false
    await orgStore.fetchDepartments()
  } catch (err) {
    console.error(err)
  } finally {
    isSaving.value = false
  }
}

onMounted(() => {
  orgStore.fetchDepartments()
})
</script>

<style scoped>
@reference "../../style.css";

.form-input {
  @apply w-full px-3 py-2 text-sm border border-gray-200 rounded-lg
         focus:outline-none focus:ring-2 focus:ring-bfs-gold/40 focus:border-bfs-gold
         transition-all bg-white;
}
.btn-primary {
  @apply px-4 py-2 bg-bfs-gold hover:bg-bfs-gold-dark text-white font-medium rounded-lg transition-colors disabled:opacity-60;
}
.btn-secondary {
  @apply px-4 py-2 border border-gray-200 text-gray-600 hover:bg-gray-50 rounded-lg transition-colors;
}
.modal-enter-active, .modal-leave-active { transition: opacity 0.2s; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
</style>