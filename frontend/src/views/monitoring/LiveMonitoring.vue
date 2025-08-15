<template>
    <div class="grid">
        <!-- Header Section -->
        <div class="col-12">
            <div class="card">
                <div class="flex justify-content-between align-items-center">
                    <div>
                        <h5 class="mb-2">SigmaVerde - Real-time Live Monitoring</h5>
                        <p class="text-600 m-0">Monitor your systems and data in real-time with live updates.</p>
                    </div>
                    <div class="flex align-items-center gap-2">
                        <div class="flex align-items-center gap-2">
                            <div class="border-circle w-3rem h-3rem bg-green-100 flex align-items-center justify-content-center">
                                <i class="pi pi-circle-fill text-green-500 animation-pulse"></i>
                            </div>
                            <span class="text-sm font-medium">Live</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Status Cards -->
        <div class="col-12 lg:col-6 xl:col-3">
            <div class="card mb-0 hover-card">
                <div class="flex justify-content-between mb-3">
                    <div>
                        <span class="block text-500 font-medium mb-3">System Status</span>
                        <div class="text-900 font-medium text-xl">{{ systemStatus.status }}</div>
                    </div>
                    <div class="flex align-items-center justify-content-center bg-green-100 border-round" style="width: 2.5rem; height: 2.5rem">
                        <i class="pi pi-check-circle text-green-500 text-xl"></i>
                    </div>
                </div>
                <span class="text-green-500 font-medium">{{ systemStatus.uptime }}</span>
                <span class="text-500"> uptime</span>
            </div>
        </div>

        <div class="col-12 lg:col-6 xl:col-3">
            <div class="card mb-0 hover-card">
                <div class="flex justify-content-between mb-3">
                    <div>
                        <span class="block text-500 font-medium mb-3">Active Users</span>
                        <div class="text-900 font-medium text-xl">{{ metrics.activeUsers.toLocaleString() }}</div>
                    </div>
                    <div class="flex align-items-center justify-content-center bg-blue-100 border-round" style="width: 2.5rem; height: 2.5rem">
                        <i class="pi pi-users text-blue-500 text-xl"></i>
                    </div>
                </div>
                <span class="text-blue-500 font-medium">+{{ metrics.newUsers }}</span>
                <span class="text-500"> new today</span>
            </div>
        </div>

        <div class="col-12 lg:col-6 xl:col-3">
            <div class="card mb-0 hover-card">
                <div class="flex justify-content-between mb-3">
                    <div>
                        <span class="block text-500 font-medium mb-3">CPU Usage</span>
                        <div class="text-900 font-medium text-xl">{{ metrics.cpuUsage }}%</div>
                    </div>
                    <div class="flex align-items-center justify-content-center border-round" 
                         :class="getCpuStatusClass(metrics.cpuUsage)" 
                         style="width: 2.5rem; height: 2.5rem">
                        <i class="pi pi-chart-line text-xl" :class="getCpuIconClass(metrics.cpuUsage)"></i>
                    </div>
                </div>
                <ProgressBar :value="metrics.cpuUsage" :showValue="false" 
                           :class="getCpuProgressClass(metrics.cpuUsage)" 
                           style="height: 8px; border-radius: 4px;"></ProgressBar>
            </div>
        </div>

        <div class="col-12 lg:col-6 xl:col-3">
            <div class="card mb-0 hover-card">
                <div class="flex justify-content-between mb-3">
                    <div>
                        <span class="block text-500 font-medium mb-3">Memory Usage</span>
                        <div class="text-900 font-medium text-xl">{{ metrics.memoryUsage }}%</div>
                    </div>
                    <div class="flex align-items-center justify-content-center border-round" 
                         :class="getMemoryStatusClass(metrics.memoryUsage)" 
                         style="width: 2.5rem; height: 2.5rem">
                        <i class="pi pi-server text-xl" :class="getMemoryIconClass(metrics.memoryUsage)"></i>
                    </div>
                </div>
                <ProgressBar :value="metrics.memoryUsage" :showValue="false" 
                           :class="getMemoryProgressClass(metrics.memoryUsage)" 
                           style="height: 8px; border-radius: 4px;"></ProgressBar>
            </div>
        </div>

        <!-- Real-time Chart -->
        <div class="col-12 xl:col-8">
            <div class="card">
                <div class="flex justify-content-between align-items-center mb-4">
                    <h5 class="m-0">Performance Metrics</h5>
                    <div class="flex align-items-center gap-2">
                        <small class="text-500">Last updated: {{ lastUpdated }}</small>
                        <Button icon="pi pi-refresh" 
                               class="p-button-text p-button-rounded p-button-sm" 
                               @click="forceUpdate"
                               :loading="isUpdating"></Button>
                    </div>
                </div>
                <Chart type="line" :data="chartData" :options="chartOptions" class="chart-container"></Chart>
            </div>
        </div>

        <!-- Live Activity Feed -->
        <div class="col-12 xl:col-4">
            <div class="card">
                <div class="flex justify-content-between align-items-center mb-4">
                    <h5 class="m-0">Live Activity Feed</h5>
                    <Button icon="pi pi-refresh" 
                           class="p-button-text p-button-rounded p-button-sm" 
                           @click="refreshActivity"></Button>
                </div>
                <div class="activity-feed">
                    <div v-for="activity in activities" 
                         :key="activity.id" 
                         class="activity-item flex align-items-start py-3 px-3 border-bottom-1 surface-border">
                        <div class="activity-time text-500 font-medium mr-3" style="min-width: 3rem;">
                            {{ activity.time }}
                        </div>
                        <div class="flex-1">
                            <div class="text-900 mb-1">{{ activity.message }}</div>
                            <Tag :value="activity.type" 
                                 :severity="getActivitySeverity(activity.type)" 
                                 class="text-xs"></Tag>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- System Alerts -->
        <div class="col-12">
            <div class="card">
                <div class="flex justify-content-between align-items-center mb-4">
                    <h5 class="m-0">System Alerts</h5>
                    <div class="flex align-items-center gap-2">
                        <Badge :value="alerts.length" severity="danger" v-if="alerts.length > 0"></Badge>
                        <Button label="Clear All" 
                               icon="pi pi-trash" 
                               class="p-button-outlined p-button-sm" 
                               @click="clearAllAlerts"
                               v-if="alerts.length > 0"></Button>
                    </div>
                </div>
                <DataTable :value="alerts" 
                          responsiveLayout="scroll" 
                          :paginator="true" 
                          :rows="5"
                          class="p-datatable-sm">
                    <Column field="timestamp" header="Time" :sortable="true" style="min-width: 12rem">
                        <template #body="slotProps">
                            <span class="font-medium">{{ formatTime(slotProps.data.timestamp) }}</span>
                        </template>
                    </Column>
                    <Column field="level" header="Level" :sortable="true" style="min-width: 8rem">
                        <template #body="slotProps">
                            <Tag :value="slotProps.data.level" 
                                 :severity="getAlertSeverity(slotProps.data.level)"></Tag>
                        </template>
                    </Column>
                    <Column field="source" header="Source" :sortable="true" style="min-width: 10rem">
                        <template #body="slotProps">
                            <span class="font-medium">{{ slotProps.data.source }}</span>
                        </template>
                    </Column>
                    <Column field="message" header="Message" style="min-width: 20rem"></Column>
                    <Column header="Actions" style="min-width: 8rem">
                        <template #body="slotProps">
                            <div class="flex gap-2">
                                <Button icon="pi pi-eye" 
                                       class="p-button-rounded p-button-text p-button-sm" 
                                       v-tooltip.top="'View Details'"
                                       @click="viewAlert(slotProps.data)"></Button>
                                <Button icon="pi pi-times" 
                                       class="p-button-rounded p-button-text p-button-sm" 
                                       v-tooltip.top="'Dismiss'"
                                       @click="dismissAlert(slotProps.data)"></Button>
                            </div>
                        </template>
                    </Column>
                </DataTable>
            </div>
        </div>
    </div>
