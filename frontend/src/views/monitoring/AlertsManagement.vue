<template>
    <div class="grid">
        <div class="col-12">
            <div class="card">
                <div class="flex justify-content-between align-items-center mb-4">
                    <h5 class="m-0">Alerts Management</h5>
                    <div class="flex gap-2">
                        <Button icon="pi pi-plus" 
                                label="Create Alert Rule" 
                                @click="showCreateDialog = true" />
                        <Button icon="pi pi-cog" 
                                label="Alert Settings" 
                                @click="showSettingsDialog = true" 
                                class="p-button-outlined" />
                        <Button icon="pi pi-refresh" 
                                label="Refresh" 





                                @click="loadAlerts" 
                                :loading="loading" 
                                class="p-button-outlined" />
                    </div>
                </div>
                
                <!-- Alert Statistics -->
                <div class="grid mb-4">
                    <div class="col-12 md:col-3">











                        <div class="surface-card p-3 border-round text-center">
                            <div class="text-2xl font-bold text-red-500">{{ alertStats.critical }}</div>
                            <div class="text-500">Critical Alerts</div>
                        </div>
                    </div>

                    <div class="col-12 md:col-3">











                        <div class="surface-card p-3 border-round text-center">
                            <div class="text-2xl font-bold text-orange-500">{{ alertStats.high }}</div>
                            <div class="text-500">High Priority</div>
                        </div>
                    </div>

                    <div class="col-12 md:col-3">











                        <div class="surface-card p-3 border-round text-center">
                            <div class="text-2xl font-bold text-yellow-500">{{ alertStats.medium }}</div>
                            <div class="text-500">Medium Priority</div>
                        </div>
                    </div>

                    <div class="col-12 md:col-3">











                        <div class="surface-card p-3 border-round text-center">
                            <div class="text-2xl font-bold text-blue-500">{{ alertStats.low }}</div>
                            <div class="text-500">Low Priority</div>
                        </div>
                    </div>
                </div>


                <!-- Alert Filters -->
                <div class="flex flex-wrap gap-3 mb-4">








                    <Dropdown v-model="selectedSeverity" 
                              :options="severityOptions" 
                              optionLabel="label" 
                              optionValue="value"
                              placeholder="All Severities" 
                              class="w-12rem" 
                              showClear />
                    <Dropdown v-model="selectedStatus" 
                              :options="statusOptions" 
                              optionLabel="label" 
                              optionValue="value"
                              placeholder="All Statuses" 
                              class="w-12rem" 
                              showClear />
                    <Dropdown v-model="selectedCategory" 
                              :options="categoryOptions" 
                              optionLabel="label" 
                              optionValue="value"
                              placeholder="All Categories" 
                              class="w-12rem" 
                              showClear />
                    <Calendar v-model="dateRange" 
                              selectionMode="range" 
                              :manualInput="false"
                              placeholder="Date Range" 
                              class="w-15rem" />
                    <InputText v-model="searchTerm" 
                               placeholder="Search alerts..." 
                               class="w-15rem" />
                </div>

                <!-- Alerts Table -->
                <DataTable :value="filteredAlerts" 
                           :paginator="true" 

                           :rows="10"
                           :loading="loading"



                           responsiveLayout="scroll"


                           :sortField="'timestamp'" 
                           :sortOrder="-1"
                           selectionMode="multiple"
                           v-model:selection="selectedAlerts"
                           dataKey="id">
                    
                    <template #header>
                        <div class="flex justify-content-between align-items-center">
                            <span class="text-xl font-semibold">Active Alerts ({{ filteredAlerts.length }})</span>
                            <div class="flex gap-2" v-if="selectedAlerts.length > 0">
                                <Button icon="pi pi-check" 
                                        label="Mark Resolved" 
                                        @click="bulkResolveAlerts" 
                                        class="p-button-sm p-button-success" />
                                <Button icon="pi pi-times" 
                                        label="Dismiss" 
                                        @click="bulkDismissAlerts" 
                                        class="p-button-sm p-button-secondary" />
                                <Button icon="pi pi-send" 
                                        label="Escalate" 
                                        @click="bulkEscalateAlerts" 
                                        class="p-button-sm p-button-warning" />
                            </div>
                        </div>
                    </template>
                    
                    <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
                    
                    <Column field="severity" header="Severity" :sortable="true" style="width: 8rem">
                        <template #body="slotProps">
                            <Tag :value="slotProps.data.severity" 


                                 :severity="getSeverityColor(slotProps.data.severity)" />
                        </template>
                    </Column>
                    
                    <Column field="title" header="Alert" :sortable="true">
                        <template #body="slotProps">
                            <div>
                                <div class="font-medium">{{ slotProps.data.title }}</div>
                                <div class="text-500 text-sm">{{ slotProps.data.description }}</div>
                                <div class="flex gap-1 mt-1">
                                    <Tag :value="slotProps.data.category" 
                                         severity="info" 
                                         class="text-xs" />
                                    <Tag v-if="slotProps.data.source" 
                                         :value="slotProps.data.source" 
                                         severity="secondary" 
                                         class="text-xs" />
                                </div>
                            </div>
                        </template>
                    </Column>
                    









                    <Column field="timestamp" header="Time" :sortable="true" style="width: 12rem">
                        <template #body="slotProps">
                            <div>
                                <div>{{ formatDate(slotProps.data.timestamp) }}</div>
                                <div class="text-500 text-sm">{{ formatTime(slotProps.data.timestamp) }}</div>
                            </div>
                        </template>
                    </Column>
                    
                    <Column field="status" header="Status" :sortable="true" style="width: 8rem">
                        <template #body="slotProps">
                            <Tag :value="slotProps.data.status" 
                                 :severity="getStatusColor(slotProps.data.status)" />
                        </template>
                    </Column>
                    

                    <Column field="assignedTo" header="Assigned To" style="width: 10rem">
                        <template #body="slotProps">


                            <div v-if="slotProps.data.assignedTo" class="flex align-items-center">
                                <Avatar :label="slotProps.data.assignedTo.charAt(0)" 
                                        size="small" 
                                        class="mr-2" />

                                {{ slotProps.data.assignedTo }}
                            </div>
                            <span v-else class="text-500">Unassigned</span>
                        </template>
                    </Column>
                    
                    <Column header="Actions" style="width: 12rem">
                        <template #body="slotProps">
                            <div class="flex gap-1">
                                <Button icon="pi pi-eye" 
                                        class="p-button-rounded p-button-text p-button-sm" 
                                        @click="viewAlert(slotProps.data)"
                                        v-tooltip.top="'View Details'" />
                                <Button icon="pi pi-user" 
                                        class="p-button-rounded p-button-text p-button-sm" 
                                        @click="assignAlert(slotProps.data)"






                                        v-tooltip.top="'Assign'"
                                        :disabled="slotProps.data.status === 'resolved'" />
                                <Button icon="pi pi-check" 
                                        class="p-button-rounded p-button-text p-button-sm p-button-success" 
                                        @click="resolveAlert(slotProps.data)"
                                        v-tooltip.top="'Resolve'"
                                        :disabled="slotProps.data.status === 'resolved'" />
                                <Button icon="pi pi-send" 
                                        class="p-button-rounded p-button-text p-button-sm p-button-warning" 
                                        @click="escalateAlert(slotProps.data)"
                                        v-tooltip.top="'Escalate'"
                                        :disabled="slotProps.data.status === 'resolved'" />
                                <Button icon="pi pi-times" 
                                        class="p-button-rounded p-button-text p-button-sm p-button-danger" 
                                        @click="dismissAlert(slotProps.data)"
                                        v-tooltip.top="'Dismiss'" />
                            </div>
                        </template>
                    </Column>
                </DataTable>
            </div>
        </div>

        <!-- Alert Details Dialog -->

        <Dialog v-model:visible="showDetailsDialog" 
                :header="selectedAlert?.title" 
                :modal="true" 


                :style="{ width: '60vw' }"
                :breakpoints="{ '960px': '80vw', '641px': '95vw' }">
            <div v-if="selectedAlert" class="alert-details">









                <!-- Alert Header -->
                <div class="flex justify-content-between align-items-start mb-4">
                    <div>
                        <div class="flex gap-2 mb-2">
                            <Tag :value="selectedAlert.severity" 
                                 :severity="getSeverityColor(selectedAlert.severity)" />
                            <Tag :value="selectedAlert.status" 
                                 :severity="getStatusColor(selectedAlert.status)" />
                            <Tag :value="selectedAlert.category" severity="info" />
                        </div>
                        <p class="text-500 m-0">{{ selectedAlert.description }}</p>
                    </div>







                    <div class="text-right">
                        <div class="text-sm text-500">Created: {{ formatDateTime(selectedAlert.timestamp) }}</div>
                        <div class="text-sm text-500" v-if="selectedAlert.assignedTo">
                            Assigned to: {{ selectedAlert.assignedTo }}
                        </div>
                    </div>
                </div>

                <!-- Alert Details -->
                <div class="grid">
                    <div class="col-12 md:col-6">





                        <div class="surface-card p-3 border-round">
                            <h6>Alert Information</h6>
                            <div class="field">
                                <label>Source</label>
                                <div>{{ selectedAlert.source || 'System' }}</div>
                            </div>
                            <div class="field">
                                <label>Rule ID</label>
                                <div>{{ selectedAlert.ruleId || 'N/A' }}</div>
                            </div>
                            <div class="field">
                                <label>Threshold</label>
                                <div>{{ selectedAlert.threshold || 'N/A' }}</div>
                            </div>
                            <div class="field">
                                <label>Current Value</label>
                                <div>{{ selectedAlert.currentValue || 'N/A' }}</div>
                            </div>
                        </div>
                    </div>
                    <div class="col-12 md:col-6">



                        <div class="surface-card p-3 border-round">
                            <h6>Related Data</h6>
                            <div v-if="selectedAlert.relatedData">
                                <div v-for="(value, key) in selectedAlert.relatedData" 
                                     :key="key" 
                                     class="field">
                                    <label>{{ formatKey(key) }}</label>
                                    <div>{{ value }}</div>
                                </div>
                            </div>
                            <div v-else class="text-500">No additional data available</div>
                        </div>
                    </div>











                </div>

                <!-- Alert History -->
                <div class="mt-4">
                    <h6>Alert History</h6>
                    <Timeline :value="selectedAlert.history || []" class="w-full">
                        <template #content="slotProps">
                            <div class="p-2">
                                <div class="font-medium">{{ slotProps.item.action }}</div>
                                <div class="text-500 text-sm">{{ slotProps.item.user }} - {{ formatDateTime(slotProps.item.timestamp) }}</div>
                                <div v-if="slotProps.item.comment" class="text-sm mt-1">{{ slotProps.item.comment }}</div>
                            </div>
                        </template>
                    </Timeline>
                </div>

                <!-- Comments Section -->
                <div class="mt-4">
                    <h6>Comments</h6>
                    <div v-if="selectedAlert.comments && selectedAlert.comments.length > 0">
                        <div v-for="comment in selectedAlert.comments" 
                             :key="comment.id" 
                             class="surface-card p-3 border-round mb-2">
                            <div class="flex justify-content-between align-items-start">
                                <div>
                                    <div class="font-medium">{{ comment.user }}</div>
                                    <div class="text-sm text-500">{{ formatDateTime(comment.timestamp) }}</div>
                                </div>
                            </div>
                            <div class="mt-2">{{ comment.text }}</div>
                        </div>
                    </div>




















                    <div class="mt-3">
                        <Textarea v-model="newComment" 
                                  rows="3" 
                                  class="w-full" 
                                  placeholder="Add a comment..." />
                        <div class="flex justify-content-end mt-2">
                            <Button label="Add Comment" 
                                    @click="addComment" 
                                    :disabled="!newComment.trim()" 
                                    class="p-button-sm" />
                        </div>
                    </div>
                </div>






















            </div>
            <template #footer>
                <Button label="Close" 
                        icon="pi pi-times" 
                        @click="showDetailsDialog = false" 
                        class="p-button-text" />
                <Button label="Assign to Me" 
                        icon="pi pi-user" 
                        @click="assignToMe(selectedAlert)" 
                        class="p-button-outlined" />
                <Button label="Add Note" 
                        icon="pi pi-comment" 
                        @click="showAddNoteDialog = true" 
                        class="p-button-outlined" />
                <Button label="Escalate" 
                        icon="pi pi-arrow-up" 
                        @click="escalateAlert(selectedAlert)" 
                        class="p-button-warning"
                        :disabled="selectedAlert.severity === 'CRITICAL'" />
                <Button label="Resolve" 
                        icon="pi pi-check" 
                        @click="resolveAlert(selectedAlert)" 
                        class="p-button-success"
                        :disabled="selectedAlert.status === 'resolved'" />
            </template>
        </Dialog>

        <!-- Create Alert Rule Dialog -->
        <Dialog v-model:visible="showCreateDialog" 
                header="Create Alert Rule" 
                :modal="true" 
                :style="{ width: '50vw' }"
                :breakpoints="{ '960px': '75vw', '641px': '90vw' }">
            <div class="grid">
                <div class="col-12">
                    <div class="field">
                        <label for="ruleName">Rule Name *</label>
                        <InputText id="ruleName" 
                                   v-model="newRule.name" 
                                   class="w-full mt-2" 
                                   placeholder="Enter rule name" />
                    </div>
                </div>
                <div class="col-12 md:col-6">
                    <div class="field">
                        <label for="ruleCategory">Category *</label>
                        <Dropdown id="ruleCategory" 
                                  v-model="newRule.category" 
                                  :options="categoryOptions" 
                                  optionLabel="label" 
                                  optionValue="value"
                                  placeholder="Select category" 
                                  class="w-full mt-2" />
                    </div>
                </div>
                <div class="col-12 md:col-6">
                    <div class="field">
                        <label for="ruleSeverity">Severity *</label>
                        <Dropdown id="ruleSeverity" 
                                  v-model="newRule.severity" 
                                  :options="severityOptions" 
                                  optionLabel="label" 
                                  optionValue="value"
                                  placeholder="Select severity" 
                                  class="w-full mt-2" />
                    </div>
                </div>
                <div class="col-12">
                    <div class="field">
                        <label for="ruleDescription">Description</label>
                        <Textarea id="ruleDescription" 
                                  v-model="newRule.description" 
                                  rows="3" 
                                  class="w-full mt-2" 
                                  placeholder="Describe the alert rule..." />
                    </div>
                </div>
                <div class="col-12 md:col-6">
                    <div class="field">
                        <label for="ruleMetric">Metric</label>
                        <Dropdown id="ruleMetric" 
                                  v-model="newRule.metric" 
                                  :options="metricOptions" 
                                  optionLabel="label" 
                                  optionValue="value"
                                  placeholder="Select metric" 
                                  class="w-full mt-2" />
                    </div>
                </div>
                <div class="col-12 md:col-6">
                    <div class="field">
                        <label for="ruleOperator">Operator</label>
                        <Dropdown id="ruleOperator" 
                                  v-model="newRule.operator" 
                                  :options="operatorOptions" 
                                  optionLabel="label" 
                                  optionValue="value"
                                  placeholder="Select operator" 
                                  class="w-full mt-2" />
                    </div>
                </div>
                <div class="col-12 md:col-6">
                    <div class="field">
                        <label for="ruleThreshold">Threshold Value</label>
                        <InputNumber id="ruleThreshold" 
                                     v-model="newRule.threshold" 
                                     class="w-full mt-2" 
                                     placeholder="Enter threshold" />
                    </div>
                </div>
                <div class="col-12 md:col-6">
                    <div class="field">
                        <label for="ruleDuration">Duration (minutes)</label>
                        <InputNumber id="ruleDuration" 
                                     v-model="newRule.duration" 
                                     :min="1" 
                                     :max="1440" 
                                     class="w-full mt-2" 
                                     placeholder="Alert duration" />
                    </div>
                </div>
                <div class="col-12">
                    <div class="field">
                        <label>Notification Methods</label>
                        <div class="flex flex-wrap gap-3 mt-2">
                            <div class="flex align-items-center">
                                <Checkbox id="notifyEmail" 
                                          v-model="newRule.notifications" 
                                          value="email" />
                                <label for="notifyEmail" class="ml-2">Email</label>
                            </div>
                            <div class="flex align-items-center">
                                <Checkbox id="notifySms" 
                                          v-model="newRule.notifications" 
                                          value="sms" />
                                <label for="notifySms" class="ml-2">SMS</label>
                            </div>
                            <div class="flex align-items-center">
                                <Checkbox id="notifySlack" 
                                          v-model="newRule.notifications" 
                                          value="slack" />
                                <label for="notifySlack" class="ml-2">Slack</label>
                            </div>
                            <div class="flex align-items-center">
                                <Checkbox id="notifyWebhook" 
                                          v-model="newRule.notifications" 
                                          value="webhook" />
                                <label for="notifyWebhook" class="ml-2">Webhook</label>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-12">
                    <div class="field">
                        <div class="flex align-items-center">
                            <Checkbox id="ruleEnabled" v-model="newRule.enabled" />
                            <label for="ruleEnabled" class="ml-2">Enable this rule immediately</label>
                        </div>
                    </div>
                </div>
            </div>
            <template #footer>
                <Button label="Cancel" 
                        icon="pi pi-times" 
                        @click="showCreateDialog = false" 
                        class="p-button-text" />
                <Button label="Create Rule" 
                        icon="pi pi-check" 
                        @click="createAlertRule" 
                        :disabled="!isRuleValid" />
            </template>
        </Dialog>

        <!-- Assign Alert Dialog -->
        <Dialog v-model:visible="showAssignDialog" 
                header="Assign Alert" 
                :modal="true" 
                :style="{ width: '30vw' }">
            <div class="field">
                <label for="assignUser">Assign to User</label>
                <Dropdown id="assignUser" 
                          v-model="assignToUser" 
                          :options="userOptions" 
                          optionLabel="label" 
                          optionValue="value"
                          placeholder="Select user" 
                          class="w-full mt-2" />
            </div>
            <div class="field">
                <label for="assignComment">Comment (Optional)</label>
                <Textarea id="assignComment" 
                          v-model="assignComment" 
                          rows="3" 
                          class="w-full mt-2" 
                          placeholder="Add assignment comment..." />
            </div>
            <template #footer>
                <Button label="Cancel" 
                        icon="pi pi-times" 
                        @click="showAssignDialog = false" 
                        class="p-button-text" />
                <Button label="Assign" 
                        icon="pi pi-check" 
                        @click="confirmAssignment" 
                        :disabled="!assignToUser" />
            </template>
        </Dialog>

        <!-- Alert Settings Dialog -->
        <Dialog v-model:visible="showSettingsDialog" 
                header="Alert Settings" 
                :modal="true" 
                :style="{ width: '40vw' }">
            <TabView>
                <TabPanel header="General">
                    <div class="field">
                        <label for="autoResolve">Auto-resolve alerts after (hours)</label>
                        <InputNumber id="autoResolve" 
                                     v-model="alertSettings.autoResolveHours" 
                                     :min="1" 
                                     :max="168" 
                                     class="w-full mt-2" />
                    </div>
                    <div class="field">
                        <label for="maxAlerts">Maximum alerts to display</label>
                        <InputNumber id="maxAlerts" 
                                     v-model="alertSettings.maxDisplayAlerts" 
                                     :min="10" 
                                     :max="1000" 
                                     class="w-full mt-2" />
                    </div>
                    <div class="field">
                        <div class="flex align-items-center">
                            <Checkbox id="enableSound" v-model="alertSettings.enableSoundAlerts" />
                            <label for="enableSound" class="ml-2">Enable sound alerts</label>
                        </div>
                    </div>
                    <div class="field">
                        <div class="flex align-items-center">
                            <Checkbox id="enableDesktop" v-model="alertSettings.enableDesktopNotifications" />
                            <label for="enableDesktop" class="ml-2">Enable desktop notifications</label>
                        </div>
                    </div>
                </TabPanel>
                <TabPanel header="Escalation">
                    <div class="field">
                        <label for="escalationTime">Escalate unresolved alerts after (minutes)</label>
                        <InputNumber id="escalationTime" 
                                     v-model="alertSettings.escalationTimeMinutes" 
                                     :min="5" 
                                     :max="1440" 
                                     class="w-full mt-2" />
                    </div>
                    <div class="field">
                        <label for="escalationLevels">Escalation levels</label>
                        <DataTable :value="alertSettings.escalationLevels" 
                                   class="mt-2">
                            <Column field="level" header="Level"></Column>
                            <Column field="users" header="Users">
                                <template #body="slotProps">
                                    <Tag v-for="user in slotProps.data.users" 
                                         :key="user" 
                                         :value="user" 
                                         class="mr-1" />
                                </template>
                            </Column>
                        </DataTable>
                    </div>
                </TabPanel>
            </TabView>
            <template #footer>
                <Button label="Cancel" 
                        icon="pi pi-times" 
                        @click="showSettingsDialog = false" 
                        class="p-button-text" />
                <Button label="Save Settings" 
                        icon="pi pi-check" 
                        @click="saveAlertSettings" />
            </template>
        </Dialog>
    </div>
