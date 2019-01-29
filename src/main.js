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

// for tooltip touch event
Vue.directive("touchend",{
  bind:function (el,binding) {
    if (typeof binding.value === "function") {
      el.addEventListener('touchend',binding.value)
    }
  }
});
Vue.directive("touchmove",{
  bind:function (el,binding) {
    if (typeof binding.value === "function") {
      el.addEventListener('touchmove',binding.value)
    }
  }
});

import store from './state'

const vue = new Vue({
  router,
  store,
  render: h => h(App)
})

vue.$mount('#app')
