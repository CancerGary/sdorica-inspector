export default class ViewerJSHelper{
  constructor(vue) {
    this.vue = vue;
    this.viewerJS = {};
    this.evalData= {};  // for plugin storage
  }

  fetchViewerJS() {
    this.vue.$http.get(`/api/viewer_js/`).then((response) => {
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

  submitViewerJS(type, code) {
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
    const imperiumId = result.reverse().find(x => x.type_id === typeId).id;
    if (imperiumId) {
      var storageKey = `imperium::${imperiumId}`;
      if (localStorage.getItem(storageKey)) return JSON.parse(localStorage.getItem(storageKey));
      var data = (await this.vue.$http.get(`/api/imperium/${imperiumId}/unpack/`)).data;
      localStorage.setItem(storageKey, JSON.stringify(data));
      return data;
    }
  }

  toastMsg(msg) {
    this.vue.$store.commit('toastMsg', msg)
  }

  runCode(type, data, extraCode) {
    // because of async call, the func eval result should write to `this.vue.interpretedData`
    var code = (type && !extraCode) ? this.getCode(type):extraCode;
    if (this.viewerJS.hasOwnProperty('$DataInit')) data = eval(this.viewerJS['$DataInit'].javascript)(data);
    //console.log('init:', data);
    var result = eval(code)(data);
    if (result) {
      // for async result
      if (result.__proto__ === Promise.prototype) {
        result.then((evalResult) => {
          this.vue.interpretedData = evalResult;
        })
      } else {
        // console.log('result:', result);
        this.vue.interpretedData = result;
      }
    }
  }
}