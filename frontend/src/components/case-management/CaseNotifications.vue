<template>
    <div class="notification-manager">
        <!-- Notification Settings -->
        <div class="card mb-4">
            <h5>Notification Settings</h5>
            <div class="grid">
                <div class="col-12 md:col-6">
                    <div class="field">
                        <label class="font-medium mb-2 block">Email Notifications</label>
                        <div class="flex flex-column gap-2">
                            <div class="flex align-items-center">
                                <Checkbox v-model="settings.emailNotifications.l1ToL2" 
                                         :binary="true" 
                                         inputId="l1tol2" />
                                <label for="l1tol2" class="ml-2">L1 to L2 Document Transfers</label>
                            </div>
                            <div class="flex align-items-center">
                                <Checkbox v-model="settings.emailNotifications.anomalies" 
                                         :binary="true" 
                                         inputId="anomalies" />
                                <label for="anomalies" class="ml-2">Anomalous Transactions</label>
                            </div>
                            <div class="flex align-items-center">
                                <Checkbox v-model="settings.emailNotifications.blacklisted" 
                                         :binary="true" 
                                         inputId="blacklisted" />
                                <label for="blacklisted" class="ml-2">New Blacklisted Wallets</label>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-12 md:col-6">
                    <div class="field">
                        <label class="font-medium mb-2 block">In-App Notifications</label>
                        <div class="flex flex-column gap-2">
                            <div class="flex align-items-center">
                                <Checkbox v-model="settings.appNotifications.documentUpdates" 
                                         :binary="true" 
                                         inputId="docUpdates" />
                                <label for="docUpdates" class="ml-2">Document Updates</label>
                            </div>
                            <div class="flex align-items-center">
                                <Checkbox v-model="settings.appNotifications.caseAssignments" 
                                         :binary="true" 
                                         inputId="caseAssign" />
                                <label for="caseAssign" class="ml-2">Case Assignments</label>
                            </div>
                            <div class="flex align-items-center">
                                <Checkbox v-model="settings.appNotifications.statusChanges" 
                                         :binary="true" 
                                         inputId="statusChanges" />
                                <label for="statusChanges" class="ml-2">Status Changes</label>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="col-12">
                    <div class="field">
                        <label class="font-medium mb-2 block">Stakeholder Email Recipients</label>
                        <div class="flex flex-wrap gap-2 mb-2">
                            <Chip v-for="recipient in settings.stakeholderEmails" 
                                  :key="recipient"
                                  :label="recipient"
                                  removable 
                                  @remove="removeStakeholder(recipient)" />
                        </div>
                        <div class="p-inputgroup">
                            <InputText v-model="newStakeholderEmail" 
                                      placeholder="Enter stakeholder email"
                                      @keydown.enter="addStakeholder" />
                            <Button icon="pi pi-plus" 
                                    @click="addStakeholder"
                                    :disabled="!isValidEmail(newStakeholderEmail)" />
                        </div>
                    </div>
                </div>
            </div>

            <div class="flex justify-content-end">
                <Button label="Save Settings" 
                        icon="pi pi-save"
                        @click="saveSettings" />
            </div>
        </div>

        <!-- Recent Notifications -->
        <div class="card">
            <div class="flex justify-content-between align-items-center mb-3">
                <h5 class="m-0">Recent Notifications</h5>
                <Button icon="pi pi-refresh" 
                        @click="loadNotifications"
                        :loading="loading"
                        class="p-button-text" />
            </div>

            <DataTable :value="notifications"
                       :paginator="true"
                       :rows="5"
                       :loading="loading"
                       class="p-datatable-sm">
                <Column field="timestamp" header="Time" :sortable="true">
                    <template #body="slotProps">
                        {{ formatDateTime(slotProps.data.timestamp) }}
                    </template>
                </Column>
                
                <Column field="type" header="Type" :sortable="true">
                    <template #body="slotProps">
                        <Tag :value="slotProps.data.type"
                             :severity="getNotificationTypeSeverity(slotProps.data.type)" />
                    </template>
                </Column>
                
                <Column field="message" header="Message">
                    <template #body="slotProps">
                        <div class="notification-message">
                            <div class="font-medium">{{ slotProps.data.title }}</div>
                            <small class="text-500">{{ slotProps.data.message }}</small>
                        </div>
                    </template>
                </Column>
                
                <Column field="status" header="Status" :sortable="true">
                    <template #body="slotProps">
                        <Tag :value="slotProps.data.status"
                             :severity="getDeliveryStatusSeverity(slotProps.data.status)" />
                    </template>
                </Column>
                
                <Column field="recipients" header="Recipients">
                    <template #body="slotProps">
                        <div class="flex align-items-center gap-2">
                            <Avatar v-for="recipient in slotProps.data.recipients.slice(0, 3)"
                                    :key="recipient"
                                    :label="getInitials(recipient)"
                                    size="small"
                                    shape="circle" />
                            <span v-if="slotProps.data.recipients.length > 3"
                                  class="text-500">
                                +{{ slotProps.data.recipients.length - 3 }} more
                            </span>
                        </div>
                    </template>
                </Column>
            </DataTable>
        </div>
    </div>
