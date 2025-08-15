import { computed, ref } from 'vue'

export function useSankeyGraph(props) {
  // View state
  const viewTransform = ref({
    x: 0,
    y: 0,
    scale: 1,
    targetX: 0,
    targetY: 0,
    targetScale: 1
  })

  // Animation state
  const flowAnimationEnabled = ref(true)
  const flowSpeed = ref(1)

  // Computed properties
  const sankeyLayout = computed(() => {
    // Calculate node positions and dimensions
    const nodes = props.nodes.map(node => ({
      ...node,
      x: node.x * viewTransform.value.scale + viewTransform.value.x,
      y: node.y * viewTransform.value.scale + viewTransform.value.y,
      width: node.width * viewTransform.value.scale,
      height: node.height * viewTransform.value.scale
    }))

    // Calculate link paths
    const links = props.links.map(link => {
      const source = nodes[link.source]
      const target = nodes[link.target]
      
      const x0 = source.x + source.width
      const x1 = target.x
      const y0 = source.y + source.height / 2
      const y1 = target.y + target.height / 2
      const xi = (x0 + x1) / 2
      
      return {
        ...link,
        path: `M${x0},${y0}C${xi},${y0} ${xi},${y1} ${x1},${y1}`,
        gradientId: `flow-gradient-${link.source}-${link.target}`
      }
    })

    return { nodes, links }
  })

  // Methods for zoom and pan
  const smoothTransform = () => {
    const dx = viewTransform.value.targetX - viewTransform.value.x
    const dy = viewTransform.value.targetY - viewTransform.value.y
    const dScale = viewTransform.value.targetScale - viewTransform.value.scale
    
    if (Math.abs(dx) < 0.5 && Math.abs(dy) < 0.5 && Math.abs(dScale) < 0.01) {
      viewTransform.value.x = viewTransform.value.targetX
      viewTransform.value.y = viewTransform.value.targetY
      viewTransform.value.scale = viewTransform.value.targetScale
      return
    }
    
    viewTransform.value.x += dx * 0.1
    viewTransform.value.y += dy * 0.1
    viewTransform.value.scale += dScale * 0.1
    
    requestAnimationFrame(smoothTransform)
  }

  const zoomTo = (scale, centerX = 400, centerY = 300) => {
    const currentCenterX = (centerX - viewTransform.value.x) / viewTransform.value.scale
    const currentCenterY = (centerY - viewTransform.value.y) / viewTransform.value.scale
    
    viewTransform.value.targetScale = Math.min(Math.max(0.1, scale), 3)
    viewTransform.value.targetX = centerX - currentCenterX * viewTransform.value.targetScale
    viewTransform.value.targetY = centerY - currentCenterY * viewTransform.value.targetScale
    
    smoothTransform()
  }

  const panTo = (x, y) => {
    viewTransform.value.targetX = x
    viewTransform.value.targetY = y
    smoothTransform()
  }

  // Methods for flow animation
  const getFlowGradient = (link) => {
    if (!flowAnimationEnabled.value) return ''
    
    return `
      <linearGradient id="${link.gradientId}" gradientUnits="userSpaceOnUse"
        x1="${sankeyLayout.value.nodes[link.source].x + sankeyLayout.value.nodes[link.source].width}"
        y1="${sankeyLayout.value.nodes[link.source].y + sankeyLayout.value.nodes[link.source].height / 2}"
        x2="${sankeyLayout.value.nodes[link.target].x}"
        y2="${sankeyLayout.value.nodes[link.target].y + sankeyLayout.value.nodes[link.target].height / 2}">
        <stop offset="0%" stop-color="rgba(255,255,255,0)">
          <animate attributeName="offset" values="0;1" dur="${2/flowSpeed.value}s" repeatCount="indefinite"/>
        </stop>
        <stop offset="50%" stop-color="rgba(255,255,255,0.3)">
          <animate attributeName="offset" values="0;1" dur="${2/flowSpeed.value}s" repeatCount="indefinite"/>
        </stop>
        <stop offset="100%" stop-color="rgba(255,255,255,0)">
          <animate attributeName="offset" values="0;1" dur="${2/flowSpeed.value}s" repeatCount="indefinite"/>
        </stop>
      </linearGradient>
    `
  }

  const toggleFlowAnimation = () => {
    flowAnimationEnabled.value = !flowAnimationEnabled.value
  }

  const setFlowSpeed = (speed) => {
    flowSpeed.value = Math.max(0.1, Math.min(5, speed))
  }

  // Export methods
  const exportAsSVG = () => {
    const svgElement = document.querySelector('#sankey-graph')
    if (!svgElement) return
    
    const serializer = new XMLSerializer()
    const svgString = serializer.serializeToString(svgElement)
    const blob = new Blob([svgString], { type: 'image/svg+xml' })
    const url = URL.createObjectURL(blob)
    
    const link = document.createElement('a')
    link.href = url
    link.download = 'sankey-graph.svg'
    link.click()
    
    URL.revokeObjectURL(url)
  }

  return {
    // State
    viewTransform,
    flowAnimationEnabled,
    flowSpeed,
    sankeyLayout,

    // Methods
    zoomTo,
    panTo,
    getFlowGradient,
    toggleFlowAnimation,
    setFlowSpeed,
    exportAsSVG
  }
}
