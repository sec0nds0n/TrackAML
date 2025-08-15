import { useAuthStore } from '@/stores/auth'

function redirectToLogin(to, next) {
  next({ path: '/auth/login', query: { redirect: to.fullPath || to.path } })
}

async function ensureInitialized(auth) {
  try { if (!auth.initialized) await auth.initialize() } catch {}
}

// Require authenticated session
export const requireAuth = async (to, from, next) => {
  const auth = useAuthStore()
  await ensureInitialized(auth)
  if (!auth.isAuthenticated) return redirectToLogin(to, next)
  return next()
}

// Require ANY of allowed roles
export const requireRole = (allowedRoles = []) => async (to, from, next) => {
  const auth = useAuthStore()
  await ensureInitialized(auth)
  if (!auth.isAuthenticated) return redirectToLogin(to, next)
  return auth.hasAnyRole(allowedRoles) ? next() : next('/auth/access')
}

// Require ALL permissions
export const requirePermission = (requiredPermissions = []) => async (to, from, next) => {
  const auth = useAuthStore()
  await ensureInitialized(auth)
  if (!auth.isAuthenticated) return redirectToLogin(to, next)
  return auth.hasAllPermissions(requiredPermissions) ? next() : next('/auth/access')
}

// Require ANY permission
export const requireAnyPermission = (permissions = []) => async (to, from, next) => {
  const auth = useAuthStore()
  await ensureInitialized(auth)
  if (!auth.isAuthenticated) return redirectToLogin(to, next)
  return auth.hasAnyPermission(permissions) ? next() : next('/auth/access')
}

// Pass if ANY role OR ANY permission
export const requireRoleOrPermission = (allowedRoles = [], requiredPermissions = []) => async (to, from, next) => {
  const auth = useAuthStore()
  await ensureInitialized(auth)
  if (!auth.isAuthenticated) return redirectToLogin(to, next)
  const ok = auth.hasAnyRole(allowedRoles) || auth.hasAnyPermission(requiredPermissions)
  return ok ? next() : next('/auth/access')
}