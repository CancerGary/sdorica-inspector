<template>
  <div>
    <ImperiumTwoSelector :imperium-list="imperiumList" @compare="loadDiffData"></ImperiumTwoSelector>
    <v-layout row wrap>
      <v-flex xs12>
        <v-card>
          <v-card-title>
            <div class="headline">Compare Option</div>
          </v-card-title>
          <v-card-text>
            <v-layout>
              <v-flex sm6>
                <v-switch
                    v-model="sortCKeys"
                    label="sort C keys"
                    color="indigo"
                ></v-switch>
              </v-flex>
              <v-flex sm6>
                <v-switch
                    v-model="textDiff"
                    label="Text Diff"
                    color="indigo"
                ></v-switch>
              </v-flex>
            </v-layout>
          </v-card-text>
        </v-card>
      </v-flex>
      <v-flex xs12>
        <v-card>
          <v-card-title>
            <div class="headline">Compare Tree View</div>
          </v-card-title>
          <v-card-text>
            <div v-if="!textDiff">
              <ImperiumTreeview :imperium-data="imperiumDiffData" :sort-c-keys="sortCKeys"></ImperiumTreeview>
              <p v-if="!loading && Object.keys(imperiumDiffData).length === 0">No Comparison yet.</p>
              <p v-if="loading">Loading...</p>
            </div>
            <code-diff :diff-string="imperiumDiffTextData" v-if="textDiff"></code-diff>
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
        imperiumDiffTextData: undefined
      }
    },
    created() {
      this.$http.get('/api/imperium/').then(response => { // 4 -> localization id
        response.data.forEach(item => {
          this.imperiumList.push({text: `[${item.type_id}] ${item.name}`, value: item.id});
        });
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
        this.$http.get('/api/imperium/diff_text/', {params: {old: old_id, new: new_id}}).then(response => {
          //console.log(response.data);
          this.imperiumDiffTextData = response.data;
          this.loading = false;
        })
      }
    }
  }
</script>

<style scoped>

</style>