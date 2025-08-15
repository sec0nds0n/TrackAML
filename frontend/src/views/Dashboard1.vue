<script setup>
import SankeyChart from '@/components/SankeyChart.vue';
import AlertsPanel from '@/components/dashboard/AlertsPanel.vue';
import ComplianceStatus from '@/components/dashboard/ComplianceStatus.vue';
import MetricsCards from '@/components/dashboard/MetricsCards.vue';
import NotificationAlert from '@/components/dashboard/NotificationAlert.vue';
import QuickActionsFAB from '@/components/dashboard/QuickActionsFAB.vue';
import RecentCasesTable from '@/components/dashboard/RecentCasesTable.vue';
import RegulatoryUpdates from '@/components/dashboard/RegulatoryUpdates.vue';
import { useLayout } from '@/layout/composables/layout';
import { useToast } from 'primevue/usetoast';
import { computed, onMounted, onBeforeUnmount, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { 
  getAnomalySummary, 
  getHighRiskCount, 
  getActiveCasesCount, 
  getUrgentCasesCount, 
  getComplianceScore, 
  getWalletRiskDistribution, 
  getAlerts, 
  getRecentCases
} from '@/services/StatsService';

const { isDarkTheme } = useLayout()

watch(isDarkTheme, () => {
  const isDark = !!isDarkTheme.value;
  localStorage.setItem('darkMode', String(isDark));
  document.documentElement.classList.toggle('dark', isDark);
});

const toast = useToast()
const router = useRouter()

// Reactive data
const selectedTimeframe = ref('24h')
const isLoading = ref(false)
const lastUpdate = ref(new Date())
const showQuickActions = ref(false) 

// Mock data for crypto AML tracking
const cryptoMetrics = ref({
  suspiciousTransactions: { count: 0, change: 0, trend: 'flat', btc: 0, eth: 0 },
  highRiskAddresses:     { count: 0, change: 0, trend: 'flat', btc: 0, eth: 0 },
  complianceScore:       { score: 0, change: 0, trend: 'flat' },
  activeCases:           { count: 0, urgent: 0, btc: 0, eth: 0 }
});
const riskDistribution = ref({
  total: 0,
  critical: 0,
  high: 0,
  medium: 0,
  pct: { critical: 0, high: 0, medium: 0 }
})

const alerts = ref([])
const recentCases = ref([])

// Alert management methods
const dismissAlert = (alertId) => {
  const index = alerts.value.findIndex(alert => alert.id === alertId);
  if (index !== -1) {
    alerts.value.splice(index, 1);
    toast.add({
      severity: 'success',
      summary: 'Alert Dismissed',
      detail: 'Security alert has been dismissed successfully',
      life: 3000
    });
  }
}

const clearAllAlerts = () => {
  const alertCount = alerts.value.length;
  alerts.value = [];
  toast.add({
    severity: 'info',
    summary: 'All Alerts Cleared',
    detail: `${alertCount} alerts have been cleared`,
    life: 3000
  });
}

const markAllAsRead = () => {
  const unreadCount = alerts.value.filter(alert => !alert.read).length;
  alerts.value.forEach(alert => {
    alert.read = true;
  });
  toast.add({
    severity: 'success',
    summary: 'Alerts Marked as Read',
    detail: `${unreadCount} alerts marked as read`,
    life: 3000
  });
}

// Methods
const toggleQuickActions = () => {
  showQuickActions.value = !showQuickActions.value
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
  loadAlerts(50)
}

const navigateTo = (route) => {
  router.push(route)
  showQuickActions.value = false
}

const exportReport = () => {
  toast.add({
    severity: 'info',
    summary: 'Export Started',
    detail: 'Generating AML compliance report...',
    life: 3000
  })
  showQuickActions.value = false
}

const updateTimeframe = (value) => {
  selectedTimeframe.value = value
}

// Computed properties
const totalCryptoVolume = computed(() => {
  return {
    btc: cryptoMetrics.value.activeCases.btc + cryptoMetrics.value.suspiciousTransactions.btc,
    eth: cryptoMetrics.value.activeCases.eth + cryptoMetrics.value.suspiciousTransactions.eth
  }
})

const alertStats = computed(() => {
  return {
    total: alerts.value.length,
    critical: alerts.value.filter(a => a.type === 'critical').length,
    high: alerts.value.filter(a => a.type === 'high').length,
    medium: alerts.value.filter(a => a.type === 'medium').length,
    unread: alerts.value.filter(a => !a.read).length
  }
})

let timeInterval, statsTimer;
let prevHighRisk = null;

function shortRef(ref) {
  if (!ref) return '—'
  const s = String(ref)
  return s.length > 12 ? `${s.slice(0,6)}...${s.slice(-4)}` : s
}

function humanStatus(s) {
  if (!s) return '—'
  // DB default: 'Under Review', di UI screenshot: 'In Review'
  if (s === 'Under Review') return 'In Review'
  return s
}

function toTitle(x) {
  if (!x) return 'High'
  return x.charAt(0).toUpperCase() + x.slice(1).toLowerCase()
}

async function loadRecentCases(limit = 10) {
  const data = await getRecentCases(limit)
  recentCases.value = (data || []).map(c => {
    const ref    = c?.reference_id
    const chain  = c?.payload?.chain || (ref?.startsWith?.('0x') ? 'ETH' : 'ETH') // system kita ETH only
    const amount = c?.payload?.amount
    const sev    = (c?.severity || 'High').toString()

    const titleCase = (s) => s ? s.charAt(0).toUpperCase() + s.slice(1).toLowerCase() : s
    const shortRef = (r) => !r ? '—' : (String(r).length > 12 ? `${String(r).slice(0,6)}...${String(r).slice(-4)}` : String(r))
    const statusUI = (s) => s === 'Under Review' ? 'In Review' : (s || '—')

    const sevLabel = titleCase(sev) // Critical/High/Medium/Low

    return {
      // kolom CASE ID
      id: `AML-${chain}-${shortRef(ref)}`,

      customer: `Wallet: ${shortRef(ref)}`,
      wallet: shortRef(ref),
      entity: shortRef(ref),

      // kolom CRYPTO & AMOUNT
      crypto: chain,
      amount: amount ? `${amount} ${chain}` : '—',

      // kolom PRIORITY / RISK
      priority: sevLabel,
      riskLevel: sevLabel,

      // kolom STATUS & DATE
      status: statusUI(c?.status),
      date: new Date(c?.created_at || Date.now()).toLocaleDateString(),

      // metadata opsional
      _rawId: c?.id,
      _reference: ref
    }
  })
}

function timeLabel(ts) {
  const t = new Date(ts), now = new Date()
  const diffMin = Math.floor((now - t)/60000)
  if (diffMin < 1) return 'Just now'
  if (diffMin < 60) return `${diffMin} min ago`
  const h = Math.floor(diffMin/60)
  if (h < 24) return `${h} hour${h>1?'s':''} ago`
  const d = Math.floor(h/24)
  return `${d} day${d>1?'s':''} ago`
}

function pickTimestamp(row) {
  // API kamu sekarang alias 'timestamp', tapi jaga-jaga kalau masih 'created_at' / 'added_on'
  return row.timestamp || row.created_at || row.added_on || new Date().toISOString();
}

async function loadAlerts(limit = 20) {
  try {
    const data = await getAlerts(limit)
    alerts.value = (data || []).map(a => {
      const ts = pickTimestamp(a);
      const rs = a.risk_score ?? a.riskScore; // dukung 2 gaya nama
      return {
        id: a.id,
        type: a.type || 'medium',
        title: a.title || 'Security Alert',
        description: a.description || '',
        time: timeLabel(ts),
        timestamp: new Date(ts),
        crypto: a.crypto || 'ETH',
        amount: a.amount || '—',
        severity: rs != null ? Math.round(Number(rs) * 10)
                 : (a.type==='critical'?90 : a.type==='high'?75 : 40),
        read: false,
        source: a.source || 'Risk Engine',
        riskScore: rs ?? null,
        affectedWallets: a.affected_wallets ?? null,
        transactionHash: a.transaction_hash ?? null,
        tags: a.tags || []
      }
    })
  } catch (err) {
    console.error('Failed to load alerts:', err)
  }
}

async function loadStats() {
  try {
    const [s, hr, ac, uc, cs, wd] = await Promise.all([
      getAnomalySummary(),
      getHighRiskCount(),
      getActiveCasesCount(),
      getUrgentCasesCount(),
      getComplianceScore(),
      getWalletRiskDistribution()
    ])

    // Suspicious Transactions
    cryptoMetrics.value.suspiciousTransactions.count  = s.total ?? 0
    cryptoMetrics.value.suspiciousTransactions.btc    = s?.by_chain?.BTC ?? 0
    cryptoMetrics.value.suspiciousTransactions.eth    = s?.by_chain?.ETH ?? 0
    cryptoMetrics.value.suspiciousTransactions.change = Math.round((s.delta_pct ?? 0) * 100)
    cryptoMetrics.value.suspiciousTransactions.trend  = s.direction || 'flat'

    // High Risk Addresses
    const current = Number(hr?.high_risk_addresses ?? hr?.count ?? 0)
    const prev    = prevHighRisk ?? current
    const changePct = prev ? Math.round(((current - prev) / prev) * 100) : 0
    cryptoMetrics.value.highRiskAddresses.count  = current
    cryptoMetrics.value.highRiskAddresses.change = changePct
    cryptoMetrics.value.highRiskAddresses.trend  = current > prev ? 'up' : current < prev ? 'down' : 'flat'
    prevHighRisk = current

    // Active Cases
    const active = Number(ac?.count ?? 0)
    cryptoMetrics.value.activeCases.count  = active
    cryptoMetrics.value.activeCases.urgent = Number(uc?.count ?? 0)   
    cryptoMetrics.value.activeCases.eth    = active                 
    cryptoMetrics.value.activeCases.btc    = 0

    // Compliance (percent normal wallets)
    const prevScore = Number(cryptoMetrics.value.complianceScore.score || 0)
    const nowScore  = Number(cs?.score ?? 0)

    cryptoMetrics.value.complianceScore.score  = Math.round(nowScore)
    cryptoMetrics.value.complianceScore.change = Math.round(nowScore - prevScore)
    cryptoMetrics.value.complianceScore.trend  = nowScore >= prevScore ? 'up' : 'down'
    // simpan meta untuk ditampilkan kecil di kartu (opsional)
    cryptoMetrics.value.complianceScore.total      = Number(cs?.total_wallets ?? 0)
    cryptoMetrics.value.complianceScore.anomalous  = Number(cs?.anomalous_wallets ?? 0)

    // Risk distribution untuk ComplianceStatus
    if (wd) {
      riskDistribution.value = {
        total: Number(wd.total ?? 0),
        critical: Number(wd.critical ?? 0),
        high: Number(wd.high ?? 0),
        medium: Number(wd.medium ?? 0),
        pct: {
          critical: Number(wd?.pct?.critical ?? 0),
          high: Number(wd?.pct?.high ?? 0),
          medium: Number(wd?.pct?.medium ?? 0)
        }
      }
    }

    lastUpdate.value = new Date()
  } catch (e) {
    console.error('Failed to load stats:', e)
  }
}

onMounted(() => {
  // 1) Start periodic jobs
  statsTimer = statsTimer = setInterval(() => {
    loadStats();
    loadRecentCases(10);
    loadAlerts(50);
  }, 30000);
  timeInterval = setInterval(() => {
    const now = new Date();
    alerts.value.forEach(alert => {
      const diff = Math.floor((now - alert.timestamp) / 60000);
      if (diff < 60) {
        alert.time = diff === 0 ? 'Just now' : `${diff} min ago`;
      } else if (diff < 1440) {
        const h = Math.floor(diff / 60);
        alert.time = `${h} hour${h > 1 ? 's' : ''} ago`;
      } else {
        const d = Math.floor(diff / 1440);
        alert.time = `${d} day${d > 1 ? 's' : ''} ago`;
      }
    });
  }, 60000);

  loadAlerts(50);
  loadStats();
  loadRecentCases(10);
});

onBeforeUnmount(() => {
  if (statsTimer) clearInterval(statsTimer);
  if (timeInterval) clearInterval(timeInterval);
});
</script>

<template>
  <div class="dashboard-container">
    <div class="dashboard-content">
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
                            SigmaVerde Crypto AML
                        </h1>
                    </div>
                    <p class="text-gray-600 dark:text-gray-300">Advanced Anti-Money Laundering monitoring for Cryptocurrency Ecosystem</p>
                </div>
                
                <div class="flex flex-col sm:flex-row items-start sm:items-center gap-4">
                    <!-- Alert Statistics -->
                    <div class="flex items-center gap-3">
                        <div class="bg-white dark:bg-gray-800 px-4 py-3 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
                            <div class="flex items-center gap-4">
                                <div class="text-center">
                                    <div class="text-lg font-bold text-red-600 dark:text-red-400">{{ alertStats.critical }}</div>
                                    <div class="text-xs text-gray-500">Critical</div>
                                </div>
                                <div class="text-center">
                                    <div class="text-lg font-bold text-orange-600 dark:text-orange-400">{{ alertStats.high }}</div>
                                    <div class="text-xs text-gray-500">High</div>
                                </div>
                                <div class="text-center">
                                    <div class="text-lg font-bold text-yellow-600 dark:text-yellow-400">{{ alertStats.medium }}</div>
                                    <div class="text-xs text-gray-500">Medium</div>
                                </div>
                                <div class="text-center">
                                    <div class="text-lg font-bold text-blue-600 dark:text-blue-400">{{ alertStats.unread }}</div>
                                    <div class="text-xs text-gray-500">Unread</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
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
        <MetricsCards 
          :crypto-metrics="cryptoMetrics" 
          :selected-timeframe="selectedTimeframe"
          @update:selected-timeframe="updateTimeframe"
        />

        <!-- Main Dashboard Grid -->
        <div class="grid grid-cols-12 gap-6">

            <!-- Compliance Status -->
            <div class="col-span-12 xl:col-span-4">
                <ComplianceStatus :risk="riskDistribution" />
            </div>

            <!-- Enhanced Alerts Panel with Full Screen Dialog -->
            <div class="col-span-12 xl:col-span-4">
                <AlertsPanel 
                    :alerts="alerts" 
                    @dismiss-alert="dismissAlert"
                    @clear-all="clearAllAlerts"
                    @mark-all-read="markAllAsRead"
                />
            </div>

            <!-- Regulatory Updates -->
            <div class="col-span-12 xl:col-span-4">
                <RegulatoryUpdates />
            </div>

            <!-- Recent Cases -->
            <div class="col-span-12">
                <RecentCasesTable :recent-cases="recentCases" />
            </div>
        </div>

        <!-- Quick Actions FAB -->
        <QuickActionsFAB 
          :show-quick-actions="showQuickActions"
          @toggle="toggleQuickActions"
          @export-report="exportReport"
          @navigate="navigateTo"
        />

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

        <!-- Real-time Alert Notifications -->
        <div class="fixed top-6 right-6 z-40 space-y-3 max-w-sm">
            <TransitionGroup name="notification" tag="div">
              <div class="fixed top-[88px] right-4 space-y-3 z-50">
                <NotificationAlert
                  v-for="alert in alerts.slice(0, 3).filter(a => !a.read && a.time === 'Just now')"
                  :key="`notification-${alert.id}`"
                  :alert="alert"
                  @dismiss="dismissAlert"
                />
              </div>

            </TransitionGroup>
        </div>
    </div>
    </div>
  </div>
</template>

<style scoped>

.dashboard-container {
  height: 100vh;
  overflow: hidden;
}

.dashboard-content {
  height: 100vh;
  overflow-y: auto;
  scroll-behavior: smooth;
}

.dashboard-content::-webkit-scrollbar {
  width: 8px;
}

.dashboard-content::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 4px;
}