</template>

<script setup>
import Avatar from 'primevue/avatar';
import Button from 'primevue/button';
import Checkbox from 'primevue/checkbox';
import Chip from 'primevue/chip';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import InputText from 'primevue/inputtext';
import Tag from 'primevue/tag';
import { onMounted, ref } from 'vue';

// Reactive state
const loading = ref(false);
const notifications = ref([]);
const newStakeholderEmail = ref('');

const settings = ref({
    emailNotifications: {
        l1ToL2: true,
        anomalies: true,
        blacklisted: true
    },
    appNotifications: {
        documentUpdates: true,
        caseAssignments: true,
        statusChanges: true
    },
    stakeholderEmails: [
        'compliance@exchange.com',
        'regulator@gov.org'
    ]
});

// Methods
const loadNotifications = async () => {
    loading.value = true;
    try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        notifications.value = [
            {
                id: 1,
                timestamp: new Date(),
                type: 'document_transfer',
                title: 'L1 Document Transfer',
                message: 'New documents transferred from L1 to L2 for review',
                status: 'delivered',
                recipients: ['John Doe', 'Jane Smith'],
            },
            {
                id: 2,
                timestamp: new Date(Date.now() - 3600000),
                type: 'anomaly',
                title: 'Suspicious Transaction Pattern',
                message: 'Multiple high-value transactions detected from unverified wallet',
                status: 'sent',
                recipients: ['Compliance Team', 'Risk Management'],
            },
            {
                id: 3,
                timestamp: new Date(Date.now() - 7200000),
                type: 'blacklist',
                title: 'New Blacklisted Wallet',
                message: 'Wallet address added to blacklist due to suspicious activity',
                status: 'pending',
                recipients: ['Exchange Admin', 'Compliance Officer'],
            }
        ];
    } catch (error) {
        console.error('Error loading notifications:', error);
    } finally {
        loading.value = false;
    }
};

const saveSettings = async () => {
    try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        console.log('Settings saved:', settings.value);
    } catch (error) {
        console.error('Error saving settings:', error);
    }
};

const addStakeholder = () => {
    if (isValidEmail(newStakeholderEmail.value) && 
        !settings.value.stakeholderEmails.includes(newStakeholderEmail.value)) {
        settings.value.stakeholderEmails.push(newStakeholderEmail.value);
        newStakeholderEmail.value = '';
    }
};

const removeStakeholder = (email) => {
    settings.value.stakeholderEmails = settings.value.stakeholderEmails.filter(e => e !== email);
};

const isValidEmail = (email) => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
};

const formatDateTime = (date) => {
    return new Date(date).toLocaleString();
};

const getInitials = (name) => {
    return name
        .split(' ')
        .map(n => n[0])
        .join('');
};

const getNotificationTypeSeverity = (type) => {
    switch (type) {
        case 'document_transfer': return 'info';
        case 'anomaly': return 'warning';
        case 'blacklist': return 'danger';
        default: return 'info';
    }
};

const getDeliveryStatusSeverity = (status) => {
    switch (status) {
        case 'delivered': return 'success';
        case 'sent': return 'info';
        case 'pending': return 'warning';
        case 'failed': return 'danger';
        default: return 'info';
    }
};

// Lifecycle hooks
onMounted(() => {
    loadNotifications();
});
</script>

<style scoped>
.notification-message {
    max-width: 400px;
}

.notification-message small {
    display: block;
    margin-top: 0.25rem;
}
</style>
