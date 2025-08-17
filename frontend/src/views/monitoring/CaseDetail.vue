<script setup>
import { useAuthStore } from '@/stores/auth';
import { useCaseStore } from '@/stores/cases';
import { amlCaseService } from '@/services/AMLCaseService';
import Avatar from 'primevue/avatar';
import Button from 'primevue/button';
import Chip from 'primevue/chip';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import Dialog from 'primevue/dialog';
import FileUpload from 'primevue/fileupload';
import InputText from 'primevue/inputtext';
import TabPanel from 'primevue/tabpanel';
import TabView from 'primevue/tabview';
import Tag from 'primevue/tag';
import Textarea from 'primevue/textarea';
import Dropdown from 'primevue/dropdown';
import Timeline from 'primevue/timeline';
import { computed, onMounted, ref, watch, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useToast } from 'primevue/usetoast'
import * as api from '@/services/api'
import { searchUsers } from '@/services/api'


// Stores and routing
const authStore = useAuthStore();
const caseStore = useCaseStore();
const route = useRoute();
const router = useRouter();
const toast = useToast()

const assignDialog = ref(false)
const assignQuery = ref('')
const assignLoading = ref(false)
const assignCandidates = ref([])
const selectedAssignee = ref(null)

// Reactive data
const caseData = ref(null);
const loading = ref(false);
const loadError = ref('');
const showAddNoteDialog = ref(false);
const showUploadDialog = ref(false);
const newNoteContent = ref('');
const documentDescription = ref('');
const selectedFile = ref(null);
const comments = ref([])
const commentBody = ref('')
const commentVis = ref('internal')
const visOptions = ['internal','external']

const commentsLoading = ref(false)
const posting = ref(false)

// Mock data for documents and notes
const documents = ref([
    {
        id: 1,
        name: 'Transaction_Report.pdf',
        type: 'PDF',
        size: '2.5 MB',
        uploadedBy: 'System',
        uploadedAt: new Date()
    },
    {
        id: 2,
        name: 'Wallet_Analysis.docx',
        type: 'DOCX',
        size: '1.2 MB',
        uploadedBy: 'John Doe',
        uploadedAt: new Date(Date.now() - 86400000)
    }
]);

const notes = ref([
    {
        id: 1,
        content: 'Initial review completed. Transaction pattern appears suspicious due to multiple small amounts being transferred in quick succession.',
        user: 'John Doe',
        timestamp: new Date(Date.now() - 3600000)
    },
    {
        id: 2,
        content: 'Requested additional documentation from the customer. Awaiting response.',
        user: 'Jane Smith',
        timestamp: new Date(Date.now() - 7200000)
    }
]);

// Computed properties
const canEscalate = computed(() => {
    return (authStore.isL1Analyst || authStore.isAdmin) && 
           caseData.value?.level === 'L1' && 
           caseData.value?.status !== 'Resolved';
});

const canApprove = computed(() => {
    return authStore.hasPermission('approve') && 
           caseData.value?.status !== 'Resolved';
});

const canReject = computed(() => {
    return authStore.hasPermission('approve') && 
           caseData.value?.status !== 'Resolved';
});

const entityType = computed(() => (caseData?.value?.case_type || '').toLowerCase())
const isTxCase = computed(() => entityType.value.includes('transaction'))

const mainRef = computed(() => caseData.value?.reference_id || '')
const txHash   = computed(() => (isTxCase.value ? mainRef.value : (caseData.value?.payload?.tx_hash || '')))
const fromAddr = computed(() => caseData.value?.payload?.from || caseData.value?.payload?.from_address || '')
const toAddr   = computed(() => caseData.value?.payload?.to || caseData.value?.payload?.to_address || '')
const chain    = computed(() => caseData.value?.payload?.chain || caseData.value?.payload?.network || '')

// Risk
const riskScore = computed(() => caseData.value?.payload?.risk_score ?? null)
const risks = computed(() => caseData.value?.payload?.risks || caseData.value?.risks || [])

function extractMentions(text='') {
  const out = []
  let m
  const r = new RegExp(mentionRegex) // bikin instance baru
  while ((m = r.exec(text)) !== null) {
    out.push(m[2])
  }
  // unikkan
  return [...new Set(out)]
}

function riskSeverity(level) {
  const v = String(level || '').toLowerCase()
  if (v === 'critical' || v === 'very high') return 'danger'
  if (v === 'high') return 'warn'
  if (v === 'medium' || v === 'moderate') return 'info'
  return 'success' // low/unknown
}

const mentionQuery = ref('')
const mentionOpen = ref(false)
const mentionList = ref([])
const textareaRef = ref(null)
let mentionDebounce = null

function getCaretToken(text, caretPos) {
  const left = text.slice(0, caretPos)
  const m = left.match(/(^|\s)@([A-Za-z0-9_.]{1,32})$/)
  return m ? m[2] : null
}

const lastCaretPos = ref(0)

async function loadCandidates() {
  assignLoading.value = true
  try {
    const r = await searchUsers(assignQuery.value || '')
    // kalau mau menonjolkan exchanger: bisa diurutkan
    assignCandidates.value = (r || []).sort((a, b) => {
      const ax = (a.username || '').toLowerCase().includes('exchanger') ? -1 : 0
      const bx = (b.username || '').toLowerCase().includes('exchanger') ? -1 : 0
      return ax - bx || (a.username || '').localeCompare(b.username || '')
    })
  } finally {
    assignLoading.value = false
  }
}

async function doAssign() {
  if (!selectedAssignee.value?.id) return
  try {
    await api.request(`/cases/${route.params.id}/assign`, {
      method: 'POST',
      body: { user_id: selectedAssignee.value.id }
    })
    assignDialog.value = false

    // refresh detail — pakai nama fungsi yang benar
    try { 
      await loadCaseData()
    } catch (e) {
      console.debug('Refresh skipped:', e)
    }

    toast.add({ severity: 'success', summary: 'Assigned', detail: `Case di-assign ke ${selectedAssignee.value.username || 'user'}`, life: 2000 })
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Assign failed', detail: e?.message || 'Gagal assign', life: 2500 })
  }
}

async function onCommentInput(e) {
  const el = e.target; // native textarea dari event input sudah benar
  const caret = el.selectionStart;
  lastCaretPos.value = caret;
  const token = getCaretToken(el.value, caret);

  clearTimeout(mentionDebounce);
  if (!token || token.length < 1) { 
    mentionOpen.value = false;
    mentionList.value = [];
    return;
  }
  mentionDebounce = setTimeout(async () => {
    try {
      const res = await searchUsers(token);
      mentionList.value = res || [];
      mentionOpen.value = mentionList.value.length > 0;
    } catch {
      mentionOpen.value = false;
    }
  }, 150);
}

function getNativeTextarea() {
  return (
    textareaRef.value?.$refs?.input ||
    textareaRef.value?.$el?.querySelector('textarea')
  );
}

async function pickMention(u) {
  const el = getNativeTextarea();
  if (!el) { console.warn('Native textarea not found'); return; }

  // Pakai sumber dari v-model + caret tersimpan
  const full  = commentBody.value ?? '';
  const caret = lastCaretPos.value ?? full.length;

  const left  = full.slice(0, caret);
  const m = left.match(/(^|\s)@([A-Za-z0-9_.]{0,32})$/);
  if (!m) return;

  const prefix   = left.slice(0, m.index + m[1].length);
  const inserted = `@${u.username} `;
  const newLeft  = prefix + inserted;
  const right    = full.slice(caret);
  const nextVal  = newLeft + right;

  // 1) Update v-model dulu (supaya reaktif)
  commentBody.value = nextVal;

  // 2) Sinkronkan native textarea + pancing PrimeVue
  await nextTick();
  el.value = nextVal;
  el.dispatchEvent(new Event('input', { bubbles: true }));

  // 3) Tutup popover & posisikan caret
  mentionOpen.value = false;
  await nextTick();
  const pos = newLeft.length;
  el.focus();
  el.setSelectionRange(pos, pos);

  // 4) Perbarui caret tersimpan
  lastCaretPos.value = pos;
}

