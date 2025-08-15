<template>
    <div class="surface-ground min-h-screen p-4">
        <div class="max-w-4xl mx-auto">
            <div class="card mb-4">
                <h2 class="text-center mb-4">RBAC Login Demo</h2>
                <p class="text-center text-500 mb-4">
                    Test the Role-Based Access Control system with different user roles
                </p>
                
                <div class="grid">
                    <div class="col-12 md:col-4">
                        <div class="surface-card p-4 border-round text-center">
                            <h5>Admin User</h5>
                            <p class="text-500 mb-3">Full access to all features</p>
                            <div class="mb-3">
                                <strong>Email:</strong> admin@example.com<br>
                                <strong>Password:</strong> password
                            </div>
                            <div class="flex flex-wrap gap-1 justify-content-center mb-3">
                                <Chip label="read" class="text-xs" />
                                <Chip label="write" class="text-xs" />
                                <Chip label="approve" class="text-xs" />
                                <Chip label="manage_users" class="text-xs" />
                            </div>
                            <Button label="Login as Admin" 
                                    @click="loginAs('admin@example.com')"
                                    class="w-full p-button-danger" />
                        </div>
                    </div>
                    
                    <div class="col-12 md:col-4">
                        <div class="surface-card p-4 border-round text-center">
                            <h5>L1 Analyst</h5>
                            <p class="text-500 mb-3">Can read and write, escalate to L2</p>
                            <div class="mb-3">
                                <strong>Email:</strong> l1@example.com<br>
                                <strong>Password:</strong> password
                            </div>
                            <div class="flex flex-wrap gap-1 justify-content-center mb-3">
                                <Chip label="read" class="text-xs" />
                                <Chip label="write" class="text-xs" />
                            </div>
                            <Button label="Login as L1" 
                                    @click="loginAs('l1@example.com')"
                                    class="w-full p-button-info" />
                        </div>
                    </div>
                    
                    <div class="col-12 md:col-4">
                        <div class="surface-card p-4 border-round text-center">
                            <h5>L2 Analyst</h5>
                            <p class="text-500 mb-3">Can read, write, and approve cases</p>
                            <div class="mb-3">
                                <strong>Email:</strong> l2@example.com<br>
                                <strong>Password:</strong> password
                            </div>
                            <div class="flex flex-wrap gap-1 justify-content-center mb-3">
                                <Chip label="read" class="text-xs" />
                                <Chip label="write" class="text-xs" />
                                <Chip label="approve" class="text-xs" />
                            </div>
                            <Button label="Login as L2" 
                                    @click="loginAs('l2@example.com')"
                                    class="w-full p-button-warning" />
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="card" v-if="authStore.isAuthenticated">
                <h4>Current User Session</h4>
                <div class="grid">
                    <div class="col-12 md:col-6">
                        <div class="flex align-items-center gap-3 mb-3">
                            <Avatar :label="userInitials" size="large" shape="circle" />
                            <div>
                                <div class="font-semibold">{{ authStore.currentUser?.email }}</div>
                                <Tag :value="roleDisplayName" 
                                     :severity="getRoleSeverity(authStore.userRole)" />
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-12 md:col-6">
                        <div class="text-right">
                            <Button label="Logout" 
                                    icon="pi pi-sign-out"
                                    @click="logout"
                                    class="p-button-outlined" />
                        </div>
                    </div>
                </div>
                
                <div class="grid">
                    <div class="col-12 md:col-6">
                        <h6>Permissions</h6>
                        <div class="flex flex-wrap gap-2">
                            <Chip v-for="permission in authStore.userPermissions" 
                                  :key="permission"
                                  :label="formatPermission(permission)" />
                        </div>
                    </div>
                    
                    <div class="col-12 md:col-6">
                        <h6>Access Test</h6>
                        <div class="flex flex-column gap-2">
                            <div class="flex align-items-center gap-2">
                                <i :class="authStore.canRead ? 'pi pi-check text-green-500' : 'pi pi-times text-red-500'"></i>
                                <span>Can Read</span>
                            </div>
                            <div class="flex align-items-center gap-2">
                                <i :class="authStore.canWrite ? 'pi pi-check text-green-500' : 'pi pi-times text-red-500'"></i>
                                <span>Can Write</span>
                            </div>
                            <div class="flex align-items-center gap-2">
                                <i :class="authStore.canApprove ? 'pi pi-check text-green-500' : 'pi pi-times text-red-500'"></i>
                                <span>Can Approve</span>
                            </div>
                            <div class="flex align-items-center gap-2">
                                <i :class="authStore.canManageUsers ? 'pi pi-check text-green-500' : 'pi pi-times text-red-500'"></i>
                                <span>Can Manage Users</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <Divider />
                
                <div class="flex flex-wrap gap-2">
                    <Button label="Go to Dashboard" 
                            icon="pi pi-home"
                            @click="$router.push('/dashboard')"
                            v-if="authStore.hasPermission('read')" />
                    <Button label="Case Management" 
                            icon="pi pi-briefcase"
                            @click="$router.push('/monitoring/cases')"
                            v-if="authStore.hasAnyRole(['l1_analyst', 'l2_analyst', 'admin'])" />
                    <Button label="Crypto Monitoring" 
                            icon="pi pi-chart-line"
                            @click="$router.push('/monitoring/crypto')"
                            v-if="authStore.hasPermission('read')" />
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth';
import Avatar from 'primevue/avatar';
import Button from 'primevue/button';
import Chip from 'primevue/chip';
import Divider from 'primevue/divider';
import Tag from 'primevue/tag';
import { computed } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const authStore = useAuthStore();

// Predefined user roles and permissions
const userRoles = {
    'admin@example.com': {
        role: 'admin',
        permissions: ['read', 'write', 'approve', 'manage_users']
    },
    'l1@example.com': {
        role: 'l1_analyst',
        permissions: ['read', 'write']
    },
    'l2@example.com': {
        role: 'l2_analyst',
        permissions: ['read', 'write', 'approve']
    }
};

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

const loginAs = async (email) => {
    const user = userRoles[email];
    if (user) {
        await authStore.login({
            email: email,
            role: user.role,
            permissions: user.permissions,
            token: 'dummy-jwt-token'
        });
    }
};

const logout = async () => {
    await authStore.logout();
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
</script>
