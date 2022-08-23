import {createApp} from 'vue'
import App from './App.vue'
import './registerServiceWorker'
import router from './router'
import store from './store'
// @ts-ignore
import Vue3VideoPlayer from '@cloudgeek/vue3-video-player'
import '@cloudgeek/vue3-video-player/dist/vue3-video-player.css'

import 'bootstrap/dist/css/bootstrap.css'



const app = createApp(App).use(Vue3VideoPlayer).use(router).mount('#app')
