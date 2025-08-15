<script setup>
import FloatingConfigurator from '@/components/FloatingConfigurator.vue';
import { ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();

// Error details from query params or defaults
const errorCode = ref(route.query.code || '500');
const errorMessage = ref(route.query.message || 'An unexpected error occurred');
const errorId = ref(route.query.id || generateErrorId());

function generateErrorId() {
    return 'ERR-' + Date.now().toString(36).toUpperCase() + '-' + Math.random().toString(36).substr(2, 5).toUpperCase();
}

function copyErrorId() {
    navigator.clipboard.writeText(errorId.value);
    // You might want to show a toast notification here
}

function goBack() {
    if (window.history.length > 1) {
        router.go(-1);
    } else {
        router.push('/');
    }
}

function reportIssue() {
    const subject = encodeURIComponent(`Error Report - ${errorId.value}`);
    const body = encodeURIComponent(`
Error ID: ${errorId.value}
Error Code: ${errorCode.value}
Message: ${errorMessage.value}
URL: ${window.location.href}
Timestamp: ${new Date().toISOString()}
User Agent: ${navigator.userAgent}

Please describe what you were doing when this error occurred:
`);
    window.open(`mailto:support@sigmaverde.com?subject=${subject}&body=${body}`);
}
</script>

<template>
    <FloatingConfigurator />
    <div class="bg-gradient-to-br from-surface-50 to-surface-100 dark:from-surface-950 dark:to-surface-900 flex items-center justify-center min-h-screen min-w-[100vw] overflow-hidden">
        <div class="flex flex-col items-center justify-center max-w-3xl mx-auto px-4 py-8">
            <div class="w-full bg-surface-0 dark:bg-surface-900 py-12 px-8 sm:px-16 flex flex-col items-center rounded-3xl shadow-2xl border border-surface-200 dark:border-surface-700 backdrop-blur-sm">
                <div class="flex flex-col items-center text-center space-y-8 w-full">
                    <!-- Company Logo/Brand -->
                    <div class="mb-2">
                        <div class="flex items-center space-x-3">
                            <div class="w-10 h-10 bg-gradient-to-br from-red-500 to-red-600 rounded-xl flex items-center justify-center">
                                <span class="text-white font-bold text-lg">SV</span>
                            </div>
                            <span class="text-surface-900 dark:text-surface-0 font-semibold text-xl">SigmaVerde</span>
                        </div>
                    </div>
                    
                    <!-- Error Icon -->
                    <div class="flex justify-center items-center bg-gradient-to-br from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/20 rounded-full p-6 shadow-lg">
                        <i class="pi pi-exclamation-triangle text-5xl text-red-500"></i>
                    </div>
                    
                    <!-- Error Title & Description -->
                    <div class="space-y-4 max-w-lg">
                        <h1 class="text-surface-900 dark:text-surface-0 font-bold text-4xl sm:text-5xl leading-tight">
                            Oops! Something went wrong
                        </h1>
                        <p class="text-surface-600 dark:text-surface-400 text-lg leading-relaxed">
                            We apologize for the inconvenience. Our team has been notified and is working to resolve this issue.
                        </p>
                    </div>
                    
                    <!-- Error Details Card -->
                    <div class="bg-surface-50 dark:bg-surface-800 rounded-xl p-6 w-full max-w-lg border border-surface-200 dark:border-surface-700">
                        <div class="space-y-3">
                            <div class="flex justify-between items-center">
                                <span class="text-surface-700 dark:text-surface-300 font-medium">Error Code:</span>
                                <code class="bg-surface-200 dark:bg-surface-700 px-3 py-1 rounded-md text-sm font-mono">{{ errorCode }}</code>
                            </div>
                            <div class="flex justify-between items-start">
                                <span class="text-surface-700 dark:text-surface-300 font-medium">Error ID:</span>
                                <div class="flex items-center space-x-2">
                                    <code class="bg-surface-200 dark:bg-surface-700 px-3 py-1 rounded-md text-sm font-mono">{{ errorId }}</code>
                                    <Button 
                                        icon="pi pi-copy" 
                                        @click="copyErrorId"
                                        text
                                        rounded
                                        size="small"
                                        severity="secondary"
                                        v-tooltip="'Copy Error ID'"
                                    />
                                </div>
                            </div>
                            <div class="pt-2 border-t border-surface-200 dark:border-surface-600">
                                <p class="text-surface-600 dark:text-surface-400 text-sm">
                                    {{ errorMessage }}
                                </p>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Troubleshooting Steps -->
                    <div class="text-left w-full max-w-lg">
                        <h3 class="text-surface-900 dark:text-surface-0 font-semibold text-lg mb-4 text-center">
                            Quick Solutions
                        </h3>
                        <div class="grid gap-3">
                            <div class="flex items-center p-3 bg-surface-50 dark:bg-surface-800 rounded-lg border border-surface-200 dark:border-surface-700">
                                <div class="flex-shrink-0 w-8 h-8 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center mr-3">
                                    <i class="pi pi-refresh text-blue-600 text-sm"></i>
                                </div>
                                <span class="text-surface-700 dark:text-surface-300 text-sm">Refresh the page or try again in a few moments</span>
                            </div>
                            <div class="flex items-center p-3 bg-surface-50 dark:bg-surface-800 rounded-lg border border-surface-200 dark:border-surface-700">
                                <div class="flex-shrink-0 w-8 h-8 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mr-3">
                                    <i class="pi pi-wifi text-green-600 text-sm"></i>
                                </div>
                                <span class="text-surface-700 dark:text-surface-300 text-sm">Check your internet connection and try again</span>
                            </div>
                            <div class="flex items-center p-3 bg-surface-50 dark:bg-surface-800 rounded-lg border border-surface-200 dark:border-surface-700">
                                <div class="flex-shrink-0 w-8 h-8 bg-purple-100 dark:bg-purple-900/30 rounded-full flex items-center justify-center mr-3">
                                    <i class="pi pi-history text-purple-600 text-sm"></i>
                                </div>
                                <span class="text-surface-700 dark:text-surface-300 text-sm">Clear your browser cache and cookies</span>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Action Buttons -->
                    <div class="flex flex-col sm:flex-row gap-4 pt-6 w-full max-w-lg">
                        <Button 
                            label="Try Again" 
                            icon="pi pi-refresh" 
                            @click="$router.go(0)"
                            severity="danger" 
                            class="flex-1 py-3 font-medium"
                            size="large"
                        />
                        <Button 
                            label="Go Back" 
                            icon="pi pi-arrow-left"
                            @click="goBack"
                            outlined
                            severity="secondary" 
                            class="flex-1 py-3 font-medium"
                            size="large"
                        />
                    </div>
                    
                    <!-- Secondary Actions -->
                    <div class="flex flex-col sm:flex-row gap-3 w-full max-w-lg">
                        <Button 
                            as="router-link" 
                            label="Dashboard" 
                            icon="pi pi-home"
                            to="/" 
                            text
                            severity="secondary" 
                            class="flex-1"
                        />
                        <Button 
                            label="Report Issue" 
                            icon="pi pi-send"
                            @click="reportIssue"
                            text
                            severity="secondary" 
                            class="flex-1"
                        />
                    </div>
                    
                    <!-- Support Contact -->
                    <div class="pt-8 border-t border-surface-200 dark:border-surface-700 w-full text-center">
                        <div class="space-y-3">
                            <p class="text-surface-600 dark:text-surface-400 text-sm">
                                Still need help? Our support team is here for you.
                            </p>
                            <div class="flex flex-col sm:flex-row items-center justify-center gap-4 text-sm">
                                <a 
                                    href="mailto:support@sigmaverde.com" 
                                    class="flex items-center space-x-2 text-red-500 hover:text-red-600 transition-colors"
                                >
                                    <i class="pi pi-envelope"></i>
                                    <span>support@sigmaverde.com</span>
                                </a>
                                <div class="hidden sm:block w-px h-4 bg-surface-300 dark:bg-surface-600"></div>
                                <a 
                                    href="tel:+1-800-SIGMA-VD" 
                                    class="flex items-center space-x-2 text-red-500 hover:text-red-600 transition-colors"
                                >
                                    <i class="pi pi-phone"></i>
                                    <span>1-800-SIGMA-VD</span>
                                </a>
                            </div>
                            <p class="text-surface-500 dark:text-surface-500 text-xs pt-2">
                                Reference Error ID: {{ errorId }} when contacting support
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
/* Add any custom animations or styles if needed */
.fade-in {
    animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}
</style>
