<template>
    <div class="document-flow">
        <div class="card">
            <div class="flex justify-content-between align-items-center mb-4">
                <h5 class="m-0">Document Flow Management</h5>
                <Button icon="pi pi-upload" 
                        label="Upload Document" 
                        @click="showUploadDialog = true" />
            </div>

            <!-- Flow Status Overview -->
            <div class="grid mb-4">
                <div class="col-12 md:col-3">
                    <div class="surface-card p-3 border-round text-center">
                        <div class="text-2xl font-bold text-blue-500">{{ flowStats.l1Pending }}</div>
                        <div class="text-500">L1 Pending</div>
                    </div>
                </div>
                <div class="col-12 md:col-3">
                    <div class="surface-card p-3 border-round text-center">
                        <div class="text-2xl font-bold text-orange-500">{{ flowStats.l2Review }}</div>
                        <div class="text-500">L2 Review</div>
                    </div>
                </div>
                <div class="col-12 md:col-3">
                    <div class="surface-card p-3 border-round text-center">
                        <div class="text-2xl font-bold text-green-500">{{ flowStats.approved }}</div>
                        <div class="text-500">Approved</div>
                    </div>
                </div>
                <div class="col-12 md:col-3">
                    <div class="surface-card p-3 border-round text-center">
                        <div class="text-2xl font-bold text-red-500">{{ flowStats.rejected }}</div>
                        <div class="text-500">Rejected</div>
                    </div>
                </div>
            </div>

            <!-- Document Flow Visualization -->
            <div class="document-flow-chart mb-4">
                <div class="flow-container">
                    <div class="flow-step" :class="{ active: currentStep >= 1 }">
                        <div class="step-icon">
                            <i class="pi pi-file-plus"></i>
                        </div>
                        <div class="step-label">Document Upload</div>
                        <div class="step-description">L1 uploads documents</div>
                    </div>

                    <div class="flow-arrow">
                        <i class="pi pi-arrow-right"></i>
                    </div>

                    <div class="flow-step" :class="{ active: currentStep >= 2 }">
                        <div class="step-icon">
                            <i class="pi pi-eye"></i>
                        </div>
                        <div class="step-label">L1 Review</div>
                        <div class="step-description">Initial validation</div>
                    </div>

                    <div class="flow-arrow">
                        <i class="pi pi-arrow-right"></i>
                    </div>

                    <div class="flow-step" :class="{ active: currentStep >= 3 }">
                        <div class="step-icon">
                            <i class="pi pi-send"></i>
                        </div>
                        <div class="step-label">Transfer to L2</div>
                        <div class="step-description">Escalation notification</div>
                    </div>

                    <div class="flow-arrow">
                        <i class="pi pi-arrow-right"></i>
                    </div>

                    <div class="flow-step" :class="{ active: currentStep >= 4 }">
                        <div class="step-icon">
                            <i class="pi pi-search"></i>
                        </div>
                        <div class="step-label">L2 Review</div>
                        <div class="step-description">Detailed analysis</div>
                    </div>

                    <div class="flow-arrow">
                        <i class="pi pi-arrow-right"></i>
                    </div>

                    <div class="flow-step" :class="{ active: currentStep >= 5 }">
                        <div class="step-icon">
                            <i class="pi pi-check"></i>
                        </div>
                        <div class="step-label">Final Decision</div>
                        <div class="step-description">Approve/Reject</div>
                    </div>
                </div>
            </div>

            <!-- Documents Table -->
            <DataTable :value="documents"
                       :paginator="true"
                       :rows="10"
                       :loading="loading"
                       v-model:selection="selectedDocuments"
                       selectionMode="multiple"
                       dataKey="id"
                       class="p-datatable-sm">
                
                <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
                
                <Column field="name" header="Document Name" :sortable="true">
                    <template #body="slotProps">
                        <div class="flex align-items-center gap-2">
                            <i :class="getFileIcon(slotProps.data.type)" class="text-lg"></i>
                            <span class="font-medium">{{ slotProps.data.name }}</span>
                        </div>
                    </template>
                </Column>

                <Column field="type" header="Type" :sortable="true">
                    <template #body="slotProps">
                        <Tag :value="slotProps.data.type" severity="info" />
                    </template>
                </Column>

                <Column field="currentLevel" header="Current Level" :sortable="true">
                    <template #body="slotProps">
                        <Tag :value="slotProps.data.currentLevel"
                             :severity="getLevelSeverity(slotProps.data.currentLevel)" />
                    </template>
                </Column>

                <Column field="status" header="Status" :sortable="true">
                    <template #body="slotProps">
                        <Tag :value="slotProps.data.status"
                             :severity="getStatusSeverity(slotProps.data.status)" />
                    </template>
                </Column>

                <Column field="uploadedBy" header="Uploaded By">
                    <template #body="slotProps">
                        <div class="flex align-items-center gap-2">
                            <Avatar :label="getInitials(slotProps.data.uploadedBy)"
                                    size="small"
                                    shape="circle" />
                            <span>{{ slotProps.data.uploadedBy }}</span>
                        </div>
                    </template>
                </Column>

                <Column field="uploadedAt" header="Upload Date" :sortable="true">
                    <template #body="slotProps">
                        {{ formatDateTime(slotProps.data.uploadedAt) }}
                    </template>
                </Column>

                <Column field="dueDate" header="Due Date" :sortable="true">
                    <template #body="slotProps">
                        <span :class="{ 'text-red-500': isOverdue(slotProps.data.dueDate) }">
                            {{ formatDate(slotProps.data.dueDate) }}
                        </span>
                    </template>
                </Column>

                <Column header="Actions" :exportable="false">
                    <template #body="slotProps">
                        <div class="flex gap-2">
                            <Button icon="pi pi-eye"
                                    class="p-button-rounded p-button-text p-button-sm"
                                    @click="viewDocument(slotProps.data)"
                                    v-tooltip.top="'View'" />
                            <Button icon="pi pi-download"
                                    class="p-button-rounded p-button-text p-button-sm"
                                    @click="downloadDocument(slotProps.data)"
                                    v-tooltip.top="'Download'" />
                            <Button icon="pi pi-send"
                                    class="p-button-rounded p-button-text p-button-sm p-button-warning"
                                    @click="transferToL2(slotProps.data)"
                                    v-tooltip.top="'Transfer to L2'"
                                    :disabled="!canTransferToL2(slotProps.data)" />
                            <Button icon="pi pi-check"
                                    class="p-button-rounded p-button-text p-button-sm p-button-success"
                                    @click="approveDocument(slotProps.data)"
                                    v-tooltip.top="'Approve'"
                                    :disabled="!canApprove(slotProps.data)" />
                        </div>
                    </template>
                </Column>
            </DataTable>
        </div>

        <!-- Upload Dialog -->
        <Dialog v-model:visible="showUploadDialog"
                header="Upload Document"
                :modal="true"
                :style="{ width: '50vw' }">
            <div class="grid">
                <div class="col-12">
                    <div class="field">
                        <label for="docName">Document Name *</label>
                        <InputText id="docName"
                                   v-model="uploadForm.name"
                                   class="w-full mt-2"
                                   placeholder="Enter document name" />
                    </div>
                </div>
                
                <div class="col-12 md:col-6">
                    <div class="field">
                        <label for="docType">Document Type *</label>
                        <Dropdown id="docType"
                                  v-model="uploadForm.type"
                                  :options="documentTypes"
                                  optionLabel="label"
                                  optionValue="value"
                                  placeholder="Select type"
                                  class="w-full mt-2" />
                    </div>
                </div>
                
                <div class="col-12 md:col-6">
                    <div class="field">
                        <label for="docPriority">Priority</label>
                        <Dropdown id="docPriority"
                                  v-model="uploadForm.priority"
                                  :options="priorityOptions"
                                  optionLabel="label"
                                  optionValue="value"
                                  placeholder="Select priority"
                                  class="w-full mt-2" />
                    </div>
                </div>
                
                <div class="col-12">
                    <div class="field">
                        <label for="docDescription">Description</label>
                        <Textarea id="docDescription"
                                  v-model="uploadForm.description"
                                  rows="3"
                                  class="w-full mt-2"
                                  placeholder="Document description..." />
                    </div>
                </div>
                
                <div class="col-12">
                    <div class="field">
                        <label>File Upload</label>
                        <FileUpload mode="basic"
                                    name="document"
                                    :auto="false"
                                    accept=".pdf,.doc,.docx,.xls,.xlsx"
                                    :maxFileSize="10000000"
                                    @select="onFileSelect"
                                    class="mt-2" />
                    </div>
                </div>
            </div>

            <template #footer>
                <Button label="Cancel"
                        icon="pi pi-times"
                        @click="showUploadDialog = false"
                        class="p-button-text" />
                <Button label="Upload"
                        icon="pi pi-upload"
                        @click="uploadDocument"
                        :disabled="!isUploadFormValid" />
            </template>
        </Dialog>

        <!-- Document Viewer Dialog -->
        <Dialog v-model:visible="showViewerDialog"
                :header="selectedDocument ? selectedDocument.name : ''"
                :modal="true"
                :style="{ width: '70vw' }"
                :maximizable="true">
            <div v-if="selectedDocument" class="document-viewer">
                <div class="grid">
                    <div class="col-12 md:col-8">
                        <div class="document-preview">
                            <div class="text-center p-6 surface-ground border-round">
                                <i :class="getFileIcon(selectedDocument.type)" class="text-6xl text-500 mb-3"></i>
                                <div class="text-xl font-medium mb-2">{{ selectedDocument.name }}</div>
                                <div class="text-500 mb-4">{{ selectedDocument.type }} Document</div>
                                <Button label="Download"
                                        icon="pi pi-download"
                                        @click="downloadDocument(selectedDocument)" />
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-12 md:col-4">
                        <div class="surface-card p-4 border-round">
                            <h6>Document Information</h6>
                            <div class="field">
                                <label class="block text-500 mb-1">Status</label>
                                <Tag :value="selectedDocument.status"
                                     :severity="getStatusSeverity(selectedDocument.status)" />
                            </div>
                            <div class="field">
                                <label class="block text-500 mb-1">Current Level</label>
                                <Tag :value="selectedDocument.currentLevel"
                                     :severity="getLevelSeverity(selectedDocument.currentLevel)" />
                            </div>
                            <div class="field">
                                <label class="block text-500 mb-1">Uploaded By</label>
                                <div>{{ selectedDocument.uploadedBy }}</div>
                            </div>
                            <div class="field">
                                <label class="block text-500 mb-1">Upload Date</label>
                                <div>{{ formatDateTime(selectedDocument.uploadedAt) }}</div>
                            </div>
                            <div class="field">
                                <label class="block text-500 mb-1">Due Date</label>
                                <div :class="{ 'text-red-500': isOverdue(selectedDocument.dueDate) }">
                                    {{ formatDate(selectedDocument.dueDate) }}
                                </div>
                            </div>
                        </div>

                        <div class="surface-card p-4 border-round mt-3">
                            <h6>Actions</h6>
                            <div class="flex flex-column gap-2">
                                <Button label="Transfer to L2"
                                        icon="pi pi-send"
                                        @click="transferToL2(selectedDocument)"
                                        :disabled="!canTransferToL2(selectedDocument)"
                                        class="p-button-warning" />
                                <Button label="Approve"
                                        icon="pi pi-check"
                                        @click="approveDocument(selectedDocument)"
                                        :disabled="!canApprove(selectedDocument)"
                                        class="p-button-success" />
                                <Button label="Reject"
                                        icon="pi pi-times"
                                        @click="rejectDocument(selectedDocument)"
                                        :disabled="!canReject(selectedDocument)"
                                        class="p-button-danger" />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </Dialog>
    </div>
