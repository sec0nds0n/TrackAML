import api from './api'
export const getAnomalySummary = () => api.request('/api/anomalies/summary')

export const getHighRiskCount   = () => api.request('/api/risk/high-risk-addresses/count');
export const getWalletRiskDistribution = () =>
  api.request('/api/risk/wallets/distribution');

export const getActiveCasesCount = () => api.request('/api/cases/active-count')
export const getUrgentCasesCount = () => api.request('/api/cases/urgent-count')
export const getRecentCases = (limit = 10) => api.request('/api/cases/recent?limit=${limit}')

export const getComplianceScore  = () => api.request('/api/compliance/score')

export const getAlerts = (limit = 20) => api.request('/api/alerts?limit=${limit}');

export const getRegulatoryUpdates = () => api.request('/api/regulatory/updates')


