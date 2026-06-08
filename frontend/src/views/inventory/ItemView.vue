<template>
  <Panel title="List of Items" subtitle="Inventory | List of Items">

    <!-- Toolbar -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
      <!-- Filter tabs: All / RM / SP -->
      <div class="flex items-center gap-1 bg-gray-100 rounded-lg p-1">
        <button
          v-for="tab in typeTabs"
          :key="tab.value"
          @click="filterType = tab.value; filterCategory = ''"
          class="px-3 py-1.5 text-xs font-medium rounded-md transition-colors"
          :class="filterType === tab.value ? 'bg-white text-gray-800 shadow-sm' : 'text-gray-500 hover:text-gray-700'"
        >
          {{ tab.label }}
        </button>
      </div>

      <div class="flex items-center gap-2 flex-wrap">
        <!-- Category filter -->
        <select
          v-model="filterCategory"
          class="text-sm border border-gray-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-bfs-gold/40"
        >
          <option value="">Semua Category</option>
          <option
            v-for="cat in filteredCategoriesForFilter"
            :key="cat.id"
            :value="cat.id"
          >
            {{ cat.name }}
          </option>
        </select>

        <!-- Search -->
        <div class="relative">
          <Search class="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-400" />
          <input
            v-model="search"
            type="text"
            placeholder="Cari kode / nama item..."
            class="pl-8 pr-3 py-1.5 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-bfs-gold/40 w-52"
          />
        </div>

        <button
          v-if="canCreate"
          @click="openAddModal"
          class="btn-primary text-xs flex items-center gap-1.5"
        >
          <Plus class="w-3.5 h-3.5" /> New Item
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="store.isLoading" class="flex justify-center py-16">
      <Loader2 class="w-6 h-6 animate-spin text-bfs-gold" />
    </div>

    <!-- Table -->
    <div v-else-if="filteredItems.length" class="border border-gray-200 rounded-xl overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 border-b border-gray-200">
          <tr>
            <th class="text-left px-4 py-2.5 text-[11px] font-semibold text-gray-500 uppercase tracking-wide w-8"></th>
            <th class="text-left px-4 py-2.5 text-[11px] font-semibold text-gray-500 uppercase tracking-wide">Item Code</th>
            <th class="text-left px-4 py-2.5 text-[11px] font-semibold text-gray-500 uppercase tracking-wide">Item Name</th>
            <th class="text-left px-4 py-2.5 text-[11px] font-semibold text-gray-500 uppercase tracking-wide">Type</th>
            <th class="text-left px-4 py-2.5 text-[11px] font-semibold text-gray-500 uppercase tracking-wide">Unit</th>
            <th class="text-right px-4 py-2.5 text-[11px] font-semibold text-gray-500 uppercase tracking-wide">Unit Price</th>
            <th class="text-center px-4 py-2.5 text-[11px] font-semibold text-gray-500 uppercase tracking-wide">Service</th>
            <th class="text-center px-4 py-2.5 text-[11px] font-semibold text-gray-500 uppercase tracking-wide">Status</th>
            <th class="px-4 py-2.5 text-right text-[11px] font-semibold text-gray-500 uppercase tracking-wide">Action</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr
            v-for="item in filteredItems"
            :key="item.id"
            class="hover:bg-gray-50 transition-colors"
          >
            <!-- Thumbnail -->
            <td class="px-4 py-2">
              <div class="w-7 h-7 rounded-lg overflow-hidden bg-gray-100 flex items-center justify-center shrink-0">
                <img
                  v-if="item.image_url"
                  :src="item.image_url"
                  class="w-full h-full object-cover"
                  :alt="item.item_name"
                />
                <Package class="w-3.5 h-3.5 text-gray-400" v-else />
              </div>
            </td>
            <td class="px-4 py-2.5 font-mono text-xs text-gray-600">{{ item.item_code }}</td>
            <td class="px-4 py-2.5 font-medium text-gray-800 max-w-xs truncate">{{ item.item_name }}</td>
            <td class="px-4 py-2.5">
              <span
                class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold"
                :class="item.item_type === 'RM' ? 'bg-blue-50 text-blue-700' : 'bg-purple-50 text-purple-700'"
              >
                {{ item.item_type_label }}
              </span>
            </td>
            <td class="px-4 py-2.5 text-gray-500 text-xs">{{ item.unit_name }}</td>
            <td class="px-4 py-2.5 text-right text-sm">
              {{ Number(item.unit_price).toLocaleString('id-ID') }}
            </td>
            <td class="px-4 py-2.5 text-center">
              <CheckCircle v-if="item.is_service" class="w-4 h-4 text-green-500 mx-auto" />
              <span v-else class="text-gray-300">—</span>
            </td>
            <td class="px-4 py-2.5 text-center">
              <span
                class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold"
                :class="item.is_active ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-500'"
              >
                {{ item.is_active ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td class="px-4 py-2.5">
              <div class="flex items-center justify-end gap-1">
                <button
                  v-if="canUpdate"
                  @click="openEditModal(item)"
                  class="p-1.5 text-gray-400 hover:text-blue-500 hover:bg-blue-50 rounded transition-colors"
                  title="Edit"
                >
                  <Pencil class="w-3.5 h-3.5" />
                </button>
                <button
                  @click="openAccountModal(item)"
                  class="p-1.5 text-gray-400 hover:text-bfs-gold hover:bg-yellow-50 rounded transition-colors"
                  title="Link Account"
                >
                  <Link class="w-3.5 h-3.5" />
                </button>
                <button
                  v-if="canDelete"
                  @click="confirmDelete(item)"
                  class="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded transition-colors"
                  title="Hapus"
                >
                  <Trash2 class="w-3.5 h-3.5" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Empty state -->
    <div v-else class="flex flex-col items-center justify-center py-20 text-gray-400">
      <Package class="w-10 h-10 mb-3" />
      <p class="text-sm">Belum ada item.</p>
      <button v-if="canCreate" @click="openAddModal" class="mt-3 text-sm text-bfs-gold hover:underline">
        Tambah item pertama
      </button>
    </div>

    <!-- ── Item Form Modal ── -->
    <ItemFormModal
      ref="itemModalRef"
      :show="modal.show"
      :mode="modal.mode"
      :initial-data="modal.initialData"
      :categories="store.categories"
      :units="store.units"
      :choices="store.choices"
      @close="modal.show = false"
      @saved="handleSaved"
    />

    <!-- ── Account Link Modal ── -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="accountModal.show" class="fixed inset-0 z-50 overflow-y-auto">
          <div class="fixed inset-0 bg-black/40" @click="accountModal.show = false" />
          <div class="flex min-h-full items-start justify-center p-4 py-8">
            <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-xl z-10" @click.stop>

              <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
                <div>
                  <h3 class="text-base font-semibold text-gray-800">Link Account</h3>
                  <p class="text-xs text-gray-400 font-mono mt-0.5">{{ accountModal.item?.item_code }}</p>
                </div>
                <button @click="accountModal.show = false" class="text-gray-400 hover:text-gray-600">
                  <X class="w-5 h-5" />
                </button>
              </div>

              <!-- Existing links -->
              <div class="px-6 py-3 max-h-52 overflow-y-auto">
                <p class="text-[11px] font-semibold text-gray-500 uppercase tracking-wide mb-2">Account Links</p>
                <div v-if="accountLinks.length" class="space-y-2">
                  <div
                    v-for="link in accountLinks"
                    :key="link.id"
                    class="flex items-center justify-between gap-2 px-3 py-2 bg-gray-50 rounded-lg"
                  >
                    <div class="min-w-0">
                      <p class="text-xs font-medium text-gray-700">{{ link.purpose_label }}</p>
                      <p class="text-[10px] text-gray-400 font-mono truncate">
                        {{ link.account_number }} {{ link.account_name }}
                        <span class="ml-1 px-1.5 py-0.5 bg-gray-200 rounded text-gray-600">{{ link.currency }}</span>
                      </p>
                    </div>
                    <button
                      @click="handleDeleteLink(link)"
                      class="p-1 text-gray-400 hover:text-red-500 shrink-0"
                      title="Hapus link"
                    >
                      <Trash2 class="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
                <p v-else class="text-sm text-gray-400 text-center py-3">Belum ada account link.</p>
              </div>

              <!-- Add new link form -->
              <div class="px-6 py-4 border-t border-gray-100 space-y-3">
                <p class="text-[11px] font-semibold text-gray-500 uppercase tracking-wide">Tambah Link Baru</p>

                <div v-if="linkFormError" class="px-3 py-2 bg-red-50 border border-red-200 rounded-lg">
                  <p class="text-xs text-red-600">{{ linkFormError }}</p>
                </div>

                <div class="grid grid-cols-2 gap-3">
                  <FormField label="Purpose" required>
                    <select v-model="linkForm.purpose" class="form-input">
                      <option value="">— Pilih Purpose —</option>
                      <option
                        v-for="p in store.choices?.account_purposes"
                        :key="p.value"
                        :value="p.value"
                      >
                        {{ p.label }}
                      </option>
                    </select>
                  </FormField>
                  <FormField label="Currency">
                    <select v-model="linkForm.currency" class="form-input">
                      <option
                        v-for="c in store.choices?.currencies"
                        :key="c.value"
                        :value="c.value"
                      >
                        {{ c.label }}
                      </option>
                    </select>
                  </FormField>
                </div>

                <FormField label="Account (COA)" required>
                  <SearchableSelect
                    v-model="linkForm.account"
                    :groups="coaGrouped"
                    value-key="id"
                    label-key="account_name"
                    :search-keys="['account_number', 'account_name']"
                    placeholder="— Cari account... —"
                    search-placeholder="Ketik nomor atau nama akun..."
                    :has-error="!!linkFormError && !linkForm.account"
                  />
                </FormField>

                <div class="flex justify-end">
                  <button
                    @click="handleAddLink"
                    :disabled="isLinkSaving"
                    class="btn-primary text-xs flex items-center gap-1.5"
                  >
                    <Loader2 v-if="isLinkSaving" class="w-3.5 h-3.5 animate-spin" />
                    <Plus v-else class="w-3.5 h-3.5" />
                    Tambah Link
                  </button>
                </div>
              </div>

            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- ── Delete Modal ── -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="deleteModal.show" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-black/40" @click="deleteModal.show = false" />
          <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6 z-10">
            <div class="flex flex-col items-center text-center gap-3">
              <div class="w-12 h-12 rounded-full bg-red-100 flex items-center justify-center">
                <Trash2 class="w-6 h-6 text-red-500" />
              </div>
              <h3 class="text-base font-semibold text-gray-800">Nonaktifkan Item?</h3>
              <p class="text-sm text-gray-500">
                <span class="font-mono font-semibold text-gray-700">{{ deleteModal.target?.item_code }}</span>
                akan dinonaktifkan dan tidak akan muncul di daftar aktif.
              </p>
            </div>
            <div v-if="deleteModal.error" class="mt-3 px-3 py-2 bg-red-50 border border-red-200 rounded-lg">
              <p class="text-sm text-red-600 text-center">{{ deleteModal.error }}</p>
            </div>
            <div class="flex gap-2 mt-5">
              <button @click="deleteModal.show = false" class="btn-secondary text-sm flex-1">Batal</button>
              <button
                @click="handleDelete"
                :disabled="isSaving"
                class="flex-1 text-sm py-2 px-4 bg-red-500 hover:bg-red-600 text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-1.5 disabled:opacity-60"
              >
                <Loader2 v-if="isSaving" class="w-3.5 h-3.5 animate-spin" />
                <Trash2 v-else class="w-3.5 h-3.5" />
                Nonaktifkan
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

  </Panel>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useInventoryStore } from '../../stores/inventory.js'
import { useAccountingStore } from '../../stores/accounting.js'
import { usePermission } from '../../composables/usePermission.js'
import Panel from '../../components/Panel.vue'
import FormField from '../../components/FormField.vue'
import ItemFormModal from '../../components/inventory/ItemFormModal.vue'
import SearchableSelect from '../../components/SearchableSelect.vue'
import { useToast } from '../../composables/useToast.js'
import {
  Plus, Pencil, Trash2, X, Loader2,
  Search, Package, Link, CheckCircle,
} from 'lucide-vue-next'

const store          = useInventoryStore()
const accountingStore = useAccountingStore()
const { canCreate, canUpdate, canDelete } = usePermission('INV-ITEM')
const toast = useToast()

const isSaving    = ref(false)
const itemModalRef = ref(null)

// ── Filter & Search ────────────────────────────────────────────────────────
const filterType     = ref('ALL')
const filterCategory = ref('')
const search         = ref('')

const typeTabs = [
  { value: 'ALL', label: 'All' },
  { value: 'RM',  label: 'Raw Material' },
  { value: 'SP',  label: 'Supplies' },
]

const filteredCategoriesForFilter = computed(() => {
  if (filterType.value === 'ALL') return store.categories
  return store.categories.filter(c => c.item_type === filterType.value)
})

const filteredItems = computed(() => {
  let list = store.items
  if (filterType.value !== 'ALL') list = list.filter(i => i.item_type === filterType.value)
  if (filterCategory.value) list = list.filter(i => i.category === Number(filterCategory.value))
  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    list = list.filter(i =>
      i.item_code.toLowerCase().includes(q) ||
      i.item_name.toLowerCase().includes(q)
    )
  }
  return list
})

