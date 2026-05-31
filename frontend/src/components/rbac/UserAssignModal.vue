<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-[60] flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/50" />
      <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-lg z-10 flex flex-col max-h-[80vh]">

        <!-- Header -->
        <div class="px-6 py-4 border-b border-gray-100 flex-shrink-0 flex items-center justify-between">
          <div>
            <h3 class="text-base font-semibold text-gray-800">User Authorization Group</h3>
            <p class="text-xs text-gray-400 mt-0.5">
              Group: <span class="font-medium text-bfs-navy">{{ group.group_name }}</span>
            </p>
          </div>
          <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600">
            <X class="w-5 h-5" />
          </button>
        </div>

        <!-- Member list -->
        <div class="flex-1 overflow-y-auto px-6 py-4">
          <div v-if="isLoading" class="flex justify-center py-10">
            <Loader2 class="w-6 h-6 animate-spin text-bfs-gold" />
          </div>
          <template v-else>
            <div class="flex items-center justify-between mb-3">
              <p class="text-sm font-medium text-gray-700">
                Members <span class="text-gray-400">({{ members.length }})</span>
              </p>
              <button @click="showAddUser = true" class="text-xs text-bfs-gold hover:underline flex items-center gap-1">
                <UserPlus class="w-3.5 h-3.5" /> Add User
              </button>
            </div>

            <div v-if="members.length" class="space-y-2">
              <div
                v-for="member in members"
                :key="member.id"
                class="flex items-center justify-between p-3 bg-gray-50 rounded-xl group"
              >
                <div class="flex items-center gap-3">
                  <div class="w-8 h-8 rounded-full bg-bfs-navy/10 flex items-center justify-center">
                    <User class="w-4 h-4 text-bfs-navy" />
                  </div>
                  <div>
                    <p class="text-sm font-medium text-gray-800">{{ member.full_name }}</p>
                    <p class="text-xs text-gray-400">@{{ member.username }}</p>
                  </div>
                </div>
                <button
                  @click="removeMember(member)"
                  class="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg opacity-0 group-hover:opacity-100 transition-all"
                >
                  <UserMinus class="w-3.5 h-3.5" />
                </button>
              </div>
            </div>

            <div v-else class="flex flex-col items-center py-10 text-gray-400">
              <Users class="w-8 h-8 mb-2" />
              <p class="text-sm">Belum ada member.</p>
            </div>
          </template>
        </div>

        <!-- Footer -->
        <div class="px-6 py-4 border-t border-gray-100 flex-shrink-0 flex justify-end">
          <button @click="$emit('close')" class="btn-secondary text-sm">Close</button>
        </div>

      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRbacStore } from '../../stores/rbac.js'
import { X, Loader2, User, UserPlus, UserMinus, Users } from 'lucide-vue-next'

const props = defineProps({ group: { type: Object, required: true } })
defineEmits(['close'])

const rbacStore  = useRbacStore()
const isLoading  = ref(true)
const members    = ref([])
const showAddUser = ref(false)

onMounted(async () => {
  isLoading.value = true
  try {
    const data = await rbacStore.fetchGroupUsers(props.group.id)
    members.value = data
  } finally {
    isLoading.value = false
  }
})

async function removeMember(member) {
  await rbacStore.removeUserFromGroup(props.group.id, member.user)
  members.value = members.value.filter(m => m.id !== member.id)
}
</script>

<style scoped>
@reference "../../style.css";

.btn-secondary { @apply px-4 py-2 border border-gray-200 text-gray-600 hover:bg-gray-50 rounded-lg transition-colors; }
</style>