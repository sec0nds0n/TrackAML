// src/stores/notifications.js
import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

export const useNotificationStore = defineStore('notifications', () => {
  const items = ref([])
  const unreadCount = ref(0)
  let timer = null
  let running = false // guard agar tak dobel polling

  async function fetchUnread() {
    try {
      const data = await api.get('/api/notifications?unread=1&limit=20')
      items.value = Array.isArray(data) ? data : []
      unreadCount.value = items.value.length
    } catch (e) {
      // bantu debug kalau auth/cors salah
      // eslint-disable-next-line no-console
      console.error('[notifications] fetchUnread error:', e?.status, e?.data || e)
    }
  }

  async function fetchAll() {
    try {
      const data = await api.get('/api/notifications?limit=20')
      items.value = Array.isArray(data) ? data : []
      unreadCount.value = items.value.filter(x => !x.is_read).length
    } catch (e) {
      // eslint-disable-next-line no-console
      console.error('[notifications] fetchAll error:', e?.status, e?.data || e)
    }
  }

  async function markAllRead() {
    try {
      await api.post('/api/notifications', { action: 'mark_all_read' })
      // optimistik: set 0 dulu biar badge responsif
      unreadCount.value = 0
      await fetchAll()
    } catch (e) {
      // eslint-disable-next-line no-console
      console.error('[notifications] markAllRead error:', e?.status, e?.data || e)
    }
  }

  async function startPoll(intervalMs = 15000) {
    if (running) return
    running = true
    stopPoll() // jaga-jaga
    // fetch pertama ditunggu → badge langsung terisi
    await fetchUnread()
    timer = setInterval(() => {
      // pause polling saat tab tidak aktif (hemat & hindari race)
      if (document.visibilityState === 'visible') fetchUnread()
    }, Math.max(3000, intervalMs)) // hard floor 3s biar ga terlalu agresif
  }

  function stopPoll() {
    if (timer) {
      clearInterval(timer)
      timer = null
    }
    running = false
  }

  function reset() {
    stopPoll()
    items.value = []
    unreadCount.value = 0
  }

  return { items, unreadCount, fetchUnread, fetchAll, markAllRead, startPoll, stopPoll, reset }
})
