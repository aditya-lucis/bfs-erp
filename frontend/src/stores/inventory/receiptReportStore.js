import { defineStore } from 'pinia'
import api from '../../services/api'

export const useReceiptReportStore = defineStore('receiptReport', {
  state: () => ({
    receiptReports: [],
    currentReceiptReport: null,
    loading: false,
    error: null,
    pagination: {
      page: 1,
      limit: 10,
      total: 0,
      totalPages: 0
    },
    filters: {
      receipt_type: 'RR_PUR',
      po_number: '',
      date_from: '',
      date_to: ''
    }
  }),
  actions: {
    async fetchReceiptReports() {
      this.loading = true
      try {
        const { data } = await api.get('/inventory/receipt-reports/', { params: this.filters })
        this.receiptReports = data.results || data
        this.pagination.total = data.count || data.length
        this.pagination.totalPages = Math.ceil(this.pagination.total / this.pagination.limit)
      } catch (error) {
        this.error = error.response?.data?.detail || error.message
      } finally {
        this.loading = false
      }
    },
    async createReceiptReport(payload) {
      try {
        const { data } = await api.post('/inventory/receipt-reports/', payload)
        await this.fetchReceiptReports()
        return data
      } catch (error) {
        throw error.response?.data || error
      }
    },
    async submitReceiptReport(id) {
      try {
        const { data } = await api.post(`/inventory/receipt-reports/${id}/submit/`)
        await this.fetchReceiptReports()
        return data
      } catch (error) {
        throw error.response?.data || error
      }
    },
    async approveReceiptReport(id, payload) {
      try {
        const { data } = await api.post(`/inventory/receipt-reports/${id}/approve/`, payload)
        await this.fetchReceiptReports()
        return data
      } catch (error) {
        throw error.response?.data || error
      }
    },
    setFilters(filters) {
      this.filters = { ...this.filters, ...filters }
      this.pagination.page = 1
      this.fetchReceiptReports()
    }
  }
})
