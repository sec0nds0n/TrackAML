// Vuex store module
export default {
  namespaced: true,
  state: {
    user: null,
    isAuthenticated: false,
    token: null
  },
  
  mutations: {
    SET_USER(state, user) {
      state.user = user
    },
    SET_AUTH_STATUS(state, status) {
      state.isAuthenticated = status
    }
  },
  
  actions: {
    initializeAuth({ commit }) {
      // Your initialization logic
      const token = localStorage.getItem('authToken')
      if (token) {
        commit('SET_AUTH_STATUS', true)
        // Load user data
      }
    }
  }
}