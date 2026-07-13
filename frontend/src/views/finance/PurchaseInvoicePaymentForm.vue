<template>
  <div class="px-6 py-4 space-y-6">
    <div class="bg-blue-50 text-blue-800 text-xs px-4 py-3 rounded-lg border border-blue-200">
      Form for <strong>Purchase Invoice Payment</strong>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 bg-gray-50/50 p-4 rounded-xl border border-gray-100">
      <!-- Left Column -->
      <div class="space-y-4">
        <FormField label="Document Number">
          <input :value="form.document_number || ''" type="text" class="form-input bg-gray-100 cursor-not-allowed" placeholder="Auto Generated" disabled />
        </FormField>
        
        <FormField label="Date" required>
          <input v-model="form.date" type="date" class="form-input" />
        </FormField>

        <FormField label="Cash Flow Type ( Budget Component)">
          <input v-model="form.budget_component_name" type="text" class="form-input bg-gray-100 cursor-not-allowed" disabled />
        </FormField>

        <FormField label="Transaction Type" required>
          <SearchableSelect
            v-model="form.transaction_type"
            :options="transactionTypeOptions"
            placeholder="----- None -----"
            searchPlaceholder="Search transaction type..."
            valueKey="id"
            labelKey="label"
          />
        </FormField>

        <FormField label="DurationDueDate">
          <select v-model="form.duration_due_date" class="form-input bg-gray-100 cursor-not-allowed" disabled>
            <option value="">----- None -----</option>
            <option value="15">15 Days</option>
            <option value="30">30 Days</option>
            <option value="45">45 Days</option>
            <option value="60">60 Days</option>
          </select>
        </FormField>

        <FormField label="Invoice Date">
          <input v-model="form.invoice_date" type="date" class="form-input bg-gray-100 cursor-not-allowed" disabled />
        </FormField>
        
        <FormField label="Due Date">
          <input v-model="form.due_date" type="date" class="form-input bg-gray-100 cursor-not-allowed" disabled />
        </FormField>

        <FormField label="Description">
          <textarea v-model="form.description" class="form-input h-20 resize-none"></textarea>
        </FormField>
        
        <FormField label="Unpaid Amount">
          <input v-model="form.unpaid_amount" type="number" step="0.01" class="form-input bg-gray-100 cursor-not-allowed" disabled />
        </FormField>
        
        <FormField label="Amount (Requested)" required>
          <input v-model="form.amount" type="number" step="0.01" class="form-input" />
        </FormField>
      </div>

      <!-- Right Column -->
      <div class="space-y-4">
        <FormField label="Currency" required>
          <select v-model="form.currency" class="form-input">
            <option value="IDR">IDR</option>
            <option value="USD">USD</option>
            <option value="EUR">EUR</option>
            <option value="SGD">SGD</option>
          </select>
        </FormField>

        <FormField label="Project" required>
          <SearchableSelect
            v-model="form.project"
            :options="projectOptions"
            placeholder="----- None -----"
            searchPlaceholder="Search project..."
            valueKey="id"
            labelKey="label"
          />
        </FormField>

        <FormField label="Payment To">
          <SearchableSelect
            v-model="form.payment_to"
            :options="paymentToOptions"
            placeholder="----- None -----"
            searchPlaceholder="Search payment to..."
            valueKey="id"
            labelKey="label"
          />
        </FormField>

        <FormField label="Notes / Payment To">
          <textarea v-model="form.notes_payment_to" class="form-input h-16 resize-none bg-gray-100 cursor-not-allowed" disabled></textarea>
        </FormField>

        <FormField label="Notes">
          <textarea v-model="form.notes" class="form-input h-16 resize-none"></textarea>
        </FormField>

        <FormField label="Requestor Department">
          <SearchableSelect
            v-model="form.requestor_department"
            :options="departmentOptions"
            placeholder="----- None -----"
            searchPlaceholder="Search department..."
            valueKey="id"
            labelKey="label"
            :disabled="true"
          />
        </FormField>

        <FormField label="Purchase Invoice" required>
          <SearchableSelect
            v-model="form.purchase_invoice"
            :options="purchaseInvoiceOptions"
            placeholder="----- None -----"
            searchPlaceholder="Search purchase invoice..."
            valueKey="id"
            labelKey="label"
            :disabled="!form.project"
          />
        </FormField>

        <FormField label="Vendor Invoice Number">
          <input v-model="form.vendor_invoice_number" type="text" class="form-input bg-gray-100 cursor-not-allowed" disabled />
        </FormField>

        <FormField label="Tax Amount">
          <input v-model="form.tax_amount" type="number" step="0.01" class="form-input bg-gray-100 cursor-not-allowed" disabled />
        </FormField>
        
        <FormField label="Unpaid Tax Amount">
          <input v-model="form.unpaid_tax_amount" type="number" step="0.01" class="form-input bg-gray-100 cursor-not-allowed" disabled />
        </FormField>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import FormField from '../../components/FormField.vue'
