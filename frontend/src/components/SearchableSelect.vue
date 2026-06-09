<template>
  <div class="relative" ref="containerRef">

    <!-- Trigger button -->
    <button
      type="button"
      @click="toggleDropdown"
      :disabled="disabled"
      class="w-full flex items-center justify-between gap-2 px-3 py-2 text-sm border rounded-lg transition-all bg-white text-left"
      :class="[
        disabled ? 'bg-gray-50 text-gray-400 cursor-not-allowed border-gray-200' : 'cursor-pointer hover:border-gray-300',
        isOpen ? 'border-bfs-gold ring-2 ring-bfs-gold/30' : 'border-gray-200',
        hasError ? 'border-red-300' : '',
      ]"
    >
      <!-- Selected value display -->
      <span class="flex-1 truncate" :class="selectedOption ? 'text-gray-800' : 'text-gray-400'">
        {{ selectedOption ? displayLabel(selectedOption) : placeholder }}
      </span>

      <div class="flex items-center gap-1 shrink-0">
        <!-- Clear button -->
        <span
          v-if="modelValue && clearable && !disabled"
          @click.stop="clearSelection"
          class="p-0.5 text-gray-400 hover:text-gray-600 rounded"
          title="Clear"
        >
          <X class="w-3.5 h-3.5" />
        </span>
        <ChevronDown
          class="w-4 h-4 text-gray-400 transition-transform duration-200"
          :class="{ 'rotate-180': isOpen }"
        />
      </div>
    </button>

    <!-- Dropdown -->
    <Teleport to="body">
      <div
        v-if="isOpen"
        ref="dropdownRef"
        class="fixed z-[9999] bg-white border border-gray-200 rounded-xl shadow-xl overflow-hidden"
        :style="dropdownStyle"
      >
        <!-- Search input -->
        <div class="p-2 border-b border-gray-100">
          <div class="relative">
            <Search class="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-400" />
            <input
              ref="searchInputRef"
              v-model="searchQuery"
              type="text"
              :placeholder="searchPlaceholder"
              class="w-full pl-8 pr-3 py-1.5 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-bfs-gold/30 focus:border-bfs-gold"
              @keydown.escape="closeDropdown"
              @keydown.arrow-down.prevent="moveHighlight(1)"
              @keydown.arrow-up.prevent="moveHighlight(-1)"
              @keydown.enter.prevent="selectHighlighted"
            />
          </div>
        </div>

        <!-- Options list -->
        <div
          ref="optionListRef"
          class="overflow-y-auto"
          :style="{ maxHeight: `${maxHeight}px` }"
        >
          <!-- Clear option -->
          <div
            v-if="clearable"
            @click="clearSelection"
            class="px-3 py-2 text-sm text-gray-400 cursor-pointer hover:bg-gray-50 italic border-b border-gray-100"
          >
            {{ placeholder }}
          </div>

          <!-- Group-based options (optgroup) -->
          <template v-if="hasGroups">
            <div v-for="group in filteredGroups" :key="group.label">
              <!-- Group header -->
              <div class="px-3 py-1.5 text-[10px] font-bold text-gray-400 uppercase tracking-wider bg-gray-50 sticky top-0">
                {{ group.label }}
                <span class="ml-1 font-normal normal-case">({{ group.options.length }})</span>
              </div>
              <!-- Group options -->
              <div
                v-for="(opt, idx) in group.options"
                :key="getOptionValue(opt)"
                @click="selectOption(opt)"
                @mouseenter="highlightedIndex = getGlobalIndex(group, idx)"
                class="px-3 py-2 text-sm cursor-pointer transition-colors"
                :class="{
                  'bg-yellow-50 text-bfs-gold font-medium': isSelected(opt),
                  'bg-gray-100': highlightedIndex === getGlobalIndex(group, idx) && !isSelected(opt),
                  'hover:bg-gray-50': !isSelected(opt) && highlightedIndex !== getGlobalIndex(group, idx),
                  'text-gray-800': !isSelected(opt),
                }"
                :ref="el => { if (el) optionRefs[getGlobalIndex(group, idx)] = el }"
              >
                <span class="font-mono text-xs text-gray-500 mr-2">{{ opt.account_number }}</span>
                {{ opt.account_name }}
              </div>
            </div>
          </template>

          <!-- Flat options -->
          <template v-else>
            <div
              v-for="(opt, idx) in filteredOptions"
              :key="getOptionValue(opt)"
              @click="selectOption(opt)"
              @mouseenter="highlightedIndex = idx"
              class="px-3 py-2 text-sm cursor-pointer transition-colors"
              :class="{
                'bg-yellow-50 text-bfs-gold font-medium': isSelected(opt),
                'bg-gray-100': highlightedIndex === idx && !isSelected(opt),
                'hover:bg-gray-50': !isSelected(opt) && highlightedIndex !== idx,
                'text-gray-800': !isSelected(opt),
              }"
              :ref="el => { if (el) optionRefs[idx] = el }"
            >
              <slot name="option" :option="opt">
                {{ displayLabel(opt) }}
              </slot>
            </div>
          </template>

          <!-- Empty state -->
          <div
            v-if="filteredOptions.length === 0 && !hasGroups"
            class="px-3 py-6 text-sm text-gray-400 text-center"
          >
            <Search class="w-5 h-5 mx-auto mb-1.5 opacity-40" />
            Tidak ada hasil untuk "<span class="font-medium">{{ searchQuery }}</span>"
          </div>
          <div
            v-else-if="hasGroups && filteredGroups.every(g => g.options.length === 0)"
            class="px-3 py-6 text-sm text-gray-400 text-center"
          >
            <Search class="w-5 h-5 mx-auto mb-1.5 opacity-40" />
            Tidak ada hasil untuk "<span class="font-medium">{{ searchQuery }}</span>"
          </div>
        </div>

        <!-- Footer info -->
        <div class="px-3 py-1.5 border-t border-gray-100 text-[10px] text-gray-400 text-right">
          {{ totalCount }} item ditemukan
        </div>
      </div>
    </Teleport>

  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { ChevronDown, X, Search } from 'lucide-vue-next'

