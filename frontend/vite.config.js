import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      'hammerjs/hammer.js': 'hammerjs',
      'hammerjs/hammer': 'hammerjs',
    }
  },
  optimizeDeps: { include: ['chart.js', 'chartjs-plugin-zoom', 'hammerjs'] },
  build: { commonjsOptions: { transformMixedEsModules: true } },

  // ⬇️ paling penting: paksa host 127.0.0.1
  server: {
    host: '127.0.0.1',
    port: 5173,
    proxy: { '/api': { target: 'http://127.0.0.1:5000', changeOrigin: true } }
  }
})