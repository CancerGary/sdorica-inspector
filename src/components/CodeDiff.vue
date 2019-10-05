<template>
  <div v-html="html" :class="{'d2h-invert':darkMode}"></div>
</template>

<script>
  import {Diff2Html} from 'diff2html'
  import 'diff2html/dist/diff2html.css'
  import {mapState} from "vuex";

  export default {
    name: 'code-diff',
    props: {
      diffString: {
        type: String,
        default: "--- left\n+++ right"
      },
      context: {
        type: Number,
        default: 1
      },
      outputFormat: {
        type: String,
        default: 'line-by-line'
      }
    },
    computed: {
      html() {
        return this.createdHtml(this.diffString, this.context, this.outputFormat)
      }, ...mapState(['darkMode'])
    },
    methods: {
      createdHtml(diffString, context, outputFormat) {
        let html = Diff2Html.getPrettyHtml(diffString, {
          inputFormat: 'diff',
          outputFormat: outputFormat,
          showFiles: false,
          matching: 'lines',
          // matchWordsThreshold:2
        })
        return html
      }
    }
  }
</script>

<style>
  .d2h-file-header {
    display: none
  }

  .d2h-invert {
    filter: invert(100%);
    color: black;
  }
</style>