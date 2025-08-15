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
                            <div class="border-circle w-2rem h-2rem bg-green-100 flex align-items-center justify-content-center">
                                <i class="pi pi-circle-fill text-green-500 text-sm animation-pulse"></i>
                            </div>
                            <span class="text-sm font-medium text-700">Live Monitoring</span>
                        </div>
                        <Button severity="secondary" label="Export Report" icon="pi pi-download" class="p-button-outlined"></Button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Alert Summary Cards with enhanced visual hierarchy -->
        <div class="col-12">
            <div class="alert-summary-grid">
                <div v-for="(alert, index) in alerts" :key="index" 
                     class="alert-card surface-card shadow-1 border-round-xl p-3">
                    <div class="flex align-items-center gap-3">
                        <div :class="['alert-icon border-round-xl p-2', alert.iconBg]">
                            <i :class="['pi text-xl', alert.icon, alert.iconColor]"></i>
                        </div>
                        <div class="flex-1">
                            <div class="text-xl font-bold text-900 mb-1">{{ alert.value }}</div>
                            <div class="text-600 text-sm font-medium">{{ alert.label }}</div>
                            <div class="flex align-items-center gap-2 mt-2">
                                <span :class="['font-medium text-sm', alert.trendColor]">
                                    {{ alert.trend }}
                                </span>
                                <span class="text-500 text-sm">{{ alert.period }}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Main Content Area with improved layout -->
        <div class="col-12 xl:col-8">
            <div class="card surface-card shadow-1">
                <div class="flex flex-column sm:flex-row sm:justify-content-between sm:align-items-center mb-4">
                    <h5 class="text-900 font-semibold m-0">Live Transaction Feed</h5>
                    <div class="flex align-items-center gap-2 mt-3 sm:mt-0">
                        <Dropdown v-model="selectedNetwork" 
                                :options="networks" 
                                optionLabel="name" 
                                placeholder="All Networks"
                                class="w-full sm:w-12rem"></Dropdown>
                        <Button :icon="isPaused ? 'pi pi-play' : 'pi pi-pause'" 
                               :class="['p-button-rounded p-button-text', {'text-primary': !isPaused, 'text-red-600': isPaused}]"
                               v-tooltip.top="isPaused ? 'Resume Feed' : 'Pause Feed'"
                               @click="togglePause"></Button>
                    </div>
                </div>
                
                <!-- Transaction Feed with improved visual feedback -->
<CryptoLiveMonitor 
    :title="'Live Transaction Feed'"
    :showNetworkFilter="true"
    :showActions="true"
    :showStats="true"
    @transaction-click="handleTransactionClick"
    @investigate="handleInvestigate"
    @flag="handleFlag"
