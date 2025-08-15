<template>
  <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 p-6">
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-3">
        <div class="p-2 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-lg">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path>
          </svg>
        </div>
        <h3 class="text-lg font-bold text-gray-900 dark:text-white">Search Results</h3>
        <span class="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-full text-sm font-medium">
          {{ results.length }} found
        </span>
      </div>
      
      <div class="flex items-center gap-2">
        <select 
          v-model="sortBy"
          @change="sortResults"
          class="px-3 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 dark:text-white"
        >
          <option value="relevance">Sort by Relevance</option>
          <option value="risk">Sort by Risk Level</option>
          <option value="balance">Sort by Balance</option>
          <option value="activity">Sort by Last Activity</option>
        </select>
        
        <button
          @click="toggleView"
          class="p-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors"
          :title="viewMode === 'grid' ? 'Switch to List View' : 'Switch to Grid View'"
        >
          <svg v-if="viewMode === 'grid'" class="w-5 h-5 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16"></path>
          </svg>
          <svg v-else class="w-5 h-5 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"></path>
          </svg>
        </button>
      </div>
    </div>

    <!-- Filters -->
    <div class="mb-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
      <div class="flex items-center justify-between mb-3">
        <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300">Filters</h4>
        <button 
          @click="clearFilters"
          class="text-sm text-blue-600 dark:text-blue-400 hover:underline"
        >
          Clear All
        </button>
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <!-- Risk Level Filter -->
        <div>
          <label class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-2">Risk Level</label>
          <div class="space-y-1">
            <label v-for="risk in riskLevels" :key="risk" class="flex items-center text-sm">
              <input 
                v-model="activeFilters.riskLevels" 
                :value="risk" 
                type="checkbox" 
                class="mr-2 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              >
              <span :class="getRiskTextClass(risk)">{{ risk }}</span>
            </label>
          </div>
        </div>

        <!-- Cryptocurrency Filter -->
        <div>
          <label class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-2">Cryptocurrency</label>
          <div class="space-y-1">
            <label v-for="crypto in cryptocurrencies" :key="crypto" class="flex items-center text-sm">
              <input 
                v-model="activeFilters.cryptocurrencies" 
                :value="crypto" 
                type="checkbox" 
                class="mr-2 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              >
              <span class="text-gray-700 dark:text-gray-300">{{ crypto }}</span>
            </label>
          </div>
        </div>

        <!-- Balance Range -->
        <div>
          <label class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-2">Balance Range</label>
          <div class="space-y-2">
            <input
              v-model="activeFilters.minBalance"
              type="number"
              step="0.00000001"
              placeholder="Min"
              class="w-full px-2 py-1 text-sm bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded focus:ring-1 focus:ring-blue-500 text-gray-900 dark:text-white"
            >
            <input
              v-model="activeFilters.maxBalance"
              type="number"
              step="0.00000001"
              placeholder="Max"
              class="w-full px-2 py-1 text-sm bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded focus:ring-1 focus:ring-blue-500 text-gray-900 dark:text-white"
            >
          </div>
        </div>

        <!-- Activity Filter -->
        <div>
          <label class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-2">Last Activity</label>
          <select 
            v-model="activeFilters.activityPeriod"
            class="w-full px-2 py-1 text-sm bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded focus:ring-1 focus:ring-blue-500 text-gray-900 dark:text-white"
          >
            <option value="">Any time</option>
            <option value="1h">Last hour</option>
            <option value="24h">Last 24 hours</option>
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Results Display -->
    <div v-if="filteredResults.length === 0" class="text-center py-12">
      <svg class="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6-4h6m2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">No Results Found</h3>
      <p class="text-gray-500 dark:text-gray-400">Try adjusting your filters or search criteria.</p>
    </div>

    <!-- Grid View -->
    <div v-else-if="viewMode === 'grid'" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="result in paginatedResults"
        :key="result.id"
        class="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-600 transition-all duration-200 cursor-pointer hover:shadow-md"
        @click="viewDetails(result)"
      >
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-2">
            <div :class="getRiskBadgeClass(result.riskLevel)" class="px-2 py-1 rounded-full text-xs font-medium">
              {{ result.riskLevel }}
            </div>
            <span class="text-xs font-medium text-gray-500 dark:text-gray-400 bg-gray-200 dark:bg-gray-600 px-2 py-1 rounded">
              {{ result.crypto }}
            </span>
          </div>
          <button
            @click.stop="toggleWatchlist(result)"
            class="p-1 hover:bg-gray-200 dark:hover:bg-gray-500 rounded transition-colors"
            :title="result.isWatched ? 'Remove from Watchlist' : 'Add to Watchlist'"
          >
            <svg 
              :class="result.isWatched ? 'text-yellow-500' : 'text-gray-400'"
              class="w-4 h-4" 
              fill="currentColor" 
              viewBox="0 0 24 24"
            >
              <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"></path>
            </svg>
          </button>
        </div>
        
        <div class="font-mono text-sm text-gray-900 dark:text-white mb-2 truncate">
          {{ result.address }}
        </div>
        
        <div class="grid grid-cols-2 gap-2 text-xs text-gray-500 dark:text-gray-400 mb-3">
          <div>
            <span class="font-medium">Balance:</span>
            <div class="text-gray-900 dark:text-white">{{ result.balance }} {{ result.crypto }}</div>
          </div>
          <div>
            <span class="font-medium">Transactions:</span>
            <div class="text-gray-900 dark:text-white">{{ result.transactionCount }}</div>
          </div>
        </div>
        
        <div class="flex items-center justify-between text-xs">
          <span class="text-gray-500 dark:text-gray-400">{{ result.lastActivity }}</span>
          <div class="flex items-center gap-1">
            <div v-for="tag in result.tags.slice(0, 2)" :key="tag" :class="getTagClass(tag)" class="px-2 py-1 rounded text-xs">
              {{ tag }}
            </div>
            <span v-if="result.tags.length > 2" class="text-gray-400">+{{ result.tags.length - 2 }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- List View -->
    <div v-else class="overflow-x-auto">
      <table class="w-full">
        <thead>
          <tr class="border-b border-gray-200 dark:border-gray-700">
            <th class="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Address</th>
            <th class="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Crypto</th>
            <th class="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Balance</th>
            <th class="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Risk Level</th>
            <th class="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Transactions</th>
            <th class="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Last Activity</th>
            <th class="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Tags</th>
            <th class="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="result in paginatedResults"
            :key="result.id"
            class="border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors cursor-pointer"
            @click="viewDetails(result)"
          >
            <td class="py-3 px-4">
              <div class="font-mono text-sm text-blue-600 dark:text-blue-400 hover:underline">
                {{ result.address.substring(0, 16) }}...{{ result.address.substring(result.address.length - 8) }}
              </div>
            </td>
            <td class="py-3 px-4">
              <div class="flex items-center gap-2">
                <div :class="getCryptoIconClass(result.crypto)" class="w-5 h-5 rounded-full flex items-center justify-center text-white text-xs font-bold">
                  {{ getCryptoSymbol(result.crypto) }}
                </div>
                <span class="text-gray-900 dark:text-white">{{ result.crypto }}</span>
              </div>
            </td>
            <td class="py-3 px-4">
              <div class="text-gray-900 dark:text-white font-mono">{{ result.balance }}</div>
              <div class="text-xs text-gray-500 dark:text-gray-400">${{ formatCurrency(result.balanceUSD) }}</div>
            </td>
            <td class="py-3 px-4">
              <span :class="getRiskBadgeClass(result.riskLevel)" class="px-2 py-1 rounded-full text-xs font-medium">
                {{ result.riskLevel }}
              </span>
            </td>
            <td class="py-3 px-4 text-gray-900 dark:text-white">{{ result.transactionCount }}</td>
            <td class="py-3 px-4 text-gray-600 dark:text-gray-400 text-sm">{{ result.lastActivity }}</td>
            <td class="py-3 px-4">
              <div class="flex flex-wrap gap-1">
                <span
                  v-for="tag in result.tags.slice(0, 2)"
                  :key="tag"
                  :class="getTagClass(tag)"
                  class="px-2 py-1 rounded text-xs"
                >
                  {{ tag }}
                </span>
                <span v-if="result.tags.length > 2" class="text-xs text-gray-400">+{{ result.tags.length - 2 }}</span>
              </div>
            </td>
            <td class="py-3 px-4">
              <div class="flex items-center gap-2">
                <button
                  @click.stop="toggleWatchlist(result)"
                  class="p-1 hover:bg-gray-200 dark:hover:bg-gray-600 rounded transition-colors"
                  :title="result.isWatched ? 'Remove from Watchlist' : 'Add to Watchlist'"
                >
                  <svg 
                    :class="result.isWatched ? 'text-yellow-500' : 'text-gray-400'"
                    class="w-4 h-4" 
                    fill="currentColor" 
                    viewBox="0 0 24 24"
                  >
                    <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"></path>
                  </svg>
                </button>
                <button
                  @click.stop="exportAddress(result)"
                  class="p-1 hover:bg-gray-200 dark:hover:bg-gray-600 rounded transition-colors"
                  title="Export Address Data"
                >
                  <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                  </svg>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="filteredResults.length > itemsPerPage" class="flex items-center justify-between mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
      <div class="text-sm text-gray-600 dark:text-gray-400">
        Showing {{ (currentPage - 1) * itemsPerPage + 1 }} to {{ Math.min(currentPage * itemsPerPage, filteredResults.length) }} of {{ filteredResults.length }} results
      </div>
      
      <div class="flex items-center gap-2">
        <button
          @click="currentPage = Math.max(1, currentPage - 1)"
          :disabled="currentPage === 1"
          class="px-3 py-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed text-gray-700 dark:text-gray-300 rounded-lg transition-colors text-sm"
        >
          Previous
        </button>
        
        <div class="flex items-center gap-1">
          <button
            v-for="page in visiblePages"
            :key="page"
            @click="currentPage = page"
            :class="page === currentPage ? 'bg-blue-600 text-white' : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'"
            class="px-3 py-2 rounded-lg transition-colors text-sm"
          >
            {{ page }}
          </button>
        </div>
        
        <button
          @click="currentPage = Math.min(totalPages, currentPage + 1)"
          :disabled="currentPage === totalPages"
          class="px-3 py-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed text-gray-700 dark:text-gray-300 rounded-lg transition-colors text-sm"
        >
          Next
        </button>
      </div>
    </div>

    <!-- Address Detail Modal -->
    <AddressDetail
      v-if="selectedAddress"
      :address-data="selectedAddress"
      :show-modal="showDetailModal"
      @close="closeDetailModal"
      @view-address="viewConnectedAddress"
    />
  </div>
</template>

<script setup>
import { useToast } from 'primevue/usetoast'
import { computed, onMounted, ref, watch } from 'vue'
import AddressDetail from './AddressDetail.vue'

const props = defineProps({
  results: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['address-selected', 'watchlist-updated'])

const toast = useToast()

// Reactive data
const viewMode = ref('grid')
const sortBy = ref('relevance')
const currentPage = ref(1)
const itemsPerPage = ref(12)
const selectedAddress = ref(null)
const showDetailModal = ref(false)

// Filter options
const riskLevels = ['Low', 'Medium', 'High', 'Critical']
const cryptocurrencies = ['BTC', 'ETH', 'LTC', 'BCH', 'XMR', 'ZEC']

// Active filters
const activeFilters = ref({
  riskLevels: [],
  cryptocurrencies: [],
  minBalance: '',
  maxBalance: '',
  activityPeriod: ''
})

// Computed properties
const filteredResults = computed(() => {
  let filtered = [...props.results]

  // Apply risk level filter
  if (activeFilters.value.riskLevels.length > 0) {
    filtered = filtered.filter(result => 
      activeFilters.value.riskLevels.includes(result.riskLevel)
    )
  }

  // Apply cryptocurrency filter
  if (activeFilters.value.cryptocurrencies.length > 0) {
    filtered = filtered.filter(result => 
      activeFilters.value.cryptocurrencies.includes(result.crypto)
    )
  }

  // Apply balance range filter
  if (activeFilters.value.minBalance) {
    filtered = filtered.filter(result => 
      parseFloat(result.balance) >= parseFloat(activeFilters.value.minBalance)
    )
  }

  if (activeFilters.value.maxBalance) {
    filtered = filtered.filter(result => 
      parseFloat(result.balance) <= parseFloat(activeFilters.value.maxBalance)
    )
  }

  // Apply activity period filter
  if (activeFilters.value.activityPeriod) {
    const now = new Date()
    const cutoff = new Date()
    
    switch (activeFilters.value.activityPeriod) {
      case '1h':
        cutoff.setHours(now.getHours() - 1)
        break
      case '24h':
        cutoff.setDate(now.getDate() - 1)
        break
      case '7d':
        cutoff.setDate(now.getDate() - 7)
        break
      case '30d':
        cutoff.setDate(now.getDate() - 30)
        break
      case '90d':
        cutoff.setDate(now.getDate() - 90)
        break
    }
    
    filtered = filtered.filter(result => {
      const activityDate = parseActivityDate(result.lastActivity)
      return activityDate >= cutoff
    })
  }

  return filtered
})

const sortedResults = computed(() => {
  const sorted = [...filteredResults.value]
  
  switch (sortBy.value) {
    case 'risk':
      return sorted.sort((a, b) => {
        const riskOrder = { 'Critical': 4, 'High': 3, 'Medium': 2, 'Low': 1 }
        return riskOrder[b.riskLevel] - riskOrder[a.riskLevel]
      })
    case 'balance':
      return sorted.sort((a, b) => parseFloat(b.balance) - parseFloat(a.balance))
    case 'activity':
      return sorted.sort((a, b) => {
        const dateA = parseActivityDate(a.lastActivity)
        const dateB = parseActivityDate(b.lastActivity)
        return dateB - dateA
      })
    default:
      return sorted
  }
})

const totalPages = computed(() => Math.ceil(filteredResults.value.length / itemsPerPage.value))

const paginatedResults = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return sortedResults.value.slice(start, end)
})

