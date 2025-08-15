<template>
    <div class="rule-management-container">
        <!-- Rule Management Header -->
        <div class="rule-header">
            <div class="rule-header-content">
                <div class="rule-title-section">
                    <h2 class="rule-title">Rule Management</h2>
                    <p class="rule-description">Configure and manage detection rules for case {{ caseId }}</p>
                </div>
                <div class="rule-actions">
                    <Button 
                        icon="pi pi-plus" 
                        label="Create Rule" 
                        severity="success"
                        @click="showCreateRuleDialog = true"
                        v-if="authStore.hasPermission('write')" />
                    <Button 
                        icon="pi pi-refresh" 
                        label="Refresh" 
                        severity="secondary"
                        outlined
                        @click="loadRules" />
                </div>
            </div>
        </div>

        <!-- Rule Filters -->
        <div class="rule-filters">
            <div class="filter-group">
                <label for="ruleType">Rule Type</label>
                <Dropdown 
                    id="ruleType"
                    v-model="filters.type" 
                    :options="ruleTypes" 
                    optionLabel="label" 
                    optionValue="value"
                    placeholder="All Types"
                    class="filter-dropdown"
                    @change="applyFilters" />
            </div>
            <div class="filter-group">
                <label for="ruleStatus">Status</label>
                <Dropdown 
                    id="ruleStatus"
                    v-model="filters.status" 
                    :options="statusOptions" 
                    optionLabel="label" 
                    optionValue="value"
                    placeholder="All Statuses"
                    class="filter-dropdown"
                    @change="applyFilters" />
            </div>
            <div class="filter-group">
                <label for="ruleSeverity">Severity</label>
                <Dropdown 
                    id="ruleSeverity"
                    v-model="filters.severity" 
                    :options="severityOptions" 
                    optionLabel="label" 
                    optionValue="value"
                    placeholder="All Severities"
                    class="filter-dropdown"
                    @change="applyFilters" />
            </div>
            <div class="filter-group">
                <label for="ruleSearch">Search</label>
                <InputText 
                    id="ruleSearch"
                    v-model="filters.search" 
                    placeholder="Search rules..."
                    class="filter-input"
                    @input="applyFilters" />
            </div>
        </div>

        <!-- Rules Table -->
        <div class="rules-table-container">
            <DataTable 
                :value="filteredRules" 
                class="rules-datatable"
                :paginator="true"
                :rows="10"
                :rowsPerPageOptions="[5, 10, 20, 50]"
                responsiveLayout="scroll"
                :loading="loading"
                sortMode="multiple"
                removableSort
                :globalFilterFields="['name', 'description', 'type']">
                
                <template #header>
                    <div class="table-header">
                        <h3>Detection Rules ({{ filteredRules.length }})</h3>
                        <div class="table-actions">
                            <Button 
                                icon="pi pi-download" 
                                label="Export" 
                                severity="secondary"
                                outlined
                                size="small"
                                @click="exportRules" />
                        </div>
                    </div>
                </template>

                <Column field="name" header="Rule Name" sortable>
                    <template #body="slotProps">
                        <div class="rule-name-cell">
                            <div class="rule-name">{{ slotProps.data.name }}</div>
                            <div class="rule-id">ID: {{ slotProps.data.id }}</div>
                        </div>
                    </template>
                </Column>

                <Column field="type" header="Type" sortable>
                    <template #body="slotProps">
                        <Tag 
                            :value="slotProps.data.type"
                            :severity="getTypeSeverity(slotProps.data.type)"
                            :icon="getTypeIcon(slotProps.data.type)" />
                    </template>
                </Column>

                <Column field="severity" header="Severity" sortable>
                    <template #body="slotProps">
                        <Tag 
                            :value="slotProps.data.severity"
                            :severity="getSeveritySeverity(slotProps.data.severity)" />
                    </template>
                </Column>

                <Column field="status" header="Status" sortable>
                    <template #body="slotProps">
                        <div class="status-cell">
                            <Tag 
                                :value="slotProps.data.status"
                                :severity="getStatusSeverity(slotProps.data.status)" />
                            <InputSwitch 
                                v-model="slotProps.data.enabled"
                                @change="toggleRule(slotProps.data)"
                                v-if="authStore.hasPermission('write')" />
                        </div>
                    </template>
                </Column>

                <Column field="triggeredCount" header="Triggered" sortable>
                    <template #body="slotProps">
                        <div class="triggered-count">
                            <Badge 
                                :value="slotProps.data.triggeredCount"
                                :severity="slotProps.data.triggeredCount > 0 ? 'warning' : 'secondary'" />
                        </div>
                    </template>
                </Column>

                <Column field="lastTriggered" header="Last Triggered" sortable>
                    <template #body="slotProps">
                        <div class="last-triggered">
                            {{ slotProps.data.lastTriggered ? formatDateTime(slotProps.data.lastTriggered) : 'Never' }}
                        </div>
                    </template>
                </Column>

                <Column field="createdBy" header="Created By" sortable>
                    <template #body="slotProps">
                        <div class="created-by">
                            <Avatar 
                                :label="getInitials(slotProps.data.createdBy)"
                                size="small"
                                shape="circle" />
                            <span>{{ slotProps.data.createdBy }}</span>
                        </div>
                    </template>
                </Column>

                <Column header="Actions" :exportable="false">
                    <template #body="slotProps">
                        <div class="rule-actions-cell">
                            <Button 
                                icon="pi pi-eye" 
                                severity="info"
                                text
                                rounded
                                size="small"
                                @click="viewRule(slotProps.data)"
                                v-tooltip.top="'View Details'" />
                            <Button 
                                icon="pi pi-pencil" 
                                severity="secondary"
                                text
                                rounded
                                size="small"
                                @click="editRule(slotProps.data)"
                                v-tooltip.top="'Edit Rule'"
                                v-if="authStore.hasPermission('write')" />
                            <Button 
                                icon="pi pi-play" 
                                severity="success"
                                text
                                rounded
                                size="small"
                                @click="testRule(slotProps.data)"
                                v-tooltip.top="'Test Rule'"
                                v-if="authStore.hasPermission('write')" />
                            <Button 
                                icon="pi pi-copy" 
                                severity="secondary"
                                text
                                rounded
                                size="small"
                                @click="duplicateRule(slotProps.data)"
                                v-tooltip.top="'Duplicate Rule'"
                                v-if="authStore.hasPermission('write')" />
                            <Button 
                                icon="pi pi-trash" 
                                severity="danger"
                                text
                                rounded
                                size="small"
                                @click="confirmDeleteRule(slotProps.data)"
                                v-tooltip.top="'Delete Rule'"
                                v-if="authStore.hasPermission('delete')" />
                        </div>
                    </template>
                </Column>
            </DataTable>
        </div>

        <!-- Create/Edit Rule Dialog -->
        <Dialog 
            v-model:visible="showCreateRuleDialog" 
            :header="editingRule ? 'Edit Rule' : 'Create New Rule'"
            :modal="true" 
            class="rule-dialog"
            :style="{ width: '90vw', maxWidth: '800px' }">
            
            <div class="dialog-content">
                <TabView class="rule-form-tabs">
                    <!-- Basic Information Tab -->
                    <TabPanel header="Basic Information">
                        <div class="form-section">
                            <div class="form-row">
                                <div class="form-group">
                                    <label for="ruleName" class="field-label">Rule Name *</label>
                                    <InputText 
                                        id="ruleName"
                                        v-model="ruleForm.name" 
                                        class="w-full"
                                        placeholder="Enter rule name..."
                                        :class="{ 'p-invalid': !ruleForm.name }" />
                                </div>
                                <div class="form-group">
                                    <label for="ruleType" class="field-label">Rule Type *</label>
                                    <Dropdown 
                                        id="ruleType"
                                        v-model="ruleForm.type" 
                                        :options="ruleTypes" 
                                        optionLabel="label" 
                                        optionValue="value"
                                        placeholder="Select type..."
                                        class="w-full"
                                        :class="{ 'p-invalid': !ruleForm.type }" />
                                </div>
                            </div>
                            
                            <div class="form-row">
                                <div class="form-group">
                                    <label for="ruleSeverity" class="field-label">Severity *</label>
                                    <Dropdown 
                                        id="ruleSeverity"
                                        v-model="ruleForm.severity" 
                                        :options="severityOptions" 
                                        optionLabel="label" 
                                        optionValue="value"
                                        placeholder="Select severity..."
                                        class="w-full"
                                        :class="{ 'p-invalid': !ruleForm.severity }" />
                                </div>
                                <div class="form-group">
                                    <label for="ruleCategory" class="field-label">Category</label>
                                    <Dropdown 
                                        id="ruleCategory"
                                        v-model="ruleForm.category" 
                                        :options="categoryOptions" 
                                        optionLabel="label" 
                                        optionValue="value"
                                        placeholder="Select category..."
                                        class="w-full" />
                                </div>
                            </div>

                            <div class="form-group">
                                <label for="ruleDescription" class="field-label">Description</label>
                                <Textarea 
                                    id="ruleDescription"
                                    v-model="ruleForm.description" 
                                    rows="3" 
                                    class="w-full"
                                    placeholder="Enter rule description..." />
                            </div>

                            <div class="form-row">
                                <div class="form-group">
                                    <div class="form-checkbox">
                                        <Checkbox 
                                            id="ruleEnabled"
                                            v-model="ruleForm.enabled" 
                                            :binary="true" />
                                        <label for="ruleEnabled">Enable rule immediately</label>
                                    </div>
                                </div>
                                <div class="form-group">
                                    <div class="form-checkbox">
                                        <Checkbox 
                                            id="ruleNotifications"
                                            v-model="ruleForm.notifications" 
                                            :binary="true" />
                                        <label for="ruleNotifications">Send notifications</label>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </TabPanel>

                    <!-- Conditions Tab -->
                    <TabPanel header="Conditions">
                        <div class="form-section">
                            <div class="conditions-header">
                                <h4>Rule Conditions</h4>
                                <Button 
                                    icon="pi pi-plus" 
                                    label="Add Condition" 
                                    size="small"
                                    @click="addCondition" />
                            </div>

                            <div class="conditions-list">
                                <div 
                                    v-for="(condition, index) in ruleForm.conditions" 
                                    :key="index"
                                    class="condition-item">
                                    <div class="condition-header">
                                        <span class="condition-number">{{ index + 1 }}</span>
                                        <Button 
                                            icon="pi pi-trash" 
                                            severity="danger"
                                            text
                                            rounded
                                            size="small"
                                            @click="removeCondition(index)"
                                            v-if="ruleForm.conditions.length > 1" />
                                    </div>
                                    
                                    <div class="condition-form">
                                        <div class="form-row">
                                            <div class="form-group">
                                                <label class="field-label">Field</label>
                                                <Dropdown 
                                                    v-model="condition.field" 
                                                    :options="fieldOptions" 
                                                    optionLabel="label" 
                                                    optionValue="value"
                                                    placeholder="Select field..."
                                                    class="w-full" />
                                            </div>
                                            <div class="form-group">
                                                <label class="field-label">Operator</label>
                                                <Dropdown 
                                                    v-model="condition.operator" 
                                                    :options="operatorOptions" 
                                                    optionLabel="label" 
                                                    optionValue="value"
                                                    placeholder="Select operator..."
                                                    class="w-full" />
                                            </div>
                                            <div class="form-group">
                                                <label class="field-label">Value</label>
                                                <InputText 
                                                    v-model="condition.value" 
                                                    class="w-full"
                                                    placeholder="Enter value..." />
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="logic-operator" v-if="ruleForm.conditions.length > 1">
                                <label class="field-label">Logic Operator</label>
                                <SelectButton 
                                    v-model="ruleForm.logicOperator" 
                                    :options="logicOperators" 
                                    optionLabel="label" 
                                    optionValue="value" />
                            </div>
                        </div>
                    </TabPanel>

                    <!-- Actions Tab -->
                    <TabPanel header="Actions">
                        <div class="form-section">
                            <div class="actions-header">
                                <h4>Rule Actions</h4>
                                <Button 
                                    icon="pi pi-plus" 
                                    label="Add Action" 
                                    size="small"
                                    @click="addAction" />
                            </div>

                            <div class="actions-list">
                                <div 
                                    v-for="(action, index) in ruleForm.actions" 
                                    :key="index"
                                    class="action-item">
                                    <div class="action-header">
                                        <span class="action-number">{{ index + 1 }}</span>
                                        <Button 
                                            icon="pi pi-trash" 
                                            severity="danger"
                                            text
                                            rounded
                                            size="small"
                                            @click="removeAction(index)"
                                            v-if="ruleForm.actions.length > 1" />
                                    </div>
                                    
                                    <div class="action-form">
                                        <div class="form-row">
                                            <div class="form-group">
                                                <label class="field-label">Action Type</label>
                                                <Dropdown 
                                                    v-model="action.type" 
                                                    :options="actionTypes" 
                                                    optionLabel="label" 
                                                    optionValue="value"
                                                    placeholder="Select action..."
                                                    class="w-full" />
                                            </div>
                                            <div class="form-group" v-if="action.type === 'email'">
                                                <label class="field-label">Recipients</label>
                                                <Chips 
                                                    v-model="action.recipients" 
                                                    class="w-full"
                                                    placeholder="Enter email addresses..." />
                                            </div>
                                            <div class="form-group" v-if="action.type === 'webhook'">
                                                <label class="field-label">Webhook URL</label>
                                                <InputText 
                                                    v-model="action.url" 
                                                    class="w-full"
                                                    placeholder="Enter webhook URL..." />
                                            </div>
                                        </div>
                                        
                                        <div class="form-group" v-if="action.type === 'escalate'">
                                            <label class="field-label">Escalation Level</label>
                                            <Dropdown 
                                                v-model="action.escalationLevel" 
                                                :options="escalationLevels" 
                                                optionLabel="label" 
                                                optionValue="value"
                                                placeholder="Select level..."
                                                class="w-full" />
                                        </div>

                                        <div class="form-group">
                                            <label class="field-label">Message Template</label>
                                            <Textarea 
                                                v-model="action.message" 
                                                rows="2" 
                                                class="w-full"
                                                placeholder="Enter message template..." />
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </TabPanel>

                    <!-- Testing Tab -->
                    <TabPanel header="Testing">
                        <div class="form-section">
                            <div class="test-section">
                                <h4>Test Rule Configuration</h4>
                                <p class="test-description">
                                    Test your rule against sample data to ensure it works as expected.
                                </p>
                                
                                <div class="test-data">
                                    <label class="field-label">Test Data (JSON)</label>
                                    <Textarea 
                                        v-model="testData" 
                                        rows="8" 
                                        class="w-full test-textarea"
                                        placeholder="Enter test data in JSON format..." />
                                </div>

                                <div class="test-actions">
                                    <Button 
                                        icon="pi pi-play" 
                                        label="Run Test" 
                                        severity="success"
                                        @click="runRuleTest"
                                        :loading="testRunning" />
                                    <Button 
                                        icon="pi pi-file" 
                                        label="Load Sample" 
                                        severity="secondary"
                                        outlined
                                        @click="loadSampleData" />
                                </div>

                                <div class="test-results" v-if="testResults">
                                    <h5>Test Results</h5>
                                    <div class="result-item" 
                                         :class="{ 'result-success': testResults.passed, 'result-failure': !testResults.passed }">
                                        <div class="result-status">
                                            <i :class="testResults.passed ? 'pi pi-check-circle' : 'pi pi-times-circle'"></i>
                                            <span>{{ testResults.passed ? 'Rule Triggered' : 'Rule Not Triggered' }}</span>
                                        </div>
                                        <div class="result-details" v-if="testResults.details">
                                            <pre>{{ JSON.stringify(testResults.details, null, 2) }}</pre>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </TabPanel>
                </TabView>
            </div>
            
            <template #footer>
                <div class="dialog-footer">
                    <Button 
                        label="Cancel" 
                        icon="pi pi-times" 
                        @click="cancelRuleDialog" 
                        severity="secondary"
                        outlined />
                    <Button 
                        label="Save & Test" 
                        icon="pi pi-check" 
                        @click="saveAndTestRule" 
                        severity="info"
                        outlined />
                    <Button 
                        :label="editingRule ? 'Update Rule' : 'Create Rule'" 
                        icon="pi pi-save" 
                        @click="saveRule" 
                        :disabled="!isRuleFormValid" />
                </div>
            </template>
        </Dialog>

        <!-- Rule Details Dialog -->
        <Dialog 
            v-model:visible="showRuleDetailsDialog" 
            header="Rule Details"
            :modal="true" 
            class="rule-details-dialog"
            :style="{ width: '90vw', maxWidth: '700px' }">
            
            <div class="rule-details-content" v-if="selectedRule">
                <div class="rule-overview">
                    <div class="rule-info">
                        <h3>{{ selectedRule.name }}</h3>
                        <p>{{ selectedRule.description }}</p>
                    </div>
                    <div class="rule-status-info">
                        <Tag 
                            :value="selectedRule.status"
                            :severity="getStatusSeverity(selectedRule.status)" />
                        <Tag 
                            :value="selectedRule.severity"
                            :severity="getSeveritySeverity(selectedRule.severity)" />
                    </div>
                </div>

                <Divider />

                <div class="rule-metrics">
                    <div class="metric-card">
                        <div class="metric-value">{{ selectedRule.triggeredCount }}</div>
                        <div class="metric-label">Times Triggered</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{{ selectedRule.accuracy || 'N/A' }}%</div>
                        <div class="metric-label">Accuracy</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{{ selectedRule.falsePositives || 0 }}</div>
                        <div class="metric-label">False Positives</div>
                    </div>
                </div>

                <Divider />

                <div class="rule-configuration">
                    <h4>Configuration</h4>
                    <div class="config-section">
                        <div class="config-item">
                            <label>Type:</label>
                            <span>{{ selectedRule.type }}</span>
                        </div>
                        <div class="config-item">
                            <label>Category:</label>
                            <span>{{ selectedRule.category || 'N/A' }}</span>
                        </div>
                        <div class="config-item">
                            <label>Created By:</label>
                            <span>{{ selectedRule.createdBy }}</span>
                        </div>
                        <div class="config-item">
                            <label>Created Date:</label>
                            <span>{{ formatDateTime(selectedRule.createdAt) }}</span>
                        </div>
                    </div>
                </div>

                <div class="rule-conditions" v-if="selectedRule.conditions">
                    <h4>Conditions</h4>
                    <div class="conditions-display">
                        <div 
                            v-for="(condition, index) in selectedRule.conditions" 
                            :key="index"
                            class="condition-display">
                            <span class="condition-field">{{ condition.field }}</span>
                            <span class="condition-operator">{{ condition.operator }}</span>
                            <span class="condition-value">{{ condition.value }}</span>
                        </div>
                    </div>
                </div>

                <div class="rule-actions-display" v-if="selectedRule.actions">
                    <h4>Actions</h4>
                    <div class="actions-display">
                        <div 
                            v-for="(action, index) in selectedRule.actions" 
                            :key="index"
                            class="action-display">
                            <Tag :value="action.type" severity="info" />
                            <span class="action-details">{{ getActionDescription(action) }}</span>
                        </div>
                    </div>
                </div>
            </div>
        </Dialog>

        <!-- Delete Confirmation Dialog -->
        <Dialog 
            v-model:visible="showDeleteDialog" 
            header="Confirm Delete"
            :modal="true" 
            class="delete-dialog"
            :style="{ width: '90vw', maxWidth: '400px' }">
            
            <div class="delete-content">
                <div class="delete-icon">
                    <i class="pi pi-exclamation-triangle"></i>
                </div>
                <div class="delete-message">
                    <p>Are you sure you want to delete the rule <strong>"{{ ruleToDelete?.name }}"</strong>?</p>
                    <p class="delete-warning">This action cannot be undone.</p>
                </div>
            </div>
            
            <template #footer>
                <div class="dialog-footer">
                    <Button 
                        label="Cancel" 
                        icon="pi pi-times" 
                        @click="showDeleteDialog = false" 
                        severity="secondary"
                        outlined />
                    <Button 
                        label="Delete" 
                        icon="pi pi-trash" 
                        @click="deleteRule" 
                        severity="danger" />
                </div>
            </template>
        </Dialog>
    </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth';