/>
            </div>
        </div>

        <!-- Risk Analysis Panel with improved data visualization -->
        <div class="col-12 xl:col-4">
            <div class="flex flex-column gap-3">
                <!-- Risk Distribution Chart -->
                <div class="card surface-card shadow-1">
                    <h5 class="text-900 font-semibold m-0 mb-3">Risk Distribution</h5>
                    <div class="flex justify-content-center">
                        <Chart type="doughnut" 
                               :data="riskChartData" 
                               :options="riskChartOptions" 
                               class="w-full" 
                               style="max-width: 300px;"></Chart>
                    </div>
                </div>
                
                <!-- Risk Indicators -->
                <div class="card surface-card shadow-1">
                    <h5 class="text-900 font-semibold m-0 mb-3">Top Risk Indicators</h5>
                    <div class="risk-indicators">
                        <div v-for="indicator in topRiskIndicators" 
                             :key="indicator.type" 
                             class="flex justify-content-between align-items-center p-3 border-round-lg mb-2 surface-ground">
                            <div class="flex-1">
                                <div class="font-medium text-900">{{ indicator.type }}</div>
                                <div class="text-sm text-600">{{ indicator.description }}</div>
                            </div>
                            <div class="text-right">
                                <div class="text-xl font-bold text-900">{{ indicator.count }}</div>
                                <div class="text-xs text-500">occurrences</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Suspicious Addresses Watchlist with improved table design -->
        <div class="col-12">
            <div class="card surface-card shadow-1">
                <div class="flex flex-column lg:flex-row lg:justify-content-between lg:align-items-center mb-4">
                    <h5 class="text-900 font-semibold m-0">Suspicious Addresses Watchlist</h5>
                    <div class="flex gap-2 mt-3 lg:mt-0">
                        <Button label="Add Address" 
                               icon="pi pi-plus" 
                               severity="success"
                               class="p-button-outlined" 
                               @click="showAddAddressDialog = true"></Button>
                        <Button label="Bulk Import" 
                               icon="pi pi-upload" 
                               severity="secondary"
                               class="p-button-outlined"></Button>
                    </div>
                </div>
                
                <DataTable :value="suspiciousAddresses" 
                          v-model:filters="filters"
                          :paginator="true" 
                          :rows="10"
                          :globalFilterFields="['address', 'reason', 'network']"
                          filterDisplay="menu"
                          responsiveLayout="scroll"
                          class="p-datatable-sm">
                    <template #header>
                        <div class="flex justify-content-end">
                            <span class="p-input-icon-left w-full sm:w-auto">
                                <i class="pi pi-search" />
                                <InputText v-model="filters['global'].value" 
                                         placeholder="Search addresses..." 
                                         class="w-full" />
                            </span>
                        </div>
                    </template>
                    
                    <Column field="address" 
                           header="Address" 
                           :sortable="true">
                        <template #body="slotProps">
                            <div class="font-mono text-sm">{{ slotProps.data.address }}</div>
                        </template>
                    </Column>
                    
                    <Column field="network" 
                           header="Network" 
                           :sortable="true">
                        <template #body="slotProps">
                            <Tag :value="slotProps.data.network" 
                                 severity="info"></Tag>
                        </template>
                    </Column>
                    
                    <Column field="riskScore" 
                           header="Risk Score" 
                           :sortable="true">
                        <template #body="slotProps">
                            <div class="flex align-items-center gap-2">
                                <div class="w-8rem">
                                    <ProgressBar :value="slotProps.data.riskScore" 
                                               :class="getRiskScoreClass(slotProps.data.riskScore)"
                                               :pt="{
                                                   root: { style: 'height: 0.5rem' }
                                               }" />
                                </div>
                                <span class="font-medium">{{ slotProps.data.riskScore }}%</span>
                            </div>
                        </template>
                    </Column>
                    
                    <Column field="reason" 
                           header="Reason">
                        <template #body="slotProps">
                            <div class="text-sm line-height-3 max-w-30rem text-600">
                                {{ slotProps.data.reason }}
                            </div>
                        </template>
                    </Column>
                    
                    <Column field="lastActivity" 
                           header="Last Activity" 
                           :sortable="true">
                        <template #body="slotProps">
                            <div class="text-sm">
                                {{ formatTime(slotProps.data.lastActivity) }}
                            </div>
                        </template>
                    </Column>
                    
                    <Column field="transactionCount" 
                           header="Transactions" 
                           :sortable="true">
                        <template #body="slotProps">
                            <div class="font-medium">
                                {{ slotProps.data.transactionCount.toLocaleString() }}
                            </div>
                        </template>
                    </Column>
                    
                    <Column header="Actions" 
                           :exportable="false" 
                           style="min-width:8rem">
                        <template #body="slotProps">
                            <div class="flex gap-2">
                                <Button icon="pi pi-eye" 
                                       class="p-button-rounded p-button-text p-button-plain" 
                                       v-tooltip.top="'View Details'"
                                       @click="viewAddressDetails(slotProps.data)"></Button>
                                <Button icon="pi pi-chart-line" 
                                       class="p-button-rounded p-button-text p-button-plain" 
                                       v-tooltip.top="'Transaction History'"
                                       @click="viewTransactionHistory(slotProps.data)"></Button>
                                <Button icon="pi pi-trash" 
                                       class="p-button-rounded p-button-text p-button-danger" 
                                       v-tooltip.top="'Remove from Watchlist'"
                                       @click="removeFromWatchlist(slotProps.data)"></Button>
                            </div>
                        </template>
                    </Column>
                </DataTable>
            </div>
        </div>

        <!-- Transaction Volume Chart with improved visualization -->
        <div class="col-12">
            <div class="card surface-card shadow-1">
                <div class="flex flex-column lg:flex-row lg:justify-content-between lg:align-items-center mb-4">
                    <h5 class="text-900 font-semibold m-0">Transaction Volume & Risk Trends</h5>
                    <div class="flex gap-2 mt-3 lg:mt-0">
                        <SelectButton v-model="chartTimeframe" 
                                    :options="timeframeOptions" 
                                    optionLabel="label" 
                                    optionValue="value"
                                    class="text-sm"></SelectButton>
                    </div>
                </div>
                <div class="chart-container">
                    <Chart type="line" 
                           :data="volumeChartData" 
                           :options="volumeChartOptions"></Chart>
                </div>
            </div>
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
            modal 
            header="Transaction Investigation" 
            :style="{ width: '90vw', maxWidth: '900px' }" 
            :breakpoints="{ '960px': '75vw', '641px': '95vw' }">
        <div v-if="selectedTransaction" class="investigation-content">
            <!-- Transaction Details -->
            <div class="grid">
                <div class="col-12 md:col-6 mb-3">
                    <label class="block font-medium text-900 mb-2">Transaction Hash</label>
                    <div class="font-mono text-sm p-3 surface-ground border-round">
                        {{ selectedTransaction.hash }}
                    </div>
                </div>
                <div class="col-12 md:col-6 mb-3">
                    <label class="block font-medium text-900 mb-2">Block Height</label>
                    <div class="p-3 surface-ground border-round">
                        {{ selectedTransaction.blockHeight }}
                    </div>
                </div>
                <div class="col-12 md:col-6 mb-3">
                    <label class="block font-medium text-900 mb-2">From Address</label>
                    <div class="font-mono text-sm p-3 surface-ground border-round">
                        {{ selectedTransaction.from }}
                    </div>
                </div>
                <div class="col-12 md:col-6 mb-3">
                    <label class="block font-medium text-900 mb-2">To Address</label>
                    <div class="font-mono text-sm p-3 surface-ground border-round">
                        {{ selectedTransaction.to }}
                    </div>
                </div>
            </div>
            
            <Divider />
            
            <!-- Transaction Values -->
            <div class="grid">
                <div class="col-12 md:col-4 mb-3">
                    <label class="block font-medium text-900 mb-2">Amount</label>
                    <div class="text-2xl font-bold text-900">
                        ${{ formatCurrency(selectedTransaction.amount) }}
                    </div>
                </div>
                <div class="col-12 md:col-4 mb-3">
                    <label class="block font-medium text-900 mb-2">Gas Fee</label>
                    <div class="text-xl text-700">
                        ${{ formatCurrency(selectedTransaction.fee) }}
                    </div>
                </div>
                <div class="col-12 md:col-4 mb-3">
                    <label class="block font-medium text-900 mb-2">Risk Level</label>
                    <Tag :value="selectedTransaction.riskLevel" 
                         :severity="getRiskSeverity(selectedTransaction.riskLevel)"
                         class="text-sm"></Tag>
                </div>
            </div>
            
            <!-- Suspicious Indicators -->
            <div v-if="selectedTransaction.suspiciousFlags.length > 0" class="mb-4">
                <Divider />
                <h6 class="font-medium text-900 mb-3">Suspicious Indicators</h6>
                <div class="flex flex-wrap gap-2">
                    <Chip v-for="flag in selectedTransaction.suspiciousFlags" 
                          :key="flag" 
                          :label="flag"
                          class="bg-red-50 text-red-900"></Chip>
                </div>
            </div>
            
            <Divider />
            
            <!-- Investigation Notes -->
            <div class="field">
                <label class="block font-medium text-900 mb-2">Investigation Notes</label>
                <Textarea v-model="investigationNotes" 
                         rows="4" 
                         placeholder="Add your investigation notes here..."
                         class="w-full" />
            </div>
        </div>
        <template #footer>
            <div class="flex flex-column sm:flex-row justify-content-end gap-2">
                <Button label="Close" 
                       icon="pi pi-times"
                       class="p-button-text"
                       @click="showInvestigationDialog = false" />
                <Button label="Flag as Suspicious" 
                       icon="pi pi-flag"
                       severity="warning"
                       @click="flagAsSupicious" />
                <Button label="Save Notes" 
                       icon="pi pi-save"
                       severity="success"
                       @click="saveInvestigationNotes" />
            </div>
        </template>
    </Dialog>
