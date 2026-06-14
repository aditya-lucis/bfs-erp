import { defineStore } from 'pinia'
import api from '../services/api.js'

export const useProjectsStore = defineStore('projects', {
  state: () => ({
    rapTypes: [],
    projects: [],
    projectTypes: [],
    projectCategories: [],
    loading: false,
    error: null,
  }),

  actions: {
    // ── RAP Types ──
    async fetchRapTypes(params = {}) {
      this.loading = true
      this.error = null
      try {
        const res = await api.get('/projects/rap-types/', { params })
        this.rapTypes = res.data.results ?? res.data
      } catch (e) {
        this.error = e
        this.rapTypes = []
        throw e
      } finally {
        this.loading = false
      }
    },

    async createRapType(payload) {
      const res = await api.post('/projects/rap-types/', payload)
      return res.data
    },

    async updateRapType(id, payload) {
      const res = await api.put(`/projects/rap-types/${id}/`, payload)
      return res.data
    },

    async deleteRapType(id) {
      const res = await api.delete(`/projects/rap-types/${id}/`)
      return res.data
    },

    // ── Projects ──
    async fetchProjects(params = {}) {
      this.loading = true
      this.error = null
      try {
        const res = await api.get('/projects/projects/', { params })
        this.projects = res.data.results ?? res.data
      } catch (e) {
        this.error = e
        this.projects = []
        throw e
      } finally {
        this.loading = false
      }
    },

    async createProject(payload) {
      const res = await api.post('/projects/projects/', payload)
      return res.data
    },

    async updateProject(id, payload) {
      const res = await api.put(`/projects/projects/${id}/`, payload)
      return res.data
    },

    async deleteProject(id) {
      const res = await api.delete(`/projects/projects/${id}/`)
      return res.data
    },

    async actionProject(id, action, status = null) {
      const res = await api.post(`/projects/projects/${id}/action/`, { action, status })
      return res.data
    },

    // ── Project Types ──
    async fetchProjectTypes(params = {}) {
      this.loading = true
      this.error = null
      try {
        const res = await api.get('/projects/project-types/', { params })
        this.projectTypes = res.data.results ?? res.data
      } catch (e) {
        this.error = e
        this.projectTypes = []
        throw e
      } finally {
        this.loading = false
      }
    },

    // ── Project Categories ──
    async fetchProjectCategories(params = {}) {
      this.loading = true
      this.error = null
      try {
        const res = await api.get('/projects/project-categories/', { params })
        this.projectCategories = res.data.results ?? res.data
      } catch (e) {
        this.error = e
        this.projectCategories = []
        throw e
      } finally {
        this.loading = false
      }
    },

    async createProjectCategory(payload) {
      const res = await api.post('/projects/project-categories/', payload)
      return res.data
    },

    async updateProjectCategory(id, payload) {
      const res = await api.put(`/projects/project-categories/${id}/`, payload)
      return res.data
    },

    async deleteProjectCategory(id) {
      const res = await api.delete(`/projects/project-categories/${id}/`)
      return res.data
    },
  },
})