import { computed, onMounted, ref, watch } from 'vue';

// Props
const props = defineProps({
    caseId: {
        type: String,
        required: true
    }
});

// Stores
const authStore = useAuthStore();

// Reactive data
const loading = ref(false);
const rules = ref([]);
const filteredRules = ref([]);
const showCreateRuleDialog = ref(false);
const showRuleDetailsDialog = ref(false);
const showDeleteDialog = ref(false);
const editingRule = ref(null);
const selectedRule = ref(null);
const ruleToDelete = ref(null);
const testRunning = ref(false);
const testResults = ref(null);
const testData = ref('');

// Filters
const filters = ref({
    type: null,
    status: null,
    severity: null,
    search: ''
});

// Form data
const ruleForm = ref({
    name: '',
    type: '',
    severity: '',
    category: '',
    description: '',
    enabled: true,
    notifications: true,
    conditions: [
        {
            field: '',
            operator: '',
            value: ''
        }
    ],
    actions: [
        {
            type: '',
            message: ''
        }
    ],
    logicOperator: 'AND'
});

// Options
const ruleTypes = ref([
    { label: 'Transaction Amount', value: 'transaction_amount' },
    { label: 'Frequency', value: 'frequency' },
    { label: 'Velocity', value: 'velocity' },
    { label: 'Pattern Matching', value: 'pattern_matching' },
    { label: 'Blacklist', value: 'blacklist' },
    { label: 'Whitelist', value: 'whitelist' },
    { label: 'Geolocation', value: 'geolocation' },
    { label: 'Time-based', value: 'time_based' }
]);

