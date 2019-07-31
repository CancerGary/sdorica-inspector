import axios from 'axios'
import Cookies from 'js-cookie'
import store from './state'
import NProgress from 'nprogress'

NProgress.configure({showSpinner: false});

let $backend = axios.create({
  //baseURL: '/api',
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': Cookies.get('csrftoken')
  }
});


$backend.interceptors.request.use(config => {
  // store.commit('setLoading', true);
  NProgress.start();
  return config;
}, error => {
  NProgress.done();
  store.commit('toastMsg', error.message);
  return Promise.reject(error);
});


$backend.interceptors.response.use(function (response) {
  // store.commit('setLoading', false);
  NProgress.done();
  return response;
}, function (error) {
  // eslint-disable-next-line
  //console.log(error)
  NProgress.done();
  store.commit('toastMsg', error.message + (error.response ? ' ' + JSON.stringify(error.response.data) : ""));
  return Promise.reject(error);
});

export default $backend