// ── Item Form Modal ────────────────────────────────────────────────────────
const modal = reactive({ show: false, mode: 'add', editId: null, initialData: null })

function openAddModal() {
  modal.show = true; modal.mode = 'add'
  modal.editId = null; modal.initialData = null
}

async function openEditModal(item) {
  // Fetch detail lengkap dulu biar semua field ter-populate
  try {
    const detail = await store.fetchItem(item.id)
    modal.show = true; modal.mode = 'edit'
    modal.editId = item.id; modal.initialData = detail
  } catch (err) {
    console.error('Gagal memuat detail item', err)
  }
}

async function handleSaved(payload) {
  itemModalRef.value?.setLoading(true)
  try {
    if (modal.mode === 'add') {
      await store.createItem(payload)
      toast.success('Item berhasil ditambahkan.')
    } else {
      await store.updateItem(modal.editId, payload)
      toast.success('Item berhasil diperbarui.')
    }
    modal.show = false
    await store.fetchItems()
  } catch (err) {
    itemModalRef.value?.setErrors(err)
    toast.error('Gagal menyimpan item. Periksa isian form.')
  } finally {
    itemModalRef.value?.setLoading(false)
  }
}

const deleteModal = reactive({ show: false, target: null, error: '' })

function confirmDelete(item) {
  deleteModal.target = item
  deleteModal.error  = ''
  deleteModal.show   = true
}

