import re

with open('c:/Traine/bfs-erp/frontend/src/views/purchase/GRNInboxView.vue', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    \"import { Search, Inbox, ChevronRight, CheckCircle, XCircle, FileText, Loader2, ArrowRight } from 'lucide-vue-next'\",
    \"import { Search, Inbox, ChevronRight, CheckCircle, XCircle, FileText, Loader2, ArrowRight } from 'lucide-vue-next'\\nimport html2pdf from 'html2pdf.js'\"
)

old_handle_approve = '''async function handleApprove() {
  if (!selectedRequest.value) return
  isLoadingAction.value = true
  try {
    await requestStore.approveRequest(selectedRequest.value.id, actionRemarks.value)
    showToast('Persetujuan berhasil diproses dan tanda tangan dibubuhkan.', 'success')
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
}'''

new_handle_approve = '''async function handleApprove() {
  if (!selectedRequest.value) return
  isLoadingAction.value = true
  try {
    const res = await requestStore.approveRequest(selectedRequest.value.id, actionRemarks.value)
    showToast('Persetujuan berhasil diproses dan tanda tangan dibubuhkan.', 'success')
    
    // Check if fully approved, if so, generate PDF and send email
    const printEl = document.getElementById('print-area-wrapper')
    if (printEl) {
        showToast('Menghasilkan PDF dan mengirim email ke vendor...', 'info')
        const opt = {
            margin:       0.5,
            filename:     'GRN.pdf',
            image:        { type: 'jpeg', quality: 0.98 },
            html2canvas:  { scale: 2 },
            jsPDF:        { unit: 'in', format: 'letter', orientation: 'portrait' }
        };
        const pdfBlob = await html2pdf().set(opt).from(printEl).output('blob');
        await grnStore.approveGRN(selectedRequest.value.model_id, pdfBlob)
        showToast('Email PDF GRN berhasil dikirim ke vendor!', 'success')
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
}'''

content = content.replace(old_handle_approve, new_handle_approve)

with open('c:/Traine/bfs-erp/frontend/src/views/purchase/GRNInboxView.vue', 'w', encoding='utf-8') as f:
    f.write(content)
