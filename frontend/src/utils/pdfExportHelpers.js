import { EXPORT_VALIDATION, PDF_EXPORT_CONFIG } from '@/config/pdfExportConfig';

export class PDFExportHelpers {
    static validateExportEnvironment() {
        const issues = [];
        
        // Check browser compatibility
        if (!window.jsPDF) {
            issues.push('jsPDF library not loaded');
        }
        
        if (!window.html2canvas) {
            issues.push('html2canvas library not loaded');
        }
        
        // Check viewport size
        if (window.innerWidth < EXPORT_VALIDATION.requirements.minWidth) {
            issues.push('Viewport width too small for optimal export');
        }
        
        // Check available memory (rough estimate)
        if (navigator.deviceMemory && navigator.deviceMemory < 2) {
            issues.push('Low device memory may affect export quality');
        }
        
        return {
            isValid: issues.length === 0,
            issues
        };
    }
    
    static formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    static generateFileName(caseData, options = {}) {
        const config = PDF_EXPORT_CONFIG.naming;
        const now = new Date();
        
        const replacements = {
            caseId: caseData?.id || 'UNKNOWN',
            date: now.toISOString().split('T')[0],
            time: now.toTimeString().split(' ')[0].replace(/:/g, '-'),
            timestamp: now.getTime(),
            type: options.type || 'executive-summary'
        };
        
        let fileName = config.pattern;
        Object.entries(replacements).forEach(([key, value]) => {
            fileName = fileName.replace(`{${key}}`, value);
        });
        
        // Sanitize filename
        fileName = fileName.replace(/[^a-zA-Z0-9._-]/g, '_');
        
        // Ensure .pdf extension
        if (!fileName.endsWith('.pdf')) {
            fileName += '.pdf';
        }
        
        // Truncate if too long
        if (fileName.length > config.maxLength) {
            const extension = '.pdf';
            const maxBase = config.maxLength - extension.length;
            fileName = fileName.substring(0, maxBase) + extension;
        }
        
        return fileName;
    }
    
    static createExportProgress(onProgress) {
        let currentStep = 0;
        const steps = [
            { name: 'Initializing', weight: 5 },
            { name: 'Preparing content', weight: 15 },
            { name: 'Capturing elements', weight: 40 },
            { name: 'Generating PDF', weight: 30 },
            { name: 'Finalizing', weight: 10 }
        ];
        
        const totalWeight = steps.reduce((sum, step) => sum + step.weight, 0);
        let completedWeight = 0;
        
        return {
            nextStep(stepName) {
                if (currentStep < steps.length) {
                    completedWeight += steps[currentStep].weight;
                    currentStep++;
                }
                
                const progress = Math.min((completedWeight / totalWeight) * 100, 100);
                
                if (onProgress) {
                    onProgress({
                        step: currentStep,
                        totalSteps: steps.length,
                        stepName: stepName || (steps[currentStep] ? steps[currentStep].name : 'Complete'),
                        progress: Math.round(progress)
                    });
                }
                
                return progress;
            },
            
            complete() {
                currentStep = steps.length;
                completedWeight = totalWeight;
                
                if (onProgress) {
                    onProgress({
                        step: steps.length,
                        totalSteps: steps.length,
                        stepName: 'Complete',
                        progress: 100
                    });
                }
            }
        };
    }
    
    static async measureExportTime(exportFunction) {
        const startTime = performance.now();
        
        try {
            const result = await exportFunction();
            const endTime = performance.now();
            const duration = endTime - startTime;
            
            return {
                ...result,
                performance: {
                    duration: Math.round(duration),
                    durationFormatted: this.formatDuration(duration)
                }
            };
        } catch (error) {
            const endTime = performance.now();
            const duration = endTime - startTime;
            
            throw {
                ...error,
                performance: {
                    duration: Math.round(duration),
                    durationFormatted: this.formatDuration(duration)
                }
            };
        }
    }
    
