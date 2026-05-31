<template>
  <Panel title="Company Information" subtitle="Setting | Organizational Structure">

    <!-- Loading -->
    <div v-if="orgStore.isLoading && !orgStore.company" class="flex items-center justify-center py-20">
      <Loader2 class="w-8 h-8 animate-spin text-bfs-gold" />
    </div>

    <template v-else-if="orgStore.company">
      <!-- Alert success/error -->
      <Transition name="fade">
        <div v-if="saveStatus" 
          :class="saveStatus === 'success'
            ? 'bg-green-50 border-green-200 text-green-700'
            : 'bg-red-50 border-red-200 text-red-600'"
          class="mb-4 px-4 py-3 border rounded-lg flex items-center gap-2 text-sm"
        >
          <CheckCircle v-if="saveStatus === 'success'" class="w-4 h-4 flex-shrink-0" />
          <XCircle v-else class="w-4 h-4 flex-shrink-0" />
          <span>{{ saveStatus === 'success' ? 'Data perusahaan berhasil disimpan.' : 'Gagal menyimpan data.' }}</span>
        </div>
      </Transition>

      <form @submit.prevent="handleSave" class="space-y-6">

        <!-- ── Logo ── -->
        <div class="flex items-start gap-6 pb-6 border-b border-gray-100">
          <div class="w-28 h-28 border-2 border-dashed border-gray-200 rounded-xl flex items-center justify-center bg-gray-50 overflow-hidden flex-shrink-0">
            <img 
              v-if="logoPreview || orgStore.company.logo"
              :src="logoPreview || orgStore.company.logo"
              class="w-full h-full object-contain p-2"
            />
            <Building2 v-else class="w-10 h-10 text-gray-300" />
          </div>
          <div class="space-y-2 pt-2">
            <p class="text-sm font-medium text-gray-700">Company Logo</p>
            <label class="cursor-pointer inline-flex items-center gap-2 px-3 py-1.5 bg-white border border-gray-200 rounded-lg text-xs text-gray-600 hover:bg-gray-50 transition-colors">
              <Upload class="w-3.5 h-3.5" />
              Upload Logo
              <input type="file" accept="image/*" class="hidden" @change="handleLogoChange" />
            </label>
            <p class="text-xs text-gray-400">PNG, JPG maks. 2MB</p>
          </div>
        </div>

        <!-- ── Fields Grid ── -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-4">

          <FormField label="Company Code" required>
            <input v-model="form.company_code" type="text" class="form-input" placeholder="e.g. PMJR" />
          </FormField>

          <FormField label="Company Type">
            <input v-model="form.company_type" type="text" class="form-input" placeholder="e.g. Medical" />
          </FormField>

          <FormField label="Company Name" required class="md:col-span-2">
            <input v-model="form.company_name" type="text" class="form-input" placeholder="PT. ..." />
          </FormField>

          <FormField label="Company Tax Number">
            <input v-model="form.company_tax_number" type="text" class="form-input" />
          </FormField>

          <FormField label="Company Tax Date">
            <input v-model="form.company_tax_date" type="date" class="form-input" />
          </FormField>

          <FormField label="Opening Balance Date" required>
            <input v-model="form.opening_balance_date" type="date" class="form-input" />
          </FormField>

          <FormField label="Tax Serial Number">
            <input v-model="form.tax_serial_number" type="text" class="form-input" />
          </FormField>

          <FormField label="Company Address" class="md:col-span-2">
            <textarea v-model="form.company_address" rows="3" class="form-input resize-none" />
          </FormField>

          <FormField label="Company Address 2" class="md:col-span-2">
            <textarea v-model="form.company_address2" rows="2" class="form-input resize-none" />
          </FormField>

          <FormField label="Bank">
            <input v-model="form.bank" type="text" class="form-input" />
          </FormField>

          <FormField label="Account Number">
            <input v-model="form.account_number" type="text" class="form-input" />
          </FormField>

          <FormField label="Country">
            <input v-model="form.country" type="text" class="form-input" />
          </FormField>

          <FormField label="State / Province">
            <input v-model="form.state" type="text" class="form-input" />
          </FormField>

          <FormField label="Postal Code">
            <input v-model="form.postal_code" type="text" class="form-input" />
          </FormField>

          <FormField label="Phone">
            <input v-model="form.phone" type="text" class="form-input" />
          </FormField>

          <FormField label="Fax">
            <input v-model="form.fax" type="text" class="form-input" />
          </FormField>

          <FormField label="Email">
            <input v-model="form.email" type="email" class="form-input" />
          </FormField>

          <FormField label="Business Template">
            <select v-model="form.business_template" class="form-input">
              <option value="trading">Trading</option>
              <option value="manufacturing">Manufacturing</option>
              <option value="service">Service</option>
              <option value="medical">Medical</option>
            </select>
          </FormField>

          <FormField label="RAP Tolerance (%)">
            <input v-model.number="form.rap_tolerance" type="number" min="0" max="200" class="form-input" />
          </FormField>

          <!-- Read-only fields -->
          <FormField label="Period Frequency">
            <input :value="orgStore.company.period_frequency" type="text" class="form-input bg-gray-50" readonly />
          </FormField>

          <FormField label="Currency ID">
            <input :value="orgStore.company.currency_id" type="text" class="form-input bg-gray-50" readonly />
          </FormField>

          <!-- Holding checkbox -->
          <div class="md:col-span-2 flex items-center gap-3">
            <input 
              v-model="form.is_holding" 
              type="checkbox" 
              id="is_holding"
              class="w-4 h-4 rounded border-gray-300 text-bfs-gold focus:ring-bfs-gold"
            />
            <label for="is_holding" class="text-sm text-gray-700">Holding Company</label>
          </div>

        </div>

        <!-- ── Divider ── -->
        <div class="border-t border-gray-100 pt-4 flex items-center justify-between">
          <p class="text-xs text-gray-400">*) Required fields</p>
          <div class="flex gap-2">
            <button 
              type="button" 
              @click="resetForm"
              class="px-4 py-2 text-sm border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-50 transition-colors"
            >
              Reset
            </button>
            <button 
              type="submit"
              :disabled="orgStore.isLoading"
              class="px-5 py-2 text-sm bg-bfs-gold hover:bg-bfs-gold-dark text-white font-medium rounded-lg transition-colors flex items-center gap-2 disabled:opacity-60"
            >
              <Loader2 v-if="orgStore.isLoading" class="w-3.5 h-3.5 animate-spin" />
              <Save v-else class="w-3.5 h-3.5" />
              Update
            </button>
          </div>
        </div>

      </form>
    </template>

    <!-- Error state -->
    <div v-else class="flex flex-col items-center justify-center py-20 text-gray-400">
      <AlertCircle class="w-10 h-10 mb-3" />
      <p class="text-sm">Gagal memuat data perusahaan.</p>
      <button @click="orgStore.fetchCompany()" class="mt-3 text-sm text-bfs-gold hover:underline">
        Coba lagi
      </button>
    </div>

  </Panel>
