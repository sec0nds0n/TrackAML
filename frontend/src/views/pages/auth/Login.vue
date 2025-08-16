<script setup>
import FloatingConfigurator from '@/components/FloatingConfigurator.vue'
import { useLayout } from '@/layout/composables/layout'
import { useAuthStore } from '@/stores/auth'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import { computed, ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const { isDarkTheme } = useLayout()

// form state
const username = ref('')
const password = ref('')
const loading = ref(false)
const usernameError = ref('')
const passwordError = ref('')
const loginError = ref('')

// ✅ VALIDATION
const validateUsername = () => {
  if (!username.value) {
    usernameError.value = 'Username is required'
  } else if (username.value.length < 2) {
    usernameError.value = 'Username must be at least 2 characters'
  } else {
    usernameError.value = ''
  }
}

const validatePassword = () => {
  if (!password.value) {
    passwordError.value = 'Password is required'
  } else if (password.value.length < 6) {
    passwordError.value = 'Password must be at least 6 characters'
  } else {
    passwordError.value = ''
  }
}

const isFormValid = computed(() =>
  username.value && password.value && !usernameError.value && !passwordError.value
)

// ✅ QUICK LOGIN (dev helper)
const quickLogin = async (usernameValue, passwordValue = 'securepassword') => {
  username.value = usernameValue
  password.value = passwordValue
  await handleSubmit()
}

// ✅ DEFAULT REDIRECT BY ROLE (disesuaikan dgn backend)
const getDefaultRedirectPath = (role) => {
  const roleRoutes = {
    admin: '/dashboard',
    analyst_l1: '/dashboard',
    analyst_l2: '/dashboard',
    exchanger: '/dashboard',
    user: '/dashboard'
  }
  return roleRoutes[role] || '/dashboard'
}

// ✅ LOGO INTERACTIONS (dipertahankan)
const logoHovered = ref(false)
const logoClicked = ref(false)
const logoRotation = ref(0)

const handleLogoMouseEnter = () => { logoHovered.value = true; logoRotation.value += 360 }
const handleLogoMouseLeave = () => { logoHovered.value = false }
const createRippleEffect = () => {
  const logoElement = document.querySelector('.logo-container')
  if (logoElement) {
    logoElement.classList.add('ripple-effect')
    setTimeout(() => logoElement.classList.remove('ripple-effect'), 600)
  }
}
const handleLogoClick = () => {
  logoClicked.value = true
  logoRotation.value += 720
  createRippleEffect()
  setTimeout(() => { logoClicked.value = false }, 600)
}

// ✅ SUBMIT (cookie-based auth via store)
const handleSubmit = async () => {
  // clear errors
  loginError.value = ''
  usernameError.value = ''
  passwordError.value = ''

  // validate
  validateUsername()
  validatePassword()
  if (!isFormValid.value) return

  loading.value = true
  try {
    await authStore.login({
      username: username.value.trim(),
      password: password.value
    })

    // bersihkan form
    username.value = ''
    password.value = ''

    // redirect: prioritas ?redirect=..., fallback by role
    const desired = route.query.redirect || getDefaultRedirectPath(authStore.user?.role || 'user')
    await router.replace(String(desired))
  } catch (e) {
    // ambil pesan error dari store/exception
    loginError.value = e?.message || 'Login failed. Please try again.'
  } finally {
    loading.value = false
  }
}

// (opsional) social login placeholder
const handleGoogleLogin = () => { console.log('Google login') }
const handleMicrosoftLogin = () => { console.log('Microsoft login') }

// ✅ Auto-redirect jika sudah login (mis. user balik ke /auth/login)
onMounted(async () => {
  if (!authStore.initialized) {
    await authStore.initialize().catch(() => {})
  }
  if (authStore.isAuthenticated) {
    const target = route.query.redirect || getDefaultRedirectPath(authStore.user?.role || 'user')
    router.replace(String(target))
  }
})

// ==== UI computed classes (dipertahankan) ====
const containerClasses = computed(() => ({
  'min-h-screen flex items-center justify-center p-4 transition-colors duration-300': true,
  'bg-gradient-to-br from-surface-50 via-surface-100 to-surface-200': !isDarkTheme.value,
  'bg-gradient-to-br from-surface-950 via-surface-900 to-surface-800': isDarkTheme.value
}))
const cardClasses = computed(() => ({
  'rounded-2xl shadow-2xl border overflow-hidden transition-colors duration-300 relative backdrop-blur-sm': true,
  'bg-white/90 border-surface-200': !isDarkTheme.value,
  'bg-surface-900/90 border-surface-700': isDarkTheme.value
}))
const headerClasses = computed(() => ({
  'px-8 pt-8 pb-6 text-center bg-gradient-to-b transition-colors duration-300': true,
  'from-primary-50/80 to-white/80': !isDarkTheme.value,
  'from-surface-800/80 to-surface-900/80': isDarkTheme.value
}))
const titleClasses = computed(() => ({
  'text-2xl font-bold mb-2 transition-colors duration-300': true,
  'text-surface-900': !isDarkTheme.value,
  'text-surface-0': isDarkTheme.value
}))
const subtitleClasses = computed(() => ({
  'text-sm transition-colors duration-300': true,
  'text-surface-600': !isDarkTheme.value,
  'text-surface-400': isDarkTheme.value
}))
const labelClasses = computed(() => ({
  'block text-sm font-medium transition-colors duration-300': true,
  'text-surface-900': !isDarkTheme.value,
  'text-surface-0': isDarkTheme.value
}))
const footerClasses = computed(() => ({
  'px-8 py-4 text-center border transition-colors duration-300': true,
  'bg-surface-50/80 border-surface-200': !isDarkTheme.value,
  'bg-surface-800/80 border-surface-700': isDarkTheme.value
}))
const footerTextClasses = computed(() => ({
  'text-sm transition-colors duration-300': true,
  'text-surface-600': !isDarkTheme.value,
  'text-surface-400': isDarkTheme.value
}))
const dividerBgClasses = computed(() => ({
  'px-4 text-surface-500 transition-colors duration-300': true,
  'bg-white/90': !isDarkTheme.value,
  'bg-surface-900/90 text-surface-400': isDarkTheme.value
}))
const logoContainerClasses = computed(() => ({
  'inline-flex items-center justify-center w-20 h-20 rounded-2xl shadow-lg cursor-pointer select-none transition-all duration-500 ease-out relative overflow-hidden': true,
  'bg-primary-500': true
}))
</script>

<template>
    <div class="mx-auto h-screen w-[calc(100%)] overflow-hidden ">
      <Vortex
        background-color="black"
        :range-y="800"
        :particle-count="500"
        :base-hue="120"
        class="flex size-full flex-col items-center justify-center px-2 py-4 md:px-10"
      >
    <!-- FloatingConfigurator with highest z-index -->

    <div class="relative z-50">
        <FloatingConfigurator />
      
    </div>

    <div :class="containerClasses">
      <div class="w-full max-w-md relative z-10">
        <!-- Main Card -->
        <div :class="cardClasses">
          <!-- Header Section -->
          <div :class="headerClasses">
            <!-- Interactive Logo -->
            <div 
              :class="logoContainerClasses"
              class="logo-container mb-6"
              @mouseenter="handleLogoMouseEnter"
              @mouseleave="handleLogoMouseLeave"
              @click="handleLogoClick"
              :style="{ transform: `rotate(${logoRotation}deg)` }"
              role="button"
              tabindex="0"
              @keydown.enter="handleLogoClick"
              @keydown.space.prevent="handleLogoClick"
              :aria-label="'SigmaVerde Logo - Click for interaction'"
            >
              <!-- Ripple effect overlay -->
              <div class="absolute inset-0 rounded-2xl overflow-hidden">
                <div class="ripple-overlay"></div>
              </div>
            
              <!-- Logo image with enhanced interactions -->
              <img 
                src="/sigma-verde-crop.svg" 
                alt="SigmaVerde Logo" 
                class="w-16 h-16 rounded-2xl transition-all duration-300 relative z-10"
                :class="{
                  'filter brightness-110 contrast-110': logoHovered,
                  'animate-bounce': logoClicked
                }"
                draggable="false"
              >
            
              <!-- Glow effect -->
              <div 
                class="absolute inset-0 rounded-2xl transition-opacity duration-300 pointer-events-none"
                :class="{
                  'opacity-100': logoHovered,
                  'opacity-0': !logoHovered
                }"
                style="background: radial-gradient(circle, rgba(34, 197, 94, 0.3) 0%, transparent 70%); filter: blur(8px);"
              ></div>
            
              <!-- Sparkle effects -->
              <div 
                v-if="logoHovered || logoClicked"
                class="absolute inset-0 pointer-events-none"
              >
                <div class="sparkle sparkle-1"></div>
                <div class="sparkle sparkle-2"></div>
                <div class="sparkle sparkle-3"></div>
                <div class="sparkle sparkle-4"></div>
              </div>
            </div>
            <!-- Title -->
            <h1 :class="titleClasses">
              Welcome Back
            </h1>
            <p :class="subtitleClasses">
              Sign in to your account to continue
            </p>
          </div>

          <!-- Form Section -->
          <div class="px-16 py-6">
            <!-- General Login Error -->
            <div v-if="loginError" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p class="text-red-700 text-sm">{{ loginError }}</p>
            </div>

            <form @submit.prevent="handleSubmit" class="space-y-6">
              <!-- Username Field -->
              <div class="space-y-2">
                <label for="username" :class="labelClasses">
                  Username
                </label>
                <InputText
                  id="username"
                  v-model="username"
                  type="text"
                  placeholder="Enter your username"
                  class="w-full"
                  :class="{ 'p-invalid': usernameError }"
                  @blur="validateUsername"
                  @input="usernameError = ''; loginError = ''"
                  autocomplete="username"
                />
                <small v-if="usernameError" class="text-red-500">{{ usernameError }}</small>
              </div>

              <!-- Password Field -->
              <div class="space-y-2">
                <label for="password" :class="labelClasses">
                  Password
                </label>
                <Password
                  id="password"
                  v-model="password"
                  placeholder="Enter your password"
                  :toggleMask="true"
                  :feedback="false"
                  fluid
                  :class="{ 'p-invalid': passwordError }"
                  @blur="validatePassword"
                  @input="passwordError = ''; loginError = ''"
                  autocomplete="current-password"
                />
                <small v-if="passwordError" class="text-red-500">{{ passwordError }}</small>
              </div>

              <!-- Forgot Password -->
              <div class="flex items-center justify-end">
                <a href="#" class="text-sm text-primary-600 hover:text-primary-700 font-medium transition-colors">
                  Forgot password?
                </a>
              </div>

              <!-- Sign In Button -->
              <Button
                type="submit"
                label="Sign In"
                :loading="loading"
                :disabled="!isFormValid || loading"
                class="w-full"
                size="large"
              />
            </form>

            <!-- Divider -->
            <div class="relative my-6">
              <div class="absolute inset-0 flex items-center">
                <div :class="{
                  'w-full border-t transition-colors duration-300': true,
                  'border-surface-300': !isDarkTheme,
                  'border-surface-600': isDarkTheme
                }"></div>
              </div>
              <div class="relative flex justify-center text-sm">
                <span :class="dividerBgClasses">
                  or continue with
                </span>
              </div>
            </div>

            <!-- Social Login Buttons -->
            <div class="space-y-3">
              <Button
                @click="handleGoogleLogin"
                label="Continue with Google"
                icon="pi pi-google"
                class="w-full"
                severity="secondary"
                outlined
                :disabled="loading"
              />
              <Button
                @click="handleMicrosoftLogin"
                label="Continue with Microsoft"
                icon="pi pi-microsoft"
                class="w-full"
                severity="secondary"
                outlined
                :disabled="loading"
              />
            </div>
          </div>

          <!-- Footer -->
          <div :class="footerClasses">
            <p :class="footerTextClasses">
              Don't have an account?
              <a href="#" class="text-primary-600 hover:text-primary-700 font-medium transition-colors ml-1">
                Sign up
              </a>
            </p>
          </div>
        </div>

        <!-- Security Notice -->
        <div class="mt-4 text-center">
          <p :class="{
            'text-xs transition-colors duration-300': true,
            'text-surface-500': !isDarkTheme,
            'text-surface-400': isDarkTheme,
            'text-white': !isDarkTheme
          }">
            🔒 Your information is secure and encrypted
          </p>
        </div>
      </div>
    </div>  
    </Vortex>
