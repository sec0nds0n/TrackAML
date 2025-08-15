<template>
    <div class="grid">
        <div class="col-12">
            <div class="card">
                <div class="flex justify-content-between align-items-center mb-4">
                    <h5 class="m-0">System Configuration</h5>
                    <div class="flex gap-2">
                        <Button icon="pi pi-save" 
                                label="Save Changes" 
                                @click="saveConfiguration" 
                                :disabled="!hasChanges" />
                        <Button icon="pi pi-refresh" 
                                label="Reset" 
                                @click="resetConfiguration" 
                                class="p-button-outlined" />
                    </div>
                </div>

                <TabView>
                    <!-- Monitoring Settings -->
                    <TabPanel header="Monitoring">
                        <div class="grid">
                            <div class="col-12 md:col-6">
                                <div class="card">
                                    <h6>Real-time Monitoring</h6>
                                    <div class="field">
                                        <label for="refreshInterval">Refresh Interval (seconds)</label>
                                        <InputNumber id="refreshInterval" 
                                                     v-model="config.monitoring.refreshInterval" 
                                                     :min="1" 
                                                     :max="300" 
                                                     class="w-full mt-2" />
                                    </div>
                                    <div class="field">
                                        <label for="dataRetention">Data Retention (days)</label>
                                        <InputNumber id="dataRetention" 
                                                     v-model="config.monitoring.dataRetention" 
                                                     :min="1" 
                                                     :max="365" 
                                                     class="w-full mt-2" />
                                    </div>
                                    <div class="field">
                                        <div class="flex align-items-center">
                                            <Checkbox id="enableRealTime" 
                                                      v-model="config.monitoring.enableRealTime" />
                                            <label for="enableRealTime" class="ml-2">Enable Real-time Updates</label>
                                        </div>
                                    </div>
                                    <div class="field">
                                        <div class="flex align-items-center">
                                            <Checkbox id="enableNotifications" 
                                                      v-model="config.monitoring.enableNotifications" />
                                            <label for="enableNotifications" class="ml-2">Enable Push Notifications</label>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="col-12 md:col-6">
                                <div class="card">
                                    <h6>Performance Thresholds</h6>
                                    <div class="field">
                                        <label for="cpuThreshold">CPU Usage Alert Threshold (%)</label>
                                        <InputNumber id="cpuThreshold" 
                                                     v-model="config.monitoring.thresholds.cpu" 
                                                     :min="1" 
                                                     :max="100" 
                                                     class="w-full mt-2" />
                                    </div>
                                    <div class="field">
                                        <label for="memoryThreshold">Memory Usage Alert Threshold (%)</label>
                                        <InputNumber id="memoryThreshold" 
                                                     v-model="config.monitoring.thresholds.memory" 
                                                     :min="1" 
                                                     :max="100" 
                                                     class="w-full mt-2" />
                                    </div>
                                    <div class="field">
                                        <label for="diskThreshold">Disk Usage Alert Threshold (%)</label>
                                        <InputNumber id="diskThreshold" 
                                                     v-model="config.monitoring.thresholds.disk" 
                                                     :min="1" 
                                                     :max="100" 
                                                     class="w-full mt-2" />
                                    </div>
                                    <div class="field">
                                        <label for="responseTimeThreshold">Response Time Threshold (ms)</label>
                                        <InputNumber id="responseTimeThreshold" 
                                                     v-model="config.monitoring.thresholds.responseTime" 
                                                     :min="100" 
                                                     :max="10000" 
                                                     class="w-full mt-2" />
                                    </div>
                                </div>
                            </div>
                        </div>
                    </TabPanel>

                    <!-- Alert Settings -->
                    <TabPanel header="Alerts">
                        <div class="grid">
                            <div class="col-12 md:col-6">
                                <div class="card">
                                    <h6>Alert Configuration</h6>
                                    <div class="field">
                                        <div class="flex align-items-center">
                                            <Checkbox id="enableEmailAlerts" 
                                                      v-model="config.alerts.enableEmail" />
                                            <label for="enableEmailAlerts" class="ml-2">Enable Email Alerts</label>
                                        </div>
                                    </div>
                                    <div class="field">
                                        <div class="flex align-items-center">
                                            <Checkbox id="enableSmsAlerts" 
                                                      v-model="config.alerts.enableSms" />
                                            <label for="enableSmsAlerts" class="ml-2">Enable SMS Alerts</label>
                                        </div>
                                    </div>
                                    <div class="field">
                                        <div class="flex align-items-center">
                                            <Checkbox id="enableSlackAlerts" 
                                                      v-model="config.alerts.enableSlack" />
                                            <label for="enableSlackAlerts" class="ml-2">Enable Slack Notifications</label>
                                        </div>
                                    </div>
                                    <div class="field">
                                        <label for="alertCooldown">Alert Cooldown Period (minutes)</label>
                                        <InputNumber id="alertCooldown" 
                                                     v-model="config.alerts.cooldownPeriod" 
                                                     :min="1" 
                                                     :max="1440" 
                                                     class="w-full mt-2" />
                                    </div>
                                </div>
                            </div>

                            <div class="col-12 md:col-6">
                                <div class="card">
                                    <h6>Severity Levels</h6>
                                    <div class="field">
                                        <label for="criticalActions">Critical Alert Actions</label>
                                        <MultiSelect id="criticalActions" 
                                                     v-model="config.alerts.severityActions.critical" 
                                                     :options="alertActions" 
                                                     optionLabel="label" 
                                                     optionValue="value"
                                                     placeholder="Select actions" 
                                                     class="w-full mt-2" />
                                    </div>
                                    <div class="field">
                                        <label for="highActions">High Alert Actions</label>
                                        <MultiSelect id="highActions" 
                                                     v-model="config.alerts.severityActions.high" 
                                                     :options="alertActions" 
                                                     optionLabel="label" 
                                                     optionValue="value"
                                                     placeholder="Select actions" 
                                                     class="w-full mt-2" />
                                    </div>
                                    <div class="field">
                                        <label for="mediumActions">Medium Alert Actions</label>
                                        <MultiSelect id="mediumActions" 
                                                     v-model="config.alerts.severityActions.medium" 
                                                     :options="alertActions" 
                                                     optionLabel="label" 
                                                     optionValue="value"
                                                     placeholder="Select actions" 
                                                     class="w-full mt-2" />
                                    </div>
                                </div>
                            </div>

                            <div class="col-12">
                                <div class="card">
                                    <h6>Notification Recipients</h6>
                                    <DataTable :value="config.alerts.recipients" 
                                               editMode="cell" 
                                               @cell-edit-complete="onCellEditComplete"
                                               responsiveLayout="scroll">
                                        <Column field="name" header="Name" style="width: 25%">
                                            <template #editor="{ data, field }">
                                                <InputText v-model="data[field]" class="w-full" />
                                            </template>
                                        </Column>
                                        <Column field="email" header="Email" style="width: 30%">
                                            <template #editor="{ data, field }">
                                                <InputText v-model="data[field]" class="w-full" />
                                            </template>
                                        </Column>
                                        <Column field="phone" header="Phone" style="width: 20%">
                                            <template #editor="{ data, field }">
                                                <InputText v-model="data[field]" class="w-full" />
                                            </template>
                                        </Column>
                                        <Column field="role" header="Role" style="width: 15%">
                                            <template #editor="{ data, field }">
                                                <Dropdown v-model="data[field]" 
                                                          :options="recipientRoles" 
                                                          optionLabel="label" 
                                                          optionValue="value"
                                                          class="w-full" />
                                            </template>
                                        </Column>
                                        <Column header="Actions" style="width: 10%">
                                            <template #body="slotProps">
                                                <Button icon="pi pi-trash" 
                                                        class="p-button-rounded p-button-text p-button-danger p-button-sm" 
                                                        @click="removeRecipient(slotProps.index)" />
                                            </template>
                                        </Column>
                                    </DataTable>
                                    <div class="mt-3">
                                        <Button icon="pi pi-plus" 
                                                label="Add Recipient" 
                                                @click="addRecipient" 
                                                class="p-button-outlined p-button-sm" />
                                    </div>
                                </div>
                            </div>
                        </div>
                    </TabPanel>

                    <!-- Transaction Monitoring -->
                    <TabPanel header="Transaction Monitoring">
                        <div class="grid">
                            <div class="col-12 md:col-6">
                                <div class="card">
                                    <h6>Transaction Thresholds</h6>
                                    <div class="field">
                                        <label for="largeTransactionThreshold">Large Transaction Threshold ($)</label>
                                        <InputNumber id="largeTransactionThreshold" 
                                                     v-model="config.transactions.thresholds.large" 
                                                     :min="1000" 
                                                     :max="1000000" 
                                                     mode="currency" 
                                                     currency="USD" 
                                                     class="w-full mt-2" />
                                    </div>
                                    <div class="field">
                                        <label for="suspiciousThreshold">Suspicious Activity Threshold ($)</label>
                                        <InputNumber id="suspiciousThreshold" 
                                                     v-model="config.transactions.thresholds.suspicious" 
                                                     :min="100" 
                                                     :max="100000" 
                                                     mode="currency" 
                                                     currency="USD" 
                                                     class="w-full mt-2" />
                                    </div>
                                    <div class="field">
                                        <label for="velocityThreshold">Velocity Threshold (transactions/hour)</label>
                                        <InputNumber id="velocityThreshold" 
                                                     v-model="config.transactions.thresholds.velocity" 
                                                     :min="1" 
                                                     :max="1000" 
                                                     class="w-full mt-2" />
                                    </div>
                                </div>
                            </div>

                            <div class="col-12 md:col-6">
                                <div class="card">
                                    <h6>Risk Scoring</h6>
                                    <div class="field">
                                        <label for="lowRiskScore">Low Risk Score Range</label>
                                        <div class="flex gap-2 mt-2">
                                            <InputNumber v-model="config.transactions.riskScoring.low.min" 
                                                         :min="0" 
                                                         :max="100" 
                                                         placeholder="Min" 
                                                         class="flex-1" />
                                            <InputNumber v-model="config.transactions.riskScoring.low.max" 
                                                         :min="0" 
                                                         :max="100" 
                                                         placeholder="Max" 
                                                         class="flex-1" />
                                        </div>
                                    </div>
                                    <div class="field">
                                        <label for="mediumRiskScore">Medium Risk Score Range</label>
                                        <div class="flex gap-2 mt-2">
                                            <InputNumber v-model="config.transactions.riskScoring.medium.min" 
                                                         :min="0" 
                                                         :max="100" 
                                                         placeholder="Min" 
                                                         class="flex-1" />
                                            <InputNumber v-model="config.transactions.riskScoring.medium.max" 
                                                         :min="0" 
                                                         :max="100" 
                                                         placeholder="Max" 
                                                         class="flex-1" />
                                        </div>
                                    </div>
                                    <div class="field">
                                        <label for="highRiskScore">High Risk Score Range</label>
                                        <div class="flex gap-2 mt-2">
                                            <InputNumber v-model="config.transactions.riskScoring.high.min" 
                                                         :min="0" 
                                                         :max="100" 
                                                         placeholder="Min" 
                                                         class="flex-1" />
                                            <InputNumber v-model="config.transactions.riskScoring.high.max" 
                                                         :min="0" 
                                                         :max="100" 
                                                         placeholder="Max" 
                                                         class="flex-1" />
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="col-12">
                                <div class="card">
                                    <h6>Monitored Networks</h6>
                                    <div class="grid">
                                        <div class="col-12 md:col-4" v-for="network in config.transactions.networks" :key="network.id">
                                            <div class="surface-card p-3 border-round">
                                                <div class="flex justify-content-between align-items-center mb-3">
                                                    <div class="flex align-items-center">
                                                        <Avatar :label="network.symbol" 
                                                                size="small" 
                                                                :style="{ backgroundColor: network.color }" 
                                                                class="mr-2" />
                                                        <span class="font-medium">{{ network.name }}</span>
                                                    </div>
                                                    <InputSwitch v-model="network.enabled" />
                                                </div>
                                                <div class="field">
                                                    <label :for="`${network.id}-threshold`" class="text-sm">Alert Threshold ($)</label>
                                                    <InputNumber :id="`${network.id}-threshold`" 
                                                                 v-model="network.threshold" 
                                                                 :min="100" 
                                                                 :max="1000000" 
                                                                 mode="currency" 
                                                                 currency="USD" 
                                                                 class="w-full mt-1" 
                                                                 size="small" />
                                                </div>
                                                <div class="field">
                                                    <label :for="`${network.id}-gas`" class="text-sm">Gas Price Monitoring</label>
                                                    <div class="flex align-items-center mt-1">
                                                        <Checkbox :id="`${network.id}-gas`" 
                                                                  v-model="network.monitorGas" />
                                                        <label :for="`${network.id}-gas`" class="ml-2 text-sm">Enable</label>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </TabPanel>

                    <!-- API & Integration -->
                    <TabPanel header="API & Integration">
                        <div class="grid">
                            <div class="col-12 md:col-6">
                                <div class="card">
                                    <h6>API Configuration</h6>
                                    <div class="field">
                                        <label for="apiRateLimit">Rate Limit (requests/minute)</label>
                                        <InputNumber id="apiRateLimit" 
                                                     v-model="config.api.rateLimit" 
                                                     :min="10" 
                                                     :max="10000" 
                                                     class="w-full mt-2" />
                                    </div>
                                    <div class="field">
                                        <label for="apiTimeout">Request Timeout (seconds)</label>
                                        <InputNumber id="apiTimeout" 
                                                     v-model="config.api.timeout" 
                                                     :min="5" 
                                                     :max="300" 
                                                     class="w-full mt-2" />
                                    </div>
                                    <div class="field">
                                        <div class="flex align-items-center">
                                            <Checkbox id="enableApiLogging" 
                                                      v-model="config.api.enableLogging" />
                                            <label for="enableApiLogging" class="ml-2">Enable API Logging</label>
                                        </div>
                                    </div>
                                    <div class="field">
                                        <div class="flex align-items-center">
                                            <Checkbox id="enableApiCache" 
                                                      v-model="config.api.enableCache" />
                                            <label for="enableApiCache" class="ml-2">Enable Response Caching</label>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="col-12 md:col-6">
                                <div class="card">
                                    <h6>External Integrations</h6>
                                    <div class="field">
                                        <label for="slackWebhook">Slack Webhook URL</label>
                                        <InputText id="slackWebhook" 
                                                   v-model="config.integrations.slack.webhookUrl" 
                                                   type="password" 
                                                   class="w-full mt-2" 
                                                   placeholder="https://hooks.slack.com/..." />
                                    </div>
                                    <div class="field">
                                        <label for="slackChannel">Default Slack Channel</label>
                                        <InputText id="slackChannel" 
                                                   v-model="config.integrations.slack.defaultChannel" 
                                                   class="w-full mt-2" 
                                                   placeholder="#alerts" />
                                    </div>
                                    <div class="field">
                                        <label for="emailSmtp">SMTP Server</label>
                                        <InputText id="emailSmtp" 
                                                   v-model="config.integrations.email.smtpServer" 
                                                   class="w-full mt-2" 
                                                   placeholder="smtp.example.com" />
                                    </div>
                                    <div class="field">
                                        <label for="emailPort">SMTP Port</label>
                                        <InputNumber id="emailPort" 
                                                     v-model="config.integrations.email.smtpPort" 
                                                     :min="25" 
                                                     :max="65535" 
                                                     class="w-full mt-2" />
                                    </div>
                                </div>
                            </div>

                            <div class="col-12">
                                <div class="card">
                                    <h6>Webhook Endpoints</h6>
                                    <DataTable :value="config.integrations.webhooks" 
                                               editMode="cell" 
                                               @cell-edit-complete="onWebhookCellEdit"
                                               responsiveLayout="scroll">
                                        <Column field="name" header="Name" style="width: 20%">
                                            <template #editor="{ data, field }">
                                                <InputText v-model="data[field]" class="w-full" />
                                            </template>
                                        </Column>
                                        <Column field="url" header="URL" style="width: 40%">
                                            <template #editor="{ data, field }">
                                                <InputText v-model="data[field]" class="w-full" />
                                            </template>
                                        </Column>
                                        <Column field="events" header="Events" style="width: 25%">
                                            <template #body="slotProps">
                                                <Tag v-for="event in slotProps.data.events" 
                                                     :key="event" 
                                                     :value="event" 
                                                     class="mr-1" />
                                            </template>
                                            <template #editor="{ data, field }">
                                                <MultiSelect v-model="data[field]" 
                                                             :options="webhookEvents" 
                                                             optionLabel="label" 
                                                             optionValue="value"
                                                             class="w-full" />
                                            </template>
                                        </Column>
                                        <Column field="enabled" header="Status" style="width: 10%">
                                            <template #body="slotProps">
                                                <Tag :value="slotProps.data.enabled ? 'Active' : 'Inactive'" 
                                                     :severity="slotProps.data.enabled ? 'success' : 'danger'" />
                                            </template>
                                            <template #editor="{ data, field }">
                                                <InputSwitch v-model="data[field]" />
                                            </template>
                                        </Column>
                                        <Column header="Actions" style="width: 5%">
                                            <template #body="slotProps">
                                                <Button icon="pi pi-trash" 
                                                        class="p-button-rounded p-button-text p-button-danger p-button-sm" 
                                                        @click="removeWebhook(slotProps.index)" />
                                            </template>
                                        </Column>
                                    </DataTable>
                                    <div class="mt-3">
                                        <Button icon="pi pi-plus" 
                                                label="Add Webhook" 
                                                @click="addWebhook" 
                                                class="p-button-outlined p-button-sm" />
                                    </div>
                                </div>
                            </div>
                        </div>
                    </TabPanel>

                    <!-- Security Settings -->
                    <TabPanel header="Security">
                        <div class="grid">
                            <div class="col-12 md:col-6">
                                <div class="card">
                                    <h6>Authentication</h6>
                                    <div class="field">
                                        <label for="sessionTimeout">Session Timeout (minutes)</label>
                                        <InputNumber id="sessionTimeout" 
                                                     v-model="config.security.sessionTimeout" 
                                                     :min="5" 
                                                     :max="1440" 
                                                     class="w-full mt-2" />
                                    </div>
                                    <div class="field">
                                        <label for="maxLoginAttempts">Max Login Attempts</label>
                                        <InputNumber id="maxLoginAttempts" 
                                                     v-model="config.security.maxLoginAttempts" 
                                                     :min="3" 
                                                     :max="10" 
                                                     class="w-full mt-2" />
                                    </div>
                                    <div class="field">
                                        <div class="flex align-items-center">
                                            <Checkbox id="requireMfa" 
                                                      v-model="config.security.requireMfa" />
                                            <label for="requireMfa" class="ml-2">Require Multi-Factor Authentication</label>
                                        </div>
                                    </div>
                                    <div class="field">
                                        <div class="flex align-items-center">
                                            <Checkbox id="enableIpWhitelist" 
                                                      v-model="config.security.enableIpWhitelist" />
                                            <label for="enableIpWhitelist" class="ml-2">Enable IP Whitelist</label>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="col-12 md:col-6">
                                <div class="card">
                                    <h6>Data Protection</h6>
                                    <div class="field">
                                        <div class="flex align-items-center">
                                            <Checkbox id="enableEncryption" 
                                                      v-model="config.security.enableEncryption" />
                                            <label for="enableEncryption" class="ml-2">Enable Data Encryption at Rest</label>
                                        </div>
                                    </div>
                                    <div class="field">
                                        <div class="flex align-items-center">
                                            <Checkbox id="enableAuditLog" 
                                                      v-model="config.security.enableAuditLog" />
                                            <label for="enableAuditLog" class="ml-2">Enable Audit Logging</label>
                                        </div>
                                    </div>
                                    <div class="field">
                                        <label for="dataRetentionPeriod">Data Retention Period (days)</label>
                                        <InputNumber id="dataRetentionPeriod" 
                                                     v-model="config.security.dataRetentionPeriod" 
                                                     :min="30" 
                                                     :max="2555" 
                                                     class="w-full mt-2" />
                                    </div>
                                    <div class="field">
                                        <label for="backupFrequency">Backup Frequency</label>
                                        <Dropdown id="backupFrequency" 
                                                  v-model="config.security.backupFrequency" 
                                                  :options="backupFrequencyOptions" 
                                                  optionLabel="label" 
                                                  optionValue="value"
                                                  class="w-full mt-2" />
                                    </div>
                                </div>
                            </div>

                            <div class="col-12" v-if="config.security.enableIpWhitelist">
                                <div class="card">
                                    <h6>IP Whitelist</h6>
                                    <div class="field">
                                        <label for="newIpAddress">Add IP Address</label>
                                        <div class="flex gap-2 mt-2">
                                            <InputText id="newIpAddress" 
                                                       v-model="newIpAddress" 
                                                       placeholder="192.168.1.1 or 192.168.1.0/24" 
                                                       class="flex-1" />
                                            <Button icon="pi pi-plus" 
                                                    label="Add" 
                                                    @click="addIpAddress" 
                                                    :disabled="!newIpAddress" />
                                        </div>
                                    </div>
                                    <div class="mt-3">
                                        <div v-for="(ip, index) in config.security.ipWhitelist" 
                                             :key="index" 
                                             class="flex justify-content-between align-items-center p-2 border-round surface-border border-1 mb-2">
                                            <span class="font-mono">{{ ip }}</span>
                                            <Button icon="pi pi-times" 
                                                    class="p-button-rounded p-button-text p-button-danger p-button-sm" 
                                                    @click="removeIpAddress(index)" />
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </TabPanel>
                </TabView>
            </div>
        </div>
    </div>
