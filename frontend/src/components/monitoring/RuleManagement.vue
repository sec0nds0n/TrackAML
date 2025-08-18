<template>
    <div class="rule-management-container">
        <!-- Rule Management Header -->
        <div class="rule-header">
            <div class="rule-header-content">
                <div class="rule-title-section">
                    <h2 class="rule-title">Rule Management</h2>
                    <p class="rule-description">Configure and manage detection rules for case</p>
                </div>
            </div>
        </div>

        <!-- Rules Table -->
        <Card>
            <template #title>Heuristic Rules</template>
            <template #content>
                <p class="text-sm text-muted-color mb-3">
                    Wallet risk dihitung berdasarkan beberapa metrik heuristik, seperti banyaknya transaksi masuk/keluar,
                    jumlah alamat unik yang terlibat, total nilai transaksi, dan proporsi aset yang dikirim keluar. 
                    Setiap aturan memiliki bobot (weight) yang menentukan kontribusinya pada skor risiko akhir.
                </p>
                <DataTable :value="rules" dataKey="id" class="w-full" :rowHover="true" responsiveLayout="scroll">
                <Column field="enabled" header="On" style="width: 80px">
                    <template #body="{ data }">
                    <InputSwitch v-model="data.enabled" />
                    </template>
                </Column>
                <Column field="key" header="Metric" />
                <Column field="operator" header="Operator" style="width: 120px" />
                <Column header="Threshold" style="width: 220px">
                    <template #body="{ data }">
                    <div v-if="Array.isArray(data.threshold)" class="flex items-center gap-2">
                        <InputNumber v-model="data.threshold[0]" :min="0" input-class="w-24" />
                        <span>to</span>
                        <InputNumber v-model="data.threshold[1]" :min="0" input-class="w-24" />
                    </div>
                    <div v-else>
                        <InputNumber v-model="data.threshold" :min="0" :maxFractionDigits="6" input-class="w-36" />
                    </div>
                    </template>
                </Column>
                <Column field="weight" header="Weight" style="width: 120px">
                    <template #body="{ data }">
                    <InputNumber v-model="data.weight" :min="0" :max="10" input-class="w-20" />
                    </template>
                </Column>
                <Column field="description" header="Description" />
                <Column header="Actions" style="width: 140px">
                    <template #body="{ data }">
                    <div class="flex gap-2">
                        <Button icon="pi pi-pencil" outlined size="small" @click="openEdit(data)" />
                        <Button icon="pi pi-trash" severity="danger" outlined size="small" @click="removeRule(data)" />
                    </div>
                    </template>
                </Column>
                </DataTable>
            </template>
        </Card>

        <!-- Risk Bands -->
        <Card>
            <template #title>Risk Bands</template>
            <template #content>
                <p class="text-sm text-muted-color mb-2">Map total score → profile. Ordered by <strong>minScore</strong> descending.</p>
                <DataTable :value="bands" dataKey="id" class="w-full" :rowHover="true">
                <Column field="label" header="Label" style="width: 200px">
                    <template #body="{ data }">
                    <InputText v-model="data.label" class="w-full" />
                    </template>
                </Column>
                <Column field="minScore" header="minScore" style="width: 160px">
                    <template #body="{ data }">
                    <InputNumber v-model="data.minScore" :min="0" input-class="w-24" />
                    </template>
                </Column>
                <Column header="Actions" style="width: 120px">
                    <template #body="{ data, index }">
                    <div class="flex gap-2">
                        <Button icon="pi pi-arrow-up" outlined size="small" :disabled="index===0" @click="moveBand(index, -1)" />
                        <Button icon="pi pi-arrow-down" outlined size="small" :disabled="index===bands.length-1" @click="moveBand(index, 1)" />
                        <Button icon="pi pi-trash" severity="danger" outlined size="small" @click="removeBand(index)" />
                    </div>
                    </template>
                </Column>
                </DataTable>
                <div class="mt-3 flex items-center gap-2">
                    <Button label="Add Band" icon="pi pi-plus" outlined @click="addBand" />
                    <Button label="Save Bands" icon="pi pi-save" @click="saveAll" :loading="saving" />
                </div>
            </template>
        </Card>

        <!-- Simulator -->
        <Card>
        <template #title>Quick Simulator</template>
            <template #content>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div v-for="m in metrics" :key="m.key" class="space-y-1">
                    <label class="text-sm font-medium">{{ m.label }}</label>
                    <InputNumber v-model="m.value" :min="0" :maxFractionDigits="6" class="w-full" />
                </div>
                </div>
                <div class="mt-4 flex items-center gap-4">
                <Button label="Compute" icon="pi pi-calculator" @click="runSimulator" />
                <Tag :severity="simResult.severity" :value="`Score: ${simResult.score}`" />
                <Tag :severity="simResult.severity" :value="`Profile: ${simResult.profile}`" />
                </div>
            </template>
        </Card>

        <!-- Add/Edit Dialog -->
        <Dialog v-model:visible="showDialog" modal :header="dialogTitle" :style="{ width: '520px' }">
            <div class="space-y-3">
                <div class="grid grid-cols-3 items-center gap-2">
                <label class="text-sm">Enabled</label>
                <div class="col-span-2"><InputSwitch v-model="form.enabled" /></div>
                </div>
                <div class="grid grid-cols-3 items-center gap-2">
                <label class="text-sm">Metric</label>
                <Dropdown class="col-span-2" v-model="form.key" :options="metricOptions" optionLabel="label" optionValue="key" placeholder="Select metric" />
                </div>
                <div class="grid grid-cols-3 items-center gap-2">
                <label class="text-sm">Operator</label>
                <Dropdown class="col-span-2" v-model="form.operator" :options="operators" placeholder=">, ≥, ≤, between, =" />
                </div>
                <div class="grid grid-cols-3 items-center gap-2">
                <label class="text-sm">Threshold</label>
                <div class="col-span-2">
                    <div v-if="form.operator==='between'" class="flex items-center gap-2">
                    <InputNumber v-model="form.threshold[0]" :min="0" input-class="w-24" />
                    <span>to</span>
                    <InputNumber v-model="form.threshold[1]" :min="0" input-class="w-24" />
                    </div>
                    <div v-else>
                    <InputNumber v-model="form.threshold" :min="0" :maxFractionDigits="6" input-class="w-36" />
                    </div>
                </div>
                </div>
                <div class="grid grid-cols-3 items-center gap-2">
                <label class="text-sm">Weight</label>
                <InputNumber class="col-span-2" v-model="form.weight" :min="0" :max="10" />
                </div>
                <div class="grid grid-cols-3 items-start gap-2">
                <label class="text-sm">Description</label>
                <Textarea class="col-span-2" v-model="form.description" rows="3" autoResize />
                </div>
            </div>
            <template #footer>
                <div class="flex justify-end gap-2">
                <Button label="Cancel" severity="secondary" @click="showDialog=false" />
                <Button label="Save" icon="pi pi-check" @click="saveDialog" />
                </div>
            </template>
        </Dialog>
    </div>
