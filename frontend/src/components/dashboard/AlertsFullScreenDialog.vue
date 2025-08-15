<script setup>
import Badge from 'primevue/badge';
import Button from 'primevue/button';
import Checkbox from 'primevue/checkbox';
import Dialog from 'primevue/dialog';
import Divider from 'primevue/divider';
import Dropdown from 'primevue/dropdown';
import InputText from 'primevue/inputtext';
import ProgressBar from 'primevue/progressbar';
import { computed, defineEmits, defineProps, ref, watch } from 'vue';

const props = defineProps({
  alerts: {
    type: Array,
    required: true
  },
  isOpen: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['close', 'dismiss-alert', 'clear-all', 'mark-all-read']);

const searchQuery = ref('');
const selectedFilter = ref('all');
const sortBy = ref('timestamp');
const sortOrder = ref('desc');
const selectedAlerts = ref(new Set());

const filterOptions = [
  { value: 'all', label: 'All Alerts', count: 0 },
  { value: 'critical', label: 'Critical', count: 0 },
  { value: 'high', label: 'High Priority', count: 0 },
  { value: 'medium', label: 'Medium', count: 0 },
  { value: 'unread', label: 'Unread', count: 0 }
];

const sortOptions = [
  { value: 'timestamp', label: 'Time' },
  { value: 'severity', label: 'Severity' },
  { value: 'type', label: 'Type' },
  { value: 'crypto', label: 'Crypto' }
];

const filteredAndSortedAlerts = computed(() => {
  let filtered = [...props.alerts];

  // Apply search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    filtered = filtered.filter(alert => 
      alert.title.toLowerCase().includes(query) ||
      alert.description.toLowerCase().includes(query) ||
      alert.crypto.toLowerCase().includes(query)
    );
  }

  // Apply type filter
  if (selectedFilter.value !== 'all') {
    if (selectedFilter.value === 'unread') {
      filtered = filtered.filter(alert => !alert.read);
    } else {
      filtered = filtered.filter(alert => alert.type === selectedFilter.value);
    }
  }

  // Apply sorting
  filtered.sort((a, b) => {
    let aValue, bValue;
    
    switch (sortBy.value) {
      case 'timestamp':
        aValue = new Date(a.timestamp || a.time);
        bValue = new Date(b.timestamp || b.time);
        break;
      case 'severity':
        const severityOrder = { critical: 3, high: 2, medium: 1 };
        aValue = severityOrder[a.type] || 0;
        bValue = severityOrder[b.type] || 0;
        break;
      case 'type':
        aValue = a.type;
        bValue = b.type;
        break;
      case 'crypto':
        aValue = a.crypto;
        bValue = b.crypto;
        break;
      default:
        return 0;
    }

    if (aValue < bValue) return sortOrder.value === 'asc' ? -1 : 1;
    if (aValue > bValue) return sortOrder.value === 'asc' ? 1 : -1;
    return 0;
  });

  return filtered;
});

const alertCounts = computed(() => {
  const counts = {
    all: props.alerts.length,
    critical: props.alerts.filter(a => a.type === 'critical').length,
    high: props.alerts.filter(a => a.type === 'high').length,
    medium: props.alerts.filter(a => a.type === 'medium').length,
    unread: props.alerts.filter(a => !a.read).length
  };
  
  // Update filter options with counts
  filterOptions.forEach(option => {
    option.count = counts[option.value] || 0;
  });
  
  return counts;
});

const toggleSelectAlert = (alertId) => {
  if (selectedAlerts.value.has(alertId)) {
    selectedAlerts.value.delete(alertId);
  } else {
    selectedAlerts.value.add(alertId);
  }
};

const selectAllAlerts = () => {
  if (selectedAlerts.value.size === filteredAndSortedAlerts.value.length) {
    selectedAlerts.value.clear();
  } else {
    selectedAlerts.value = new Set(filteredAndSortedAlerts.value.map(a => a.id));
  }
};

const dismissSelectedAlerts = () => {
  selectedAlerts.value.forEach(alertId => {
    emit('dismiss-alert', alertId);
  });
  selectedAlerts.value.clear();
};

const closeDialog = () => {
  emit('close');
};

const getSeverityValue = (alert) => {
  return alert.severity || (alert.type === 'critical' ? 90 : alert.type === 'high' ? 70 : 40);
};

const getSeverityClass = (type) => {
  const classes = {
    critical: 'p-progressbar-critical',
    high: 'p-progressbar-high', 
    medium: 'p-progressbar-medium'
  };
  return classes[type] || '';
};

