import { defineStore } from 'pinia'
import { amlCaseService } from '@/services/AMLCaseService'

export const useCaseStore = defineStore('cases', {
    state: () => ({
      cases: [],
      loading: false,
      error: null,
      lastFetch: null
    }),

    getters: {
      getCaseById: (state) => (id) => {
        return state.cases.find(case_ => case_.id === id)
      },

      getCasesByStatus: (state) => (status) => {
        return state.cases.filter(case_ => case_.status === status)
      },

      getCasesByLevel: (state) => (level) => {
        return state.cases.filter(case_ => case_.level === level)
      },

      getCasesByPriority: (state) => (priority) => {
        return state.cases.filter(case_ => case_.priority === priority)
      },

      getHighPriorityCases: (state) => {
        return state.cases.filter(case_ => case_.priority === 'high')
      },

      getPendingCases: (state) => {
        return state.cases.filter(case_ => 
          case_.status !== 'approved' && case_.status !== 'rejected'
        )
      }
    },

    actions: {
      async fetchCases() {
        this.loading = true
        this.error = null

        try {
          const cases = await amlCaseService.getAnomalies()
          this.cases = cases
          this.lastFetch = new Date()
          return cases
        } catch (error) {
          this.error = error.message
          console.error('Error fetching cases:', error)
          throw error
        } finally {
          this.loading = false
        }
      },

      async updateCase(caseId, updates) {
        try {
          await amlCaseService.updateCase(caseId, updates)
        
          const index = this.cases.findIndex(case_ => case_.id === caseId)
          if (index !== -1) {
            this.cases[index] = { ...this.cases[index], ...updates }
          }
        
          return this.cases[index]
        } catch (error) {
          this.error = error.message
          console.error('Error updating case:', error)
          throw error
        }
      },

      addCase(newCase) {
        this.cases.unshift(newCase)
      },

      removeCase(caseId) {
        const index = this.cases.findIndex(case_ => case_.id === caseId)
        if (index !== -1) {
          this.cases.splice(index, 1)
        }
      },

      clearError() {
        this.error = null
      },

      // Auto-refresh functionality
      startAutoRefresh(intervalMs = 30000) {
        return setInterval(() => {
          if (!this.loading) {
            this.fetchCases()
          }
        }, intervalMs)
      }
    }
})
