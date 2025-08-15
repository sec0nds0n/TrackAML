<script setup>
import FloatingConfigurator from '@/components/FloatingConfigurator.vue';
import { useLayout } from '@/layout/composables/layout';
import { useAuthStore } from '@/stores/auth';
import Button from 'primevue/button';
import Checkbox from 'primevue/checkbox';
import InputText from 'primevue/inputtext';
import Password from 'primevue/password';
import { computed, onMounted, onUnmounted, ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const authStore = useAuthStore();

const email = ref('');
const password = ref('');
const rememberMe = ref(false);
const loading = ref(false);
const emailError = ref('');
const passwordError = ref('');
const { isDarkTheme } = useLayout();


// Predefined user roles and permissions
const userRoles = {
    'admin@example.com': {
        role: 'admin',
        permissions: ['read', 'write', 'approve', 'manage_users']
    },
    'l1@example.com': {
        role: 'l1_analyst',
        permissions: ['read', 'write']
    },
    'l2@example.com': {
        role: 'l2_analyst',
        permissions: ['read', 'write', 'approve']
    }
};



const validateEmail = () => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email.value) {
        emailError.value = 'Email is required';
    } else if (!emailRegex.test(email.value)) {
        emailError.value = 'Please enter a valid email address';
    } else {
        emailError.value = '';
    }
};

const validatePassword = () => {
    if (!password.value) {
        passwordError.value = 'Password is required';
    } else if (password.value.length < 6) {
        passwordError.value = 'Password must be at least 6 characters';
    } else {
        passwordError.value = '';
    }
};

const quickLogin = async (emailAddress) => {
    email.value = emailAddress;
    password.value = 'password';
    await login();
};

const login = async () => {
    validateEmail();
    validatePassword();
    
    if (!isFormValid.value) return;
    
    loading.value = true;
    try {
        // Simulate API call delay
        await new Promise(resolve => setTimeout(resolve, 1000));

        const user = userRoles[email.value];
        if (user && password.value === 'password') { // In real app, use proper password validation
            // Store user data and token
            await authStore.login({
                email: email.value,
                role: user.role,
                permissions: user.permissions,
                token: 'dummy-jwt-token'
            });

            // Redirect based on role
            switch (user.role) {
                case 'admin':
                    router.push('/dashboard');
                    break;
                case 'l1_analyst':
                    router.push('/monitoring/cases');
                    break;
                case 'l2_analyst':
                    router.push('/monitoring/cases');
                    break;
                default:
                    router.push('/dashboard');
            }
        } else {
            emailError.value = 'Invalid credentials';
            passwordError.value = 'Invalid credentials';
        }
    } catch (error) {
        console.error('Login error:', error);
        emailError.value = 'Login failed. Please try again.';
    } finally {
        loading.value = false;
    }
};

// Logo interaction states
const logoHovered = ref(false);
const logoClicked = ref(false);
const logoRotation = ref(0);

// Polygon animation
const polygonCanvas = ref(null);
let animationId = null;
let particles = [];

// Computed properties
const isFormValid = computed(() => {
  return email.value && password.value && !emailError.value && !passwordError.value;
});

// Dynamic classes based on theme
const containerClasses = computed(() => ({
  'min-h-screen flex items-center justify-center p-4 transition-colors duration-300 relative overflow-hidden': true,
  'bg-gradient-to-br from-surface-50 via-surface-100 to-surface-200': !isDarkTheme.value,
  'bg-gradient-to-br from-surface-950 via-surface-900 to-surface-800': isDarkTheme.value
}));

const cardClasses = computed(() => ({
  'rounded-2xl shadow-2xl border overflow-hidden transition-colors duration-300 relative backdrop-blur-sm': true,
  'bg-white/90 border-surface-200': !isDarkTheme.value,
  'bg-surface-900/90 border-surface-700': isDarkTheme.value
}));

const headerClasses = computed(() => ({
  'px-8 pt-8 pb-6 text-center bg-gradient-to-b transition-colors duration-300': true,
  'from-primary-50/80 to-white/80': !isDarkTheme.value,
  'from-surface-800/80 to-surface-900/80': isDarkTheme.value
}));

const titleClasses = computed(() => ({
  'text-2xl font-bold mb-2 transition-colors duration-300': true,
  'text-surface-900': !isDarkTheme.value,
  'text-surface-0': isDarkTheme.value
}));

const subtitleClasses = computed(() => ({
  'text-sm transition-colors duration-300': true,
  'text-surface-600': !isDarkTheme.value,
  'text-surface-400': isDarkTheme.value
}));

const labelClasses = computed(() => ({
  'block text-sm font-medium transition-colors duration-300': true,
  'text-surface-900': !isDarkTheme.value,
  'text-surface-0': isDarkTheme.value
}));

const footerClasses = computed(() => ({
  'px-8 py-4 text-center border-t transition-colors duration-300': true,
  'bg-surface-50/80 border-surface-200': !isDarkTheme.value,
  'bg-surface-800/80 border-surface-700': isDarkTheme.value
}));

