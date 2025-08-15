<script setup>
import { useCryptoMonitoring } from '@/composables/useCryptoMonitoring';
import Button from 'primevue/button';
import Chart from 'primevue/chart';
import Chip from 'primevue/chip';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import Dialog from 'primevue/dialog';
import Divider from 'primevue/divider';
import Dropdown from 'primevue/dropdown';
import InputText from 'primevue/inputtext';
import ProgressBar from 'primevue/progressbar';
import SelectButton from 'primevue/selectbutton';
import Slider from 'primevue/slider';
import Tag from 'primevue/tag';
import Textarea from 'primevue/textarea';
import { ref, onMounted, computed, reactive } from 'vue';
import { useToast } from 'primevue/usetoast'
import { useRouter } from 'vue-router'
import * as api from '@/services/api'


// Use the composable
const {
    alertSummary,
    monitoringStats,
    networks,
    alerts,
    selectedNetwork,
    isPaused,
    liveTransactions,
    suspiciousAddresses,
    topRiskIndicators,
    chartTimeframe,
    timeframeOptions,
    riskChartData,
    volumeChartData,
    togglePause,
    getTransactionClass,
    getRiskSeverity,
    getRiskScoreClass,
    truncateAddress,
    formatCurrency,
    formatTime
} = useCryptoMonitoring();

// --- API base ---
const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:5000/api'

// Local state for dialogs and forms
const showAddAddressDialog = ref(false);
const showInvestigationDialog = ref(false);
const selectedTransaction = ref(null);
const investigationNotes = ref('');

// --- NEW: state untuk 2 tabel ---
const loadingBlacklist = ref(false)
const loadingAnoms = ref(false)
const blacklistRows = ref([])
const anomalyRows = ref([])

const blacklistCount = ref(null)

// --- formatter util ---
const shortAddr = (a) => a ? `${a.slice(0,6)}…${a.slice(-4)}` : '-'
const shortHash = (h) => h ? `${h.slice(0,10)}…${h.slice(-6)}` : '-'
const fmtETH = (n) => (n==null || Number.isNaN(+n)) ? '-' : (+n).toFixed(6).replace(/\.?0+$/,'')
const fmtDT = (ts) => {
  if (!ts && ts!==0) return '-'
  // backend output_json pakai default=str → string datetime; handle number juga
  const d = typeof ts === 'number'
    ? new Date(ts > 1e12 ? ts : ts * 1000)
    : new Date(String(ts).replace(' ', 'T'))
  return isNaN(+d) ? String(ts) : d.toLocaleString()
}

const newAddress = ref({
    address: '',
    network: '',
    reason: '',
    riskScore: 50
});

const filters = ref({
    global: { value: null, matchMode: 'contains' },
    address: { value: null, matchMode: 'contains' },
    network: { value: null, matchMode: 'equals' },
    reason: { value: null, matchMode: 'contains' }
});

// Chart options
const riskChartOptions = ref({
    plugins: {
        legend: {
            labels: {
                color: '#374151'
            }
        }
    },
    responsive: true,
    maintainAspectRatio: true
});

const volumeChartOptions = ref({
    maintainAspectRatio: false,
    responsive: true,
    plugins: {
        legend: {
            labels: {
                color: '#374151'
            }
        }
    },
    scales: {
        x: {
            ticks: {
                color: '#6b7280'
            },
            grid: {
                color: '#e5e7eb'
            }
        },
        y: {
            ticks: {
                color: '#6b7280'
            },
            grid: {
                color: '#e5e7eb'
            }
        }
    }
});

// Methods
const investigateTransaction = (transaction) => {
    selectedTransaction.value = transaction;
    investigationNotes.value = '';
    showInvestigationDialog.value = true;
};

const flagTransaction = (transaction) => {
    // Add transaction address to suspicious addresses if not already there
    const existingAddress = suspiciousAddresses.value.find(addr => 
        addr.address === transaction.from || addr.address === transaction.to
    );
    
    if (!existingAddress) {
        const newSuspiciousAddress = {
            id: suspiciousAddresses.value.length + 1,
            address: transaction.from,
            network: transaction.network,
            riskScore: transaction.riskLevel === 'CRITICAL' ? 95 : 
                      transaction.riskLevel === 'HIGH' ? 80 : 65,
            reason: `Flagged from transaction: ${transaction.suspiciousFlags?.join(', ') || 'Manual flag'}`,
            lastActivity: transaction.timestamp,
            transactionCount: 1
        };
        
        suspiciousAddresses.value.unshift(newSuspiciousAddress);
        alertSummary.value.flaggedAddresses++;
        alertSummary.value.newFlagged++;
    }
    
    console.log('Transaction flagged successfully');
};

const addToWatchlist = () => {
    if (newAddress.value.address && newAddress.value.network && newAddress.value.reason) {
        const newSuspiciousAddress = {
            id: suspiciousAddresses.value.length + 1,
            address: newAddress.value.address,
            network: newAddress.value.network,
            riskScore: newAddress.value.riskScore,
            reason: newAddress.value.reason,
            lastActivity: new Date(),
            transactionCount: 0
        };
        
        suspiciousAddresses.value.unshift(newSuspiciousAddress);
        alertSummary.value.flaggedAddresses++;
        
        // Reset form
        newAddress.value = {
            address: '',
            network: '',
            reason: '',
            riskScore: 50
        };
        
        showAddAddressDialog.value = false;
    }
};

