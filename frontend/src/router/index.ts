import {createRouter, createWebHistory} from 'vue-router'
// @ts-ignore
import HomeView from '../views/HomeView.vue'
// @ts-ignore
import FileUploadView from '@/views/FileUploadView.vue'
// @ts-ignore
import OrdersView from '@/views/OrdersView.vue'
// @ts-ignore
import DepartmentReportView from '@/views/DepartmentReportView.vue'

// @ts-ignore
// @ts-ignore
const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'home',
            component: HomeView
        },
        {
            path: '/files/upload',
            name: 'files-upload',
            // route level code-splitting
            // this generates a separate chunk (About.[hash].js) for this route
            // which is lazy-loaded when the route is visited.
            component: FileUploadView
        },
        {
            path: '/orders',
            name: 'orders',
            // route level code-splitting
            // this generates a separate chunk (About.[hash].js) for this route
            // which is lazy-loaded when the route is visited.
            component: OrdersView
        },
        {
            path: '/report/dept',
            name: 'dept-report',
            // route level code-splitting
            // this generates a separate chunk (About.[hash].js) for this route
            // which is lazy-loaded when the route is visited.
            component: DepartmentReportView
        },
        {
            path: '/about',
            name: 'about',
            // route level code-splitting
            // this generates a separate chunk (About.[hash].js) for this route
            // which is lazy-loaded when the route is visited.
            component: () => import('../views/AboutView.vue')
        }
    ]
})

export default router