import SearchableSelect from '../../components/SearchableSelect.vue'
import api from '../../services/api'

const props = defineProps({
  form: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['update:form'])

const transactionTypeOptions = ref([])
const projectOptions = ref([])
const paymentToOptions = ref([])
const departmentOptions = ref([])
const purchaseInvoiceOptions = ref([])
const durationOptions = ref([])

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
    const [trsTypeRes, projRes, paymentToRes, deptRes] = await Promise.all([
      api.get('master-type/transaction-type/'),
      api.get(`projects/projects/?usage=purchase_invoice_payment${props.form.id ? '&exclude_cbr=' + props.form.id : ''}&_t=${Date.now()}`),
      api.get('master-type/payment-to/'),
      api.get('org/departments/')
    ])

    transactionTypeOptions.value = (trsTypeRes.data.results || trsTypeRes.data).map(t => ({
      id: t.id,
      label: `${t.type_code} - ${t.type_name_en || t.type_name_id || t.type_name}`
    }))

    // Filter Project status 'start'
    projectOptions.value = (projRes.data.results || projRes.data)
      .filter(p => p.status === 'start' || p.status === 'START')
      .map(p => ({
        id: p.id,
        label: p.project_name
      }))

    // Filter Payment To that is not hidden
    paymentToOptions.value = (paymentToRes.data.results || paymentToRes.data)
      .filter(p => p.is_hide === false)
      .map(p => ({
        id: p.id,
        label: p.name,
        description: p.description
      }))

    const flatDepts = flattenDepartments(deptRes.data.results || deptRes.data)
    departmentOptions.value = flatDepts.map(d => ({
      id: d.id,
      label: `${d.code} - ${d.name}`
    }))
  } catch (error) {
    alert('Error fetching options: ' + (error.response ? error.response.status + ' ' + error.response.statusText : error.message))
    console.error('Error fetching options:', error)
  }
}

watch(() => props.form.payment_to, (newVal) => {
  if (newVal) {
    const selected = paymentToOptions.value.find(p => p.id === newVal)
    if (selected) {
      props.form.notes_payment_to = selected.description || ''
    }
  } else {
    props.form.notes_payment_to = ''
  }
})

