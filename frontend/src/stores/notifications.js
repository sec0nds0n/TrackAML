// src/stores/notifications.js
import { defineStore } from 'pinia'
import * as api from '@/services/api'

export const useNotifStore = defineStore('notif', {
  state: () => ({
    items: [],      // [{ id, title?, message, created_at, read_at? }]
    unread: 0
  }),
  actions: {
    async fetch() {
      try {
        const res = api.getNotifications ? await api.getNotifications() : []
        this.items = Array.isArray(res) ? res : []
        this.unread = this.items.filter(i => !i.read_at).length
      } catch (e) {
        // silent fail supaya header nggak rusak
      }
    },
    async markAllRead() {
      try { if (api.readNotifications) await api.readNotifications() } catch (e) {}
      const now = new Date().toISOString()
      this.items = this.items.map(i => ({ ...i, read_at: i.read_at || now }))
      this.unread = 0
    },
    // bisa dipanggil saat ada event realtime (websocket) atau setelah post mention
    pushLocal(n) {
      if (!n) return
      if (!n.id) n.id = `tmp-${Date.now()}`
      if (!n.created_at) n.created_at = new Date().toISOString()
      this.items.unshift(n)
      this.unread = (this.unread || 0) + 1
    }
  }
})