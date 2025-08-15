<script setup>
const updates = [
  {
    id: 'bappebti-pasar-fisik',
    title: 'Pedoman Perdagangan Pasar Fisik Aset Kripto',
    source: 'Bappebti',
    region: 'Indonesia',
    status: { label: 'IN EFFECT', tone: 'green' },
    tone: 'emerald',
    summary:
      'Persyaratan pendaftaran pedagang aset kripto, kewajiban KYC/AML, pencatatan & pelaporan transaksi.',
    time: '2 hours ago',
    // Portal JDIH Bappebti (stabil untuk referensi resmi)
    link: 'https://jdih.bappebti.go.id/'
  },
  {
    id: 'bappebti-whitelist',
    title: 'Daftar Aset Kripto yang Diperdagangkan (Whitelist)',
    source: 'Bappebti',
    region: 'Indonesia',
    status: { label: 'UPDATED', tone: 'amber' },
    tone: 'amber',
    summary:
      'Hanya aset dalam whitelist yang boleh diperdagangkan; ada mekanisme evaluasi & delisting periodik.',
    time: '1 day ago',
    link: 'https://jdih.bappebti.go.id/'
  },
  {
    id: 'bursa-kliring-kustodian',
    title: 'Bursa Kripto, Lembaga Kliring & Kustodian Domestik',
    source: 'Bappebti',
    region: 'Indonesia',
    status: { label: 'LIVE', tone: 'green' },
    tone: 'green',
    summary:
      'Perdagangan melalui bursa kripto lokal dengan kliring & penyimpanan terpusat untuk perlindungan nasabah.',
    time: '3 days ago',
    link: 'https://jdih.bappebti.go.id/'
  },
  {
    id: 'bi-pembayaran',
    title: 'Larangan Kripto sebagai Alat Pembayaran',
    source: 'Bank Indonesia',
    region: 'Indonesia',
    status: { label: 'REMINDER', tone: 'slate' },
    tone: 'slate',
    summary:
      'Rupiah satu-satunya alat pembayaran; kripto dilarang untuk pembayaran—hanya sebagai komoditas investasi.',
    time: '1 week ago',
    link: 'https://jdih.bi.go.id/'
  }
]

const dotClass = (t) => ({
  green:  'bg-emerald-500',
  red:    'bg-rose-500',
  blue:   'bg-sky-500',
  amber:  'bg-amber-500',
  emerald:'bg-emerald-500',
  purple: 'bg-purple-500',
  slate:  'bg-slate-500',
  indigo: 'bg-indigo-500'
}[t] || 'bg-slate-400')

const tagClass = (t) => ({
  green:  'bg-emerald-100 text-emerald-700',
  amber:  'bg-amber-100 text-amber-700',
  blue:   'bg-sky-100 text-sky-700',
  emerald:'bg-emerald-100 text-emerald-700',
  purple: 'bg-purple-100 text-purple-700',
  slate:  'bg-slate-100 text-slate-700',
  indigo: 'bg-indigo-100 text-indigo-700'
}[t] || 'bg-slate-100 text-slate-700')
</script>

<template>
  <div class="bg-white dark:bg-gray-900 rounded-3xl shadow-2xl border border-gray-200 dark:border-gray-800 p-8">
    <!-- Header -->
    <div class="flex items-start justify-between mb-6">
      <div class="flex items-center gap-4">
        <div class="relative p-3 rounded-2xl bg-gradient-to-br from-emerald-500 to-green-600 text-white shadow-lg">
          <svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M12 11c0-3 2-5 5-5 0 6-5 9-5 9s-5-3-5-9c3 0 5 2 5 5z"/>
          </svg>
          <span
            class="absolute -top-1 -right-1 w-5 h-5 text-xs font-bold bg-red-500 text-white rounded-full grid place-items-center">
            {{ updates.length }}
          </span>
        </div>
        <div>
          <h3 class="text-2xl font-bold text-gray-900 dark:text-white">Regulatory Intelligence</h3>
          <p class="text-sm text-gray-600 dark:text-gray-300">Real-time compliance monitoring</p>
        </div>
      </div>
      <div class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-50 dark:bg-emerald-900/30">
        <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
        <span class="text-sm font-semibold text-emerald-700 dark:text-emerald-300">Live</span>
      </div>
    </div>

    <!-- List -->
    <div class="space-y-4">
      <article
        v-for="u in updates"
        :key="u.id"
        class="relative rounded-2xl border p-5 shadow-sm bg-gradient-to-b from-white to-gray-50/30 dark:from-gray-800 dark:to-gray-800/30"
        :class="{
          'border-emerald-200 dark:border-emerald-800': u.tone==='green' || u.tone==='emerald',
          'border-amber-200 dark:border-amber-800': u.tone==='amber',
          'border-sky-200 dark:border-sky-800': u.tone==='blue',
          'border-rose-200 dark:border-rose-800': u.tone==='red',
          'border-purple-200 dark:border-purple-800': u.tone==='purple',
          'border-slate-200 dark:border-slate-700': u.tone==='slate',
          'border-indigo-200 dark:border-indigo-800': u.tone==='indigo'
        }"
      >
        <!-- View Details: fixed di pojok kanan atas, buka tab baru -->
        <a
          :href="u.link"
          target="_blank"
          rel="noopener noreferrer"
          :title="`Buka dokumen resmi: ${u.title}`"
          class="group absolute top-5 right-5 inline-flex items-center gap-1 text-emerald-600 dark:text-emerald-400 font-semibold hover:underline focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400 rounded-md px-1"
        >
          View Details
          <svg class="w-4 h-4 transition-transform group-hover:translate-x-0.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h4m0 0v4m0-4L10 14"/>
          </svg>
        </a>

        <!-- Konten kiri diberi padding-right agar tidak ketabrak link -->
        <div class="pr-28">
          <!-- Header judul + badge -->
          <div class="flex items-start gap-3">
            <span class="mt-1 w-3 h-3 rounded-full" :class="dotClass(u.tone)"></span>

            <div class="flex-1">
              <div class="flex items-center gap-3 flex-wrap">
                <h4 class="text-lg font-semibold text-gray-900 dark:text-white leading-tight">
                  {{ u.title }}
                </h4>
                <span class="text-xs font-bold px-2.5 py-0.5 rounded-full" :class="tagClass(u.status.tone)">
                  {{ u.status.label }}
                </span>
              </div>

              <!-- Tag sumber & region -->
              <div class="mt-2 flex items-center gap-3 text-sm">
                <span class="px-2 py-0.5 rounded-lg bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200 font-medium">
                  {{ u.source }}
                </span>
                <span class="text-gray-500 dark:text-gray-400">🌐 {{ u.region }}</span>
              </div>

              <!-- Deskripsi -->
              <p class="mt-3 text-gray-700 dark:text-gray-300">
                {{ u.summary }}
              </p>

              <!-- Waktu -->
              <div class="mt-4 flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" aria-hidden="true">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
                <span>{{ u.time }}</span>
              </div>
            </div>
          </div>
        </div>
      </article>
    </div>
  </div>
</template>