const updateInvoiceDetails = async (newVal) => {
  if (newVal) {
    const selected = purchaseInvoiceOptions.value.find(p => p.id === newVal)
    if (selected && selected.raw) {
      const pi = selected.raw
      props.form.invoice_date = pi.invoice_date
      props.form.due_date = pi.due_date
      props.form.description = pi.notes || `Payment for invoice ${pi.invoice_number}`
      props.form.vendor_invoice_number = pi.vendor_invoice_number || '-'
      // Unpaid Amount Calculation
      let calculatedAmount = 0
      if (pi.details && Array.isArray(pi.details)) {
        calculatedAmount = pi.details.reduce((sum, d) => sum + (parseFloat(d.quantity || 0) * parseFloat(d.unit_price || 0)), 0)
      } else {
        // Fallback if details are somehow missing
        calculatedAmount = parseFloat(pi.grand_total) - parseFloat(pi.tax_amount || 0) 
      }
      const unpaid = calculatedAmount - parseFloat(pi.paid_amount || 0)
      props.form.unpaid_amount = unpaid.toFixed(2)
      props.form.tax_amount = parseFloat(pi.tax_amount || 0).toFixed(2)
      props.form.unpaid_tax_amount = parseFloat(pi.tax_amount || 0).toFixed(2) // We can assume unpaid tax is the whole tax for now
      
      // Auto-fill Amount only if not already set or it's new
      if (!props.form.id && !props.form.amount) {
        props.form.amount = unpaid.toFixed(2)
      }

      // Try to get Requestor Department from PO
      try {
        const poRes = await api.get(`purchase/po/${pi.po}/`)
        const po = poRes.data
        if (po.requestor_department) {
          props.form.requestor_department = po.requestor_department
        }
        
        // Calculate diff days for duration_due_date
        if (pi.invoice_date && pi.due_date) {
          const invDate = new Date(pi.invoice_date)
          const dueDate = new Date(pi.due_date)
          const diffTime = dueDate - invDate
          const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
          props.form.duration_due_date = diffDays.toString()
        } else {
          props.form.duration_due_date = ''
        }
      } catch (error) {
        console.error('Error fetching details:', error)
        props.form.duration_due_date = ''
      }
    }
  } else {
    props.form.invoice_date = ''
    props.form.due_date = ''
    props.form.description = ''
    props.form.vendor_invoice_number = ''
    props.form.unpaid_amount = '0.00'
    props.form.tax_amount = '0.00'
    props.form.unpaid_tax_amount = '0.00'
    props.form.requestor_department = null
    props.form.duration_due_date = ''
  }
}

watch(() => props.form.project, async (newVal, oldVal) => {
  const isInitialLoad = (oldVal === undefined || oldVal === null) && newVal !== null
  if (!isInitialLoad) {
    props.form.purchase_invoice = null
  }
  purchaseInvoiceOptions.value = []
  if (newVal) {
    try {
      // Fetch POs connected to this project
      const poRes = await api.get(`purchase/po/?project=${newVal}`)
      const pos = (poRes.data.results || poRes.data)
      const poIds = pos.map(po => po.id)

      // Fetch PIs connected to those POs
      if (poIds.length > 0) {
        const piRes = await api.get(`purchase/purchase-invoices/?po__in=${poIds.join(',')}`)
        purchaseInvoiceOptions.value = (piRes.data.results || piRes.data)
          .map(pi => ({
            id: pi.id,
            label: pi.invoice_number,
            raw: pi
          }))
      }

      // Fetch RAP for this project
      const rapRes = await api.get(`projects/raps/?project=${newVal}`)
      const raps = rapRes.data.results || rapRes.data
      if (raps && raps.length > 0) {
        props.form.budget_component = raps[0].budget_component || null
        props.form.budget_component_name = raps[0].budget_component_name || ''
      }
      
      // Inject initial purchase invoice if it's an edit and it wasn't fetched
      if (isInitialLoad && props.form.purchase_invoice) {
        const exists = purchaseInvoiceOptions.value.find(p => p.id === props.form.purchase_invoice)
        if (!exists) {
          purchaseInvoiceOptions.value.push({
            id: props.form.purchase_invoice,
            label: props.form.purchase_invoice_display || `Invoice ID: ${props.form.purchase_invoice}`,
            raw: null
          })
        }
      }
      
      // Update invoice details if we already have one selected
      if (props.form.purchase_invoice) {
        updateInvoiceDetails(props.form.purchase_invoice)
      }
    } catch (error) {
      console.error('Error fetching data for project:', error)
    }
  }
}, { immediate: true })

watch(() => props.form.purchase_invoice, async (newVal) => {
  updateInvoiceDetails(newVal)
})

onMounted(() => {
  fetchOptions()
})
</script>
