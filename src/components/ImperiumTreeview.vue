<template>
  <v-treeview :items="items"></v-treeview>
</template>

<script>
  export default {
    data: () => ({
      items: []
    }),
    props: {
      imperiumData: {
        type: Object,
        default() {
          return {}
        }
      }
    },
    watch: {
      imperiumData: function () {
        this.uploadTreeview()
      }
    },
    methods: {
      uploadTreeview() {

        var id = 0;

        function handle(root, alterKey) {
          var result = [];

          // fallback
          if (root.constructor === Object || root.constructor === Array) {
            for (var key in root) {
              //debugger;
              // special optimize
              // C : [{keys:[],title:"",type:[],rows:[]}]
              if (key === 'C') {
                var result_ = [];
                for (var i in root[key]) {
                  var cObject = root[key][i];
                  var keyIndex = cObject.keys.indexOf('Key');
                  id += 1;
                  var baseId = id;
                  var result__ = [];
                  cObject.rows.forEach(function (item, index) {
                    id += 1;
                    var newKeys=[];
                    cObject.keys.forEach((item,index)=>{
                      newKeys.push(`${item}:${cObject.type[index]}`)
                    });
                    result__.push({
                      id: id,
                      name: (keyIndex > -1 ? item[keyIndex] : index),
                      children: handle(item, newKeys)
                    })
                  })
                  result_.push({id: baseId, name: cObject.title, children: result__})
                }
                result.push({id: id, name: key + ' [C]', children: result_});
                continue;
              }
              id += 1;
              if (root[key].constructor === Object || root[key].constructor === Array) {
                result.push({id: id, name: key + ' [' + root[key].constructor.name + ']', children: handle(root[key])});
              } else {
                if (alterKey) result.push({id: id, name: key + ' [' + alterKey[key] + '] : ' + root[key]});
                else result.push({id: id, name: key + ' : ' + root[key]});
              }
            }
          } else {
            id += 1;
            return {id: id, name: root.toString()}
          }
          return result;
        }

        var d = handle(this.imperiumData);
        //console.log(d);
        this.items = d;
      }
    }
  }
</script>

<style scoped>
  >>> .v-treeview-node {
    margin-left: 10px !important;
  }

  >>> .v-treeview-node__root {
    padding-top: 4px !important;
    height: auto !important;
  }

  >>> .v-treeview-node__content {
    width: 100px !important;
  }

  >>> .v-treeview-node__label {
    width: 100px !important;
  }
</style>