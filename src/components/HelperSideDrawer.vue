<template>
  <div>
    <v-list dense>
      <v-list-tile @click="openRuleEditDialog()">
        <v-list-tile-action>
          <v-icon>create</v-icon>
        </v-list-tile-action>
        <v-list-tile-content>
          <v-list-tile-title>New Convert Rule</v-list-tile-title>
        </v-list-tile-content>
      </v-list-tile>
      <v-list-tile @click="ruleListDialog=true">
        <v-list-tile-action>
          <v-icon>list_alt</v-icon>
        </v-list-tile-action>
        <v-list-tile-content>
          <v-list-tile-title>Convert Rules list</v-list-tile-title>
        </v-list-tile-content>
      </v-list-tile>
      <v-list-tile v-if="currentABData" @click="0" class="copy-button" data-clipboard-action="copy">
        <v-list-tile-action>
          <v-icon>mdi-content-copy</v-icon>
        </v-list-tile-action>
        <v-list-tile-content>
          <v-list-tile-title>Copy selected md5 url</v-list-tile-title>
        </v-list-tile-content>
      </v-list-tile>
    </v-list>

    <!--convert rule edit form-->
    <v-dialog
        v-model="ruleEditDialog"
        width="500"
    >
      <v-card>
        <v-card-title class="headline">Edit Convert Rule</v-card-title>
        <v-card-text>
          <p>Pattern supports regular expression. You can select the code you want to create pattern for before opening
            editor. You can also submit by API
            <code>POST /api/convert_rule/ {pattern:String,text:String}</code>.
          </p>
          <v-text-field label="Pattern" v-model="ruleOnEditing.pattern"></v-text-field>
          <v-textarea label="Text" rows="2" v-model="ruleOnEditing.text"></v-textarea>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
              color="primary"
              flat
              @click="submitRuleEdit()"
          >
            Submit
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog
        v-model="ruleListDialog"
        width="500"
    >
      <v-card>
        <v-card-title class="headline">Convert Rules</v-card-title>
        <v-card-text>
          <v-list>
            <v-list-tile
                v-for="(item,index) in convertRule"
                :key="item.id"
                @click="openRuleEditDialog(index)"
            >
              <v-list-tile-content>
                <v-list-tile-title>
                  <pre>{{ item.pattern }}</pre>
                </v-list-tile-title>
                <v-list-tile-sub-title>{{ item.text }}</v-list-tile-sub-title>
              </v-list-tile-content>
            </v-list-tile>
          </v-list>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
  import {mapState} from 'vuex'
  import ClipboardJS from 'clipboard';

  export default {
    name: "HelperSideDrawer",
    props: {
      show: Boolean,
      currentABData: {
        type: Object,
        default: null
      }
    },
    data() {
      return {
        ruleEditDialog: false,
        ruleListDialog: false,
        ruleOnEditing: {
          id: -1,
          pattern: "",
          text: ""
        },
        ruleIndex: -1,
        copyButton: null
      }
    },
    mounted() {
      this.copyButton = new ClipboardJS('.copy-button', {
        // eslint-disable-next-line
        text: (trigger) => {
          return this.currentABData.url
        }
      });

      this.copyButton.on('success', () => {
        this.$store.commit('toastMsg', 'Copied.')
      });
      this.copyButton.on('error', () => {
        this.$store.commit('toastMsg', this.currentABData.url)
      });
    },
    methods: {
      // console.log(item);
      openRuleEditDialog(index) {
        if (typeof index === 'number') {
          this.ruleOnEditing = JSON.parse(JSON.stringify(this.$store.state.convertRule[index]));
          this.ruleIndex = index;
        } else {
          this.ruleOnEditing = {
            id: -1,
            pattern: window.getSelection().toString(), // use selected text
            text: ""
          };
          this.ruleIndex = -1;
        }
        this.ruleEditDialog = true
      },
      submitRuleEdit() {
        // for local state ,just update locally
        var newl = JSON.parse(JSON.stringify(this.$store.state.convertRule));
        if (this.ruleOnEditing.id !== -1) {
          // update
          this.$http.put(`/api/convert_rule/${this.ruleOnEditing.id}/`, this.ruleOnEditing).then((response) => {
              newl[this.ruleIndex] = response.data;
              this.$store.commit('updateConvertRule', newl);
              this.ruleEditDialog = false
            }
          )
        } else {
          // create
          this.$http.post(`/api/convert_rule/`, this.ruleOnEditing).then((response) => {
            newl.push(response.data);
            this.$store.commit('updateConvertRule', newl);
            this.ruleEditDialog = false;
          })
        }
      },
    },
    computed: {
      ...mapState(['convertRule']),
    },
  }
</script>

<style scoped>

</style>