.dashboard-content::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
}

.dashboard-content::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.3);
}

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

/* Enhanced grid layout for address lookup */
.address-lookup-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

@media (max-width: 1280px) {
  .address-lookup-grid {
    grid-template-columns: 1fr;
  }
}

/* Real-time notification animations */
.notification-enter-active,
.notification-leave-active {
  transition: all 0.5s ease;
}

.notification-enter-from {
  opacity: 0;
  transform: translateX(100%) scale(0.8);
}

.notification-leave-to {
  opacity: 0;
  transform: translateX(100%) scale(0.8);
}

.notification-move {
  transition: transform 0.5s ease;
}

/* Alert statistics styling */
.alert-stats {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(147, 51, 234, 0.1) 100%);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.dark .alert-stats {
  background: linear-gradient(135deg, rgba(17, 24, 39, 0.8) 0%, rgba(31, 41, 55, 0.6) 100%);
  border-color: rgba(75, 85, 99, 0.3);
}

/* Enhanced alert notification styling */
.alert-notification {
  backdrop-filter: blur(20px);
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 
    0 20px 25px -5px rgba(0, 0, 0, 0.1),
    0 10px 10px -5px rgba(0, 0, 0, 0.04),
    0 0 0 1px rgba(255, 255, 255, 0.05);
}

