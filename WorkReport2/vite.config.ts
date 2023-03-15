import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { viteMockServe } from 'vite-plugin-mock'
import resolveExternalsPlugin from 'vite-plugin-resolve-externals'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    viteMockServe({
      mockPath: 'mock',
      localEnabled: true
    }),
    // resolveExternalsPlugin({
    //   './cptable': 'var cptable'
    // })
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  build:{
    outDir: "../WorkReport2BackEnd/static",
    emptyOutDir: true
  }
})
