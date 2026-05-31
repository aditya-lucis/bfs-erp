import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api.js'

export const useOrganizationStore = defineStore('organization', () => {
  // ── State ─────────────────────────────────────────────────────────────────
  const company     = ref(null)
  const departments = ref([])   // tree structure dari backend
  const positions   = ref([])
  const employees   = ref([])
  const isLoading   = ref(false)
  const error       = ref(null)

  // ── Getters ───────────────────────────────────────────────────────────────
  const companyName = computed(() => company.value?.company_name || '')
  const companyCode = computed(() => company.value?.company_code || '')

  // Flatten department tree jadi list untuk dropdown, dll
  const departmentList = computed(() => {
    const result = []
    const flatten = (depts, level = 0) => {
      depts.forEach(dept => {
        result.push({ ...dept, level })
        if (dept.children?.length) {
          flatten(dept.children, level + 1)
        }
      })
    }
    flatten(departments.value)
    return result
  })

  // ── Actions ───────────────────────────────────────────────────────────────
  async function fetchCompany() {
    isLoading.value = true
    error.value     = null
    try {
      const res      = await api.get('/org/company/')
      company.value  = res.data
    } catch (err) {
      error.value = 'Gagal memuat data perusahaan.'
      console.error(err)
    } finally {
      isLoading.value = false
    }
  }

  async function updateCompany(payload) {
    isLoading.value = true
    error.value     = null
    try {
      const res     = await api.patch('/org/company/', payload)
      company.value = res.data
      return { success: true }
    } catch (err) {
      error.value = 'Gagal menyimpan data perusahaan.'
      return { success: false, errors: err.response?.data }
    } finally {
      isLoading.value = false
    }
  }

  async function fetchDepartments() {
    try {
      const res        = await api.get('/org/departments/')
      departments.value = res.data
    } catch (err) {
      console.error('Gagal memuat departments', err)
    }
  }

  async function fetchPositions(departmentId = null) {
    try {
      const params = departmentId ? { department: departmentId } : {}
      const res    = await api.get('/org/positions/', { params })
      positions.value = res.data.results || res.data
    } catch (err) {
      console.error('Gagal memuat positions', err)
    }
  }

  async function fetchEmployees(filters = {}) {
    isLoading.value = true
    try {
      const res       = await api.get('/org/employees/', { params: filters })
      employees.value = res.data.results || res.data
    } catch (err) {
      console.error('Gagal memuat employees', err)
    } finally {
      isLoading.value = false
    }
  }

  // Fetch semua sekaligus
  async function fetchAll() {
    await Promise.all([
      fetchCompany(),
      fetchDepartments(),
    ])
  }

  return {
    company, departments, positions, employees, isLoading, error,
    companyName, companyCode, departmentList,
    fetchCompany, updateCompany, fetchDepartments,
    fetchPositions, fetchEmployees, fetchAll,
  }
})