export type WalletHistoryItem = {
  address: string
  queried_at?: string | null
}

async function apiGet<T>(url: string): Promise<T> {
  const res = await fetch(url, { headers: { 'Accept': 'application/json' } })
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.json() as Promise<T>
}

/** Ambil 10 riwayat pencarian terakhir dari backend */
export async function getWalletHistory(): Promise<WalletHistoryItem[]> {
  // backend: @ns_wallets_api.route('/history')
  // asumsi base prefix /api/wallets
  return apiGet<WalletHistoryItem[]>('/api/wallets/history')
}