<template>
  <v-layout row wrap>
    <v-flex xs12>
      <v-card>
        <v-card-title primary-title>
          <div>
            <div class="headline">Select Imperium</div>
            <p>Caution: You should select two files which their type are same.</p></div>
        </v-card-title>
        <v-card-text>
          <v-layout justify-center column>
            <v-flex>
              <v-layout row wrap>
                <v-flex sm4>
                  <v-select
                      :items="imperiumType"
                      v-model="typeFilter"
                      label="Type Filter"
                      placeholder="All"
                  ></v-select>
                </v-flex>
                <v-flex sm4>
                  <v-select
                      :items="imperiumSelectList"
                      v-model="oldSelect"
                      label="Old"
                  ></v-select>
                </v-flex>
                <v-flex sm4>
                  <v-select
                      :items="imperiumSelectList"
                      v-model="newSelect"
                      label="New"
                  ></v-select>
                </v-flex>
              </v-layout>
            </v-flex>
            <v-flex>
              <v-btn color="primary"
                     @click="imperiumInfoNew.type_id===imperiumInfoOld.type_id?$emit('compare',oldSelect,newSelect):$store.commit('toastMsg', 'Type not same')">
                <v-icon>compare_arrows</v-icon>
                Start
              </v-btn>
            </v-flex>
          </v-layout>
        </v-card-text>
      </v-card>
    </v-flex>
    <v-flex xs12 sm6>
      <v-card>
        <v-card-title>
          <div>
            <div class="headline">Old - {{imperiumInfoOld.name}}</div>
          </div>
        </v-card-title>
        <v-card-text>
          <div v-for="(value,index) in imperiumInfoOld" :key="index">{{index}}: {{value}}</div>
        </v-card-text>
      </v-card>
    </v-flex>
    <v-flex xs12 sm6>
      <v-card>
        <v-card-title>
          <div>
            <div class="headline">New - {{imperiumInfoNew.name}}</div>
          </div>
        </v-card-title>
        <v-card-text>
          <div v-for="(value,index) in imperiumInfoNew" :key="index">{{index}}: {{value}}</div>
        </v-card-text>
      </v-card>
    </v-flex>
  </v-layout>
</template>

<script>
  export default {
    name: "ImperiumTwoSelector",
    props: {
      imperiumList: Array
    },
    data() {
      return {
        oldSelect: null,
        newSelect: null,
        imperiumInfoOld: {},
        imperiumInfoNew: {},
        typeFilter: null
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
    computed: {
      imperiumSelectList() {
        var a = Array();
        this.imperiumList.forEach((v, i) => {
          if (!this.typeFilter || this.typeFilter === v.type_id) a.push({'text': v.name, 'value': v.id})
        })
        return a;
      },
      imperiumType() {
        var a = Array();
        this.$imperiumType.forEach((v, i) => {
          a.push({'text': v, 'value': i})
        });
        return a;
      }
    }
  }
</script>

<style scoped>

</style>