</template>

<script setup>
import Button from 'primevue/button'
import Card from 'primevue/card'
import Dropdown from 'primevue/dropdown'
import InputText from 'primevue/inputtext'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'
import InputSwitch from 'primevue/inputswitch'
import Dialog from 'primevue/dialog'
import Textarea from 'primevue/textarea'
import InputNumber from 'primevue/inputnumber'

import { useAuthStore } from '@/stores/auth';
import { computed, onMounted, ref, watch } from 'vue';
import { useToast } from 'primevue/usetoast'
import api from '@/services/api'

import Tooltip from 'primevue/tooltip'

const toast = useToast()
const authStore = useAuthStore()
// ---------------- Metric Catalog ----------------
const metricOptions = [
  { key: 'outbound_tx', label: 'Outbound TX Count' },
  { key: 'unique_receivers', label: 'Unique Receivers' },
  { key: 'inbound_tx', label: 'Inbound TX Count' },
  { key: 'unique_senders', label: 'Unique Senders' },
  { key: 'total_value', label: 'Total Value (ETH)' },
  { key: 'outbound_ratio', label: 'Outbound Value Ratio' },
]

const operators = ['>', '>=', '<', '<=', 'between', '=']

// ---------------- State ----------------
const rules = ref([])
const bands = ref([
  { id: 1, label: 'High Risk',   minScore: 4 },
  { id: 2, label: 'Medium Risk', minScore: 2 },
  { id: 3, label: 'Low Risk',    minScore: 0 },
])

