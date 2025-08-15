<!-- src/components/dashboard/ComplianceStatus.vue -->
<script setup>
const props = defineProps({
  risk: {
    type: Object,
    default: () => ({
      total: 0,
      critical: 0,
      high: 0,
      medium: 0,
      pct: { critical: 0, high: 0, medium: 0 }
    })
  }
})
</script>

<template>
  <div class="bg-gradient-to-br from-white via-emerald-50/30 to-green-50/50 dark:from-gray-900 dark:via-emerald-950/20 dark:to-green-950/30 rounded-3xl shadow-2xl border border-emerald-200/50 dark:border-emerald-800/30 p-8 mb-8 backdrop-blur-sm">
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div class="flex items-center gap-4">
        <div class="relative p-3 bg-gradient-to-br from-emerald-500 via-green-500 to-teal-500 rounded-2xl shadow-lg">
          <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
          </svg>
          <div class="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
        </div>
        <div>
          <h3 class="text-2xl font-bold bg-gradient-to-r from-emerald-700 via-green-700 to-teal-700 dark:from-emerald-300 dark:via-green-300 dark:to-teal-300 bg-clip-text text-transparent">
            Crypto Compliance Status
          </h3>
          <p class="text-sm text-emerald-600 dark:text-emerald-400 font-medium">Real-time risk assessment</p>
        </div>
      </div>
      <div class="flex items-center gap-2 px-4 py-2 bg-emerald-100 dark:bg-emerald-900/30 rounded-full">
        <div class="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
        <span class="text-xs font-semibold text-emerald-700 dark:text-emerald-300">LIVE</span>
      </div>
    </div>

    <!-- Risk Status Cards -->
    <div class="grid gap-4 mb-2">
      <!-- Critical -->
      <div class="group relative overflow-hidden bg-gradient-to-r from-red-50 via-rose-50 to-pink-50 dark:from-red-950/30 dark:via-rose-950/30 dark:to-pink-950/30 rounded-2xl border border-red-200/60 dark:border-red-800/40 p-5">
        <div class="relative flex items-center justify-between">
          <div class="flex items-center gap-4">
            <div class="relative">
              <div class="w-5 h-5 bg-gradient-to-br from-red-500 to-rose-600 rounded-full shadow-lg"></div>
              <div class="absolute inset-0 w-5 h-5 bg-gradient-to-br from-red-500 to-rose-600 rounded-full animate-ping opacity-20"></div>
            </div>
            <div>
              <span class="text-base font-bold text-red-700 dark:text-red-300">Critical Risk</span>
              <p class="text-xs text-red-600/80 dark:text-red-400/80">Immediate attention required</p>
            </div>
          </div>
          <div class="text-right">
            <div class="flex items-baseline gap-1">
              <span class="text-3xl font-black text-red-900 dark:text-red-100">{{ Math.round(props.risk.pct?.critical ?? 0) }}</span>
              <span class="text-lg font-bold text-red-700 dark:text-red-300">%</span>
            </div>
            <p class="text-sm text-red-600 dark:text-red-400 font-semibold">{{ props.risk.critical }} addresses</p>
          </div>
        </div>
      </div>

      <!-- High -->
      <div class="group relative overflow-hidden bg-gradient-to-r from-orange-50 via-amber-50 to-yellow-50 dark:from-orange-950/30 dark:via-amber-950/30 dark:to-yellow-950/30 rounded-2xl border border-orange-200/60 dark:border-orange-800/40 p-5">
        <div class="relative flex items-center justify-between">
          <div class="flex items-center gap-4">
            <div class="relative">
              <div class="w-5 h-5 bg-gradient-to-br from-orange-500 to-amber-600 rounded-full shadow-lg"></div>
              <div class="absolute inset-0 w-5 h-5 bg-gradient-to-br from-orange-500 to-amber-600 rounded-full animate-ping opacity-20"></div>
            </div>
            <div>
              <span class="text-base font-bold text-orange-700 dark:text-orange-300">High Risk</span>
              <p class="text-xs text-orange-600/80 dark:text-orange-400/80">Enhanced monitoring needed</p>
            </div>
          </div>
          <div class="text-right">
            <div class="flex items-baseline gap-1">
              <span class="text-3xl font-black text-orange-900 dark:text-orange-100">{{ Math.round(props.risk.pct?.high ?? 0) }}</span>
              <span class="text-lg font-bold text-orange-700 dark:text-orange-300">%</span>
            </div>
            <p class="text-sm text-orange-600 dark:text-orange-400 font-semibold">{{ props.risk.high }} addresses</p>
          </div>
        </div>
      </div>

      <!-- Medium -->
      <div class="group relative overflow-hidden bg-gradient-to-r from-emerald-50 via-green-50 to-teal-50 dark:from-emerald-950/30 dark:via-green-950/30 dark:to-teal-950/30 rounded-2xl border border-emerald-200/60 dark:border-emerald-800/40 p-5">
        <div class="relative flex items-center justify-between">
          <div class="flex items-center gap-4">
            <div class="relative">
              <div class="w-5 h-5 bg-gradient-to-br from-emerald-500 to-green-600 rounded-full shadow-lg"></div>
              <div class="absolute inset-0 w-5 h-5 bg-gradient-to-br from-emerald-500 to-green-600 rounded-full animate-ping opacity-20"></div>
            </div>
            <div>
              <span class="text-base font-bold text-emerald-700 dark:text-emerald-300">Medium Risk</span>
              <p class="text-xs text-emerald-600/80 dark:text-emerald-400/80">Standard compliance level</p>
            </div>
          </div>
          <div class="text-right">
            <div class="flex items-baseline gap-1">
              <span class="text-3xl font-black text-emerald-900 dark:text-emerald-100">{{ Math.round(props.risk.pct?.medium ?? 0) }}</span>
              <span class="text-lg font-bold text-emerald-700 dark:text-emerald-300">%</span>
            </div>
            <p class="text-sm text-emerald-600 dark:text-emerald-400 font-semibold">{{ props.risk.medium }} addresses</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="mt-6 flex items-center justify-between p-4 bg-gradient-to-r from-emerald-50 to-green-50 dark:from-emerald-950/20 dark:to-green-950/20 rounded-2xl border border-emerald-200/50 dark:border-emerald-700/30">
      <div class="flex items-center gap-3">
        <div class="w-8 h-8 bg-gradient-to-br from-emerald-500 to-green-600 rounded-xl flex items-center justify-center">
          <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
          </svg>
        </div>
        <div>
          <p class="text-sm font-bold text-emerald-800 dark:text-emerald-200">SigmaVerde Compliance Engine</p>
          <p class="text-xs text-emerald-600 dark:text-emerald-400">Powered by advanced risk analytics</p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <div class="px-3 py-1 bg-emerald-500 text-white text-xs font-bold rounded-full">ACTIVE</div>
        <div class="px-3 py-1 bg-white dark:bg-gray-800 text-emerald-600 dark:text-emerald-400 text-xs font-semibold rounded-full border border-emerald-200 dark:border-emerald-700">
          {{ props.risk.total }} Total Addresses
        </div>
      </div>
    </div>
  </div>
</template>
