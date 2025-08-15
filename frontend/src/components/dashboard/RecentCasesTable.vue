<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  // data sudah dipetakan di Dashboard1.vue (punya _rawId, id, customer, crypto, amount, riskLevel, status, date)
  recentCases: { type: Array, default: () => [] }
})

const router = useRouter()

// Pakai langsung data dari parent; fallback kosong
const rows = computed(() => Array.isArray(props.recentCases) ? props.recentCases : [])

const viewCase = (row) => {
  // gunakan _rawId (numeric dari DB). Jika tidak ada, coba parse angka dari id.
  const raw = row?._rawId ?? row?.id
  const id = typeof raw === 'number' ? raw : parseInt(raw, 10)
  if (!Number.isNaN(id)) router.push(`/monitoring/detail/${id}`)
}

const formatDate = (date) => {
  if (!date) return ''
  const d = date instanceof Date ? date : new Date(date)
  return d.toLocaleDateString()
}

const getStatusLabel = (s) => ({
  new: 'New',
  in_review: 'In Review',
  pending_docs: 'Pending Documents',
  escalated: 'Escalated',
  approved: 'Approved',
  rejected: 'Rejected',
  'Under Review': 'Under Review',
  Pending: 'Pending',
  Resolved: 'Resolved',
  Investigating: 'Investigating'
}[s] || s)

const formatWalletAddress = (address) =>
  !address ? '' : `${address.slice(0,6)}...${address.slice(-4)}`
</script>

<template>
  <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 p-6">
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-3">
        <div class="p-2 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-lg">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2"/>
          </svg>
        </div>
        <h3 class="text-lg font-bold text-gray-900 dark:text-white">Recent Crypto AML Cases</h3>
      </div>

      <button 
        @click="$router.push('/monitoring/cases')"
        class="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 font-semibold flex items-center gap-1">
        View All Cases
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
        </svg>
      </button>
    </div>

    <!-- Empty state -->
    <div v-if="rows.length === 0" class="text-center py-8">
      <svg class="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2"/>
      </svg>
      <p class="text-gray-600 dark:text-gray-400">No recent cases found</p>
    </div>

    <!-- Table -->
    <div v-else class="overflow-x-auto">
      <table class="w-full">
        <thead>
          <tr class="border-b-2 border-gray-200 dark:border-gray-700">
            <th class="text-left text-xs font-bold text-gray-600 dark:text-gray-400 uppercase tracking-wider py-4">Case ID</th>
            <th class="text-left text-xs font-bold text-gray-600 dark:text-gray-400 uppercase tracking-wider py-4">Wallet/Entity</th>
            <th class="text-left text-xs font-bold text-gray-600 dark:text-gray-400 uppercase tracking-wider py-4">Crypto</th>
            <th class="text-left text-xs font-bold text-gray-600 dark:text-gray-400 uppercase tracking-wider py-4">Amount</th>
            <th class="text-left text-xs font-bold text-gray-600 dark:text-gray-400 uppercase tracking-wider py-4">Priority</th>
            <th class="text-left text-xs font-bold text-gray-600 dark:text-gray-400 uppercase tracking-wider py-4">Status</th>
            <th class="text-left text-xs font-bold text-gray-600 dark:text-gray-400 uppercase tracking-wider py-4">Date</th>
            <th class="text-left text-xs font-bold text-gray-600 dark:text-gray-400 uppercase tracking-wider py-4">Actions</th>
          </tr>
        </thead>

        <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
          <tr v-for="row in rows" :key="row.id" class="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
            <td class="py-4">
              <span class="text-sm font-bold text-blue-600 dark:text-blue-400 cursor-pointer hover:underline"
                    @click="viewCase(row)">
                {{ row.id }}
              </span>
            </td>

            <td class="py-4">
              <div class="flex flex-col">
                <span class="text-sm font-medium text-gray-900 dark:text-white font-mono">
                  {{ row.wallet ? formatWalletAddress(row.wallet) : (row.customer || 'N/A') }}
                </span>
                <span class="text-xs text-gray-500 dark:text-gray-400">
                  {{ row.wallet ? 'Wallet' : (row.customer?.includes('Wallet') ? 'Individual' : 'Exchange') }}
                </span>
              </div>
            </td>

            <td class="py-4">
              <div class="inline-flex items-center gap-1 px-2 py-1 rounded-md text-xs font-bold"
                   :class="{
                     'bg-orange-100 dark:bg-orange-900/50 text-orange-800 dark:text-orange-300': row.crypto === 'BTC',
                     'bg-blue-100 dark:bg-blue-900/50 text-blue-800 dark:text-blue-300': row.crypto === 'ETH',
                     'bg-green-100 dark:bg-green-900/50 text-green-800 dark:text-green-300': row.crypto === 'USDT' || row.crypto === 'USDC',
                     'bg-gray-100 dark:bg-gray-900/50 text-gray-800 dark:text-gray-300': !['BTC','ETH','USDT','USDC'].includes(row.crypto)
                   }">
                <div class="w-2 h-2 rounded-full"
                     :class="{
                       'bg-orange-500': row.crypto === 'BTC',
                       'bg-blue-500': row.crypto === 'ETH',
                       'bg-green-500': row.crypto === 'USDT' || row.crypto === 'USDC',
                       'bg-gray-500': !['BTC','ETH','USDT','USDC'].includes(row.crypto)
                     }"></div>
                {{ row.crypto }}
              </div>
            </td>

            <td class="py-4">
              <span class="text-sm font-semibold text-gray-900 dark:text-white">{{ row.amount }}</span>
            </td>

            <td class="py-4">
              <span class="inline-flex px-3 py-1 text-xs font-bold rounded-full"
                    :class="{
                      'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300': (row.priority || row.riskLevel) === 'high' || (row.priority || row.riskLevel) === 'High',
                      'bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-300': (row.priority || row.riskLevel) === 'medium' || (row.priority || row.riskLevel) === 'Medium',
                      'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300': (row.priority || row.riskLevel) === 'low' || (row.priority || row.riskLevel) === 'Low'
                    }">
                {{ row.priority || row.riskLevel || 'Medium' }}
              </span>
            </td>

            <td class="py-4">
              <span class="inline-flex px-3 py-1 text-xs font-bold rounded-full"
                    :class="{
                      'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300': row.status === 'new',
                      'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300': ['in_review','Under Review','Pending','pending_docs'].includes(row.status),
                      'bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-300': row.status === 'escalated',
                      'bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-300': row.status === 'Investigating',
                      'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300': ['approved','Resolved'].includes(row.status),
                      'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300': row.status === 'rejected'
                    }">
                {{ getStatusLabel(row.status) }}
              </span>
            </td>

            <td class="py-4">
              <div class="flex flex-col">
                <span class="text-sm font-medium text-gray-900 dark:text-white">
                  {{ formatDate(row.createdAt || row.date) }}
                </span>
                <span class="text-xs text-gray-500 dark:text-gray-400">
                  {{ row.createdAt ? new Date(row.createdAt).toLocaleTimeString() : '' }}
                </span>
              </div>
            </td>

            <td class="py-4">
              <button
                @click="viewCase(row)"
                class="p-1 text-blue-600 dark:text-blue-400 hover:bg-blue-100 dark:hover:bg-blue-900/30 rounded-md transition-colors"
                title="View Details">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>