const statusOptions = ref([
    { label: 'Active', value: 'active' },
    { label: 'Inactive', value: 'inactive' },
    { label: 'Draft', value: 'draft' },
    { label: 'Archived', value: 'archived' }
]);

const severityOptions = ref([
    { label: 'Critical', value: 'critical' },
    { label: 'High', value: 'high' },
    { label: 'Medium', value: 'medium' },
    { label: 'Low', value: 'low' },
    { label: 'Info', value: 'info' }
]);

const categoryOptions = ref([
    { label: 'Anti-Money Laundering', value: 'aml' },
    { label: 'Fraud Detection', value: 'fraud' },
    { label: 'Compliance', value: 'compliance' },
    { label: 'Risk Assessment', value: 'risk' },
    { label: 'Behavioral Analysis', value: 'behavioral' },
    { label: 'Transaction Monitoring', value: 'transaction' }
]);

const fieldOptions = ref([
    { label: 'Transaction Amount', value: 'transaction.amount' },
    { label: 'Transaction Count', value: 'transaction.count' },
    { label: 'Sender Address', value: 'transaction.from' },
    { label: 'Receiver Address', value: 'transaction.to' },
    { label: 'Transaction Hash', value: 'transaction.hash' },
    { label: 'Cryptocurrency Type', value: 'transaction.crypto' },
    { label: 'Transaction Time', value: 'transaction.timestamp' },
    { label: 'User ID', value: 'user.id' },
    { label: 'User Country', value: 'user.country' },
    { label: 'User Risk Score', value: 'user.riskScore' }
]);

