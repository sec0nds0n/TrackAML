<script setup>
import AddressLookup from '@/components/dashboard/AddressLookup.vue'
import { useLayout } from '@/layout/composables/layout'
import { onMounted, ref, watch } from 'vue'

/* Theme watcher */
const { isDarkTheme } = useLayout()
watch(isDarkTheme, () => {})

/* Base URL API
   - set di .env.local -> VITE_API_BASE=http://127.0.0.1:5000/api
   - fallback ke '/api' (pakai proxy Vite jika ada)
*/
const API_BASE = (import.meta.env.VITE_API_BASE ?? '/api').replace(/\/$/, '')
const HISTORY_URL = `${API_BASE}/wallets/history`

/* Recent dari backend */
const recentSearches = ref([])

async function loadRecentSearches() {
  try {
    const res = await fetch(HISTORY_URL)              // ⬅️ tidak pakai credentials
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
    const data = await res.json()
    // bentuk dari backend: [{ address, queried_at }]
    recentSearches.value = (data ?? []).map(r => ({
      address: r.address,
      queried_at: r.queried_at ?? null,
    }))
  } catch (err) {
    console.error('Gagal memuat recent searches:', err)
    recentSearches.value = []
  }
}

onMounted(loadRecentSearches)
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-6 transition-all duration-300">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">Address Lookup</h1>
      <p class="text-gray-600 dark:text-gray-400">
        Search dan lihat “Recent Searches” dari backend
      </p>
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-16 gap-6">
      <div class="xl:col-span-5">
        <AddressLookup
          :recent-searches="recentSearches"
          @reload-recent="loadRecentSearches"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.grid > * { animation: fadeInUp .4s ease-out }
@keyframes fadeInUp { from {opacity:0; transform: translateY(12px)} to {opacity:1; transform:none} }
</style>
