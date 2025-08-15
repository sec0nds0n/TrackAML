import { onMounted, onUnmounted, ref } from 'vue';

export function useCryptoMonitoring() {
    // Reactive state
    const alertSummary = ref({
        highRisk: 23,
        newHighRisk: 5,
        flaggedAddresses: 156,
        newFlagged: 12,
        largeTransactions: 89,
        totalVolume: 15420000,
    });

    const monitoringStats = ref({
        activeNodes: 12,
        networksMonitored: 8
    });

    const networks = ref([
        { name: 'Bitcoin', code: 'BTC' },
        { name: 'Ethereum', code: 'ETH' },
        { name: 'Binance Smart Chain', code: 'BSC' },
        { name: 'Polygon', code: 'MATIC' },
        { name: 'Solana', code: 'SOL' },
        { name: 'Cardano', code: 'ADA' }
    ]);

    const alerts = ref([
        {
            label: 'High Risk Transactions',
            value: '23',
            trend: '+5',
            period: 'in last hour',
            icon: 'pi pi-exclamation-triangle',
            iconBg: 'bg-red-100',
            iconColor: 'text-red-500',
            trendColor: 'text-red-500'
        },
        {
            label: 'Flagged Addresses',
            value: '156',
            trend: '+12',
            period: 'new today',
            icon: 'pi pi-flag',
            iconBg: 'bg-orange-100',
            iconColor: 'text-orange-500',
            trendColor: 'text-orange-500'
        },
        {
            label: 'Large Transactions',
            value: '89',
            trend: '$15.42M',
            period: 'total volume',
            icon: 'pi pi-dollar',
            iconBg: 'bg-blue-100',
            iconColor: 'text-blue-500',
            trendColor: 'text-blue-500'
        },
        {
            label: 'Monitoring Status',
            value: '12',
            trend: '8',
            period: 'networks',
            icon: 'pi pi-eye',
            iconBg: 'bg-green-100',
            iconColor: 'text-green-500',
            trendColor: 'text-green-500'
        }
    ]);

    const selectedNetwork = ref(null);
    const isPaused = ref(false);
    const liveTransactions = ref([]);
    const suspiciousAddresses = ref([]);
    const topRiskIndicators = ref([]);
    const chartTimeframe = ref('24h');

    const timeframeOptions = ref([
        { label: '1H', value: '1h' },
        { label: '24H', value: '24h' },
        { label: '7D', value: '7d' },
        { label: '30D', value: '30d' }
    ]);

    // Chart data
    const riskChartData = ref({
        labels: ['Low Risk', 'Medium Risk', 'High Risk', 'Critical Risk'],
        datasets: [{
            data: [65, 25, 8, 2],
            backgroundColor: [
                '#10b981', // green
                '#f59e0b', // yellow
                '#f97316', // orange
                '#ef4444'  // red
            ]
        }]
    });

    const volumeChartData = ref({
        labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00'],
        datasets: [
            {
                label: 'Transaction Volume ($M)',
                data: [12, 19, 25, 32, 45, 38, 42],
                borderColor: '#3b82f6',
                backgroundColor: '#3b82f6',
                tension: 0.4,
                fill: false
            },
            {
                label: 'Suspicious Transactions',
                data: [2, 3, 5, 8, 12, 9, 7],
                borderColor: '#ef4444',
                backgroundColor: '#ef4444',
                tension: 0.4,
                fill: false
            }
        ]
    });

    // Methods
    const generateMockTransaction = () => {
        const networks = ['BTC', 'ETH', 'BSC', 'MATIC', 'SOL'];
        const riskLevels = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'];
        const suspiciousFlags = [
            'Large Amount',
            'Known Suspicious Address',
            'Rapid Transactions',
            'Mixing Service',
            'Privacy Coin',
            'High-Risk Exchange',
            'Unusual Pattern',
            'Blacklisted Address'
        ];

        const amount = Math.random() * 1000000;
        const riskLevel = riskLevels[Math.floor(Math.random() * riskLevels.length)];
        const flagCount = riskLevel === 'CRITICAL' ? 3 : riskLevel === 'HIGH' ? 2 : riskLevel === 'MEDIUM' ? 1 : 0;
        
        return {
            id: Date.now() + Math.random(),
            hash: '0x' + Math.random().toString(16).substr(2, 64),
            network: networks[Math.floor(Math.random() * networks.length)],
            from: '0x' + Math.random().toString(16).substr(2, 40),
            to: '0x' + Math.random().toString(16).substr(2, 40),
            amount: amount,
            fee: amount * 0.001,
            timestamp: new Date(),
            riskLevel: riskLevel,
            blockHeight: Math.floor(Math.random() * 1000000),
            suspiciousFlags: Array.from({ length: flagCount }, () => 
                suspiciousFlags[Math.floor(Math.random() * suspiciousFlags.length)]
            ).filter((flag, index, arr) => arr.indexOf(flag) === index)
        };
    };

    const addNewTransaction = () => {
        if (!isPaused.value) {
            const newTransaction = generateMockTransaction();
            liveTransactions.value.unshift(newTransaction);
            
            if (liveTransactions.value.length > 20) {
                liveTransactions.value.pop();
            }

            if (newTransaction.riskLevel === 'HIGH' || newTransaction.riskLevel === 'CRITICAL') {
                alertSummary.value.highRisk++;
                alertSummary.value.newHighRisk++;
            }
        }
    };

    const togglePause = () => {
        isPaused.value = !isPaused.value;
    };

    const getTransactionClass = (transaction) => {
        switch (transaction.riskLevel) {
            case 'CRITICAL': return 'critical-risk';
            case 'HIGH': return 'high-risk';
            case 'MEDIUM': return 'medium-risk';
            default: return 'low-risk';
        }
    };

    const getRiskSeverity = (riskLevel) => {
        switch (riskLevel) {
            case 'CRITICAL': return 'danger';
            case 'HIGH': return 'danger';
            case 'MEDIUM': return 'warning';
            case 'LOW': return 'success';
            default: return 'info';
        }
    };

    const getRiskScoreClass = (score) => {
        if (score >= 80) return 'risk-score-critical';
        if (score >= 60) return 'risk-score-high';
        if (score >= 40) return 'risk-score-medium';
        return 'risk-score-low';
    };

    const truncateAddress = (address) => {
        if (!address) return '';
        return `${address.substring(0, 6)}...${address.substring(address.length - 4)}`;
    };

    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(amount);
    };

    const formatTime = (timestamp) => {
        return new Date(timestamp).toLocaleString();
    };

    // Lifecycle hooks
    let transactionInterval;

    onMounted(() => {
        // Generate initial transactions
        for (let i = 0; i < 10; i++) {
            liveTransactions.value.push(generateMockTransaction());
        }

        // Generate suspicious addresses
        suspiciousAddresses.value = Array.from({ length: 50 }, (_, index) => ({
            id: index + 1,
            address: '0x' + Math.random().toString(16).substr(2, 40),
            network: networks.value[Math.floor(Math.random() * networks.value.length)].code,
            riskScore: Math.floor(Math.random() * 100),
            reason: [
                'Connected to known criminal organization',
                'High-frequency trading patterns',
                'Money laundering indicators',
                'Sanctions list match',
                'Unusual transaction patterns',
                'Connected to darknet markets'
            ][Math.floor(Math.random() * 6)],
            lastActivity: new Date(Date.now() - Math.random() * 86400000 * 30),
            transactionCount: Math.floor(Math.random() * 10000)
        }));

        // Generate risk indicators
        topRiskIndicators.value = [
            { type: 'Large Transactions', description: 'Transactions over $100K', count: 45 },
            { type: 'Rapid Fire', description: 'Multiple transactions in short time', count: 32 },
            { type: 'Mixing Services', description: 'Transactions through mixers', count: 28 },
            { type: 'Blacklisted Addresses', description: 'Known suspicious addresses', count: 19 },
            { type: 'Privacy Coins', description: 'Anonymous cryptocurrency usage', count: 15 }
        ];

        // Add new transaction every 3-5 seconds
        transactionInterval = setInterval(addNewTransaction, Math.random() * 2000 + 3000);
    });

    onUnmounted(() => {
        if (transactionInterval) {
            clearInterval(transactionInterval);
        }
    });

    return {
        // State
        alertSummary,
        monitoringStats,
        networks,
        alerts,
        selectedNetwork,
        isPaused,
        liveTransactions,
        suspiciousAddresses,
        topRiskIndicators,
        chartTimeframe,
        timeframeOptions,
        riskChartData,
        volumeChartData,

        // Methods
        togglePause,
        getTransactionClass,
        getRiskSeverity,
        getRiskScoreClass,
        truncateAddress,
        formatCurrency,
        formatTime
    };
}
