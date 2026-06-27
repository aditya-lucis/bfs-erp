import re

def update_modal():
    with open('c:/Traine/bfs-erp/frontend/src/components/purchase/CompletionCertificateFormModal.vue', 'r', encoding='utf-8') as f:
        content = f.read()

    # Style input replacements
    input_class = 'w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-1 focus:ring-bfs-navy focus:border-bfs-navy bg-white text-gray-900 disabled:bg-gray-100 disabled:text-gray-500'
    
    # Replace <select class="input"
    content = content.replace('class="input"', f'class="{input_class}"')
    content = content.replace('class="input px-2 py-1 text-sm h-8"', f'class="px-2 py-1 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-bfs-navy bg-white"')
    content = content.replace('class="input py-1 h-8"', f'class="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-bfs-navy bg-white"')
    content = content.replace('class="input min-h-[80px]"', f'class="{input_class} resize-none"')
    content = content.replace('class="input py-1.5 h-auto text-sm"', f'class="{input_class}"')

    # Style table replacements
    content = content.replace('class="table min-w-[800px]"', 'class="w-full text-left border-collapse min-w-[800px]"')
    content = content.replace('<thead>\n              <tr>\n                <th class="w-12 text-center">CHK</th>', 
                              '<thead>\n              <tr class="bg-gray-50 border-b border-t border-gray-200 text-[11px] font-semibold text-gray-600 uppercase tracking-wider">\n                <th class="py-3 px-4 w-12 text-center">CHK</th>')
    content = content.replace('<th>DOCUMENT NAME</th>', '<th class="py-3 px-4">DOCUMENT NAME</th>')
    content = content.replace('<th class="w-32 text-center">ADA/TIDAK</th>', '<th class="py-3 px-4 w-32 text-center">ADA/TIDAK</th>')
    content = content.replace('<th>FILE (MAX 2MB)</th>', '<th class="py-3 px-4">FILE (MAX 2MB)</th>')
    content = content.replace('<th>DOCUMENT NUMBER</th>', '<th class="py-3 px-4">DOCUMENT NUMBER</th>')
    content = content.replace('<th>KETERANGAN</th>', '<th class="py-3 px-4">KETERANGAN</th>')
    
    # Table body rows
    content = content.replace('<tr v-if="loadingDocs">', '<tr v-if="loadingDocs" class="border-b border-gray-100">')
    content = content.replace('<tr v-else-if="!activeDocs.length">', '<tr v-else-if="!activeDocs.length" class="border-b border-gray-100">')
    content = content.replace('<tr v-else v-for="(doc, idx) in activeDocs" :key="doc.id">', '<tr v-else v-for="(doc, idx) in activeDocs" :key="doc.id" class="border-b border-gray-100 hover:bg-yellow-50/20 text-xs">')
    
    content = content.replace('<td class="text-center">', '<td class="py-2 px-4 text-center">')
    content = content.replace('<td class="text-sm font-medium">', '<td class="py-2 px-4 text-sm font-medium text-gray-700">')
    content = content.replace('<td>\n                  <input \n                    type="file"', '<td class="py-2 px-4">\n                  <input \n                    type="file"')
    content = content.replace('<td>\n                  <input type="text" v-model="doc.document_number"', '<td class="py-2 px-4">\n                  <input type="text" v-model="doc.document_number"')
    content = content.replace('<td>\n                  <input type="text" v-model="doc.keterangan"', '<td class="py-2 px-4">\n                  <input type="text" v-model="doc.keterangan"')

    content = content.replace('bg-gray-100', 'bg-gray-100 cursor-not-allowed')
    
    # Form labels update
    content = content.replace('<label class="form-label">', '<label class="text-xs font-bold text-gray-700 uppercase tracking-wider mb-1 block">')
    content = content.replace('<label class="form-label text-sm">', '<label class="text-xs font-bold text-gray-700 uppercase tracking-wider mb-1 block">')

    # Add background style to grid and payment calculations to match the gray styling
    content = content.replace('<div class="grid grid-cols-1 md:grid-cols-2 gap-6">', '<div class="grid grid-cols-1 md:grid-cols-2 gap-6 bg-white p-4 rounded-xl border border-gray-200 shadow-sm">')

    with open('c:/Traine/bfs-erp/frontend/src/components/purchase/CompletionCertificateFormModal.vue', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    update_modal()
