<template>
    <div class="crypto-live-monitor">
        <!-- Header with Controls -->
        <div class="monitor-header">
            <div class="header-left">
                <h6 class="monitor-title">{{ title }}</h6>
                <div v-if="showStats" class="stats-info">
                    <span class="stat-item">{{ transactions.length }} transactions</span>
                    <span class="stat-divider">•</span>
                    <span class="stat-item flagged">{{ flaggedCount }} flagged</span>
                </div>
            </div>
            
            <div class="header-controls">
                <div v-if="showNetworkFilter" class="network-filter">
                    <Dropdown v-model="selectedNetwork" 
                             :options="networkOptions" 
                             optionLabel="name" 
                             optionValue="code"
                             placeholder="All Networks"
                             class="network-dropdown" />
                </div>
                
                <Button :icon="isLive ? 'pi pi-pause' : 'pi pi-play'" 
                       :class="['control-btn', 'live-toggle', {'live-active': isLive, 'live-paused': !isLive}]"
                       v-tooltip.top="isLive ? 'Pause Feed' : 'Resume Feed'"
                       @click="toggleLiveFeed" />
                
                <Button icon="pi pi-refresh" 
                       class="control-btn refresh-btn"
                       v-tooltip.top="'Refresh Data'"
                       :loading="loading"
                       @click="refreshData" />
            </div>
        </div>

        <!-- Live Status Indicator -->
        <div class="status-indicator">
            <div class="status-content">
                <div :class="['status-icon', {'status-live': isLive, 'status-paused': !isLive}]">
                    <i :class="['pi pi-circle-fill', {'pulse-animation': isLive}]"></i>
                </div>
                <span class="status-text">
                    {{ isLive ? 'Live Monitoring Active' : 'Monitoring Paused' }}
                </span>
            </div>
            
            <div class="last-updated">
                Last updated: {{ lastUpdated }}
            </div>
        </div>

        <!-- Transaction Feed -->
        <div class="transaction-feed">
            <!-- Loading State -->
            <div v-if="loading && transactions.length === 0" class="empty-state">
                <ProgressSpinner size="50px" strokeWidth="4" />
                <p class="empty-message">Loading anomalous transactions...</p>
            </div>
            
            <!-- Empty State -->
            <div v-else-if="filteredTransactions.length === 0" class="empty-state">
                <i class="pi pi-info-circle empty-icon"></i>
                <p class="empty-message">No anomalous transactions found</p>
                <p class="empty-submessage">Transactions will appear here when anomalies are detected</p>
            </div>
            
            <!-- Transaction List -->
            <div v-else class="transaction-list">
                <TransitionGroup name="transaction" tag="div">
                    <div v-for="transaction in paginatedTransactions" 
                         :key="transaction.id"
                         :class="['transaction-item', getRiskClass(transaction.riskLevel)]"
                         @click="$emit('transaction-click', transaction)">
                        
                        <!-- Risk Indicator Bar -->
                        <div :class="['risk-bar', getRiskBarClass(transaction.riskLevel)]"></div>
                        
                        <!-- Transaction Header -->
                        <div class="transaction-header">
                            <div class="transaction-main">
                                <div :class="['transaction-icon', getRiskIconClass(transaction.riskLevel)]">
                                    <i :class="['pi', getRiskIcon(transaction.riskLevel)]"></i>
                                </div>
                                <div class="transaction-info">
                                    <div class="amount">{{ transaction.formattedAmount }}</div>
                                    <div class="time">{{ transaction.timeAgo }}</div>
                                </div>
                            </div>
                            
                            <div class="transaction-meta">
                                <Tag :value="transaction.riskLevel" 
                                     :severity="getRiskSeverity(transaction.riskLevel)"
                                     class="risk-tag" />
                                <div class="value-info">
                                    <div class="usd-value">${{ formatCurrency(transaction.amount * 2000) }}</div>
                                    <div class="network">{{ transaction.network }}</div>
                                </div>
                            </div>
                        </div>

                        <!-- Transaction Details -->
                        <div class="transaction-details">
                            <div class="address-row">
                                <div class="address-item">
                                    <span class="address-label">From</span>
                                    <span class="address-value">{{ truncateAddress(transaction.from) }}</span>
                                </div>
                                <div class="address-arrow">
                                    <i class="pi pi-arrow-right"></i>
                                </div>
                                <div class="address-item">
                                    <span class="address-label">To</span>
                                    <span class="address-value">{{ truncateAddress(transaction.to) }}</span>
                                </div>
                            </div>
                        </div>

                        <!-- Suspicious Flags -->
                        <div v-if="transaction.suspiciousFlags.length > 0" class="suspicious-flags">
                            <div class="flags-container">
                                <Chip v-for="flag in transaction.suspiciousFlags.slice(0, 3)" 
                                      :key="flag"
                                      :label="flag"
                                      class="flag-chip" />
                                <Chip v-if="transaction.suspiciousFlags.length > 3"
                                      :label="`+${transaction.suspiciousFlags.length - 3} more`"
                                      class="flag-chip more-flags" />
                            </div>
                        </div>

                        <!-- Detection Info -->
                        <div class="detection-info">
                            <div class="detection-content">
                                <span class="detection-reason">{{ transaction.reason }}</span>
                                <span class="detection-source">{{ transaction.detector }}</span>
                            </div>
                        </div>

                        <!-- Action Buttons -->
                        <div v-if="showActions" class="transaction-actions">
                            <Button label="Investigate" 
                                   icon="pi pi-search"
                                   size="small"
                                   severity="secondary"
                                   class="action-btn investigate-btn"
                                   @click.stop="$emit('investigate', transaction)" />
                            <Button label="Flag" 
                                   icon="pi pi-flag"
                                   size="small"
                                   severity="warning"
                                   class="action-btn flag-btn"
                                   @click.stop="$emit('flag', transaction)" />
                        </div>
                    </div>
                </TransitionGroup>
            </div>

            <!-- Pagination -->
            <div v-if="totalPages > 1" class="pagination-container">
                <Paginator v-model:first="first" 
                          :rows="rowsPerPage" 
                          :totalRecords="filteredTransactions.length"
                          :rowsPerPageOptions="[10, 20, 50]"
                          template="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink RowsPerPageDropdown"
                          class="custom-paginator" />
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { anomalousTransactionsService } from '@/services/AnomalousTransactionsService';
import Button from 'primevue/button';
import Chip from 'primevue/chip';
import Dropdown from 'primevue/dropdown';
import Paginator from 'primevue/paginator';
import ProgressSpinner from 'primevue/progressspinner';
import Tag from 'primevue/tag';

