import Vue from 'vue'
import Router from 'vue-router'
import Home from "./components/Home";
import GameVersionList from "./components/GameVersionList";
import ImperiumList from "./components/ImperiumList";
import ImperiumShow from "./components/ImperiumShow";
import ImperiumDiff from "./components/ImperiumDiff";
import ImperiumABDiff from "./components/ImperiumABDiff";
import ContainerSearch from "./components/ContainerSearch";
import AssetBundleViewer from "./components/AssetBundleViewer";
import ViewerJSPlayground from './components/ViewerJSPlayground';
import SpineWebPlayer from "./components/SpineWebPlayer";

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home,
      meta: {title: 'Dashboard'}
    },
    {
      path: '/game_version',
      name: 'game_version',
      component: GameVersionList,
      meta: {title: 'Game Version'}
    },
    {
      path: '/imperium',
      name: 'imperium',
      component: ImperiumList,
      meta: {title: 'Imperium'}
    },
    {
      path: '/imperium/diff',
      name: 'imperium_diff',
      component: ImperiumDiff,
      meta: {title: 'Imperium Diff'}
    },
    {
      path: '/imperium/ab_diff',
      name: 'imperium_ab_diff',
      component: ImperiumABDiff,
      meta: {title: 'Imperium AB Diff', keepAlive: true}
    },
    {
      path: '/imperium/:imperium_id',
      name: 'imperium_show',
      component: ImperiumShow,
      meta: {title: 'Imperium Show'}
    },
    {
      path: '/container/search',
      name: 'container_search',
      component: ContainerSearch,
      meta: {title: 'Container Search', keepAlive: true}
    },
    {
      path: '/asset_bundle/:ab_md5?/:container_path_id?',
      name: 'asset_bundle_viewer',
      component: AssetBundleViewer,
      meta: {title: 'AssetBundle Viewer'}
    },
    {
      path: '/playground',
      name: 'playground',
      component: ViewerJSPlayground,
      meta: {title: 'ViewerJS Playground'}
    },
    {
      path: '/spine',
      name: 'spine',
      component: SpineWebPlayer,
      meta: {title: 'Spine Web Player'}
    },
    {
      path: '*',
      redirect: '/'
    }
  ]
})