</template>

<script setup>
import Badge from 'primevue/badge';
import Button from 'primevue/button';
import Chart from 'primevue/chart';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import ProgressBar from 'primevue/progressbar';
import Tag from 'primevue/tag';
import { computed, onMounted, onUnmounted, ref } from 'vue';

// Reactive data
const systemStatus = ref({
    status: 'Online',
    uptime: '99.9%'
});

const metrics = ref({
    activeUsers: 1247,
    newUsers: 23,
    cpuUsage: 45,
    memoryUsage: 67
});

const chartData = ref({});
const chartOptions = ref({});
const isUpdating = ref(false);

const activities = ref([
    { id: 1, time: '09:30', message: 'User login detected from new location', type: 'INFO' },
    { id: 2, time: '09:28', message: 'Database backup completed successfully', type: 'SUCCESS' },
    { id: 3, time: '09:25', message: 'High CPU usage detected on server-02', type: 'WARNING' },
    { id: 4, time: '09:20', message: 'New user registration: john.doe@example.com', type: 'INFO' },
    { id: 5, time: '09:15', message: 'System update deployed successfully', type: 'SUCCESS' }
]);

const alerts = ref([
    {
        id: 1,
        timestamp: new Date(),
        level: 'WARNING',
        source: 'Server-01',
        message: 'High memory usage detected (85%)'
    },
    {
        id: 2,
        timestamp: new Date(Date.now() - 300000),
        level: 'INFO',
        source: 'Database',
        message: 'Scheduled maintenance completed'
    },
    {
        id: 3,
        timestamp: new Date(Date.now() - 600000),
        level: 'ERROR',
        source: 'API Gateway',
        message: 'Connection timeout to external service'
    }
]);