const viewTransactionHistory = (address) => {
    console.log('Viewing transaction history for:', address);
    // Implement transaction history view
};

const removeFromWatchlist = (address) => {
    const index = suspiciousAddresses.value.findIndex(addr => addr.id === address.id);
    if (index > -1) {
        suspiciousAddresses.value.splice(index, 1);
        alertSummary.value.flaggedAddresses--;
    }
};

const saveInvestigationNotes = () => {
    if (selectedTransaction.value && investigationNotes.value) {
        console.log('Saving investigation notes:', investigationNotes.value);
        showInvestigationDialog.value = false;
    }
};

const handleTransactionClick = (transaction) => {
    investigateTransaction(transaction);
};

const handleInvestigate = (transaction) => {
    investigateTransaction(transaction);
};

const handleFlag = (transaction) => {
    flagTransaction(transaction);
};

const summary = ref(null)

const anomalyCount = ref(null)
const anomalyLastHour = ref(null)

// jumlah suspicious wallets (blacklist)
const suspiciousWalletCount = computed(() =>
  Number.isFinite(blacklistCount.value) ? blacklistCount.value
  : (blacklistRows.value?.length ?? 0)
)

const suspiciousNewToday = computed(() => summary.value?.new_flagged_today ?? null)

const formatNumber = (n) => (Number.isFinite(+n) ? (+n).toLocaleString() : '—')

// === STATE MODAL CREATE CASE ===
const showCreateCaseModal = ref(false)
const createLoading = ref(false)
const createError = ref('')
const severityOptions = ['low', 'medium', 'high', 'critical']
const typeOptions = [
  { label: 'Wallet', value: 'wallet' },
  { label: 'Transaction', value: 'transaction' }
]

const caseForm = reactive({
  type: 'wallet',
  reference_id: '',
  severity: 'medium',
  reason: '',
  notes: '',
  // metadata opsional
  payload: {
    source: null,
    category: null,
    added_on: null,
    extra: null
  },
  assignToMe: true          // kalau true → pakai /cases/assign (idempotent)
})

const metricCards = computed(() => [
  {
    key: 'anoms',
    label: 'Anomaly Transactions',
    value: formatNumber(anomalyCount.value),
    icon: 'pi-exclamation-triangle',
    color: 'text-red-500',
    bg: '#ffeceb'
  },
  {
    key: 'swallets',
    label: 'Suspicious Wallets',
    value: formatNumber(suspiciousWalletCount.value),
    icon: 'pi-flag',
    color: 'text-orange-500',
    bg: '#fff3e6'
  }
])

const router = useRouter()
const toast = useToast()

function safeCurrency(n, digits = 2) {
  const x = Number(n)
  if (!Number.isFinite(x)) return '—'
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: digits }).format(x)
}

function fmtInt(n) {
  const x = Number(n)
  return Number.isFinite(x) ? new Intl.NumberFormat('en-US').format(x) : '—'
}

function copyToClipboard(v) {
  if (!v) return
  navigator.clipboard?.writeText(String(v))
  toast.add({ severity: 'success', summary: 'Copied', detail: String(v).slice(0, 10) + '…', life: 1500 })
}

function explorerUrl(kind, v) {
  const base = 'https://etherscan.io'
  if (!v) return null
  if (kind === 'tx') return `${base}/tx/${v}`
  if (kind === 'addr') return `${base}/address/${v}`
  if (kind === 'block') return `${base}/block/${v}`
  return base
}

function viewAddressDetails({ address /*, network*/ }) {
  if (!address) return
  router.push({ name: 'wallet-detail', params: { address } })
}

function viewTransactionDetails(tx) {
  const addr = tx?.from || tx?.sender || tx?.address
  if (addr) router.push({ name: 'wallet-detail', params: { address: addr } })
}

// reset util
function resetCaseForm () {
  caseForm.type = 'wallet'
  caseForm.reference_id = ''
  caseForm.severity = 'medium'
  caseForm.reason = ''
  caseForm.notes = ''
  caseForm.payload.source = null
  caseForm.payload.category = null
  caseForm.payload.added_on = null
  caseForm.payload.extra = null
  caseForm.assignToMe = true
  createError.value = ''
}

// === BUKA MODAL dari baris WALLET ===
function openCreateCaseFromWallet(row) {
  resetCaseForm()
  caseForm.type = 'wallet'
  caseForm.reference_id = row?.address || ''
  caseForm.payload.source = row?.source ?? null
  caseForm.payload.category = row?.category ?? null
  caseForm.payload.added_on = row?.added_on ?? null
  caseForm.reason = row?.reason || row?.category || 'Flagged suspicious wallet'
  showCreateCaseModal.value = true
}

