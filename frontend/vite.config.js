import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// 本地后端 8011（8001 被 Docker 端口转发占死）；Docker 部署时用 api:8001
const API = process.env.VITE_API_TARGET || 'http://127.0.0.1:8011'

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
