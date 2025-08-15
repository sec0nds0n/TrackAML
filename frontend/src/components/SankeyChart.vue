<template>
  <div class="sankey-container">
    
    <div class="flex items-center justify-between mb-4">
      <h4 class="text-lg font-bold text-gray-900 dark:text-white">Transaction Flow Analysis</h4>
      <div class="flex items-center gap-2">
        <select 
          v-model="selectedCrypto" 
          @change="updateChart"
          class="text-sm border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
        >
          <option value="all">All Cryptocurrencies</option>
          <option value="BTC">Bitcoin (BTC)</option>
          <option value="ETH">Ethereum (ETH)</option>
        </select>
      </div>
    </div>
    
    <div ref="sankeyContainer" class="sankey-chart-wrapper">
      <svg ref="sankeyChart" :width="width" :height="height">
        <!-- Chart will be rendered here -->
      </svg>
    </div>
    
    <!-- Legend -->
    <div class="mt-4 flex flex-wrap gap-4 text-xs">
      <div class="flex items-center gap-2">
        <div class="w-3 h-3 bg-red-500 rounded-sm"></div>
        <span class="text-gray-600 dark:text-gray-300">High Risk</span>
      </div>
      <div class="flex items-center gap-2">
        <div class="w-3 h-3 bg-orange-500 rounded-sm"></div>
        <span class="text-gray-600 dark:text-gray-300">Medium Risk</span>
      </div>
      <div class="flex items-center gap-2">
        <div class="w-3 h-3 bg-green-500 rounded-sm"></div>
        <span class="text-gray-600 dark:text-gray-300">Low Risk</span>
      </div>
      <div class="flex items-center gap-2">
        <div class="w-3 h-3 bg-blue-500 rounded-sm"></div>
        <span class="text-gray-600 dark:text-gray-300">Exchanges</span>
      </div>
      <div class="flex items-center gap-2">
        <div class="w-3 h-3 bg-purple-500 rounded-sm"></div>
        <span class="text-gray-600 dark:text-gray-300">Mixers/Privacy</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { sankey, sankeyLinkHorizontal } from 'd3-sankey'
import * as d3 from 'd3-selection'
import { nextTick, onMounted, onUnmounted, ref, watch } from 'vue'

const props = defineProps({
  data: {
    type: Object,
    default: () => ({})
  }
})

const sankeyContainer = ref(null)
const sankeyChart = ref(null)
const selectedCrypto = ref('all')
const width = ref(800)
const height = ref(400)

// Sample data for crypto AML transaction flows
const sankeyData = ref({
  nodes: [
    // Source nodes (left side)
    { id: 0, name: "Legitimate Wallets", category: "source", risk: "low" },
    { id: 1, name: "Exchanges", category: "source", risk: "low" },
    { id: 2, name: "DeFi Protocols", category: "source", risk: "medium" },
    { id: 3, name: "Unknown Wallets", category: "source", risk: "high" },
    
    // Intermediate nodes (middle)
    { id: 4, name: "Mixing Services", category: "intermediate", risk: "high" },
    { id: 5, name: "Privacy Coins", category: "intermediate", risk: "high" },
    { id: 6, name: "Cross-Chain Bridges", category: "intermediate", risk: "medium" },
    { id: 7, name: "P2P Exchanges", category: "intermediate", risk: "medium" },
    
    // Destination nodes (right side)
    { id: 8, name: "Sanctioned Entities", category: "destination", risk: "critical" },
    { id: 9, name: "Darknet Markets", category: "destination", risk: "critical" },
    { id: 10, name: "Gambling Sites", category: "destination", risk: "high" },
    { id: 11, name: "Legitimate Services", category: "destination", risk: "low" }
  ],
  links: [
    // From sources to intermediates
    { source: 0, target: 6, value: 45.7, crypto: "BTC" },
    { source: 0, target: 7, value: 23.4, crypto: "ETH" },
    { source: 1, target: 4, value: 12.8, crypto: "BTC" },
    { source: 1, target: 6, value: 34.2, crypto: "ETH" },
    { source: 2, target: 5, value: 18.9, crypto: "ETH" },
    { source: 2, target: 7, value: 27.3, crypto: "BTC" },
    { source: 3, target: 4, value: 56.1, crypto: "BTC" },
    { source: 3, target: 5, value: 41.7, crypto: "ETH" },
    
    // From intermediates to destinations
    { source: 4, target: 8, value: 28.4, crypto: "BTC" },
    { source: 4, target: 9, value: 40.5, crypto: "BTC" },
    { source: 5, target: 8, value: 22.1, crypto: "ETH" },
    { source: 5, target: 10, value: 38.5, crypto: "ETH" },
    { source: 6, target: 11, value: 65.3, crypto: "BTC" },
    { source: 6, target: 10, value: 14.6, crypto: "ETH" },
    { source: 7, target: 11, value: 42.8, crypto: "ETH" },
    { source: 7, target: 10, value: 7.9, crypto: "BTC" },
    
    // Direct flows (bypassing intermediates)
    { source: 0, target: 11, value: 89.2, crypto: "BTC" },
    { source: 1, target: 11, value: 156.7, crypto: "ETH" }
  ]
})

