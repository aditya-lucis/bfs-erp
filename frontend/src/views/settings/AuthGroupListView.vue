<template>
  <Panel title="User Authorization Group" subtitle="Setting | Function Authorization">

    <!-- Search + Add -->
    <div class="flex items-center justify-between mb-4 gap-3">
      <div class="flex items-center gap-2 flex-1 max-w-sm">
        <div class="relative flex-1">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            v-model="search"
            type="text"
            placeholder="Cari group..."
            class="w-full pl-9 pr-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-bfs-gold/40 focus:border-bfs-gold"
            @input="onSearch"
          />
        </div>
        <select 
          v-model="filterStatus" 
          @change="onSearch"
          class="text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-bfs-gold/40"
        >
          <option value="">All Status</option>
          <option value="true">Active</option>
          <option value="false">Inactive</option>
        </select>
      </div>
      <button v-if="canCreate" @click="openForm(null)" class="btn-primary text-sm flex items-center gap-1.5">
        <Plus class="w-4 h-4" /> Add Group
      </button>
    </div>

    <!-- Table -->
    <div class="border border-gray-200 rounded-xl overflow-hidden">
      <!-- Header -->
      <div class="bg-gray-50 border-b border-gray-200 grid grid-cols-12 px-4 py-2.5 text-[11px] font-semibold text-gray-500 uppercase tracking-wide">
        <div class="col-span-1">No.</div>
        <div class="col-span-1">ID</div>
        <div class="col-span-3">Group Name</div>
        <div class="col-span-5">Description</div>
        <div class="col-span-1 text-center">Status</div>
        <div class="col-span-1 text-right">Action</div>
      </div>

      <!-- Loading -->
      <div v-if="rbacStore.isLoading" class="flex justify-center py-12">
        <Loader2 class="w-6 h-6 animate-spin text-bfs-gold" />
      </div>

      <!-- Rows -->
      <template v-else-if="rbacStore.groups.length">
        <div
          v-for="(group, idx) in rbacStore.groups"
          :key="group.id"
          class="grid grid-cols-12 px-4 py-3 items-center border-b border-gray-100 last:border-0 hover:bg-blue-50/30 transition-colors group"
        >
          <div class="col-span-1 text-sm text-gray-500">
            {{ (pagination.page - 1) * 15 + idx + 1 }}
          </div>
          <div class="col-span-1 text-sm text-gray-500">{{ group.id }}</div>
          <div class="col-span-3">
            <button 
              @click="openForm(group)"
              class="text-sm font-medium text-bfs-navy hover:text-bfs-gold transition-colors text-left"
            >
              {{ group.group_name }}
            </button>
          </div>
          <div class="col-span-5 text-sm text-gray-600 truncate">{{ group.description }}</div>
          <div class="col-span-1 flex justify-center">
            <span :class="group.status ? 'badge-active' : 'badge-inactive'">
              {{ group.status ? 'Active' : 'Inactive' }}
            </span>
          </div>
          <div class="col-span-1 flex justify-end">
            <div class="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
              <button v-if="canUpdate"
                @click="openForm(group)" 
                class="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                title="Edit"
              >
                <Pencil class="w-3.5 h-3.5" />
              </button>
              <button v-if="canDelete"
                @click="confirmDelete(group)"
                class="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                title="Delete"
              >
                <Trash2 class="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>
      </template>

      <!-- Empty -->
      <div v-else class="flex flex-col items-center justify-center py-16 text-gray-400">
        <ShieldOff class="w-8 h-8 mb-2" />
        <p class="text-sm">Tidak ada data group.</p>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="pagination.count > 15" class="flex items-center justify-between mt-4">
      <p class="text-xs text-gray-500">
        Total: <span class="font-medium">{{ pagination.count }}</span> groups
      </p>
      <div class="flex items-center gap-1">
        <button 
          :disabled="!pagination.previous"
          @click="changePage(pagination.page - 1)"
          class="p-1.5 rounded-lg border border-gray-200 disabled:opacity-40 hover:bg-gray-50 transition-colors"
        >
          <ChevronLeft class="w-4 h-4" />
        </button>
        <span class="text-sm px-3">{{ pagination.page }}</span>
        <button 
          :disabled="!pagination.next"
          @click="changePage(pagination.page + 1)"
          class="p-1.5 rounded-lg border border-gray-200 disabled:opacity-40 hover:bg-gray-50 transition-colors"
        >
          <ChevronRight class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- ── Group Form Modal ── -->
    <AuthGroupFormModal
      v-if="formModal.show"
      :group="formModal.group"
      @close="formModal.show = false"
      @saved="onGroupSaved"
    />

    <!-- ── Delete Confirm ── -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="deleteModal.show" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-black/40" @click="deleteModal.show = false" />
          <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6 z-10">
            <div class="flex flex-col items-center text-center gap-3">
              <div class="w-12 h-12 rounded-full bg-red-100 flex items-center justify-center">
                <Trash2 class="w-6 h-6 text-red-500" />
              </div>
              <h3 class="font-semibold text-gray-800">Hapus Group?</h3>
              <p class="text-sm text-gray-500">
                Group <span class="font-medium text-gray-700">{{ deleteModal.target?.group_name }}</span> 
                akan dihapus permanen beserta semua function assignment-nya.
              </p>
            </div>
            <div class="flex gap-2 mt-5">
              <button @click="deleteModal.show = false" class="btn-secondary flex-1 text-sm">Batal</button>
              <button 
                @click="handleDelete"
                :disabled="isDeleting"
                class="flex-1 text-sm py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg font-medium flex items-center justify-center gap-1.5"
              >
                <Loader2 v-if="isDeleting" class="w-3.5 h-3.5 animate-spin" />
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
import { useRbacStore } from '../../stores/rbac.js'
import { usePermission } from '../../composables/usePermission.js'
import Panel from '../../components/Panel.vue'
import AuthGroupFormModal from '../../components/rbac/AuthGroupFormModal.vue'
import {
  Search, Plus, Pencil, Trash2, Loader2,
  ShieldOff, ChevronLeft, ChevronRight,
} from 'lucide-vue-next'

