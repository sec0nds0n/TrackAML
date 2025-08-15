<template>
    <div class="grid">
        <div class="col-12">
            <!-- Header Section -->
            <div class="surface-card p-4 border-round mb-4 shadow-2">
                <div class="flex flex-column md:flex-row align-items-center gap-4">
                    <div class="relative">
                        <Avatar :label="userInitials" 
                                size="xlarge" 
                                shape="circle"
                                class="bg-gradient-to-br from-primary-400 to-primary-600 text-white shadow-4" 
                                style="width: 140px; height: 140px; font-size: 3.5rem;" />
                        <div class="absolute -bottom-2 -right-2 bg-green-500 border-circle p-2 shadow-3">
                            <i class="pi pi-check text-white text-sm"></i>
                        </div>
                    </div>
                    
                    <div class="flex-1 text-center md:text-left">
                        <h2 class="text-3xl font-bold text-900 mb-2">
                            {{ profileData.firstName }} {{ profileData.lastName }}
                        </h2>
                        <p class="text-600 text-lg mb-3">{{ authStore.currentUser?.email }}</p>
                        
                        <div class="flex flex-wrap gap-2 justify-content-center md:justify-content-start mb-3">
                            <Tag :value="roleDisplayName" 
                                 :severity="getRoleSeverity(authStore.userRole)"
                                 class="px-3 py-2 text-sm font-semibold" />
                            <Tag value="Verified Account" 
                                 severity="success"
                                 icon="pi pi-verified"
                                 class="px-3 py-2 text-sm font-semibold" />
                        </div>
                        
                        <div class="flex align-items-center gap-2 text-500 justify-content-center md:justify-content-start">
                            <i class="pi pi-calendar"></i>
                            <span>Member since {{ memberSince }}</span>
                        </div>
                    </div>
                    
                    <div class="flex flex-column gap-2">
                        <Button v-if="!editMode"
                                icon="pi pi-pencil" 
                                label="Edit Profile" 
                                @click="editMode = true"
                                severity="primary"
                                class="px-4 py-2 white-space-nowrap" />
                        
                        <template v-else>
                            <Button icon="pi pi-check" 
                                    label="Save Changes"
                                    @click="saveProfile"
                                    :loading="saving"
                                    severity="success"
                                    class="px-4 py-2 white-space-nowrap mb-2" />
                            <Button icon="pi pi-times" 
                                    label="Cancel"
                                    @click="cancelEdit"
                                    severity="secondary"
                                    outlined
                                    class="px-4 py-2 white-space-nowrap" />
                        </template>
                    </div>
                </div>
            </div>

            <div class="grid">
                <!-- Profile Information -->
                <div class="col-12 lg:col-8">
                    <div class="surface-card p-5 border-round shadow-2 mb-4">
                        <div class="flex align-items-center gap-3 mb-4">
                            <div class="bg-primary-100 border-circle p-3">
                                <i class="pi pi-user text-primary-600 text-xl"></i>
                            </div>
                            <div>
                                <h5 class="text-900 mb-1">Profile Information</h5>
                                <p class="text-600 m-0">Manage your personal details and preferences</p>
                            </div>
                        </div>
                        
                        <Divider class="mb-4" />
                        
                        <div class="grid">
                            <div class="col-12 md:col-6">
                                <div class="field">
                                    <label for="firstName" class="block text-900 font-semibold mb-2">
                                        <i class="pi pi-user mr-2"></i>First Name
                                    </label>
                                    <InputText id="firstName" 
                                               v-model="profileData.firstName" 
                                               :disabled="!editMode"
                                               class="w-full p-3"
                                               :class="{ 'surface-100': !editMode }" />
                                </div>
                            </div>
                            
                            <div class="col-12 md:col-6">
                                <div class="field">
                                    <label for="lastName" class="block text-900 font-semibold mb-2">
                                        <i class="pi pi-user mr-2"></i>Last Name
                                    </label>
                                    <InputText id="lastName" 
                                               v-model="profileData.lastName" 
                                               :disabled="!editMode"
                                               class="w-full p-3"
                                               :class="{ 'surface-100': !editMode }" />
                                </div>
                            </div>
                            
                            <div class="col-12">
                                <div class="field">
                                    <label for="email" class="block text-900 font-semibold mb-2">
                                        <i class="pi pi-envelope mr-2"></i>Email Address
                                    </label>
                                    <InputText id="email" 
                                               v-model="profileData.email" 
                                               disabled
                                               class="w-full p-3 surface-100" />
                                    <small class="text-500 flex align-items-center gap-1 mt-1">
                                        <i class="pi pi-info-circle"></i>
                                        Email cannot be changed for security reasons
                                    </small>
                                </div>
                            </div>
                            
                            <div class="col-12 md:col-6">
                                <div class="field">
                                    <label for="phone" class="block text-900 font-semibold mb-2">
                                        <i class="pi pi-phone mr-2"></i>Phone Number
                                    </label>
                                    <InputText id="phone" 
                                               v-model="profileData.phone" 
                                               :disabled="!editMode"
                                               class="w-full p-3"
                                               :class="{ 'surface-100': !editMode }" />
                                </div>
                            </div>
                            
                            <div class="col-12 md:col-6">
                                <div class="field">
                                    <label for="department" class="block text-900 font-semibold mb-2">
                                        <i class="pi pi-building mr-2"></i>Department
                                    </label>
                                    <InputText id="department" 
                                               v-model="profileData.department" 
                                               :disabled="!editMode"
                                               class="w-full p-3"
                                               :class="{ 'surface-100': !editMode }" />
                                </div>
                            </div>
                            
                            <div class="col-12">
                                <div class="field">
                                    <label for="bio" class="block text-900 font-semibold mb-2">
                                        <i class="pi pi-file-edit mr-2"></i>Bio
                                    </label>
                                    <Textarea id="bio" 
                                              v-model="profileData.bio" 
                                              :disabled="!editMode"
                                              rows="4" 
                                              class="w-full p-3"
                                              :class="{ 'surface-100': !editMode }"
                                              placeholder="Tell us about yourself..." />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Quick Stats & Role Info -->
                <div class="col-12 lg:col-4">
                    <!-- Role Information -->
                    <div class="surface-card p-4 border-round shadow-2 mb-4">
                        <div class="flex align-items-center gap-3 mb-3">
                            <div class="bg-orange-100 border-circle p-3">
                                <i class="pi pi-shield text-orange-600 text-xl"></i>
                            </div>
                            <div>
                                <h6 class="text-900 mb-1">Role & Access</h6>
                                <p class="text-600 text-sm m-0">Current permissions</p>
                            </div>
                        </div>
                        
                        <div class="bg-primary-50 p-3 border-round mb-3">
                            <div class="flex align-items-center justify-content-between mb-2">
                                <span class="font-semibold text-primary-700">{{ roleDisplayName }}</span>
                                <Tag :value="authStore.userRole.toUpperCase()" 
                                     :severity="getRoleSeverity(authStore.userRole)"
                                     class="text-xs" />
                            </div>
                            <p class="text-primary-600 text-sm m-0 line-height-3">
                                {{ getRoleDescription(authStore.userRole) }}
                            </p>
                        </div>
                        
                        <div class="mb-3">
                            <h6 class="text-900 mb-2">Permissions</h6>
                            <div class="flex flex-wrap gap-1">
                                <Chip v-for="permission in authStore.userPermissions" 
                                      :key="permission"
                                      :label="formatPermission(permission)"
                                      class="bg-green-100 text-green-700 text-xs px-2 py-1" />
                            </div>
                        </div>
                    </div>

                    <!-- Quick Stats -->
                    <div class="surface-card p-4 border-round shadow-2 mb-4">
                        <h6 class="text-900 mb-3">Quick Stats</h6>
                        <div class="grid">
                            <div class="col-6">
                                <div class="text-center p-3 bg-blue-50 border-round">
                                    <div class="text-blue-600 text-2xl font-bold">24</div>
                                    <div class="text-blue-600 text-sm">Cases</div>
                                </div>
                            </div>
                            <div class="col-6">
                                <div class="text-center p-3 bg-green-50 border-round">
                                    <div class="text-green-600 text-2xl font-bold">12</div>
                                    <div class="text-green-600 text-sm">Reports</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Security Settings -->
            <div class="surface-card p-5 border-round shadow-2 mb-4">
                <div class="flex align-items-center gap-3 mb-4">
                    <div class="bg-red-100 border-circle p-3">
                        <i class="pi pi-lock text-red-600 text-xl"></i>
                    </div>
                    <div>
                        <h5 class="text-900 mb-1">Security Settings</h5>
                        <p class="text-600 m-0">Manage your account security and authentication</p>
                    </div>
                </div>
                
                <Divider class="mb-4" />
                
                <div class="grid">
                    <div class="col-12 md:col-6">
                        <div class="border-1 surface-border border-round p-4 hover:shadow-2 transition-all transition-duration-200">
                            <div class="flex align-items-center justify-content-between">
                                <div class="flex align-items-center gap-3">
                                    <div class="bg-primary-100 border-circle p-2">
                                        <i class="pi pi-key text-primary-600"></i>
                                    </div>
                                    <div>
                                        <div class="font-semibold text-900">Password</div>
                                        <div class="text-500 text-sm">Last changed 30 days ago</div>
                                    </div>
                                </div>
                                <Button label="Change" 
                                        icon="pi pi-pencil" 
                                        size="small"
                                        outlined
                                        @click="showChangePasswordDialog = true" />
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-12 md:col-6">
                        <div class="border-1 surface-border border-round p-4 hover:shadow-2 transition-all transition-duration-200">
                            <div class="flex align-items-center justify-content-between">
                                <div class="flex align-items-center gap-3">
                                    <div class="bg-green-100 border-circle p-2">
                                        <i class="pi pi-mobile text-green-600"></i>
                                    </div>
                                    <div>
                                        <div class="font-semibold text-900">Two-Factor Authentication</div>
                                        <div class="text-500 text-sm flex align-items-center gap-1">
                                            <i :class="twoFactorEnabled ? 'pi pi-check-circle text-green-500' : 'pi pi-times-circle text-red-500'"></i>
                                            {{ twoFactorEnabled ? 'Enabled' : 'Disabled' }}
                                        </div>
                                    </div>
                                </div>
                                <Button :label="twoFactorEnabled ? 'Disable' : 'Enable'" 
                                        :icon="twoFactorEnabled ? 'pi pi-times' : 'pi pi-plus'"
                                        size="small"
                                        :severity="twoFactorEnabled ? 'danger' : 'success'"
                                        :outlined="!twoFactorEnabled"
                                        @click="toggle2FA" />
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Activity Log -->
            <div class="surface-card p-5 border-round shadow-2">
                <div class="flex align-items-center gap-3 mb-4">
                    <div class="bg-purple-100 border-circle p-3">
                        <i class="pi pi-history text-purple-600 text-xl"></i>
                    </div>
                    <div>
                        <h5 class="text-900 mb-1">Recent Activity</h5>
                        <p class="text-600 m-0">Track your recent account activities</p>
                    </div>
                </div>
                
                <Divider class="mb-4" />
                
                <DataTable :value="activityLog" 
                           :paginator="true" 
                           :rows="5"
                           responsiveLayout="scroll"
                           class="p-datatable-sm"
                           :rowHover="true">
                    <Column field="action" header="Action" :sortable="true" class="font-semibold">
                        <template #body="slotProps">
                            <div class="flex align-items-center gap-3">
                                <div :class="getActivityIconClass(slotProps.data.type)" 
                                     class="border-circle p-2">
                                    <i :class="getActivityIcon(slotProps.data.type)" 
                                       class="text-sm"></i>
                                </div>
                                <div>
                                    <div class="font-semibold text-900">{{ slotProps.data.action }}</div>
                                    <div class="text-500 text-sm">{{ slotProps.data.description }}</div>
                                </div>
                            </div>
                        </template>
                    </Column>
                    <Column field="timestamp" header="Date & Time" :sortable="true">
                        <template #body="slotProps">
                            <div class="text-900">
                                {{ formatDateTime(slotProps.data.timestamp) }}
                            </div>
                        </template>
                    </Column>
                    <Column field="ipAddress" header="IP Address" :sortable="true">
                        <template #body="slotProps">
                            <div class="flex align-items-center gap-2">
                                <i class="pi pi-globe text-500"></i>
                                <span class="font-mono text-sm">{{ slotProps.data.ipAddress }}</span>
                            </div>
                        </template>
                    </Column>
                    <Column field="device" header="Device" :sortable="true">
                        <template #body="slotProps">
                            <div class="flex align-items-center gap-2">
                                <i class="pi pi-desktop text-500"></i>
                                <span class="text-sm">{{ slotProps.data.device }}</span>
                            </div>
                        </template>
                    </Column>
                    <Column header="Status">
                        <template #body="slotProps">
                            <Tag :value="slotProps.data.status" 
                                 :severity="getStatusSeverity(slotProps.data.status)"
                                 class="text-xs" />
                        </template>
                    </Column>
                </DataTable>
            </div>
        </div>

        <!-- Change Password Dialog -->
        <Dialog v-model:visible="showChangePasswordDialog" 
                header="Change Password" 
                :modal="true" 
                :style="{ width: '450px' }"
                class="p-fluid">
            <template #header>
                <div class="flex align-items-center gap-2">
                    <i class="pi pi-key text-primary-600"></i>
                    <span class="font-semibold">Change Password</span>
                </div>
            </template>
            
            <div class="flex flex-column gap-4 p-4">
                <div class="field">
                    <label for="currentPassword" class="block text-900 font-semibold mb-2">
                        <i class="pi pi-lock mr-2"></i>Current Password
                    </label>
                    <Password id="currentPassword" 
                              v-model="passwordData.current" 
                              :feedback="false"
                              :toggleMask="true"
                              class="w-full"
                              placeholder="Enter your current password"
                              :class="{ 'p-invalid': passwordErrors.current }" />
                    <small v-if="passwordErrors.current" class="p-error">{{ passwordErrors.current }}</small>
                </div>
                
                <div class="field">
                    <label for="newPassword" class="block text-900 font-semibold mb-2">
                        <i class="pi pi-key mr-2"></i>New Password
                    </label>
                    <Password id="newPassword" 
                              v-model="passwordData.new" 
                              :feedback="true"
                              :toggleMask="true"
                              class="w-full"
                              placeholder="Enter your new password"
                              :class="{ 'p-invalid': passwordErrors.new }" />
                    <small v-if="passwordErrors.new" class="p-error">{{ passwordErrors.new }}</small>
                </div>
                
                <div class="field">
                    <label for="confirmPassword" class="block text-900 font-semibold mb-2">
                        <i class="pi pi-check mr-2"></i>Confirm New Password
                    </label>
                    <Password id="confirmPassword" 
                              v-model="passwordData.confirm" 
                              :feedback="false"
                              :toggleMask="true"
                              class="w-full"
                              placeholder="Confirm your new password"
                              :class="{ 'p-invalid': passwordErrors.confirm }" />
                    <small v-if="passwordErrors.confirm" class="p-error">{{ passwordErrors.confirm }}</small>
                </div>
                
                <div class="bg-blue-50 p-3 border-round">
                    <div class="flex align-items-center gap-2 mb-2">
                        <i class="pi pi-info-circle text-blue-600"></i>
                        <span class="font-semibold text-blue-900">Password Requirements</span>
                    </div>
                    <ul class="text-blue-700 text-sm m-0 pl-4">
                        <li>At least 8 characters long</li>
                        <li>Contains uppercase and lowercase letters</li>
                        <li>Contains at least one number</li>
                        <li>Contains at least one special character</li>
                    </ul>
                </div>
            </div>
            
            <template #footer>
                <div class="flex gap-2">
                    <Button label="Cancel" 
                            icon="pi pi-times" 
                            @click="closePasswordDialog" 
                            outlined
                            class="flex-1" />
                    <Button label="Change Password" 
                            icon="pi pi-check" 
                            @click="changePassword" 
                            :disabled="!isPasswordValid"
                            :loading="changingPassword"
                            class="flex-1" />
                </div>
            </template>
        </Dialog>

        <!-- Success Toast -->
        <Toast />
    </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth';
