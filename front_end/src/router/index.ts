import {createRouter, createWebHashHistory, createWebHistory, RouteRecordRaw} from 'vue-router'
import HomeView from '../views/HomeView.vue'

const routes: Array<RouteRecordRaw> = [
    {
        path: '/',
        name: 'home',
        component: HomeView
    },
    {
        path: '/clips_viewer/:streamerName?',
        name: 'clips',
        // route level code-splitting
        // this generates a separate chunk (about.[hash].js) for this route
        // which is lazy-loaded when the route is visited.
        component: () => import(/* webpackChunkName: "ClipView" */ '@/views/ClipView.vue')
    },
    {
        path: '/search_twitch/',
        name: 'search_twitch',
        // route level code-splitting
        // this generates a separate chunk (about.[hash].js) for this route
        // which is lazy-loaded when the route is visited.
        component: () => import(/* webpackChunkName: "SearchTwitch" */ '@/views/SearchTwitch.vue')
    },
    {
        path: '/list_scan_jobs/',
        name: 'list_scan_jobs',
        // route level code-splitting
        // this generates a separate chunk (about.[hash].js) for this route
        // which is lazy-loaded when the route is visited.
        component: () => import(/* webpackChunkName: "ListScanJobs" */ '@/views/ListScanJobs.vue')
    },
    {
        path: '/options/',
        name: 'options',
        // route level code-splitting
        // this generates a separate chunk (about.[hash].js) for this route
        // which is lazy-loaded when the route is visited.
        component: () => import(/* webpackChunkName: "ListScanJobs" */ '@/views/Options.vue')
    }, {
        path: '/ListClipsMade/',
        name: 'listclipsmade',
        component: () => import(/* webpackChunkName: "ListClipsMade" */ '@/views/ListClipsMade.vue')
    }, {
        path: '/video/:tag_id',
        name: 'video',
        component: () => import(/* webpackChunkName: "VideoPlayer" */ '@/views/VideoPlayer.vue')
    }
]

const router = createRouter({
    history: createWebHistory(process.env.BASE_URL),
    routes,

})

export default router