const visiblePages = computed(() => {
  const pages = []
  const maxVisible = 5
  let start = Math.max(1, currentPage.value - Math.floor(maxVisible / 2))
  let end = Math.min(totalPages.value, start + maxVisible - 1)
  
  if (end - start + 1 < maxVisible) {
    start = Math.max(1, end - maxVisible + 1)
  }
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})

// Methods
const toggleView = () => {
  viewMode.value = viewMode.value === 'grid' ? 'list' : 'grid'
}

const sortResults = () => {
  currentPage.value = 1
}

const clearFilters = () => {
  activeFilters.value = {
    riskLevels: [],
    cryptocurrencies: [],
    minBalance: '',
    maxBalance: '',
    activityPeriod: ''
  }
  currentPage.value = 1
}

const viewDetails = (result) => {
  selectedAddress.value = result
  showDetailModal.value = true
  emit('address-selected', result)
}

const closeDetailModal = () => {
  showDetailModal.value = false
  selectedAddress.value = null
}

const viewConnectedAddress = (address) => {
  // Handle viewing connected address
  selectedAddress.value = address
}

const toggleWatchlist = (result) => {
  result.isWatched = !result.isWatched
  
  toast.add({
    severity: result.isWatched ? 'success' : 'info',
    summary: result.isWatched ? 'Added to Watchlist' : 'Removed from Watchlist',
    detail: `${result.address.substring(0, 10)}... ${result.isWatched ? 'added to' : 'removed from'} monitoring`,
    life: 3000
  })
  
  emit('watchlist-updated', result)
}

