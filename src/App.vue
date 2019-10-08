<template>
  <div id="app" @click="convertSelectedText" @mouseup="changeConvertTooltipPosition" v-touchend="tooltipTouchend">
    <v-app id="inspire" :dark="darkMode">
      <!--      <div id="progress" v-show="loading">-->
      <!--        <div role="progressbar" aria-valuemin="0" aria-valuemax="100" class="v-progress-linear"-->
      <!--             style="height: 3px; margin: 0">-->
      <!--          <div class="v-progress-linear__background" style="height: 7px; opacity: 0.3; width: 100%;"></div>-->
      <!--          <div class="v-progress-linear__bar">-->
      <!--            <div class="v-progress-linear__bar__indeterminate v-progress-linear__bar__indeterminate&#45;&#45;active">-->
      <!--              <div class="v-progress-linear__bar__indeterminate long error"></div>-->
      <!--              <div class="v-progress-linear__bar__indeterminate short error"></div>-->
      <!--            </div>&lt;!&ndash;&ndash;&gt;</div>-->
      <!--        </div>-->
      <!--      </div>-->
      <v-navigation-drawer
          fixed
          v-model="drawer"
          app
      >
        <v-toolbar flat class="transparent">
          <v-list class="pa-0">
            <v-list-tile avatar>
              <v-list-tile-avatar>
                <img v-if="user.avatar" :src="user.avatar">
                <v-avatar v-else color="indigo">
                  <v-icon dark>account_circle</v-icon>
                </v-avatar>
              </v-list-tile-avatar>

              <v-list-tile-content>
                <v-list-tile-title>{{user.username}}<span class="pl-1 grey--text" v-if="user.groups.length>0">{{user.groups[0]}}</span>
                </v-list-tile-title>
              </v-list-tile-content>
            </v-list-tile>
          </v-list>
        </v-toolbar>
        <v-divider></v-divider>
        <v-list dense>
          <router-link tag="v-list-tile" to="/">
            <v-list-tile-action>
              <v-icon>mdi-view-dashboard</v-icon>
            </v-list-tile-action>
            <v-list-tile-content>
              <v-list-tile-title>Dashboard</v-list-tile-title>
            </v-list-tile-content>
          </router-link>
          <router-link tag="v-list-tile" to="/game_version">
            <v-list-tile-action>
              <v-icon>all_inbox</v-icon>
            </v-list-tile-action>
            <v-list-tile-content>
              <v-list-tile-title>Game Version</v-list-tile-title>
            </v-list-tile-content>
          </router-link>
          <router-link tag="v-list-tile" to="/imperium">
            <v-list-tile-action>
              <v-icon>description</v-icon>
            </v-list-tile-action>
            <v-list-tile-content>
              <v-list-tile-title>Imperium</v-list-tile-title>
            </v-list-tile-content>
          </router-link>
          <router-link tag="v-list-tile" to="/imperium/diff">
            <v-list-tile-action>
              <v-icon>mdi-file-compare</v-icon>
            </v-list-tile-action>
            <v-list-tile-content>
              <v-list-tile-title>Imperium Diff</v-list-tile-title>
            </v-list-tile-content>
          </router-link>
          <router-link tag="v-list-tile" to="/imperium/ab_diff">
            <v-list-tile-action>
              <v-icon>mdi-vector-difference</v-icon>
            </v-list-tile-action>
            <v-list-tile-content>
              <v-list-tile-title>Imperium AB Diff</v-list-tile-title>
            </v-list-tile-content>
          </router-link>
          <router-link tag="v-list-tile" to="/container/search">
            <v-list-tile-action>
              <v-icon>search</v-icon>
            </v-list-tile-action>
            <v-list-tile-content>
              <v-list-tile-title>Container Search</v-list-tile-title>
            </v-list-tile-content>
          </router-link>
          <router-link tag="v-list-tile" to="/asset_bundle">
            <v-list-tile-action>
              <v-icon>mdi-glasses</v-icon>
            </v-list-tile-action>
            <v-list-tile-content>
              <v-list-tile-title>AssetBundle Viewer</v-list-tile-title>
            </v-list-tile-content>
          </router-link>
          <router-link tag="v-list-tile" to="/playground">
            <v-list-tile-action>
              <v-icon>mdi-gamepad-variant</v-icon>
            </v-list-tile-action>
            <v-list-tile-content>
              <v-list-tile-title>ViewerJS Playground</v-list-tile-title>
            </v-list-tile-content>
          </router-link>
          <router-link tag="v-list-tile" to="/spine">
            <v-list-tile-action>
              <v-icon>mdi-animation-play</v-icon>
            </v-list-tile-action>
            <v-list-tile-content>
              <v-list-tile-title>Spine Web Player</v-list-tile-title>
            </v-list-tile-content>
          </router-link>
        </v-list>
      </v-navigation-drawer>
      <v-toolbar color="indigo" dark fixed app>
        <v-toolbar-side-icon @click.stop="drawer = !drawer"></v-toolbar-side-icon>
        <v-toolbar-title>{{ $route.meta.title }}</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-menu bottom left>
          <template slot="activator">
            <v-btn icon>
              <v-icon>more_vert</v-icon>
            </v-btn>
          </template>
          <helper-side-drawer :current-a-b-data="currentABData"></helper-side-drawer>
        </v-menu>
      </v-toolbar>
      <v-content v-scroll="onScroll">
        <v-container fluid grid-list-lg>
          <keep-alive>
            <router-view v-if="$route.meta.keepAlive"></router-view>
          </keep-alive>
          <transition name="fade" mode="out-in">
            <router-view v-if="!$route.meta.keepAlive"></router-view>
          </transition>
        </v-container>
      </v-content>

      <v-footer color="indigo" app inset>
        <span class="white--text">&copy; CancerGary</span>
      </v-footer>
      <v-snackbar
          v-model="snackbarState"
          :timeout="6000"
      >
        {{snackbarMessage}}
        <v-btn
            color="pink"
            flat
            @click="snackbarState = false"
        >
          Close
        </v-btn>
      </v-snackbar>
      <v-tooltip bottom v-model="convertTooltipShow" :absolute="true" :position-x="convertTooltipX"
                 :position-y="convertTooltipY">
        <span>{{convertResult?convertResult:'Nothing matched.'}}</span>
      </v-tooltip>
      <transition name="fade">
        <v-btn v-show="showGotoTop" bottom fixed right float dark fab color="red" class="goto-top"
               @click="$vuetify.goTo(0, {
          duration: 300,
          offset: 0
        })">
          <v-icon dark>keyboard_arrow_up</v-icon>
        </v-btn>
      </transition>
    </v-app>
  </div>
