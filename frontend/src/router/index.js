import AppLayout from '@/layout/AppLayout.vue';
import { requireAuth, requirePermission, requireRole } from '@/middleware/auth';
import { createRouter, createWebHistory } from 'vue-router';


const router = createRouter({
    history: createWebHistory(),
    routes: [ 
        {
            path: '/',
            component: AppLayout,
            children: [
                {
                    path: '/',
                    name: 'dashboard',
                    component: () => import('@/views/Dashboard1.vue'),
                    beforeEnter: requireAuth
                },
                {
                    path: '/dashboard',
                    name: 'dashboard1',
                    component: () => import('@/views/Dashboard1.vue'),
                    beforeEnter: requireAuth
                },
                {
                    path: '/search',
                    name: 'search',
                    component: () => import('@/views/Search.vue')
                },
                {
                    path: '/monitoring/live',
                    name: 'live-monitoring',
                    component: () => import('@/views/monitoring/LiveMonitoring.vue'),
                    beforeEnter: requirePermission(['read'])
                },
                {
                    path: '/monitoring/crypto',
                    name: 'crypto-monitoring',
                    component: () => import('@/views/monitoring/CryptoMonitoring.vue'),
                    beforeEnter: requirePermission(['read'])
                },
                {
                    path: '/monitoring/cases',
                    name: 'case-management',
                    component: () => import('@/views/monitoring/CaseManagement.vue'),
                    beforeEnter: requireRole(['analyst_L1', 'analyst_L2', 'admin'])
                },
                {
                    path: '/monitoring/cases/:id',
                    name: 'case-detail',
                    component: () => import('@/views/monitoring/CaseDetail.vue'),
                    beforeEnter: requireRole(['analyst_L1', 'analyst_L2', 'admin'])
                },
                {
                    path: '/monitoring/rules',
                    name: 'rules',
                    component: () => import('@/views/monitoring/Rules.vue'),
                    beforeEnter: requireRole(['L2', 'admin'])
                },
                {
                    path: '/monitoring/reports',
                    name: 'reports',
                    component: () => import('@/views/monitoring/ExecutiveReports.vue'),
                    beforeEnter: requireRole(['analyst_L1', 'analyst_L2', 'admin'])
                },
                {
                    path: '/wallet/:address',
                    name: 'wallet-detail',
                    component: () => import('@/views/WalletDetail.vue'),
                    beforeEnter: requirePermission(['read'])
                },
                {
                    path: '/uikit/panel',
                    name: 'panel',
                    component: () => import('@/views/uikit/PanelsDoc.vue')
                },

                {
                    path: '/uikit/overlay',
                    name: 'overlay',
                    component: () => import('@/views/uikit/OverlayDoc.vue')
                },
                {
                    path: '/uikit/media',
                    name: 'media',
                    component: () => import('@/views/uikit/MediaDoc.vue')
                },
                {
                    path: '/uikit/message',
                    name: 'message',
                    component: () => import('@/views/uikit/MessagesDoc.vue')
                },
                {
                    path: '/uikit/file',
                    name: 'file',
                    component: () => import('@/views/uikit/FileDoc.vue')
                },
                {
                    path: '/uikit/menu',
                    name: 'menu',
                    component: () => import('@/views/uikit/MenuDoc.vue')
                },
                {
                    path: '/uikit/charts',
                    name: 'charts',
                    component: () => import('@/views/uikit/ChartDoc.vue')
                },
                {
                    path: '/uikit/misc',
                    name: 'misc',
                    component: () => import('@/views/uikit/MiscDoc.vue')
                },
                {
                    path: '/uikit/timeline',
                    name: 'timeline',
                    component: () => import('@/views/uikit/TimelineDoc.vue')
                },
                {
                    path: '/pages/empty',
                    name: 'empty',
                    component: () => import('@/views/pages/Empty.vue')
                },
                {
                    path: '/pages/crud',
                    name: 'crud',
                    component: () => import('@/views/pages/Crud.vue')
                },
                {
                    path: '/documentation',
                    name: 'documentation',
                    component: () => import('@/views/pages/Documentation.vue')
                },
                {
                    path: '/profile',
                    name: 'profile',
                    component: () => import('@/views/UserProfile.vue'),
                    beforeEnter: requireAuth
                },
                {
                    path: '/exchanger/create-case',
                    name: 'exchanger-create-case',
                    component: () => import('@/views/exchanger/ExchangerCaseCreation.vue'),
                    beforeEnter: requireRole(['Exchanger', 'admin'])
                },
                { path: '/monitoring/detail/:id', name: 'CaseDetail', component: () => import('@/views/monitoring/CaseDetail.vue') },
                { path: '/cases', redirect: '/monitoring/cases' },
                { path: '/cases/:id', redirect: to => `/monitoring/cases/${to.params.id}` },
            ]
        },
        {
            path: '/landing',
            name: 'landing',
            component: () => import('@/views/pages/Landing.vue')
        },
        {
            path: '/pages/notfound',
            name: 'notfound',
            component: () => import('@/views/pages/NotFound.vue')
        },

        {
            path: '/auth/login',
            name: 'login',
            component: () => import('@/views/pages/auth/Login.vue')
        },
        {
            path: '/auth/access',
            name: 'accessDenied',
            component: () => import('@/components/auth/AccessDenied.vue')
        },
        {
            path: '/auth/error',
            name: 'error',
            component: () => import('@/views/pages/auth/Error.vue')
        },
        {
            path: '/rbac-demo',
            name: 'rbac-demo',
            component: () => import('@/views/RBACDemo.vue')
        },
        {
            path: '/logout',
            name: 'logout',
            beforeEnter: async (to, from, next) => {
                const { useAuthStore } = await import('@/stores/auth');
                const authStore = useAuthStore();
                await authStore.logout();
                next('/auth/login');
            }
        }
    ]
});

// Global navigation guard
router.beforeEach(async (to, from, next) => {
    // Use the store inside the guard function
    const { useAuthStore } = await import('@/stores/auth');
    const authStore = useAuthStore();
    next()
});

export default router;
