import {openDB} from 'idb'

export default class ViewerJSHelper {
  constructor(vue) {
    this.vue = vue;
    this.viewerJS = {};
    this.evalData = {};  // for plugin storage
    this.dbName = 'Sdorica Inspector';
    this.dbVersion = 1;
  }

  fetchViewerJS() {
    return this.vue.$http.get(`/api/viewer_js/`).then((response) => {
      response.data.forEach((value) => {
        this.viewerJS[value.unity_type] = {javascript: value.javascript, id: value.id}
        // execute $ViewerInit
      });
      if (this.viewerJS.hasOwnProperty('$ViewerInit')) {
        eval(this.viewerJS['$ViewerInit'].javascript)(this);
      }
    })
  }

  getCode(type) {
    return this.viewerJS[type];
  }

  getTypes() {
    return Object.keys(this.viewerJS);
  }

  submitViewerJS(type, code) {
    if (!type) return this.toastMsg('No type yet');
    var _ = this.viewerJS[type];
    var p = undefined;
    if (_) p = this.vue.$http.put(`/api/viewer_js/${type}/`, {
      javascript: code,
      unity_type: type
    });
    else p = this.vue.$http.post('/api/viewer_js/', {javascript: code, unity_type: type});
    p.then(
      () => {
        this.toastMsg('Success');
        this.fetchViewerJS()
      }
    ).catch((error) => (this.toastMsg(error.response.data)))
  }

  async getImperium(typeName,) { // for viewerJS
    var typeId = this.vue.$imperiumType.indexOf(typeName);
    if (typeId < 0) return;
    const {data: result} = await this.vue.$http.get('/api/imperium/');
    var i = result.find(x => x.type_id === typeId);
    if (i) {
      var imperiumId = i.id;
      var storageKey = `imperium::${imperiumId}`;
      // query
      const db = await openDB(this.dbName, this.dbVersion, {
        upgrade(db) {
          db.createObjectStore('imperium');
        }
      });
      var queryResult = await db.get('imperium', storageKey);
      if (queryResult) {
        console.log('hit cache:', storageKey);
        return queryResult;
      } else {
        // or fetch & write
        var data = (await this.vue.$http.get(`/api/imperium/${imperiumId}/unpack/`)).data;
        await db.put('imperium', data, storageKey);
        return data;
      }
    } else return this.toastMsg(`Can't find any ${typeName}`);
  }

  toastMsg(msg) {
    this.vue.$store.commit('toastMsg', msg)
  }

  runCode(type, data, extraCode, callback) {
    // because of async call, the func eval result should write to `this.vue.interpretedData`
    try {
      var code = (type && !extraCode) ? this.getCode(type).javascript : extraCode;
      // check initFirst here?
      if (this.viewerJS.hasOwnProperty('$DataInit')) data = eval(this.viewerJS['$DataInit'].javascript)(data);
      //console.log('init:', data);
      var result = eval(code)(data);
      if (callback) {
        // for async result
        if (result && (typeof result.then == "function")) {
          return result.then(callback);
        } else {
          // console.log('result:', result);
          return callback(result);
        }
      } else return result;
    } catch (error) {
      this.toastMsg(error.message);
      throw error;
    }
  }
}