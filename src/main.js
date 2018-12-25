import Vue from 'vue'
import App from '@/App.vue'

import router from '@/router'
import $backend from '@/backend'
Vue.prototype.$backend = $backend
Vue.config.productionTip = false

// Vue.use(VueRouter)
import Vuetify from 'vuetify'
import 'vuetify/dist/vuetify.min.css'

const axios = require('axios');
axios.defaults.withCredentials = true;
Vue.prototype.$http = axios;
// Vue.prototype.$http = axios.create({withCredentials: true});

import moment from "moment";
Vue.prototype.$moment = moment;

Vue.use(Vuetify)


const vue = new Vue({
  router,
  render: h => h(App)
})

vue.$mount('#app')