// Props
const props = defineProps({
    title: {
        type: String,
        default: 'Live Transaction Monitor'
    },
    showNetworkFilter: {
        type: Boolean,
        default: true
    },
    showActions: {
        type: Boolean,
        default: true
    },
    showStats: {
        type: Boolean,
        default: true
    },
    autoRefresh: {
        type: Boolean,
        default: true
    },
    refreshInterval: {
        type: Number,
        default: 30000 // 30 seconds
    }
});

// Emits
const emit = defineEmits(['transaction-click', 'investigate', 'flag']);

// Reactive state
const transactions = ref([]);
const loading = ref(false);
const isLive = ref(true);
const selectedNetwork = ref(null);
const lastUpdated = ref('Never');
const first = ref(0);
const rowsPerPage = ref(10);

// Auto-refresh interval
let refreshIntervalId = null;
let unsubscribeUpdates = null;

// Network options
const networkOptions = ref([
    { name: 'All Networks', code: null },
    { name: 'Ethereum', code: 'Ethereum' },
    { name: 'Bitcoin', code: 'Bitcoin' },
    { name: 'Polygon', code: 'Polygon' }
]);

// Computed properties
const filteredTransactions = computed(() => {
    let filtered = transactions.value;
    
    if (selectedNetwork.value) {
        filtered = filtered.filter(tx => tx.network === selectedNetwork.value);
    }
    
    return filtered.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
});

const paginatedTransactions = computed(() => {
    const start = first.value;
    const end = start + rowsPerPage.value;
    return filteredTransactions.value.slice(start, end);
});

const totalPages = computed(() => {
    return Math.ceil(filteredTransactions.value.length / rowsPerPage.value);
});

const flaggedCount = computed(() => {
    return transactions.value.filter(tx => tx.riskLevel === 'CRITICAL' || tx.riskLevel === 'HIGH').length;
});

// Methods
const loadTransactions = async () => {
    try {
        loading.value = true;
        const data = await anomalousTransactionsService.getAnomalousTransactions();
        transactions.value = data;
        lastUpdated.value = new Date().toLocaleTimeString();
    } catch (error) {
        console.error('Failed to load transactions:', error);
    } finally {
        loading.value = false;
    }
};

