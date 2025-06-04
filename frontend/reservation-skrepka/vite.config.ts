import react from '@vitejs/plugin-react-swc'
import { defineConfig } from 'vite'

// https://vitejs.dev/config/
export default defineConfig({
  base: "/skrepka",
  assetsInclude: ['**/*.glb'],
  build: {
    sourcemap: true,
  },
  plugins: [react()],
  preview: {
    port: 8081,
    strictPort: true,
   },
  server: {
    port: 8081,
    strictPort: true,
    host: true,
   },
})
