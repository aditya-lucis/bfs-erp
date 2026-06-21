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
import GeneralJournalListView from './views/gl/GeneralJournalListView.vue'
import GeneralJournalFormView from './views/gl/GeneralJournalFormView.vue'
import GeneralJournalInboxView from './views/gl/GeneralJournalInboxView.vue'
import UnitMeasurementView from './views/inventory/UnitMeasurementView.vue'
import ItemCategoryView from './views/inventory/ItemCategoryView.vue'
import ItemView from './views/inventory/ItemView.vue'
import CustomerView from './views/sales/CustomerView.vue'
import VendorCategoryView from './views/purchase/VendorCategoryView.vue'
import VendorGroupView from './views/purchase/VendorGroupView.vue'
import VendorView from './views/purchase/VendorView.vue'
import BudgetComponentView from './views/budgetcomponent/BudgetComponentView.vue'
import AnnualBudgetView from './views/annualbudget/AnnualBudgetView.vue'
import AnnualPeriodView from './views/gl/AnnualPeriodView.vue'
import QuarterPeriodView from './views/gl/QuarterPeriodView.vue'
import MonthlyPeriodView from './views/gl/MonthlyPeriodView.vue'
import AccountingPeriodView from './views/gl/AccountingPeriodView.vue'
import PeriodActivityLogView from './views/gl/PeriodActivityLogView.vue'
import RequestApprovalSettingView from './views/settings/RequestApprovalSettingView.vue'
import RapInboxView from './views/projects/RapInboxView.vue'
import RapTypeView from './views/projects/RapTypeView.vue'
import ProjectListView from './views/projects/ProjectListView.vue'
import RapView from './views/projects/RapView.vue'
import ProjectCategoryView from './views/settings/ProjectCategoryView.vue'
import PurchaseRequisitionView from './views/purchase/PurchaseRequisitionView.vue'
import PurchaseRequisitionInboxView from './views/purchase/PurchaseRequisitionInboxView.vue'
import PurchaseOrderView from './views/purchase/PurchaseOrderView.vue'
import { menuData } from './menuData.js'

// Route yang sudah punya halaman nyata — jangan generate UnderConstruction
const implementedRoutes = [
  { path: '/settings/company-information', component: CompanyInformationView, meta: { title: 'Company Information', moduleId: 'settings', moduleName: 'Settings', layout: 'default' } },
  { path: '/settings/organizational-level', component: DepartmentView, meta: { title: 'Organizational Level', moduleId: 'settings', moduleName: 'Settings', layout: 'default' } },
  { path: '/settings/user-authorization-group', component: AuthGroupListView, meta: { title: 'User Authorization Group', moduleId: 'settings', moduleName: 'Settings', layout: 'default' } },
  { path: '/settings/employee-data', component: EmployeeView, meta: { title: 'Employee Data', moduleId: 'settings', moduleName: 'Settings', layout: 'default' } },
  { path: '/gl/chart-of-accounts', component: ChartOfAccountView, meta: { title: 'Chart of Accounts', moduleId: 'gl', moduleName: 'General Ledger', layout: 'default' } },
  { path: '/gl/general-journal-transaction', component: GeneralJournalListView, meta: { title: 'General Journal Transaction', moduleId: 'gl', moduleName: 'General Ledger', layout: 'default' } },
  { path: '/gl/general-journal-transaction/entry', component: GeneralJournalFormView, meta: { title: 'General Journal Entry', moduleId: 'gl', moduleName: 'General Ledger', layout: 'default' } },
  { path: '/gl/general-journal-transaction/entry/:id', component: GeneralJournalFormView, meta: { title: 'General Journal Entry', moduleId: 'gl', moduleName: 'General Ledger', layout: 'default' } },
  { path: '/gl/general-journal-inbox', component: GeneralJournalInboxView, meta: { title: 'General Journal Inbox', moduleId: 'gl', moduleName: 'General Ledger', layout: 'default' } },
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
  { path: '/finance/annual-budget', component: AnnualBudgetView, meta: { title: 'Annual Budget', moduleId: 'finance', moduleName: 'Finance', layout: 'default' } },
  { path: '/settings/annual-period', component: AnnualPeriodView, meta: { title: 'Annual Period', moduleId: 'gl', moduleName: 'General Ledger', layout: 'default' } },
  { path: '/settings/quarter-period', component: QuarterPeriodView, meta: { title: 'Quarter Period', moduleId: 'gl', moduleName: 'General Ledger', layout: 'default' } },
  { path: '/settings/monthly-period', component: MonthlyPeriodView, meta: { title: 'Monthly Period', moduleId: 'gl', moduleName: 'General Ledger', layout: 'default' } },
  { path: '/settings/accounting-period', component: AccountingPeriodView, meta: { title: 'Accounting Period', moduleId: 'gl', moduleName: 'General Ledger', layout: 'default' } },
  { path: '/settings/period-activity-log', component: PeriodActivityLogView, meta: { title: 'Period Activity Log', moduleId: 'gl', moduleName: 'General Ledger', layout: 'default' } },
  { path: '/settings/request-approval-setting', component: RequestApprovalSettingView, meta: { title: 'Request Approval Setting', moduleId: 'settings', moduleName: 'Settings', layout: 'default' } },
  { path: '/projects/rap-inbox', component: RapInboxView, meta: { title: 'RAP Inbox', moduleId: 'projects', moduleName: 'Projects', layout: 'default' } },
  { path: '/projects/rap-type', component: RapTypeView, meta: { title: 'RAP Type', moduleId: 'projects', moduleName: 'Projects', layout: 'default' } },
  { path: '/projects/rap', component: RapView, meta: { title: 'RAP', moduleId: 'projects', moduleName: 'Projects', layout: 'default' } },
  { path: '/projects/list-of-projects', component: ProjectListView, meta: { title: 'List of Projects', moduleId: 'projects', moduleName: 'Projects', layout: 'default' } },
  { path: '/commercial/list-of-projects', component: ProjectListView, meta: { title: 'List of Projects', moduleId: 'commercial', moduleName: 'Commercial', layout: 'default' } },
  { path: '/settings/project-category', component: ProjectCategoryView, meta: { title: 'Project Category', moduleId: 'settings', moduleName: 'Settings', layout: 'default' } },
  { path: '/purchases/purchase-requisition', component: PurchaseRequisitionView, meta: { title: 'Purchase Requisition', moduleId: 'purchases', moduleName: 'Purchases', layout: 'default' } },
  { path: '/purchases/purchase-requisition-inbox', component: PurchaseRequisitionInboxView, meta: { title: 'Purchase Requisition Inbox', moduleId: 'purchases', moduleName: 'Purchases', layout: 'default' } },
  { path: '/purchases/purchase-order', component: PurchaseOrderView, meta: { title: 'Purchase Order', moduleId: 'purchases', moduleName: 'Purchases', layout: 'default' } },
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