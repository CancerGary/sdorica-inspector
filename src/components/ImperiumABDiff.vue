<template>
  <div>
    <ImperiumTwoSelector :imperium-list="imperiumList" @compare="loadDiffData"></ImperiumTwoSelector>
    <v-layout>
      <v-flex xs12>
        <v-card>
          <v-card-title>
            <div class="headline">Compare Result</div>
          </v-card-title>
          <v-card-text style="word-break: break-all;font-family: Menlo,Monaco,Consolas,'Courier New',monospace">
            <div v-if="imperiumDiffData">
              <v-layout row wrap>
                <v-flex xs12>Asset Bundle Delete & Add</v-flex>
                <v-flex xs12 sm6 class="red--text">
                  <div>[-]</div>
                  <div v-for="(data,bundleName) in imperiumDiffData.delete">{{bundleName}} | {{data.md5}}</div>
                </v-flex>
                <v-flex xs12 sm6 class="green--text">
                  <div>[+]</div>
                  <div v-for="(data,bundleName) in imperiumDiffData.add">{{bundleName}} | {{data.md5}}</div>
                </v-flex>
              </v-layout>
                <v-layout row wrap v-for="(data,bundleName) in imperiumDiffData.change">
                  <v-flex xs12>{{bundleName}}</v-flex>
                  <v-flex xs12 sm6 class="red--text">
                    <div>[-] {{data.md5[0]}}</div>
                    <div v-for="containerName in data.delete">{{containerName}}</div>
                  </v-flex>
                  <v-flex xs12 sm6 class="green--text">
                    <div>[+] {{data.md5[1]}}</div>
                    <div v-for="containerName in data.add">{{containerName}}</div>
                  </v-flex>
                </v-layout>
            </div>
            <div v-else>No comparison yet.</div>
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
        imperiumDiffData: null,
        loading: false,
      }
    },
    created() {
      this.$http.get('/api/imperium/', {params: {finished: 'true'}}).then(response => { // 4 -> localization id
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