// === BUKA MODAL dari baris TRANSAKSI ===
function openCreateCaseFromTx(row) {
  resetCaseForm()
  caseForm.type = 'transaction'
  caseForm.reference_id = row?.tx_hash || row?.hash || row?.txHash || ''
  caseForm.payload.source = row?.detector ?? 'anomaly'
  caseForm.payload.category = row?.category ?? null
  caseForm.payload.added_on = row?.timestamp ?? null
  caseForm.reason = row?.reason || row?.detector || 'Anomalous transaction'
  showCreateCaseModal.value = true
}

// validasi sederhana
const isValid = computed(() =>
  !!caseForm.type &&
  !!caseForm.reference_id &&
  severityOptions.includes(caseForm.severity)
)

async function submitCreateCase () {
  createError.value = ''
  if (!isValid.value) {
    createError.value = 'Lengkapi type, reference, dan severity.'
    return
  }
  createLoading.value = true
  try {
    let res
    if (caseForm.assignToMe) {
      // idempotent + langsung assign ke diri sendiri (backend harus kenal user dari session)
      res = await api.assignEntityToCase({
        entity_type: caseForm.type === 'transaction' ? 'tx' : 'wallet',
        entity_key: caseForm.reference_id,
        severity: caseForm.severity,
        reason: caseForm.reason,
        payload: { ...caseForm.payload, notes: caseForm.notes }
      })
      const caseId = res?.case_id || res?.id
      toast.add({ severity: 'success', summary: 'Case prepared', detail: `#${caseId}`, life: 2200 })
      showCreateCaseModal.value = false
      await router.push(`/monitoring/cases/${caseId}`)
    } else {
      // buat case baru tanpa auto-assign
      res = await api.createCase({
        type: caseForm.type,
        reference_id: caseForm.reference_id,
        severity: caseForm.severity,
        reason: caseForm.reason,
        payload: { ...caseForm.payload, notes: caseForm.notes }
      })
      const caseId = res?.case_id || res?.id
      toast.add({ severity: 'success', summary: 'Case created', detail: `#${caseId}`, life: 2200 })
      showCreateCaseModal.value = false
      await router.push(`/monitoring/cases/${caseId}`)
    }
  } catch (e) {
    createError.value = e?.data?.message || e?.message || 'Create Case failed'
    toast.add({ severity: 'error', summary: 'Create Case failed', detail: createError.value, life: 4000 })
  } finally {
    createLoading.value = false
  }
}

async function loadBlacklistCount() {
  try {
    const res = await fetch(`${API_BASE}/anomalies/blacklist/count`, { headers: { Accept: 'application/json' } })
    if (res.ok) {
      const j = await res.json()
      if (typeof j.count === 'number') blacklistCount.value = j.count
    }
  } catch (e) {
    console.warn('loadBlacklistCount', e)
  }
}

// --- fetchers ---
async function loadBlacklist() {
  loadingBlacklist.value = true
  try {
    const res = await fetch(`${API_BASE}/anomalies/blacklist`, { headers: { Accept: 'application/json' } })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    blacklistRows.value = await res.json()
  } catch (e) {
    console.error('loadBlacklist', e)
    // optional toast if you use it here
  } finally { loadingBlacklist.value = false }
}

async function loadAnomalies() {
  loadingAnoms.value = true
  try {
    const res = await fetch(`${API_BASE}/anomalies/transactions`, { headers: { Accept: 'application/json' } })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const rows = await res.json()
    anomalyRows.value = rows

    // Ambil nilai terbesar antara backend count & panjang tabel (fallback aman)
    const backend = Number.isFinite(anomalyCount.value) ? anomalyCount.value : 0
    const local = Array.isArray(rows) ? rows.length : 0
    anomalyCount.value = Math.max(backend, local)
  } catch (e) {
    console.error('loadAnomalies', e)
  } finally {
    loadingAnoms.value = false
  }
}

async function loadAnomalyCard() {
  try {
    const c = await fetch(`${API_BASE}/anomalies/count`, { headers:{Accept:'application/json'} })
    if (c.ok) {
      const j = await c.json()
      // kalau backend kirim null/undefined, jangan force 0
      if (typeof j.count === 'number') anomalyCount.value = j.count
    }
  } catch (e) {
    console.warn('load anomaly count', e)
  }
  try {
    const s = await fetch(`${API_BASE}/anomalies/summary`, { headers:{Accept:'application/json'} })
    if (s.ok) {
      const sj = await s.json()
      summary.value = sj
      anomalyLastHour.value = sj.inc_anomaly_hour ?? sj.last_hour ?? null
    }
  } catch {}
}

onMounted(() => {
  loadBlacklist()
  loadAnomalies()
  loadAnomalyCard()
  loadBlacklistCount()
})
</script>

