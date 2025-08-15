<template>
    <div class="grid">
        <div class="col-12">
            <div class="card">
                <!-- Header Section -->
                <div class="exchanger-header">
                    <div class="header-main">
                        <div class="header-left">
                            <div class="title-section">
                                <div class="icon-container">
                                    <div class="header-icon-wrapper">
                                        <i class="pi pi-plus-circle header-icon"></i>
                                        <div class="icon-glow"></div>
                                    </div>
                                </div>
                                <div class="title-content">
                                    <h1 class="page-title">Create AML Case</h1>
                                    <p class="page-subtitle">Report suspicious transaction or compliance concern</p>
                                </div>
                            </div>
                        </div>
                        
                        <div class="header-actions">
                            <Button 
                                icon="pi pi-arrow-left" 
                                label="Back to Dashboard" 
                                @click="router.push('/')"
                                class="p-button-outlined" />
                        </div>
                    </div>
                </div>

                <!-- Case Creation Form -->
                <div class="case-form-container">
                    <form @submit.prevent="submitCase" class="case-form">
                        <!-- Basic Information -->
                        <div class="form-section">
                            <h3 class="section-title">
                                <i class="pi pi-info-circle"></i>
                                Basic Information
                            </h3>
                            
                            <div class="form-grid">
                                <div class="form-field">
                                    <label for="caseTitle" class="field-label">Case Title *</label>
                                    <InputText 
                                        id="caseTitle"
                                        v-model="caseData.title" 
                                        placeholder="Enter descriptive case title"
                                        :class="{ 'p-invalid': errors.title }"
                                        class="w-full" />
                                    <small v-if="errors.title" class="p-error">{{ errors.title }}</small>
                                </div>
                                
                                <div class="form-field">
                                    <label for="priority" class="field-label">Priority *</label>
                                    <Dropdown 
                                        id="priority"
                                        v-model="caseData.priority" 
                                        :options="priorityOptions" 
                                        optionLabel="label" 
                                        optionValue="value"
                                        placeholder="Select priority level"
                                        :class="{ 'p-invalid': errors.priority }"
                                        class="w-full" />
                                    <small v-if="errors.priority" class="p-error">{{ errors.priority }}</small>
                                </div>
                                
                                <div class="form-field span-2">
                                    <label for="description" class="field-label">Description *</label>
                                    <Textarea 
                                        id="description"
                                        v-model="caseData.description" 
                                        placeholder="Provide detailed description of the suspicious activity or compliance concern"
                                        :class="{ 'p-invalid': errors.description }"
                                        rows="4"
                                        class="w-full" />
                                    <small v-if="errors.description" class="p-error">{{ errors.description }}</small>
                                </div>
                            </div>
                        </div>

                        <!-- Transaction Details -->
                        <div class="form-section">
                            <h3 class="section-title">
                                <i class="pi pi-credit-card"></i>
                                Transaction Details
                            </h3>
                            
                            <div class="form-grid">
                                <div class="form-field">
                                    <label for="transactionId" class="field-label">Transaction ID</label>
                                    <InputText 
                                        id="transactionId"
                                        v-model="caseData.transactionId" 
                                        placeholder="Enter transaction hash/ID"
                                        class="w-full" />
                                </div>
                                
                                <div class="form-field">
                                    <label for="cryptocurrency" class="field-label">Cryptocurrency</label>
                                    <Dropdown 
                                        id="cryptocurrency"
                                        v-model="caseData.cryptocurrency" 
                                        :options="cryptoOptions" 
                                        optionLabel="label" 
                                        optionValue="value"
                                        placeholder="Select cryptocurrency"
                                        class="w-full" />
                                </div>
                                
                                <div class="form-field">
                                    <label for="amount" class="field-label">Transaction Amount</label>
                                    <InputNumber 
                                        id="amount"
                                        v-model="caseData.amount" 
                                        placeholder="0.00"
                                        :minFractionDigits="2"
                                        :maxFractionDigits="8"
                                        class="w-full" />
                                </div>
                                
                                <div class="form-field">
                                    <label for="transactionDate" class="field-label">Transaction Date</label>
                                    <Calendar 
                                        id="transactionDate"
                                        v-model="caseData.transactionDate" 
                                        placeholder="Select transaction date"
                                        :showIcon="true"
                                        class="w-full" />
                                </div>
                            </div>
                        </div>

                        <!-- Wallet Information -->
                        <div class="form-section">
                            <h3 class="section-title">
                                <i class="pi pi-wallet"></i>
                                Wallet Information
                            </h3>
                            
                            <div class="form-grid">
                                <div class="form-field">
                                    <label for="senderWallet" class="field-label">Sender Wallet Address</label>
                                    <InputText 
                                        id="senderWallet"
                                        v-model="caseData.senderWallet" 
                                        placeholder="Enter sender wallet address"
                                        class="w-full font-mono" />
                                </div>
                                
                                <div class="form-field">
                                    <label for="receiverWallet" class="field-label">Receiver Wallet Address</label>
                                    <InputText 
                                        id="receiverWallet"
                                        v-model="caseData.receiverWallet" 
                                        placeholder="Enter receiver wallet address"
                                        class="w-full font-mono" />
                                </div>
                            </div>
                        </div>

                        <!-- Risk Indicators -->
                        <div class="form-section">
                            <h3 class="section-title">
                                <i class="pi pi-exclamation-triangle"></i>
                                Risk Indicators
                            </h3>
                            
                            <div class="risk-indicators">
                                <div class="indicator-group">
                                    <label class="indicator-label">Select applicable risk factors:</label>
                                    <div class="indicator-checkboxes">
                                        <div 
                                            v-for="indicator in riskIndicators" 
                                            :key="indicator.value"
                                            class="indicator-item">
                                            <Checkbox 
                                                :id="indicator.value"
                                                v-model="caseData.riskIndicators" 
                                                :value="indicator.value" />
                                            <label :for="indicator.value" class="indicator-text">
                                                {{ indicator.label }}
                                            </label>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Additional Information -->
                        <div class="form-section">
                            <h3 class="section-title">
                                <i class="pi pi-file-o"></i>
                                Additional Information
                            </h3>
                            
                            <div class="form-grid">
                                <div class="form-field span-2">
                                    <label for="additionalNotes" class="field-label">Additional Notes</label>
                                    <Textarea 
                                        id="additionalNotes"
                                        v-model="caseData.additionalNotes" 
                                        placeholder="Any additional information or context that might be relevant"
                                        rows="3"
                                        class="w-full" />
                                </div>
                                
                                <div class="form-field">
                                    <label for="attachments" class="field-label">Attachments</label>
                                    <FileUpload 
                                        mode="basic" 
                                        :multiple="true"
                                        accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
                                        :maxFileSize="5000000"
                                        @select="onFileSelect"
                                        chooseLabel="Choose Files"
                                        class="w-full" />
                                    <small class="help-text">Max 5MB per file. PDF, images, and documents allowed.</small>
                                </div>
                                
                                <div class="form-field">
                                    <label for="contactInfo" class="field-label">Contact Information</label>
                                    <InputText 
                                        id="contactInfo"
                                        v-model="caseData.contactInfo" 
                                        placeholder="Email or phone for follow-up"
                                        class="w-full" />
                                </div>
                            </div>
                        </div>

                        <!-- Form Actions -->
                        <div class="form-actions">
                            <Button 
                                type="button"
                                icon="pi pi-times" 
                                label="Cancel" 
                                @click="resetForm"
                                class="p-button-text" />
                            <Button 
                                type="button"
                                icon="pi pi-save" 
                                label="Save Draft" 
                                @click="saveDraft"
                                class="p-button-outlined" />
                            <Button 
                                type="submit"
                                icon="pi pi-send" 
                                label="Submit Case" 
                                :loading="submitting"
                                class="p-button-primary" />
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const toast = useToast()
const authStore = useAuthStore()

