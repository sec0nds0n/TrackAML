<script setup>
import { ref, onMounted, computed, onBeforeUnmount } from 'vue';
import { getAnomalySummary } from '@/services/StatsService';

const total = ref(0);
const eth = ref(0);
const btc = ref(0);
const deltaPct = ref(null);   // ex: 0.12 untuk +12%
const direction = ref('flat'); // 'up' | 'down' | 'flat'
const loading = ref(false);
const error = ref('');
const lastUpdated = ref(new Date().toLocaleString());

const deltaText = computed(() => {
  if (deltaPct.value === null) return '— from yesterday';
  const pct = Math.round(Math.abs(deltaPct.value) * 100);
  return `${direction.value === 'down' ? '−' : '+'}${pct}% from yesterday`;
});
const deltaClass = computed(() => {
  if (deltaPct.value === null) return 'text-gray-500 dark:text-gray-400';
  return direction.value === 'up'
    ? 'text-red-600 dark:text-red-400'
    : 'text-green-600 dark:text-green-400';
});

let timer;

async function loadSummary() {
  loading.value = true;
  try {
    const s = await getAnomalySummary();
    total.value = s.total ?? 0;
    eth.value = s?.by_chain?.ETH ?? 0;
    btc.value = s?.by_chain?.BTC ?? 0;
    deltaPct.value = s?.delta_pct ?? null;
    direction.value = s?.direction ?? 'flat';
    lastUpdated.value = new Date().toLocaleString();
  } catch (e) {
    error.value = e.message || 'Failed to load';
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadSummary();
  // opsional: auto-refresh tiap 30 detik
  timer = setInterval(loadSummary, 30000);
});
onBeforeUnmount(() => { if (timer) clearInterval(timer); });
</script>