<template>
    <div class="grid crypto-monitoring">
        <!-- Header Section with improved styling -->
        <div class="col-12">
            <div class="card surface-card shadow-1">
                <div class="flex flex-column lg:flex-row lg:justify-content-between lg:align-items-center gap-3">
                    <div class="flex-1">
                        <h4 class="text-900 font-semibold m-0 mb-2">Cryptocurrency Transaction Monitoring</h4>
                        <p class="text-600 text-sm m-0 line-height-3">Real-time monitoring of cryptocurrency transactions to detect suspicious activities and compliance violations.</p>
                    </div>
                    <div class="flex flex-column sm:flex-row align-items-stretch sm:align-items-center gap-3">
                        <div class="flex align-items-center gap-2 surface-100 border-round px-3 py-2">
                            <div class="status-pill">
                                <span class="status-dot"></span>
                                <span class="text-sm font-medium text-700">Live Monitoring</span>
                            </div>
                        </div>
                        <Button severity="secondary" label="Export Report" icon="pi pi-download" class="p-button-outlined"></Button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Metrics row (2 cards sejajar) -->
        <div class="col-12 mb-3">
            <div class="alert-summary-grid">
                <div v-for="m in metricCards" :key="m.key"
                    class="alert-card surface-card shadow-1 border-round-xl p-3">
                    <div class="flex align-items-center gap-3">
                        <div class="alert-icon border-round-xl p-2" :style="{ background: m.bg }">
                        <i class="pi text-xl" :class="[m.icon, m.color]"></i>
                        </div>
                        <div class="flex-1">
                        <div class="text-xl font-bold text-900 mb-1">{{ m.value }}</div>
                        <div class="text-600 text-sm font-medium">{{ m.label }}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Suspicious Addresses Watchlist with improved table design -->
        <div class="col-12">
            <div class="card surface-card shadow-1">
                <div class="mb-4">
                  <h5 class="text-900 font-semibold m-0">Suspicious Addresses Watchlist</h5>
                </div>
                
                <DataTable
                    :value="blacklistRows"
                    v-model:filters="filters"
                    :loading="loadingBlacklist"
                    dataKey="address"
                    :paginator="true" :rows="10"
                    :globalFilterFields="['address','source','category','reason']"
                    filterDisplay="menu"
                    responsiveLayout="scroll"
                    class="p-datatable-sm"
                    >
                    <template #header>
                        <div class="flex justify-content-end align-items-center w-full py-2">
                        <span class="p-input-icon-left">
                            <i class="pi pi-search" />
                            <InputText v-model="filters['global'].value" placeholder="Search wallets…" class="w-16rem" />
                        </span>
                        </div>
                    </template>

                    <Column field="address" header="Address" sortable>
                        <template #body="{ data }">
                        <span class="font-mono text-sm" :title="data.address">{{ shortAddr(data.address) }}</span>
                        </template>
                    </Column>

                    <Column field="source" header="Source" sortable>
                        <template #body="{ data }">
                        <Tag :value="data.source || '-'" severity="info" />
                        </template>
                    </Column>

                    <Column field="category" header="Category" sortable>
                        <template #body="{ data }">
                        <Tag :value="data.category || '-'" :severity="(data.category||'').toLowerCase().includes('sanction') ? 'danger' : 'warning'" />
                        </template>
                    </Column>

                    <Column field="reason" header="Reason">
                        <template #body="{ data }">
                        <span class="text-sm text-600">{{ data.reason || '-' }}</span>
                        </template>
                    </Column>

                    <Column field="added_on" header="Added On" sortable>
                        <template #body="{ data }">
                        <span class="text-sm">{{ fmtDT(data.added_on) }}</span>
                        </template>
                    </Column>
                    <Column header="Actions" :exportable="false" style="min-width:8rem">
                        <template #body="{ data }">
                            <div class="flex gap-2">
                            <Button
                                icon="pi pi-eye"
                                class="p-button-rounded p-button-text p-button-plain"
                                v-tooltip.top="'View Wallet'"
                                @click="viewAddressDetails(data)"
                            />
                            <Button
                                icon="pi pi-briefcase"
                                class="p-button-rounded p-button-text p-button-warning"
                                v-tooltip.top="'Create Case'"
                                @click="openCreateCaseFromWallet(data)"
                            />
                            </div>
                        </template>
                    </Column>
                </DataTable>
            </div>
        </div>

        <div class="card surface-card shadow-1 mt-4">
            <div class="flex flex-column lg:flex-row lg:justify-content-between lg:align-items-center mb-4">
                <h5 class="text-900 font-semibold m-0">Anomaly Transactions</h5>
            </div>

            <DataTable
                :value="anomalyRows"
                v-model:filters="filters"
                :loading="loadingAnoms"
                dataKey="tx_hash"
                :paginator="true" :rows="10"
                responsiveLayout="scroll"
                class="p-datatable-sm"
                :globalFilterFields="['tx_hash','sender','receiver','detector','reason']"
                filterDisplay="menu"
            >
                <template #header>
                <div class="flex justify-content-end py-2">
                    <span class="p-input-icon-left">
                    <i class="pi pi-search" />
                    <InputText v-model="filters['global'].value" placeholder="Search transactions…" class="w-16rem" />
                    </span>
                </div>
                </template>

                <Column field="tx_hash" header="Tx Hash" sortable>
                <template #body="{ data }">
                    <span class="font-mono text-sm" :title="data.tx_hash">{{ shortHash(data.tx_hash) }}</span>
                </template>
                </Column>

                <Column field="sender" header="Sender" sortable>
                <template #body="{ data }">
                    <span class="font-mono text-sm" :title="data.sender">{{ shortAddr(data.sender) }}</span>
                </template>
                </Column>

                <Column field="receiver" header="Receiver" sortable>
                <template #body="{ data }">
                    <span class="font-mono text-sm" :title="data.receiver">{{ shortAddr(data.receiver) }}</span>
                </template>
                </Column>

                <Column field="value" header="Value (ETH)" sortable>
                <template #body="{ data }">
                    {{ fmtETH(data.value) }}
                </template>
                </Column>

                <Column field="timestamp" header="Timestamp" sortable>
                <template #body="{ data }">
                    {{ fmtDT(data.timestamp) }}
                </template>
                </Column>

                <Column field="detector" header="Detector" sortable />
                <Column field="reason" header="Reason" />

                <Column header="Actions" :exportable="false" style="min-width:8rem">
                    <template #body="{ data }">
                        <div class="flex gap-2">
                        <Button icon="pi pi-search"
                                class="p-button-rounded p-button-text p-button-plain"
                                v-tooltip.top="'View Details'"
                                @click="investigateTransaction({
                                hash: data.tx_hash, from: data.sender, to: data.receiver,
                                amount: data.value, timestamp: data.timestamp,
                                riskLevel: 'HIGH', suspiciousFlags: [data.reason]
                                })" />
                        <Button icon="pi pi-briefcase"
                                class="p-button-rounded p-button-text p-button-warning"
                                v-tooltip.top="'Create Case'"
                                @click="openCreateCaseFromTx(data)" />
                        </div>
                    </template>
                </Column>
            </DataTable>
        </div>
    </div>

    <!-- Add Address Dialog with improved form layout -->
    <Dialog v-model:visible="showAddAddressDialog" 
            modal 
            header="Add Suspicious Address" 
            :style="{ width: '90vw', maxWidth: '500px' }" 
            :breakpoints="{ '960px': '75vw', '641px': '90vw' }"
            class="p-fluid">
        <div class="grid formgrid p-fluid">
            <div class="col-12 field">
                <label for="address" class="font-medium text-900">Wallet Address</label>
                <InputText id="address" 
                          v-model="newAddress.address" 
                          placeholder="Enter wallet address"
                          class="p-inputtext-sm" />
            </div>
            <div class="col-12 field">
                <label for="network" class="font-medium text-900">Network</label>
                <Dropdown id="network" 
                         v-model="newAddress.network" 
                         :options="networks" 
                         optionLabel="name" 
                         optionValue="code"
                         placeholder="Select Network"
                         class="p-inputtext-sm" />
            </div>
            <div class="col-12 field">
                <label for="reason" class="font-medium text-900">Reason</label>
                <Textarea id="reason" 
                         v-model="newAddress.reason" 
                         rows="3" 
                         placeholder="Describe why this address is suspicious"
                         class="p-inputtext-sm" />
            </div>
            <div class="col-12 field">
                <label for="riskScore" class="font-medium text-900">Risk Score</label>
                <div class="flex align-items-center gap-2">
                    <Slider id="riskScore" 
                           v-model="newAddress.riskScore" 
                           :min="0" 
                           :max="100"
                           class="w-full" />
                    <div class="text-900 font-medium" style="min-width: 3rem">
                        {{ newAddress.riskScore }}%
                    </div>
                </div>
            </div>
        </div>
        <template #footer>
            <div class="flex justify-content-end gap-2">
                <Button label="Cancel" 
                       icon="pi pi-times" 
                       @click="showAddAddressDialog = false"
                       class="p-button-text" />
                <Button label="Add to Watchlist" 
                       icon="pi pi-check"
                       severity="success"
                       @click="addToWatchlist" />
            </div>
        </template>
    </Dialog>

    <!-- Transaction Investigation Dialog with improved layout -->
    <Dialog v-model:visible="showInvestigationDialog"
        modal header="Transaction Investigation"
        :style="{ width: '90vw', maxWidth: '900px' }"
        :breakpoints="{ '960px': '75vw', '641px': '95vw' }">

        <div v-if="selectedTransaction" class="investigation-content">
            <!-- Header bar kecil -->
            <div class="flex align-items-center justify-content-between mb-3">
            <div class="text-sm text-600">
                {{ new Date(selectedTransaction.timestamp || selectedTransaction.time || Date.now()).toLocaleString() }}
            </div>
            <Tag :value="selectedTransaction.riskLevel || 'UNKNOWN'"
                :severity="getRiskSeverity(selectedTransaction.riskLevel)" />
            </div>

            <!-- Row 1: Identitas -->
            <div class="grid">
            <div class="col-12 md:col-8 mb-3">
                <label class="block font-medium text-900 mb-2">Transaction Hash</label>
                <div class="flex gap-2 align-items-center">
                <div class="font-mono text-sm p-3 surface-ground border-round flex-1 overflow-auto">
                    {{ selectedTransaction.tx_hash || selectedTransaction.hash }}
                </div>
                <Button icon="pi pi-copy" class="p-button-text"
                        @click="copyToClipboard(selectedTransaction.tx_hash || selectedTransaction.hash)" />
                <Button icon="pi pi-external-link" class="p-button-text"
                        :disabled="!(selectedTransaction.tx_hash || selectedTransaction.hash)"
                        :as="'a'"
                        :href="explorerUrl('tx', selectedTransaction.tx_hash || selectedTransaction.hash)"
                        target="_blank" />
                </div>
            </div>

            <div class="col-12 md:col-4 mb-3">
                <label class="block font-medium text-900 mb-2">Block Height</label>
                <div class="flex gap-2 align-items-center">
                <div class="p-3 surface-ground border-round flex-1">
                    {{ fmtInt(selectedTransaction.block_number || selectedTransaction.blockHeight) }}
                </div>
                <Button icon="pi pi-external-link" class="p-button-text"
                        :disabled="!(selectedTransaction.block_number || selectedTransaction.blockHeight)"
                        :as="'a'"
                        :href="explorerUrl('block', selectedTransaction.block_number || selectedTransaction.blockHeight)"
                        target="_blank" />
                </div>
            </div>

            <div class="col-12 md:col-6 mb-3">
                <label class="block font-medium text-900 mb-2">From Address</label>
                <div class="flex gap-2 align-items-center">
                <div class="font-mono text-sm p-3 surface-ground border-round flex-1 overflow-auto">
                    {{ selectedTransaction.from }}
                </div>
                <Button icon="pi pi-copy" class="p-button-text" @click="copyToClipboard(selectedTransaction.from)" />
                <Button icon="pi pi-external-link" class="p-button-text"
                        :disabled="!selectedTransaction.from"
                        :as="'a'"
                        :href="explorerUrl('addr', selectedTransaction.from)" target="_blank" />
                </div>
            </div>

            <div class="col-12 md:col-6 mb-3">
                <label class="block font-medium text-900 mb-2">To Address</label>
                <div class="flex gap-2 align-items-center">
                <div class="font-mono text-sm p-3 surface-ground border-round flex-1 overflow-auto">
                    {{ selectedTransaction.to }}
                </div>
                <Button icon="pi pi-copy" class="p-button-text" @click="copyToClipboard(selectedTransaction.to)" />
                <Button icon="pi pi-external-link" class="p-button-text"
                        :disabled="!selectedTransaction.to"
                        :as="'a'"
                        :href="explorerUrl('addr', selectedTransaction.to)" target="_blank" />
                </div>
            </div>
            </div>

            <Divider />

            <!-- Row 2: Metrik -->
            <div class="grid">
            <div class="col-12 md:col-4 mb-3">
                <label class="block font-medium text-900 mb-2">Amount</label>
                <div class="text-2xl font-bold text-900">
                {{ safeCurrency(selectedTransaction.amount ?? selectedTransaction.amount_usd) }}
                </div>
                <div v-if="selectedTransaction.amount_eth" class="text-500 text-sm mt-1">
                {{ selectedTransaction.amount_eth }} ETH
                </div>
            </div>

            <div class="col-12 md:col-4 mb-3">
                <label class="block font-medium text-900 mb-2">Gas Fee</label>
                <div class="text-xl text-700">
                {{ safeCurrency(selectedTransaction.fee ?? selectedTransaction.fee_usd) }}
                </div>
                <div class="text-500 text-sm mt-1">
                gas_used: {{ selectedTransaction.gas_used ?? '—' }} • gas_price: {{ selectedTransaction.gas_price ?? '—' }}
                </div>
            </div>

            <div class="col-12 md:col-4 mb-3">
                <label class="block font-medium text-900 mb-2">Status</label>
                <Tag :value="selectedTransaction.status || 'unknown'"
                    :severity="(selectedTransaction.status||'').toLowerCase()==='success' ? 'success' : 'info'" />
            </div>
            </div>

            <!-- Indicators -->
            <div v-if="(selectedTransaction.suspiciousFlags && selectedTransaction.suspiciousFlags.length) ||
                        (selectedTransaction.indicators && selectedTransaction.indicators.length)" class="mb-3">
            <Divider />
            <h6 class="font-medium text-900 mb-3">Suspicious Indicators</h6>
            <div class="flex flex-wrap gap-2">
                <Chip v-for="flag in (selectedTransaction.suspiciousFlags || selectedTransaction.indicators)"
                    :key="flag" :label="flag" class="bg-red-50 text-red-900" />
            </div>
            </div>

            <Divider />

            <!-- Notes -->
            <div class="field">
            <label class="block font-medium text-900 mb-2">Investigation Notes</label>
            <Textarea v-model="investigationNotes" rows="4" placeholder="Add your investigation notes here..." class="w-full" />
            </div>
        </div>

        <template #footer>
            <div class="flex flex-column sm:flex-row justify-content-end gap-2">
            <Button label="Close" icon="pi pi-times" class="p-button-text" @click="showInvestigationDialog = false" />
            <Button label="Create Case"
                icon="pi pi-briefcase"
                severity="success"
                @click="createCaseFromTx(selectedTransaction)" />
            </div>
        </template>
    </Dialog>

    <!-- === MODAL CREATE CASE === -->
    <Dialog v-model:visible="showCreateCaseModal"
            modal
            header="Create Case"
            :style="{ width: '520px' }">
        <div class="p-fluid formgrid grid gap-3">
            <div class="field col-12">
            <label class="block text-sm mb-2">Type</label>
            <Dropdown :options="typeOptions" optionLabel="label" optionValue="value"
                        v-model="caseForm.type" class="w-full" />
            </div>

            <div class="field col-12">
            <label class="block text-sm mb-2">Reference ID<span class="text-red-500">*</span></label>
            <InputText v-model="caseForm.reference_id" placeholder="Wallet address atau Tx hash" />
            </div>

            <div class="field col-12 md:col-6">
            <label class="block text-sm mb-2">Severity<span class="text-red-500">*</span></label>
            <Dropdown :options="severityOptions" v-model="caseForm.severity" class="w-full" />
            </div>

            <div class="field col-12 md:col-6">
                <label class="block text-sm mb-2">Reason</label>
                <InputText v-model="caseForm.reason" class="w-full" placeholder="Alasan / indikator" />
            </div>

            <div class="field col-12 md:col-6">
                <label class="block text-sm mb-2">Notes</label>
                <Textarea v-model="caseForm.notes" class="w-full" rows="4" autoResize placeholder="Catatan tambahan (opsional)" />
            </div>

            <!-- Opsional metadata -->
            <div class="field col-12 md:col-6">
            <label class="block text-sm mb-2">Source</label>
            <InputText v-model="caseForm.payload.source" placeholder="mis: blacklist, detector" />
            </div>
            <div class="field col-12 md:col-6">
            <label class="block text-sm mb-2">Category</label>
            <InputText v-model="caseForm.payload.category" placeholder="mis: phishing, mixer, dll" />
            </div>

            <div class="field col-12">
                <div class="flex items-center gap-2">
                    <Checkbox v-model="caseForm.assignToMe" :binary="true" inputId="assignme" />
                    <label for="assignme">Assign ke saya (idempotent)</label>
                </div>
            </div>

            <div v-if="createError" class="col-12">
            <small class="p-error">{{ createError }}</small>
            </div>
        </div>

    <template #footer>
        <Button label="Batal" severity="secondary" text @click="showCreateCaseModal = false" />
        <Button label="Create Case" :loading="createLoading" :disabled="!isValid" @click="submitCreateCase" />
    </template>
    </Dialog>
