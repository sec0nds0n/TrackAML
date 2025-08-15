import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

export function useAuth() {
  const authStore = useAuthStore()

  // Reactive computed properties
  const isAuthenticated = computed(() => authStore.isAuthenticated)
  const user = computed(() => authStore.user)
  const loading = computed(() => authStore.loading)
  const error = computed(() => authStore.error)
  const token = computed(() => authStore.token)
  const role = computed(() => authStore.role)
  const permissions = computed(() => authStore.permissions)

  // Auth methods
  const login = async (credentials) => {
    try {
      const result = await authStore.login(credentials)
      console.log('Login completed in composable:', result)
      return result
    } catch (error) {
      console.error('Login failed in composable:', error)
      throw error
    }
  }

  const logout = async () => {
    try {
      return await authStore.logout()
    } catch (error) {
      console.error('Logout failed in composable:', error)
      throw error
    }
  }

  const initialize = async () => {
    try {
      return await authStore.initialize()
    } catch (error) {
      console.error('Auth initialization failed in composable:', error)
      throw error
    }
  }

  // Permission helpers
  const hasRole = (role) => authStore.hasRole(role)
  const hasAnyRole = (roles) => authStore.hasAnyRole(roles)
  const hasPermission = (permission) => authStore.hasPermission(permission)
  const hasAllPermissions = (permissions) => authStore.hasAllPermissions(permissions)
  const hasAnyPermission = (permissions) => authStore.hasAnyPermission(permissions)

  return {
    // State
    isAuthenticated,
    user,
    loading,
    error,
    token,
    role,
    permissions,
    
    // Methods
    login,
    logout,
    initialize,
    
    // Helpers
    hasRole,
    hasAnyRole,
    hasPermission,
    hasAllPermissions,
    hasAnyPermission,
    
    // Store instance (for advanced usage)
    authStore
  }
}