async function handleDelete() {
  isSaving.value    = true
  deleteModal.error = ''
  try {
    await store.deleteItem(deleteModal.target.id)
    deleteModal.show = false
    toast.success('Item berhasil dinonaktifkan.')
    await store.fetchItems()
  } catch (err) {
    deleteModal.error = err?.response?.data?.detail || 'Gagal menonaktifkan item.'
    toast.error(deleteModal.error)
  } finally {
    isSaving.value = false
  }
}

// ── Account Link Modal ─────────────────────────────────────────────────────
const accountModal  = reactive({ show: false, item: null })
const accountLinks  = ref([])
const linkForm      = reactive({ purpose: '', currency: 'ALL', account: null })
const linkFormError = ref('')
const isLinkSaving  = ref(false)

// COA flat dikelompokkan by account_group untuk optgroup
const coaGrouped = computed(() => {
  const flat = accountingStore.coaFlat.filter(a => a.is_postable && a.is_active)
  const groups = {}
  flat.forEach(acc => {
    const gname = acc.account_group_name || 'Lainnya'
    if (!groups[gname]) groups[gname] = []
    groups[gname].push(acc)
  })
  // PERBAIKAN: Ubah 'accounts' yang kanan menjadi 'options'
  return Object.entries(groups).map(([label, accounts]) => ({ label, options: accounts }))
})