</template>

<script setup>
import Avatar from 'primevue/avatar';
import Button from 'primevue/button';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import Dialog from 'primevue/dialog';
import Dropdown from 'primevue/dropdown';
import FileUpload from 'primevue/fileupload';
import InputText from 'primevue/inputtext';
import Tag from 'primevue/tag';
import Textarea from 'primevue/textarea';
import { computed, onMounted, ref } from 'vue';

// Reactive state
const loading = ref(false);
const documents = ref([]);
const selectedDocuments = ref([]);
const selectedDocument = ref(null);
const showUploadDialog = ref(false);
const showViewerDialog = ref(false);
const currentStep = ref(3);

const uploadForm = ref({
    name: '',
    type: null,
    priority: 'medium',
    description: '',
    file: null
});

const flowStats = ref({
    l1Pending: 0,
    l2Review: 0,
    approved: 0,
    rejected: 0
});

// Options
const documentTypes = [
    { label: 'Transaction Report', value: 'transaction_report' },
    { label: 'KYC Document', value: 'kyc_document' },
    { label: 'Compliance Certificate', value: 'compliance_cert' },
    { label: 'Risk Assessment', value: 'risk_assessment' },
    { label: 'Other', value: 'other' }
];

const priorityOptions = [
    { label: 'High', value: 'high' },
    { label: 'Medium', value: 'medium' },
    { label: 'Low', value: 'low' }
];

