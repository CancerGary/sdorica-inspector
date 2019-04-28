<template>
  <div>
    <v-layout row wrap>
      <v-flex xs12>
        <v-card>
          <v-card-title primary-title>
            <div>
              <div class="headline">Container Search</div>
              <p>Notice: You can use space to separate multi keywords. Making query more accurate can save more
                time.</p></div>
          </v-card-title>
          <v-card-text>
            <v-layout row wrap>
              <!--<v-flex xs12 class="d-flex">-->
              <!--<v-select-->
              <!--:items="imperiumList"-->
              <!--v-model="selectedImperium"-->
              <!--multiple-->
              <!--chips-->
              <!--label="Search range"-->
              <!--&gt;</v-select>-->
              <!--</v-flex>-->
              <v-flex xs12 sm10>
                <v-text-field
                    v-model="query"
                    label="Query keywords"
                    required @keyup.enter="$router.push({name:'container_search',query:{q:query}})">
                ></v-text-field>
              </v-flex>
              <v-flex xs12 sm2 class="d-flex">
                <router-link tag="v-btn" class="primary"
                             :to="{name:'container_search',query:{q:query}}">
                  <v-icon>search</v-icon>
                  Search
                </router-link>
              </v-flex>
            </v-layout>
          </v-card-text>
        </v-card>
      </v-flex>
      <v-flex xs12 v-if="searchResult">
        <v-card>
          <v-card-title primary-title>
            <div>
              <div class="headline">Search Result</div>
            </div>
          </v-card-title>
          <v-card-text class="code-text">
            <div v-for="result in searchResult" :key="result.name">
              <div> {{result.name}}</div>
              <div class="ml-4 grey--text">
                <div v-for="ab in result.asset_bundles" :key="ab.md5">{{ab.md5}} |
                  <router-link
                      :to="{name:'asset_bundle_viewer',params:{ab_md5:ab.md5},query:{container_name:result.name}}"
                      class="grey--text">{{ab.name}}
                  </router-link>
                </div> <!--TODO: jump to specified container-->
              </div>
            </div>
            <div v-if="searchResult.length===0">
              No result.
            </div>
          </v-card-text>
        </v-card>
      </v-flex>
    </v-layout>
  </div>
</template>

<script>
  export default {
    name: "ContainerSearch",
    data() {
      return {
        imperiumList: [],
        query: null,
        searchResult: null
      }
    },
    created() {
      this.$http.get('/api/imperium/', {params: {finished: 'true'}}).then(response => { // 4 -> localization id
        response.data.forEach(item => {
          this.imperiumList.push({text: `[${item.type_id}] ${item.name}`, value: item.id});
        });
      })
      if (this.$route.query.q) {
        this.query = this.$route.query.q;
        this.searchContainer()
      }
    },
    methods: {
      searchContainer() {
        if (!this.query) this.$store.commit('toastMsg', 'Input query first');
        else {
          this.$http.get('/api/container/search/', {params: {query: this.query}}).then(response => {
            this.searchResult = response.data;
          })
        }
      }
    },
    watch: {
      '$route'() {
        if (this.$route.query.q) {
          // TODO: keep-alive optimize
          this.query = this.$route.query.q;
          this.searchContainer()
        }
      }
    }
  }
</script>

<style scoped>

</style>