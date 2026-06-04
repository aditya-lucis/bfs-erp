import { computed } from 'vue'
import { useMenuStore } from '../stores/menu.js'
import { useAuthStore } from '../stores/auth.js'

export function usePermission(functionCode) {
  const menuStore = useMenuStore()
  const authStore = useAuthStore()

  const su = computed(() => authStore.isSuperuser)

  const canRead    = computed(() => su.value || menuStore.can(functionCode, 'can_read'))
  const canCreate  = computed(() => su.value || menuStore.can(functionCode, 'can_create'))
  const canUpdate  = computed(() => su.value || menuStore.can(functionCode, 'can_update'))
  const canDelete  = computed(() => su.value || menuStore.can(functionCode, 'can_delete'))
  const canApprove = computed(() => su.value || menuStore.can(functionCode, 'can_approve'))
  const canPrint   = computed(() => su.value || menuStore.can(functionCode, 'can_print'))
  const canExport  = computed(() => su.value || menuStore.can(functionCode, 'can_export'))

  return { canRead, canCreate, canUpdate, canDelete, canApprove, canPrint, canExport }
}