<script setup>
import { ref, watch, onMounted, onBeforeUnmount, computed } from 'vue'
import { useToast } from 'primevue/usetoast'
import { Network } from 'vis-network/standalone'

const props = defineProps({
  addressData: { type: Object, required: true },
  apiBase:     { type: String, default: 'http://127.0.0.1:5000/api' },
  // UI Hops ditampilkan tapi TIDAK dipakai
  defaultHops: { type: Number, default: 2 }
})

const toast = useToast()
const containerRef = ref(null)
let network = null

const hops = ref(String(props.defaultHops)) // hanya untuk UI
const wallet = computed(() => props.addressData?.address || '')

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
  return new Intl.NumberFormat('en-US', {
    maximumFractionDigits: 8,
    minimumFractionDigits: 0
  }).format(num)
}

async function fetchGraphSummary() {
  const url = `${props.apiBase}/wallets/${encodeURIComponent(wallet.value)}/graph?mode=summary`
  const res = await fetch(url, { headers: { Accept: 'application/json' } })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return await res.json()
}

function draw(payload) {
  const center = wallet.value?.toLowerCase()

  const nodes = payload.nodes.map(n => ({
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

  const edges = payload.edges.map(e => {
    const isLargest = e.etype === 'largest'
    const label = isLargest
      ? `${human(e.value)} ETH`
      : `${e.count} tx • ${human(e.total)} ETH`

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
  if (!wallet.value) return
  try {
    const data = await fetchGraphSummary()
    draw(data)
  } catch (err) {
    console.error(err)
    toast.add({ severity: 'error', summary: 'Graph', detail: `Gagal memuat graph: ${err.message}`, life: 3000 })
  }
}

watch(() => wallet.value, render, { immediate: true })
onMounted(render)
onBeforeUnmount(destroy)
</script>

<template>
  <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
    <div class="flex items-center justify-between mb-4">
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

      <!-- Hops UI (ignored) -->
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

    <div ref="containerRef" style="height: 520px;"></div>
  </div>
</template>

<style scoped>
/* sedikit pemanis agar cocok dengan style sebelumnya */
:deep(.vis-network) {
  border-radius: 0.75rem;
  background-image:
    radial-gradient(#e5e7eb 1px, transparent 1px),
    radial-gradient(#e5e7eb 1px, transparent 1px);
  background-position: 0 0, 10px 10px;
  background-size: 20px 20px;
}
</style>