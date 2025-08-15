$(document).ready(function () {
    const carId = $('#section-car-details').data('car-id'); // 從 data-car-id 屬性中取得 car_id

    $.ajax({
        url: `/api/cars/${carId}`,
        method: 'GET',
        success: function (data) {
            // 更新車子的名字
            $('#car-name').text(data.name);

            // 更新車子的租金
            $('#car-daily-rate').text(`$${Number(data.price).toFixed(2)}`);

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
 * 更新輪播圖片 - 摧毀重做版本
 * @param {Array} newImages - 新的圖片 URL 陣列
 */
function updateCarouselImages(newImages) {
    if (!newImages || !Array.isArray(newImages) || newImages.length === 0) {
        console.warn('沒有提供有效的圖片資料');
        return;
    }

    const slider = $('#slider-carousel');

    // 1. 摧毀原本的 Carousel
    if (slider.hasClass('owl-loaded')) {
        slider.trigger('destroy.owl.carousel');
        slider.removeClass('owl-loaded owl-drag');
        slider.find('.owl-stage-outer').children().unwrap();
        slider.html(''); // 清空內容
    }

    // 2. 重新加入新的圖片項目
    newImages.forEach((imgUrl, index) => {
        slider.append(`
            <div class="item">
                <img src="${imgUrl}" alt="Car image ${index + 1}"
                     onerror="this.src='/static/images/car-single/1.jpg'">
            </div>
        `);
    });

    // 3. 重新初始化 Carousel
    slider.owlCarousel({
        items: 1,
        loop: true,
        autoplay: false,
        autoplayHoverPause: true,
        nav: false,
        dots: false,
        responsive: {
            0: { items: 1 },
            600: { items: 1 },
            1000: { items: 1 }
        }
    });

    console.log('已摧毀重建輪播圖片和縮圖，共', newImages.length, '張');
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