<template>
  <div>
    <ImperiumTwoSelector :imperium-list="imperiumList" @compare="loadDiffData"></ImperiumTwoSelector>
    <v-layout>
      <v-flex xs12>
        <v-card>
          <v-card-title>
            <div class="headline">Compare Result</div>
          </v-card-title>
          <v-card-text>
            <div>
              <p>result</p>
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
    name: "ImperiumABDiff",
    components: {ImperiumTwoSelector, ImperiumTreeview},
    data() {
      return {
        imperiumList: [],
        imperiumDiffData: {},
        loading: false
      }
    },
    created() {
      this.$http.get('/api/imperium/',{params:{finished:'true'}}).then(response => { // 4 -> localization id
        response.data.forEach(item => {
          this.imperiumList.push({text: `[${item.type_id}] ${item.name}`, value: item.id});
        });
      })
    },
    methods: {
      loadDiffData(old_id, new_id) {
        this.loading = true;
        this.$http.get('/api/imperium/ab_diff/', {params: {old: old_id, new: new_id}}).then(response => {
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