<script setup>
import { ref, watch, onMounted, onBeforeUnmount, computed, nextTick } from 'vue'
import { useToast } from 'primevue/usetoast'
import { Network } from 'vis-network/standalone'
import api from '@/services/api'
import Card from 'primevue/card'
import TabPanel from 'primevue/tabpanel'

const props = defineProps({
  addressData: { type: Object, required: true },
  apiBase:     { type: String, default: 'http://127.0.0.1:5000/api' },

  defaultHops: { type: Number, default: 2 },
  address: { type: String, required: true },
  depth:   { type: Number, default: 2 }
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

// --- Sankey ---
const sankeyEl = ref(null)
let echarts = null
let sankeyChart = null
const sankeyLoading = ref(false)
const sankeyData = ref({ nodes: [], links: [], summary: null })

async function loadSankey() {
  // pakai props.address kalau ada, fallback ke addressData.address
  const target = (props.address || wallet.value || '').trim()
  if (!target) {
    sankeyData.value = { nodes: [], links: [], summary: null }
    return
  }

  sankeyLoading.value = true
  try {
    const base = (props.apiBase || '').replace(/\/$/, '')
    const url = `${base}/aml/addresses/${encodeURIComponent(target)}/flow_sankey?depth=${props.depth}`
    const data = await api.get(url)

    sankeyData.value = data || { nodes: [], links: [], summary: null }

    // gambar hanya kalau panel Flow sedang tampil (sankeyEl sudah ada)
    if (currentView.value === 'flow') {
      if (!sankeyData.value?.links?.length) {
        await loadSankey()
      }
      await nextTick()
      renderSankey()
      // beberapa layout butuh resize setelah visible
      setTimeout(() => sankeyChart && sankeyChart.resize(), 0)
    }
  } catch (e) {
    console.error('loadSankey error', e)
    toast.add({ severity: 'error', summary: 'Failed to load flow', detail: e?.data?.message || e?.message || 'Error', life: 4000 })
  } finally {
    sankeyLoading.value = false
  }
}

function colorForFlag(flag) {
  // keep consistent: blacklisted=red, risky=orange, normal=gray
  if (flag === 'blacklisted') return '#dc3545'
  if (flag === 'risky') return '#fd7e14'
  return '#adb5bd'
}

async function renderSankey() {
  if (!sankeyEl.value) return

  if (!echarts) {
    // register modular agar sinkey pasti ada
    const E = await import('echarts/core')
    const { SankeyChart } = await import('echarts/charts')
    const { TooltipComponent } = await import('echarts/components')
    const { CanvasRenderer } = await import('echarts/renderers')
    E.use([SankeyChart, TooltipComponent, CanvasRenderer])
    echarts = E
  }

  if (sankeyChart) {
    sankeyChart.dispose()
    sankeyChart = null
  }
  sankeyChart = echarts.init(sankeyEl.value)

  const nodes = sankeyData.value.nodes || []
  const links = (sankeyData.value.links || []).map(l => ({
    ...l,
    lineStyle: { color: colorForFlag(l.flag), opacity: 0.6 },
    itemStyle: { color: colorForFlag(l.flag) }
  }))

  sankeyChart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: (p) => p.dataType === 'edge'
        ? `<div style="min-width:220px">
             <div><b>${p.data.source}</b> → <b>${p.data.target}</b></div>
             <div>Value: ${p.data.value} ETH</div>
             <div>Flag: ${p.data.flag}</div>
           </div>`
        : `<b>${p.data.name}</b>`
    },
    series: [{
      type: 'sankey',
      nodeAlign: 'justify',
      draggable: true,
      emphasis: { focus: 'adjacency' },
      label: { color: '#495057' },
      data: nodes,
      links: links,
      lineStyle: { curveness: 0.5 }
    }]
  })
}

function destroySankey() {
  if (sankeyChart) { sankeyChart.dispose(); sankeyChart = null }
}

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
watch(() => wallet.value, () => loadSankey(), { immediate: true })
watch(() => [props.address, props.depth], () => loadSankey())

watch(() => currentView.value, async (v) => {
  if (v === 'network') {
    await nextTick()
    render()
  }
  if (v === 'flow') {
    // data mungkin sudah ada, tinggal render
    await nextTick()
    renderSankey()
    setTimeout(() => sankeyChart && sankeyChart.resize(), 0)
  }
})

onMounted(render)
onMounted(() => {
  window.addEventListener('resize', () => sankeyChart && sankeyChart.resize())
})

onBeforeUnmount(destroy)
onBeforeUnmount(() => {
  destroySankey()
  window.removeEventListener('resize', () => sankeyChart && sankeyChart.resize())
})

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
          <!-- <p class="text-sm text-gray-500 dark:text-gray-400">Top 3 biggest tx + Top 3 most-frequent peers</p> -->
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
        <TabPanel header="Flow">
        <Card>
          <template #content>

            <!-- Sankey Graph -->
            <div class="mt-4" style="height: 420px; width: 100%; position: relative;">
              <div v-if="sankeyLoading" class="flex align-items-center justify-content-center" style="height:100%;">
                Loading flow…
              </div>
              <div v-else-if="(sankeyData.links?.length || 0) > 0" ref="sankeyEl" style="height:100%; width:100%;"></div>
              <div v-else class="h-full flex items-center justify-center text-sm text-gray-500">
                No transactions found for this address.
              </div>
            </div>

            <!-- Legend sederhana -->
            <div class="mt-3 text-sm">
              <span class="mr-3"><span class="inline-block" style="width:12px;height:12px;background:#dc3545;border-radius:2px;display:inline-block;margin-right:6px;"></span>Blacklisted</span>
              <span class="mr-3"><span class="inline-block" style="width:12px;height:12px;background:#fd7e14;border-radius:2px;display:inline-block;margin-right:6px;"></span>High Risk</span>
              <span><span class="inline-block" style="width:12px;height:12px;background:#adb5bd;border-radius:2px;display:inline-block;margin-right:6px;"></span>Normal</span>
            </div>
          </template>
        </Card>
      </TabPanel>
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