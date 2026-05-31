<template>
  <Teleport to="body">
    <Transition name="modal">
      <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/40" @click="$emit('close')" />

        <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-lg z-10 overflow-hidden">

          <!-- Header -->
          <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
            <div>
              <h3 class="text-base font-semibold text-gray-800">
                {{ isEdit ? 'Edit Authorization Group' : 'Add Authorization Group' }}
              </h3>
              <p class="text-xs text-gray-400 mt-0.5">Function Authorization | User Authorization Group</p>
            </div>
            <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600 transition-colors">
              <X class="w-5 h-5" />
            </button>
          </div>

          <!-- Form -->
          <form @submit.prevent="handleSubmit" class="px-6 py-5 space-y-4">

            <FormField label="Group Name" required>
              <input
                v-model="form.group_name"
                type="text"
                class="form-input font-mono uppercase"
                placeholder="e.g. ACC-ACCMGR"
                :class="{ 'border-red-300 focus:ring-red-200': errors.group_name }"
              />
              <p v-if="errors.group_name" class="mt-1 text-xs text-red-500">{{ errors.group_name }}</p>
            </FormField>

            <FormField label="Description">
              <input
                v-model="form.description"
                type="text"
                class="form-input"
                placeholder="e.g. ACCOUNTING MANAGER"
              />
            </FormField>

            <div class="flex items-center gap-3">
              <input
                v-model="form.status"
                type="checkbox"
                id="grp_status"
                class="w-4 h-4 rounded border-gray-300 text-bfs-gold focus:ring-bfs-gold"
              />
              <label for="grp_status" class="text-sm text-gray-700 font-medium">Active</label>
            </div>

            <!-- Error umum -->
            <div v-if="serverError" class="p-3 bg-red-50 border border-red-200 text-red-600 rounded-lg text-xs flex items-center gap-2">
              <AlertCircle class="w-4 h-4 flex-shrink-0" />
              {{ serverError }}
            </div>

            <!-- Required note -->
            <p class="text-xs text-gray-400">*) Required</p>

          </form>

          <!-- Footer buttons — sama persis seperti screenshot 2 -->
          <div class="px-6 py-4 border-t border-gray-100 flex items-center justify-between">
            <div class="flex gap-2">
              <button
                @click="handleSubmit"
                :disabled="isSaving"
                class="btn-primary text-sm flex items-center gap-1.5"
              >
                <Loader2 v-if="isSaving" class="w-3.5 h-3.5 animate-spin" />
                <Save v-else class="w-3.5 h-3.5" />
                {{ isEdit ? 'Update' : 'Save' }}
              </button>

              <!-- Tombol Admin Group → ke function assignment -->
              <button
                v-if="isEdit"
                @click="goToFunctionAssign"
                type="button"
                class="btn-secondary text-sm flex items-center gap-1.5"
              >
                <ShieldCheck class="w-3.5 h-3.5" />
                Admin Group
              </button>

              <!-- User Authorization Group → manage users -->
              <button
                v-if="isEdit"
                @click="goToUserAssign"
                type="button"
                class="btn-secondary text-sm flex items-center gap-1.5"
              >
                <Users class="w-3.5 h-3.5" />
                User Authorization Group
              </button>
            </div>

            <div class="flex gap-2">
              <button type="button" @click="$emit('close')" class="btn-secondary text-sm">
                Cancel
              </button>
              <button
                v-if="isEdit"
                type="button"
                @click="confirmDelete"
                class="text-sm px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg font-medium transition-colors flex items-center gap-1.5"
              >
                <Trash2 class="w-3.5 h-3.5" />
                Delete
              </button>
            </div>
          </div>

        </div>
      </div>
    </Transition>
  </Teleport>

  <!-- Function Assignment Modal -->
  <FunctionAssignModal
    v-if="showFunctionAssign"
    :group="props.group"
    @close="showFunctionAssign = false"
  />

  <!-- User Assign Modal -->
  <UserAssignModal
    v-if="showUserAssign"
    :group="props.group"
    @close="showUserAssign = false"
  />
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRbacStore } from '../../stores/rbac.js'
import FormField from '../FormField.vue'
import FunctionAssignModal from './FunctionAssignModal.vue'
import UserAssignModal from './UserAssignModal.vue'
import {
  X, Save, Loader2, Trash2,
  ShieldCheck, Users, AlertCircle,
} from 'lucide-vue-next'

const props  = defineProps({ group: { type: Object, default: null } })
const emit   = defineEmits(['close', 'saved', 'delete'])

const rbacStore = useRbacStore()
const isSaving  = ref(false)
const serverError = ref('')
const isEdit    = computed(() => !!props.group)

const showFunctionAssign = ref(false)
const showUserAssign     = ref(false)

const form = reactive({
  group_name:  props.group?.group_name  || '',
  description: props.group?.description || '',
  status:      props.group?.status      ?? true,
})

const errors = reactive({ group_name: '' })

function validate() {
  errors.group_name = ''
  if (!form.group_name.trim()) {
    errors.group_name = 'Group name wajib diisi.'
    return false
  }
  return true
}

async function handleSubmit() {
  if (!validate()) return
  isSaving.value   = true
  serverError.value = ''

  try {
    if (isEdit.value) {
      await rbacStore.updateGroup(props.group.id, form)
    } else {
      await rbacStore.createGroup(form)
    }
    emit('saved')
  } catch (err) {
    serverError.value = err.response?.data?.group_name?.[0]
                     || err.response?.data?.detail
                     || 'Gagal menyimpan data.'
  } finally {
    isSaving.value = false
  }
}

function goToFunctionAssign() {
  showFunctionAssign.value = true
}

function goToUserAssign() {
  showUserAssign.value = true
}

function confirmDelete() {
  emit('delete', props.group)
  emit('close')
}
</script>

<style scoped>
@reference "../../style.css";

.form-input  { @apply w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-bfs-gold/40 focus:border-bfs-gold transition-all bg-white; }
.btn-primary { @apply px-4 py-2 bg-bfs-gold hover:bg-bfs-gold-dark text-white font-medium rounded-lg transition-colors disabled:opacity-60; }
.btn-secondary { @apply px-4 py-2 border border-gray-200 text-gray-600 hover:bg-gray-50 rounded-lg transition-colors; }
.modal-enter-active, .modal-leave-active { transition: opacity 0.2s; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
</style>