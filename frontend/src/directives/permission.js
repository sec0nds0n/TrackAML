import { useAuthStore } from '@/stores/auth';

export const vPermission = {
    mounted(el, binding) {
        const authStore = useAuthStore();
        const { value } = binding;

        if (value) {
            // Handle array of permissions (any permission required)
            if (Array.isArray(value)) {
                const hasPermission = value.some(permission => 
                    authStore.hasPermission(permission)
                );
                if (!hasPermission) {
                    el.style.display = 'none';
                }
            }
            // Handle single permission
            else if (!authStore.hasPermission(value)) {
                el.style.display = 'none';
            }
        }
    }
};

export const vRole = {
    mounted(el, binding) {
        const authStore = useAuthStore();
        const { value } = binding;

        if (value) {
            // Handle array of roles (any role required)
            if (Array.isArray(value)) {
                const hasRole = value.some(role => 
                    authStore.hasRole(role)
                );
                if (!hasRole) {
                    el.style.display = 'none';
                }
            }
            // Handle single role
            else if (!authStore.hasRole(value)) {
                el.style.display = 'none';
            }
        }
    }
};

// Register directives globally
export default {
    install(app) {
        app.directive('permission', vPermission);
        app.directive('role', vRole);
    }
};

// Usage examples:
// v-permission="'read'"                    // Single permission
// v-permission="['read', 'write']"         // Any of these permissions
// v-role="'admin'"                         // Single role
// v-role="['admin', 'l2_analyst']"         // Any of these roles
