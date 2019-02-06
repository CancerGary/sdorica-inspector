<template>
  <v-layout row wrap>
    <v-flex xs12>
      <v-card>
        <v-card-text>
          <div v-if="currentABMd5">Current: {{currentABInfo.name}} | {{currentABMd5}}</div>
          <div v-else>No asset bundle been loaded yet.</div>
        </v-card-text>
      </v-card>
    </v-flex>
    <v-flex xs12 sm4 lg3>
      <v-card>
        <v-toolbar card dense>
          <v-toolbar-title>Containers</v-toolbar-title>
          <!--TODO: search bar-->
        </v-toolbar>

        <!--text-align: left;direction: rtl;-->
        <v-list dense style="height: 400px;overflow-y:auto">
          <router-link tag='v-list-tile'
                       :to="{name:'asset_bundle_viewer',params:{ab_md5:$route.params.ab_md5,container_path_id:k}}"
                       v-for="(v,k) in containers"
                       :class="{active:currentContainerKey===k}">
            <v-list-tile-title>{{v.name.split('/')[v.name.split('/').length-1]}}</v-list-tile-title>
          </router-link>
        </v-list>
      </v-card>
    </v-flex>
    <v-flex xs12 sm8 lg9>
      <v-card>
        <v-toolbar card dense>
          <v-toolbar-title>Viewer</v-toolbar-title>
          <v-spacer></v-spacer>
          <v-tooltip left>
            <v-btn icon slot="activator" @click="interpret = !interpret">
              <v-icon>{{interpret?'pause':'play_arrow'}}</v-icon>
            </v-btn>
            <span>Interpret</span>
          </v-tooltip>
        </v-toolbar>
        <v-card-text>
          <div style="word-break: break-all" v-if="currentContainerKey">{{containers[currentContainerKey].name}}
            <{{containers[currentContainerKey].type}}>
          </div>
          <imperium-treeview :imperiumData="interpretedData"></imperium-treeview>
        </v-card-text>
      </v-card>
    </v-flex>
  </v-layout>
</template>

<script>
  import ImperiumTreeview from "./ImperiumTreeview";

  export default {
    name: "AssetBundleViewer",
    components: {ImperiumTreeview},
    data() {
      return {
        containers: {},
        currentContainerKey: null,
        interpret: false,
        treeviewData: {},
        currentContainerData: {},
        currentABMd5: null,
        currentABInfo: {}
      }
    },
    created() {
      this.load();
    },
    methods: {
      load() {
        // TODO: more precise logic here
        if (this.$route.params.ab_md5) {
          // router recycled or created
          if (this.$route.params.ab_md5 !== this.currentABMd5 || !this.currentABMd5) {
            this.fetchABInfo();
            this.fetchContainerList();
          }
          if (this.$route.params.container_path_id) {
            this.fetchContainerData(this.$route.params.container_path_id)
          }
        } else this.$router.push({name: 'asset_bundle_viewer', params: {ab_md5: prompt("Input AB md5", "")}});
      },
      fetchABInfo() {
        this.$http.get(`/api/asset_bundle/${this.$route.params.ab_md5}/`).then((response) => {
          this.currentABInfo = response.data;
        })
      },
      fetchContainerList() {
        this.currentContainerKey = null;
        this.currentContainerData = {};
        this.$http.get(`/api/asset_bundle/${this.$route.params.ab_md5}/containers/`).then((response) => {
          this.containers = response.data;
          // v-if
          this.currentABMd5 = this.$route.params.ab_md5;
        })
      },
      fetchContainerData(key) {
        this.currentContainerData = {};
        this.$http.get(`/api/asset_bundle/${this.$route.params.ab_md5}/containers/${key}/`).then((response) => {
          this.currentContainerData = response.data;
          // v-if
          this.currentContainerKey = key;
        })
      },
    },
    computed: {
      interpretedData() {
        if (this.interpret) {
          if (this.containers[this.currentContainerKey].type === 'DialogAsset') {
            return eval('(data)=>{var result=[]; for (var e in data._serializedStateValues) {var raw=JSON.parse(data._serializedStateValues[e].replace(":.0",":0.0"));raw.$interpreted=[];for (var i in raw.$content) raw.$interpreted.push(`${raw.$content[i].SpeakerName}: ${raw.$content[i].Text}`);result.push(raw)};return result;}')(this.currentContainerData);
          }
          this.interpret = false;
          this.$store.commit('toastMsg', 'Currently not support this type');
        }
        return this.currentContainerData;
      }
    },
    watch: {
      '$route'(to, from) {
        this.load();
        //this.$forceUpdate();
      }
    }
  }
</script>

<style scoped>
  .active {
    background-color: rgba(0, 0, 0, .08);
  }
</style>