</template>

<style scoped>
/* CSS Custom Properties for consistent theming */
.crypto-monitoring {
    --card-bg: var(--surface-card, #ffffff);
    --card-border-radius: 1rem;
    --card-padding: 1.5rem;
    --card-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    --card-hover-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    --card-hover-transform: translateY(-2px);
    --transition-speed: 0.3s;
    --glass-bg: rgba(255, 255, 255, 0.7);
    --glass-backdrop: blur(10px);
    
}

/* Card Base Styles */
.surface-card {
    background: var(--card-bg);
    border-radius: var(--card-border-radius);
    padding: var(--card-padding);
    transition: all var(--transition-speed) cubic-bezier(0.4, 0, 0.2, 1);
    border: 1px solid rgba(0, 0, 0, 0.05);
    backdrop-filter: var(--glass-backdrop);
    background: var(--glass-bg);
}

/* Enhanced Shadow Effects */
.shadow-1 {
    box-shadow: var(--card-shadow);
}

.shadow-1:hover {
    box-shadow: var(--card-hover-shadow);
    transform: var(--card-hover-transform);
}

/* Improved Chart Container */
.chart-container {
    position: relative;
    width: 100%;
    height: 400px;
    border-radius: var(--card-border-radius);
    overflow: hidden;
}

/* Enhanced Risk Indicators */
.risk-indicators {
    max-height: 300px;
    overflow-y: auto;
    padding-right: 0.5rem;
    scrollbar-width: thin;
    scrollbar-color: rgba(0, 0, 0, 0.2) transparent;
}

.risk-indicators::-webkit-scrollbar {
    width: 6px;
}

.risk-indicators::-webkit-scrollbar-track {
    background: transparent;
}

.risk-indicators::-webkit-scrollbar-thumb {
    background-color: rgba(0, 0, 0, 0.2);
    border-radius: 3px;
}

/* Modernized Alert Summary Grid */
.alert-summary-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.25rem;
    margin-bottom: 1.5rem;
}

