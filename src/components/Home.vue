<template>
  <div>
    <div>
      <h1 class="font-weight-regular">Status</h1>
    </div>

    <v-container grid-list-xl fluid>
      <v-layout row wrap>
        <v-flex :class="miniClass">
          <mini-statistic
              icon="mdi-package"
              :title="status.asset_bundles"
              sub-title="Asset bundles"
              color="indigo"
          >
          </mini-statistic>
        </v-flex>
        <v-flex :class="miniClass">
          <mini-statistic
              icon="description"
              :title="status.imperiums"
              sub-title="Imperiums"
              color="green"
          >
          </mini-statistic>
        </v-flex>
        <v-flex :class="miniClass">
          <mini-statistic
              icon="view_module"
              :title="status.containers"
              sub-title="Containers"
              color="light-blue"
          >
          </mini-statistic>
        </v-flex>
        <v-flex :class="miniClass">
          <mini-statistic
              icon="mdi-chart-donut"
              :title="(status.data_size/1024/1024).toFixed(1)+'M'"
              sub-title="Disk usage"
              color="purple"
          >
          </mini-statistic>
        </v-flex>
        <v-flex :class="miniClass">
          <mini-statistic
              :icon="status.redis?'mdi-database-check':'mdi-database-remove'"
              :title="String(status.redis)"
              sub-title="Redis service"
              color="red"
          >
          </mini-statistic>
        </v-flex>
        <v-flex :class="miniClass">
          <mini-statistic
              icon="people"
              :title="status.users"
              sub-title="Users"
              color="blue-grey"
          >
          </mini-statistic>
        </v-flex>
        <v-flex :class="miniClass">
          <mini-statistic
              icon="mdi-git"
              :title="status.master_hash?status.master_hash.slice(0,6):'Not found'"
              sub-title="Git master"
              color="deep-orange"
          >
          </mini-statistic>
        </v-flex>
        <v-flex :class="miniClass">
          <v-card>
            <v-card-text class="pa-0">
              <v-container class="pa-0">
                <div class="layout row ma-0">
                  <div class="sm6 xs6 flex">
                    <div class="layout column ma-0 justify-center align-center">
                      <img src="/static/img/puggi_smile.png" height="56">
                    </div>
                  </div>
                  <div class="sm6 xs6 flex text-sm-center py-3 white--text" :class="'orange'">
                    <div class="headline">Puggi~</div>
                    <span class="caption">A le le~</span>
                  </div>
                </div>
              </v-container>
            </v-card-text>
          </v-card>
        </v-flex>
      </v-layout>
    </v-container>
  </div>
</template>

<script>
  import MiniStatistic from "./MiniStatistic";

  export default {
    name: "Home",
    components: {MiniStatistic},
    data() {
      return {
        status: {
          "asset_bundles": 0,
          "imperiums": 0,
          "containers": 0,
          "data_size": 0,
          "redis": false,
          "users": 0,
          "master_hash": null
        },
        miniClass: 'lg3 sm6 xs12'
      }
    },
    created() {
      this.$http.get('/api/status/').then((response) => {
        this.status = response.data
      })
    }
  }
</script>

<style scoped>

</style>