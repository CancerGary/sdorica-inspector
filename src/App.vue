<template>
  <div id="app">
    <v-app id="inspire">
      <v-navigation-drawer
          fixed
          v-model="drawer"
          app
      >
        <v-list dense>
          <v-list-tile @click="">
            <v-list-tile-action>
              <v-icon>home</v-icon>
            </v-list-tile-action>
            <v-list-tile-content>
              <v-list-tile-title>Home</v-list-tile-title>
            </v-list-tile-content>
          </v-list-tile>
        </v-list>
      </v-navigation-drawer>
      <v-toolbar color="indigo" dark fixed app>
        <v-toolbar-side-icon @click.stop="drawer = !drawer"></v-toolbar-side-icon>
        <v-toolbar-title>Application</v-toolbar-title>
      </v-toolbar>
      <v-content>
        <v-container fluid fill-height>
          <v-layout
              justify-center
              align-center
          >
            <v-flex text-xs-center>
              <v-tooltip left>
                <v-btn icon large :href="source" target="_blank" slot="activator">
                  <v-icon large>code</v-icon>
                </v-btn>
                <span>Source</span>
              </v-tooltip>
            </v-flex>
          </v-layout>
        </v-container>
      </v-content>
      <v-footer color="indigo" app inset>
        <span class="white--text">&copy; CancerGary</span>
      </v-footer>
    </v-app>
  </div>

</template>

<script>
  export default {
    data: () => ({
      drawer: null
    })
  }
</script>
<style>
  #app {
    font-family: 'Avenir', Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-align: center;
    color: #2c3e50;
    margin-top: 60px;
  }
</style>