</template>

<script setup>
import Avatar from 'primevue/avatar';
import Button from 'primevue/button';
import Calendar from 'primevue/calendar';
import Checkbox from 'primevue/checkbox';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import Dialog from 'primevue/dialog';
import Dropdown from 'primevue/dropdown';
import InputNumber from 'primevue/inputnumber';
import InputText from 'primevue/inputtext';
import TabPanel from 'primevue/tabpanel';
import TabView from 'primevue/tabview';
import Tag from 'primevue/tag';
import Textarea from 'primevue/textarea';
import Timeline from 'primevue/timeline';
import { computed, ref } from 'vue';

// Reactive data
const alerts = ref([]);
const selectedAlerts = ref([]);
const selectedAlert = ref(null);
const loading = ref(false);
const searchTerm = ref('');
const newComment = ref('');

// Dialog states
const showDetailsDialog = ref(false);
const showCreateDialog = ref(false);
const showAssignDialog = ref(false);
const showSettingsDialog = ref(false);

// Filters
const selectedSeverity = ref(null);
const selectedStatus = ref(null);
const selectedCategory = ref(null);
const dateRange = ref(null);

// Assignment
const assignToUser = ref(null);
const assignComment = ref('');

// New rule form
const newRule = ref({
    name: '',
    category: null,
    severity: null,
    description: '',
    metric: null,
    operator: null,
    threshold: null,
    duration: 5,
    notifications: ['email'],
    enabled: true
});

