import Vue from 'vue'
import './assets/main.css'

import { createApp } from 'vue'
// import { BootstrapVue, IconsPlugin } from 'bootstrap-vue'

import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap/dist/js/bootstrap.js'
// import 'bootstrap-vue-next/dist/bootstrap-vue.css'

import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import axios from 'axios'

// Set base URL for axios requests to Django backend
axios.defaults.baseURL = 'http://127.0.0.1:8000'

// TODO Bootstrap and vue3 support is not yet ready
// Make BootstrapVue available throughout project
// Vue.use(BootstrapVue)

// Optionally install the BootstrapVue icon components plugin
// Vue.use(IconsPlugin)
// TODO: Theming for BootstrapVue https://bootstrap-vue.org/docs#theming-bootstrap

const app = createApp(App)

app.use(createPinia())
app.use(router, axios)

app.mount('#app')
