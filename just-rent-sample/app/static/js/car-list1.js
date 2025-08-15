$(document).ready(function () {
    $.ajax({
        url: `/api/cars`,
        method: 'GET',
        success: function (data) {
            const carListContainer = $('#car-list .row');
            carListContainer.empty();

            data.forEach(function(car) {
                const carHtml = `
                <div class="col-xl-4 col-lg-6">
                    <div class="de-item mb30">
                        <div class="d-img">
                            <img src="${car.image_url || '/static/images/cars/jeep-renegade.jpg'}" class="img-fluid" alt="">
                        </div>
                        <div class="d-info">
                            <div class="d-text">
                                <h4>${car.name}</h4>
                                <div class="d-item_like">
                                    <i class="fa fa-heart"></i><span>25</span>
                                </div>
                                <div class="d-atr-group">
                                    <span class="d-atr"><img src="/static/images/icons/1.svg" alt="">${car.seats}</span>
                                    <span class="d-atr"><img src="/static/images/icons/2.svg" alt="">${car.luggage_capacity}</span>
                                    <span class="d-atr"><img src="/static/images/icons/3.svg" alt="">${car.doors}</span>
                                    <span class="d-atr"><img src="/static/images/icons/4.svg" alt="">${car.body}</span>
                                </div>
                                <div class="d-price">
                                    Daily rate from <span>$${Number(car.price).toFixed(2)}</span>
                                    <a class="btn-main" href="/cars/${car.id}">Rent Now</a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                `;
                carListContainer.append(carHtml);
            });
        },
        error: function () {
            $('#car-list .row').html('<p>載入車輛資料失敗</p>');
        }
    });
});