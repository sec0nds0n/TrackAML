<script setup>
import { computed, defineEmits, defineProps, ref } from 'vue';
import AlertsFullScreenDialog from './AlertsFullScreenDialog.vue';

const props = defineProps({
  alerts: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['dismiss-alert', 'clear-all', 'mark-all-read']);

const showFullScreenDialog = ref(false);
const hoveredAlert = ref(null);

const displayedAlerts = computed(() => {
  return props.alerts.slice(0, 3);
});

const criticalCount = computed(() => {
  return props.alerts.filter(a => a.type === 'critical').length;
});

const openFullScreenDialog = () => {
  showFullScreenDialog.value = true;
};

const closeFullScreenDialog = () => {
  showFullScreenDialog.value = false;
};

const dismissAlert = (alertId) => {
  emit('dismiss-alert', alertId);
};

const handleClearAll = () => {
  emit('clear-all');
};

const handleMarkAllRead = () => {
  emit('mark-all-read');
};
</script>

<template>
  <div class="alerts-panel">
    <!-- Header Section -->
    <div class="panel-header">
      <div class="header-content">
        <div class="title-section">
          <div class="icon-wrapper">
            <svg class="alert-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"/>
            </svg>
          </div>
          <div>
            <h3 class="panel-title">Security Alerts</h3>
            <p class="panel-subtitle">Real-time crypto monitoring</p>
          </div>
        </div>
        
        <div class="header-actions">
          <div class="critical-badge" v-if="criticalCount > 0">
            <div class="pulse-ring"></div>
            <span class="critical-count">{{ criticalCount }}</span>
            <span class="critical-text">Critical</span>
          </div>
          
          <button @click="openFullScreenDialog" class="view-all-btn">
            <span>View All ({{ alerts.length }})</span>
            <svg class="btn-icon" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h4a1 1 0 010 2H6.414l2.293 2.293a1 1 0 11-1.414 1.414L5 6.414V8a1 1 0 01-2 0V4zm9 1a1 1 0 010-2h4a1 1 0 011 1v4a1 1 0 01-2 0V6.414l-2.293 2.293a1 1 0 11-1.414-1.414L13.586 5H12zm-9 7a1 1 0 012 0v1.586l2.293-2.293a1 1 0 111.414 1.414L6.414 15H8a1 1 0 010 2H4a1 1 0 01-1-1v-4zm13-1a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 010-2h1.586l-2.293-2.293a1 1 0 111.414-1.414L15.586 13H17a1 1 0 01-1-1z" clip-rule="evenodd"/>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Preview Alerts List (First 3) -->
    <div class="alerts-container">
      <TransitionGroup name="alert" tag="div" class="alerts-list">
        <div 
          v-for="(alert, index) in displayedAlerts" 
          :key="alert.id"
          class="alert-card"
          :class="[
            `alert-${alert.type}`,
            { 'alert-hovered': hoveredAlert === alert.id }
          ]"
          @mouseenter="hoveredAlert = alert.id"
          @mouseleave="hoveredAlert = null"
          :style="{ '--delay': index * 0.1 + 's' }"
        >
          <!-- Alert Indicator -->
          <div class="alert-indicator">
            <div class="indicator-dot" :class="`dot-${alert.type}`">
              <div class="dot-pulse"></div>
            </div>
            <div class="indicator-line"></div>
          </div>

          <!-- Alert Content -->
          <div class="alert-content">
            <div class="alert-header">
              <div class="alert-meta">
                <span class="alert-type-badge" :class="`badge-${alert.type}`">
                  {{ alert.type.toUpperCase() }}
                </span>
                <span class="alert-time">{{ alert.time }}</span>
                <div v-if="!alert.read" class="unread-indicator"></div>
              </div>
              
              <div class="alert-actions">
                <button class="action-btn" @click="dismissAlert(alert.id)">
                  <svg viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/>
                  </svg>
                </button>
              </div>
            </div>

            <div class="alert-body">
              <h4 class="alert-title">{{ alert.title }}</h4>
              <p class="alert-description">{{ alert.description }}</p>
              
              <div class="alert-details">
                <div class="crypto-info">
                  <div class="crypto-badge" :class="`crypto-${alert.crypto.toLowerCase()}`">
                    <div class="crypto-icon">
                      <span>{{ alert.crypto }}</span>
                    </div>
                  </div>
                  <div class="amount-info">
                    <span class="amount">{{ alert.amount }}</span>
                  </div>
                </div>
                
                <div class="alert-progress">
                  <div class="progress-bar" :class="`progress-${alert.type}`">
                    <div class="progress-fill" :style="{ width: alert.type === 'critical' ? '90%' : alert.type === 'high' ? '70%' : '40%' }"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Hover Effect Overlay -->
          <div class="alert-overlay"></div>
        </div>
      </TransitionGroup>

      <!-- Show More Button (if more than 3 alerts) -->
      <div v-if="alerts.length > 3" class="show-more-section">
        <button @click="openFullScreenDialog" class="show-more-btn">
          <div class="show-more-content">
            <div class="show-more-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
              </svg>
            </div>
            <div class="show-more-text">
              <span class="show-more-title">{{ alerts.length - 3 }} more alerts</span>
              <span class="show-more-subtitle">Click to view all alerts</span>
            </div>
          </div>
        </button>
      </div>

      <!-- Empty State -->
      <div v-if="alerts.length === 0" class="empty-state">
        <div class="empty-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
        </div>
        <h4>All Clear!</h4>
        <p>No security alerts at this time</p>
      </div>
    </div>

    <!-- Full Screen Dialog -->
    <AlertsFullScreenDialog
      :alerts="alerts"
      :is-open="showFullScreenDialog"
      @close="closeFullScreenDialog"
      @dismiss-alert="dismissAlert"
      @clear-all="handleClearAll"
      @mark-all-read="handleMarkAllRead"
    />
  </div>
