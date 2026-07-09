<template>
  <Panel title="Global Linked Accounts" subtitle="Settings | Accounting Setting">
    <template #actions>
      <button 
        type="button" 
        class="flex items-center gap-2 px-4 py-2 bg-bfs-gold text-white text-sm font-medium rounded-lg hover:bg-yellow-600 transition-colors disabled:opacity-50"
        @click="saveSettings" 
        :disabled="isSaving"
      >
        <span v-if="isSaving" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
        <svg v-else xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
        Save Settings
      </button>
    </template>

    <div v-if="isLoading" class="flex justify-center py-12">
      <div class="w-8 h-8 border-4 border-bfs-gold border-t-transparent rounded-full animate-spin"></div>
    </div>

    <div v-else class="space-y-6">
      
      <!-- General Ledger Linked Accounts -->
      <div class="border border-gray-200 rounded-xl p-4 bg-gray-50/50">
        <h3 class="text-md font-semibold text-gray-800 mb-4 pb-2 border-b border-gray-200">General Ledger Linked Accounts</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Equity Account for Current Earnings">
            <SearchableSelect v-model="formData.current_earnings" :groups="coaGrouped" label-key="account_name" :search-keys="['account_number', 'account_name']" :label-fn="formatCoa" value-key="id" placeholder="None" />
          </FormField>
          <FormField label="Equity Account for Retained Earnings">
            <SearchableSelect v-model="formData.retained_earnings" :groups="coaGrouped" label-key="account_name" :search-keys="['account_number', 'account_name']" :label-fn="formatCoa" value-key="id" placeholder="None" />
          </FormField>
          <FormField label="Equity Account for Historical Balancing">
            <SearchableSelect v-model="formData.historical_balancing" :groups="coaGrouped" label-key="account_name" :search-keys="['account_number', 'account_name']" :label-fn="formatCoa" value-key="id" placeholder="None" />
          </FormField>
        </div>
      </div>

      <!-- SO PO DISC Account -->
      <div class="border border-gray-200 rounded-xl p-4 bg-gray-50/50">
        <h3 class="text-md font-semibold text-gray-800 mb-4 pb-2 border-b border-gray-200">SO PO DISC Account</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Sales Discount">
            <SearchableSelect v-model="formData.sales_discount" :groups="coaGrouped" label-key="account_name" :search-keys="['account_number', 'account_name']" :label-fn="formatCoa" value-key="id" placeholder="None" />
          </FormField>
          <FormField label="Purchase Discount">
            <SearchableSelect v-model="formData.purchase_discount" :groups="coaGrouped" label-key="account_name" :search-keys="['account_number', 'account_name']" :label-fn="formatCoa" value-key="id" placeholder="None" />
          </FormField>
        </div>
      </div>

      <!-- PPIC Accounts -->
      <div class="border border-gray-200 rounded-xl p-4 bg-gray-50/50">
        <h3 class="text-md font-semibold text-gray-800 mb-4 pb-2 border-b border-gray-200">PPIC Accounts</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Work In Process (WIP)">
            <SearchableSelect v-model="formData.wip_account" :groups="coaGrouped" label-key="account_name" :search-keys="['account_number', 'account_name']" :label-fn="formatCoa" value-key="id" placeholder="None" />
          </FormField>
          <FormField label="Direct Labor Liability">
            <SearchableSelect v-model="formData.direct_labor_liability" :groups="coaGrouped" label-key="account_name" :search-keys="['account_number', 'account_name']" :label-fn="formatCoa" value-key="id" placeholder="None" />
          </FormField>
        </div>
      </div>

      <!-- Revaluation Linked Accounts -->
      <div class="border border-gray-200 rounded-xl p-4 bg-gray-50/50">
        <h3 class="text-md font-semibold text-gray-800 mb-4 pb-2 border-b border-gray-200">Revaluation Linked Accounts</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Income for Revaluation">
            <SearchableSelect v-model="formData.income_for_revaluation" :groups="coaGrouped" label-key="account_name" :search-keys="['account_number', 'account_name']" :label-fn="formatCoa" value-key="id" placeholder="None" />
          </FormField>
          <FormField label="Expense for Revaluation">
            <SearchableSelect v-model="formData.expense_for_revaluation" :groups="coaGrouped" label-key="account_name" :search-keys="['account_number', 'account_name']" :label-fn="formatCoa" value-key="id" placeholder="None" />
          </FormField>
        </div>
      </div>

      <!-- Sales Linked Accounts -->
      <div class="border border-gray-200 rounded-xl p-4 bg-gray-50/50">
        <h3 class="text-md font-semibold text-gray-800 mb-4 pb-2 border-b border-gray-200">Sales Linked Accounts</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Asset Account for Tracking Receivables">
            <SearchableSelect v-model="formData.ar_trade" :groups="coaGrouped" label-key="account_name" :search-keys="['account_number', 'account_name']" :label-fn="formatCoa" value-key="id" placeholder="None" />
          </FormField>
          <FormField label="Track Deposits Collected from Customers">
            <SearchableSelect v-model="formData.customer_deposit" :groups="coaGrouped" label-key="account_name" :search-keys="['account_number', 'account_name']" :label-fn="formatCoa" value-key="id" placeholder="None" />
          </FormField>
          <FormField label="DS for Tracking Receivables">
            <SearchableSelect v-model="formData.ds_for_tracking_receivables" :groups="coaGrouped" label-key="account_name" :search-keys="['account_number', 'account_name']" :label-fn="formatCoa" value-key="id" placeholder="None" />
          </FormField>
          <FormField label="Ds for Tracking Sales Return">
            <SearchableSelect v-model="formData.ds_for_tracking_sales_return" :groups="coaGrouped" label-key="account_name" :search-keys="['account_number', 'account_name']" :label-fn="formatCoa" value-key="id" placeholder="None" />
          </FormField>
        </div>
      </div>

      <!-- Purchase Linked Accounts -->
      <div class="border border-gray-200 rounded-xl p-4 bg-gray-50/50">
        <h3 class="text-md font-semibold text-gray-800 mb-4 pb-2 border-b border-gray-200">Purchase Linked Accounts</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Liability Account for Tracking Payables">
            <SearchableSelect v-model="formData.ap_trade" :groups="coaGrouped" label-key="account_name" :search-keys="['account_number', 'account_name']" :label-fn="formatCoa" value-key="id" placeholder="None" />
          </FormField>
          <FormField label="Account For Tracking Price Different">
            <SearchableSelect v-model="formData.account_for_tracking_price_different" :groups="coaGrouped" label-key="account_name" :search-keys="['account_number', 'account_name']" :label-fn="formatCoa" value-key="id" placeholder="None" />
          </FormField>
          <FormField label="Deposit Fund Vendor">
            <SearchableSelect v-model="formData.vendor_deposit" :groups="coaGrouped" label-key="account_name" :search-keys="['account_number', 'account_name']" :label-fn="formatCoa" value-key="id" placeholder="None" />
          </FormField>
        </div>
      </div>

      <!-- Asset Management -->
      <div class="border border-gray-200 rounded-xl p-4 bg-gray-50/50">
        <h3 class="text-md font-semibold text-gray-800 mb-4 pb-2 border-b border-gray-200">Asset Management</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Profit on Selling Assets">
            <SearchableSelect v-model="formData.profit_on_selling_assets" :groups="coaGrouped" label-key="account_name" :search-keys="['account_number', 'account_name']" :label-fn="formatCoa" value-key="id" placeholder="None" />
          </FormField>
          <FormField label="Loss on Selling Assets">
            <SearchableSelect v-model="formData.loss_on_selling_assets" :groups="coaGrouped" label-key="account_name" :search-keys="['account_number', 'account_name']" :label-fn="formatCoa" value-key="id" placeholder="None" />
          </FormField>
        </div>
      </div>

      <!-- Commission -->
      <div class="border border-gray-200 rounded-xl p-4 bg-gray-50/50">
        <h3 class="text-md font-semibold text-gray-800 mb-4 pb-2 border-b border-gray-200">Commission</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Amount">
            <SearchableSelect v-model="formData.commission_amount" :groups="coaGrouped" label-key="account_name" :search-keys="['account_number', 'account_name']" :label-fn="formatCoa" value-key="id" placeholder="None" />
          </FormField>
          <FormField label="Amount Payable">
            <SearchableSelect v-model="formData.commission_amount_payable" :groups="coaGrouped" label-key="account_name" :search-keys="['account_number', 'account_name']" :label-fn="formatCoa" value-key="id" placeholder="None" />
          </FormField>
          <FormField label="Tax Payable">
            <SearchableSelect v-model="formData.commission_tax_payable" :groups="coaGrouped" label-key="account_name" :search-keys="['account_number', 'account_name']" :label-fn="formatCoa" value-key="id" placeholder="None" />
          </FormField>
        </div>
      </div>

      <!-- Expense Kurs -->
      <div class="border border-gray-200 rounded-xl p-4 bg-gray-50/50">
        <h3 class="text-md font-semibold text-gray-800 mb-4 pb-2 border-b border-gray-200">Expense Kurs</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Gain">
            <SearchableSelect v-model="formData.currency_gain" :groups="coaGrouped" label-key="account_name" :search-keys="['account_number', 'account_name']" :label-fn="formatCoa" value-key="id" placeholder="None" />
          </FormField>
          <FormField label="Loss">
            <SearchableSelect v-model="formData.currency_loss" :groups="coaGrouped" label-key="account_name" :search-keys="['account_number', 'account_name']" :label-fn="formatCoa" value-key="id" placeholder="None" />
          </FormField>
        </div>
      </div>

      <!-- Journal Difference Container Account -->
      <div class="border border-gray-200 rounded-xl p-4 bg-gray-50/50">
        <h3 class="text-md font-semibold text-gray-800 mb-4 pb-2 border-b border-gray-200">Journal Difference Container Account</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Account">
            <SearchableSelect v-model="formData.journal_difference" :groups="coaGrouped" label-key="account_name" :search-keys="['account_number', 'account_name']" :label-fn="formatCoa" value-key="id" placeholder="None" />
          </FormField>
        </div>
      </div>

      <!-- Waste Account -->
      <div class="border border-gray-200 rounded-xl p-4 bg-gray-50/50">
        <h3 class="text-md font-semibold text-gray-800 mb-4 pb-2 border-b border-gray-200">Waste Account</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Waste Account">
            <SearchableSelect v-model="formData.waste_account" :groups="coaGrouped" label-key="account_name" :search-keys="['account_number', 'account_name']" :label-fn="formatCoa" value-key="id" placeholder="None" />
          </FormField>
        </div>
      </div>

      <!-- Production Waste Account -->
      <div class="border border-gray-200 rounded-xl p-4 bg-gray-50/50">
        <h3 class="text-md font-semibold text-gray-800 mb-4 pb-2 border-b border-gray-200">Production Waste Account</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Production Waste Account">
            <SearchableSelect v-model="formData.production_waste_account" :groups="coaGrouped" label-key="account_name" :search-keys="['account_number', 'account_name']" :label-fn="formatCoa" value-key="id" placeholder="None" />
          </FormField>
        </div>
      </div>

      <!-- WHT Account -->
      <div class="border border-gray-200 rounded-xl p-4 bg-gray-50/50">
        <h3 class="text-md font-semibold text-gray-800 mb-4 pb-2 border-b border-gray-200">WHT Account</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Account">
            <SearchableSelect v-model="formData.wht_account" :groups="coaGrouped" label-key="account_name" :search-keys="['account_number', 'account_name']" :label-fn="formatCoa" value-key="id" placeholder="None" />
          </FormField>
        </div>
      </div>

    </div>
  </Panel>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import api from '../../services/api.js'