.dark .alert-notification {
  background: rgba(31, 41, 55, 0.95);
  box-shadow: 
    0 20px 25px -5px rgba(0, 0, 0, 0.25),
    0 10px 10px -5px rgba(0, 0, 0, 0.1),
    0 0 0 1px rgba(75, 85, 99, 0.2);
}

/* Line clamp utility */
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Enhanced hover effects for interactive elements */
.interactive-card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.interactive-card:hover {
  transform: translateY(-4px) scale(1.02);
  box-shadow: 
    0 25px 50px -12px rgba(0, 0, 0, 0.25),
    0 0 0 1px rgba(255, 255, 255, 0.1);
}

/* Glassmorphism effect for modern UI */
.glass-effect {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.dark .glass-effect {
  background: rgba(17, 24, 39, 0.6);
  border-color: rgba(75, 85, 99, 0.3);
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(156, 163, 175, 0.1);
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
    max-width: calc(100vw - 2rem);
  }
  
  .grid-cols-12 > * {
    grid-column: span 12;
  }
  
  .alert-notification {
    margin: 0 1rem;
  }
}

@media (max-width: 640px) {
  .dashboard-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .header-stats {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .alert-stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 0.5rem;
  }
}

/* Print styles for reports */
@media print {
  .fixed {
    display: none !important;
  }
  
  .bg-gradient-to-br {
    background: white !important;
  }
  
  .dark\:bg-gray-900 {
    background: white !important;
  }
  
  .text-white {
    color: black !important;
  }
  
  .shadow-lg,
  .shadow-xl,
  .shadow-2xl {
    box-shadow: none !important;
    border: 1px solid #e5e7eb !important;
  }
}

/* High contrast mode */
@media (prefers-contrast: high) {
  .bg-gray-50 {
    background-color: white;
  }
  
  .bg-gray-100 {
    background-color: #f5f5f5;
  }
  
  .border-gray-200 {
    border-color: #000;
  }
  
  .text-gray-600 {
    color: #000;
  }
  
  .glass-effect,
  .alert-notification {
    background: white !important;
    border: 2px solid #000 !important;
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
  
  .animate-pulse,
  .animate-spin {
    animation: none !important;
  }
}

/* Enhanced focus indicators for accessibility */
.focus-visible:focus {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
  border-radius: 0.375rem;
}

/* Custom scrollbar for webkit browsers */
.custom-scrollbar::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 4px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 4px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.5);
}

.dark .custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
}

.dark .custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
}

.dark .custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}
</style>