const showDialog = ref(false)
const dialogTitle = computed(() => (form.value.id ? 'Edit Rule' : 'Add Rule'))
const form = ref({
  id: null,
  enabled: true,
  key: null,
  operator: '>',
  threshold: 0,
  weight: 1,
  description: '',
})
const saving = ref(false)

// ---------------- API helpers ----------------
async function fetchAll() {
  try {
    const data = await api.get('/api/risk-rules') // expected { rules: [], bands: [] }
    rules.value = Array.isArray(data?.rules) ? data.rules : []
    if (Array.isArray(data?.bands) && data.bands.length) bands.value = data.bands
  } catch (e) {
    // Fallback to defaults if API not ready
    loadDefaultRules()
    // toast.add({ severity: 'warn', summary: 'Using defaults', detail: 'Risk rules API not available, using local defaults.', life: 4000 })
  }
}

async function saveAll() {
  try {
    saving.value = true
    const payload = { rules: rules.value, bands: bands.value }
    await api.put('/api/risk-rules', payload)
    toast.add({ severity: 'success', summary: 'Saved', detail: 'Rules & bands saved successfully.' })
  } catch (e) {
    console.error(e)
    // toast.add({ severity: 'error', summary: 'Save failed', detail: e?.data?.message || e?.message || 'Unknown error' })
  } finally {
    saving.value = false
  }
}

// ---------------- CRUD (client-side) ----------------
function openAdd() {
  form.value = { id: null, enabled: true, key: null, operator: '>', threshold: 0, weight: 1, description: '' }
  showDialog.value = true
}
function openEdit(row) {
  form.value = JSON.parse(JSON.stringify(row))
  // normalize between operator threshold to array
  if (form.value.operator === 'between' && !Array.isArray(form.value.threshold)) {
    form.value.threshold = [0, Number(form.value.threshold) || 0]
  }
  showDialog.value = true
}
function saveDialog() {
  const f = form.value
  if (!f.key) return toast.add({ severity: 'warn', summary: 'Validation', detail: 'Metric is required.' })
  if (f.operator === 'between' && (!Array.isArray(f.threshold) || f.threshold.length !== 2)) {
    return toast.add({ severity: 'warn', summary: 'Validation', detail: 'Between requires [min, max].' })
  }
  if (f.id == null) {
    f.id = Date.now()
    rules.value.push({ ...f })
  } else {
    const idx = rules.value.findIndex(r => r.id === f.id)
    if (idx >= 0) rules.value[idx] = { ...f }
  }
  showDialog.value = false
}
function removeRule(row) {
  rules.value = rules.value.filter(r => r.id !== row.id)
}

// ---------------- Bands helpers ----------------
function addBand() {
  bands.value.push({
    id: Date.now() + Math.random(),
    label: 'New Band',
    minScore: 0,
  })
}
function removeBand(i) {
  bands.value.splice(i, 1)
}
function moveBand(i, dir) {
  const j = i + dir
  if (j < 0 || j >= bands.value.length) return
  const tmp = bands.value[i]
  bands.value[i] = bands.value[j]
  bands.value[j] = tmp
}

// ---------------- Defaults (match current heuristic) ----------------
function loadDefaultRules() {
  rules.value = [
    {
      id: 1,
      enabled: true,
      key: 'outbound_tx',
      operator: '>',
      threshold: 50,
      weight: 2,
      description: 'Banyak transaksi keluar',
    },
    {
      id: 2,
      enabled: true,
      key: 'unique_receivers',
      operator: '>',
      threshold: 20,
      weight: 2,
      description: 'Banyak alamat tujuan unik',
    },
    {
      id: 3,
      enabled: true,
      key: 'inbound_tx',
      operator: '>',
      threshold: 50,
      weight: 2,
      description: 'Banyak transaksi masuk',
    },
    {
      id: 4,
      enabled: true,
      key: 'unique_senders',
      operator: '>',
      threshold: 20,
      weight: 2,
      description: 'Banyak alamat sumber unik',
    },
    {
      id: 5,
      enabled: true,
      key: 'total_value',
      operator: '>',
      threshold: 100, // ETH
      weight: 1,
      description: 'Total nilai transaksi besar',
    },
    {
      id: 6,
      enabled: true,
      key: 'outbound_ratio',
      operator: '>=',
      threshold: 0.8, // 80%
      weight: 1,
      description: 'Sebagian besar nilai dikirim keluar',
    },
  ]
  bands.value = [
    { label: 'High Risk', minScore: 4 },
    { label: 'Medium Risk', minScore: 2 },
    { label: 'Low Risk', minScore: 0 },
  ]
}

