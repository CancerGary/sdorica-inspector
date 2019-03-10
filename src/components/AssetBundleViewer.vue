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
          <v-text-field
              v-if="showContainersFilters"
              single-line
              regular hide-details class="pa-0"
              v-model="containersFiltersInput"
              placeholder="Filters"
          ></v-text-field>
          <v-toolbar-title v-show="!showContainersFilters">Containers</v-toolbar-title>
          <v-spacer v-show="!showContainersFilters"></v-spacer>
          <v-btn icon @click="showContainersFilters = !showContainersFilters ">
            <v-icon>mdi-filter</v-icon>
          </v-btn>
        </v-toolbar>
        <!--text-align: left;direction: rtl;-->
        <v-list dense style="height: 400px;overflow-y:auto">
          <!--:to="{name:'asset_bundle_viewer',params:{ab_md5:$route.params.ab_md5,container_path_id:k}}"-->
          <div v-if="forceContainersList || Object.keys(containersList).length<500 ">
            <v-list-tile @click="fetchContainerData(k)"
                         v-for="(v,k) in containersList"
                         :class="{active:currentContainerKey===k}"
                         :key="k">
              <!--v-show="showContainersFilters?(containerFilters?containerFilters.every(fk=>v.shortName.includes(fk)): true):true">-->
              <v-list-tile-title>{{v.shortName}}</v-list-tile-title>
            </v-list-tile>
          </div>
          <div v-else>
            Too long to show (>500), please use container search or filters or <a @click="forceContainersList=true">force
            show</a>
          </div>
        </v-list>
      </v-card>
    </v-flex>
    <v-flex xs12 sm8 lg9>
      <v-layout column>
        <v-flex xs12 v-show="interpreterEditor">
          <v-card>
            <v-toolbar card dense>
              <v-toolbar-title>Interpreter JavaScript</v-toolbar-title>
              <v-spacer></v-spacer>
              <v-tooltip bottom>
                <v-btn icon slot="activator" @click="setCodeEditing">
                  <v-icon>restore</v-icon>
                </v-btn>
                <span>Reset</span>
              </v-tooltip>
              <v-tooltip bottom>
                <v-btn icon slot="activator" @click="submitViewerJS">
                  <v-icon>save</v-icon>
                </v-btn>
                <span>Save</span>
              </v-tooltip>
            </v-toolbar>
            <v-card-text>
              <codemirror v-model="codeEditing" :options="{lineNumbers:true,theme: 'monokai',styleActiveLine: true}"
                          @input="interpret = false"></codemirror>
            </v-card-text>
          </v-card>
        </v-flex>
        <v-flex xs12>
          <v-card>
            <v-toolbar card dense>
              <v-toolbar-title>Viewer</v-toolbar-title>
              <v-spacer></v-spacer>
              <v-tooltip bottom>
                <v-btn icon slot="activator" @click="interpreterEditor = !interpreterEditor">
                  <v-icon>code</v-icon>
                </v-btn>
                <span>Edit Interpreter</span>
              </v-tooltip>
              <v-tooltip bottom>
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
    </v-flex>
  </v-layout>
</template>

<script>
  import ImperiumTreeview from "./ImperiumTreeview";
  import {codemirror} from 'vue-codemirror'
  import 'codemirror/mode/javascript/javascript.js'
  import 'codemirror/lib/codemirror.css'
  import 'codemirror/theme/monokai.css'


  export default {
    name: "AssetBundleViewer",
    components: {ImperiumTreeview, codemirror},
    data() {
      return {
        containers: {},
        containersFiltersInput: "",
        forceContainersList: false,
        showContainersFilters: false,
        currentContainerKey: null,
        interpret: false,
        treeviewData: {},
        currentContainerData: {},
        currentABMd5: null,
        currentABInfo: {},
        showMedia: false,
        interpreterEditor: false,
        codeEditing: 'alert("hello")',
        viewerJS: {}
      }
    },
    created() {
      this.fetchViewerJS();
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
      fetchViewerJS() {
        this.$http.get(`/api/viewer_js/`).then((response) => {
          response.data.forEach((value) => {
            this.viewerJS[value.unity_type] = {javascript: value.javascript, id: value.id}
          });
        })
      },
      fetchContainerList() {
        this.currentContainerKey = null;
        this.currentContainerData = {};
        this.$http.get(`/api/asset_bundle/${this.$route.params.ab_md5}/containers/`).then((response) => {
          for (var k in response.data) response.data[k] = {shortName: response.data[k].name.split('/').pop(), ...response.data[k]};
          this.containers = response.data;
          if (this.$route.query.container_name) {
            for (var key in this.containers)
              if (this.containers[key].name === this.$route.query.container_name) {
                this.fetchContainerData(key);
                break;
              }
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
          this.setCodeEditing();
        })
      },
      setCodeEditing() {
        var _ = this.viewerJS[this.containers[this.currentContainerKey].type];
        // console.log(_);
        this.codeEditing = _ ? _.javascript : "(data) => {\nconsole.log('handleing');\nconsole.log(data);\n" +
          "return {result:data.m_Name}\n}";
      },
      checkSupportType(type) {
        return this.interpreterEditor || this.viewerJS.hasOwnProperty(type);
      },
      interpretData() {
        if (this.interpret) {
          // stop interpreting
          this.showMedia = false;
          this.interpret = false;
        } else {
          // check interpreting
          var type = this.containers[this.currentContainerKey].type;
          // internal type check
          if (['Sprite', 'AudioClip'].indexOf(type) > -1) {
            this.interpret = true;
            this.showMedia = true;
          } else if (this.checkSupportType(type)) { // external type check
            this.interpret = true;
          } else {
            // not support
            this.interpret = false;
            this.showMedia = false;
            this.$store.commit('toastMsg', 'Currently not support this type');
          }
        }
      },
      submitViewerJS() {
        var type = this.containers[this.currentContainerKey].type;
        var _ = this.viewerJS[type];
        var p = undefined;
        if (_) p = this.$http.put(`/api/viewer_js/${type}/`, {
          javascript: this.codeEditing,
          unity_type: type
        });
        else p = this.$http.post('/api/viewer_js/', {javascript: this.codeEditing, unity_type: type});
        p.then(
          () => {
            this.$store.commit('toastMsg', 'Success'), this.fetchViewerJS()
          }
        ).catch((error) => (this.$store.commit('toastMsg', error.response.data)))
      }
    }
    ,
    computed: {
      interpretedData() {
        if (this.interpret) {
          var type = this.containers[this.currentContainerKey].type;
          if (this.checkSupportType(type)) {
            // customized code dict
            var code = this.interpreterEditor ? this.codeEditing : this.viewerJS[type].javascript;
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
      },
      containerFilters() {
        if (this.containersFiltersInput) return this.containersFiltersInput.trim().split(' '); else return [];
      },
      containersList() {
        var result = {};
        for (var k in this.containers) if (this.containerFilters.every(fk => this.containers[k].shortName.includes(fk)))
          result[k] = this.containers[k];
        return result;
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