const exportAddress = (result) => {
  toast.add({
    severity: 'info',
    summary: 'Export Started',
    detail: `Exporting data for ${result.address.substring(0, 10)}...`,
    life: 3000
  })
}

const parseActivityDate = (activityString) => {
  const now = new Date()
  
  if (activityString.includes('min')) {
    const minutes = parseInt(activityString)
    return new Date(now.getTime() - minutes * 60000)
  } else if (activityString.includes('hour')) {
    const hours = parseInt(activityString)
    return new Date(now.getTime() - hours * 3600000)
  } else if (activityString.includes('day')) {
    const days = parseInt(activityString)
    return new Date(now.getTime() - days * 86400000)
  }
  
  return now
}

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount)
}

const getRiskBadgeClass = (riskLevel) => {
  const classes = {
    'Low': 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300',
    'Medium': 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300',
    'High': 'bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300',
    'Critical': 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300'
  }
  return classes[riskLevel] || classes['Low']
}

const getRiskTextClass = (riskLevel) => {
  const classes = {
    'Low': 'text-green-700 dark:text-green-300',
    'Medium': 'text-yellow-700 dark:text-yellow-300',
    'High': 'text-orange-700 dark:text-orange-300',
    'Critical': 'text-red-700 dark:text-red-300'
  }
  return classes[riskLevel] || classes['Low']
}

