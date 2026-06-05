// src/composables/useBreadcrumb.js
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useMenuStore } from '../stores/menu.js'

export function useBreadcrumb() {
  const route     = useRoute()
  const menuStore = useMenuStore()

  const breadcrumbs = computed(() => {
    const crumbs = []
    const path   = route.path

    if (path === '/') {
      crumbs.push({ label: 'Home', path: '/', isLast: true })
      return crumbs
    }

    if (path === '/dashboard') {
      crumbs.push({ label: 'My Dashboard', path: '/',         isLast: false })
      crumbs.push({ label: 'Dashboard',    path: null,        isLast: true  })
      return crumbs
    }

    crumbs.push({ label: 'My Dashboard', path: '/dashboard', isLast: false })

    // Cari item di menu tree backend berdasarkan url_path
    const found = findInTree(menuStore.tree, path)

    if (found) {
      // Tambah module name
      crumbs.push({
        label:  found.moduleName,
        path:   null,
        isLast: false,
      })
      // Tambah parent kalau ada
      if (found.parentName) {
        crumbs.push({ label: found.parentName, path: null, isLast: false })
      }
      // Tambah item sendiri
      crumbs.push({ label: found.item.name, path: null, isLast: true })
    } else {
      // Fallback ke route meta
      const meta = route.meta
      if (meta?.moduleName) {
        crumbs.push({ label: meta.moduleName, path: null, isLast: false })
      }
      crumbs.push({
        label:  meta?.title || route.path.split('/').pop()?.replace(/-/g, ' ') || 'Page',
        path:   null,
        isLast: true,
      })
    }

    return crumbs
  })

  const pageTitle = computed(() => {
    const path  = route.path
    const found = findInTree(menuStore.tree, path)
    return found?.item.name || route.meta?.title || 'BFS ERP'
  })

  return { breadcrumbs, pageTitle }
}

// Helper: cari item di tree berdasarkan url_path
function findInTree(tree, targetPath) {
  for (const module of (tree || [])) {
    const result = searchChildren(module.children, targetPath, module.module_name, null)
    if (result) return result
  }
  return null
}

function searchChildren(items, targetPath, moduleName, parentName) {
  for (const item of (items || [])) {
    if (item.url_path && item.url_path === targetPath) {
      return { item, moduleName, parentName }
    }
    if (item.children?.length) {
      const found = searchChildren(item.children, targetPath, moduleName, item.name)
      if (found) return found
    }
  }
  return null
}