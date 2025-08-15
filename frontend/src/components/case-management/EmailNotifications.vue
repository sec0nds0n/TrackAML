<template>
    <div class="email-notifications">
        <div class="card">
            <div class="flex justify-content-between align-items-center mb-4">
                <h5 class="m-0">Email Notification System</h5>
                <div class="flex gap-2">
                    <Button icon="pi pi-plus" 
                            label="New Template" 
                            @click="showTemplateDialog = true"
                            class="p-button-outlined" />
                    <Button icon="pi pi-send" 
                            label="Send Test Email" 
                            @click="sendTestEmail"
                            class="p-button-warning" />
                </div>
            </div>

            <!-- Email Statistics -->
            <div class="grid mb-4">
                <div class="col-12 md:col-3">
                    <div class="surface-card p-3 border-round text-center">
                        <div class="text-2xl font-bold text-blue-500">{{ emailStats.sent }}</div>
                        <div class="text-500">Emails Sent Today</div>
                    </div>
                </div>
                <div class="col-12 md:col-3">
                    <div class="surface-card p-3 border-round text-center">
                        <div class="text-2xl font-bold text-green-500">{{ emailStats.delivered }}</div>
                        <div class="text-500">Delivered</div>
                    </div>
                </div>
                <div class="col-12 md:col-3">
                    <div class="surface-card p-3 border-round text-center">
                        <div class="text-2xl font-bold text-orange-500">{{ emailStats.pending }}</div>
                        <div class="text-500">Pending</div>
                    </div>
                </div>
                <div class="col-12 md:col-3">
                    <div class="surface-card p-3 border-round text-center">
                        <div class="text-2xl font-bold text-red-500">{{ emailStats.failed }}</div>
                        <div class="text-500">Failed</div>
                    </div>
                </div>
            </div>

            <!-- Email Templates -->
            <div class="grid">
                <div class="col-12 md:col-6">
                    <div class="surface-card p-4 border-round">
                        <h6>Email Templates</h6>
                        <div class="flex flex-column gap-3">
                            <div v-for="template in emailTemplates" 
                                 :key="template.id"
                                 class="template-item p-3 border-round surface-ground">
                                <div class="flex justify-content-between align-items-start">
                                    <div class="flex-1">
                                        <div class="font-medium mb-1">{{ template.name }}</div>
                                        <div class="text-500 text-sm mb-2">{{ template.description }}</div>
                                        <div class="flex gap-2">
                                            <Tag :value="template.type" 
                                                 :severity="getTemplateTypeSeverity(template.type)" />
                                            <Tag :value="template.status" 
                                                 :severity="template.status === 'active' ? 'success' : 'secondary'" />
                                        </div>
                                    </div>
                                    <div class="flex gap-1">
                                        <Button icon="pi pi-eye"
                                                class="p-button-rounded p-button-text p-button-sm"
                                                @click="previewTemplate(template)"
                                                v-tooltip.top="'Preview'" />
                                        <Button icon="pi pi-pencil"
                                                class="p-button-rounded p-button-text p-button-sm"
                                                @click="editTemplate(template)"
                                                v-tooltip.top="'Edit'" />
                                        <Button icon="pi pi-send"
                                                class="p-button-rounded p-button-text p-button-sm"
                                                @click="sendTemplateEmail(template)"
                                                v-tooltip.top="'Send'"
                                                :disabled="template.status !== 'active'" />
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="col-12 md:col-6">
                    <div class="surface-card p-4 border-round">
                        <h6>Recipient Groups</h6>
                        <div class="flex flex-column gap-3">
                            <div v-for="group in recipientGroups" 
                                 :key="group.id"
                                 class="group-item p-3 border-round surface-ground">
                                <div class="flex justify-content-between align-items-center mb-2">
                                    <div class="font-medium">{{ group.name }}</div>
                                    <Tag :value="group.members.length + ' members'" severity="info" />
                                </div>
                                <div class="text-500 text-sm mb-2">{{ group.description }}</div>
                                <div class="flex flex-wrap gap-1">
                                    <Chip v-for="member in group.members.slice(0, 3)" 
                                          :key="member"
                                          :label="member"
                                          class="text-xs" />
                                    <span v-if="group.members.length > 3" 
                                          class="text-500 text-xs">
                                        +{{ group.members.length - 3 }} more
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Recent Email Activity -->
            <div class="mt-4">
                <h6>Recent Email Activity</h6>
                <DataTable :value="recentEmails"
                           :paginator="true"
                           :rows="5"
                           :loading="loading"
                           class="p-datatable-sm">
                    <Column field="timestamp" header="Time" :sortable="true">
                        <template #body="slotProps">
                            {{ formatDateTime(slotProps.data.timestamp) }}
                        </template>
                    </Column>
                    
                    <Column field="template" header="Template">
                        <template #body="slotProps">
                            <div>
                                <div class="font-medium">{{ slotProps.data.template }}</div>
                                <small class="text-500">{{ slotProps.data.subject }}</small>
                            </div>
                        </template>
                    </Column>
                    
                    <Column field="recipients" header="Recipients">
                        <template #body="slotProps">
                            <div class="flex align-items-center gap-2">
                                <Avatar v-for="recipient in slotProps.data.recipients.slice(0, 2)"
                                        :key="recipient"
                                        :label="getInitials(recipient)"
                                        size="small"
                                        shape="circle" />
                                <span v-if="slotProps.data.recipients.length > 2"
                                      class="text-500">
                                    +{{ slotProps.data.recipients.length - 2 }}
                                </span>
                            </div>
                        </template>
                    </Column>
                    
                    <Column field="status" header="Status" :sortable="true">
                        <template #body="slotProps">
                            <Tag :value="slotProps.data.status"
                                 :severity="getEmailStatusSeverity(slotProps.data.status)" />
                        </template>
                    </Column>
                    
                    <Column field="deliveryRate" header="Delivery Rate">
                        <template #body="slotProps">
                            <div class="flex align-items-center gap-2">
                                <ProgressBar :value="slotProps.data.deliveryRate" 
                                           :showValue="false"
                                           style="width: 100px; height: 6px" />
                                <span class="text-sm">{{ slotProps.data.deliveryRate }}%</span>
                            </div>
                        </template>
                    </Column>
                </DataTable>
            </div>
        </div>

        <!-- Template Dialog -->
        <Dialog v-model:visible="showTemplateDialog"
                :header="editingTemplate ? 'Edit Template' : 'New Email Template'"
                :modal="true"
                :style="{ width: '70vw' }"
                :maximizable="true">
            <div class="grid">
                <div class="col-12 md:col-6">
                    <div class="field">
                        <label for="templateName">Template Name *</label>
                        <InputText id="templateName"
                                   v-model="templateForm.name"
                                   class="w-full mt-2"
                                   placeholder="Enter template name" />
                    </div>
                </div>
                
                <div class="col-12 md:col-6">
                    <div class="field">
                        <label for="templateType">Template Type *</label>
                        <Dropdown id="templateType"
                                  v-model="templateForm.type"
                                  :options="templateTypes"
                                  optionLabel="label"
                                  optionValue="value"
                                  placeholder="Select type"
                                  class="w-full mt-2" />
                    </div>
                </div>
                
                <div class="col-12">
                    <div class="field">
                        <label for="templateDescription">Description</label>
                        <InputText id="templateDescription"
                                   v-model="templateForm.description"
                                   class="w-full mt-2"
                                   placeholder="Template description" />
                    </div>
                </div>
                
                <div class="col-12">
                    <div class="field">
                        <label for="emailSubject">Email Subject *</label>
                        <InputText id="emailSubject"
                                   v-model="templateForm.subject"
                                   class="w-full mt-2"
                                   placeholder="Email subject line" />
                    </div>
                </div>
                
                <div class="col-12">
                    <div class="field">
                        <label for="emailBody">Email Body *</label>
                        <Textarea id="emailBody"
                                  v-model="templateForm.body"
                                  rows="10"
                                  class="w-full mt-2"
                                  placeholder="Email content with variables: {{caseId}}, {{documentName}}, {{assignedTo}}, etc." />
                    </div>
                </div>
                
                <div class="col-12 md:col-6">
                    <div class="field">
                        <label for="recipientGroup">Default Recipients</label>
                        <MultiSelect id="recipientGroup"
                                     v-model="templateForm.defaultRecipients"
                                     :options="recipientGroups"
                                     optionLabel="name"
                                     optionValue="id"
                                     placeholder="Select recipient groups"
                                     class="w-full mt-2" />
                    </div>
                </div>
                
                <div class="col-12 md:col-6">
                    <div class="field">
                        <label for="templateStatus">Status</label>
                        <Dropdown id="templateStatus"
                                  v-model="templateForm.status"
                                  :options="[
                                      { label: 'Active', value: 'active' },
                                      { label: 'Draft', value: 'draft' },
                                      { label: 'Inactive', value: 'inactive' }
                                  ]"
                                  optionLabel="label"
                                  optionValue="value"
                                  class="w-full mt-2" />
                    </div>
                </div>
            </div>

            <template #footer>
                <Button label="Cancel"
                        icon="pi pi-times"
                        @click="closeTemplateDialog"
                        class="p-button-text" />
                <Button label="Preview"
                        icon="pi pi-eye"
                        @click="previewCurrentTemplate"
                        class="p-button-outlined" />
                <Button :label="editingTemplate ? 'Update' : 'Create'"
                        icon="pi pi-check"
                        @click="saveTemplate"
                        :disabled="!isTemplateFormValid" />
            </template>
        </Dialog>

        <!-- Preview Dialog -->
        <Dialog v-model:visible="showPreviewDialog"
                header="Email Preview"
                :modal="true"
                :style="{ width: '60vw' }">
            <div v-if="previewContent" class="email-preview">
                <div class="surface-card p-4 border-round mb-3">
                    <div class="grid">
                        <div class="col-3 font-medium">Subject:</div>
                        <div class="col-9">{{ previewContent.subject }}</div>
                        <div class="col-3 font-medium">Type:</div>
                        <div class="col-9">
                            <Tag :value="previewContent.type" 
                                 :severity="getTemplateTypeSeverity(previewContent.type)" />
                        </div>
                    </div>
                </div>
                
                <div class="surface-card p-4 border-round">
                    <h6>Email Content</h6>
                    <div class="email-body" v-html="formatEmailBody(previewContent.body)"></div>
                </div>
            </div>
        </Dialog>
    </div>
