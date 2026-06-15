<template>
  <Panel title="Chart of Accounts" subtitle="General Ledger | Chart of Accounts">

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
      <div class="flex items-center gap-2">
        <button
          v-if="canCreate"
          @click="openGroupModal"
          class="btn-secondary text-xs flex items-center gap-1.5"
        >
          <FolderPlus class="w-3.5 h-3.5" /> Add Group
        </button>
        <button
          v-if="canCreate"
          @click="openAddModal(null)"
          class="btn-primary text-xs flex items-center gap-1.5"
        >
          <Plus class="w-3.5 h-3.5" /> New Account
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="store.isLoading" class="flex justify-center py-20">
      <Loader2 class="w-7 h-7 animate-spin text-bfs-gold" />
    </div>

    <!-- COA Tree — grouped by AccountGroup -->
    <div v-else-if="store.coaTree.length" class="space-y-4">
      <div
        v-for="section in store.coaTree"
        :key="section.group.id"
        class="border border-gray-200 rounded-xl overflow-hidden"
      >
        <!-- Group Header -->
        <div class="bg-gray-700 px-4 py-2.5 flex items-center justify-between">
          <div class="flex items-center gap-2">
            <Layers class="w-4 h-4 text-gray-300" />
            <span class="text-sm font-semibold text-white tracking-wide">
              {{ section.group.name }}
            </span>
            <span class="text-xs text-gray-400 font-mono">[{{ section.group.number_prefix }}]</span>
            <span class="text-xs font-bold text-bfs-gold bg-black/30 px-2 py-0.5 rounded ml-3">
              Total: Rp {{ Number(section.group.amount || 0).toLocaleString('id-ID') }}
            </span>
          </div>
          <span class="text-xs text-gray-400 font-semibold">
            {{ section.group.default_position }}
          </span>
        </div>
 
        <!-- Column Headers -->
        <div class="bg-gray-50 border-b border-gray-200 px-4 py-2 grid grid-cols-12 text-[11px] font-semibold text-gray-500 uppercase tracking-wide">
          <div class="col-span-5">Account Name</div>
          <div class="col-span-2">Type</div>
          <div class="col-span-1">Position</div>
          <div class="col-span-2">Currency / Amount</div>
          <div class="col-span-2 text-right">Action</div>
        </div>

        <!-- Account rows -->
        <div v-if="section.accounts.length">
          <AccountTreeNode
            v-for="account in section.accounts"
            :key="account.id"
            :node="account"
            :expanded-ids="expandedIds"
            :can-create="canCreate"
            :can-update="canUpdate"
            :can-delete="canDelete"
            @toggle="toggleNode"
            @edit="openEditModal"
            @delete="confirmDelete"
            @add-child="openAddModal"
          />
        </div>
        <div v-else class="px-4 py-6 text-sm text-gray-400 text-center">
          Belum ada akun di group ini.
          <button v-if="canCreate" @click="openAddModalInGroup(section.group)" class="ml-1 text-bfs-gold hover:underline">
            Tambah sekarang
          </button>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else class="flex flex-col items-center justify-center py-20 text-gray-400">
      <BookOpen class="w-10 h-10 mb-3" />
      <p class="text-sm">Belum ada Chart of Account.</p>
      <button v-if="canCreate" @click="openAddModal(null)" class="mt-3 text-sm text-bfs-gold hover:underline">
        Buat akun pertama
      </button>
    </div>

    <!-- ── Account Form Modal ── -->
    <AccountFormModal
      ref="accountFormModalRef"
      :show="modal.show"
      :mode="modal.mode"
      :edit-id="modal.editId"
      :initial-data="modal.initialData"
      :parent-account="modal.parentAccount"
      :account-groups="store.accountGroups"
      :header-accounts="headerAccountsFlat"
      :choices="store.choices"
      @close="modal.show = false"
      @saved="handleSaved"
    />

    <!-- ── Account Group Form Modal ── -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="groupModal.show" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-black/40" @click="groupModal.show = false" />
          <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6 z-10">

            <div class="flex items-center justify-between mb-5">
              <h3 class="text-base font-semibold text-gray-800">
                {{ groupModal.mode === 'add' ? 'New Account Group' : 'Edit Group' }}
              </h3>
              <button @click="groupModal.show = false" class="text-gray-400 hover:text-gray-600">
                <X class="w-5 h-5" />
              </button>
            </div>

            <div class="space-y-3">
              <FormField label="Code" required>
                <input v-model="groupForm.code" class="form-input" placeholder="e.g. AKTIVA" />
                <p v-if="groupErrors.code" class="mt-1 text-xs text-red-500">{{ groupErrors.code }}</p>
              </FormField>
              <FormField label="Name" required>
                <input v-model="groupForm.name" class="form-input" placeholder="e.g. Aktiva" />
                <p v-if="groupErrors.name" class="mt-1 text-xs text-red-500">{{ groupErrors.name }}</p>
              </FormField>
              <FormField label="Number Prefix" required>
                <input v-model="groupForm.number_prefix" class="form-input font-mono" placeholder="e.g. 1" />
                <p class="mt-1 text-xs text-gray-400">Semua nomor akun di group ini harus diawali prefix ini.</p>
              </FormField>
              <FormField label="Default Position">
                <select v-model="groupForm.default_position" class="form-input">
                  <option value="DEBET">Debet</option>
                  <option value="KREDIT">Kredit</option>
                </select>
              </FormField>
              <FormField label="Order">
                <input v-model.number="groupForm.order" type="number" min="0" class="form-input" />
              </FormField>
            </div>

            <div class="flex justify-end gap-2 mt-5 pt-4 border-t border-gray-100">
              <button @click="groupModal.show = false" class="btn-secondary text-sm">Cancel</button>
              <button @click="handleGroupSave" :disabled="isSaving" class="btn-primary text-sm flex items-center gap-1.5">
                <Loader2 v-if="isSaving" class="w-3.5 h-3.5 animate-spin" />
                <Save v-else class="w-3.5 h-3.5" />
                Save
              </button>
            </div>
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
              <h3 class="text-base font-semibold text-gray-800">Hapus Akun?</h3>
              <p class="text-sm text-gray-500">
                <span class="font-medium text-gray-700">
                  {{ deleteModal.target?.account_number }} {{ deleteModal.target?.account_name }}
                </span>
                akan dihapus. Akun yang masih punya child tidak bisa dihapus.
              </p>
            </div>
            <div class="flex gap-2 mt-5">
              <button @click="deleteModal.show = false" class="btn-secondary text-sm flex-1">Batal</button>
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
import { useAccountingStore } from '../../stores/accounting.js'
import { usePermission } from '../../composables/usePermission.js'
import Panel from '../../components/Panel.vue'
import FormField from '../../components/FormField.vue'
import AccountTreeNode from '../../components/accounting/AccountTreeNode.vue'
import AccountFormModal from '../../components/accounting/AccountFormModal.vue'
import {
  Plus, Save, X, Loader2, Trash2, BookOpen,
  ChevronsDown, ChevronsUp, FolderPlus, Layers,
} from 'lucide-vue-next'

