//import './assets/main.css'

import { createApp } from 'vue'

import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap/dist/js/bootstrap.js'

import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import axios from 'axios'

// Set base URL for axios requests to Django backend
axios.defaults.baseURL = 'http://127.0.0.1:8000'

// TODO Bootstrap and vue3 support is not yet ready
// TODO: Theming for BootstrapVue https://bootstrap-vue.org/docs#theming-bootstrap
// TODO: Delete following init?

import mapInit from 'highcharts/modules/map'
import stockInit from 'highcharts/modules/stock'
import addWorldMap from 'highcharts/modules/map'
import Highcharts from 'highcharts'
import HighchartsVue from 'highcharts-vue'

stockInit(Highcharts)
mapInit(Highcharts)
addWorldMap(Highcharts)

const app = createApp(App)

app.use(createPinia())
app.use(HighchartsVue)
app.use(router)

app.mount('#app')