import Avatar from 'primevue/avatar';
import Button from 'primevue/button';
import Chip from 'primevue/chip';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import Dialog from 'primevue/dialog';
import Divider from 'primevue/divider';
import InputText from 'primevue/inputtext';
import Password from 'primevue/password';
import Tag from 'primevue/tag';
import Textarea from 'primevue/textarea';
import Toast from 'primevue/toast';
import { useToast } from 'primevue/usetoast';
import { computed, onMounted, ref, watch } from 'vue';

const authStore = useAuthStore();
const toast = useToast();

// Reactive data
const editMode = ref(false);
const saving = ref(false);
const showChangePasswordDialog = ref(false);
const changingPassword = ref(false);
const twoFactorEnabled = ref(false);

const profileData = ref({
    firstName: 'John',
    lastName: 'Doe',
    email: '',
    phone: '+1 (555) 123-4567',
    department: 'Compliance & Risk',
    bio: 'Experienced analyst specializing in cryptocurrency compliance and anti-money laundering investigations with over 5 years of expertise in financial crime detection.'
});

const originalProfileData = ref({});

const passwordData = ref({
    current: '',
    new: '',
    confirm: ''
});

const passwordErrors = ref({
    current: '',
    new: '',
    confirm: ''
});

const activityLog = ref([
    {
        action: 'Logged in',
        description: 'Successful login to dashboard',
        type: 'login',
        timestamp: new Date(),
        ipAddress: '192.168.1.100',
        device: 'Chrome on Windows',
        status: 'Success'
    },
    {
        action: 'Updated case #12345',
        description: 'Modified case details and status',
        type: 'case',
        timestamp: new Date(Date.now() - 3600000),
        ipAddress: '192.168.1.100',
        device: 'Chrome on Windows',
        status: 'Success'
    },
    {
        action: 'Generated compliance report',
        description: 'Created monthly compliance summary',
        type: 'report',
        timestamp: new Date(Date.now() - 7200000),
        ipAddress: '192.168.1.100',
        device: 'Chrome on Windows',
        status: 'Success'
    },
    {
        action: 'Profile updated',
        description: 'Changed profile information',
        type: 'profile',
        timestamp: new Date(Date.now() - 86400000),
        ipAddress: '192.168.1.100',
        device: 'Chrome on Windows',
        status: 'Success'
    },
    {
        action: 'Failed login attempt',
        description: 'Invalid credentials provided',
        type: 'security',
        timestamp: new Date(Date.now() - 172800000),
        ipAddress: '203.0.113.45',
        device: 'Unknown Browser',
        status: 'Failed'
    }
]);

