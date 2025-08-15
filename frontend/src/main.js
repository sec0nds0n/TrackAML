import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import PermissionDirectives from './directives/permission';
import router from './router';

import Aura from '@primeuix/themes/aura';
import PrimeVue from 'primevue/config';
import ConfirmationService from 'primevue/confirmationservice';
import ToastService from 'primevue/toastservice';
import Tooltip from 'primevue/tooltip'
import Toast from 'primevue/toast'

import '@/assets/styles.scss'
import 'primeicons/primeicons.css'

import { useAuthStore } from '@/stores/auth';

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);
app.use(PrimeVue, {
    theme: {
        preset: Aura,
        options: {
            darkModeSelector: '.app-dark'
        }
    }
});
app.use(ToastService);
app.use(ConfirmationService);
app.use(PermissionDirectives);

app.directive('tooltip', Tooltip)
app.component('Toast', Toast)

const clickOutside = {
  beforeMount(el, binding) {
    el.__clickOutside__ = (e) => {
      if (!(el === e.target || el.contains(e.target))) binding.value?.(e)
    }
    // gunakan capture biar lebih andal untuk overlay
    document.addEventListener('click', el.__clickOutside__, true)
  },
  unmounted(el) {
    document.removeEventListener('click', el.__clickOutside__, true)
    delete el.__clickOutside__
  }
}
app.directive('click-outside', clickOutside)

// Initialize auth store before mounting the app
const authStore = useAuthStore()

// Initialize auth store and then mount app
authStore
  .initialize()
  .then(() => {
    console.log('Auth store initialized, mounting app…')
    app.mount('#app')
  })
  .catch((error) => {
    console.error('Failed to initialize auth store:', error)
    app.mount('#app')
  })