const footerTextClasses = computed(() => ({
  'text-sm transition-colors duration-300': true,
  'text-surface-600': !isDarkTheme.value,
  'text-surface-400': isDarkTheme.value
}));

const dividerBgClasses = computed(() => ({
  'px-4 text-surface-500 transition-colors duration-300': true,
  'bg-white/90': !isDarkTheme.value,
  'bg-surface-900/90 text-surface-400': isDarkTheme.value
}));

// Logo interaction computed classes
const logoContainerClasses = computed(() => ({
  'inline-flex items-center justify-center w-20 h-20 rounded-2xl shadow-lg cursor-pointer select-none transition-all duration-500 ease-out relative overflow-hidden': true,
  'bg-primary-500': !logoHovered.value,
  'bg-primary-600': logoHovered.value,
  'transform hover:scale-110 hover:rotate-12 active:scale-95': true,
  'shadow-2xl': logoHovered.value,
  'animate-pulse': logoClicked.value
}));

// Logo interaction handlers
const handleLogoMouseEnter = () => {
  logoHovered.value = true;
  logoRotation.value += 360;
};

const handleLogoMouseLeave = () => {
  logoHovered.value = false;
};

const handleLogoClick = () => {
  logoClicked.value = true;
  logoRotation.value += 720; // Double spin on click
  
  // Create ripple effect
  createRippleEffect();
  
  // Reset click state after animation
  setTimeout(() => {
    logoClicked.value = false;
  }, 600);
  
  // Optional: Add some fun interaction like showing a message
  console.log('🎯 SigmaVerde Logo Clicked! Welcome to the future of productivity!');
};

const createRippleEffect = () => {
  // This will be handled by CSS animations
  const logoElement = document.querySelector('.logo-container');
  if (logoElement) {
    logoElement.classList.add('ripple-effect');
    setTimeout(() => {
      logoElement.classList.remove('ripple-effect');
    }, 600);
  }
};

// Enhanced Polygon Background Animation with Bolder Connections
class Particle {
  constructor(canvas) {
      this.canvas = canvas;
      this.x = Math.random() * canvas.width;
      this.y = Math.random() * canvas.height;
      this.vx = (Math.random() - 0.5) * 0.8; // Slightly faster movement
      this.vy = (Math.random() - 0.5) * 0.8;
      this.radius = Math.random() * 3 + 2; // Larger particles
  }

  update() {
      this.x += this.vx;
      this.y += this.vy;

      if (this.x < 0 || this.x > this.canvas.width) this.vx *= -1;
      if (this.y < 0 || this.y > this.canvas.height) this.vy *= -1;
  }

  draw(ctx) {
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
      ctx.fill();
        
      // Add glow effect to particles
      ctx.shadowBlur = 10;
      ctx.shadowColor = isDarkTheme.value ? 'rgba(34, 197, 94, 0.8)' : 'rgba(34, 197, 94, 0.6)';
      ctx.fill();
      ctx.shadowBlur = 0;
  }
}

const initPolygonBackground = () => {
  if (!polygonCanvas.value) return;

  const canvas = polygonCanvas.value;
  const ctx = canvas.getContext('2d');
    
  const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
  };

  resizeCanvas();
  window.addEventListener('resize', resizeCanvas);

  // Create more particles for denser network
  particles = [];
  const particleCount = Math.floor((canvas.width * canvas.height) / 12000); // More particles
    
  for (let i = 0; i < particleCount; i++) {
      particles.push(new Particle(canvas));
  }

  const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
        
      // Enhanced particle and line colors with better visibility
      const particleColor = isDarkTheme.value ? 'rgba(34, 197, 94, 0.9)' : 'rgba(34, 197, 94, 1)';
      const lineColor = isDarkTheme.value ? 'rgba(34, 197, 94, 0.6)' : 'rgba(34, 197, 94, 0.7)';
        
      ctx.fillStyle = particleColor;
      ctx.strokeStyle = lineColor;

      // Update and draw particles
      particles.forEach(particle => {
          particle.update();
          particle.draw(ctx);
      });

      // Draw bolder connections with enhanced styling
      for (let i = 0; i < particles.length; i++) {
          for (let j = i + 1; j < particles.length; j++) {
              const dx = particles[i].x - particles[j].x;
              const dy = particles[i].y - particles[j].y;
              const distance = Math.sqrt(dx * dx + dy * dy);

              // Increased connection distance for more connections
              if (distance < 150) {
                  const opacity = (150 - distance) / 150;
                    
                  // Create gradient line for more visual appeal
                  const gradient = ctx.createLinearGradient(
                      particles[i].x, particles[i].y,
                      particles[j].x, particles[j].y
                  );
                    
                  const baseOpacity = opacity * (isDarkTheme.value ? 0.8 : 0.9);
                  const centerColor = isDarkTheme.value 
                      ? `rgba(34, 197, 94, ${baseOpacity})` 
                      : `rgba(34, 197, 94, ${baseOpacity})`;
                  const edgeColor = isDarkTheme.value 
                      ? `rgba(34, 197, 94, ${baseOpacity * 0.3})` 
                      : `rgba(34, 197, 94, ${baseOpacity * 0.4})`;
                    
                  gradient.addColorStop(0, edgeColor);
                  gradient.addColorStop(0.5, centerColor);
                  gradient.addColorStop(1, edgeColor);
                    
                  ctx.strokeStyle = gradient;
                    
                  // Bolder line width based on distance
                  const lineWidth = distance < 100 ? 2.5 : distance < 125 ? 2 : 1.5;
                  ctx.lineWidth = lineWidth;
                    
                  // Add glow effect to lines
                  ctx.shadowBlur = 3;
                  ctx.shadowColor = isDarkTheme.value ? 'rgba(34, 197, 94, 0.5)' : 'rgba(34, 197, 94, 0.4)';
                    
                  ctx.beginPath();
                  ctx.moveTo(particles[i].x, particles[i].y);
                  ctx.lineTo(particles[j].x, particles[j].y);
                  ctx.stroke();
                    
                  // Reset shadow
                  ctx.shadowBlur = 0;
              }
          }
      }

      animationId = requestAnimationFrame(animate);
  };

  animate();
};


