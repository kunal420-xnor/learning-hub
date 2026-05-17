import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/login': 'http://127.0.0.1:5000',
      '/explain': 'http://127.0.0.1:5000',
      '/spanish': 'http://127.0.0.1:5000',
      '/feedback': 'http://127.0.0.1:5000',
      '/create_dataset': 'http://127.0.0.1:5000',
      '/rag': 'http://127.0.0.1:5000',
      '/metrics': 'http://127.0.0.1:5000',
      '/health': 'http://127.0.0.1:5000',
    }
  }
})