</template>

<script setup>
import Avatar from 'primevue/avatar';
import Button from 'primevue/button';
import Checkbox from 'primevue/checkbox';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import Dropdown from 'primevue/dropdown';
import InputNumber from 'primevue/inputnumber';
import InputSwitch from 'primevue/inputswitch';
import InputText from 'primevue/inputtext';
import MultiSelect from 'primevue/multiselect';
import TabPanel from 'primevue/tabpanel';
import TabView from 'primevue/tabview';
import Tag from 'primevue/tag';
import { computed, onMounted, ref, watch } from 'vue';

// Reactive data
const config = ref({});
const originalConfig = ref({});
const newIpAddress = ref('');

// Computed properties
const hasChanges = computed(() => {
    return JSON.stringify(config.value) !== JSON.stringify(originalConfig.value);
});

// Options data
const alertActions = [
    { label: 'Send Email', value: 'email' },
    { label: 'Send SMS', value: 'sms' },
    { label: 'Slack Notification', value: 'slack' },
    { label: 'Create Ticket', value: 'ticket' },
    { label: 'Auto-escalate', value: 'escalate' },
    { label: 'Block Transaction', value: 'block' }
];

const recipientRoles = [
    { label: 'Administrator', value: 'admin' },
    { label: 'Analyst', value: 'analyst' },
    { label: 'Manager', value: 'manager' },
    { label: 'Compliance Officer', value: 'compliance' }
];

