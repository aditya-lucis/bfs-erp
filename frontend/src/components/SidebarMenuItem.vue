<template>
  <div>
    <div
      v-if="hasChildren"
      class="flex items-center justify-between px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 cursor-pointer select-none transition-colors"
      :style="{ paddingLeft: `${16 + depth * 12}px` }"
      @click="isOpen = !isOpen"
    >
      <span class="truncate">{{ item.name }}</span>
      <ChevronDown
        :class="isOpen ? 'rotate-180' : ''"
        class="w-3.5 h-3.5 text-gray-400 flex-shrink-0 transition-transform duration-200"
      />
    </div>

    <router-link
      v-else
      :to="itemUrl"
      class="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
      :style="{ paddingLeft: `${16 + depth * 12}px` }"
      active-class="bg-bfs-gold/10 text-bfs-gold font-medium border-r-2 border-bfs-gold"
      @click="$emit('navigate', item)"
    >
      <span class="truncate">{{ item.name }}</span>
    </router-link>

    <Transition name="slide">
      <div v-if="isOpen && hasChildren">
        <SidebarMenuItem
          v-for="child in item.children"
          :key="child.id || child.name"
          :item="child"
          :depth="depth + 1"
          :moduleId="moduleId"
          @navigate="$emit('navigate', $event)"
        />
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ChevronDown } from 'lucide-vue-next'

const props = defineProps({
  item:     { type: Object, required: true },
  depth:    { type: Number, default: 0 },
  moduleId: { type: String, default: '' },
})

const isOpen = ref(false)
const hasChildren = computed(() => props.item.children?.length > 0)

const itemUrl = computed(() => {
  // Prioritas 1: url_path dari backend / menuData (pastikan tidak 'undefined' string)
  const urlPath = props.item.url_path?.trim()
  if (urlPath && urlPath !== 'undefined') {
    return urlPath
  }

  // Prioritas 2: pakai module_code dari item, fallback ke moduleId prop
  const mod = (props.item.module_code?.trim() && props.item.module_code !== 'undefined')
    ? props.item.module_code.trim()
    : (props.moduleId?.trim() && props.moduleId !== 'undefined')
      ? props.moduleId.trim()
      : null

  if (!mod) {
    console.warn('[SidebarMenuItem] Missing module_code for item:', props.item.name, props.item)
    return '/'
  }

  return `/${mod}/${slugify(props.item.name)}`
})

function slugify(text) {
  return (text || '')
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '')
}
</script>

<script>
export default { name: 'SidebarMenuItem' }
</script>

<style scoped>
.slide-enter-active, .slide-leave-active { transition: all 0.2s ease; overflow: hidden; }
.slide-enter-from, .slide-leave-to { max-height: 0; opacity: 0; }
.slide-enter-to, .slide-leave-from { max-height: 1000px; opacity: 1; }
</style>