// Computed properties
const userInitials = computed(() => {
    const firstName = profileData.value.firstName || '';
    const lastName = profileData.value.lastName || '';
    return (firstName.charAt(0) + lastName.charAt(0)).toUpperCase();
});

const roleDisplayName = computed(() => {
    const roleMap = {
        'admin': 'Administrator',
        'l1_analyst': 'L1 Analyst',
        'l2_analyst': 'L2 Analyst'
    };
    return roleMap[authStore.userRole] || authStore.userRole;
});

const memberSince = computed(() => {
    return new Date().toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'long' 
    });
});

const isPasswordValid = computed(() => {
    return passwordData.value.current && 
           passwordData.value.new && 
           passwordData.value.confirm &&
           passwordData.value.new === passwordData.value.confirm &&
           passwordData.value.new.length >= 8 &&
           !passwordErrors.value.current &&
           !passwordErrors.value.new &&
           !passwordErrors.value.confirm;
});

// Methods
const getRoleSeverity = (role) => {
    switch (role) {
        case 'admin': return 'danger';
        case 'l2_analyst': return 'warning';
        case 'l1_analyst': return 'info';
        default: return 'secondary';
    }
};

const getRoleDescription = (role) => {
    const descriptions = {
        'admin': 'Full system access with user management capabilities and advanced configuration options',
        'l1_analyst': 'Basic analysis and case creation permissions with standard reporting access',
        'l2_analyst': 'Advanced analysis with case approval capabilities and enhanced reporting features'
    };
    return descriptions[role] || 'Standard user access';
};

