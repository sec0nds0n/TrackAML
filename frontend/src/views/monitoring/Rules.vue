<template>
    <div class="rules-page">
        <RuleManagement />
    </div>
</template>

<script setup>
import RuleManagement from '@/components/monitoring/RuleManagement.vue';

// Example rule configuration for detecting high-value transactions
const highValueRule = {
    name: 'High Value Transaction Alert',
    type: 'transaction_amount',
    severity: 'high',
    category: 'aml',
    description: 'Triggers when transaction amount exceeds $10,000',
    conditions: [
        {
            field: 'transaction.amount',
            operator: 'greater_than',
            value: '10000'
        }
    ],
    actions: [
        {
            type: 'alert',
            message: 'High value transaction detected'
        },
        {
            type: 'email',
            recipients: ['compliance@company.com'],
            message: 'Alert: High value transaction requires review'
        }
    ]
};

// Multiple rapid transactions rule
const rapidTransactionRule = {
    name: 'Rapid Transaction Frequency',
    type: 'frequency',
    severity: 'medium',
    category: 'fraud',
    conditions: [
        {
            field: 'transaction.count',
            operator: 'greater_than',
            value: '5'
        },
        {
            field: 'transaction.timeframe',
            operator: 'less_than',
            value: '300' // 5 minutes
        }
    ],
    logicOperator: 'AND',
    actions: [
        {
            type: 'flag',
            message: 'Account flagged for rapid transactions'
        },
        {
            type: 'escalate',
            escalationLevel: 'L2',
            message: 'Suspicious transaction pattern detected'
        }
    ]
};

// Blacklisted address detection
const blacklistRule = {
    name: 'Blacklisted Address Check',
    type: 'blacklist',
    severity: 'critical',
    category: 'compliance',
    conditions: [
        {
            field: 'transaction.from',
            operator: 'in_list',
            value: 'blacklist_addresses'
        }
    ],
    actions: [
        {
            type: 'block',
            message: 'Transaction blocked - blacklisted address'
        },
        {
            type: 'escalate',
            escalationLevel: 'compliance',
            message: 'Blacklisted address detected'
        }
    ]
};
</script>
