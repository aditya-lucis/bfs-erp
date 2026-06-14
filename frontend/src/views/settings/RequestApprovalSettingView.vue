<template>
  <Panel title="Request Approval Setting" subtitle="Setting | Document Setting">

    <div v-if="isBootstrapping" class="flex items-center justify-center py-20">
      <Loader2 class="w-8 h-8 animate-spin text-bfs-gold" />
    </div>

    <template v-else>
      <!-- Alert -->
      <Transition name="fade">
        <div
          v-if="alertMessage"
          :class="alertType === 'success'
            ? 'bg-green-50 border-green-200 text-green-700'
            : 'bg-red-50 border-red-200 text-red-600'"
          class="mb-4 px-4 py-3 border rounded-lg flex items-center gap-2 text-sm"
        >
          <CheckCircle v-if="alertType === 'success'" class="w-4 h-4 flex-shrink-0" />
          <XCircle v-else class="w-4 h-4 flex-shrink-0" />
          <span>{{ alertMessage }}</span>
        </div>
      </Transition>

      <!-- Header config -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6 pb-6 border-b border-gray-100">
        <FormField label="Document Name" required>
          <SearchableSelect
            v-model="form.document_code"
            :options="documentOptions"
            value-key="code"
            label-key="name"
            placeholder="Pilih dokumen"
            @update:model-value="handleHeaderChange"
          />
        </FormField>

        <FormField label="Position (Creator)" required>
          <SearchableSelect
            v-model="form.creator_position"
            :options="positionOptions"
            value-key="id"
            :label-fn="posLabel"
            placeholder="Pilih posisi pembuat"
            search-placeholder="Cari posisi..."
            @update:model-value="handleHeaderChange"
          />
        </FormField>

        <FormField label="Differentiate Approval base on">
          <div class="flex flex-col gap-2 pt-1">
            <label class="flex items-center gap-2 text-sm cursor-pointer">
              <input
                v-model="form.basis"
                type="radio"
                value="AMOUNT"
                class="text-bfs-gold focus:ring-bfs-gold"
              />
              Total Amount (After Disc &amp; Tax)
            </label>
            <label class="flex items-center gap-2 text-sm cursor-pointer">
              <input
                v-model="form.basis"
                type="radio"
                value="QUANTITY"
                class="text-bfs-gold focus:ring-bfs-gold"
              />
              Total Quantity
            </label>
          </div>
        </FormField>
      </div>

      <!-- Range blocks -->
      <div class="space-y-4 mb-6">
        <div
          v-for="(block, blockIdx) in form.ranges"
          :key="block._key"
          class="border border-gray-200 rounded-xl p-4 bg-gray-50/50"
        >
          <div class="flex items-center gap-2 mb-4">
            <button
              type="button"
              class="w-8 h-8 flex items-center justify-center rounded-lg border border-gray-200 bg-white hover:bg-gray-50 text-gray-600"
              title="Tambah range"
              @click="addRange(blockIdx)"
            >
              <Plus class="w-4 h-4" />
            </button>
            <button
              type="button"
              class="w-8 h-8 flex items-center justify-center rounded-lg border border-gray-200 bg-white hover:bg-gray-50 text-gray-600 disabled:opacity-40"
              title="Hapus range"
              :disabled="form.ranges.length <= 1"
              @click="removeRange(blockIdx)"
            >
              <Minus class="w-4 h-4" />
            </button>
            <span class="text-sm font-medium text-gray-600 ml-2">Range {{ blockIdx + 1 }}</span>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
            <FormField :label="form.basis === 'AMOUNT' ? 'From (Rp)' : 'From'">
              <input
                v-model.number="block.from_value"
                type="number"
                min="0"
                step="0.01"
                class="form-input"
              />
            </FormField>
            <FormField :label="form.basis === 'AMOUNT' ? 'To (Rp)' : 'To'">
              <input
                v-model.number="block.to_value"
                type="number"
                min="0"
                step="0.01"
                class="form-input"
              />
            </FormField>
            <FormField label="Step of Approval">
              <select
                v-model.number="block.step_count"
                class="form-input"
                @change="syncSteps(block)"
              >
                <option v-for="n in 10" :key="n" :value="n">{{ n }}</option>
              </select>
            </FormField>
          </div>

          <div class="space-y-3">
            <div
              v-for="(step, stepIdx) in block.steps"
              :key="stepIdx"
              class="grid grid-cols-1 md:grid-cols-12 gap-3 items-end bg-white rounded-lg p-3 border border-gray-100"
            >
              <div class="md:col-span-1 text-sm font-medium text-gray-500 pb-2">
                Step {{ step.step_number }}
              </div>
              <FormField label="Role" class="md:col-span-4">
                <select v-model="step.role" class="form-input">
                  <option v-for="role in approvalStore.approvalRoles" :key="role.code" :value="role.code">
                    {{ role.name }}
                  </option>
                </select>
              </FormField>
              <FormField label="Position" class="md:col-span-7">
                <SearchableSelect
                  v-model="step.position"
                  :options="positionOptions"
                  value-key="id"
                  :label-fn="posLabel"
                  placeholder="Pilih posisi approver"
                  search-placeholder="Cari posisi..."
                />
              </FormField>
            </div>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex items-center gap-3 mb-8">
        <button
          type="button"
          class="px-5 py-2 bg-bfs-gold text-white rounded-lg text-sm font-medium hover:bg-bfs-gold/90 disabled:opacity-50"
          :disabled="!canCreate && !canUpdate || approvalStore.isLoading"
          @click="handleSave"
        >
          <Loader2 v-if="approvalStore.isLoading" class="w-4 h-4 animate-spin inline mr-1" />
          Add
        </button>
        <button
          type="button"
          class="px-5 py-2 border border-gray-200 rounded-lg text-sm text-gray-600 hover:bg-gray-50"
          @click="handleReset"
        >
          Reset
        </button>
      </div>

      <!-- Saved matrices list -->
      <div class="border-t border-gray-100 pt-6">
        <h4 class="text-sm font-semibold text-gray-700 mb-4">Matrix Approval Tersimpan</h4>

        <div v-if="approvalStore.isLoading && !approvalStore.matrices.length" class="text-center py-8 text-gray-400 text-sm">
          Memuat data...
        </div>
        <div v-else-if="!approvalStore.matrices.length" class="text-center py-8 text-gray-400 text-sm">
          Belum ada matrix approval.
        </div>
        <div v-else class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b border-gray-100 text-left text-gray-500">
                <th class="py-2 pr-4 font-medium">Dokumen</th>
                <th class="py-2 pr-4 font-medium">Posisi Creator</th>
                <th class="py-2 pr-4 font-medium">Basis</th>
                <th class="py-2 pr-4 font-medium">Range</th>
                <th class="py-2 font-medium text-right">Aksi</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="item in approvalStore.matrices"
                :key="item.id"
                class="border-b border-gray-50 hover:bg-gray-50/50"
              >
                <td class="py-3 pr-4">
                  <div class="font-medium text-gray-800">{{ item.document_name }}</div>
                  <div class="text-xs text-gray-400">{{ item.document_code }}</div>
                </td>
                <td class="py-3 pr-4">
                  <div>{{ item.creator_position_name }}</div>
                  <div class="text-xs text-gray-400">{{ item.creator_department_name }}</div>
                </td>
                <td class="py-3 pr-4">{{ item.basis_display }}</td>
                <td class="py-3 pr-4">{{ item.range_count }} tier</td>
                <td class="py-3 text-right">
                  <button
                    type="button"
                    class="text-bfs-gold hover:underline mr-3"
                    @click="loadMatrix(item)"
                  >
                    Edit
                  </button>
                  <button
                    v-if="canDelete"
                    type="button"
                    class="text-red-500 hover:underline"
                    @click="handleDelete(item)"
                  >
                    Hapus
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </Panel>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Loader2, Plus, Minus, CheckCircle, XCircle } from 'lucide-vue-next'
import Panel from '../../components/Panel.vue'
import FormField from '../../components/FormField.vue'
import SearchableSelect from '../../components/SearchableSelect.vue'
import { useApprovalMatrixStore } from '../../stores/approvalMatrix.js'
import { useOrganizationStore } from '../../stores/organization.js'
import { usePermission } from '../../composables/usePermission.js'

