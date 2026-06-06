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
      if (!Array.isArray(depts)) return   // ← guard ini yang missing
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

  async function createDepartment(payload) {
    const res = await api.post('/org/departments/', payload)
    return res.data
  }

  async function updateDepartment(id, payload) {
    const res = await api.patch(`/org/departments/${id}/`, payload)
    return res.data
  }

  async function deleteDepartment(id) {
    await api.delete(`/org/departments/${id}/`)
  }


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
      const res = await api.patch('/org/company/', payload, {
        headers: payload instanceof FormData
          ? { 'Content-Type': 'multipart/form-data' }
          : { 'Content-Type': 'application/json' }
      })
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
      const res = await api.get('/org/departments/')
      // ← Backend bisa return { results: [...] } atau langsung [...]
      departments.value = res.data.results ?? res.data
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
      employees.value = res.data.results ?? res.data
    } catch (err) {
      console.error(err)
    } finally {
      isLoading.value = false
    }
  }

  async function createEmployee(formData) {
    // formData bisa FormData (ada file) atau plain object
    const res = await api.post('/org/employees/', formData, {
      headers: formData instanceof FormData
        ? { 'Content-Type': 'multipart/form-data' }
        : { 'Content-Type': 'application/json' }
    })
    return res.data
  }

  async function updateEmployee(id, formData) {
    const res = await api.patch(`/org/employees/${id}/`, formData, {
      headers: formData instanceof FormData
        ? { 'Content-Type': 'multipart/form-data' }
        : { 'Content-Type': 'application/json' }
    })
    return res.data
  }

  async function uploadSignature(employeeId, payload) {
    // payload: FormData dengan signature_image atau { signature_draw: '...' }
    const res = await api.post(`/org/employees/${employeeId}/signature/`, payload, {
      headers: payload instanceof FormData
        ? { 'Content-Type': 'multipart/form-data' }
        : { 'Content-Type': 'application/json' }
    })
    return res.data
  }

  async function createUserForEmployee(employeeId, payload) {
    // POST /org/employees/<id>/create-user/
    // payload: { username, password, password2 }
    const res = await api.post(`/org/employees/${employeeId}/create-user/`, payload)
    return res.data
  }

  async function adminResetPassword(userId, payload) {
    // POST /auth/users/<id>/reset-password/
    // payload: { new_password, new_password2 }
    const res = await api.post(`/auth/users/${userId}/reset-password/`, payload)
    return res.data
  }

  // Fetch semua sekaligus
  async function fetchAll() {
    await Promise.all([
      fetchCompany(),
      fetchDepartments(),
    ])
  }

  async function fetchPositionsByDept(deptId) {
    const res = await api.get(`/org/departments/${deptId}/positions/`)
    return res.data.results || res.data
  }

  async function createPosition(deptId, payload) {
    const res = await api.post(`/org/departments/${deptId}/positions/`, payload)
    return res.data
  }

  async function updatePosition(deptId, posId, payload) {
    const res = await api.patch(`/org/departments/${deptId}/positions/${posId}/`, payload)
    return res.data
  }

  async function deletePosition(deptId, posId) {
    await api.delete(`/org/departments/${deptId}/positions/${posId}/`)
  }

  return {
    company, departments, positions, employees, isLoading, error,
    companyName, companyCode, departmentList,
    createDepartment, updateDepartment, deleteDepartment,
    fetchCompany, updateCompany, fetchDepartments,
    fetchPositions, fetchEmployees, createEmployee, updateEmployee,
    uploadSignature, createUserForEmployee, adminResetPassword,
    fetchAll,
    fetchPositionsByDept, createPosition, updatePosition, deletePosition,
  }
})