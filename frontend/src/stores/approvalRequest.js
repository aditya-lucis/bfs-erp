import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../services/api.js'

export const useApprovalRequestStore = defineStore('approvalRequest', () => {
  const requests = ref([])
  const currentRequest = ref(null)
  const signatures = ref([])
  const isLoading = ref(false)
  const error = ref(null)

  async function fetchRequests(filters = {}) {
    isLoading.value = true
    error.value = null
    try {
      const res = await api.get('/approval/requests/', { params: filters })
      requests.value = res.data.results ?? res.data
      return requests.value
    } catch (err) {
      error.value = err.response?.data?.detail || 'Gagal memuat request approval.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function fetchRequestDetail(id) {
    isLoading.value = true
    error.value = null
    try {
      const res = await api.get(`/approval/requests/${id}/`)
      currentRequest.value = res.data
      return res.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Gagal memuat detail request approval.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function approveRequest(id, remarks = '') {
    isLoading.value = true
    error.value = null
    try {
      const res = await api.post(`/approval/requests/${id}/approve/`, { remarks })
      // Update local request if cached
      if (currentRequest.value?.id === id) {
        currentRequest.value = res.data
      }
      requests.value = requests.value.map(r => r.id === id ? res.data : r)
      return res.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Gagal menyetujui request approval.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function rejectRequest(id, remarks) {
    isLoading.value = true
    error.value = null
    try {
      const res = await api.post(`/approval/requests/${id}/reject/`, { remarks })
      if (currentRequest.value?.id === id) {
        currentRequest.value = res.data
      }
      requests.value = requests.value.map(r => r.id === id ? res.data : r)
      return res.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Gagal menolak request approval.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function reviseRequest(id, remarks) {
    isLoading.value = true
    error.value = null
    try {
      const res = await api.post(`/approval/requests/${id}/revise/`, { remarks })
      if (currentRequest.value?.id === id) {
        currentRequest.value = res.data
      }
      requests.value = requests.value.map(r => r.id === id ? res.data : r)
      return res.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Gagal meminta revisi request approval.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function fetchSignatures(documentCode, documentId) {
    isLoading.value = true
    error.value = null
    try {
      const res = await api.get('/approval/signatures/', {
        params: {
          document_code: documentCode,
          document_id: documentId
        }
      })
      signatures.value = res.data
      return res.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Gagal memuat tanda tangan dokumen.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function submitApprovalRequest(payload) {
    isLoading.value = true
    error.value = null
    try {
      const res = await api.post('/approval/requests/', payload)
      return res.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Gagal mengirim request approval.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return {
    requests,
    currentRequest,
    signatures,
    isLoading,
    error,
    fetchRequests,
    fetchRequestDetail,
    approveRequest,
    rejectRequest,
    reviseRequest,
    fetchSignatures,
    submitApprovalRequest,
  }
})
