<template>
  <Panel title="Setting | Bank Obligation" subtitle="Settings | Bank Obligation Setting">
    <div v-if="loading" class="flex justify-center items-center py-20">
      <Loader2 class="w-8 h-8 text-bfs-navy animate-spin" />
    </div>
    
    <div v-else class="max-w-2xl mx-auto bg-white rounded-lg shadow-sm border border-gray-200">
      <div class="px-6 py-4 border-b border-gray-100 bg-gray-50 flex items-center justify-between">
        <h3 class="font-semibold text-gray-800">Componen Budget</h3>
      </div>
      
      <div class="p-6 space-y-4">
        <!-- Bunga Budget Component -->
        <div class="grid grid-cols-4 items-center gap-4">
          <label class="text-sm font-medium text-gray-700 text-right">Bunga</label>
          <div class="col-span-3">
            <SearchSelect 
              v-model="form.bunga_budget_component"
              :options="budgetComponentOpts"
              placeholder="Select Bunga Component..."
            />
          </div>
        </div>

        <!-- Pokok Budget Component -->
        <div class="grid grid-cols-4 items-center gap-4">
          <label class="text-sm font-medium text-gray-700 text-right">Pokok</label>
          <div class="col-span-3">
            <SearchSelect 
              v-model="form.pokok_budget_component"
              :options="budgetComponentOpts"
              placeholder="Select Pokok Component..."
            />
          </div>
        </div>
      </div>

      <div class="px-6 py-4 bg-gray-50 border-t border-gray-100 flex justify-end">
        <button 
          @click="save" 
          :disabled="isSaving"
          class="btn-primary flex items-center gap-2"
        >
          <Loader2 v-if="isSaving" class="w-4 h-4 animate-spin" />
          <Save v-else class="w-4 h-4" />
          Save
        </button>
      </div>
    </div>
  </Panel>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Save, Loader2 } from 'lucide-vue-next'
import Panel from '../../components/Panel.vue'
import SearchSelect from '../../components/SearchableSelect.vue'
import api from '../../services/api'
import { useAuthStore } from '../../stores/auth'
import Swal from 'sweetalert2'

const authStore = useAuthStore()

const loading = ref(false)
const isSaving = ref(false)
const budgetComponentOpts = ref([])

const form = ref({
  bunga_budget_component: null,
  pokok_budget_component: null
})

onMounted(async () => {
  await fetchMasterData()
  await fetchData()
})

const fetchMasterData = async () => {
  try {
    const res = await api.get('budget-component/budget-component/?component_type=bank_obligation')
    const results = res.data.results || res.data || []
    budgetComponentOpts.value = results.map(item => ({
      id: item.id,
      label: item.name
    }))
  } catch (error) {
    console.error('Failed to fetch budget components:', error)
  }
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await api.get('accounting/bank-obligation-setting/')
    form.value.bunga_budget_component = res.data.bunga_budget_component
    form.value.pokok_budget_component = res.data.pokok_budget_component
  } catch (error) {
    console.error('Failed to fetch settings:', error)
  } finally {
    loading.value = false
  }
}

const save = async () => {
  isSaving.value = true
  try {
    await api.put('accounting/bank-obligation-setting/', {
      bunga_budget_component: form.value.bunga_budget_component,
      pokok_budget_component: form.value.pokok_budget_component
    })
    Swal.fire({
      icon: 'success',
      title: 'Success',
      text: 'Bank Obligation settings updated successfully',
      timer: 1500,
      showConfirmButton: false
    })
  } catch (error) {
    Swal.fire('Error', 'Failed to update settings', 'error')
  } finally {
    isSaving.value = false
  }
}
</script>