</template>

<script setup>
import Avatar from 'primevue/avatar';
import Button from 'primevue/button';
import Chip from 'primevue/chip';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import Dialog from 'primevue/dialog';
import Dropdown from 'primevue/dropdown';
import InputText from 'primevue/inputtext';
import MultiSelect from 'primevue/multiselect';
import ProgressBar from 'primevue/progressbar';
import Tag from 'primevue/tag';
import Textarea from 'primevue/textarea';
import { computed, onMounted, ref } from 'vue';

// Reactive state
const loading = ref(false);
const showTemplateDialog = ref(false);
const showPreviewDialog = ref(false);
const editingTemplate = ref(null);
const previewContent = ref(null);

const emailStats = ref({
    sent: 0,
    delivered: 0,
    pending: 0,
    failed: 0
});

const emailTemplates = ref([]);
const recipientGroups = ref([]);
const recentEmails = ref([]);

const templateForm = ref({
    name: '',
    type: null,
    description: '',
    subject: '',
    body: '',
    defaultRecipients: [],
    status: 'active'
});

// Options
const templateTypes = [
    { label: 'L1 to L2 Transfer', value: 'l1_to_l2_transfer' },
    { label: 'Anomaly Alert', value: 'anomaly_alert' },
    { label: 'Blacklist Notification', value: 'blacklist_notification' },
    { label: 'Case Assignment', value: 'case_assignment' },
    { label: 'Document Approval', value: 'document_approval' },
    { label: 'Compliance Update', value: 'compliance_update' }
];