import { useToast } from '../../composables/useToast.js'
import { useAccountingStore } from '../../stores/accounting.js'
import Panel from '../../components/Panel.vue'
import FormField from '../../components/FormField.vue'
import SearchableSelect from '../../components/SearchableSelect.vue'

export default {
  name: 'GlobalLinkedAccountView',
  components: {
    Panel,
    FormField,
    SearchableSelect
  },
  setup() {
    const toast = useToast()
    const accountingStore = useAccountingStore()
    const isLoading = ref(false)
    const isSaving = ref(false)
    
    const formData = ref({
      current_earnings: null,
      retained_earnings: null,
      historical_balancing: null,
      sales_discount: null,
      purchase_discount: null,
      wip_account: null,
      direct_labor_liability: null,
      income_for_revaluation: null,
      expense_for_revaluation: null,
      ar_trade: null,
      customer_deposit: null,
      ds_for_tracking_receivables: null,
      ds_for_tracking_sales_return: null,
      ap_trade: null,
      account_for_tracking_price_different: null,
      vendor_deposit: null,
      profit_on_selling_assets: null,
      loss_on_selling_assets: null,
      commission_amount: null,
      commission_amount_payable: null,
      commission_tax_payable: null,
      currency_gain: null,
      currency_loss: null,
      journal_difference: null,
      waste_account: null,
      production_waste_account: null,
      wht_account: null
    })

    const fetchSettings = async () => {
      isLoading.value = true
      try {
        const response = await api.get('/accounting/global-linked-accounts/')
        if (response.data) {
          Object.keys(formData.value).forEach(key => {
            if (response.data[key] !== undefined) {
              formData.value[key] = response.data[key]
            }
          })
        }
      } catch (error) {
        console.error('Failed to load settings', error)
      } finally {
        isLoading.value = false
      }
    }

    const saveSettings = async () => {
      isSaving.value = true
      try {
        await api.put('/accounting/global-linked-accounts/', formData.value)
        toast.success('Global Linked Accounts saved successfully')
      } catch (error) {
        toast.error('Failed to save settings')
        console.error(error)
      } finally {
        isSaving.value = false
      }
    }

    onMounted(async () => {
      if (!accountingStore.coaFlat.length) {
        await accountingStore.fetchCoaFlat({ postable: 'true', active: 'true' })
      }
      await fetchSettings()
    })

    const coaGrouped = computed(() => {
      const flat = accountingStore.coaFlat.filter(a => a.is_postable && a.is_active)
      const groups = {}
      flat.forEach(acc => {
        const gname = acc.account_group_name || 'Lainnya'
        if(!groups[gname]) groups[gname] = []
        groups[gname].push(acc)
      })
      return Object.entries(groups).map(([label, options]) => ({ label, options }))
    })
    
    // Format label for display
    const formatCoa = (opt) => `[${opt.account_number}] ${opt.account_name}`

    return {
      isLoading,
      isSaving,
      formData,
      coaGrouped,
      formatCoa,
      saveSettings
    }
  }
}
</script>
