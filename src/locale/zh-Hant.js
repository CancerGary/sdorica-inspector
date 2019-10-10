export default {
  dataIterator: {
    rowsPerPageText: '每頁記錄數：',
    rowsPerPageAll: '全部',
    pageText: '{0}-{1} 共 {2} 條',
    noResultsText: '沒有找到匹配記錄',
    nextPage: '下一頁',
    prevPage: '上一頁'
  },
  dataTable: {
    rowsPerPageText: '每頁行數：'
  },
  noDataText: '無可用數據',
  carousel: {
    prev: '以前的視覺',
    next: '下一個視覺'
  },
  sideHelper: {
    newConvertRule:'新的轉換規則',
    convertRulesList:'轉換規則表',
    promptMD5url: '顯示選定md5的URL',
    searchSelected:'搜尋選定文字',
    darkMode: '明暗外觀切換',
    locale: '更換語言',
    eruda: '召喚Eruda (偵錯)',
    logout: '登出',

    editConvertRule: '編輯轉換規則',
    editConvertRuleIntro: '<p>支援正規表達式。 你可以先選定要作為規則的文字，再點選創建。 你也可以透過API <code>POST /api/convert_rule/ {pattern:String,text:String}</code>來提交規則。</p>',
    editPattern:'規則',
    editText:'轉換后文字',

  },
  form:{
    cancel:'取消',
    submit:'提交'
  }
};
