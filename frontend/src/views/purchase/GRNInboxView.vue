<template>
  <Panel title="Good Receipt Note (GRN) Inbox" subtitle="Purchases | GRN Inbox">
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
      
      <!-- LEFT PANEL: INBOX LIST (col-span-4) -->
      <div class="lg:col-span-4 border-r border-gray-100 pr-0 lg:pr-6 flex flex-col gap-4">
        <div class="flex items-center justify-between pb-2 border-b border-gray-100">
          <h4 class="text-sm font-semibold text-gray-700 flex items-center gap-2">
            <Inbox class="w-4 h-4 text-bfs-gold" />
            Kotak Masuk Persetujuan
          </h4>
          <span class="px-2 py-0.5 text-xs bg-bfs-gold/10 text-bfs-gold rounded-full font-medium">
            {{ inboxRequests.length }} pending
          </span>
        </div>

        <!-- Filter / Search -->
        <div class="relative">
          <Search class="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Cari nomor GRN..."
            class="w-full pl-9 pr-4 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-1 focus:ring-bfs-gold focus:border-bfs-gold"
          />
        </div>

        <!-- Inbox List -->
        <div v-if="isLoadingRequests" class="flex flex-col items-center justify-center py-12 text-gray-400 text-sm">
          <Loader2 class="w-6 h-6 animate-spin text-bfs-gold mb-2" />
          <span>Memuat inbox...</span>
        </div>

        <div v-else-if="filteredRequests.length === 0" class="text-center py-12 border border-dashed border-gray-200 rounded-xl bg-gray-50/50">
          <Inbox class="w-8 h-8 text-gray-300 mx-auto mb-2" />
          <p class="text-xs text-gray-400">Tidak ada GRN yang membutuhkan persetujuan Anda saat ini.</p>
        </div>

        <div v-else class="space-y-3 overflow-y-auto max-h-[600px] pr-1">
          <div
            v-for="req in filteredRequests"
            :key="req.id"
            :class="selectedRequest?.id === req.id 
              ? 'border-bfs-gold bg-bfs-gold/5 shadow-sm' 
              : 'border-gray-100 hover:border-gray-200 bg-white'"
            class="border rounded-xl p-4 cursor-pointer transition-all duration-200 flex flex-col gap-2 relative overflow-hidden"
            @click="selectRequest(req)"
          >
            <!-- Badge indicates it is currently this user's turn -->
            <div 
              v-if="req.is_my_turn" 
              class="absolute top-0 right-0 bg-bfs-gold text-white text-[9px] font-bold px-2 py-0.5 rounded-bl"
            >
              GILIRAN ANDA
            </div>

            <div class="flex items-center justify-between">
              <span class="text-sm font-semibold text-gray-800">{{ req.document_number }}</span>
              <span class="text-xs font-semibold text-bfs-gold">
                {{ formatCurrency(req.amount) }}
              </span>
            </div>
            
            <div class="text-xs text-gray-500 flex flex-col gap-0.5">
              <span class="flex items-center gap-1">
                <User class="w-3.5 h-3.5" />
                Pembuat: {{ req.creator_employee_name || req.creator_name }}
              </span>
              <span class="text-[10px] text-gray-400">
                Diajukan: {{ formatDate(req.created_at) }}
              </span>
            </div>

            <!-- Visual mini progress -->
            <div class="flex items-center gap-1 mt-1">
              <div 
                v-for="step in req.steps" 
                :key="step.id" 
                :class="getMiniStepClass(step, req.current_step_number)"
                class="h-1.5 flex-1 rounded-full transition-all duration-300"
                :title="`Step ${step.step_number}: ${step.role_display}`"
              ></div>
            </div>
          </div>
        </div>

        <!-- History/All Requests Link Toggle -->
        <div class="pt-4 border-t border-gray-100">
          <label class="flex items-center gap-2 text-xs text-gray-600 cursor-pointer">
            <input 
              v-model="showAllRequests" 
              type="checkbox" 
              class="text-bfs-gold focus:ring-bfs-gold rounded"
              @change="loadAllRequests"
            />
            Tampilkan semua riwayat pengajuan GRN
          </label>
        </div>
      </div>

      <!-- RIGHT PANEL: DETAILS, STEPPER & SIGNATURES (col-span-8) -->
      <div class="lg:col-span-8 min-h-[400px] flex flex-col">
        
        <div v-if="!selectedRequest" class="flex-1 flex flex-col items-center justify-center text-gray-400 py-20 bg-gray-50/30 rounded-2xl border border-dashed border-gray-100">
          <FileText class="w-12 h-12 text-gray-200 mb-3" />
          <p class="text-sm font-medium">Pilih dokumen GRN dari panel kiri untuk memproses persetujuan.</p>
        </div>

        <div v-else class="space-y-6">
          <!-- Document Header Card -->
          <div class="bg-gray-50/50 border border-gray-100 rounded-2xl p-5 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <div>
              <div class="flex items-center gap-2.5 mb-1.5">
                <span class="text-lg font-bold text-gray-800">{{ selectedRequest.document_number }}</span>
                <span :class="getStatusBadgeClass(selectedRequest.status)" class="px-2.5 py-0.5 text-xs font-semibold rounded-full">
                  {{ selectedRequest.status_display }}
                </span>
              </div>
              <p class="text-xs text-gray-500">
                Persetujuan untuk dokumen Good Receipt Note (GRN)
              </p>
            </div>

            <div class="text-left md:text-right border-l md:border-l-0 md:border-r border-gray-200 pl-4 md:pl-0 md:pr-4">
              <span class="text-xs text-gray-400 uppercase tracking-wider block font-medium">Total Nilai (GRN)</span>
              <button 
                @click="openDetailModal" 
                class="text-xl font-extrabold text-bfs-gold hover:text-bfs-gold-dark hover:underline focus:outline-none transition-colors"
                title="Klik untuk melihat detail GRN"
              >
                {{ formatCurrency(selectedRequest.amount) }}
              </button>
            </div>
          </div>

          <!-- Alert State -->
          <div
            v-if="alertMessage"
            :class="alertType === 'success' ? 'bg-green-50 border-green-200 text-green-700' : 'bg-red-50 border-red-200 text-red-700'"
            class="px-4 py-3 border rounded-xl flex items-center gap-2 text-sm"
          >
            <CheckCircle v-if="alertType === 'success'" class="w-4 h-4 flex-shrink-0" />
            <XCircle v-else class="w-4 h-4 flex-shrink-0" />
            <span>{{ alertMessage }}</span>
          </div>

          <!-- Visual Stepper: vertical timeline style -->
          <div class="border border-gray-100 rounded-2xl p-5">
            <h5 class="text-sm font-semibold text-gray-700 mb-5 flex items-center gap-2">
              <GitCommit class="w-4 h-4 text-bfs-gold" />
              Alur Persetujuan (Approval Timeline)
            </h5>

            <div class="relative pl-6 space-y-6 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-gray-100">
              <div 
                v-for="step in selectedRequest.steps" 
                :key="step.id" 
                class="relative flex flex-col gap-1"
              >
                <!-- Stepper Node Indicator -->
                <span 
                  :class="getStepperNodeClass(step, selectedRequest.current_step_number, selectedRequest.status)" 
                  class="absolute -left-6 top-1 w-4.5 h-4.5 rounded-full border-2 flex items-center justify-center text-[9px] font-bold z-10 transition-all duration-300"
                >
                  <Check v-if="step.status === 'APPROVED'" class="w-2.5 h-2.5 text-white" />
                  <X v-else-if="step.status === 'REJECTED'" class="w-2.5 h-2.5 text-white" />
                  <span v-else>{{ step.step_number }}</span>
                </span>

                <!-- Step Info -->
                <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-1.5 ml-2">
                  <div>
                    <span class="text-xs font-semibold text-gray-800 uppercase tracking-wide">
                      {{ step.role_display }}
                    </span>
                    <span class="text-xs text-gray-400 ml-2">
                      ({{ step.position_name }} / {{ step.department_name }})
                    </span>
                  </div>
                  
                  <!-- Step Status Badge -->
                  <span :class="getStepBadgeClass(step.status)" class="text-[10px] font-bold px-2 py-0.5 rounded-full">
                    {{ step.status_display }}
                  </span>
                </div>

                <!-- Step Action Trail (if approved/rejected) -->
                <div v-if="step.approved_by" class="ml-2 bg-gray-50/50 rounded-xl p-3 border border-gray-50 flex flex-col gap-1.5 mt-1">
                  <div class="flex items-center gap-1.5 text-xs text-gray-600">
                    <UserCheck class="w-3.5 h-3.5 text-gray-400" />
                    <span>Oleh: <strong class="text-gray-700">{{ step.approved_by_employee_name || step.approved_by_name }}</strong></span>
                    <span class="text-[10px] text-gray-400 ml-auto">{{ formatDate(step.approved_at) }}</span>
                  </div>
                  <div v-if="step.remarks" class="text-xs text-gray-500 pl-5 border-l-2 border-gray-200 italic">
                    "{{ step.remarks }}"
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Document Signatures Library Block (Simulasi Footer RAP) -->
          <div class="border border-gray-100 rounded-2xl p-5 bg-gray-50/30">
            <h5 class="text-sm font-semibold text-gray-700 mb-4 flex items-center gap-2">
              <PenTool class="w-4 h-4 text-bfs-gold" />
              Tanda Tangan Dokumen GRN (Signature Blocks)
            </h5>

            <div v-if="isLoadingSignatures" class="flex items-center justify-center py-8">
              <Loader2 class="w-5 h-5 animate-spin text-bfs-gold" />
            </div>

            <div v-else class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div 
                v-for="sig in signatureList" 
                :key="sig.id"
                :class="sig.is_signed ? 'bg-white border-green-200' : 'bg-gray-50/80 border-dashed border-gray-200'"
                class="border rounded-xl p-4 flex flex-col items-center justify-between text-center min-h-[160px] shadow-sm relative transition-all"
              >
                <!-- Role / Position Name Header -->
                <div>
                  <div class="text-[10px] uppercase font-bold text-gray-400 tracking-wider">
                    {{ sig.role_display }}
                  </div>
                  <div class="text-xs font-semibold text-gray-700 mt-0.5">
                    {{ sig.position_name }}
                  </div>
                </div>

                <!-- Signature Image / Graphic / Placeholder -->
                <div class="my-4 flex items-center justify-center h-16 w-full">
                  <div v-if="sig.is_signed" class="flex flex-col items-center">
                    <!-- If canvas signature exists -->
                    <div v-if="sig.signature_draw && sig.signature_draw.startsWith('data:image')" class="max-h-14">
                      <img :src="sig.signature_draw" alt="Signature Draw" class="max-h-14 object-contain mx-auto" />
                    </div>
                    <!-- If signature image exists -->
                    <div v-else-if="sig.signature_image" class="max-h-14">
                      <img :src="sig.signature_image" alt="Signature Image" class="max-h-14 object-contain mx-auto" />
                    </div>
                    <!-- Stylized digital signature stamp -->
                    <div 
                      v-else 
                      class="px-3 py-1 border border-green-500 rounded bg-green-50/30 text-green-600 font-serif italic text-xs font-semibold tracking-wide border-double scale-95"
                    >
                      SIGNED DIGITALLY
                    </div>
                  </div>

                  <div v-else class="text-[11px] text-gray-400 italic">
                    Belum ditandatangani
                  </div>
                </div>

                <!-- Signer Metadata Footer -->
                <div class="w-full border-t border-gray-100 pt-2 text-[10px]">
                  <div v-if="sig.is_signed" class="text-gray-600">
                    <div class="font-semibold text-gray-700 truncate" :title="sig.signer_employee_name">
                      {{ sig.signer_employee_name || sig.signer_name }}
                    </div>
                    <div class="text-gray-400 mt-0.5">
                      {{ formatDateShort(sig.signed_at) }}
                    </div>
                    <div class="text-[8px] text-gray-400 mt-0.5 truncate" :title="`IP: ${sig.ip_address} | UA: ${sig.user_agent}`">
                      IP: {{ sig.ip_address || 'N/A' }}
                    </div>
                  </div>
                  <div v-else class="text-gray-400">
                    (Menunggu giliran)
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- ACTION FORM: APPROVE / REJECT (Visible only on user's turn) -->
          <Transition name="slide-up">
            <div 
              v-if="selectedRequest.is_my_turn && selectedRequest.status === 'PENDING'" 
              class="border border-bfs-gold bg-bfs-gold/5 rounded-2xl p-5 space-y-4"
            >
              <h5 class="text-sm font-semibold text-gray-800 flex items-center gap-2">
                <ShieldAlert class="w-4.5 h-4.5 text-bfs-gold" />
                Tindakan Persetujuan
              </h5>
              
              <div class="space-y-1.5">
                <label class="block text-xs font-medium text-gray-700">
                  Catatan / Keterangan (Wajib diisi jika menolak)
                </label>
                <textarea
                  v-model="actionRemarks"
                  placeholder="Tulis catatan persetujuan atau penolakan di sini..."
                  rows="3"
                  class="w-full p-3 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-1 focus:ring-bfs-gold focus:border-bfs-gold"
                ></textarea>
              </div>

              <div class="flex items-center gap-3 justify-end">
                <!-- Revise Button -->
                <button
                  type="button"
                  class="px-5 py-2 border border-amber-200 text-amber-600 rounded-lg text-sm font-medium hover:bg-amber-50/50 disabled:opacity-50 transition-colors"
                  :disabled="isLoadingAction"
                  @click="handleRevise"
                >
                  <FileText v-if="!isLoadingAction" class="w-4 h-4 inline-block mr-1" />
                  <Loader2 v-else class="w-4 h-4 animate-spin inline-block mr-1" />
                  Revisi (Revise)
                </button>

                <!-- Reject Button -->
                <button
                  type="button"
                  class="px-5 py-2 border border-red-200 text-red-600 rounded-lg text-sm font-medium hover:bg-red-50/50 disabled:opacity-50 transition-colors"
                  :disabled="isLoadingAction"
                  @click="handleReject"
                >
                  <XCircle v-if="!isLoadingAction" class="w-4 h-4 inline-block mr-1" />
                  <Loader2 v-else class="w-4 h-4 animate-spin inline-block mr-1" />
                  Tolak (Reject)
                </button>

                <!-- Approve Button -->
                <button
                  type="button"
                  class="px-6 py-2 bg-bfs-gold text-white rounded-lg text-sm font-medium hover:bg-bfs-gold/90 disabled:opacity-50 transition-colors flex items-center gap-1.5"
                  :disabled="isLoadingAction"
                  @click="handleApprove"
                >
                  <CheckCircle v-if="!isLoadingAction" class="w-4 h-4" />
                  <Loader2 v-else class="w-4 h-4 animate-spin" />
                  Setujui & Tanda Tangan
                </button>
              </div>
            </div>
          </Transition>

        </div>
      </div>
      
    </div>
    
    <!-- PO Detail Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showDetailModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-black/40" @click="closeDetailModal" />
          <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-4xl p-6 z-10 max-h-[90vh] flex flex-col">
            <div class="flex items-center justify-between mb-5">
              <div>
                <h3 class="text-lg font-semibold text-gray-800">Detail GRN</h3>
                <p class="text-sm text-gray-500">{{ selectedRequest?.document_number }}</p>
              </div>
              <div class="flex items-center gap-2">
                <button v-if="documentDetail" @click="openPrintPreview" class="text-blue-600 hover:bg-blue-50 p-2 rounded-lg transition-colors flex items-center gap-1 text-sm font-semibold">
                  <Printer class="w-5 h-5" />
                  <span>Print</span>
                </button>
                <button @click="closeDetailModal" class="text-gray-400 hover:text-gray-600">
                  <X class="w-6 h-6" />
                </button>
              </div>
            </div>
            <div class="overflow-y-auto flex-1 border border-gray-100 rounded-xl bg-gray-50/50 p-4">
              <div v-if="isLoadingDetail" class="flex justify-center py-10">
                <Loader2 class="w-8 h-8 animate-spin text-bfs-gold" />
              </div>
              <div v-else-if="documentDetail">
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6 bg-white p-4 rounded-xl border border-gray-100">
                  <div><span class="text-xs text-gray-500 block">Vendor</span><span class="font-medium text-sm">{{ documentDetail.vendor_name || '-' }}</span></div>
                  <div><span class="text-xs text-gray-500 block">Purchase Order</span><span class="font-medium text-sm">{{ documentDetail.po_number || '-' }}</span></div>
                  <div><span class="text-xs text-gray-500 block">Payment Term</span><span class="font-medium text-sm">{{ documentDetail.term_desc || '-' }} ({{ documentDetail.term_percentage || 0 }}%)</span></div>
                  <div><span class="text-xs text-gray-500 block">GRN Amount</span><span class="font-medium text-bfs-gold">{{ formatCurrency(documentDetail.amount) }}</span></div>
                </div>

                <h4 class="font-semibold text-gray-800 text-sm mb-3 mt-4 px-1">Purchase Order Detail</h4>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6 bg-white p-4 rounded-xl border border-gray-100">
                  <div><span class="text-xs text-gray-500 block">PO Type</span><span class="font-medium text-sm">{{ documentDetail.po_detail?.po_type || '-' }}</span></div>
                  <div><span class="text-xs text-gray-500 block">PO Amount</span><span class="font-medium text-sm">{{ formatCurrency(documentDetail.po_detail?.total_amount) }}</span></div>
                  <div>
                    <span class="text-xs text-gray-500 block">
                      PO Tax ({{ ((documentDetail.po_detail?.total_tax || 0) / (documentDetail.po_detail?.total_amount || 1) * 100).toFixed(0) }}%)
                    </span>
                    <span class="font-medium text-sm">{{ formatCurrency(documentDetail.po_detail?.total_tax) }}</span>
                  </div>
                  <div><span class="text-xs text-gray-500 block">PO Grand Total</span><span class="font-medium text-bfs-gold">{{ formatCurrency(documentDetail.po_detail?.grand_total) }}</span></div>
                </div>
                
                <h4 class="font-semibold text-gray-800 text-sm mb-3 mt-4 px-1">Dokumen Kelengkapan</h4>
                <div class="overflow-x-auto rounded-xl border border-gray-200 bg-white shadow-sm">
                  <table class="w-full text-left border-collapse text-sm">
                    <thead>
                      <tr class="bg-gray-50 border-b border-gray-200">
                        <th class="px-4 py-3 font-semibold text-gray-600">Available</th>
                        <th class="px-4 py-3 font-semibold text-gray-600">Requirement</th>
                        <th class="px-4 py-3 font-semibold text-gray-600">Document No</th>
                        <th class="px-4 py-3 font-semibold text-gray-600">Keterangan</th>
                        <th class="px-4 py-3 font-semibold text-gray-600 text-center">File</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="d in documentDetail.documents" :key="d.id" class="border-b border-gray-100 last:border-none hover:bg-gray-50/50">
                        <td class="px-4 py-3">
                          <span v-if="d.is_available" class="px-2 py-1 bg-green-100 text-green-700 text-xs rounded font-bold">Ada</span>
                          <span v-else class="px-2 py-1 bg-red-100 text-red-700 text-xs rounded font-bold">Tidak</span>
                        </td>
                        <td class="px-4 py-3 text-gray-800 font-medium">{{ d.document_name || '-' }}</td>
                        <td class="px-4 py-3 text-gray-600">{{ d.document_number || '-' }}</td>
                        <td class="px-4 py-3 text-gray-600">{{ d.keterangan || '-' }}</td>
                        <td class="px-4 py-3 text-center">
                          <a v-if="d.file" :href="d.file" target="_blank" class="text-blue-600 hover:underline font-semibold text-xs">Lihat File</a>
                          <span v-else class="text-gray-400 text-xs">-</span>
                        </td>
                      </tr>
                      <tr v-if="!documentDetail.documents?.length">
                        <td colspan="5" class="px-4 py-8 text-center text-gray-400 text-sm">Tidak ada dokumen kelengkapan</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
              <div v-else class="text-center py-10 text-gray-400">Gagal memuat detail dokumen</div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Print Template -->
    <GRNPrintTemplate
      :show="showPrintPreview"
      :grn="documentDetail"
      :signatures="printSignatures"
      @close="showPrintPreview = false"
    />
  </Panel>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { 
  Inbox, Search, Loader2, User, CheckCircle, XCircle, 
  FileText, GitCommit, Check, X, UserCheck, PenTool, ShieldAlert, Printer
} from 'lucide-vue-next'
import Panel from '../../components/Panel.vue'
import GRNPrintTemplate from '../../components/purchase/GRNPrintTemplate.vue'
import { useApprovalRequestStore } from '../../stores/approvalRequest.js'
import api from '../../services/api.js'
import Swal from 'sweetalert2'
import html2pdf from 'html2pdf.js'
import { useGoodReceiptNoteStore } from '../../stores/goodReceiptNote'

const requestStore = useApprovalRequestStore()
const grnStore = useGoodReceiptNoteStore()

const searchQuery = ref('')
const selectedRequest = ref(null)
const actionRemarks = ref('')
const showAllRequests = ref(false)

const isLoadingRequests = ref(false)
const isLoadingSignatures = ref(false)
const isLoadingAction = ref(false)

const alertMessage = ref('')
const alertType = ref('success')

const showDetailModal = ref(false)
const isLoadingDetail = ref(false)
const documentDetail = ref(null)

const showPrintPreview = ref(false)
const printSignatures = ref([])

// Filter requests depending on showAllRequests flag
// If showAllRequests is FALSE: show only PENDING requests in my inbox
// If showAllRequests is TRUE: show all requests in the system
const inboxRequests = computed(() => {
  return requestStore.requests
})

const filteredRequests = computed(() => {
  let list = inboxRequests.value
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(r => r.document_number.toLowerCase().includes(q))
  }
  return list
})

