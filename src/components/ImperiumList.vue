<template>
  <div>
    <v-toolbar flat color="white">
      <v-toolbar-title>Imperium</v-toolbar-title>
      <v-divider
          class="mx-2"
          inset
          vertical
      ></v-divider>
      <v-spacer></v-spacer>
      <v-dialog v-model="dialog" max-width="500px">
        <v-btn slot="activator" color="primary" dark class="mb-2">New Item</v-btn>
        <v-card>
          <v-card-title>
            <span class="headline">{{ formTitle }}</span>
          </v-card-title>

          <v-card-text>
            <v-container grid-list-md>
              <v-layout wrap>
                <v-flex xs12>
                  <p>Notice that the system will use the file you upload first. If the file is missing, the system will
                    fetch it from UUID <b>only if UUID exists. </b></p>
                  <p>The form will auto complete UUID by the name of the file you upload.</p>
                </v-flex>
                <v-flex xs12>
                  <v-text-field v-model="editedItem.name" label="Imperium Name"></v-text-field>
                </v-flex>
                <v-flex xs12>
                  <v-text-field v-model="editedItem.uuid" label="UUID (optional)"></v-text-field>
                </v-flex>
                <v-flex xs12>
                  <v-select v-model="editedItem.type_id" label="Type" :items="imperiumTypeSelect"></v-select>
                </v-flex>
                <v-flex xs12>
                  <v-select v-model="editedItem.game_version" label="Game Version"
                            :items="gameVersionSelect"></v-select>
                </v-flex>
                <v-flex xs12>
                  <label class="pr-2">Create Time</label><input v-model="editedItem.create_time" type="datetime-local">
                </v-flex>
                <v-flex xs12>
                  <upload-button :fileChangedCallback="fileChanged" title="Select"></upload-button>
                  <span v-if="editedItem.upload_file">{{editedItem.upload_file.name}}</span>
                </v-flex>
              </v-layout>
            </v-container>
          </v-card-text>

          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="blue darken-1" flat @click="close">Cancel</v-btn>
            <v-btn color="blue darken-1" flat @click="save">Save</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-toolbar>
    <v-data-table
        :headers="headers"
        :items="table_data"
        class="elevation-1"
        :pagination.sync="pagination"
        :rows-per-page-items='[  10, 20,40, { "text": "$vuetify.dataIterator.rowsPerPageAll", "value": -1 } ]'
    >
      <template slot="items" slot-scope="props">
        <td>{{ props.item.id }}</td>
        <td>{{ props.item.name }}</td>
        <td>{{ $moment(props.item.create_time).format("YYYY-MM-DDTHH:mm") }}</td>
        <!--<td>{{props.item.create_time}}</td>-->
        <td>{{ props.item.md5.slice(0,6) }}</td>
        <td>{{ props.item.uuid?props.item.uuid.slice(0,6):null }}</td>
        <td>{{ gameVersionName[props.item.game_version] }}</td>
        <td>{{ imperiumType[props.item.type_id] }}</td>
        <td class="justify-center layout px-0">
          <v-icon v-if="['android','androidExp'].indexOf(imperiumType[props.item.type_id]) > -1"
                  small
                  class="mr-2"
                  @click="handleImperium(props.item)"
          >
            {{props.item.finished?'done':(props.item.celery_task_id?'cached':'play_arrow')}}
          </v-icon>
          <v-icon
              small
              class="mr-2"
              @click="showItem(props.item)"
          >
            remove_red_eye
          </v-icon>
          <v-icon
              small
              class="mr-2"
              @click="editItem(props.item)"
          >
            edit
          </v-icon>
          <v-icon
              small
              @click="deleteItem(props.item)"
          >
            delete
          </v-icon>
        </td>
      </template>
      <template slot="no-data">
        <v-btn color="primary" @click="initialize">Reset</v-btn>
      </template>
    </v-data-table>
  </div>
</template>

