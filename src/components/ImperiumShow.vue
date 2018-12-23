<template>
  <div>
    <v-card>
      <v-card-title primary-title>
        <div>
          <h3 class="headline mb-0">Info - {{imperiumInfo.name}}</h3>
        </div>
      </v-card-title>
      <v-card-text>
        <div v-for="(value,index) in imperiumInfo">{{index}}: {{value}}</div>
      </v-card-text>
    </v-card>
    <h3>Treeview</h3>
    <ImperiumTreeview :imperium-data="imperiumData"></ImperiumTreeview>
  </div>
</template>

<script>
  import ImperiumTreeview from "./ImperiumTreeview";

  export default {
    name: "ImperiumShow",
    components: {ImperiumTreeview},
    data() {
      return {
        imperiumData: {},
        imperiumInfo: {},
      }
    },
    created() {
      this.$http.get('/api/imperium/' + this.$route.params.imperium_id).then(response => {
        console.log(response.data);
        this.imperiumInfo = response.data;
      })
      this.$http.get('/api/imperium/' + this.$route.params.imperium_id + '/unpack/').then(response => {
        console.log(response.data);
        this.imperiumData = response.data;
      })
    }
  }
</script>

<style scoped>

</style>