const getAlertTypeClass = (type) => {
  const classes = {
    critical: 'p-badge-danger',
    high: 'p-badge-warning',
    medium: 'p-badge-info'
  };
  return classes[type] || '';
};

const getCryptoClass = (crypto) => {
  const classes = {
    btc: 'crypto-btc',
    eth: 'crypto-eth', 
    ada: 'crypto-ada',
    dot: 'crypto-dot',
    link: 'crypto-link'
  };
  return classes[crypto.toLowerCase()] || '';
};

// Watch for dialog close to reset selections
watch(() => props.isOpen, (newVal) => {
  if (!newVal) {
    selectedAlerts.value.clear();
  }
});
</script>

<template>
  <Dialog
    :visible="isOpen"
    modal
    maximizable
    :closable="true"
    :draggable="false"
    :resizable="false"
    class="alerts-dialog"
    :style="{ width: '95vw', height: '95vh' }"
    @hide="closeDialog"
  >
    <template #header>
      <div class="dialog-header-content">
        <div class="header-left">
          <div class="header-icon">
            <i class="pi pi-exclamation-triangle"></i>
          </div>
          <div>
            <h2 class="dialog-title">Security Alerts</h2>
            <p class="dialog-subtitle">{{ filteredAndSortedAlerts.length }} of {{ alerts.length }} alerts</p>
          </div>
        </div>
        
        <div class="header-actions">
          <Button
            label="Mark All Read"
            icon="pi pi-check"
            class="p-button-outlined p-button-secondary"
            size="small"
            @click="emit('mark-all-read')"
          />
          
          <Button
            label="Clear All"
            icon="pi pi-trash"
            class="p-button-outlined p-button-danger"
            size="small"
            @click="emit('clear-all')"
          />
        </div>
      </div>
    </template>

    <div class="dialog-body">
      <!-- Filters and Search -->
      <div class="dialog-filters">
        <div class="search-section">
          <div class="p-inputgroup">
            <span class="p-inputgroup-addon">
            </span>
            <InputText
              v-model="searchQuery"
              placeholder="Search alerts..."
              class="search-input"
            />
          </div>
        </div>

        <div class="filter-section">
          <div class="filter-tabs">
            <Button
              v-for="filter in filterOptions"
              :key="filter.value"
              :label="filter.label"
              :class="{ 'p-button-outlined': selectedFilter !== filter.value }"
              size="small"
              @click="selectedFilter = filter.value"
            >
              <template #default>
                {{ filter.label }}
                <Badge :value="filter.count" class="ml-2" />
              </template>
            </Button>
          </div>

          <div class="sort-controls">
            <Dropdown
              v-model="sortBy"
              :options="sortOptions"
              option-label="label"
              option-value="value"
              placeholder="Sort by"
              class="sort-dropdown"
            />
            
            <Button
              :icon="sortOrder === 'asc' ? 'pi pi-sort-up' : 'pi pi-sort-down'"
              class="p-button-outlined"
              size="small"
              @click="sortOrder = sortOrder === 'asc' ? 'desc' : 'asc'"
            />
          </div>
        </div>
      </div>

      <Divider />

      <!-- Bulk Actions -->
      <div v-if="selectedAlerts.size > 0" class="bulk-actions">
        <div class="bulk-info">
          <span>{{ selectedAlerts.size }} alert{{ selectedAlerts.size !== 1 ? 's' : '' }} selected</span>
        </div>
        <div class="bulk-buttons">
          <Button
            label="Dismiss Selected"
            icon="pi pi-times"
            class="p-button-danger"
            size="small"
            @click="dismissSelectedAlerts"
          />
          <Button
            label="Clear Selection"
            icon="pi pi-refresh"
            class="p-button-outlined"
            size="small"
            @click="selectedAlerts.clear()"
          />
        </div>
      </div>

      <!-- Alerts List -->
      <div class="dialog-content">
        <div class="alerts-grid">
          <!-- Select All Header -->
          <div class="select-all-header">
            <div class="p-field-checkbox">
              <Checkbox
                :model-value="selectedAlerts.size === filteredAndSortedAlerts.length && filteredAndSortedAlerts.length > 0"
                :indeterminate="selectedAlerts.size > 0 && selectedAlerts.size < filteredAndSortedAlerts.length"
                @update:model-value="selectAllAlerts"
                input-id="select-all"
              />
              <label for="select-all" class="checkbox-label">Select All</label>
            </div>
          </div>

          <!-- Alert Items -->
          <div class="alerts-list-grid">
            <div
              v-for="(alert, index) in filteredAndSortedAlerts"
              :key="alert.id"
              class="alert-item"
              :class="[
                `alert-${alert.type}`,
                { 'selected': selectedAlerts.has(alert.id), 'unread': !alert.read }
              ]"
              :style="{ '--delay': (index % 20) * 0.05 + 's' }"
            >
              <div class="alert-checkbox">
                <Checkbox
                  :model-value="selectedAlerts.has(alert.id)"
                  @update:model-value="toggleSelectAlert(alert.id)"
                  :input-id="`alert-${alert.id}`"
                />
              </div>

              <div class="alert-indicator">
                <div class="indicator-dot" :class="`dot-${alert.type}`">
                  <div class="dot-pulse"></div>
                </div>
              </div>

              <div class="alert-content">
                <div class="alert-header">
                  <div class="alert-meta">
                    <Badge
                      :value="alert.type.toUpperCase()"
                      :class="getAlertTypeClass(alert.type)"
                    />
                    <span class="alert-time">{{ alert.time }}</span>
                    <div v-if="!alert.read" class="unread-indicator">
                      <i class="pi pi-circle-fill"></i>
                    </div>
                  </div>
                  
                  <div class="alert-actions">
                    <Button
                      icon="pi pi-times"
                      class="p-button-rounded p-button-text p-button-sm"
                      @click="emit('dismiss-alert', alert.id)"
                    />
                  </div>
                </div>

                <div class="alert-body">
                  <h4 class="alert-title">{{ alert.title }}</h4>
                  <p class="alert-description">{{ alert.description }}</p>
                  
                  <div class="alert-details">
                    <div class="crypto-info">
                      <Badge
                        :value="alert.crypto"
                        :class="getCryptoClass(alert.crypto)"
                        class="crypto-badge"
                      />
                      <span class="amount">{{ alert.amount }}</span>
                    </div>
                    
                    <div class="alert-progress">
                      <ProgressBar
                        :value="getSeverityValue(alert)"
                        :class="getSeverityClass(alert.type)"
                        class="progress-bar"
                      />
                      <span class="severity-text">{{ getSeverityValue(alert) }}% severity</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Empty State -->
          <div v-if="filteredAndSortedAlerts.length === 0" class="empty-state">
            <div class="empty-icon">
              <i class="pi pi-search" style="font-size: 4rem;"></i>
            </div>
            <h3>No alerts found</h3>
            <p v-if="searchQuery">Try adjusting your search terms or filters</p>
            <p v-else>All clear! No security alerts at this time.</p>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer-content">
        <div class="footer-info">
          <span class="footer-text">Last updated: {{ new Date().toLocaleTimeString() }}</span>
        </div>
        <div class="footer-actions">
          <Button
            label="Close"
            icon="pi pi-times"
            class="p-button-outlined"
            @click="closeDialog"
          />
        </div>
      </div>
    </template>
  </Dialog>
