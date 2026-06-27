<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
    <div class="bg-white rounded-xl shadow-xl w-full max-w-lg overflow-hidden flex flex-col">
      <!-- Header -->
      <div class="px-5 py-4 border-b border-gray-100 flex items-center justify-between bg-gray-50/50">
        <h2 class="text-base font-semibold text-gray-800">
          Purchase | Good Receipt Note | GRN-SES Document | {{ isAdd ? 'Add' : 'Edit' }}
        </h2>
        <button @click="$emit('close')" class="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
          <X class="w-4 h-4" />
        </button>
      </div>

      <!-- Form -->
      <div class="p-5 flex-1 overflow-y-auto">
        <form @submit.prevent="save" class="space-y-4 text-sm">
          <div class="grid grid-cols-[130px_1fr] items-center gap-4">
            <label class="text-gray-600">Document Name</label>
            <input
              v-model="form.document_name"
              type="text"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded focus:ring-1 focus:ring-bfs-gold focus:border-bfs-gold"
            />
          </div>
          
          <div class="grid grid-cols-[130px_1fr] items-center gap-4">
            <label class="text-gray-600">Type</label>
            <select
              v-model="form.type"
              class="w-full px-3 py-2 border border-gray-300 rounded focus:ring-1 focus:ring-bfs-gold focus:border-bfs-gold"
            >
              <option value="GRN">GRN</option>
              <option value="SES">SES</option>
            </select>
          </div>

          <div class="grid grid-cols-[130px_1fr] items-center gap-4">
            <label class="text-gray-600">Is Active</label>
            <div class="flex items-center">
              <input
                v-model="form.is_active"
                type="checkbox"
                class="w-4 h-4 text-bfs-gold border-gray-300 rounded focus:ring-bfs-gold"
              />
            </div>
          </div>
        </form>
      </div>

      <!-- Footer -->
      <div class="px-5 py-4 border-t border-gray-100 bg-gray-50 flex justify-start gap-2">
        <button
          type="button"
          @click="save"
          class="btn-primary px-6 py-2"
          :disabled="store.loading"
        >
          Save
        </button>
        <button
          type="button"
          @click="$emit('close')"
          class="px-6 py-2 border border-gray-300 rounded bg-white text-gray-700 hover:bg-gray-50 transition-colors"
        >
          Cancel
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { X } from 'lucide-vue-next'
import Swal from 'sweetalert2'
import { useGrnSesDocumentStore } from '../../stores/grnSesDocument'

const props = defineProps({
  isOpen: Boolean,
  mode: String,
  editId: Number,
  initialData: Object
})

const emit = defineEmits(['close'])

const store = useGrnSesDocumentStore()

const isAdd = computed(() => props.mode === 'add')

const form = ref({
  document_name: '',
  type: 'GRN',
  is_active: true
})

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    if (isAdd.value) {
      form.value = {
        document_name: '',
        type: 'GRN',
        is_active: true
      }
    } else {
      form.value = { ...props.initialData }
    }
  }
})

async function save() {
  if (!form.value.document_name) {
    Swal.fire('Error', 'Document Name is required.', 'error')
    return
  }

  const payload = { ...form.value }

  try {
    if (isAdd.value) {
      await store.createDocument(payload)
    } else {
      await store.updateDocument(props.editId, payload)
    }

    if (store.error) {
      Swal.fire('Error', store.error, 'error')
    } else {
      Swal.fire({
        icon: 'success',
        title: 'Success',
        text: `Dokumen berhasil di${isAdd.value ? 'tambahkan' : 'perbarui'}.`,
        timer: 1500,
        showConfirmButton: false
      })
      emit('close')
    }
  } catch (err) {
    Swal.fire('Error', 'Terjadi kesalahan sistem.', 'error')
  }
}
</script>
