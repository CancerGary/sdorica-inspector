<template>
  <ImperiumTreeview :imperium-data="imperiumData"></ImperiumTreeview>
</template>

<script>
  import ImperiumTreeview from "./ImperiumTreeview";

  export default {
    name: "ImperiumShow",
    components: {ImperiumTreeview},
    data() {
      return {
        imperiumData: {},
      }
    },
    created() {
      this.$http.get('/api/imperium/' + this.$route.params.imperium_id + '/unpack/').then(response => {
        console.log(response.data);
        this.imperiumData = response.data;
      })
    }
  }
</script>

<style scoped>

</style>