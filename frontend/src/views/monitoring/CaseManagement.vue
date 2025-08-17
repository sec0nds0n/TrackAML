<template>
    <div class="grid">
        <div class="col-12">
            <div class="card">
                <!-- Modern Header Section -->
                <div class="case-management-header">
                    <div class="header-main">
                        <div class="header-left">
                            <div class="title-section">
                                <div class="title-content">
                                    <h1 class="page-title">Case Management</h1>
                                    <p class="page-subtitle">Advanced AML monitoring and compliance oversight</p>
                                </div>
                            </div>
                            
                            <div class="header-stats">
                                <div class="stat-card active-cases">
                                    <div class="stat-icon">
                                        <i class="pi pi-folder-open"></i>
                                    </div>
                                    <div class="stat-content">
                                        <span class="stat-value">{{ caseStats.pendingL1 + caseStats.pendingL2 }}</span>
                                        <span class="stat-label">Active Cases</span>
                                        <div class="stat-trend positive">
                                            <i class="pi pi-arrow-up"></i>
                                            <span>12%</span>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="stat-card priority-cases">
                                    <div class="stat-icon urgent">
                                        <i class="pi pi-exclamation-triangle"></i>
                                    </div>
                                    <div class="stat-content">
                                        <span class="stat-value urgent">{{ caseStats.anomalies }}</span>
                                        <span class="stat-label">High Priority</span>
                                        <div class="stat-trend negative">
                                            <i class="pi pi-arrow-down"></i>
                                            <span>5%</span>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="stat-card completion-rate">
                                    <div class="stat-icon success">
                                        <i class="pi pi-check-circle"></i>
                                    </div>
                                    <div class="stat-content">
                                        <span class="stat-value">94%</span>
                                        <span class="stat-label">Resolution Rate</span>
                                        <div class="stat-trend positive">
                                            <i class="pi pi-arrow-up"></i>
                                            <span>8%</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="header-actions">
                            <div class="action-group">
                                <!-- Notification Button with modern design -->
                                <div class="action-item notification-wrapper" v-if="authStore.hasPermission('read')">
                                    <Button 
                                        @click="showNotificationsDialog = true"
                                        class="modern-notification-btn"
                                        :class="{ 'has-notifications': unreadNotifications.length > 0 }"
                                        v-tooltip.bottom="'View notifications'"
                                        text>
                                        <template #icon>
                                            <div class="notification-container">
                                                <i class="pi pi-bell"></i>
                                                <div 
                                                    v-if="unreadNotifications.length > 0" 
                                                    class="notification-indicator">
                                                    <span>{{ unreadNotifications.length > 9 ? '9+' : unreadNotifications.length }}</span>
                                                </div>
                                            </div>
                                        </template>
                                    </Button>
                                </div>
                                
                                <!-- Action buttons -->
                                <div class="action-item">
                                    <Button 
                                        icon="pi pi-refresh" 
                                        @click="fetchAnomalies"
                                        :loading="loading"
                                        class="action-button refresh-btn"
                                        v-tooltip.bottom="'Refresh data'"
                                        outlined />
                                </div>
                                
                                <div class="action-item" v-if="authStore.hasPermission('write')">
                                    <Button
                                        label="Create Case"
                                        icon="pi pi-plus"
                                        severity="success"
                                        class="ml-auto"
                                        @click="showCreateModal = true"
                                    />
                                </div>
                            </div>
                            
                            <!-- User Profile Section -->
                            <div class="user-profile" v-if="authStore.user">
                                <div class="profile-info">
                                    <span class="user-name">{{ authStore.user.name }}</span>
                                    <span class="user-role">{{ formatRole(authStore.user.role) }}</span>
                                </div>
                                <div class="profile-avatar">
                                    <Avatar 
                                        :label="getInitials(authStore.user.name)"
                                        size="large"
                                        shape="circle"
                                        class="modern-avatar"
                                        :style="{ backgroundColor: getAvatarColor(authStore.user.name) }" />
                                    <div class="status-indicator online"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Enhanced Quick Actions -->
                    <div class="quick-actions-panel" v-if="authStore.hasPermission('write')">
                        <div class="actions-grid">
                            <div class="action-card" @click="bulkImport">
                                <div class="action-icon">
                                    <i class="pi pi-cloud-upload"></i>
                                </div>
                                <div class="action-text">
                                    <span class="action-title">Bulk Import</span>
                                    <span class="action-desc">Import multiple cases</span>
                                </div>
                            </div>
                            
                            <div class="action-card" @click="exportCases">
                                <div class="action-icon">
                                    <i class="pi pi-download"></i>
                                </div>
                                <div class="action-text">
                                    <span class="action-title">Export</span>
                                    <span class="action-desc">Download case data</span>
                                </div>
                            </div>
                            
                            <div class="action-card" @click="showAdvancedFiltersDialog">
                                <div class="action-icon">
                                    <i class="pi pi-filter"></i>
                                </div>
                                <div class="action-text">
                                    <span class="action-title">Advanced Filter</span>
                                    <span class="action-desc">Complex queries</span>
                                </div>
                            </div>
                            
                            <div class="action-card" @click="showAnalytics">
                                <div class="action-icon">
                                    <i class="pi pi-chart-line"></i>
                                </div>
                                <div class="action-text">
                                    <span class="action-title">Analytics</span>
                                    <span class="action-desc">View insights</span>
                                </div>
                            </div>
                            
                            <div class="action-card" @click="bulkActions">
                                <div class="action-icon">
                                    <i class="pi pi-objects-column"></i>
                                </div>
                                <div class="action-text">
                                    <span class="action-title">Bulk Actions</span>
                                    <span class="action-desc">Process multiple</span>
                                </div>
                            </div>
                            
                            <div class="action-card" @click="automatedRules">
                                <div class="action-icon">
                                    <i class="pi pi-cog"></i>
                                </div>
                                <div class="action-text">
                                    <span class="action-title">Auto Rules</span>
                                    <span class="action-desc">Configure automation</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- API Status Indicator -->
                <div v-if="apiError" class="api-error-banner p-3 mb-4 border-round" 
                     style="background: var(--red-50); border: 1px solid var(--red-200); color: var(--red-700);">
                    <div class="flex align-items-center gap-2">
                        <i class="pi pi-exclamation-triangle"></i>
                        <span class="font-medium">API Connection Error:</span>
                        <span>{{ apiError }}</span>
                        <Button 
                            icon="pi pi-refresh" 
                            label="Retry" 
                            class="p-button-sm p-button-text p-button-danger ml-auto"
                            @click="fetchAnomalies" />
                    </div>
                </div>
                <!-- Cases Table -->
                <div class="table-container overflow-x-auto">
                    <table class="w-full border border-gray-200 dark:border-gray-700 rounded-xl">
                        <thead class="bg-gray-50 dark:bg-gray-800/50">
                        <tr class="border-b-2 border-gray-200 dark:border-gray-700">
                            <!-- CASE ID -->
                            <th @click="sortBy('id')"
                                class="select-none cursor-pointer text-left text-xs font-bold text-gray-600 dark:text-gray-400 uppercase tracking-wider py-4 pl-3">
                            Case ID
                            <SortIcon :active="sort.key==='id'" :dir="sort.dir" />
                            </th>

                            <!-- WALLET / ENTITY -->
                            <th @click="sortBy('wallet')"
                                class="select-none cursor-pointer text-left text-xs font-bold text-gray-600 dark:text-gray-400 uppercase tracking-wider py-4">
                            Wallet/Entity
                            <SortIcon :active="sort.key==='wallet'" :dir="sort.dir" />
                            </th>

                            <!-- CRYPTO -->
                            <th @click="sortBy('crypto')"
                                class="select-none cursor-pointer text-left text-xs font-bold text-gray-600 dark:text-gray-400 uppercase tracking-wider py-4">
                            Crypto
                            <SortIcon :active="sort.key==='crypto'" :dir="sort.dir" />
                            </th>

                            <!-- AMOUNT -->
                            <th @click="sortBy('amount')"
                                class="select-none cursor-pointer text-left text-xs font-bold text-gray-600 dark:text-gray-400 uppercase tracking-wider py-4">
                            Amount
                            <SortIcon :active="sort.key==='amount'" :dir="sort.dir" />
                            </th>

                            <!-- PRIORITY -->
                            <th @click="sortBy('priority')"
                                class="select-none cursor-pointer text-left text-xs font-bold text-gray-600 dark:text-gray-400 uppercase tracking-wider py-4">
                            Priority
                            <SortIcon :active="sort.key==='priority'" :dir="sort.dir" />
                            </th>

                            <!-- STATUS -->
                            <th @click="sortBy('status')"
                                class="select-none cursor-pointer text-left text-xs font-bold text-gray-600 dark:text-gray-400 uppercase tracking-wider py-4">
                            Status
                            <SortIcon :active="sort.key==='status'" :dir="sort.dir" />
                            </th>

                            <!-- DATE -->
                            <th @click="sortBy('created_at')"
                                class="select-none cursor-pointer text-left text-xs font-bold text-gray-600 dark:text-gray-400 uppercase tracking-wider py-4">
                            Date
                            <SortIcon :active="sort.key==='created_at'" :dir="sort.dir" />
                            </th>

                            <th class="text-left text-xs font-bold text-gray-600 dark:text-gray-400 uppercase tracking-wider py-4 pr-3">
                            Actions
                            </th>
                        </tr>
                        </thead>

                        <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
                        <tr v-for="row in sortedRows" :key="row.id" class="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                            <!-- Case ID -->
                            <td class="py-4 pl-3">
                            <span class="text-sm font-bold text-blue-600 dark:text-blue-400 cursor-pointer hover:underline"
                                    @click="viewCase(row)">{{ row.id }}</span>
                            </td>

                            <!-- Wallet / Entity -->
                            <td class="py-4">
                            <div class="flex flex-col">
                                <span class="text-sm font-medium text-gray-900 dark:text-white font-mono">
                                {{ row.wallet ? formatWalletAddress(row.wallet) : (row.customer || 'N/A') }}
                                </span>
                                <span class="text-xs text-gray-500 dark:text-gray-400">
                                {{ row.wallet ? 'Wallet' : (row.customer?.includes('Wallet') ? 'Individual' : 'Exchange') }}
                                </span>
                            </div>
                            </td>

                            <!-- Crypto -->
                            <td class="py-4">
                            <div class="inline-flex items-center gap-1 px-2 py-1 rounded-md text-xs font-bold"
                                :class="{
                                    'bg-orange-100 dark:bg-orange-900/50 text-orange-800 dark:text-orange-300': row.crypto === 'BTC',
                                    'bg-blue-100 dark:bg-blue-900/50 text-blue-800 dark:text-blue-300': row.crypto === 'ETH',
                                    'bg-green-100 dark:bg-green-900/50 text-green-800 dark:text-green-300': row.crypto === 'USDT' || row.crypto === 'USDC',
                                    'bg-gray-100 dark:bg-gray-900/50 text-gray-800 dark:text-gray-300': !['BTC','ETH','USDT','USDC'].includes(row.crypto)
                                }">
                                <div class="w-2 h-2 rounded-full"
                                    :class="{
                                    'bg-orange-500': row.crypto === 'BTC',
                                    'bg-blue-500': row.crypto === 'ETH',
                                    'bg-green-500': row.crypto === 'USDT' || row.crypto === 'USDC',
                                    'bg-gray-500': !['BTC','ETH','USDT','USDC'].includes(row.crypto)
                                    }"></div>
                                {{ row.crypto }}
                            </div>
                            </td>

                            <!-- Amount -->
                            <td class="py-4">
                            <span class="text-sm font-semibold text-gray-900 dark:text-white">{{ row.amount || '—' }}</span>
                            </td>

                            <!-- Priority -->
                            <td class="py-4">
                            <span class="inline-flex px-3 py-1 text-xs font-bold rounded-full"
                                    :class="{
                                    'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300': (row.priority || row.riskLevel) === 'high' || (row.priority || row.riskLevel) === 'High',
                                    'bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-300': (row.priority || row.riskLevel) === 'medium' || (row.priority || row.riskLevel) === 'Medium',
                                    'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300': (row.priority || row.riskLevel) === 'low' || (row.priority || row.riskLevel) === 'Low'
                                    }">
                                {{ row.priority || row.riskLevel || 'Medium' }}
                            </span>
                            </td>

                            <!-- Status -->
                            <td class="py-4">
                            <span class="inline-flex px-3 py-1 text-xs font-bold rounded-full"
                                    :class="{
                                    'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300': row.status === 'new',
                                    'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300': ['in_review','Under Review','Pending','pending_docs'].includes(row.status),
                                    'bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-300': row.status === 'escalated',
                                    'bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-300': row.status === 'Investigating',
                                    'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300': ['approved','Resolved'].includes(row.status),
                                    'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300': row.status === 'rejected'
                                    }">
                                {{ getStatusLabel(row.status) }}
                            </span>
                            </td>

                            <!-- Date -->
                            <td class="py-4">
                            <div class="flex flex-col">
                                <span class="text-sm font-medium text-gray-900 dark:text-white">
                                {{ formatDate(row.created_at || row.createdAt || row.date) }}
                                </span>
                                <span class="text-xs text-gray-500 dark:text-gray-400">
                                {{ (row.created_at || row.createdAt) ? new Date(row.created_at || row.createdAt).toLocaleTimeString() : '' }}
                                </span>
                            </div>
                            </td>

                            <!-- Actions -->
                            <td class="py-4 pr-3">
                                <button
                                    @click="goDetail(row.id)"
                                    class="p-1 text-blue-600 dark:text-blue-400 hover:bg-blue-100 dark:hover:bg-blue-900/30 rounded-md transition-colors"
                                    title="View Details"
                                    aria-label="View Details"
                                >
                                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                            d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                            d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                                    </svg>
                                </button>
                            </td>
                        </tr>
                        </tbody>
                    </table>
                    </div>
            </div>
        </div>

        <!-- Modal Create Case -->
        <Dialog v-model:visible="showCreateModal"
                modal header="Create Case"
                :style="{ width: '760px' }"
                :breakpoints="{ '960px':'85vw', '641px':'98vw' }">

        <div class="p-fluid formgrid grid gap-3">
            <div class="field col-12 md:col-4">
            <label class="block text-sm mb-2">Type</label>
            <Dropdown v-model="caseForm.type"
                        :options="[{label:'Suspicious Wallet',value:'wallet'},{label:'Anomaly Transaction',value:'transaction'}]"
                        optionLabel="label" optionValue="value" class="w-full"
                        placeholder="Select type"/>
            </div>

            <div class="field col-12 md:col-8">
            <label class="block text-sm mb-2">Reference ID</label>
            <InputText v-model.trim="caseForm.reference_id" class="w-full" placeholder="Wallet address atau Tx hash"/>
            </div>

            <div class="field col-12">
            <label class="block text-sm mb-2">Title</label>
            <InputText v-model.trim="caseForm.title" class="w-full" placeholder="Judul singkat"/>
            </div>

            <div class="field col-12 md:col-4">
            <label class="block text-sm mb-2">Severity</label>
            <Dropdown v-model="caseForm.severity" :options="severityOptions" class="w-full"/>
            </div>
            <div class="field col-12 md:col-4">
            <label class="block text-sm mb-2">Priority</label>
            <Dropdown v-model="caseForm.priority" :options="priorityOptions" class="w-full"/>
            </div>
            <div class="field col-12 md:col-4">
            <label class="block text-sm mb-2">Typology</label>
            <InputText v-model.trim="caseForm.typology" class="w-full" placeholder="mixer / sanctions / fraud ..."/>
            </div>

            <div class="field col-12 md:col-6">
            <label class="block text-sm mb-2">Reason</label>
            <InputText v-model.trim="caseForm.reason" class="w-full" placeholder="Alasan / indikator"/>
            </div>
            <div class="field col-12 md:col-6">
            <label class="block text-sm mb-2">Notes</label>
            <Textarea v-model="caseForm.notes" rows="3" autoResize class="w-full"
                        placeholder="Catatan analisa awal"/>
            </div>

            <div class="field col-12 md:col-6">
            <label class="block text-sm mb-2">Tags</label>
            <Chips v-model="caseForm.tags" separator="," class="w-full"
                    inputClass="w-full" placeholder="Ketik lalu Enter/koma untuk tambah tag"/>
            </div>

            <div class="field col-6 md:col-3">
            <label class="block text-sm mb-2">TLP</label>
            <Dropdown v-model="caseForm.tlp" :options="tlpOptions" class="w-full"/>
            </div>
            <div class="field col-6 md:col-3">
            <label class="block text-sm mb-2">Visibility</label>
            <Dropdown v-model="caseForm.visibility" :options="visibilityOptions" class="w-full"/>
            </div>

            <div class="field col-12 md:col-6">
            <label class="block text-sm mb-2">SLA Due</label>
            <Calendar v-model="caseForm.sla_due_at" showTime hourFormat="24" showIcon dateFormat="yy-mm-dd" class="w-full"/>
            </div>

            <div class="field col-12">
            <div class="flex items-center gap-2">
                <Checkbox v-model="caseForm.assignToMe" :binary="true" inputId="assignme" />
                <label for="assignme">Assign ke saya</label>
            </div>
            </div>

            <div v-if="createError" class="col-12">
            <small class="p-error">{{ createError }}</small>
            </div>
        </div>

        <template #footer>
            <Button label="Cancel" severity="secondary" text @click="showCreateModal=false"/>
            <Button label="Create Case" :loading="creating" :disabled="!isValidCreate" @click="onCreateCase"/>
        </template>
        </Dialog>
    </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth';