// Computed
const isTemplateFormValid = computed(() => {
    return templateForm.value.name && 
           templateForm.value.type && 
           templateForm.value.subject && 
           templateForm.value.body;
});

// Methods
const loadEmailData = async () => {
    loading.value = true;
    try {
        // Simulate API calls
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        emailStats.value = {
            sent: 45,
            delivered: 42,
            pending: 2,
            failed: 1
        };

        emailTemplates.value = [
            {
                id: 1,
                name: 'L1 to L2 Document Transfer',
                type: 'l1_to_l2_transfer',
                description: 'Notification when documents are transferred from L1 to L2',
                subject: 'Document Transfer: {{caseId}} - {{documentName}}',
                body: 'Dear {{recipientName}},\n\nA new document has been transferred from L1 to L2 for review.\n\nCase ID: {{caseId}}\nDocument: {{documentName}}\nTransferred by: {{transferredBy}}\nDue Date: {{dueDate}}\n\nPlease review at your earliest convenience.\n\nBest regards,\nCompliance Team',
                status: 'active',
                defaultRecipients: [1, 2]
            },
            {
                id: 2,
                name: 'Anomalous Transaction Alert',
                type: 'anomaly_alert',
                description: 'Alert for suspicious transaction patterns',
                subject: 'URGENT: Anomalous Transaction Detected - {{transactionId}}',
                body: 'URGENT ALERT\n\nAn anomalous transaction pattern has been detected:\n\nTransaction ID: {{transactionId}}\nWallet Address: {{walletAddress}}\nAmount: {{amount}}\nRisk Level: {{riskLevel}}\nDetected at: {{detectionTime}}\n\nImmediate review required.\n\nCompliance System',
                status: 'active',
                defaultRecipients: [1, 3]
            },
            {
                id: 3,
                name: 'New Blacklisted Wallet',
                type: 'blacklist_notification',
                description: 'Notification for newly blacklisted wallets',
                subject: 'New Wallet Blacklisted - {{walletAddress}}',
                body: 'A new wallet has been added to the blacklist:\n\nWallet Address: {{walletAddress}}\nReason: {{blacklistReason}}\nAdded by: {{addedBy}}\nDate: {{blacklistDate}}\n\nAll transactions involving this wallet will be flagged.\n\nSecurity Team',
                status: 'active',
                defaultRecipients: [2, 3]
            }
        ];

        recipientGroups.value = [
            {
                id: 1,
                name: 'L2 Analysts',
                description: 'Level 2 compliance analysts',
                members: ['john.doe@company.com', 'jane.smith@company.com', 'mike.chen@company.com']
            },
            {
                id: 2,
                name: 'Exchange Stakeholders',
                description: 'Exchange management and compliance officers',
                members: ['compliance@exchange.com', 'ceo@exchange.com', 'cto@exchange.com']
            },
            {
                id: 3,
                name: 'Regulatory Contacts',
                description: 'External regulatory bodies',
                members: ['regulator@gov.org', 'compliance.officer@regulator.gov']
            }
        ];

        recentEmails.value = [
            {
                id: 1,
                timestamp: new Date(),
                template: 'L1 to L2 Document Transfer',
                subject: 'Document Transfer: CASE-001 - Transaction Report',
                recipients: ['John Doe', 'Jane Smith'],
                status: 'delivered',
                deliveryRate: 100
            },
            {
                id: 2,
                timestamp: new Date(Date.now() - 3600000),
                template: 'Anomalous Transaction Alert',
                subject: 'URGENT: Anomalous Transaction Detected - TX123456',
                recipients: ['Compliance Team', 'Risk Management', 'Exchange Admin'],
                status: 'delivered',
                deliveryRate: 100
            },
            {
                id: 3,
                timestamp: new Date(Date.now() - 7200000),
                template: 'New Blacklisted Wallet',
                subject: 'New Wallet Blacklisted - 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
                recipients: ['Exchange Stakeholders', 'Regulatory Contacts'],
                status: 'pending',
                deliveryRate: 75
            }
        ];
    } catch (error) {
        console.error('Error loading email data:', error);
    } finally {
        loading.value = false;
    }
};