const RBAC_CODE = 'SETTINGS-REQUEST-APPROVAL-SETTING'
const { canCreate, canUpdate, canDelete } = usePermission(RBAC_CODE)

const approvalStore = useApprovalMatrixStore()
const orgStore = useOrganizationStore()

const isBootstrapping = ref(true)
const alertMessage = ref('')
const alertType = ref('success')
let rangeKeyCounter = 0

function nextRangeKey() {
  rangeKeyCounter += 1
  return `range-${rangeKeyCounter}`
}

function createEmptyStep(stepNumber = 1) {
  const defaultRole = approvalStore.approvalRoles[0]?.code || 'PREPARED_BY'
  return {
    step_number: stepNumber,
    role: defaultRole,
    position: null,
  }
}

function createEmptyRange() {
  return {
    _key: nextRangeKey(),
    from_value: 0,
    to_value: 0,
    step_count: 1,
    steps: [createEmptyStep(1)],
  }
}

const form = ref({
  document_code: 'RAP',
  creator_position: null,
  basis: 'AMOUNT',
  ranges: [createEmptyRange()],
})

const documentOptions = computed(() =>
  approvalStore.documentTypes.map(d => ({ code: d.code, name: d.name }))
)

const positionOptions = computed(() =>
  orgStore.positions.map(p => ({
    id: p.id,
    code: p.code,
    name: p.name,
    department_name: p.department_name || p.department?.name || '',
  }))
)