const webhookEvents = [
    { label: 'Transaction Alert', value: 'transaction_alert' },
    { label: 'System Alert', value: 'system_alert' },
    { label: 'Compliance Alert', value: 'compliance_alert' },
    { label: 'Risk Score Update', value: 'risk_update' },
    { label: 'User Activity', value: 'user_activity' }
];

const backupFrequencyOptions = [
    { label: 'Hourly', value: 'hourly' },
    { label: 'Daily', value: 'daily' },
    { label: 'Weekly', value: 'weekly' },
    { label: 'Monthly', value: 'monthly' }
];

// Methods
const loadConfiguration = async () => {
    try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 500));
        
        const defaultConfig = {
            monitoring: {
                refreshInterval: 30,
                dataRetention: 90,
                enableRealTime: true,
                enableNotifications: true,
                thresholds: {
                    cpu: 80,
                    memory: 85,
                    disk: 90,
                    responseTime: 5000
                }
            },
            alerts: {
                enableEmail: true,
                enableSms: false,
                enableSlack: true,
                cooldownPeriod: 15,
                severityActions: {
                    critical: ['email', 'sms', 'slack', 'escalate'],
                    high: ['email', 'slack', 'ticket'],
                    medium: ['email', 'ticket']
                },
                recipients: [
                    {
                        name: 'John Smith',
                        email: 'john.smith@company.com',
                        phone: '+1-555-0123',
                        role: 'admin'
                    },
                    {
                        name: 'Sarah Johnson',
                        email: 'sarah.johnson@company.com',
                        phone: '+1-555-0124',
                        role: 'analyst'
                    },
                    {
                        name: 'Mike Chen',
                        email: 'mike.chen@company.com',
                        phone: '+1-555-0125',
                        role: 'compliance'
                    }
                ]
            },
            transactions: {
                thresholds: {
                    large: 50000,
                    suspicious: 10000,
                    velocity: 50
                },
                riskScoring: {
                    low: { min: 0, max: 30 },
                    medium: { min: 31, max: 70 },
                    high: { min: 71, max: 100 }
                },
                networks: [
                    {
                        id: 'ethereum',
                        name: 'Ethereum',
                        symbol: 'ETH',
                        color: '#627EEA',
                        enabled: true,
                        threshold: 25000,
                        monitorGas: true
                    },
                    {
                        id: 'bitcoin',
                        name: 'Bitcoin',
                        symbol: 'BTC',
                        color: '#F7931A',
                        enabled: true,
                        threshold: 50000,
                        monitorGas: false
                    },
                    {
                        id: 'polygon',
                        name: 'Polygon',
                        symbol: 'MATIC',
                        color: '#8247E5',
                        enabled: false,
                        threshold: 10000,
                        monitorGas: true
                    },
                    {
                        id: 'binance',
                        name: 'Binance Smart Chain',
                        symbol: 'BNB',
                        color: '#F3BA2F',
                        enabled: true,
                        threshold: 15000,
                        monitorGas: true
                    }
                ]
            },
            api: {
                rateLimit: 1000,
                timeout: 30,
                enableLogging: true,
                enableCache: true
            },
            integrations: {
                slack: {
                    webhookUrl: '',
                    defaultChannel: '#alerts'
                },
                email: {
                    smtpServer: 'smtp.company.com',
                    smtpPort: 587
                },
                webhooks: [
                    {
                        name: 'Security Webhook',
                        url: 'https://api.security-system.com/webhook',
                        events: ['transaction_alert', 'compliance_alert'],
                        enabled: true
                    },
                    {
                        name: 'Analytics Webhook',
                        url: 'https://analytics.company.com/webhook',
                        events: ['risk_update', 'user_activity'],
                        enabled: false
                    }
                ]
            },
            security: {
                sessionTimeout: 60,
                maxLoginAttempts: 5,
                requireMfa: true,
                enableIpWhitelist: false,
                enableEncryption: true,
                enableAuditLog: true,
                dataRetentionPeriod: 365,
                backupFrequency: 'daily',
                ipWhitelist: [
                    '192.168.1.0/24',
                    '10.0.0.0/8'
                ]
            }
        };
        
        config.value = JSON.parse(JSON.stringify(defaultConfig));
        originalConfig.value = JSON.parse(JSON.stringify(defaultConfig));
    } catch (error) {
        console.error('Error loading configuration:', error);
    }
};