const previewTemplate = (template) => {
    previewContent.value = {
        ...template,
        subject: replaceVariables(template.subject),
        body: replaceVariables(template.body)
    };
    showPreviewDialog.value = true;
};

const editTemplate = (template) => {
    editingTemplate.value = template;
    templateForm.value = { ...template };
    showTemplateDialog.value = true;
};

const previewCurrentTemplate = () => {
    previewContent.value = {
        ...templateForm.value,
        subject: replaceVariables(templateForm.value.subject),
        body: replaceVariables(templateForm.value.body)
    };
    showPreviewDialog.value = true;
};

const saveTemplate = async () => {
    try {
        if (editingTemplate.value) {
            // Update existing template
            const index = emailTemplates.value.findIndex(t => t.id === editingTemplate.value.id);
            if (index !== -1) {
                emailTemplates.value[index] = { ...templateForm.value, id: editingTemplate.value.id };
            }
        } else {
            // Create new template
            const newTemplate = {
                ...templateForm.value,
                id: Date.now()
            };
            emailTemplates.value.push(newTemplate);
        }
        
        closeTemplateDialog();
        console.log('Template saved successfully');
    } catch (error) {
        console.error('Error saving template:', error);
    }
};

const closeTemplateDialog = () => {
    showTemplateDialog.value = false;
    editingTemplate.value = null;
    templateForm.value = {
        name: '',
        type: null,
        description: '',
        subject: '',
        body: '',
        defaultRecipients: [],
        status: 'active'
    };
};

