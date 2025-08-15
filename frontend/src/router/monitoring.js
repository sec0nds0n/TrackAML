export default [
    {
        path: '/monitoring',
        name: 'monitoring',
        redirect: '/monitoring/live'
    },
    {
        path: '/monitoring/live',
        name: 'live-monitoring',
        component: () => import('@/views/monitoring/LiveMonitoring.vue'),
        meta: {
            title: 'Live Monitoring',
            requiresAuth: true,
            permissions: ['monitoring.view']
        }
    },
    {
        path: '/monitoring/alerts',
        name: 'alerts-management',
        component: () => import('@/views/monitoring/AlertsManagement.vue'),
        meta: {
            title: 'Alerts Management',
            requiresAuth: true,
            permissions: ['alerts.view']
        }
    },
    {
        path: '/monitoring/reports',
        name: 'monitoring-reports',
        component: () => import('@/views/monitoring/MonitoringReports.vue'),
        meta: {
            title: 'Monitoring Reports',
            requiresAuth: true,
            permissions: ['reports.view']
        }
    },
    {
        path: '/monitoring/configuration',
        name: 'system-configuration',
        component: () => import('@/views/monitoring/SystemConfiguration.vue'),
        meta: {
            title: 'System Configuration',
            requiresAuth: true,
            permissions: ['system.configure']
        }
    }
];