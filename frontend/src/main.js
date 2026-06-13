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
import UnitMeasurementView from './views/inventory/UnitMeasurementView.vue'
import ItemCategoryView from './views/inventory/ItemCategoryView.vue'
import ItemView from './views/inventory/ItemView.vue'
import CustomerView from './views/sales/CustomerView.vue'
import VendorCategoryView from './views/purchase/VendorCategoryView.vue'
import VendorGroupView from './views/purchase/VendorGroupView.vue'
import VendorView from './views/purchase/VendorView.vue'
import BudgetComponentView from './views/budgetcomponent/BudgetComponentView.vue'
import { menuData } from './menuData.js'

// Route yang sudah punya halaman nyata — jangan generate UnderConstruction
const implementedRoutes = [
  { path: '/settings/company-information', component: CompanyInformationView, meta: { title: 'Company Information', moduleId: 'settings', moduleName: 'Settings', layout: 'default' } },
  { path: '/settings/organizational-level', component: DepartmentView, meta: { title: 'Organizational Level', moduleId: 'settings', moduleName: 'Settings', layout: 'default' } },
  { path: '/settings/user-authorization-group', component: AuthGroupListView, meta: { title: 'User Authorization Group', moduleId: 'settings', moduleName: 'Settings', layout: 'default' } },
  { path: '/settings/employee-data', component: EmployeeView, meta: { title: 'Employee Data', moduleId: 'settings', moduleName: 'Settings', layout: 'default' } },
  { path: '/gl/chart-of-accounts', component: ChartOfAccountView, meta: { title: 'Chart of Accounts', moduleId: 'gl', moduleName: 'General Ledger', layout: 'default' } },
  { path: '/inventory/unit-measurement', component: UnitMeasurementView, meta: { title: 'Unit Measurement', moduleId: 'inventory', moduleName: 'Inventory', layout: 'default' } },
  { path: '/inventory/item-category', component: ItemCategoryView, meta: { title: 'Item Category', moduleId: 'inventory', moduleName: 'Inventory', layout: 'default' } },
  { path: '/inventory/items', component: ItemView, meta: { title: 'List of Items', moduleId: 'inventory', moduleName: 'Inventory', layout: 'default' } },
  { path: '/sales/customers', component: CustomerView, meta: { title: 'Customers', moduleId: 'sales', moduleName: 'Sales', layout: 'default' } },
  { path: '/commercial/customers', component: CustomerView, meta: { title: 'Customers', moduleId: 'commercial', moduleName: 'Commercial', layout: 'default' } },
  { path: '/finance/penyerapan-rap', component: FinanceView, meta: { title: 'Penyerapan RAP', moduleId: 'finance', moduleName: 'Finance', layout: 'default' } },
  { path: '/purchases/vendor-category', component: VendorCategoryView, meta: { title: 'Vendor Category', moduleId: 'purchases', moduleName: 'Purchases', layout: 'default' } },
  { path: '/purchases/vendor-group', component: VendorGroupView, meta: { title: 'Vendor Group', moduleId: 'purchases', moduleName: 'Purchases', layout: 'default' } },
  { path: '/purchases/vendor', component: VendorView, meta: { title: 'List Of Vendors', moduleId: 'purchases', moduleName: 'Purchases', layout: 'default' } },
  { path: '/finance/budget-component', component: BudgetComponentView, meta: { title: 'Budget Component', moduleId: 'finance', moduleName: 'Finance', layout: 'default' } },
]

const implementedPaths = new Set(implementedRoutes.map(r => r.path))

function generateRoutesFromMenu() {
  const routes = []

  Object.entries(menuData).forEach(([moduleId, items]) => {
    const flatten = (menuItems, parentPath = '') => {
      menuItems.forEach(item => {
        if (item.children && item.children.length > 0) {
          flatten(item.children, parentPath)
        } else {
          const explicitUrl = item.url?.trim()
          const slug = slugify(item.name)
          const path = explicitUrl || (parentPath
            ? `${parentPath}/${slug}`
            : `/${moduleId}/${slug}`)

          if (implementedPaths.has(path)) return

          routes.push({
            path,
            component: UnderConstruction,
            meta: {
              title: item.name,
              moduleId: moduleId,
              moduleName: getModuleName(moduleId),
              layout: 'default',
            },
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
    meta: { layout: 'auth', public: true },
  },
  {
    path: '/',
    component: HomeView,
    meta: { layout: 'default' },
  },
  {
    path: '/dashboard',
    component: DashboardView,
    meta: { layout: 'default' },
  },
  // Halaman yang sudah diimplementasi — HARUS sebelum dynamicRoutes
  ...implementedRoutes,
  ...dynamicRoutes,
  {
    path: '/:pathMatch(.*)*',
    component: UnderConstruction,
    meta: { layout: 'default' },
  },
]

// Buat pinia dan router
const pinia = createPinia()
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