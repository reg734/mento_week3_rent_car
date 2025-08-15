$(document).ready(function() {
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
});