const saveConfiguration = async () => {
    try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        originalConfig.value = JSON.parse(JSON.stringify(config.value));
        
        // In a real app, this would make an API call
        console.log('Configuration saved:', config.value);
        
        // Show success message (you might want to use a toast notification)
        alert('Configuration saved successfully!');
    } catch (error) {
        console.error('Error saving configuration:', error);
        alert('Error saving configuration. Please try again.');
    }
};

const resetConfiguration = () => {
    if (confirm('Are you sure you want to reset all changes?')) {
        config.value = JSON.parse(JSON.stringify(originalConfig.value));
    }
};

// Alert recipients methods
const addRecipient = () => {
    config.value.alerts.recipients.push({
        name: '',
        email: '',
        phone: '',
        role: 'analyst'
    });
};

const removeRecipient = (index) => {
    config.value.alerts.recipients.splice(index, 1);
};

const onCellEditComplete = (event) => {
    const { data, newValue, field } = event;
    data[field] = newValue;
};

// Webhook methods
const addWebhook = () => {
    config.value.integrations.webhooks.push({
        name: '',
        url: '',
        events: [],
        enabled: false
    });
};

const removeWebhook = (index) => {
    config.value.integrations.webhooks.splice(index, 1);
};

const onWebhookCellEdit = (event) => {
    const { data, newValue, field } = event;
    data[field] = newValue;
};

