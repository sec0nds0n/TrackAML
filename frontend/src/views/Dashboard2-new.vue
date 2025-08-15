<script setup>
import { useToast } from 'primevue/usetoast'
import { computed, onMounted, ref } from 'vue'

const toast = useToast()

// Reactive data
const selectedTimeframe = ref('24h')
const isLoading = ref(false)
const lastUpdate = ref(new Date())

// Start Tambahan

// Reactive data  

// Lifecycle
onMounted(() => {
  // Check for saved dark mode preference
  const savedDarkMode = localStorage.getItem('darkMode')
  if (savedDarkMode === 'true' || (!savedDarkMode && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    document.documentElement.classList.add('dark')
  }
  
  // Set up auto-refresh interval (every 30 seconds)
  setInterval(() => {
    if (!isLoading.value) {
      refreshData()
    }
  }, 30000)
  
  // Add keyboard shortcuts
  document.addEventListener('keydown', (e) => {
    if (e.ctrlKey || e.metaKey) {
      switch (e.key) {
        case 'd':
          e.preventDefault()
          toggleDarkMode()
          break
        case 'e':
          e.preventDefault()
          exportReport()
          break
        case 'r':
          e.preventDefault()
          refreshData()
          break
      }
    }
  })
})
// End Tambahan

// Mock data for crypto AML tracking
const cryptoMetrics = ref({
  suspiciousTransactions: {
    count: 247,
    change: 12,
    trend: 'up',
    btc: 156,
    eth: 91
  },
  highRiskAddresses: {
    count: 89,
    change: -3,
    trend: 'down',
    btc: 52,
    eth: 37
  },
  complianceScore: {
    score: 94.2,
    change: 2.1,
    trend: 'up'
  },
  activeCases: {
    count: 156,
    urgent: 23,
    btc: 89,
    eth: 67
  }
})

const alerts = ref([
  {
    id: 1,
    type: 'critical',
    title: 'Large BTC mixing service detected',
    description: 'Address 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa involved in tumbling',
    time: '2 min ago',
    crypto: 'BTC',
    amount: '45.7 BTC'
  },
  {
    id: 2,
    type: 'high',
    title: 'ETH privacy coin conversion',
    description: 'Suspicious ETH to Monero exchange pattern detected',
    time: '15 min ago',
    crypto: 'ETH',
    amount: '234.5 ETH'
  },
  {
    id: 3,
    type: 'medium',
    title: 'Rapid transaction structuring',
    description: 'Multiple small BTC transactions below reporting threshold',
    time: '1 hour ago',
    crypto: 'BTC',
    amount: '12.3 BTC'
  }
])

const recentCases = ref([
  {
    id: 'AML-BTC-001',
    customer: 'Wallet: 1A1zP1eP...',
    crypto: 'BTC',
    riskLevel: 'High',
    status: 'Under Review',
    date: '2024-01-15',
    amount: '125.7 BTC'
  },
  {
    id: 'AML-ETH-002',
    customer: 'Wallet: 0x742d35C...',
    crypto: 'ETH',
    riskLevel: 'Medium',
    status: 'Resolved',
    date: '2024-01-14',
    amount: '456.2 ETH'
  },
  {
    id: 'AML-BTC-003',
    customer: 'Exchange: Binance',
    crypto: 'BTC',
    riskLevel: 'High',
    status: 'Investigating',
    date: '2024-01-13',
    amount: '89.4 BTC'
  }
])

// Methods
const toggleDarkMode = () => {
  document.documentElement.classList.toggle('dark')
  const isDark = document.documentElement.classList.contains('dark')
  localStorage.setItem('darkMode', isDark)
}

const refreshData = async () => {
  isLoading.value = true
  // Simulate API call
  await new Promise(resolve => setTimeout(resolve, 1000))
  lastUpdate.value = new Date()
  isLoading.value = false
  toast.add({
    severity: 'success',
    summary: 'Data Refreshed',
    detail: 'AML data has been updated successfully',
    life: 3000
  })
}

const exportReport = () => {
  toast.add({
    severity: 'info',
    summary: 'Export Started',
    detail: 'Generating AML compliance report...',
    life: 3000
  })
}

// Computed properties
const totalCryptoVolume = computed(() => {
  return {
    btc: cryptoMetrics.value.activeCases.btc + cryptoMetrics.value.suspiciousTransactions.btc,
    eth: cryptoMetrics.value.activeCases.eth + cryptoMetrics.value.suspiciousTransactions.eth
  }
})

onMounted(() => {
  // Check for saved dark mode preference
  const savedDarkMode = localStorage.getItem('darkMode')
  if (savedDarkMode === 'true' || (!savedDarkMode && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    document.documentElement.classList.add('dark')
  }
})
</script>

<template>
    <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-6 transition-all duration-300">
        <!-- Header Section -->
        <div class="mb-8">
            <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                <div>
                    <div class="flex items-center gap-3 mb-2">
                        <div class="p-2 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg">
                            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path>
                            </svg>
                        </div>
                        <h1 class="text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-300 bg-clip-text text-transparent">
                            Crypto AML Compliance
                        </h1>
                    </div>
                    <p class="text-gray-600 dark:text-gray-300">Advanced Anti-Money Laundering monitoring for Bitcoin & Ethereum</p>
                </div>
                
                <div class="flex flex-col sm:flex-row items-start sm:items-center gap-4">
                    <div class="bg-white dark:bg-gray-800 px-4 py-3 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
                        <div class="flex items-center gap-2">
                            <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                            </svg>
                            <span class="text-sm text-gray-500 dark:text-gray-400">Last Updated:</span>
                            <span class="text-sm font-semibold text-gray-900 dark:text-white">{{ lastUpdate.toLocaleTimeString() }}</span>
                        </div>
                    </div>
                    
                    <div class="flex items-center gap-3">
                        <div class="flex items-center gap-2 bg-green-50 dark:bg-green-900/20 px-3 py-2 rounded-lg">
                            <div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                            <span class="text-sm font-medium text-green-700 dark:text-green-400">Live Monitoring</span>
                        </div>
                        
                        <button 
                            @click="refreshData" 
                            :disabled="isLoading"
                            class="p-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-lg transition-colors"
                        >
                            <svg class="w-4 h-4" :class="{ 'animate-spin': isLoading }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Crypto AML Key Metrics -->
        <div class="mb-8">
            <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 p-6">
                <div class="flex items-center justify-between mb-6">
                    <h2 class="text-xl font-bold text-gray-900 dark:text-white">Cryptocurrency AML Metrics</h2>
                    <div class="flex items-center gap-2">
                        <select 
                            v-model="selectedTimeframe"
                            class="text-sm border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        >
                            <option value="1h">Last Hour</option>
                            <option value="24h">Last 24 Hours</option>
                            <option value="7d">Last 7 Days</option>
                            <option value="30d">Last 30 Days</option>
                        </select>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
                    <!-- Suspicious Transactions -->
                    <div class="relative overflow-hidden bg-gradient-to-br from-red-50 via-red-50 to-red-100 dark:from-red-900/20 dark:via-red-900/15 dark:to-red-800/20 rounded-xl p-6 border border-red-200 dark:border-red-800/30">
                        <div class="flex items-start justify-between">
                            <div class="flex-1">
                                <p class="text-red-600 dark:text-red-400 text-sm font-semibold mb-1">Suspicious Transactions</p>
                                <p class="text-3xl font-bold text-red-900 dark:text-red-100 mb-2">{{ cryptoMetrics.suspiciousTransactions.count }}</p>
                                <div class="flex items-center gap-4 text-xs">
                                    <div class="flex items-center gap-1">
                                        <div class="w-2 h-2 bg-orange-500 rounded-full"></div>
                                        <span class="text-gray-600 dark:text-gray-300">BTC: {{ cryptoMetrics.suspiciousTransactions.btc }}</span>
                                    </div>
                                    <div class="flex items-center gap-1">
                                        <div class="w-2 h-2 bg-blue-500 rounded-full"></div>
                                        <span class="text-gray-600 dark:text-gray-300">ETH: {{ cryptoMetrics.suspiciousTransactions.eth }}</span>
                                    </div>
                                </div>
                                <div class="flex items-center mt-3">
                                    <svg class="w-4 h-4 text-red-500 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                        <path fill-rule="evenodd" d="M5.293 7.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L6.707 7.707a1 1 0 01-1.414 0z" clip-rule="evenodd"></path>
                                    </svg>
                                    <span class="text-red-600 dark:text-red-400 text-xs font-medium">+{{ cryptoMetrics.suspiciousTransactions.change }}% from yesterday</span>
                                </div>
                            </div>
                            <div class="bg-red-200 dark:bg-red-800/50 p-3 rounded-xl">
                                <svg class="w-6 h-6 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                                </svg>
                            </div>
                        </div>
                        <div class="absolute -bottom-2 -right-2 w-20 h-20 bg-red-200/30 dark:bg-red-800/20 rounded-full"></div>
                    </div>

                    <!-- High Risk Addresses -->
                    <div class="relative overflow-hidden bg-gradient-to-br from-orange-50 via-orange-50 to-orange-100 dark:from-orange-900/20 dark:via-orange-900/15 dark:to-orange-800/20 rounded-xl p-6 border border-orange-200 dark:border-orange-800/30">
                        <div class="flex items-start justify-between">
                            <div class="flex-1">
                                <p class="text-orange-600 dark:text-orange-400 text-sm font-semibold mb-1">High Risk Addresses</p>
                                <p class="text-3xl font-bold text-orange-900 dark:text-orange-100 mb-2">{{ cryptoMetrics.highRiskAddresses.count }}</p>
                                <div class="flex items-center gap-4 text-xs">
                                    <div class="flex items-center gap-1">
                                        <div class="w-2 h-2 bg-orange-500 rounded-full"></div>
                                        <span class="text-gray-600 dark:text-gray-300">BTC: {{ cryptoMetrics.highRiskAddresses.btc }}</span>
                                    </div>
                                    <div class="flex items-center gap-1">
                                        <div class="w-2 h-2 bg-blue-500 rounded-full"></div>
                                        <span class="text-gray-600 dark:text-gray-300">ETH: {{ cryptoMetrics.highRiskAddresses.eth }}</span>
                                    </div>
                                </div>
                                <div class="flex items-center mt-3">
                                    <svg class="w-4 h-4 text-green-500 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                        <path fill-rule="evenodd" d="M14.707 12.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 14.586V3a1 1 0 012 0v11.586l2.293-2.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
                                    </svg>
                                    <span class="text-green-600 dark:text-green-400 text-xs font-medium">{{ Math.abs(cryptoMetrics.highRiskAddresses.change) }}% from yesterday</span>
                                </div>
                            </div>
                            <div class="bg-orange-200 dark:bg-orange-800/50 p-3 rounded-xl">
                                <svg class="w-6 h-6 text-orange-600 dark:text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                                </svg>
                            </div>
                        </div>
                        <div class="absolute -bottom-2 -right-2 w-20 h-20 bg-orange-200/30 dark:bg-orange-800/20 rounded-full"></div>
                    </div>

                    <!-- Compliance Score -->
                    <div class="relative overflow-hidden bg-gradient-to-br from-green-50 via-green-50 to-green-100 dark:from-green-900/20 dark:via-green-900/15 dark:to-green-800/20 rounded-xl p-6 border border-green-200 dark:border-green-800/30">
                        <div class="flex items-start justify-between">
                            <div class="flex-1">
                                <p class="text-green-600 dark:text-green-400 text-sm font-semibold mb-1">Compliance Score</p>
                                <p class="text-3xl font-bold text-green-900 dark:text-green-100 mb-2">{{ cryptoMetrics.complianceScore.score.toFixed(1) }}%</p>
                                <div class="w-full bg-green-200 dark:bg-green-800/30 rounded-full h-2 mb-3">
                                    <div class="bg-green-500 h-2 rounded-full transition-all duration-500" :style="`width: ${cryptoMetrics.complianceScore.score}%`"></div>
                                </div>
                                <div class="flex items-center">
                                    <svg class="w-4 h-4 text-green-500 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                        <path fill-rule="evenodd" d="M5.293 7.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L6.707 7.707a1 1 0 01-1.414 0z" clip-rule="evenodd"></path>
                                    </svg>
                                    <span class="text-green-600 dark:text-green-400 text-xs font-medium">+{{ cryptoMetrics.complianceScore.change }}% from last week</span>
                                </div>
                            </div>
                            <div class="bg-green-200 dark:bg-green-800/50 p-3 rounded-xl">
                                <svg class="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                </svg>
                            </div>
                        </div>
                        <div class="absolute -bottom-2 -right-2 w-20 h-20 bg-green-200/30 dark:bg-green-800/20 rounded-full"></div>
                    </div>

                    <!-- Active Cases -->
                    <div class="relative overflow-hidden bg-gradient-to-br from-blue-50 via-blue-50 to-blue-100 dark:from-blue-900/20 dark:via-blue-900/15 dark:to-blue-800/20 rounded-xl p-6 border border-blue-200 dark:border-blue-800/30">
                        <div class="flex items-start justify-between">
                            <div class="flex-1">
                                <p class="text-blue-600 dark:text-blue-400 text-sm font-semibold mb-1">Active Cases</p>
                                <p class="text-3xl font-bold text-blue-900 dark:text-blue-100 mb-2">{{ cryptoMetrics.activeCases.count }}</p>
                                <div class="flex items-center gap-4 text-xs mb-2">
                                    <div class="flex items-center gap-1">
                                        <div class="w-2 h-2 bg-orange-500 rounded-full"></div>
                                        <span class="text-gray-600 dark:text-gray-300">BTC: {{ cryptoMetrics.activeCases.btc }}</span>
                                    </div>
                                    <div class="flex items-center gap-1">
                                        <div class="w-2 h-2 bg-blue-500 rounded-full"></div>
                                        <span class="text-gray-600 dark:text-gray-300">ETH: {{ cryptoMetrics.activeCases.eth }}</span>
                                    </div>
                                </div>
                                <div class="flex items-center">
                                    <div class="w-2 h-2 bg-red-500 rounded-full mr-2 animate-pulse"></div>
                                    <span class="text-blue-600 dark:text-blue-400 text-xs font-medium">{{ cryptoMetrics.activeCases.urgent }} require immediate attention</span>
                                </div>
                            </div>
                            <div class="bg-blue-200 dark:bg-blue-800/50 p-3 rounded-xl">
                                <svg class="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path>
                                </svg>
                            </div>
                        </div>
                        <div class="absolute -bottom-2 -right-2 w-20 h-20 bg-blue-200/30 dark:bg-blue-800/20 rounded-full"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Main Dashboard Grid -->
        <div class="grid grid-cols-12 gap-6">
            <!-- Alerts Panel -->
            <div class="col-span-12 xl:col-span-8">
                <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 p-6 mb-6">
                    <div class="flex items-center justify-between mb-6">
                        <div class="flex items-center gap-3">
                            <h3 class="text-xl font-bold text-gray-900 dark:text-white">Critical Crypto Alerts</h3>
                            <span class="bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300 text-xs font-bold px-3 py-1 rounded-full animate-pulse">
                                {{ alerts.filter(a => a.type === 'critical').length }} Critical
                            </span>
                        </div>
                        <button class="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 font-semibold">
                            View All Alerts
                        </button>
                    </div>
                    
                    <div class="space-y-4">
                        <div 
                            v-for="alert in alerts" 
                            :key="alert.id"
                            class="group relative overflow-hidden rounded-xl border transition-all duration-200 hover:shadow-md"
                            :class="{
                                'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800/30': alert.type === 'critical',
                                'bg-orange-50 dark:bg-orange-900/20 border-orange-200 dark:border-orange-800/30': alert.type === 'high',
                                'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800/30': alert.type === 'medium'
                            }"
                        >
                            <div class="flex items-start p-4">
                                <div class="flex-shrink-0 mr-4">
                                    <div 
                                        class="w-3 h-3 rounded-full animate-pulse"
                                        :class="{
                                            'bg-red-500': alert.type === 'critical',
                                            'bg-orange-500': alert.type === 'high',
                                            'bg-yellow-500': alert.type === 'medium'
                                        }"
                                    ></div>
                                </div>
                                
                                <div class="flex-1 min-w-0">
                                    <div class="flex items-start justify-between">
                                        <div class="flex-1">
                                            <h4 
                                                class="text-sm font-bold mb-1"
                                                :class="{
                                                    'text-red-900 dark:text-red-100': alert.type === 'critical',
                                                    'text-orange-900 dark:text-orange-100': alert.type === 'high',
                                                    'text-yellow-900 dark:text-yellow-100': alert.type === 'medium'
                                                }"
                                            >
                                                {{ alert.title }}
                                            </h4>
                                            <p 
                                                class="text-xs mb-2"
                                                :class="{
                                                    'text-red-700 dark:text-red-300': alert.type === 'critical',
                                                    'text-orange-700 dark:text-orange-300': alert.type === 'high',
                                                    'text-yellow-700 dark:text-yellow-300': alert.type === 'medium'
                                                }"
                                            >
                                                {{ alert.description }}
                                            </p>
                                            <div class="flex items-center gap-4">
                                                <div class="flex items-center gap-2">
                                                    <div 
                                                        class="px-2 py-1 rounded-md text-xs font-bold"
                                                        :class="{
                                                            'bg-orange-100 dark:bg-orange-900/50 text-orange-800 dark:text-orange-300': alert.crypto === 'BTC',
                                                            'bg-blue-100 dark:bg-blue-900/50 text-blue-800 dark:text-blue-300': alert.crypto === 'ETH'
                                                        }"
                                                    >
                                                        {{ alert.crypto }}
                                                    </div>
                                                    <span class="text-xs font-semibold text-gray-600 dark:text-gray-300">{{ alert.amount }}</span>
                                                </div>
                                            </div>
                                        </div>
                                        
                                        <div class="flex flex-col items-end gap-2">
                                            <span 
                                                class="text-xs font-medium"
                                                :class="{
                                                    'text-red-600 dark:text-red-400': alert.type === 'critical',
                                                    'text-orange-600 dark:text-orange-400': alert.type === 'high',
                                                    'text-yellow-600 dark:text-yellow-400': alert.type === 'medium'
                                                }"
                                            >
                                                {{ alert.time }}
                                            </span>
                                            <button class="p-1 rounded-md hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors">
                                                <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z"></path>
                                                </svg>
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Compliance Status -->
            <div class="col-span-12 xl:col-span-4">
                <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 p-6 mb-6">
                    <div class="flex items-center gap-3 mb-6">
                        <div class="p-2 bg-gradient-to-r from-green-500 to-emerald-500 rounded-lg">
                            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path>
                            </svg>
                        </div>
                        <h3 class="text-lg font-bold text-gray-900 dark:text-white">Crypto Compliance Status</h3>
                    </div>
                    <div class="space-y-6">
                        <div class="space-y-4">
                            <div class="flex items-center justify-between p-3 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800/30">
                                <div class="flex items-center gap-3">
                                    <div class="w-4 h-4 bg-red-500 rounded-full"></div>
                                    <span class="text-sm font-semibold text-red-700 dark:text-red-300">Critical Risk</span>
                                </div>
                                <div class="text-right">
                                    <span class="text-lg font-bold text-red-900 dark:text-red-100">23%</span>
                                    <p class="text-xs text-red-600 dark:text-red-400">58 addresses</p>
                                </div>
                            </div>
                            
                            <div class="flex items-center justify-between p-3 bg-orange-50 dark:bg-orange-900/20 rounded-lg border border-orange-200 dark:border-orange-800/30">
                                <div class="flex items-center gap-3">
                                    <div class="w-4 h-4 bg-orange-500 rounded-full"></div>
                                    <span class="text-sm font-semibold text-orange-700 dark:text-orange-300">High Risk</span>
                                </div>
                                <div class="text-right">
                                    <span class="text-lg font-bold text-orange-900 dark:text-orange-100">31%</span>
                                    <p class="text-xs text-orange-600 dark:text-orange-400">78 addresses</p>
                                </div>
                            </div>
                            
                            <div class="flex items-center justify-between p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800/30">
                                <div class="flex items-center gap-3">
                                    <div class="w-4 h-4 bg-yellow-500 rounded-full"></div>
                                    <span class="text-sm font-semibold text-yellow-700 dark:text-yellow-300">Medium Risk</span>
                                </div>
                                <div class="text-right">
                                    <span class="text-lg font-bold text-yellow-900 dark:text-yellow-100">46%</span>
                                    <p class="text-xs text-yellow-600 dark:text-yellow-400">115 addresses</p>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Risk Trend Chart Placeholder -->
                        <div class="h-32 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-700/50 dark:to-gray-800/50 rounded-xl border border-gray-200 dark:border-gray-600 flex items-center justify-center">
                            <div class="text-center">
                                <svg class="w-8 h-8 text-gray-400 dark:text-gray-500 mx-auto mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                                </svg>
                                <p class="text-gray-500 dark:text-gray-400 text-sm">Chart visualization will be displayed here</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Transaction Flow Analysis with Chart -->
            <div class="col-span-12 xl:col-span-8">
                <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 p-6 mb-6">
                    <div class="flex items-center justify-between mb-6">
                        <div class="flex items-center gap-3">
                            <div class="p-2 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-lg">
                                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
                                </svg>
                            </div>
                            <h3 class="text-lg font-bold text-gray-900 dark:text-white">Suspicious Transaction Flow</h3>
                        </div>
                        <div class="flex items-center gap-2">
                            <button class="px-4 py-2 text-xs font-bold bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 rounded-lg hover:bg-indigo-200 dark:hover:bg-indigo-900/50 transition-colors">
                                Real-time
                            </button>
                            <button class="px-4 py-2 text-xs font-medium text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">
                                Historical
                            </button>
                        </div>
                    </div>
                    
                    <!-- Transaction Flow Chart -->
                    <div class="h-80 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-700/50 dark:to-gray-800/50 rounded-xl border border-gray-200 dark:border-gray-600 p-4">
                        <canvas ref="transactionFlowChart" class="w-full h-full"></canvas>
                    </div>
                </div>
            </div>

            <!-- Crypto Volume Distribution -->
            <div class="col-span-12 xl:col-span-4">
                <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 p-6 mb-6">
                    <div class="flex items-center gap-3 mb-6">
                        <div class="p-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg">
                            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z"></path>
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z"></path>
                            </svg>
                        </div>
                        <h3 class="text-lg font-bold text-gray-900 dark:text-white">Crypto Volume Distribution</h3>
                    </div>
                    
                    <div class="h-64 mb-4">
                        <canvas ref="cryptoVolumeChart" class="w-full h-full"></canvas>
                    </div>
                    
                    <div class="grid grid-cols-2 gap-4 text-center">
                        <div class="bg-orange-50 dark:bg-orange-900/20 p-3 rounded-lg">
                            <div class="flex items-center justify-center gap-2 mb-1">
                                <div class="w-3 h-3 bg-orange-500 rounded-full"></div>
                                <span class="text-sm font-semibold text-orange-700 dark:text-orange-300">BTC Total</span>
                            </div>
                            <p class="text-lg font-bold text-orange-900 dark:text-orange-100">{{ totalCryptoVolume.btc }}</p>
                        </div>
                        <div class="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg">
                            <div class="flex items-center justify-center gap-2 mb-1">
                                <div class="w-3 h-3 bg-blue-500 rounded-full"></div>
                                <span class="text-sm font-semibold text-blue-700 dark:text-blue-300">ETH Total</span>
                            </div>
                            <p class="text-lg font-bold text-blue-900 dark:text-blue-100">{{ totalCryptoVolume.eth }}</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Transaction Pattern Analysis -->
            <div class="col-span-12 xl:col-span-6">
                <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 p-6 mb-6">
                    <div class="flex items-center gap-3 mb-6">
                        <div class="p-2 bg-gradient-to-r from-red-500 to-pink-500 rounded-lg">
                            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                            </svg>
                        </div>
                        <h3 class="text-lg font-bold text-gray-900 dark:text-white">Suspicious Patterns</h3>
                    </div>
                    
                    <div class="h-64">
                        <canvas ref="transactionPatternChart" class="w-full h-full"></canvas>
                    </div>
                </div>
            </div>

            <!-- Geographic Risk Distribution -->
            <div class="col-span-12 xl:col-span-6">
                <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 p-6 mb-6">
                    <div class="flex items-center gap-3 mb-6">
                        <div class="p-2 bg-gradient-to-r from-green-500 to-teal-500 rounded-lg">
                            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                            </svg>
                        </div>
                        <h3 class="text-lg font-bold text-gray-900 dark:text-white">Geographic Risk</h3>
                    </div>
                    
                    <div class="h-64">
                        <canvas ref="geographicRiskChart" class="w-full h-full"></canvas>
                    </div>
                </div>
            </div>

            <!-- Alert Trends -->
            <div class="col-span-12 xl:col-span-8">
                <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 p-6 mb-6">
                    <div class="flex items-center gap-3 mb-6">
                        <div class="p-2 bg-gradient-to-r from-yellow-500 to-orange-500 rounded-lg">
                            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                            </svg>
                        </div>
                        <h3 class="text-lg font-bold text-gray-900 dark:text-white">Alert Trends (7 Days)</h3>
                    </div>
                    
                    <div class="h-64">
                        <canvas ref="alertTrendChart" class="w-full h-full"></canvas>
                    </div>
                </div>
            </div>

            <!-- Compliance Score Trend -->
            <div class="col-span-12 xl:col-span-4">
                <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 p-6 mb-6">
                    <div class="flex items-center gap-3 mb-6">
                        <div class="p-2 bg-gradient-to-r from-emerald-500 to-green-500 rounded-lg">
                            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
                            </svg>
                        </div>
                        <h3 class="text-lg font-bold text-gray-900 dark:text-white">Compliance Trend</h3>
                    </div>
                    
                    <div class="h-48 mb-4">
                        <canvas ref="complianceScoreChart" class="w-full h-full"></canvas>
                    </div>
                    
                    <div class="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
                        <div class="flex items-center justify-between mb-2">
                            <span class="text-sm font-semibold text-green-700 dark:text-green-300">Current Score</span>
                            <span class="text-2xl font-bold text-green-900 dark:text-green-100">{{ cryptoMetrics.complianceScore.score.toFixed(1) }}%</span>
                        </div>
                        <div class="w-full bg-green-200 dark:bg-green-800/30 rounded-full h-2">
                            <div class="bg-green-500 h-2 rounded-full transition-all duration-500" :style="`width: ${cryptoMetrics.complianceScore.score}%`"></div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Recent Cases -->
            <div class="col-span-12">
                <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 p-6">
                    <div class="flex items-center justify-between mb-6">
                        <div class="flex items-center gap-3">
                            <div class="p-2 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-lg">
                                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path>
                                </svg>
                            </div>
                            <h3 class="text-lg font-bold text-gray-900 dark:text-white">Recent Crypto AML Cases</h3>
                        </div>
                                                <button class="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 font-semibold flex items-center gap-1">
                            View All Cases
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                            </svg>
                        </button>
                    </div>
                    
                    <div class="overflow-x-auto">
                        <table class="w-full">
                            <thead>
                                <tr class="border-b-2 border-gray-200 dark:border-gray-700">
                                    <th class="text-left text-xs font-bold text-gray-600 dark:text-gray-400 uppercase tracking-wider py-4">Case ID</th>
                                    <th class="text-left text-xs font-bold text-gray-600 dark:text-gray-400 uppercase tracking-wider py-4">Wallet/Entity</th>
                                    <th class="text-left text-xs font-bold text-gray-600 dark:text-gray-400 uppercase tracking-wider py-4">Crypto</th>
                                    <th class="text-left text-xs font-bold text-gray-600 dark:text-gray-400 uppercase tracking-wider py-4">Amount</th>
                                    <th class="text-left text-xs font-bold text-gray-600 dark:text-gray-400 uppercase tracking-wider py-4">Risk</th>
                                    <th class="text-left text-xs font-bold text-gray-600 dark:text-gray-400 uppercase tracking-wider py-4">Status</th>
                                    <th class="text-left text-xs font-bold text-gray-600 dark:text-gray-400 uppercase tracking-wider py-4">Date</th>
                                    <th class="text-left text-xs font-bold text-gray-600 dark:text-gray-400 uppercase tracking-wider py-4">Actions</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
                                <tr v-for="case_ in recentCases" :key="case_.id" class="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                                    <td class="py-4">
                                        <span class="text-sm font-bold text-blue-600 dark:text-blue-400">{{ case_.id }}</span>
                                    </td>
                                    <td class="py-4">
                                        <div class="flex flex-col">
                                            <span class="text-sm font-medium text-gray-900 dark:text-white">{{ case_.customer }}</span>
                                            <span class="text-xs text-gray-500 dark:text-gray-400">{{ case_.customer.includes('Wallet') ? 'Individual' : 'Exchange' }}</span>
                                        </div>
                                    </td>
                                    <td class="py-4">
                                        <div 
                                            class="inline-flex items-center gap-1 px-2 py-1 rounded-md text-xs font-bold"
                                            :class="{
                                                'bg-orange-100 dark:bg-orange-900/50 text-orange-800 dark:text-orange-300': case_.crypto === 'BTC',
                                                'bg-blue-100 dark:bg-blue-900/50 text-blue-800 dark:text-blue-300': case_.crypto === 'ETH'
                                            }"
                                        >
                                            <div 
                                                class="w-2 h-2 rounded-full"
                                                :class="{
                                                    'bg-orange-500': case_.crypto === 'BTC',
                                                    'bg-blue-500': case_.crypto === 'ETH'
                                                }"
                                            ></div>
                                            {{ case_.crypto }}
                                        </div>
                                    </td>
                                    <td class="py-4">
                                        <span class="text-sm font-semibold text-gray-900 dark:text-white">{{ case_.amount }}</span>
                                    </td>
                                    <td class="py-4">
                                        <span 
                                            class="inline-flex px-3 py-1 text-xs font-bold rounded-full"
                                            :class="{
                                                'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300': case_.riskLevel === 'High',
                                                'bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-300': case_.riskLevel === 'Medium',
                                                'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300': case_.riskLevel === 'Low'
                                            }"
                                        >
                                            {{ case_.riskLevel }}
                                        </span>
                                    </td>
                                    <td class="py-4">
                                        <span 
                                            class="inline-flex px-3 py-1 text-xs font-bold rounded-full"
                                            :class="{
                                                'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300': case_.status === 'Under Review' || case_.status === 'Pending',
                                                'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300': case_.status === 'Resolved',
                                                'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300': case_.status === 'Investigating'
                                            }"
                                        >
                                            {{ case_.status }}
                                        </span>
                                    </td>
                                    <td class="py-4">
                                        <span class="text-sm text-gray-600 dark:text-gray-300">{{ case_.date }}</span>
                                    </td>
                                    <td class="py-4">
                                        <div class="flex items-center gap-2">
                                            <button class="p-1 text-blue-600 dark:text-blue-400 hover:bg-blue-100 dark:hover:bg-blue-900/30 rounded-md transition-colors">
                                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                                                </svg>
                                            </button>
                                            <button class="p-1 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md transition-colors">
                                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z"></path>
                                                </svg>
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Regulatory Updates & News -->
            <div class="col-span-12 xl:col-span-4">
                <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 p-6">
                    <div class="flex items-center gap-3 mb-6">
                        <div class="p-2 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-lg">
                            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
                            </svg>
                        </div>
                        <h3 class="text-lg font-bold text-gray-900 dark:text-white">Crypto Regulatory Updates</h3>
                    </div>
                    
                    <div class="space-y-4">
                        <div class="relative pl-6 pb-4 border-l-2 border-blue-200 dark:border-blue-800">
                            <div class="absolute -left-2 top-0 w-4 h-4 bg-blue-500 rounded-full border-2 border-white dark:border-gray-800"></div>
                            <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800/30">
                                <div class="flex items-start justify-between mb-2">
                                    <h4 class="text-sm font-bold text-blue-900 dark:text-blue-100">New FATF Crypto Guidelines</h4>
                                    <span class="inline-flex px-2 py-1 text-xs font-bold bg-blue-100 dark:bg-blue-900/50 text-blue-800 dark:text-blue-300 rounded-full">New</span>
                                </div>
                                <p class="text-xs text-blue-700 dark:text-blue-300 mb-2">Enhanced requirements for virtual asset service providers and DeFi protocols</p>
                                <span class="text-xs text-blue-600 dark:text-blue-400 font-medium">2 hours ago</span>
                            </div>
                        </div>
                        
                        <div class="relative pl-6 pb-4 border-l-2 border-orange-200 dark:border-orange-800">
                            <div class="absolute -left-2 top-0 w-4 h-4 bg-orange-500 rounded-full border-2 border-white dark:border-gray-800"></div>
                            <div class="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4 border border-orange-200 dark:border-orange-800/30">
                                <div class="flex items-start justify-between mb-2">
                                    <h4 class="text-sm font-bold text-orange-900 dark:text-orange-100">FinCEN Crypto Advisory</h4>
                                    <span class="inline-flex px-2 py-1 text-xs font-bold bg-orange-100 dark:bg-orange-900/50 text-orange-800 dark:text-orange-300 rounded-full">Important</span>
                                </div>
                                <p class="text-xs text-orange-700 dark:text-orange-300 mb-2">Updated guidance on cryptocurrency mixing and privacy coins</p>
                                <span class="text-xs text-orange-600 dark:text-orange-400 font-medium">1 day ago</span>
                            </div>
                        </div>
                        
                        <div class="relative pl-6 pb-4 border-l-2 border-green-200 dark:border-green-800">
                            <div class="absolute -left-2 top-0 w-4 h-4 bg-green-500 rounded-full border-2 border-white dark:border-gray-800"></div>
                            <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4 border border-green-200 dark:border-green-800/30">
                                <div class="flex items-start justify-between mb-2">
                                    <h4 class="text-sm font-bold text-green-900 dark:text-green-100">EU MiCA Regulation</h4>
                                    <span class="inline-flex px-2 py-1 text-xs font-bold bg-green-100 dark:bg-green-900/50 text-green-800 dark:text-green-300 rounded-full">Reviewed</span>
                                </div>
                                <p class="text-xs text-green-700 dark:text-green-300 mb-2">Markets in Crypto-Assets regulation implementation timeline</p>
                                <span class="text-xs text-green-600 dark:text-green-400 font-medium">3 days ago</span>
                            </div>
                        </div>
                        
                        <div class="relative pl-6 border-l-2 border-purple-200 dark:border-purple-800">
                            <div class="absolute -left-2 top-0 w-4 h-4 bg-purple-500 rounded-full border-2 border-white dark:border-gray-800"></div>
                            <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4 border border-purple-200 dark:border-purple-800/30">
                                <div class="flex items-start justify-between mb-2">
                                    <h4 class="text-sm font-bold text-purple-900 dark:text-purple-100">CFTC Digital Assets</h4>
                                                                        <span class="inline-flex px-2 py-1 text-xs font-bold bg-purple-100 dark:bg-purple-900/50 text-purple-800 dark:text-purple-300 rounded-full">Update</span>
                                </div>
                                <p class="text-xs text-purple-700 dark:text-purple-300 mb-2">New enforcement actions against unregistered crypto derivatives</p>
                                <span class="text-xs text-purple-600 dark:text-purple-400 font-medium">1 week ago</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
                        <button class="w-full text-sm text-emerald-600 dark:text-emerald-400 hover:text-emerald-800 dark:hover:text-emerald-300 font-bold text-center py-2 hover:bg-emerald-50 dark:hover:bg-emerald-900/20 rounded-lg transition-colors">
                            View All Regulatory Updates
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Quick Actions Floating Panel -->
        <div class="fixed bottom-6 right-6 z-50">
            <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700 p-6 backdrop-blur-sm">
                <div class="flex items-center gap-2 mb-4">
                    <div class="p-1 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg">
                        <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                        </svg>
                    </div>
                    <h3 class="text-sm font-bold text-gray-900 dark:text-white">Quick Actions</h3>
                </div>
                
                <div class="space-y-2">
                    <button 
                        @click="exportReport"
                        class="w-full text-left px-4 py-3 text-sm text-blue-700 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-xl transition-colors flex items-center gap-3 group"
                    >
                        <div class="p-1 bg-blue-100 dark:bg-blue-900/30 rounded-lg group-hover:bg-blue-200 dark:group-hover:bg-blue-900/50 transition-colors">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                            </svg>
                        </div>
                        <div>
                            <p class="font-semibold">Generate AML Report</p>
                            <p class="text-xs text-gray-500 dark:text-gray-400">Export compliance data</p>
                        </div>
                    </button>
                    
                    <button class="w-full text-left px-4 py-3 text-sm text-orange-700 dark:text-orange-400 hover:bg-orange-50 dark:hover:bg-orange-900/20 rounded-xl transition-colors flex items-center gap-3 group">
                        <div class="p-1 bg-orange-100 dark:bg-orange-900/30 rounded-lg group-hover:bg-orange-200 dark:group-hover:bg-orange-900/50 transition-colors">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                            </svg>
                        </div>
                        <div>
                            <p class="font-semibold">Create Alert Rule</p>
                            <p class="text-xs text-gray-500 dark:text-gray-400">Set up monitoring rules</p>
                        </div>
                    </button>
                    
                    <button class="w-full text-left px-4 py-3 text-sm text-green-700 dark:text-green-400 hover:bg-green-50 dark:hover:bg-green-900/20 rounded-xl transition-colors flex items-center gap-3 group">
                        <div class="p-1 bg-green-100 dark:bg-green-900/30 rounded-lg group-hover:bg-green-200 dark:group-hover:bg-green-900/50 transition-colors">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                            </svg>
                        </div>
                        <div>
                            <p class="font-semibold">Address Lookup</p>
                            <p class="text-xs text-gray-500 dark:text-gray-400">Search crypto addresses</p>
                        </div>
                    </button>
                    
                    <button class="w-full text-left px-4 py-3 text-sm text-purple-700 dark:text-purple-400 hover:bg-purple-50 dark:hover:bg-purple-900/20 rounded-xl transition-colors flex items-center gap-3 group">
                        <div class="p-1 bg-purple-100 dark:bg-purple-900/30 rounded-lg group-hover:bg-purple-200 dark:group-hover:bg-purple-900/50 transition-colors">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                            </svg>
                        </div>
                        <div>
                            <p class="font-semibold">Live Monitor</p>
                            <p class="text-xs text-gray-500 dark:text-gray-400">Real-time tracking</p>
                        </div>
                    </button>
                </div>
            </div>
        </div>

        <!-- Dark Mode Toggle -->
        <div class="fixed top-6 right-6 z-40">
            <button 
                @click="toggleDarkMode" 
                class="p-3 bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-all duration-200 group"
            >
                <svg class="w-5 h-5 text-gray-600 dark:text-gray-300 hidden dark:block group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"></path>
                </svg>
                <svg class="w-5 h-5 text-gray-600 dark:text-gray-300 block dark:hidden group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path>
                </svg>
            </button>
        </div>

        <!-- Loading Overlay -->
        <div v-if="isLoading" class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center">
            <div class="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-2xl border border-gray-200 dark:border-gray-700">
                <div class="flex items-center gap-4">
                    <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                    <div>
                        <h3 class="text-lg font-bold text-gray-900 dark:text-white">Updating AML Data</h3>
                        <p class="text-sm text-gray-600 dark:text-gray-300">Fetching latest cryptocurrency compliance information...</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

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