    static formatDuration(milliseconds) {
        if (milliseconds < 1000) {
            return `${Math.round(milliseconds)}ms`;
        } else if (milliseconds < 60000) {
            return `${(milliseconds / 1000).toFixed(1)}s`;
        } else {
            const minutes = Math.floor(milliseconds / 60000);
            const seconds = Math.floor((milliseconds % 60000) / 1000);
            return `${minutes}m ${seconds}s`;
        }
    }
    
    static createExportNotification(type, options = {}) {
        const notifications = {
            start: {
                severity: 'info',
                summary: 'Export Started',
                detail: 'Generating PDF report...',
                life: 3000,
                icon: 'pi pi-spin pi-spinner'
            },
            progress: {
                severity: 'info',
                summary: 'Export Progress',
                detail: `${options.stepName} (${options.progress}%)`,
                life: 2000,
                icon: 'pi pi-clock'
            },
            success: {
                severity: 'success',
                summary: 'Export Successful',
                detail: `PDF saved as: ${options.filename}`,
                life: 5000,
                icon: 'pi pi-check-circle'
            },
            warning: {
                severity: 'warn',
                summary: 'Export Warning',
                detail: options.message || 'Export completed with warnings',
                life: 4000,
                icon: 'pi pi-exclamation-triangle'
            },
            error: {
                severity: 'error',
                summary: 'Export Failed',
                detail: options.message || 'An error occurred while generating the PDF',
                life: 6000,
                icon: 'pi pi-times-circle'
            }
        };
        
        return notifications[type] || notifications.error;
    }
    
    static async optimizeForExport(element) {
        const optimizations = [];
        
        // Store original styles
        const originalStyles = new Map();
        
        // Find all elements that need optimization
        const elementsToOptimize = element.querySelectorAll('*');
        
        elementsToOptimize.forEach(el => {
            const computedStyle = window.getComputedStyle(el);
            
            // Store original styles
            originalStyles.set(el, {
                transform: el.style.transform,
                transition: el.style.transition,
                animation: el.style.animation,
                filter: el.style.filter,
                opacity: el.style.opacity
            });
            
            // Apply optimizations
            if (computedStyle.transform !== 'none') {
                el.style.transform = 'none';
                optimizations.push({ element: el, type: 'transform' });
            }
            
            if (computedStyle.transition !== 'none') {
                el.style.transition = 'none';
                optimizations.push({ element: el, type: 'transition' });
            }
            
            if (computedStyle.animation !== 'none') {
                el.style.animation = 'none';
                optimizations.push({ element: el, type: 'animation' });
            }
            
            // Ensure high contrast for PDF
            if (computedStyle.color === 'rgba(0, 0, 0, 0)' || computedStyle.color === 'transparent') {
                el.style.color = '#000000';
                optimizations.push({ element: el, type: 'color' });
            }
        });
        
        // Wait for layout to stabilize
        await new Promise(resolve => requestAnimationFrame(resolve));
        
        return {
            originalStyles,
            optimizations,
            restore() {
                originalStyles.forEach((styles, el) => {
                    Object.assign(el.style, styles);
                });
            }
        };
    }
    
    static detectBrowserCapabilities() {
        const capabilities = {
            html2canvas: typeof html2canvas !== 'undefined',
            jsPDF: typeof jsPDF !== 'undefined',
            webGL: !!window.WebGLRenderingContext,
            canvas: !!document.createElement('canvas').getContext,
            fileAPI: !!(window.File && window.FileReader && window.FileList && window.Blob),
            downloadAPI: 'download' in document.createElement('a'),
            clipboardAPI: !!navigator.clipboard,
            shareAPI: !!navigator.share,
            performanceAPI: !!window.performance,
            intersectionObserver: !!window.IntersectionObserver
        };
        
        const score = Object.values(capabilities).filter(Boolean).length;
        const maxScore = Object.keys(capabilities).length;
        
        return {
            ...capabilities,
            score,
            maxScore,
            percentage: Math.round((score / maxScore) * 100),
            isOptimal: score >= maxScore * 0.8
        };
    }
    