const refreshData = async () => {
    await loadTransactions();
};

const toggleLiveFeed = () => {
    isLive.value = !isLive.value;
    
    if (isLive.value && props.autoRefresh) {
        startAutoRefresh();
    } else {
        stopAutoRefresh();
    }
};

const startAutoRefresh = () => {
    if (refreshIntervalId) return;
    
    refreshIntervalId = setInterval(() => {
        if (isLive.value) {
            loadTransactions();
        }
    }, props.refreshInterval);
};

const stopAutoRefresh = () => {
    if (refreshIntervalId) {
        clearInterval(refreshIntervalId);
        refreshIntervalId = null;
    }
};

const getRiskClass = (riskLevel) => {
    return `risk-${riskLevel.toLowerCase()}`;
};

const getRiskBarClass = (riskLevel) => {
    return `risk-bar-${riskLevel.toLowerCase()}`;
};

const getRiskIconClass = (riskLevel) => {
    switch (riskLevel) {
        case 'CRITICAL':
            return 'icon-critical';
        case 'HIGH':
            return 'icon-high';
        case 'MEDIUM':
            return 'icon-medium';
        default:
            return 'icon-low';
    }
};

const getRiskIcon = (riskLevel) => {
    switch (riskLevel) {
        case 'CRITICAL':
            return 'pi-exclamation-triangle';
        case 'HIGH':
            return 'pi-exclamation-circle';
        case 'MEDIUM':
            return 'pi-info-circle';
        default:
            return 'pi-check-circle';
    }
};

const getRiskSeverity = (riskLevel) => {
    switch (riskLevel) {
        case 'CRITICAL':
            return 'danger';
        case 'HIGH':
            return 'warning';
        case 'MEDIUM':
            return 'info';
        default:
            return 'success';
    }
};

const truncateAddress = (address) => {
    if (!address) return '';
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
};

const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(value);
};

// Watchers
watch(() => props.autoRefresh, (newVal) => {
    if (newVal && isLive.value) {
        startAutoRefresh();
    } else {
        stopAutoRefresh();
    }
});

// Lifecycle
onMounted(async () => {
    await loadTransactions();
    
    if (props.autoRefresh && isLive.value) {
        startAutoRefresh();
    }
    
    // Subscribe to real-time updates
    unsubscribeUpdates = anomalousTransactionsService.subscribeToTransactionUpdates((newTransactions) => {
        if (isLive.value) {
            transactions.value = newTransactions;
            lastUpdated.value = new Date().toLocaleTimeString();
        }
    });
});

onUnmounted(() => {
    stopAutoRefresh();
    if (unsubscribeUpdates) {
        unsubscribeUpdates();
    }
});
</script>

<style scoped>
.crypto-live-monitor {
    --primary-color: #10b981;
    --danger-color: #ef4444;
    --warning-color: #f59e0b;
    --info-color: #3b82f6;
    --success-color: #10b981;
    --surface-color: #ffffff;
    --surface-hover: #f8fafc;
    --border-color: #e2e8f0;
    --text-primary: #1e293b;
    --text-secondary: #64748b;
    --text-muted: #94a3b8;
    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    --radius-sm: 0.375rem;
    --radius-md: 0.5rem;
    --radius-lg: 0.75rem;
    --transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Header Styles */
.monitor-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    padding: 1rem;
    background: var(--surface-color);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-sm);
}

