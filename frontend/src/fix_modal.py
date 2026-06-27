import re

def fix_modal():
    with open('c:/Traine/bfs-erp/frontend/src/components/purchase/CompletionCertificateFormModal.vue', 'r', encoding='utf-8') as f:
        content = f.read()

    # Import SearchableSelect
    if "import SearchableSelect" not in content:
        content = content.replace("import { usePeriodCheck } from '../../composables/usePeriodCheck'", "import { usePeriodCheck } from '../../composables/usePeriodCheck'\nimport SearchableSelect from '../../components/SearchableSelect.vue'")

    # Replace Vendor select with SearchableSelect
    content = re.sub(
        r'<select v-model="form\.vendor".*?>\s*<option.*?>.*?</option>\s*<option v-for="v in store\.validVendors".*?>\s*{{ v\.name }}\s*</option>\s*</select>',
        '''<SearchableSelect
              v-model="form.vendor"
              :options="store.validVendors"
              value-key="id"
              label-key="name"
              placeholder="Select Vendor"
              @change="onVendorChange"
              :disabled="isEdit"
            />''',
        content,
        flags=re.DOTALL
    )

    # Replace PO select with SearchableSelect
    # First, validPOs items are an object like { id: 1, po_number: 'PO-001', project: { site_name: 'xyz' } }
    # So we need a computed getter to format the label, or just use a custom options array.
    # We can add a watcher or computed property for poOptions.
    
    # Actually, SearchableSelect supports simple label-key, but if we want concatenated label like "PO-001 - Site", we should create a computed property.
    if 'poOptions' not in content:
        content = content.replace('const selectedRAPName = computed(() => {', '''const poOptions = computed(() => {
  return store.validPOs.map(po => ({
    id: po.id,
    label: `${po.po_number} - ${po.project?.site_name || ''}`
  }))
})

const selectedRAPName = computed(() => {''')

    content = re.sub(
        r'<select v-model="form\.po".*?>\s*<option.*?>.*?</option>\s*<option v-for="po in store\.validPOs".*?>\s*{{ po\.po_number }} - {{ po\.project\?\.site_name \|\| \'\' }}\s*</option>\s*</select>',
        '''<SearchableSelect
              v-model="form.po"
              :options="poOptions"
              value-key="id"
              label-key="label"
              placeholder="Select PO"
              @change="onPOChange"
              :disabled="isEdit || !form.vendor"
            />''',
        content,
        flags=re.DOTALL
    )

    # Default date today for document_date_from_vendor
    content = content.replace("document_date_from_vendor: ''", "document_date_from_vendor: new Date().toISOString().split('T')[0]")

    with open('c:/Traine/bfs-erp/frontend/src/components/purchase/CompletionCertificateFormModal.vue', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    fix_modal()
