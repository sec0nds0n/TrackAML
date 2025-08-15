<template>
    <div class="executive-summary-container" ref="summaryContainer">
        <div class="summary-header">
            <div class="header-content">
                <div class="header-icon">
                    <i class="pi pi-chart-line"></i>
                </div>
                <div class="header-text">
                    <h2>Executive Summary</h2>
                    <p>Comprehensive case analysis and risk assessment overview</p>
                </div>
            </div>
            <div class="summary-actions">
                <Button 
                    icon="pi pi-download" 
                    label="Export PDF"
                    size="small"
                    severity="secondary"
                    outlined
                    :loading="isExporting"
                    @click="showExportOptions" />
                <Button 
                    icon="pi pi-share-alt" 
                    label="Share"
                    size="small"
                    @click="shareSummary" />
            </div>
        </div>

        <div class="summary-content">
            <!-- Key Metrics Row -->
            <div class="metrics-grid">
                <div class="metric-card risk-score">
                    <div class="metric-icon">
                        <i class="pi pi-exclamation-triangle"></i>
                    </div>
                    <div class="metric-content">
                        <div class="metric-value">{{ riskScore }}/100</div>
                        <div class="metric-label">Risk Score</div>
                        <div class="metric-trend" :class="riskTrendClass">
                            <i :class="riskTrendIcon"></i>
                            <span>{{ riskTrend }}%</span>
                        </div>
                    </div>
                </div>

                <div class="metric-card confidence-level">
                    <div class="metric-icon">
                        <i class="pi pi-verified"></i>
                    </div>
                    <div class="metric-content">
                        <div class="metric-value">{{ confidenceLevel }}%</div>
                        <div class="metric-label">Confidence Level</div>
                        <div class="metric-description">Analysis Accuracy</div>
                    </div>
                </div>

                <div class="metric-card financial-impact">
                    <div class="metric-icon">
                        <i class="pi pi-dollar"></i>
                    </div>
                    <div class="metric-content">
                        <div class="metric-value">${{ formatAmount(financialImpact) }}</div>
                        <div class="metric-label">Financial Impact</div>
                        <div class="metric-description">Potential Loss</div>
                    </div>
                </div>

                <div class="metric-card time-to-resolution">
                    <div class="metric-icon">
                        <i class="pi pi-clock"></i>
                    </div>
                    <div class="metric-content">
                        <div class="metric-value">{{ timeToResolution }}</div>
                        <div class="metric-label">Est. Resolution</div>
                        <div class="metric-description">Business Days</div>
                    </div>
                </div>
            </div>

            <!-- Summary Sections -->
            <div class="summary-sections">
                <!-- Case Overview -->
                <div class="summary-section overview-section">
                    <div class="section-header">
                        <h3>
                            <i class="pi pi-info-circle"></i>
                            Case Overview
                        </h3>
                        <Tag 
                            :value="caseData?.status"
                            :severity="getStatusSeverity(caseData?.status)"
                            class="status-indicator" />
                    </div>
                    <div class="section-content">
                        <div class="overview-grid">
                            <div class="overview-item">
                                <label>Case Type</label>
                                <span class="overview-value">{{ caseType }}</span>
                            </div>
                            <div class="overview-item">
                                <label>Detection Method</label>
                                <span class="overview-value">{{ detectionMethod }}</span>
                            </div>
                            <div class="overview-item">
                                <label>Jurisdiction</label>
                                <span class="overview-value">{{ jurisdiction }}</span>
                            </div>
                            <div class="overview-item">
                                <label>Regulatory Impact</label>
                                <span class="overview-value">{{ regulatoryImpact }}</span>
                            </div>
                        </div>
                        <div class="case-description">
                            <p>{{ caseData?.details?.description || 'No description available.' }}</p>
                        </div>
                    </div>
                </div>

                <!-- Risk Assessment -->
                <div class="summary-section risk-section">
                    <div class="section-header">
                        <h3>
                            <i class="pi pi-shield"></i>
                            Risk Assessment
                        </h3>
                        <div class="risk-level-indicator" :class="getRiskLevelClass(caseData?.riskLevel)">
                            {{ caseData?.riskLevel }} Risk
                        </div>
                    </div>
                    <div class="section-content">
                        <div class="risk-factors">
                            <div class="risk-factor-item" 
                                 v-for="factor in riskFactors" 
                                 :key="factor.name">
                                <div class="factor-header">
                                    <span class="factor-name">{{ factor.name }}</span>
                                    <div class="factor-score" :class="getFactorScoreClass(factor.score)">
                                        {{ factor.score }}/10
                                    </div>
                                </div>
                                <div class="factor-bar">
                                    <div class="factor-progress" 
                                         :style="{ width: (factor.score * 10) + '%' }"
                                         :class="getFactorScoreClass(factor.score)"></div>
                                </div>
                                <div class="factor-description">{{ factor.description }}</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Key Findings -->
                <div class="summary-section findings-section">
                    <div class="section-header">
                        <h3>
                            <i class="pi pi-search"></i>
                            Key Findings
                        </h3>
                        <Badge :value="keyFindings.length" severity="info" />
                    </div>
                    <div class="section-content">
                        <div class="findings-list">
                            <div class="finding-item" 
                                 v-for="(finding, index) in keyFindings" 
                                 :key="index">
                                <div class="finding-priority" :class="getFindingPriorityClass(finding.priority)">
                                    <i :class="getFindingPriorityIcon(finding.priority)"></i>
                                </div>
                                <div class="finding-content">
                                    <div class="finding-title">{{ finding.title }}</div>
                                    <div class="finding-description">{{ finding.description }}</div>
                                    <div class="finding-tags">
                                        <Chip 
                                            v-for="tag in finding.tags" 
                                            :key="tag"
                                            :label="tag"
                                            class="finding-tag" />
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Recommendations -->
                <div class="summary-section recommendations-section">
                    <div class="section-header">
                        <h3>
                            <i class="pi pi-lightbulb"></i>
                            Recommendations
                        </h3>
                        <div class="recommendation-priority">
                            <Tag value="Action Required" severity="warning" />
                        </div>
                    </div>
                    <div class="section-content">
                        <div class="recommendations-list">
                            <div class="recommendation-item" 
                                 v-for="(rec, index) in recommendations" 
                                 :key="index">
                                <div class="recommendation-header">
                                    <div class="recommendation-priority" :class="getRecommendationPriorityClass(rec.priority)">
                                        {{ rec.priority }}
                                    </div>
                                    <div class="recommendation-timeline">
                                        <i class="pi pi-clock"></i>
                                        {{ rec.timeline }}
                                    </div>
                                </div>
                                <div class="recommendation-title">{{ rec.title }}</div>
                                <div class="recommendation-description">{{ rec.description }}</div>
                                <div class="recommendation-impact">
                                    <span class="impact-label">Expected Impact:</span>
                                    <span class="impact-value">{{ rec.impact }}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Compliance Status -->
                <div class="summary-section compliance-section">
                    <div class="section-header">
                        <h3>
                            <i class="pi pi-check-circle"></i>
                            Compliance Status
                        </h3>
                        <div class="compliance-score" :class="getComplianceScoreClass(complianceScore)">
                            {{ complianceScore }}%
                        </div>
                    </div>
                    <div class="section-content">
                        <div class="compliance-items">
                            <div class="compliance-item" 
                                 v-for="item in complianceItems" 
                                 :key="item.regulation">
                                <div class="compliance-status" :class="getComplianceStatusClass(item.status)">
                                    <i :class="getComplianceStatusIcon(item.status)"></i>
                                </div>
                                <div class="compliance-content">
                                    <div class="compliance-regulation">{{ item.regulation }}</div>
                                    <div class="compliance-description">{{ item.description }}</div>
                                    <div class="compliance-requirements">
                                        <span v-for="req in item.requirements" 
                                              :key="req"
                                              class="requirement-tag">{{ req }}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Export Options Dialog -->
        <Dialog 
            v-model:visible="showExportDialog" 
            modal 
            header="Export Options"
            :style="{ width: '450px' }"
            class="export-dialog">
            <div class="export-options">
                <div class="export-option">
                    <div class="option-header">
                        <i class="pi pi-file-pdf"></i>
                        <h4>PDF Export Type</h4>
                    </div>
                    <div class="option-content">
                        <div class="radio-group">
                            <div class="radio-item">
                                <RadioButton 
                                    v-model="exportType" 
                                    inputId="structured" 
                                    value="structured" />
                                <label for="structured">Structured Report</label>
                                <small>Professional formatted PDF with optimized layout</small>
                            </div>
                            <div class="radio-item">
                                <RadioButton 
                                    v-model="exportType" 
                                    inputId="visual" 
                                    value="visual" />
                                <label for="visual">Visual Capture</label>
                                <small>High-quality image capture of current view</small>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="export-option">
                    <div class="option-header">
                        <i class="pi pi-cog"></i>
                        <h4>Export Settings</h4>
                    </div>
                    <div class="option-content">
                        <div class="setting-item">
                            <Checkbox 
                                v-model="exportSettings.includeCharts" 
                                inputId="includeCharts" 
                                binary />
                            <label for="includeCharts">Include Charts and Graphs</label>
                        </div>
                        <div class="setting-item">
                            <Checkbox 
                                v-model="exportSettings.includeMetadata" 
                                inputId="includeMetadata" 
                                binary />
                            <label for="includeMetadata">Include Case Metadata</label>
                        </div>
                        <div class="setting-item">
                            <Checkbox 
                                v-model="exportSettings.includeTimestamp" 
                                inputId="includeTimestamp" 
                                binary />
                            <label for="includeTimestamp">Include Generation Timestamp</label>
                        </div>
                    </div>
                </div>
            </div>

            <template #footer>
                <Button 
                    label="Cancel" 
                    icon="pi pi-times" 
                    text 
                    @click="showExportDialog = false" />
                <Button 
                    label="Export PDF" 
                    icon="pi pi-download" 
                    :loading="isExporting"
                    @click="exportSummary" />
            </template>
        </Dialog>

        <!-- Export Progress Toast -->
        <Toast ref="toast" />
    </div>