</template>

<style scoped>
/* Dialog Overlay */
.dialog-overlay {
  @apply fixed inset-0 z-50 flex items-center justify-center;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(8px);
}

.dialog-container {
  @apply w-full h-full max-w-none bg-white dark:bg-gray-900 flex flex-col;
  @apply shadow-2xl;
}

/* Header */
.dialog-header {
  @apply flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(147, 51, 234, 0.05) 100%);
}

.header-left {
  @apply flex items-center gap-4;
}

.header-icon {
  @apply w-12 h-12 bg-gradient-to-br from-amber-400 to-orange-500 rounded-xl flex items-center justify-center;
  box-shadow: 0 8px 25px rgba(245, 158, 11, 0.3);
}

.header-icon svg {
  @apply w-6 h-6 text-white;
}

.dialog-title {
  @apply text-2xl font-bold text-gray-900 dark:text-white;
}

.dialog-subtitle {
  @apply text-sm text-gray-600 dark:text-gray-400 mt-1;
}

.header-actions {
  @apply flex items-center gap-3;
}

.action-button {
  @apply flex items-center gap-2 px-4 py-2 rounded-xl font-medium transition-all duration-300;
  @apply border backdrop-blur-sm;
}

.action-button.secondary {
  @apply bg-gray-50 dark:bg-gray-800 text-gray-700 dark:text-gray-300;
  @apply border-gray-200 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-700;
}

.action-button.danger {
  @apply bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300;
  @apply border-red-200 dark:border-red-800/30 hover:bg-red-100 dark:hover:bg-red-900/30;
}

