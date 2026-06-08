<template>
  <Panel title="Customers" icon="Table">

    <!-- Toolbar -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
      <div class="flex items-center gap-2 flex-wrap">
        <select
          v-model="filterStatus"
          @change="load"
          class="text-sm border border-gray-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-bfs-gold/40"
        >
          <option value="">All Status</option>
          <option value="open">Active</option>
          <option value="closed">Closed</option>
          <option value="hold">Hold</option>
        </select>

        <div class="relative">
          <Search class="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-400" />
          <input
            v-model="search"
            @keyup.enter="load"
            type="text"
            placeholder="Cari kode / nama..."
            class="pl-8 pr-3 py-1.5 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-bfs-gold/40 w-56"
          />
        </div>

        <button @click="load" class="btn-secondary text-xs">Search</button>
      </div>

      <button
        v-if="canCreate"
        @click="openCreate"
        class="btn-primary text-xs flex items-center gap-1.5"
      >
        <Plus class="w-3.5 h-3.5" /> New Customer
      </button>
    </div>

    <!-- Loading -->
    <div v-if="store.loading" class="flex justify-center py-16">
      <Loader2 class="w-6 h-6 animate-spin text-bfs-gold" />
    </div>

    <!-- Error -->
    <div v-else-if="store.error" class="text-center py-10 text-red-500 text-sm">
      Gagal memuat data customer.
    </div>

    <!-- Table -->
    <div v-else class="border border-gray-200 rounded-xl overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 border-b border-gray-200">
          <tr>
            <th class="text-left px-4 py-2.5 text-[11px] font-semibold text-gray-500 uppercase tracking-wide w-12">No</th>
            <th class="text-left px-4 py-2.5 text-[11px] font-semibold text-gray-500 uppercase tracking-wide">Customer Code</th>
            <th class="text-left px-4 py-2.5 text-[11px] font-semibold text-gray-500 uppercase tracking-wide">Customer Name</th>
            <th class="text-left px-4 py-2.5 text-[11px] font-semibold text-gray-500 uppercase tracking-wide">City</th>
            <th class="text-left px-4 py-2.5 text-[11px] font-semibold text-gray-500 uppercase tracking-wide">Phone</th>
            <th class="text-left px-4 py-2.5 text-[11px] font-semibold text-gray-500 uppercase tracking-wide">Currency</th>
            <th class="text-left px-4 py-2.5 text-[11px] font-semibold text-gray-500 uppercase tracking-wide">Status</th>
            <th class="px-4 py-2.5 text-right text-[11px] font-semibold text-gray-500 uppercase tracking-wide">Action</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-if="!store.customers.length">
            <td colspan="8" class="text-center py-10 text-gray-400">Tidak ada data</td>
          </tr>
          <tr
            v-for="(row, i) in store.customers"
            :key="row.id"
            class="hover:bg-gray-50/80 transition-colors"
          >
            <td class="px-4 py-2.5 text-gray-500">{{ i + 1 }}</td>
            <td class="px-4 py-2.5">
              <button
                @click="openDetail(row)"
                class="font-mono text-xs text-bfs-navy hover:text-bfs-gold font-medium transition-colors"
              >
                {{ row.code }}
              </button>
            </td>
            <td class="px-4 py-2.5 text-gray-800">{{ row.title }} {{ row.name }}</td>
            <td class="px-4 py-2.5 text-gray-600">{{ row.city }}</td>
            <td class="px-4 py-2.5 text-gray-600">{{ row.phone_1 }}</td>
            <td class="px-4 py-2.5 text-gray-600">{{ row.currency }}</td>
            <td class="px-4 py-2.5">
              <span :class="statusClass(row.status)">{{ row.status }}</span>
            </td>
            <td class="px-4 py-2.5 text-right">
              <div class="flex items-center justify-end gap-1">
                <button
                  v-if="canUpdate"
                  @click="openEdit(row)"
                  class="p-1.5 text-gray-400 hover:text-bfs-gold rounded transition-colors"
                  title="Edit"
                >
                  <Pencil class="w-3.5 h-3.5" />
                </button>
                <button
                  v-if="canDelete"
                  @click="confirmDelete(row)"
                  class="p-1.5 text-gray-400 hover:text-red-500 rounded transition-colors"
                  title="Nonaktifkan"
                >
                  <Trash2 class="w-3.5 h-3.5" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <CustomerFormModal
      v-if="showForm"
      :customer="selectedCustomer"
      @close="showForm = false"
      @saved="onSaved"
    />
  </Panel>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Swal from 'sweetalert2'
import { Plus, Pencil, Trash2, Search, Loader2 } from 'lucide-vue-next'
import { useSalesStore } from '../../stores/sales.js'
import { usePermission } from '../../composables/usePermission.js'
import { useToast } from '../../composables/useToast.js'
import Panel from '../../components/Panel.vue'
import CustomerFormModal from '../../components/sales/CustomerFormModal.vue'

const store = useSalesStore()
const toast = useToast()
const { canCreate, canUpdate, canDelete } = usePermission('SALES-CUSTOMER')

const filterStatus = ref('open')
const search = ref('')
const showForm = ref(false)
const selectedCustomer = ref(null)

function load() {
  store.fetchCustomers({
    status: filterStatus.value || undefined,
    search: search.value || undefined,
  })
}

onMounted(load)

function openCreate() {
  selectedCustomer.value = null
  showForm.value = true
}

function openEdit(row) {
  selectedCustomer.value = row
  showForm.value = true
}

function openDetail(row) {
  selectedCustomer.value = row
  showForm.value = true
}

function onSaved() {
  showForm.value = false
  load()
}

async function confirmDelete(row) {
  const result = await Swal.fire({
    title: `Nonaktifkan ${row.code}?`,
    text: 'Customer akan di-set Closed.',
    icon: 'warning',
    showCancelButton: true,
    confirmButtonText: 'Ya, nonaktifkan',
    cancelButtonText: 'Batal',
  })
  if (!result.isConfirmed) return

  try {
    await store.deleteCustomer(row.id)
    toast.success('Customer berhasil dinonaktifkan.')
    load()
  } catch {
    toast.error('Gagal menonaktifkan customer.')
  }
}

function statusClass(s) {
  return {
    'inline-flex px-2 py-0.5 rounded-full text-xs font-medium': true,
    'bg-green-100 text-green-700': s === 'open',
    'bg-red-100 text-red-600': s === 'closed',
    'bg-yellow-100 text-yellow-700': s === 'hold',
  }
}
</script>
