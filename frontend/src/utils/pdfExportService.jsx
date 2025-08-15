import jsPDF from 'jspdf';

export class PDFExportService {
    constructor() {
        this.doc = null;
        this.pageWidth = 210; // A4 width in mm
        this.pageHeight = 297; // A4 height in mm
        this.margin = 20;
        this.currentY = this.margin;
        this.lineHeight = 7;
    }

    async exportExecutiveSummary(caseData, summaryData) {
        this.doc = new jsPDF();
        this.currentY = this.margin;

        try {
            // Add header
            this.addHeader(caseData);
            
            // Add executive summary content
            this.addKeyMetrics(summaryData);
            this.addCaseOverview(caseData, summaryData);
            this.addRiskAssessment(summaryData);
            this.addKeyFindings(summaryData);
            this.addRecommendations(summaryData);
            this.addComplianceStatus(summaryData);
            
            // Add footer
            this.addFooter();
            
            // Generate filename
            const filename = this.generateFilename(caseData);
            
            // Save the PDF
            this.doc.save(filename);
            
            return { success: true, filename };
        } catch (error) {
            console.error('Error generating PDF:', error);
            return { success: false, error: error.message };
        }
    }

    addHeader(caseData) {
        // Company logo area (placeholder)
        this.doc.setFillColor(41, 128, 185);
        this.doc.rect(this.margin, this.currentY, 170, 25, 'F');
        
        // Title
        this.doc.setTextColor(255, 255, 255);
        this.doc.setFontSize(20);
        this.doc.setFont('helvetica', 'bold');
        this.doc.text('EXECUTIVE SUMMARY', this.margin + 5, this.currentY + 10);
        
        // Subtitle
        this.doc.setFontSize(12);
        this.doc.setFont('helvetica', 'normal');
        this.doc.text('Comprehensive Case Analysis and Risk Assessment', this.margin + 5, this.currentY + 18);
        
        this.currentY += 35;
        
        // Case information header
        this.doc.setTextColor(0, 0, 0);
        this.doc.setFontSize(14);
        this.doc.setFont('helvetica', 'bold');
        this.doc.text('Case Information', this.margin, this.currentY);
        this.currentY += 10;
        
        // Case details
        this.doc.setFontSize(10);
        this.doc.setFont('helvetica', 'normal');
        this.doc.text(`Case ID: ${caseData?.id || 'N/A'}`, this.margin, this.currentY);
        this.doc.text(`Status: ${caseData?.status || 'N/A'}`, this.margin + 80, this.currentY);
        this.currentY += 6;
        
        this.doc.text(`Generated: ${new Date().toLocaleDateString()}`, this.margin, this.currentY);
        this.doc.text(`Time: ${new Date().toLocaleTimeString()}`, this.margin + 80, this.currentY);
        this.currentY += 15;
        
        // Add separator line
        this.doc.setDrawColor(200, 200, 200);
        this.doc.line(this.margin, this.currentY, this.pageWidth - this.margin, this.currentY);
        this.currentY += 10;
    }

    addKeyMetrics(summaryData) {
        this.addSectionTitle('Key Metrics');
        
        // Create metrics grid
        const metrics = [
            { label: 'Risk Score', value: `${summaryData.riskScore}/100`, color: this.getRiskColor(summaryData.riskScore) },
            { label: 'Confidence Level', value: `${summaryData.confidenceLevel}%`, color: [52, 152, 219] },
            { label: 'Financial Impact', value: `$${this.formatAmount(summaryData.financialImpact)}`, color: [231, 76, 60] },
            { label: 'Est. Resolution', value: `${summaryData.timeToResolution} days`, color: [155, 89, 182] }
        ];
        
        const boxWidth = 40;
        const boxHeight = 20;
        const spacing = 5;
        
        metrics.forEach((metric, index) => {
            const x = this.margin + (index * (boxWidth + spacing));
            
            // Draw metric box
            this.doc.setFillColor(...metric.color);
            this.doc.rect(x, this.currentY, boxWidth, boxHeight, 'F');
            
            // Add metric value
            this.doc.setTextColor(255, 255, 255);
            this.doc.setFontSize(12);
            this.doc.setFont('helvetica', 'bold');
            this.doc.text(metric.value, x + 2, this.currentY + 8);
            
            // Add metric label
            this.doc.setTextColor(0, 0, 0);
            this.doc.setFontSize(8);
            this.doc.setFont('helvetica', 'normal');
            this.doc.text(metric.label, x + 2, this.currentY + 15);
        });
        
        this.currentY += 30;
    }