// Computed
const isUploadFormValid = computed(() => {
    return uploadForm.value.name && uploadForm.value.type && uploadForm.value.file;
});

// Methods
const loadDocuments = async () => {
    loading.value = true;
    try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        documents.value = [
            {
                id: 1,
                name: 'Transaction Analysis Report',
                type: 'transaction_report',
                currentLevel: 'L1',
                status: 'pending_review',
                uploadedBy: 'John Doe',
                uploadedAt: new Date(),
                dueDate: new Date(Date.now() + 86400000 * 2),
                priority: 'high'
            },
            {
                id: 2,
                name: 'KYC Verification Document',
                type: 'kyc_document',
                currentLevel: 'L2',
                status: 'under_review',
                uploadedBy: 'Jane Smith',
                uploadedAt: new Date(Date.now() - 86400000),
                dueDate: new Date(Date.now() + 86400000),
                priority: 'medium'
            }
        ];

        updateFlowStats();
    } catch (error) {
        console.error('Error loading documents:', error);
    } finally {
        loading.value = false;
    }
};

const updateFlowStats = () => {
    flowStats.value = {
        l1Pending: documents.value.filter(d => d.currentLevel === 'L1' && d.status === 'pending_review').length,
        l2Review: documents.value.filter(d => d.currentLevel === 'L2' && d.status === 'under_review').length,
        approved: documents.value.filter(d => d.status === 'approved').length,
        rejected: documents.value.filter(d => d.status === 'rejected').length
    };
};