// Form data
const caseData = reactive({
    title: '',
    description: '',
    priority: null,
    transactionId: '',
    cryptocurrency: null,
    amount: null,
    transactionDate: null,
    senderWallet: '',
    receiverWallet: '',
    riskIndicators: [],
    additionalNotes: '',
    contactInfo: '',
    attachments: []
})

// Form validation errors
const errors = reactive({})

// Form submission state
const submitting = ref(false)

// Options for dropdowns
const priorityOptions = [
    { label: 'Low', value: 'low' },
    { label: 'Medium', value: 'medium' },
    { label: 'High', value: 'high' },
    { label: 'Critical', value: 'critical' }
]

const cryptoOptions = [
    { label: 'Bitcoin (BTC)', value: 'BTC' },
    { label: 'Ethereum (ETH)', value: 'ETH' },
    { label: 'Tether (USDT)', value: 'USDT' },
    { label: 'Binance Coin (BNB)', value: 'BNB' },
    { label: 'USD Coin (USDC)', value: 'USDC' },
    { label: 'Cardano (ADA)', value: 'ADA' },
    { label: 'Solana (SOL)', value: 'SOL' },
    { label: 'Other', value: 'OTHER' }
]

const riskIndicators = [
    { label: 'Large unusual transaction amount', value: 'large_amount' },
    { label: 'Frequent small transactions (structuring)', value: 'structuring' },
    { label: 'Transactions to/from high-risk jurisdictions', value: 'high_risk_jurisdiction' },
    { label: 'Transactions involving blacklisted addresses', value: 'blacklisted_address' },
    { label: 'Unusual transaction timing or patterns', value: 'unusual_timing' },
    { label: 'Transactions through mixing services', value: 'mixing_service' },
    { label: 'Customer behavior inconsistent with profile', value: 'inconsistent_behavior' },
    { label: 'Rapid movement of funds', value: 'rapid_movement' },
    { label: 'Connection to known criminal activity', value: 'criminal_connection' }
]