const getRiskColor = (risk) => {
  const colors = {
    low: '#10b981',      // green
    medium: '#f59e0b',   // orange
    high: '#ef4444',     // red
    critical: '#dc2626'  // dark red
  }
  return colors[risk] || '#6b7280'
}

const getNodeColor = (node) => {
  if (node.category === 'source') return '#3b82f6'      // blue
  if (node.category === 'intermediate') return '#8b5cf6' // purple
  if (node.category === 'destination') return getRiskColor(node.risk)
  return '#6b7280'
}

const createSankeyChart = () => {
  if (!sankeyChart.value) return

  const svg = d3.select(sankeyChart.value)
  svg.selectAll("*").remove()

  // Filter data based on selected crypto
  let filteredData = { ...sankeyData.value }
  if (selectedCrypto.value !== 'all') {
    filteredData.links = sankeyData.value.links.filter(link => 
      link.crypto === selectedCrypto.value
    )
  }

  // Create sankey generator
  const sankeyGenerator = sankey()
    .nodeWidth(15)
    .nodePadding(10)
    .extent([[1, 1], [width.value - 1, height.value - 6]])

  // Generate the sankey layout
  const { nodes, links } = sankeyGenerator(filteredData)

  // Create gradient definitions
  const defs = svg.append("defs")
  
  links.forEach((link, i) => {
    const gradient = defs.append("linearGradient")
      .attr("id", `gradient-${i}`)
      .attr("gradientUnits", "userSpaceOnUse")
      .attr("x1", link.source.x1)
      .attr("x2", link.target.x0)
    
    gradient.append("stop")
      .attr("offset", "0%")
      .attr("stop-color", getNodeColor(link.source))
      .attr("stop-opacity", 0.6)
    
    gradient.append("stop")
      .attr("offset", "100%")
      .attr("stop-color", getNodeColor(link.target))
      .attr("stop-opacity", 0.6)
  })

  // Add links
  const link = svg.append("g")
    .selectAll("path")
    .data(links)
    .join("path")
    .attr("d", sankeyLinkHorizontal())
    .attr("stroke", (d, i) => `url(#gradient-${i})`)
    .attr("stroke-width", d => Math.max(1, d.width))
    .attr("fill", "none")
    .attr("opacity", 0.7)
    .on("mouseover", function(event, d) {
      d3.select(this).attr("opacity", 1)
      
      // Show tooltip
      const tooltip = d3.select("body").append("div")
        .attr("class", "sankey-tooltip")
        .style("position", "absolute")
        .style("background", "rgba(0, 0, 0, 0.8)")
        .style("color", "white")
        .style("padding", "8px 12px")
        .style("border-radius", "6px")
        .style("font-size", "12px")
        .style("pointer-events", "none")
        .style("z-index", "1000")
        .html(`
          <div><strong>${d.source.name} → ${d.target.name}</strong></div>
          <div>Amount: ${d.value} ${d.crypto || 'Crypto'}</div>
          <div>Risk Level: ${d.target.risk || 'Unknown'}</div>
        `)
        .style("left", (event.pageX + 10) + "px")
        .style("top", (event.pageY - 10) + "px")
    })
    .on("mouseout", function() {
      d3.select(this).attr("opacity", 0.7)
      d3.selectAll(".sankey-tooltip").remove()
    })

  // Add nodes
  const node = svg.append("g")
    .selectAll("rect")
    .data(nodes)
    .join("rect")
    .attr("x", d => d.x0)
    .attr("y", d => d.y0)
    .attr("height", d => d.y1 - d.y0)
    .attr("width", d => d.x1 - d.x0)
    .attr("fill", getNodeColor)
    .attr("stroke", "#000")
    .attr("stroke-width", 0.5)
    .attr("rx", 3)
    .on("mouseover", function(event, d) {
      d3.select(this).attr("opacity", 0.8)
      
      // Highlight connected links
      link.attr("opacity", l => 
        l.source === d || l.target === d ? 1 : 0.3
      )
    })
    .on("mouseout", function() {
      d3.select(this).attr("opacity", 1)
      link.attr("opacity", 0.7)
    })

  // Add node labels
  svg.append("g")
    .selectAll("text")
    .data(nodes)
    .join("text")
    .attr("x", d => d.x0 < width.value / 2 ? d.x1 + 6 : d.x0 - 6)
    .attr("y", d => (d.y1 + d.y0) / 2)
    .attr("dy", "0.35em")
    .attr("text-anchor", d => d.x0 < width.value / 2 ? "start" : "end")
    .attr("font-size", "11px")
    .attr("font-weight", "500")
    .attr("fill", "currentColor")
    .text(d => d.name)
    .style("user-select", "none")

  // Add value labels on nodes
  svg.append("g")
    .selectAll("text")
    .data(nodes.filter(d => d.value > 0))
    .join("text")
    .attr("x", d => (d.x0 + d.x1) / 2)
    .attr("y", d => (d.y0 + d.y1) / 2)
    .attr("dy", "0.35em")
    .attr("text-anchor", "middle")
    .attr("font-size", "9px")
    .attr("font-weight", "bold")
    .attr("fill", "white")
    .text(d => d.value > 10 ? d.value.toFixed(1) : '')
    .style("user-select", "none")
}

