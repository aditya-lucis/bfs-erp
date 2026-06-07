import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../services/api.js'

export const useAccountingStore = defineStore('accounting', () => {

  // ── State ──────────────────────────────────────────────────────────────────
  const accountGroups = ref([])   // list of AccountGroup
  const coaTree       = ref([])   // [{ group, accounts: [tree] }]
  const coaFlat       = ref([])   // flat list untuk dropdown
  const choices       = ref(null) // enum choices dari backend
  const isLoading     = ref(false)
  const error         = ref(null)

  // ── Account Groups ─────────────────────────────────────────────────────────

  async function fetchAccountGroups() {
    try {
      const res = await api.get('/accounting/account-groups/')
      accountGroups.value = res.data
    } catch (err) {
      console.error('Gagal memuat account groups', err)
    }
  }

  async function createAccountGroup(payload) {
    const res = await api.post('/accounting/account-groups/', payload)
    return res.data
  }

  async function updateAccountGroup(id, payload) {
    const res = await api.patch(`/accounting/account-groups/${id}/`, payload)
    return res.data
  }

  async function deleteAccountGroup(id) {
    await api.delete(`/accounting/account-groups/${id}/`)
  }

  // ── Chart of Accounts ──────────────────────────────────────────────────────

  async function fetchCoaTree() {
    isLoading.value = true
    error.value     = null
    try {
      const res   = await api.get('/accounting/coa/tree/')
      coaTree.value = res.data
    } catch (err) {
      error.value = 'Gagal memuat Chart of Account.'
      console.error(err)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchCoaFlat(params = {}) {
    try {
      const res     = await api.get('/accounting/coa/', { params })
      coaFlat.value = res.data.results ?? res.data
    } catch (err) {
      console.error('Gagal memuat COA flat', err)
    }
  }

  async function createAccount(payload) {
    const res = await api.post('/accounting/coa/', payload)
    return res.data
  }

  async function updateAccount(id, payload) {
    const res = await api.patch(`/accounting/coa/${id}/`, payload)
    return res.data
  }

  async function deleteAccount(id) {
    await api.delete(`/accounting/coa/${id}/`)
  }

  // ── Choices (enum dropdown) ────────────────────────────────────────────────
  // Di-fetch sekali, di-cache di store

  async function fetchChoices() {
    if (choices.value) return  // udah ada, skip
    try {
      const res   = await api.get('/accounting/coa/choices/')
      choices.value = res.data
    } catch (err) {
      console.error('Gagal memuat choices', err)
    }
  }

  return {
    accountGroups, coaTree, coaFlat, choices, isLoading, error,
    fetchAccountGroups, createAccountGroup, updateAccountGroup, deleteAccountGroup,
    fetchCoaTree, fetchCoaFlat, createAccount, updateAccount, deleteAccount,
    fetchChoices,
  }
})