import Vue from 'vue'
import Router from 'vue-router'
import Home from "./components/Home";
import GameVersionList from "./components/GameVersionList";
import ImperiumList from "./components/ImperiumList";

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/game_version',
      name: 'game_version',
      component: GameVersionList
    },
    {
      path: '/imperium',
      name: 'imperium',
      component: ImperiumList
    }
  ]
})
