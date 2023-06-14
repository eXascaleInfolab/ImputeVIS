import {createRouter, createWebHistory} from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'home',
            component: HomeView
        },
        {
            path: '/about',
            name: 'about',
            // route level code-splitting
            // this generates a separate chunk (About.[hash].js) for this route
            // which is lazy-loaded when the route is visited.
            component: () => import('../views/AboutView.vue')
        },
        {
            path: '/algorithms/iim',
            name: 'iim',
            // route level code-splitting
            component: () => import('../views/algorithms/IIMView.vue')
        },
        {
            path: '/algorithms/m-rnn',
            name: 'm-rnn',
            // route level code-splitting
            component: () => import('../views/algorithms/M-RNNView.vue')
        }
    ]
})
//// path: '/algorithms/:algorithmId',
export default router