<template>
    <div class="min-h-screen bg-gray-50 dark:bg-gray-900 p-6 transition-colors duration-200">
        <!-- Header Section -->
        <div class="mb-8">
            <div class="flex items-center justify-between">
                <div>
                    <h1 class="text-3xl font-bold text-gray-900 dark:text-white">AML Compliance Dashboard</h1>
                    <p class="text-gray-600 dark:text-gray-300 mt-1">Monitor anti-money laundering activities and compliance status</p>
                </div>
                <div class="flex items-center space-x-4">
                    <div class="bg-white dark:bg-gray-800 px-4 py-2 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
                        <span class="text-sm font-medium text-gray-900 dark:text-white ml-1">{{ lastUpdated }}</span>
                        <span class="text-sm font-medium text-gray-900 dark:text-white ml-1">{{ new Date().toLocaleString() }}</span>
                    </div>
                    <div class="flex items-center space-x-2">
                        <div class="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                        <span class="text-sm font-medium text-green-700 dark:text-green-400">System Active</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- AML Key Metrics -->
        <div class="mb-8">
            <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                <div class="flex items-center justify-between mb-6">
                    <h2 class="text-xl font-semibold text-gray-900 dark:text-white">AML Key Metrics</h2>
                    <div class="flex items-center space-x-2">
                        <select class="text-sm border border-gray-300 dark:border-gray-600 rounded-md px-3 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                            <option>Last 24 Hours</option>
                            <option>Last 7 Days</option>
                            <option>Last 30 Days</option>
                        </select>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <!-- Suspicious Transactions -->
                    <div class="bg-gradient-to-br from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/20 rounded-lg p-4 border border-red-200 dark:border-red-800/30">
                        <div class="flex items-center justify-between">
                            <div>
                            <p class="text-red-600 dark:text-red-400 text-sm font-medium">Suspicious Transactions</p>
                            <p class="text-2xl font-bold text-red-900 dark:text-red-100 mt-1">
                                <span v-if="!loading">{{ total }}</span>
                                <span v-else>…</span>
                            </p>

                            <!-- BTC / ETH badges -->
                            <div class="flex items-center gap-3 mt-2 text-xs">
                                <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-white/70 dark:bg-red-900/30 border border-red-200/70 dark:border-red-800/40">
                                <span class="w-2 h-2 rounded-full bg-orange-500"></span> WEW: {{ btc }}
                                </span>
                                <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-white/70 dark:bg-red-900/30 border border-red-200/70 dark:border-red-800/40">
                                <span class="w-2 h-2 rounded-full bg-blue-500"></span> ETH: {{ eth }}
                                </span>
                            </div>

                            <!-- Delta vs yesterday -->
                            <div class="flex items-center mt-2" v-if="deltaPct !== null">
                                <svg v-if="direction==='up'" class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M5.293 7.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L6.707 7.707a1 1 0 01-1.414 0z" clip-rule="evenodd"/>
                                </svg>
                                <svg v-else class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M14.707 12.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 14.586V3a1 1 0 012 0v11.586l2.293-2.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                                </svg>
                                <span :class="deltaClass">{{ deltaText }}</span>
                            </div>
                            <div v-else class="mt-2 text-xs text-gray-500 dark:text-gray-400">— from yesterday</div>
                            </div>

                            <div class="bg-red-200 dark:bg-red-800/50 p-3 rounded-full">
                            <svg class="w-6 h-6 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"/>
                            </svg>
                            </div>
                        </div>
                        </div>

                    <!-- Compliance Score -->
                    <div class="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 rounded-lg p-4 border border-green-200 dark:border-green-800/30">
                        <div class="flex items-center justify-between">
                            <div>
                                <p class="text-green-600 dark:text-green-400 text-sm font-medium">Compliance Score</p>
                                <p class="text-2xl font-bold text-green-900 dark:text-green-100 mt-1">94.2%</p>
                                <div class="flex items-center mt-2">
                                    <svg class="w-4 h-4 text-green-500 dark:text-green-400 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                        <path fill-rule="evenodd" d="M5.293 7.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L6.707 7.707a1 1 0 01-1.414 0z" clip-rule="evenodd"></path>
                                    </svg>
                                    <span class="text-green-600 dark:text-green-400 text-xs font-medium">+2.1% from last week</span>
                                </div>
                            </div>
                            <div class="bg-green-200 dark:bg-green-800/50 p-3 rounded-full">
                                <svg class="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                </svg>
                            </div>
                        </div>
                    </div>

                    <!-- Active Cases -->
                    <div class="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800/30">
                        <div class="flex items-center justify-between">
                            <div>
                                <p class="text-blue-600 dark:text-blue-400 text-sm font-medium">Active Cases</p>
                                <p class="text-2xl font-bold text-blue-900 dark:text-blue-100 mt-1">156</p>
                                <div class="flex items-center mt-2">
                                    <div class="w-4 h-4 bg-blue-500 dark:bg-blue-400 rounded-full mr-1"></div>
                                    <span class="text-blue-600 dark:text-blue-400 text-xs font-medium">23 require attention</span>
                                </div>
                            </div>
                            <div class="bg-blue-200 dark:bg-blue-800/50 p-3 rounded-full">
                                <svg class="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                                </svg>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Main Dashboard Grid -->
        <div class="grid grid-cols-12 gap-6">
            <!-- Alerts Panel -->
            <div class="col-span-12 lg:col-span-8">
                <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-6">
                    <div class="flex items-center justify-between mb-4">
                        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Critical Alerts</h3>
                        <span class="bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300 text-xs font-medium px-2.5 py-0.5 rounded-full">5 Active</span>
                    </div>
                    <div class="space-y-3">
                        <div class="flex items-center p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800/30 rounded-lg">
                            <div class="flex-shrink-0">
                                <div class="w-2 h-2 bg-red-500 dark:bg-red-400 rounded-full"></div>
                            </div>
                            <div class="ml-3 flex-1">
                                <p class="text-sm font-medium text-red-900 dark:text-red-100">High-value transaction pattern detected</p>
                                <p class="text-xs text-red-700 dark:text-red-300">Customer ID: 78432 - Multiple transactions above $10,000</p>
                            </div>
                            <div class="text-xs text-red-600 dark:text-red-400">2 min ago</div>
                        </div>
                        <div class="flex items-center p-3 bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800/30 rounded-lg">
                            <div class="flex-shrink-0">
                                <div class="w-2 h-2 bg-orange-500 dark:bg-orange-400 rounded-full"></div>
                            </div>
                            <div class="ml-3 flex-1">
                                <p class="text-sm font-medium text-orange-900 dark:text-orange-100">Unusual geographic activity</p>
                                <p class="text-xs text-orange-700 dark:text-orange-300">Account accessed from high-risk jurisdiction</p>
                            </div>
                            <div class="text-xs text-orange-600 dark:text-orange-400">15 min ago</div>
                        </div>
                        <div class="flex items-center p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800/30 rounded-lg">
                            <div class="flex-shrink-0">
                                <div class="w-2 h-2 bg-yellow-500 dark:bg-yellow-400 rounded-full"></div>
                            </div>
                            <div class="ml-3 flex-1">
                                <p class="text-sm font-medium text-yellow-900 dark:text-yellow-100">Structuring pattern identified</p>
                                <p class="text-xs text-yellow-700 dark:text-yellow-300">Multiple deposits just below reporting threshold</p>
                            </div>
                            <div class="text-xs text-yellow-600 dark:text-yellow-400">1 hour ago</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Compliance Status -->
            <div class="col-span-12 lg:col-span-4">
                <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-6">
                    <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Compliance Status</h3>
                    <div class="space-y-4">
                        <div class="flex items-center justify-between">
                            <span class="text-sm text-gray-600 dark:text-gray-300">KYC Verification</span>
                            <div class="flex items-center">
                                <div class="w-16 bg-gray-200 dark:bg-gray-700 rounded-full h-2 mr-2">
                                    <div class="bg-green-500 dark:bg-green-400 h-2 rounded-full" style="width: 92%"></div>
                                </div>
                                <span class="text-sm font-medium text-green-600 dark:text-green-400">92%</span>
                            </div>
                        </div>
                        <div class="flex items-center justify-between">
                            <span class="text-sm text-gray-600 dark:text-gray-300">Transaction Monitoring</span>
                            <div class="flex items-center">
                                <div class="w-16 bg-gray-200 dark:bg-gray-700 rounded-full h-2 mr-2">
                                    <div class="bg-green-500 dark:bg-green-400 h-2 rounded-full" style="width: 98%"></div>
                                </div>
                                <span class="text-sm font-medium text-green-600 dark:text-green-400">98%</span>
                            </div>
                        </div>
                        <div class="flex items-center justify-between">
                            <span class="text-sm text-gray-600 dark:text-gray-300">Risk Assessment</span>
                            <div class="flex items-center">
                                <div class="w-16 bg-gray-200 dark:bg-gray-700 rounded-full h-2 mr-2">
                                    <div class="bg-yellow-500 dark:bg-yellow-400 h-2 rounded-full" style="width: 76%"></div>
                                </div>
                                <span class="text-sm font-medium text-yellow-600 dark:text-yellow-400">76%</span>
                            </div>
                        </div>
                        <div class="flex items-center justify-between">
                            <span class="text-sm text-gray-600 dark:text-gray-300">Regulatory Reporting</span>
                            <div class="flex items-center">
                                <div class="w-16 bg-gray-200 dark:bg-gray-700 rounded-full h-2 mr-2">
                                    <div class="bg-green-500 dark:bg-green-400 h-2 rounded-full" style="width: 89%"></div>
                                </div>
                                <span class="text-sm font-medium text-green-600 dark:text-green-400">89%</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Transaction Analysis -->
            <div class="col-span-12 xl:col-span-8">
                <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-6">
                    <div class="flex items-center justify-between mb-4">
                        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Suspicious Transaction Trends</h3>
                        <div class="flex space-x-2">
                            <button class="px-3 py-1 text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-full">Daily</button>
                            <button class="px-3 py-1 text-xs font-medium text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full">Weekly</button>
                            <button class="px-3 py-1 text-xs font-medium text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full">Monthly</button>
                        </div>
                    </div>
                    <div class="h-64 bg-gray-50 dark:bg-gray-700/50 rounded-lg flex items-center justify-center">
                        <div class="text-center">
                            <svg class="w-12 h-12 text-gray-400 dark:text-gray-500 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                            </svg>
                            <p class="text-gray-500 dark:text-gray-400 text-sm">Chart visualization will be displayed here</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Risk Assessment -->
            <div class="col-span-12 xl:col-span-4">
                <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-6">
                    <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Risk Distribution</h3>
                    <div class="space-y-4">
                        <div class="flex items-center justify-between">
                            <div class="flex items-center">
                                <div class="w-3 h-3 bg-red-500 dark:bg-red-400 rounded-full mr-2"></div>
                                <span class="text-sm text-gray-600 dark:text-gray-300">High Risk</span>
                            </div>
                            <span class="text-sm font-medium text-gray-900 dark:text-white">23%</span>
                        </div>
                        <div class="flex items-center justify-between">
                            <div class="flex items-center">
                                <div class="w-3 h-3 bg-yellow-500 dark:bg-yellow-400 rounded-full mr-2"></div>
                                <span class="text-sm text-gray-600 dark:text-gray-300">Medium Risk</span>
                            </div>
                            <span class="text-sm font-medium text-gray-900 dark:text-white">45%</span>
                        </div>
                        <div class="flex items-center justify-between">
                            <div class="flex items-center">
                                <div class="w-3 h-3 bg-green-500 dark:bg-green-400 rounded-full mr-2"></div>
                                <span class="text-sm text-gray-600 dark:text-gray-300">Low Risk</span>
                            </div>
                            <span class="text-sm font-medium text-gray-900 dark:text-white">32%</span>
                        </div>
                    </div>
                    <div class="mt-6">
                        <div class="h-32 bg-gray-50 dark:bg-gray-700/50 rounded-lg flex items-center justify-center">
                            <div class="text-center">
                                <svg class="w-8 h-8 text-gray-400 dark:text-gray-500 mx-auto mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"></path>
                                </svg>
                                <p class="text-gray-500 dark:text-gray-400 text-xs">Risk chart</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Recent Cases -->
            <div class="col-span-12 lg:col-span-8">
                <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                    <div class="flex items-center justify-between mb-4">
                        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Recent AML Cases</h3>
                        <button class="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 font-medium">View All</button>
                    </div>
                    <div class="overflow-x-auto">
                        <table class="w-full">
                            <thead>
                                <tr class="border-b border-gray-200 dark:border-gray-700">
                                    <th class="text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider py-3">Case ID</th>
                                    <th class="text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider py-3">Customer</th>
                                    <th class="text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider py-3">Risk Level</th>
                                    <th class="text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider py-3">Status</th>
                                    <th class="text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider py-3">Date</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
                                <tr>
                                    <td class="py-3 text-sm font-medium text-gray-900 dark:text-white">AML-2024-001</td>
                                    <td class="py-3 text-sm text-gray-600 dark:text-gray-300">John Smith</td>
                                    <td class="py-3">
                                        <span class="inline-flex px-2 py-1 text-xs font-medium bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300 rounded-full">High</span>
                                    </td>
                                    <td class="py-3">
                                        <span class="inline-flex px-2 py-1 text-xs font-medium bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300 rounded-full">Under Review</span>
                                    </td>
                                    <td class="py-3 text-sm text-gray-600 dark:text-gray-300">2024-01-15</td>
                                </tr>
                                <tr>
                                    <td class="py-3 text-sm font-medium text-gray-900 dark:text-white">AML-2024-002</td>
                                    <td class="py-3 text-sm text-gray-600 dark:text-gray-300">ABC Corp</td>
                                    <td class="py-3">
                                        <span class="inline-flex px-2 py-1 text-xs font-medium bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-300 rounded-full">Medium</span>
                                    </td>
                                    <td class="py-3">
                                        <span class="inline-flex px-2 py-1 text-xs font-medium bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300 rounded-full">Resolved</span>
                                    </td>
                                    <td class="py-3 text-sm text-gray-600 dark:text-gray-300">2024-01-14</td>
                                </tr>
                                <tr>
                                    <td class="py-3 text-sm font-medium text-gray-900 dark:text-white">AML-2024-003</td>
                                    <td class="py-3 text-sm text-gray-600 dark:text-gray-300">Maria Garcia</td>
                                    <td class="py-3">
                                        <span class="inline-flex px-2 py-1 text-xs font-medium bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300 rounded-full">High</span>
                                    </td>
                                    <td class="py-3">
                                        <span class="inline-flex px-2 py-1 text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 rounded-full">Investigating</span>
                                    </td>
                                    <td class="py-3 text-sm text-gray-600 dark:text-gray-300">2024-01-13</td>
                                </tr>
                                <tr>
                                    <td class="py-3 text-sm font-medium text-gray-900 dark:text-white">AML-2024-004</td>
                                    <td class="py-3 text-sm text-gray-600 dark:text-gray-300">XYZ Holdings</td>
                                    <td class="py-3">
                                        <span class="inline-flex px-2 py-1 text-xs font-medium bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-300 rounded-full">Medium</span>
                                    </td>
                                    <td class="py-3">
                                        <span class="inline-flex px-2 py-1 text-xs font-medium bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300 rounded-full">Pending</span>
                                    </td>
                                    <td class="py-3 text-sm text-gray-600 dark:text-gray-300">2024-01-12</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Regulatory Updates -->
            <div class="col-span-12 lg:col-span-4">
                <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                    <div class="flex items-center justify-between mb-4">
                        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Regulatory Updates</h3>
                        <svg class="w-5 h-5 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
                        </svg>
                    </div>
                    <div class="space-y-4">
                        <div class="border-l-4 border-blue-500 dark:border-blue-400 pl-4">
                            <div class="flex items-start justify-between">
                                <div class="flex-1">
                                    <h4 class="text-sm font-medium text-gray-900 dark:text-white">New FATF Guidelines</h4>
                                    <p class="text-xs text-gray-600 dark:text-gray-300 mt-1">Updated requirements for virtual asset service providers</p>
                                    <span class="text-xs text-blue-600 dark:text-blue-400 font-medium">2 days ago</span>
                                </div>
                                <span class="inline-flex px-2 py-1 text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 rounded-full">New</span>
                            </div>
                        </div>
                        <div class="border-l-4 border-orange-500 dark:border-orange-400 pl-4">
                            <div class="flex items-start justify-between">
                                <div class="flex-1">
                                    <h4 class="text-sm font-medium text-gray-900 dark:text-white">BSA/AML Examination Manual</h4>
                                    <p class="text-xs text-gray-600 dark:text-gray-300 mt-1">Updated procedures for cryptocurrency transactions</p>
                                    <span class="text-xs text-orange-600 dark:text-orange-400 font-medium">1 week ago</span>
                                </div>
                                <span class="inline-flex px-2 py-1 text-xs font-medium bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-300 rounded-full">Important</span>
                            </div>
                        </div>
                        <div class="border-l-4 border-green-500 dark:border-green-400 pl-4">
                            <div class="flex items-start justify-between">
                                <div class="flex-1">
                                    <h4 class="text-sm font-medium text-gray-900 dark:text-white">FinCEN Advisory</h4>
                                    <p class="text-xs text-gray-600 dark:text-gray-300 mt-1">Enhanced due diligence for high-risk jurisdictions</p>
                                    <span class="text-xs text-green-600 dark:text-green-400 font-medium">2 weeks ago</span>
                                </div>
                                <span class="inline-flex px-2 py-1 text-xs font-medium bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300 rounded-full">Reviewed</span>
                            </div>
                        </div>
                    </div>
                    <div class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                        <button class="w-full text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 font-medium text-center">
                            View All Updates
                        </button>
                    </div>
                </div>
            </div>


        </div>

        <!-- Quick Actions Floating Panel -->
        <div class="fixed bottom-6 right-6 z-50">
            <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-4">
                <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-3">Quick Actions</h3>
                <div class="space-y-2">
                    <button class="w-full text-left px-3 py-2 text-sm text-blue-700 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-md transition-colors flex items-center">
                        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                        </svg>
                        Generate Report
                    </button>
                    <button class="w-full text-left px-3 py-2 text-sm text-orange-700 dark:text-orange-400 hover:bg-orange-50 dark:hover:bg-orange-900/20 rounded-md transition-colors flex items-center">
                        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                        </svg>
                        Create Alert
                    </button>
                    <button class="w-full text-left px-3 py-2 text-sm text-green-700 dark:text-green-400 hover:bg-green-50 dark:hover:bg-green-900/20 rounded-md transition-colors flex items-center">
                        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                        </svg>
                        Export Data
                    </button>
                    <button class="w-full text-left px-3 py-2 text-sm text-purple-700 dark:text-purple-400 hover:bg-purple-50 dark:hover:bg-purple-900/20 rounded-md transition-colors flex items-center">
                        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                        </svg>
                        Monitor Live
                    </button>
                </div>
            </div>
        </div>

        <!-- Dark Mode Toggle (Optional) -->
        <div class="fixed top-6 right-6 z-40">
            <button @click="toggleDarkMode" class="p-2 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                <svg class="w-5 h-5 text-gray-600 dark:text-gray-300 hidden dark:block" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"></path>
                </svg>
                <svg class="w-5 h-5 text-gray-600 dark:text-gray-300 block dark:hidden" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path>
                </svg>
            </button>
        </div>
    </div>
</template>

<style scoped>
/* Custom scrollbar for better aesthetics */
::-webkit-scrollbar {
    width: 6px;
}

::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 3px;
}

::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
    background: #a8a8a8;
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
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}
</style>
<script>
export default {
    methods: {
        toggleDarkMode() {
            document.documentElement.classList.toggle('dark');
            const isDark = document.documentElement.classList.contains('dark');
            localStorage.setItem('darkMode', isDark);
        }
    },
    mounted() {
        // Check for saved dark mode preference or default to light mode
        const savedDarkMode = localStorage.getItem('darkMode');
        if (savedDarkMode === 'true' || (!savedDarkMode && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
            document.documentElement.classList.add('dark');
        }
    }
}

</script>