.alert-card {
    transition: all var(--transition-speed) cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}

.alert-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, var(--primary-color), var(--primary-lighter-color));
    opacity: 0;
    transition: opacity var(--transition-speed);
}

.alert-card:hover::before {
    opacity: 1;
}

/* Enhanced Alert Icons */
.alert-icon {
    width: 3.5rem;
    height: 3.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 1rem;
    transition: transform var(--transition-speed);
}

.alert-card:hover .alert-icon {
    transform: scale(1.05);
}

/* Improved Animation */
.animation-pulse {
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
    0%, 100% {
        opacity: 1;
        transform: scale(1);
    }
    50% {
        opacity: 0.7;
        transform: scale(0.95);
    }
}

/* Enhanced Table Styles */
.p-datatable-wrapper {
    overflow-x: auto;
    border-radius: var(--card-border-radius);
    scrollbar-width: thin;
}

.p-datatable .p-datatable-thead > tr > th {
    background: var(--surface-ground);
    border-width: 0;
    font-weight: 600;
    padding: 1rem;
}

.p-datatable .p-datatable-tbody > tr {
    transition: background-color var(--transition-speed);
}

.p-datatable .p-datatable-tbody > tr:hover {
    background: var(--surface-hover);
}

/* Responsive Design Improvements */
@media screen and (max-width: 960px) {
    .crypto-monitoring {
        --card-padding: 1.25rem;
    }

    .alert-summary-grid {
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1rem;
    }
}

