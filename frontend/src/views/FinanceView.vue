<template>
  <div class="space-y-4">
    <!-- Filter Panel (mirip SOKKA) -->
    <Panel title="Filter Parameters" icon="Filter">
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-4">
        <div class="space-y-1 lg:col-span-4">
          <label class="text-sm font-medium text-erp-text">Period RAP</label>
          <div class="flex gap-2">
            <input 
              type="date" 
              v-model="filters.periodStart"
              class="flex-1 min-w-0 border border-erp-border rounded px-2 py-2 text-sm focus:ring-2 focus:ring-bfs-gold focus:border-transparent"
            />
            <span class="text-erp-text-light self-center">s/d</span>
            <input 
              type="date" 
              v-model="filters.periodEnd"
              class="flex-1 min-w-0 border border-erp-border rounded px-2 py-2 text-sm focus:ring-2 focus:ring-bfs-gold focus:border-transparent"
            />
          </div>
        </div>
        
        <div class="space-y-1 lg:col-span-5">
          <label class="text-sm font-medium text-erp-text">Period Transaksi (PO/CBR)</label>
          <div class="flex gap-2">
            <input 
              type="date" 
              v-model="filters.transStart"
              class="flex-1 min-w-0 border border-erp-border rounded px-2 py-2 text-sm focus:ring-2 focus:ring-bfs-gold focus:border-transparent"
            />
            <span class="text-erp-text-light self-center">s/d</span>
            <input 
              type="date" 
              v-model="filters.transEnd"
              class="flex-1 min-w-0 border border-erp-border rounded px-2 py-2 text-sm focus:ring-2 focus:ring-bfs-gold focus:border-transparent"
            />
          </div>
        </div>
        
        <div class="space-y-1 lg:col-span-3">
          <label class="text-sm font-medium text-erp-text">Tipe</label>
          <div class="flex gap-4 pt-2">
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="radio" v-model="filters.type" value="detail" class="text-bfs-gold focus:ring-bfs-gold" />
              <span class="text-sm">Detail</span>
            </label>
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="radio" v-model="filters.type" value="total" class="text-bfs-gold focus:ring-bfs-gold" />
              <span class="text-sm">Total</span>
            </label>
          </div>
        </div>
      </div>
      
      <!-- Multi-select Filters (mirip SOKKA) -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
        <!-- Cost Category -->
        <div class="space-y-1">
          <label class="text-sm font-medium text-erp-text">Cost of Category</label>
          <select 
            v-model="filters.costCategory"
            multiple
            class="w-full border border-erp-border rounded px-3 py-2 text-sm h-32 focus:ring-2 focus:ring-bfs-gold"
          >
            <option value="ALL" class="bg-blue-100 font-medium">ALL</option>
            <option value="CAPEX">CAPEX</option>
            <option value="HPP">HPP</option>
            <option value="OPEX">OPEX</option>
          </select>
        </div>
        
        <!-- Department -->
        <div class="space-y-1">
          <label class="text-sm font-medium text-erp-text">Departement</label>
          <select 
            v-model="filters.department"
            multiple
            class="w-full border border-erp-border rounded px-3 py-2 text-sm h-32 focus:ring-2 focus:ring-bfs-gold"
          >
            <option value="ALL" class="bg-blue-100 font-medium">ALL</option>
            <option value="engineering">Engineering</option>
            <option value="finance">Finance, Accounting dan Tax</option>
            <option value="hrga">HRGA</option>
            <option value="marketing">Marketing dan Business Development</option>
            <option value="network">Network Operation</option>
            <option value="operation">Operation dan Maintenance</option>
            <option value="sales">Sales</option>
            <option value="technical">Technical Operation</option>
          </select>
        </div>
        
        <!-- Cost Unit -->
        <div class="space-y-1">
          <label class="text-sm font-medium text-erp-text">Cost of Unit</label>
          <select 
            v-model="filters.costUnit"
            multiple
            class="w-full border border-erp-border rounded px-3 py-2 text-sm h-32 focus:ring-2 focus:ring-bfs-gold"
          >
            <option value="ALL" class="bg-blue-100 font-medium">ALL</option>
            <option value="accounting">Accounting dan Tax</option>
            <option value="billing">Billing dan AP</option>
            <option value="costcontrol">Cost Control</option>
            <option value="datacomm">Data Comm</option>
            <option value="engineering">Engineering</option>
            <option value="finance">Finance</option>
            <option value="ga">GA</option>
            <option value="hr">HR</option>
            <option value="marketing">Marketing Event dan Commercial</option>
          </select>
        </div>
      </div>
      
      <!-- Search Button -->
      <div class="mt-4 flex justify-center">
        <button 
          @click="search"
          class="bg-bfs-navy hover:bg-bfs-navy-light text-white px-8 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 shadow-md"
        >
          <Search class="w-4 h-4" />
          Search
        </button>
      </div>
    </Panel>
    
    <!-- Results Table (mirip SOKKA) -->
    <Panel title="Penyerapan RAP" icon="Table">
      <div class="overflow-x-auto">
        <table class="w-full text-sm border-collapse">
          <thead>
            <tr class="bg-gray-100 border-b-2 border-gray-300">
              <th class="border border-gray-300 px-3 py-2 text-center font-semibold">NO</th>
              <th class="border border-gray-300 px-3 py-2 text-center font-semibold">Departemen</th>
              <th class="border border-gray-300 px-3 py-2 text-center font-semibold">Kategori Cost</th>
              <th class="border border-gray-300 px-3 py-2 text-center font-semibold">Amount RAP<br/><span class="text-xs font-normal">A</span></th>
              <th class="border border-gray-300 px-3 py-2 text-center font-semibold">Qty RAP</th>
              <th class="border border-gray-300 px-3 py-2 text-center font-semibold">RAP Belum Terserap<br/><span class="text-xs font-normal">B (A-C)</span></th>
              <th class="border border-gray-300 px-3 py-2 text-center font-semibold" colspan="2">
                Penyerapan RAP<br/><span class="text-xs font-normal">C</span>
              </th>
              <th class="border border-gray-300 px-3 py-2 text-center font-semibold" colspan="2">
                Realisasi Payment<br/><span class="text-xs font-normal">D</span>
              </th>
            </tr>
            <tr class="bg-gray-50 border-b border-gray-300">
              <th class="border border-gray-300 px-2 py-1"></th>
              <th class="border border-gray-300 px-2 py-1"></th>
              <th class="border border-gray-300 px-2 py-1"></th>
              <th class="border border-gray-300 px-2 py-1"></th>
              <th class="border border-gray-300 px-2 py-1"></th>
              <th class="border border-gray-300 px-2 py-1"></th>
              <th class="border border-gray-300 px-2 py-1 text-xs">PO</th>
              <th class="border border-gray-300 px-2 py-1 text-xs">CBR / NON PO</th>
              <th class="border border-gray-300 px-2 py-1 text-xs">Sudah Terbayar</th>
              <th class="border border-gray-300 px-2 py-1 text-xs">Belum Terbayar<br/>E(C-D)</th>
            </tr>
          </thead>
          <tbody>
            <!-- Empty state -->
            <tr v-if="!results.length">
              <td colspan="10" class="border border-gray-300 px-4 py-8 text-center text-erp-text-light">
                <div class="flex flex-col items-center gap-2">
                  <Inbox class="w-10 h-10 text-gray-300" />
                  <p>No data available. Please apply filters and click Search.</p>
                </div>
              </td>
            </tr>
            
            <!-- Data rows -->
            <tr 
              v-for="(row, index) in results" 
              :key="row.id"
              class="hover:bg-blue-50 transition-colors"
              :class="index % 2 === 0 ? 'bg-white' : 'bg-gray-50'"
            >
              <td class="border border-gray-300 px-3 py-2 text-center">{{ index + 1 }}</td>
              <td class="border border-gray-300 px-3 py-2">{{ row.department }}</td>
              <td class="border border-gray-300 px-3 py-2">{{ row.category }}</td>
              <td class="border border-gray-300 px-3 py-2 text-right font-mono">{{ formatCurrency(row.amountRap) }}</td>
              <td class="border border-gray-300 px-3 py-2 text-right">{{ row.qtyRap }}</td>
              <td class="border border-gray-300 px-3 py-2 text-right font-mono text-erp-red">{{ formatCurrency(row.remaining) }}</td>
              <td class="border border-gray-300 px-3 py-2 text-right font-mono">{{ formatCurrency(row.po) }}</td>
              <td class="border border-gray-300 px-3 py-2 text-right font-mono">{{ formatCurrency(row.cbr) }}</td>
              <td class="border border-gray-300 px-3 py-2 text-right font-mono text-erp-green">{{ formatCurrency(row.paid) }}</td>
              <td class="border border-gray-300 px-3 py-2 text-right font-mono text-erp-orange">{{ formatCurrency(row.unpaid) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </Panel>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { Search, Inbox } from 'lucide-vue-next'
import Panel from '../components/Panel.vue'

const filters = reactive({
  periodStart: '2026-05-29',
  periodEnd: '2026-05-29',
  transStart: '2026-05-29',
  transEnd: '2026-05-29',
  type: 'detail',
  costCategory: ['ALL'],
  department: ['ALL'],
  costUnit: ['ALL'],
})

const results = ref([])

const search = () => {
  // Simulate API call
  results.value = [
    {
      id: 1,
      department: 'Engineering',
      category: 'CAPEX',
      amountRap: 150000000,
      qtyRap: 5,
      remaining: 50000000,
      po: 80000000,
      cbr: 20000000,
      paid: 70000000,
      unpaid: 30000000,
    },
    {
      id: 2,
      department: 'Finance',
      category: 'OPEX',
      amountRap: 75000000,
      qtyRap: 12,
      remaining: 15000000,
      po: 45000000,
      cbr: 15000000,
      paid: 50000000,
      unpaid: 10000000,
    },
  ]
}

const formatCurrency = (value) => {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0,
  }).format(value)
}
</script>