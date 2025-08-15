/**
 * Utility functions for cryptocurrency operations
 */

/**
 * Format cryptocurrency amount with proper decimal places
 * @param {number} amount - Amount to format
 * @param {string} currency - Currency code (e.g., 'BTC', 'ETH')
 * @returns {string} Formatted amount
 */
export const formatCryptoAmount = (amount, currency = 'BTC') => {
    const decimals = {
        BTC: 8,
        ETH: 18,
        BSC: 18,
        MATIC: 18,
        SOL: 9,
        ADA: 6
    };

    return amount.toFixed(decimals[currency] || 8);
};

/**
 * Format fiat currency amount
 * @param {number} amount - Amount to format
 * @param {string} currency - Currency code (e.g., 'USD', 'EUR')
 * @returns {string} Formatted amount
 */
export const formatFiatAmount = (amount, currency = 'USD') => {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(amount);
};

/**
 * Truncate blockchain address
 * @param {string} address - Full address
 * @param {number} startChars - Number of characters to show at start
 * @param {number} endChars - Number of characters to show at end
 * @returns {string} Truncated address
 */
export const truncateAddress = (address, startChars = 6, endChars = 4) => {
    if (!address) return '';
    if (address.length <= startChars + endChars) return address;
    return `${address.slice(0, startChars)}...${address.slice(-endChars)}`;
};

/**
 * Calculate risk score based on various factors
 * @param {Object} factors - Risk factors
 * @returns {number} Risk score (0-100)
 */
export const calculateRiskScore = (factors) => {
    const {
        transactionVolume = 0,
        frequency = 0,
        mixerUsage = false,
        knownBadActor = false,
        sanctionedCountry = false,
        privacyCoin = false
    } = factors;

    let score = 0;

    // Volume factor (0-30 points)
    if (transactionVolume > 1000000) score += 30;
    else if (transactionVolume > 100000) score += 20;
    else if (transactionVolume > 10000) score += 10;

    // Frequency factor (0-20 points)
    if (frequency > 100) score += 20;
    else if (frequency > 50) score += 15;
    else if (frequency > 10) score += 10;

    // Risk flags (10 points each)
    if (mixerUsage) score += 10;
    if (knownBadActor) score += 10;
    if (sanctionedCountry) score += 10;
    if (privacyCoin) score += 10;

    return Math.min(score, 100);
};

/**
 * Get risk level based on score
 * @param {number} score - Risk score (0-100)
 * @returns {string} Risk level
 */
export const getRiskLevel = (score) => {
    if (score >= 80) return 'CRITICAL';
    if (score >= 60) return 'HIGH';
    if (score >= 40) return 'MEDIUM';
    return 'LOW';
};

/**
 * Get severity class for risk level
 * @param {string} riskLevel - Risk level
 * @returns {string} Severity class
 */
export const getRiskSeverity = (riskLevel) => {
    switch (riskLevel) {
        case 'CRITICAL': return 'danger';
        case 'HIGH': return 'danger';
        case 'MEDIUM': return 'warning';
        case 'LOW': return 'success';
        default: return 'info';
    }
};

/**
 * Format blockchain timestamp
 * @param {number|string|Date} timestamp - Timestamp to format
 * @param {string} format - Format type ('relative' or 'full')
 * @returns {string} Formatted timestamp
 */
export const formatBlockchainTime = (timestamp, format = 'relative') => {
    const date = new Date(timestamp);
    
    if (format === 'relative') {
        const seconds = Math.floor((new Date() - date) / 1000);
        
        if (seconds < 60) return 'just now';
        if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
        if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
        if (seconds < 2592000) return `${Math.floor(seconds / 86400)}d ago`;
        return date.toLocaleDateString();
    }
    
    return date.toLocaleString();
};

/**
 * Validate blockchain address format
 * @param {string} address - Address to validate
 * @param {string} network - Network/chain (e.g., 'ETH', 'BTC')
 * @returns {boolean} Is valid address
 */
export const isValidAddress = (address, network) => {
    const patterns = {
        ETH: /^0x[a-fA-F0-9]{40}$/,
        BTC: /^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$/,
        BSC: /^0x[a-fA-F0-9]{40}$/,
        MATIC: /^0x[a-fA-F0-9]{40}$/,
        SOL: /^[1-9A-HJ-NP-Za-km-z]{32,44}$/,
        ADA: /^addr1[a-zA-Z0-9]{98}$/
    };

    return patterns[network]?.test(address) || false;
};

/**
 * Get transaction type description
 * @param {Object} transaction - Transaction data
 * @returns {string} Transaction type description
 */
export const getTransactionType = (transaction) => {
    const types = {
        TRANSFER: 'Standard Transfer',
        SMART_CONTRACT: 'Smart Contract Interaction',
        TOKEN_TRANSFER: 'Token Transfer',
        NFT_TRANSFER: 'NFT Transfer',
        EXCHANGE: 'Exchange Transaction',
        MIXING: 'Mixing Service',
        STAKING: 'Staking Operation',
        LENDING: 'DeFi Lending',
        UNKNOWN: 'Unknown Transaction'
    };

    return types[transaction.type] || types.UNKNOWN;
};

/**
 * Calculate transaction fee in USD
 * @param {number} gasUsed - Gas used
 * @param {number} gasPrice - Gas price in wei
 * @param {number} ethPrice - Current ETH price in USD
 * @returns {number} Fee in USD
 */
export const calculateTransactionFee = (gasUsed, gasPrice, ethPrice) => {
    const ethFee = (gasUsed * gasPrice) / 1e18;
    return ethFee * ethPrice;
};

/**
 * Get network explorer URL
 * @param {string} network - Network code
 * @param {string} type - URL type ('address' or 'transaction')
 * @param {string} hash - Address or transaction hash
 * @returns {string} Explorer URL
 */
export const getExplorerUrl = (network, type, hash) => {
    const explorers = {
        ETH: 'https://etherscan.io',
        BTC: 'https://blockchain.com/btc',
        BSC: 'https://bscscan.com',
        MATIC: 'https://polygonscan.com',
        SOL: 'https://solscan.io',
        ADA: 'https://cardanoscan.io'
    };

    const baseUrl = explorers[network];
    if (!baseUrl) return '';

    if (type === 'address') return `${baseUrl}/address/${hash}`;
    if (type === 'transaction') return `${baseUrl}/tx/${hash}`;
    
    return baseUrl;
};