// Alert settings
const alertSettings = ref({
    autoResolveHours: 24,
    maxDisplayAlerts: 100,
    enableSoundAlerts: true,
    enableDesktopNotifications: true,
    escalationTimeMinutes: 30,
    escalationLevels: [
        { level: 1, users: ['Manager', 'Team Lead'] },
        { level: 2, users: ['Director', 'VP'] },
        { level: 3, users: ['CTO', 'CEO'] }
    ]
});

// Alert statistics
const alertStats = ref({
    critical: 0,
    high: 0,
    medium: 0,
    low: 0
});

// Options
const severityOptions = [
    { label: 'Critical', value: 'critical' },
    { label: 'High', value: 'high' },
    { label: 'Medium', value: 'medium' },
    { label: 'Low', value: 'low' }
];

const statusOptions = [
    { label: 'Active', value: 'active' },
    { label: 'Acknowledged', value: 'acknowledged' },
    { label: 'In Progress', value: 'in_progress' },
    { label: 'Resolved', value: 'resolved' },
    { label: 'Dismissed', value: 'dismissed' }
];

const categoryOptions = [
    { label: 'System Performance', value: 'performance' },
    { label: 'Security', value: 'security' },
    { label: 'Transaction', value: 'transaction' },
    { label: 'Compliance', value: 'compliance' },
    { label: 'Network', value: 'network' },
    { label: 'Database', value: 'database' }
];