</template>

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
import { ref } from 'vue';

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

// Local state for dialogs and forms
const showAddAddressDialog = ref(false);
const showInvestigationDialog = ref(false);
const selectedTransaction = ref(null);
const investigationNotes = ref('');

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

const viewAddressDetails = (address) => {
    console.log('Viewing address details:', address);
    // Implement address details view
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

const flagAsSupicious = () => {
    if (selectedTransaction.value) {
        flagTransaction(selectedTransaction.value);
        showInvestigationDialog.value = false;
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
</script>


<style scoped>
.crypto-monitoring {
    --card-shadow: 0 2px 4px rgba(0,0,0,0.05);
    --hover-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.surface-card {
    background: var(--surface-card);
    border-radius: var(--border-radius);
    padding: 1.5rem;
    transition: all 0.3s ease;
}

.shadow-1 {
    box-shadow: var(--card-shadow);
}

.shadow-1:hover {
    box-shadow: var(--hover-shadow);
}

/* Chart Container */
.chart-container {
    position: relative;
    width: 100%;
    height: 400px;
}

/* Risk Indicators */
.risk-indicators {
    max-height: 300px;
    overflow-y: auto;
    padding-right: 0.5rem;
}

/* Alert Summary Grid */
.alert-summary-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
    margin-bottom: 1rem;
}

.alert-card {
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.alert-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--hover-shadow);
}

/* Alert Icons */
.alert-icon {
    width: 3rem;
    height: 3rem;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* Animation */
.animation-pulse {
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% {
        opacity: 1;
    }
    50% {
        opacity: 0.5;
    }
    100% {
        opacity: 1;
    }
}

/* Responsive Table */
.p-datatable-wrapper {
    overflow-x: auto;
}

/* Chart Responsiveness */
@media screen and (max-width: 640px) {
    .chart-container {
        height: 300px;
    }
}
</style>
