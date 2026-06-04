<template>
  <Teleport to="body">
    <Transition name="modal">
      <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="$emit('close')" />

        <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-md z-10 overflow-hidden">

          <!-- ── Header ── -->
          <div class="bg-bfs-navy px-6 py-4 flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div class="w-9 h-9 rounded-xl bg-bfs-gold/20 flex items-center justify-center">
                <ShieldCheck class="w-5 h-5 text-bfs-gold" />
              </div>
              <div>
                <h3 class="text-sm font-semibold text-white">
                  {{ isEdit ? 'Edit Authorization Group' : 'Add Authorization Group' }}
                </h3>
                <p class="text-[11px] text-white/50 mt-0.5">
                  Function Authorization | User Authorization Group
                </p>
              </div>
            </div>
            <button
              @click="$emit('close')"
              class="w-7 h-7 rounded-lg flex items-center justify-center text-white/50 hover:text-white hover:bg-white/10 transition-colors"
            >
              <X class="w-4 h-4" />
            </button>
          </div>

          <!-- ── Form Body ── -->
          <div class="px-6 py-5 space-y-4">

            <!-- Group Name -->
            <div>
              <label class="block text-[11px] font-semibold text-gray-500 tracking-widest uppercase mb-1.5">
                Group Name <span class="text-red-400">*</span>
              </label>
              <input
                v-model="form.group_name"
                type="text"
                class="form-input font-mono tracking-wider uppercase"
                placeholder="e.g. ACC-ACCMGR"
                :class="errors.group_name ? 'border-red-300 focus:ring-red-200 focus:border-red-400' : ''"
              />
              <p v-if="errors.group_name" class="mt-1.5 text-xs text-red-500 flex items-center gap-1">
                <AlertCircle class="w-3.5 h-3.5" />{{ errors.group_name }}
              </p>
            </div>

            <!-- Description -->
            <div>
              <label class="block text-[11px] font-semibold text-gray-500 tracking-widest uppercase mb-1.5">
                Description
              </label>
              <input
                v-model="form.description"
                type="text"
                class="form-input"
                placeholder="e.g. ACCOUNTING MANAGER"
              />
            </div>

            <!-- Status toggle -->
            <div class="flex items-center justify-between p-3 bg-gray-50 rounded-xl border border-gray-100">
              <div class="flex items-center gap-2.5">
                <div :class="form.status ? 'bg-green-100' : 'bg-gray-100'"
                  class="w-8 h-8 rounded-lg flex items-center justify-center transition-colors">
                  <CheckCircle :class="form.status ? 'text-green-600' : 'text-gray-400'"
                    class="w-4 h-4 transition-colors" />
                </div>
                <div>
                  <p class="text-sm font-medium text-gray-800">Status</p>
                  <p class="text-xs text-gray-400">{{ form.status ? 'Group aktif dan bisa digunakan' : 'Group tidak aktif' }}</p>
                </div>
              </div>
              <!-- Toggle switch -->
              <button
                type="button"
                @click="form.status = !form.status"
                :class="form.status ? 'bg-bfs-gold' : 'bg-gray-200'"
                class="relative w-11 h-6 rounded-full transition-colors duration-200 focus:outline-none"
              >
                <span
                  :class="form.status ? 'translate-x-5' : 'translate-x-0.5'"
                  class="inline-block w-5 h-5 bg-white rounded-full shadow transition-transform duration-200"
                />
              </button>
            </div>

            <!-- Server error -->
            <div v-if="serverError"
              class="p-3 bg-red-50 border border-red-200 text-red-600 rounded-xl text-xs flex items-center gap-2">
              <AlertCircle class="w-4 h-4 flex-shrink-0" />
              {{ serverError }}
            </div>

            <p class="text-xs text-gray-400">*) Required</p>

          </div>

          <!-- ── Action Buttons ── -->
          <div class="px-6 pb-5 space-y-3">

            <!-- Primary actions -->
            <div class="grid grid-cols-3 gap-2" v-if="isEdit">
              <button
                @click="handleSubmit"
                :disabled="isSaving"
                class="flex items-center justify-center gap-1.5 py-2.5 bg-bfs-gold hover:bg-bfs-gold-dark text-white text-sm font-medium rounded-xl transition-colors disabled:opacity-60"
              >
                <Loader2 v-if="isSaving" class="w-3.5 h-3.5 animate-spin" />
                <Save v-else class="w-3.5 h-3.5" />
                Update
              </button>

              <button
                @click="goToFunctionAssign"
                type="button"
                class="flex items-center justify-center gap-1.5 py-2.5 bg-bfs-navy/5 hover:bg-bfs-navy/10 text-bfs-navy text-sm font-medium rounded-xl border border-bfs-navy/10 transition-colors"
              >
                <ShieldCheck class="w-3.5 h-3.5" />
                Functions
              </button>

              <button
                @click="goToUserAssign"
                type="button"
                class="flex items-center justify-center gap-1.5 py-2.5 bg-bfs-navy/5 hover:bg-bfs-navy/10 text-bfs-navy text-sm font-medium rounded-xl border border-bfs-navy/10 transition-colors"
              >
                <Users class="w-3.5 h-3.5" />
                Members
              </button>
            </div>

            <!-- Save button kalau new -->
            <button
              v-else
              @click="handleSubmit"
              :disabled="isSaving"
              class="w-full flex items-center justify-center gap-1.5 py-2.5 bg-bfs-gold hover:bg-bfs-gold-dark text-white text-sm font-medium rounded-xl transition-colors disabled:opacity-60"
            >
              <Loader2 v-if="isSaving" class="w-3.5 h-3.5 animate-spin" />
              <Save v-else class="w-3.5 h-3.5" />
              Save Group
            </button>

            <!-- Secondary actions -->
            <div class="flex gap-2">
              <button
                type="button"
                @click="$emit('close')"
                class="flex-1 py-2.5 border border-gray-200 text-gray-600 hover:bg-gray-50 text-sm rounded-xl transition-colors"
              >
                Cancel
              </button>
              <button
                v-if="isEdit"
                type="button"
                @click="$emit('delete', props.group); $emit('close')"
                class="flex-1 py-2.5 bg-red-50 hover:bg-red-100 text-red-600 text-sm font-medium rounded-xl border border-red-100 transition-colors flex items-center justify-center gap-1.5"
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

  <!-- Sub-modals -->
  <FunctionAssignModal
    v-if="showFunctionAssign"
    :group="props.group"
    @close="showFunctionAssign = false"
  />
  <UserAssignModal
    v-if="showUserAssign"
    :group="props.group"
    @close="showUserAssign = false"
  />
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRbacStore } from '../../stores/rbac.js'
import FunctionAssignModal from './FunctionAssignModal.vue'
import UserAssignModal from './UserAssignModal.vue'
import {
  X, Save, Loader2, Trash2, ShieldCheck,
  Users, AlertCircle, CheckCircle,
} from 'lucide-vue-next'

const props = defineProps({ group: { type: Object, default: null } })
const emit  = defineEmits(['close', 'saved', 'delete'])

const rbacStore  = useRbacStore()
const isSaving   = ref(false)
const serverError = ref('')
const isEdit     = computed(() => !!props.group)

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
  isSaving.value    = true
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

const goToFunctionAssign = () => { showFunctionAssign.value = true }
const goToUserAssign     = () => { showUserAssign.value     = true }
</script>

<style scoped>
@reference "../../style.css";
.form-input {
  @apply w-full px-3.5 py-2.5 text-sm border border-gray-200 rounded-xl
         focus:outline-none focus:ring-2 focus:ring-bfs-gold/30 focus:border-bfs-gold
         transition-all bg-white placeholder-gray-300;
}
.modal-enter-active, .modal-leave-active { transition: opacity 0.2s; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
</style>