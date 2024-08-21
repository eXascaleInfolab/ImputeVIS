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
            path: '/compare/:datasetName',
            name: 'compare-overview',
            // route level code-splitting
            // this generates a separate chunk (About.[hash].js) for this route
            // which is lazy-loaded when the route is visited.
            component: () => import('../views/CompareView.vue')
        },
        {
            path: '/contamination',
            name: 'contamination',
            // route level code-splitting
            // this generates a separate chunk (About.[hash].js) for this route
            // which is lazy-loaded when the route is visited.
            component: () => import('../views/ContaminationView.vue')
        },
        {
            path: '/display',
            name: 'display',
            // route level code-splitting
            // this generates a separate chunk (About.[hash].js) for this route
            // which is lazy-loaded when the route is visited.
            component: () => import('../views/PresentDatasetView.vue')
        },
        {
            path: '/display/:datasetName',
            name: 'display-dataset',
            // route level code-splitting
            // this generates a separate chunk (About.[hash].js) for this route
            // which is lazy-loaded when the route is visited.
            component: () => import('../views/DisplayView.vue')
        },
        {
            path: '/feature_extraction',
            name: 'feature_extraction',
            // route level code-splitting
            // this generates a separate chunk (About.[hash].js) for this route
            // which is lazy-loaded when the route is visited.
            component: () => import('../views/FeatureExtractionView.vue')
        },
        {
            path: '/user_optimizer',
            name: 'user_optimizer',
            // route level code-splitting
            // this generates a separate chunk (About.[hash].js) for this route
            // which is lazy-loaded when the route is visited.
            component: () => import('../views/UserOptimizerView.vue')
        },
        {
            path: '/auto_optimizer',
            name: 'auto_optimizer',
            // route level code-splitting
            // this generates a separate chunk (About.[hash].js) for this route
            // which is lazy-loaded when the route is visited.
            component: () => import('../views/AutoOptimizerView.vue')
        },
        {
            path: '/imputation',
            name: 'imputation',
            // route level code-splitting
            // this generates a separate chunk (About.[hash].js) for this route
            // which is lazy-loaded when the route is visited.
            component: () => import('../views/ImputationManagerView.vue')
        },
        {
            path: '/explainer',
            name: 'explainer',
            // route level code-splitting
            // this generates a separate chunk (About.[hash].js) for this route
            // which is lazy-loaded when the route is visited.
            component: () => import('../views/ExplainerView.vue')
        },
        {
            path: '/explainers',
            name: 'explainers',
            // route level code-splitting
            // this generates a separate chunk (About.[hash].js) for this route
            // which is lazy-loaded when the route is visited.
            component: () => import('../views/ExplainersView.vue')
        },
        {
            path: '/compare',
            name: 'compare',
            // route level code-splitting
            // this generates a separate chunk (About.[hash].js) for this route
            // which is lazy-loaded when the route is visited.
            component: () => import('../views/CompareOverviewView.vue')
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
            path: '/datasets/categorizer',
            name: 'categorizer-overview',
            // route level code-splitting
            component: () => import('../views/datasets/CategorizerOverviewView.vue')
        },
        {
            path: '/datasets/categorizer/:datasetName',
            name: 'categorizer',
            // route level code-splitting
            component: () => import('../views/datasets/CategorizerView.vue')
        },
        {
            path: '/algorithms/stmvl',
            name: 'stmvl',
            // route level code-splitting
            component: () => import('../views/algorithms/STMVLView.vue')
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