@media screen and (max-width: 640px) {
    .crypto-monitoring {
        --card-padding: 1rem;
    }

    .chart-container {
        height: 300px;
    }

    .alert-summary-grid {
        grid-template-columns: 1fr;
    }
}

/* Dialog Enhancements */
:deep(.p-dialog) {
    backdrop-filter: var(--glass-backdrop);
}

:deep(.p-dialog .p-dialog-header) {
    border-bottom: 1px solid var(--surface-border);
    padding: 1.5rem;
}

:deep(.p-dialog .p-dialog-content) {
    padding: 1.5rem;
}

:deep(.p-dialog .p-dialog-footer) {
    border-top: 1px solid var(--surface-border);
    padding: 1.5rem;
}

/* Form Field Improvements */
:deep(.p-inputtext),
:deep(.p-dropdown),
:deep(.p-multiselect) {
    transition: all var(--transition-speed);
}

:deep(.p-inputtext:hover),
:deep(.p-dropdown:hover),
:deep(.p-multiselect:hover) {
    border-color: var(--primary-color);
}

:deep(.p-inputtext:focus),
:deep(.p-dropdown:focus),
:deep(.p-multiselect:focus) {
    box-shadow: 0 0 0 2px var(--primary-lighter-color);
}

/* Button Enhancements */
:deep(.p-button) {
    transition: all var(--transition-speed);
}

