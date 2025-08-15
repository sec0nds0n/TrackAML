<script setup>
import { ref, watch, onMounted, onActivated, computed } from 'vue'
import { useToast } from 'primevue/usetoast'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:5000/api'
const props = defineProps({
  addressData: { type: Object, required: true } // { address: '0x...' }
})

const toast = useToast()
const loading = ref(false)
const err = ref('')
const d = ref(null)

const wallet = computed(() => (props.addressData?.address || '').trim().toLowerCase())

async function load() {
  console.log('[Compliance] load() wallet =', wallet.value)
  if (!wallet.value) {
    console.warn('[Compliance] skip: wallet kosong')
    d.value = null
    return
  }
  loading.value = true
  err.value = ''
  d.value = null
  try {
    const res = await fetch(`${API_BASE}/compliance/${encodeURIComponent(wallet.value)}`, {
        headers: { Accept: 'application/json' }
    })
    if (!res.ok) {
      if (res.status === 401) throw new Error('Unauthorized: silakan login.')
      if (res.status === 404) throw new Error('Endpoint /api/compliance tidak ditemukan.')
      throw new Error(`HTTP ${res.status}`)
    }
    const ctype = res.headers.get('content-type') || ''
    if (!ctype.includes('application/json')) {
      const text = await res.text()
      console.warn('[Compliance] Non-JSON response:', text.slice(0,200))
      throw new Error('Response bukan JSON (kemungkinan HTML redirect).')
    }
    const json = await res.json()
    d.value = json
    if (json.wallet_not_found) {
      toast.add({
        severity:'warn',
        summary:'Wallet belum di-fetch',
        detail:`Transaksi untuk ${wallet.value} belum ada.`,
        life:5000
      })
    }
  } catch (e) {
    err.value = String(e?.message || e)
    console.error('[Compliance] load error:', e)
    toast.add({ severity:'error', summary:'Gagal memuat Compliance', detail: err.value, life:6000 })
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  console.log('[Compliance] mounted. wallet =', wallet.value)
  load()
})

onActivated(() => {
  console.log('[Compliance] activated. wallet =', wallet.value)
  load()
})

// Re-fetch ketika address berubah
watch(() => props.addressData?.address, (nv, ov) => {
  console.log('[Compliance] address changed:', ov, '->', nv)
  load()
})

// Biar parent bisa paksa reload saat tab berubah
defineExpose({ reload: load })

const score = computed(() => d.value?.compliance?.score ?? 0)
const bd = computed(() => d.value?.compliance?.breakdown ?? {})
const sanctionsFlag = computed(() => !!(d.value?.is_blacklisted || (d.value?.blacklist_interactions?.length || 0) > 0))

function ringStyle(val) {
  const pct = Math.max(0, Math.min(100, Number(val) || 0))
  return { background: `conic-gradient(#f0b400 ${pct * 3.6}deg, #e5e7eb 0deg)` }
}
</script>