const { canCreate, canUpdate, canDelete } = usePermission('SETTINGS-USER-AUTHORIZATION-GROUP')

const rbacStore = useRbacStore()

// Search & filter
const search       = ref('')
const filterStatus = ref('')
let   searchTimer  = null

function onSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => loadGroups(), 400)
}

// Pagination
const pagination = computed(() => rbacStore.pagination)

function changePage(page) {
  loadGroups(page)
}

function loadGroups(page = 1) {
  const params = { page }
  if (search.value)       params.search = search.value
  if (filterStatus.value) params.status = filterStatus.value
  rbacStore.fetchGroups(params)
}

// Form modal
const formModal = reactive({ show: false, group: null })

function openForm(group) {
  formModal.group = group
  formModal.show  = true
}

function onGroupSaved() {
  formModal.show = false
  loadGroups()
}

// Delete
const deleteModal = reactive({ show: false, target: null })
const isDeleting  = ref(false)

function confirmDelete(group) {
  deleteModal.target = group
  deleteModal.show   = true
}

async function handleDelete() {
  isDeleting.value = true
  try {
    await rbacStore.deleteGroup(deleteModal.target.id)
    deleteModal.show = false
    loadGroups()
  } catch (err) {
    console.error(err)
  } finally {
    isDeleting.value = false
  }
}

onMounted(() => loadGroups())
</script>

<style scoped>
@reference "../../style.css";

.btn-primary  { @apply px-4 py-2 bg-bfs-gold hover:bg-bfs-gold-dark text-white font-medium rounded-lg transition-colors; }
.btn-secondary { @apply px-4 py-2 border border-gray-200 text-gray-600 hover:bg-gray-50 rounded-lg transition-colors; }
.badge-active   { @apply text-xs px-2 py-0.5 rounded-full bg-green-100 text-green-700 font-medium; }
.badge-inactive { @apply text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-500 font-medium; }
.modal-enter-active, .modal-leave-active { transition: opacity 0.2s; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
</style>