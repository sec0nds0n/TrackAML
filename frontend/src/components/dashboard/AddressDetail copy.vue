<script setup>
import { useToast } from 'primevue/usetoast'
import { onMounted, ref } from 'vue'
import AddressGraphAnalysis from './AddressGraphAnalysis.vue'

const props = defineProps({
  addressData: {
    type: Object,
    required: true
  },
  showModal: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'view-address'])

const toast = useToast()

// Active tab state
const activeTab = ref('overview')

// Add graph analysis to the tabs
const tabs = ref([
  { id: 'overview', label: 'Overview', icon: '📊' },
  { id: 'transactions', label: 'Transactions', icon: '💸' },
  { id: 'connections', label: 'Connections', icon: '🔗' },
  { id: 'graph', label: 'Graph Analysis', icon: '🕸️' }, // New tab
  { id: 'compliance', label: 'Compliance', icon: '⚖️' },
  { id: 'reports', label: 'Reports', icon: '📋' }
])

// Reactive data
const lastUpdated = ref(new Date().toLocaleString())

// Mock data for comprehensive address details
const riskFactors = ref([
  { name: 'Transaction Pattern', score: 75, level: 'High' },
  { name: 'Counterparty Risk', score: 45, level: 'Medium' },
  { name: 'Geographic Risk', score: 30, level: 'Low' },
  { name: 'Behavioral Analysis', score: 85, level: 'High' }
])

const transactions = ref([
  {
    hash: '1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z',
    type: 'incoming',
    amount: '2.45678901',
    amountUSD: 98234.56,
    counterparty: '1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2',
    counterpartyType: 'Exchange',
    timestamp: '2 hours ago',
    riskLevel: 'Medium'
  },
  {
    hash: '9z8y7x6w5v4u3t2s1r0q9p8o7n6m5l4k3j2i1h0g9f8e7d6c5b4a',
    type: 'outgoing',
    amount: '0.12345678',
    amountUSD: 4932.12,
    counterparty: '3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy',
    counterpartyType: 'Personal Wallet',
    timestamp: '5 hours ago',
    riskLevel: 'Low'
  },
  {
    hash: 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6',
    type: 'incoming',
    amount: '15.87654321',
    amountUSD: 634521.87,
    counterparty: 'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh',
    counterpartyType: 'Mixing Service',
    timestamp: '1 day ago',
    riskLevel: 'Critical'
  },
  {
    hash: 'z6y5x4w3v2u1t0s9r8q7p6o5n4m3l2k1j0i9h8g7f6e5d4c3b2a1',
    type: 'outgoing',
    amount: '5.00000000',
    amountUSD: 200000.00,
    counterparty: '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
    counterpartyType: 'Darknet Market',
    timestamp: '2 days ago',
    riskLevel: 'Critical'
  }
])

const connectedAddresses = ref([
  {
    address: '1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2',
    label: 'Binance Exchange',
    riskLevel: 'Low',
    transactionCount: 45,
    totalAmount: '125.67890123',
    relationship: 'Direct'
  },
  {
    address: 'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh',
    label: 'ChipMixer Service',
    riskLevel: 'Critical',
    transactionCount: 12,
    totalAmount: '89.12345678',
    relationship: 'Direct'
  },
  {
    address: '3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy',
    label: 'Personal Wallet',
    riskLevel: 'Medium',
    transactionCount: 8,
    totalAmount: '23.45678901',
    relationship: '2-hop'
  },
  {
    address: '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
    label: 'Silk Road Wallet',
    riskLevel: 'Critical',
    transactionCount: 156,
    totalAmount: '567.89012345',
    relationship: 'Direct'
  },
  {
    address: '1F1tAaz5x1HUXrCNLbtMDqcw6o5GNn4xqX',
    label: 'Coinbase Exchange',
    riskLevel: 'Low',
    transactionCount: 23,
    totalAmount: '78.90123456',
    relationship: '2-hop'
  },
  {
    address: 'bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4',
    label: 'Unknown Wallet',
    riskLevel: 'High',
    transactionCount: 67,
    totalAmount: '234.56789012',
    relationship: '3-hop'
  }
])

const sanctionsData = ref([
  {
    list: 'OFAC SDN List',
    description: 'US Treasury Sanctions',
    status: 'Clear',
    lastChecked: '2024-01-15 14:30:00'
  },
  {
    list: 'EU Sanctions',
    description: 'European Union Sanctions',
    status: 'Clear',
    lastChecked: '2024-01-15 14:30:00'
  },
  {
    list: 'UN Sanctions',
    description: 'United Nations Sanctions',
    status: 'Clear',
    lastChecked: '2024-01-15 14:30:00'
  },
  {
    list: 'Chainalysis Sanctions',
    description: 'Blockchain Analytics Sanctions',
    status: 'Flagged',
    lastChecked: '2024-01-15 14:30:00'
  }
])

const complianceScore = ref({
  score: 67,
  factors: [
    { name: 'KYC Compliance', score: 85 },
    { name: 'Transaction Monitoring', score: 72 },
    { name: 'Sanctions Screening', score: 45 },
    { name: 'Risk Assessment', score: 68 },
    { name: 'Regulatory Compliance', score: 78 }
  ]
})

// Methods
const closeModal = () => {
  emit('close')
}

const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    toast.add({
      severity: 'success',
      summary: 'Copied',
      detail: 'Address copied to clipboard',
      life: 2000
    })
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Copy Failed',
      detail: 'Unable to copy to clipboard',
      life: 3000
    })
  }
}

const addToWatchlist = () => {
  toast.add({
    severity: 'success',
    summary: 'Added to Watchlist',
    detail: `${props.addressData.address.substring(0, 10)}... added to monitoring`,
    life: 3000
  })
}

const exportReport = () => {
  toast.add({
    severity: 'info',
    summary: 'Export Started',
    detail: 'Generating comprehensive address report...',
    life: 3000
  })
}

const flagAddress = () => {
  toast.add({
    severity: 'warn',
    summary: 'Address Flagged',
    detail: 'Address has been flagged for manual review',
    life: 3000
  })
}