.close-button {
  @apply p-2 rounded-xl text-gray-500 hover:text-gray-700 dark:hover:text-gray-300;
  @apply hover:bg-gray-100 dark:hover:bg-gray-800 transition-all duration-200;
}

/* Filters */
.dialog-filters {
  @apply p-6 border-b border-gray-200 dark:border-gray-700 space-y-4;
  background: rgba(249, 250, 251, 0.5);
}

.dark .dialog-filters {
  background: rgba(17, 24, 39, 0.5);
}

.search-section {
  @apply flex items-center gap-4;
}

.search-input-wrapper {
  @apply relative flex-1 max-w-md;
}

.search-icon {
  @apply absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400;
}

.search-input {
  @apply w-full pl-10 pr-4 py-3 rounded-xl border border-gray-200 dark:border-gray-700;
  @apply bg-white dark:bg-gray-800 text-gray-900 dark:text-white;
  @apply focus:ring-2 focus:ring-blue-500 focus:border-transparent;
  @apply placeholder-gray-500 dark:placeholder-gray-400;
}

.filter-section {
  @apply flex items-center justify-between gap-4;
}

.filter-tabs {
  @apply flex items-center gap-2;
}

.filter-tab {
  @apply flex items-center gap-2 px-4 py-2 rounded-xl font-medium transition-all duration-300;
  @apply text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white;
  @apply hover:bg-white dark:hover:bg-gray-800;
}

.filter-tab.active {
  @apply bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300;
  @apply border border-blue-200 dark:border-blue-800/30;
}

.filter-count {
  @apply px-2 py-1 rounded-lg text-xs font-bold;
  @apply bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300;
}

.filter-tab.active .filter-count {
  @apply bg-blue-200 dark:bg-blue-800/50 text-blue-800 dark:text-blue-200;
}

.sort-controls {
  @apply flex items-center gap-2;
}

.sort-select {
  @apply px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-700;
  @apply bg-white dark:bg-gray-800 text-gray-900 dark:text-white;
  @apply focus:ring-2 focus:ring-blue-500 focus:border-transparent;
}

.sort-order-btn {
  @apply p-2 rounded-lg text-gray-600 dark:text-gray-400;
  @apply hover:bg-gray-100 dark:hover:bg-gray-800 transition-all duration-200;
}

.sort-order-btn svg {
  @apply transition-transform duration-300;
}

/* Bulk Actions */
.bulk-actions {
  @apply flex items-center justify-between px-6 py-4 bg-blue-50 dark:bg-blue-900/20;
  @apply border-b border-blue-200 dark:border-blue-800/30;
}

.bulk-info {
  @apply text-sm font-medium text-blue-700 dark:text-blue-300;
}

.bulk-buttons {
  @apply flex items-center gap-3;
}

.bulk-button {
  @apply px-4 py-2 rounded-lg font-medium transition-all duration-300;
}

.bulk-button.danger {
  @apply bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300;
  @apply hover:bg-red-200 dark:hover:bg-red-900/50;
}

.bulk-button.secondary {
  @apply bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300;
  @apply hover:bg-gray-200 dark:hover:bg-gray-700;
}

/* Content */
.dialog-content {
  @apply flex-1 overflow-auto p-6;
}

.alerts-grid {
  @apply space-y-4;
}

.select-all-header {
  @apply flex items-center p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl;
}

.checkbox-wrapper {
  @apply flex items-center gap-3 cursor-pointer;
}

.checkbox {
  @apply w-4 h-4 rounded border-2 border-gray-300 dark:border-gray-600;
  @apply checked:bg-blue-500 checked:border-blue-500;
  @apply focus:ring-2 focus:ring-blue-500 focus:ring-offset-2;
}

.checkbox-label {
  @apply text-sm font-medium text-gray-700 dark:text-gray-300;
}

.alerts-list-grid {
  @apply space-y-3;
}

.alert-item {
  @apply flex items-start gap-4 p-5 rounded-2xl border transition-all duration-500;
  @apply hover:shadow-lg hover:-translate-y-1;
  animation: slideInGrid 0.6s ease-out forwards;
  animation-delay: var(--delay);
  opacity: 0;
  transform: translateY(20px);
}

.alert-item.selected {
  @apply ring-2 ring-blue-500 ring-offset-2 dark:ring-offset-gray-900;
}

.alert-item.unread {
  @apply border-l-4;
}

.alert-item.unread.alert-critical {
  @apply border-l-red-500;
}

