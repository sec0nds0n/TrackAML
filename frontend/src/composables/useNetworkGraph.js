import { computed, onMounted, reactive, ref } from 'vue'

export function useNetworkGraph({ nodes, edges }) {
  // Initialize node positions
  const nodePositions = reactive({})
  
  // Initialize positions for all nodes
  const initializeNodePositions = () => {
    nodes.forEach((node, index) => {
      const angle = (index / nodes.length) * 2 * Math.PI
      const radius = 150
      const centerX = 400
      const centerY = 200
      
      nodePositions[node.id] = {
        x: centerX + Math.cos(angle) * radius,
        y: centerY + Math.sin(angle) * radius
      }
    })
  }
  
  // Graph state
  const hoveredNode = ref(null)
  const selectedNode = ref(null)
  const searchQuery = ref('')
  const riskFilter = ref('all')
  const typeFilter = ref('all')
  
  // View transform for zoom/pan
  const viewTransform = reactive({
    x: 0,
    y: 0,
    scale: 1
  })
  
  // Connected elements for highlighting
  const connectedElements = reactive({
    nodes: [],
    edges: []
  })
  
  // Context menu
  const contextMenuNode = ref(null)
  const contextMenuPosition = reactive({ x: 0, y: 0 })
  
  // Minimap viewport
  const minimapViewport = reactive({
    x: 0,
    y: 0,
    viewWidth: 100,
    viewHeight: 60,
    scale: 0.2
  })
  
  // Filtered nodes based on search and filters
  const filteredNodes = computed(() => {
    return nodes.filter(node => {
      const matchesSearch = !searchQuery.value || 
        node.label.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
        node.address.toLowerCase().includes(searchQuery.value.toLowerCase())
      
      const matchesRisk = riskFilter.value === 'all' || node.risk === riskFilter.value
      const matchesType = typeFilter.value === 'all' || node.type === typeFilter.value
      
      return matchesSearch && matchesRisk && matchesType
    })
  })
  
  // Utility functions
  const getNodeColor = (type, risk) => {
    const colors = {
      target: '#8b5cf6',
      exchange: '#3b82f6',
      mixer: '#ef4444',
      wallet: '#10b981',
      darknet: '#dc2626',
      defi: '#f59e0b'
    }
    return colors[type] || '#6b7280'
  }
  
  const getNodeSize = (importance) => {
    return Math.max(8, importance * 20)
  }
  
  const getNodeIcon = (type) => {
    const icons = {
      target: '🎯',
      exchange: '🏦',
      mixer: '🌀',
      wallet: '💼',
      darknet: '🕳️',
      defi: '⚡'
    }
    return icons[type] || '●'
  }
  
  const getEdgeColor = (risk) => {
    const colors = {
      Low: '#10b981',
      Medium: '#f59e0b',
      High: '#f97316',
      Critical: '#ef4444'
    }
    return colors[risk] || '#6b7280'
  }
  
  const getEdgeWidth = (amount) => {
    return Math.max(1, Math.log10(amount || 1) * 2)
  }
  
  const getEdgeLength = (edge) => {
    if (!nodePositions[edge.source] || !nodePositions[edge.target]) return 0
    
    const dx = nodePositions[edge.target].x - nodePositions[edge.source].x
    const dy = nodePositions[edge.target].y - nodePositions[edge.source].y
    return Math.sqrt(dx * dx + dy * dy)
  }
  
  // Interaction handlers
  const startDrag = (node, event) => {
    // Implement drag functionality
    console.log('Start drag:', node)
  }
  
  const handleDrag = (event) => {
    // Implement drag handling
  }
  
  const endDrag = () => {
    // Implement drag end
  }
  
  const handleZoom = (event) => {
    const delta = event.deltaY > 0 ? 0.9 : 1.1
    viewTransform.scale = Math.max(0.1, Math.min(3, viewTransform.scale * delta))
  }
  
  const handleKeyNavigation = (event) => {
    // Implement keyboard navigation
  }
  
  const showContextMenu = (event) => {
    contextMenuPosition.x = event.clientX
    contextMenuPosition.y = event.clientY
    // Set contextMenuNode based on clicked element
  }
  
  const hideContextMenu = () => {
    contextMenuNode.value = null
  }
  
  const copyNodeAddress = () => {
    if (contextMenuNode.value) {
      navigator.clipboard.writeText(contextMenuNode.value.address)
    }
    hideContextMenu()
  }
  
  const highlightConnections = () => {
    // Implement connection highlighting
    hideContextMenu()
  }
  
  const expandNode = () => {
    // Implement node expansion
    hideContextMenu()
  }
  
  // Zoom controls
  const zoomIn = () => {
    viewTransform.scale = Math.min(3, viewTransform.scale * 1.2)
  }
  
  const zoomOut = () => {
    viewTransform.scale = Math.max(0.1, viewTransform.scale * 0.8)
  }
  
  const resetView = () => {
    viewTransform.x = 0
    viewTransform.y = 0
    viewTransform.scale = 1
  }
  
  const exportAsSVG = () => {
    // Implement SVG export
    console.log('Export as SVG')
  }
  
  // Initialize on mount
  onMounted(() => {
    initializeNodePositions()
  })
  
  return {
    nodePositions,
    hoveredNode,
    selectedNode,
    searchQuery,
    riskFilter,
    typeFilter,
    viewTransform,
    connectedElements,
    contextMenuNode,
    contextMenuPosition,
    minimapViewport,
    filteredNodes,
    getNodeColor,
    getNodeSize,
    getNodeIcon,
    getEdgeColor,
    getEdgeWidth,
    getEdgeLength,
    startDrag,
    handleDrag,
    endDrag,
    handleZoom,
    handleKeyNavigation,
    showContextMenu,
    hideContextMenu,
    copyNodeAddress,
    highlightConnections,
    expandNode,
    zoomIn,
    zoomOut,
    resetView,
    exportAsSVG
  }
}
