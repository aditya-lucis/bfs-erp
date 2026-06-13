import { defineStore } from 'pinia'
import api from '../services/api.js'

export const useBudgetComponentStore = defineStore('budgetComponent', {
    state: () => ({
        budgetComponents: [],
        currentBudgetComponent: null,
        templates: [],
        currentTemplate: null,
        templateDetails: [],
        itemsForPicker: [],
        positionsByDept: {},
        loading: false,
        error: null,
    }),

    actions: {

        // ── Budget Components ──────────────────────────────────────
        async fetchBudgetComponents(params = {}) {
            this.loading = true
            this.error = null
            try {
                const res = await api.get('/budget-components/budget-components/', { params })
                this.budgetComponents = res.data.results ?? res.data
            } catch (e) {
                this.error = e
                this.budgetComponents = []
                throw e
            } finally {
                this.loading = false
            }
        },

        async createBudgetComponent(payload) {
            const res = await api.post('/budget-components/budget-components/', payload)
            return res.data
        },

        async updateBudgetComponent(id, payload) {
            const res = await api.patch(`/budget-components/budget-components/${id}/`, payload)
            return res.data
        },

        async deleteBudgetComponent(id) {
            await api.delete(`/budget-components/budget-components/${id}/`)
        },

        // ── Template RAP ───────────────────────────────────────────
        async fetchTemplates(params = {}) {
            this.loading = true
            try {
                const res = await api.get('/budget-components/templates-rap/', { params })
                this.templates = res.data.results ?? res.data
                return this.templates
            } catch (e) {
                this.error = e
                throw e
            } finally {
                this.loading = false
            }
        },

        async fetchTemplate(id) {
            this.loading = true
            try {
                const res = await api.get(`/budget-components/templates-rap/${id}/`)
                this.currentTemplate = res.data
                return res.data
            } catch (e) {
                this.error = e
                throw e
            } finally {
                this.loading = false
            }
        },

        async createTemplate(payload) {
            const res = await api.post('/budget-components/templates-rap/', payload)
            return res.data
        },

        async updateTemplate(id, payload) {
            const res = await api.patch(`/budget-components/templates-rap/${id}/`, payload)
            return res.data
        },

        async deleteTemplate(id) {
            await api.delete(`/budget-components/templates-rap/${id}/`)
        },

        async fetchTemplateDetails(templateId) {
            // HAPUS parent parameter — ambil semua detail untuk template ini
            const res = await api.get('/budget-components/templates-rap-details/', {
                params: { template: templateId }  // tanpa parent filter
            })
            return res.data.results ?? res.data
        },


        async createTemplateDetail(templateId, payload) {
            const res = await api.post('/budget-components/templates-rap-details/', payload)
            return res.data
        },

        async updateTemplateDetail(id, payload) {
            const res = await api.patch(`/budget-components/templates-rap-details/${id}/`, payload)
            return res.data
        },

        async deleteTemplateDetail(id) {
            await api.delete(`/budget-components/templates-rap-details/${id}/`)
        },

        // ── Item Picker ──────────────────────────────────────────────
        async searchItems(search = '', category = '') {
            const params = {}
            if (search) params.search = search
            if (category) params.category = category
            const res = await api.get('/budget-components/items/picker/', { params })
            this.itemsForPicker = res.data.results ?? res.data
            return this.itemsForPicker
        },

        async fetchPositionsByDepartment(deptId) {
            // Hapus cache check biar selalu fetch fresh
            // if (this.positionsByDept[deptId]) return this.positionsByDept[deptId]

            try {
                const res = await api.get(`/budget-components/departments/${deptId}/positions/`)
                this.positionsByDept[deptId] = res.data
                return res.data
            } catch (e) {
                console.error('fetchPositionsByDepartment error:', e)
                throw e
            }
        }
    },
})