const viewDocument = (document) => {
    selectedDocument.value = document;
    showViewerDialog.value = true;
};

const downloadDocument = (document) => {
    console.log('Downloading document:', document.name);
    // Implement download logic
};

const transferToL2 = async (document) => {
    try {
        document.currentLevel = 'L2';
        document.status = 'transferred';
        
        // Send notification
        await sendTransferNotification(document);
        
        updateFlowStats();
        console.log('Document transferred to L2:', document.name);
    } catch (error) {
        console.error('Error transferring document:', error);
    }
};

const approveDocument = async (document) => {
    try {
        document.status = 'approved';
        
        // Send notification
        await sendApprovalNotification(document);
        
        updateFlowStats();
        console.log('Document approved:', document.name);
    } catch (error) {
        console.error('Error approving document:', error);
    }
};

const rejectDocument = async (document) => {
    try {
        document.status = 'rejected';
        
        // Send notification
        await sendRejectionNotification(document);
        
        updateFlowStats();
        console.log('Document rejected:', document.name);
    } catch (error) {
        console.error('Error rejecting document:', error);
    }
};

const uploadDocument = async () => {
    try {
        const newDocument = {
            id: Date.now(),
            name: uploadForm.value.name,
            type: uploadForm.value.type,
            currentLevel: 'L1',
            status: 'pending_review',
            uploadedBy: 'Current User',
            uploadedAt: new Date(),
            dueDate: new Date(Date.now() + 86400000 * 3),
            priority: uploadForm.value.priority,
            description: uploadForm.value.description
        };

        documents.value.unshift(newDocument);
        updateFlowStats();

        // Reset form
        uploadForm.value = {
            name: '',
            type: null,
            priority: 'medium',
            description: '',
            file: null
        };

        showUploadDialog.value = false;
        console.log('Document uploaded successfully');
    } catch (error) {
        console.error('Error uploading document:', error);
    }
};