</div>
</template>

<style scoped>
/* Enhanced backdrop blur for card */
.backdrop-blur-sm {
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
}

/* Interactive Logo Styles */
.logo-container {
    position: relative;
    transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    will-change: transform;
}

.logo-container:hover {
    transform: scale(1.1) rotate(12deg);
    box-shadow: 
      0 20px 40px rgba(34, 197, 94, 0.3),
      0 0 0 4px rgba(34, 197, 94, 0.1),
      inset 0 0 20px rgba(255, 255, 255, 0.1);
}

.logo-container:active {
    transform: scale(0.95) rotate(12deg);
}

.logo-container:focus {
    outline: none;
    box-shadow: 
      0 0 0 3px rgba(34, 197, 94, 0.5),
      0 20px 40px rgba(34, 197, 94, 0.3);
}

/* Ripple Effect */
.logo-container.ripple-effect::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 0;
    height: 0;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(34, 197, 94, 0.4) 0%, transparent 70%);
    transform: translate(-50%, -50%);
    animation: ripple 0.6s ease-out;
    z-index: 0;
}

@keyframes ripple {
    0% {
      width: 0;
      height: 0;
      opacity: 1;
    }
    100% {
      width: 200px;
      height: 200px;
      opacity: 0;
    }
}

/* Sparkle Effects */
.sparkle {
    position: absolute;
    width: 4px;
    height: 4px;
    background: #22c55e;
    border-radius: 50%;
    animation: sparkle 1.5s ease-in-out infinite;
    box-shadow: 0 0 6px #22c55e;
}

