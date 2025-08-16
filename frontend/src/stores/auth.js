import { defineStore } from 'pinia'
import api from '@/services/api' // pastikan services/api mengekspor default; kalau tidak, pakai: import * as api from '@/services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    isAuthenticated: false,
    loading: false,
    error: null,
    initialized: false,
  }),

  getters: {
    role: (s) => s.user?.role || null,
    permissions: (s) => s.user?.permissions || [],
    isAdmin: (s) => s.user?.role === 'admin',
    isL1Analyst: (s) => s.user?.role === 'analyst_L1',
    isL2Analyst: (s) => s.user?.role === 'analyst_L2',
    isExchanger: (s) => s.user?.role === 'Exchanger', // cek huruf besar/kecil sesuai backend
    hasPermission: (s) => (p) => !!s.user?.permissions?.includes(p),
    canRead: (s) => !!s.user?.permissions?.includes('read'),
    canWrite: (s) => !!s.user?.permissions?.includes('write'),
    canApprove: (s) => !!s.user?.permissions?.includes('approve'),
    canManageUsers: (s) => !!s.user?.permissions?.includes('manage_users'),
    userInitials: (s) => {
      const name = s.user?.name || s.user?.username || ''
      return name ? name.split(' ').filter(Boolean).map(w => w[0].toUpperCase()).join('').slice(0, 2) : ''
    },
    isLoggedIn: (s) => s.isAuthenticated
  },

  actions: {
    async initialize() {
      if (this.initialized) return { success: true, user: this.user }
      this.loading = true
      this.error = null
      try {
        const res = await api.me()
        const user = res?.user || null
        this.user = user
        this.isAuthenticated = !!user
        return { success: !!user, user }
      } catch {
        this.user = null
        this.isAuthenticated = false
        this.error = null
        return { success: false }
      } finally {
        this.loading = false
        this.initialized = true
      }
    },

    async login(credentials) {
      if (!credentials?.username || !credentials?.password) {
        throw new Error('Username and password are required')
      }
      this.loading = true
      this.error = null
      try {
        await api.login(credentials)
        api.resetCsrfCache()
        const res = await api.me()
        const user = res?.user || null
        this.user = user
        this.isAuthenticated = !!user
        return { success: !!user, user }
      } catch (e) {
        this.user = null
        this.isAuthenticated = false
        this.error = e?.data?.message || e?.message || 'Login failed'
        throw new Error(this.error)
      } finally {
        this.loading = false
      }
    },

    async logout() {
      this.loading = true
      try { await api.logout() } catch {}
      api.resetCsrfCache()
      this.user = null
      this.isAuthenticated = false
      this.loading = false
      return { success: true }
    },

    clearError() { this.error = null },
    hasRole(role) { return this.user?.role === role },
    hasAnyRole(roles = []) { return roles.length === 0 || roles.includes(this.user?.role) },
    hasAllPermissions(perms = []) {
      const owned = new Set(this.user?.permissions || [])
      return perms.every(p => owned.has(p))
    },
    hasAnyPermission(perms = []) {
      const owned = new Set(this.user?.permissions || [])
      return perms.some(p => owned.has(p))
    },
  }
})