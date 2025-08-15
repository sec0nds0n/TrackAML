<template>
    <div class="user-profile">
        <Button type="button" 
                class="p-link layout-topbar-button"
                @click="toggle">
            <Avatar :label="userInitials" 
                    shape="circle" 
                    size="normal" />
        </Button>
        
        <OverlayPanel ref="op" 
                      appendTo="body" 
                      :showCloseIcon="true" 
                      id="overlay_panel" 
                      style="width: 300px">
            <div class="flex flex-column gap-3 w-full">
                <div class="flex align-items-center gap-3 p-3 surface-100 border-round">
                    <Avatar :label="userInitials" 
                            size="large" 
                            shape="circle" />
                    <div class="flex flex-column">
                        <span class="font-semibold">{{ authStore.currentUser?.email }}</span>
                        <Tag :value="roleDisplayName" 
                             :severity="getRoleSeverity(authStore.userRole)" />
                    </div>
                </div>
                
                <div class="flex flex-column gap-2">
                    <div class="text-sm font-medium text-900">Permissions</div>
                    <div class="flex flex-wrap gap-1">
                        <Chip v-for="permission in authStore.userPermissions" 
                              :key="permission"
                              :label="formatPermission(permission)"
                              class="text-xs" />
                    </div>
                </div>
                
                <Divider />
                
                <div class="flex flex-column gap-2">
                    <Button label="Profile Settings" 
                            icon="pi pi-user" 
                            class="p-button-text p-button-sm justify-content-start"
                            @click="goToProfile" />
                    <Button label="Change Password" 
                            icon="pi pi-key" 
                            class="p-button-text p-button-sm justify-content-start"
                            @click="changePassword" />
                    <Button label="Logout" 
                            icon="pi pi-sign-out" 
                            class="p-button-text p-button-sm justify-content-start text-red-500"
                            @click="logout" />
                </div>
            </div>
        </OverlayPanel>
    </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth';
import Avatar from 'primevue/avatar';
import Button from 'primevue/button';
import Chip from 'primevue/chip';
import Divider from 'primevue/divider';
import OverlayPanel from 'primevue/overlaypanel';
import Tag from 'primevue/tag';
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const authStore = useAuthStore();
const op = ref();

const userInitials = computed(() => {
    const email = authStore.currentUser?.email || '';
    return email.substring(0, 2).toUpperCase();
});

const roleDisplayName = computed(() => {
    const roleMap = {
        'admin': 'Administrator',
        'l1_analyst': 'L1 Analyst',
        'l2_analyst': 'L2 Analyst'
    };
    return roleMap[authStore.userRole] || authStore.userRole;
});

const toggle = (event) => {
    op.value.toggle(event);
};

const formatPermission = (permission) => {
    return permission.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
};

const getRoleSeverity = (role) => {
    switch (role) {
        case 'admin': return 'danger';
        case 'l2_analyst': return 'warning';
        case 'l1_analyst': return 'info';
        default: return 'secondary';
    }
};

const goToProfile = () => {
    op.value.hide();
    router.push('/profile');
};

const changePassword = () => {
    op.value.hide();
    // Open change password dialog (to be implemented)
    console.log('Change password');
};

const logout = async () => {
    op.value.hide();
    await authStore.logout();
    router.push('/auth/login');
};
</script>

<style scoped>
.user-profile {
    position: relative;
}

.layout-topbar-button {
    background: transparent;
    border: none;
    padding: 0.5rem;
    border-radius: 50%;
    transition: background-color 0.2s;
}

.layout-topbar-button:hover {
    background: var(--surface-hover);
}
</style>