async function openAccountModal(item) {
  accountModal.item = item
  accountModal.show = true
  linkFormError.value = ''
  Object.assign(linkForm, { purpose: '', currency: 'ALL', account: null })

  try {
    accountLinks.value = await store.fetchAccountLinks(item.id)
  } catch (err) {
    accountLinks.value = []
  }

  // Fetch flat COA kalau belum ada
  if (!accountingStore.coaFlat.length) {
    await accountingStore.fetchCoaFlat({ postable: 'true', active: 'true' })
  }
}

async function handleAddLink() {
  linkFormError.value = ''
  if (!linkForm.purpose) { linkFormError.value = 'Purpose wajib dipilih.'; return }
  if (!linkForm.account) { linkFormError.value = 'Account wajib dipilih.'; return }

  isLinkSaving.value = true
  try {
    await store.createAccountLink(accountModal.item.id, { ...linkForm })
    accountLinks.value = await store.fetchAccountLinks(accountModal.item.id)
    Object.assign(linkForm, { purpose: '', currency: 'ALL', account: null })
    toast.success('Account link berhasil ditambahkan.')
  } catch (err) {
    const data = err?.response?.data
    if (data && typeof data === 'object') {
      const msgs = Object.values(data).flat()
      linkFormError.value = msgs[0] || 'Gagal menambah link.'
    } else {
      toast.error('Gagal menambah account link.')
    }
  } finally {
    isLinkSaving.value = false
  }
}

async function handleDeleteLink(link) {
  try {
    await store.deleteAccountLink(accountModal.item.id, link.id)
    accountLinks.value = await store.fetchAccountLinks(accountModal.item.id)
    toast.success('Account link berhasil dihapus.')
  } catch (err) {
    linkFormError.value = err?.response?.data?.detail || 'Gagal menghapus link.'
    toast.error(linkFormError.value)
  }
}

// ── Init ───────────────────────────────────────────────────────────────────
onMounted(async () => {
  await Promise.all([
    store.fetchItems(),
    store.fetchCategories(),
    store.fetchUnits(),
    store.fetchChoices(),
  ])
})
</script>

<style scoped>
@reference "../../style.css";
.form-input {
  @apply w-full px-3 py-2 text-sm border border-gray-200 rounded-lg
         focus:outline-none focus:ring-2 focus:ring-bfs-gold/40 focus:border-bfs-gold
         transition-all bg-white disabled:bg-gray-50 disabled:cursor-not-allowed;
}
.btn-primary   { @apply px-4 py-2 bg-bfs-gold hover:bg-bfs-gold-dark text-white font-medium rounded-lg transition-colors disabled:opacity-60; }
.btn-secondary { @apply px-4 py-2 border border-gray-200 text-gray-600 hover:bg-gray-50 rounded-lg transition-colors; }
.modal-enter-active, .modal-leave-active { transition: opacity 0.2s; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
</style>