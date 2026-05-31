import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { menuData } from '../menuData.js'

export function useBreadcrumb() {
  const route = useRoute()

  const breadcrumbs = computed(() => {
    const crumbs = []
    const path = route.path

    // Home page
    if (path === '/') {
      crumbs.push({
        label: 'Home',
        path: '/',
        isLast: true
      })
      return crumbs
    }

    // Dashboard selector page
    if (path === '/dashboard') {
      crumbs.push({
        label: 'My Dashboard',
        path: '/',
        isLast: false
      })
      crumbs.push({
        label: 'Dashboard',
        path: null,
        isLast: true
      })
      return crumbs
    }

    // Default: My Dashboard as first crumb
    crumbs.push({
      label: 'My Dashboard',
      path: '/dashboard',
      isLast: false
    })

    const meta = route.meta
    if (!meta || !meta.moduleId) {
      // If no meta, just show current path
      crumbs.push({
        label: route.meta?.title || 'Unknown',
        path: null,
        isLast: true
      })
      return crumbs
    }

    const moduleId = meta.moduleId
    const itemName = meta.title

    // Find the item in menuData to get parent info
    const moduleItems = menuData[moduleId] || []
    const findItem = (items, targetName, parentName = null) => {
      for (const item of items) {
        if (item.name === targetName) {
          return { item, parentName }
        }
        if (item.children) {
          const found = findItem(item.children, targetName, item.name)
          if (found) return found
        }
      }
      return null
    }

    const found = findItem(moduleItems, itemName)

    // Add module name
    const moduleNames = {
      commercial: 'Commercial',
      gl: 'General Ledger',
      ar: 'Account Receivable',
      sales: 'Sales',
      ap: 'Account Payable',
      purchases: 'Purchases',
      finance: 'Finance',
      assets: 'Assets',
      inventory: 'Inventory',
      projects: 'Projects',
      settings: 'Settings',
    }

    crumbs.push({
      label: moduleNames[moduleId] || moduleId,
      path: null,
      isLast: false
    })

    // Add parent if exists (for nested menu items)
    if (found && found.parentName) {
      crumbs.push({
        label: found.parentName,
        path: null,
        isLast: false
      })
    }

    // Add the actual page title
    crumbs.push({
      label: itemName || 'Unknown',
      path: null,
      isLast: true
    })

    return crumbs
  })

  const pageTitle = computed(() => {
    return route.meta?.title || 'BFS ERP'
  })

  return {
    breadcrumbs,
    pageTitle
  }
}