const viewConnectedAddress = (connection) => {
  emit('view-address', connection)
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

const getRiskColor = (level) => {
  const colors = {
    'Low': 'text-green-500',
    'Medium': 'text-yellow-500',
    'High': 'text-orange-500',
    'Critical': 'text-red-500'
  }
  return colors[level] || colors['Low']
}

const getRiskDotClass = (riskLevel) => {
  const classes = {
    'Low': 'bg-green-500',
    'Medium': 'bg-yellow-500',
    'High': 'bg-orange-500',
    'Critical': 'bg-red-500'
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
    'Sanctioned': 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300'
  }
  return tagClasses[tag] || 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
}

const getComplianceScoreColor = (score) => {
  if (score >= 80) return 'text-green-500'
  if (score >= 60) return 'text-yellow-500'
  if (score >= 40) return 'text-orange-500'
  return 'text-red-500'
}

const getComplianceBarColor = (score) => {
  if (score >= 80) return 'bg-green-500'
  if (score >= 60) return 'bg-yellow-500'
  if (score >= 40) return 'bg-orange-500'
  return 'bg-red-500'
}

onMounted(() => {
  // Initialize any required data or API calls
})
</script>

<template>
  <div v-if="showModal" class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
    <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700 w-full max-w-7xl max-h-[95vh] overflow-y-auto">
      <!-- Header -->
      <div class="sticky top-0 bg-white dark:bg-gray-800 p-6 border-b border-gray-200 dark:border-gray-700 z-10">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4">
            <div class="p-3 bg-gradient-to-r from-green-500 to-emerald-500 rounded-xl">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path>
              </svg>
            </div>
            <div>
              <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Address Details</h2>
              <p class="text-gray-500 dark:text-gray-400">Comprehensive analysis and risk assessment</p>
            </div>
          </div>
          <div class="flex items-center gap-3">
            <button
              @click="addToWatchlist"
              class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium text-sm flex items-center gap-2"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
              </svg>
              Add to Watchlist
            </button>
            <button 
              @click="closeModal"
              class="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              <svg class="w-6 h-6 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
        </div>

        <!-- Navigation Tabs -->
        <div class="flex space-x-1 mt-6 bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              'flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors',
              activeTab === tab.id
                ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow-sm'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            ]"
          >
            <span>{{ tab.icon }}</span>
            {{ tab.label }}
          </button>
        </div>
      </div>

      <div class="p-6 space-y-6">
        <!-- Overview Tab -->
        <div v-if="activeTab === 'overview'" class="space-y-6">
          <!-- Address Overview -->
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <!-- Address Info Card -->
            <div class="lg:col-span-2 bg-gray-50 dark:bg-gray-700 rounded-xl p-6">
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Address Information</h3>
                <div :class="getRiskBadgeClass(addressData.riskLevel)" class="px-3 py-1 rounded-full text-sm font-medium">
                  {{ addressData.riskLevel }} Risk
                </div>
              </div>
              
              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Address</label>
                  <div class="flex items-center gap-3 p-3 bg-white dark:bg-gray-800 rounded-lg border">
                    <code class="flex-1 font-mono text-sm text-gray-900 dark:text-white break-all">{{ addressData.address }}</code>
                    <button 
                      @click="copyToClipboard(addressData.address)"
                      class="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                      title="Copy Address"
                    >
                      <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                      </svg>
                    </button>
                  </div>
                </div>

                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Cryptocurrency</label>
                    <div class="flex items-center gap-2">
                      <div class="w-6 h-6 bg-orange-500 rounded-full flex items-center justify-center">
                        <span class="text-white text-xs font-bold">₿</span>
                      </div>
                      <span class="font-medium text-gray-900 dark:text-white">{{ addressData.crypto }}</span>
                    </div>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Address Type</label>
                    <span class="text-gray-900 dark:text-white">{{ addressData.addressType }}</span>
                  </div>
                </div>

                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">First Seen</label>
                    <span class="text-gray-900 dark:text-white">{{ addressData.firstSeen }}</span>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Last Activity</label>
                    <span class="text-gray-900 dark:text-white">{{ addressData.lastActivity }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Balance & Stats Card -->
            <div class="bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-xl p-6 border border-green-200 dark:border-green-800">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Balance & Statistics</h3>
              
              <div class="space-y-4">
                <div class="text-center">
                  <div class="text-3xl font-bold text-green-600 dark:text-green-400">
                    {{ addressData.balance }}
                  </div>
                  <div class="text-sm text-gray-600 dark:text-gray-400">{{ addressData.crypto }}</div>
                  <div class="text-lg font-medium text-gray-900 dark:text-white mt-1">
                    ≈ ${{ formatCurrency(addressData.balanceUSD) }}
                  </div>
                </div>

                <div class="grid grid-cols-2 gap-4 pt-4 border-t border-green-200 dark:border-green-800">
                  <div class="text-center">
                    <div class="text-xl font-bold text-gray-900 dark:text-white">{{ addressData.transactionCount }}</div>
                    <div class="text-xs text-gray-600 dark:text-gray-400">Transactions</div>
                  </div>
                  <div class="text-center">
                    <div class="text-xl font-bold text-gray-900 dark:text-white">{{ addressData.uniqueCounterparties }}</div>
                    <div class="text-xs text-gray-600 dark:text-gray-400">Counterparties</div>
                  </div>
                </div>

                <div class="grid grid-cols-2 gap-4">
                  <div class="text-center">
                    <div class="text-lg font-semibold text-green-600 dark:text-green-400">{{ addressData.totalReceived }}</div>
                    <div class="text-xs text-gray-600 dark:text-gray-400">Total Received</div>
                  </div>
                  <div class="text-center">
                    <div class="text-lg font-semibold text-red-600 dark:text-red-400">{{ addressData.totalSent }}</div>
                    <div class="text-xs text-gray-600 dark:text-gray-400">Total Sent</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Risk Assessment -->
          <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Risk Assessment</h3>
            
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              <div v-for="risk in riskFactors" :key="risk.name" class="text-center">
                <div class="relative w-16 h-16 mx-auto mb-2">
                  <svg class="w-16 h-16 transform -rotate-90" viewBox="0 0 36 36">
                    <path
                      class="text-gray-200 dark:text-gray-700"
                      stroke="currentColor"
                      stroke-width="3"
                      fill="none"
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    />
                    <path
                      :class="getRiskColor(risk.level)"
                      stroke="currentColor"
                      stroke-width="3"
                      fill="none"
                      stroke-linecap="round"
                      :stroke-dasharray="`${risk.score}, 100`"
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    />
                  </svg>
                  <div class="absolute inset-0 flex items-center justify-center">
                    <span class="text-sm font-bold text-gray-900 dark:text-white">{{ risk.score }}%</span>
                  </div>
                </div>
                <div class="text-sm font-medium text-gray-900 dark:text-white">{{ risk.name }}</div>
                <div class="text-xs text-gray-500 dark:text-gray-400">{{ risk.level }}</div>
              </div>
            </div>

            <!-- Risk Tags -->
            <div class="flex flex-wrap gap-2">
              <span
                v-for="tag in addressData.riskTags"
                :key="tag"
                :class="getTagClass(tag)"
                class="px-3 py-1 rounded-full text-sm font-medium"
              >
                {{ tag }}
              </span>
            </div>
          </div>
        </div>

        <!-- Transactions Tab -->
        <div v-if="activeTab === 'transactions'" class="space-y-6">
          <!-- Transaction History -->
          <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Transaction History</h3>
              <div class="flex gap-2">
                <select class="px-3 py-1 bg-gray-100 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-sm">
                  <option>All Types</option>
                  <option>Incoming</option>
                  <option>Outgoing</option>
                </select>
                <button class="px-4 py-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-lg transition-colors text-sm">
                  Export
                </button>
              </div>
            </div>

            <div class="overflow-x-auto">
              <table class="w-full">
                <thead>
                  <tr class="border-b border-gray-200 dark:border-gray-700">
                    <th class="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Transaction Hash</th>
                    <th class="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Type</th>
                    <th class="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Amount</th>
                    <th class="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Counterparty</th>
                    <th class="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Time</th>
                    <th class="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Risk</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="tx in transactions"
                    :key="tx.hash"
                    class="border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                  >
                    <td class="py-3 px-4">
                      <code class="text-sm text-blue-600 dark:text-blue-400 hover:underline cursor-pointer">
                        {{ tx.hash.substring(0, 12) }}...
                      </code>
                    </td>
                    <td class="py-3 px-4">
                      <span :class="tx.type === 'incoming' ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'" class="font-medium">
                        {{ tx.type === 'incoming' ? '↓ Received' : '↑ Sent' }}
                      </span>
                    </td>
                    <td class="py-3 px-4">
                      <div class="font-mono text-sm text-gray-900 dark:text-white">{{ tx.amount }} {{ addressData.crypto }}</div>
                      <div class="text-xs text-gray-500 dark:text-gray-400">${{ formatCurrency(tx.amountUSD) }}</div>
                    </td>
                    <td class="py-3 px-4">
                      <div class="text-sm text-gray-900 dark:text-white">{{ tx.counterparty }}</div>
                      <div class="text-xs text-gray-500 dark:text-gray-400">{{ tx.counterpartyType }}</div>
                    </td>
                    <td class="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">{{ tx.timestamp }}</td>
                    <td class="py-3 px-4">
                      <span :class="getRiskBadgeClass(tx.riskLevel)" class="px-2 py-1 rounded-full text-xs font-medium">
                        {{ tx.riskLevel }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Connections Tab -->
        <div v-if="activeTab === 'connections'" class="space-y-6">
          <!-- Connected Addresses Network -->
          <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Connected Addresses</h3>
              <div class="flex gap-2">
                <button class="px-3 py-1 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-lg transition-colors text-sm">
                  1 Hop
                </button>
                <button class="px-3 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 rounded-lg text-sm">
                  2 Hops
                </button>
                <button class="px-3 py-1 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-lg transition-colors text-sm">
                  3 Hops
                </button>
              </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div
                v-for="connection in connectedAddresses"
                :key="connection.address"
                class="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors cursor-pointer"
                @click="viewConnectedAddress(connection)"
              >
                <div class="flex items-center justify-between mb-2">
                  <div class="flex items-center gap-2">
                    <div :class="getRiskDotClass(connection.riskLevel)" class="w-3 h-3 rounded-full"></div>
                    <span class="text-sm font-medium text-gray-900 dark:text-white">{{ connection.label }}</span>
                  </div>
                  <span class="text-xs text-gray-500 dark:text-gray-400">{{ connection.transactionCount }} txs</span>
                </div>
                
                <div class="font-mono text-xs text-gray-600 dark:text-gray-400 mb-2">
                  {{ connection.address.substring(0, 16) }}...
                </div>
                
                <div class="flex items-center justify-between text-xs">
                  <span class="text-gray-500 dark:text-gray-400">{{ connection.totalAmount }} {{ addressData.crypto }}</span>
                  <span :class="getRiskBadgeClass(connection.riskLevel)" class="px-2 py-1 rounded-full font-medium">
                    {{ connection.riskLevel }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Graph Analysis Tab -->
        <div v-if="activeTab === 'graph'" class="space-y-6">
          <AddressGraphAnalysis :address-data="addressData" />
        </div>

        <!-- Compliance Tab -->
        <div v-if="activeTab === 'compliance'" class="space-y-6">
          <!-- Compliance & Sanctions Check -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Sanctions Check -->
            <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
              <div class="flex items-center gap-3 mb-4">
                <div class="p-2 bg-red-100 dark:bg-red-900/30 rounded-lg">
                  <svg class="w-5 h-5 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.314 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                  </svg>
                </div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Sanctions Check</h3>
              </div>

              <div class="space-y-3">
                <div v-for="sanction in sanctionsData" :key="sanction.list" class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div>
                    <div class="font-medium text-gray-900 dark:text-white">{{ sanction.list }}</div>
                    <div class="text-sm text-gray-500 dark:text-gray-400">{{ sanction.description }}</div>
                  </div>
                  <div class="flex items-center gap-2">
                    <div :class="sanction.status === 'Clear' ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300' : 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300'" class="px-3 py-1 rounded-full text-sm font-medium">
                      {{ sanction.status }}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Compliance Score -->
            <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
              <div class="flex items-center gap-3 mb-4">
                <div class="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                  <svg class="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                </div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Compliance Score</h3>
              </div>

              <div class="text-center mb-6">
                <div class="relative w-32 h-32 mx-auto">
                  <svg class="w-32 h-32 transform -rotate-90" viewBox="0 0 36 36">
                    <path
                      class="text-gray-200 dark:text-gray-700"
                      stroke="currentColor"
                      stroke-width="3"
                      fill="none"
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    />
                    <path
                      :class="getComplianceScoreColor(complianceScore.score)"
                      stroke="currentColor"
                      stroke-width="3"
                      fill="none"
                      stroke-linecap="round"
                      :stroke-dasharray="`${complianceScore.score}, 100`"
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    />
                  </svg>
                  <div class="absolute inset-0 flex items-center justify-center">
                    <div class="text-center">
                      <div class="text-2xl font-bold text-gray-900 dark:text-white">{{ complianceScore.score }}%</div>
                      <div class="text-xs text-gray-500 dark:text-gray-400">Score</div>
                    </div>
                  </div>
                </div>
              </div>

              <div class="space-y-2">
                <div v-for="factor in complianceScore.factors" :key="factor.name" class="flex items-center justify-between">
                  <span class="text-sm text-gray-600 dark:text-gray-400">{{ factor.name }}</span>
                  <div class="flex items-center gap-2">
                    <div class="w-20 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div :class="getComplianceBarColor(factor.score)" class="h-2 rounded-full" :style="`width: ${factor.score}%`"></div>
                    </div>
                    <span class="text-sm font-medium text-gray-900 dark:text-white w-8">{{ factor.score }}%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        Reports Tab
        <div v-if="activeTab === 'reports'" class="space-y-6">
          <!-- Report Generation -->
          <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
            <div class="flex items-center gap-3 mb-6">
              <div class="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
                <svg class="w-5 h-5 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
              </div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Generate Reports</h3>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div class="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors cursor-pointer">
                <div class="flex items-center gap-3 mb-3">
                  <div class="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                    <svg class="w-4 h-4 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                    </svg>
                  </div>
                  <h4 class="font-medium text-gray-900 dark:text-white">Risk Assessment Report</h4>
                </div>
                <p class="text-sm text-gray-600 dark:text-gray-400 mb-3">Comprehensive risk analysis and scoring</p>
                <button class="w-full px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm transition-colors">
                  Generate PDF
                </button>
              </div>

              <div class="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors cursor-pointer">
                <div class="flex items-center gap-3 mb-3">
                  <div class="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
                    <svg class="w-4 h-4 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"></path>
                    </svg>
                  </div>
                  <h4 class="font-medium text-gray-900 dark:text-white">Transaction Report</h4>
                </div>
                <p class="text-sm text-gray-600 dark:text-gray-400 mb-3">Detailed transaction history and analysis</p>
                <button class="w-full px-3 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm transition-colors">
                  Generate CSV
                </button>
              </div>

              <div class="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors cursor-pointer">
                <div class="flex items-center gap-3 mb-3">
                  <div class="p-2 bg-red-100 dark:bg-red-900/30 rounded-lg">
                    <svg class="w-4 h-4 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.314 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                    </svg>
                  </div>
                  <h4 class="font-medium text-gray-900 dark:text-white">Compliance Report</h4>
                </div>
                <p class="text-sm text-gray-600 dark:text-gray-400 mb-3">Regulatory compliance and sanctions check</p>
                <button class="w-full px-3 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm transition-colors">
                  Generate PDF
                </button>
              </div>

              <div class="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors cursor-pointer">
                <div class="flex items-center gap-3 mb-3">
                  <div class="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
                    <svg class="w-4 h-4 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"></path>
                    </svg>
                  </div>
                  <h4 class="font-medium text-gray-900 dark:text-white">Network Analysis</h4>
                </div>
                <p class="text-sm text-gray-600 dark:text-gray-400 mb-3">Connected addresses and relationship mapping</p>
                <button class="w-full px-3 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm transition-colors">
                  Generate JSON
                </button>
              </div>

              <div class="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors cursor-pointer">
                <div class="flex items-center gap-3 mb-3">
                  <div class="p-2 bg-orange-100 dark:bg-orange-900/30 rounded-lg">
                    <svg class="w-4 h-4 text-orange-600 dark:text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z"></path>
                    </svg>
                  </div>
                  <h4 class="font-medium text-gray-900 dark:text-white">Executive Summary</h4>
                </div>
                <p class="text-sm text-gray-600 dark:text-gray-400 mb-3">High-level overview for management</p>
                <button class="w-full px-3 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-lg text-sm transition-colors">
                  Generate PDF
                </button>
              </div>

              <div class="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors cursor-pointer">
                <div class="flex items-center gap-3 mb-3">
                  <div class="p-2 bg-indigo-100 dark:bg-indigo-900/30 rounded-lg">
                    <svg class="w-4 h-4 text-indigo-600 dark:text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                    </svg>
                  </div>
                  <h4 class="font-medium text-gray-900 dark:text-white">Custom Report</h4>
                </div>
                <p class="text-sm text-gray-600 dark:text-gray-400 mb-3">Build your own custom analysis report</p>
                <button class="w-full px-3 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm transition-colors">
                  Configure
                </button>
              </div>
            </div>

            <!-- Report History -->
            <div class="mt-8">
              <h4 class="text-md font-semibold text-gray-900 dark:text-white mb-4">Recent Reports</h4>
              <div class="space-y-3">
                <div class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div class="flex items-center gap-3">
                    <div class="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                      <svg class="w-4 h-4 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path>
                      </svg>
                    </div>
                    <div>
                      <div class="font-medium text-gray-900 dark:text-white">Risk Assessment Report</div>
                      <div class="text-sm text-gray-500 dark:text-gray-400">Generated 2 hours ago</div>
                    </div>
                  </div>
                  <div class="flex items-center gap-2">
                    <button class="px-3 py-1 bg-gray-200 dark:bg-gray-600 hover:bg-gray-300 dark:hover:bg-gray-500 text-gray-700 dark:text-gray-300 rounded text-sm transition-colors">
                      Download
                    </button>
                    <button class="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-sm transition-colors">
                      View
                    </button>
                  </div>
                </div>

                <div class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div class="flex items-center gap-3">
                    <div class="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
                      <svg class="w-4 h-4 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                      </svg>
                    </div>
                    <div>
                      <div class="font-medium text-gray-900 dark:text-white">Transaction Report</div>
                      <div class="text-sm text-gray-500 dark:text-gray-400">Generated 1 day ago</div>
                    </div>
                  </div>
                  <div class="flex items-center gap-2">
                    <button class="px-3 py-1 bg-gray-200 dark:bg-gray-600 hover:bg-gray-300 dark:hover:bg-gray-500 text-gray-700 dark:text-gray-300 rounded text-sm transition-colors">
                      Download
                    </button>
                    <button class="px-3 py-1 bg-green-600 hover:bg-green-700 text-white rounded text-sm transition-colors">
                      View
                    </button>
                  </div>
                </div>

                <div class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div class="flex items-center gap-3">
                    <div class="p-2 bg-red-100 dark:bg-red-900/30 rounded-lg">
                      <svg class="w-4 h-4 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.314 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                      </svg>
                    </div>
                    <div>
                      <div class="font-medium text-gray-900 dark:text-white">Compliance Report</div>
                      <div class="text-sm text-gray-500 dark:text-gray-400">Generated 3 days ago</div>
                    </div>
                  </div>
                  <div class="flex items-center gap-2">
                    <button class="px-3 py-1 bg-gray-200 dark:bg-gray-600 hover:bg-gray-300 dark:hover:bg-gray-500 text-gray-700 dark:text-gray-300 rounded text-sm transition-colors">
                      Download
                    </button>
                    <button class="px-3 py-1 bg-red-600 hover:bg-red-700 text-white rounded text-sm transition-colors">
                      View
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Export & Actions -->
        <div class="flex items-center justify-between pt-6 border-t border-gray-200 dark:border-gray-700">
          <div class="flex gap-3">
            <button
              @click="exportReport"
              class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors font-medium text-sm flex items-center gap-2"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
              </svg>
              Export Report
            </button>
            <button
              @click="flagAddress"
              class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors font-medium text-sm flex items-center gap-2"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9"></path>
              </svg>
              Flag Address
            </button>
          </div>
          
          <div class="text-sm text-gray-500 dark:text-gray-400">
            Last updated: {{ lastUpdated }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Modal backdrop blur */
.backdrop-blur-sm {
  backdrop-filter: blur(4px);
}

/* Custom scrollbar for modal */
.max-h-\[95vh\]::-webkit-scrollbar {
  width: 8px;
}

.max-h-\[95vh\]::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 4px;
}

.max-h-\[95vh\]::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

.max-h-\[95vh\]::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

.dark .max-h-\[95vh\]::-webkit-scrollbar-track {
  background: #374151;
}

.dark .max-h-\[95vh\]::-webkit-scrollbar-thumb {
  background: #6b7280;
}

.dark .max-h-\[95vh\]::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}

/* Tab navigation styling */
.space-x-1 > button {
  transition: all 0.2s ease;
}

.space-x-1 > button:hover {
  transform: translateY(-1px);
}

/* Smooth animations */
.fixed.inset-0 {
  animation: modalFadeIn 0.3s ease-out;
}

@keyframes modalFadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.bg-white.dark\:bg-gray-800 {
  animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

/* Tab content animation */
.space-y-6 {
  animation: tabContentFadeIn 0.4s ease-out;
}

@keyframes tabContentFadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Enhanced hover effects */
.cursor-pointer:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

/* Table row hover effects */
tbody tr:hover {
  transform: translateX(2px);
}

/* Button hover animations */
button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

button:active {
  transform: translateY(0);
}

/* Progress circle animations */
.transform.-rotate-90 path:last-child {
  animation: progressFill 1s ease-out;
}

@keyframes progressFill {
  from {
    stroke-dasharray: 0, 100;
  }
}

/* Risk badge pulse animation */
.bg-red-100.dark\:bg-red-900\/30 {
  animation: riskPulse 2s ease-in-out infinite;
}

@keyframes riskPulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4);
  }
  50% {
    box-shadow: 0 0 0 8px rgba(239, 68, 68, 0);
  }
}

/* Gradient backgrounds */
.bg-gradient-to-br {
  background: linear-gradient(135deg, var(--tw-gradient-stops));
}

/* Enhanced focus styles */
button:focus-visible,
input:focus-visible {
  outline: 2px solid #16a34a;
  outline-offset: 2px;
}

/* Sticky header shadow */
.sticky {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.dark .sticky {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

/* Transaction type icons */
.text-green-600::before {
  content: '↓';
  margin-right: 0.25rem;
}

.text-red-600::before {
  content: '↑';
  margin-right: 0.25rem;
}

/* Connected addresses grid animation */
.grid > div {
  animation: fadeInUp 0.4s ease-out;
  animation-fill-mode: both;
}

.grid > div:nth-child(1) { animation-delay: 0.1s; }
.grid > div:nth-child(2) { animation-delay: 0.2s; }
.grid > div:nth-child(3) { animation-delay: 0.3s; }
.grid > div:nth-child(4) { animation-delay: 0.4s; }
.grid > div:nth-child(5) { animation-delay: 0.5s; }
.grid > div:nth-child(6) { animation-delay: 0.6s; }

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

/* Risk factor circles animation */
.relative.w-16.h-16 {
  animation: scaleIn 0.6s ease-out;
}

@keyframes scaleIn {
  from {
    transform: scale(0);
  }
  to {
    transform: scale(1);
  }
}

/* Compliance score animation */
.relative.w-32.h-32 {
  animation: bounceIn 0.8s ease-out;
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

/* Sanctions status indicators */
.bg-green-100.dark\:bg-green-900\/30::before {
  content: '✓';
  margin-right: 0.5rem;
  font-weight: bold;
}

.bg-red-100.dark\:bg-red-900\/30::before {
  content: '⚠';
  margin-right: 0.5rem;
  font-weight: bold;
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

/* Loading states */
.loading {
  position: relative;
  overflow: hidden;
}

.loading::after {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% {
    left: -100%;
  }
  100% {
    left: 100%;
  }
}

/* Report cards hover effects */
.p-4.bg-gray-50:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
}

/* Tab indicator animation */
.bg-white.dark\:bg-gray-600 {
  position: relative;
}

.bg-white.dark\:bg-gray-600::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  right: 0;
  height: 2px;
  background: #16a34a;
  border-radius: 1px;
}

/* Enhanced card styling */
.card-elevated {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.card-elevated:hover {
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  transform: translateY(-2px);
}

/* Responsive adjustments */
@media (max-width: 1024px) {
  .grid-cols-1.lg\:grid-cols-3 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
  
  .grid-cols-1.lg\:grid-cols-2 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
  
  .max-w-7xl {
    max-width: 100%;
    margin: 0.5rem;
  }
}

@media (max-width: 768px) {
  .grid-cols-1.md\:grid-cols-2 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
  
  .flex.gap-3 {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .overflow-x-auto {
    font-size: 0.875rem;
  }
  
  .p-6 {
    padding: 1rem;
  }
  
  /* Stack tab navigation on mobile */
  .space-x-1 {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.25rem;
  }
  
  .space-x-1 > button {
    font-size: 0.75rem;
    padding: 0.5rem;
  }
}

@media (max-width: 640px) {
  .text-2xl {
    font-size: 1.5rem;
  }
  
  .grid-cols-2 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
  
  .grid-cols-4 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  
  /* Single column tab navigation on small screens */
  .space-x-1 {
    grid-template-columns: repeat(1, 1fr);
  }
  
  /* Adjust report cards for mobile */
  .grid-cols-1.md\:grid-cols-2.lg\:grid-cols-3 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
}

/* Print styles */
@media print {
  .fixed {
    position: static !important;
    background: white !important;
  }
  
  .bg-black\/50 {
    background: transparent !important;
  }
  
  .backdrop-blur-sm {
    backdrop-filter: none !important;
  }
  
  .shadow-2xl {
    box-shadow: none !important;
  }
  
  .sticky {
    position: static !important;
  }
  
  button {
    display: none !important;
  }
  
  .overflow-y-auto {
    overflow: visible !important;
  }
  
  .max-h-\[95vh\] {
    max-height: none !important;
  }
  
  /* Hide tab navigation in print */
  .space-x-1 {
    display: none !important;
  }
  
  /* Show all content in print */
  .space-y-6 {
    display: block !important;
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

/* Custom focus indicators for accessibility */
.focus-ring:focus {
  outline: 2px solid #16a34a;
  outline-offset: 2px;
  border-radius: 0.375rem;
}

/* Enhanced visual hierarchy */
.section-header {
  border-left: 4px solid #16a34a;
  padding-left: 1rem;
}

/* Status indicators */
.status-indicator {
  position: relative;
}

.status-indicator::before {
  content: '';
  position: absolute;
  top: 50%;
  left: -12px;
  transform: translateY(-50%);
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: currentColor;
}

/* Interactive elements enhancement */
.interactive:hover {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05));
}

.dark .interactive:hover {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.02));
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

/* SigmaVerde brand colors */
.bg-sigmaverde {
  background: linear-gradient(135deg, #16a34a 0%, #059669 100%);
}

.text-sigmaverde {
  color: #16a34a;
}

.border-sigmaverde {
  border-color: #16a34a;
}

.ring-sigmaverde {
  --tw-ring-color: #16a34a;
}

/* Data visualization enhancements */
.chart-container {
  position: relative;
  overflow: hidden;
}

.chart-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg, transparent 30%, rgba(255, 255, 255, 0.1) 50%, transparent 70%);
  animation: chartShine 3s ease-in-out infinite;
}

@keyframes chartShine {
  0%, 100% {
    transform: translateX(-100%);
  }
  50% {
    transform: translateX(100%);
  }
}

/* Tab content specific animations */
.space-y-6 > * {
  animation: slideInFromBottom 0.5s ease-out;
  animation-fill-mode: both;
}

.space-y-6 > *:nth-child(1) { animation-delay: 0.1s; }
.space-y-6 > *:nth-child(2) { animation-delay: 0.2s; }
.space-y-6 > *:nth-child(3) { animation-delay: 0.3s; }
.space-y-6 > *:nth-child(4) { animation-delay: 0.4s; }

@keyframes slideInFromBottom {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Report generation cards special effects */
.report-card {
  position: relative;
  overflow: hidden;
}

.report-card::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  transform: rotate(45deg);
  transition: all 0.5s ease;
  opacity: 0;
}

.report-card:hover::before {
  animation: shimmerEffect 0.8s ease-out;
}

@keyframes shimmerEffect {
  0% {
    transform: translateX(-100%) translateY(-100%) rotate(45deg);
    opacity: 0;
  }
  50% {
    opacity: 1;
  }
  100% {
    transform: translateX(100%) translateY(100%) rotate(45deg);
    opacity: 0;
  }
}

/* Enhanced button states */
.btn-primary {
  background: linear-gradient(135deg, #16a34a, #059669);
  transition: all 0.3s ease;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #15803d, #047857);
  box-shadow: 0 8px 25px rgba(22, 163, 74, 0.3);
}

.btn-secondary {
  background: linear-gradient(135deg, #6b7280, #4b5563);
  transition: all 0.3s ease;
}

.btn-secondary:hover {
  background: linear-gradient(135deg, #4b5563, #374151);
  box-shadow: 0 8px 25px rgba(107, 114, 128, 0.3);
}

/* Risk level specific styling */
.risk-critical {
  background: linear-gradient(135deg, #dc2626, #b91c1c);
  animation: criticalPulse 2s ease-in-out infinite;
}

@keyframes criticalPulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(220, 38, 38, 0.7);
  }
  50% {
    box-shadow: 0 0 0 10px rgba(220, 38, 38, 0);
  }
}

.risk-high {
  background: linear-gradient(135deg, #ea580c, #dc2626);
}

.risk-medium {
  background: linear-gradient(135deg, #eab308, #f59e0b);
}

.risk-low {
  background: linear-gradient(135deg, #16a34a, #22c55e);
}

/* Transaction flow visualization */
.transaction-flow {
  position: relative;
}

.transaction-flow::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, #16a34a, transparent);
  animation: flowAnimation 3s ease-in-out infinite;
}

@keyframes flowAnimation {
  0%, 100% {
    opacity: 0;
    transform: translateX(-100%);
  }
  50% {
    opacity: 1;
    transform: translateX(0);
  }
}

/* Network connection lines */
.connection-line {
  position: relative;
}

.connection-line::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, currentColor, transparent);
  animation: connectionPulse 2s ease-in-out infinite;
}

@keyframes connectionPulse {
  0%, 100% {
    opacity: 0.3;
  }
  50% {
    opacity: 1;
  }
}

/* Compliance score ring enhancement */
.compliance-ring {
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.1));
}

.compliance-ring:hover {
  filter: drop-shadow(0 8px 16px rgba(0, 0, 0, 0.2));
  transform: scale(1.05);
}

/* Address type badges */
.address-type-badge {
  position: relative;
  overflow: hidden;
}

.address-type-badge::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s ease;
}

.address-type-badge:hover::before {
  left: 100%;
}

/* Enhanced scrollbar for tables */
.table-container {
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 #f1f5f9;
}

.table-container::-webkit-scrollbar {
  height: 8px;
}

.table-container::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 4px;
}

.table-container::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

.table-container::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

.dark .table-container {
  scrollbar-color: #6b7280 #374151;
}

.dark .table-container::-webkit-scrollbar-track {
  background: #374151;
}

.dark .table-container::-webkit-scrollbar-thumb {
  background: #6b7280;
}

.dark .table-container::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}