const formatPermission = (permission) => {
    return permission.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
};

const getActivityIcon = (type) => {
    const icons = {
        'login': 'pi pi-sign-in',
        'case': 'pi pi-file',
        'report': 'pi pi-chart-bar',
        'profile': 'pi pi-user',
        'security': 'pi pi-shield'
    };
    return icons[type] || 'pi pi-circle';
};

const getActivityIconClass = (type) => {
    const classes = {
        'login': 'bg-blue-100 text-blue-600',
        'case': 'bg-green-100 text-green-600',
        'report': 'bg-purple-100 text-purple-600',
        'profile': 'bg-orange-100 text-orange-600',
        'security': 'bg-red-100 text-red-600'
    };
    return classes[type] || 'bg-gray-100 text-gray-600';
};

const getStatusSeverity = (status) => {
    switch (status.toLowerCase()) {
        case 'success': return 'success';
        case 'failed': return 'danger';
        case 'warning': return 'warning';
        default: return 'info';
    }
};

const formatDateTime = (date) => {
    return new Date(date).toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
};

const validatePassword = () => {
    passwordErrors.value = {
        current: '',
        new: '',
        confirm: ''
    };

    if (!passwordData.value.current) {
        passwordErrors.value.current = 'Current password is required';
    }

    if (!passwordData.value.new) {
        passwordErrors.value.new = 'New password is required';
    } else if (passwordData.value.new.length < 8) {
        passwordErrors.value.new = 'Password must be at least 8 characters long';
    }

    if (!passwordData.value.confirm) {
        passwordErrors.value.confirm = 'Please confirm your new password';
    } else if (passwordData.value.new !== passwordData.value.confirm) {
        passwordErrors.value.confirm = 'Passwords do not match';
    }
};

