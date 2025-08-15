import { generateRandomAlert, mockAlerts } from '@/data/alertsData.js';
import { computed, onMounted, onUnmounted, ref } from 'vue';

export function useAlerts() {
  const alerts = ref([...mockAlerts]);
  const isLoading = ref(false);
  const error = ref(null);
  const autoRefresh = ref(true);
  const refreshInterval = ref(null);

  // Computed properties
  const criticalAlerts = computed(() => 
    alerts.value.filter(alert => alert.type === 'critical')
  );

  const highAlerts = computed(() => 
    alerts.value.filter(alert => alert.type === 'high')
  );

  const mediumAlerts = computed(() => 
    alerts.value.filter(alert => alert.type === 'medium')
  );

  const alertCounts = computed(() => ({
    total: alerts.value.length,
    critical: criticalAlerts.value.length,
    high: highAlerts.value.length,
    medium: mediumAlerts.value.length
  }));

  const sortedAlerts = computed(() => {
    return [...alerts.value].sort((a, b) => {
      // Sort by severity first, then by timestamp
      const severityOrder = { critical: 3, high: 2, medium: 1 };
      const severityDiff = severityOrder[b.type] - severityOrder[a.type];
      
      if (severityDiff !== 0) return severityDiff;
      
      return new Date(b.timestamp) - new Date(a.timestamp);
    });
  });

  // Methods
  const addAlert = (alert) => {
    const newAlert = {
      ...alert,
      id: alert.id || `alert-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      timestamp: alert.timestamp || new Date(),
      time: alert.time || 'Just now'
    };
    
    alerts.value.unshift(newAlert);
    
    // Limit to 50 alerts max
    if (alerts.value.length > 50) {
      alerts.value = alerts.value.slice(0, 50);
    }
  };

  const removeAlert = (alertId) => {
    const index = alerts.value.findIndex(alert => alert.id === alertId);
    if (index > -1) {
      alerts.value.splice(index, 1);
    }
  };

  const dismissAlert = (alertId) => {
    removeAlert(alertId);
  };

  const clearAllAlerts = () => {
    alerts.value = [];
  };

  const markAsRead = (alertId) => {
    const alert = alerts.value.find(a => a.id === alertId);
    if (alert) {
      alert.read = true;
    }
  };

  const markAllAsRead = () => {
    alerts.value.forEach(alert => {
      alert.read = true;
    });
  };

  const refreshAlerts = async () => {
    isLoading.value = true;
    error.value = null;
    
    try {
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // In a real app, this would be an API call
      // const response = await fetch('/api/alerts');
      // const newAlerts = await response.json();
      
      // For demo, we'll add a random alert occasionally
      if (Math.random() > 0.7) {
        const newAlert = generateRandomAlert();
        addAlert(newAlert);
      }
      
    } catch (err) {
      error.value = err.message;
    } finally {
      isLoading.value = false;
    }
  };

  const startAutoRefresh = (intervalMs = 30000) => {
    if (refreshInterval.value) {
      clearInterval(refreshInterval.value);
    }
    
    refreshInterval.value = setInterval(() => {
      if (autoRefresh.value) {
        refreshAlerts();
      }
    }, intervalMs);
  };

  const stopAutoRefresh = () => {
    if (refreshInterval.value) {
      clearInterval(refreshInterval.value);
      refreshInterval.value = null;
    }
  };

  const toggleAutoRefresh = () => {
    autoRefresh.value = !autoRefresh.value;
    
    if (autoRefresh.value) {
      startAutoRefresh();
    } else {
      stopAutoRefresh();
    }
  };

  // Simulate real-time alerts
  const simulateRealTimeAlert = () => {
    const newAlert = generateRandomAlert();
    addAlert(newAlert);
  };

  // Lifecycle
  onMounted(() => {
    startAutoRefresh();
    
    // Simulate receiving alerts every 45 seconds
    const simulationInterval = setInterval(() => {
      if (Math.random() > 0.6) {
        simulateRealTimeAlert();
      }
    }, 45000);
    
    // Store interval for cleanup
    refreshInterval.simulation = simulationInterval;
  });

  onUnmounted(() => {
    stopAutoRefresh();
    if (refreshInterval.simulation) {
      clearInterval(refreshInterval.simulation);
    }
  });

  return {
    // State
    alerts: sortedAlerts,
    isLoading,
    error,
    autoRefresh,
    
    // Computed
    criticalAlerts,
    highAlerts,
    mediumAlerts,
    alertCounts,
    
    // Methods
    addAlert,
    removeAlert,
    dismissAlert,
    clearAllAlerts,
    markAsRead,
    markAllAsRead,
    refreshAlerts,
    toggleAutoRefresh,
    simulateRealTimeAlert
  };
}