.sparkle-1 {
    top: 10%;
    left: 20%;
    animation-delay: 0s;
}

.sparkle-2 {
    top: 20%;
    right: 15%;
    animation-delay: 0.3s;
}

.sparkle-3 {
    bottom: 15%;
    left: 15%;
    animation-delay: 0.6s;
}

.sparkle-4 {
    bottom: 20%;
    right: 20%;
    animation-delay: 0.9s;
}

@keyframes sparkle {
    0%, 100% {
      opacity: 0;
      transform: scale(0) rotate(0deg);
    }
    50% {
      opacity: 1;
      transform: scale(1) rotate(180deg);
    }
}

/* Enhanced Logo Image Effects */
.logo-container img {
    transition: all 0.3s ease;
    will-change: filter, transform;
}

.logo-container:hover img {
    filter: brightness(1.1) contrast(1.1) drop-shadow(0 0 10px rgba(34, 197, 94, 0.5));
}

/* Glow Animation */
@keyframes glow-pulse {
    0%, 100% {
      opacity: 0.3;
      transform: scale(1);
    }
    50% {
      opacity: 0.6;
      transform: scale(1.05);
    }
}

.logo-container:hover .absolute:nth-child(3) {
    animation: glow-pulse 2s ease-in-out infinite;
}

/* Cursor Styles */
.logo-container {
    cursor: pointer;
}

