import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const buildMarker = new Date().toISOString()

export default defineConfig({
  define: {
    __APP_BUILD_MARKER__: JSON.stringify(buildMarker),
  },
  plugins: [react()],
  server: {
    host: '127.0.0.1',
    allowedHosts: ['mean-facts-think.loca.lt'],
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  },
  build: {
    outDir: 'dist',
    rollupOptions: {
      plugins: [
        {
          name: 'emit-release-meta',
          generateBundle() {
            this.emitFile({
              type: 'asset',
              fileName: 'release-meta.json',
              source: JSON.stringify(
                {
                  build_marker: buildMarker,
                  built_at: buildMarker,
                },
                null,
                2
              ),
            })
          },
        },
      ],
    },
  }
})
