/**
 * BFS ERP — Period Check Composable
 * src/composables/usePeriodCheck.js
 *
 * Vue 3 composable for real-time period validation in forms.
 * Calls backend API to check if a transaction date falls in an open period.
 *
 * Usage:
 *   import { usePeriodCheck } from '@/composables/usePeriodCheck'
 *
 *   const { periodStatus, checkPeriod, isPeriodOpen, periodMessage, periodLoading } = usePeriodCheck()
 *
 *   // In a watcher or input handler:
 *   watch(() => form.journal_date, async (date) => {
 *     await checkPeriod(date)
 *   })
 *
 *   // In template:
 *   <PeriodStatusBadge :date="form.journal_date" />
 *   <p v-if="!isPeriodOpen" class="error">{{ periodMessage }}</p>
 */

import { ref, computed } from 'vue'
import api from '../services/api.js'

export function usePeriodCheck(options = {}) {
    const {
        levels = null,   // null = all levels, or ['MONTHLY', 'ACCOUNTING']
        debounce = 400,    // ms to wait before calling API
        autoCheck = true,   // auto-check when date changes
    } = options

    // ── State ──────────────────────────────────────────────────────────────────
    const periodStatus = ref(null)    // full API response object
    const periodLoading = ref(false)
    const periodError = ref(null)
    let _debounceTimer = null

    // ── Computed ───────────────────────────────────────────────────────────────
    const isPeriodOpen = computed(() => {
        if (!periodStatus.value) return true   // not checked yet → allow
        return periodStatus.value.is_open
    })

    const isPeriodClosed = computed(() => !isPeriodOpen.value)

    const periodMessage = computed(() => {
        if (!periodStatus.value) return ''
        return periodStatus.value.message || ''
    })

    const blockedLevel = computed(() => periodStatus.value?.blocked_level || null)

    const periodLabel = computed(() => periodStatus.value?.period_label || '')

    const periodDetails = computed(() => periodStatus.value?.details || {})

    const statusByLevel = computed(() => {
        const details = periodDetails.value
        return {
            ANNUAL: details.ANNUAL?.status || null,
            QUARTER: details.QUARTER?.status || null,
            MONTHLY: details.MONTHLY?.status || null,
            ACCOUNTING: details.ACCOUNTING?.status || null,
        }
    })

    // ── Methods ────────────────────────────────────────────────────────────────

    async function checkPeriod(dateStr) {
        if (!dateStr) {
            periodStatus.value = null
            return null
        }

        periodLoading.value = true
        periodError.value = null

        try {
            const params = { date: dateStr }
            if (levels) params.levels = levels.join(',')

            const res = await api.get('/accounting/periods/status/', { params })
            periodStatus.value = res.data
            return res.data
        } catch (err) {
            periodError.value = err?.response?.data?.detail || 'Gagal memeriksa status period.'
            periodStatus.value = null
            return null
        } finally {
            periodLoading.value = false
        }
    }

    /** Debounced version — use in watch() to avoid too many API calls */
    function checkPeriodDebounced(dateStr) {
        clearTimeout(_debounceTimer)
        _debounceTimer = setTimeout(() => {
            checkPeriod(dateStr)
        }, debounce)
    }

    /** Bulk check multiple dates */
    async function checkPeriodBulk(dates) {
        if (!dates?.length) return null
        try {
            const body = { dates }
            if (levels) body.levels = levels
            const res = await api.post('/accounting/periods/status/bulk/', body)
            return res.data
        } catch (err) {
            console.error('[usePeriodCheck] bulk error:', err)
            return null
        }
    }

    /** Reset state */
    function resetPeriodCheck() {
        periodStatus.value = null
        periodLoading.value = false
        periodError.value = null
        clearTimeout(_debounceTimer)
    }

    /**
     * Guard function — use before form submit.
     * Returns true if period is open (allow submit), false if closed (block submit).
     * Also triggers API check if not yet checked.
     */
    async function guardSubmit(dateStr) {
        if (!dateStr) return true   // no date → don't block

        if (!periodStatus.value || periodStatus.value.date !== dateStr) {
            await checkPeriod(dateStr)
        }

        return isPeriodOpen.value
    }

    return {
        // State
        periodStatus,
        periodLoading,
        periodError,

        // Computed
        isPeriodOpen,
        isPeriodClosed,
        periodMessage,
        blockedLevel,
        periodLabel,
        periodDetails,
        statusByLevel,

        // Methods
        checkPeriod,
        checkPeriodDebounced,
        checkPeriodBulk,
        resetPeriodCheck,
        guardSubmit,
    }
}