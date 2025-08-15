<script setup>
import { computed } from 'vue'

const props = defineProps({
  address: { type: String, required: true },
  riskProfile: { type: String, default: 'Unknown' },
  tags: { type: Array, default: () => [] },
})

const emit = defineEmits(['open-graph', 'check-darkweb'])

const shortAddr = computed(() => {
  const a = props.address || ''
  return a.length > 14 ? `${a.slice(0, 6)}…${a.slice(-4)}` : a
})

function openGraph() { emit('open-graph', props.address) }
function checkDarkweb() { emit('check-darkweb', props.address) }
</script>

<template>
  <div class="rounded-2xl border p-4 space-y-4">
    <div class="flex items-center justify-between">
      <div class="text-sm text-gray-600">Overview</div>
      <div class="text-xs text-gray-500 font-mono">{{ shortAddr }}</div>
    </div>

    <div class="flex items-center gap-2">
      <span class="px-3 py-1 rounded-full bg-gray-100 text-gray-700 text-xs">
        Risk: {{ riskProfile }}
      </span>
      <span
        v-for="t in tags"
        :key="t"
        class="px-2 py-0.5 rounded-full bg-gray-50 border text-xs text-gray-600"
      >
        {{ t }}
      </span>
    </div>

    <div class="flex gap-2">
      <button class="px-3 py-2 rounded-xl border hover:bg-gray-50" @click="openGraph">
        Open Graph
      </button>
      <button class="px-3 py-2 rounded-xl border hover:bg-gray-50" @click="checkDarkweb">
        Check Darkweb
      </button>
    </div>
  </div>
</template>

<style scoped>
/* minimal styling, boleh kamu ganti ke komponen PrimeVue kalau mau */
</style>