const operatorOptions = ref([
    { label: 'Equals', value: 'equals' },
    { label: 'Not Equals', value: 'not_equals' },
    { label: 'Greater Than', value: 'greater_than' },
    { label: 'Less Than', value: 'less_than' },
    { label: 'Greater Than or Equal', value: 'greater_than_equal' },
    { label: 'Less Than or Equal', value: 'less_than_equal' },
    { label: 'Contains', value: 'contains' },
    { label: 'Not Contains', value: 'not_contains' },
    { label: 'Starts With', value: 'starts_with' },
    { label: 'Ends With', value: 'ends_with' },
    { label: 'In List', value: 'in_list' },
    { label: 'Not In List', value: 'not_in_list' }
]);

const actionTypes = ref([
    { label: 'Send Email', value: 'email' },
    { label: 'Send Webhook', value: 'webhook' },
    { label: 'Create Alert', value: 'alert' },
    { label: 'Escalate Case', value: 'escalate' },
    { label: 'Block Transaction', value: 'block' },
    { label: 'Flag Account', value: 'flag' },
    { label: 'Log Event', value: 'log' }
]);

const escalationLevels = ref([
    { label: 'L1 Analyst', value: 'L1' },
    { label: 'L2 Analyst', value: 'L2' },
    { label: 'Senior Analyst', value: 'L3' },
    { label: 'Manager', value: 'manager' },
    { label: 'Compliance Officer', value: 'compliance' }
]);

const logicOperators = ref([
    { label: 'AND', value: 'AND' },
    { label: 'OR', value: 'OR' }
]);

// Computed properties
const isRuleFormValid = computed(() => {
    return ruleForm.value.name && 
           ruleForm.value.type && 
           ruleForm.value.severity &&
           ruleForm.value.conditions.every(c => c.field && c.operator && c.value) &&
           ruleForm.value.actions.every(a => a.type);
});

// Methods
const loadRules = async () => {
    loading.value = true;
    try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        rules.value = [
            {
                id: 'RULE-001',
                name: 'High Value Transaction Alert',
                type: 'transaction_amount',
                severity: 'high',
                category: 'aml',
                status: 'active',
                enabled: true,
                description: 'Triggers when transaction amount exceeds $10,000',
                triggeredCount: 45,
                lastTriggered: new Date(Date.now() - 3600000),
                createdBy: 'John Doe',
                createdAt: new Date(Date.now() - 86400000 * 30),
                accuracy: 92,
                falsePositives: 3,
                conditions: [
                    { field: 'transaction.amount', operator: 'greater_than', value: '10000' }
                ],
                actions: [
                    { type: 'alert', message: 'High value transaction detected' },
                    { type: 'email', recipients: ['analyst@company.com'], message: 'Alert: High value transaction' }
                ]
            },
            {
                id: 'RULE-002',
                name: 'Rapid Transaction Frequency',
                type: 'frequency',
                severity: 'medium',
                category: 'fraud',
                status: 'active',
                enabled: true,
                description: 'Detects multiple transactions within short time frame',
                triggeredCount: 23,
                lastTriggered: new Date(Date.now() - 7200000),
                createdBy: 'Jane Smith',
                createdAt: new Date(Date.now() - 86400000 * 15),
                accuracy: 87,
                falsePositives: 5,
                conditions: [
                    { field: 'transaction.count', operator: 'greater_than', value: '5' },
                    { field: 'transaction.timeframe', operator: 'less_than', value: '300' }
                ],
                actions: [
                    { type: 'flag', message: 'Account flagged for rapid transactions' }
                ]
            },
            {
                id: 'RULE-003',
                name: 'Blacklisted Address Check',
                type: 'blacklist',
                severity: 'critical',
                category: 'compliance',
                status: 'active',
                enabled: true,
                description: 'Checks transactions against known blacklisted addresses',
                triggeredCount: 12,
                lastTriggered: new Date(Date.now() - 14400000),
                createdBy: 'Mike Johnson',
                createdAt: new Date(Date.now() - 86400000 * 45),
                accuracy: 98,
                falsePositives: 0,
                conditions: [
                    { field: 'transaction.from', operator: 'in_list', value: 'blacklist_addresses' },
                    { field: 'transaction.to', operator: 'in_list', value: 'blacklist_addresses' }
                ],
                actions: [
                    { type: 'block', message: 'Transaction blocked - blacklisted address' },
                    { type: 'escalate', escalationLevel: 'compliance', message: 'Blacklisted address detected' }
                ]
            },
            {
                id: 'RULE-004',
                name: 'Unusual Geographic Pattern',
                type: 'geolocation',
                severity: 'medium',
                category: 'behavioral',
                status: 'draft',
                enabled: false,
                description: 'Detects transactions from unusual geographic locations',
                triggeredCount: 0,
                lastTriggered: null,
                createdBy: 'Sarah Wilson',
                createdAt: new Date(Date.now() - 86400000 * 7),
                accuracy: null,
                falsePositives: 0,
                conditions: [
                    { field: 'user.country', operator: 'not_in_list', value: 'allowed_countries' }
                ],
                actions: [
                    { type: 'alert', message: 'Unusual geographic activity detected' }
                ]
            }
        ];
        
        applyFilters();
    } catch (error) {
        console.error('Error loading rules:', error);
    } finally {
        loading.value = false;
    }
};

const applyFilters = () => {
    let filtered = [...rules.value];
    
    if (filters.value.type) {
        filtered = filtered.filter(rule => rule.type === filters.value.type);
    }
    
    if (filters.value.status) {
        filtered = filtered.filter(rule => rule.status === filters.value.status);
    }
    
    if (filters.value.severity) {
        filtered = filtered.filter(rule => rule.severity === filters.value.severity);
    }
    
    if (filters.value.search) {
        const searchTerm = filters.value.search.toLowerCase();
        filtered = filtered.filter(rule => 
            rule.name.toLowerCase().includes(searchTerm) ||
            rule.description.toLowerCase().includes(searchTerm) ||
            rule.id.toLowerCase().includes(searchTerm)
        );
    }
    
    filteredRules.value = filtered;
};