const signatureList = computed(() => {
  return requestStore.signatures
})

async function loadInbox() {
  isLoadingRequests.value = true
  try {
    const filters = { document_code: 'GRN' }
    if (!showAllRequests.value) {
      filters.inbox = 'true'
    }
    await requestStore.fetchRequests(filters)
    
    // Auto-select first request if available and none selected
    if (filteredRequests.value.length > 0) {
      // If we came from notification/external routing, check currentRequest in store
      const targetId = requestStore.currentRequest?.id || selectedRequest.value?.id
      const found = filteredRequests.value.find(r => r.id === targetId)
      if (found) {
        selectRequest(found)
        requestStore.currentRequest = null
      } else {
        selectRequest(filteredRequests.value[0])
      }
    } else {
      selectedRequest.value = null
    }
  } catch (err) {
    showToast('Gagal memuat daftar inbox.', 'error')
  } finally {
    isLoadingRequests.value = false
  }
}

async function loadAllRequests() {
  selectedRequest.value = null
  await loadInbox()
}

async function selectRequest(req) {
  selectedRequest.value = req
  actionRemarks.value = ''
  
  // Load full details & signature status
  isLoadingSignatures.value = true
  try {
    await requestStore.fetchRequestDetail(req.id)
    // Overwrite with full detailed request object containing steps
    selectedRequest.value = requestStore.currentRequest
    
    // Fetch signatures registry for this document
    await requestStore.fetchSignatures(req.document_code, req.document_id)
  } catch (err) {
    showToast('Gagal memuat detail persetujuan.', 'error')
  } finally {
    isLoadingSignatures.value = false
  }
}