</template>

<style scoped>
.alerts-panel {
  @apply relative overflow-hidden;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.dark .alerts-panel {
  background: linear-gradient(135deg, rgba(17, 24, 39, 0.8) 0%, rgba(31, 41, 55, 0.6) 100%);
  border-color: rgba(75, 85, 99, 0.3);
}

/* Header Styles */
.panel-header {
  @apply p-6 pb-4;
  background: linear-gradient(90deg, rgba(59, 130, 246, 0.05) 0%, rgba(147, 51, 234, 0.05) 100%);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.header-content {
  @apply flex items-center justify-between;
}

.title-section {
  @apply flex items-center gap-4;
}

.icon-wrapper {
  @apply relative;
}

.alert-icon {
  @apply w-8 h-8 text-amber-500;
  filter: drop-shadow(0 0 8px rgba(245, 158, 11, 0.4));
  animation: pulse-glow 2s ease-in-out infinite;
}

.panel-title {
  @apply text-xl font-bold text-gray-900 dark:text-white;
  background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.dark .panel-title {
  background: linear-gradient(135deg, #f9fafb 0%, #d1d5db 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.panel-subtitle {
  @apply text-sm text-gray-600 dark:text-gray-400 mt-1;
}

.header-actions {
  @apply flex items-center gap-4;
}

.critical-badge {
  @apply relative flex items-center gap-2 px-4 py-2 rounded-full;
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.1) 100%);
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.pulse-ring {
  @apply absolute -inset-1 rounded-full;
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.3) 0%, rgba(220, 38, 38, 0.3) 100%);
  animation: pulse-ring 2s cubic-bezier(0.455, 0.03, 0.515, 0.955) infinite;
}

.critical-count {
  @apply text-sm font-bold text-red-600 dark:text-red-400;
}

.critical-text {
  @apply text-xs font-medium text-red-700 dark:text-red-300;
}

.view-all-btn {
  @apply flex items-center gap-2 px-4 py-2 rounded-xl font-medium transition-all duration-300;
  @apply text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300;
  @apply bg-blue-50 dark:bg-blue-900/20 hover:bg-blue-100 dark:hover:bg-blue-900/30;
  @apply border border-blue-200 dark:border-blue-800/30;
  transform: translateY(0);
}

.view-all-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.btn-icon {
  @apply w-4 h-4 transition-transform duration-300;
}

.view-all-btn:hover .btn-icon {
  transform: scale(1.1);
}

/* Alerts Container */
.alerts-container {
  @apply p-6 pt-2;
}

.alerts-list {
  @apply space-y-4;
}

.alert-card {
  @apply relative flex gap-4 p-5 rounded-2xl transition-all duration-500;
  @apply border backdrop-blur-sm;
  animation: slideInUp 0.6s ease-out forwards;
  animation-delay: var(--delay);
  opacity: 0;
  transform: translateY(20px);
}

.alert-critical {
  @apply bg-red-50/80 dark:bg-red-900/20 border-red-200/60 dark:border-red-800/30;
  box-shadow: 0 4px 20px rgba(239, 68, 68, 0.1);
}

.alert-high {
  @apply bg-orange-50/80 dark:bg-orange-900/20 border-orange-200/60 dark:border-orange-800/30;
  box-shadow: 0 4px 20px rgba(249, 115, 22, 0.1);
}

.alert-medium {
  @apply bg-yellow-50/80 dark:bg-yellow-900/20 border-yellow-200/60 dark:border-yellow-800/30;
  box-shadow: 0 4px 20px rgba(245, 158, 11, 0.1);
}

.alert-card:hover {
  transform: translateY(-4px) scale(1.02);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.alert-hovered .alert-overlay {
  opacity: 1;
}

/* Alert Indicator */
.alert-indicator {
  @apply flex flex-col items-center;
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

.indicator-line {
  @apply w-px h-16 bg-gradient-to-b from-gray-300 to-transparent dark:from-gray-600 mt-2;
}

/* Alert Content */
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
  @apply space-y-3;
}

.crypto-info {
  @apply flex items-center gap-3;
}

.crypto-badge {
  @apply flex items-center gap-2 px-3 py-1 rounded-lg;
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

.crypto-icon span {
  @apply text-xs font-bold;
}

.amount-info {
  @apply flex-1;
}

.amount {
  @apply text-sm font-semibold text-gray-700 dark:text-gray-300;
}

.alert-progress {
  @apply w-full;
}

.progress-bar {
  @apply w-full h-2 rounded-full overflow-hidden;
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

.alert-overlay {
  @apply absolute inset-0 rounded-2xl opacity-0 transition-opacity duration-300;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
  pointer-events: none;
}

/* Show More Section */
.show-more-section {
  @apply mt-6;
}

.show-more-btn {
  @apply w-full p-4 rounded-2xl transition-all duration-300;
  @apply bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20;
  @apply border border-blue-200 dark:border-blue-800/30;
  @apply hover:from-blue-100 hover:to-purple-100 dark:hover:from-blue-900/30 dark:hover:to-purple-900/30;
  @apply hover:shadow-lg hover:-translate-y-1;
}

.show-more-content {
  @apply flex items-center gap-4;
}

.show-more-icon {
  @apply w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center;
  box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
}

.show-more-icon svg {
  @apply w-5 h-5 text-white;
}

.show-more-text {
  @apply flex-1 text-left;
}

.show-more-title {
  @apply block text-base font-bold text-gray-900 dark:text-white;
}

.show-more-subtitle {
  @apply block text-sm text-gray-600 dark:text-gray-400 mt-1;
}

.show-more-arrow {
  @apply w-5 h-5 text-gray-400 transition-transform duration-300;
}

.show-more-btn:hover .show-more-arrow {
  transform: translateX(4px);
}

/* Empty State */
.empty-state {
  @apply flex flex-col items-center justify-center py-12 text-center;
}

.empty-icon {
  @apply w-16 h-16 text-green-500 mb-4;
  filter: drop-shadow(0 0 10px rgba(34, 197, 94, 0.3));
}

.empty-state h4 {
  @apply text-lg font-bold text-gray-900 dark:text-white mb-2;
}

.empty-state p {
  @apply text-gray-600 dark:text-gray-400;
}

/* Animations */
@keyframes pulse-glow {
  0%, 100% {
    filter: drop-shadow(0 0 8px rgba(245, 158, 11, 0.4));
  }
  50% {
    filter: drop-shadow(0 0 16px rgba(245, 158, 11, 0.8));
  }
}

@keyframes pulse-ring {
  0% {
    transform: scale(0.8);
    opacity: 1;
  }
  100% {
    transform: scale(2);
    opacity: 0;
  }
}

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

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Alert Transitions */
.alert-enter-active,
.alert-leave-active {
  transition: all 0.5s ease;
}

.alert-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.alert-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

.alert-move {
  transition: transform 0.5s ease;
}

/* Responsive Design */
@media (max-width: 768px) {
  .panel-header {
    @apply p-4;
  }
  
  .header-content {
    @apply flex-col gap-4 items-start;
  }
  
  .header-actions {
    @apply w-full justify-between;
  }
  
  .alerts-container {
    @apply p-4;
  }
  
  .alert-card {
    @apply p-4;
  }
  
  .alert-header {
    @apply flex-col gap-2 items-start;
  }
  
  .alert-details {
    @apply space-y-2;
  }
  
  .crypto-info {
    @apply flex-col gap-2 items-start;
  }
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
  .alert-icon,
  .pulse-ring,
  .dot-pulse,
  .progress-fill {
    animation: none;
  }
  
  .alert-card {
    animation: none;
    opacity: 1;
    transform: none;
  }
  
  .alert-enter-active,
  .alert-leave-active,
  .alert-move {
    transition: none;
  }
}

/* Focus states for accessibility */
.view-all-btn:focus,
.show-more-btn:focus,
.action-btn:focus {
  @apply outline-none ring-2 ring-blue-500 ring-offset-2 dark:ring-offset-gray-800;
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .alerts-panel,
  .alert-card,
  .view-all-btn,
  .show-more-btn {
    border-width: 2px;
  }
  
  .alert-type-badge,
  .crypto-badge {
    border: 1px solid currentColor;
  }
}
</style>
