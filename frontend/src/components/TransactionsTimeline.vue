<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { useToast } from 'primevue/usetoast'
import Chart from 'chart.js/auto'
import zoomPlugin from 'chartjs-plugin-zoom'
Chart.register(zoomPlugin)

const props = defineProps({
  wallet:  { type: String, required: true },
  apiBase: { type: String, default: 'http://127.0.0.1:5000/api' },
  height:  { type: Number, default: 360 }
})

const toast = useToast()
const canvasRef = ref(null)
let chart = null

function destroyChart () { if (chart) { chart.destroy(); chart = null } }

function normalizeTx(tx) {
  if (!tx) return null
  const value = Number(tx.value ?? tx.amount ?? 0)
  const tsRaw = tx.timestamp ?? tx.time ?? tx.block_time ?? tx.blockTime
  const timestamp = typeof tsRaw === 'number'
    ? (tsRaw > 1e12 ? new Date(tsRaw) : new Date(tsRaw * 1000))
    : new Date(String(tsRaw).replace(' ', 'T'))
  return {
    value,
    timestamp: isNaN(timestamp) ? null : timestamp,
    is_anomaly: !!(tx.is_anomaly ?? tx.anomaly ?? tx.isAnomaly)
  }
}

async function fetchAll() {
  const url = `${props.apiBase}/wallets/${encodeURIComponent(props.wallet)}/transactions/all`
  const res = await fetch(url, { headers: { Accept: 'application/json' } })
  if (!res.ok) {
    const msg = `Timeline API gagal (HTTP ${res.status})`
    toast.add({ severity: 'error', summary: 'Timeline', detail: msg, life: 2500 })
    throw new Error(msg)
  }
  const data = await res.json()
  return Array.isArray(data) ? data : (data.transactions || [])
}

function buildDataset(raw) {
  const rows = raw.map(normalizeTx).filter(r => r && r.timestamp)
  rows.sort((a,b) => a.timestamp - b.timestamp)

  const labels = rows.map(r => r.timestamp.toLocaleString())
  const values = rows.map(r => r.value)
  const colors = rows.map(r => (r.is_anomaly ? 'red' : 'blue'))

  return { labels, values, colors }
}

async function render() {
  destroyChart()
  if (!props.wallet) return
  let rows = []
  try { rows = await fetchAll() } catch (e) { return }
  const { labels, values, colors } = buildDataset(rows)

  chart = new Chart(canvasRef.value.getContext('2d'), {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: 'ETH Transactions Over Time',
        data: values,
        pointBackgroundColor: colors,
        pointRadius: 3,
        borderColor: '#9ca3af',
        borderWidth: 2,
        fill: false,
        tension: 0
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: true },
        zoom: {
          pan: { enabled: true, mode: 'x' },
          zoom: { wheel: { enabled: true }, pinch: { enabled: true }, mode: 'x' }
        },
        tooltip: {
          callbacks: { label: (ctx) => ` ${ctx.parsed.y?.toLocaleString()} ETH` }
        }
      },
      scales: {
        x: { title: { display: true, text: 'Time' } },
        y: { title: { display: true, text: 'ETH Transacted' } }
      }
    }
  })
}

watch(() => props.wallet, render, { immediate: true })
onBeforeUnmount(destroyChart)
</script>

<template>
  <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
        Transaction Timeline <span v-if="wallet" class="text-gray-500">for {{ wallet }}</span>
      </h3>
      <div class="text-sm text-gray-500 dark:text-gray-400">Scroll = zoom • Drag = pan</div>
    </div>
    <div :style="{height: `${height}px`}">
      <canvas ref="canvasRef"></canvas>
    </div>
  </div>
</template>