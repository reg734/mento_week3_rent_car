$(document).ready(function () {
    // 監聽 cars-loaded 事件，當車輛資料載入完成後執行
    $(document).on('cars-loaded', function () {
        // 1. 取得所有車輛卡片的 car_id
        const cardElements = $('.d-item_like[data-car-id]');
        const carIds = cardElements.map(function () {
            return $(this).data('car-id');
        }).get();

        // 2. 取得每台車的收藏狀態與數量
        $.ajax({
            url: '/api/my_favorites/status',
            type: 'GET',
            traditional: true,  // 這個很重要！
            data: { car_ids: carIds },
            success: function (statusList) {
                cardElements.each(function () {
                    const carId = $(this).data('car-id');
                    // 轉換成數字來比對
                    const status = statusList.find(s => s.car_id ===
                        parseInt(carId));

                    const isFavorite = status && status.is_favorite;
                    const count = status ? status.count : 0;
                    const heartColor = isFavorite ? 'red' : 'gray';
                    // 更新愛心顏色與數字
                    $(this).find('.fa-heart').css('color',
                        heartColor);
                    $(this).find('span').text(count);
                    $(this).data('is-favorite', isFavorite);
                });
            }
        });
    });

    // 3. 點擊愛心切換收藏狀態（這個保持在 document.ready中）
    $(document).on('click', '.d-item_like .fa-heart',
        function () {
            const $like = $(this).closest('.d-item_like');
            const carId = $like.data('car-id');
            const isFavorite = $like.data('is-favorite') ===
                true;

            if (isFavorite) {
                // 取消收藏
                $.ajax({
                    url: `/api/my_favorites/${carId}`,
                    type: 'DELETE',
                    success: function () {
                        $like.find('.fa-heart').css('color', 'gray');
                        let count = parseInt($like.find('span').text(),
                            10) || 0;
                        $like.find('span').text(Math.max(count - 1,
                            0));
                        $like.data('is-favorite', false);
                    }
                });
            } else {
                // 加入收藏
                $.ajax({
                    url: '/api/my_favorites',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({ car_id: carId }),
                    success: function () {
                        $like.find('.fa-heart').css('color', 'red');
                        let count = parseInt($like.find('span').text(),
                            10) || 0;
                        $like.find('span').text(count + 1);
                        $like.data('is-favorite', true);
                    }
                });
            }
        });
});