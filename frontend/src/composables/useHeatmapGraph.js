import { onMounted, ref } from 'vue'

export function useHeatmapGraph(props) {
  const heatmapData = ref([])

  // Selected time range or cell
  const selectedCell = ref(null)

  // Generate heatmap data with transactions count and intensity
  const generateHeatmapData = () => {
    const data = []
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

    for (let day = 0; day < 7; day++) {
      for (let hour = 0; hour < 24; hour++) {
        // Calculate transactions count and intensity based on props.transactions
        const transactions = props.transactions || []
        const count = transactions.filter(tx => {
          const date = new Date(tx.timestamp)
          return date.getDay() === day && date.getHours() === hour
        }).length

        const intensity = Math.min(1, count / 20) // Normalize intensity

        data.push({
          day: days[day],
          hour,
          transactions: count,
          intensity
        })
      }
    }

    heatmapData.value = data
  }

  // Color scale for heatmap cells
  const getHeatmapCellColor = (intensity) => {
    if (intensity === 0) return 'bg-gray-200 dark:bg-gray-700'
    if (intensity < 0.2) return 'bg-green-200 dark:bg-green-800'
    if (intensity < 0.4) return 'bg-green-300 dark:bg-green-700'
    if (intensity < 0.6) return 'bg-green-400 dark:bg-green-600'
    if (intensity < 0.8) return 'bg-green-500 dark:bg-green-500'
    return 'bg-green-600 dark:bg-green-400'
  }

  // Select a heatmap cell
  const selectHeatmapCell = (cell) => {
    selectedCell.value = cell
  }

  // Clear selection
  const clearSelection = () => {
    selectedCell.value = null
  }

  // Export heatmap data as CSV
  const exportHeatmapData = () => {
    const csv = [
      ['Day', 'Hour', 'Transactions', 'Intensity'],
      ...heatmapData.value.map(cell => [
        cell.day,
        cell.hour,
        cell.transactions,
        cell.intensity.toFixed(2)
      ])
    ].map(row => row.join(',')).join('\n')

    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)

    const link = document.createElement('a')
    link.href = url
    link.download = 'heatmap-data.csv'
    link.click()

    URL.revokeObjectURL(url)
  }

  onMounted(() => {
    generateHeatmapData()
  })

  return {
    heatmapData,
    selectedCell,
    getHeatmapCellColor,
    selectHeatmapCell,
    clearSelection,
    exportHeatmapData,
    generateHeatmapData
  }
}
