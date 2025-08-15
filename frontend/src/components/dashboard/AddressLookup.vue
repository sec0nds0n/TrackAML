<template>
  <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 p-6">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-3">
        <div class="p-2 bg-gradient-to-r from-green-500 to-emerald-500 rounded-lg">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
        </div>
        <h3 class="text-lg font-bold text-gray-900 dark:text-white">Address Lookup</h3>
      </div>
      <button
        @click="openLookupModal"
        class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors font-medium text-sm"
      >
        Advanced Search
      </button>
    </div>

    <!-- Quick Search -->
    <div class="space-y-4">
      <div class="relative">
        <input
          v-model="quickSearchAddress"
          @keyup.enter="performQuickSearch"
          type="text"
          placeholder="Enter wallet address or transaction hash..."
          class="w-full px-4 py-3 pl-12 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
        >
        <svg class="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
      </div>

      <div class="flex gap-2">
        <button
          @click="performQuickSearch"
          :disabled="!quickSearchAddress || isSearching"
          class="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-colors font-medium"
        >
          <span v-if="!isSearching">Search</span>
          <span v-else class="flex items-center justify-center gap-2">
            <svg class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
            </svg>
            Searching...
          </span>
        </button>
        <button
          @click="clearSearch"
          class="px-4 py-2 bg-gray-200 dark:bg-gray-600 hover:bg-gray-300 dark:hover:bg-gray-500 text-gray-700 dark:text-gray-200 rounded-lg transition-colors"
        >
          Clear
        </button>
      </div>
    </div>

    <!-- Recent Searches -->
    <div v-if="displayRecent.length > 0" class="mt-6">
      <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Recent Searches</h4>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="item in displayRecent.slice(0, 5)"
          :key="item.address"
          @click="quickSearchAddress = item.address; performQuickSearch()"
          class="px-3 py-1 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-full text-xs transition-colors"
        >
          {{ item.address.length > 14 ? (item.address.slice(0, 8) + '...' + item.address.slice(-6)) : item.address }}
        </button>
      </div>
    </div>

    <!-- Result Action Panel (2 opsi) -->
    <div
      v-if="foundSummary"
      class="mt-6 p-4 rounded-xl border border-emerald-200 dark:border-emerald-900/40 bg-emerald-50 dark:bg-emerald-900/10"
    >
      <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        <div>
          <div class="font-mono text-sm text-gray-900 dark:text-white">{{ foundSummary.address }}</div>
          <div class="text-xs text-gray-600 dark:text-gray-400">
            {{ txTotal }} transactions • Last Activity: {{ formatDateTime(foundSummary.lastActivity) }}
          </div>
        </div>
        <div class="flex gap-2">
          <button
            @click="viewTransactions(foundSummary.address)"
            class="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm font-semibold"
          >
            View Transactions
          </button>
          <button
            @click="openWalletDetail(foundSummary.address)"
            class="px-4 py-2 bg-white border border-gray-300 dark:border-gray-600 dark:bg-gray-700 text-gray-700 dark:text-gray-200 rounded-lg text-sm font-semibold"
          >
            View Wallet Detail
          </button>
        </div>
      </div>
    </div>

    <!-- Transactions Table -->
    <div v-if="transactions.length" class="mt-6">
      <div class="flex items-center justify-between mb-3">
        <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300">Transactions</h4>
        <span class="text-xs text-gray-500 dark:text-gray-400">{{ txTotal }} total</span>
      </div>

      <div class="overflow-x-auto rounded-xl border border-gray-200 dark:border-gray-700">
        <table class="min-w-full text-sm">
          <thead class="bg-gray-50 dark:bg-gray-700/50">
            <tr>
              <th class="text-left px-4 py-3">Timestamp</th>
              <th class="text-left px-4 py-3">Sender</th>
              <th class="text-left px-4 py-3">Receiver</th>
              <th class="text-left px-4 py-3">Value</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="tx in transactions" :key="txKey(tx)">
              <td class="px-4 py-2">{{ formatDateTime(tx.timestamp) }}</td>
              <td class="px-4 py-2 font-mono">{{ tx.sender }}</td>
              <td class="px-4 py-2 font-mono">{{ tx.receiver }}</td>
              <td class="px-4 py-2">{{ tx.value }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div class="flex items-center justify-end gap-2 mt-3">
        <button
          class="px-3 py-1 rounded border dark:border-gray-600"
          :disabled="txPage === 1 || loadingTx"
          @click="changePage(txPage - 1)"
        >
          Prev
        </button>
        <span class="text-xs text-gray-500 dark:text-gray-400">Page {{ txPage }}</span>
        <button
          class="px-3 py-1 rounded border dark:border-gray-600"
          :disabled="txPage * txPerPage >= txTotal || loadingTx"
          @click="changePage(txPage + 1)"
        >
          Next
        </button>
      </div>
    </div>

    <!-- Empty -->
    <div v-if="hasSearched && !foundSummary && !transactions.length" class="mt-6 text-center py-8">
      <svg class="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6-4h6m2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
      </svg>
      <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">No data for this wallet</h3>
      <p class="text-gray-500 dark:text-gray-400">Try a different address.</p>
    </div>

    <!-- Advanced Lookup Modal -->
    <Dialog
      v-model:visible="showLookupModal"
      modal
      header="Advanced Address Lookup"
      :style="{ width: '50rem' }"
      :breakpoints="{ '1199px': '75vw', '575px': '90vw' }"
      class="p-fluid"
    >
      <template #default>
        <form @submit.prevent="performAdvancedSearch" class="space-y-6">
          <!-- type -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Search Type</label>
            <div class="grid grid-cols-2 gap-3">
              <label class="flex items-center p-3 border border-gray-200 dark:border-gray-600 rounded-lg cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700">
                <input v-model="searchForm.type" type="radio" value="address" class="mr-3">
                <div>
                  <div class="font-medium text-gray-900 dark:text-white">Wallet Address</div>
                  <div class="text-sm text-gray-500 dark:text-gray-400">Search by crypto address</div>
                </div>
              </label>
              <label class="flex items-center p-3 border border-gray-200 dark:border-gray-600 rounded-lg cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700">
                <input v-model="searchForm.type" type="radio" value="transaction" class="mr-3">
                <div>
                  <div class="font-medium text-gray-900 dark:text-white">Transaction Hash</div>
                  <div class="text-sm text-gray-500 dark:text-gray-400">Search by TX hash</div>
                </div>
              </label>
            </div>
          </div>

          <!-- query -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {{ searchForm.type === 'address' ? 'Wallet Address' : 'Transaction Hash' }}
            </label>
            <input
              v-model="searchForm.query"
              type="text"
              :placeholder="searchForm.type === 'address' ? 'Enter wallet address...' : 'Enter transaction hash...'"
              class="w-full px-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
              required
            >
          </div>

          <!-- crypto (opsional UI) -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Cryptocurrency</label>
            <select
              v-model="searchForm.crypto"
              class="w-full px-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent text-gray-900 dark:text-white"
            >
              <option value="">All Cryptocurrencies</option>
              <option value="BTC">Bitcoin (BTC)</option>
              <option value="ETH">Ethereum (ETH)</option>
              <option value="LTC">Litecoin (LTC)</option>
              <option value="BCH">Bitcoin Cash (BCH)</option>
              <option value="XMR">Monero (XMR)</option>
              <option value="ZEC">Zcash (ZEC)</option>
            </select>
          </div>

          <!-- filters -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">From Date</label>
              <input
                v-model="searchForm.dateFrom"
                type="date"
                class="w-full px-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent text-gray-900 dark:text-white"
              >
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">To Date</label>
              <input
                v-model="searchForm.dateTo"
                type="date"
                class="w-full px-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent text-gray-900 dark:text-white"
              >
            </div>
          </div>

          <div class="flex items-center">
            <input v-model="searchForm.includeSanctioned" type="checkbox" id="sanctioned" class="mr-3">
            <label for="sanctioned" class="text-sm font-medium text-gray-700 dark:text-gray-300">
              Include sanctioned addresses in results
            </label>
          </div>

          <div class="flex gap-3 pt-4">
            <button
              type="submit"
              :disabled="!searchForm.query || isSearching"
              class="flex-1 px-6 py-3 bg-green-600 hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-colors font-medium"
            >
              <span v-if="!isSearching">Search Address</span>
              <span v-else class="flex items-center justify-center gap-2">
                <svg class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                </svg>
                Searching...
              </span>
            </button>
            <button
              type="button"
              @click="resetForm"
              class="px-6 py-3 bg-gray-200 dark:bg-gray-600 hover:bg-gray-300 dark:hover:bg-gray-500 text-gray-700 dark:text-gray-200 rounded-lg transition-colors font-medium"
            >
              Reset
            </button>
            <button
              type="button"
              @click="closeLookupModal"
              class="px-6 py-3 bg-red-100 dark:bg-red-900/30 hover:bg-red-200 dark:hover:bg-red-900/50 text-red-700 dark:text-red-300 rounded-lg transition-colors font-medium"
            >
              Cancel
            </button>
          </div>
        </form>
      </template>
    </Dialog>

    <!-- Address Detail Modal -->
    <AddressDetail
      :addressData="selectedAddress"
      :showModal="showAddressDetail"
      @close="closeAddressDetail"
    />
  </div>
</template>

<script setup>
import Dialog from 'primevue/dialog'
import { useToast } from 'primevue/usetoast'
import { reactive, ref, computed } from 'vue'
import AddressDetail from './AddressDetail.vue'

const toast = useToast()
const props = defineProps({
  // dari backend: [{ address, queried_at }]
  recentSearches: { type: Array, default: () => [] }
})

/* ---------- ENV / API base ---------- */
const API_BASE = import.meta.env.VITE_API_BASE ?? '/api'

/* ---------- state ---------- */
const quickSearchAddress = ref('')
const isSearching = ref(false)
const showLookupModal = ref(false)
const showAddressDetail = ref(false)
const hasSearched = ref(false)

const foundSummary = ref(null)           // { address, lastActivity }
const transactions = ref([])
const txTotal = ref(0)
const txPage = ref(1)
const txPerPage = ref(20)
const loadingTx = ref(false)

const selectedAddress = ref({})
const localRecentSearches = ref([])

const displayRecent = computed(() => {
  const list = (props.recentSearches && props.recentSearches.length)
    ? props.recentSearches
    : localRecentSearches.value
  return list.map(r => ({ address: r.address, timestamp: r.timestamp ?? r.queried_at ?? null }))
})

/* ---------- utils ---------- */
const formatDateTime = (d) => {
  if (!d) return '-'
  const date = typeof d === 'string' ? new Date(d) : d
  return date.toLocaleString()
}
const txKey = (tx) => `${tx.timestamp}-${tx.sender}-${tx.receiver}-${tx.value}`
const inferCrypto = (addr) => addr?.startsWith('0x') ? 'ETH' : 'BTC'

const getJSON = async (url) => {
  const res = await fetch(url)
  if (!res.ok) throw new Error(`${res.status} ${await res.text()}`)
  return res.json()
}

/* ---------- SEARCH (Quick & Advanced) ---------- */
const checkWalletAndPrepare = async (address) => {
  // gunakan pagination endpoint: ambil 1 baris untuk cek total & last activity
  const u = `${API_BASE}/wallets/transactions?wallet=${encodeURIComponent(address)}&page=1&per_page=1`
  const data = await getJSON(u)
  txTotal.value = data.total ?? 0
  if (txTotal.value > 0) {
    const last = data.transactions?.[0]?.timestamp ?? null
    foundSummary.value = { address, lastActivity: last }
    transactions.value = []
    txPage.value = 1
  } else {
    foundSummary.value = null
    transactions.value = []
  }
}

const performQuickSearch = async () => {
  const q = quickSearchAddress.value.trim()
  if (!q) return
  isSearching.value = true
  hasSearched.value = true
  try {
    await checkWalletAndPrepare(q)

    // update recent lokal (fallback bila props kosong)
    const i = localRecentSearches.value.findIndex(s => s.address === q)
    if (i !== -1) localRecentSearches.value.splice(i, 1)
    localRecentSearches.value.unshift({ address: q, timestamp: new Date() })
    if (localRecentSearches.value.length > 10) localRecentSearches.value.length = 10

    if (foundSummary.value) {
      toast.add({ severity: 'success', summary: 'Wallet Found', detail: `Transactions: ${txTotal.value}`, life: 2500 })
    } else {
      toast.add({ severity: 'warn', summary: 'Not Found', detail: 'No transactions for this address', life: 2500 })
    }
  } catch (err) {
    console.error(err)
    toast.add({ severity: 'error', summary: 'Search Failed', detail: String(err.message || err), life: 3500 })
  } finally {
    isSearching.value = false
  }
}

/* Advanced form */
const searchForm = reactive({
  type: 'address',
  query: '',
  crypto: '',
  dateFrom: '',
  dateTo: '',
  includeSanctioned: false
})
const performAdvancedSearch = async () => {
  isSearching.value = true
  hasSearched.value = true
  try {
    const q = (searchForm.query || '').trim()
    await checkWalletAndPrepare(q)
    // simpan juga ke recent lokal
    if (q) {
      const i = localRecentSearches.value.findIndex(s => s.address === q)
      if (i !== -1) localRecentSearches.value.splice(i, 1)
      localRecentSearches.value.unshift({ address: q, timestamp: new Date() })
      if (localRecentSearches.value.length > 10) localRecentSearches.value.length = 10
    }
    showLookupModal.value = false
    if (foundSummary.value) {
      toast.add({ severity: 'success', summary: 'Wallet Found', detail: `Transactions: ${txTotal.value}`, life: 2500 })
    } else {
      toast.add({ severity: 'warn', summary: 'Not Found', detail: 'No transactions for this address', life: 2500 })
    }
  } catch (err) {
    console.error(err)
    toast.add({ severity: 'error', summary: 'Search Failed', detail: String(err.message || err), life: 3500 })
  } finally {
    isSearching.value = false
  }
}

/* ---------- Actions ---------- */
const viewTransactions = async (address) => {
  await fetchTransactions(address, 1)
}

const fetchTransactions = async (address, page) => {
  loadingTx.value = true
  try {
    const u = `${API_BASE}/wallets/transactions?wallet=${encodeURIComponent(address)}&page=${page}&per_page=${txPerPage.value}`
    const data = await getJSON(u)
    transactions.value = data.transactions ?? []
    txTotal.value = data.total ?? 0
    txPage.value = data.page ?? page
  } catch (err) {
    console.error(err)
    toast.add({ severity: 'error', summary: 'Load Transactions Failed', detail: String(err.message || err), life: 3500 })
  } finally {
    loadingTx.value = false
  }
}

const changePage = async (p) => {
  if (!foundSummary.value) return
  await fetchTransactions(foundSummary.value.address, p)
}

const openWalletDetail = (addr) => {
  selectedAddress.value = { address: addr }
  showAddressDetail.value = true
}

/* ---------- Modal & misc ---------- */
const openLookupModal = () => { showLookupModal.value = true }
const closeLookupModal = () => { showLookupModal.value = false }
const resetForm = () => Object.assign(searchForm, { type:'address', query:'', crypto:'', dateFrom:'', dateTo:'', includeSanctioned:false })
const clearSearch = () => { quickSearchAddress.value = ''; foundSummary.value = null; transactions.value = []; hasSearched.value = false }

const closeAddressDetail = () => {
  showAddressDetail.value = false
  selectedAddress.value = {}
}
const viewConnectedAddress = (connection) => {
  // placeholder: tampilkan detail address terhubung sebagai modal
  openWalletDetail(connection.address)
}
</script>

<style scoped>
/* PrimeVue Dialog Customization (singkat) */
:deep(.p-dialog){border-radius:1rem;box-shadow:0 25px 50px -12px rgba(0,0,0,.25)}
:deep(.p-dialog-header){background:linear-gradient(135deg,#f8fafc 0%,#e2e8f0 100%);border-bottom:1px solid #e2e8f0;border-radius:1rem 1rem 0 0;padding:1.5rem}
:deep(.p-dialog-title){font-weight:700;font-size:1.25rem;color:#1f2937}
:deep(.p-dialog-content){padding:1.5rem;background:#fff}
:deep(.p-dialog-footer){background:#f8fafc;border-top:1px solid #e2e8f0;border-radius:0 0 1rem 1rem;padding:1rem 1.5rem}
.dark :deep(.p-dialog-header){background:linear-gradient(135deg,#1f2937 0%,#111827 100%);border-bottom-color:#374151}
.dark :deep(.p-dialog-title){color:#f9fafb}
.dark :deep(.p-dialog-content){background:#1f2937;color:#f9fafb}
.dark :deep(.p-dialog-footer){background:#111827;border-top-color:#374151}
</style>