const saveProfile = async () => {
    saving.value = true;
    try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // Update original data
        originalProfileData.value = { ...profileData.value };
        editMode.value = false;
        
        toast.add({
            severity: 'success',
            summary: 'Profile Updated',
            detail: 'Your profile has been successfully updated.',
            life: 3000
        });
        
        console.log('Profile saved:', profileData.value);
    } catch (error) {
        toast.add({
            severity: 'error',
            summary: 'Update Failed',
            detail: 'Failed to update profile. Please try again.',
            life: 3000
        });
        console.error('Error saving profile:', error);
    } finally {
        saving.value = false;
    }
};

const cancelEdit = () => {
    profileData.value = { ...originalProfileData.value };
    editMode.value = false;
    toast.add({
        severity: 'info',
        summary: 'Edit Cancelled',
        detail: 'Profile changes have been discarded.',
        life: 3000
    });
};

const closePasswordDialog = () => {
    passwordData.value = {
        current: '',
        new: '',
        confirm: ''
    };
    passwordErrors.value = {
        current: '',
        new: '',
        confirm: ''
    };
    showChangePasswordDialog.value = false;
};

const changePassword = async () => {
    validatePassword();
    
    if (!isPasswordValid.value) {
        return;
    }
    
    changingPassword.value = true;
    try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Reset form
        closePasswordDialog();
        
        toast.add({
            severity: 'success',
            summary: 'Password Changed',
            detail: 'Your password has been successfully updated.',
            life: 3000
        });
        
        console.log('Password changed successfully');
    } catch (error) {
        toast.add({
            severity: 'error',
            summary: 'Password Change Failed',
            detail: 'Failed to change password. Please try again.',
            life: 3000
        });
        console.error('Error changing password:', error);
    } finally {
        changingPassword.value = false;
    }
};