.alert-item.unread.alert-high {
  @apply border-l-orange-500;
}

.alert-item.unread.alert-medium {
  @apply border-l-yellow-500;
}

.alert-critical {
  @apply bg-red-50/80 dark:bg-red-900/20 border-red-200/60 dark:border-red-800/30;
}

.alert-high {
  @apply bg-orange-50/80 dark:bg-orange-900/20 border-orange-200/60 dark:border-orange-800/30;
}

.alert-medium {
  @apply bg-yellow-50/80 dark:bg-yellow-900/20 border-yellow-200/60 dark:border-yellow-800/30;
}

.alert-checkbox {
  @apply flex-shrink-0 pt-1;
}

.alert-indicator {
  @apply flex-shrink-0;
}

.indicator-dot {
  @apply relative w-4 h-4 rounded-full flex items-center justify-center;
}

.dot-critical {
  @apply bg-red-500;
  box-shadow: 0 0 20px rgba(239, 68, 68, 0.6);
}

.dot-high {
  @apply bg-orange-500;
  box-shadow: 0 0 20px rgba(249, 115, 22, 0.6);
}

.dot-medium {
  @apply bg-yellow-500;
  box-shadow: 0 0 20px rgba(245, 158, 11, 0.6);
}

.dot-pulse {
  @apply absolute inset-0 rounded-full;
  animation: dot-pulse 2s ease-in-out infinite;
}

.dot-critical .dot-pulse {
  @apply bg-red-400;
}

.dot-high .dot-pulse {
  @apply bg-orange-400;
}

.dot-medium .dot-pulse {
  @apply bg-yellow-400;
}

.alert-content {
  @apply flex-1 min-w-0;
}

.alert-header {
  @apply flex items-start justify-between mb-3;
}

.alert-meta {
  @apply flex items-center gap-3;
}

.alert-type-badge {
  @apply px-3 py-1 rounded-lg text-xs font-bold;
}

.badge-critical {
  @apply bg-red-100 dark:bg-red-900/50 text-red-800 dark:text-red-300;
}

.badge-high {
  @apply bg-orange-100 dark:bg-orange-900/50 text-orange-800 dark:text-orange-300;
}

.badge-medium {
  @apply bg-yellow-100 dark:bg-yellow-900/50 text-yellow-800 dark:text-yellow-300;
}

.alert-time {
  @apply text-xs text-gray-500 dark:text-gray-400 font-medium;
}

.unread-indicator {
  @apply w-2 h-2 bg-blue-500 rounded-full;
  animation: pulse 2s infinite;
}

.alert-actions {
  @apply flex items-center gap-2;
}

.action-btn {
  @apply p-2 rounded-lg transition-all duration-200;
  @apply text-gray-400 hover:text-gray-600 dark:hover:text-gray-300;
  @apply hover:bg-gray-100 dark:hover:bg-gray-700;
}

.action-btn svg {
  @apply w-4 h-4;
}

.alert-body {
  @apply space-y-3;
}

.alert-title {
  @apply text-base font-bold text-gray-900 dark:text-white;
}

.alert-description {
  @apply text-sm text-gray-600 dark:text-gray-300 leading-relaxed;
}

.alert-details {
  @apply flex items-center gap-3;
}

.crypto-info {
  @apply flex items-center gap-3;
}

.crypto-badge {
  @apply flex items-center px-3 py-1 rounded-lg text-xs font-bold;
}

.crypto-btc {
  @apply bg-orange-100 dark:bg-orange-900/50 text-orange-800 dark:text-orange-300;
}

.crypto-eth {
  @apply bg-blue-100 dark:bg-blue-900/50 text-blue-800 dark:text-blue-300;
}

.crypto-ada {
  @apply bg-purple-100 dark:bg-purple-900/50 text-purple-800 dark:text-purple-300;
}

.crypto-dot {
  @apply bg-pink-100 dark:bg-pink-900/50 text-pink-800 dark:text-pink-300;
}

.crypto-link {
  @apply bg-indigo-100 dark:bg-indigo-900/50 text-indigo-800 dark:text-indigo-300;
}

.amount {
  @apply text-sm font-semibold text-gray-700 dark:text-gray-300;
}

.alert-progress {
  @apply flex items-center gap-3 flex-1;
}

.progress-bar {
  @apply flex-1 h-2 rounded-full overflow-hidden;
}

.progress-critical {
  @apply bg-red-100 dark:bg-red-900/30;
}