/* Smooth animations */
.grid > * {
    animation: fadeInUp 0.6s ease-out;
}

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

/* Professional card hover effects */
.dashboard-card {
    transition: all 0.3s ease;
}

.dashboard-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

/* Gradient text animation */
@keyframes gradient {
    0% {
        background-position: 0% 50%;
    }
    50% {
        background-position: 100% 50%;
    }
    100% {
        background-position: 0% 50%;
    }
}

.animate-gradient {
    background-size: 200% 200%;
    animation: gradient 3s ease infinite;
}

/* Pulse animation for critical elements */
@keyframes pulse-glow {
    0%, 100% {
        box-shadow: 0 0 5px rgba(239, 68, 68, 0.5);
    }
    50% {
        box-shadow: 0 0 20px rgba(239, 68, 68, 0.8);
    }
}

.pulse-glow {
    animation: pulse-glow 2s ease-in-out infinite;
}

/* Table row hover effects */
tbody tr {
    transition: all 0.2s ease;
}

tbody tr:hover {
    transform: translateX(4px);
}

/* Button hover animations */
button {
    transition: all 0.2s ease;
}

button:hover {
    transform: translateY(-1px);
}

/* Loading animation */
@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

.animate-spin {
    animation: spin 1s linear infinite;
}

/* Backdrop blur support */
.backdrop-blur-sm {
    backdrop-filter: blur(4px);
}

