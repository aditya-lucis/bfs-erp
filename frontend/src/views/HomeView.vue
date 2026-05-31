<template>
  <div class="min-h-[70vh] flex flex-col items-center justify-center">
    <!-- Welcome Text -->
    <div class="text-center mb-8">
      <h1 class="text-4xl font-bold text-[#4A90C2] mb-2">
        Welcome To BFS ERP
      </h1>
      <p class="text-lg text-[#4A90C2] font-medium">
        {{ currentDateTime }}
      </p>
    </div>

    <!-- Logo -->
    <div class="mb-8">
      <img 
        src="/bfs-logo.png" 
        alt="BFS ERP Logo" 
        class="w-auto object-contain drop-shadow-lg"
        style="height: 280px;"
      />
    </div>

    <!-- Footer -->
    <div class="mt-auto pt-8 text-center">
      <p class="text-[#4A90C2] font-medium">
        <span class="font-bold">BFS ERP</span> Application &copy; 2026
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const currentDateTime = ref('')

const updateDateTime = () => {
  const now = new Date()
  const options = { 
    weekday: 'long', 
    year: 'numeric', 
    month: '2-digit', 
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }
  currentDateTime.value = now.toLocaleDateString('en-US', options)
}

onMounted(() => {
  updateDateTime()
  setInterval(updateDateTime, 1000)
})
</script>