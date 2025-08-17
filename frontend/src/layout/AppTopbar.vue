<script setup>
import { useLayout } from '@/layout/composables/layout'
import { ref, onMounted, onBeforeUnmount, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'primevue/usetoast'
import { useNotificationStore } from '@/stores/notifications'

const { toggleMenu, toggleDarkMode, isDarkTheme } = useLayout()
useLayout()

const toast = useToast()
const router = useRouter()

// Pakai satu instance store saja (hindari duplikasi variabel yg sama)
const auth = useAuthStore()
const notif = useNotificationStore()

const showDropdown = ref(false)
const showProfileDropdown = ref(false)

const displayName = computed(() => {
  const u = auth.user || {}
  return u.username || u.email || 'User'
})
const initials = computed(() => {
  const n = displayName.value.trim()
  return n ? n.split(/\s+/).map(s => s[0]).join('').slice(0, 2).toUpperCase() : '?'
})

const toggleProfileDropdown = () => { showProfileDropdown.value = !showProfileDropdown.value }
const closeProfileDropdown = () => { showProfileDropdown.value = false }

const handleSignOut = async () => {
  closeProfileDropdown()
  try { await auth.logout?.() } finally { router.replace('/auth/login') }
}
const handleMyProfile = () => { closeProfileDropdown(); router.push('/profile') }

// --- Notifikasi ---

// 1) Snapshot ID, supaya toast hanya muncul untuk item BARU setelah initial fetch
let lastIds = new Set()

onMounted(async () => {
  console.log('[Topbar] mounted')
  const justLoggedIn = sessionStorage.getItem('justLoggedIn') === '1'
  if (justLoggedIn) {
    sessionStorage.removeItem('justLoggedIn')
    toast.add({
      severity: 'success',
      summary: 'Welcome!',
      detail: `Hi ${auth.user?.name || displayName.value}, you are now logged in.`,
      life: 4000
    })
  }

  // Trigger fetch awal agar badge tidak 0 sampai interval polling berikutnya
  try { await notif.fetchUnread?.() } catch {}

  // Ambil snapshot ID setelah fetch pertama (hindari toast pada batch awal)
  setTimeout(() => {
    lastIds = new Set((notif.items || []).map(i => i.id))
  }, 200)
})

// 2) Mulai/stop polling mengikuti status auth
watch(
  () => auth.isAuthenticated,
  (ok) => { ok ? notif.startPoll(10000) : notif.stopPoll() },
  { immediate: true }
)

onBeforeUnmount(() => {
  notif.stopPoll()
})

// 3) Deteksi item notifikasi baru → toast
watch(
  () => notif.items.map(i => i.id).join(','),
  () => {
    const nowIds = new Set(notif.items.map(i => i.id))
    for (const n of notif.items) {
      if (!lastIds.has(n.id) && n.type === 'case_assigned') {
        toast.add({
          severity: 'info',
          summary: 'New assignment',
          detail: n.message,
          life: 5000
        })
      }
    }
    lastIds = nowIds
  }
)

// Klik item di dropdown
function onClickNotification(n) {
  if (n?.meta?.case_id) {
    router.push({ name: 'case-detail', params: { id: n.meta.case_id } })
  }
  showDropdown.value = false
}

async function onMarkAllRead() {
  await notif.markAllRead()
  showDropdown.value = false
}
</script>

<template>
  <div class="layout-topbar">
    <div class="layout-topbar-logo-container">
      <button class="layout-menu-button layout-topbar-action" @click="toggleMenu">
        <i class="pi pi-bars"></i>
      </button>
      <router-link to="/" class="layout-topbar-logo">
        <img src="/sigma-verde-logo.svg" alt="Sigma Verde" class="logo-image" />
      </router-link>
    </div>

    <div class="layout-topbar-actions">
      <div class="layout-config-menu">
        <button type="button" class="layout-topbar-action" @click="toggleDarkMode">
          <i :class="['pi', { 'pi-moon': isDarkTheme, 'pi-sun': !isDarkTheme }]"></i>
        </button>
      </div>

      <div class="layout-topbar-menu hidden lg:block">
        <div class="layout-topbar-menu-content flex items-center gap-2">
            <button type="button" class="layout-topbar-action">
                <i class="pi pi-calendar"></i>
                <span>Calendar</span>
            </button>
            <button type="button" class="layout-topbar-action">
                <i class="pi pi-inbox"></i>
                <span>Messages</span>
            </button>

            <!-- Bell -->
            <div class="relative">
            <button class="relative" @click="showDropdown = !showDropdown" aria-label="Notifications">
                <i class="pi pi-bell text-xl"></i>
                <span v-if="notif.unreadCount > 0"
                    class="absolute -top-1 -right-1 bg-red-500 text-white rounded-full text-xs px-1">
                {{ notif.unreadCount }}
                </span>
            </button>

            <!-- Dropdown -->
            <div v-if="showDropdown"
                class="absolute right-0 mt-2 w-80 rounded-lg border bg-white shadow-lg z-50">
                <div class="flex items-center justify-between p-3 border-b">
                <div class="font-semibold">Notifications</div>
                <button class="text-sm text-emerald-600 hover:underline" @click="onMarkAllRead">
                    Mark all read
                </button>
                </div>

                <div class="max-h-80 overflow-auto">
                <div v-if="notif.items.length === 0" class="p-3 text-gray-500 text-sm">
                    Belum ada notifikasi.
                </div>

                <button v-for="n in notif.items" :key="n.id"
                        class="w-full text-left p-3 hover:bg-gray-50 border-b last:border-b-0"
                        @click="onClickNotification(n)">
                    <div class="text-sm" :class="{'font-semibold': !n.is_read}">
                    {{ n.message }}
                    </div>
                    <div class="text-xs text-gray-500 mt-1">
                    {{ new Date(n.created_at).toLocaleString() }}
                    </div>
                </button>
                </div>
            </div>
        </div>

          <div class="relative">
            <button
              type="button"
              class="layout-topbar-action"
              @click="toggleProfileDropdown"
            >
              <i class="pi pi-user"></i>
              <span class="truncate max-w-[10rem]">{{ displayName }}</span>
            </button>
            <div
              class="profile-dropdown"
              :class="{ 'profile-dropdown-visible': showProfileDropdown }"
            >
              <div class="profile-dropdown-content">
                <div class="px-4 py-3 text-sm text-color-secondary border-b">
                 Signed in as <span class="font-medium text-color">{{ displayName }}</span>
               </div>
                <button type="button" class="profile-dropdown-item" @click="handleMyProfile">
                  <i class="pi pi-user"></i>
                  <span>My Profile</span>
                </button>
                <button type="button" class="profile-dropdown-item" @click="handleSignOut">
                  <i class="pi pi-sign-out"></i>
                  <span>Sign Out</span>
                </button>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.logo-image { height: 2rem; width: auto; margin-right: 0.5rem; }
.layout-topbar-logo { display: flex; align-items: center; }

.profile-dropdown {
  position: absolute; top: 100%; right: 0; z-index: 1000;
  min-width: 12rem; margin-top: 0.5rem;
  opacity: 0; visibility: hidden; transform: translateY(-10px);
  transition: all 0.2s ease-in-out;
}
.profile-dropdown-visible { opacity: 1; visibility: visible; transform: translateY(0); }
.profile-dropdown-content {
  background: var(--surface-card); border: 1px solid var(--surface-border);
  border-radius: var(--border-radius); box-shadow: var(--shadow-2); padding: 0.5rem 0;
}
.profile-dropdown-item {
  display: flex; align-items: center; width: 100%; padding: 0.75rem 1rem;
  border: none; background: transparent; color: var(--text-color);
  cursor: pointer; transition: background-color 0.2s; text-align: left; gap: 0.5rem;
}
.profile-dropdown-item:hover { background: var(--surface-hover); }
.profile-dropdown-item i { font-size: 0.875rem; }
.profile-dropdown-item span { font-size: 0.875rem; }

/* === Notif dropdown === */
.notif-dropdown {
  position: absolute; right: 0; top: 2.5rem; z-index: 1100;
  width: 20rem; background: var(--surface-card);
  border: 1px solid var(--surface-border);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-2);
}
.notif-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 0.5rem 0.75rem; border-bottom: 1px solid var(--surface-border);
}
.mark-read {
  font-size: .75rem; background: transparent; border: none;
  color: var(--primary-color); cursor: pointer;
}
.notif-list { max-height: 24rem; overflow-y: auto; }
.notif-item {
  padding: 0.5rem 0.75rem; border-bottom: 1px solid var(--surface-border);
}
.notif-item:last-child { border-bottom: 0; }
.notif-title { font-weight: 600; font-size: .9rem; }
.notif-msg { color: var(--text-color-secondary); font-size: .85rem; }
.notif-time { color: var(--text-color-secondary); }
</style>