function showToast(message, type = 'success') {
  alertMessage.value = message
  alertType.value = type
  setTimeout(() => { alertMessage.value = '' }, 4000)
}

async function handleApprove() {
  if (!selectedRequest.value) return
  isLoadingAction.value = true
  try {
    const res = await requestStore.approveRequest(selectedRequest.value.id, actionRemarks.value)
    showToast('Persetujuan berhasil diproses dan tanda tangan dibubuhkan.', 'success')
    
    // Generate PDF and send email
    // We need to fetch details to render the print template invisibly
    if (!documentDetail.value) {
        const ccData = await api.get(`/purchase/good-receipt-notes/${selectedRequest.value.document_id}/`).then(r => r.data);
        const poRes = await api.get(`/purchase/po/${ccData.po}/`).then(r => r.data);
        ccData.po_detail = poRes;
        documentDetail.value = ccData;
        printSignatures.value = await requestStore.fetchSignatures('GRN', documentDetail.value.id);
    }
    
    showPrintPreview.value = true;
    // Wait for Vue to render the print template
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const printEl = document.getElementById('print-area-wrapper')
    let pdfBlob = new Blob([''], { type: 'application/pdf' }); // empty blob fallback
    if (printEl) {
        showToast('Menghasilkan PDF dan mengirim email ke vendor...', 'info')
        try {
            const { toJpeg } = await import('html-to-image');
            const { jsPDF } = await import('jspdf');

            const dataUrlPromise = toJpeg(printEl, { 
                quality: 0.85,
                pixelRatio: 1.5, 
                backgroundColor: '#ffffff',
                cacheBust: true
            });
            const timeoutPromise = new Promise((_, reject) => setTimeout(() => reject(new Error('PDF generation timeout (15s)')), 15000));
            
            const dataUrl = await Promise.race([dataUrlPromise, timeoutPromise]);
            
            const pdf = new jsPDF({
                orientation: 'portrait',
                unit: 'mm',
                format: 'a4'
            });
            
            pdf.addImage(dataUrl, 'JPEG', 0, 0, 210, 297);
            pdfBlob = pdf.output('blob');
            
        } catch (pdfErr) {
            window.__pdf_error = pdfErr;
            console.error("PDF Error:", pdfErr);
            showToast('Gagal membuat PDF. Mengirim email dengan log error...', 'warning');
            const errStr = pdfErr ? (pdfErr.stack || pdfErr.toString()) : 'Unknown Error';
            pdfBlob = new Blob(['HTML-TO-IMAGE FAILED:\n' + errStr], { type: 'text/plain' });
        }

    } else {
        showToast('Gagal menemukan template PDF, mengirim email tanpa lampiran...', 'warning')
    }
    
    // Close the print preview modal after generating PDF
    showPrintPreview.value = false;
    
    let fileName = pdfBlob.type === 'text/plain' ? 'ERROR_LOG.txt' : 'GRN_Approved.pdf';
    const response = await grnStore.approveGRN(selectedRequest.value.document_id, pdfBlob, fileName)
    
    if (response.status === 'approved_no_email') {
        showToast('GRN Disetujui, tapi email tidak dikirim (SMTP belum diatur).', 'warning')
    } else if (response.status === 'approved_email_failed') {
        showToast('GRN Disetujui, tapi ' + response.detail, 'error')
    } else {
        showToast('Email notifikasi GRN berhasil dikirim ke vendor!', 'success')
    }

    actionRemarks.value = ''
    await loadInbox()
  } catch (err) {
    let msg = 'Gagal memproses persetujuan.'
    if (err.response?.data) {
      if (Array.isArray(err.response.data)) msg = err.response.data[0]
      else if (err.response.data.detail) msg = err.response.data.detail
      else if (typeof err.response.data === 'string') msg = err.response.data
    }
    Swal.fire({
      icon: 'error',
      title: 'Gagal Memproses',
      text: msg
    })
  } finally {
    isLoadingAction.value = false
  }
}

