<script setup>
import { defineEmits, defineProps } from 'vue'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  showQuickActions: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['toggle', 'export-report', 'navigate'])
const authStore = useAuthStore()
console.log(authStore);
const toggleActions = () => {
  emit('toggle')
}

const handleExportReport = () => {
  emit('export-report')
}

const handleNavigate = (route) => {
  emit('navigate', route)
}
</script>

<template>
  <div class="fixed bottom-6 right-6 z-50">
    <div class="relative">
      <!-- Expandable Action Buttons -->
      <transition-group
        name="fab"
        tag="div"
        class="absolute bottom-16 right-0 space-y-3"
        v-show="showQuickActions"
      >
        <button
          key="report"
          @click="handleNavigate('/monitoring/reports')"
          class="flex items-center gap-3 bg-blue-600 hover:bg-blue-700 text-white px-4 py-3 rounded-full shadow-lg hover:shadow-xl transition-all duration-200 transform hover:scale-105 group"
          title="Generate AML Report"
          
        >
          <div class="p-1 bg-blue-500 rounded-lg">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
          </div>
          <span class="text-sm font-semibold whitespace-nowrap">Generate Report</span>
        </button>

        <!-- Exchanger Case Creation Button -->
        <button
          v-if="authStore.isExchanger"
          key="exchanger-case"
          class="flex items-center gap-3 bg-orange-600 hover:bg-orange-700 text-white px-4 py-3 rounded-full shadow-lg hover:shadow-xl transition-all duration-200 transform hover:scale-105 group"
          title="Create AML Case"
          @click="handleNavigate('/exchanger/create-case')"
        >
          <div class="p-1 bg-orange-500 rounded-lg">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
            </svg>
          </div>
          <span class="text-sm font-semibold whitespace-nowrap">Create Case</span>
        </button>

        <!-- Analyst Case Management Button -->
        <button
          v-else
          key="alert"
          class="flex items-center gap-3 bg-orange-600 hover:bg-orange-700 text-white px-4 py-3 rounded-full shadow-lg hover:shadow-xl transition-all duration-200 transform hover:scale-105 group"
          title="Case Management"
          @click="handleNavigate('/monitoring/cases')"
        >
          <div class="p-1 bg-orange-500 rounded-lg">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
            </svg>
          </div>
          <span class="text-sm font-semibold whitespace-nowrap">Manage Cases</span>
        </button>

        <button
          key="search"
          class="flex items-center gap-3 bg-green-600 hover:bg-green-700 text-white px-4 py-3 rounded-full shadow-lg hover:shadow-xl transition-all duration-200 transform hover:scale-105 group"
          title="Address Lookup"
          @click="handleNavigate('/search')"
        >
          <div class="p-1 bg-green-500 rounded-lg">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
            </svg>
          </div>
          <span class="text-sm font-semibold whitespace-nowrap">Address Lookup</span>
        </button>

        <button
          key="monitor"
          class="flex items-center gap-3 bg-purple-600 hover:bg-purple-700 text-white px-4 py-3 rounded-full shadow-lg hover:shadow-xl transition-all duration-200 transform hover:scale-105 group"
          title="Live Monitor"
          @click="handleNavigate('/monitoring/crypto')"
        >
          <div class="p-1 bg-purple-500 rounded-lg">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
            </svg>
          </div>
          <span class="text-sm font-semibold whitespace-nowrap">Live Monitor</span>
        </button>
      </transition-group>

      <!-- Main FAB Button -->
      <button
        @click="toggleActions"
        class="w-14 h-14 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-full shadow-2xl hover:shadow-3xl transition-all duration-300 transform hover:scale-110 flex items-center justify-center group relative overflow-hidden"
        :class="{ 'rotate-45': showQuickActions }"
      >
        <!-- Background pulse effect -->
        <div class="absolute inset-0 bg-gradient-to-r from-blue-400 to-purple-400 rounded-full animate-ping opacity-20"></div>
        
        <!-- Icon -->
        <svg 
          class="w-6 h-6 transition-transform duration-300 relative z-10" 
          :class="{ 'rotate-45': showQuickActions }"
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path 
            v-if="!showQuickActions"
            stroke-linecap="round" 
            stroke-linejoin="round" 
            stroke-width="2" 
            d="M13 10V3L4 14h7v7l9-11h-7z"
          />
          <path 
            v-else
            stroke-linecap="round" 
            stroke-linejoin="round" 
            stroke-width="2" 
            d="M12 6v6m0 0v6m0-6h6m-6 0H6"
          />
        </svg>

        <!-- Ripple effect on click -->
        <div class="absolute inset-0 rounded-full bg-white opacity-0 group-active:opacity-20 transition-opacity duration-150"></div>
      </button>

      <!-- Backdrop to close menu -->
      <div 
        v-if="showQuickActions"
        @click="toggleActions"
        class="fixed inset-0 -z-10"
      ></div>
    </div>
  </div>
</template>

<style scoped>
.fab-enter-active,
.fab-leave-active {
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.fab-enter-from {
  opacity: 0;
  transform: translateY(20px) scale(0.8);
}

.fab-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.8);
}

.fab-move {
  transition: transform 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

/* Enhanced shadow for floating buttons */
.shadow-3xl {
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

/* Pulse animation for main FAB */
@keyframes ping {
  75%, 100% {
    transform: scale(2);
    opacity: 0;
  }
}

/* Smooth rotation */
.rotate-45 {
  transform: rotate(45deg);
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .fixed.bottom-6.right-6 {
    bottom: 1rem;
    right: 1rem;
  }
  
  /* Hide text labels on mobile for compact view */
  @media (max-width: 640px) {
    .whitespace-nowrap {
      display: none;
    }
    
    .fab-enter-from,
    .fab-leave-to {
      transform: translateY(10px) scale(0.9);
    }
  }
}

/* Hover effects for action buttons */
.group:hover .group-hover\:scale-110 {
  transform: scale(1.1);
}

/* Focus styles for accessibility */
button:focus-visible {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}
</style>