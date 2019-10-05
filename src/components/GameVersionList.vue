<template>
  <div>
    <v-toolbar flat>
      <v-toolbar-title>Game Version</v-toolbar-title>
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
                  <v-text-field v-model="editedItem.name" label="Version Name"></v-text-field>
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
    >
      <template slot="items" slot-scope="props">
        <td>{{ props.item.id }}</td>
        <td>{{ props.item.name }}</td>
        <td>{{ props.item.create_time }}</td>
        <td class="justify-center layout px-0">
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
  export default {
    name: "GameVersionList",
    data: () => ({
      dialog: false,
      headers: [
        {text: 'ID', value: 'id'},
        {text: 'Name', value: 'name'},
        {text: 'Create Time', value: 'create_time'},
        {text: 'Actions', value: 'name', sortable: false}
      ],
      table_data: [],
      editedIndex: -1,
      editedItem: {},
      defaultItem: {
        name: ''
      }
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

    methods: {
      initialize() {
        this.$http.get('/api/game_version/').then(response => (
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
        confirm('Are you sure you want to delete this item?') && this.$http.delete(this.table_data[index].url).then(response => (response.status===204?this.table_data.splice(index, 1):undefined))
      },

      showItem(item){
        // this.$route.go('/game_version/1')
      },

      close() {
        this.dialog = false
        setTimeout(() => {
          this.editedItem = Object.assign({}, this.defaultItem)
          this.editedIndex = -1
        }, 300)
      },

      save() {
        if (this.editedIndex > -1) {
          //Object.assign(this.table_data[this.editedIndex], this.editedItem)
          this.$http.patch(this.editedItem.url,this.editedItem).then(response => (
            Object.assign(this.table_data[this.editedIndex] , response.data)
          ))
        } else {
          this.$http.post('/api/game_version/',this.editedItem).then(response => (
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