const metricOptions = [
    { label: 'CPU Usage', value: 'cpu_usage' },
    { label: 'Memory Usage', value: 'memory_usage' },
    { label: 'Disk Usage', value: 'disk_usage' },
    { label: 'Response Time', value: 'response_time' },
    { label: 'Transaction Volume', value: 'transaction_volume' },
    { label: 'Error Rate', value: 'error_rate' },
    { label: 'Network Latency', value: 'network_latency' },
    { label: 'Database Connections', value: 'db_connections' }
];

const operatorOptions = [
    { label: 'Greater Than', value: 'gt' },
    { label: 'Less Than', value: 'lt' },
    { label: 'Equal To', value: 'eq' },
    { label: 'Greater Than or Equal', value: 'gte' },
    { label: 'Less Than or Equal', value: 'lte' },
    { label: 'Not Equal', value: 'ne' }
];

const userOptions = [
    { label: 'John Smith', value: 'john.smith' },
    { label: 'Sarah Johnson', value: 'sarah.johnson' },
    { label: 'Mike Chen', value: 'mike.chen' },
    { label: 'Lisa Rodriguez', value: 'lisa.rodriguez' },
    { label: 'David Wilson', value: 'david.wilson' }
];

// Computed properties
const filteredAlerts = computed(() => {
    let filtered = alerts.value;

    if (selectedSeverity.value) {
        filtered = filtered.filter(alert => alert.severity === selectedSeverity.value);
    }

    if (selectedStatus.value) {
        filtered = filtered.filter(alert => alert.status === selectedStatus.value);
    }

    if (selectedCategory.value) {
        filtered = filtered.filter(alert => alert.category === selectedCategory.value);
    }

    if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase();
        filtered = filtered.filter(alert => 
            alert.title.toLowerCase().includes(term) ||
            alert.description.toLowerCase().includes(term) ||
            alert.source?.toLowerCase().includes(term)
        );
    }

    if (dateRange.value && dateRange.value[0] && dateRange.value[1]) {
        const startDate = dateRange.value[0];
        const endDate = dateRange.value[1];
        filtered = filtered.filter(alert => {
            const alertDate = new Date(alert.timestamp);
            return alertDate >= startDate && alertDate <= endDate;
        });
    }

    return filtered;
});

