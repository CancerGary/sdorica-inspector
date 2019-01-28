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
          <v-layout row wrap>
            <v-flex sm5 order-sm1>
              <v-select
                  :items="imperiumList"
                  v-model="oldSelect"
                  label="Old"
              ></v-select>
            </v-flex>
            <v-flex sm5 order-sm3>
              <v-select
                  :items="imperiumList"
                  v-model="newSelect"
                  label="New"
              ></v-select>
            </v-flex>
            <v-flex xs12 sm2 order-sm2 class="d-flex">
                  <v-btn color="info" @click="imperiumInfoNew.type_id===imperiumInfoOld.type_id?$emit('compare',oldSelect,newSelect):$store.commit('toastMsg', 'Type not same')">
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
    props: ['imperiumList'],
    data() {
      return {
        oldSelect: null,
        newSelect: null,
        imperiumInfoOld: {},
        imperiumInfoNew: {},
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
  }
</script>

<style scoped>

</style>