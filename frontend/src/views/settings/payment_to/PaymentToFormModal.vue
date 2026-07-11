<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <!-- Overlay -->
        <div class="absolute inset-0 bg-bfs-navy/40 backdrop-blur-sm transition-opacity" @click="handleOverlayClick"></div>

        <!-- Modal Content -->
        <Transition name="modal-scale">
          <div v-if="show" class="relative w-full max-w-2xl bg-white rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
            
            <!-- Decoration -->
            <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-bfs-navy via-bfs-gold to-bfs-navy"></div>

            <!-- Header -->
            <div class="flex items-center justify-between px-6 py-5 border-b border-gray-100 shrink-0">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-full bg-bfs-navy/10 flex items-center justify-center">
                  <FileText class="w-4 h-4 text-bfs-navy" />
                </div>
                <h3 class="text-base font-bold text-gray-800">
                  {{ mode === 'add' ? 'Setting | Payment To | Add' : 'Setting | Payment To | Edit' }}
                </h3>
              </div>
              <button @click="$emit('close')" class="p-1.5 rounded-full text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors">
                <X class="w-4 h-4" />
              </button>
            </div>

            <!-- Scrollable Form Area -->
            <div class="flex-1 overflow-y-auto">
              <form @submit.prevent="saveData" class="px-6 py-6 space-y-4">
                
                <FormField label="Payment To Name" required>
                  <input v-model="form.name" type="text" class="form-input" placeholder="e.g. PT. Sokka Tama Fiber" required />
                </FormField>

                <div class="grid grid-cols-2 gap-4">
                  <FormField label="Bank Name" required>
                    <SearchableSelect
                      v-model="form.bank"
                      :options="bankOptions"
                      placeholder="Select Bank"
                      searchPlaceholder="Search banks..."
                      required
                    />
                  </FormField>
                  <FormField label="Bank Branch" required>
                    <input v-model="form.bank_branch" type="text" class="form-input" placeholder="e.g. KCU Bekasi" required />
                  </FormField>
                </div>

                <div class="grid grid-cols-2 gap-4">
                  <FormField label="Bank City" required>
                    <input v-model="form.bank_city" type="text" class="form-input" placeholder="e.g. Bekasi" required />
                  </FormField>
                  <FormField label="Account Number" required>
                    <input v-model="form.account_number" type="text" class="form-input" placeholder="e.g. 0663247023" required />
                  </FormField>
                </div>

                <div class="grid grid-cols-2 gap-4">
                  <FormField label="Account Name" required>
                    <input v-model="form.account_name" type="text" class="form-input" placeholder="e.g. PT. Sokka Tama Fiber" required />
                  </FormField>
                  <FormField label="Departement">
                    <SearchableSelect
                      v-model="form.department"
                      :options="departmentOptions"
                      placeholder="None"
                      searchPlaceholder="Search departements..."
                      clearable
                    />
                  </FormField>
                </div>

                <FormField label="Email" required>
                  <input v-model="form.email" type="email" class="form-input" placeholder="finance@sokkafiber.com" required />
                </FormField>

                <FormField label="Payment To Description" required>
                  <textarea v-model="form.description" class="form-input min-h-[100px] resize-y" placeholder="Enter description..." required></textarea>
                </FormField>

              </form>
            </div>

            <!-- Footer / Actions -->
            <div class="flex items-center justify-between px-6 py-5 bg-gray-50/80 border-t border-gray-100 shrink-0">
              <!-- Left side: Hide/UnHide buttons (Only in Edit mode) -->
              <div v-if="mode === 'edit'" class="flex gap-2">
                <button 
                  type="button" 
                  @click="toggleHide(true)" 
                  :disabled="form.is_hide"
                  class="text-sm font-semibold px-5 py-2.5 rounded-xl transition-colors shadow-sm"
                  :class="form.is_hide ? 'bg-gray-200 text-gray-400 cursor-not-allowed' : 'bg-red-50 text-red-600 hover:bg-red-100 border border-red-200'"
                >
                  Hide
                </button>
                <button 
                  type="button" 
                  @click="toggleHide(false)" 
                  :disabled="!form.is_hide"
                  class="text-sm font-semibold px-5 py-2.5 rounded-xl transition-colors shadow-sm"
                  :class="!form.is_hide ? 'bg-gray-200 text-gray-400 cursor-not-allowed' : 'bg-green-50 text-green-600 hover:bg-green-100 border border-green-200'"
                >
                  Un Hide
                </button>
              </div>
              <div v-else></div> <!-- Spacer -->

              <!-- Right side: Update/Save & Cancel -->
              <div class="flex gap-3">
                <button type="button" @click="$emit('close')" class="bg-white border border-gray-200 text-gray-700 hover:bg-gray-50 text-sm font-semibold px-5 py-2.5 rounded-xl transition-colors shadow-sm">
                  Cancel
                </button>
                <button 
                  type="button"
                  @click="saveData"
                  class="bg-bfs-navy text-white hover:bg-blue-900 text-sm font-semibold flex items-center gap-2 px-6 py-2.5 rounded-xl shadow-md shadow-bfs-navy/20 hover:shadow-lg hover:shadow-bfs-navy/30 transition-all duration-300 transform hover:-translate-y-0.5" 
                  :disabled="saving"
                >
                  <Save v-if="!saving" class="w-4 h-4" />
                  <div v-else class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  {{ saving ? 'Saving...' : (mode === 'edit' ? 'Update' : 'Save') }}
                </button>
              </div>
            </div>

          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { X, Save, FileText } from 'lucide-vue-next'
