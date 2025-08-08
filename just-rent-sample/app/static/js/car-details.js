$(document).ready(function () {
    const carId = $('#section-car-details').data('car-id'); // 從 data-car-id 屬性中取得 car_id

    $.ajax({
        url: `/api/cars/${carId}`,
        method: 'GET',
        success: function (data) {
            // 更新車子的名字
            $('#car-name').text(data.name);

            // 更新車子的租金
            $('#car-daily-rate').text(`$${data.daily_rate}`);

            // 簡單的圖片替換方法 - 不摧毀 Carousel
            updateCarouselImages(data.images);

            // 動態更新 HTML 中的內容
            updateCarSpecifications(data);
        },
        error: function (xhr) {
            if (xhr.status === 404) {
                $('#car-name').html('<p>Car not found</p>');
            } else {
                $('#car-name').html('<p>An error occurred</p>');
            }
        }
    });
});

/**
 * 更新輪播圖片 - 簡單版本
 * @param {Array} newImages - 新的圖片 URL 陣列
 */
function updateCarouselImages(newImages) {
    // 檢查是否有有效的圖片資料
    if (!newImages || !Array.isArray(newImages) || newImages.length === 0) {
        console.warn('沒有提供有效的圖片資料');
        return;
    }

    const carouselImages = $('#slider-carousel .item img');

    // 如果 Carousel 還沒初始化，先初始化
    if (!$('#slider-carousel').hasClass('owl-loaded')) {
        initializeCarousel();
    }

    // 1. 更新主輪播圖片
    carouselImages.each(function (index) {
        const img = $(this);
        const newSrc = newImages[index] || newImages[0]; // 如果沒有對應圖片，使用第一張

        // 設定新的圖片 src
        img.attr('src', newSrc);
        img.attr('alt', `Car image ${index + 1}`);

        // 加入錯誤處理
        img.off('error').on('error', function () {
            console.warn('圖片載入失敗:', newSrc);
            // 載入失敗時使用預設圖片
            this.src = `/static/images/car-single/${index + 1}.jpg`;
        });

        // 載入成功時的處理
        img.off('load').on('load', function () {
            console.log('圖片載入成功:', newSrc);
        });
    });

    // 2. 更新縮圖按鈕的圖片
    updateThumbnailImages(newImages);

    // 如果 API 提供的圖片比現有的多，需要添加新的項目
    if (newImages.length > carouselImages.length) {
        const slider = $('#slider-carousel');

        for (let i = carouselImages.length; i < newImages.length; i++) {
            slider.append(`
                <div class="item">
                    <img src="${newImages[i]}" 
                         alt="Car image ${i + 1}"
                         onerror="this.src='/static/images/car-single/1.jpg'">
                </div>
            `);
        }

        // 刷新 Carousel 以包含新添加的項目
        slider.trigger('refresh.owl.carousel');

        // 同時更新縮圖（如果有新增項目）
        updateThumbnailImages(newImages);
    }

    console.log('已更新輪播圖片和縮圖，共', Math.max(newImages.length, carouselImages.length), '張');
}

/**
 * 更新縮圖按鈕的圖片
 * @param {Array} newImages - 新的圖片 URL 陣列
 */
function updateThumbnailImages(newImages) {
    const thumbnailImages = $('.owl-thumbs .owl-thumb-item img');

    // 更新現有的縮圖
    thumbnailImages.each(function (index) {
        const img = $(this);
        const newSrc = newImages[index] || newImages[0];

        img.attr('src', newSrc);
        img.attr('alt', `Thumbnail ${index + 1}`);

        // 縮圖的錯誤處理
        img.off('error').on('error', function () {
            console.warn('縮圖載入失敗:', newSrc);
            this.src = `/static/images/car-single/${index + 1}.jpg`;
        });
    });

    // 如果需要添加新的縮圖按鈕
    if (newImages.length > thumbnailImages.length) {
        const thumbsContainer = $('.owl-thumbs');

        for (let i = thumbnailImages.length; i < newImages.length; i++) {
            const isActive = i === 0 && thumbnailImages.length === 0 ? 'active' : '';
            thumbsContainer.append(`
                <button class="owl-thumb-item ${isActive}">
                    <img src="${newImages[i]}" 
                         alt="Thumbnail ${i + 1}"
                         onerror="this.src='/static/images/car-single/1.jpg'">
                </button>
            `);
        }
    }

    // 如果 API 圖片較少，隱藏多餘的縮圖按鈕
    if (newImages.length < thumbnailImages.length) {
        $('.owl-thumbs .owl-thumb-item').slice(newImages.length).hide();
    } else {
        // 確保所有需要的縮圖按鈕都顯示
        $('.owl-thumbs .owl-thumb-item').slice(0, newImages.length).show();
    }

    console.log('已更新', Math.min(newImages.length, thumbnailImages.length), '個縮圖按鈕');
}

/**
 * 初始化 Owl Carousel（如果尚未初始化）
 */
function initializeCarousel() {
    const slider = $('#slider-carousel');

    if (!slider.hasClass('owl-loaded')) {
        slider.owlCarousel({
            items: 1,
            loop: true,
            autoplay: false,
            autoplayHoverPause: true,
            nav: true,
            navText: [
                '<i class="fa fa-chevron-left"></i>',
                '<i class="fa fa-chevron-right"></i>'
            ],
            dots: true,
            responsive: {
                0: { items: 1 },
                600: { items: 1 },
                1000: { items: 1 }
            }
        });
        console.log('Carousel 初始化完成');
    }
}

/**
 * 更新車輛規格資訊
 * @param {Object} data - API 回傳的車輛資料
 */
function updateCarSpecifications(data) {
    $('.de-spec .d-row').each(function () {
        const title = $(this).find('.d-title').text().trim();
        const valueElement = $(this).find('.d-value');

        switch (title) {
            case 'Body':
                valueElement.text(data.body || 'N/A');
                break;
            case 'Seat':
                valueElement.text(data.seats ? `${data.seats} seats` : 'N/A');
                break;
            case 'Door':
                valueElement.text(data.doors ? `${data.doors} doors` : 'N/A');
                break;
            case 'Luggage':
                valueElement.text(data.luggage_capacity || 'N/A');
                break;
            case 'Fuel Type':
                valueElement.text(data.fuel_type || 'N/A');
                break;
            case 'Engine':
                valueElement.text(data.engine || 'N/A');
                break;
            case 'Year':
                valueElement.text(data.year || 'N/A');
                break;
            case 'Mileage':
                valueElement.text(data.mileage ? `${data.mileage} km` : 'N/A');
                break;
            case 'Transmission':
                valueElement.text(data.transmission || 'N/A');
                break;
            case 'Drive':
                valueElement.text(data.drive_type || 'N/A');
                break;
            case 'Fuel Economy':
                valueElement.text(data.fuel_economy ? `${data.fuel_economy} km/l` : 'N/A');
                break;
            case 'Exterior Color':
                valueElement.text(data.exterior_color || 'N/A');
                break;
            case 'Interior Color':
                valueElement.text(data.interior_color || 'N/A');
                break;
            default:
                valueElement.text('N/A');
                break;
        }
    });

    console.log('車輛規格資訊已更新');
}