// Form validation
const validateForm = () => {
    const newErrors = {}
    
    if (!caseData.title?.trim()) {
        newErrors.title = 'Case title is required'
    }
    
    if (!caseData.description?.trim()) {
        newErrors.description = 'Case description is required'
    }
    
    if (!caseData.priority) {
        newErrors.priority = 'Priority level is required'
    }
    
    // Clear previous errors and set new ones
    Object.keys(errors).forEach(key => delete errors[key])
    Object.assign(errors, newErrors)
    
    return Object.keys(newErrors).length === 0
}

// File upload handler
const onFileSelect = (event) => {
    caseData.attachments = event.files
}

// Form submission
const submitCase = async () => {
    if (!validateForm()) {
        toast.add({
            severity: 'error',
            summary: 'Validation Error',
            detail: 'Please fix the highlighted errors before submitting',
            life: 5000
        })
        return
    }
    
    try {
        submitting.value = true
        
        // Prepare case data for submission
        const submissionData = {
            ...caseData,
            status: 'pending_l1',
            created_by: authStore.user?.id,
            created_at: new Date().toISOString(),
            case_type: 'exchanger_report'
        }
        
        // Here you would call your API to create the case
        // await apiService.createCase(submissionData)
        
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 2000))
        
        toast.add({
            severity: 'success',
            summary: 'Case Created',
            detail: 'Your AML case has been successfully submitted for review',
            life: 5000
        })
        
        // Navigate back to dashboard or cases list
        router.push('/')
        
    } catch (error) {
        console.error('Failed to submit case:', error)
        toast.add({
            severity: 'error',
            summary: 'Submission Failed',
            detail: 'Failed to submit case. Please try again.',
            life: 5000
        })
    } finally {
        submitting.value = false
    }
}

// Save as draft
const saveDraft = async () => {
    try {
        const draftData = {
            ...caseData,
            status: 'draft',
            created_by: authStore.user?.id,
            updated_at: new Date().toISOString()
        }
        
        // Here you would save to localStorage or API
        localStorage.setItem('case_draft', JSON.stringify(draftData))
        
        toast.add({
            severity: 'info',
            summary: 'Draft Saved',
            detail: 'Your case has been saved as a draft',
            life: 3000
        })
    } catch (error) {
        console.error('Failed to save draft:', error)
        toast.add({
            severity: 'error',
            summary: 'Save Failed',
            detail: 'Failed to save draft',
            life: 3000
        })
    }
}

// Reset form
const resetForm = () => {
    Object.keys(caseData).forEach(key => {
        if (Array.isArray(caseData[key])) {
            caseData[key] = []
        } else {
            caseData[key] = key === 'amount' ? null : ''
        }
    })
    Object.keys(errors).forEach(key => delete errors[key])
}

// Load draft on component mount
const loadDraft = () => {
    try {
        const saved = localStorage.getItem('case_draft')
        if (saved) {
            const draftData = JSON.parse(saved)
            Object.assign(caseData, draftData)
            toast.add({
                severity: 'info',
                summary: 'Draft Loaded',
                detail: 'Previous draft has been restored',
                life: 3000
            })
        }
    } catch (error) {
        console.error('Failed to load draft:', error)
    }
}

