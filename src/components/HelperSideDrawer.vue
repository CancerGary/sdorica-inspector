<template>
  <div>
    <v-list dense>
      <v-list-tile @click.stop="openRuleEditDialog()">
        <v-list-tile-action>
          <v-icon>create</v-icon>
        </v-list-tile-action>
        <v-list-tile-content>
          <v-list-tile-title>{{ $vuetify.t('$vuetify.sideHelper.newConvertRule') }}</v-list-tile-title>
        </v-list-tile-content>
      </v-list-tile>
      <v-list-tile @click.stop="ruleListDialog=true">
        <v-list-tile-action>
          <v-icon>list_alt</v-icon>
        </v-list-tile-action>
        <v-list-tile-content>
          <v-list-tile-title>{{ $vuetify.t('$vuetify.sideHelper.convertRulesList') }}</v-list-tile-title>
        </v-list-tile-content>
      </v-list-tile>
      <v-list-tile v-show="currentABData" @click="promptUrl">
        <v-list-tile-action>
          <v-icon>link</v-icon>
        </v-list-tile-action>
        <v-list-tile-content>
          <v-list-tile-title>{{ $vuetify.t('$vuetify.sideHelper.promptMD5url') }}</v-list-tile-title>
        </v-list-tile-content>
      </v-list-tile>
      <v-list-tile @click="toContainerSearch">
        <v-list-tile-action>
          <v-icon>search</v-icon>
        </v-list-tile-action>
        <v-list-tile-content>
          <v-list-tile-title>{{ $vuetify.t('$vuetify.sideHelper.searchSelected') }}</v-list-tile-title>
        </v-list-tile-content>
      </v-list-tile>
      <v-list-tile @click="toggleDark">
        <v-list-tile-action>
          <v-icon>mdi-theme-light-dark</v-icon>
        </v-list-tile-action>
        <v-list-tile-content>
          <v-list-tile-title>{{ $vuetify.t('$vuetify.sideHelper.darkMode') }}</v-list-tile-title>
        </v-list-tile-content>
      </v-list-tile>
      <v-list-tile @click="changeLocale">
        <v-list-tile-action>
          <v-icon>mdi-google-translate</v-icon>
        </v-list-tile-action>
        <v-list-tile-content>
          <v-list-tile-title>{{ $vuetify.t('$vuetify.sideHelper.locale') }}</v-list-tile-title>
        </v-list-tile-content>
      </v-list-tile>
      <v-list-tile @click="toLogout">
        <v-list-tile-action>
          <v-icon>mdi-logout-variant</v-icon>
        </v-list-tile-action>
        <v-list-tile-content>
          <v-list-tile-title>{{ $vuetify.t('$vuetify.sideHelper.logout') }}</v-list-tile-title>
        </v-list-tile-content>
      </v-list-tile>
    </v-list>

    <!--convert rule edit form-->
    <v-dialog
        v-model="ruleEditDialog"
        width="500" persistent
    >
      <v-card>
        <v-card-title class="headline">{{ $vuetify.t('$vuetify.sideHelper.editConvertRule') }}</v-card-title>
        <v-card-text>
          <div v-html="$vuetify.t('$vuetify.sideHelper.editConvertRuleIntro')"></div>
          <v-text-field :label="$vuetify.t('$vuetify.sideHelper.editPattern')"
                        v-model="ruleOnEditing.pattern"></v-text-field>
          <v-textarea :label="$vuetify.t('$vuetify.sideHelper.editText')" rows="2"
                      v-model="ruleOnEditing.text"></v-textarea>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
              flat
              @click="ruleEditDialog=false"
          >
            {{ $vuetify.t('$vuetify.form.cancel') }}
          </v-btn>
          <v-btn
              color="primary"
              flat
              @click="submitRuleEdit()"
          >
            {{ $vuetify.t('$vuetify.form.submit') }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog
        v-model="ruleListDialog"
        width="500"
    >
      <v-card>
        <v-card-title class="headline">{{ $vuetify.t('$vuetify.sideHelper.convertRulesList') }}</v-card-title>
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
      promptUrl() {
        prompt('AB URL', this.currentABData.url);
      },
      toContainerSearch() {
        this.$router.push({name: 'container_search', query: {q: window.getSelection().toString()}});
      },
      toLogout() {
        confirm('Are you sure to logout?') && (window.location.href = '/api-auth/logout/?next=/');
      },
      toggleDark() {
        // this.$vuetify.dark = this.dark;
        // console.log(this.darkMode);

        this.$store.commit('setDarkMode', !this.darkMode);
        localStorage.setItem('darkMode', this.darkMode);
      },
      changeLocale() {
        let locales = ['en', 'zhHant'];
        this.$vuetify.lang.current = locales[(locales.indexOf(this.$vuetify.lang.current) + 1) % locales.length];
        localStorage.setItem('locale', this.$vuetify.lang.current);
      }
    },
    computed: {
      ...mapState(['convertRule', 'darkMode']),
    },
  }
</script>

<style scoped>

</style>