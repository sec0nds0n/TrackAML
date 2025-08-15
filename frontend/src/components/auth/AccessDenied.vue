<template>
    <div class="surface-ground flex align-items-center justify-content-center min-h-screen min-w-screen overflow-hidden">
        <div class="flex flex-column align-items-center justify-content-center">
            <div style="border-radius: 56px; padding: 0.3rem; background: linear-gradient(180deg, rgba(233, 30, 99, 0.4) 10%, rgba(33, 150, 243, 0) 30%);">
                <div class="w-full surface-card py-8 px-5 sm:px-8 flex flex-column align-items-center" style="border-radius: 53px">
                    <div class="flex justify-content-center align-items-center bg-pink-500 border-circle" style="height:3.2rem; width:3.2rem;">
                        <i class="pi pi-fw pi-exclamation-circle text-2xl text-white"></i>
                    </div>
                    <h1 class="text-900 font-bold text-5xl mb-2">Access Denied</h1>
                    <div class="text-600 mb-5">You do not have the required permissions to access this page.</div>
                    <img src="/demo/images/access/asset-access.svg" alt="Access denied" class="mb-5" width="80%">
                    <Button icon="pi pi-arrow-left" 
                            label="Go to Dashboard" 
                            @click="goToDashboard"
                            class="p-button-text" />
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth';
import Button from 'primevue/button';
import { useRouter } from 'vue-router';

const router = useRouter();
const authStore = useAuthStore();

const goToDashboard = () => {
    // Redirect based on user role
    if (authStore.isAuthenticated) {
        switch (authStore.userRole) {
            case 'l1_analyst':
            case 'l2_analyst':
                router.push('/monitoring/cases');
                break;
            case 'admin':
                router.push('/dashboard');
                break;
            default:
                router.push('/');
        }
    } else {
        router.push('/auth/login');
    }
};
</script>