// IP whitelist methods
const addIpAddress = () => {
    if (newIpAddress.value && isValidIpAddress(newIpAddress.value)) {
        config.value.security.ipWhitelist.push(newIpAddress.value);
        newIpAddress.value = '';
    } else {
        alert('Please enter a valid IP address or CIDR notation');
    }
};

const removeIpAddress = (index) => {
    config.value.security.ipWhitelist.splice(index, 1);
};

const isValidIpAddress = (ip) => {
    // Basic IP address validation (IPv4 and CIDR)
    const ipv4Regex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?:\/(?:[0-9]|[1-2][0-9]|3[0-2]))?$/;
    return ipv4Regex.test(ip);
};

// Watch for changes to enable/disable save button
watch(config, () => {
    // This will trigger the hasChanges computed property
}, { deep: true });

// Lifecycle
onMounted(() => {
    loadConfiguration();
});
</script>

<style scoped>
.surface-card {
    background: var(--surface-card);
    border: 1px solid var(--surface-border);
}

.font-mono {
    font-family: 'Courier New', monospace;
}

:deep(.p-tabview-panels) {
    padding: 1rem 0;
}

:deep(.p-tabview-nav-link) {
    padding: 1rem 1.5rem;
}

.card h6 {
    color: var(--text-color);
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--surface-border);
}

.field {
    margin-bottom: 1rem;
}

.field label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: var(--text-color);
}
</style>