let updateInterval = null;

// Computed properties
const lastUpdated = computed(() => {
    return new Date().toLocaleTimeString();
});

// Methods
const initChart = () => {
    const documentStyle = getComputedStyle(document.documentElement);
    const textColor = documentStyle.getPropertyValue('--text-color');
    const textColorSecondary = documentStyle.getPropertyValue('--text-color-secondary');
    const surfaceBorder = documentStyle.getPropertyValue('--surface-border');

    chartData.value = {
        labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00'],
        datasets: [
            {
                label: 'CPU Usage',
                data: [12, 19, 25, 32, 45, 38, 42],
                fill: false,
                borderColor: documentStyle.getPropertyValue('--blue-500'),
                backgroundColor: documentStyle.getPropertyValue('--blue-500'),
                tension: 0.4,
                borderWidth: 2
            },
            {
                label: 'Memory Usage',
                data: [28, 48, 40, 67, 58, 72, 65],
                fill: false,
                borderColor: documentStyle.getPropertyValue('--pink-500'),
                backgroundColor: documentStyle.getPropertyValue('--pink-500'),
                tension: 0.4,
                borderWidth: 2
            }
        ]
    };

    chartOptions.value = {
        maintainAspectRatio: false,
        aspectRatio: 0.6,
        plugins: {
            legend: {
                labels: {
                    color: textColor,
                    usePointStyle: true,
                    font: {
                        weight: 700
                    }
                }
            }
        },
        scales: {
            x: {
                ticks: {
                    color: textColorSecondary,
                    font: {
                        weight: 500
                    }
                },
                grid: {
                    color: surfaceBorder,
                    drawBorder: false
                }
            },
            y: {
                ticks: {
                    color: textColorSecondary
                },
                grid: {
                    color: surfaceBorder,
                    drawBorder: false
                }
            }
        }
    };
};

const updateMetrics = () => {
    // Simulate real-time data updates
    metrics.value.cpuUsage = Math.floor(Math.random() * 100);
    metrics.value.memoryUsage = Math.floor(Math.random() * 100);
    metrics.value.activeUsers = 1200 + Math.floor(Math.random() * 100);
    
    // Update chart data
    const newCpuData = chartData.value.datasets[0].data.slice(1);
    newCpuData.push(metrics.value.cpuUsage);
    chartData.value.datasets[0].data = newCpuData;
    
    const newMemoryData = chartData.value.datasets[1].data.slice(1);
    newMemoryData.push(metrics.value.memoryUsage);
    chartData.value.datasets[1].data = newMemoryData;
};

const forceUpdate = async () => {
    isUpdating.value = true;
    await new Promise(resolve => setTimeout(resolve, 1000));
    updateMetrics();
    isUpdating.value = false;
};

const refreshActivity = () => {
    const messages = [
        'System refresh triggered by user',
        'New data synchronization completed',
        'User session timeout detected',
        'Cache cleared successfully',
        'Performance optimization applied'
    ];
    
    const newActivity = {
        id: Date.now(),
        time: new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit' }),
        message: messages[Math.floor(Math.random() * messages.length)],
        type: ['INFO', 'SUCCESS', 'WARNING'][Math.floor(Math.random() * 3)]
    };
    activities.value.unshift(newActivity);
    if (activities.value.length > 10) {
        activities.value.pop();
    }
};

const getCpuStatusClass = (usage) => {
    if (usage >= 80) return 'bg-red-100';
    if (usage >= 60) return 'bg-orange-100';
    return 'bg-green-100';
};