const resetRuleForm = () => {
    ruleForm.value = {
        name: '',
        type: '',
        severity: '',
        category: '',
        description: '',
        enabled: true,
        notifications: true,
        conditions: [
            {
                field: '',
                operator: '',
                value: ''
            }
        ],
        actions: [
            {
                type: '',
                message: ''
            }
        ],
        logicOperator: 'AND'
    };
    testResults.value = null;
    testData.value = '';
};

const addCondition = () => {
    ruleForm.value.conditions.push({
        field: '',
        operator: '',
        value: ''
    });
};

const removeCondition = (index) => {
    ruleForm.value.conditions.splice(index, 1);
};

const addAction = () => {
    ruleForm.value.actions.push({
        type: '',
        message: ''
    });
};

const removeAction = (index) => {
    ruleForm.value.actions.splice(index, 1);
};

const saveRule = async () => {
    if (!isRuleFormValid.value) return;
    
    try {
        const ruleData = {
            ...ruleForm.value,
            id: editingRule.value?.id || `RULE-${Date.now()}`,
            createdBy: authStore.currentUser?.email || 'Current User',
            createdAt: editingRule.value?.createdAt || new Date(),
            updatedAt: new Date(),
            triggeredCount: editingRule.value?.triggeredCount || 0,
            lastTriggered: editingRule.value?.lastTriggered || null,
            status: ruleForm.value.enabled ? 'active' : 'inactive'
        };
        
        if (editingRule.value) {
            // Update existing rule
            const index = rules.value.findIndex(r => r.id === editingRule.value.id);
            if (index !== -1) {
                rules.value[index] = ruleData;
            }
        } else {
            // Add new rule
            rules.value.unshift(ruleData);
        }
        
        applyFilters();
        cancelRuleDialog();
        
        // Show success message
        console.log('Rule saved successfully');
    } catch (error) {
        console.error('Error saving rule:', error);
    }
};

const saveAndTestRule = async () => {
    await saveRule();
    if (testData.value) {
        await runRuleTest();
    }
};

const cancelRuleDialog = () => {
    showCreateRuleDialog.value = false;
    editingRule.value = null;
    resetRuleForm();
};

const viewRule = (rule) => {
    selectedRule.value = rule;
    showRuleDetailsDialog.value = true;
};

const editRule = (rule) => {
    editingRule.value = rule;
    ruleForm.value = {
        ...rule,
        conditions: [...rule.conditions],
        actions: [...rule.actions]
    };
    showCreateRuleDialog.value = true;
};

const duplicateRule = (rule) => {
    ruleForm.value = {
        ...rule,
        name: `${rule.name} (Copy)`,
        id: undefined,
        conditions: [...rule.conditions],
        actions: [...rule.actions]
    };
    editingRule.value = null;
    showCreateRuleDialog.value = true;
};

const toggleRule = async (rule) => {
    try {
        rule.status = rule.enabled ? 'active' : 'inactive';
        // Simulate API call
        console.log(`Rule ${rule.id} ${rule.enabled ? 'enabled' : 'disabled'}`);
    } catch (error) {
        console.error('Error toggling rule:', error);
        // Revert the change
        rule.enabled = !rule.enabled;
    }
};

const testRule = (rule) => {
    selectedRule.value = rule;
    ruleForm.value = {
        ...rule,
        conditions: [...rule.conditions],
        actions: [...rule.actions]
    };
    loadSampleData();
    showCreateRuleDialog.value = true;
};

const confirmDeleteRule = (rule) => {
    ruleToDelete.value = rule;
    showDeleteDialog.value = true;
};

const deleteRule = async () => {
    try {
        const index = rules.value.findIndex(r => r.id === ruleToDelete.value.id);
        if (index !== -1) {
            rules.value.splice(index, 1);
            applyFilters();
        }
        showDeleteDialog.value = false;
        ruleToDelete.value = null;
        console.log('Rule deleted successfully');
    } catch (error) {
        console.error('Error deleting rule:', error);
    }
};

const runRuleTest = async () => {
    testRunning.value = true;
    try {
        // Simulate rule testing
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        const testDataObj = JSON.parse(testData.value);
        
        // Simple test logic (in real implementation, this would be more sophisticated)
        const passed = Math.random() > 0.3; // 70% chance of passing
        
        testResults.value = {
            passed,
            details: {
                evaluatedConditions: ruleForm.value.conditions.length,
                matchedConditions: passed ? ruleForm.value.conditions.length : Math.floor(Math.random() * ruleForm.value.conditions.length),
                executionTime: Math.floor(Math.random() * 100) + 50,
                testData: testDataObj
            }
        };
    } catch (error) {
        console.error('Error running test:', error);
        testResults.value = {
            passed: false,
            details: {
                error: 'Invalid test data format'
            }
        };
    } finally {
        testRunning.value = false;
    }
};

const loadSampleData = () => {
    testData.value = JSON.stringify({
        transaction: {
            amount: 15000,
            count: 3,
            from: "0x1234567890abcdef",
            to: "0xfedcba0987654321",
            hash: "0xabcdef1234567890",
            crypto: "BTC",
            timestamp: new Date().toISOString(),
            timeframe: 180
        },
        user: {
            id: "USER-12345",
            country: "US",
            riskScore: 75
        }
    }, null, 2);
};