const toggle2FA = async () => {
    try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        twoFactorEnabled.value = !twoFactorEnabled.value;
        
        toast.add({
            severity: twoFactorEnabled.value ? 'success' : 'warn',
            summary: `2FA ${twoFactorEnabled.value ? 'Enabled' : 'Disabled'}`,
            detail: `Two-factor authentication has been ${twoFactorEnabled.value ? 'enabled' : 'disabled'} for your account.`,
            life: 3000
        });
        
        console.log('2FA toggled:', twoFactorEnabled.value);
    } catch (error) {
        toast.add({
            severity: 'error',
            summary: '2FA Toggle Failed',
            detail: 'Failed to update two-factor authentication settings.',
            life: 3000
        });
        console.error('Error toggling 2FA:', error);
    }
};

// Watch for password changes to validate in real-time
watch([() => passwordData.value.new, () => passwordData.value.confirm], () => {
    if (passwordData.value.new && passwordData.value.confirm) {
        if (passwordData.value.new !== passwordData.value.confirm) {
            passwordErrors.value.confirm = 'Passwords do not match';
        } else {
            passwordErrors.value.confirm = '';
        }
    }
});

// Lifecycle
onMounted(() => {
    // Initialize profile data with current user info
    profileData.value.email = authStore.currentUser?.email || '';
    originalProfileData.value = { ...profileData.value };
    
    // Simulate loading 2FA status
    setTimeout(() => {
        twoFactorEnabled.value = Math.random() > 0.5; // Random for demo
    }, 500);
});
</script>

<style scoped>
.field {
    margin-bottom: 1.5rem;
}

.surface-card {
    background: var(--surface-card);
    border: 1px solid var(--surface-border);
    transition: all 0.2s ease-in-out;
}

.surface-card:hover {
    border-color: var(--primary-200);
}

.bg-gradient-to-br {
    background: linear-gradient(135deg, var(--primary-400), var(--primary-600));
}

