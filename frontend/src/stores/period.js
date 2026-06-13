/**
 * BFS ERP — Financial Period Store
 * Manages: Annual, Quarter, Monthly, Accounting Period & Activity Logs
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../services/api.js'

export const usePeriodStore = defineStore('period', () => {

    // ── State ────────────────────────────────────────────────────────────────
    const annualPeriods = ref([])
    const quarterPeriods = ref([])   // grouped by year: [{ id, year, quarters:[{id,quarter,status}] }]
    const monthlyPeriods = ref([])   // grouped by year: [{ id, year, months:[{id,month,status}] }]
    const accountingPeriods = ref([])  // flat list
    const activityLogs = ref([])
    const isLoading = ref(false)
    const error = ref(null)

    // ── Annual ───────────────────────────────────────────────────────────────

    async function fetchAnnualPeriods() {
        isLoading.value = true
        error.value = null
        try {
            const res = await api.get('/accounting/periods/annual/')
            annualPeriods.value = res.data
        } catch (err) {
            error.value = 'Gagal memuat Annual Period.'
            console.error(err)
        } finally {
            isLoading.value = false
        }
    }

    async function addAnnualPeriod(year) {
        const res = await api.post('/accounting/periods/annual/', { year })
        return res.data
    }

    async function toggleAnnualPeriod(id, reason) {
        const res = await api.patch(`/accounting/periods/annual/${id}/toggle/`, { reason })
        // Update local state
        const idx = annualPeriods.value.findIndex(a => a.id === id)
        if (idx !== -1) annualPeriods.value[idx] = res.data
        return res.data
    }

    async function fetchAnnualLogs(id) {
        const res = await api.get(`/accounting/periods/annual/${id}/logs/`)
        return res.data
    }

    // ── Quarter ──────────────────────────────────────────────────────────────

    async function fetchQuarterPeriods() {
        isLoading.value = true
        error.value = null
        try {
            const res = await api.get('/accounting/periods/quarter/')
            quarterPeriods.value = res.data
        } catch (err) {
            error.value = 'Gagal memuat Quarter Period.'
            console.error(err)
        } finally {
            isLoading.value = false
        }
    }

    async function toggleQuarterPeriod(id, reason) {
        const res = await api.patch(`/accounting/periods/quarter/${id}/toggle/`, { reason })
        return res.data
    }

    async function fetchQuarterLogs(id) {
        const res = await api.get(`/accounting/periods/quarter/${id}/logs/`)
        return res.data
    }

    // ── Monthly ──────────────────────────────────────────────────────────────

    async function fetchMonthlyPeriods() {
        isLoading.value = true
        error.value = null
        try {
            const res = await api.get('/accounting/periods/monthly/')
            monthlyPeriods.value = res.data
        } catch (err) {
            error.value = 'Gagal memuat Monthly Period.'
            console.error(err)
        } finally {
            isLoading.value = false
        }
    }

    async function toggleMonthlyPeriod(id, reason) {
        const res = await api.patch(`/accounting/periods/monthly/${id}/toggle/`, { reason })
        return res.data
    }

    async function fetchMonthlyLogs(id) {
        const res = await api.get(`/accounting/periods/monthly/${id}/logs/`)
        return res.data
    }

    // ── Accounting Period ─────────────────────────────────────────────────────

    async function fetchAccountingPeriods(params = {}) {
        isLoading.value = true
        error.value = null
        try {
            const res = await api.get('/accounting/periods/accounting/', { params })
            accountingPeriods.value = res.data
        } catch (err) {
            error.value = 'Gagal memuat Accounting Period.'
            console.error(err)
        } finally {
            isLoading.value = false
        }
    }

    async function toggleAccountingPeriod(id, reason) {
        const res = await api.patch(`/accounting/periods/accounting/${id}/toggle/`, { reason })
        // Update local state
        const idx = accountingPeriods.value.findIndex(a => a.id === id)
        if (idx !== -1) accountingPeriods.value[idx] = res.data
        return res.data
    }

    async function fetchAccountingLogs(id) {
        const res = await api.get(`/accounting/periods/accounting/${id}/logs/`)
        return res.data
    }

    // ── Global Logs ───────────────────────────────────────────────────────────

    async function fetchAllLogs(params = {}) {
        isLoading.value = true
        try {
            const res = await api.get('/accounting/periods/logs/', { params })
            activityLogs.value = res.data
        } catch (err) {
            console.error(err)
        } finally {
            isLoading.value = false
        }
    }

    return {
        annualPeriods, quarterPeriods, monthlyPeriods,
        accountingPeriods, activityLogs,
        isLoading, error,

        fetchAnnualPeriods, addAnnualPeriod, toggleAnnualPeriod, fetchAnnualLogs,
        fetchQuarterPeriods, toggleQuarterPeriod, fetchQuarterLogs,
        fetchMonthlyPeriods, toggleMonthlyPeriod, fetchMonthlyLogs,
        fetchAccountingPeriods, toggleAccountingPeriod, fetchAccountingLogs,
        fetchAllLogs,
    }
})