const isRuleValid = computed(() => {
    return newRule.value.name && 
           newRule.value.category && 
           newRule.value.severity;
});

// Auto-refresh interval
let refreshInterval = null;

// Methods
const loadAlerts = async () => {
    loading.value = true;
    try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        alerts.value = [
            {
                id: 1,
                title: 'High CPU Usage Detected',
                description: 'CPU usage has exceeded 85% for more than 5 minutes on server-01',
                severity: 'critical',
                status: 'active',
                category: 'performance',
                source: 'Server-01',
                timestamp: new Date(),
                assignedTo: null,
                ruleId: 'CPU_HIGH_001',
                threshold: '85%',
                currentValue: '92%',
                relatedData: {
                    server: 'server-01',
                    process: 'application.exe',
                    duration: '7 minutes'
                },
                history: [
                    {
                        action: 'Alert Created',
                        user: 'System',
                        timestamp: new Date(),
                        comment: 'Threshold exceeded'
                    }
                ],
                comments: []
            },
            {
                id: 2,
                title: 'Suspicious Transaction Pattern',
                description: 'Multiple large transactions detected from the same IP address',
                severity: 'high',
                status: 'acknowledged',
                category: 'security',
                source: 'Transaction Monitor',
                timestamp: new Date(Date.now() - 300000),
                assignedTo: 'Sarah Johnson',
                ruleId: 'SEC_TRANS_002',
                threshold: '$50,000',
                currentValue: '$75,000',
                relatedData: {
                    ipAddress: '192.168.1.100',
                    transactionCount: 5,
                    totalAmount: '$375,000'
                },
                history: [
                    {
                        action: 'Alert Created',
                        user: 'System',
                        timestamp: new Date(Date.now() - 300000),
                        comment: 'Pattern detection triggered'
                    },
                    {
                        action: 'Acknowledged',
                        user: 'Sarah Johnson',
                        timestamp: new Date(Date.now() - 240000),
                        comment: 'Investigating transaction pattern'
                    }
                ],
                comments: [
                    {
                        id: 1,
                        user: 'Sarah Johnson',
                        timestamp: new Date(Date.now() - 180000),
                        text: 'Reviewing transaction details and user history'
                    }
                ]
            },
            {
                id: 3,
                title: 'Database Connection Pool Exhausted',
                description: 'All database connections are in use, new requests are being queued',
                severity: 'high',
                status: 'in_progress',
                category: 'database',
                source: 'Database Monitor',
                timestamp: new Date(Date.now() - 600000),
                assignedTo: 'Mike Chen',
                ruleId: 'DB_CONN_003',
                threshold: '95%',
                currentValue: '100%',
                relatedData: {
                    activeConnections: 100,
                    maxConnections: 100,
                    queuedRequests: 15
                },
                history: [
                    {
                        action: 'Alert Created',
                        user: 'System',
                        timestamp: new Date(Date.now() - 600000),
                        comment: 'Connection pool exhausted'
                    },
                    {
                        action: 'Assigned',
                        user: 'Admin',
                        timestamp: new Date(Date.now() - 480000),
                        comment: 'Assigned to database team'
                    }
                ],
                comments: [
                    {
                        id: 1,
                        user: 'Mike Chen',
                        timestamp: new Date(Date.now() - 420000),
                        text: 'Investigating slow queries that might be holding connections'
                    }
                ]
            },
            {
                id: 4,
                title: 'Network Latency Spike',
                description: 'Network response time has increased significantly',
                severity: 'medium',
                status: 'active',
                category: 'network',
                source: 'Network Monitor',
                timestamp: new Date(Date.now() - 900000),
                assignedTo: null,
                ruleId: 'NET_LAT_004',
                threshold: '200ms',
                currentValue: '450ms',
                relatedData: {
                    averageLatency: '450ms',
                    peakLatency: '800ms',
                    affectedServices: 3
                },
                history: [
                    {
                        action: 'Alert Created',
                        user: 'System',
                        timestamp: new Date(Date.now() - 900000),
                        comment: 'Latency threshold exceeded'
                    }
                ],
                comments: []
            },
            {
                id: 5,
                title: 'Compliance Check Failed',
                description: 'Daily compliance validation has failed for AML requirements',
                severity: 'high',
                status: 'resolved',
                category: 'compliance',
                source: 'Compliance Engine',
                timestamp: new Date(Date.now() - 86400000),
                assignedTo: 'Lisa Rodriguez',
                ruleId: 'COMP_AML_005',
                relatedData: {
                    checkType: 'AML Validation',
                    failedRules: 2,
                    affectedTransactions: 15
                },
                history: [
                    {
                        action: 'Alert Created',
                        user: 'System',
                        timestamp: new Date(Date.now() - 86400000),
                        comment: 'Compliance validation failed'
                    },
                    {
                        action: 'Resolved',
                        user: 'Lisa Rodriguez',
                        timestamp: new Date(Date.now() - 82800000),
                        comment: 'Rules updated and validation passed'
                    }
                ],
                comments: [
                    {
                        id: 1,
                        user: 'Lisa Rodriguez',
                        timestamp: new Date(Date.now() - 84600000),
                        text: 'Updated compliance rules to address new requirements'
                    }
                ]
            }
        ];

        // Calculate alert statistics
        updateAlertStats();
    } catch (error) {
        console.error('Error loading alerts:', error);
    } finally {
        loading.value = false;
    }
};