</template>

<script setup>
import Badge from 'primevue/badge';
import Button from 'primevue/button';
import Checkbox from 'primevue/checkbox';
import Chip from 'primevue/chip';
import Dialog from 'primevue/dialog';
import RadioButton from 'primevue/radiobutton';
import Tag from 'primevue/tag';
import Toast from 'primevue/toast';
import { computed, ref, nextTick } from 'vue';
import { useToast } from 'primevue/usetoast';

// Import PDF services
import { pdfExportService } from '@/utils/pdfExportService';
import { advancedPdfExport } from '@/utils/advancedPdfExport';

// Props
const props = defineProps({
    caseData: {
        type: Object,
        required: true
    }
});

// Composables
const toast = useToast();

// Template refs
const summaryContainer = ref(null);

// Reactive data
const riskScore = ref(78);
const confidenceLevel = ref(92);
const financialImpact = ref(125000);
const timeToResolution = ref('3-5');
const riskTrend = ref(-12);
const complianceScore = ref(85);

// Export-related reactive data
const isExporting = ref(false);
const showExportDialog = ref(false);
const exportType = ref('structured');
const exportSettings = ref({
    includeCharts: true,
    includeMetadata: true,
    includeTimestamp: true
});

// Computed properties
const riskTrendClass = computed(() => {
    return riskTrend.value > 0 ? 'trend-up' : 'trend-down';
});

