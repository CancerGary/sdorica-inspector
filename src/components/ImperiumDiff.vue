<template>
  <div>
    <ImperiumTwoSelector :imperium-list="imperiumList" @compare="loadDiffData"></ImperiumTwoSelector>
    <v-layout>
      <v-flex xs12>
        <v-card>
          <v-card-title>
            <div class="headline">Compare Tree View</div><v-switch
          v-model="sortCKeys"
          label="sort C keys"
          color="indigo"
        ></v-switch>
          </v-card-title>
          <v-card-text>
            <div>
              <ImperiumTreeview :imperium-data="imperiumDiffData" :sort-c-keys="sortCKeys"></ImperiumTreeview>
              <p v-if="!loading && Object.keys(imperiumDiffData).length === 0">No Comparison yet.</p>
              <p v-if="loading">Loading...</p>
            </div>
          </v-card-text>
        </v-card>
      </v-flex>
    </v-layout>
  </div>
</template>

<script>
  import ImperiumTreeview from "./ImperiumTreeview";
  import ImperiumTwoSelector from "./ImperiumTwoSelector";

  export default {
    name: "ImperiumDiff",
    components: {ImperiumTwoSelector, ImperiumTreeview},
    data() {
      return {
        imperiumList: [],
        imperiumDiffData: {},
        loading: false,
        sortCKeys: false
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
      }
    }
  }
</script>

<style scoped>

</style>