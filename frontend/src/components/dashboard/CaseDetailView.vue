<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { amlCaseService } from '@/services/AMLCaseService'

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const data = ref(null)
const error = ref('')

onMounted(async () => {
  try {
    const id = route.params.id
    data.value = await amlCaseService.getCaseById(id)
  } catch (e) {
    error.value = 'Failed to load case'
    console.error(e)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="p-6">
    <button class="mb-4 text-blue-600" @click="router.back()">← Back</button>
    <div v-if="loading">Loading…</div>
    <div v-else-if="error">{{ error }}</div>
    <div v-else class="space-y-3">
      <h1 class="text-xl font-bold">Case #{{ data.id }}</h1>
      <div class="text-sm text-gray-600">Status: {{ data.status }} | Severity: {{ data.severity }}</div>
      <div class="font-mono">Reference: {{ data.reference_id }}</div>
      <div>Reason: {{ data.reason || '—' }}</div>
      <div>Description: {{ data.description || '—' }}</div>
      <div class="flex flex-wrap gap-2">
        <span v-for="t in data.tags" :key="t" class="px-2 py-1 text-xs bg-gray-100 rounded">#{{ t }}</span>
      </div>
      <div>
        <div class="text-sm text-gray-600 mb-1">Payload</div>
        <pre class="text-xs bg-gray-50 p-3 rounded border overflow-auto">{{ JSON.stringify(data.payload, null, 2) }}</pre>
      </div>
    </div>
  </div>
</template>