// Form submission
const handleSubmit = async () => {
  validateEmail();
  validatePassword();
  
  if (!isFormValid.value) return;
  
  isLoading.value = true;
  
  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Handle successful login
    router.push('/');
  } catch (error) {
    console.error('Login failed:', error);
    // Handle login error
  } finally {
    isLoading.value = false;
  }
};

// Social login handlers
const handleGoogleLogin = () => {
  console.log('Google login');
};

const handleMicrosoftLogin = () => {
  console.log('Microsoft login');
};

// Lifecycle hooks
onMounted(() => {
  initPolygonBackground();
});

onUnmounted(() => {
  if (animationId) {
      cancelAnimationFrame(animationId);
  }
  window.removeEventListener('resize', () => {});
});
</script>

<template>
  <!-- FloatingConfigurator with highest z-index -->
  <div class="relative z-50">
      <FloatingConfigurator />
  </div>
    
  <div :class="containerClasses">
    <!-- Animated Polygon Background -->
    <canvas 
      ref="polygonCanvas"
      class="absolute inset-0 w-full h-full z-0"
      style="pointer-events: none;"
    ></canvas>
      
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
        <div class="px-8 py-6">
          <form @submit.prevent="handleSubmit" class="space-y-6">
            <!-- Email Field -->
            <div class="space-y-2">
              <label for="email" :class="labelClasses">
                Email Address
              </label>
              <InputText
                id="email"
                v-model="email"
                type="email"
                placeholder="Enter your email"
                class="w-full"
                :class="{ 'p-invalid': emailError }"
                @blur="validateEmail"
                @input="emailError = ''"
                autocomplete="email"
              />
              <small v-if="emailError" class="text-red-500">{{ emailError }}</small>
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
                @input="passwordError = ''"
                autocomplete="current-password"
              />
              <small v-if="passwordError" class="text-red-500">{{ passwordError }}</small>
            </div>

            <!-- Remember Me & Forgot Password -->
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-2">
                <Checkbox v-model="rememberMe" id="remember" binary />
                <label for="remember" :class="{ 
                  'text-sm cursor-pointer transition-colors duration-300': true,
                  'text-surface-700': !isDarkTheme,
                  'text-surface-300': isDarkTheme
                }">
                  Remember me
                </label>
              </div>
              <a href="#" class="text-sm text-primary-600 hover:text-primary-700 font-medium transition-colors">
                Forgot password?
              </a>
            </div>

            <!-- Sign In Button -->
            <Button
              type="submit"
              label="Sign In"
              @click="login"
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
                Or continue with
              </span>
            </div>
          </div>

          <!-- Social Login Buttons -->
          <div class="grid grid-cols-2 gap-3">
            <Button
              @click="handleGoogleLogin"
              outlined
              class="flex items-center justify-center space-x-2"
              :disabled="isLoading"
            >
              <svg class="w-4 h-4" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
              <span class="text-sm">Google</span>
            </Button>
            
            <Button
              @click="handleMicrosoftLogin"
              outlined
              class="flex items-center justify-center space-x-2"
              :disabled="isLoading"
            >
              <svg class="w-4 h-4" viewBox="0 0 24 24">
                <path fill="#f25022" d="M1 1h10v10H1z"/>
                <path fill="#00a4ef" d="M13 1h10v10H13z"/>
                <path fill="#7fba00" d="M1 13h10v10H1z"/>
                <path fill="#ffb900" d="M13 13h10v10H13z"/>
              </svg>
              <span class="text-sm">Microsoft</span>
            </Button>
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
          'text-surface-400': isDarkTheme
        }">
          🔒 Your information is secure and encrypted
        </p>
      </div>
    </div>
    </div>  

</template>

<style scoped>
/* Canvas styling with enhanced performance */
canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  will-change: auto;
  transform: translateZ(0);
}

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

/* Social button specific styles */
:deep(.p-button-outlined)
</style>
