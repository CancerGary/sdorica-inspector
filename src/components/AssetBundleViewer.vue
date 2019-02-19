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
          <!--:to="{name:'asset_bundle_viewer',params:{ab_md5:$route.params.ab_md5,container_path_id:k}}"-->
          <v-list-tile @click="fetchContainerData(k)"
                       v-for="(v,k) in containers"
                       :class="{active:currentContainerKey===k}"
                       :key="k">
            <v-list-tile-title>{{v.name.split('/')[v.name.split('/').length-1]}}</v-list-tile-title>
          </v-list-tile>
        </v-list>
      </v-card>
    </v-flex>
    <v-flex xs12 sm8 lg9>
      <v-card>
        <v-toolbar card dense>
          <v-toolbar-title>Viewer</v-toolbar-title>
          <v-spacer></v-spacer>
          <v-tooltip left>
            <v-btn icon slot="activator" @click="interpretData">
              <v-icon>{{interpret?'pause':'play_arrow'}}</v-icon>
            </v-btn>
            <span>Interpret</span>
          </v-tooltip>
        </v-toolbar>
        <v-card-text>
          <div style="word-break: break-all" v-if="currentContainerKey">{{containers[currentContainerKey].name}}
            &#40;{{containers[currentContainerKey].type}}&#41; | {{currentContainerKey}}
          </div>
          <imperium-treeview :imperiumData="interpretedData" v-show="!showMedia"></imperium-treeview>
          <div v-if="showMedia" v-html="interpretedMedia"></div>
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
        currentABInfo: {},
        showMedia: false,
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
          if (this.$route.query.container_name) {
            for (var key in this.containers)
              if (this.containers[key].name === this.$route.query.container_name)
                this.fetchContainerData(key);
          }
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
      checkSupportType(type) {
        return ['DialogAsset'].indexOf(type) > -1;
      },
      interpretData() {
        if (this.interpret) {
          // stop interpreting
          this.showMedia = false;
          this.interpret = false;
        } else {
          this.interpret = true;
          // check interpreting
          var type = this.containers[this.currentContainerKey].type;
          // internal type check
          if (['Sprite', 'AudioClip'].indexOf(type) > -1) {
            this.showMedia = true;
          } else if (this.checkSupportType(type)) { // external type check

          } else {
            // not support
            this.interpret = false;
            this.showMedia = false;
            this.$store.commit('toastMsg', 'Currently not support this type');
          }
        }
      }
    }
    ,
    computed: {
      interpretedData() {
        if (this.interpret) {
          var type = this.containers[this.currentContainerKey].type;
          if (this.checkSupportType(type)) {
            // customized code dict
            var code = {DialogAsset: '(data)=>{var result=[]; for (var e in data._serializedStateValues) {var raw=JSON.parse(data._serializedStateValues[e].replace(":.0",":0.0"));raw.$interpreted=[];for (var i in raw.$content) raw.$interpreted.push(`${raw.$content[i].SpeakerName}: ${raw.$content[i].Text}`);result.push(raw)};return result;}'}[type];
            return eval(code)(this.currentContainerData);
          } else return this.currentContainerData;
        }
        return this.currentContainerData;
      },
      interpretedMedia() {
        if (!this.showMedia) return "<div>If you see this, maybe there's a bug occurred.</div>";
        var type = this.containers[this.currentContainerKey].type;
        var source = `/api/asset_bundle/${this.currentABMd5}/containers/${this.currentContainerKey}/data/`;
        if (type === 'Sprite') return `<img src="${source}" style="max-width: 100%">`;
        else if (type === 'AudioClip') return `<audio controls style="width: 100%"> <source src="${source}" type="audio/ogg"></audio>`;
      }
    },
    watch: {
      // eslint-disable-next-line
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