    addCaseOverview(caseData, summaryData) {
        this.addSectionTitle('Case Overview');
        
        const overviewData = [
            { label: 'Case Type', value: summaryData.caseType },
            { label: 'Detection Method', value: summaryData.detectionMethod },
            { label: 'Jurisdiction', value: summaryData.jurisdiction },
            { label: 'Regulatory Impact', value: summaryData.regulatoryImpact }
        ];
        
        this.doc.setFontSize(10);
        overviewData.forEach(item => {
            this.doc.setFont('helvetica', 'bold');
            this.doc.text(`${item.label}:`, this.margin, this.currentY);
            this.doc.setFont('helvetica', 'normal');
            this.doc.text(item.value, this.margin + 40, this.currentY);
            this.currentY += 6;
        });
        
        // Add description
        if (caseData?.details?.description) {
            this.currentY += 5;
            this.doc.setFont('helvetica', 'bold');
            this.doc.text('Description:', this.margin, this.currentY);
            this.currentY += 6;
            
            this.doc.setFont('helvetica', 'normal');
            const description = this.doc.splitTextToSize(caseData.details.description, 150);
            this.doc.text(description, this.margin, this.currentY);
            this.currentY += description.length * 5;
        }
        
        this.currentY += 10;
    }

    addRiskAssessment(summaryData) {
        this.addSectionTitle('Risk Assessment');
        
        // Risk level indicator
        this.doc.setFontSize(12);
        this.doc.setFont('helvetica', 'bold');
        this.doc.text(`Risk Level: ${summaryData.caseData?.riskLevel || 'Medium'} Risk`, this.margin, this.currentY);
        this.currentY += 10;
        
        // Risk factors
        this.doc.setFontSize(10);
        this.doc.setFont('helvetica', 'bold');
        this.doc.text('Risk Factors:', this.margin, this.currentY);
        this.currentY += 8;
        
        summaryData.riskFactors.forEach(factor => {
            this.doc.setFont('helvetica', 'bold');
            this.doc.text(`• ${factor.name}:`, this.margin + 5, this.currentY);
            this.doc.text(`${factor.score}/10`, this.margin + 120, this.currentY);
            this.currentY += 5;
            
            this.doc.setFont('helvetica', 'normal');
            const description = this.doc.splitTextToSize(factor.description, 140);
            this.doc.text(description, this.margin + 10, this.currentY);
            this.currentY += description.length * 4 + 3;
        });
        
        this.currentY += 5;
    }

    addKeyFindings(summaryData) {
        this.checkPageBreak(40);
        this.addSectionTitle('Key Findings');
        
        summaryData.keyFindings.forEach((finding, index) => {
            this.checkPageBreak(25);
            
            // Priority indicator
            const priorityColor = this.getPriorityColor(finding.priority);
            this.doc.setFillColor(...priorityColor);
            this.doc.circle(this.margin + 3, this.currentY + 2, 2, 'F');
            
            // Finding title
            this.doc.setFontSize(11);
            this.doc.setFont('helvetica', 'bold');
            this.doc.text(`${index + 1}. ${finding.title}`, this.margin + 8, this.currentY + 3);
            this.currentY += 7;
            
            // Finding description
            this.doc.setFontSize(9);
            this.doc.setFont('helvetica', 'normal');
            const description = this.doc.splitTextToSize(finding.description, 150);
            this.doc.text(description, this.margin + 8, this.currentY);
            this.currentY += description.length * 4;
            
            // Tags
            if (finding.tags && finding.tags.length > 0) {
                this.doc.setFontSize(8);
                this.doc.setTextColor(100, 100, 100);
                this.doc.text(`Tags: ${finding.tags.join(', ')}`, this.margin + 8, this.currentY + 3);
                this.currentY += 6;
            }
            
            this.doc.setTextColor(0, 0, 0);
            this.currentY += 5;
        });
    }

    addRecommendations(summaryData) {
        this.checkPageBreak(40);
        this.addSectionTitle('Recommendations');
        
        summaryData.recommendations.forEach((rec, index) => {
            this.checkPageBreak(30);
            
            // Priority and timeline
            this.doc.setFontSize(10);
            this.doc.setFont('helvetica', 'bold');
            this.doc.text(`${index + 1}. ${rec.title}`, this.margin, this.currentY);
            
            this.doc.setFontSize(8);
            this.doc.setTextColor(200, 0, 0);
            this.doc.text(`[${rec.priority} Priority]`, this.margin + 120, this.currentY);
            this.doc.setTextColor(0, 0, 200);
            this.doc.text(`Timeline: ${rec.timeline}`, this.margin + 150, this.currentY);
            this.currentY += 7;
            
            // Description
            this.doc.setTextColor(0, 0, 0);
            this.doc.setFontSize(9);
            this.doc.setFont('helvetica', 'normal');
            const description = this.doc.splitTextToSize(rec.description, 160);
            this.doc.text(description, this.margin + 5, this.currentY);
            this.currentY += description.length * 4;
            
            // Impact
            this.doc.setFontSize(8);
            this.doc.setFont('helvetica', 'italic');
            this.doc.setTextColor(0, 150, 0);
            this.doc.text(`Expected Impact: ${rec.impact}`, this.margin + 5, this.currentY + 3);
            this.currentY += 10;
            
            this.doc.setTextColor(0, 0, 0);
        });
    }

