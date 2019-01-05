<template>
  <div id="app">
    <v-app id="inspire">
      <v-navigation-drawer
          fixed
          v-model="drawer"
          app
      >
        <v-list dense>
          <router-link tag="v-list-tile" to="/">
            <v-list-tile-action>
              <v-icon>home</v-icon>
            </v-list-tile-action>
            <v-list-tile-content>
              <v-list-tile-title>Home</v-list-tile-title>
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
              <v-icon>compare_arrows</v-icon>
            </v-list-tile-action>
            <v-list-tile-content>
              <v-list-tile-title>Imperium Diff</v-list-tile-title>
            </v-list-tile-content>
          </router-link>
        </v-list>
      </v-navigation-drawer>
      <v-toolbar color="indigo" dark fixed app>
        <v-toolbar-side-icon @click.stop="drawer = !drawer"></v-toolbar-side-icon>
        <v-toolbar-title>Application</v-toolbar-title>
      </v-toolbar>
      <v-content>
      <v-container fluid>
        <router-view></router-view>
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
    </v-app>
  </div>

</template>

<script>
  import { mapState } from 'vuex'
  export default {
    data: () => ({
      drawer: null,
    }),
    methods:{

    },
    computed:{
      ...mapState(['snackbarMessage']),
      snackbarState:{
        get: function () {
          return this.$store.state.snackbarState
        },
        set: function (newValue) { // because v-snackbar will change v-model by itself
          this.$store.commit('setToastState',newValue)
        }
      }
    }
  }
</script>
<style>
  #app {
    font-family: 'Avenir', Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    /*text-align: center;*/
    color: #2c3e50;
    margin-top: 60px;
  }
</style>
