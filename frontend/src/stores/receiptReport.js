import { defineStore } from 'pinia'
import api from '@/utils/api'

export const useReceiptReportStore = defineStore('receiptReport', {
  state: () => ({
    receiptReports: [],
    loading: false,
    error: null,
  }),
  actions: {
    async fetchReceiptReports(type = 'RR_PUR') {
      this.loading = true
      try {
        const response = await api.get('/inventory/receipt-reports/', { params: { receipt_type: type } })
        this.receiptReports = response.data
      } catch (err) {
        this.error = err.response?.data || 'Gagal memuat Receipt Report'
        throw err
      } finally {
        this.loading = false
      }
    },
    async createReceiptReport(payload) {
      this.loading = true
      try {
        const response = await api.post('/inventory/receipt-reports/', payload)
        return response.data
      } catch (err) {
        this.error = err.response?.data || 'Gagal membuat Receipt Report'
        throw err
      } finally {
        this.loading = false
      }
    },
    async approveReceiptReport(id) {
      this.loading = true
      try {
        const response = await api.post(/inventory/receipt-reports//approve/)
        return response.data
      } catch (err) {
        this.error = err.response?.data || 'Gagal menyetujui Receipt Report'
        throw err
      } finally {
        this.loading = false
      }
    }
  }
})