const riskTrendIcon = computed(() => {
    return riskTrend.value > 0 ? 'pi pi-arrow-up' : 'pi pi-arrow-down';
});

// Computed summary data for PDF export
const summaryData = computed(() => ({
    riskScore: riskScore.value,
    confidenceLevel: confidenceLevel.value,
    financialImpact: financialImpact.value,
    timeToResolution: timeToResolution.value,
    riskTrend: riskTrend.value,
    complianceScore: complianceScore.value,
    caseType: caseType.value,
    detectionMethod: detectionMethod.value,
    jurisdiction: jurisdiction.value,
    regulatoryImpact: regulatoryImpact.value,
    riskFactors: riskFactors.value,
    keyFindings: keyFindings.value,
    recommendations: recommendations.value,
    complianceItems: complianceItems.value,
    caseData: props.caseData
}));

// Mock data
const caseType = ref('Suspicious Transaction Monitoring');
const detectionMethod = ref('AI/ML Pattern Recognition');
const jurisdiction = ref('United States - Federal');
const regulatoryImpact = ref('BSA/AML Compliance');

const riskFactors = ref([
    {
        name: 'Transaction Pattern',
        score: 8,
        description: 'Unusual transaction frequency and amounts detected'
    },
    {
        name: 'Geographic Risk',
        score: 6,
        description: 'Transactions involving high-risk jurisdictions'
    },
    {
        name: 'Entity Risk',
        score: 7,
        description: 'Customer profile indicates elevated risk factors'
    },
    {
        name: 'Behavioral Analysis',
        score: 9,
        description: 'Significant deviation from historical patterns'
    }
]);