const getTagClass = (tag) => {
  const tagClasses = {
    'Exchange': 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300',
    'Mixing Service': 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300',
    'Darknet Market': 'bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300',
    'Personal Wallet': 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300',
    'DeFi Protocol': 'bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300',
    'Gambling': 'bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300',
    'Sanctioned': 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300',
    'Mining Pool': 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300'
  }
  return tagClasses[tag] || 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
}

const getCryptoIconClass = (crypto) => {
  const iconClasses = {
    'BTC': 'bg-orange-500',
    'ETH': 'bg-blue-600',
    'LTC': 'bg-gray-500',
    'BCH': 'bg-green-500',
    'XMR': 'bg-orange-600',
    'ZEC': 'bg-yellow-600'
  }
  return iconClasses[crypto] || 'bg-gray-500'
}

const getCryptoSymbol = (crypto) => {
  const symbols = {
    'BTC': '₿',
    'ETH': 'Ξ',
    'LTC': 'Ł',
    'BCH': '₿',
    'XMR': 'ɱ',
    'ZEC': 'ⓩ'
  }
  return symbols[crypto] || crypto.charAt(0)
}
const getRiskColor = (riskLevel) => {
  const colors = {
    'Low': 'bg-green-500',
    'Medium': 'bg-yellow-500',
    'High': 'bg-orange-500',
    'Critical': 'bg-red-500'
  }
  return colors[riskLevel] || colors['Low']
}