const props = defineProps({
  // v-model value — ID atau value dari option yang dipilih
  modelValue:       { type: [Number, String, null], default: null },

  // Flat options array: [{ id, label, ... }]
  options:          { type: Array, default: () => [] },

  // Grouped options: [{ label: 'Group A', options: [...] }]
  // Kalau ini diisi, props.options diabaikan
  groups:           { type: Array, default: () => [] },

  // Field name untuk value dan label dari setiap option
  valueKey:         { type: String, default: 'id' },
  labelKey:         { type: String, default: 'label' },

  // Custom search function — default: search by labelKey
  searchKeys:       { type: Array, default: () => [] }, // field tambahan yang disearch

  placeholder:      { type: String, default: '— Pilih —' },
  searchPlaceholder: { type: String, default: 'Ketik untuk mencari...' },
  disabled:         { type: Boolean, default: false },
  clearable:        { type: Boolean, default: true },
  hasError:         { type: Boolean, default: false },
  maxHeight:        { type: Number, default: 280 },
})

const emit = defineEmits(['update:modelValue', 'change'])

// ── Refs ───────────────────────────────────────────────────────────────────
const containerRef   = ref(null)
const dropdownRef    = ref(null)
const searchInputRef = ref(null)
const optionListRef  = ref(null)
const optionRefs     = ref([])

const isOpen         = ref(false)
const searchQuery    = ref('')
const highlightedIndex = ref(-1)
const dropdownStyle  = ref({})

// ── Computed ───────────────────────────────────────────────────────────────
const hasGroups = computed(() => props.groups.length > 0)

// Semua options dalam satu flat array (untuk keyboard nav)
const allOptions = computed(() => {
  if (hasGroups.value) return props.groups.flatMap(g => g.options ?? [])
  return props.options
})

const filteredOptions = computed(() => {
  if (!searchQuery.value.trim()) return props.options
  const q = searchQuery.value.toLowerCase()
  return props.options.filter(opt => matchesSearch(opt, q))
})

const filteredGroups = computed(() => {
  if (!searchQuery.value.trim()) return props.groups.map(g => ({ ...g, options: g.options ?? [] }))
  const q = searchQuery.value.toLowerCase()
  return props.groups.map(group => ({
    ...group,
    options: (group.options ?? []).filter(opt => matchesSearch(opt, q)),
  })).filter(g => g.options.length > 0)
})

const totalCount = computed(() => {
  if (hasGroups.value) return filteredGroups.value.reduce((sum, g) => sum + g.options.length, 0)
  return filteredOptions.value.length
})

const selectedOption = computed(() => {
  if (props.modelValue === null || props.modelValue === undefined) return null
  return allOptions.value.find(opt => getOptionValue(opt) === props.modelValue) ?? null
})