<template>
  <div class="space-y-6">
    <!-- Loading / Error -->
    <div v-if="loading" class="p-6 text-center text-gray-500">Loading compliance…</div>
    <div v-else-if="err" class="p-4 rounded-md bg-red-50 text-red-700">{{ err }}</div>

    <template v-else-if="d">
    <div v-if="d.wallet_not_found" class="p-4 rounded-md bg-yellow-50 text-yellow-700 mb-4">
    ❌ Wallet <span class="font-mono">{{ d.wallet }}</span> belum memiliki data transaksi.
    Silakan lakukan fetch transaksi terlebih dahulu.
    </div>
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Sanctions -->
        <div class="rounded-2xl border p-5">
          <div class="flex items-center gap-2 mb-3">
            <span class="text-lg font-semibold">Sanctions Check</span>
          </div>
          <div v-if="sanctionsFlag" class="p-4 rounded-md bg-red-50 text-red-700">
            ⚠️ Wallet memiliki indikasi terkait sanksi / interaksi dengan blacklist.
            <div v-if="d.is_blacklisted" class="mt-2 text-sm">
              Listed by <b>{{ d.is_blacklisted.source }}</b> — {{ d.is_blacklisted.reason }}
            </div>
          </div>
          <div v-else class="p-4 rounded-md bg-green-50 text-green-700">
            ✅ Tidak ada temuan sanksi/blacklist.
          </div>
        </div>

        <!-- Compliance Score -->
        <div class="rounded-2xl border p-5">
          <div class="flex items-center justify-between">
            <span class="text-lg font-semibold">Compliance Score</span>
            <div class="w-28 h-28 rounded-full grid place-items-center" :style="ringStyle(score)">
              <div class="w-20 h-20 rounded-full bg-white grid place-items-center text-xl font-bold">
                {{ score }}%
              </div>
            </div>
          </div>

          <div class="mt-4 space-y-3">
            <div class="flex items-center gap-3">
              <div class="w-52 text-sm text-gray-600">KYC Compliance</div>
              <div class="flex-1 h-2 bg-gray-200 rounded"><div class="h-2 rounded" :style="{ width: (bd.kyc_compliance||0)+'%' }"></div></div>
              <div class="w-10 text-right text-sm">{{ bd.kyc_compliance || 0 }}%</div>
            </div>
            <div class="flex items-center gap-3">
              <div class="w-52 text-sm text-gray-600">Transaction Monitoring</div>
              <div class="flex-1 h-2 bg-gray-200 rounded"><div class="h-2 rounded" :style="{ width: (bd.transaction_monitoring||0)+'%' }"></div></div>
              <div class="w-10 text-right text-sm">{{ bd.transaction_monitoring || 0 }}%</div>
            </div>
            <div class="flex items-center gap-3">
              <div class="w-52 text-sm text-gray-600">Sanctions Screening</div>
              <div class="flex-1 h-2 bg-gray-200 rounded"><div class="h-2 rounded" :style="{ width: (bd.sanctions_screening||0)+'%' }"></div></div>
              <div class="w-10 text-right text-sm">{{ bd.sanctions_screening || 0 }}%</div>
            </div>
            <div class="flex items-center gap-3">
              <div class="w-52 text-sm text-gray-600">Risk Assessment</div>
              <div class="flex-1 h-2 bg-gray-200 rounded"><div class="h-2 rounded" :style="{ width: (bd.risk_assessment||0)+'%' }"></div></div>
              <div class="w-10 text-right text-sm">{{ bd.risk_assessment || 0 }}%</div>
            </div>
            <div class="flex items-center gap-3">
              <div class="w-52 text-sm text-gray-600">Regulatory Compliance</div>
              <div class="flex-1 h-2 bg-gray-200 rounded"><div class="h-2 rounded" :style="{ width: (bd.regulatory_compliance||0)+'%' }"></div></div>
              <div class="w-10 text-right text-sm">{{ bd.regulatory_compliance || 0 }}%</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Wallet Summary -->
      <div class="rounded-2xl border p-5">
        <div class="flex items-center justify-between mb-4">
          <div class="text-lg font-semibold">Wallet Summary</div>
          <div class="text-sm">
            <span class="mr-2 text-gray-500">Risk Profile:</span>
            <span class="font-semibold"
              :class="{
                'text-red-600': d.risk_profile==='High Risk',
                'text-yellow-600': d.risk_profile==='Medium Risk',
                'text-green-600': d.risk_profile==='Low Risk'
              }"
            >{{ d.risk_profile }}</span>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="rounded-xl border p-4">
            <div class="text-sm text-gray-500">Saldo</div>
            <div class="text-2xl font-semibold mt-1">{{ d.summary?.balance }} ETH</div>
            <div class="mt-3 text-sm">
              <div><b>Total Diterima:</b> {{ d.summary?.total_received }} ETH</div>
              <div><b>Total Dikirim:</b> {{ d.summary?.total_sent }} ETH</div>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="rounded-xl border p-4">
              <div class="text-sm text-gray-500">Transaksi Pertama</div>
              <div class="mt-2 text-sm" v-if="d.summary?.first_transaction">
                <div><b>Sender:</b> {{ d.summary.first_transaction[0] }}</div>
                <div><b>Receiver:</b> {{ d.summary.first_transaction[1] }}</div>
                <div><b>Value:</b> {{ d.summary.first_transaction[2] }} ETH</div>
                <div><b>Time:</b> {{ d.summary.first_transaction[3] }}</div>
              </div>
              <div v-else class="text-gray-500 text-sm">—</div>
            </div>
            <div class="rounded-xl border p-4">
              <div class="text-sm text-gray-500">Transaksi Terakhir</div>
              <div class="mt-2 text-sm" v-if="d.summary?.last_transaction">
                <div><b>Sender:</b> {{ d.summary.last_transaction[0] }}</div>
                <div><b>Receiver:</b> {{ d.summary.last_transaction[1] }}</div>
                <div><b>Value:</b> {{ d.summary.last_transaction[2] }} ETH</div>
                <div><b>Time:</b> {{ d.summary.last_transaction[3] }}</div>
              </div>
              <div v-else class="text-gray-500 text-sm">—</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Alerts ringkas -->
      <div class="rounded-2xl border p-5">
        <div class="text-lg font-semibold mb-3">Status Wallet</div>
        <ul class="space-y-2 text-sm">
          <li v-if="(d.blacklist_interactions?.length||0)>0" class="text-red-600">⚠️ Ada interaksi dengan wallet blacklist</li>
          <li v-else>✅ Tidak ada interaksi dengan wallet blacklist</li>

          <li v-if="(d.risky_interactions?.length||0)>0" class="text-red-600">⚠️ Ada interaksi dengan wallet berisiko tinggi</li>
          <li v-else>✅ Tidak ada interaksi dengan wallet berisiko tinggi</li>

          <li v-if="d.recurring_pattern" class="text-yellow-700">⚠️ {{ d.recurring_pattern }}</li>
          <li v-else>✅ Tidak ada pola transaksi rutin mencurigakan</li>
        </ul>
      </div>

      <!-- Tabel ringkas -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="rounded-2xl border p-5 overflow-auto">
          <div class="text-lg font-semibold mb-3">Top 3 Transaksi Terbesar</div>
          <table class="min-w-full text-sm">
            <thead>
              <tr class="text-left text-gray-500">
                <th class="py-2 pr-4">Sender</th>
                <th class="py-2 pr-4">Receiver</th>
                <th class="py-2 pr-4">Value (ETH)</th>
                <th class="py-2">Timestamp</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="tx in d.top_transactions" :key="tx[0]" class="border-t">
                <td class="py-2 pr-4">{{ tx[1] }}</td>
                <td class="py-2 pr-4">{{ tx[2] }}</td>
                <td class="py-2 pr-4">{{ tx[3] }}</td>
                <td class="py-2">{{ tx[4] }}</td>
              </tr>
              <tr v-if="!d.top_transactions?.length"><td colspan="4" class="py-3 text-gray-500">Tidak ada data</td></tr>
            </tbody>
          </table>
        </div>

        <div class="rounded-2xl border p-5">
          <div class="text-lg font-semibold mb-3">Top Frequent Senders/Receivers</div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <div class="text-sm text-gray-600 mb-2">Top Receivers</div>
              <ul class="text-sm space-y-1">
                <li v-for="r in d.top_receivers" :key="r[0]" class="flex justify-between">
                  <span class="truncate">{{ r[0] }}</span><span class="ml-2 font-medium">{{ r[1] }}</span>
                </li>
                <li v-if="!d.top_receivers?.length" class="text-gray-500">—</li>
              </ul>
            </div>
            <div>
              <div class="text-sm text-gray-600 mb-2">Top Senders</div>
              <ul class="text-sm space-y-1">
                <li v-for="s in d.top_senders" :key="s[0]" class="flex justify-between">
                  <span class="truncate">{{ s[0] }}</span><span class="ml-2 font-medium">{{ s[1] }}</span>
                </li>
                <li v-if="!d.top_senders?.length" class="text-gray-500">—</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer actions (opsional) -->
      <div class="flex items-center justify-between text-xs text-gray-500">
        <div>Last updated: {{ d.last_updated || '—' }}</div>
        <div class="flex gap-2">
          <button class="px-3 py-2 rounded-xl border hover:bg-gray-50" @click="$emit('export', d)">Export Report</button>
          <button class="px-3 py-2 rounded-xl border hover:bg-gray-50" @click="$emit('flag', wallet)">Flag Address</button>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
/* progress bar fill warna default mengikuti tema; cukup biarkan browser yang pilih */
</style>