.progress-high {
  @apply bg-orange-100 dark:bg-orange-900/30;
}

.progress-medium {
  @apply bg-yellow-100 dark:bg-yellow-900/30;
}

.progress-fill {
  @apply h-full rounded-full transition-all duration-1000 ease-out;
}

.progress-critical .progress-fill {
  @apply bg-red-500;
  box-shadow: 0 0 10px rgba(239, 68, 68, 0.5);
}

.progress-high .progress-fill {
  @apply bg-orange-500;
  box-shadow: 0 0 10px rgba(249, 115, 22, 0.5);
}

.progress-medium .progress-fill {
  @apply bg-yellow-500;
  box-shadow: 0 0 10px rgba(245, 158, 11, 0.5);
}

.severity-text {
  @apply text-xs font-medium text-gray-600 dark:text-gray-400 whitespace-nowrap;
}

/* Empty State */
.empty-state {
  @apply flex flex-col items-center justify-center py-16 text-center;
}

.empty-icon {
  @apply w-16 h-16 text-gray-400 dark:text-gray-500 mb-4;
}

.empty-icon svg {
  @apply w-full h-full;
}

.empty-state h3 {
  @apply text-lg font-bold text-gray-900 dark:text-white mb-2;
}

.empty-state p {
  @apply text-gray-600 dark:text-gray-400;
}

/* Footer */
.dialog-footer {
  @apply flex items-center justify-between p-6 border-t border-gray-200 dark:border-gray-700;
  background: rgba(249, 250, 251, 0.5);
}

.dark .dialog-footer {
  background: rgba(17, 24, 39, 0.5);
}

.footer-text {
  @apply text-sm text-gray-600 dark:text-gray-400;
}

.footer-button {
  @apply px-6 py-2 rounded-xl font-medium transition-all duration-300;
}

.footer-button.secondary {
  @apply bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300;
  @apply hover:bg-gray-200 dark:hover:bg-gray-700;
}

/* Animations */
@keyframes dot-pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.5);
    opacity: 0.7;
  }
}

@keyframes slideInGrid {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Dialog Transitions */
.dialog-enter-active,
.dialog-leave-active {
  transition: all 0.3s ease;
}

.dialog-enter-from,
.dialog-leave-to {
  opacity: 0;
  backdrop-filter: blur(0px);
}

.dialog-enter-from .dialog-container,
.dialog-leave-to .dialog-container {
  transform: scale(0.95);
  opacity: 0;
}

/* Alert Grid Transitions */
.alert-grid-enter-active,
.alert-grid-leave-active {
  transition: all 0.5s ease;
}

.alert-grid-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.alert-grid-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

.alert-grid-move {
  transition: transform 0.5s ease;
}

/* Responsive Design */
@media (max-width: 768px) {
  .dialog-container {
    @apply m-0 rounded-none;
  }
  
  .dialog-header {
    @apply flex-col gap-4 items-start;
  }
  
  .header-actions {
    @apply w-full justify-between;
  }
  
  .dialog-filters {
    @apply space-y-4;
  }
  
  .filter-section {
    @apply flex-col gap-4 items-start;
  }
  
  .filter-tabs {
    @apply flex-wrap;
  }
  
  .alert-item {
    @apply flex-col gap-3;
  }
  
  .alert-header {
    @apply flex-col gap-2 items-start;
  }
  
  .alert-details {
    @apply flex-col gap-3 items-start;
  }
  
  .bulk-actions {
    @apply flex-col gap-3 items-start;
  }
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
  .dot-pulse,
  .progress-fill,
  .alert-item {
    animation: none;
  }
  
  .alert-item {
    opacity: 1;
    transform: none;
  }
  
  .dialog-enter-active,
  .dialog-leave-active,
  .alert-grid-enter-active,
  .alert-grid-leave-active,
  .alert-grid-move {
    transition: none;
  }
}

/* Focus states */
.search-input:focus,
.sort-select:focus,
.checkbox:focus,
.action-button:focus,
.close-button:focus,
.filter-tab:focus,
.sort-order-btn:focus,
.bulk-button:focus,
.action-btn:focus,
.footer-button:focus {
  @apply outline-none ring-2 ring-blue-500 ring-offset-2 dark:ring-offset-gray-900;
}

/* High contrast mode */
@media (prefers-contrast: high) {
  .dialog-container,
  .alert-item,
  .filter-tab,
  .action-button {
    border-width: 2px;
  }
  
  .alert-type-badge,
  .crypto-badge {
    border: 1px solid currentColor;
  }
}
</style>