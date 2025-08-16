// src/main.js
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import PermissionDirectives from './directives/permission'

import PrimeVue from 'primevue/config'
import Aura from '@primeuix/themes/aura'          // ✅ pilih AURA (v4 pakai preset, bukan CSS)
import ConfirmationService from 'primevue/confirmationservice'
import ToastService from 'primevue/toastservice'
import Tooltip from 'primevue/tooltip'
import Toast from 'primevue/toast'

import '@/assets/styles.scss'
import 'primeicons/primeicons.css'                // ikon (centang, dll)

import { useAuthStore } from '@/stores/auth'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(PrimeVue, {
  ripple: true,
  theme: {
    preset: Aura,
    options: {
      darkModeSelector: '.app-dark',             // tambahkan class ini di <html> / <body> untuk dark mode
    },
  },
})
app.use(ToastService)
app.use(ConfirmationService)
app.use(PermissionDirectives)

app.directive('tooltip', Tooltip)
app.component('Toast', Toast)

// click-outside (tetap seperti punyamu)
const clickOutside = {
  beforeMount(el, binding) {
    el.__clickOutside__ = (e) => {
      if (!(el === e.target || el.contains(e.target))) binding.value?.(e)
    }
    document.addEventListener('click', el.__clickOutside__, true)
  },
  unmounted(el) {
    document.removeEventListener('click', el.__clickOutside__, true)
    delete el.__clickOutside__
  }
}
app.directive('click-outside', clickOutside)

// init auth lalu mount
const authStore = useAuthStore()
authStore.initialize()
  .then(() => app.mount('#app'))
  .catch(() => app.mount('#app'))
