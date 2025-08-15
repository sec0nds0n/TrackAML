export const mockAlerts = [
  {
    id: 'alert-001',
    type: 'critical',
    title: 'Suspicious Large Transaction Detected',
    description: 'Unusual outbound transaction of 15.7 BTC detected from wallet address 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
    crypto: 'BTC',
    amount: '15.7 BTC (~$678,450)',
    time: '2 min ago',
    timestamp: new Date(Date.now() - 2 * 60 * 1000),
    severity: 95,
    walletAddress: '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
    transactionHash: '000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f'
  },
  {
    id: 'alert-002',
    type: 'critical',
    title: 'Multiple Failed Login Attempts',
    description: 'Over 50 failed login attempts detected from IP 192.168.1.100 in the last 5 minutes',
    crypto: 'ETH',
    amount: 'Account: trading-main',
    time: '5 min ago',
    timestamp: new Date(Date.now() - 5 * 60 * 1000),
    severity: 90,
    ipAddress: '192.168.1.100',
    attemptCount: 53
  },
  {
    id: 'alert-003',
    type: 'high',
    title: 'Price Volatility Alert',
    description: 'Bitcoin price dropped 8.5% in the last hour, triggering stop-loss protocols',
    crypto: 'BTC',
    amount: 'Portfolio Impact: -$12,340',
    time: '12 min ago',
    timestamp: new Date(Date.now() - 12 * 60 * 1000),
    severity: 75,
    priceChange: -8.5,
    currentPrice: '$43,250'
  },
  {
    id: 'alert-004',
    type: 'high',
    title: 'Wallet Connection from New Device',
    description: 'MetaMask wallet connected from unrecognized device in London, UK',
    crypto: 'ETH',
    amount: 'Wallet: 0x742d...4f2e',
    time: '18 min ago',
    timestamp: new Date(Date.now() - 18 * 60 * 1000),
    severity: 80,
    location: 'London, UK',
    deviceInfo: 'Chrome 120.0 on Windows 11'
  },
  {
    id: 'alert-005',
    type: 'medium',
    title: 'API Rate Limit Exceeded',
    description: 'Trading bot exceeded API rate limits on Binance exchange',
    crypto: 'BTC',
    amount: 'Bot: arbitrage-v2',
    time: '25 min ago',
    timestamp: new Date(Date.now() - 25 * 60 * 1000),
    severity: 60,
    exchange: 'Binance',
    botName: 'arbitrage-v2'
  },
  {
    id: 'alert-006',
    type: 'critical',
    title: 'Smart Contract Vulnerability',
    description: 'Potential reentrancy attack detected on DeFi protocol contract',
    crypto: 'ETH',
    amount: 'At Risk: 245.8 ETH',
    time: '32 min ago',
    timestamp: new Date(Date.now() - 32 * 60 * 1000),
    severity: 98,
    contractAddress: '0x1f9840a85d5af5bf1d1762f925bdaddc4201f984',
    protocol: 'UniswapV3'
  },
  {
    id: 'alert-007',
    type: 'high',
    title: 'Unusual Trading Pattern',
    description: 'Detected coordinated buying activity across multiple exchanges',
    crypto: 'ETH',
    amount: 'Volume: 1,250 ETH',
    time: '45 min ago',
    timestamp: new Date(Date.now() - 45 * 60 * 1000),
    severity: 78,
    exchanges: ['Binance', 'Coinbase', 'Kraken'],
    pattern: 'Coordinated Buy'
  },
  {
    id: 'alert-008',
    type: 'medium',
    title: 'Network Congestion Alert',
    description: 'Ethereum network experiencing high gas fees and slow confirmations',
    crypto: 'ETH',
    amount: 'Gas Price: 85 Gwei',
    time: '1 hour ago',
    timestamp: new Date(Date.now() - 60 * 60 * 1000),
    severity: 55,
    gasPrice: 85,
    avgConfirmTime: '12 minutes'
  },
  {
    id: 'alert-009',
    type: 'medium',
    title: 'Portfolio Rebalancing Required',
    description: 'Asset allocation drifted beyond target thresholds',
    crypto: 'BTC',
    amount: 'Drift: +3.2% BTC allocation',
    time: '1.5 hours ago',
    timestamp: new Date(Date.now() - 90 * 60 * 1000),
    severity: 50,
    targetAllocation: '60% BTC, 30% ETH, 10% Others',
    currentAllocation: '63.2% BTC, 28.1% ETH, 8.7% Others'
  },
  {
    id: 'alert-010',
    type: 'high',
    title: 'Phishing Attempt Detected',
    description: 'Email phishing attempt targeting crypto wallet credentials',
    crypto: 'BTC',
    amount: 'Target: admin@company.com',
    time: '2 hours ago',
    timestamp: new Date(Date.now() - 120 * 60 * 1000),
    severity: 85,
    senderEmail: 'support@coinbase-security.net',
    targetEmail: 'admin@company.com'
  }
];

// Helper functions for generating dynamic data
export const generateRandomAlert = () => {
  const types = ['critical', 'high', 'medium'];
  const cryptos = ['BTC', 'ETH', 'ADA', 'DOT', 'LINK'];
  const titles = [
    'Suspicious Transaction Detected',
    'Price Alert Triggered',
    'Security Breach Attempt',
    'Wallet Activity Warning',
    'Network Anomaly Detected',
    'Trading Bot Malfunction',
    'API Limit Exceeded',
    'Smart Contract Alert'
  ];
  
  const type = types[Math.floor(Math.random() * types.length)];
  const crypto = cryptos[Math.floor(Math.random() * cryptos.length)];
  const title = titles[Math.floor(Math.random() * titles.length)];
  
  return {
    id: `alert-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    type,
    title,
    description: `Generated alert for ${crypto} - ${title.toLowerCase()}`,
    crypto,
    amount: `${(Math.random() * 100).toFixed(2)} ${crypto}`,
    time: `${Math.floor(Math.random() * 60)} min ago`,
    timestamp: new Date(Date.now() - Math.random() * 3600000),
    severity: Math.floor(Math.random() * 100)
  };
};

// Real-time alert categories
export const alertCategories = {
  security: [
    'Suspicious Transaction',
    'Failed Login Attempts',
    'New Device Connection',
    'Phishing Attempt',
    'API Breach'
  ],
  trading: [
    'Price Volatility',
    'Stop Loss Triggered',
    'Portfolio Rebalancing',
    'Trading Bot Error',
    'Order Execution Failed'
  ],
  technical: [
    'Network Congestion',
    'Smart Contract Issue',
    'API Rate Limit',
    'System Maintenance',
    'Connection Timeout'
  ],
  compliance: [
    'KYC Verification Required',
    'Transaction Limit Exceeded',
    'Regulatory Alert',
    'Tax Reporting Due',
    'Account Verification'
  ]
};

// Severity levels with colors and descriptions
export const severityLevels = {
  critical: {
    level: 'critical',
    color: 'red',
    threshold: 80,
    description: 'Immediate action required',
    icon: '🚨'
  },
  high: {
    level: 'high',
    color: 'orange',
    threshold: 60,
    description: 'Action required soon',
    icon: '⚠️'
  },
  medium: {
    level: 'medium',
    color: 'yellow',
    threshold: 40,
    description: 'Monitor closely',
    icon: '⚡'
  },
  low: {
    level: 'low',
    color: 'blue',
    threshold: 20,
    description: 'Informational',
    icon: 'ℹ️'
  }
};

export default mockAlerts;