</template>

<script setup>
import { ref, reactive, watch, onMounted } from 'vue'
import { useOrganizationStore } from '../../stores/organization.js'
import Panel from '../../components/Panel.vue'
import FormField from '../../components/FormField.vue'
import {
  Building2, Upload, Save, Loader2,
  CheckCircle, XCircle, AlertCircle
} from 'lucide-vue-next'

const orgStore   = useOrganizationStore()
const saveStatus = ref(null)   // null | 'success' | 'error'
const logoPreview = ref(null)
const logoFile    = ref(null)

// Form state — mirror dari company data
const form = reactive({
  company_code:         '',
  company_type:         '',
  company_name:         '',
  company_tax_number:   '',
  company_tax_date:     '',
  opening_balance_date: '',
  tax_serial_number:    '',
  company_address:      '',
  company_address2:     '',
  bank:                 '',
  account_number:       '',
  country:              '',
  state:                '',
  postal_code:          '',
  phone:                '',
  fax:                  '',
  email:                '',
  business_template:    'trading',
  rap_tolerance:        100,
  is_holding:           false,
})

// Populate form saat data company sudah tersedia
function populateForm(data) {
  Object.keys(form).forEach(key => {
    if (data[key] !== undefined && data[key] !== null) {
      form[key] = data[key]
    }
  })
}

// Watch company store → update form
watch(() => orgStore.company, (val) => {
  if (val) populateForm(val)
}, { immediate: true })

function resetForm() {
  if (orgStore.company) populateForm(orgStore.company)
  logoPreview.value = null
  logoFile.value    = null
}

function handleLogoChange(e) {
  const file = e.target.files[0]
  if (!file) return
  logoFile.value    = file
  logoPreview.value = URL.createObjectURL(file)
}

async function handleSave() {
  saveStatus.value = null

  // Kalau ada logo baru → pakai FormData
  let payload
  if (logoFile.value) {
    payload = new FormData()
    Object.entries(form).forEach(([k, v]) => payload.append(k, v))
    payload.append('logo', logoFile.value)
  } else {
    payload = { ...form }
  }

  const result = await orgStore.updateCompany(payload)
  saveStatus.value = result.success ? 'success' : 'error'

  // Auto-hide setelah 3 detik
  setTimeout(() => { saveStatus.value = null }, 3000)
}

onMounted(() => {
  if (!orgStore.company) orgStore.fetchCompany()
})
</script>

<style scoped>
/* Ganti "tailwindcss" dengan path relatif ke file CSS utamamu. */
/* Contoh di bawah ini mengasumsikan file CSS-mu ada di src/assets/main.css */
@reference "../../style.css";

.form-input {
  @apply w-full px-3 py-2 text-sm border border-gray-200 rounded-lg 
         focus:outline-none focus:ring-2 focus:ring-bfs-gold/40 focus:border-bfs-gold 
         transition-all bg-white;
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>