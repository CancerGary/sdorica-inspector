<template>
  <v-layout row wrap>
    <v-flex xs12 v-bind:class="{md6:showCode}">
      <v-layout column>
        <v-flex>
          <v-card>
            <v-toolbar card dense>
              <v-toolbar-title>Select</v-toolbar-title>
              <v-spacer></v-spacer>
              <v-tooltip bottom v-show="hideJS">
                <v-btn icon slot="activator" @click="hideJS = false">
                  <v-icon>mdi-eye</v-icon>
                </v-btn>
                <span>Show @</span>
              </v-tooltip>
              <v-tooltip bottom v-show="!hideJS">
                <v-btn icon slot="activator" @click="hideJS = true">
                  <v-icon>mdi-eye-off</v-icon>
                </v-btn>
                <span>Hide not @</span>
              </v-tooltip>
              <v-tooltip bottom>
                <v-btn icon slot="activator" @click="showCode = !showCode">
                  <v-icon>mdi-code-tags</v-icon>
                </v-btn>
                <span>Show/Hide code</span>
              </v-tooltip>
              <v-tooltip bottom>
                <v-btn icon slot="activator" @click="onInterpret">
                  <v-icon>play_arrow</v-icon>
                </v-btn>
                <span>Run</span>
              </v-tooltip>
              <v-tooltip bottom>
                <v-btn icon slot="activator" @click="types_ = jsHelper.getTypes()">
                  <v-icon>mdi-reload</v-icon>
                </v-btn>
                <span>Reload type list</span>
              </v-tooltip>
              <v-tooltip bottom>
                <v-btn icon slot="activator" @click="promptCodeEditingType">
                  <v-icon>mdi-file-plus</v-icon>
                </v-btn>
                <span>Set new one</span>
              </v-tooltip>
            </v-toolbar>
            <v-card-text>
              <v-select
                  :items="types"
                  v-model="codeEditingType"
                  label="ViewerJS Unity Type"
              ></v-select>
            </v-card-text>
          </v-card>
        </v-flex>
        <v-flex v-if="showCode">
          <v-card>
            <v-toolbar card dense>
              <v-toolbar-title>Interpreter JavaScript - {{codeEditingType}}</v-toolbar-title>
              <v-spacer></v-spacer>
              <v-tooltip bottom>
                <v-btn icon slot="activator" @click="setCodeEditing">
                  <v-icon>restore</v-icon>
                </v-btn>
                <span>Reset</span>
              </v-tooltip>
              <v-tooltip bottom>
                <v-btn icon slot="activator"
                       @click="jsHelper.submitViewerJS(codeEditingType,codeEditing)">
                  <v-icon>save</v-icon>
                </v-btn>
                <span>Save</span>
              </v-tooltip>
              <v-tooltip bottom>
                <v-btn icon slot="activator" @click="onInterpret">
                  <v-icon>play_arrow</v-icon>
                </v-btn>
                <span>Run</span>
              </v-tooltip>
            </v-toolbar>
            <v-card-text>
              <codemirror v-model="codeEditing"
                          :options="{lineNumbers:true,theme: 'monokai',styleActiveLine: true}"></codemirror>
            </v-card-text>
          </v-card>
        </v-flex>
      </v-layout>
    </v-flex>
    <v-flex>
      <v-layout row wrap>
        <v-flex xs12>
          <v-card>
            <v-toolbar card dense>
              <v-toolbar-title>Treeview Output</v-toolbar-title>
              <v-spacer></v-spacer>
              <v-tooltip bottom>
                <v-btn icon slot="activator" @click="expandTreeview">
                  <v-icon v-show="!expanded">mdi-arrow-expand-vertical</v-icon>
                  <v-icon v-show="expanded">mdi-arrow-collapse-vertical</v-icon>
                </v-btn>
                <span>Expand/Collapse</span>
              </v-tooltip>
            </v-toolbar>
            <v-card-text>
              <div class="text-xs-center" v-if="loading">
                <v-progress-linear :indeterminate="true"></v-progress-linear>
              </div>
              <imperium-treeview :imperium-data="interpretedData" ref="itreeview"></imperium-treeview>
            </v-card-text>
          </v-card>
        </v-flex>
      </v-layout>
    </v-flex>
  </v-layout>
</template>

<script>
  import ViewerJSHelper from './ViewerJSHelper'
  import {codemirror} from 'vue-codemirror'
  import 'codemirror/mode/javascript/javascript.js'
  import 'codemirror/lib/codemirror.css'
  import 'codemirror/theme/monokai.css'
  import ImperiumTreeview from "./ImperiumTreeview";

  export default {
    name: "ViewerJSPlayground",
    components: {ImperiumTreeview, codemirror},
    data() {
      return {
        codeEditing: "()=>{return {result:'hello world'}}",
        jsHelper: new ViewerJSHelper(),
        codeEditingType: null,
        types_: [],
        interpretedData: {writeCode: 'Then run it!'},
        hideJS: true,
        expanded: false,
        loading: false,
        showCode: false
      }
    },
    mounted() {
      this.jsHelper = new ViewerJSHelper(this);
      this.jsHelper.fetchViewerJS().then(() => {
        this.setCodeEditing();
        this.types_ = this.jsHelper.getTypes();
      });
    },
    methods: {
      setCodeEditing() {
        var _ = this.jsHelper.getCode(this.codeEditingType);
        // console.log(_);
        this.codeEditing = _ ? _.javascript : this.codeEditing;
      },
      promptCodeEditingType() {
        var typeName = prompt('Input ViewerJS type name');
        if (typeName) this.codeEditingType = typeName
      },
      onInterpret() {
        // TODO: add special support for `$ViewerInit`
        var data = {};
        this.loading = true;
        this.jsHelper.runCode(null, data, this.codeEditing, (result) => {
          this.interpretedData = result;
          this.loading = false
        });
      },
      expandTreeview() {
        this.$refs.itreeview.updateAll(this.expanded = !this.expanded);
      }
    },
    watch: {
      codeEditingType() {
        this.setCodeEditing()
      }
    },
    computed: {
      types: {
        get: function () {
          if (this.hideJS) {
            return this.types_.filter(x => x[0] === '@')
          } else return this.types_
        }
      }
    }
  }
</script>

<style scoped>
  >>> .CodeMirror {
    border: 1px solid #eee;
    height: auto;
  }
</style>