const getAlertBorderClass = (type) => {
  const classes = {
    'critical': 'border-l-red-500',
    'high': 'border-l-orange-500',
    'medium': 'border-l-yellow-500',
    'low': 'border-l-blue-500'
  }
  return classes[type] || classes['low']
}

const getAlertIconClass = (type) => {
  const classes = {
    'critical': 'bg-red-500',
    'high': 'bg-orange-500',
    'medium': 'bg-yellow-500',
    'low': 'bg-blue-500'
  }
  return classes[type] || classes['low']
}

// Watch for filter changes to reset pagination
watch(activeFilters, () => {
  currentPage.value = 1
}, { deep: true })

// Watch for results changes to reset pagination
watch(() => props.results, () => {
  currentPage.value = 1
})

onMounted(() => {
  // Initialize component
})
</script>

<style scoped>
/* Custom scrollbar styling */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

.dark ::-webkit-scrollbar-track {
  background: #374151;
}

.dark ::-webkit-scrollbar-thumb {
  background: #6b7280;
}

.dark ::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}

/* Grid item animations */
.grid > div {
  animation: fadeInUp 0.4s ease-out;
  animation-fill-mode: both;
}

.grid > div:nth-child(1) { animation-delay: 0.05s; }
.grid > div:nth-child(2) { animation-delay: 0.1s; }
.grid > div:nth-child(3) { animation-delay: 0.15s; }
.grid > div:nth-child(4) { animation-delay: 0.2s; }
.grid > div:nth-child(5) { animation-delay: 0.25s; }
.grid > div:nth-child(6) { animation-delay: 0.3s; }

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Table row hover effects */
tbody tr {
  transition: all 0.2s ease;
}

tbody tr:hover {
  transform: translateX(2px);
}

/* Button hover animations */
button:hover {
  transform: translateY(-1px);
}

button:active {
  transform: translateY(0);
}

/* Card hover effects */
/* .cursor-pointer:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
} */

/* .dark .cursor-pointer:hover {
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
} */

/* Pagination button styles */
.pagination-button {
  transition: all 0.2s ease;
}

.pagination-button:hover {
  transform: scale(1.05);
}

/* Filter section animations */
.grid.grid-cols-1.md\:grid-cols-4 > div {
  animation: slideInLeft 0.3s ease-out;
  animation-fill-mode: both;
}

