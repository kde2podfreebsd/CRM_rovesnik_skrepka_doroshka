import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  base: "/hostes/",
  build: {
    sourcemap: true,
  },
  plugins: [react()],
  preview: {
    port: 5172,
    strictPort: true,
   },
  server: {
    port: 5172,
    strictPort: true,
    host: true,
   },
})