:deep(.p-button:not(.p-button-text):hover) {
    transform: translateY(-1px);
    box-shadow: var(--card-shadow);
}

/* Status Indicators */
.status-indicator {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 0.5rem;
}

.status-active {
    background: var(--green-500);
    box-shadow: 0 0 0 4px var(--green-100);
}

.status-inactive {
    background: var(--gray-500);
    box-shadow: 0 0 0 4px var(--gray-100);
}

/* === Gutters untuk PrimeFlex grid === */
.crypto-monitoring {
  /* gutter horizontal minor di kiri/kanan baris */
  margin-left: -0.75rem;   /* -12px */
  margin-right: -0.75rem;
}
.crypto-monitoring > [class^="col-"],
.crypto-monitoring > [class*=" col-"] {
  padding-left: 0.75rem;   /* 12px */
  padding-right: 0.75rem;
  margin-bottom: 1rem;     /* gutter vertikal antar section */
}

/* === Card padding seragam di semua section === */
.surface-card {
  padding: 1rem;           /* sm */
}
@media (min-width: 768px) {
  .surface-card { padding: 1.25rem; }  /* md */
}
@media (min-width: 1024px) {
  .surface-card { padding: 1.5rem; }   /* lg+ */
}

/* Header bar: rapikan gap & align */
.header-flex {
  gap: 1rem;
}
@media (min-width: 1024px) {
  .header-flex { gap: 1.25rem; }
}

/* Kartu ringkas (alert) konsisten */
.alert-card { padding: 1rem; }
@media (min-width: 768px) {
  .alert-card { padding: 1.25rem; }
}

/* Risk indicators list: tinggi tetap + scroll halus */
.risk-indicators {
  max-height: 320px;
  overflow-y: auto;
  padding-right: .25rem;
  scrollbar-width: thin;
}
.risk-indicators::-webkit-scrollbar { width: 6px; }
.risk-indicators::-webkit-scrollbar-thumb {
  background-color: rgba(0,0,0,.18);
  border-radius: 3px;
}

/* Donut chart container: tinggi stabil */
.donut-wrap {
  min-height: 280px;
  display: grid;
  place-items: center;
}

/* Chart besar: beri padding kecil supaya tidak “nempel” */
.chart-container { padding: .25rem; }
.crypto-monitoring > .col-12 .card + .card { margin-top: 1rem; }

.status-pill{
  display:inline-flex;
  align-items:center;
  gap:.5rem;
  padding:.5rem .75rem;
  border-radius:9999px;            /* pill */
  background:#ECFDF5;              /* hijau muda (setara bg-green-100) */
}

.status-dot{
  width:10px;
  height:10px;
  border-radius:50%;
  background:#22C55E;              /* hijau */
  box-shadow:0 0 0 6px rgba(34,197,94,.15); /* efek glow/pulse ringan */
}

</style>
