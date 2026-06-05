import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../services/api.js'
import { menuData } from '../menuData.js'

export const useMenuStore = defineStore('menu', () => {
  const tree      = ref([])
  const myPerms   = ref({})
  const isReady   = ref(false)
  const isLoading = ref(false)

  // Build URL map dari menuData — flat lookup: name → url
  function buildUrlMap() {
    const map = {}
    const flatten = (items) => {
      for (const item of items) {
        if (item.url) map[item.name] = item.url
        if (item.children?.length) flatten(item.children)
      }
    }
    Object.values(menuData).forEach(items => flatten(items))
    return map
  }

  // Module code map dari menuData keys
  const MODULE_CODE_MAP = {
    'commercial': 'commercial',
    'general ledger': 'gl',
    'account receivable': 'ar',
    'sales': 'sales',
    'account payable': 'ap',
    'purchases': 'purchases',
    'finance': 'finance',
    'fixed assets': 'assets',
    'inventory': 'inventory',
    'projects': 'projects',
    'setting': 'settings',
    'settings': 'settings',
  }

  async function init() {
    isLoading.value = true
    try {
      const [treeRes, permsRes] = await Promise.all([
        api.get('/rbac/menu-tree/'),
        api.get('/rbac/my-permissions/'),
      ])

      const urlMap  = buildUrlMap()
      const rawTree = Array.isArray(treeRes.data) ? treeRes.data : []

      tree.value = rawTree.map(module => {
        let moduleCode = module.module_code?.trim()

        // Jangan pakai string 'undefined' atau 'null'
        if (!moduleCode || moduleCode === 'undefined' || moduleCode === 'null') {
          const name = module.module_name?.trim() || ''
          moduleCode = MODULE_CODE_MAP[name.toLowerCase()]
                    || name.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '')
                    || 'unknown'
        }

        console.log('🔧 Module processed:', {
          module_name: module.module_name,
          original_code: module.module_code,
          final_code: moduleCode
        })

        return {
          ...module,
          module_code: moduleCode,
          children: injectMeta(module.children, moduleCode, urlMap),
        }
      })

      myPerms.value = permsRes.data || {}
      isReady.value = true
    } catch (err) {
      console.error('Menu init error:', err)
      tree.value = []
      myPerms.value = {}
    } finally {
      isLoading.value = false
    }
  }

  function injectMeta(items, moduleCode, urlMap) {
    if (!Array.isArray(items)) return []
    return items.map(item => {
      // Resolve URL: backend url_path → menuData url → generate slug
      const resolvedUrl = (item.url_path && item.url_path.trim())
        ? item.url_path                          // dari backend DB
        : (urlMap[item.name] && urlMap[item.name].trim())
          ? urlMap[item.name]                    // dari menuData.js
          : ''                                   // kosong → generate di SidebarMenuItem

      return {
        ...item,
        module_code: moduleCode,                 // inject module_code
        url_path:    resolvedUrl,                // resolved URL
        children:    injectMeta(item.children, moduleCode, urlMap),
      }
    })
  }

  function can(functionCode, action = 'can_read') {
    return myPerms.value?.[functionCode]?.[action] ?? false
  }

  function reset() {
    tree.value      = []
    myPerms.value   = {}
    isReady.value   = false
    isLoading.value = false
  }

  return { tree, myPerms, isReady, isLoading, init, can, reset }
})