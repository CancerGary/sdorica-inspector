<template>

  <v-layout row wrap>
    <v-flex xs12 md3>
      <v-layout column>
        <v-flex>
          <v-card>
            <v-toolbar card dense>
              <v-toolbar-title>Select Preview</v-toolbar-title>
              <v-spacer></v-spacer>
              <v-btn icon @click="submitSpine">
                <v-icon>play_arrow</v-icon>
              </v-btn>
            </v-toolbar>
            <v-card-text>
              <div>Select resource first, then submit the selection.</div>
              <v-divider></v-divider>
              <div>skel: {{selectedSkel.name}}</div>
              <div>atlas: {{selectedAtlas.name}}</div>
              images: <span v-for="i in selectedImages" :key="i.name">{{i.name}}, </span><span
                @click="selectedImages=[]" class="ml-2 blue--text" style="cursor:pointer;">[reset]</span>
            </v-card-text>
          </v-card>
        </v-flex>
        <v-flex>
          <v-card>
            <v-toolbar card dense>
              <v-text-field single-line
                            regular hide-details class="pa-0"
                            v-model="containerSearchQuery"
                            placeholder="Search here"
              ></v-text-field>
              <v-btn icon @click="searchContainer(containerSearchQuery)">
                <v-icon>mdi-magnify</v-icon>
              </v-btn>
            </v-toolbar>
            <v-card-text style="height: 400px;overflow-y:auto">
              <div v-for="result in searchResult" :key="result.name">
                <div> {{result.name.split('/').pop()}}</div>
                <div class="ml-4 grey--text">
                  <div v-for="ab in result.asset_bundles" :key="ab.md5">{{ab.md5}} | {{ab.name}}
                    <div class="span-selector">
                      <span @click="selectSkel(ab.md5,result.name)"
                            :class="{'red--text':selectedSkel.md5===ab.md5&&selectedSkel.name===result.name}">[S]</span>
                      <span @click="selectAtlas(ab.md5,result.name)"
                            :class="{'red--text':selectedAtlas.md5===ab.md5&&selectedAtlas.name===result.name}">[A]</span>
                      <span @click="selectImage(ab.md5,result.name)">[I]</span>
                    </div>
                  </div>

                  <!--<div>            <v-btn small color="primary" dark>Small Button</v-btn>-->
                  <!--<v-btn small color="primary" dark>Small Button</v-btn>-->
                  <!--<v-btn small color="primary" dark>Small Button</v-btn>-->
                  <!--</div>-->
                </div>
              </div>
            </v-card-text>
          </v-card>
        </v-flex>
      </v-layout>
    </v-flex>
    <v-flex xs12 md9>
      <v-layout column>
        <v-flex>
          <v-card>
            <v-toolbar card dense>
              <v-toolbar-title>Player</v-toolbar-title>
              <v-spacer></v-spacer>
            </v-toolbar>
            <v-card-text>
              <div id="player-container" style="width: 100%; height: 500px;"></div>
            </v-card-text>
          </v-card>
        </v-flex>
      </v-layout>
    </v-flex>
  </v-layout>
</template>

<script>
  export default {
    name: "SpineWebPlayer",
    data() {
      return {
        containerSearchQuery: "",
        searchResult: {},
        selectedSkel: {},
        selectedAtlas: {},
        selectedImages: [],
        spinePlayer: null
      }
    },
    mounted() {
      if (this.$route.query.uuid) {
        var uuid = this.$route.query.uuid;
        this.spinePlayer = new spine.SpinePlayer("player-container", {
          jsonUrl: `/api/spine/${uuid}/json/`,
          atlasUrl: `/api/spine/${uuid}/atlas/`,
          backgroundColor: "#666666",
          premultipliedAlpha: false
        });
      }
    },
    methods: {
      searchContainer(query) {
        if (!query) this.$store.commit('toastMsg', 'Input query first');
        else {
          this.$http.get('/api/container/search/', {params: {query: query}}).then(response => {
            this.searchResult = response.data;
            this.searchResult.reverse();
          })
        }
      },
      selectSkel(md5, name) {
        this.selectedSkel = {md5: md5, name: name}
      },
      selectAtlas(md5, name) {
        this.selectedAtlas = {md5: md5, name: name}
      },
      selectImage(md5, name) {
        this.selectedImages.push({md5: md5, name: name})
      },
      submitSpine() {
        this.$http.post('/api/spine/', {
          skeleton: this.selectedSkel,
          atlas: this.selectedAtlas,
          images: this.selectedImages
        }).then((res) => {
          var uuid = res.data.task_uuid;
          if (this.spinePlayer) {
            delete this.spinePlayer;
            document.getElementsByClassName('spine-player')[0].remove()
          }
          this.spinePlayer = new spine.SpinePlayer("player-container", {
            jsonUrl: `/api/spine/${uuid}/json/`,
            atlasUrl: `/api/spine/${uuid}/atlas/`,
            backgroundColor: "#666666",
            premultipliedAlpha: false
          });
          this.$router.push({name: 'spine', query: {uuid: uuid}});
        }).catch((err) => {
          this.$store.commit('toastMsg', err.msg)
        })
      }
    }
  }
</script>

<style scoped>
  .span-selector > span {
    margin-right: 1rem;
    cursor: pointer;
  }
</style>