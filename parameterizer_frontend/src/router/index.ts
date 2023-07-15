import {createRouter, createWebHistory} from 'vue-router'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'home',
            component: () => import('../views/HomeView.vue')
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
            path: '/algorithms/CDRec',
            name: 'cdrec',
            // route level code-splitting
            component: () => import('../views/algorithms/CDRec.vue')
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
        },
        {
            path: '/algorithms/stmvl',
            name: 'stmvl',
            // route level code-splitting
            component: () => import('../views/algorithms/STMVLView.vue')
        },
        {
            path: '/datasets/bafu',
            name: 'bafu',
            // route level code-splitting
            component: () => import('../views/datasets/BAFUView.vue')
        },
        {
            path: '/datasets/chlorine',
            name: 'chlorine',
            // route level code-splitting
            component: () => import('../views/datasets/ChlorineView.vue')
        },
        {
            path: '/datasets/climate',
            name: 'climate',
            // route level code-splitting
            component: () => import('../views/datasets/ClimateView.vue')
        },
        {
            path: '/datasets/drift',
            name: 'drift',
            // route level code-splitting
            component: () => import('../views/datasets/DriftView.vue')
        },
        {
            path: '/datasets/electricity',
            name: 'electricity',
            // route level code-splitting
            component: () => import('../views/datasets/ElectricityView.vue')
        },
        {
            path: '/datasets/meteo',
            name: 'meteo',
            // route level code-splitting
            component: () => import('../views/datasets/MeteoView.vue')
        },
        {
            path: '/optimization/cdrec',
            name: 'optimization cdrec',
            component: () => import('../views/optimization/CDRecView.vue')
        },
                {
            path: '/optimization/iim',
            name: 'optimization iim',
            component: () => import('../views/optimization/IIMView.vue')
        },
        {
            path: '/optimization/mrnn',
            name: 'optimization mrnn',
            component: () => import('../views/optimization/MRNNView.vue')
        },
        {
            path: '/optimization/stmvl',
            name: 'optimization stmvl',
            component: () => import('../views/optimization/STMVLView.vue')
        }
    ]
})
//// path: '/algorithms/:algorithmId',
export default router
