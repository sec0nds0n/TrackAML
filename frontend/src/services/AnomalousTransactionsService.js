/**
 * Service for handling Anomalous Transactions API calls
 */
class AnomalousTransactionsService {
    constructor() {
        this.baseURL = 'http://203.194.113.33/api';
        this.endpoints = {
            transactions: '/anomalies/transactions'
        };
    }

    /**
     * Fetch anomalous transactions from the API
     * @returns {Promise} Promise object with transactions data
     */
    async getAnomalousTransactions() {
        try {
            const response = await fetch(`${this.baseURL}${this.endpoints.transactions}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return this.transformTransactionData(data);
        } catch (error) {
            console.error('Error fetching anomalous transactions:', error);
            throw new Error(`Failed to fetch anomalous transactions: ${error.message}`);
        }
    }

    /**
     * Transform API data to match component expectations
     * @param {Array} apiData - Raw API data
     * @returns {Array} Transformed data
     */
    transformTransactionData(apiData) {
        return apiData.map(item => ({
            id: item.tx_hash,
            hash: item.tx_hash,
            from: item.sender,
            to: item.receiver,
            amount: item.value,
            timestamp: new Date(item.timestamp),
            network: this.detectNetwork(item.tx_hash),
            riskLevel: this.determineRiskLevel(item.value, item.detector),
            riskScore: this.calculateRiskScore(item.value, item.detector),
            status: 'flagged',
            detector: item.detector,
            reason: item.reason,
            suspiciousFlags: this.generateSuspiciousFlags(item),
            fee: this.estimateFee(item.value),
            blockHeight: this.generateBlockHeight(),
            confirmations: this.generateConfirmations(),
            gasUsed: this.estimateGasUsed(),
            gasPrice: this.estimateGasPrice(),
            
            // Additional computed fields
            formattedAmount: this.formatAmount(item.value),
            timeAgo: this.getTimeAgo(new Date(item.timestamp)),
            addressType: this.determineAddressType(item.sender, item.receiver),
            anomalyScore: this.calculateAnomalyScore(item.detector, item.value)
        }));
    }

    /**
     * Detect network based on transaction hash format
     * @param {string} txHash - Transaction hash
     * @returns {string} Network name
     */
    detectNetwork(txHash) {
        // Ethereum-style hash (0x prefix, 64 hex chars)
        if (txHash.startsWith('0x') && txHash.length === 66) {
            return 'Ethereum';
        }
        return 'Unknown';
    }

    /**
     * Determine risk level based on value and detector
     * @param {number} value - Transaction value
     * @param {string} detector - Detection method
     * @returns {string} Risk level
     */
    determineRiskLevel(value, detector) {
        if (value > 1000) return 'CRITICAL';
        if (value > 100) return 'HIGH';
        if (value > 10) return 'MEDIUM';
        return 'LOW';
    }

    /**
     * Calculate risk score (0-100)
     * @param {number} value - Transaction value
     * @param {string} detector - Detection method
     * @returns {number} Risk score
     */
    calculateRiskScore(value, detector) {
        let baseScore = 50;
        
        // Adjust based on value
        if (value > 1000) baseScore += 40;
        else if (value > 100) baseScore += 30;
        else if (value > 10) baseScore += 20;
        else baseScore += 10;
        
        // Adjust based on detector
        if (detector.includes('isolation_forest')) baseScore += 10;
        
        return Math.min(100, baseScore);
    }

    /**
     * Generate suspicious flags based on transaction data
     * @param {Object} transaction - Transaction data
     * @returns {Array} Array of suspicious flags
     */
    generateSuspiciousFlags(transaction) {
        const flags = [];
        
        if (transaction.value > 1000) {
            flags.push('High Value Transaction');
        }
        
        if (transaction.detector.includes('ml:')) {
            flags.push('ML Anomaly Detection');
        }
        
        if (transaction.detector.includes('isolation_forest')) {
            flags.push('Isolation Forest Alert');
        }
        
        // Check for round numbers (potential structuring)
        if (transaction.value % 1 === 0 && transaction.value > 100) {
            flags.push('Round Amount');
        }
        
        // Check for very small amounts (potential testing)
        if (transaction.value < 0.01) {
            flags.push('Micro Transaction');
        }
        
        return flags;
    }

    /**
     * Estimate transaction fee
     * @param {number} value - Transaction value
     * @returns {number} Estimated fee
     */
    estimateFee(value) {
        // Simple fee estimation (typically 0.1-2% for crypto)
        return value * (0.001 + Math.random() * 0.019);
    }

    /**
     * Generate mock block height
     * @returns {number} Block height
     */
    generateBlockHeight() {
        return Math.floor(Math.random() * 1000000) + 18000000;
    }

    /**
     * Generate mock confirmations
     * @returns {number} Number of confirmations
     */
    generateConfirmations() {
        return Math.floor(Math.random() * 100) + 1;
    }

    /**
     * Estimate gas used
     * @returns {number} Gas used
     */
    estimateGasUsed() {
        return Math.floor(Math.random() * 50000) + 21000;
    }

    /**
     * Estimate gas price in Gwei
     * @returns {number} Gas price
     */
    estimateGasPrice() {
        return Math.floor(Math.random() * 100) + 10;
    }

    /**
     * Format amount for display
     * @param {number} value - Raw value
     * @returns {string} Formatted amount
     */
    formatAmount(value) {
        if (value >= 1000) {
            return `${(value / 1000).toFixed(2)}K ETH`;
        } else if (value >= 1) {
            return `${value.toFixed(4)} ETH`;
        } else {
            return `${(value * 1000).toFixed(2)} mETH`;
        }
    }

    /**
     * Get time ago string
     * @param {Date} date - Transaction date
     * @returns {string} Time ago string
     */
    getTimeAgo(date) {
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 60) {
            return `${diffMins}m ago`;
        } else if (diffHours < 24) {
            return `${diffHours}h ago`;
        } else {
            return `${diffDays}d ago`;
        }
    }

    /**
     * Determine address type
     * @param {string} sender - Sender address
     * @param {string} receiver - Receiver address
     * @returns {string} Address type
     */
    determineAddressType(sender, receiver) {
        // Simple heuristic based on address patterns
        const commonExchanges = ['0xe3c44d4d25172ef2e0cdb9e09189a8ca4ed878f4'];
        
        if (commonExchanges.includes(sender) || commonExchanges.includes(receiver)) {
            return 'Exchange';
        }
        
        return 'Wallet';
    }

    /**
     * Calculate anomaly score
     * @param {string} detector - Detection method
     * @param {number} value - Transaction value
     * @returns {number} Anomaly score
     */
    calculateAnomalyScore(detector, value) {
        let score = 0.5; // Base anomaly score
        
        if (detector.includes('isolation_forest')) {
            score += 0.3;
        }
        
        if (value > 1000) {
            score += 0.2;
        }
        
        return Math.min(1.0, score);
    }

    /**
     * Get real-time transaction updates (WebSocket simulation)
     * @param {Function} callback - Callback function for new transactions
     * @returns {Function} Cleanup function
     */
    subscribeToTransactionUpdates(callback) {
        // Simulate real-time updates by polling the API
        const interval = setInterval(async () => {
            try {
                const transactions = await this.getAnomalousTransactions();
                callback(transactions);
            } catch (error) {
                console.error('Error in transaction updates:', error);
            }
        }, 30000); // Poll every 30 seconds

        // Return cleanup function
        return () => clearInterval(interval);
    }

    /**
     * Export transactions to CSV
     * @param {Array} transactions - Transactions to export
     * @returns {string} CSV data
     */
    exportTransactions(transactions) {
        const headers = [
            'Transaction Hash',
            'From',
            'To',
            'Amount (ETH)',
            'USD Value',
            'Timestamp',
            'Risk Level',
            'Risk Score',
            'Detector',
            'Reason',
            'Network'
        ];

        const csvData = transactions.map(tx => [
            tx.hash,
            tx.from,
            tx.to,
            tx.amount,
            (tx.amount * 2000).toFixed(2), // Assuming $2000 per ETH
            tx.timestamp.toISOString(),
            tx.riskLevel,
            tx.riskScore,
            tx.detector,
            tx.reason,
            tx.network
        ]);

        return [headers, ...csvData]
            .map(row => row.join(','))
            .join('\n');
    }
}

export const anomalousTransactionsService = new AnomalousTransactionsService();
export default AnomalousTransactionsService;