async function handleReject() {
  if (!selectedRequest.value) return
  if (!actionRemarks.value.trim()) {
    showToast('Catatan alasan penolakan wajib diisi.', 'error')
    return
  }
  isLoadingAction.value = true
  try {
    await requestStore.rejectRequest(selectedRequest.value.id, actionRemarks.value)
    showToast('Dokumen berhasil ditolak.', 'success')
    actionRemarks.value = ''
    await loadInbox()
  } catch (err) {
    let msg = 'Gagal menolak dokumen.'
    if (err.response?.data) {
      if (Array.isArray(err.response.data)) msg = err.response.data[0]
      else if (err.response.data.detail) msg = err.response.data.detail
      else if (typeof err.response.data === 'string') msg = err.response.data
    }
    Swal.fire({
      icon: 'error',
      title: 'Gagal Menolak',
      text: msg
    })
  } finally {
    isLoadingAction.value = false
  }
}

async function handleRevise() {
  if (!selectedRequest.value) return
  if (!actionRemarks.value.trim()) {
    showToast('Catatan alasan revisi wajib diisi.', 'error')
    return
  }
  isLoadingAction.value = true
  try {
    await requestStore.reviseRequest(selectedRequest.value.id, actionRemarks.value)
    showToast('Dokumen berhasil dikembalikan untuk revisi.', 'success')
    actionRemarks.value = ''
    await loadInbox()
  } catch (err) {
    let msg = 'Gagal meminta revisi dokumen.'
    if (err.response?.data) {
      if (Array.isArray(err.response.data)) msg = err.response.data[0]
      else if (err.response.data.detail) msg = err.response.data.detail
      else if (typeof err.response.data === 'string') msg = err.response.data
    }
    Swal.fire({
      icon: 'error',
      title: 'Gagal Revisi',
      text: msg
    })
  } finally {
    isLoadingAction.value = false
  }
}

