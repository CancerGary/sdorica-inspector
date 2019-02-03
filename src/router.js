import Vue from 'vue'
import Router from 'vue-router'
import Home from "./components/Home";
import GameVersionList from "./components/GameVersionList";
import ImperiumList from "./components/ImperiumList";
import ImperiumShow from "./components/ImperiumShow";
import ImperiumDiff from "./components/ImperiumDiff";
import ImperiumABDiff from "./components/ImperiumABDiff";
import ContainerSearch from "./components/ContainerSearch";

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
    },
    {
      path: '/imperium/diff',
      name: 'imperium_diff',
      component: ImperiumDiff
    },
    {
      path: '/imperium/ab_diff',
      name: 'imperium_ab_diff',
      component: ImperiumABDiff
    },
    {
      path: '/imperium/:imperium_id',
      name: 'imperium_show',
      component: ImperiumShow
    },
    {
      path: '/container/search',
      name: 'container_search',
      component: ContainerSearch
    }
  ]
})
