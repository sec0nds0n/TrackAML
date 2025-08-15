<script setup>
import { ref, watch, onMounted, onBeforeUnmount, computed, nextTick } from 'vue'
import { useToast } from 'primevue/usetoast'
import { Network } from 'vis-network/standalone'

const props = defineProps({
  addressData: { type: Object, required: true },
  apiBase:     { type: String, default: 'http://127.0.0.1:5000/api' },
  // UI Hops ditampilkan tapi TIDAK dipakai untuk query (sementara)
  defaultHops: { type: Number, default: 2 }
})

/* ---------------- state ---------------- */
const toast = useToast()
const containerRef = ref(null)
let network = null

const currentView = ref('network')
const viewModes = [
  { id: 'network', label: 'Network' },
  { id: 'flow',     label: 'Flow' },
  { id: 'timeline', label: 'Timeline' }
]

const hops = ref(String(props.defaultHops)) // hanya untuk UI
const wallet = computed(() => props.addressData?.address || '')

/* ---------------- utils ---------------- */
function destroy () {
  if (network) { network.destroy(); network = null }
}

function shorten(addr = '', left = 6, right = 4) {
  if (!addr || addr.length <= left + right + 1) return addr
  return addr.slice(0, left) + '…' + addr.slice(-right)
}

function human(n) {
  const num = Number(n)
  if (!isFinite(num)) return '0'
  // Maks 8 desimal, tanpa trailing zero berlebih
  const s = num.toFixed(8)
  return s.replace(/\.?0+$/, '') // buang nol di belakang
}

/* ---------------- API ---------------- */
async function fetchGraphSummary() {
  const url = `${props.apiBase}/wallets/${encodeURIComponent(wallet.value)}/graph?mode=summary`
  const res = await fetch(url, { headers: { Accept: 'application/json' } })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return await res.json()
}

/* ---------------- draw vis-network ---------------- */
function draw(payload) {
  const center = wallet.value?.toLowerCase()

  const nodes = (payload.nodes || []).map(n => ({
    id: n.id,
    label: shorten(n.label || n.id),
    shape: 'dot',
    size: (n.id?.toLowerCase() === center) ? 28 : 18,
    color: (n.id?.toLowerCase() === center)
      ? { background: '#7c3aed', border: '#ede9fe' }
      : { background: '#22c55e', border: '#e5e7eb' },
    borderWidth: 3,
    font: { color: '#111827' }
  }))

  const edges = (payload.edges || []).map(e => {
    const isLargest = e.etype === 'largest'
    const label = isLargest
      ? `${human(e.value)} ${props.addressData?.crypto || ''}`       // biggest
      : `${e.count} tx • ${human(e.total)} ${props.addressData?.crypto || ''}` // most-frequent
    return {
      id: e.id,
      from: e.from,
      to: e.to,
      arrows: 'to',
      label,
      font: { size: 11, align: 'horizontal', color: '#374151' },
      color: { color: isLargest ? '#f87171' : '#f59e0b' },
      width: isLargest ? 3 : 2,
      smooth: { type: 'dynamic' }
    }
  })

  destroy()
  network = new Network(
    containerRef.value,
    { nodes, edges },
    {
      layout: { improvedLayout: true },
      physics: {
        stabilization: true,
        barnesHut: { gravitationalConstant: -30000, springLength: 160, springConstant: 0.02 }
      },
      interaction: {
        hover: true,
        tooltipDelay: 120,
        zoomView: true,
        dragView: true,
        dragNodes: true
      }
    }
  )
}

async function render() {
  if (!wallet.value || currentView.value !== 'network') return
  try {
    const data = await fetchGraphSummary()
    draw(data)
  } catch (err) {
    console.error(err)
    toast.add({ severity: 'error', summary: 'Graph', detail: `Gagal memuat graph: ${err.message}`, life: 3000 })
  }
}

/* ---------------- watchers & lifecycle ---------------- */
watch(() => wallet.value, () => { if (currentView.value === 'network') render() }, { immediate: true })
watch(() => currentView.value, async (v) => {
  if (v === 'network') await nextTick().then(render)
})
onMounted(render)
onBeforeUnmount(destroy)

/* ---------------- derived for Flow tab ---------------- */
const flowSummary = ref({ inTotal: 0, outTotal: 0, biggestPeers: [], frequentPeers: [] })

async function computeFlow() {
  try {
    const payload = await fetchGraphSummary()
    const center = wallet.value?.toLowerCase()
    const edges = payload.edges || []
    const inEdges  = edges.filter(e => String(e.to).toLowerCase()   === center)
    const outEdges = edges.filter(e => String(e.from).toLowerCase() === center)
    const inTotal  = inEdges.reduce((s, e)  => s + Number(e.value || e.total || 0), 0)
    const outTotal = outEdges.reduce((s, e) => s + Number(e.value || e.total || 0), 0)

    const biggestPeers  = edges.filter(e => e.etype === 'largest').slice(0, 3)
    const frequentPeers = edges.filter(e => e.etype === 'frequent').slice(0, 3)

    flowSummary.value = { inTotal, outTotal, biggestPeers, frequentPeers }
  } catch (e) {
    console.error(e)
  }
}