// ── Helpers ────────────────────────────────────────────────────────────────
function getOptionValue(opt) {
  return opt[props.valueKey]
}

function displayLabel(opt) {
  if (!opt) return ''
  // Untuk COA: tampilkan account_number + account_name
  if (opt.account_number && opt.account_name) {
    return `${opt.account_number} ${opt.account_name}`
  }
  return opt[props.labelKey] ?? String(getOptionValue(opt))
}

function isSelected(opt) {
  return getOptionValue(opt) === props.modelValue
}

function matchesSearch(opt, query) {
  // Search di labelKey
  const label = displayLabel(opt).toLowerCase()
  if (label.includes(query)) return true
  // Search di searchKeys tambahan
  for (const key of props.searchKeys) {
    if (String(opt[key] ?? '').toLowerCase().includes(query)) return true
  }
  return false
}

// Untuk keyboard nav di grouped options — konversi ke global index
function getGlobalIndex(targetGroup, indexInGroup) {
  let offset = 0
  for (const group of filteredGroups.value) {
    if (group.label === targetGroup.label) return offset + indexInGroup
    offset += group.options.length
  }
  return offset + indexInGroup
}

// ── Dropdown position ──────────────────────────────────────────────────────
function calculatePosition() {
  if (!containerRef.value) return
  const rect = containerRef.value.getBoundingClientRect()
  const spaceBelow = window.innerHeight - rect.bottom
  const spaceAbove = rect.top
  const dropHeight = props.maxHeight + 80 // tambah search bar height

  const openAbove = spaceBelow < dropHeight && spaceAbove > spaceBelow

  dropdownStyle.value = {
    width:  `${rect.width}px`,
    left:   `${rect.left + window.scrollX}px`,
    ...(openAbove
      ? { bottom: `${window.innerHeight - rect.top + window.scrollY}px`, top: 'auto' }
      : { top: `${rect.bottom + window.scrollY + 4}px`, bottom: 'auto' }
    ),
  }
}

// ── Open / Close ───────────────────────────────────────────────────────────
function toggleDropdown() {
  if (props.disabled) return
  isOpen.value ? closeDropdown() : openDropdown()
}

function openDropdown() {
  isOpen.value     = true
  searchQuery.value = ''
  highlightedIndex.value = -1
  optionRefs.value = []

  nextTick(() => {
    calculatePosition()
    searchInputRef.value?.focus()
  })
}

function closeDropdown() {
  isOpen.value      = false
  searchQuery.value  = ''
  highlightedIndex.value = -1
}

// ── Selection ──────────────────────────────────────────────────────────────
function selectOption(opt) {
  emit('update:modelValue', getOptionValue(opt))
  emit('change', opt)
  closeDropdown()
}

function clearSelection() {
  emit('update:modelValue', null)
  emit('change', null)
  closeDropdown()
}

// ── Keyboard navigation ────────────────────────────────────────────────────
const flatFiltered = computed(() => {
  if (hasGroups.value) return filteredGroups.value.flatMap(g => g.options)
  return filteredOptions.value
})

function moveHighlight(direction) {
  const len = flatFiltered.value.length
  if (!len) return
  highlightedIndex.value = (highlightedIndex.value + direction + len) % len
  // Scroll into view
  nextTick(() => {
    optionRefs.value[highlightedIndex.value]?.scrollIntoView({ block: 'nearest' })
  })
}

function selectHighlighted() {
  if (highlightedIndex.value >= 0 && flatFiltered.value[highlightedIndex.value]) {
    selectOption(flatFiltered.value[highlightedIndex.value])
  }
}

// ── Click outside ──────────────────────────────────────────────────────────
function handleClickOutside(e) {
  if (
    containerRef.value && !containerRef.value.contains(e.target) &&
    dropdownRef.value  && !dropdownRef.value.contains(e.target)
  ) {
    closeDropdown()
  }
}

// Recalculate position on scroll/resize
function handleScroll() { if (isOpen.value) calculatePosition() }

onMounted(() => {
  document.addEventListener('mousedown', handleClickOutside)
  window.addEventListener('scroll', handleScroll, true)
  window.addEventListener('resize', handleScroll)
})

onUnmounted(() => {
  document.removeEventListener('mousedown', handleClickOutside)
  window.removeEventListener('scroll', handleScroll, true)
  window.removeEventListener('resize', handleScroll)
})
</script>