.grid.grid-cols-1.md\:grid-cols-4 > div:nth-child(1) { animation-delay: 0.1s; }
.grid.grid-cols-1.md\:grid-cols-4 > div:nth-child(2) { animation-delay: 0.2s; }
.grid.grid-cols-1.md\:grid-cols-4 > div:nth-child(3) { animation-delay: 0.3s; }
.grid.grid-cols-1.md\:grid-cols-4 > div:nth-child(4) { animation-delay: 0.4s; }

@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* Loading states */
.loading-shimmer {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

.dark .loading-shimmer {
  background: linear-gradient(90deg, #374151 25%, #4b5563 50%, #374151 75%);
  background-size: 200% 100%;
}

@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}

/* Enhanced focus styles */
button:focus-visible,
input:focus-visible,
select:focus-visible {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

/* Responsive adjustments */
@media (max-width: 1024px) {
  .grid-cols-1.lg\:grid-cols-3 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .grid-cols-1.md\:grid-cols-2 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
  
  .grid-cols-1.md\:grid-cols-4 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
  
  .overflow-x-auto table {
    font-size: 0.875rem;
  }
  
  .flex.items-center.justify-between {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
}

@media (max-width: 640px) {
  .px-4 {
    padding-left: 0.75rem;
    padding-right: 0.75rem;
  }
  
  .py-3 {
    padding-top: 0.5rem;
    padding-bottom: 0.5rem;
  }
  
  .text-sm {
    font-size: 0.75rem;
  }
  
  .gap-4 {
    gap: 0.5rem;
  }
}

/* Print styles */
@media print {
  .no-print {
    display: none !important;
  }
  
  .grid-cols-1.lg\:grid-cols-3 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
  
  .bg-gradient-to-r {
    background: #3b82f6 !important;
    -webkit-print-color-adjust: exact;
  }
  
  .shadow-lg {
    box-shadow: none !important;
  }
  
  .hover\:bg-gray-100:hover {
    background-color: transparent !important;
  }
}

/* High contrast mode */
@media (prefers-contrast: high) {
  .bg-gray-50 {
    background-color: white;
  }
  
  .dark .bg-gray-700 {
    background-color: black;
  }
  
  .border-gray-200 {
    border-color: #000;
  }
  
  .dark .border-gray-600 {
    border-color: #fff;
  }
  
  .text-gray-600 {
    color: #000;
  }
  
  .dark .text-gray-400 {
    color: #fff;
  }
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* Custom checkbox styles */
input[type="checkbox"] {
  accent-color: #3b82f6;
}

/* Enhanced table styling */
table {
  border-collapse: separate;
  border-spacing: 0;
}

thead th {
  position: sticky;
  top: 0;
  background: inherit;
  z-index: 1;
}

/* Tooltip styles */
[title] {
  position: relative;
}

[title]:hover::after {
  content: attr(title);
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  white-space: nowrap;
  z-index: 1000;
  animation: tooltipFadeIn 0.2s ease-out;
}

@keyframes tooltipFadeIn {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(4px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

/* Enhanced visual hierarchy */
.section-divider {
  position: relative;
}

.section-divider::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: linear-gradient(to bottom, #3b82f6, #1d4ed8);
  border-radius: 2px;
}

/* Interactive elements enhancement */
.interactive-element {
  position: relative;
  overflow: hidden;
}

.interactive-element::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.interactive-element:hover::before {
  left: 100%;
}

/* Status indicators */
.status-online {
  position: relative;
}

.status-online::before {
  content: '';
  position: absolute;
  top: -2px;
  right: -2px;
  width: 8px;
  height: 8px;
  background: #10b981;
  border-radius: 50%;
  border: 2px solid white;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(16, 185, 129, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
  }
}

/* Modern card design */
.modern-card {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.dark .modern-card {
  background: rgba(31, 41, 55, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* Gradient text */
.gradient-text {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Enhanced button styles */
.btn-primary {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  border: none;
  color: white;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #1d4ed8, #1e40af);
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(59, 130, 246, 0.3);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: inherit;
  font-weight: 500;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
  transform: translateY(-1px);
}

.dark .btn-secondary {
  background: rgba(0, 0, 0, 0.1);
  border-color: rgba(0, 0, 0, 0.2);
}

.dark .btn-secondary:hover {
  background: rgba(0, 0, 0, 0.2);
  border-color: rgba(0, 0, 0, 0.3);
}

/* Advanced grid layouts */
.masonry-grid {
  columns: 3;
  column-gap: 1rem;
}

.masonry-grid > div {
  break-inside: avoid;
  margin-bottom: 1rem;
}

@media (max-width: 1024px) {
  .masonry-grid {
    columns: 2;
  }
}

@media (max-width: 640px) {
  .masonry-grid {
    columns: 1;
  }
}

/* CSS Grid auto-fit */
.auto-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

/* Smooth scrolling */
.smooth-scroll {
  scroll-behavior: smooth;
}

/* Custom selection */
::selection {
  background: rgba(59, 130, 246, 0.3);
  color: inherit;
}

.dark ::selection {
  background: rgba(59, 130, 246, 0.5);
}

/* Focus within styles */
.form-group:focus-within {
  transform: scale(1.02);
  transition: transform 0.2s ease;
}

/* Container queries support */
@supports (container-type: inline-size) {
  .container-aware {
    container-type: inline-size;
  }
  
  @container (min-width: 400px) {
    .container-responsive {
      display: grid;
      grid-template-columns: 1fr 1fr;
    }
  }
  
  @container (min-width: 600px) {
    .container-responsive {
      grid-template-columns: 1fr 1fr 1fr;
    }
  }
}

/* Modern scrollbar */
.modern-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: rgba(59, 130, 246, 0.3) transparent;
}

.modern-scrollbar::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.modern-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.modern-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(59, 130, 246, 0.3);
  border-radius: 4px;
  border: 2px solid transparent;
  background-clip: content-box;
}

.modern-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(59, 130, 246, 0.5);
  background-clip: content-box;
}

/* Glassmorphism effect */
.glass {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.dark .glass {
  background: rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* Neumorphism effect */
.neomorphic {
  background: #f0f0f0;
  box-shadow: 
    8px 8px 16px rgba(0, 0, 0, 0.1),
    -8px -8px 16px rgba(255, 255, 255, 0.8);
  border: none;
}

.dark .neomorphic {
  background: #2d3748;
  box-shadow: 
    8px 8px 16px rgba(0, 0, 0, 0.3),
    -8px -8px 16px rgba(255, 255, 255, 0.05);
}

.neomorphic:hover {
  box-shadow: 
    inset 8px 8px 16px rgba(0, 0, 0, 0.1),
    inset -8px -8px 16px rgba(255, 255, 255, 0.8);
}

.dark .neomorphic:hover {
  box-shadow: 
    inset 8px 8px 16px rgba(0, 0, 0, 0.3),
    inset -8px -8px 16px rgba(255, 255, 255, 0.05);
}

/* Advanced animations */
@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
}

.floating {
  animation: float 3s ease-in-out infinite;
}

@keyframes glow {
  0%, 100% {
    box-shadow: 0 0 5px rgba(59, 130, 246, 0.5);
  }
  50% {
    box-shadow: 0 0 20px rgba(59, 130, 246, 0.8);
  }
}

.glowing {
  animation: glow 2s ease-in-out infinite;
}

@keyframes slideInFromRight {
  0% {
    transform: translateX(100%);
    opacity: 0;
  }
  100% {
    transform: translateX(0);
    opacity: 1;
  }
}

.slide-in-right {
  animation: slideInFromRight 0.5s ease-out;
}

@keyframes bounceIn {
  0% {
    transform: scale(0.3);
    opacity: 0;
  }
  50% {
    transform: scale(1.05);
  }
  70% {
    transform: scale(0.9);
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

.bounce-in {
  animation: bounceIn 0.6s ease-out;
}

/* Micro-interactions */
.micro-bounce:active {
  transform: scale(0.95);
  transition: transform 0.1s ease;
}

.micro-rotate:hover {
  transform: rotate(5deg);
  transition: transform 0.2s ease;
}

.micro-shake:hover {
  animation: shake 0.5s ease-in-out;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-2px); }
  20%, 40%, 60%, 80% { transform: translateX(2px); }
}

/* Progressive enhancement */
@supports (backdrop-filter: blur(10px)) {
  .backdrop-blur-supported {
    backdrop-filter: blur(10px);
  }
}

@supports (color: color(display-p3 1 0 0)) {
  .wide-gamut-color {
    color: color(display-p3 0.2 0.5 1);
  }
}

@supports (font-variation-settings: normal) {
  .variable-font {
    font-variation-settings: 'wght' 400, 'wdth' 100;
    transition: font-variation-settings 0.3s ease;
  }
  
  .variable-font:hover {
    font-variation-settings: 'wght' 600, 'wdth' 110;
  }
}

/* Dark mode enhancements */
@media (prefers-color-scheme: dark) {
  .auto-dark {
    background: #1a202c;
    color: #e2e8f0;
  }
}

/* Accessibility improvements */
.skip-to-content {
  position: absolute;
  top: -40px;
  left: 6px;
  background: #000;
  color: #fff;
  padding: 8px;
  text-decoration: none;
  border-radius: 4px;
  z-index: 1000;
}

.skip-to-content:focus {
  top: 6px;
}

/* Screen reader only */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

/* Focus management */
.focus-trap {
  position: relative;
}

.focus-trap::before,
.focus-trap::after {
  content: '';
  position: absolute;
  width: 1px;
  height: 1px;
  opacity: 0;
  pointer-events: none;
}

/* High contrast improvements */
@media (prefers-contrast: high) {
  .high-contrast-border {
    border: 2px solid currentColor;
  }
  
  .high-contrast-bg {
    background: Canvas;
    color: CanvasText;
  }
  
  .high-contrast-button {
    border: 2px solid ButtonText;
    background: ButtonFace;
    color: ButtonText;
  }
}

/* Motion preferences */
@media (prefers-reduced-motion: no-preference) {
  .motion-safe-animate {
    animation: fadeInUp 0.6s ease-out;
  }
}

/* Print optimizations */
@media print {
  .print-break-before {
    page-break-before: always;
  }
  
  .print-break-after {
    page-break-after: always;
  }
  
  .print-break-inside-avoid {
    page-break-inside: avoid;
  }
  
  .print-hidden {
    display: none !important;
  }
  
  .print-visible {
    display: block !important;
  }
  
  /* Optimize for print colors */
  .print-optimize {
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
}

/* Container query polyfill fallback */
@media (max-width: 400px) {
  .cq-fallback-small {
    display: block;
  }
}

@media (min-width: 401px) and (max-width: 600px) {
  .cq-fallback-medium {
    display: grid;
    grid-template-columns: 1fr 1fr;
  }
}

@media (min-width: 601px) {
  .cq-fallback-large {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
  }
}

/* Future CSS features with fallbacks */
.modern-layout {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(300px, 100%), 1fr));
  gap: clamp(1rem, 2vw, 2rem);
}

/* CSS Houdini support */
@supports (background: paint(something)) {
  .houdini-bg {
    background: paint(checkerboard);
  }
}

/* Logical properties */
.logical-spacing {
  margin-block: 1rem;
  margin-inline: 2rem;
  padding-block-start: 0.5rem;
  padding-inline-end: 1rem;
}

/* Subgrid support */
@supports (grid-template-rows: subgrid) {
  .subgrid-container {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
  }
  
  .subgrid-item {
    display: grid;
    grid-template-rows: subgrid;
    grid-row: span 3;
  }
}

/* CSS nesting fallback */
.nested-fallback {
  color: #3b82f6;
}

.nested-fallback:hover {
  color: #1d4ed8;
}

.nested-fallback .child {
  margin-left: 1rem;
}

.nested-fallback .child:first-child {
  margin-left: 0;
}

/* Modern color functions */
.modern-colors {
  background: hsl(220 14% 96%);
  color: hsl(220 9% 46%);
  border-color: hsl(220 13% 91%);
}

.dark .modern-colors {
  background: hsl(220 13% 18%);
  color: hsl(220 9% 78%);
  border-color: hsl(220 13% 28%);
}

/* Aspect ratio */
.aspect-video {
  aspect-ratio: 16 / 9;
}

.aspect-square {
  aspect-ratio: 1 / 1;
}

/* Gap support fallback */
.gap-fallback > * + * {
  margin-top: 1rem;
}

@supports (gap: 1rem) {
  .gap-fallback {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  
  .gap-fallback > * + * {
    margin-top: 0;
  }
}

/* Final cleanup */
.component-root {
  isolation: isolate;
  contain: layout style paint;
}
</style>
