<template>
  <v-treeview :items="items"></v-treeview>
</template>

<script>
  export default {
    props: {
      imperiumData: {
        default() {
          return {}
        }
      },
      sortCKeys: {
        type: Boolean,
        default: false
      }
    },
    computed: {
      items() {
        var id = 0;

        function handle(root, alterKey, sortCKeys) {
          var result = [];
          // fallback
          if (root.constructor === Object || root.constructor === Array) {
            for (var key in root) {
              //debugger;
              // special optimize
              // C : [{keys:[],title:"",type:[],rows:[]}]
              if (key === 'C') {
                var result_ = [];
                // loop by table
                for (var title in root[key]) {
                  var cObject = root[key][title];
                  var keyIndex = cObject.K.indexOf('Key');
                  id += 1;
                  var baseId = id;
                  var result__ = [];
                  if (sortCKeys && keyIndex > -1) cObject.D.sort((a, b) => a[keyIndex].localeCompare(b[keyIndex]));
                  cObject.D.forEach(function (item, index) {
                    id += 1;
                    var newKeys = [];
                    cObject.K.forEach((item, index) => {
                      newKeys.push(`${item}:${cObject.T[index]}`)
                    });
                    result__.push({
                      id: id,
                      name: (keyIndex > -1 ? item[keyIndex] : index),
                      children: handle(item, newKeys)
                    })
                  })
                  result_.push({id: baseId, name: title, children: result__})
                }
                result.push({id: id, name: key + ' [C]', children: result_});
                continue;
              }
              id += 1;
              if (root[key] && (root[key].constructor === Object || root[key].constructor === Array)) {
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

        return handle(this.imperiumData, null, this.sortCKeys);
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