const onFileSelect = (event) => {
    uploadForm.value.file = event.files[0];
};

const sendTransferNotification = async (document) => {
    console.log('Sending L1→L2 transfer notification for:', document.name);
    // Implement notification logic
};

const sendApprovalNotification = async (document) => {
    console.log('Sending approval notification for:', document.name);
    // Implement notification logic
};

const sendRejectionNotification = async (document) => {
    console.log('Sending rejection notification for:', document.name);
    // Implement notification logic
};

// Utility functions
const formatDate = (date) => {
    return new Date(date).toLocaleDateString();
};

const formatDateTime = (date) => {
    return new Date(date).toLocaleString();
};

const isOverdue = (date) => {
    return new Date(date) < new Date();
};

const getInitials = (name) => {
    return name
        .split(' ')
        .map(n => n[0])
        .join('');
};

const getFileIcon = (type) => {
    switch (type) {
        case 'transaction_report': return 'pi pi-chart-line';
        case 'kyc_document': return 'pi pi-id-card';
        case 'compliance_cert': return 'pi pi-verified';
        case 'risk_assessment': return 'pi pi-exclamation-triangle';
        default: return 'pi pi-file';
    }
};

const getLevelSeverity = (level) => {
    switch (level) {
        case 'L1': return 'info';
        case 'L2': return 'warning';
        default: return 'info';
    }
};

const getStatusSeverity = (status) => {
    switch (status) {
        case 'pending_review': return 'warning';
        case 'under_review': return 'info';
        case 'transferred': return 'warning';
        case 'approved': return 'success';
        case 'rejected': return 'danger';
        default: return 'info';
    }
};

const canTransferToL2 = (document) => {
    return document.currentLevel === 'L1' && 
           (document.status === 'pending_review' || document.status === 'under_review');
};

const canApprove = (document) => {
    return document.status !== 'approved' && document.status !== 'rejected';
};

const canReject = (document) => {
    return document.status !== 'approved' && document.status !== 'rejected';
};

// Lifecycle hooks
onMounted(() => {
    loadDocuments();
});
</script>

<style scoped>
.document-flow-chart {
    padding: 2rem 0;
}

.flow-container {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-wrap: wrap;
    gap: 1rem;
}

.flow-step {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 1rem;
    border-radius: 8px;
    background: var(--surface-card);
    border: 2px solid var(--surface-border);
    min-width: 150px;
    transition: all 0.3s ease;
}

.flow-step.active {
    border-color: var(--primary-color);
    background: var(--primary-50);
}

.step-icon {
    width: 3rem;
    height: 3rem;
    border-radius: 50%;
    background: var(--surface-100);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 0.5rem;
    font-size: 1.25rem;
    color: var(--text-color-secondary);
}

.flow-step.active .step-icon {
    background: var(--primary-color);
    color: white;
}

.step-label {
    font-weight: 600;
    margin-bottom: 0.25rem;
    color: var(--text-color);
}

.step-description {
    font-size: 0.875rem;
    color: var(--text-color-secondary);
}

.flow-arrow {
    font-size: 1.5rem;
    color: var(--text-color-secondary);
}

.document-preview {
    height: 400px;
    display: flex;
    align-items: center;
    justify-content: center;
}

@media (max-width: 768px) {
    .flow-container {
        flex-direction: column;
    }
    
    .flow-arrow {
        transform: rotate(90deg);
    }
}
</style>