.font-mono {
    font-family: 'Courier New', Courier, monospace;
}

.line-height-3 {
    line-height: 1.5;
}

.shadow-2 {
    box-shadow: 0 4px 25px 0 rgba(0, 0, 0, 0.1);
}

.shadow-3 {
    box-shadow: 0 6px 30px 0 rgba(0, 0, 0, 0.15);
}

.shadow-4 {
    box-shadow: 0 8px 35px 0 rgba(0, 0, 0, 0.2);
}

.transition-all {
    transition: all 0.3s ease;
}

.transition-duration-200 {
    transition-duration: 200ms;
}

.hover\:shadow-2:hover {
    box-shadow: 0 4px 25px 0 rgba(0, 0, 0, 0.1);
}

/* Custom animations */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.surface-card {
    animation: fadeInUp 0.5s ease-out;
}

.surface-card:nth-child(2) {
    animation-delay: 0.1s;
}

.surface-card:nth-child(3) {
    animation-delay: 0.2s;
}

.surface-card:nth-child(4) {
    animation-delay: 0.3s;
}

/* Enhanced input focus states */
.p-inputtext:enabled:focus,
.p-password:not(.p-disabled).p-focus .p-inputtext,
.p-inputtextarea:enabled:focus {
    outline: 0 none;
    outline-offset: 0;
    box-shadow: 0 0 0 0.2rem var(--primary-200);
    border-color: var(--primary-500);
}

/* Custom button hover effects */
.p-button:not(:disabled):hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.p-button:not(:disabled):active {
    transform: translateY(0);
}

/* Enhanced card hover effects */
.surface-card {
    position: relative;
    overflow: hidden;
}

.surface-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
    transition: left 0.5s;
}

.surface-card:hover::before {
    left: 100%;
}

/* Custom scrollbar for activity log */
.p-datatable .p-datatable-tbody::-webkit-scrollbar {
    width: 6px;
}

.p-datatable .p-datatable-tbody::-webkit-scrollbar-track {
    background: var(--surface-100);
    border-radius: 3px;
}

.p-datatable .p-datatable-tbody::-webkit-scrollbar-thumb {
    background: var(--primary-300);
    border-radius: 3px;
}

.p-datatable .p-datatable-tbody::-webkit-scrollbar-thumb:hover {
    background: var(--primary-400);
}

/* Responsive enhancements */
@media (max-width: 768px) {
    .surface-card {
        margin-bottom: 1rem;
    }
    
    .grid .col-12:last-child .surface-card {
        margin-bottom: 0;
    }
}

/* Loading state animations */
@keyframes pulse {
    0%, 100% {
        opacity: 1;
    }
    50% {
        opacity: 0.5;
    }
}

.p-button-loading .p-button-icon {
    animation: pulse 1.5s ease-in-out infinite;
}

/* Enhanced tag styles */
.p-tag {
    font-weight: 600;
    letter-spacing: 0.02em;
}

/* Custom chip styles */
.p-chip {
    font-size: 0.75rem;
    font-weight: 500;
    border-radius: 12px;
}

/* Dialog enhancements */
.p-dialog .p-dialog-header {
    background: linear-gradient(135deg, var(--primary-50), var(--surface-0));
    border-bottom: 1px solid var(--surface-200);
}

.p-dialog .p-dialog-content {
    padding: 0;
}

.p-dialog .p-dialog-footer {
    background: var(--surface-50);
    border-top: 1px solid var(--surface-200);
}

/* Avatar enhancements */
.p-avatar {
    border: 3px solid var(--surface-0);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

/* DataTable row hover effect */
.p-datatable .p-datatable-tbody > tr:hover {
    background: var(--primary-50);
    transform: scale(1.01);
    transition: all 0.2s ease;
}

/* Custom divider */
.p-divider.p-divider-horizontal:before {
    border-top: 1px solid var(--surface-300);
}

/* Toast positioning */
.p-toast {
    z-index: 9999;
}

/* Form validation styles */
.p-invalid.p-component {
    border-color: var(--red-500);
    box-shadow: 0 0 0 0.2rem rgba(239, 68, 68, 0.2);
}

.p-error {
    color: var(--red-500);
    font-size: 0.875rem;
    margin-top: 0.25rem;
    display: flex;
    align-items: center;;
    gap: 0.25rem;
}

.p-error::before {
    content: '⚠';
    font-size: 0.75rem;
}
</style>
