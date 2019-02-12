<template>
  <div>
    <ImperiumTwoSelector :imperium-list="imperiumList" @compare="loadDiffData"></ImperiumTwoSelector>
    <v-layout>
      <v-flex xs12>
        <v-card>
          <v-card-title>
            <div class="headline">Compare Result</div>
          </v-card-title>
          <v-card-text class="code-text">
            <div v-if="imperiumDiffData">
              <v-layout row wrap>
                <v-flex xs12>Delete & Add</v-flex>
                <v-flex xs12 sm6 class="red--text">
                  <div>[-]</div>
                  <v-expansion-panel>
                    <v-expansion-panel-content
                        v-for="(data,bundleName) in imperiumDiffData.delete"
                        :key="bundleName"
                    >
                      <div slot="header">
                        <div>{{bundleName}} [{{data.data.length}}] |
                          <router-link :to="{name:'asset_bundle_viewer',params:{ab_md5:data.md5}}">{{data.md5}}
                          </router-link>
                        </div>
                      </div>
                      <v-card>
                        <v-card-text>
                          <div v-for="c in data.data">{{c}}</div>
                        </v-card-text>
                      </v-card>
                    </v-expansion-panel-content>
                  </v-expansion-panel>
                </v-flex>
                <v-flex xs12 sm6 class="green--text">
                  <div>[+]</div>
                  <v-expansion-panel>
                    <v-expansion-panel-content
                        v-for="(data,bundleName) in imperiumDiffData.add"
                        :key="bundleName"
                    >
                      <div slot="header">
                        <div>{{bundleName}} [{{data.data.length}}] |
                          <router-link :to="{name:'asset_bundle_viewer',params:{ab_md5:data.md5}}">{{data.md5}}
                          </router-link>
                        </div>
                      </div>
                      <v-card>
                        <v-card-text>
                          <div v-for="c in data.data">{{c}}</div>
                        </v-card-text>
                      </v-card>
                    </v-expansion-panel-content>
                  </v-expansion-panel>
                </v-flex>
              </v-layout>
              <v-layout row wrap>
                <v-flex xs12>Size change only</v-flex>
                <v-flex xs12>
                  <div v-for="(data,bundleName) in imperiumDiffData.nochange">{{bundleName}} |
                    <router-link :to="{name:'asset_bundle_viewer',params:{ab_md5:data[0]}}">{{data[0]}}</router-link>
                    |
                    <router-link :to="{name:'asset_bundle_viewer',params:{ab_md5:data[1]}}">{{data[1]}}</router-link>
                  </div>
                </v-flex>
              </v-layout>
              <v-layout row wrap v-for="(data,bundleName) in imperiumDiffData.change">
                <v-flex xs12>{{bundleName}}</v-flex>
                <v-flex xs12 sm6 class="red--text">
                  <div>[-]
                    <router-link :to="{name:'asset_bundle_viewer',params:{ab_md5:data.md5[0]}}">{{data.md5[0]}}
                    </router-link>
                  </div>
                  <div v-for="containerName in data.delete">{{containerName}}</div>
                </v-flex>
                <v-flex xs12 sm6 class="green--text">
                  <div>[+]
                    <router-link :to="{name:'asset_bundle_viewer',params:{ab_md5:data.md5[1]}}">{{data.md5[1]}}
                    </router-link>
                  </div>
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
  a {
    color: inherit;
  }
</style>