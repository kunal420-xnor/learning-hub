import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/login': 'http://localhost:5000',
      '/explain': 'http://localhost:5000',
      '/spanish': 'http://localhost:5000',
      '/feedback': 'http://localhost:5000',
      '/create_dataset': 'http://localhost:5000',
      '/rag': 'http://localhost:5000',
    }
  }
})
