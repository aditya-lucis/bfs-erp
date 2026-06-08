/**
 * useToast — simple toast notification tanpa library eksternal.
 * Usage:
 *   const toast = useToast()
 *   toast.success('Data berhasil disimpan.')
 *   toast.error('Terjadi kesalahan.')
 */
import { ref } from 'vue'

const toasts = ref([])
let counter = 0

function addToast(message, type = 'success', duration = 3500) {
  const id = ++counter
  toasts.value.push({ id, message, type })
  setTimeout(() => {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }, duration)
}

export function useToast() {
  return {
    success: (msg) => addToast(msg, 'success'),
    error:   (msg) => addToast(msg, 'error'),
    info:    (msg) => addToast(msg, 'info'),
    toasts,
  }
}