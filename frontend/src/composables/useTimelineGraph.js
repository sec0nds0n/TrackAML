import { computed, ref } from 'vue'

export function useTimelineGraph(props) {
  // View state
  const timeRange = ref({
    start: null,
    end: null,
    brushStart: null,
    brushEnd: null
  })

  // Filter state
  const typeFilter = ref('all')
  const riskFilter = ref('all')
  const minAmount = ref(0)
  const maxAmount = ref(Infinity)

  // Animation state
  const isAnimating = ref(false)
  const animationSpeed = ref(1)

  // Computed time scale
  const timeScale = computed(() => {
    const transactions = props.transactions || []
    if (transactions.length === 0) return { min: new Date(), max: new Date() }

    const dates = transactions.map(tx => new Date(tx.timestamp))
    return {
      min: timeRange.value.start || Math.min(...dates),
      max: timeRange.value.end || Math.max(...dates)
    }
  })

  // Filtered transactions
  const filteredTransactions = computed(() => {
    const transactions = props.transactions || []
    return transactions.filter(tx => {
      const matchesType = typeFilter.value === 'all' || tx.type === typeFilter.value
      const matchesRisk = riskFilter.value === 'all' || tx.risk === riskFilter.value
      const matchesAmount = tx.amount >= minAmount.value && tx.amount <= maxAmount.value
      const matchesTimeRange = true // Implement time range filtering if needed
      
      return matchesType && matchesRisk && matchesAmount && matchesTimeRange
    })
  })

  // Timeline layout
  const timelineLayout = computed(() => {
    const margin = { top: 20, right: 20, bottom: 30, left: 40 }
    const width = 800 - margin.left - margin.right
    const height = 400 - margin.top - margin.bottom

    const transactions = filteredTransactions.value
    if (transactions.length === 0) return { width, height, margin, points: [] }

    // Calculate point positions
    const points = transactions.map(tx => {
      const date = new Date(tx.timestamp)
      const x = ((date - timeScale.value.min) / (timeScale.value.max - timeScale.value.min)) * width
      
      // Stack points vertically if they occur at similar times
      const similarTimePoints = transactions.filter(t => 
        Math.abs(new Date(t.timestamp) - date) < 1000 * 60 * 60 // 1 hour threshold
      )
      const index = similarTimePoints.indexOf(tx)
      const y = height - (index * 30) - 20 // Stack with 30px spacing
      
      return {
        ...tx,
        x: x + margin.left,
        y: y + margin.top,
        radius: Math.sqrt(tx.amount) / 2 + 5 // Scale radius by transaction amount
      }
    })

    return { width, height, margin, points }
  })

  // Time axis ticks
  const timelineTicks = computed(() => {
    const { width, margin } = timelineLayout.value
    const numTicks = 6
    const ticks = []
    
    for (let i = 0; i <= numTicks; i++) {
      const date = new Date(
        timeScale.value.min.getTime() +
        (i / numTicks) * (timeScale.value.max.getTime() - timeScale.value.min.getTime())
      )
      
      ticks.push({
        x: (i / numTicks) * width + margin.left,
        label: formatDate(date)
      })
    }
    
    return ticks
  })

  // Methods
  const setTimeRange = (start, end) => {
    timeRange.value.start = start
    timeRange.value.end = end
  }

  const setBrushRange = (start, end) => {
    timeRange.value.brushStart = start
    timeRange.value.brushEnd = end
  }

  const clearBrush = () => {
    timeRange.value.brushStart = null
    timeRange.value.brushEnd = null
  }

  const setFilters = (filters) => {
    if (filters.type !== undefined) typeFilter.value = filters.type
    if (filters.risk !== undefined) riskFilter.value = filters.risk
    if (filters.minAmount !== undefined) minAmount.value = filters.minAmount
    if (filters.maxAmount !== undefined) maxAmount.value = filters.maxAmount
  }

  const toggleAnimation = () => {
    isAnimating.value = !isAnimating.value
    if (isAnimating.value) {
      animateTimeline()
    }
  }

  const setAnimationSpeed = (speed) => {
    animationSpeed.value = Math.max(0.1, Math.min(5, speed))
  }

  const animateTimeline = () => {
    if (!isAnimating.value) return

    const transactions = filteredTransactions.value
    if (transactions.length === 0) return

    let currentIndex = 0
    const animate = () => {
      if (!isAnimating.value) return
      if (currentIndex >= transactions.length) {
        currentIndex = 0
      }

      // Highlight transaction at currentIndex
      const tx = transactions[currentIndex]
      // Implement highlight logic here

      currentIndex++
      setTimeout(animate, 1000 / animationSpeed.value)
    }

    animate()
  }

  // Utility functions
  const formatDate = (date) => {
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: 'numeric'
    }).format(date)
  }

  // Export methods
  const exportData = () => {
    const data = filteredTransactions.value.map(tx => ({
      timestamp: tx.timestamp,
      type: tx.type,
      amount: tx.amount,
      risk: tx.risk,
      hash: tx.hash
    }))

    const csv = [
      ['Timestamp', 'Type', 'Amount', 'Risk', 'Hash'],
      ...data.map(row => [
        row.timestamp,
        row.type,
        row.amount,
        row.risk,
        row.hash
      ])
    ].map(row => row.join(',')).join('\n')

    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    
    const link = document.createElement('a')
    link.href = url
    link.download = 'timeline-data.csv'
    link.click()
    
    URL.revokeObjectURL(url)
  }

  return {
    // State
    timeRange,
    typeFilter,
    riskFilter,
    minAmount,
    maxAmount,
    isAnimating,
    animationSpeed,

    // Computed
    timeScale,
    filteredTransactions,
    timelineLayout,
    timelineTicks,

    // Methods
    setTimeRange,
    setBrushRange,
    clearBrush,
    setFilters,
    toggleAnimation,
    setAnimationSpeed,
    exportData
  }
}
