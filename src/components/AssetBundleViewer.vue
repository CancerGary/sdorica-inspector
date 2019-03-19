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
                <v-btn icon slot="activator"
                       @click="jsHelper.submitViewerJS(containers[currentContainerKey].type,codeEditing)">
                  <v-icon>save</v-icon>
                </v-btn>
                <span>Save</span>
              </v-tooltip>
            </v-toolbar>
            <v-card-text>
              <codemirror v-model="codeEditing" :options="{lineNumbers:true,theme: 'monokai',styleActiveLine: true}"
                          @input="showInterpretedData = false"></codemirror>
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
                <v-btn icon slot="activator" @click="onInterpret">
                  <v-icon>{{showInterpretedData?'pause':'play_arrow'}}</v-icon>
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
  import ViewerJSHelper from './ViewerJSHelper'

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
        showInterpretedData: null,
        currentContainerData: {},
        currentABMd5: null,
        currentABInfo: {},
        showMedia: false,
        interpreterEditor: false,
        codeEditing: 'alert("hello")',
        interpretedData: {},
        jsHelper: new ViewerJSHelper()
      }
    },
    mounted() {
      this.jsHelper = new ViewerJSHelper(this);
      this.jsHelper.fetchViewerJS();
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
          this.updateInterpretedData();
          this.setCodeEditing();
        })
      },
      setCodeEditing() {
        var _ = this.jsHelper.getCode(this.containers[this.currentContainerKey].type);
        // console.log(_);
        this.codeEditing = _ ? _.javascript : "(data) => {\nconsole.log('handling');\nconsole.log(data);\n" +
          "return {result:data.m_Name}\n}";
      },
      checkSupportType(type) {
        return this.interpreterEditor || this.jsHelper.getCode(type);
      },
      onInterpret() {
        if (this.showInterpretedData) {
          // stop interpreting
          this.showMedia = false;
          this.showInterpretedData = false;
        } else {
          // check interpreting
          var type = this.containers[this.currentContainerKey].type;
          // internal type check
          if (['Sprite', 'AudioClip', 'Texture2D'].indexOf(type) > -1) {
            this.showInterpretedData = true;
            this.showMedia = true;
          } else if (this.checkSupportType(type)) { // external type check
            this.showInterpretedData = true;
          } else {
            // not support
            this.showInterpretedData = false;
            this.showMedia = false;
            this.$store.commit('toastMsg', 'Currently not support this type');
          }
        }
        this.updateInterpretedData();
      },
      updateInterpretedData() {
        var type = this.currentContainerKey ? this.containers[this.currentContainerKey].type : null;
        if (this.showInterpretedData && this.checkSupportType(type)) {
          // customized code dict
          var code = this.interpreterEditor ? this.codeEditing : null;
          var data = Object.assign({}, this.currentContainerData);
          if (code) this.jsHelper.runCode(null, data, code);
          else this.jsHelper.runCode(type, data, null);
        } else this.interpretedData = this.currentContainerData;
      }
    },
    computed: {
      interpretedMedia() {
        if (!this.showMedia) return "<div>If you see this, maybe there's a bug occurred.</div>";
        var type = this.containers[this.currentContainerKey].type;
        var source = `/api/asset_bundle/${this.currentABMd5}/containers/${this.currentContainerKey}/data/`;
        if (type === 'Sprite') return `<img src="${source}" style="max-width: 100%">`;
        else if (type === 'AudioClip') return `<audio controls style="width: 100%"> <source src="${source}" type="audio/ogg"></audio>`;
        else if (type === 'Texture2D') return `<img src="${source}" style="max-width: 100%">`;
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