import Avatar from 'primevue/avatar';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import Dropdown from 'primevue/dropdown';
import InputText from 'primevue/inputtext';
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import * as api from '@/services/api'
import { createCase } from '@/services/api'
import Textarea from 'primevue/textarea'
import Chips from 'primevue/chips'
import Checkbox from 'primevue/checkbox'
import Calendar from 'primevue/calendar'

// Auth store
const authStore = useAuthStore();

// Reactive State
const loading = ref(false);
const apiError = ref(null);
const cases = ref([]);
const selectedCases = ref([]);
const selectedCase = ref(null);
const showCaseDialog = ref(false);
const showCreateDialog = ref(false);
const showNotificationsDialog = ref(false);
const searchTerm = ref('');
const selectedLevel = ref(null);
const selectedStatus = ref(null);
const selectedPriority = ref(null);
const selectedCrypto = ref(null);
const dateRange = ref(null);
const newNote = ref('');
const unreadNotifications = ref([]);

const router = useRouter()
const toast = useToast()


// New reactive data for enhanced UI
const showAdvancedFilters = ref(false);
const showSearchSuggestions = ref(false);
const quickFilters = ref([
    { id: 'urgent', label: 'Urgent Cases', icon: 'pi pi-exclamation-triangle', count: 12, active: false },
    { id: 'unassigned', label: 'Unassigned', icon: 'pi pi-user-minus', count: 8, active: false },
    { id: 'overdue', label: 'Overdue', icon: 'pi pi-clock', count: 5, active: false },
    { id: 'new', label: 'New Cases', icon: 'pi pi-plus-circle', count: 15, active: false }
]);
const searchSuggestions = ref([]);
const levelButtonOptions = ref([
    { label: 'L1', value: 'L1' },
    { label: 'L2', value: 'L2' }
]);
const riskScoreRange = ref([0, 100]);
const selectedSources = ref([]);
const selectedTags = ref([]);
const selectedAssignees = ref([]);
const amountRange = ref({ min: null, max: null });
const datePresets = ref([
    { label: 'Today', value: 'today' },
    { label: 'Last 7 days', value: '7d' },
    { label: 'Last 30 days', value: '30d' },
    { label: 'This month', value: 'month' }
]);
const sourceOptions = ref([
    { label: 'Internal System', value: 'internal' },
    { label: 'External API', value: 'external' },
    { label: 'Manual Entry', value: 'manual' }
]);
const assigneeOptions = ref([
    { name: 'John Smith', role: 'L1 Analyst', id: 1 },
    { name: 'Sarah Johnson', role: 'L2 Analyst', id: 2 },
    { name: 'Mike Davis', role: 'Senior Analyst', id: 3 }
]);
const circumference = ref(2 * Math.PI * 18); // For progress ring