/* Custom focus styles */
button:focus {
    outline: 2px solid #3b82f6;
    outline-offset: 2px;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .fixed.bottom-6.right-6 {
        bottom: 1rem;
        right: 1rem;
    }
    
    .fixed.top-6.right-6 {
        top: 1rem;
        right: 1rem;
    }
}

/* Chart container styling */
canvas {
    max-width: 100%;
    height: auto;
}

/* Enhanced hover effects for metric cards */
.metric-card {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.metric-card:hover {
    transform: translateY(-4px) scale(1.02);
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

/* Animated progress bars */
.progress-bar {
    transition: width 1s ease-in-out;
}

/* Floating animation for action buttons */
@keyframes float {
    0%, 100% {
        transform: translateY(0px);
    }
    50% {
        transform: translateY(-10px);
    }
}

.float-animation {
    animation: float 3s ease-in-out infinite;
}

/* Glow effect for critical alerts */
@keyframes glow {
    0%, 100% {
        box-shadow: 0 0 5px rgba(239, 68, 68, 0.3);
    }
    50% {
        box-shadow: 0 0 20px rgba(239, 68, 68, 0.6), 0 0 30px rgba(239, 68, 68, 0.4);
    }
}

.glow-red {
    animation: glow 2s ease-in-out infinite;
}

/* Shimmer loading effect */
@keyframes shimmer {
    0% {
        background-position: -200px 0;
    }
    100% {
        background-position: calc(200px + 100%) 0;
    }
}

.shimmer {
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200px 100%;
    animation: shimmer 1.5s infinite;
}

.dark .shimmer {
    background: linear-gradient(90deg, #374151 25%, #4b5563 50%, #374151 75%);
    background-size: 200px 100%;
}

/* Typewriter effect for titles */
@keyframes typewriter {
    from {
        width: 0;
    }
    to {
        width: 100%;
    }
}

.typewriter {
    overflow: hidden;
    border-right: 2px solid;
    white-space: nowrap;
    animation: typewriter 2s steps(40, end), blink-caret 0.75s step-end infinite;
}

@keyframes blink-caret {
    from, to {
        border-color: transparent;
    }
    50% {
        border-color: currentColor;
    }
}

/* Slide in animations */
@keyframes slideInLeft {
    from {
        transform: translateX(-100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

@keyframes slideInRight {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

.slide-in-left {
    animation: slideInLeft 0.6s ease-out;
}

.slide-in-right {
    animation: slideInRight 0.6s ease-out;
}

/* Bounce animation for notifications */
@keyframes bounce {
    0%, 20%, 53%, 80%, 100% {
        transform: translate3d(0, 0, 0);
    }
    40%, 43% {
        transform: translate3d(0, -30px, 0);
    }
    70% {
        transform: translate3d(0, -15px, 0);
    }
    90% {
        transform: translate3d(0, -4px, 0);
    }
}

.bounce {
    animation: bounce 1s ease-in-out;
}

/* Pulse animation for live indicators */
@keyframes pulse-dot {
    0% {
        transform: scale(0.95);
        box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7);
    }
    70% {
        transform: scale(1);
        box-shadow: 0 0 0 10px rgba(34, 197, 94, 0);
    }
    100% {
        transform: scale(0.95);
        box-shadow: 0 0 0 0 rgba(34, 197, 94, 0);
    }
}

.pulse-dot {
    animation: pulse-dot 2s infinite;
}

/* Gradient border animation */
@keyframes gradient-border {
    0%, 100% {
        background-position: 0% 50%;
    }
    50% {
        background-position: 100% 50%;
    }
}

.gradient-border {
    background: linear-gradient(45deg, #3b82f6, #8b5cf6, #ef4444, #10b981);
    background-size: 400% 400%;
    animation: gradient-border 3s ease infinite;
    padding: 2px;
    border-radius: 12px;
}

.gradient-border-content {
    background: white;
    border-radius: 10px;
    padding: 1rem;
}

.dark .gradient-border-content {
    background: #1f2937;
}

/* Stagger animation for list items */
.stagger-item {
    opacity: 0;
    transform: translateY(20px);
    animation: staggerFadeIn 0.6s ease-out forwards;
}

.stagger-item:nth-child(1) { animation-delay: 0.1s; }
.stagger-item:nth-child(2) { animation-delay: 0.2s; }
.stagger-item:nth-child(3) { animation-delay: 0.3s; }
.stagger-item:nth-child(4) { animation-delay: 0.4s; }
.stagger-item:nth-child(5) { animation-delay: 0.5s; }

@keyframes staggerFadeIn {
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Smooth transitions for theme switching */
* {
    transition: background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease;
}

/* Enhanced focus states for accessibility */
.focus-visible:focus {
    outline: 2px solid #3b82f6;
    outline-offset: 2px;
    border-radius: 4px;
}

/* Print styles */
@media print {
    .fixed {
        display: none !important;
    }
    
    .no-print {
        display: none !important;
    }
    
    .print-break {
        page-break-before: always;
    }
}

/* High contrast mode support */
@media (prefers-contrast: high) {
    .bg-gradient-to-br {
        background: white;
    }
    
    .dark .bg-gradient-to-br {
        background: black;
    }
    
    .border {
        border-width: 2px;
    }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}

/* Custom utility classes */
.text-shadow {
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.backdrop-filter {
    backdrop-filter: blur(10px) saturate(180%);
}

.glass-morphism {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.dark .glass-morphism {
    background: rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.1);
}

/* Scrollbar styling for different browsers */
.custom-scrollbar {
    scrollbar-width: thin;
    scrollbar-color: #cbd5e1 #f1f5f9;
}

.dark .custom-scrollbar {
    scrollbar-color: #6b7280 #374151;
}

/* Loading skeleton styles */
.skeleton {
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200px 100%;
    animation: shimmer 1.5s infinite;
}

.dark .skeleton {
    background: linear-gradient(90deg, #374151 25%, #4b5563 50%, #374151 75%);
    background-size: 200px 100%;
}

/* Tooltip styles */
.tooltip {
    position: relative;
}

.tooltip::before {
    content: attr(data-tooltip);
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
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.3s ease;
    z-index: 1000;
}

.tooltip:hover::before {
    opacity: 1;
}

/* Enhanced button styles */
.btn-primary {
    background: linear-gradient(135deg, #3b82f6, #1d4ed8);
    border: none;
    color: white;
    padding: 0.75rem 1.5rem;
    border-radius: 0.5rem;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.btn-primary:hover {
    background: linear-gradient(135deg, #1d4ed8, #1e40af);
    transform: translateY(-2px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

.btn-primary:active {
    transform: translateY(0);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

/* Card elevation levels */
.elevation-1 {
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24);
}

.elevation-2 {
    box-shadow: 0 3px 6px rgba(0, 0, 0, 0.16), 0 3px 6px rgba(0, 0, 0, 0.23);
}

.elevation-3 {
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.19), 0 6px 6px rgba(0, 0, 0, 0.23);
}

.elevation-4 {
    box-shadow: 0 14px 28px rgba(0, 0, 0, 0.25), 0 10px 10px rgba(0, 0, 0, 0.22);
}

.elevation-5 {
    box-shadow: 0 19px 38px rgba(0, 0, 0, 0.30), 0 15px 12px rgba(0, 0, 0, 0.22);
}
</style>