const sendTemplateEmail = async (template) => {
    try {
        console.log('Sending email with template:', template.name);
        
        // Add to recent emails
        const newEmail = {
            id: Date.now(),
            timestamp: new Date(),
            template: template.name,
            subject: replaceVariables(template.subject),
            recipients: getRecipientsFromGroups(template.defaultRecipients),
            status: 'sent',
            deliveryRate: 0
        };
        
        recentEmails.value.unshift(newEmail);
        emailStats.value.sent++;
        
        // Simulate delivery
        setTimeout(() => {
            newEmail.status = 'delivered';
            newEmail.deliveryRate = 100;
            emailStats.value.delivered++;
        }, 2000);
        
    } catch (error) {
        console.error('Error sending email:', error);
    }
};

const sendTestEmail = async () => {
    try {
        console.log('Sending test email');
        
        const testEmail = {
            id: Date.now(),
            timestamp: new Date(),
            template: 'Test Email',
            subject: 'Test Email - System Check',
            recipients: ['Test User'],
            status: 'sent',
            deliveryRate: 0
        };
        
        recentEmails.value.unshift(testEmail);
        emailStats.value.sent++;
        
        setTimeout(() => {
            testEmail.status = 'delivered';
            testEmail.deliveryRate = 100;
            emailStats.value.delivered++;
        }, 1000);
        
    } catch (error) {
        console.error('Error sending test email:', error);
    }
};

const replaceVariables = (text) => {
    const variables = {
        '{{caseId}}': 'CASE-001',
        '{{documentName}}': 'Transaction Analysis Report',
        '{{recipientName}}': 'John Doe',
        '{{transferredBy}}': 'Jane Smith',
        '{{dueDate}}': new Date(Date.now() + 86400000 * 2).toLocaleDateString(),
        '{{transactionId}}': 'TX123456789',
        '{{walletAddress}}': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
        '{{amount}}': '$50,000',
        '{{riskLevel}}': 'HIGH',
        '{{detectionTime}}': new Date().toLocaleString(),
        '{{blacklistReason}}': 'Suspicious activity pattern',
        '{{addedBy}}': 'Security Team',
        '{{blacklistDate}}': new Date().toLocaleDateString()
    };
    
    let result = text;
    Object.keys(variables).forEach(key => {
        result = result.replace(new RegExp(key, 'g'), variables[key]);
    });
    
    return result;
};

const getRecipientsFromGroups = (groupIds) => {
    const recipients = [];
    groupIds.forEach(groupId => {
        const group = recipientGroups.value.find(g => g.id === groupId);
        if (group) {
            recipients.push(...group.members);
        }
    });
    return [...new Set(recipients)]; // Remove duplicates
};

const formatEmailBody = (body) => {
    return body.replace(/\n/g, '<br>');
};

// Utility functions
const formatDateTime = (date) => {
    return new Date(date).toLocaleString();
};

const getInitials = (name) => {
    return name
        .split(' ')
        .map(n => n[0])
        .join('');
};

const getTemplateTypeSeverity = (type) => {
    switch (type) {
        case 'l1_to_l2_transfer': return 'info';
        case 'anomaly_alert': return 'warning';
        case 'blacklist_notification': return 'danger';
        case 'case_assignment': return 'info';
        case 'document_approval': return 'success';
        case 'compliance_update': return 'secondary';
        default: return 'info';
    }
};

const getEmailStatusSeverity = (status) => {
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
    loadEmailData();
});
</script>

<style scoped>
.template-item,
.group-item {
    transition: all 0.2s ease;
}

.template-item:hover,
.group-item:hover {
    background: var(--surface-hover) !important;
}

.email-preview {
    max-height: 500px;
    overflow-y: auto;
}

.email-body {
    line-height: 1.6;
    white-space: pre-line;
    padding: 1rem;
    background: var(--surface-50);
    border-radius: 6px;
    border-left: 4px solid var(--primary-color);
}
</style>
