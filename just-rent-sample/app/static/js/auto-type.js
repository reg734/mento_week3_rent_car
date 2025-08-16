$(document).ready(function () {
  // 假設你有一個地址 API，這裡用靜態資料範例
  var addresses = ['台北站', '台中站', '高雄站'];

  var addressSource = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.whitespace,
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    local: addresses
    // 若用 API，請改用 remote: { url: 'API_URL?q=%QUERY', wildcard: '%QUERY' }
  });

  $('#autocomplete, #autocomplete2').typeahead(
    {
      hint: true,
      highlight: true,
      minLength: 1
    },
    {
      name: 'addresses',
      source: addressSource
    }
  );

  // 針對每個 input-group 的 dropdown-item，填入對應 input
  // 因為 typeahead 會改變 DOM 結構，所以使用更直接的方式
  $('.input-group .dropdown-menu .dropdown-item').on('click', function(e) {
    e.preventDefault();
    
    // 找到最近的 input-group，然後找到其中的 input
    // typeahead 會將 input 包在 .twitter-typeahead 內
    var group = $(this).closest('.input-group');
    var targetInput = group.find('input.tt-input').first();
    
    // 如果找不到 typeahead 的 input，試著找原始的 input
    if (!targetInput.length) {
      targetInput = group.find('input[type="text"]').first();
    }
    
    if (targetInput.length) {
      var valueToSet = $(this).text();
      
      // 嘗試使用 typeahead 的方法設定值
      try {
        targetInput.typeahead('val', valueToSet);
      } catch(e) {
        // 如果 typeahead 方法失敗，直接設定值
        targetInput.val(valueToSet);
      }
      
      // 觸發 change 事件，確保其他相關的處理器能接收到變更
      targetInput.trigger('change');
      
      // 除錯：確認值已經填入
      console.log('填入值:', valueToSet, '到 input:', targetInput.attr('name') || targetInput.attr('id'));
    } else {
      console.log('找不到對應的 input 欄位');
    }
  });
});