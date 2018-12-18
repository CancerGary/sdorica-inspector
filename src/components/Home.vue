<template>
  <v-container fluid fill-height>
    <v-layout
        justify-center
        align-center
    >
      <v-flex text-xs-center>
        <v-tooltip left>
          <v-btn icon large target="_blank" slot="activator">
            <v-icon large>code</v-icon>
          </v-btn>
          <span>Source</span>
        </v-tooltip>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
  export default {
    name: "Home"
  }
</script>

<style scoped>

</style>