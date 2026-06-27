<template>
  <Panel title="GRN-SES Document" subtitle="Purchase | Good Receipt Note | GRN-SES Document">

    <!-- Toolbar -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
      <div class="flex items-center gap-2">
        <select v-model="searchField" class="pl-2 pr-8 py-1.5 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-bfs-gold/40">
          <option value="document_name">Document Name</option>
          <option value="type">Type</option>
        </select>
        <div class="relative">
          <Search class="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-400" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search..."
            class="pl-8 pr-3 py-1.5 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-bfs-gold/40 focus:border-bfs-gold w-56"
          />
        </div>
      </div>
      <div class="flex items-center gap-2">
        <button
          v-if="canCreate"
          @click="openAddModal"
          class="btn-primary text-xs flex items-center gap-1.5"
        >
          <Plus class="w-3.5 h-3.5" /> New Document
        </button>
      </div>
    </div>

    <!-- Table -->
    <div class="overflow-x-auto rounded-xl border border-gray-200 bg-white">
      <table class="w-full text-sm text-left text-gray-600">
        <thead class="text-xs text-gray-700 uppercase bg-gray-50 border-b border-gray-200">
          <tr>
            <th class="px-4 py-3 text-center w-16">No.</th>
            <th class="px-4 py-3">Document Name</th>
            <th class="px-4 py-3 text-center w-32">Is Active</th>
            <th class="px-4 py-3 text-center w-32">Type</th>
            <th class="px-4 py-3 text-center w-24">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="store.loading">
            <td colspan="5" class="px-4 py-8 text-center text-gray-500">
              <Loader2 class="w-6 h-6 animate-spin mx-auto text-bfs-gold mb-2" />
              Loading data...
            </td>
          </tr>
          <tr v-else-if="filteredDocs.length === 0">
            <td colspan="5" class="px-4 py-8 text-center text-gray-500">
              Tidak ada dokumen GRN/SES.
            </td>
          </tr>
          <tr
            v-for="(doc, idx) in filteredDocs"
            :key="doc.id"
            class="border-b border-gray-100 hover:bg-yellow-50/30 transition-colors"
          >
            <td class="px-4 py-3 text-center text-gray-500 font-mono">{{ idx + 1 }}.</td>
            <td class="px-4 py-3 font-medium text-gray-800">{{ doc.document_name }}</td>
            <td class="px-4 py-3 text-center">
              <span v-if="doc.is_active" class="text-green-500 font-bold text-lg">✓</span>
              <span v-else class="text-red-500 font-bold text-lg">✗</span>
            </td>
            <td class="px-4 py-3 text-center font-semibold">{{ doc.type }}</td>
            <td class="px-4 py-3 text-center">
              <div class="flex items-center justify-center gap-2">
                <button
                  v-if="canUpdate"
                  @click="openEditModal(doc)"
                  class="p-1.5 text-gray-400 hover:text-bfs-gold hover:bg-yellow-50 rounded-lg transition-colors"
                  title="Edit"
                >
                  <Pencil class="w-4 h-4" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <GrnSesDocumentFormModal
      :is-open="isModalOpen"
      :mode="modalMode"
      :edit-id="editId"
      :initial-data="editData"
      @close="closeModal"
    />

  </Panel>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import Panel from '../../components/Panel.vue'
import GrnSesDocumentFormModal from '../../components/purchase/GrnSesDocumentFormModal.vue'
import { Plus, Search, Loader2, Pencil } from 'lucide-vue-next'
import Swal from 'sweetalert2'
import { useGrnSesDocumentStore } from '../../stores/grnSesDocument'
import { usePermission } from '../../composables/usePermission.js'

const { canCreate, canUpdate } = usePermission('PURCHASES-GRNSES-DOCUMENT')

const store = useGrnSesDocumentStore()

const searchField = ref('document_name')
const searchQuery = ref('')

const filteredDocs = computed(() => {
  if (!searchQuery.value) return store.documents
  const q = searchQuery.value.toLowerCase()
  return store.documents.filter(d => {
    if (searchField.value === 'document_name') return d.document_name.toLowerCase().includes(q)
    if (searchField.value === 'type') return d.type.toLowerCase().includes(q)
    return true
  })
})

const isModalOpen = ref(false)
const modalMode = ref('add')
const editId = ref(null)
const editData = ref(null)

onMounted(() => {
  store.fetchDocuments()
})

function openAddModal() {
  modalMode.value = 'add'
  editId.value = null
  editData.value = null
  isModalOpen.value = true
}

function openEditModal(doc) {
  modalMode.value = 'edit'
  editId.value = doc.id
  editData.value = { ...doc }
  isModalOpen.value = true
}

function closeModal() {
  isModalOpen.value = false
}
</script>
