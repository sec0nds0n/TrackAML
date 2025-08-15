/**
 * Service for handling AML Case related API calls
 */
class AMLCaseService {
    constructor() {
        this.baseURL = 'http://203.194.113.33/api';
        this.endpoints = {
            anomalies: '/aml-cases/anomalies'
        };
    }

    /**
     * Fetch anomalies from the API
     * @returns {Promise} Promise object with anomalies data
     */
    async getAnomalies() {
        try {
            const response = await fetch(`${this.baseURL}${this.endpoints.anomalies}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    // Add any authentication headers if needed
                    // 'Authorization': `Bearer ${token}`
                },
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return this.transformAnomaliesData(data);
        } catch (error) {
            console.error('Error fetching anomalies:', error);
            throw new Error(`Failed to fetch anomalies: ${error.message}`);
        }
    }

    /**
     * Transform API data to match component expectations
     * @param {Array} apiData - Raw API data
     * @returns {Array} Transformed data
     */
    transformAnomaliesData(apiData) {
        return apiData.map(item => ({
            id: item.case_id,
            title: `${item.crypto} Transaction Alert`,
            description: `Suspicious ${item.crypto} transaction detected from wallet ${item.wallet}`,
            level: this.determineLevel(item.risk),
            status: this.mapStatus(item.status),
            priority: this.mapPriority(item.risk),
            assignedTo: this.assignCase(item.risk),
            createdAt: new Date(item.date),
            updatedAt: new Date(item.date),
            dueDate: this.calculateDueDate(new Date(item.date), item.risk),
            createdBy: 'System',
            
            // Additional fields from API
            wallet: item.wallet,
            entityType: item.entity_type,
            crypto: item.crypto,
            amount: item.amount,
            risk: item.risk,
            originalStatus: item.status,
            
            // Mock additional data that might be needed
            documents: this.generateMockDocuments(item.case_id),
            activities: this.generateMockActivities(item.case_id, item.date),
            notes: [],
            stakeholders: this.generateMockStakeholders(item.risk)
        }));
    }

    /**
     * Determine case level based on risk
     * @param {string} risk - Risk level from API
     * @returns {string} Case level
     */
    determineLevel(risk) {
        switch (risk.toLowerCase()) {
            case 'high':
                return 'L2';
            case 'medium':
                return 'L1';
            case 'low':
                return 'L1';
            default:
                return 'L1';
        }
    }

    /**
     * Map API status to component status
     * @param {string} apiStatus - Status from API
     * @returns {string} Mapped status
     */
    mapStatus(apiStatus) {
        const statusMap = {
            'Under Review': 'in_review',
            'New': 'new',
            'Pending': 'pending_docs',
            'Approved': 'approved',
            'Rejected': 'rejected',
            'Escalated': 'escalated'
        };
        return statusMap[apiStatus] || 'new';
    }

    /**
     * Map risk to priority
     * @param {string} risk - Risk level from API
     * @returns {string} Priority level
     */
    mapPriority(risk) {
        switch (risk.toLowerCase()) {
            case 'high':
                return 'high';
            case 'medium':
                return 'medium';
            case 'low':
                return 'low';
            default:
                return 'medium';
        }
    }

    /**
     * Auto-assign cases based on risk level
     * @param {string} risk - Risk level
     * @returns {string} Assigned analyst
     */
    assignCase(risk) {
        const analysts = {
            high: ['Senior Analyst', 'Lead Investigator', 'Compliance Manager'],
            medium: ['AML Analyst', 'Junior Investigator', 'Compliance Officer'],
            low: ['Junior Analyst', 'Trainee Investigator']
        };
        
        const riskLevel = risk.toLowerCase();
        const availableAnalysts = analysts[riskLevel] || analysts.medium;
        return availableAnalysts[Math.floor(Math.random() * availableAnalysts.length)];
    }

    /**
     * Calculate due date based on risk level
     * @param {Date} createdDate - Case creation date
     * @param {string} risk - Risk level
     * @returns {Date} Due date
     */
    calculateDueDate(createdDate, risk) {
        const daysToAdd = {
            'High': 1,    // 1 day for high risk
            'Medium': 3,  // 3 days for medium risk
            'Low': 7      // 7 days for low risk
        };
        
        const days = daysToAdd[risk] || 3;
        const dueDate = new Date(createdDate);
        dueDate.setDate(dueDate.getDate() + days);
        return dueDate;
    }

    /**
     * Generate mock documents for a case
     * @param {string} caseId - Case ID
     * @returns {Array} Mock documents
     */
    generateMockDocuments(caseId) {
        return [
            {
                id: `doc-${caseId}-1`,
                name: 'Transaction Evidence',
                type: 'Blockchain Data',
                status: 'pending_review',
                uploadedBy: 'System',
                uploadedAt: new Date()
            },
            {
                id: `doc-${caseId}-2`,
                name: 'Wallet Analysis',
                type: 'Investigation Report',
                status: 'approved',
                uploadedBy: 'AML Analyst',
                uploadedAt: new Date()
            }
        ];
    }

    /**
     * Generate mock activities for a case
     * @param {string} caseId - Case ID
     * @param {string} date - Case date
     * @returns {Array} Mock activities
     */
    generateMockActivities(caseId, date) {
        return [
            {
                id: `activity-${caseId}-1`,
                timestamp: new Date(date),
                action: 'Case Created',
                user: 'System',
                comment: 'Anomaly detected by monitoring system'
            },
            {
                id: `activity-${caseId}-2`,
                timestamp: new Date(),
                action: 'Initial Review',
                user: 'AML Analyst',
                comment: 'Case assigned for preliminary investigation'
            }
        ];
    }

    /**
     * Generate mock stakeholders based on risk level
     * @param {string} risk - Risk level
     * @returns {Array} Mock stakeholders
     */
    generateMockStakeholders(risk) {
        const baseStakeholders = [
            {
                id: 'stakeholder-1',
                name: 'AML Compliance Officer',
                role: 'Primary Reviewer',
                notificationStatus: 'sent'
            }
        ];

        if (risk === 'High') {
            baseStakeholders.push({
                id: 'stakeholder-2',
                name: 'Senior Compliance Manager',
                role: 'Escalation Contact',
                notificationStatus: 'pending'
            });
        }

        return baseStakeholders;
    }

    /**
     * Update case status (mock implementation)
     * @param {string} caseId - Case ID
     * @param {Object} updates - Updates to apply
     * @returns {Promise} Promise with update result
     */
    async updateCase(caseId, updates) {
        // TODO: Implement actual API call when endpoint is available
        console.log(`Updating case ${caseId}:`, updates);
        return Promise.resolve({ success: true });
    }

    /**
     * Export cases data
     * @param {Array} cases - Cases to export
     * @returns {string} CSV data
     */
    exportCases(cases) {
        const headers = [
            'Case ID',
            'Wallet',
            'Crypto',
            'Amount',
            'Risk',
            'Status',
            'Date',
            'Assigned To'
        ];

        const csvData = cases.map(case_ => [
            case_.id,
            case_.wallet,
            case_.crypto,
            case_.amount,
            case_.risk,
            case_.originalStatus,
            case_.createdAt.toISOString().split('T')[0],
            case_.assignedTo
        ]);

        return [headers, ...csvData]
            .map(row => row.join(','))
            .join('\n');
    }
}

// export const amlCaseService = new AMLCaseService();
export const amlCaseService = {
  // ...method lain
  async getCaseById(id) {
    const res = await fetch(`/api/cases/${encodeURIComponent(id)}`);
    if (!res.ok) throw new Error(`Failed to fetch case ${id}`);
    return await res.json();
  }
};
export default AMLCaseService;