</template>

<script>
  import {mapState} from 'vuex'
  import HelperSideDrawer from "./components/HelperSideDrawer";

  export default {
    components: {HelperSideDrawer},
    data: () => ({
      drawer: false,
      convertConfigDrawer: false,
      convertResult: null,
      convertTooltipX: 0,
      convertTooltipY: 0,
      convertTooltipShow: false,
      lastTouchmoveEvent: null,
      currentABData: null,
      showGotoTop: false,
      user: {
        username: "[loading]",
        avatar: null,
        groups: []
      },
      loading: false
    }),
    methods: {
      convertSelectedText() {
        var selectedText = window.getSelection().toString().trim();
        // console.log(selectedText)
        if (/^[a-f0-9]{32}$/.test(selectedText)) {
          // md5 -> query
          this.convertResult = 'Loading...';
          this.convertTooltipShow = true;
          this.$http.get(`/api/asset_bundle/${selectedText}/`).then((response) => {
            this.convertResult = response.data.imperiums.join(', ');
            this.currentABData = response.data;
            // eslint-disable-next-line
          }).catch(error => {
            this.convertResult = 'No result.';
          })
        } else {
          var convertResult = [];
          // eslint-disable-next-line
          this.$store.state.convertRule.forEach((value, index) => {
            if (selectedText.search(value.pattern) > -1) convertResult.push(`${value.pattern}: ${value.text} `);
          })
          this.convertResult = convertResult.join('; ')
          this.convertTooltipShow = Boolean(selectedText)
        }
      },
      changeConvertTooltipPosition(e) {
        //console.log(e)
        this.convertTooltipX = e.clientX ? e.clientX : (e.changedTouches ? e.changedTouches[0].clientX : 0);
        this.convertTooltipY = e.clientY ? e.clientY : (e.changedTouches ? e.changedTouches[0].clientY : 0);
      },
      tooltipTouchend(e) {
        //
        this.convertSelectedText();
        this.changeConvertTooltipPosition(e)
      },
      onScroll(e) {
        // console.log(e);
        if (e.target.scrollingElement.scrollTop > 100) this.showGotoTop = true;
        else this.showGotoTop = false;
      }
    },
    created() {
      this.$store.commit('setDarkMode', localStorage.getItem('darkMode') === 'true');
      this.$vuetify.lang.current = localStorage.getItem('locale');

      this.$http.get('/api/convert_rule/').then((response) => {
        this.$store.commit('updateConvertRule', response.data);
      });
      this.$http.get('/api/user/').then((response) => {
        this.user = response.data
      })
    },
    computed: {
      ...mapState(['snackbarMessage', 'onLoading', 'darkMode']),
      snackbarState: {
        get: function () {
          return this.$store.state.snackbarState
        },
        set: function (newValue) { // because v-snackbar will change v-model by itself
          this.$store.commit('setToastState', newValue)
        }
      }
    }
  }
</script>
<style>
  @import "assets/style.css";

  #app {
    font-family: 'Avenir', Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    /*text-align: center;*/
    color: #2c3e50;
    /*margin-top: 60px;*/
  }

  .fade-enter-active, .fade-leave-active {
    transition: opacity .25s;
    /*transform: scale(.5);*/
  }

  .fade-enter, .fade-leave-to {
    opacity: 0;
  }

  #progress {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    z-index: 10000;
  }
</style>