async function openDetailModal() {
  if (!selectedRequest.value?.document_id) return
  showDetailModal.value = true
  isLoadingDetail.value = true
  try {
    const res = await api.get(`/purchase/good-receipt-notes/${selectedRequest.value.document_id}/`)
    const ccData = res.data
    
    const poRes = await api.get(`/purchase/po/${ccData.po}/`)
    ccData.po_detail = poRes.data
    
    documentDetail.value = ccData
  } catch (err) {
    console.error('Failed to load detail', err)
  } finally {
    isLoadingDetail.value = false
  }
}

function closeDetailModal() {
  showDetailModal.value = false
  documentDetail.value = null
}

async function openPrintPreview() {
  if (!documentDetail.value) return
  
  showPrintPreview.value = true
  try {
    const sigs = await requestStore.fetchSignatures('GRN', documentDetail.value.id)
    printSignatures.value = sigs
  } catch (e) {
    console.error(e)
    printSignatures.value = []
  }
}

// Visual helpers
function formatCurrency(val) {
  if (!val) return 'Rp 0'
  const parsed = typeof val === 'string' ? parseFloat(val) : val
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(parsed)
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return d.toLocaleString('id-ID', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function formatDateShort(dateStr) {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return d.toLocaleString('id-ID', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function getMiniStepClass(step, currentStepNo) {
  if (step.status === 'APPROVED') return 'bg-green-500'
  if (step.status === 'REJECTED') return 'bg-red-500'
  if (step.step_number === currentStepNo) return 'bg-bfs-gold animate-pulse'
  return 'bg-gray-200'
}

function getStatusBadgeClass(status) {
  switch (status) {
    case 'APPROVED': return 'bg-green-50 text-green-700 border border-green-200'
    case 'REJECTED': return 'bg-red-50 text-red-700 border border-red-200'
    case 'PENDING': return 'bg-bfs-gold/10 text-bfs-gold border border-bfs-gold/20 animate-pulse'
    default: return 'bg-gray-50 text-gray-500 border border-gray-200'
  }
}

function getStepBadgeClass(status) {
  switch (status) {
    case 'APPROVED': return 'bg-green-50 text-green-600'
    case 'REJECTED': return 'bg-red-50 text-red-600'
    case 'PENDING': return 'bg-bfs-gold/10 text-bfs-gold'
    default: return 'bg-gray-50 text-gray-400'
  }
}

function getStepperNodeClass(step, currentStepNo, requestStatus) {
  if (step.status === 'APPROVED') {
    return 'bg-green-500 border-green-500 text-white'
  }
  if (step.status === 'REJECTED') {
    return 'bg-red-500 border-red-500 text-white'
  }
  if (step.step_number === currentStepNo && requestStatus === 'PENDING') {
    return 'bg-white border-bfs-gold text-bfs-gold ring-4 ring-bfs-gold/10 scale-110'
  }
  return 'bg-white border-gray-200 text-gray-400'
}

onMounted(() => {
  loadInbox()
})
</script>

<style scoped>
.slide-up-enter-active, .slide-up-leave-active {
  transition: all 0.3s ease-out;
}
.slide-up-enter-from, .slide-up-leave-to {
  transform: translateY(20px);
  opacity: 0;
}
</style>