// Case Statistics
const caseStats = computed(() => ({
    pendingL1: cases.value.filter(c => c.level === 'L1' && c.status !== 'approved').length,
    pendingL2: cases.value.filter(c => c.level === 'L2' && c.status !== 'approved').length,
    anomalies: cases.value.filter(c => c.priority === 'high').length,
    blacklisted: cases.value.filter(c => c.status === 'rejected').length
}));

// Legacy options (will be replaced by computed versions below)
const levelOptions = [
    { label: 'L1', value: 'L1' },
    { label: 'L2', value: 'L2' }
];

// Computed
const filteredCases = computed(() => {
  const uid = authStore?.user?.id
  // Amankan: kalau belum tahu user.id, jangan tampilkan apa pun dulu
  let filtered = uid
    ? cases.value.filter(c => {
        const assigned = Array.isArray(c.assignments) && c.assignments.some(a => a?.user_id === uid)
        const owned     = c.owner_id === uid
        return assigned || owned
      })
    : []

  // (lanjutan) filter lain tetap seperti semula:
  if (selectedLevel.value) {
    filtered = filtered.filter(case_ => case_.level === selectedLevel.value.value)
  }
  if (selectedStatus.value) {
    filtered = filtered.filter(case_ => case_.status === selectedStatus.value.value)
  }
  if (selectedPriority.value) {
    filtered = filtered.filter(case_ => case_.priority === selectedPriority.value.value)
  }
  if (selectedCrypto.value) {
    filtered = filtered.filter(case_ => case_.crypto === selectedCrypto.value.value)
  }
  if (searchTerm.value) {
    const term = searchTerm.value.toLowerCase()
    filtered = filtered.filter(case_ =>
      String(case_.id).toLowerCase().includes(term) ||
      case_.title?.toLowerCase().includes(term) ||
      case_.description?.toLowerCase().includes(term) ||
      case_.wallet?.toLowerCase().includes(term)
    )
  }
  if (dateRange.value && dateRange.value[0] && dateRange.value[1]) {
    const [startDate, endDate] = dateRange.value
    filtered = filtered.filter(case_ => {
      const d = new Date(case_.created_at || case_.createdAt)
      return d >= startDate && d <= endDate
    })
  }

  return filtered
})

// Methods
const fetchAnomalies = async () => {
    loading.value = true;
    apiError.value = null;
    
    try {
        console.log('Fetching anomalies from API...');
        const anomalies = await amlCaseService.getAnomalies();
        cases.value = anomalies;
        console.log(`Loaded ${anomalies.length} cases from API`);
    } catch (error) {
        console.error('Error fetching anomalies:', error);
        apiError.value = error.message;
    } finally {
        loading.value = false;
    }
};

const viewCase = (case_) => {
    selectedCase.value = case_;
    showCaseDialog.value = true;
    // router.push(`/monitoring/detail/${case_}`);

};

const escalateCase = async (case_) => {
    try {
        const updatedCase = {
            ...case_,
            level: 'L2',
            status: 'escalated',
            activities: [
                ...case_.activities || [],
                {
                    timestamp: new Date(),
                    action: 'Case Escalated to L2',
                    user: authStore.user?.name || 'Current User',
                    comment: 'Escalated for further review'
                }
            ]
        };

        await amlCaseService.updateCase(case_.id, updatedCase);
        
        // Update local case
        const index = cases.value.findIndex(c => c.id === case_.id);
        if (index !== -1) {
            cases.value[index] = updatedCase;
        }
        
        // Send notifications
        await sendNotifications(case_, 'escalation');
    } catch (error) {
        console.error('Error escalating case:', error);
        apiError.value = 'Failed to escalate case';
    }
};

const approveCase = async (case_) => {
    try {
        const updatedCase = {
            ...case_,
            status: 'approved',
            activities: [
                ...case_.activities || [],
                {
                    timestamp: new Date(),
                    action: 'Case Approved',
                    user: authStore.user?.name || 'Current User',
                    comment: 'All requirements met'
                }
            ]
        };

        await amlCaseService.updateCase(case_.id, updatedCase);
        
        // Update local case
        const index = cases.value.findIndex(c => c.id === case_.id);
        if (index !== -1) {
            cases.value[index] = updatedCase;
        }
        
        // Send notifications
        await sendNotifications(case_, 'approval');
    } catch (error) {
        console.error('Error approving case:', error);
        apiError.value = 'Failed to approve case';
    }
};

const addNote = () => {
    if (selectedCase.value && newNote.value.trim()) {
        selectedCase.value.notes.push({
            id: Date.now(),
            content: newNote.value,
            user: authStore.user?.name || 'Current User',
            timestamp: new Date()
        });
        newNote.value = '';
    }
};

