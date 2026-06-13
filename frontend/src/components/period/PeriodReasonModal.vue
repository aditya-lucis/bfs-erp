<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/45 backdrop-blur-xs" @click.self="$emit('cancel')">
        <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden transform transition-all animate-in fade-in zoom-in-95 duration-200">
          
          <!-- Header -->
          <div class="flex items-center gap-4 px-6 py-5 text-white" :class="isClosing ? 'bg-gradient-to-r from-red-600 to-rose-700' : 'bg-gradient-to-r from-emerald-600 to-teal-700'">
            <div class="w-11 h-11 bg-white/20 rounded-full flex items-center justify-center text-xl shrink-0">
              <Lock v-if="isClosing" class="w-5 h-5 text-white" />
              <Unlock v-else class="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 class="font-bold text-base tracking-wide">{{ isClosing ? 'Close Period' : 'Open Period' }}</h3>
              <p class="text-xs text-white/85 mt-0.5">{{ periodLabel }}</p>
            </div>
            <button @click="$emit('cancel')" class="ml-auto p-1.5 rounded-full hover:bg-white/10 text-white/80 hover:text-white transition-colors">
              <X class="w-4 h-4" />
            </button>
          </div>

          <!-- Body -->
          <div class="p-6 space-y-4">
            <div class="flex gap-3 p-4 rounded-xl text-sm" :class="isClosing ? 'bg-red-50 border border-red-150 text-red-800' : 'bg-emerald-50 border border-emerald-150 text-emerald-800'">
              <AlertTriangle v-if="isClosing" class="w-5 h-5 text-red-600 shrink-0" />
              <Info v-else class="w-5 h-5 text-emerald-600 shrink-0" />
              <span>
                <template v-if="isClosing">
                  Menutup period ini akan <strong>mencegah</strong> transaksi baru diposting ke periode tersebut.
                </template>
                <template v-else font-normal>
                  Membuka period ini akan <strong>mengizinkan</strong> kembali transaksi diposting ke periode tersebut.
                </template>
              </span>
            </div>

            <div class="space-y-2">
              <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider">
                Alasan {{ isClosing ? 'Penutupan' : 'Pembukaan' }} <span class="text-red-500">*</span>
              </label>
              <textarea
                ref="reasonRef"
                v-model="reason"
                class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-bfs-gold/40 focus:border-bfs-gold transition-all bg-white disabled:bg-gray-50 disabled:cursor-not-allowed"
                :class="{ 'border-red-500 focus:ring-red-200': showError }"
                rows="3"
                :placeholder="isClosing
                  ? 'Contoh: Penutupan periode akhir bulan April 2026...'
                  : 'Contoh: Pembukaan kembali untuk koreksi jurnal...'"
                @input="showError = false"
                :disabled="loading"
              ></textarea>
              
              <div class="flex justify-between items-center mt-1">
                <p v-if="showError" class="flex items-center gap-1 text-xs text-red-500 font-medium">
                  <AlertCircle class="w-3.5 h-3.5" />
                  Alasan wajib diisi (minimal 3 karakter).
                </p>
                <div v-else></div>
                <p class="text-xs font-mono font-medium" :class="reason.length < 3 ? 'text-red-500' : 'text-emerald-600'">
                  {{ reason.length }} karakter
                </p>
              </div>
            </div>
          </div>

          <!-- Footer -->
          <div class="flex justify-end gap-2 px-6 py-4 bg-gray-50 border-t border-gray-100">
            <button class="px-4 py-2 border border-gray-200 text-gray-600 hover:bg-gray-150 rounded-lg transition-colors cursor-pointer text-sm font-medium flex items-center gap-1.5" @click="$emit('cancel')" :disabled="loading">
              <X class="w-4 h-4" /> Batal
            </button>
            <button
              class="px-5 py-2 text-white font-semibold rounded-lg transition-all cursor-pointer text-sm flex items-center gap-1.5 disabled:opacity-60 disabled:cursor-not-allowed shadow-md hover:shadow-lg"
              :class="isClosing ? 'bg-red-600 hover:bg-red-750' : 'bg-emerald-600 hover:bg-emerald-750'"
              @click="handleConfirm"
              :disabled="loading"
            >
              <Loader2 v-if="loading" class="w-4 h-4 animate-spin" />
              <template v-else>
                <Lock v-if="isClosing" class="w-4 h-4" />
                <Unlock v-else class="w-4 h-4" />
              </template>
              {{ isClosing ? 'Ya, Tutup Period' : 'Ya, Buka Period' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { Lock, Unlock, AlertTriangle, Info, X, AlertCircle, Loader2 } from 'lucide-vue-next'

const props = defineProps({
  show:        { type: Boolean, default: false },
  isClosing:   { type: Boolean, default: true },
  periodLabel: { type: String, default: '' },
  loading:     { type: Boolean, default: false },
})

const emit = defineEmits(['confirm', 'cancel'])

const reason    = ref('')
const showError = ref(false)
const reasonRef = ref(null)

watch(() => props.show, (val) => {
  if (val) {
    reason.value    = ''
    showError.value = false
    nextTick(() => reasonRef.value?.focus())
  }
})

function handleConfirm() {
  if (reason.value.trim().length < 3) {
    showError.value = true
    reasonRef.value?.focus()
    return
  }
  emit('confirm', reason.value.trim())
}
</script>

<style scoped>
.modal-enter-active, .modal-leave-active { transition: opacity 0.2s; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
</style>