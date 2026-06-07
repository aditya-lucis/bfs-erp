/**
 * useFormError — composable untuk handle error form secara konsisten.
 *
 * Usage:
 *   const { serverError, fieldErrors, setErrors, clearErrors, parseApiError } = useFormError()
 *
 * Di modal: expose { setErrors } ke parent via defineExpose.
 * Di view: catch error dari API, panggil modalRef.value.setErrors(err)
 */
import { ref, reactive } from 'vue'

export function useFormError() {
  const serverError = ref('')
  const fieldErrors = reactive({})

  function clearErrors() {
    serverError.value = ''
    Object.keys(fieldErrors).forEach(k => delete fieldErrors[k])
  }

  /**
   * Parse error dari Axios response dan populate serverError + fieldErrors.
   * Bisa dipanggil dari view (lempar ke modal) atau dari modal langsung.
   */
  function parseApiError(err) {
    clearErrors()
    const data = err?.response?.data

    if (!data) {
      serverError.value = 'Terjadi kesalahan server. Silakan coba lagi.'
      return
    }

    if (typeof data === 'object' && !Array.isArray(data)) {
      let hasFieldError = false
      for (const [field, messages] of Object.entries(data)) {
        const msg = Array.isArray(messages) ? messages[0] : String(messages)
        if (field === 'non_field_errors' || field === 'detail') {
          serverError.value = msg
        } else {
          fieldErrors[field] = msg
          hasFieldError = true
        }
      }
      if (hasFieldError && !serverError.value) {
        serverError.value = 'Periksa kembali isian form.'
      }
    } else {
      serverError.value = String(data)
    }
  }

  /**
   * Dipanggil dari view via modalRef.value.setErrors(err)
   */
  function setErrors(err) {
    parseApiError(err)
  }

  return { serverError, fieldErrors, clearErrors, parseApiError, setErrors }
}