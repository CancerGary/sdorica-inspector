<template>
  <v-layout row wrap>
    <v-flex xs12 md6>
      <v-layout row wrap>
        <v-flex xs12>
          <v-card>
            <v-toolbar card dense>
              <v-toolbar-title>Select</v-toolbar-title>
              <v-spacer></v-spacer>
              <v-tooltip bottom>
                <v-btn icon slot="activator" @click="types = jsHelper.getTypes()">
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
        <v-flex>
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
    <v-flex xs12 md6>
      <v-layout row wrap>
        <v-flex xs12>
          <v-card>
            <v-toolbar card dense>
              <v-toolbar-title>Treeview Output</v-toolbar-title>
            </v-toolbar>
            <v-card-text>
              <imperium-treeview :imperium-data="interpretedData"></imperium-treeview>
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
        types: [],
        interpretedData: {writeCode: 'Then run it!'}
      }
    },
    mounted() {
      this.jsHelper = new ViewerJSHelper(this);
      this.jsHelper.fetchViewerJS().then(() => {
        this.setCodeEditing();
        this.types = this.jsHelper.getTypes();
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
        this.jsHelper.runCode(null, data, this.codeEditing, true);
      }
    },
    watch: {
      codeEditingType() {
        this.setCodeEditing()
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