const keyFindings = ref([
    {
        title: 'Structured Transaction Pattern',
        description: 'Multiple transactions just below reporting thresholds detected over 30-day period',
        priority: 'high',
        tags: ['Structuring', 'BSA', 'Pattern Analysis']
    },
    {
        title: 'Cross-Border Activity',
        description: 'Unusual cross-border cryptocurrency transfers to high-risk jurisdictions',
        priority: 'high',
        tags: ['Cross-Border', 'Cryptocurrency', 'High-Risk']
    },
    {
        title: 'Customer Due Diligence Gap',
        description: 'Insufficient documentation for customer risk profile verification',
        priority: 'medium',
        tags: ['CDD', 'Documentation', 'KYC']
    }
]);

const recommendations = ref([
    {
        title: 'File Suspicious Activity Report (SAR)',
        description: 'Based on the structured transaction pattern and risk indicators, filing a SAR is recommended within regulatory timeframes.',
        priority: 'High',
        timeline: 'Within 30 days',
        impact: 'Regulatory compliance maintained'
    },
    {
        title: 'Enhanced Customer Due Diligence',
        description: 'Conduct enhanced KYC procedures to better understand customer business model and transaction patterns.',
        priority: 'Medium',
        timeline: '2-3 weeks',
        impact: 'Improved risk assessment accuracy'
    },
    {
        title: 'Transaction Monitoring Enhancement',
        description: 'Update monitoring rules to better detect similar patterns in the future.',
        priority: 'Low',
        timeline: '1-2 months',
        impact: 'Preventive measure for future cases'
    }
]);

const complianceItems = ref([
    {
        regulation: 'Bank Secrecy Act (BSA)',
        description: 'Suspicious activity reporting requirements',
        status: 'pending',
        requirements: ['SAR Filing', 'Record Keeping', 'Monitoring']
    },
    {
        regulation: 'Anti-Money Laundering (AML)',
        description: 'Customer due diligence and risk assessment',
        status: 'compliant',
        requirements: ['CDD', 'Risk Assessment', 'Ongoing Monitoring']
    },
    {
        regulation: 'Know Your Customer (KYC)',
        description: 'Customer identification and verification',
        status: 'non-compliant',
        requirements: ['Identity Verification', 'Beneficial Ownership', 'Risk Profiling']
    }
]);

// Methods
const formatAmount = (amount) => {
    return new Intl.NumberFormat('en-US').format(amount);
};

const showExportOptions = () => {
    showExportDialog.value = true;
};

const exportSummary = async () => {
    if (isExporting.value) return;
    
    isExporting.value = true;
    showExportDialog.value = false;
    
    try {
        toast.add({
            severity: 'info',
            summary: 'Export Started',
            detail: 'Generating PDF report...',
            life: 3000
        });

        let result;
        
        if (exportType.value === 'structured') {
            // Use structured PDF export
            result = await pdfExportService.exportExecutiveSummary(
                props.caseData, 
                summaryData.value
            );
        } else {
            // Use visual capture export
            await nextTick(); // Ensure DOM is updated
            result = await advancedPdfExport.exportExecutiveSummaryComplete(
                summaryContainer.value,
                props.caseData
            );
        }

        if (result.success) {
            toast.add({
                severity: 'success',
                summary: 'Export Successful',
                detail: `PDF saved as: ${result.filename}`,
                life: 5000
            });
            
            // Track export event
            trackExportEvent(result.filename);
        } else {
            throw new Error(result.error || 'Export failed');
        }
    } catch (error) {
        console.error('Export error:', error);
        toast.add({
            severity: 'error',
            summary: 'Export Failed',
            detail: error.message || 'An error occurred while generating the PDF',
            life: 5000
        });
    } finally {
        isExporting.value = false;
    }
};

const trackExportEvent = (filename) => {
    // Analytics tracking
    if (window.gtag) {
        window.gtag('event', 'pdf_export', {
            event_category: 'executive_summary',
            event_label: filename,
            case_id: props.caseData?.id
        });
    }
    
    // Custom event for internal tracking
    window.dispatchEvent(new CustomEvent('pdfExported', {
        detail: {
            filename,
            caseId: props.caseData?.id,
            exportType: exportType.value,
            timestamp: new Date().toISOString()
        }
    }));
};

