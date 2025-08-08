  $(document).ready(function() {
      // 專門處理收藏頁面的移除功能
      $('.d-item_like').on('click', function(e) {
          e.preventDefault();
          const $heart = $(this);
          const $item = $heart.closest('.de-item-list');
          const carId = $heart.data('car-id');

          if (confirm('確定要移除此車輛的收藏嗎？')) {
              $.ajax({
                  url: `/api/my_favorites/${carId}`,
                  type: 'DELETE',
                  success: function() {
                      $item.fadeOut(500, function() {
                          $(this).remove();
                          if ($('.de-item-list').length ===
   0) {
                              location.reload();
                          }
                      });
                  }
              });
          }
      });
  });