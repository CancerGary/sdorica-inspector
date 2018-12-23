<template>
  <div>
    <v-layout row wrap>
      <v-flex md5>
        <v-select
            :items="imperiumList"
            v-model="oldSelect"
            label="Old"
        ></v-select>
      </v-flex>
      <v-flex md2>
        <v-layout row align-end justify-center>
          <div>
            <v-btn color="info" @click="loadDiffData">
              <v-icon>compare_arrows</v-icon>
              Start
            </v-btn>
          </div>
        </v-layout>
      </v-flex>
      <v-flex md5>
        <v-select
            :items="imperiumList"
            v-model="newSelect"
            label="New"
        ></v-select>
      </v-flex>
    </v-layout>
    <v-layout row wrap>
      <v-flex>
        <v-card xs12>
          <v-card-title primary-title>
            <div>
              <h3 class="headline mb-0">Old - {{imperiumInfoOld.name}}</h3>
            </div>
          </v-card-title>
          <v-card-text>
            <div v-for="(value,index) in imperiumInfoOld">{{index}}: {{value}}</div>
          </v-card-text>
        </v-card>
      </v-flex>
      <v-flex>
        <v-card xs12>
          <v-card-title primary-title>
            <div>
              <h3 class="headline mb-0">New - {{imperiumInfoNew.name}}</h3>
            </div>
          </v-card-title>
          <v-card-text>
            <div v-for="(value,index) in imperiumInfoNew">{{index}}: {{value}}</div>
          </v-card-text>
        </v-card>
      </v-flex>
    </v-layout>
    <h3>Treeview</h3>
    <ImperiumTreeview :imperium-data="imperiumDiffData"></ImperiumTreeview>
  </div>
</template>

<script>
  import ImperiumTreeview from "./ImperiumTreeview";

  export default {
    name: "ImperiumDiff",
    components: {ImperiumTreeview},
    data() {
      return {
        imperiumList: [],
        oldSelect: null,
        newSelect: null,
        imperiumDiffData: {},
        imperiumInfoOld: {},
        imperiumInfoNew: {}
      }
    },
    watch: {
      oldSelect() {
        this.$http.get('/api/imperium/' + this.oldSelect).then(response => {
          this.imperiumInfoOld = response.data;
        })
      },
      newSelect() {
        this.$http.get('/api/imperium/' + this.newSelect).then(response => {
          this.imperiumInfoNew = response.data;
        })
      }
    },
    created() {
      this.$http.get('/api/imperium/').then(response => {
        response.data.forEach(item => {
          this.imperiumList.push({text: item.name, value: item.id});
        });
      })
    },
    methods: {
      loadDiffData() {
        this.$http.get('/api/imperium/diff/', {params:{old: this.oldSelect, new: this.newSelect}}).then(response => {
          console.log(response.data);
          this.imperiumDiffData = response.data;
        })
      }
    }
  }
</script>

<style scoped>

</style>