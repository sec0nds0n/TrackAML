const RAW_BASE = (import.meta.env?.VITE_API_BASE_URL || import.meta.env?.VITE_API_BASE || '');
const DEFAULT_BASE = '/api';
let BASE = (RAW_BASE || '').trim() || DEFAULT_BASE;
BASE = BASE.replace(/\/+$/, '');

export async function ensureCsrf() {
  if (CSRF_CACHE) return CSRF_CACHE;
  const res = await fetch(`${BASE}/auth/csrf`, { credentials: 'include' });
  // backend bisa mengirim { csrf_token } atau { csrf }
  const data = await res.json().catch(() => ({}));
  CSRF_CACHE = data.csrf_token || data.csrf || data.token || null;
  return CSRF_CACHE;
}

function normalizeBase(url) {
  if (!url) return '';
  return url.replace(/\/+$/, '');
}
const API_BASE_URL = normalizeBase(RAW_BASE);

function ensureLeadingSlash(p) {
  return p.startsWith('/') ? p : `/${p}`;
}

// Gabung base + endpoint, sekaligus de-dupe '/api' kalau base sudah mengandung '/api'
function joinURL(base, path) {
  const b = (base || '').replace(/\/+$/, '');
  const p = (path || '').toString();
  return /^https?:\/\//i.test(p) ? p : `${b}${p.startsWith('/') ? '' : '/'}${p}`;
}

function readCookie(name) {
  return document.cookie.split('; ').reduce((acc, c) => {
    const [k, ...v] = c.split('=');
    return k === name ? decodeURIComponent(v.join('=')) : acc;
  }, null);
}

let CSRF_CACHE = null;
let CSRF_TS = 0;
const CSRF_TTL = 5 * 60 * 1000;

export function resetCsrfCache() {
  CSRF_CACHE = null;
  CSRF_TS = 0;
}

async function fetchCsrfToken(force = false) {
  const now = Date.now();
  if (!force && CSRF_CACHE && now - CSRF_TS < CSRF_TTL) return CSRF_CACHE;

  // minta token ke backend
  const res = await fetch(joinURL(BASE, '/auth/csrf'), { credentials: 'include' });
  let data = {};
  try { data = await res.json(); } catch {}
  const token =
    data.csrf_token ||
    data.csrf ||
    data.token ||
    readCookie('csrf_token') ||      // kalau backend pakai double-submit cookie
    readCookie('XSRF-TOKEN') ||      // beberapa lib pakai nama ini
    null;

  if (token) {
    CSRF_CACHE = token;
    CSRF_TS = now;
  }
  return token;
}

function getCookie(name) {
  const m = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'));
  return m ? decodeURIComponent(m[1]) : null;
}

class ApiService {
  constructor(baseURL = API_BASE_URL) {
    this.baseURL = baseURL;
    this.timeout = 15000;
  }
  setBaseURL(url) { this.baseURL = normalizeBase(url); }