// ---------------- Simulator ----------------
const metrics = ref([
  { key: 'outbound_tx', label: 'Outbound TX Count', value: 0 },
  { key: 'unique_receivers', label: 'Unique Receivers', value: 0 },
  { key: 'inbound_tx', label: 'Inbound TX Count', value: 0 },
  { key: 'unique_senders', label: 'Unique Senders', value: 0 },
  { key: 'total_value', label: 'Total Value (ETH)', value: 0 },
  { key: 'outbound_ratio', label: 'Outbound Value Ratio', value: 0 },
])

function evaluateRule(rule, values) {
  const v = values[rule.key]
  if (v == null) return false
  switch (rule.operator) {
    case '>': return v > rule.threshold
    case '>=': return v >= rule.threshold
    case '<': return v < rule.threshold
    case '<=': return v <= rule.threshold
    case '=': return Number(v) === Number(rule.threshold)
    case 'between':
      return Array.isArray(rule.threshold) && v >= Number(rule.threshold[0]) && v <= Number(rule.threshold[1])
    default: return false
  }
}

function scoreFromValues(values) {
  let score = 0
  for (const r of rules.value) {
    if (!r.enabled) continue
    if (evaluateRule(r, values)) score += Number(r.weight) || 0
  }
  return score
}

function profileFromScore(score) {
  const sorted = [...bands.value].sort((a, b) => b.minScore - a.minScore)
  const band = sorted.find(b => score >= Number(b.minScore)) || sorted[sorted.length - 1]
  return band?.label || 'Low Risk'
}

const simResult = ref({ score: 0, profile: 'Low Risk', severity: 'info' })
function runSimulator() {
  const values = Object.fromEntries(metrics.value.map(m => [m.key, Number(m.value) || 0]))
  const score = scoreFromValues(values)
  const profile = profileFromScore(score)
  const severity = profile === 'High Risk' ? 'danger' : profile === 'Medium Risk' ? 'warning' : 'success'
  simResult.value = { score, profile, severity }
}

onMounted(fetchAll)
</script>

<style scoped>

/* Rule Header */
.rule-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 20px;
    padding: 2rem;
    margin-bottom: 2rem;
    color: white;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.rule-header-content {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    flex-wrap: wrap;
    gap: 1rem;
}

.rule-title-section {
    flex: 1;
    min-width: 300px;
}

.rule-title {
    font-size: 2rem;
    font-weight: 700;
    margin: 0;
    background: linear-gradient(45deg, #fff, #e0e7ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

@media (max-width: 768px) {
    .rule-management-container {
        padding: 0.5rem;
    }
    
    .rule-header {
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border-radius: 15px;
    }
    
    .rule-header-content {
        flex-direction: column;
        align-items: flex-start;
        gap: 1.5rem;
    }
    
    .rule-title-section {
        min-width: auto;
        width: 100%;
    }
    
    .rule-title {
        font-size: 1.75rem;
    }
    
    .rule-description {
        font-size: 1rem;
    }
    
    .rule-actions {
        width: 100%;
        justify-content: stretch;
    }
    
    .rule-actions .p-button {
        flex: 1;
        justify-content: center;
    }
    
    .rule-filters {
        grid-template-columns: 1fr;
        padding: 1.5rem;
        gap: 1rem;
    }
    
    .table-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 1rem;
    }
    
    .table-actions {
        width: 100%;
        justify-content: stretch;
    }
    
    .table-actions .p-button {
        flex: 1;
        justify-content: center;
    }
    
    .rules-datatable :deep(.p-datatable-wrapper) {
        overflow-x: auto;
    }
    
    .rule-actions-cell {
        flex-direction: column;
        gap: 0.25rem;
    }
    
    .status-cell {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.5rem;
    }
    
    .created-by {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.5rem;
    }
    
    .form-section {
        padding: 1rem;
    }
    
    .conditions-header,
    .actions-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 1rem;
    }
    
    .conditions-header .p-button,
    .actions-header .p-button {
        width: 100%;
    }
    
    .condition-display,
    .action-display {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.5rem;
    }
    
    .test-actions {
        flex-direction: column;
    }
    
    .test-actions .p-button {
        width: 100%;
    }
    
    .rule-overview {
        flex-direction: column;
        gap: 1rem;
    }
    
    .rule-status-info {
        width: 100%;
        justify-content: flex-start;
    }
    
    .rule-metrics {
        grid-template-columns: 1fr;
    }
    
    .config-section {
        grid-template-columns: 1fr;
    }
    
    .dialog-footer {
        flex-direction: column;
        gap: 0.75rem;
    }
    
    .dialog-footer .p-button {
        width: 100%;
    }
}

