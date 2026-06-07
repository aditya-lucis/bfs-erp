import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import { useAuthStore } from './stores/auth.js'
import App from './App.vue'
import './style.css'

// Views
import LoginView from './views/LoginView.vue'
import HomeView from './views/HomeView.vue'
import DashboardView from './views/DashboardView.vue'
import FinanceView from './views/FinanceView.vue'
import UnderConstruction from './views/UnderConstruction.vue'
import CompanyInformationView from './views/settings/CompanyInformationView.vue'
import DepartmentView from './views/settings/DepartmentView.vue'
import AuthGroupListView from './views/settings/AuthGroupListView.vue'
import EmployeeView from './views/settings/EmployeeView.vue'
import ChartOfAccountView from './views/gl/ChartOfAccountView.vue'
import { menuData } from './menuData.js'

function generateRoutesFromMenu() {
  const routes = []

  Object.entries(menuData).forEach(([moduleId, items]) => {
    const flatten = (menuItems, parentPath = '') => {
      menuItems.forEach(item => {
        if (item.children && item.children.length > 0) {
          flatten(item.children, parentPath)
        } else {
          const slug = slugify(item.name)
          const path = parentPath 
            ? `${parentPath}/${slug}`
            : `/${moduleId}/${slug}`

          routes.push({
            path: path,
            component: UnderConstruction,
            meta: {
              title: item.name,
              moduleId: moduleId,
              moduleName: getModuleName(moduleId)
            }
          })
        }
      })
    }

    flatten(items)
  })

  return routes
}

function slugify(text) {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '')
}

function getModuleName(moduleId) {
  const names = {
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
  return names[moduleId] || moduleId
}

const dynamicRoutes = generateRoutesFromMenu()

const routes = [
  { 
    path: '/login', 
    component: LoginView,
     meta: { layout: 'auth', public: true }
  },
  { 
    path: '/', 
    component: HomeView,
    meta: { layout: 'default' }
  },
  { 
    path: '/dashboard', 
    component: DashboardView,
    meta: { layout: 'default' }
  },
  { 
    path: '/finance/penyerapan-rap', 
    component: FinanceView,
    meta: { title: 'Penyerapan RAP', moduleId: 'finance', moduleName: 'Finance', layout: 'default' }
  },
  {
    path: '/settings/company-information',
    component: CompanyInformationView,
    meta: { 
      title: 'Company Information', 
      moduleId: 'settings', 
      moduleName: 'Settings',
      layout: 'default' 
    }
  },
  {
    path: '/settings/organizational-level',
    component: DepartmentView,
    meta: {
      title: 'Organizational Level',
      moduleId: 'settings',
      moduleName: 'Settings',
      layout: 'default'
    }
  },
  {
    path: '/settings/user-authorization-group',
    component: AuthGroupListView,
    meta: {
      title: 'User Authorization Group',
      moduleId: 'settings',
      moduleName: 'Settings',
      layout: 'default'
    }
  },
  {
    path: '/settings/employee-data',
    component: EmployeeView,
    meta: { title: 'Employee Data', moduleId: 'settings', moduleName: 'Settings', layout: 'default' }
  },
  {
    path: '/gl/chart-of-accounts',
    component: ChartOfAccountView,
    meta: {
      title: 'Chart of Accounts',
      moduleId: 'gl',
      moduleName: 'General Ledger',
      layout: 'default'
    }
  },
  ...dynamicRoutes.map(r => ({ ...r, meta: { ...r.meta, layout: 'default' } })),
  {
    path: '/:pathMatch(.*)*',
    component: UnderConstruction,
    meta: { layout: 'default' }
    // ← HAPUS redirect: '/login'
  }
]

// Buat pinia dan router
const pinia  = createPinia()
const router = createRouter({
  history: createWebHistory(),
  routes,
})

// ── Route Guard ──────────────────────────────────────────────────────────────
router.beforeEach(async (to, from, next) => {
  const auth = useAuthStore()

  // Restore session sekali saja
  if (auth.accessToken && !auth.user) {
    await auth.restoreSession()
  }

  if (to.meta.public) {
    // Sudah login + mau ke /login → ke home
    if (auth.isLoggedIn && to.path === '/login') {
      return next('/')
    }
    return next()
  }

  if (!auth.isLoggedIn) {
    return next('/login')
  }

  next()
})

const app = createApp(App)
app.use(pinia)
app.use(router)
app.mount('#app')