    addComplianceStatus(summaryData) {
        this.checkPageBreak(40);
        this.addSectionTitle('Compliance Status');
        
        // Overall compliance score
        this.doc.setFontSize(12);
        this.doc.setFont('helvetica', 'bold');
        this.doc.text(`Overall Compliance Score: ${summaryData.complianceScore}%`, this.margin, this.currentY);
        this.currentY += 10;
        
        // Compliance items
        summaryData.complianceItems.forEach(item => {
            this.checkPageBreak(20);
            
            // Status indicator
            const statusColor = this.getComplianceStatusColor(item.status);
            this.doc.setFillColor(...statusColor);
            this.doc.circle(this.margin + 3, this.currentY + 2, 2, 'F');
            
            // Regulation name
            this.doc.setFontSize(10);
            this.doc.setFont('helvetica', 'bold');
            this.doc.text(item.regulation, this.margin + 8, this.currentY + 3);
            
            // Status
            this.doc.setFontSize(8);
            this.doc.setTextColor(...statusColor);
            this.doc.text(`[${item.status.toUpperCase()}]`, this.margin + 120, this.currentY + 3);
            this.currentY += 7;
            
            // Description
            this.doc.setTextColor(0, 0, 0);
            this.doc.setFontSize(9);
            this.doc.setFont('helvetica', 'normal');
            this.doc.text(item.description, this.margin + 8, this.currentY);
            this.currentY += 5;
            
            // Requirements
            if (item.requirements && item.requirements.length > 0) {
                this.doc.setFontSize(8);
                this.doc.setTextColor(100, 100, 100);
                this.doc.text(`Requirements: ${item.requirements.join(', ')}`, this.margin + 8, this.currentY);
                this.currentY += 6;
            }
            
            this.doc.setTextColor(0, 0, 0);
            this.currentY += 3;
        });
    }

    addSectionTitle(title) {
        this.checkPageBreak(15);
        
        this.doc.setFillColor(240, 240, 240);
        this.doc.rect(this.margin, this.currentY - 2, this.pageWidth - (2 * this.margin), 10, 'F');
        
        this.doc.setTextColor(0, 0, 0);
        this.doc.setFontSize(12);
        this.doc.setFont('helvetica', 'bold');
        this.doc.text(title, this.margin + 2, this.currentY + 5);
        this.currentY += 15;
    }

    addFooter() {
        const pageCount = this.doc.internal.getNumberOfPages();
        
        for (let i = 1; i <= pageCount; i++) {
            this.doc.setPage(i);
            
            // Footer line
            this.doc.setDrawColor(200, 200, 200);
            this.doc.line(this.margin, this.pageHeight - 15, this.pageWidth - this.margin, this.pageHeight - 15);
            
            // Footer text
            this.doc.setFontSize(8);
            this.doc.setFont('helvetica', 'normal');
            this.doc.setTextColor(100, 100, 100);
            
            // Left side - confidentiality notice
            this.doc.text('CONFIDENTIAL - Executive Summary Report', this.margin, this.pageHeight - 8);
            
            // Right side - page number
            this.doc.text(`Page ${i} of ${pageCount}`, this.pageWidth - this.margin - 20, this.pageHeight - 8);
            
            // Center - generation timestamp
            const timestamp = new Date().toLocaleString();
            this.doc.text(`Generated: ${timestamp}`, this.pageWidth / 2 - 25, this.pageHeight - 8);
        }
    }

    checkPageBreak(requiredSpace) {
        if (this.currentY + requiredSpace > this.pageHeight - 30) {
            this.doc.addPage();
            this.currentY = this.margin;
        }
    }

    generateFilename(caseData) {
        const date = new Date().toISOString().split('T')[0];
        const caseId = caseData?.id || 'UNKNOWN';
        return `Executive_Summary_${caseId}_${date}.pdf`;
    }

    formatAmount(amount) {
        return new Intl.NumberFormat('en-US').format(amount);
    }

    getRiskColor(score) {
        if (score >= 80) return [231, 76, 60]; // Red
        if (score >= 60) return [243, 156, 18]; // Orange
        if (score >= 40) return [241, 196, 15]; // Yellow
        return [46, 204, 113]; // Green
    }

    getPriorityColor(priority) {
        switch (priority.toLowerCase()) {
            case 'high': return [231, 76, 60];
            case 'medium': return [243, 156, 18];
            case 'low': return [46, 204, 113];
            default: return [149, 165, 166];
        }
    }

    getComplianceStatusColor(status) {
        switch (status.toLowerCase()) {
            case 'compliant': return [46, 204, 113];
            case 'pending': return [243, 156, 18];
            case 'non-compliant': return [231, 76, 60];
            default: return [149, 165, 166];
        }
    }
}

// Export singleton instance
export const pdfExportService = new PDFExportService();
