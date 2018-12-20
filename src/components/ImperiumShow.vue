<template>
  <v-treeview :items="items"></v-treeview>
</template>

<script>
  export default {
    data: () => ({
      items: []
    }),
    created() {
      this.$http.get('/api/imperium/' + this.$route.params.imperium_id + '/unpack/').then(response => {
        console.log(response.data);

        var id = 0;

        function handle(root) {
          var result = [];

          // fallback
          if (root.constructor === Object || root.constructor === Array) {
            for (var key in root) {
              //debugger;
              // special optimize
              // C : [{keys:[],title:"",]
              if (key==='C') {
                var result_=[];
                for (var i in root[key]) {
                  var cObject=root[key][i];
                  var keyIndex=cObject.keys.indexOf('Key');
                  id+=1;
                  var baseId=id;
                  var result__=[];
                  cObject.rows.forEach(function (item,index) {
                    id+=1;
                    result__.push({id:id,name:(keyIndex > -1 ?item[keyIndex]:index),children:handle(item)})
                  })
                  result_.push({id:baseId,name:cObject.title,children:result__})
                }
                result.push({id:id,name:key+' [C]',children:result_});
                continue;
              }
              id += 1;
              if (root[key].constructor === Object || root[key].constructor === Array) {
                result.push({id: id, name: key + ' [' + root[key].constructor.name + ']', children: handle(root[key])});
              } else {
                result.push({id: id, name: key + ' : ' + root[key]})
              }
            }
          } else {
            id += 1;
            return {id: id, name: root.toString()}
          }
          return result;
        }

        var d = handle(response.data);
        console.log(d);
        this.items = d;
      })
    }

  }
</script>

<style scoped>
  >>>.v-treeview-node{
    margin-left:10px!important;
  }
  >>>.v-treeview-node__root{
    padding-top: 4px!important;
    height: auto!important;
  }
  >>>.v-treeview-node__content{
    width: 100px!important;
  }
  >>>.v-treeview-node__label{
    width: 100px!important;
  }
</style>