// Load draft on mount
loadDraft()
</script>

<style scoped>
/* ===== HEADER STYLES ===== */
.exchanger-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    margin: -1.5rem -1.5rem 2rem -1.5rem;
    padding: 2rem;
    border-radius: 0;
}

.header-main {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.title-section {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.icon-container {
    position: relative;
}

.header-icon-wrapper {
    position: relative;
    width: 3rem;
    height: 3rem;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 12px;
    backdrop-filter: blur(10px);
}

.header-icon {
    font-size: 1.5rem;
    color: white;
}

.icon-glow {
    position: absolute;
    inset: -4px;
    background: linear-gradient(45deg, rgba(255, 255, 255, 0.3), transparent);
    border-radius: 16px;
    z-index: -1;
}

.page-title {
    font-size: 2rem;
    font-weight: 700;
    margin: 0 0 0.25rem 0;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.page-subtitle {
    font-size: 1rem;
    opacity: 0.9;
    margin: 0;
    font-weight: 400;
}

/* ===== FORM STYLES ===== */
.case-form-container {
    max-width: 1000px;
    margin: 0 auto;
}

.case-form {
    display: flex;
    flex-direction: column;
    gap: 2rem;
}

.form-section {
    background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    border: 1px solid rgba(226, 232, 240, 0.6);
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.section-title {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 1.125rem;
    font-weight: 600;
    color: #1e293b;
    margin: 0 0 1.5rem 0;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid rgba(226, 232, 240, 0.6);
}

.section-title i {
    color: #667eea;
}

.form-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
    align-items: start;
}

.form-field {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.form-field.span-2 {
    grid-column: span 2;
}

.field-label {
    font-weight: 600;
    color: #374151;
    font-size: 0.875rem;
}

.help-text {
    color: #64748b;
    font-size: 0.75rem;
    margin-top: 0.25rem;
}

/* ===== RISK INDICATORS ===== */
.risk-indicators {
    padding: 1rem;
    background: rgba(248, 250, 252, 0.8);
    border-radius: 8px;
    border: 1px solid rgba(226, 232, 240, 0.6);
}

.indicator-label {
    font-weight: 600;
    color: #374151;
    margin-bottom: 1rem;
    display: block;
}

.indicator-checkboxes {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 0.75rem;
}

.indicator-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem;
    background: rgba(255, 255, 255, 0.8);
    border-radius: 6px;
    border: 1px solid rgba(226, 232, 240, 0.4);
    transition: all 0.2s ease;
}

.indicator-item:hover {
    background: rgba(255, 255, 255, 1);
    border-color: rgba(226, 232, 240, 0.8);
}

.indicator-text {
    font-size: 0.875rem;
    color: #374151;
    cursor: pointer;
}

/* ===== FORM ACTIONS ===== */
.form-actions {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    padding-top: 1.5rem;
    border-top: 1px solid rgba(226, 232, 240, 0.6);
}

/* ===== RESPONSIVE ===== */
@media (max-width: 768px) {
    .exchanger-header {
        margin: -1rem -1rem 1.5rem -1rem;
        padding: 1.5rem 1rem;
    }
    
    .header-main {
        flex-direction: column;
        gap: 1rem;
        align-items: flex-start;
    }
    
    .page-title {
        font-size: 1.5rem;
    }
    
    .form-grid {
        grid-template-columns: 1fr;
    }
    
    .form-field.span-2 {
        grid-column: span 1;
    }
    
    .indicator-checkboxes {
        grid-template-columns: 1fr;
    }
    
    .form-actions {
        flex-direction: column;
    }
}

/* ===== VALIDATION STYLES ===== */
.p-invalid {
    border-color: #ef4444 !important;
    box-shadow: 0 0 0 0.2rem rgba(239, 68, 68, 0.2) !important;
}

.p-error {
    color: #ef4444;
    font-size: 0.75rem;
    margin-top: 0.25rem;
}

/* ===== CUSTOM COMPONENT STYLES ===== */
.font-mono {
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 0.875rem;
}

:deep(.p-fileupload-basic .p-button) {
    width: 100%;
}

:deep(.p-dropdown-panel) {
    border-radius: 8px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

:deep(.p-calendar .p-datepicker) {
    border-radius: 8px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}
</style>
