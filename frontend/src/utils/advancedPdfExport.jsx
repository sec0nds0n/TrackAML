import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';

export class AdvancedPDFExport {
    constructor() {
        this.options = {
            html2canvas: {
                scale: 2,
                useCORS: true,
                allowTaint: true,
                backgroundColor: '#ffffff',
                logging: false,
                width: 1200,
                height: null
            },
            jsPDF: {
                unit: 'mm',
                format: 'a4',
                orientation: 'portrait'
            }
        };
    }

    async exportElementToPDF(element, filename, options = {}) {
        try {
            const mergedOptions = { ...this.options, ...options };
            
            // Show loading state
            this.showLoadingState(element);
            
            // Prepare element for capture
            this.prepareElementForCapture(element);
            
            // Capture the element
            const canvas = await html2canvas(element, mergedOptions.html2canvas);
            
            // Create PDF
            const pdf = new jsPDF(mergedOptions.jsPDF);
            const imgData = canvas.toDataURL('image/png');
            
            // Calculate dimensions
            const pdfWidth = pdf.internal.pageSize.getWidth();
            const pdfHeight = pdf.internal.pageSize.getHeight();
            const imgWidth = canvas.width;
            const imgHeight = canvas.height;
            
            // Calculate scaling
            const ratio = Math.min(pdfWidth / imgWidth, pdfHeight / imgHeight);
            const scaledWidth = imgWidth * ratio;
            const scaledHeight = imgHeight * ratio;
            
            // Center the image
            const x = (pdfWidth - scaledWidth) / 2;
            const y = (pdfHeight - scaledHeight) / 2;
            
            // Add image to PDF
            pdf.addImage(imgData, 'PNG', x, y, scaledWidth, scaledHeight);
            
            // Add metadata
            this.addPDFMetadata(pdf, filename);
            
            // Save PDF
            pdf.save(filename);
            
            // Restore element
            this.restoreElementAfterCapture(element);
            
            return { success: true, filename };
        } catch (error) {
            console.error('Error exporting to PDF:', error);
            this.restoreElementAfterCapture(element);
            return { success: false, error: error.message };
        }
    }

    async exportExecutiveSummaryComplete(summaryElement, caseData) {
        const filename = this.generateFilename(caseData);
        
        // Custom options for executive summary
        const options = {
            html2canvas: {
                ...this.options.html2canvas,
                height: summaryElement.scrollHeight,
                windowWidth: 1200,
                windowHeight: summaryElement.scrollHeight
            }
        };
        
        return await this.exportElementToPDF(summaryElement, filename, options);
    }

    prepareElementForCapture(element) {
        // Store original styles
        this.originalStyles = new Map();
        
        // Optimize for PDF capture
        const elementsToOptimize = element.querySelectorAll('*');
        elementsToOptimize.forEach(el => {
            this.originalStyles.set(el, {
                transform: el.style.transform,
                transition: el.style.transition,
                animation: el.style.animation
            });
            
            // Disable animations and transitions
            el.style.transition = 'none';
            el.style.animation = 'none';
            el.style.transform = 'none';
        });
        
        // Ensure all images are loaded
        const images = element.querySelectorAll('img');
        return Promise.all(Array.from(images).map(img => {
            if (img.complete) return Promise.resolve();
            return new Promise(resolve => {
                img.onload = resolve;
                img.onerror = resolve;
            });
        }));
    }

    restoreElementAfterCapture(element) {
        if (!this.originalStyles) return;
        
        // Restore original styles
        this.originalStyles.forEach((styles, el) => {
            Object.assign(el.style, styles);
        });
        
        this.originalStyles.clear();
        
        // Hide loading state
        this.hideLoadingState(element);
    }

    showLoadingState(element) {
        // Add loading overlay
        const overlay = document.createElement('div');
        overlay.className = 'pdf-export-loading';
        overlay.innerHTML = `
            <div class="loading-content">
                <div class="loading-spinner"></div>
                <p>Generating PDF...</p>
            </div>
        `;
        overlay.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(255, 255, 255, 0.9);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
        `;
        
        element.style.position = 'relative';
        element.appendChild(overlay);
    }

    hideLoadingState(element) {
        const overlay = element.querySelector('.pdf-export-loading');
        if (overlay) {
            overlay.remove();
        }
    }

    addPDFMetadata(pdf, filename) {
        pdf.setProperties({
            title: 'Executive Summary Report',
            subject: 'Case Analysis and Risk Assessment',
            author: 'SigmaVerde Compliance System',
            creator: 'SigmaVerde PDF Export Service',
            producer: 'SigmaVerde',
            creationDate: new Date(),
            keywords: 'compliance, risk assessment, executive summary, case analysis'
        });
    }

    generateFilename(caseData) {
        const date = new Date().toISOString().split('T')[0];
        const time = new Date().toTimeString().split(' ')[0].replace(/:/g, '-');
        const caseId = caseData?.id || 'CASE';
        return `Executive_Summary_${caseId}_${date}_${time}.pdf`;
    }
}

export const advancedPdfExport = new AdvancedPDFExport();