watch(() => currentView.value, (v) => { if (v === 'flow') computeFlow() })
</script>

<template>
  <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-3">
        <div class="p-2 bg-gradient-to-r from-purple-500 to-indigo-500 rounded-lg">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
          </svg>
        </div>
        <div>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Transaction Flow Analysis</h3>
          <p class="text-sm text-gray-500 dark:text-gray-400">Top 3 biggest tx + Top 3 most-frequent peers</p>
        </div>
      </div>

      <!-- Tabs + Hops (Hops diabaikan) -->
      <div class="flex items-center gap-4">
        <div class="flex bg-gray-100 dark:bg-gray-700 rounded-2xl p-1">
          <button
            v-for="view in viewModes"
            :key="view.id"
            @click="currentView = view.id"
            :class="[
              'px-4 py-1 rounded-xl text-sm font-medium transition-colors',
              currentView === view.id
                ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow-sm'
                : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
            ]"
          >
            {{ view.label }}
          </button>
        </div>

        <div class="flex items-center gap-2">
          <label class="text-sm font-medium text-gray-700 dark:text-gray-300">Depth:</label>
          <select
            v-model="hops"
            @change="render"
            class="px-3 py-1 bg-gray-50 dark:bg-gray-700 border border-purple-400 rounded-xl text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            title="Ignored for now"
          >
            <option value="1">1 Hops</option>
            <option value="2">2 Hops</option>
            <option value="3">3 Hops</option>
            <option value="4">4 Hops</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Views -->
    <div v-if="currentView === 'network'">
      <div ref="containerRef" style="height: 520px;"></div>
    </div>

    <div v-else-if="currentView === 'flow'" class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
          <div class="text-sm text-gray-600 dark:text-gray-300 mb-1">Incoming Total</div>
          <div class="text-2xl font-semibold text-gray-900 dark:text-white">
            {{ human(flowSummary.inTotal) }} {{ addressData.crypto }}
          </div>
          <div class="mt-3 h-2 rounded bg-gray-200 dark:bg-gray-700 overflow-hidden">
            <div
              class="h-2 bg-emerald-500"
              :style="{ width: (flowSummary.inTotal + flowSummary.outTotal) ? (100 * flowSummary.inTotal / (flowSummary.inTotal + flowSummary.outTotal)).toFixed(1) + '%' : '0%' }"
            ></div>
          </div>
        </div>
        <div class="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
          <div class="text-sm text-gray-600 dark:text-gray-300 mb-1">Outgoing Total</div>
          <div class="text-2xl font-semibold text-gray-900 dark:text-white">
            {{ human(flowSummary.outTotal) }} {{ addressData.crypto }}
          </div>
          <div class="mt-3 h-2 rounded bg-gray-200 dark:bg-gray-700 overflow-hidden">
            <div
              class="h-2 bg-rose-500"
              :style="{ width: (flowSummary.inTotal + flowSummary.outTotal) ? (100 * flowSummary.outTotal / (flowSummary.inTotal + flowSummary.outTotal)).toFixed(1) + '%' : '0%' }"
            ></div>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
          <div class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Top 3 Biggest</div>
          <ul class="space-y-2">
            <li v-for="e in flowSummary.biggestPeers" :key="e.id" class="flex items-center justify-between">
              <span class="font-mono text-xs truncate">{{ shorten(e.to === wallet?.toLowerCase() ? e.from : e.to) }}</span>
              <span class="text-rose-600 dark:text-rose-400 font-semibold">{{ human(e.value) }} {{ addressData.crypto }}</span>
            </li>
          </ul>
        </div>
        <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
          <div class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Top 3 Most Frequent</div>
          <ul class="space-y-2">
            <li v-for="e in flowSummary.frequentPeers" :key="e.id" class="flex items-center justify-between">
              <span class="font-mono text-xs truncate">{{ shorten(e.to === wallet?.toLowerCase() ? e.from : e.to) }}</span>
              <span class="text-amber-600 dark:text-amber-400 font-semibold">{{ e.count }} tx • {{ human(e.total) }} {{ addressData.crypto }}</span>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <div v-else-if="currentView === 'timeline'" class="bg-gray-50 dark:bg-gray-900 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
      <div class="text-sm text-gray-600 dark:text-gray-300">
        Timeline membutuhkan data transaksi mentah per-event. Pada mode <span class="font-medium">summary</span>,
        endpoint belum menyediakan granularitas tersebut. Jika kamu punya endpoint transaksi (mis. <code>/wallets/:addr/txs</code>),
        kita bisa sambungkan di sini untuk menampilkan sumbu waktu.
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Grid halus ala kertas */
:deep(.vis-network) {
  border-radius: 0.75rem;
  background-image:
    radial-gradient(#e5e7eb 1px, transparent 1px),
    radial-gradient(#e5e7eb 1px, transparent 1px);
  background-position: 0 0, 10px 10px;
  background-size: 20px 20px;
}
/* Tab group feel */
button:focus-visible,
select:focus-visible {
  outline: 2px solid #8b5cf6;
  outline-offset: 2px;
}
</style>