const highlighterRef = ref(null)

function escapeHtml(s='') {
  return s
    .replace(/&/g,'&amp;')
    .replace(/</g,'&lt;')
    .replace(/>/g,'&gt;')
    .replace(/"/g,'&quot;')
    .replace(/'/g,'&#39;')
}

const mentionRegex = /(^|[\s(,;[\{])@([A-Za-z0-9_.-]{1,32})\b/g

const highlightedHtml = computed(() => {
  // Escape dulu, baru inject <mark> untuk @mention
  const safe = escapeHtml(commentBody.value || '')
  // Tambahkan \n sentinel supaya tinggi baris sinkron walau baris terakhir kosong
  const colored = safe.replace(mentionRegex, (m, p1, uname) => {
    return `${p1}<mark class="mention">@${uname}</mark>`
  })
  return colored + '\n'
})

function syncScroll(e) {
  // samakan scrollY-nya highlighter dengan textarea
  if (highlighterRef.value) {
    highlighterRef.value.scrollTop = e.target.scrollTop
  }
}

// Methods
function title(x) {
  if (!x) return '';
  return x.charAt(0).toUpperCase() + x.slice(1).toLowerCase();
}

function shortRef(s) {
  if (!s) return '—';
  const x = String(s);
  return x.length > 12 ? `${x.slice(0,6)}...${x.slice(-4)}` : x;
}

function mapCaseToView(c) {
  const payload = c?.payload || {};

  // === NEW: derive owner & assignees by username
  const ownerName = c?.owner?.username || c?.owner_username || (c?.owner_id ? `user#${c.owner_id}` : 'Unassigned');
  const assignees = Array.isArray(c?.assignments) ? c.assignments.map(a => a?.username || `user#${a?.id}`) : [];
  const assignedToDisplay = assignees.length ? assignees.join(', ') : ownerName;

  return {
    id: `CASE-${c.id}`,
    _rawId: c.id,
    title: c?.title || null,
    crypto: (c.payload?.chain) || (String(c.reference_id||'').startsWith('0x') ? 'ETH' : 'BTC'),
    amount: (c.payload?.amount != null) ? `${c.payload.amount} ${ (c.payload?.chain)||'' }` : '—',
    level: c?.payload?.level || 'L1',
    status: c.status,
    riskLevel: c.severity,
    customer: payload.wallet || `${(c?.case_type || 'Wallet')}: ${shortRef(c?.reference_id)}`,
    date: c?.created_at || new Date().toISOString(),
    createdAt: c.created_at,
    updatedAt: c?.updated_at,

    // === UPDATED: gunakan username
    details: {
      description: c.description || c.reason || 'Unknown description',
      assignedTo: assignedToDisplay,
      priority: c.priority,
      typology: c.typology,
      tlp: c.tlp,
      visibility: c.visibility,
      tags: Array.isArray(c.tags) ? c.tags : [],
      reference: c.reference_id,
      caseType: c.case_type,
      slaDue: c.sla_due_at,
    },

    // simpan list agar bisa ditampilkan sebagai chips
    assignees, // <-- ['aph', 'exchanger1', ...]
    activities: Array.isArray(payload.activities) ? payload.activities : []
  };
}

const loadCaseData = async () => {
  const id = route.params.id;
  loading.value = true;
  loadError.value = '';
  try {
    // 1) coba API langsung
    const raw = await amlCaseService.getCaseById(id);     // GET /api/cases/:id
    caseData.value = mapCaseToView(raw);
  } catch (e) {
    console.warn('Case detail API fallback to store:', e);
    // 2) fallback ke store lama (kalau masih ada)
    const fromStore = caseStore.getCaseById?.(id);
    if (fromStore) {
      caseData.value = fromStore;
    } else {
      loadError.value = 'Case not found';
    }
  } finally {
    loading.value = false;
  }
};

const goBack = () => {
  if (window.history.length > 1) router.back();
  else router.push('/monitoring/cases');
};

const escalateCase = async () => {
    try {
        const updatedCase = {
            ...caseData.value,
            level: 'L2',
            status: 'escalated',
            activities: [
                ...caseData.value.activities || [],
                {
                    timestamp: new Date(),
                    action: 'Case Escalated to L2',
                    user: authStore.currentUser?.email || 'Current User',
                    comment: 'Escalated for further review'
                }
            ]
        };

        caseStore.updateCase(caseData.value.id, updatedCase);
        caseData.value = updatedCase;
    } catch (error) {
        console.error('Error escalating case:', error);
    }
};

const approveCase = async () => {
    try {
        const updatedCase = {
            ...caseData.value,
            status: 'Resolved',
            activities: [
                ...caseData.value.activities || [],
                {
                    timestamp: new Date(),
                    action: 'Case Approved',
                    user: authStore.currentUser?.email || 'Current User',
                    comment: 'Case approved and resolved'
                }
            ]
        };

        caseStore.updateCase(caseData.value.id, updatedCase);
        caseData.value = updatedCase;
    } catch (error) {
        console.error('Error approving case:', error);
    }
};

const rejectCase = async () => {
    try {
        const updatedCase = {
            ...caseData.value,
            status: 'Rejected',
            activities: [
                ...caseData.value.activities || [],
                {
                    timestamp: new Date(),
                    action: 'Case Rejected',
                    user: authStore.currentUser?.email || 'Current User',
                    comment: 'Case rejected after review'
                }
            ]
        };

        caseStore.updateCase(caseData.value.id, updatedCase);
        caseData.value = updatedCase;
    } catch (error) {
        console.error('Error rejecting case:', error);
    }
};

const editCase = () => {
    // Navigate to edit case page or open edit dialog
    console.log('Edit case functionality');
};

const addNote = () => {
    if (newNoteContent.value.trim()) {
        notes.value.unshift({
            id: Date.now(),
            content: newNoteContent.value,
            user: authStore.currentUser?.email || 'Current User',
            timestamp: new Date()
        });
        
        newNoteContent.value = '';
        showAddNoteDialog.value = false;
    }
};

const onFileSelect = (event) => {
    selectedFile.value = event.files[0];
};

const uploadDocument = () => {
    if (selectedFile.value) {
        documents.value.unshift({
            id: Date.now(),
            name: selectedFile.value.name,
            type: selectedFile.value.name.split('.').pop().toUpperCase(),
            size: (selectedFile.value.size / 1024 / 1024).toFixed(2) + ' MB',
            uploadedBy: authStore.currentUser?.email || 'Current User',
            uploadedAt: new Date()
        });
        
        selectedFile.value = null;
        documentDescription.value = '';
        showUploadDialog.value = false;
    }
};

const downloadDocument = (document) => {
    console.log('Download document:', document.name);
};

const previewDocument = (document) => {
    console.log('Preview document:', document.name);
};

// Utility functions
const formatDate = (date) => {
    return new Date(date).toLocaleDateString();
};

const formatDateTime = (date) => {
    return new Date(date).toLocaleString();
};

const getDueDate = () => {
    const due = caseData.value?.details?.slaDue;
    if (due) return new Date(due);
    const created = new Date(caseData.value?.createdAt || Date.now());
    return new Date(created.getTime() + 7 * 24 * 60 * 60 * 1000); // fallback 7 days
};

const getInitials = (name) => {
    return name
        ? name
              .split(' ')
              .map(n => n[0])
              .join('')
        : '?';
};

// New methods for enhanced UX
const copyToClipboard = async (text) => {
    try {
        await navigator.clipboard.writeText(text);
        // Show toast notification (you can implement this with PrimeVue Toast)
        console.log('Copied to clipboard:', text);
    } catch (err) {
        console.error('Failed to copy:', err);
    }
};

const exportCase = () => {
    // Export case data as PDF or JSON
    console.log('Exporting case:', caseData.value?.id);
};

const showMoreOptions = () => {
    // Show additional options menu
    console.log('Showing more options');
};

const getTimeElapsed = (date) => {
    if (!date) return 'N/A';
    const now = new Date();
    const created = new Date(date);
    const diffTime = Math.abs(now - created);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return '1 day ago';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.ceil(diffDays / 7)} weeks ago`;
    return `${Math.ceil(diffDays / 30)} months ago`;
};

const getLevelSeverity = (level) => {
    switch (level) {
        case 'L1': return 'info';
        case 'L2': return 'warning';
        default: return 'info';
    }
};

const getStatusSeverity = (status) => {
    switch (status) {
        case 'Under Review': return 'warning';
        case 'Investigating': return 'info';
        case 'Pending': return 'warning';
        case 'Resolved': return 'success';
        case 'Rejected': return 'danger';
        case 'escalated': return 'danger';
        default: return 'info';
    }
};

const getRiskSeverity = (risk) => {
    switch (risk) {
        case 'High': return 'danger';
        case 'Medium': return 'warning';
        case 'Low': return 'success';
        default: return 'info';
    }
};

const getPrioritySeverity = (priority) => {
    const p = String(priority || '').toUpperCase();
    switch (p) {
        case 'P1': return 'danger';
        case 'P2': return 'warning';
        case 'P3': return 'info';
        case 'P4': return 'success';
        case 'HIGH': return 'danger';
        case 'MEDIUM': return 'warning';
        case 'LOW': return 'info';
        default: return 'secondary';
    }
};

const getTlpSeverity = (tlp) => {
    const t = String(tlp || '').toUpperCase();
    switch (t) {
        case 'RED': return 'danger';
        case 'AMBER': return 'warning';
        case 'GREEN': return 'success';
        case 'WHITE': return 'secondary';
        default: return 'info';
    }
};

const getVisibilitySeverity = (v) => {
    return String(v || '').toLowerCase() === 'external' ? 'info' : 'secondary';
};


const getFileIcon = (type) => {
    switch (type.toLowerCase()) {
        case 'pdf': return 'pi pi-file-pdf text-red-500';
        case 'doc':
        case 'docx': return 'pi pi-file-word text-blue-500';
        case 'jpg':
        case 'png': return 'pi pi-image text-green-500';
        default: return 'pi pi-file text-gray-500';
    }
};

const getActivityIcon = (action) => {
    if (action.includes('Created')) return 'pi pi-plus';
    if (action.includes('Escalated')) return 'pi pi-arrow-up';
    if (action.includes('Approved')) return 'pi pi-check';
    if (action.includes('Rejected')) return 'pi pi-times';
    return 'pi pi-circle';
};

const getActivityColor = (action) => {
    if (action.includes('Created')) return '#3B82F6';
    if (action.includes('Escalated')) return '#F59E0B';
    if (action.includes('Approved')) return '#10B981';
    if (action.includes('Rejected')) return '#EF4444';
    return '#6B7280';
};

async function loadComments() {
  commentsLoading.value = true
  try {
    const list = await api.getCaseComments(route.params.id)
    comments.value = (list || []).sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  } catch (e) {
    if (e?.status === 404) {
      // endpoint belum ada → tampilkan empty state, tapi jangan spam toast
      comments.value = []
    } else if (e?.status === 401 || e?.isAuthError) {
      toast.add({ severity: 'warn', summary: 'Auth', detail: 'Sesi berakhir. Silakan login lagi.', life: 2500 })
    } else if (e?.status === 403) {
      toast.add({ severity: 'warn', summary: 'Akses ditolak', detail: 'Anda tidak punya akses ke komentar case ini.', life: 2500 })
    } else {
      toast.add({ severity: 'warn', summary: 'Comments', detail: e?.message || 'Load failed', life: 2000 })
    }
  } finally {
    commentsLoading.value = false
  }
}

async function postComment() {
  const body = commentBody.value.trim()
  if (!body) return
  posting.value = true
  const optimistic = {
    id: `tmp-${Date.now()}`,
    body,
    visibility: commentVis.value,
    created_at: new Date().toISOString()
  }
  comments.value = [optimistic, ...comments.value]
  try {
    const created = await api.addCaseComment(route.params.id, { body, visibility: commentVis.value })
    commentBody.value = ''
    await loadComments()

    // === NEW: notifikasi mention ===
    const usernames = extractMentions(optimistic.body)
    if (usernames.length) {
      // jika API backend belum ada, buatkan endpoint sederhana; ini akan diabaikan kalau 404
      try {
        await api.notifyMentions({
          case_id: route.params.id,
          comment_id: created?.id, // kalau backend balikin id komentar
          usernames
        })
      } catch (err) {
        // jangan keras—anggap optional
        console.debug('notifyMentions skipped:', err?.message || err)
      }
    }
  } catch (e) {
    comments.value = comments.value.filter(c => c.id !== optimistic.id)
    toast.add({ severity: 'error', summary: 'Comment', detail: e?.message || 'Failed', life: 2000 })
  } finally {
    posting.value = false
  }
}

// Copy ke clipboard
async function copyText(txt) {
  try {
    await navigator.clipboard.writeText(String(txt))
    toast.add({ severity: 'success', summary: 'Copied', detail: 'Copied to clipboard', life: 1200 })
  } catch {
    toast.add({ severity: 'warn', summary: 'Copy failed', life: 1500 })
  }
}

function buildExplorerUrl(kind, value, chain) {
  if (!value) return null
  const c = (chain || '').toLowerCase()
  const host =
    c.includes('bsc') ? 'https://bscscan.com' :
    c.includes('polygon') ? 'https://polygonscan.com' :
    'https://etherscan.io'
  return kind === 'tx' ? `${host}/tx/${value}` : `${host}/address/${value}`
}
// Shorten hash/address agar tidak kepanjangan
function shorten(v, head = 10, tail = 6) {
  if (!v) return '-'
  const s = String(v)
  if (s.length <= head + tail + 3) return s
  return `${s.slice(0, head)}…${s.slice(-tail)}`
}

function onCommentKeydown(e) {
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter' && commentBody.value.trim()) {
    e.preventDefault()
    postComment()
  }
}

// Lifecycle
onMounted(loadCaseData);
onMounted(loadComments)

watch(() => route.params.id, () => loadCaseData());
</script>

<template>
    <div class="case-detail-container">
        <!-- Modern Header with Glass Effect -->
        <div class="modern-header">
            <div class="header-backdrop"></div>
            <div class="header-content">
                <!-- Navigation & Title -->
                <div class="nav-section">
                    <Button 
                        icon="pi pi-arrow-left" 
                        class="modern-back-btn"
                        @click="goBack" 
                        severity="secondary"
                        text
                        rounded />
                    <div class="breadcrumb">
                        <span class="breadcrumb-item">Cases</span>
                        <i class="pi pi-chevron-right breadcrumb-separator"></i>
                        <span class="breadcrumb-current">{{ caseData?.id }}</span>
                    </div>
                </div>
                
                <!-- Case Title & Meta -->
                <div class="case-meta-section">
                    <div class="case-title-group">
                        <h1 class="modern-case-id">{{ caseData?.id }} — {{ caseData?.title || shortRef(caseData?.details?.reference) }}</h1>
                        <p class="case-subtitle">{{ caseData?.details?.description }}</p>
                    </div>
                    
                    <!-- Status Pills -->
                    <div class="status-pills">
                        <div class="pill-group">
                            <span class="pill-label">Status</span>
                            <Tag 
                                :value="caseData?.status"
                                :severity="getStatusSeverity(caseData?.status)"
                                class="modern-tag" />
                        </div>
                        <div class="pill-group">
                            <span class="pill-label">Risk</span>
                            <Tag 
                                :value="caseData?.riskLevel"
                                :severity="getRiskSeverity(caseData?.riskLevel)"
                                class="modern-tag" />
                        </div>
                        <div class="pill-group">
                            <span class="pill-label">TLP</span>
                            <Tag 
                                :value="caseData?.details?.tlp"
                                :severity="getTlpSeverity(caseData?.details?.tlp)"
                                class="modern-tag" />
                        </div>
                        <div class="pill-group">
                            <span class="pill-label">Visibility</span>
                            <Tag 
                                :value="caseData?.details?.visibility"
                                :severity="getVisibilitySeverity(caseData?.details?.visibility)"
                                class="modern-tag" />

                        </div>
                    </div>
                </div>

                <!-- Action Bar -->
                <div class="action-bar">
                    <div class="action-group primary-actions">
                        <Button
                            v-if="authStore.isL1Analyst || authStore.isL2Analyst || authStore.isExchanger || authStore.isAdmin"
                            label="Assign / Escalate"
                            icon="pi pi-user-plus"
                            size="small"
                            class="action-btn"
                            @click="assignDialog = true; loadCandidates()"
                        />
                    </div>
                    <div class="action-group secondary-actions">
                        <Button 
                            icon="pi pi-pencil"
                            severity="secondary"
                            size="small"
                            outlined
                            rounded
                            v-tooltip.top="'Edit Case'"
                            @click="editCase"
                            v-if="authStore.hasPermission('write')" />
                        <Button 
                            icon="pi pi-download"
                            severity="secondary"
                            size="small"
                            outlined
                            rounded
                            v-tooltip.top="'Export Case'"
                            @click="exportCase" />
                        <Button 
                            icon="pi pi-ellipsis-v"
                            severity="secondary"
                            size="small"
                            outlined
                            rounded
                            v-tooltip.top="'More Options'"
                            @click="showMoreOptions" />
                    </div>
                </div>
            </div>
        </div>

        <!-- Key Metrics Cards -->
        <div class="metrics-grid">
            <div class="metric-card crypto-metric">
                <div class="metric-icon">
                    <i class="pi pi-bitcoin"></i>
                </div>
                <div class="metric-content">
                    <div class="metric-value">{{ caseData?.crypto }}</div>
                    <div class="metric-label">Cryptocurrency</div>
                </div>
                <div class="metric-trend">
                    <i class="pi pi-arrow-up trend-icon positive"></i>
                </div>
            </div>
            
            <div class="metric-card amount-metric">
                <div class="metric-icon">
                    <i class="pi pi-dollar"></i>
                </div>
                <div class="metric-content">
                    <div class="metric-value">{{ caseData?.amount }}</div>
                    <div class="metric-label">Transaction Amount</div>
                </div>
                <div class="metric-progress">
                    <div class="progress-bar" style="width: 75%"></div>
                </div>
            </div>
            
            <div class="metric-card analyst-metric">
                <div class="metric-icon">
                    <Avatar 
                        :label="getInitials(caseData?.details?.assignedTo)"
                        size="small"
                        shape="circle"
                        class="analyst-avatar" />
                </div>
                <div class="metric-content">
                    <div class="metric-value">{{ caseData?.details?.assignedTo }}</div>
                    <div class="metric-label">Assigned Analyst</div>
                </div>
                <div class="metric-status online"></div>
            </div>
            
            <div class="metric-card timeline-metric">
                <div class="metric-icon">
                    <i class="pi pi-clock"></i>
                </div>
                <div class="metric-content">
                    <div class="metric-value">{{ getTimeElapsed(caseData?.date) }}</div>
                    <div class="metric-label">Time Elapsed</div>
                </div>
                <div class="metric-urgency">
                    <span class="urgency-indicator medium"></span>
                </div>
            </div>
        </div>

        <!-- Main Content -->
        <div class="main-content">
            <!-- Primary Content Area -->
            <div class="content-main">
                <!-- Enhanced Tabs -->
                <div class="modern-tabs-container">
                    <TabView class="modern-tabview">
                        <TabPanel header="Comments">
                            <section class="card mt-4">
                                <div class="card-header">Discussion</div>
                                    <div class="card-body">
                                    <div class="flex flex-col md:flex-row gap-2">
                                        <div class="relative w-full">
                                            <!-- Layer bawah: highlighter -->
                                            <pre
                                                ref="highlighterRef"
                                                class="mention-highlighter"
                                                aria-hidden="true"
                                                v-html="highlightedHtml"
                                            ></pre>

                                            <!-- Layer atas: textarea PrimeVue -->
                                            <Textarea
                                                ref="textareaRef"
                                                v-model="commentBody"
                                                rows="3"
                                                autoResize
                                                class="w-full mention-textarea"
                                                placeholder="Tulis komentar… pakai @username untuk mention"
                                                @input="onCommentInput"
                                                @keydown="onCommentKeydown"
                                                @scroll="syncScroll"
                                            />

                                            <!-- Mention popover -->
                                            <div
                                            v-if="mentionOpen"
                                            class="mention-popover absolute left-0 mt-1 w-64 max-h-60 overflow-y-auto
                                                bg-white border rounded-md shadow-lg"
                                            :style="{ zIndex: 2147483647, pointerEvents: 'auto' }"
                                            @pointerdown.stop
                                            >
                                                <ul class="divide-y">
                                                    <li
                                                        v-for="u in mentionList"
                                                        :key="u.id ?? u.username"
                                                        class="px-3 py-2 cursor-pointer hover:bg-gray-100 text-sm"
                                                        @pointerdown.prevent.stop="pickMention(u)"
                                                        @mousedown.prevent.stop="pickMention(u)"
                                                        @click.prevent.stop="pickMention(u)"
                                                        tabindex="0"
                                                        @keydown.enter.prevent.stop="pickMention(u)"
                                                    >
                                                        <span class="font-medium">@{{ u.username }}</span>
                                                    </li>
                                                </ul>
                                            </div>
                                        </div>

                                        
                                        <div class="flex items-start gap-2">
                                        <Dropdown v-model="commentVis" :options="visOptions" class="min-w-12rem" />
                                        <Button label="Post" @click="postComment" :loading="posting" :disabled="posting || !commentBody.trim()" />
                                        </div>
                                    </div>

                                    <!-- skeleton saat loading -->
                                    <div v-if="commentsLoading" class="mt-3 space-y-2">
                                        <div class="animate-pulse h-4 w-3/4 surface-300 rounded"></div>
                                        <div class="animate-pulse h-4 w-2/3 surface-300 rounded"></div>
                                        <div class="animate-pulse h-4 w-1/2 surface-300 rounded"></div>
                                    </div>

                                    <div v-else-if="!comments.length" class="text-sm text-color-secondary mt-3">
                                        Belum ada komentar.
                                    </div>

                                    <ul v-else class="mt-3 space-y-2">
                                        <li v-for="c in comments" :key="c.id" class="border-b surface-border pb-2">
                                        <div class="text-sm text-color-secondary">
                                            #{{ c.id }} • {{ c.created_at }} •
                                            <Tag severity="secondary" :value="c.visibility" />
                                        </div>
                                        <div class="mt-1 whitespace-pre-line">{{ c.body }}</div>
                                        </li>
                                    </ul>
                                </div>
                            </section>
                        </TabPanel>
                        <!-- Documents Tab -->
                        <TabPanel header="Documents">
                            <div class="tab-content">
                                <div class="section-header">
                                    <h3>Case Documents</h3>
                                    <Button 
                                        icon="pi pi-upload" 
                                        label="Upload Document" 
                                        size="small"
                                        @click="showUploadDialog = true"
                                        v-if="authStore.hasPermission('write')" />
                                </div>
                                
                                <div class="documents-table">
                                    <DataTable 
                                        :value="documents" 
                                        class="modern-datatable"
                                        :paginator="true"
                                        :rows="10"
                                        responsiveLayout="scroll">
                                        <Column field="name" header="Document Name">
                                            <template #body="slotProps">
                                                <div class="document-name">
                                                    <i :class="getFileIcon(slotProps.data.type)"></i>
                                                    <span>{{ slotProps.data.name }}</span>
                                                </div>
                                            </template>
                                        </Column>
                                        <Column field="type" header="Type">
                                            <template #body="slotProps">
                                                <Tag :value="slotProps.data.type" severity="info" />
                                            </template>
                                        </Column>
                                        <Column field="size" header="Size"></Column>
                                        <Column field="uploadedBy" header="Uploaded By"></Column>
                                        <Column field="uploadedAt" header="Upload Date">
                                            <template #body="slotProps">
                                                {{ formatDateTime(slotProps.data.uploadedAt) }}
                                            </template>
                                        </Column>
                                        <Column header="Actions">
                                            <template #body="slotProps">
                                                <div class="document-actions">
                                                    <Button 
                                                        icon="pi pi-download" 
                                                        severity="secondary"
                                                        text
                                                        rounded
                                                        size="small"
                                                        @click="downloadDocument(slotProps.data)"
                                                        v-tooltip.top="'Download'" />
                                                    <Button 
                                                        icon="pi pi-eye" 
                                                        severity="info"
                                                        text
                                                        rounded
                                                        size="small"
                                                        @click="previewDocument(slotProps.data)"
                                                        v-tooltip.top="'Preview'" />
                                                </div>
                                            </template>
                                        </Column>
                                    </DataTable>
                                </div>
                            </div>
                        </TabPanel>

                        <!-- Activity Timeline Tab -->
                        <TabPanel header="Activity Timeline">
                            <div class="tab-content">
                                <div class="section-header">
                                    <h3>Case Activity</h3>
                                </div>
                                <div class="timeline-container">
                                    <Timeline :value="caseData?.activities || []" class="custom-timeline">
                                        <template #marker="slotProps">
                                            <div class="timeline-marker"
                                                 :style="{ backgroundColor: getActivityColor(slotProps.item.action) }">
                                                <i :class="getActivityIcon(slotProps.item.action)"></i>
                                            </div>
                                        </template>
                                        <template #content="slotProps">
                                            <div class="timeline-content">
                                                <div class="timeline-action">{{ slotProps.item.action }}</div>
                                                <div class="timeline-meta">
                                                    by {{ slotProps.item.user }} • {{ formatDateTime(slotProps.item.timestamp) }}
                                                </div>
                                                <div v-if="slotProps.item.comment" 
                                                     class="timeline-comment">
                                                    {{ slotProps.item.comment }}
                                                </div>
                                            </div>
                                        </template>
                                    </Timeline>
                                </div>
                            </div>
                        </TabPanel>

                        <!-- Notes Tab -->
                        <TabPanel header="Notes">
                            <div class="tab-content">
                                <div class="section-header">
                                    <h3>Case Notes</h3>
                                    <Button 
                                        icon="pi pi-plus" 
                                        label="Add Note" 
                                        size="small"
                                        @click="showAddNoteDialog = true"
                                        v-if="authStore.hasPermission('write')" />
                                </div>

                                <div class="notes-container">
                                    <div v-for="note in notes" 
                                         :key="note.id"
                                         class="note-item">
                                        <div class="note-header">
                                            <div class="note-author">
                                                <Avatar 
                                                    :label="getInitials(note.user)"
                                                    size="small"
                                                    shape="circle" 
                                                    class="note-avatar" />
                                                <span class="author-name">{{ note.user }}</span>
                                            </div>
                                            <small class="note-timestamp">{{ formatDateTime(note.timestamp) }}</small>
                                        </div>
                                        <div class="note-content">{{ note.content }}</div>
                                    </div>
                                </div>
                            </div>
                        </TabPanel>
                    </TabView>
                </div>
            </div>

            <!-- Right Column - Case Metadata -->
            <div class="content-right">
                <!-- Case Status Card -->
                <div class="metadata-card status-card">
                    <div class="card-header">
                        <h4>Case Status</h4>
                    </div>
                    <div class="card-body">
                        <div class="status-item">
                            <span class="status-label">Current Status</span>
                            <Tag 
                                :value="caseData?.status"
                                :severity="getStatusSeverity(caseData?.status)" />
                        </div>
                        <div class="status-item">
                            <span class="status-label">Priority Level</span>
                            <Tag 
                                :value="caseData?.details?.priority"
                                :severity="getPrioritySeverity(caseData?.details?.priority)" />
                        </div>
                        <div class="status-item">
                            <span class="status-label">Risk Level</span>
                            <Tag 
                                :value="caseData?.riskLevel"
                                :severity="getRiskSeverity(caseData?.riskLevel)" />
                        </div>
                        <div class="status-item">
                            <span class="status-label">TLP</span>
                            <Tag 
                                :value="caseData?.details?.tlp"
                                :severity="getTlpSeverity(caseData?.details?.tlp)" />
                        </div>
                        <div class="status-item">
                            <span class="status-label">Visibility</span>
                            <Tag 
                                :value="caseData?.details?.visibility"
                                :severity="getVisibilitySeverity(caseData?.details?.visibility)" />
                        </div>
                        <div class="status-item">
                            <span class="status-label">SLA Due</span>
                            <span class="timeline-value due-date">{{ formatDateTime(caseData?.details?.slaDue || getDueDate()) }}</span>
                        </div>
                    </div>
                </div>

                <!-- Assignment Card -->
                <div class="metadata-card assignment-card">
                    <div class="card-header">
                        <h4>Assignment</h4>
                    </div>
                    <div class="card-body">
                        <div class="assignment-item">
                        <label>Assigned To</label>

                        <!-- Tampilkan daftar assignee sebagai chips bila ada -->
                        <div v-if="Array.isArray(caseData?.assignees) && caseData.assignees.length" class="flex flex-wrap gap-2">
                            <Tag
                            v-for="u in caseData.assignees"
                            :key="u"
                            :value="u"
                            severity="info"
                            rounded
                            />
                        </div>

                        <!-- Fallback: single display string -->
                        <div v-else class="assignee-info">
                            <Avatar 
                            :label="getInitials(caseData?.details?.assignedTo)"
                            size="small"
                            shape="circle" />
                            <span class="ml-2">{{ caseData?.details?.assignedTo }}</span>
                        </div>
                        </div>

                        <div class="assignment-item">
                        <label>Review Level</label>
                        <div class="review-level">{{ caseData?.level }} Review</div>
                        </div>
                    </div>
                </div>

                <!-- Timeline Card -->
                <div class="metadata-card timeline-card">
                    <div class="card-header">
                        <h4>Timeline</h4>
                    </div>
                    <div class="card-body">
                        <div class="timeline-item">
                            <label>Created</label>
                            <div class="timeline-value">{{ formatDateTime(caseData?.createdAt) }}</div>
                        </div>
                        <div class="timeline-item">
                            <label>Last Updated</label>
                            <div class="timeline-value">{{ formatDateTime(caseData?.updatedAt || new Date()) }}</div>
                        </div>
                        <div class="timeline-item">
                            <label>Due Date</label>
                            <div class="timeline-value due-date">{{ formatDate(getDueDate()) }}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <!-- === Assign / Escalate Dialog === -->
        <Dialog v-model:visible="assignDialog" header="Assign / Escalate Case" modal
                :style="{ width: '90vw', maxWidth: '520px' }">
        <div class="p-fluid">
            <div class="field">
            <Dropdown
                :options="assignCandidates"
                v-model="selectedAssignee"
                optionLabel="username"
                placeholder="Pilih user"
                :loading="assignLoading"
                class="w-full"
            />
            </div>
            <div class="flex justify-end gap-2 mt-3">
            <Button label="Batal" text @click="assignDialog=false" />
            <Button label="Assign" @click="doAssign" :disabled="!selectedAssignee" />
            </div>
        </div>
        </Dialog>
        <!-- Add Note Dialog -->
        <Dialog 
            v-model:visible="showAddNoteDialog" 
            header="Add Note" 
            :modal="true" 
            class="note-dialog"
            :style="{ width: '90vw', maxWidth: '500px' }">
            <div class="dialog-content">
                <div class="field">
                    <label for="noteContent" class="field-label">Note Content</label>
                    <Textarea 
                        id="noteContent" 
                        v-model="newNoteContent" 
                        rows="4" 
                        class="w-full"
                        placeholder="Enter your note..." />
                </div>
            </div>
            
            <template #footer>
                <div class="dialog-footer">
                    <Button 
                        label="Cancel" 
                        icon="pi pi-times" 
                        @click="showAddNoteDialog = false" 
                        severity="secondary"
                        outlined />
                    <Button 
                        label="Add Note" 
                        icon="pi pi-check" 
                        @click="addNote" 
                        :disabled="!newNoteContent.trim()" />
                </div>
            </template>
        </Dialog>

        <!-- Upload Document Dialog -->
        <Dialog 
            v-model:visible="showUploadDialog" 
            header="Upload Document" 
            :modal="true" 
            class="upload-dialog"
            :style="{ width: '90vw', maxWidth: '500px' }">
            <div class="dialog-content">
                <div class="field">
                    <label class="field-label">Select File</label>
                    <FileUpload 
                        mode="basic" 
                        name="document" 
                        :maxFileSize="10000000"
                        accept=".pdf,.doc,.docx,.jpg,.png"
                        @select="onFileSelect"
                        class="custom-file-upload" />
                </div>
                <div class="field">
                    <label for="docDescription" class="field-label">Description</label>
                    <InputText 
                        id="docDescription" 
                        v-model="documentDescription" 
                        class="w-full"
                        placeholder="Document description..." />
                </div>
            </div>
            
            <template #footer>
                <div class="dialog-footer">
                    <Button 
                        label="Cancel" 
                        icon="pi pi-times" 
                        @click="showUploadDialog = false" 
                        severity="secondary"
                        outlined />
                    <Button 
                        label="Upload" 
                        icon="pi pi-upload" 
                        @click="uploadDocument" 
                        :disabled="!selectedFile" />
                </div>
            </template>
        </Dialog>
    </div>
</template>

<style scoped>
/* Modern Container */
.case-detail-container {
    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 50%, #f1f5f9 100%);
    min-height: 100vh;
    padding: 1.5rem;
    color: #1e293b;
    max-width: 1400px;
    margin: 0 auto;
}
:deep(.p-inputtextarea) {
  position: relative;
  z-index: 0;
}

.mention-popover {
  pointer-events: auto;
}

/* Modern Header with Glass Effect */
.modern-header {
    position: relative;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px) saturate(180%);
    border: 1px solid rgba(255, 255, 255, 0.25);
    border-radius: 24px;
    margin-bottom: 2rem;
    box-shadow: 
        0 25px 50px -12px rgba(0, 0, 0, 0.1),
        0 0 0 1px rgba(255, 255, 255, 0.05),
        inset 0 1px 0 rgba(255, 255, 255, 0.1);
    overflow: hidden;
}

.header-backdrop {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: 
        radial-gradient(circle at 20% 50%, rgba(59, 130, 246, 0.03) 0%, transparent 50%),
        radial-gradient(circle at 80% 20%, rgba(139, 92, 246, 0.03) 0%, transparent 50%);
    z-index: 0;
}

.header-content {
    position: relative;
    z-index: 1;
    padding: 2rem;
}

/* Navigation */
.nav-section {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1.5rem;
}

.modern-back-btn {
    background: rgba(59, 130, 246, 0.08) !important;
    color: #3b82f6 !important;
    border: 1px solid rgba(59, 130, 246, 0.15) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    backdrop-filter: blur(10px);
}

.modern-back-btn:hover {
    background: rgba(59, 130, 246, 0.15) !important;
    transform: translateX(-2px);
    box-shadow: 0 8px 25px rgba(59, 130, 246, 0.15);
}

.breadcrumb {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.875rem;
    color: #64748b;
}

.breadcrumb-item {
    color: #64748b;
    transition: color 0.2s;
}

.breadcrumb-item:hover {
    color: #3b82f6;
}

.breadcrumb-separator {
    font-size: 0.75rem;
    color: #cbd5e1;
}

.breadcrumb-current {
    color: #1e293b;
    font-weight: 600;
}

/* Case Meta Section */
.case-meta-section {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 2rem;
    gap: 2rem;
}

.case-title-group {
    flex: 1;
}

.modern-case-id {
    font-size: 2.25rem;
    font-weight: 800;
    color: #0f172a;
    margin: 0 0 0.5rem 0;
    letter-spacing: -0.025em;
    background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.case-subtitle {
    font-size: 1rem;
    color: #64748b;
    margin: 0;
    line-height: 1.6;
    max-width: 500px;
}

/* Status Pills */
.status-pills {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    align-items: flex-end;
}

.pill-group {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.pill-label {
    font-size: 0.75rem;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    min-width: 40px;
    text-align: right;
}

.modern-tag {
    border-radius: 100px !important;
    padding: 0.5rem 1rem !important;
    font-weight: 600 !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    border: none !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06) !important;
}

/* Action Bar */
.action-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    padding-top: 1.5rem;
    border-top: 1px solid rgba(148, 163, 184, 0.1);
}

.action-group {
    display: flex;
    gap: 0.75rem;
}

.action-btn {
    border-radius: 12px !important;
    font-weight: 600 !important;
    padding: 0.625rem 1.25rem !important;
    font-size: 0.875rem !important;
    border: none !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06) !important;
}

.action-btn:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06) !important;
}

.secondary-actions .p-button {
    width: 40px !important;
    height: 40px !important;
    padding: 0 !important;
    border-radius: 12px !important;
    background: rgba(148, 163, 184, 0.08) !important;
    border: 1px solid rgba(148, 163, 184, 0.15) !important;
    color: #64748b !important;
}

.secondary-actions .p-button:hover {
    background: rgba(148, 163, 184, 0.15) !important;
    color: #475569 !important;
}

/* Metrics Grid */
.metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.metric-card {
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(20px) saturate(180%);
    border: 1px solid rgba(255, 255, 255, 0.25);
    border-radius: 20px;
    padding: 1.5rem;
    position: relative;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 
        0 4px 6px -1px rgba(0, 0, 0, 0.1),
        0 2px 4px -1px rgba(0, 0, 0, 0.06);
    overflow: hidden;
    display: flex;
    align-items: flex-start;
    gap: 1rem;
}

.metric-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%);
}

.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 
        0 20px 25px -5px rgba(0, 0, 0, 0.1),
        0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.metric-icon {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
    color: white;
    background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
    box-shadow: 0 4px 14px 0 rgba(59, 130, 246, 0.3);
    flex-shrink: 0;
}

.analyst-avatar {
    background: linear-gradient(135deg, #10b981 0%, #06b6d4 100%) !important;
}

.metric-content {
    flex: 1;
    min-width: 0;
}

.metric-value {
    font-size: 1.125rem;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 0.25rem;
    line-height: 1.3;
}

.metric-label {
    font-size: 0.75rem;
    color: #64748b;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Metric Indicators */
.metric-trend {
    position: absolute;
    top: 1rem;
    right: 1rem;
    width: 32px;
    height: 32px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(16, 185, 129, 0.1);
}

.trend-icon {
    font-size: 0.875rem;
}

.trend-icon.positive {
    color: #10b981;
}

.metric-progress {
    margin-top: 0.75rem;
    height: 4px;
    background: rgba(148, 163, 184, 0.2);
    border-radius: 2px;
    overflow: hidden;
}

.progress-bar {
    height: 100%;
    background: linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%);
    border-radius: 2px;
    transition: width 0.3s ease;
}

.metric-status {
    position: absolute;
    top: 1rem;
    right: 1rem;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    border: 2px solid white;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.metric-status.online {
    background: #10b981;
}

.metric-urgency {
    position: absolute;
    top: 1rem;
    right: 1rem;
}

.urgency-indicator {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    animation: pulse 2s infinite;
}

.urgency-indicator.medium {
    background: #f59e0b;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.case-header-content {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 2rem;
    flex-wrap: wrap;
    gap: 1rem;
}

.case-title-section {
    display: flex;
    align-items: center;
    gap: 1rem;
    flex: 1;
    min-width: 300px;
}

.back-button {
    background: rgba(255, 255, 255, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.3);
    color: white;
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
}

.back-button:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateX(-2px);
}

.case-title-info {
    flex: 1;
}

.case-id {
    font-size: 2.5rem;
    font-weight: 700;
    margin: 0;
    background: linear-gradient(45deg, #fff, #e0e7ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.case-description {
    font-size: 1.1rem;
    margin: 0.5rem 0 0 0;
    opacity: 0.9;
    line-height: 1.5;
}

.case-status-tags {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
}

.status-tag {
    font-weight: 600;
    padding: 0.5rem 1rem;
    border-radius: 25px;
    backdrop-filter: blur(10px);
}

/* Quick Actions */
.quick-actions {
    display: flex;
    gap: 1rem;
    margin-bottom: 2rem;
    flex-wrap: wrap;
}

.quick-actions .p-button {
    backdrop-filter: blur(10px);
    border-radius: 25px;
    font-weight: 600;
    transition: all 0.3s ease;
}

.quick-actions .p-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
}

/* Overview Cards */
.overview-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
}

.overview-card {
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(15px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 20px;
    padding: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    transition: all 0.3s ease;
}

.overview-card:hover {
    transform: translateY(-5px);
    background: rgba(255, 255, 255, 0.25);
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
}

.card-icon {
    width: 60px;
    height: 60px;
    border-radius: 15px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    background: rgba(255, 255, 255, 0.2);
    color: white;
}

.crypto-card .card-icon {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.amount-card .card-icon {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.analyst-card .card-icon {
    background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.date-card .card-icon {
    background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.card-content {
    flex: 1;
}

.card-value {
    font-size: 1.25rem;
    font-weight: 700;
    margin-bottom: 0.25rem;
    color: white;
}

.card-label {
    font-size: 0.9rem;
    opacity: 0.8;
    color: white;
}

/* Main Content */
.main-content {
    display: grid;
    grid-template-columns: 1fr 350px;
    gap: 2rem;
}

.content-left {
    min-width: 0;
}

.content-right {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

/* Case Tabs */
.case-tabs {
    background: white;
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.custom-tabview :deep(.p-tabview-nav) {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    padding: 0;
}

.custom-tabview :deep(.p-tabview-nav li .p-tabview-nav-link) {
    background: transparent;
    border: none;
    color: rgba(255, 255, 255, 0.8);
    padding: 1rem 1.5rem;
    font-weight: 600;
    transition: all 0.3s ease;
}

.custom-tabview :deep(.p-tabview-nav li.p-highlight .p-tabview-nav-link) {
    background: rgba(255, 255, 255, 0.2);
    color: white;
    backdrop-filter: blur(10px);
}

.custom-tabview :deep(.p-tabview-nav li .p-tabview-nav-link:hover) {
    background: rgba(255, 255, 255, 0.1);
    color: white;
}

.custom-tabview :deep(.p-tabview-panels) {
    background: white;
    border: none;
    padding: 0;
}

/* Tab Content */
.tab-content {
    padding: 2rem;
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
    flex-wrap: wrap;
    gap: 1rem;
}

.section-header h3 {
    margin: 0;
    color: #2d3748;
    font-size: 1.5rem;
    font-weight: 700;
}

/* Transaction Details */
.transaction-details {
    display: flex;
    flex-direction: column;
    gap: 2rem;
}

.detail-group {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
}

.detail-item {
    background: #f8fafc;
    padding: 1.5rem;
    border-radius: 15px;
    border-left: 4px solid #667eea;
    transition: all 0.3s ease;
}

.detail-item:hover {
    background: #f1f5f9;
    transform: translateX(5px);
}

.detail-item.full-width {
    grid-column: 1 / -1;
}

.detail-item label {
    display: block;
    font-weight: 600;
    color: #4a5568;
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.detail-value {
    font-size: 1.1rem;
    font-weight: 600;
    color: #2d3748;
    word-break: break-all;
}

.hash-value {
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    background: #e2e8f0;
    padding: 0.5rem;
    border-radius: 8px;
    font-size: 0.9rem;
}

.risk-indicators {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
}

.risk-chip {
    background: linear-gradient(135deg, #fc8181 0%, #f56565 100%);
    color: white;
    font-weight: 600;
    border-radius: 20px;
    padding: 0.5rem 1rem;
}

/* Documents Table */
.documents-table {
    background: white;
    border-radius: 15px;
    overflow: hidden;
}

.modern-datatable :deep(.p-datatable-header) {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 1rem;
}

.modern-datatable :deep(.p-datatable-thead > tr > th) {
    background: #f8fafc;
    color: #4a5568;
    font-weight: 700;
    padding: 1rem;
    border: none;
    text-transform: uppercase;
    font-size: 0.8rem;
    letter-spacing: 0.5px;
}

.modern-datatable :deep(.p-datatable-tbody > tr > td) {
    padding: 1rem;
    border: none;
    border-bottom: 1px solid #e2e8f0;
}

.modern-datatable :deep(.p-datatable-tbody > tr:hover) {
    background: #f8fafc;
}

.document-name {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.document-name i {
    font-size: 1.25rem;
}

.document-actions {
    display: flex;
    gap: 0.5rem;
}

/* Timeline */
.timeline-container {
    background: #f8fafc;
    padding: 2rem;
    border-radius: 15px;
}

.custom-timeline :deep(.p-timeline-event-marker) {
    border: none;
    border-radius: 50%;
    width: 3rem;
    height: 3rem;
}

.timeline-marker {
    width: 100%;
    height: 100%;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 1rem;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.timeline-content {
    margin-left: 1rem;
    background: white;
    padding: 1.5rem;
    border-radius: 15px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
    border-left: 4px solid #667eea;
}

.timeline-action {
    font-weight: 700;
    color: #2d3748;
    font-size: 1.1rem;
    margin-bottom: 0.5rem;
}

.timeline-meta {
    color: #718096;
    font-size: 0.9rem;
    margin-bottom: 1rem;
}

.timeline-comment {
    background: #f8fafc;
    padding: 1rem;
    border-radius: 10px;
    color: #4a5568;
    line-height: 1.6;
    font-style: italic;
}

/* Notes */
.notes-container {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.note-item {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 15px;
    padding: 1.5rem;
    transition: all 0.3s ease;
    border-left: 4px solid #667eea;
}

.note-item:hover {
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    transform: translateY(-2px);
}

.note-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.note-author {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.note-avatar {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

.author-name {
    font-weight: 600;
    color: #2d3748;
}

.note-timestamp {
    color: #718096;
    font-size: 0.85rem;
}

.note-content {
    color: #4a5568;
    line-height: 1.7;
    margin: 0;
}

/* Metadata Cards */
.metadata-card {
    background: white;
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
}

.metadata-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.card-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1.5rem;
    color: white;
}

.card-header h4 {
    margin: 0;
    font-size: 1.2rem;
    font-weight: 700;
}

.card-body {
    padding: 1.5rem;
}

/* Status Card */
.status-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 0;
    border-bottom: 1px solid #e2e8f0;
}

.status-item:last-child {
    border-bottom: none;
}

.status-label {
    font-weight: 600;
    color: #4a5568;
}

/* Assignment Card */
.assignment-item {
    margin-bottom: 1.5rem;
}

.assignment-item:last-child {
    margin-bottom: 0;
}

.assignment-item label {
    display: block;
    font-weight: 600;
    color: #4a5568;
    margin-bottom: 0.75rem;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.assignee-info {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.assignee-info span {
    font-weight: 600;
    color: #2d3748;
}

.review-level {
    font-weight: 600;
    color: #2d3748;
    background: #f8fafc;
    padding: 0.5rem 1rem;
    border-radius: 10px;
    display: inline-block;
}

/* Timeline Card */
.timeline-item {
    margin-bottom: 1.5rem;
}

.timeline-item:last-child {
    margin-bottom: 0;
}

.timeline-item label {
    display: block;
    font-weight: 600;
    color: #4a5568;
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.timeline-value {
    font-weight: 600;
    color: #2d3748;
}

.due-date {
    color: #f56565;
    background: #fed7d7;
    padding: 0.5rem 1rem;
    border-radius: 10px;
    display: inline-block;
}

/* Dialogs */
.note-dialog :deep(.p-dialog-header),
.upload-dialog :deep(.p-dialog-header) {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 15px 15px 0 0;
}

.note-dialog :deep(.p-dialog-content),
.upload-dialog :deep(.p-dialog-content) {
    border-radius: 0 0 15px 15px;
}

.dialog-content {
    padding: 1rem 0;
}

.field {
    margin-bottom: 1.5rem;
}

.field-label {
    display: block;
    font-weight: 600;
    color: #4a5568;
    margin-bottom: 0.75rem;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    padding-top: 1rem;
}

.custom-file-upload :deep(.p-fileupload-choose) {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    border-radius: 10px;
    padding: 0.75rem 1.5rem;
    font-weight: 600;
    transition: all 0.3s ease;
}

.custom-file-upload :deep(.p-fileupload-choose:hover) {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

/* Responsive Design */
@media (max-width: 1200px) {
    .main-content {
        grid-template-columns: 1fr;
        gap: 1.5rem;
    }
    
    .content-right {
        order: -1;
    }
}

@media (max-width: 768px) {
    .case-detail-container {
        padding: 0.5rem;
    }
    
    .case-header {
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border-radius: 15px;
    }
    
    .case-header-content {
        flex-direction: column;
        align-items: flex-start;
        gap: 1.5rem;
    }
    
    .case-title-section {
        min-width: auto;
        width: 100%;
    }
    
    .case-id {
        font-size: 2rem;
    }
    
    .case-description {
        font-size: 1rem;
    }
    
    .case-status-tags {
        width: 100%;
        justify-content: flex-start;
    }
    
    .quick-actions {
        flex-direction: column;
        gap: 0.75rem;
    }
    
    .quick-actions .p-button {
        width: 100%;
        justify-content: center;
    }
    
    .overview-cards {
        grid-template-columns: 1fr;
        gap: 1rem;
    }
    
    .overview-card {
        padding: 1rem;
    }
    
    .card-icon {
        width: 50px;
        height: 50px;
        font-size: 1.25rem;
    }
    
    .card-value {
        font-size: 1.1rem;
    }
    
    .tab-content {
        padding: 1rem;
    }
    
    .section-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 1rem;
    }
    
    .section-header .p-button {
        width: 100%;
    }
    
    .detail-group {
        grid-template-columns: 1fr;
        gap: 1rem;
    }
    
    .detail-item {
        padding: 1rem;
    }
    
    .timeline-content {
        margin-left: 0.5rem;
        padding: 1rem;
    }
    
    .note-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.75rem;
    }
    
    .metadata-card {
        border-radius: 15px;
    }
    
    .card-header,
    .card-body {
        padding: 1rem;
    }
    
    .status-item {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.5rem;
        padding: 0.75rem 0;
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
    .case-header {
        padding: 1rem;
    }
    
    .case-title-section {
        flex-direction: column;
        align-items: flex-start;
        gap: 1rem;
    }
    
    .back-button {
        align-self: flex-start;
    }
    
    .case-id {
        font-size: 1.75rem;
    }
    
    .overview-card {
        flex-direction: column;
        text-align: center;
        gap: 0.75rem;
    }
    
    .card-content {
        width: 100%;
    }
    
    .custom-tabview :deep(.p-tabview-nav) {
        flex-wrap: wrap;
    }
    
    .custom-tabview :deep(.p-tabview-nav li) {
        flex: 1;
        min-width: 120px;
    }
    
    .custom-tabview :deep(.p-tabview-nav li .p-tabview-nav-link) {
        padding: 0.75rem 1rem;
        font-size: 0.9rem;
        text-align: center;
    }
    
    .timeline-marker {
        width: 2rem;
        height: 2rem;
        font-size: 0.8rem;
    }
    
    .modern-datatable :deep(.p-datatable-wrapper) {
        overflow-x: auto;
    }
    
    .document-name {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.5rem;
    }
    
    .document-actions {
        flex-direction: column;
        gap: 0.25rem;
    }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
    .case-detail-container {
        background: linear-gradient(135deg, #1a202c 0%, #2d3748 100%);
    }
    
    .case-tabs,
    .metadata-card,
    .note-item,
    .timeline-content {
        background: #2d3748;
        color: #e2e8f0;
        border-color: #4a5568;
    }
    
    .detail-item {
        background: #374151;
        border-left-color: #667eea;
    }
    
    .detail-item:hover {
        background: #4a5568;
    }
    
    .hash-value {
        background: #4a5568;
        color: #e2e8f0;
    }
    
    .timeline-container {
        background: #374151;
    }
    
    .timeline-comment {
        background: #4a5568;
        color: #e2e8f0;
    }
    
    .section-header h3,
    .timeline-action,
    .author-name,
    .assignee-info span,
    .review-level,
    .timeline-value {
        color: #e2e8f0;
    }
    
    .status-label,
    .field-label,
    .note-content {
        color: #cbd5e0;
    }
    
    .note-timestamp,
    .timeline-meta {
        color: #a0aec0;
    }
}

/* Print styles */
@media print {
    .case-detail-container {
        background: white;
        padding: 0;
    }
    
    .case-header {
        background: #f8fafc !important;
        color: #2d3748 !important;
        box-shadow: none;
        border: 1px solid #e2e8f0;
    }
    
    .back-button,
    .quick-actions,
    .section-header .p-button,
    .document-actions,
    .dialog-footer {
        display: none !important;
    }
    
    .overview-cards {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .main-content {
        grid-template-columns: 1fr;
    }
    
    .content-right {
        order: -1;
        display: flex;
        flex-direction: row;
        gap: 1rem;
    }
    
    .metadata-card {
        flex: 1;
        box-shadow: none;
        border: 1px solid #e2e8f0;
    }
}

/* Animation keyframes */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes slideInRight {
    from {
        opacity: 0;
        transform: translateX(30px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

/* Apply animations */
.case-header {
    animation: fadeInUp 0.6s ease-out;
}

.overview-card {
    animation: fadeInUp 0.6s ease-out;
}

.overview-card:nth-child(1) { animation-delay: 0.1s; }
.overview-card:nth-child(2) { animation-delay: 0.2s; }
.overview-card:nth-child(3) { animation-delay: 0.3s; }
.overview-card:nth-child(4) { animation-delay: 0.4s; }

.case-tabs {
    animation: fadeInUp 0.6s ease-out 0.3s both;
}

.metadata-card {
    animation: slideInRight 0.6s ease-out;
}

.metadata-card:nth-child(1) { animation-delay: 0.4s; }
.metadata-card:nth-child(2) { animation-delay: 0.5s; }
.metadata-card:nth-child(3) { animation-delay: 0.6s; }

/* Accessibility improvements */
.back-button:focus,
.quick-actions .p-button:focus,
.document-actions .p-button:focus {
    outline: 2px solid #667eea;
    outline-offset: 2px;
}

.overview-card:focus-within {
    outline: 2px solid #667eea;
    outline-offset: 2px;
}

/* High contrast mode */
@media (prefers-contrast: high) {
    .case-header {
        background: #000;
        color: #fff;
        border: 2px solid #fff;
    }
    
    .overview-card {
        background: #fff;
        color: #000;
        border: 2px solid #000;
    }
    
    .card-icon {
        background: #000 !important;
        color: #fff;
    }
    
    .metadata-card,
    .case-tabs {
        border: 2px solid #000;
    }
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
    
    .overview-card:hover,
    .metadata-card:hover,
    .note-item:hover,
    .detail-item:hover {
        transform: none;
    }
}

.mention-highlighter {
  position: absolute;
  inset: 0;
  overflow: auto;
  pointer-events: none;

  /* samakan dengan textarea */
  font: inherit;
  line-height: inherit;
  white-space: pre-wrap;
  word-wrap: break-word;
  padding: var(--p-inputtext-padding, 0.75rem 1rem);
  border-radius: var(--p-inputtext-border-radius, 8px);

  /* teks highlighter terlihat (bukan transparan) */
  color: var(--text-color, inherit);
  background: transparent;
}

mark.mention {
  background: transparent;
  color: var(--p-primary-color, #2563eb);
  font-weight: 600;
}

/* Textarea: sembunyikan teksnya supaya tak dobel, tapi caret tetap terlihat */
.mention-textarea :deep(textarea),
.mention-textarea {
  position: relative;
  background: transparent !important;
  color: transparent !important;     /* <- sembunyikan teks */
  caret-color: var(--text-color);    /* <- caret tetap terlihat */
}
</style>