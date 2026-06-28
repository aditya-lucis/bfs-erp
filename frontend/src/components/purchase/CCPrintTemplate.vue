<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="show" class="fixed inset-0 z-50 overflow-y-auto print-modal-overlay">
        <!-- Backdrop -->
        <div class="fixed inset-0 bg-black/40 print:hidden" @click="$emit('close')" />
        
        <div class="flex min-h-full items-start justify-center p-4 py-8 print:p-0">
          <div class="relative bg-white shadow-2xl w-full max-w-[210mm] min-h-[297mm] z-10 print-modal-container" @click.stop>
            
            <!-- Web-only Header -->
            <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100 print:hidden sticky top-0 bg-white z-20 shadow-sm">
              <h3 class="text-base font-bold text-gray-800 flex items-center gap-2">
                <Printer class="w-5 h-5 text-bfs-gold" />
                Print Preview: {{ cc?.cc_number || 'CC' }}
              </h3>
              <div class="flex gap-2">
                <button @click="printDocument" class="btn-primary text-sm px-4 py-2 flex items-center gap-2 shadow-md bg-bfs-navy text-white rounded-lg hover:bg-opacity-90">
                  <Printer class="w-4 h-4" /> Print Document
                </button>
                <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600 bg-gray-100 hover:bg-gray-200 p-2 rounded-lg transition-colors">
                  <X class="w-5 h-5" />
                </button>
              </div>
            </div>

            <div class="p-4 bg-white text-black text-[11px] font-sans">
              <!-- Header: Company Info -->
              <div class="flex justify-between items-start border-b-2 border-black pb-2 mb-4">
                <div class="flex items-center space-x-4">
                  <img v-if="orgStore.company?.logo_url" :src="orgStore.company.logo_url" alt="Company Logo" class="h-16 object-contain" />
                  <div v-else class="h-16 w-16 bg-gray-200 flex items-center justify-center rounded">
                    <span class="text-[10px] text-gray-500 font-bold">LOGO</span>
                  </div>
                  <div class="text-[10px] leading-tight max-w-xs">
                    <p class="font-bold text-sm">{{ orgStore.company?.company_name || 'COMPANY NAME' }}</p>
                    <p>{{ printAddress }}</p>
                    <p>Phone: {{ orgStore.company?.company_phone || '-' }}</p>
                    <p>Email: {{ orgStore.company?.company_email || '-' }}</p>
                  </div>
                </div>
                <div class="text-right">
                  <h1 class="text-xl font-bold tracking-tight uppercase">Completion Certificate</h1>
                  <p class="text-base font-bold mt-1">No: {{ cc?.cc_number }}</p>
                </div>
              </div>

              <!-- Document Info Table -->
              <div class="mb-4">
                <table class="w-full border-collapse border border-black text-[11px]">
                  <tbody>
                    <tr>
                      <td class="border border-black px-2 py-1 font-semibold w-1/3 bg-gray-100">Vendor / Kontraktor</td>
                      <td class="border border-black px-2 py-1 font-semibold">{{ cc?.vendor_name || '-' }}</td>
                    </tr>
                    <tr>
                      <td class="border border-black px-2 py-1 w-1/3 bg-gray-100">No SPK / PO</td>
                      <td class="border border-black px-2 py-1">{{ cc?.po_number || '-' }}</td>
                    </tr>
                    <tr>
                      <td class="border border-black px-2 py-1 w-1/3 bg-gray-100">Nilai SPK / PO</td>
                      <td class="border border-black px-2 py-1">{{ formatCurrencyRaw(cc?.po_detail?.total_amount) }}</td>
                    </tr>
                    <tr>
                      <td class="border border-black px-2 py-1 w-1/3 bg-gray-100">RAP Name</td>
                      <td class="border border-black px-2 py-1">{{ cc?.po_detail?.rap_name || '-' }}</td>
                    </tr>
                    <tr>
                      <td class="border border-black px-2 py-1 w-1/3 bg-gray-100">Project / Site ID</td>
                      <td class="border border-black px-2 py-1">{{ cc?.po_detail?.project_name || '-' }}</td>
                    </tr>
                    <tr>
                      <td class="border border-black px-2 py-1 w-1/3 font-semibold bg-gray-100">Nilai yang ditagihkan (CC / BAST)</td>
                      <td class="border border-black px-2 py-1 font-semibold">{{ formatCurrencyRaw(cc?.amount) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- Paragraph Text -->
              <div class="mb-4 text-justify leading-relaxed">
                <p>
                  Pada hari ini <strong>{{ dayName }}</strong> tanggal <strong>{{ dateWord }}</strong> bulan <strong>{{ monthWord }}</strong> tahun <strong>{{ yearWord }}</strong>, telah dilakukan verifikasi terhadap Pekerjaan Material/Jasa sesuai dengan Berita Acara Selesai Pekerjaan yang terlampir, dengan hasil kelengkapan dokumen sebagai berikut:
                </p>
              </div>

              <!-- Documents Table -->
              <div class="mb-4">
                <table class="w-full border-collapse border border-black text-[11px]">
                  <thead>
                    <tr class="bg-gray-100">
                      <th class="border border-black px-2 py-1 w-10 text-center">No</th>
                      <th class="border border-black px-2 py-1 text-center">KELENGKAPAN DOKUMEN</th>
                      <th class="border border-black px-2 py-1 w-24 text-center">Status</th>
                      <th class="border border-black px-2 py-1 text-center">Keterangan</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(doc, idx) in cc?.documents" :key="idx">
                      <td class="border border-black px-2 py-1 text-center">{{ idx + 1 }}</td>
                      <td class="border border-black px-2 py-1">{{ doc.document_name || '-' }}</td>
                      <td class="border border-black px-2 py-1 text-center font-bold" :class="doc.is_available ? 'text-black' : 'text-gray-500'">
                        {{ doc.is_available ? 'Ada' : 'Tidak Ada' }}
                      </td>
                      <td class="border border-black px-2 py-1">{{ doc.document_number ? doc.document_number : '' }} {{ doc.keterangan ? '- ' + doc.keterangan : '' }}</td>
                    </tr>
                    <tr v-if="!cc?.documents?.length">
                      <td colspan="4" class="border border-black px-2 py-2 text-center text-gray-500">:: Tidak ada data yang ditampilkan ::</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- Closing Text -->
              <div class="mb-4 text-justify leading-relaxed space-y-2">
                <p>Pekerjaan tersebut dinyatakan telah selesai dan dapat diterima sesuai dengan syarat-syarat Kontrak/PO tersebut di atas. Tanggal penerimaan adalah sesuai dengan tanggal yang tercantum dibawah ini.</p>
                <p>Completion Certificate ini tidak menghapus kewajiban Supplier/Subkon untuk melaksanakan kewajibannya yang masih berlaku sesuai Kontrak/PO.</p>
                <p>Demikian Berita Acara ini dibuat dalam rangkap 2 (dua) dan akan digunakan sebagai dasar untuk proses lebih lanjut.</p>
              </div>
              
              <div class="mb-4">
                <p class="font-bold border-b border-black pb-1 mb-1">Tanggal Pemeriksaan: {{ formatDatePrint(cc?.document_date) }}</p>
                <div class="min-h-[60px] border border-black p-2 mt-2">
                  <p class="font-semibold mb-1">Catatan:</p>
                  <p>{{ cc?.description || '-' }}</p>
                </div>
              </div>

              <!-- Document Signatures Box -->
              <div v-if="cc?.approval_status && cc.approval_status !== 'draft'" class="mt-6 border border-gray-300 bg-white p-4">
                <div class="text-[9px] uppercase font-bold text-gray-400 mb-3 tracking-wider">Document Signatures (Persetujuan Dokumen)</div>
                <div class="flex flex-wrap gap-4 justify-start">
                  <div 
                    v-for="sig in signatures" 
                    :key="sig.id"
                    class="border border-gray-300 rounded p-3 text-center min-w-[150px] flex flex-col justify-between h-[130px] bg-white"
                  >
                    <!-- Header Position -->
                    <div>
                      <div class="text-[8px] uppercase font-bold text-gray-500 tracking-wider">
                        {{ sig.role_display }}
                      </div>
                      <div class="text-[9px] font-semibold text-gray-700">
                        {{ sig.position_name }}
                      </div>
                    </div>

                    <!-- Signature Area -->
                    <div class="flex-1 flex items-center justify-center py-1.5 h-12">
                      <template v-if="sig.is_signed">
                        <img v-if="sig.signature_draw && sig.signature_draw.startsWith('data:image')" :src="sig.signature_draw" alt="Signature" class="max-h-10 max-w-full object-contain" />
                        <img v-else-if="sig.signature_image" :src="sig.signature_image" alt="Signature" class="max-h-10 max-w-full object-contain" />
                        <div v-else class="px-2 py-0.5 border border-green-500 rounded text-[8px] text-green-600 font-serif italic font-bold border-double scale-95">SIGNED DIGITALLY</div>
                      </template>
                      <div v-else class="text-[9px] italic text-gray-300">Pending Signature</div>
                    </div>

                    <!-- Footer Name & Date -->
                    <div class="border-t border-gray-100 pt-1 text-[8px] text-gray-600 mt-1">
                      <div class="font-bold truncate text-gray-800" :title="sig.signer_employee_name">
                        {{ sig.signer_employee_name || sig.signer_name || '(Pending)' }}
                      </div>
                      <div class="text-[7px] text-gray-400 mt-0.5">{{ sig.signed_at ? new Date(sig.signed_at).toLocaleString() : 'Not signed' }}</div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Footer -->
              <div class="text-[8px] flex justify-between mt-8">
                <span>REV#01</span>
                <span>{{ formatDatePrint(new Date()) }}</span>
                <span>FRM-CCD-02-01</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { Printer, X } from 'lucide-vue-next'
import { useOrganizationStore } from '../../stores/organization'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  cc: {
    type: Object,
    default: () => null
  },
  signatures: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['close'])

const orgStore = useOrganizationStore()

onMounted(() => {
  if (!orgStore.company) {
    orgStore.fetchCompany()
  }
})

function printDocument() {
  window.print()
}

const printAddress = computed(() => {
  const addr1 = orgStore.company?.company_address || ''
  const addr2 = orgStore.company?.company_address2 || ''
  if (addr2 && addr2.trim().toLowerCase() !== addr1.trim().toLowerCase()) {
    return addr1 + ', ' + addr2
  }
  return addr1
})

const creatorName = computed(() => {
  return props.cc?.created_by_name || props.cc?.vendor_name || '-'
})

function formatCurrencyRaw(val) {
  if (val === null || val === undefined) return '0.00'
  const parsed = typeof val === 'string' ? parseFloat(val) : val
  return parsed.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function formatDatePrint(dateStr) {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return d.toLocaleDateString('id-ID', { day: '2-digit', month: 'short', year: 'numeric' })
}

const indonesianDays = ["Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"]
const indonesianMonths = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

const terbilang = (angka) => {
  const words = ["", "Satu", "Dua", "Tiga", "Empat", "Lima", "Enam", "Tujuh", "Delapan", "Sembilan", "Sepuluh", "Sebelas"]
  let num = parseInt(angka, 10)
  if (num < 12) return words[num]
  if (num < 20) return terbilang(num - 10) + " Belas"
  if (num < 100) return terbilang(Math.floor(num / 10)) + " Puluh " + terbilang(num % 10)
  if (num < 200) return "Seratus " + terbilang(num - 100)
  if (num < 1000) return terbilang(Math.floor(num / 100)) + " Ratus " + terbilang(num % 100)
  if (num < 2000) return "Seribu " + terbilang(num - 1000)
  if (num < 1000000) return terbilang(Math.floor(num / 1000)) + " Ribu " + terbilang(num % 1000)
  return num.toString() 
}

const targetDate = computed(() => {
  if (!props.cc?.document_date) return new Date()
  return new Date(props.cc.document_date)
})

const dayName = computed(() => indonesianDays[targetDate.value.getDay()])
const dateWord = computed(() => terbilang(targetDate.value.getDate()))
const monthWord = computed(() => indonesianMonths[targetDate.value.getMonth()])
const yearWord = computed(() => {
  const year = targetDate.value.getFullYear()
  let result = terbilang(Math.floor(year/1000)) + " Ribu "
  let rem = year % 1000
  if (rem > 0) result += terbilang(rem)
  return result.trim()
})

</script>

<style scoped>
@media print {
  @page {
    size: A4;
    margin: 10mm;
  }
  .print-modal-overlay {
    position: static !important;
    background: none !important;
  }
  .print-modal-container {
    position: absolute !important;
    left: 0 !important;
    top: 0 !important;
    width: 210mm !important;
    max-width: 210mm !important;
    height: auto !important;
    max-height: none !important;
    border: none !important;
    box-shadow: none !important;
    background: white !important;
    display: flex !important;
    flex-direction: column !important;
    overflow: visible !important;
  }
}
</style>