function posLabel(pos) {
  if (!pos) return ''
  const dept = pos.department_name ? ` (${pos.department_name})` : ''
  return `${pos.name}${dept}`
}

function syncSteps(block) {
  const count = block.step_count
  const current = block.steps.length
  if (count > current) {
    for (let i = current + 1; i <= count; i++) {
      block.steps.push(createEmptyStep(i))
    }
  } else if (count < current) {
    block.steps = block.steps.slice(0, count)
  }
  block.steps.forEach((s, idx) => { s.step_number = idx + 1 })
}

function addRange(afterIdx) {
  const newBlock = createEmptyRange()
  form.value.ranges.splice(afterIdx + 1, 0, newBlock)
}

function removeRange(idx) {
  if (form.value.ranges.length <= 1) return
  form.value.ranges.splice(idx, 1)
}

function showAlert(message, type = 'success') {
  alertMessage.value = message
  alertType.value = type
  setTimeout(() => { alertMessage.value = '' }, 4000)
}

function buildPayload() {
  return {
    document_code: form.value.document_code,
    creator_position: form.value.creator_position,
    basis: form.value.basis,
    is_active: true,
    ranges: form.value.ranges.map((block, order) => ({
      from_value: block.from_value,
      to_value: block.to_value,
      order_no: order,
      steps: block.steps.map(step => ({
        step_number: step.step_number,
        role: step.role,
        position: step.position,
      })),
    })),
  }
}

function validateForm() {
  if (!form.value.document_code) return 'Pilih dokumen terlebih dahulu.'
  if (!form.value.creator_position) return 'Pilih posisi creator terlebih dahulu.'
  for (const block of form.value.ranges) {
    for (const step of block.steps) {
      if (!step.position) return 'Semua step harus memiliki posisi approver.'
    }
  }
  return null
}

async function handleSave() {
  const err = validateForm()
  if (err) {
    showAlert(err, 'error')
    return
  }
  try {
    await approvalStore.saveMatrix(buildPayload())
    showAlert('Matrix approval berhasil disimpan.')
    await approvalStore.fetchMatrices()
  } catch (e) {
    const msg = typeof approvalStore.error === 'string'
      ? approvalStore.error
      : approvalStore.error?.ranges || 'Gagal menyimpan matrix approval.'
    showAlert(Array.isArray(msg) ? msg.join(', ') : String(msg), 'error')
  }
}

function handleReset() {
  form.value = {
    document_code: 'RAP',
    creator_position: null,
    basis: 'AMOUNT',
    ranges: [createEmptyRange()],
  }
}

async function handleHeaderChange() {
  if (!form.value.document_code || !form.value.creator_position) return
  try {
    const data = await approvalStore.lookupMatrix(
      form.value.document_code,
      form.value.creator_position,
    )
    if (data) {
      loadMatrixFromDetail(data)
    } else {
      form.value.basis = 'AMOUNT'
      form.value.ranges = [createEmptyRange()]
    }
  } catch {
    // ignore lookup errors
  }
}

function loadMatrixFromDetail(data) {
  form.value.document_code = data.document_code
  form.value.creator_position = data.creator_position
  form.value.basis = data.basis
  form.value.ranges = data.ranges.map(block => ({
    _key: nextRangeKey(),
    from_value: parseFloat(block.from_value),
    to_value: parseFloat(block.to_value),
    step_count: block.steps.length,
    steps: block.steps.map(s => ({
      step_number: s.step_number,
      role: s.role,
      position: s.position,
    })),
  }))
  if (!form.value.ranges.length) {
    form.value.ranges = [createEmptyRange()]
  }
}

function loadMatrix(item) {
  const detail = approvalStore.matrices.find(m => m.id === item.id)
  if (!detail) return
  approvalStore.lookupMatrix(item.document_code, item.creator_position).then(data => {
    if (data) loadMatrixFromDetail(data)
  })
}

async function handleDelete(item) {
  if (!confirm(`Hapus matrix approval untuk ${item.document_name} — ${item.creator_position_name}?`)) return
  try {
    await approvalStore.deleteMatrix(item.id)
    showAlert('Matrix approval dihapus.')
    if (
      form.value.document_code === item.document_code &&
      form.value.creator_position === item.creator_position
    ) {
      handleReset()
    }
  } catch {
    showAlert('Gagal menghapus matrix approval.', 'error')
  }
}

onMounted(async () => {
  try {
    await Promise.all([
      approvalStore.fetchDocumentTypes(),
      approvalStore.fetchApprovalRoles(),
      orgStore.fetchPositions(),
      approvalStore.fetchMatrices(),
    ])
  } finally {
    isBootstrapping.value = false
  }
})
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