.logo-container:hover {
    cursor: grab;
}

.logo-container:active {
    cursor: grabbing;
}

/* Enhanced Bounce Animation */
@keyframes enhanced-bounce {
    0%, 20%, 53%, 80%, 100% {
      transform: translate3d(0, 0, 0);
    }
    40%, 43% {
      transform: translate3d(0, -15px, 0);
    }
    70% {
      transform: translate3d(0, -7px, 0);
    }
    90% {
      transform: translate3d(0, -2px, 0);
    }
}

.animate-bounce {
    animation: enhanced-bounce 1s ease-in-out;
}

/* Magnetic Effect */
.logo-container::after {
    content: '';
    position: absolute;
    top: -10px;
    left: -10px;
    right: -10px;
    bottom: -10px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(34, 197, 94, 0.1) 0%, transparent 70%);
    opacity: 0;
    transition: opacity 0.3s ease;
    pointer-events: none;
    z-index: -1;
}

.logo-container:hover::after {
    opacity: 1;
    animation: magnetic-pulse 2s ease-in-out infinite;
}

@keyframes magnetic-pulse {
    0%, 100% {
      transform: scale(1);
      opacity: 0.1;
    }
    50% {
      transform: scale(1.2);
      opacity: 0.3;
    }
}

/* 3D Transform Effects */
.logo-container {
    transform-style: preserve-3d;
    perspective: 1000px;
}

.logo-container:hover {
    transform: scale(1.1) rotateY(15deg) rotateX(5deg);
}

/* Color Shift Animation */
@keyframes color-shift {
    0% { background-color: #22c55e; }
    25% { background-color: #16a34a; }
    50% { background-color: #15803d; }
    75% { background-color: #166534; }
    100% { background-color: #22c55e; }
}

.logo-container:hover {
    animation: color-shift 3s ease-in-out infinite;
}

/* FloatingConfigurator z-index fix */
:deep(.floating-configurator) {
    z-index: 9999 !important;
    position: relative;
}

/* Ensure all floating elements are above everything */
:deep(.p-overlaypanel),
:deep(.p-dropdown-panel),
:deep(.p-tooltip),
:deep(.p-dialog),
:deep(.p-sidebar) {
    z-index: 9999 !important;
}

/* Custom styles for password toggle icons */
:deep(.p-password-toggle-icon) {
    width: 1rem;
    height: 1rem;
}

/* Enhanced focus states */
:deep(.p-inputtext:focus),
:deep(.p-password-input:focus) {
    box-shadow: 0 0 0 2px rgb(var(--primary-500) / 0.2);
    border-color: rgb(var(--primary-500));
}

/* Loading state for form */
.form-loading {
    pointer-events: none;
    opacity: 0.7;
}

/* Smooth transitions for all elements */
* {
    transition: all 0.3s ease-in-out;
}

/* Custom button hover effects */
:deep(.p-button:not(:disabled):hover) {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* Error message styling */
.text-red-500 {
    color: #ef4444;
}

.text-red-700 {
    color: #b91c1c;
}

.bg-red-50 {
    background-color: #fef2f2;
}

.border-red-200 {
    border-color: #fecaca;
}

/* API status indicator */
.text-surface-400 {
    opacity: 0.6;
}
</style>