// If using Pinia
import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    isAuthenticated: false,
    token: null
  }),
  
  actions: {
    // Make sure this method exists
    initializeAuth() {
      // Your initialization logic here
      const token = localStorage.getItem('authToken')
      if (token) {
        this.token = token
        this.isAuthenticated = true
        // Load user data, etc.
      }
    },
    
    login(credentials) {
      // Login logic
    },
    
    logout() {
      // Logout logic
    }
  }
})