const exportRules = () => {
    const dataStr = JSON.stringify(filteredRules.value, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `rules_export_${new Date().toISOString().split('T')[0]}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
};

// Utility functions
const formatDateTime = (date) => {
    return new Date(date).toLocaleString();
};

const getInitials = (name) => {
    return name
        ? name
              .split(' ')
              .map(n => n[0])
              .join('')
        : '?';
};

const getTypeSeverity = (type) => {
    switch (type) {
        case 'transaction_amount': return 'warning';
        case 'frequency': return 'info';
        case 'velocity': return 'info';
        case 'pattern_matching': return 'secondary';
        case 'blacklist': return 'danger';
        case 'whitelist': return 'success';
        case 'geolocation': return 'warning';
        case 'time_based': return 'info';
        default: return 'secondary';
    }
};

const getTypeIcon = (type) => {
    switch (type) {
        case 'transaction_amount': return 'pi-dollar';
        case 'frequency': return 'pi-clock';
        case 'velocity': return 'pi-forward';
        case 'pattern_matching': return 'pi-search';
        case 'blacklist': return 'pi-ban';
        case 'whitelist': return 'pi-check-circle';
        case 'geolocation': return 'pi-map-marker';
        case 'time_based': return 'pi-calendar';
        default: return 'pi-cog';
    }
};

const getStatusSeverity = (status) => {
    switch (status) {
        case 'active': return 'success';
        case 'inactive': return 'secondary';
        case 'draft': return 'warning';
        case 'archived': return 'info';
        default: return 'secondary';
    }
};

const getSeveritySeverity = (severity) => {
    switch (severity) {
        case 'critical': return 'danger';
        case 'high': return 'danger';
        case 'medium': return 'warning';
        case 'low': return 'info';
        case 'info': return 'secondary';
        default: return 'secondary';
    }
};

const getActionDescription = (action) => {
    switch (action.type) {
        case 'email':
            return `Send to: ${action.recipients?.join(', ') || 'N/A'}`;
        case 'webhook':
            return `URL: ${action.url || 'N/A'}`;
        case 'escalate':
            return `Level: ${action.escalationLevel || 'N/A'}`;
        case 'alert':
            return 'Create system alert';
        case 'block':
            return 'Block transaction';
        case 'flag':
            return 'Flag account';
        case 'log':
            return 'Log event';
        default:
            return action.message || 'No description';
    }
};

// Watchers
watch(filters, () => {
    applyFilters();
}, { deep: true });

// Lifecycle
onMounted(() => {
    loadRules();
});
</script>

<style scoped>
/* Container */
.rule-management-container {
    padding: 1rem;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    min-height: 100vh;
}

/* Rule Header */
.rule-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 20px;
    padding: 2rem;
    margin-bottom: 2rem;
    color: white;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.rule-header-content {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    flex-wrap: wrap;
    gap: 1rem;
}

.rule-title-section {
    flex: 1;
    min-width: 300px;
}

.rule-title {
    font-size: 2rem;
    font-weight: 700;
    margin: 0;
    background: linear-gradient(45deg, #fff, #e0e7ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.rule-description {
    font-size: 1.1rem;
    margin: 0.5rem 0 0 0;
    opacity: 0.9;
    line-height: 1.5;
}

.rule-actions {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
}

.rule-actions .p-button {
    backdrop-filter: blur(10px);
    border-radius: 25px;
    font-weight: 600;
    transition: all 0.3s ease;
}

.rule-actions .p-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
}

/* Rule Filters */
.rule-filters {
    background: white;
    border-radius: 20px;
    padding: 2rem;
    margin-bottom: 2rem;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
}

.filter-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.filter-group label {
    font-weight: 600;
    color: #4a5568;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.filter-dropdown,
.filter-input {
    border-radius: 10px;
    border: 2px solid #e2e8f0;
    transition: all 0.3s ease;
}

.filter-dropdown:focus,
.filter-input:focus {
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* Rules Table */
.rules-table-container {
    background: white;
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.rules-datatable :deep(.p-datatable-header) {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 0;
}

.table-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem;
    flex-wrap: wrap;
    gap: 1rem;
}

.table-header h3 {
    margin: 0;
    font-size: 1.5rem;
    font-weight: 700;
    color: white;
}

.table-actions {
    display: flex;
    gap: 1rem;
}

.rules-datatable :deep(.p-datatable-thead > tr > th) {
    background: #f8fafc;
    color: #4a5568;
    font-weight: 700;
    padding: 1rem;
    border: none;
    text-transform: uppercase;
    font-size: 0.8rem;
    letter-spacing: 0.5px;
}

.rules-datatable :deep(.p-datatable-tbody > tr > td) {
    padding: 1rem;
    border: none;
    border-bottom: 1px solid #e2e8f0;
    vertical-align: middle;
}

.rules-datatable :deep(.p-datatable-tbody > tr:hover) {
    background: #f8fafc;
}

/* Table Cell Styles */
.rule-name-cell {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.rule-name {
    font-weight: 600;
    color: #2d3748;
    font-size: 1rem;
}

.rule-id {
    font-size: 0.8rem;
    color: #718096;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.status-cell {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.triggered-count {
    display: flex;
    align-items: center;
    justify-content: center;
}

.last-triggered {
    font-size: 0.9rem;
    color: #4a5568;
}

.created-by {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.rule-actions-cell {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
}

/* Dialog Styles */
.rule-dialog :deep(.p-dialog-header),
.rule-details-dialog :deep(.p-dialog-header),
.delete-dialog :deep(.p-dialog-header) {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 15px 15px 0 0;
}

.rule-dialog :deep(.p-dialog-content),
.rule-details-dialog :deep(.p-dialog-content),
.delete-dialog :deep(.p-dialog-content) {
    border-radius: 0 0 15px 15px;
    padding: 0;
}

.dialog-content {
    padding: 2rem;
}

/* Form Styles */
.rule-form-tabs :deep(.p-tabview-nav) {
    background: #f8fafc;
    border: none;
    padding: 0;
}

.rule-form-tabs :deep(.p-tabview-nav li .p-tabview-nav-link) {
    background: transparent;
    border: none;
    color: #4a5568;
    padding: 1rem 1.5rem;
    font-weight: 600;
    transition: all 0.3s ease;
}

.rule-form-tabs :deep(.p-tabview-nav li.p-highlight .p-tabview-nav-link) {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

.rule-form-tabs :deep(.p-tabview-panels) {
    background: white;
    border: none;
    padding: 0;
}

.form-section {
    padding: 2rem;
}

.form-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin-bottom: 1.5rem;
}

.form-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.field-label {
    font-weight: 600;
    color: #4a5568;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.form-checkbox {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.form-checkbox label {
    font-weight: 500;
    color: #2d3748;
    text-transform: none;
    letter-spacing: normal;
}

/* Conditions and Actions */
.conditions-header,
.actions-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
    flex-wrap: wrap;
    gap: 1rem;
}

.conditions-header h4,
.actions-header h4 {
    margin: 0;
    color: #2d3748;
    font-size: 1.3rem;
    font-weight: 700;
}

.conditions-list,
.actions-list {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.condition-item,
.action-item {
    background: #f8fafc;
    border: 2px solid #e2e8f0;
    border-radius: 15px;
    padding: 1.5rem;
    transition: all 0.3s ease;
}

.condition-item:hover,
.action-item:hover {
    border-color: #667eea;
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.1);
}

.condition-header,
.action-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}

.condition-number,
.action-number {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    width: 30px;
    height: 30px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 0.9rem;
}

.logic-operator {
    margin-top: 2rem;
    padding-top: 2rem;
    border-top: 2px solid #e2e8f0;
}

.logic-operator label {
    display: block;
    margin-bottom: 1rem;
}

/* Test Section */
.test-section {
    padding: 2rem;
}

.test-section h4 {
    margin: 0 0 1rem 0;
    color: #2d3748;
    font-size: 1.3rem;
    font-weight: 700;
}

.test-description {
    color: #718096;
    margin-bottom: 2rem;
    line-height: 1.6;
}

.test-data {
    margin-bottom: 2rem;
}

.test-textarea {
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 0.9rem;
    background: #1a202c;
    color: #e2e8f0;
    color: #e2e8f0;
    border: 2px solid #4a5568;
    border-radius: 10px;
}

.test-actions {
    display: flex;
    gap: 1rem;
    margin-bottom: 2rem;
    flex-wrap: wrap;
}

.test-results {
    background: #f8fafc;
    border: 2px solid #e2e8f0;
    border-radius: 15px;
    padding: 1.5rem;
}

.test-results h5 {
    margin: 0 0 1rem 0;
    color: #2d3748;
    font-size: 1.1rem;
    font-weight: 700;
}

.result-item {
    border-radius: 10px;
    padding: 1rem;
    border: 2px solid;
}

.result-success {
    background: #f0fff4;
    border-color: #68d391;
}

.result-failure {
    background: #fff5f5;
    border-color: #fc8181;
}

.result-status {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1rem;
    font-weight: 600;
}

.result-success .result-status {
    color: #38a169;
}

.result-failure .result-status {
    color: #e53e3e;
}

.result-details {
    background: #2d3748;
    color: #e2e8f0;
    padding: 1rem;
    border-radius: 8px;
    overflow-x: auto;
}

.result-details pre {
    margin: 0;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 0.8rem;
    line-height: 1.4;
}

/* Rule Details Dialog */
.rule-details-content {
    padding: 2rem;
}

.rule-overview {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 2rem;
    flex-wrap: wrap;
}

.rule-info h3 {
    margin: 0 0 0.5rem 0;
    color: #2d3748;
    font-size: 1.5rem;
    font-weight: 700;
}

.rule-info p {
    margin: 0;
    color: #718096;
    line-height: 1.6;
}

.rule-status-info {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
}

.rule-metrics {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1.5rem;
    margin: 2rem 0;
}

.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1.5rem;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

.metric-value {
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}

.metric-label {
    font-size: 0.9rem;
    opacity: 0.9;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.rule-configuration h4,
.rule-conditions h4,
.rule-actions-display h4 {
    margin: 0 0 1rem 0;
    color: #2d3748;
    font-size: 1.2rem;
    font-weight: 700;
}

.config-section {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
}

.config-item {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.config-item label {
    font-weight: 600;
    color: #4a5568;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.config-item span {
    color: #2d3748;
    font-weight: 500;
}

.conditions-display,
.actions-display {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.condition-display {
    background: #f8fafc;
    padding: 1rem;
    border-radius: 10px;
    border-left: 4px solid #667eea;
    display: flex;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
}

.condition-field {
    background: #e2e8f0;
    padding: 0.25rem 0.75rem;
    border-radius: 15px;
    font-weight: 600;
    color: #2d3748;
    font-size: 0.9rem;
}

.condition-operator {
    background: #667eea;
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 15px;
    font-weight: 600;
    font-size: 0.9rem;
}

.condition-value {
    background: #38a169;
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 15px;
    font-weight: 600;
    font-size: 0.9rem;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.action-display {
    background: #f8fafc;
    padding: 1rem;
    border-radius: 10px;
    border-left: 4px solid #38a169;
    display: flex;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
}

.action-details {
    color: #4a5568;
    font-weight: 500;
}

/* Delete Dialog */
.delete-content {
    padding: 2rem;
    text-align: center;
}

.delete-icon {
    font-size: 3rem;
    color: #f56565;
    margin-bottom: 1rem;
}

.delete-message p {
    margin: 0 0 1rem 0;
    color: #2d3748;
    line-height: 1.6;
}

.delete-warning {
    color: #e53e3e;
    font-weight: 600;
    font-size: 0.9rem;
}

/* Dialog Footer */
.dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    padding: 1.5rem 2rem;
    background: #f8fafc;
    border-top: 1px solid #e2e8f0;
    flex-wrap: wrap;
}

/* Responsive Design */
@media (max-width: 1200px) {
    .rule-filters {
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    }
    
    .form-row {
        grid-template-columns: 1fr;
    }
    
    .rule-metrics {
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    }
}

@media (max-width: 768px) {
    .rule-management-container {
        padding: 0.5rem;
    }
    
    .rule-header {
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border-radius: 15px;
    }
    
    .rule-header-content {
        flex-direction: column;
        align-items: flex-start;
        gap: 1.5rem;
    }
    
    .rule-title-section {
        min-width: auto;
        width: 100%;
    }
    
    .rule-title {
        font-size: 1.75rem;
    }
    
    .rule-description {
        font-size: 1rem;
    }
    
    .rule-actions {
        width: 100%;
        justify-content: stretch;
    }
    
    .rule-actions .p-button {
        flex: 1;
        justify-content: center;
    }
    
    .rule-filters {
        grid-template-columns: 1fr;
        padding: 1.5rem;
        gap: 1rem;
    }
    
    .table-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 1rem;
    }
    
    .table-actions {
        width: 100%;
        justify-content: stretch;
    }
    
    .table-actions .p-button {
        flex: 1;
        justify-content: center;
    }
    
    .rules-datatable :deep(.p-datatable-wrapper) {
        overflow-x: auto;
    }
    
    .rule-actions-cell {
        flex-direction: column;
        gap: 0.25rem;
    }
    
    .status-cell {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.5rem;
    }
    
    .created-by {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.5rem;
    }
    
    .form-section {
        padding: 1rem;
    }
    
    .conditions-header,
    .actions-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 1rem;
    }
    
    .conditions-header .p-button,
    .actions-header .p-button {
        width: 100%;
    }
    
    .condition-display,
    .action-display {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.5rem;
    }
    
    .test-actions {
        flex-direction: column;
    }
    
    .test-actions .p-button {
        width: 100%;
    }
    
    .rule-overview {
        flex-direction: column;
        gap: 1rem;
    }
    
    .rule-status-info {
        width: 100%;
        justify-content: flex-start;
    }
    
    .rule-metrics {
        grid-template-columns: 1fr;
    }
    
    .config-section {
        grid-template-columns: 1fr;
    }
    
    .dialog-footer {
        flex-direction: column;
        gap: 0.75rem;
    }
    
    .dialog-footer .p-button {
        width: 100%;
    }
}

@media (max-width: 480px) {
    .rule-header {
        padding: 1rem;
    }
    
    .rule-title {
        font-size: 1.5rem;
    }
    
    .rule-filters {
        padding: 1rem;
    }
    
    .rules-datatable :deep(.p-datatable-thead > tr > th),
    .rules-datatable :deep(.p-datatable-tbody > tr > td) {
        padding: 0.75rem 0.5rem;
        font-size: 0.9rem;
    }
    
    .rule-name {
        font-size: 0.9rem;
    }
    
    .rule-id {
        font-size: 0.7rem;
    }
    
    .form-section {
        padding: 0.75rem;
    }
    
    .condition-item,
    .action-item {
        padding: 1rem;
    }
    
    .test-section {
        padding: 1rem;
    }
    
    .rule-details-content {
        padding: 1rem;
    }
    
    .metric-card {
        padding: 1rem;
    }
    
    .metric-value {
        font-size: 1.5rem;
    }
    
    .delete-content {
        padding: 1rem;
    }
    
    .delete-icon {
        font-size: 2rem;
    }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
    .rule-management-container {
        background: linear-gradient(135deg, #1a202c 0%, #2d3748 100%);
    }
    
    .rule-filters,
    .rules-table-container,
    .condition-item,
    .action-item,
    .test-results,
    .rule-details-content {
        background: #2d3748;
        color: #e2e8f0;
        border-color: #4a5568;
    }
    
    .rules-datatable :deep(.p-datatable-thead > tr > th) {
        background: #374151;
        color: #e2e8f0;
    }
    
    .rules-datatable :deep(.p-datatable-tbody > tr:hover) {
        background: #374151;
    }
    
    .filter-dropdown,
    .filter-input {
        background: #374151;
        color: #e2e8f0;
        border-color: #4a5568;
    }
    
    .rule-name,
    .field-label,
    .config-item span,
    .action-details {
        color: #e2e8f0;
    }
    
    .rule-id,
    .last-triggered,
    .rule-info p {
        color: #cbd5e0;
    }
    
    .condition-field {
        background: #4a5568;
        color: #e2e8f0;
    }
    
    .test-textarea {
        background: #1a202c;
        color: #e2e8f0;
        border-color: #4a5568;
    }
}

/* Print styles */
@media print {
    .rule-management-container {
        background: white;
        padding: 0;
    }
    
    .rule-header {
        background: #f8fafc !important;
        color: #2d3748 !important;
        box-shadow: none;
        border: 1px solid #e2e8f0;
    }
    
    .rule-actions,
    .table-actions,
    .rule-actions-cell,
    .conditions-header .p-button,
    .actions-header .p-button,
    .test-actions,
    .dialog-footer {
        display: none !important;
    }
    
    .rule-filters {
        display: none !important;
    }
    
    .rules-datatable :deep(.p-datatable-paginator) {
        display: none !important;
    }
}

/* Animation keyframes */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
    }

@keyframes slideInRight {
    from {
        opacity: 0;
        transform: translateX(30px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

@keyframes pulse {
    0%, 100% {
        opacity: 1;
    }
    50% {
        opacity: 0.5;
    }
}

/* Apply animations */
.rule-header {
    animation: fadeInUp 0.6s ease-out;
}

.rule-filters {
    animation: fadeInUp 0.6s ease-out 0.2s both;
}

.rules-table-container {
    animation: fadeInUp 0.6s ease-out 0.4s both;
}

.condition-item,
.action-item {
    animation: slideInRight 0.4s ease-out;
}

.metric-card {
    animation: fadeInUp 0.4s ease-out;
}

.metric-card:nth-child(1) { animation-delay: 0.1s; }
.metric-card:nth-child(2) { animation-delay: 0.2s; }
.metric-card:nth-child(3) { animation-delay: 0.3s; }

.test-results {
    animation: fadeInUp 0.4s ease-out;
}

/* Loading animation */
.loading-pulse {
    animation: pulse 1.5s ease-in-out infinite;
}

/* Accessibility improvements */
.rule-actions .p-button:focus,
.table-actions .p-button:focus,
.rule-actions-cell .p-button:focus {
    outline: 2px solid #667eea;
    outline-offset: 2px;
}

.condition-item:focus-within,
.action-item:focus-within {
    outline: 2px solid #667eea;
    outline-offset: 2px;
}

/* High contrast mode */
@media (prefers-contrast: high) {
    .rule-header {
        background: #000;
        color: #fff;
        border: 2px solid #fff;
    }
    
    .rule-filters,
    .rules-table-container {
        border: 2px solid #000;
    }
    
    .condition-item,
    .action-item {
        border: 2px solid #000;
    }
    
    .metric-card {
        background: #000 !important;
        color: #fff;
        border: 2px solid #fff;
    }
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
    
    .condition-item:hover,
    .action-item:hover,
    .rule-actions .p-button:hover {
        transform: none;
    }
}

/* Custom scrollbar */
.test-textarea::-webkit-scrollbar,
.result-details::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

.test-textarea::-webkit-scrollbar-track,
.result-details::-webkit-scrollbar-track {
    background: #4a5568;
    border-radius: 4px;
}

.test-textarea::-webkit-scrollbar-thumb,
.result-details::-webkit-scrollbar-thumb {
    background: #667eea;
    border-radius: 4px;
}

.test-textarea::-webkit-scrollbar-thumb:hover,
.result-details::-webkit-scrollbar-thumb:hover {
    background: #5a67d8;
}

/* Tooltip styles */
.p-tooltip {
    background: #2d3748;
    color: #e2e8f0;
    border-radius: 8px;
    padding: 0.5rem 0.75rem;
    font-size: 0.8rem;
    font-weight: 500;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.p-tooltip .p-tooltip-arrow {
    border-top-color: #2d3748;
}

/* Focus styles for better accessibility */
.p-dropdown:focus,
.p-inputtext:focus,
.p-textarea:focus,
.p-checkbox:focus,
.p-inputswitch:focus {
    outline: 2px solid #667eea;
    outline-offset: 2px;
}

/* Custom checkbox and switch styles */
.p-checkbox .p-checkbox-box {
    border-radius: 6px;
    border: 2px solid #e2e8f0;
    transition: all 0.3s ease;
}

.p-checkbox .p-checkbox-box.p-highlight {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-color: #667eea;
}

.p-inputswitch .p-inputswitch-slider {
    background: #e2e8f0;
    border-radius: 20px;
    transition: all 0.3s ease;
}

.p-inputswitch.p-inputswitch-checked .p-inputswitch-slider {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* Custom dropdown styles */
.p-dropdown {
    border-radius: 10px;
    border: 2px solid #e2e8f0;
    transition: all 0.3s ease;
}

.p-dropdown:hover {
    border-color: #cbd5e0;
}

.p-dropdown.p-focus {
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.p-dropdown-panel {
    border-radius: 10px;
    border: 2px solid #667eea;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.p-dropdown-item {
    padding: 0.75rem 1rem;
    transition: all 0.2s ease;
}

.p-dropdown-item:hover {
    background: #f8fafc;
}

.p-dropdown-item.p-highlight {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

/* Custom input styles */
.p-inputtext,
.p-textarea {
    border-radius: 10px;
    border: 2px solid #e2e8f0;
    padding: 0.75rem 1rem;
    transition: all 0.3s ease;
}

.p-inputtext:hover,
.p-textarea:hover {
    border-color: #cbd5e0;
}

.p-inputtext:focus,
.p-textarea:focus {
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* Custom button styles */
.p-button {
    border-radius: 10px;
    font-weight: 600;
    padding: 0.75rem 1.5rem;
    transition: all 0.3s ease;
}

.p-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.p-button.p-button-sm {
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
}

.p-button.p-button-outlined {
    background: transparent;
    border: 2px solid;
}

.p-button.p-button-text {
    background: transparent;
    border: none;
}

.p-button.p-button-rounded {
    border-radius: 25px;
}

/* Custom tag styles */
.p-tag {
    border-radius: 15px;
    font-weight: 600;
    padding: 0.4rem 0.8rem;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Custom badge styles */
.p-badge {
    border-radius: 10px;
    font-weight: 700;
    min-width: 1.5rem;
    height: 1.5rem;
    line-height: 1.5rem;
    text-align: center;
}

/* Custom avatar styles */
.p-avatar {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    font-weight: 600;
}

/* Custom divider styles */
.p-divider {
    margin: 2rem 0;
}

.p-divider .p-divider-content {
    background: white;
    padding: 0 1rem;
    color: #4a5568;
    font-weight: 600;
}

/* Custom selectbutton styles */
.p-selectbutton .p-button {
    border-radius: 0;
    border-right: none;
}

.p-selectbutton .p-button:first-child {
    border-radius: 10px 0 0 10px;
}

.p-selectbutton .p-button:last-child {
    border-radius: 0 10px 10px 0;
    border-right: 2px solid #e2e8f0;
}

.p-selectbutton .p-button.p-highlight {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-color: #667eea;
    color: white;
}

/* Custom chips styles */
.p-chips .p-chips-multiple-container {
    border-radius: 10px;
    border: 2px solid #e2e8f0;
    padding: 0.5rem;
    min-height: 3rem;
}

.p-chips .p-chips-token {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 15px;
    padding: 0.25rem 0.75rem;
    margin: 0.25rem;
    font-weight: 600;
}

.p-chips .p-chips-input-token input {
    border: none;
    outline: none;
    background: transparent;
    padding: 0.5rem;
    font-size: 1rem;
}

/* Custom fileupload styles */
.p-fileupload .p-fileupload-choose {
    border-radius: 10px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    color: white;
    font-weight: 600;
    padding: 0.75rem 1.5rem;
    transition: all 0.3s ease;
}

.p-fileupload .p-fileupload-choose:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

/* Loading states */
.p-button.p-button-loading {
    pointer-events: none;
}

.p-button.p-button-loading .p-button-icon {
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* Error states */
.p-invalid {
    border-color: #e53e3e !important;
}

.p-invalid:focus {
    box-shadow: 0 0 0 3px rgba(229, 62, 62, 0.1) !important;
}

.p-error {
    color: #e53e3e;
    font-size: 0.8rem;
    margin-top: 0.25rem;
    font-weight: 500;
}

/* Success states */
.p-valid {
    border-color: #38a169 !important;
}

.p-valid:focus {
    box-shadow: 0 0 0 3px rgba(56, 161, 105, 0.1) !important;
}

.p-success {
    color: #38a169;
    font-size: 0.8rem;
    margin-top: 0.25rem;
    font-weight: 500;
}
</style>
