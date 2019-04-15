<template>

  <v-layout row wrap>
    <v-flex xs12 md3>
      <v-layout column>
        <v-flex>
          <v-card style="word-break: break-all">
            <v-toolbar card dense>
              <v-toolbar-title>Select Preview</v-toolbar-title>
              <v-spacer></v-spacer>
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
            <v-card-text style="height: 400px;overflow-y:auto;word-break: break-all">
              <div v-for="result in searchResult" :key="result.name">
                <div> {{result.name}}</div>
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
              <v-btn icon v-if="$route.query.uuid" @click="recordGIF">
                <v-icon>mdi-gif</v-icon>
              </v-btn>
              <v-btn icon v-if="$route.query.uuid">
                <a :href="`/api/spine/${$route.query.uuid}/zip/`" download
                   style="color: inherit;text-decoration: none;">
                  <v-icon>mdi-package-down</v-icon>
                </a>
              </v-btn>
              <v-btn icon @click="submitSpine">
                <v-icon>play_arrow</v-icon>
              </v-btn>
            </v-toolbar>
            <v-card-text>
              <div class="text-xs-center" v-if="playerLoading">
                <v-progress-linear :indeterminate="true"></v-progress-linear>
              </div>
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
        spinePlayer: null,
        playerLoading: false,
        caputurer: null
      }
    },
    mounted() {
      if (this.$route.query.uuid) {
        var uuid = this.$route.query.uuid;
        this.spinePlayer = new spine.SpinePlayer("player-container", {
          jsonUrl: `/api/spine/${uuid}/json/`,
          atlasUrl: `/api/spine/${uuid}/atlas/`,
          backgroundColor: "#666666",
          // backgroundImage:{url:'/api/asset_bundle/f5c8fdfe349362aa734fc2af7f1b4f10/containers/-2952096878925393890/data/'},
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
        this.playerLoading = true;
        this.$http.post('/api/spine/', {
          skeleton: this.selectedSkel,
          atlas: this.selectedAtlas,
          images: this.selectedImages
        }).then((res) => {
          var uuid = res.data.task_uuid;
          this.playerLoading = false;
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
          this.playerLoading = false;
          this.$store.commit('toastMsg', err.message + err.response.data)
        })
      },
      recordGIF() {
        this.spinePlayer.pause();
        var animation = this.spinePlayer.animationState.getCurrent(0).animation;
        var name = animation.name;
        this.spinePlayer.setAnimation(animation.name);
        let recording = true;
        this.capturer = new CCapture({
          format: 'gif',
          workersPath: 'static/js/',
          framerate: 60,
          timeLimit: this.spinePlayer.animationState.getCurrent(0).animation.duration,
          name: `${this.$route.query.uuid}_${name}_peanuts.hentai.animation`
        });
        this.spinePlayer.play();

        let capturer = this.capturer;
        let canvas = document.getElementsByClassName('spine-player-canvas')[0]
        function render() {
          if (recording) requestAnimationFrame(render);
          // TODO: black frames -> `preserveDrawingBuffer`
          capturer.capture(canvas);
        }

        render();
        capturer.start();
        setTimeout(animation * 2000, () => {
          recording = false;
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