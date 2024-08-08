import {fileURLToPath, URL} from 'node:url'

import {defineConfig} from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import Components from 'unplugin-vue-components/vite'
import {BootstrapVueNextResolver} from 'bootstrap-vue-next'

// https://vitejs.dev/config/
export default defineConfig({
    base: '/',
    plugins: [
        vue({
            // template: {
            //     compilerOptions: {
            //         compatConfig: {
            //             MODE: 2
            //         }
            //     }
            // }
        }),
        vueDevTools(),
        Components({
            resolvers: [BootstrapVueNextResolver()],
        }),
    ],
    resolve: {
        alias: {
            // vue: '@vue/compat',
            '@': fileURLToPath(new URL('./src', import.meta.url))
        }
    },
    build: {
        outDir: '../static/'
    }
    // ,
    // define: {
    //     __VUE_OPTIONS_API__: true,
    //     __VUE_PROD_DEVTOOLS__: false,
    //     __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: false
    // }
})
