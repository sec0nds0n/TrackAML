// src/services/api.js
const RAW_BASE = (import.meta.env?.VITE_API_BASE_URL || import.meta.env?.VITE_API_BASE || '');
const BASE = RAW_BASE.replace(/\/+$/, ''); // info global (tidak dipakai langsung di request)

let CSRF_CACHE = null;

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
function joinURL(base, endpoint) {
  const ep = ensureLeadingSlash(endpoint);
  if (!base) return ep; // same-origin (mis. Vite proxy) → pakai path relatif
  const b = normalizeBase(base);
  if (b.endsWith('/api') && ep.startsWith('/api/')) {
    return b + ep.replace(/^\/api/, '');
  }
  return b + ep;
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
export async function request(path, { method = 'GET', headers = {}, body, timeout = 15000 } = {}) {
  const url = path.startsWith('http') ? path : `${BASE}${path.startsWith('/') ? '' : '/'}${path}`;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);

  const finalHeaders = { ...headers };

  const isUnsafe = !/^(GET|HEAD|OPTIONS|TRACE)$/i.test(method);
  if (isUnsafe) {
    const token = await ensureCsrf();
    if (token) finalHeaders['X-CSRF-Token'] = token; // terima juga 'X-CSRFToken' di backend
    if (body && typeof body !== 'string' && !finalHeaders['Content-Type']) {
      finalHeaders['Content-Type'] = 'application/json';
    }
  }

  const res = await fetch(url, {
    method,
    headers: finalHeaders,
    body: body && typeof body !== 'string' ? JSON.stringify(body) : body,
    credentials: 'include',
    signal: controller.signal,
  }).finally(() => clearTimeout(timer));

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
}

const api = new ApiService();
export default api;
export const createCase = ({ type, reference_id, severity, reason, payload }) =>
  request('/cases', { method: 'POST', body: { type, reference_id, severity, reason, payload } });

export const assignEntityToCase = ({ entity_type, entity_key, severity, reason, payload }) =>
  request('/cases/assign', { method: 'POST', body: { entity_type, entity_key, severity, reason, payload } });