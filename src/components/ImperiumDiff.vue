<template>
  <div>
    <v-layout row wrap>
      <v-flex xs12>
        <v-card>
          <v-card-title>
            <div class="headline">Compare Option</div>
          </v-card-title>
          <v-card-text>
            <v-layout row wrap>
              <v-flex>
                <div class="v-subheader pa-0">Display type</div>
                <v-radio-group v-model="textDiff">
                  <v-radio :value="false" label="Treeview" color="indigo"></v-radio>
                  <v-radio :value="true" label="Text" color="indigo"></v-radio>
                </v-radio-group>
              </v-flex>
              <v-flex v-if="textDiff">
                <div class="v-subheader pa-0">Text Diff Options</div>
                <v-switch
                    v-model="showIndex"
                    label="Show index"
                    color="indigo" hide-details
                ></v-switch>
                <v-switch
                    v-model="showType"
                    label="Show type"
                    color="indigo" hide-details
                ></v-switch>
                <v-switch
                    v-model="cellLines"
                    label="One cell one line (better for long text)"
                    color="indigo" hide-details
                ></v-switch>
                <v-radio-group v-model="outputFormat">
                  <template v-slot:label>
                    <div>Diff display type</div>
                  </template>
                  <v-radio :value="'line-by-line'" label="Line by line" color="indigo"></v-radio>
                  <v-radio :value="'side-by-side'" label="Side by side" color="indigo"></v-radio>
                </v-radio-group>
                <v-text-field v-model="expandLines" type="number" label="Expand lines"></v-text-field>
              </v-flex>
              <v-flex v-else>
                <div class="v-subheader pa-0">Treeview Diff Option</div>
                <v-switch
                    v-model="sortCKeys"
                    label="Sort C keys"
                    color="indigo"
                ></v-switch>
              </v-flex>
            </v-layout>
          </v-card-text>
        </v-card>
      </v-flex>
    </v-layout>
    <ImperiumTwoSelector :imperium-list="imperiumList" @compare="loadDiffData"></ImperiumTwoSelector>
    <v-layout row wrap>
      <v-flex xs12>
        <v-card>
          <v-card-title>
            <div class="headline">Compare Result</div>
            <v-btn @click="expandTreeview">Expand/Collapse</v-btn>
          </v-card-title>
          <v-card-text>
            <div v-if="!textDiff">
              <ImperiumTreeview :imperium-data="imperiumDiffData" :sort-c-keys="sortCKeys"
                                ref="itreeview"></ImperiumTreeview>
              <p v-if="!loading && Object.keys(imperiumDiffData).length === 0">No Comparison yet.</p>
              <p v-if="loading">Loading...</p>
            </div>
            <code-diff :diff-string="imperiumDiffTextData" v-if="textDiff" :output-format="outputFormat"></code-diff>
          </v-card-text>
        </v-card>
      </v-flex>
    </v-layout>
  </div>
</template>

<script>
  import ImperiumTreeview from "./ImperiumTreeview";
  import ImperiumTwoSelector from "./ImperiumTwoSelector";
  import CodeDiff from "./CodeDiff";

  export default {
    name: "ImperiumDiff",
    components: {CodeDiff, ImperiumTwoSelector, ImperiumTreeview},
    data() {
      return {
        imperiumList: [],
        imperiumDiffData: {},
        loading: false,
        sortCKeys: false,
        textDiff: false,
        imperiumDiffTextData: undefined,
        showIndex: true,
        showType: false,
        cellLines: false,
        outputFormat: 'line-by-line',
        expandLines: 0
      }
    },
    created() {
      this.$http.get('/api/imperium/').then(response => { // 4 -> localization id
        this.imperiumList = response.data;
      })
    },
    methods: {
      loadDiffData(old_id, new_id) {
        this.loading = true;
        this.$http.get('/api/imperium/diff/', {params: {old: old_id, new: new_id}}).then(response => {
          //console.log(response.data);
          this.imperiumDiffData = response.data;
          this.loading = false;
        })
        this.$http.get('/api/imperium/diff_text/', {
          params: {
            old: old_id,
            new: new_id,
            show_index: this.showIndex,
            show_type: this.showType,
            cell_lines: this.cellLines,
            expand_lines: this.expandLines
          }
        }).then(response => {
          //console.log(response.data);
          this.imperiumDiffTextData = response.data;
          this.loading = false;
        })
      },
      expandTreeview() {
        this.$refs.itreeview.updateAll(this.expanded = !this.expanded);
      }
    }
  }
</script>

<style scoped>

</style>