import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// Docker 里 API 服务名是 api:8001，本地是 127.0.0.1:8001
const API = process.env.VITE_API_TARGET || 'http://127.0.0.1:8001'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    host: true,
    proxy: {
      '/campaigns': API,
      '/companies': API,
      '/emails': API,
      '/contacts': API,
      '/followup': API,
      '/health': API,
      '/t': API,
    },
  },
})
