<template>
  <div :class="[$attrs.class]">
    <label class="block text-[11px] font-semibold text-gray-500 tracking-wide uppercase mb-1.5">
      {{ label }}
      <span v-if="required" class="text-red-400 ml-0.5">*</span>
    </label>
    <slot />
    <p v-if="error" class="mt-1 text-xs text-red-500">{{ error }}</p>
  </div>
</template>

<script setup>
defineProps({
  label:    { type: String, required: true },
  required: { type: Boolean, default: false },
  error:    { type: String, default: '' },
})
</script>