const store   = useAccountingStore()
const { canCreate, canUpdate, canDelete } = usePermission('GL-CHART-OF-ACCOUNT')
const isSaving = ref(false)
const accountFormModalRef = ref(null)

// ── Expand / Collapse ──────────────────────────────────────────────────────
const expandedIds = ref(new Set())

function toggleNode(id) {
  if (expandedIds.value.has(id)) expandedIds.value.delete(id)
  else expandedIds.value.add(id)
}

function expandAll() {
  const addAll = (nodes) => {
    nodes.forEach(n => {
      expandedIds.value.add(n.id)
      if (n.children?.length) addAll(n.children)
    })
  }
  store.coaTree.forEach(s => addAll(s.accounts))
}

function collapseAll() {
  expandedIds.value.clear()
}

// ── Flat list HEADER accounts untuk dropdown parent di form ────────────────
const headerAccountsFlat = computed(() => {
  const result = []
  const flatten = (nodes, level = 0) => {
    nodes.forEach(n => {
      if (n.account_type === 'HEADER') {
        result.push({ ...n, level })
        if (n.children?.length) flatten(n.children, level + 1)
      }
    })
  }
  store.coaTree.forEach(s => flatten(s.accounts))
  return result
})

// ── Account Form Modal ─────────────────────────────────────────────────────
const modal = reactive({
  show:          false,
  mode:          'add',
  editId:        null,
  initialData:   null,
  parentAccount: null,
})

