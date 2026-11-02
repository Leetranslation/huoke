import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/campaigns': 'http://127.0.0.1:8001',
      '/companies': 'http://127.0.0.1:8001',
      '/emails': 'http://127.0.0.1:8001',
      '/contacts': 'http://127.0.0.1:8001',
      '/health': 'http://127.0.0.1:8001',
    },
  },
})