    static createExportMetrics() {
        const startTime = performance.now();
        const startMemory = performance.memory ? performance.memory.usedJSHeapSize : null;
        
        return {
            start: {
                time: startTime,
                memory: startMemory,
                timestamp: new Date().toISOString()
            },
            
            finish() {
                const endTime = performance.now();
                const endMemory = performance.memory ? performance.memory.usedJSHeapSize : null;
                
                return {
                    duration: endTime - startTime,
                    memoryDelta: endMemory && startMemory ? endMemory - startMemory : null,
                    timestamp: new Date().toISOString(),
                    performance: {
                        duration: Math.round(endTime - startTime),
                        durationFormatted: PDFExportHelpers.formatDuration(endTime - startTime),
                        memoryUsed: endMemory && startMemory ? 
                            PDFExportHelpers.formatFileSize(Math.abs(endMemory - startMemory)) : 'Unknown'
                    }
                };
            }
        };
    }
    
    static async preloadImages(element) {
        const images = element.querySelectorAll('img');
        const imagePromises = Array.from(images).map(img => {
            return new Promise((resolve) => {
                if (img.complete) {
                    resolve();
                } else {
                    const timeout = setTimeout(() => {
                        resolve(); // Resolve anyway after timeout
                    }, 5000);
                    
                    img.onload = () => {
                        clearTimeout(timeout);
                        resolve();
                    };
                    
                    img.onerror = () => {
                        clearTimeout(timeout);
                        resolve(); // Resolve even on error
                    };
                }
            });
        });
        
        await Promise.all(imagePromises);
        
        // Additional wait for layout stabilization
        await new Promise(resolve => setTimeout(resolve, 100));
    }
}

// Export error types for better error handling
export class PDFExportError extends Error {
    constructor(message, type = 'UNKNOWN', details = {}) {
        super(message);
        this.name = 'PDFExportError';
        this.type = type;
        this.details = details;
        this.timestamp = new Date().toISOString();
    }
}

export const PDF_ERROR_TYPES = {
    BROWSER_UNSUPPORTED: 'BROWSER_UNSUPPORTED',
    LIBRARY_MISSING: 'LIBRARY_MISSING',
    ELEMENT_NOT_FOUND: 'ELEMENT_NOT_FOUND',
    CAPTURE_FAILED: 'CAPTURE_FAILED',
    PDF_GENERATION_FAILED: 'PDF_GENERATION_FAILED',
    FILE_TOO_LARGE: 'FILE_TOO_LARGE',
    TIMEOUT: 'TIMEOUT',
    MEMORY_EXCEEDED: 'MEMORY_EXCEEDED',
    NETWORK_ERROR: 'NETWORK_ERROR'
};

// Utility functions for common export tasks
export const exportUtils = {
    async waitForFonts() {
        if (document.fonts && document.fonts.ready) {
            await document.fonts.ready;
        }
        return new Promise(resolve => setTimeout(resolve, 100));
    },
    
    async waitForImages(container) {
        return PDFExportHelpers.preloadImages(container);
    },
    
    async stabilizeLayout(element) {
        // Force reflow
        element.offsetHeight;
        
        // Wait for any pending animations
        await new Promise(resolve => requestAnimationFrame(resolve));
        await new Promise(resolve => requestAnimationFrame(resolve));
        
        return true;
    },
    
    createProgressTracker(onUpdate) {
        let progress = 0;
        const steps = [];
        
        return {
            addStep(name, weight = 1) {
                steps.push({ name, weight, completed: false });
            },
            
            completeStep(name) {
                const step = steps.find(s => s.name === name);
                if (step && !step.completed) {
                    step.completed = true;
                    this.updateProgress();
                }
            },
            
            updateProgress() {
                const totalWeight = steps.reduce((sum, step) => sum + step.weight, 0);
                const completedWeight = steps
                    .filter(step => step.completed)
                    .reduce((sum, step) => sum + step.weight, 0);
                
                progress = totalWeight > 0 ? (completedWeight / totalWeight) * 100 : 0;
                
                if (onUpdate) {
                    onUpdate({
                        progress: Math.round(progress),
                        currentStep: steps.find(s => !s.completed)?.name || 'Complete',
                        completedSteps: steps.filter(s => s.completed).length,
                        totalSteps: steps.length
                    });
                }
                
                return progress;
            },
            
            getProgress() {
                return progress;
            }
        };
    }
};