@media (max-width: 480px) {
    .rule-header {
        padding: 1rem;
    }
    
    .rule-title {
        font-size: 1.5rem;
    }
    
    .rule-filters {
        padding: 1rem;
    }
    
    .rules-datatable :deep(.p-datatable-thead > tr > th),
    .rules-datatable :deep(.p-datatable-tbody > tr > td) {
        padding: 0.75rem 0.5rem;
        font-size: 0.9rem;
    }
    
    .rule-name {
        font-size: 0.9rem;
    }
    
    .rule-id {
        font-size: 0.7rem;
    }
    
    .form-section {
        padding: 0.75rem;
    }
    
    .condition-item,
    .action-item {
        padding: 1rem;
    }
    
    .test-section {
        padding: 1rem;
    }
    
    .rule-details-content {
        padding: 1rem;
    }
    
    .metric-card {
        padding: 1rem;
    }
    
    .metric-value {
        font-size: 1.5rem;
    }
    
    .delete-content {
        padding: 1rem;
    }
    
    .delete-icon {
        font-size: 2rem;
    }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
    .rule-management-container {
        background: linear-gradient(135deg, #1a202c 0%, #2d3748 100%);
    }
    
    .rule-filters,
    .rules-table-container,
    .condition-item,
    .action-item,
    .test-results,
    .rule-details-content {
        background: #2d3748;
        color: #e2e8f0;
        border-color: #4a5568;
    }
    
    .rules-datatable :deep(.p-datatable-thead > tr > th) {
        background: #374151;
        color: #e2e8f0;
    }
    
    .rules-datatable :deep(.p-datatable-tbody > tr:hover) {
        background: #374151;
    }
    
    .filter-dropdown,
    .filter-input {
        background: #374151;
        color: #e2e8f0;
        border-color: #4a5568;
    }
    
    .rule-name,
    .field-label,
    .config-item span,
    .action-details {
        color: #e2e8f0;
    }
    
    .rule-id,
    .last-triggered,
    .rule-info p {
        color: #cbd5e0;
    }
    
    .condition-field {
        background: #4a5568;
        color: #e2e8f0;
    }
    
    .test-textarea {
        background: #1a202c;
        color: #e2e8f0;
        border-color: #4a5568;
    }
}

/* Print styles */
@media print {
    .rule-management-container {
        background: white;
        padding: 0;
    }
    
    .rule-header {
        background: #f8fafc !important;
        color: #2d3748 !important;
        box-shadow: none;
        border: 1px solid #e2e8f0;
    }
    
    .rule-actions,
    .table-actions,
    .rule-actions-cell,
    .conditions-header .p-button,
    .actions-header .p-button,
    .test-actions,
    .dialog-footer {
        display: none !important;
    }
    
    .rule-filters {
        display: none !important;
    }
    
    .rules-datatable :deep(.p-datatable-paginator) {
        display: none !important;
    }
}

/* Apply animations */
.rule-header {
    animation: fadeInUp 0.6s ease-out;
}

/* High contrast mode */
@media (prefers-contrast: high) {
    .rule-header {
        background: #000;
        color: #fff;
        border: 2px solid #fff;
    }
    
    .rule-filters,
    .rules-table-container {
        border: 2px solid #000;
    }
    
    .condition-item,
    .action-item {
        border: 2px solid #000;
    }
    
    .metric-card {
        background: #000 !important;
        color: #fff;
        border: 2px solid #fff;
    }
}

.rule-management-container{
  display: grid;
  grid-auto-flow: row;
  gap: 16px;
  padding: 12px;
}
.section :deep(.p-card){
  border-radius: 12px;
}

</style>
