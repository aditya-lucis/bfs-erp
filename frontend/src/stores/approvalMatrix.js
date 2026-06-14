import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../services/api.js'

export const useApprovalMatrixStore = defineStore('approvalMatrix', () => {
  const matrices = ref([])
  const currentMatrix = ref(null)
  const documentTypes = ref([])
  const approvalRoles = ref([])
  const isLoading = ref(false)
  const error = ref(null)

  async function fetchDocumentTypes() {
    const res = await api.get('/approval/document-types/')
    documentTypes.value = res.data
    return res.data
  }

  async function fetchApprovalRoles() {
    const res = await api.get('/approval/roles/')
    approvalRoles.value = res.data
    return res.data
  }

  async function fetchMatrices(filters = {}) {
    isLoading.value = true
    error.value = null
    try {
      const res = await api.get('/approval/matrix/', { params: filters })
      matrices.value = res.data.results ?? res.data
      return matrices.value
    } catch (err) {
      error.value = 'Gagal memuat matrix approval.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function lookupMatrix(documentCode, creatorPositionId) {
    const res = await api.get('/approval/matrix/lookup/', {
      params: {
        document_code: documentCode,
        creator_position: creatorPositionId,
      },
    })
    currentMatrix.value = res.data
    return res.data
  }

  async function saveMatrix(payload) {
    isLoading.value = true
    error.value = null
    try {
      const res = await api.post('/approval/matrix/', payload)
      currentMatrix.value = res.data
      return res.data
    } catch (err) {
      error.value = err.response?.data || 'Gagal menyimpan matrix approval.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function deleteMatrix(id) {
    await api.delete(`/approval/matrix/${id}/`)
    matrices.value = matrices.value.filter(m => m.id !== id)
    if (currentMatrix.value?.id === id) {
      currentMatrix.value = null
    }
  }

  async function resolveApproval(payload) {
    const res = await api.post('/approval/resolve/', payload)
    return res.data
  }

  return {
    matrices,
    currentMatrix,
    documentTypes,
    approvalRoles,
    isLoading,
    error,
    fetchDocumentTypes,
    fetchApprovalRoles,
    fetchMatrices,
    lookupMatrix,
    saveMatrix,
    deleteMatrix,
    resolveApproval,
  }
})