const getCpuIconClass = (usage) => {
    if (usage >= 80) return 'text-red-500';
    if (usage >= 60) return 'text-orange-500';
    return 'text-green-500';
};

const getCpuProgressClass = (usage) => {
    if (usage >= 80) return 'progress-danger';
    if (usage >= 60) return 'progress-warning';
    return 'progress-success';
};

const getMemoryStatusClass = (usage) => {
    if (usage >= 80) return 'bg-red-100';
    if (usage >= 60) return 'bg-purple-100';
    return 'bg-blue-100';
};

const getMemoryIconClass = (usage) => {
    if (usage >= 80) return 'text-red-500';
    if (usage >= 60) return 'text-purple-500';
    return 'text-blue-500';
};

const getMemoryProgressClass = (usage) => {
    if (usage >= 80) return 'progress-danger';
    if (usage >= 60) return 'progress-warning';
    return 'progress-info';
};

const getActivitySeverity = (type) => {
    switch (type) {
        case 'SUCCESS': return 'success';
        case 'WARNING': return 'warning';
        case 'ERROR': return 'danger';
        default: return 'info';
    }
};

const getAlertSeverity = (level) => {
    switch (level) {
        case 'ERROR': return 'danger';
        case 'WARNING': return 'warning';
        case 'INFO': return 'info';
        default: return 'secondary';
    }
};

const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleString();
};

const viewAlert = (alert) => {
    console.log('Viewing alert:', alert);
    // You can implement a dialog or modal here
};

const dismissAlert = (alert) => {
    const index = alerts.value.findIndex(a => a.id === alert.id);
    if (index > -1) {
        alerts.value.splice(index, 1);
    }
};

const clearAllAlerts = () => {
    alerts.value = [];
};

// Lifecycle hooks
onMounted(() => {
    initChart();
    // Start real-time updates every 3 seconds
    updateInterval = setInterval(updateMetrics, 3000);
});

onUnmounted(() => {
    if (updateInterval) {
        clearInterval(updateInterval);
    }
});
</script>

<style scoped>
.card {
    box-shadow: 0 2px 1px -1px rgba(0,0,0,.2), 0 1px 1px 0 rgba(0,0,0,.14), 0 1px 3px 0 rgba(0,0,0,.12);
    transition: all 0.3s ease;
}

.hover-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.12), 0 2px 4px rgba(0,0,0,0.08);
}

.chart-container {
    height: 400px;
}

.activity-feed {
    max-height: 400px;
    overflow-y: auto;
}

.activity-item {
    transition: background-color 0.2s ease;
}

.activity-item:hover {
    background-color: var(--surface-hover);
}

.activity-time {
    font-size: 0.875rem;
}

@keyframes pulse {
    0%, 100% {
        opacity: 1;
    }
    50% {
        opacity: 0.5;
    }
}

.animation-pulse {
    animation: pulse 2s infinite;
}

/* Progress bar custom styles */
:deep(.progress-success .p-progressbar-value) {
    background: linear-gradient(90deg, #10b981, #059669);
}

:deep(.progress-warning .p-progressbar-value) {
    background: linear-gradient(90deg, #f59e0b, #d97706);
}

:deep(.progress-danger .p-progressbar-value) {
    background: linear-gradient(90deg, #ef4444, #dc2626);
}

:deep(.progress-info .p-progressbar-value) {
    background: linear-gradient(90deg, #3b82f6, #2563eb);
}

/* DataTable responsive improvements */
:deep(.p-datatable-sm .p-datatable-tbody > tr > td) {
    padding: 0.75rem;
}

:deep(.p-datatable-sm .p-datatable-thead > tr > th) {
    padding: 0.75rem;
    font-weight: 600;
}

/* Custom scrollbar for activity feed */
.activity-feed::-webkit-scrollbar {
    width: 6px;
}

.activity-feed::-webkit-scrollbar-track {
    background: var(--surface-ground);
    border-radius: 3px;
}

.activity-feed::-webkit-scrollbar-thumb {
    background: var(--surface-border);
    border-radius: 3px;
}

.activity-feed::-webkit-scrollbar-thumb:hover {
    background: var(--text-color-secondary);
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .chart-container {
        height: 300px;
    }
    
    .activity-feed {
        max-height: 300px;
    }
    
    .activity-time {
        min-width: 2.5rem !important;
        font-size: 0.75rem;
    }
}
</style>