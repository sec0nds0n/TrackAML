<template>
  <div
    class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 p-4 w-80 transition"
    :class="borderColor"
  >
    <div class="flex items-start gap-3">
      <div class="w-2 h-2 rounded-full mt-1.5 animate-pulse" :class="dotColor"></div>
      <div class="flex-1 min-w-0">
        <div class="flex items-center justify-between mb-1">
          <span class="text-xs font-bold px-2 py-1 rounded" :class="badgeColor">
            {{ alert.type.toUpperCase() }}
          </span>
          <button @click="$emit('dismiss', alert.id)" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
        <h4 class="text-sm font-semibold text-gray-900 dark:text-white mb-1">{{ alert.title }}</h4>
        <p class="text-xs text-gray-600 dark:text-gray-400 line-clamp-2">{{ alert.description }}</p>
        <div class="flex items-center justify-between mt-2">
          <span class="text-xs font-medium text-gray-500">{{ alert.crypto }} • {{ alert.amount }}</span>
          <span class="text-xs text-gray-400">{{ alert.time }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps(['alert'])

const colorMap = {
  critical: {
    border: 'border-l-4 border-red-500',
    dot: 'bg-red-500',
    badge: 'bg-red-100 text-red-800 dark:bg-red-900/50 dark:text-red-300'
  },
  high: {
    border: 'border-l-4 border-orange-500',
    dot: 'bg-orange-500',
    badge: 'bg-orange-100 text-orange-800 dark:bg-orange-900/50 dark:text-orange-300'
  },
  medium: {
    border: 'border-l-4 border-yellow-500',
    dot: 'bg-yellow-500',
    badge: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/50 dark:text-yellow-300'
  },
  low: {
    border: 'border-l-4 border-blue-500',
    dot: 'bg-blue-500',
    badge: 'bg-blue-100 text-blue-800 dark:bg-blue-900/50 dark:text-blue-300'
  }
}

const borderColor = colorMap[alert.type]?.border || 'border-l-4 border-gray-300'
const dotColor = colorMap[alert.type]?.dot || 'bg-gray-300'
const badgeColor = colorMap[alert.type]?.badge || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
</script>



<style scoped>
.notification-alert {
  @apply bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-4 border-l-4;
}
.notification-content {
  @apply flex items-start gap-3;
}
.status-dot {
  @apply w-2 h-2 rounded-full mt-2 animate-pulse;
}
.alert-info {
  @apply flex-1 min-w-0;
}
.info-header {
  @apply flex items-center justify-between mb-1;
}
.severity-tag {
  @apply text-xs font-bold px-2 py-1 rounded;
}
.severity-critical {
  @apply bg-red-100 text-red-800 dark:bg-red-900/50 dark:text-red-300;
}
.severity-high {
  @apply bg-orange-100 text-orange-800 dark:bg-orange-900/50 dark:text-orange-300;
}
.severity-medium {
  @apply bg-yellow-100 text-yellow-800 dark:bg-yellow-900/50 dark:text-yellow-300;
}
.dismiss-button {
  @apply text-gray-400 hover:text-gray-600 dark:hover:text-gray-300;
}
.icon {
  @apply w-4 h-4;
}
.alert-title {
  @apply text-sm font-semibold text-gray-900 dark:text-white mb-1;
}
.alert-description {
  @apply text-xs text-gray-600 dark:text-gray-400 line-clamp-2;
}
.alert-meta {
  @apply flex items-center justify-between mt-2 text-xs text-gray-500 dark:text-gray-400;
}
.time-text {
  @apply text-gray-400;
}
</style>
