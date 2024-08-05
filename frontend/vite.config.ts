import {fileURLToPath, URL} from 'node:url'

import {defineConfig} from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vitejs.dev/config/
export default defineConfig({
    base: '/static',
    plugins: [
        vue({
            template: {
                compilerOptions: {
                    compatConfig: {
                        MODE: 3
                    }
                }
            }
        }),
        vueDevTools(),
    ],
    resolve: {
        alias: {
            vue: '@vue/compat',
            '@': fileURLToPath(new URL('./src', import.meta.url))
        }
    },
    build: {
        outDir: '../static/'
    }
})