function openAddModal(parentNode) {
  modal.show          = true
  modal.mode          = 'add'
  modal.editId        = null
  modal.initialData   = null
  modal.parentAccount = parentNode  // bisa null (root) atau node HEADER
}

function openAddModalInGroup(group) {
  modal.show          = true
  modal.mode          = 'add'
  modal.editId        = null
  modal.initialData   = null
  modal.parentAccount = { account_group: group.id }
}

function openEditModal(account) {
  modal.show          = true
  modal.mode          = 'edit'
  modal.editId        = account.id
  modal.initialData   = account
  modal.parentAccount = null
}

async function handleSaved(formData) {
  // Set loading di modal
  accountFormModalRef.value?.setLoading(true)

  try {
    if (modal.mode === 'add') {
      await store.createAccount(formData)
    } else {
      await store.updateAccount(modal.editId, formData)
    }
    // Sukses — tutup modal & refresh tree
    modal.show = false
    await store.fetchCoaTree()

  } catch (err) {
    // Parse error dari backend → kirim ke modal
    const data = err?.response?.data

    if (!data) {
      accountFormModalRef.value?.setErrors('Terjadi kesalahan server. Silakan coba lagi.')
      return
    }

    if (typeof data === 'object' && !Array.isArray(data)) {
      const fieldErrors = {}
      let generalError  = ''

      for (const [field, messages] of Object.entries(data)) {
        const msg = Array.isArray(messages) ? messages[0] : String(messages)
        if (field === 'non_field_errors' || field === 'detail') {
          generalError = msg
        } else {
          fieldErrors[field] = msg
        }
      }

      // Kalau ada field error tapi gak ada general error, kasih hint
      if (Object.keys(fieldErrors).length && !generalError) {
        generalError = 'Periksa kembali isian form.'
      }

      accountFormModalRef.value?.setErrors(generalError, fieldErrors)
    } else {
      accountFormModalRef.value?.setErrors(String(data))
    }

  } finally {
    accountFormModalRef.value?.setLoading(false)
  }
}

// ── Delete ─────────────────────────────────────────────────────────────────
const deleteModal = reactive({ show: false, target: null })

function confirmDelete(account) {
  deleteModal.target = account
  deleteModal.show   = true
}

async function handleDelete() {
  isSaving.value = true
  try {
    await store.deleteAccount(deleteModal.target.id)
    deleteModal.show = false
    await store.fetchCoaTree()
  } catch (err) {
    console.error(err)
  } finally {
    isSaving.value = false
  }
}

// ── Account Group Modal ────────────────────────────────────────────────────
const groupModal  = reactive({ show: false, mode: 'add', editId: null })
const groupForm   = reactive({ code: '', name: '', number_prefix: '', default_position: 'DEBET', order: 0 })
const groupErrors = reactive({})

function openGroupModal() {
  groupModal.show = true
  groupModal.mode = 'add'
  Object.assign(groupForm, { code: '', name: '', number_prefix: '', default_position: 'DEBET', order: 0 })
  Object.keys(groupErrors).forEach(k => delete groupErrors[k])
}

async function handleGroupSave() {
  Object.keys(groupErrors).forEach(k => delete groupErrors[k])
  if (!groupForm.code.trim())          { groupErrors.code = 'Wajib diisi.'; return }
  if (!groupForm.name.trim())          { groupErrors.name = 'Wajib diisi.'; return }
  if (!groupForm.number_prefix.trim()) { groupErrors.number_prefix = 'Wajib diisi.'; return }

  isSaving.value = true
  try {
    await store.createAccountGroup({ ...groupForm })
    groupModal.show = false
    await Promise.all([store.fetchAccountGroups(), store.fetchCoaTree()])
  } catch (err) {
    console.error(err)
  } finally {
    isSaving.value = false
  }
}

// ── Init ───────────────────────────────────────────────────────────────────
onMounted(async () => {
  await Promise.all([
    store.fetchCoaTree(),
    store.fetchAccountGroups(),
    store.fetchChoices(),
  ])
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