const updateChart = () => {
  nextTick(() => {
    createSankeyChart()
  })
}

const handleResize = () => {
  if (sankeyContainer.value) {
    width.value = sankeyContainer.value.clientWidth
    height.value = Math.min(400, width.value * 0.5)
    updateChart()
  }
}

let resizeListener = null

onMounted(() => {
  handleResize()
  createSankeyChart()
  resizeListener = () => handleResize()
  window.addEventListener('resize', resizeListener)
})

onUnmounted(() => {
  if (resizeListener) {
    window.removeEventListener('resize', resizeListener)
  }
})

watch(() => props.data, () => {
  updateChart()
}, { deep: true })
</script>

<style scoped>
.sankey-container {
  width: 100%;
  min-height: 450px;
}

.sankey-chart-wrapper {
  width: 100%;
  overflow-x: auto;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
}

.dark .sankey-chart-wrapper {
  border-color: #374151;
  background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
}

svg {
  display: block;
  margin: 0 auto;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .sankey-chart-wrapper {
    min-height: 300px;
  }
  
  .sankey-container {
    min-height: 350px;
  }
}

@media (max-width: 640px) {
  .flex.flex-wrap.gap-4 {
    gap: 0.5rem;
  }
  
  .text-xs {
    font-size: 0.7rem;
  }
}

/* Tooltip styling */
:global(.sankey-tooltip) {
  font-family: system-ui, -apple-system, sans-serif;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}
</style>