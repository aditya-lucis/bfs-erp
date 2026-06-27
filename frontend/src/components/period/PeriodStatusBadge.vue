<template>
  <!--
    PeriodStatusBadge — reusable period status indicator for forms.

    Usage:
      <PeriodStatusBadge :date="form.journal_date" />

      <PeriodStatusBadge
        :date="form.invoice_date"
        :levels="['MONTHLY', 'ACCOUNTING']"
        show-details
        @status-change="onStatusChange"
      />
  -->
  <div v-if="date" class="period-badge-wrapper">
    <!-- Loading -->
    <div v-if="loading" class="period-badge badge-loading">
      <i class="fas fa-circle-notch fa-spin"></i>
      <span>Memeriksa periode...</span>
    </div>

    <!-- Open -->
    <div v-else-if="status && status.is_open" class="period-badge badge-open">
      <i class="fas fa-lock-open"></i>
      <span>Period <strong>{{ periodName }}</strong> terbuka</span>
    </div>

    <!-- Closed -->
    <div v-else-if="status && !status.is_open" class="period-badge badge-closed">
      <i class="fas fa-lock"></i>
      <div class="badge-content">
        <span class="badge-main">
          Period <strong>{{ status.period_label }}</strong> sudah DITUTUP
        </span>
        <span class="badge-sub">
          Diblokir di level: <strong>{{ status.blocked_level }}</strong>
        </span>
      </div>
    </div>

    <!-- Details (expandable) -->
    <div v-if="showDetails && status && status.details" class="period-details">
      <div
        v-for="(detail, level) in status.details"
        :key="level"
        class="detail-row"
      >
        <span class="detail-level">{{ level }}</span>
        <span
          class="detail-status"
          :class="detail.is_open ? 'ds-open' : 'ds-closed'"
        >
          {{ detail.status || '-' }}
        </span>
        <span class="detail-label">{{ detail.period_label }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onUnmounted } from 'vue'
import api from '../../services/api.js'

const props = defineProps({
  date:        { type: String, default: '' },
  levels:      { type: Array,  default: null },
  showDetails: { type: Boolean, default: false },
  debounce:    { type: Number,  default: 400 },
})

const emit = defineEmits(['status-change'])

const status  = ref(null)
const loading = ref(false)
let   timer   = null

const periodName = computed(() => {
  if (!props.date) return ''
  const d = new Date(props.date)
  if (isNaN(d)) return props.date
  return d.toLocaleString('en', { month: 'long', year: 'numeric' })
})

async function fetchStatus(dateStr) {
  if (!dateStr) { status.value = null; return }

  loading.value = true
  try {
    const params = { date: dateStr }
    if (props.levels) params.levels = props.levels.join(',')
    const res = await api.get('/accounting/periods/status/', { params })
    status.value = res.data
    emit('status-change', res.data)
  } catch {
    status.value = null
  } finally {
    loading.value = false
  }
}

watch(() => props.date, (val) => {
  clearTimeout(timer)
  if (!val) { status.value = null; return }
  timer = setTimeout(() => fetchStatus(val), props.debounce)
}, { immediate: true })

onUnmounted(() => clearTimeout(timer))
</script>

<style scoped>
.period-badge-wrapper {
  display: flex; flex-direction: column; gap: 6px;
  margin-top: 4px;
}

.period-badge {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 500;
}

.badge-loading {
  background: #f3f4f6;
  color: #6b7280;
  border: 1px solid #e5e7eb;
}

.badge-open {
  background: #f0fdf4;
  color: #166534;
  border: 1px solid #bbf7d0;
}
.badge-open i { color: #16a34a; }

.badge-closed {
  background: #fef2f2;
  color: #991b1b;
  border: 1px solid #fecaca;
  align-items: flex-start;
}
.badge-closed i { color: #dc2626; margin-top: 2px; flex-shrink: 0; }

.badge-content { display: flex; flex-direction: column; gap: 2px; }
.badge-main    { font-size: 12px; }
.badge-sub     { font-size: 11px; opacity: 0.85; }

/* Details table */
.period-details {
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  overflow: hidden;
  font-size: 11px;
}
.detail-row {
  display: grid;
  grid-template-columns: 100px 70px 1fr;
  gap: 8px;
  padding: 5px 10px;
  border-bottom: 1px solid #f3f4f6;
}
.detail-row:last-child { border-bottom: none; }
.detail-row:nth-child(even) { background: #f9fafb; }

.detail-level  { font-weight: 600; color: #374151; }
.detail-status { font-weight: 700; border-radius: 4px; padding: 1px 6px; text-align: center; }
.ds-open   { color: #166534; background: #dcfce7; }
.ds-closed { color: #991b1b; background: #fee2e2; }
.detail-label  { color: #6b7280; }
</style>