import FormField from '../../../components/FormField.vue'
import SearchableSelect from '../../../components/SearchableSelect.vue'
import api from '../../../services/api'
import Swal from 'sweetalert2'

const props = defineProps({
  show: Boolean,
  mode: String,
  initialData: Object
})

const emit = defineEmits(['close', 'saved'])

const saving = ref(false)

const form = ref({
  name: '',
  bank: null,
  bank_branch: '',
  bank_city: '',
  account_number: '',
  account_name: '',
  department: null,
  email: '',
  description: '',
  is_hide: false
})

const bankOptions = ref([])
const departmentOptions = ref([])

const flattenDepartments = (depts) => {
  let flat = []
  depts.forEach(d => {
    flat.push(d)
    if (d.children && d.children.length > 0) {
      flat = flat.concat(flattenDepartments(d.children))
    }
  })
  return flat
}

const fetchOptions = async () => {
  try {
    const [banksRes, deptsRes] = await Promise.all([
      api.get('master-type/master-bank/'),
      api.get('org/departments/')
    ])
    // Map to { id, label } format required by default SearchableSelect
    bankOptions.value = (banksRes.data.results || banksRes.data).map(b => ({
      id: b.id,
      label: `${b.bank_code} - ${b.bank_name}`
    }))
    
    const flatDepts = flattenDepartments(deptsRes.data.results || deptsRes.data)
    departmentOptions.value = flatDepts.map(d => ({
      id: d.id,
      label: `${d.code} - ${d.name}`
    }))
  } catch (error) {
    console.error('Error fetching options:', error)
  }
}

watch(() => props.show, (newVal) => {
  if (newVal) {
    if (props.mode === 'edit' && props.initialData) {
      form.value = {
        name: props.initialData.name,
        bank: props.initialData.bank,
        bank_branch: props.initialData.bank_branch,
        bank_city: props.initialData.bank_city,
        account_number: props.initialData.account_number,
        account_name: props.initialData.account_name,
        department: props.initialData.department,
        email: props.initialData.email,
        description: props.initialData.description,
        is_hide: props.initialData.is_hide
      }
    } else {
      // Reset form for add
      form.value = {
        name: '',
        bank: null,
        bank_branch: '',
        bank_city: '',
        account_number: '',
        account_name: '',
        department: null,
        email: '',
        description: '',
        is_hide: false
      }
    }
    fetchOptions()
  }
})

const handleOverlayClick = (e) => {
  if (e.target === e.currentTarget) {
    emit('close')
  }
}

const toggleHide = (hideStatus) => {
  form.value.is_hide = hideStatus
}

const saveData = async () => {
  if (!form.value.name || !form.value.bank || !form.value.bank_branch || !form.value.bank_city || !form.value.account_number || !form.value.account_name || !form.value.email || !form.value.description) {
    Swal.fire({
      icon: 'warning',
      title: 'Validation Error',
      text: 'Please fill all required fields.',
      confirmButtonColor: '#1e3a8a'
    })
    return
  }

  saving.value = true
  try {
    if (props.mode === 'add') {
      await api.post('master-type/payment-to/', form.value)
      Swal.fire({ icon: 'success', title: 'Created!', text: 'Payment To has been created.', timer: 1500, showConfirmButton: false })
    } else {
      await api.patch(`master-type/payment-to/${props.initialData.id}/`, form.value)
      Swal.fire({ icon: 'success', title: 'Updated!', text: 'Payment To has been updated.', timer: 1500, showConfirmButton: false })
    }
    emit('saved')
    emit('close')
  } catch (error) {
    console.error('Error saving:', error)
    Swal.fire({
      icon: 'error',
      title: 'Save Failed',
      text: 'Failed to save data. Please try again.',
      confirmButtonColor: '#1e3a8a'
    })
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-scale-enter-active,
.modal-scale-leave-active {
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.modal-scale-enter-from,
.modal-scale-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(10px);
}
</style>