const updateAlertStats = () => {
    const activeAlerts = alerts.value.filter(alert => alert.status !== 'resolved' && alert.status !== 'dismissed');
    
    alertStats.value = {
        critical: activeAlerts.filter(alert => alert.severity === 'critical').length,
        high: activeAlerts.filter(alert => alert.severity === 'high').length,
        medium: activeAlerts.filter(alert => alert.severity === 'medium').length,
        low: activeAlerts.filter(alert => alert.severity === 'low').length
    };
};

const viewAlert = (alert) => {
    selectedAlert.value = alert;
    showDetailsDialog.value = true;
};

const assignAlert = (alert) => {
    selectedAlert.value = alert;
    assignToUser.value = alert.assignedTo || null;
    assignComment.value = '';
    showAssignDialog.value = true;
};

const confirmAssignment = () => {
    if (selectedAlert.value && assignToUser.value) {
        selectedAlert.value.assignedTo = assignToUser.value;
        selectedAlert.value.status = 'acknowledged';
        
        // Add to history
        selectedAlert.value.history.push({
            action: 'Assigned',
            user: 'Current User', // In real app, get from auth context
            timestamp: new Date(),
            comment: assignComment.value || `Assigned to ${assignToUser.value}`
        });
        
        showAssignDialog.value = false;
        updateAlertStats();
        
        console.log('Alert assigned:', selectedAlert.value);
    }
};

