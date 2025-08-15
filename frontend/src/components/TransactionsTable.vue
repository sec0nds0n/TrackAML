<script setup>
import { ref, watch, onMounted, computed } from 'vue'
import { useToast } from 'primevue/usetoast'

const props = defineProps({
  wallet: { type: String, required: true },
  apiBase: { type: String, default: 'http://127.0.0.1:5000/api' },
  pageSize: { type: Number, default: 10 },
  compact: { type: Boolean, default: false }
})

const toast = useToast()
const loading = ref(false)
const rows = ref([])
const page = ref(1)
const perPage = ref(props.pageSize)
const total = ref(0)
const sortBy = ref('timestamp')
const sortOrder = ref('desc')

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / perPage.value)))

function fmtTs(ts) {
  if (!ts) return '-'
  const d = new Date(ts)
  return isNaN(d) ? ts : d.toLocaleString()
}

function fmtAmount(v) {
  if (v === null || v === undefined) return '-'
  const num = Number(v)
  if (Number.isNaN(num)) return String(v)
  return num.toFixed(8).replace(/\.?0+$/,'')
}

function inferType(row) {
  const me = (props.wallet || '').toLowerCase()
  const sender = (row.sender || '').toLowerCase()
  return sender === me ? 'outgoing' : 'incoming'
}

async function fetchTransactions() {
  if (!props.wallet) return
  loading.value = true
  try {
    const qs = new URLSearchParams({
      wallet: props.wallet,
      page: String(page.value),
      per_page: String(perPage.value),
      // backend /api/wallets/transactions sekarang fixed ORDER BY timestamp DESC,
      // tapi kalau nanti ditambah sort_by/order di backend, ini sudah siap:
      sort_by: sortBy.value,
      order: sortOrder.value
    })
    const url = `${props.apiBase}/wallets/transactions?${qs.toString()}`
    const res = await fetch(url, { headers: { Accept: 'application/json' } })
    if (!res.ok) {
      const msg = `Gagal mengambil transaksi (HTTP ${res.status}).`
      toast.add({ severity: 'error', summary: 'Fetch error', detail: msg, life: 2500 })
      throw new Error(msg)
    }
    const data = await res.json()
    // data shape dari backend:
    // { transactions: [{sender, receiver, value, timestamp}], total, page, per_page }
    rows.value = (data.transactions || []).map(r => ({
      ...r,
      // tambahkan helper untuk UI
      type: inferType(r),
      counterparty: inferType(r) === 'incoming' ? r.sender : r.receiver
    }))
    total.value = data.total ?? 0
    page.value = data.page ?? page.value
    perPage.value = data.per_page ?? perPage.value
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function go(p) {
  const next = Math.min(Math.max(1, p), totalPages.value)
  if (next !== page.value) {
    page.value = next
    fetchTransactions()
  }
}

function onChangePageSize(e) {
  perPage.value = Number(e.target.value) || 10
  page.value = 1
  fetchTransactions()
}

watch(() => props.wallet, () => {
  page.value = 1
  fetchTransactions()
})

onMounted(fetchTransactions)
</script>

<template>
  <div :class="['p-6', compact ? 'p-4' : 'p-6']">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Transaction History</h3>
      <div class="flex items-center gap-3">
        <label class="text-sm text-gray-600 dark:text-gray-300">Rows</label>
        <select
          :value="perPage"
          @change="onChangePageSize"
          class="px-3 py-1 bg-gray-100 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-sm"
        >
          <option :value="10">10</option>
          <option :value="20">20</option>
          <option :value="50">50</option>
        </select>
      </div>
    </div>

    <div class="overflow-x-auto">
      <table class="w-full">
        <thead>
          <tr class="border-b border-gray-200 dark:border-gray-700 text-left">
            <th class="py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Type</th>
            <th class="py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Sender</th>
            <th class="py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Receiver</th>
            <th class="py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Amount (ETH)</th>
            <th class="py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Timestamp</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="5" class="py-6 text-center text-gray-500 dark:text-gray-400">Loading…</td>
          </tr>
          <tr v-else-if="rows.length === 0">
            <td colspan="5" class="py-6 text-center text-gray-500 dark:text-gray-400">No transactions</td>
          </tr>
          <tr
            v-else
            v-for="(tx, i) in rows"
            :key="i"
            class="border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
          >
            <td class="py-3 px-4">
              <span
                :class="tx.type === 'incoming'
                  ? 'text-green-600 dark:text-green-400'
                  : 'text-red-600 dark:text-red-400'"
                class="font-medium"
              >
                {{ tx.type === 'incoming' ? '↓ Incoming' : '↑ Outgoing' }}
              </span>
            </td>
            <td class="py-3 px-4 font-mono break-all">{{ tx.sender }}</td>
            <td class="py-3 px-4 font-mono break-all">{{ tx.receiver }}</td>
            <td class="py-3 px-4 font-mono">{{ fmtAmount(tx.value) }}</td>
            <td class="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">{{ fmtTs(tx.timestamp) }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div class="flex items-center justify-between mt-4">
      <div class="text-sm text-gray-600 dark:text-gray-400">
        Page {{ page }} / {{ totalPages }} · {{ total }} total
      </div>
      <div class="flex items-center gap-2">
        <button
          class="px-3 py-1 rounded-lg bg-gray-100 dark:bg-gray-700 disabled:opacity-50"
          :disabled="page <= 1"
          @click="go(page - 1)"
        >
          Prev
        </button>
        <button
          class="px-3 py-1 rounded-lg bg-gray-100 dark:bg-gray-700 disabled:opacity-50"
          :disabled="page >= totalPages"
          @click="go(page + 1)"
        >
          Next
        </button>
      </div>
    </div>
  </div>
</template>