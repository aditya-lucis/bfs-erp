import re

def update_modal():
    with open('c:/Traine/bfs-erp/frontend/src/components/purchase/CompletionCertificateFormModal.vue', 'r', encoding='utf-8') as f:
        content = f.read()

    # Buttons replacement
    content = content.replace('class="btn-secondary"', 'class="px-5 py-2 text-sm font-semibold text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-xl transition-colors"')
    content = content.replace('class="btn-primary flex items-center gap-2"', 'class="px-6 py-2 text-sm font-bold text-white bg-bfs-gold hover:bg-yellow-600 rounded-xl shadow-md transition-all flex items-center justify-center gap-2 min-w-[120px]"')

    # Modal wrapper
    content = content.replace('bg-white rounded-xl shadow-xl', 'bg-white rounded-2xl shadow-2xl')
    
    with open('c:/Traine/bfs-erp/frontend/src/components/purchase/CompletionCertificateFormModal.vue', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    update_modal()
