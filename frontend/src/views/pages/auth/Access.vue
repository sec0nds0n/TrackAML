<script setup>
import FloatingConfigurator from '@/components/FloatingConfigurator.vue';
</script>

<template>
    <FloatingConfigurator />
    <div class="bg-surface-50 dark:bg-surface-950 flex items-center justify-center min-h-screen min-w-[100vw] overflow-hidden">
        <div class="flex flex-col items-center justify-center max-w-2xl mx-auto px-6">
            <!-- Professional Card Container -->
            <div class="w-full bg-surface-0 dark:bg-surface-900 rounded-2xl shadow-2xl border border-surface-200 dark:border-surface-700 overflow-hidden">
                <!-- Header Section with Subtle Accent -->
                <div class="bg-gradient-to-r from-orange-50 to-red-50 dark:from-orange-950/20 dark:to-red-950/20 px-8 py-6 border-b border-surface-200 dark:border-surface-700">
                    <div class="flex items-center justify-center mb-4">
                        <div class="flex justify-center items-center bg-orange-100 dark:bg-orange-900/30 rounded-full p-4">
                            <i class="text-orange-600 dark:text-orange-400 pi pi-shield !text-3xl"></i>
                        </div>
                    </div>
                    <h1 class="text-surface-900 dark:text-surface-0 font-semibold text-3xl text-center mb-2">
                        Access Restricted
                    </h1>
                    <p class="text-surface-600 dark:text-surface-400 text-center text-lg">
                        Authentication Required
                    </p>
                </div>

                <!-- Content Section -->
                <div class="px-8 py-10">
                    <div class="text-center mb-8">
                        <div class="bg-surface-100 dark:bg-surface-800 rounded-xl p-6 mb-6">
                            <i class="pi pi-exclamation-triangle text-orange-500 !text-4xl mb-4 block"></i>
                            <h2 class="text-surface-800 dark:text-surface-200 font-medium text-xl mb-3">
                                Insufficient Permissions
                            </h2>
                            <p class="text-surface-600 dark:text-surface-400 leading-relaxed">
                                You don't have the required permissions to access this resource. 
                                Please contact your system administrator or request appropriate access rights.
                            </p>
                        </div>

                        <!-- Professional Info Box -->
                        <div class="bg-blue-50 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mb-8">
                            <div class="flex items-start gap-3">
                                <i class="pi pi-info-circle text-blue-600 dark:text-blue-400 !text-lg mt-0.5 flex-shrink-0"></i>
                                <div class="text-left">
                                    <p class="text-blue-800 dark:text-blue-200 font-medium text-sm mb-1">
                                        Need Access?
                                    </p>
                                    <p class="text-blue-700 dark:text-blue-300 text-sm">
                                        Contact your administrator with your user ID and the resource you're trying to access.
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Action Buttons -->
                    <div class="flex flex-col sm:flex-row gap-3 justify-center">
                        <Button 
                            as="router-link" 
                            to="/" 
                            label="Return to Dashboard" 
                            icon="pi pi-home"
                            class="flex-1 sm:flex-initial"
                            severity="secondary"
                            outlined
                        />
                        <Button 
                            label="Contact Support" 
                            icon="pi pi-envelope"
                            class="flex-1 sm:flex-initial"
                            severity="warn"
                            @click="contactSupport"
                        />
                    </div>

                    <!-- Footer Info -->
                    <div class="mt-8 pt-6 border-t border-surface-200 dark:border-surface-700">
                        <p class="text-surface-500 dark:text-surface-400 text-sm text-center">
                            Error Code: 403 • Access Denied • 
                            <span class="font-mono">{{ new Date().toISOString().split('T')[0] }}</span>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    methods: {
        contactSupport() {
            // Add your support contact logic here
            // For example: open email client, show modal, etc.
            window.location.href = 'mailto:support@sigmaverde.com?subject=Access Request';
        }
    }
}
</script>
