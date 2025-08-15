<script setup>
import { useLayout } from '@/layout/composables/layout';
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const { toggleMenu, toggleDarkMode, isDarkTheme } = useLayout();
useLayout();
const router = useRouter();

const showProfileDropdown = ref(false);

const toggleProfileDropdown = () => {
    showProfileDropdown.value = !showProfileDropdown.value;
};

const closeProfileDropdown = () => {
    showProfileDropdown.value = false;
};

const handleSignOut = () => {
    console.log('Signing out...');
    closeProfileDropdown();
    router.push('/logout');
};

const handleMyProfile = () => {
    console.log('Navigate to profile...');
    closeProfileDropdown();
    router.push('/profile');
};
</script>

<template>
    <div class="layout-topbar">
        <div class="layout-topbar-logo-container">
            <button class="layout-menu-button layout-topbar-action" @click="toggleMenu">
                <i class="pi pi-bars"></i>
            </button>
            <router-link to="/" class="layout-topbar-logo">
                <img src="/sigma-verde-logo.svg" alt="Sigma Verde" class="logo-image" />
            </router-link>
        </div>

        <div class="layout-topbar-actions">
            <div class="layout-config-menu">
                <button type="button" class="layout-topbar-action" @click="toggleDarkMode">
                    <i :class="['pi', { 'pi-moon': isDarkTheme, 'pi-sun': !isDarkTheme }]"></i>
                </button>
            </div>

            <div class="layout-topbar-menu hidden lg:block">
                <div class="layout-topbar-menu-content">
                    <button type="button" class="layout-topbar-action">
                        <i class="pi pi-calendar"></i>
                        <span>Calendar</span>
                    </button>
                    <button type="button" class="layout-topbar-action">
                        <i class="pi pi-inbox"></i>
                        <span>Messages</span>
                    </button>
                    <div class="relative" v-click-outside="closeProfileDropdown">
                        <button 
                            type="button" 
                            class="layout-topbar-action"
                            @click="toggleProfileDropdown"
                        >
                            <i class="pi pi-user"></i>
                            <span>Profile</span>
                        </button>
                        <div 
                            class="profile-dropdown"
                            :class="{ 'profile-dropdown-visible': showProfileDropdown }"
                        >
                            <div class="profile-dropdown-content">
                                <button type="button" class="profile-dropdown-item" @click="handleMyProfile">
                                    <i class="pi pi-user"></i>
                                    <span>My Profile</span>
                                </button>
                                <button type="button" class="profile-dropdown-item" @click="handleSignOut">
                                    <i class="pi pi-sign-out"></i>
                                    <span>Sign Out</span>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.logo-image {
    height: 2rem;
    width: auto;
    margin-right: 0.5rem;
}

.layout-topbar-logo {
    display: flex;
    align-items: center;
}

.profile-dropdown {
    position: absolute;
    top: 100%;
    right: 0;
    z-index: 1000;
    min-width: 12rem;
    margin-top: 0.5rem;
    opacity: 0;
    visibility: hidden;
    transform: translateY(-10px);
    transition: all 0.2s ease-in-out;
}

.profile-dropdown-visible {
    opacity: 1;
    visibility: visible;
    transform: translateY(0);
}

.profile-dropdown-content {
    background: var(--surface-card);
    border: 1px solid var(--surface-border);
    border-radius: var(--border-radius);
    box-shadow: var(--shadow-2);
    padding: 0.5rem 0;
}

.profile-dropdown-item {
    display: flex;
    align-items: center;
    width: 100%;
    padding: 0.75rem 1rem;
    border: none;
    background: transparent;
    color: var(--text-color);
    cursor: pointer;
    transition: background-color 0.2s;
    text-align: left;
    gap: 0.5rem;
}

.profile-dropdown-item:hover {
    background: var(--surface-hover);
}

.profile-dropdown-item i {
    font-size: 0.875rem;
}

.profile-dropdown-item span {
    font-size: 0.875rem;
}
</style>