/* Loading skeleton animation */
.skeleton {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
}

.dark .skeleton {
  background: linear-gradient(90deg, #374151 25%, #4b5563 50%, #374151 75%);
  background-size: 200% 100%;
}

@keyframes loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

/* Enhanced modal backdrop */
.modal-backdrop {
  background: radial-gradient(circle at center, rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.4));
}

/* Floating action button style */
.fab {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #16a34a, #059669);
  box-shadow: 0 8px 24px rgba(22, 163, 74, 0.3);
  transition: all 0.3s ease;
}

.fab:hover {
  transform: scale(1.1);
  box-shadow: 0 12px 32px rgba(22, 163, 74, 0.4);
}

/* Notification badge */
.notification-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  background: #dc2626;
  color: white;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  font-size: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: badgePulse 2s ease-in-out infinite;
}

@keyframes badgePulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.2);
  }
}

/* Glass morphism effect */
.glass {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.dark .glass {
  background: rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* Gradient text effect */
.gradient-text {
  background: linear-gradient(135deg, #16a34a, #059669, #0891b2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: gradientShift 3s ease-in-out infinite;
}

@keyframes gradientShift {
  0%, 100% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
}

/* Enhanced form elements */
.form-input {
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.form-input:focus {
  border-color: #16a34a;
  box-shadow: 0 0 0 3px rgba(22, 163, 74, 0.1);
  transform: translateY(-1px);
}

.form-select {
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='m6 8 4 4 4-4'/%3e%3c/svg%3e");
  background-position: right 0.5rem center;
  background-repeat: no-repeat;
  background-size: 1.5em 1.5em;
  padding-right: 2.5rem;
}

/* Micro-interactions */
.micro-bounce:hover {
  animation: microBounce 0.3s ease;
}

@keyframes microBounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-2px);
  }
}

.micro-rotate:hover {
  animation: microRotate 0.3s ease;
}

@keyframes microRotate {
  0%, 100% {
    transform: rotate(0deg);
  }
  50% {
    transform: rotate(5deg);
  }
}

/* Success/Error state animations */
.success-flash {
  animation: successFlash 0.6s ease;
}

@keyframes successFlash {
  0%, 100% {
    background-color: transparent;
  }
  50% {
    background-color: rgba(34, 197, 94, 0.1);
  }
}

.error-shake {
  animation: errorShake 0.5s ease;
}

@keyframes errorShake {
  0%, 100% {
    transform: translateX(0);
  }
  25% {
    transform: translateX(-5px);
  }
  75% {
    transform: translateX(5px);
  }
}

/* Dark mode transitions */
* {
  transition: background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease;
}

/* Accessibility improvements */
@media (prefers-reduced-motion: reduce) {
  .micro-bounce:hover,
  .micro-rotate:hover {
    animation: none;
  }
  
  .success-flash,
  .error-shake {
    animation: none;
  }
}

/* Focus management for keyboard navigation */
.focus-trap {
  outline: none;
}

.focus-trap:focus-within {
  outline: 2px solid #16a34a;
  outline-offset: 2px;
}

/* Enhanced typography */
.text-balance {
  text-wrap: balance;
}

.text-pretty {
  text-wrap: pretty;
}

/* Container queries support */
@container (max-width: 768px) {
  .container-responsive {
    padding: 1rem;
  }
  
  .container-responsive .grid {
    grid-template-columns: 1fr;
  }
}

/* Modern CSS features */
.scroll-smooth {
  scroll-behavior: smooth;
}

.scroll-snap-y {
  scroll-snap-type: y mandatory;
}

.scroll-snap-start {
  scroll-snap-align: start;
}

/* Color scheme adaptation */
@media (prefers-color-scheme: dark) {
  :root {
    color-scheme: dark;
  }
}

/* Enhanced accessibility */
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

/* Focus indicators for better accessibility */
.focus-visible:focus {
  outline: 2px solid #16a34a;
  outline-offset: 2px;
  border-radius: 0.25rem;
}

/* High contrast mode enhancements */
@media (prefers-contrast: high) {
  .bg-gradient-to-br,
  .bg-gradient-to-r {
    background: var(--fallback-color, #16a34a) !important;
  }
  
  .text-gray-500,
  .text-gray-400 {
    color: var(--high-contrast-text, #000) !important;
  }
  
  .dark .text-gray-500,
  .dark .text-gray-400 {
    color: var(--high-contrast-text-dark, #fff) !important;
  }
}

/* Print optimizations */
@media print {
  .no-print {
    display: none !important;
  }
  
  .print-break-before {
    break-before: page;
  }
  
  .print-break-after {
    break-after: page;
  }
  
  .print-break-inside-avoid {
    break-inside: avoid;
  }
  
  /* Optimize spacing for print */
  .space-y-6 > * {
    margin-bottom: 1rem !important;
  }
  
  /* Hide interactive elements */
  button,
  .cursor-pointer {
    display: none !important;
  }
  
  /* Show all tab content in print */
  .hidden {
    display: block !important;
  }
}

/* Performance optimizations */
.will-change-transform {
  will-change: transform;
}

.will-change-opacity {
  will-change: opacity;
}

.gpu-accelerated {
  transform: translateZ(0);
  backface-visibility: hidden;
  perspective: 1000px;
}

/* Modern layout features */
.subgrid {
  display: subgrid;
}

.container-query {
  container-type: inline-size;
}

/* Advanced animations */
@keyframes morphBackground {
  0%, 100% {
    border-radius: 0.5rem;
    background: linear-gradient(135deg, #16a34a, #059669);
  }
  25% {
    border-radius: 1rem;
    background: linear-gradient(135deg, #059669, #0891b2);
  }
  50% {
    border-radius: 1.5rem;
    background: linear-gradient(135deg, #0891b2, #7c3aed);
  }
  75% {
    border-radius: 1rem;
    background: linear-gradient(135deg, #7c3aed, #16a34a);
  }
}

.morph-animation {
  animation: morphBackground 8s ease-in-out infinite;
}

/* Particle effect background */
@keyframes particleFloat {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
    opacity: 1;
  }
  50% {
    transform: translateY(-20px) rotate(180deg);
    opacity: 0.5;
  }
}

.particle-bg::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: radial-gradient(circle at 20% 80%, rgba(22, 163, 74, 0.1) 0%, transparent 50%),
                    radial-gradient(circle at 80% 20%, rgba(5, 150, 105, 0.1) 0%, transparent 50%),
                    radial-gradient(circle at 40% 40%, rgba(8, 145, 178, 0.1) 0%, transparent 50%);
  animation: particleFloat 6s ease-in-out infinite;
  pointer-events: none;
}

/* Advanced hover states */
.hover-lift {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.hover-lift:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

/* Glassmorphism cards */
.glass-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.dark .glass-card {
  background: rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

/* Neon glow effects */
.neon-glow {
  box-shadow: 0 0 5px #16a34a,
              0 0 10px #16a34a,
              0 0 15px #16a34a,
              0 0 20px #16a34a;
  animation: neonPulse 2s ease-in-out infinite alternate;
}

@keyframes neonPulse {
  from {
    box-shadow: 0 0 5px #16a34a,
                0 0 10px #16a34a,
                0 0 15px #16a34a,
                0 0 20px #16a34a;
  }
  to {
    box-shadow: 0 0 2px #16a34a,
                0 0 5px #16a34a,
                0 0 8px #16a34a,
                0 0 12px #16a34a;
  }
}

/* Liquid button effect */
.liquid-button {
  position: relative;
  overflow: hidden;
}

.liquid-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.liquid-button:hover::before {
  left: 100%;
}

/* Magnetic hover effect */
.magnetic {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.magnetic:hover {
  transform: scale(1.05) rotate(1deg);
}

/* Typewriter effect */
.typewriter {
  overflow: hidden;
  border-right: 0.15em solid #16a34a;
  white-space: nowrap;
  margin: 0 auto;
  letter-spacing: 0.15em;
  animation: typing 3.5s steps(40, end),
             blink-caret 0.75s step-end infinite;
}

@keyframes typing {
  from {
    width: 0;
  }
  to {
    width: 100%;
  }
}

@keyframes blink-caret {
  from, to {
    border-color: transparent;
  }
  50% {
    border-color: #16a34a;
  }
}

/* Parallax scrolling effect */
.parallax {
  transform: translateZ(0);
  transition: transform 0.1s ease-out;
}

/* 3D card flip effect */
.flip-card {
  perspective: 1000px;
}

.flip-card-inner {
  position: relative;
  width: 100%;
  height: 100%;
  text-align: center;
  transition: transform 0.6s;
  transform-style: preserve-3d;
}

.flip-card:hover .flip-card-inner {
  transform: rotateY(180deg);
}

.flip-card-front,
.flip-card-back {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
}

.flip-card-back {
  transform: rotateY(180deg);
}

/* Ripple effect */
.ripple {
  position: relative;
  overflow: hidden;
}

.ripple::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  transform: translate(-50%, -50%);
  transition: width 0.6s, height 0.6s;
}

.ripple:active::before {
  width: 300px;
  height: 300px;
}

/* Floating elements */
.float {
  animation: float 6s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-20px);
  }
}

.float-delayed {
  animation: float 6s ease-in-out infinite;
  animation-delay: 2s;
}

/* Breathing animation */
.breathe {
  animation: breathe 4s ease-in-out infinite;
}

@keyframes breathe {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

/* Text reveal animation */
.text-reveal {
  position: relative;
  overflow: hidden;
}

.text-reveal::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: #16a34a;
  animation: textReveal 2s ease-in-out;
}

@keyframes textReveal {
  0% {
    left: 0;
  }
  50% {
    left: 0;
    right: 0;
  }
  100% {
    left: 100%;
  }
}

/* Stagger animation for lists */
.stagger-item {
  animation: staggerFadeIn 0.6s ease-out both;
}

.stagger-item:nth-child(1) { animation-delay: 0.1s; }
.stagger-item:nth-child(2) { animation-delay: 0.2s; }
.stagger-item:nth-child(3) { animation-delay: 0.3s; }
.stagger-item:nth-child(4) { animation-delay: 0.4s; }
.stagger-item:nth-child(5) { animation-delay: 0.5s; }

@keyframes staggerFadeIn {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Modern scrollbar */
.modern-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: #16a34a transparent;
}

.modern-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.modern-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.modern-scrollbar::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, #16a34a, #059669);
  border-radius: 3px;
}

.modern-scrollbar::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg, #15803d, #047857);
}

/* Utility classes for common patterns */
.center-absolute {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.full-bleed {
  width: 100vw;
  margin-left: 50%;
  transform: translateX(-50%);
}

.aspect-ratio-16-9 {
  aspect-ratio: 16 / 9;
}

.aspect-ratio-4-3 {
  aspect-ratio: 4 / 3;
}

.aspect-ratio-1-1 {
  aspect-ratio: 1 / 1;
}

/* Modern CSS Grid utilities */
.grid-auto-fit {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.grid-auto-fill {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

/* Container queries for responsive components */
@container (min-width: 400px) {
  .container-md\:grid-cols-2 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@container (min-width: 600px) {
  .container-lg\:grid-cols-3 {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

/* CSS Logical Properties */
.margin-inline-auto {
  margin-inline: auto;
}

.padding-block-4 {
  padding-block: 1rem;
}

.padding-inline-6 {
  padding-inline: 1.5rem;
}

/* Modern color functions */
.bg-primary-hsl {
  background: hsl(142 71% 45%);
}

.text-primary-oklch {
  color: oklch(0.6 0.15 142);
}

/* View transitions API support */
@supports (view-transition-name: none) {
  .view-transition-fade {
    view-transition-name: fade;
  }
  
  ::view-transition-old(fade),
  ::view-transition-new(fade) {
    animation-duration: 0.3s;
  }
}

/* Scroll-driven animations */
@supports (animation-timeline: scroll()) {
  .scroll-animate {
    animation: scrollProgress linear;
    animation-timeline: scroll();
  }
  
  @keyframes scrollProgress {
    from {
      transform: translateX(-100%);
    }
    to {
      transform: translateX(0);
    }
  }
}

/* CSS Anchor Positioning */
@supports (anchor-name: --anchor) {
  .anchor-element {
    anchor-name: --my-anchor;
  }
  
  .positioned-element {
    position: absolute;
    left: anchor(--my-anchor right);
    top: anchor(--my-anchor bottom);
  }
}


/* CSS Custom Properties for theming */
:root {
  --color-primary: 22 163 74;
  --color-primary-dark: 21 128 61;
  --color-secondary: 107 114 128;
  --color-success: 34 197 94;
  --color-warning: 234 179 8;
  --color-error: 239 68 68;
  --color-info: 59 130 246;
  
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
  --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
  
  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-xl: 1rem;
  
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;
  
  --font-size-xs: 0.75rem;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;
  --font-size-xl: 1.25rem;
  --font-size-2xl: 1.5rem;
  --font-size-3xl: 1.875rem;
  
  --line-height-tight: 1.25;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.75;
  
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
  
  --z-index-dropdown: 1000;
  --z-index-sticky: 1020;
  --z-index-fixed: 1030;
  --z-index-modal-backdrop: 1040;
  --z-index-modal: 1050;
  --z-index-popover: 1060;
  --z-index-tooltip: 1070;
}

/* Dark theme custom properties */
[data-theme="dark"] {
  --color-primary: 34 197 94;
  --color-primary-dark: 22 163 74;
}

/* High contrast theme */
[data-theme="high-contrast"] {
  --color-primary: 0 0 0;
  --color-primary-dark: 255 255 255;
}

/* Reduced motion theme */
@media (prefers-reduced-motion: reduce) {
  :root {
    --transition-duration: 0.01ms;
    --animation-duration: 0.01ms;
  }
  
  *,
  *::before,
  *::after {
    animation-duration: var(--animation-duration) !important;
    animation-iteration-count: 1 !important;
    transition-duration: var(--transition-duration) !important;
    scroll-behavior: auto !important;
  }
}

/* Color scheme preference */
@media (prefers-color-scheme: dark) {
  :root:not([data-theme]) {
    color-scheme: dark;
  }
}

/* Contrast preference */
@media (prefers-contrast: high) {
  :root {
    --shadow-sm: 0 0 0 1px rgb(0 0 0);
    --shadow-md: 0 0 0 2px rgb(0 0 0);
    --shadow-lg: 0 0 0 3px rgb(0 0 0);
    --shadow-xl: 0 0 0 4px rgb(0 0 0);
  }
}

/* Modern CSS features detection */
@supports (color: color(display-p3 1 0 0)) {
  .color-p3 {
    color: color(display-p3 0.086 0.639 0.290);
  }
}

@supports (backdrop-filter: blur(10px)) {
  .backdrop-blur-supported {
    backdrop-filter: blur(10px);
  }
}

@supports (container-type: inline-size) {
  .container-queries-supported {
    container-type: inline-size;
  }
}

@supports (view-transition-name: slide) {
  .view-transitions-supported {
    view-transition-name: slide;
  }
}

/* Performance optimizations */
.optimize-rendering {
  contain: layout style paint;
  content-visibility: auto;
  contain-intrinsic-size: 0 500px;
}

.optimize-animations {
  will-change: transform, opacity;
  transform: translateZ(0);
  backface-visibility: hidden;
}

/* Accessibility enhancements */
.focus-ring {
  outline: 2px solid transparent;
  outline-offset: 2px;
}

.focus-ring:focus-visible {
  outline-color: rgb(var(--color-primary));
}

.screen-reader-only {
  position: absolute !important;
  width: 1px !important;
  height: 1px !important;
  padding: 0 !important;
  margin: -1px !important;
  overflow: hidden !important;
  clip: rect(0, 0, 0, 0) !important;
  white-space: nowrap !important;
  border: 0 !important;
}

/* Skip link for keyboard navigation */
.skip-link {
  position: absolute;
  top: -40px;
  left: 6px;
  background: rgb(var(--color-primary));
  color: white;
  padding: 8px;
  text-decoration: none;
  border-radius: 4px;
  z-index: 9999;
}

.skip-link:focus {
  top: 6px;
}

/* High contrast mode improvements */
@media (prefers-contrast: high) {
  .btn {
    border: 2px solid currentColor;
  }
  
  .card {
    border: 2px solid currentColor;
  }
  
  .input {
    border: 2px solid currentColor;
  }
}

/* Print styles optimization */
@media print {
  @page {
    margin: 1in;
    size: letter;
  }
  
  .print-hidden {
    display: none !important;
  }
  
  .print-visible {
    display: block !important;
  }
  
  .print-break-before {
    page-break-before: always;
  }
  
  .print-break-after {
    page-break-after: always;
  }
  
  .print-break-inside-avoid {
    page-break-inside: avoid;
  }
  
  /* Optimize colors for print */
  .bg-gradient-to-r,
  .bg-gradient-to-br {
    background: rgb(var(--color-primary)) !important;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
  
  /* Ensure text is readable */
  .text-white {
    color: black !important;
  }
  
  /* Remove shadows for print */
  * {
    box-shadow: none !important;
    text-shadow: none !important;
  }
}

/* Modern layout with CSS Grid and Flexbox */
.layout-grid {
  display: grid;
  grid-template-areas: 
    "header header"
    "sidebar main"
    "footer footer";
  grid-template-columns: 250px 1fr;
  grid-template-rows: auto 1fr auto;
  min-height: 100vh;
}

.layout-header {
  grid-area: header;
}

.layout-sidebar {
  grid-area: sidebar;
}

.layout-main {
  grid-area: main;
}

.layout-footer {
  grid-area: footer;
}

@media (max-width: 768px) {
  .layout-grid {
    grid-template-areas: 
      "header"
      "main"
      "footer";
    grid-template-columns: 1fr;
  }
  
  .layout-sidebar {
    display: none;
  }
}

/* CSS Subgrid support */
@supports (grid-template-rows: subgrid) {
  .subgrid-rows {
    display: grid;
    grid-template-rows: subgrid;
  }
}

/* CSS :has() selector support */
@supports selector(:has(*)) {
  .card:has(.urgent) {
    border-color: rgb(var(--color-error));
    box-shadow: 0 0 0 1px rgb(var(--color-error) / 0.2);
  }
  
  .form-group:has(.input:invalid) {
    color: rgb(var(--color-error));
  }
}

/* CSS Cascade Layers for better organization */
@layer reset, base, components, utilities, overrides;

@layer reset {
  *, *::before, *::after {
    box-sizing: border-box;
  }
  
  * {
    margin: 0;
  }
  
  html, body {
    height: 100%;
  }
  
  body {
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
  }
  
  img, picture, video, canvas, svg {
    display: block;
    max-width: 100%;
  }
  
  input, button, textarea, select {
    font: inherit;
  }
  
  p, h1, h2, h3, h4, h5, h6 {
    overflow-wrap: break-word;
  }
}

/* Future CSS features with fallbacks */
.modern-button {
  background: rgb(var(--color-primary));
  background: color-mix(in srgb, rgb(var(--color-primary)) 90%, white 10%);
  border-radius: var(--radius-md);
  padding: var(--spacing-sm) var(--spacing-md);
  transition: all 0.2s ease;
}

.modern-button:hover {
  background: rgb(var(--color-primary-dark));
  background: color-mix(in srgb, rgb(var(--color-primary)) 80%, black 20%);
  transform: translateY(-1px);
}

/* CSS Nesting support */
.nested-styles {
  color: rgb(var(--color-primary));
  
  &:hover {
    color: rgb(var(--color-primary-dark));
  }
  
  & .child-element {
    margin-left: var(--spacing-md);
    
    &:first-child {
      margin-left: 0;
    }
  }
  
  @media (max-width: 768px) {
    font-size: var(--font-size-sm);
  }
}

/* CSS Container Queries */
.responsive-component {
  container-type: inline-size;
  container-name: component;
}

@container component (min-width: 400px) {
  .responsive-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--spacing-md);
  }
}

@container component (min-width: 600px) {
  .responsive-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

/* CSS Scroll Timeline */
@supports (animation-timeline: scroll()) {
  .scroll-progress {
    animation: progress-bar linear;
    animation-timeline: scroll(root);
    animation-range: 0% 100%;
  }
  
  @keyframes progress-bar {
    from {
      transform: scaleX(0);
    }
    to {
      transform: scaleX(1);
    }
  }
}

</style>