const sendNotifications = async (case_, type) => {
    // Simulate sending notifications
    console.log(`Sending ${type} notifications for case ${case_.id}`);
    
    // Update stakeholder notification status
    case_.stakeholders.forEach(stakeholder => {
        stakeholder.notificationStatus = 'sent';
    });
};

const exportCases = () => {
    try {
        const csvData = amlCaseService.exportCases(filteredCases.value);
        const blob = new Blob([csvData], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `aml-cases-${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Error exporting cases:', error);
        apiError.value = 'Failed to export cases';
    }
};

const copyToClipboard = async (text) => {
    try {
        await navigator.clipboard.writeText(text);
        // You could add a toast notification here
        console.log('Copied to clipboard:', text);
    } catch (error) {
        console.error('Failed to copy to clipboard:', error);
    }
};

// Utility functions
const formatDate = (date) => {
    return new Date(date).toLocaleDateString();
};

const formatTime = (date) => {
    return new Date(date).toLocaleTimeString();
};

const formatDateTime = (date) => {
    return new Date(date).toLocaleString();
};

const formatWalletAddress = (address) => {
    if (!address) return '';
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
};

const getInitials = (name) => {
    return name
        ? name
              .split(' ')
              .map(n => n[0])
              .join('')
        : '?';
};

const getAvatarColor = (name) => {
    const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8'];
    const index = name ? name.length % colors.length : 0;
    return colors[index];
};

const getLevelSeverity = (level) => {
    switch (level) {
        case 'L1': return 'info';
        case 'L2': return 'warning';
        default: return 'info';
    }
};

const getStatusSeverity = (status) => {
    switch (status) {
        case 'new': return 'info';
        case 'in_review': return 'warning';
        case 'pending_docs': return 'warning';
        case 'escalated': return 'danger';
        case 'approved': return 'success';
        case 'rejected': return 'danger';
        default: return 'info';
    }
};

const getStatusLabel = (status) => {
    const statusLabels = {
        'new': 'New',
        'in_review': 'In Review',
        'pending_docs': 'Pending Documents',
        'escalated': 'Escalated',
        'approved': 'Approved',
        'rejected': 'Rejected'
    };
    return statusLabels[status] || status;
};

const getPrioritySeverity = (priority) => {
    switch (priority) {
        case 'high': return 'danger';
        case 'medium': return 'warning';
        case 'low': return 'info';
        default: return 'info';
    }
};

const getCryptoSeverity = (crypto) => {
    switch (crypto) {
        case 'BTC': return 'warning';
        case 'ETH': return 'info';
        case 'USDT': return 'success';
        case 'USDC': return 'success';
        default: return 'secondary';
    }
};

const getDocumentStatusSeverity = (status) => {
    switch (status) {
        case 'pending_review': return 'warning';
        case 'approved': return 'success';
        case 'rejected': return 'danger';
        default: return 'info';
    }
};

const getNotificationStatusSeverity = (status) => {
    switch (status) {
        case 'sent': return 'success';
        case 'pending': return 'warning';
        case 'failed': return 'danger';
        default: return 'info';
    }
};

const canEscalate = (case_) => {
    const hasPermission = authStore.isL1Analyst || authStore.isAdmin;
    return hasPermission && case_.level === 'L1' && case_.status !== 'approved' && case_.status !== 'rejected';
};

const canApprove = (case_) => {
    const hasPermission = authStore.hasPermission('approve');
    return hasPermission && case_.status !== 'approved' && case_.status !== 'rejected';
};

// ===== NEW METHODS FOR ENHANCED UI =====

// Format role for display
const formatRole = (role) => {
    const roleMap = {
        'admin': 'Administrator',
        'l1_analyst': 'L1 Analyst',
        'l2_analyst': 'L2 Analyst'
    };
    return roleMap[role] || role;
};

// Quick filter methods
const toggleQuickFilter = (filter) => {
    filter.active = !filter.active;
    // Apply filter logic here
    console.log('Quick filter toggled:', filter);
};

// Enhanced filter methods
const hasActiveFilters = computed(() => {
    return selectedStatus.value || selectedPriority.value || 
           selectedLevel.value || selectedCrypto.value || 
           searchTerm.value || dateRange.value ||
           selectedAssignees.value?.length > 0;
});

const activeFiltersCount = computed(() => {
    let count = 0;
    if (selectedStatus.value) count++;
    if (selectedPriority.value) count++;
    if (selectedLevel.value) count++;
    if (selectedCrypto.value) count++;
    if (searchTerm.value) count++;
    if (dateRange.value) count++;
    if (selectedAssignees.value?.length > 0) count++;
    return count;
});

const activeFiltersList = computed(() => {
    const filters = [];
    if (selectedStatus.value) filters.push({ id: 'status', label: `Status: ${selectedStatus.value.label}` });
    if (selectedPriority.value) filters.push({ id: 'priority', label: `Priority: ${selectedPriority.value.label}` });
    if (selectedLevel.value) filters.push({ id: 'level', label: `Level: ${selectedLevel.value.label}` });
    if (selectedCrypto.value) filters.push({ id: 'crypto', label: `Crypto: ${selectedCrypto.value.label}` });
    if (searchTerm.value) filters.push({ id: 'search', label: `Search: ${searchTerm.value}` });
    return filters;
});

const clearAllFilters = () => {
    selectedStatus.value = null;
    selectedPriority.value = null;
    selectedLevel.value = null;
    selectedCrypto.value = null;
    selectedAssignees.value = [];
    searchTerm.value = '';
    dateRange.value = null;
    amountRange.value = { min: null, max: null };
    riskScoreRange.value = [0, 100];
    selectedSources.value = [];
    selectedTags.value = [];
};

const removeFilter = (filter) => {
    switch (filter.id) {
        case 'status':
            selectedStatus.value = null;
            break;
        case 'priority':
            selectedPriority.value = null;
            break;
        case 'level':
            selectedLevel.value = null;
            break;
        case 'crypto':
            selectedCrypto.value = null;
            break;
        case 'search':
            searchTerm.value = '';
            break;
    }
};

const saveCurrentFilter = () => {
    console.log('Save current filter configuration');
    // Implementation for saving filter presets
};

// Search methods
const performSearch = () => {
    console.log('Performing search:', searchTerm.value);
    showSearchSuggestions.value = false;
};

const clearSearch = () => {
    searchTerm.value = '';
    showSearchSuggestions.value = false;
};

const selectSuggestion = (suggestion) => {
    searchTerm.value = suggestion.text;
    showSearchSuggestions.value = false;
    performSearch();
};

// Date preset methods
const applyDatePreset = (preset) => {
    const today = new Date();
    let startDate, endDate = today;
    
    switch (preset.value) {
        case 'today':
            startDate = today;
            break;
        case '7d':
            startDate = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
            break;
        case '30d':
            startDate = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000);
            break;
        case 'month':
            startDate = new Date(today.getFullYear(), today.getMonth(), 1);
            break;
    }
    
    dateRange.value = [startDate, endDate];
};

// Stats card filter methods
const filterByStatus = (status) => {
    selectedStatus.value = statusOptions.find(opt => opt.value === status);
};

const filterByPriority = (priority) => {
    selectedPriority.value = priorityOptions.find(opt => opt.value === priority);
};

const filterByType = (type) => {
    console.log('Filter by type:', type);
};

// Analytics methods
const showCompletionAnalytics = () => {
    console.log('Show completion analytics');
};

const showTimeAnalytics = () => {
    console.log('Show time analytics');
};

// Enhanced action methods
const bulkImport = () => {
    console.log('Bulk import cases');
};

const showAdvancedFiltersDialog = () => {
    console.log('Show advanced filters');
};

const showAnalytics = () => {
    console.log('Show analytics dashboard');
};

const bulkActions = () => {
    console.log('Show bulk actions menu');
};

const automatedRules = () => {
    console.log('Configure automated rules');
};

// Crypto icon helper
const getCryptoIcon = (crypto) => {
    const iconMap = {
        'BTC': 'pi pi-bitcoin',
        'ETH': 'pi pi-ethereum',
        'USDT': 'pi pi-dollar',
        'USDC': 'pi pi-dollar'
    };
    return iconMap[crypto] || 'pi pi-money-bill';
};

// Updated status options with counts
const statusOptions = computed(() => [
    { label: 'New', value: 'new', count: cases.value.filter(c => c.status === 'new').length },
    { label: 'In Review', value: 'in_review', count: cases.value.filter(c => c.status === 'in_review').length },
    { label: 'Pending Documents', value: 'pending_docs', count: cases.value.filter(c => c.status === 'pending_docs').length },
    { label: 'Escalated', value: 'escalated', count: cases.value.filter(c => c.status === 'escalated').length },
    { label: 'Approved', value: 'approved', count: cases.value.filter(c => c.status === 'approved').length },
    { label: 'Rejected', value: 'rejected', count: cases.value.filter(c => c.status === 'rejected').length }
]);

// Updated crypto options with counts
const cryptoOptions = computed(() => {
    const cryptos = [...new Set(cases.value.map(c => c.crypto))];
    return cryptos.map(crypto => ({ 
        label: crypto, 
        value: crypto,
        count: cases.value.filter(c => c.crypto === crypto).length 
    }));
});

// ----- Sorting state & helpers (JS only) -----
const sort = ref({ key: 'created_at', dir: 'desc' }) // dir: 'asc' | 'desc'

function sortBy(key) {
  if (sort.value.key === key) {
    sort.value.dir = sort.value.dir === 'asc' ? 'desc' : 'asc'
  } else {
    sort.value.key = key
    sort.value.dir = 'asc'
  }
}
function goDetail(id) {
  router.push(`/monitoring/cases/${id}`)
}

function valFor(row, key) {
  if (key === 'amount') {
    const n = parseFloat(String(row.amount ?? '').replace(/[^\d.]/g, ''))
    return Number.isFinite(n) ? n : -Infinity
  }
  if (key === 'created_at') {
    const t = new Date(row.created_at || row.createdAt || row.date || 0).getTime()
    return Number.isFinite(t) ? t : 0
  }
  const v = row?.[key]
  return typeof v === 'string' ? v.toLowerCase() : (v ?? '')
}

const sortedRows = computed(() => {
  const arr = Array.isArray(filteredCases.value) ? [...filteredCases.value] : []
  const { key, dir } = sort.value
  arr.sort((a, b) => {
    const av = valFor(a, key)
    const bv = valFor(b, key)
    if (av < bv) return dir === 'asc' ? -1 : 1
    if (av > bv) return dir === 'asc' ? 1 : -1
    return 0
  })
  return arr
})

// Ikon indikator sort untuk header
const SortIcon = {
  name: 'SortIcon',
  props: { active: Boolean, dir: { type: String, default: 'asc' } },
  template: `
    <span class="inline-block align-middle ml-1">
      <svg v-if="active && dir==='asc'" xmlns="http://www.w3.org/2000/svg" class="w-3 h-3 inline" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M14.707 10.293a1 1 0 01-1.414 0L10 6.999 6.707 10.293A1 1 0 015.293 8.88l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z" clip-rule="evenodd"/>
      </svg>
      <svg v-else-if="active && dir==='desc'" xmlns="http://www.w3.org/2000/svg" class="w-3 h-3 inline" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M5.293 9.707a1 1 0 011.414 0L10 12.999l3.293-3.292a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"/>
      </svg>
      <svg v-else xmlns="http://www.w3.org/2000/svg" class="w-3 h-3 inline opacity-30" viewBox="0 0 20 20" fill="currentColor">
        <path d="M7 7l3-3 3 3H7zM13 13l-3 3-3-3h6z"/>
      </svg>
    </span>
  `
}
const showCreateModal = ref(false)
const creating = ref(false)
const createError = ref('')

const severityOptions   = ['LOW','MEDIUM','HIGH','CRITICAL']
const priorityOptions   = ['P1','P2','P3','P4']
const tlpOptions        = ['WHITE','GREEN','AMBER','RED']
const visibilityOptions = ['internal','external']

const caseForm = ref({
  type: null,            // 'wallet' | 'transaction'
  reference_id: '',
  title: '',
  severity: 'MEDIUM',
  priority: 'P3',
  typology: '',
  reason: '',
  notes: '',
  tags: [],
  tlp: 'GREEN',
  visibility: 'internal',
  sla_due_at: null,      // Date object dari Calendar
  assignToMe: true
})

const isValidCreate = computed(() =>
  !!caseForm.value.type &&
  !!caseForm.value.reference_id &&
  severityOptions.includes(caseForm.value.severity) &&
  priorityOptions.includes(caseForm.value.priority) &&
  tlpOptions.includes(caseForm.value.tlp) &&
  visibilityOptions.includes(caseForm.value.visibility)
)

function resetCreateForm () {
  caseForm.value = {
    type: null,
    reference_id: '',
    title: '',
    severity: 'MEDIUM',
    priority: 'P3',
    typology: '',
    reason: '',
    notes: '',
    tags: [],
    tlp: 'GREEN',
    visibility: 'internal',
    sla_due_at: null,
    assignToMe: true
  }
  createError.value = ''
}

async function onCreateCase() {
  createError.value = ''
  if (!isValidCreate.value) {
    createError.value = 'Lengkapi field wajib (Type, Reference ID, Severity, Priority, TLP, Visibility).'
    return
  }
  creating.value = true
  try {
    const slaISO = caseForm.value.sla_due_at
      ? new Date(caseForm.value.sla_due_at).toISOString()
      : undefined

    const common = {
      title: caseForm.value.title || undefined,
      priority: caseForm.value.priority,
      typology: caseForm.value.typology || undefined,
      severity: caseForm.value.severity,
      reason: caseForm.value.reason || undefined,
      tags: (caseForm.value.tags?.length ? caseForm.value.tags : undefined),
      tlp: caseForm.value.tlp,
      visibility: caseForm.value.visibility,
      sla_due_at: slaISO,
      // catatan awal ikut ke payload
      payload: { notes: caseForm.value.notes || undefined }
    }

    let res
    if (caseForm.value.assignToMe) {
      // assign ke user saat ini
      res = await createCase({
        type: caseForm.value.type,
        reference_id: caseForm.value.reference_id,
        assignToMe: true,
        ...common
      })
    } else {
      // fallback lain bila tidak auto-assign (opsional, sama seperti CryptoMonitoring.vue)
      res = await api.assignEntityToCase({
        entity_type: caseForm.value.type === 'transaction' ? 'tx' : 'wallet',
        entity_key: caseForm.value.reference_id,
        ...common
      })
    }

    const newId = res?.case_id || res?.id
    toast.add({ severity: 'success', summary: 'Case created', detail: `ID: ${newId}`, life: 2500 })
    showCreateModal.value = false
    resetCreateForm()
    router.push(`/monitoring/cases/${newId}`)
  } catch (e) {
    createError.value = e?.data?.message || e?.message || 'Create Case failed'
    toast.add({ severity: 'error', summary: 'Failed', detail: createError.value, life: 3000 })
  } finally {
    creating.value = false
  }
}

function mapRow(c) {
  const p = c?.payload || {}
  const ref = c?.reference_id || p?.wallet || p?.address || ''
  const crypto = p?.chain || p?.network || (String(ref||'').startsWith('0x') ? 'ETH' : 'BTC')
  const amount = (p?.amount != null) ? `${p.amount} ${crypto}` : null
  return {
    id: c.id,
    wallet: p?.wallet || ref,
    crypto,
    amount,
    level: p?.level || c.level || 'L1',
    status: c.status,
    priority: c.priority || p?.priority || null,
    assigned_to: c.owner_id ? `Owner #${c.owner_id}` : (c.assignee || 'Unassigned'),
    created_at: c.created_at,
    owner_id: c.owner_id ?? null,
    assignments: Array.isArray(c.assignments) ? c.assignments : [], // <— penting
    raw: c
  }
}

async function fetchAllCases() {
  loading.value = true
  try {
    // backend-mu sudah punya GET /cases yang mengembalikan list
    const res = await api.request('/cases', { method: 'GET' })
    const list = Array.isArray(res) ? res : (res?.items || [])
    cases.value = list.map(mapRow)
  } catch (e) {
    toast.add({ severity: 'warn', summary: 'Cases', detail: e?.message || 'Load failed', life: 2500 })
  } finally {
    loading.value = false
  }
}

function openDetail(row) {
  router.push(`/monitoring/cases/${row.id}`)
}

// Lifecycle
onMounted(fetchAllCases)
</script>

<style scoped>
/* Page Header Styling */
.page-header {
    background: linear-gradient(135deg, var(--surface-card) 0%, var(--surface-ground) 100%);
    border: 1px solid var(--surface-border);
    border-radius: 12px;
    margin-bottom: 2rem;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.header-content {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    padding: 2rem;
    gap: 2rem;
}

/* Title Section */
.title-section {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    flex: 1;
}

.title-wrapper {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.header-icon {
    font-size: 2.5rem;
    color: var(--primary-color);
    background: var(--primary-50);
    padding: 1rem;
    border-radius: 12px;
    border: 2px solid var(--primary-100);
}

.title-text {
    flex: 1;
}

.page-title {
    margin: 0;
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-color);
    line-height: 1.2;
}

.page-subtitle {
    margin: 0.5rem 0 0 0;
    color: var(--text-color-secondary);
    font-size: 1rem;
    font-weight: 500;
}

/* Stats Summary */
.stats-summary {
    display: flex;
    gap: 2rem;
}

.quick-stat {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 1rem 1.5rem;
    background: var(--surface-card);
    border: 1px solid var(--surface-border);
    border-radius: 8px;
    min-width: 100px;
    transition: all 0.3s ease;
}

.quick-stat:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.quick-stat.urgent {
    border-color: var(--red-200);
    background: var(--red-50);
}

.stat-number {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--primary-color);
    line-height: 1;
}

.quick-stat.urgent .stat-number {
    color: var(--red-500);
}

.stat-label {
    font-size: 0.75rem;
    color: var(--text-color-secondary);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 0.25rem;
}

/* Action Section */
.action-section {
    display: flex;
    align-items: center;
    gap: 1.5rem;
}

.action-buttons {
    display: flex;
    gap: 0.75rem;
}

/* Notification Button */
.notification-btn {
    position: relative;
    transition: all 0.3s ease;
}

.notification-btn.has-notifications {
    animation: pulse 2s infinite;
}

.notification-icon-wrapper {
    position: relative;
    display: inline-block;
}

.notification-badge {
    position: absolute;
    top: -8px;
    right: -8px;
    background: var(--red-500);
    color: white;
    font-size: 0.7rem;
    font-weight: 700;
    padding: 0.2rem 0.4rem;
    border-radius: 10px;
    min-width: 18px;
    height: 18px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 2px solid var(--surface-card);
}

/* Primary Action Button */
.primary-action-btn {
    background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-600) 100%);
    border: none;
    font-weight: 600;
    padding: 0.75rem 1.5rem;
    transition: all 0.3s ease;
}

