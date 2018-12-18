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
                  <v-text-field v-model="editedItem.name" label="Imperium Name"></v-text-field>
                </v-flex>
                <v-flex xs12>
                  <v-text-field v-model="editedItem.type_id" label="Type ID"></v-text-field>
                </v-flex>
                <v-flex xs12>
                  <v-text-field v-model="editedItem.game_version" label="Game Version"></v-text-field>
                </v-flex>
                <upload-button :fileChangedCallback="fileChanged"></upload-button>
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
        :rows-per-page-items='[  10, 20,40, { "text": "$vuetify.dataIterator.rowsPerPageAll", "value": -1 } ]'
    >
      <template slot="items" slot-scope="props">
        <td>{{ props.item.id }}</td>
        <td>{{ props.item.name }}</td>
        <td>{{ props.item.create_time }}</td>
        <td>{{ props.item.md5 }}</td>
        <td>{{ props.item.game_version }}</td>
        <td>{{ props.item.type_id }}</td>
        <td class="layout px-0">
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

  const qs = require('qs');
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
        {text: 'GV', value: 'game_version'},
        {text: 'Type',value: 'type_id',sortable: false},
        {text: 'Actions', value: 'name', sortable: false}
      ],
      table_data: [],
      editedIndex: -1,
      editedItem: {},
      defaultItem: {
        name: ''
      },
      upload_file: null
    }),

    computed: {
      formTitle() {
        return this.editedIndex === -1 ? 'New Item' : 'Edit Item'
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

    mounted() {
      this.initialize()
    },

    methods: {
      fileChanged(file) {
        console.log(file);
        this.editedItem.upload_file = file;
      },
      initialize() {
        this.$http.get('/api/imperium/').then(response => (
          this.table_data = response.data
        ))
      },

      editItem(item) {
        this.editedIndex = this.table_data.indexOf(item)
        this.editedItem = Object.assign({}, item)
        this.dialog = true
      },

      deleteItem(item) {
        const index = this.table_data.indexOf(item)
        confirm('Are you sure you want to delete this item?') && this.$http.delete(this.table_data[index].url).then(response => (response.status === 204 ? this.table_data.splice(index, 1) : undefined))
      },

      showItem(item) {

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
        if (this.editedItem.upload_file) form.append('upload_file', this.editedItem.upload_file);
        if (this.editedIndex > -1) {
          //Object.assign(this.table_data[this.editedIndex], this.editedItem)
          this.$http.patch(this.editedItem.url, form).then(response => (
            Object.assign(this.table_data[this.editedIndex], response.data)
          ))
        } else {
          this.$http.post('/api/imperium/', form).then(response => (
            this.table_data.push(response.data)
          ))
        }
        this.close()
      }
    }
  }
</script>

<style scoped>

</style>