  async request(endpoint, { method = 'GET', headers = {}, body, json = true } = {}) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), this.timeout);

    const isWrite = ['POST', 'PUT', 'PATCH', 'DELETE'].includes(String(method).toUpperCase());
    const csrf = getCookie('csrf_token');

    const finalHeaders = {
      Accept: 'application/json',
      // Hindari set Content-Type kalau tidak ada body (biar GET tidak aneh-aneh)
      ...(json && body != null ? { 'Content-Type': 'application/json' } : {}),
      ...(isWrite && csrf ? { 'X-CSRF-Token': csrf } : {}),
      ...headers,
    };

    const url = joinURL(this.baseURL, endpoint);

    try {
      const res = await fetch(url, {
        method,
        headers: finalHeaders,
        body: json && body && typeof body !== 'string' ? JSON.stringify(body) : body,
        credentials: 'include',
        signal: controller.signal,
      });
      clearTimeout(timer);

      const contentType = res.headers.get('content-type') || '';
      const data = contentType.includes('application/json') ? await res.json() : await res.text();

      if (!res.ok) {
        const err = new Error((data && data.message) || `HTTP ${res.status}`);
        err.status = res.status;
        err.data = data;
        if (res.status === 401) err.isAuthError = true;
        throw err;
      }
      return data;
    } catch (e) {
      clearTimeout(timer);
      throw e;
    }
  }

  // Shorthands
  get(url, opts)         { return this.request(url, { method: 'GET',    ...(opts || {}) }); }
  post(url, body, opts)  { return this.request(url, { method: 'POST',   body, ...(opts || {}) }); }
  put(url, body, opts)   { return this.request(url, { method: 'PUT',    body, ...(opts || {}) }); }
  patch(url, body, opts) { return this.request(url, { method: 'PATCH',  body, ...(opts || {}) }); }
  delete(url, body, opts){ return this.request(url, { method: 'DELETE', body, ...(opts || {}) }); }

  // Auth helpers
  async login(credentials) { return await this.post('/api/auth/login', credentials); }
  async me()               { return await this.get('/api/auth/me'); }
  async logout()           { return await this.post('/api/auth/logout', {}); }
  async health() {
    try { return await this.get('/api/health'); }
    catch (e) { return { status: 'error', message: e.message }; }
  }
}
// wrapper fetch utama
export async function request(path, { method = 'GET', headers = {}, body, timeout = 20000 } = {}) {
  const url = joinURL(BASE, path);
  const controller = new AbortController();
  const finalHeaders = { ...headers };
  const isUnsafe = !/^(GET|HEAD|OPTIONS|TRACE)$/i.test(method);
  const isForm = typeof FormData !== 'undefined' && body instanceof FormData;

  if (isUnsafe) {
    const token = await fetchCsrfToken();
    if (token) {
      // kirim semua variasi header yang umum
      finalHeaders['X-CSRF-Token'] = token;
      finalHeaders['X-CSRFToken'] = token;
      finalHeaders['X-XSRF-TOKEN'] = token;
    }
    if (!isForm && body && typeof body !== 'string' && !finalHeaders['Content-Type']) {
      finalHeaders['Content-Type'] = 'application/json';
    }
  }

  const doFetch = async () => {
    const t = setTimeout(() => controller.abort(), timeout);
    try {
      const res = await fetch(url, {
        method,
        headers: finalHeaders,
        body: isForm ? body : (body && typeof body !== 'string' ? JSON.stringify(body) : body),
        credentials: 'include',
        signal: controller.signal,
      });
      const ct = res.headers.get('content-type') || '';
      const data = ct.includes('application/json') ? await res.json() : await res.text();

      if (!res.ok) {
        const err = new Error((data && data.message) || `HTTP ${res.status}`);
        err.status = res.status;
        err.data = data;
        if (res.status === 401) err.isAuthError = true;
        throw err;
      }
      return data;
    } finally {
      clearTimeout(t);
    }
  };

  try {
    return await doFetch();
  } catch (e) {
    // jika CSRF gagal, refresh token & retry sekali
    const msg = (e?.data && (e.data.message || e.data.error)) || e?.message || '';
    if (e?.status === 403 && /csrf/i.test(msg)) {
      resetCsrfCache();
      const fresh = await fetchCsrfToken(true);
      if (fresh) {
        finalHeaders['X-CSRF-Token'] = fresh;
        finalHeaders['X-CSRFToken'] = fresh;
        finalHeaders['X-XSRF-TOKEN'] = fresh;
      }
      return await doFetch();
    }
    throw e;
  }
}

const api = new ApiService();
api.resetCsrfCache = resetCsrfCache;
export default api;
export const createCase = (body) => request('/cases', { method: 'POST', body });
export const assignEntityToCase = (body) => request('/cases/assign', { method: 'POST', body });
export const me = () => request('/auth/me');
export const login = (credentials) => request('/auth/login', { method: 'POST', body: credentials });
export const logout = () => request('/auth/logout', { method: 'POST' });

// --- CASE DETAIL ---
export const getCase = (id) => request(`/cases/${id}`);

// --- COMMENTS ---
export const getCaseComments = (id) => request(`/cases/${id}/comments`);
export const addCaseComment = (id, body) =>
  request(`/cases/${id}/comments`, { method: 'POST', body }); // { body, visibility }

// --- TASKS ---
export const getCaseTasks = (id) => request(`/cases/${id}/tasks`);
export const createCaseTask = (id, body) =>
  request(`/cases/${id}/tasks`, { method: 'POST', body }); // { title, due_at, assignee_id, status }
export const updateTask = (taskId, body) =>
  request(`/tasks/${taskId}`, { method: 'PATCH', body });
export const deleteTask = (taskId) =>
  request(`/tasks/${taskId}`, { method: 'DELETE' });

// --- ATTACHMENTS (opsional, jika endpoint sudah ada) ---
export const getCaseAttachments = (id) => request(`/cases/${id}/attachments`);
export const uploadCaseAttachment = (id, file, meta = {}) => {
  const fd = new FormData();
  fd.append('file', file);
  Object.entries(meta).forEach(([k, v]) => fd.append(k, v ?? ''));
  // request() sudah mendeteksi FormData (lihat patch di bawah)
  return request(`/cases/${id}/attachments`, { method: 'POST', body: fd });
};
export const searchUsers = (q) =>
   request(`/users/search?q=${encodeURIComponent(q)}`, { method: 'GET' });

export async function getNotifications() {
  return request('GET', '/api/notifications?limit=20')
}
export async function readNotifications() {
  return request('PUT', '/api/notifications/read-all')
}

export async function notifyMentions(payload) {
  // Harapannya ada endpoint POST /api/cases/:id/comments/mentions
  // Jika belum ada, bisa sementara diarahkan ke /api/notifications/mention
  try {
    return await request('POST', `/api/notifications/mention`, payload)
  } catch (e) {
    // biarkan diam (opsional)
    throw e
  }
}