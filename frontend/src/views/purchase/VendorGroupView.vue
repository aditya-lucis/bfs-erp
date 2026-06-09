<template>
  <Panel title="Vendor Group" icon="Table">

    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
      <div class="relative">
        <Search class="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-400" />
        <input
          v-model="search"
          type="text"
          placeholder="Cari group..."
          class="pl-8 pr-3 py-1.5 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-bfs-gold/40 w-56"
        />
      </div>
      <button v-if="canCreate" @click="openAdd" class="btn-primary text-xs flex items-center gap-1.5">
        <Plus class="w-3.5 h-3.5" /> Add Group
      </button>
    </div>

    <div v-if="store.loading" class="flex justify-center py-16">
      <Loader2 class="w-6 h-6 animate-spin text-bfs-gold" />
    </div>

    <div v-else-if="filtered.length" class="border border-gray-200 rounded-xl overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 border-b border-gray-200">
          <tr>
            <th class="text-left px-4 py-2.5 text-[11px] font-semibold text-gray-500 uppercase w-12">No</th>
            <th class="text-left px-4 py-2.5 text-[11px] font-semibold text-gray-500 uppercase">Group Name</th>
            <th class="px-4 py-2.5 text-right text-[11px] font-semibold text-gray-500 uppercase w-28">Action</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="(row, i) in filtered" :key="row.id" class="hover:bg-gray-50/80">
            <td class="px-4 py-2.5 text-gray-500">{{ i + 1 }}</td>
            <td class="px-4 py-2.5 font-medium text-gray-800">{{ row.name }}</td>
            <td class="px-4 py-2.5 text-right">
              <div class="flex justify-end gap-1">
                <button v-if="canUpdate" @click="openEdit(row)" class="p-1.5 text-gray-400 hover:text-bfs-gold rounded" title="Edit">
                  <Pencil class="w-3.5 h-3.5" />
                </button>
                <button v-if="canDelete" @click="confirmDelete(row)" class="p-1.5 text-gray-400 hover:text-red-500 rounded" title="Hapus">
                  <Trash2 class="w-3.5 h-3.5" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-else class="flex flex-col items-center py-20 text-gray-400">
      <Users class="w-10 h-10 mb-3" />
      <p class="text-sm">Belum ada vendor group.</p>
    </div>

    <!-- Form Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="modal.show" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-black/45" @click="modal.show = false" />
          <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-sm z-10" @click.stop>
            <div class="flex items-center justify-between px-6 py-4 border-b">
              <h3 class="font-semibold text-gray-800">{{ modal.mode === 'add' ? 'Add Vendor Group' : 'Edit Vendor Group' }}</h3>
              <button @click="modal.show = false"><X class="w-5 h-5 text-gray-400" /></button>
            </div>
            <div class="px-6 py-4">
              <FormField label="Group Name" required :error="formError.fieldErrors.name">
                <input v-model="form.name" class="form-input" :class="{ 'border-red-300': formError.fieldErrors.name }" />
              </FormField>
            </div>
            <div class="flex justify-end gap-2 px-6 py-4 border-t bg-gray-50 rounded-b-2xl">
              <button @click="modal.show = false" class="btn-secondary text-sm">Cancel</button>
              <button @click="handleSubmit" :disabled="isSaving" class="btn-primary text-sm flex items-center gap-1.5">
                <Loader2 v-if="isSaving" class="w-3.5 h-3.5 animate-spin" />
                <Save v-else class="w-3.5 h-3.5" />
                Save
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
import Swal from 'sweetalert2'
import { Plus, Pencil, Trash2, Save, X, Loader2, Search, Users } from 'lucide-vue-next'
import { usePurchaseStore } from '../../stores/purchase.js'
import { usePermission } from '../../composables/usePermission.js'
import { useFormError } from '../../composables/useFormError.js'
import { useToast } from '../../composables/useToast.js'
import Panel from '../../components/Panel.vue'
import FormField from '../../components/FormField.vue'

const store = usePurchaseStore()
const { canCreate, canUpdate, canDelete } = usePermission('PURCHASES-VENDOR-GROUP')
const formError = useFormError()
const toast = useToast()
const isSaving = ref(false)
const search = ref('')

const filtered = computed(() => {
  if (!search.value.trim()) return store.groups
  const q = search.value.toLowerCase()
  return store.groups.filter(g => g.name.toLowerCase().includes(q))
})

const modal = reactive({ show: false, mode: 'add', editId: null })
const form = reactive({ name: '' })

function openAdd() {
  modal.show = true; modal.mode = 'add'; modal.editId = null
  form.name = ''; formError.clearErrors()
}

function openEdit(row) {
  modal.show = true; modal.mode = 'edit'; modal.editId = row.id
  form.name = row.name; formError.clearErrors()
}

async function handleSubmit() {
  formError.clearErrors()
  if (!form.name.trim()) {
    formError.fieldErrors.name = 'Nama group wajib diisi.'
    return
  }
  isSaving.value = true
  try {
    if (modal.mode === 'add') {
      await store.createGroup({ name: form.name })
    } else {
      await store.updateGroup(modal.editId, { name: form.name })
    }
    modal.show = false
    toast.success('Group berhasil disimpan.')
    await store.fetchGroups()
  } catch (err) {
    formError.parseApiError(err)
    toast.error('Gagal menyimpan group.')
  } finally {
    isSaving.value = false
  }
}

async function confirmDelete(row) {
  const result = await Swal.fire({
    title: `Hapus "${row.name}"?`,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonText: 'Hapus',
    cancelButtonText: 'Batal',
  })
  if (!result.isConfirmed) return
  try {
    await store.deleteGroup(row.id)
    toast.success('Group berhasil dihapus.')
    await store.fetchGroups()
  } catch {
    toast.error('Gagal menghapus. Group mungkin masih dipakai vendor.')
  }
}

onMounted(() => store.fetchGroups())
</script>

<style scoped>
@reference "../../style.css";
.form-input { @apply w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-bfs-gold/40 bg-white; }
.btn-primary { @apply px-4 py-2 bg-bfs-gold hover:bg-bfs-gold-dark text-white font-medium rounded-lg disabled:opacity-60; }
.btn-secondary { @apply px-4 py-2 border border-gray-200 text-gray-600 hover:bg-gray-50 rounded-lg; }
.modal-enter-active, .modal-leave-active { transition: opacity 0.2s; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
</style>