const shareSummary = async () => {
    try {
        if (navigator.share) {
            // Use native Web Share API if available
            await navigator.share({
                title: 'Executive Summary Report',
                text: `Case ${props.caseData?.id} Executive Summary`,
                url: window.location.href
            });
        } else {
            // Fallback to clipboard
            await navigator.clipboard.writeText(window.location.href);
            toast.add({
                severity: 'success',
                summary: 'Link Copied',
                detail: 'Summary link copied to clipboard',
                life: 3000
            });
        }
    } catch (error) {
        console.error('Share error:', error);
        toast.add({
            severity: 'error',
            summary: 'Share Failed',
            detail: 'Unable to share summary',
            life: 3000
        });
    }
};

const getStatusSeverity = (status) => {
    switch (status) {
        case 'Under Review': return 'warning';
        case 'Investigating': return 'info';
        case 'Pending': return 'warning';
        case 'Resolved': return 'success';
        case 'Rejected': return 'danger';
        case 'escalated': return 'danger';
        default: return 'info';
    }
};

const getRiskLevelClass = (riskLevel) => {
    switch (riskLevel) {
        case 'High': return 'risk-high';
        case 'Medium': return 'risk-medium';
        case 'Low': return 'risk-low';
        default: return 'risk-medium';
    }
};

const getFactorScoreClass = (score) => {
    if (score >= 8) return 'score-high';
    if (score >= 6) return 'score-medium';
    return 'score-low';
};

const getFindingPriorityClass = (priority) => {
    switch (priority) {
        case 'high': return 'priority-high';
        case 'medium': return 'priority-medium';
        case 'low': return 'priority-low';
        default: return 'priority-medium';
    }
};

const getFindingPriorityIcon = (priority) => {
    switch (priority) {
        case 'high': return 'pi pi-exclamation-triangle';
        case 'medium': return 'pi pi-info-circle';
        case 'low': return 'pi pi-check-circle';
        default: return 'pi pi-info-circle';
    }
};

const getRecommendationPriorityClass = (priority) => {
    switch (priority.toLowerCase()) {
        case 'high': return 'rec-priority-high';
        case 'medium': return 'rec-priority-medium';
        case 'low': return 'rec-priority-low';
        default: return 'rec-priority-medium';
    }
};

const getComplianceScoreClass = (score) => {
    if (score >= 90) return 'compliance-excellent';
    if (score >= 75) return 'compliance-good';
    if (score >= 60) return 'compliance-fair';
    return 'compliance-poor';
};

const getComplianceStatusClass = (status) => {
    switch (status) {
        case 'compliant': return 'status-compliant';
        case 'pending': return 'status-pending';
        case 'non-compliant': return 'status-non-compliant';
        default: return 'status-pending';
    }
};

const getComplianceStatusIcon = (status) => {
    switch (status) {
        case 'compliant': return 'pi pi-check-circle';
        case 'pending': return 'pi pi-clock';
        case 'non-compliant': return 'pi pi-times-circle';
        default: return 'pi pi-clock';
    }
};
</script>

<style scoped>
@import './CaseExecutiveSummary.css';

/* Export Dialog Styles */
.export-dialog .export-options {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.export-option {
    border: 1px solid var(--surface-border);
    border-radius: 8px;
    padding: 1rem;
}

.option-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1rem;
}

.option-header i {
    color: var(--primary-color);
    font-size: 1.2rem;
}

.option-header h4 {
    margin: 0;
    color: var(--text-color);
}

.radio-group {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.radio-item {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.radio-item label {
    font-weight: 600;
    color: var(--text-color);
}

.radio-item small {
    color: var(--text-color-secondary);
    margin-left: 1.5rem;
}

.setting-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.75rem;
}

.setting-item label {
    color: var(--text-color);
}

/* Loading overlay styles */
.pdf-export-loading .loading-content {
    text-align: center;
    color: var(--text-color);
}

.pdf-export-loading .loading-spinner {
    width: 40px;
    height: 40px;
    border: 4px solid var(--surface-border);
    border-top: 4px solid var(--primary-color);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 1rem;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
</style>