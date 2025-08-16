<script setup>
import { useLayout } from '@/layout/composables/layout';
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useNotifStore } from '@/stores/notifications';
import { useAuthStore } from '@/stores/auth';

const { toggleMenu, toggleDarkMode, isDarkTheme } = useLayout();
useLayout();
const router = useRouter();

const showProfileDropdown = ref(false);
const openNotif = ref(false);
const notifStore = useNotifStore();
const authStore = useAuthStore();
const displayName = computed(() => {
  const u = authStore.user || {};
  return u.username || u.email || 'User';
});
const initials = computed(() => {
  const n = displayName.value.trim();
  return n ? n.split(/\s+/).map(s => s[0]).join('').slice(0,2).toUpperCase() : '?';
});

const toggleProfileDropdown = () => { showProfileDropdown.value = !showProfileDropdown.value; };
const closeProfileDropdown = () => { showProfileDropdown.value = false; };

const handleSignOut = async () => {
  closeProfileDropdown();
  try {
    await authStore.logout?.();
  } finally {
    router.replace('/auth/login');
  }
};

const handleMyProfile = () => {
  console.log('Navigate to profile...');
  closeProfileDropdown();
  router.push('/profile');
};

// load notifikasi saat topbar mount
onMounted(() => {
  // aman kalau endpoint belum ada—biar nggak ganggu UI
  notifStore.fetch?.().catch(() => {});
});
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

          <!-- ========== Bell Notif (ADD) ========== -->
          <div class="relative" v-click-outside="() => (openNotif = false)">
            <button type="button" class="layout-topbar-action relative" @click="openNotif = !openNotif">
              <i class="pi pi-bell"></i>
              <span
                v-if="notifStore.unread"
                class="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full px-1"
              >
                {{ notifStore.unread }}
              </span>
              <span>Notifications</span>
            </button>

            <!-- Dropdown notif -->
            <div
              v-if="openNotif"
              class="notif-dropdown"
            >
              <div class="notif-header">
                <span class="font-medium">Notifications</span>
                <button class="mark-read" @click="notifStore.markAllRead?.()">Mark all read</button>
              </div>

              <ul class="notif-list">
                <li v-if="!notifStore.items?.length" class="px-3 py-4 text-sm text-gray-500">
                  Belum ada notifikasi.
                </li>

                <li
                  v-for="n in notifStore.items"
                  :key="n.id"
                  class="notif-item"
                >
                  <div class="notif-title">{{ n.title || 'Mention' }}</div>
                  <div class="notif-msg">{{ n.message }}</div>
                  <small class="notif-time">{{ new Date(n.created_at).toLocaleString() }}</small>
                </li>
              </ul>
            </div>
          </div>
          <!-- ========== /Bell Notif ========== -->

          <div class="relative" v-click-outside="closeProfileDropdown">
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