<script>
  import UploadButton from 'vuetify-upload-button';

  // const qs = require('qs');
  export default {
    name: "ImperiumList",
    components: {UploadButton},
    data: () => ({
      dialog: false,
      headers: [
        {text: 'ID', value: 'id'},
        {text: 'Name', value: 'name'},
        {text: 'Create Time', value: 'create_time'},
        {text: 'MD5', value: 'md5'},
        {text: 'UUID', value: 'uuid'},
        {text: 'GV', value: 'game_version'},
        {text: 'Type', value: 'type_id', sortable: false},
        {text: 'Actions', value: 'name', sortable: false}
      ],
      pagination: {sortBy: 'create_time', descending: true},
      table_data: [],
      editedIndex: -1,
      editedItem: {},
      defaultItem: {
        name: ''
      },
      upload_file: null,
      snackbar: false,
      snackbarMessage: false,
      error: null,
      imperiumTypeSelect: [],
      gameVersionSelect: [],
      gameVersionName: {}
    }),

    computed: {
      formTitle() {
        return this.editedIndex === -1 ? 'New Item' : 'Edit Item'
      },

      imperiumType() {
        return this.$imperiumType
      }
    },

    watch: {
      dialog(val) {
        val || this.close()
      }
    },

    created() {
      this.initialize()
    },

    methods: {
      fileChanged(file) {
        //console.log(file);
        this.editedItem.upload_file = file;
        if (file.name.length === 36) {
          this.showSnackbarMessage('UUID detected');
          this.editedItem.uuid = file.name;
        }
      },
      initialize() {
        this.$http.get('/api/imperium/').then(response => (
          this.table_data = response.data
        ))
        this.$http.get('/api/game_version/').then(response => {
          this.gameVersionSelect = [];
          response.data.forEach(item => {
            this.gameVersionSelect.push({text: item.name, value: item.id});
            this.gameVersionName[item.id] = item.name;
          })
        })
        this.imperiumType.forEach((item, index) => {
          this.imperiumTypeSelect.push({text: item, value: index})
        })
      },

      editItem(item) {
        this.editedIndex = this.table_data.indexOf(item)
        this.editedItem = Object.assign({}, item)
        this.editedItem.create_time = this.$moment(this.editedItem.create_time).format("YYYY-MM-DDTHH:mm");
        this.dialog = true
      },

      deleteItem(item) {
        const index = this.table_data.indexOf(item)
        confirm('Are you sure you want to delete this item?') && this.$http.delete(this.table_data[index].url).then(response => (response.status === 204 ? this.table_data.splice(index, 1) : undefined))
      },

      showItem(item) {
        this.$router.push({name: 'imperium_show', params: {imperium_id: item.id}})
      },

      handleImperium(item) {
        if (!item.finished) this.$http.get(item.url + 'download_ab/').then(response => {
          this.showSnackbarMessage(response.data)
          item.celery_task_id = 'l'; // for icon show :D
        })
      },

      close() {
        this.dialog = false
        setTimeout(() => {
          this.editedItem = Object.assign({}, this.defaultItem)
          this.editedIndex = -1
        }, 300)
      },

      save() {
        var form = new FormData();
        form.append('name', this.editedItem.name);
        form.append('type_id', this.editedItem.type_id);
        form.append('game_version', this.editedItem.game_version);
        if (this.editedItem.create_time) form.append('create_time', this.editedItem.create_time);
        if (this.editedItem.uuid) form.append('uuid', this.editedItem.uuid);
        if (this.editedItem.upload_file) form.append('upload_file', this.editedItem.upload_file);
        if (this.editedIndex > -1) {
          //Object.assign(this.table_data[this.editedIndex], this.editedItem)
          this.$http.patch(this.editedItem.url, form).then(response => {
            Object.assign(this.table_data[this.editedIndex], response.data);
            this.showSnackbarMessage('Success');
            this.close();
          }).catch(error => {
            this.showSnackbarMessage(error.response.data)
          })
        } else {
          this.$http.post('/api/imperium/', form).then(response => {
            this.table_data.push(response.data);
            this.showSnackbarMessage('Success');
            this.close();
          }).catch(error => {
            this.showSnackbarMessage(error.response.data)
          })
        }
      },
      showSnackbarMessage(msg) {
        this.$store.commit('toastMsg', msg)
      }
    }
  }
</script>

<style scoped>

</style>