$(document).ready(function () {
    $.ajax({
        url: `/api/cars`,
        method: 'GET',
        success: function (data) {
            // 動態渲染車輛列表
            const carListContainer = $('#car-list .row');
            carListContainer.empty();

            data.forEach(function(car) {
                const carHtml = `
                <div class="col-lg-12">
                    <div class="de-item-list mb30">
                        <div class="d-img">
                            <img src="${car.image_url || '/static/images/cars/jeep-renegade.jpg'}" class="img-fluid" alt="">
                        </div>
                        <div class="d-info">
                            <div class="d-text">
                                <h4>${car.name}</h4>
                                <div class="d-atr-group">
                                    <ul class="d-atr">
                                        <li><span>Seats:</span>${car.seats}</li>
                                        <li><span>Luggage:</span>${car.luggage_capacity}</li>
                                        <li><span>Doors:</span>${car.doors}</li>
                                        <li><span>Fuel:</span>${car.fuel_type}</li>
                                        <li><span>Year:</span>${car.year}</li>
                                        <li><span>Engine:</span>${car.engine}</li>
                                        <li><span>Drive:</span>${car.drive_type}</li>
                                        <li><span>Type:</span>${car.body}</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                        <div class="d-price">
                            Daily rate from <span>$${car.daily_rate}</span>
                            <a class="btn-main" href="/cars/${car.id}">Rent Now</a>
                        </div>
                        <div class="clearfix"></div>
                    </div>
                </div>
                `;
                carListContainer.append(carHtml);
            });
        },
        error: function (xhr) {
            $('#car-list .row').html('<p>載入車輛資料失敗</p>');
        }
    });
});