const resolveAlert = (alert) => {
    if (confirm('Are you sure you want to resolve this alert?')) {
        alert.status = 'resolved';
        
        // Add to history
        alert.history.push({
            action: 'Resolved',
            user: 'Current User',
            timestamp: new Date(),
            comment: 'Alert resolved by user'
        });
        
        updateAlertStats();
        console.log('Alert resolved:', alert);
    }
};

const escalateAlert = (alert) => {
    if (confirm('Are you sure you want to escalate this alert?')) {
        alert.severity = getNextSeverityLevel(alert.severity);
        
        // Add to history
        alert.history.push({
            action: 'Escalated',
            user: 'Current User',
            timestamp: new Date(),
            comment: `Alert escalated to ${alert.severity} priority`
        });
        
        updateAlertStats();
        console.log('Alert escalated:', alert);
    }
};

const dismissAlert = (alert) => {
    if (confirm('Are you sure you want to dismiss this alert?')) {
        alert.status = 'dismissed';
        
        // Add to history
        alert.history.push({
            action: 'Dismissed',
            user: 'Current User',
            timestamp: new Date(),
            comment: 'Alert dismissed by user'
        });
        
        updateAlertStats();
        console.log('Alert dismissed:', alert);
    }
};

const bulkResolveAlerts = () => {
    if (confirm(`Are you sure you want to resolve ${selectedAlerts.value.length} selected alerts?`)) {
        selectedAlerts.value.forEach(alert => {
            alert.status = 'resolved';
            alert.history.push({
                action: 'Bulk Resolved',
                user: 'Current User',
                timestamp: new Date(),
                comment: 'Resolved via bulk action'
            });
        });
        
        selectedAlerts.value = [];
        updateAlertStats();
    }
};