.header-left {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.monitor-title {
    color: var(--text-primary);
    font-size: 1.125rem;
    font-weight: 600;
    margin: 0;
}

.stats-info {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.875rem;
    color: var(--text-secondary);
}

.stat-item {
    font-weight: 500;
}

.stat-item.flagged {
    color: var(--warning-color);
    font-weight: 600;
}

.stat-divider {
    color: var(--text-muted);
}

.header-controls {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.network-dropdown {
    min-width: 10rem;
}

.control-btn {
    border-radius: 50%;
    width: 2.5rem;
    height: 2.5rem;
    border: none;
    transition: var(--transition);
}

.live-toggle.live-active {
    background-color: rgba(16, 185, 129, 0.1);
    color: var(--success-color);
}

.live-toggle.live-paused {
    background-color: rgba(239, 68, 68, 0.1);
    color: var(--danger-color);
}

.refresh-btn {
    background-color: rgba(59, 130, 246, 0.1);
    color: var(--info-color);
}

.control-btn:hover {
    transform: scale(1.05);
    box-shadow: var(--shadow-md);
}

/* Status Indicator */
.status-indicator {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    margin-bottom: 1.5rem;
}

.status-content {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.status-icon {
    width: 2.5rem;
    height: 2.5rem;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: var(--transition);
}

.status-icon.status-live {
    background-color: rgba(16, 185, 129, 0.1);
    color: var(--success-color);
}

.status-icon.status-paused {
    background-color: rgba(148, 163, 184, 0.1);
    color: var(--text-muted);
}

.pulse-animation {
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

.status-text {
    font-weight: 600;
    color: var(--text-primary);
}

.last-updated {
    font-size: 0.75rem;
    color: var(--text-muted);
    font-weight: 500;
}

/* Transaction Feed */
.transaction-feed {
    background: var(--surface-color);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    overflow: hidden;
}

.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 3rem 1rem;
    text-align: center;
}

.empty-icon {
    font-size: 3rem;
    color: var(--text-muted);
    margin-bottom: 1rem;
}

.empty-message {
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-secondary);
    margin: 0.5rem 0;
}

.empty-submessage {
    font-size: 0.875rem;
    color: var(--text-muted);
    margin: 0;
}

/* Transaction List */
.transaction-list {
    max-height: 600px;
    overflow-y: auto;
    scrollbar-width: thin;
    scrollbar-color: var(--text-muted) transparent;
}

.transaction-list::-webkit-scrollbar {
    width: 6px;
}

.transaction-list::-webkit-scrollbar-track {
    background: transparent;
}

.transaction-list::-webkit-scrollbar-thumb {
    background-color: var(--text-muted);
    border-radius: 3px;
}

/* Transaction Item */
.transaction-item {
    position: relative;
    padding: 1.25rem;
    border-bottom: 1px solid var(--border-color);
    cursor: pointer;
    transition: var(--transition);
    background: var(--surface-color);
}

.transaction-item:last-child {
    border-bottom: none;
}

.transaction-item:hover {
    background: var(--surface-hover);
    transform: translateX(4px);
    box-shadow: var(--shadow-md);
}

/* Risk Indicator Bar */
.risk-bar {
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 4px;
    transition: var(--transition);
}

.risk-bar-critical {
    background: linear-gradient(180deg, var(--danger-color) 0%, #dc2626 100%);
}

.risk-bar-high {
    background: linear-gradient(180deg, var(--warning-color) 0%, #d97706 100%);
}

.risk-bar-medium {
    background: linear-gradient(180deg, var(--info-color) 0%, #2563eb 100%);
}

.risk-bar-low {
    background: linear-gradient(180deg, var(--success-color) 0%, #059669 100%);
}

/* Transaction Header */
.transaction-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1rem;
}

.transaction-main {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.transaction-icon {
    width: 2.5rem;
    height: 2.5rem;
    border-radius: var(--radius-md);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.875rem;
    font-weight: 600;
}

.icon-critical {
    background: rgba(239, 68, 68, 0.1);
    color: var(--danger-color);
}

.icon-high {
    background: rgba(245, 158, 11, 0.1);
    color: var(--warning-color);
}

.icon-medium {
    background: rgba(59, 130, 246, 0.1);
    color: var(--info-color);
}

.icon-low {
    background: rgba(16, 185, 129, 0.1);
    color: var(--success-color);
}

.transaction-info .amount {
    font-weight: 700;
    font-size: 1rem;
    color: var(--text-primary);
    font-family: 'JetBrains Mono', monospace;
}

.transaction-info .time {
    font-size: 0.75rem;
    color: var(--text-muted);
    margin-top: 0.25rem;
}

.transaction-meta {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    text-align: right;
}

.risk-tag {
    font-size: 0.75rem;
    font-weight: 600;
}

.value-info .usd-value {
    font-weight: 600;
    font-size: 0.875rem;
    color: var(--text-primary);
}

.value-info .network {
    font-size: 0.75rem;
    color: var(--text-muted);
    margin-top: 0.25rem;
}

/* Transaction Details */
.transaction-details {
    margin-bottom: 1rem;
}

.address-row {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.75rem;
    background: rgba(248, 250, 252, 0.5);
    border-radius: var(--radius-sm);
    border: 1px solid rgba(226, 232, 240, 0.5);
}

.address-item {
    flex: 1;
    min-width: 0;
}

.address-label {
    display: block;
    font-size: 0.75rem;
    color: var(--text-muted);
    font-weight: 500;
    margin-bottom: 0.25rem;
}

.address-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.875rem;
    color: var(--text-primary);
    font-weight: 500;
}

.address-arrow {
    color: var(--text-muted);
    font-size: 0.75rem;
}

/* Suspicious Flags */
.suspicious-flags {
    margin-bottom: 1rem;
}

.flags-container {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.flag-chip {
    font-size: 0.75rem;
    font-weight: 500;
    background: rgba(245, 158, 11, 0.1);
    color: #92400e;
    border: 1px solid rgba(245, 158, 11, 0.2);
}

.flag-chip.more-flags {
    background: rgba(148, 163, 184, 0.1);
    color: var(--text-muted);
    border: 1px solid rgba(148, 163, 184, 0.2);
}

/* Detection Info */
.detection-info {
    padding: 0.75rem;
    background: rgba(59, 130, 246, 0.05);
    border: 1px solid rgba(59, 130, 246, 0.1);
    border-radius: var(--radius-sm);
    margin-bottom: 1rem;
}

.detection-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.75rem;
}

.detection-reason {
    color: var(--text-secondary);
    flex: 1;
}

.detection-source {
    color: var(--info-color);
    font-weight: 600;
}

/* Action Buttons */
.transaction-actions {
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
    padding-top: 0.75rem;
    border-top: 1px solid var(--border-color);
}

.action-btn {
    font-size: 0.75rem;
    padding: 0.5rem 1rem;
    border-radius: var(--radius-sm);
    font-weight: 500;
    transition: var(--transition);
}

.investigate-btn:hover {
    background-color: rgba(59, 130, 246, 0.1);
    border-color: var(--info-color);
}

.flag-btn:hover {
    background-color: rgba(245, 158, 11, 0.1);
    border-color: var(--warning-color);
}

/* Pagination */
.pagination-container {
    padding: 1rem;
    border-top: 1px solid var(--border-color);
    background: var(--surface-hover);
}

.custom-paginator {
    justify-content: center;
}

/* Animations */
.transaction-enter-active,
.transaction-leave-active {
    transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.transaction-enter-from {
    opacity: 0;
    transform: translateX(-20px) scale(0.95);
}

.transaction-leave-to {
    opacity: 0;
    transform: translateX(20px) scale(0.95);
}

.transaction-move {
    transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Responsive Design */
@media screen and (max-width: 1024px) {
    .monitor-header {
        flex-direction: column;
        gap: 1rem;
        align-items: stretch;
    }
    
    .header-left,
    .header-controls {
        justify-content: center;
    }
    
    .stats-info {
        justify-content: center;
    }
}

@media screen and (max-width: 768px) {
    .crypto-live-monitor {
        padding: 0.5rem;
    }
    
    .monitor-header {
        padding: 0.75rem;
        margin-bottom: 1rem;
    }
    
    .monitor-title {
        font-size: 1rem;
    }
    
    .stats-info {
        font-size: 0.75rem;
        flex-wrap: wrap;
    }
    
    .header-controls {
        flex-wrap: wrap;
        justify-content: center;
        gap: 0.5rem;
    }
    
    .network-dropdown {
        min-width: 8rem;
        font-size: 0.875rem;
    }
    
    .control-btn {
        width: 2.25rem;
        height: 2.25rem;
    }
    
    .status-indicator {
        padding: 0.75rem;
        flex-direction: column;
        gap: 0.5rem;
        text-align: center;
    }
    
    .status-content {
        justify-content: center;
    }
    
    .transaction-item {
        padding: 1rem;
    }
    
    .transaction-header {
        flex-direction: column;
        gap: 0.75rem;
        align-items: stretch;
    }
    
    .transaction-main {
        justify-content: flex-start;
    }
    
    .transaction-meta {
        justify-content: space-between;
        text-align: left;
    }
    
    .address-row {
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .address-arrow {
        transform: rotate(90deg);
        align-self: center;
    }
    
    .transaction-actions {
        justify-content: stretch;
    }
    
    .action-btn {
        flex: 1;
    }
    
    .transaction-list {
        max-height: 500px;
    }
}

@media screen and (max-width: 480px) {
    .monitor-header {
        padding: 0.5rem;
    }
    
    .status-indicator {
        padding: 0.5rem;
    }
    
    .transaction-item {
        padding: 0.75rem;
    }
    
    .transaction-icon {
        width: 2rem;
        height: 2rem;
        font-size: 0.75rem;
    }
    
    .transaction-info .amount {
        font-size: 0.875rem;
    }
    
    .flags-container {
        gap: 0.25rem;
    }
    
    .flag-chip {
        font-size: 0.625rem;
        padding: 0.25rem 0.5rem;
    }
    
    .detection-info {
        padding: 0.5rem;
    }
    
    .detection-content {
        flex-direction: column;
        gap: 0.25rem;
        align-items: flex-start;
    }
    
    .pagination-container {
        padding: 0.75rem;
    }
}

/* Dark Mode Support */
@media (prefers-color-scheme: dark) {
    .crypto-live-monitor {
        --surface-color: #1e293b;
        --surface-hover: #334155;
        --border-color: #475569;
        --text-primary: #f8fafc;
        --text-secondary: #cbd5e1;
        --text-muted: #94a3b8;
    }
    
    .monitor-header,
    .transaction-feed {
        background: var(--surface-color);
        border-color: var(--border-color);
    }
    
    .status-indicator {
        background: linear-gradient(135deg, #334155 0%, #475569 100%);
    }
    
    .address-row {
        background: rgba(51, 65, 85, 0.5);
        border-color: rgba(71, 85, 105, 0.5);
    }
    
    .detection-info {
        background: rgba(59, 130, 246, 0.1);
        border-color: rgba(59, 130, 246, 0.2);
    }
    
    .transaction-item:hover {
        background: var(--surface-hover);
    }
}

/* High Contrast Mode */
@media (prefers-contrast: high) {
    .crypto-live-monitor {
        --border-color: #000000;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.3);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }
    
    .transaction-item {
        border: 2px solid var(--border-color);
    }
    
    .risk-bar {
        width: 6px;
    }
}

/* Reduced Motion */
@media (prefers-reduced-motion: reduce) {
    .crypto-live-monitor * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
    
    .pulse-animation {
        animation: none;
    }
    
    .transaction-enter-active,
    .transaction-leave-active,
    .transaction-move {
        transition: none;
    }
}

/* Print Styles */
@media print {
    .crypto-live-monitor {
        background: white;
        color: black;
    }
    
    .header-controls,
    .transaction-actions,
    .pagination-container {
        display: none;
    }
    
    .transaction-item {
        break-inside: avoid;
        border: 1px solid #000;
        margin-bottom: 0.5rem;
    }
    
    .risk-bar {
        background: #000 !important;
    }
}

/* Focus Styles for Accessibility */
.control-btn:focus,
.transaction-item:focus,
.action-btn:focus {
    outline: 2px solid var(--primary-color);
    outline-offset: 2px;
}

/* Loading States */
.control-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.transaction-item.loading {
    opacity: 0.7;
    pointer-events: none;
}

/* Custom Scrollbar for Better UX */
.transaction-list {
    scrollbar-width: thin;
    scrollbar-color: var(--text-muted) transparent;
}

.transaction-list::-webkit-scrollbar {
    width: 8px;
}

.transaction-list::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.05);
    border-radius: 4px;
}

.transaction-list::-webkit-scrollbar-thumb {
    background: var(--text-muted);
    border-radius: 4px;
    border: 2px solid transparent;
    background-clip: content-box;
}

.transaction-list::-webkit-scrollbar-thumb:hover {
    background: var(--text-secondary);
    background-clip: content-box;
}

/* Utility Classes */
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

/* Enhanced Visual Hierarchy */
.risk-critical {
    box-shadow: 0 0 0 1px rgba(239, 68, 68, 0.1);
}

.risk-high {
    box-shadow: 0 0 0 1px rgba(245, 158, 11, 0.1);
}

.risk-medium {
    box-shadow: 0 0 0 1px rgba(59, 130, 246, 0.1);
}

.risk-low {
    box-shadow: 0 0 0 1px rgba(16, 185, 129, 0.1);
}

/* Improved Typography */
.transaction-info .amount,
.address-value {
    font-feature-settings: 'tnum' 1, 'kern' 1;
    letter-spacing: -0.025em;
}

/* Enhanced Hover Effects */
.transaction-item:hover .risk-bar {
    width: 6px;
    box-shadow: 0 0 8px rgba(0, 0, 0, 0.2);
}

.transaction-item:hover .transaction-icon {
    transform: scale(1.05);
}

/* Status Indicator Enhancements */
.status-live .pulse-animation {
    filter: drop-shadow(0 0 4px rgba(16, 185, 129, 0.4));
}

/* Network Badge Styling */
.network {
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 600;
}
</style>