.primary-action-btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(var(--primary-color-rgb), 0.3);
}

/* User Info */
.user-info {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
    background: var(--surface-card);
    border: 1px solid var(--surface-border);
    border-radius: 8px;
    transition: all 0.3s ease;
}

.user-info:hover {
    background: var(--surface-hover);
}

.user-avatar {
    border: 2px solid var(--surface-border);
}

.user-details {
    display: flex;
    flex-direction: column;
}

.user-name {
    font-weight: 600;
    color: var(--text-color);
    font-size: 0.9rem;
}

.user-role {
    font-size: 0.75rem;
    color: var(--text-color-secondary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Quick Actions Bar */
.quick-actions-bar {
    background: var(--surface-ground);
    border-top: 1px solid var(--surface-border);
    padding: 1rem 2rem;
}

.quick-actions-content {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.quick-actions-label {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--text-color-secondary);
    white-space: nowrap;
}

.quick-action-items {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
}

.quick-action-item {
    font-size: 0.875rem;
    padding: 0.5rem 0.75rem;
    border-radius: 6px;
    transition: all 0.2s ease;
}

.quick-action-item:hover {
    background: var(--surface-hover);
    color: var(--primary-color);
}

/* Table Styling */
.wallet-cell {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.amount-cell {
    text-align: right;
}

.date-cell {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.action-btn {
    transition: all 0.2s ease;
}

.action-btn:hover {
    transform: scale(1.1);
}

/* Filter Section */
.filter-section {
    border: 1px solid var(--surface-border);
}

.filter-group {
    min-width: 150px;
}

/* Case Details Dialog */
.case-details-dialog :deep(.p-dialog-content) {
    padding: 0;
}

.case-tabs :deep(.p-tabview-panels) {
    padding: 1rem 0;
}

.timeline-content {
    margin-left: 1rem;
}

.note-item {
    border-left: 3px solid var(--primary-color);
}

.stakeholder-item {
    transition: all 0.2s ease;
}

.stakeholder-item:hover {
    background: var(--surface-hover);
}

/* Animations */
@keyframes pulse {
    0% {
        box-shadow: 0 0 0 0 rgba(var(--red-500-rgb), 0.7);
    }
    70% {
        box-shadow: 0 0 0 10px rgba(var(--red-500-rgb), 0);
    }
    100% {
        box-shadow: 0 0 0 0 rgba(var(--red-500-rgb), 0);
    }
}

/* Responsive Design */
@media (max-width: 1024px) {
    .header-content {
        flex-direction: column;
        align-items: stretch;
        gap: 1.5rem;
    }
    
    .title-section {
        align-items: center;
        text-align: center;
    }
    
    .stats-summary {
        justify-content: center;
    }
    
    .action-section {
        justify-content: center;
        flex-wrap: wrap;
    }
}

@media (max-width: 768px) {
    .header-content {
        padding: 1.5rem;
    }
    
    .title-wrapper {
        flex-direction: column;
        text-align: center;
        gap: 0.75rem;
    }
    
    .header-icon {
        font-size: 2rem;
        padding: 0.75rem;
    }
    
    .page-title {
        font-size: 1.5rem;
    }
    
    .stats-summary {
        flex-direction: column;
        gap: 1rem;
        width: 100%;
    }
    
    .quick-stat {
        flex-direction: row;
        justify-content: space-between;
        align-items: center;
        text-align: left;
    }
    
    .action-buttons {
        flex-direction: column;
        width: 100%;
    }
    
    .action-buttons .p-button {
        width: 100%;
        justify-content: center;
    }
    
    .quick-actions-bar {
        padding: 1rem 1.5rem;
    }
    
    .quick-actions-content {
        flex-direction: column;
        align-items: stretch;
        gap: 0.75rem;
    }
    
    .quick-action-items {
        justify-content: center;
    }
}

@media (max-width: 480px) {
    .user-info {
        flex-direction: column;
        text-align: center;
        padding: 1rem;
    }
    
    .notification-btn :deep(.p-button-label) {
        display: none;
    }
    
    .quick-action-item :deep(.p-button-label) {
        display: none;
    }
    
    .filter-section {
        padding: 1rem;
    }
    
    .filter-group {
        min-width: 100%;
    }
    
    .wallet-cell {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.25rem;
    }
}

/* Dark Mode Adjustments */
@media (prefers-color-scheme: dark) {
    .page-header {
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    .quick-stat:hover {
        box-shadow: 0 4px 12px rgba(255, 255, 255, 0.1);
    }
    
    .primary-action-btn:hover {
        box-shadow: 0 6px 20px rgba(255, 255, 255, 0.2);
    }
}

/* Loading States */
.p-datatable.p-datatable-loading .p-datatable-tbody > tr > td {
    background: var(--surface-ground);
}

/* API Error Banner */
.api-error-banner {
    animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
    from {
        opacity: 0;
        transform: translateY(-10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Stats Cards */
.stats-card {
    transition: all 0.3s ease;
    cursor: pointer;
}

.stats-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

/* Table Container */
.table-container {
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid var(--surface-border);
}

.case-table :deep(.p-datatable-header) {
    background: var(--surface-section);
    border-bottom: 2px solid var(--surface-border);
}

.case-table :deep(.p-datatable-thead > tr > th) {
    background: var(--surface-section);
    color: var(--text-color);
    font-weight: 600;
    padding: 1rem;
    border-bottom: 1px solid var(--surface-border);
}

.case-table :deep(.p-datatable-tbody > tr) {
    transition: all 0.2s ease;
}

.case-table :deep(.p-datatable-tbody > tr:hover) {
    background: var(--surface-hover);
}

.case-table :deep(.p-datatable-tbody > tr > td) {
    padding: 1rem;
    border-bottom: 1px solid var(--surface-border);
}

/* Case Title Cell */
.case-title-cell {
    max-width: 300px;
}

.case-title-cell .font-medium {
    display: -webkit-box;
    -webkit-line-clamp: 1;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.case-title-cell .text-600 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

/* Sidebar Content */
.sidebar-content {
    position: sticky;
    top: 2rem;
}

.info-item {
    transition: all 0.2s ease;
}

.info-item:hover {
    background: var(--surface-hover);
    padding: 0.5rem;
    border-radius: 4px;
    margin: -0.5rem;
}

/* Custom Timeline */
.custom-timeline :deep(.p-timeline-event-content) {
    margin-left: 1rem;
}

.custom-timeline :deep(.p-timeline-event-marker) {
    background: var(--primary-color);
    border: 2px solid var(--surface-card);
}

.custom-timeline :deep(.p-timeline-event-connector) {
    background: var(--surface-border);
}

/* Utility Classes */
.font-mono {
    font-family: 'Courier New', Courier, monospace;
}

.cursor-pointer {
    cursor: pointer;
}

.cursor-pointer:hover {
    text-decoration: underline;
}

/* Print Styles */
@media print {
    .page-header,
    .quick-actions-bar,
    .action-buttons,
    .p-paginator {
        display: none !important;
    }
    
    .case-table {
        font-size: 0.8rem;
    }
    
    .case-table :deep(.p-datatable-tbody > tr > td) {
        padding: 0.5rem;
    }
}

/* ===== MODERN UI REDESIGN STYLES ===== */

/* Modern Header Styles */
.case-management-header {
    background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    border-radius: 16px;
    margin-bottom: 2rem;
    box-shadow: 
        0 1px 3px rgba(0, 0, 0, 0.05),
        0 4px 16px rgba(0, 0, 0, 0.08);
    border: 1px solid rgba(226, 232, 240, 0.6);
    overflow: hidden;
    backdrop-filter: blur(10px);
}

.header-main {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    padding: 2rem 2.5rem;
    gap: 2rem;
}

.header-left {
    display: flex;
    flex-direction: column;
    gap: 2rem;
    flex: 1;
}

.title-section {
    display: flex;
    align-items: center;
    gap: 1.5rem;
}

.icon-container {
    position: relative;
}

.header-icon-wrapper {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 4rem;
    height: 4rem;
    background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-600) 100%);
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(var(--primary-color-rgb), 0.3);
}

.header-icon {
    font-size: 1.75rem;
    color: white;
    z-index: 2;
}

.icon-glow {
    position: absolute;
    top: -2px;
    left: -2px;
    right: -2px;
    bottom: -2px;
    background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-600) 100%);
    border-radius: 18px;
    opacity: 0.3;
    filter: blur(8px);
    z-index: 1;
}

.title-content {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.page-title {
    font-size: 2.5rem;
    font-weight: 800;
    color: #1e293b;
    margin: 0;
    line-height: 1.1;
    background: linear-gradient(135deg, #1e293b 0%, #475569 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.page-subtitle {
    font-size: 1.1rem;
    color: #64748b;
    margin: 0;
    font-weight: 500;
}

/* Header Stats */
.header-stats {
    display: flex;
    gap: 1rem;
    margin-top: 1rem;
}

.stat-card {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem 1.25rem;
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(226, 232, 240, 0.6);
    border-radius: 12px;
    transition: all 0.3s ease;
    cursor: pointer;
    min-width: 140px;
}

.stat-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
    background: rgba(255, 255, 255, 0.95);
}

.stat-icon {
    font-size: 1.25rem;
    color: var(--primary-color);
}

.stat-icon.urgent {
    color: #ef4444;
}

.stat-icon.success {
    color: #10b981;
}

.stat-content {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.stat-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: #1e293b;
    line-height: 1;
}

.stat-value.urgent {
    color: #ef4444;
}

.stat-label {
    font-size: 0.75rem;
    color: #64748b;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.stat-trend {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    font-size: 0.7rem;
    font-weight: 600;
}

.stat-trend.positive {
    color: #10b981;
}

.stat-trend.negative {
    color: #ef4444;
}

/* Header Actions */
.header-actions {
    display: flex;
    align-items: flex-start;
    gap: 2rem;
}

.action-group {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.action-item {
    display: flex;
    align-items: center;
}

.modern-notification-btn {
    width: 2.75rem;
    height: 2.75rem;
    border-radius: 12px;
    border: 1px solid rgba(226, 232, 240, 0.6);
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
    position: relative;
}

.modern-notification-btn:hover {
    background: rgba(255, 255, 255, 1);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.modern-notification-btn.has-notifications {
    animation: notificationPulse 2s infinite;
}

.notification-container {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
}

.notification-indicator {
    position: absolute;
    top: -8px;
    right: -8px;
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
    color: white;
    font-size: 0.65rem;
    font-weight: 700;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 2px solid white;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.action-button {
    border-radius: 12px;
    padding: 0.75rem 1rem;
    font-weight: 600;
    transition: all 0.3s ease;
}

.modern-primary-btn {
    background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-600) 100%);
    border: none;
    border-radius: 12px;
    padding: 0.75rem 1.5rem;
    font-weight: 600;
    color: white;
    box-shadow: 0 4px 12px rgba(var(--primary-color-rgb), 0.3);
    transition: all 0.3s ease;
}

.modern-primary-btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(var(--primary-color-rgb), 0.4);
}

/* User Profile */
.user-profile {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.75rem 1rem;
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(226, 232, 240, 0.6);
    border-radius: 12px;
    transition: all 0.3s ease;
}

.user-profile:hover {
    background: rgba(255, 255, 255, 1);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.profile-info {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 0.25rem;
}

.user-name {
    font-weight: 600;
    color: #1e293b;
    font-size: 0.9rem;
}

.user-role {
    font-size: 0.75rem;
    color: #64748b;
    font-weight: 500;
}

.profile-avatar {
    position: relative;
}

.modern-avatar {
    border: 2px solid rgba(226, 232, 240, 0.6);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.status-indicator {
    position: absolute;
    bottom: 0;
    right: 0;
    width: 0.75rem;
    height: 0.75rem;
    border-radius: 50%;
    border: 2px solid white;
}

.status-indicator.online {
    background: #10b981;
}

/* Quick Actions Panel */
.quick-actions-panel {
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    border-top: 1px solid rgba(226, 232, 240, 0.6);
    padding: 1.5rem 2.5rem;
}

.actions-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 1rem;
}

.action-card {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem;
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(226, 232, 240, 0.6);
    border-radius: 12px;
    transition: all 0.3s ease;
    cursor: pointer;
}

.action-card:hover {
    background: rgba(255, 255, 255, 1);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.action-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 2.5rem;
    height: 2.5rem;
    background: linear-gradient(135deg, var(--primary-50) 0%, var(--primary-100) 100%);
    color: var(--primary-color);
    border-radius: 10px;
    font-size: 1.1rem;
}

.action-text {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.action-title {
    font-weight: 600;
    color: #1e293b;
    font-size: 0.875rem;
}

.action-desc {
    font-size: 0.75rem;
    color: #64748b;
}

/* ===== ENHANCED STATISTICS DASHBOARD ===== */

.stats-dashboard {
    margin-bottom: 2rem;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.5rem;
    margin-bottom: 1rem;
}

.modern-stat-card {
    background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    border: 1px solid rgba(226, 232, 240, 0.6);
    border-radius: 16px;
    padding: 1.5rem;
    transition: all 0.3s ease;
    cursor: pointer;
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(10px);
    box-shadow: 
        0 1px 3px rgba(0, 0, 0, 0.05),
        0 4px 16px rgba(0, 0, 0, 0.08);
}

.modern-stat-card:hover {
    transform: translateY(-4px);
    box-shadow: 
        0 4px 16px rgba(0, 0, 0, 0.12),
        0 8px 32px rgba(0, 0, 0, 0.08);
}

.modern-stat-card.urgent {
    border-color: rgba(239, 68, 68, 0.3);
    background: linear-gradient(135deg, #fef2f2 0%, #ffffff 100%);
}

.stat-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}

.stat-icon-wrapper {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 2.5rem;
    height: 2.5rem;
    background: linear-gradient(135deg, var(--primary-50) 0%, var(--primary-100) 100%);
    border-radius: 10px;
    color: var(--primary-color);
}

.stat-icon-wrapper.urgent {
    background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
    color: #ef4444;
}

.stat-icon-wrapper.success {
    background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
    color: #10b981;
}

.stat-icon {
    font-size: 1.25rem;
}

.stat-actions {
    opacity: 0;
    transition: opacity 0.3s ease;
}

.modern-stat-card:hover .stat-actions {
    opacity: 1;
}

.stat-content {
    margin-bottom: 1rem;
}

.stat-main {
    display: flex;
    align-items: baseline;
    gap: 0.75rem;
    margin-bottom: 0.5rem;
}

.stat-number {
    font-size: 2rem;
    font-weight: 800;
    color: #1e293b;
    line-height: 1;
}

.stat-number.urgent {
    color: #ef4444;
}

.stat-change {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.25rem 0.5rem;
    border-radius: 6px;
}

.stat-change.positive {
    background: #f0fdf4;
    color: #10b981;
}

.stat-change.negative {
    background: #fef2f2;
    color: #ef4444;
}

.stat-change.neutral {
    background: #f8fafc;
    color: #64748b;
}

.stat-change.urgent {
    background: #fef2f2;
    color: #ef4444;
}

.stat-label {
    font-weight: 600;
    color: #1e293b;
    font-size: 0.875rem;
    margin-bottom: 0.25rem;
}

.stat-sublabel {
    font-size: 0.75rem;
    color: #64748b;
}

/* Mini Charts */
.stat-chart {
    height: 40px;
    display: flex;
    align-items: end;
    gap: 2px;
}

.mini-chart {
    display: flex;
    align-items: end;
    gap: 2px;
    width: 100%;
    height: 100%;
}

.chart-bar {
    flex: 1;
    background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-600) 100%);
    border-radius: 2px 2px 0 0;
    transition: all 0.3s ease;
    opacity: 0.7;
}

.l1-chart .chart-bar {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
}

.l2-chart .chart-bar {
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.anomaly-chart .chart-bar {
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

.blacklist-chart .chart-bar {
    background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
}

.modern-stat-card:hover .chart-bar {
    opacity: 1;
}

/* Progress Ring */
.progress-ring {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 40px;
}

.progress-ring-svg {
    transform: rotate(-90deg);
}

.progress-ring-circle {
    transition: stroke-dashoffset 0.35s;
    transform-origin: 50% 50%;
}

/* Time Visualization */
.time-visualization {
    height: 40px;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.time-segments {
    display: flex;
    height: 20px;
    border-radius: 6px;
    overflow: hidden;
}

.time-segment {
    height: 100%;
    transition: all 0.3s ease;
}

.time-labels {
    display: flex;
    justify-content: space-between;
    font-size: 0.65rem;
    color: #64748b;
    font-weight: 500;
}

/* ===== ENHANCED FILTERS PANEL ===== */

.filters-panel {
    background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    border: 1px solid rgba(226, 232, 240, 0.6);
    border-radius: 16px;
    margin-bottom: 2rem;
    overflow: hidden;
    backdrop-filter: blur(10px);
    box-shadow: 
        0 1px 3px rgba(0, 0, 0, 0.05),
        0 4px 16px rgba(0, 0, 0, 0.08);
}

.filters-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem 2rem;
    border-bottom: 1px solid rgba(226, 232, 240, 0.6);
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
}

.filters-title .title {
    font-size: 1.25rem;
    font-weight: 700;
    color: #1e293b;
    margin: 0 0 0.25rem 0;
}

.filters-title .subtitle {
    font-size: 0.875rem;
    color: #64748b;
    margin: 0;
}

.filters-actions {
    display: flex;
    gap: 0.75rem;
}

/* Quick Filter Pills */
.quick-filters {
    padding: 1rem 2rem;
    border-bottom: 1px solid rgba(226, 232, 240, 0.4);
    background: rgba(248, 250, 252, 0.5);
}

.quick-filters-label {
    font-size: 0.875rem;
    font-weight: 600;
    color: #64748b;
    margin-right: 1rem;
}

.filter-pills {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
    margin-top: 0.5rem;
}

.filter-pill {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 0.75rem;
    background: rgba(255, 255, 255, 0.8);
    border: 1px solid rgba(226, 232, 240, 0.6);
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s ease;
    font-size: 0.875rem;
}

.filter-pill:hover {
    background: rgba(255, 255, 255, 1);
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.filter-pill.active {
    background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-600) 100%);
    color: white;
    border-color: var(--primary-color);
}

.filter-count {
    background: rgba(0, 0, 0, 0.1);
    color: inherit;
    padding: 0.125rem 0.375rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
}

.filter-pill.active .filter-count {
    background: rgba(255, 255, 255, 0.2);
}

/* Main Filters */
.main-filters {
    padding: 2rem;
}

/* Search Container */
.search-container {
    position: relative;
    margin-bottom: 2rem;
}

.search-input-wrapper {
    position: relative;
    display: flex;
    align-items: center;
}

.search-icon {
    position: absolute;
    left: 1rem;
    color: #64748b;
    z-index: 2;
}

.smart-search-input {
    width: 100%;
    padding: 0.875rem 1rem 0.875rem 2.5rem;
    border: 1px solid rgba(226, 232, 240, 0.8);
    border-radius: 12px;
    font-size: 0.9rem;
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
}

.smart-search-input:focus {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(var(--primary-color-rgb), 0.1);
    background: rgba(255, 255, 255, 1);
}

.clear-search-btn {
    position: absolute;
    right: 0.5rem;
    z-index: 2;
}

/* Search Suggestions */
.search-suggestions {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: white;
    border: 1px solid rgba(226, 232, 240, 0.8);
    border-radius: 8px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
    z-index: 1000;
    max-height: 200px;
    overflow-y: auto;
}

.search-suggestion {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
    cursor: pointer;
    transition: background 0.2s ease;
}

.search-suggestion:hover {
    background: #f8fafc;
}

.suggestion-text {
    flex: 1;
    font-weight: 500;
}

.suggestion-type {
    font-size: 0.75rem;
    color: #64748b;
    background: #f1f5f9;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
}

/* Filter Controls */
.filter-controls {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.filter-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    align-items: end;
}

.filter-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.filter-label {
    font-weight: 600;
    color: #374151;
    font-size: 0.875rem;
}

.modern-multiselect,
.modern-dropdown,
.modern-calendar {
    border-radius: 8px;
    border: 1px solid rgba(226, 232, 240, 0.8);
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
}

.modern-multiselect:focus-within,
.modern-dropdown:focus-within,
.modern-calendar:focus-within {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(var(--primary-color-rgb), 0.1);
}

/* Filter Options */
.filter-option {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.option-tag {
    font-size: 0.75rem;
}

.option-count {
    font-size: 0.75rem;
    color: #64748b;
    margin-left: auto;
}

/* Crypto Options */
.crypto-option {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.crypto-icon {
    width: 1.5rem;
    height: 1.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #f1f5f9;
    border-radius: 4px;
}

.crypto-name {
    flex: 1;
    font-weight: 500;
}

.crypto-count {
    font-size: 0.75rem;
    color: #64748b;
}

/* Assignee Options */
.assignee-option {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.assignee-name {
    font-weight: 500;
}

.assignee-role {
    font-size: 0.75rem;
    color: #64748b;
}

/* Date and Amount Filters */
.date-filter-container,
.amount-filter-container {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.date-presets {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
}

.date-preset-btn {
    font-size: 0.75rem;
    padding: 0.375rem 0.75rem;
    border-radius: 6px;
}

.amount-inputs {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.amount-input {
    flex: 1;
}

.amount-separator {
    color: #64748b;
    font-weight: 500;
}

/* Level Selector */
.level-selector {
    display: flex;
    gap: 0.5rem;
}

/* Advanced Filters */
.advanced-toggle {
    text-align: center;
    padding: 1rem 0;
    border-top: 1px solid rgba(226, 232, 240, 0.4);
}

.advanced-filters {
    border-top: 1px solid rgba(226, 232, 240, 0.4);
    padding-top: 1.5rem;
}

.advanced-filters-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}

.advanced-filters-header h5 {
    margin: 0;
    color: #374151;
    font-weight: 600;
}

.advanced-controls {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
}

/* Risk Score Slider */
.risk-score-slider {
    margin: 1rem 0;
}

.slider-labels {
    display: flex;
    justify-content: space-between;
    font-size: 0.875rem;
    color: #64748b;
    font-weight: 500;
}

/* Active Filters */
.active-filters {
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    border-top: 1px solid rgba(226, 232, 240, 0.6);
    padding: 1rem 2rem;
}

.active-filters-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
}

.active-count {
    font-size: 0.875rem;
    font-weight: 600;
    color: #374151;
}

.active-filter-tags {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
}

.active-filter-tag {
    font-size: 0.75rem;
}

/* Animations */
@keyframes notificationPulse {
    0% {
        box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4);
    }
    70% {
        box-shadow: 0 0 0 8px rgba(239, 68, 68, 0);
    }
    100% {
        box-shadow: 0 0 0 0 rgba(239, 68, 68, 0);
    }
}
</style>