const bulkDismissAlerts = () => {
    if (confirm(`Are you sure you want to dismiss ${selectedAlerts.value.length} selected alerts?`)) {
        selectedAlerts.value.forEach(alert => {
            alert.status = 'dismissed';
            alert.history.push({
                action: 'Bulk Dismissed',
                user: 'Current User',
                timestamp: new Date(),
                comment: 'Dismissed via bulk action'
            });
        });
        
        selectedAlerts.value = [];
        updateAlertStats();
    }
};

const bulkEscalateAlerts = () => {
    if (confirm(`Are you sure you want to escalate ${selectedAlerts.value.length} selected alerts?`)) {
        selectedAlerts.value.forEach(alert => {
            alert.severity = getNextSeverityLevel(alert.severity);
            alert.history.push({
                action: 'Bulk Escalated',
                user: 'Current User',
                timestamp: new Date(),
                comment: `Escalated to ${alert.severity} priority via bulk action`
            });
        });
        
        selectedAlerts.value = [];
        updateAlertStats();
    }
};

const createAlertRule = () => {
    try {
        const rule = {
            ...newRule.value,
            id: Date.now(),
            createdAt: new Date(),
            createdBy: 'Current User'
        };
        
        console.log('Alert rule created:', rule);
        
        // Reset form
        newRule.value = {
            name: '',
            category: null,
            severity: null,
            description: '',
            metric: null,
            operator: null,
            threshold: null,
            duration: 5,
            notifications: ['email'],
            enabled: true
        };
        
        showCreateDialog.value = false;
        
        // In a real app, this would make an API call
        alert('Alert rule created successfully!');
    } catch (error) {
        console.error('Error creating alert rule:', error);
    }
};

const saveAlertSettings = () => {
    try {
        console.log('Alert settings saved:', alertSettings.value);
        showSettingsDialog.value = false;
        alert('Alert settings saved successfully!');
    } catch (error) {
        console.error('Error saving alert settings:', error);
    }
};

const addComment = () => {
    if (selectedAlert.value && newComment.value.trim()) {
        const comment = {
            id: Date.now(),
            user: 'Current User',
            timestamp: new Date(),
            text: newComment.value.trim()
        };
        
        if (!selectedAlert.value.comments) {
            selectedAlert.value.comments = [];
        }
        
        selectedAlert.value.comments.push(comment);
        newComment.value = '';
        
        console.log('Comment added:', comment);
    }
};