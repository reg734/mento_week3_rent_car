$(document).ready(function () {
  $.ajax({
    url: '/api/cars/popular',
    method: 'GET',
    success: function (data) {
      const container = $('#items-carousel');
      container.trigger('destroy.owl.carousel'); // 🔥先摧毀原本的 carousel
      container.html(''); // 清空原本內容

      data.forEach((car, index) => {
        const html = `
          <div class="col-lg-12">
            <div class="de-item mb30">
              <div class="d-img">
                 <img src="${car.image_url}" class="img-fluid" alt="Car Image">
              </div>
              <div class="d-info">
                <div class="d-text">
                  <h4>${car.name}</h4>
                  <div class="d-item_like" data-car-id="${car.id}">
                    <i class="fa fa-heart"></i><span>0</span>
                  </div>
                  <div class="d-atr-group">
                    <span class="d-atr"><img src="/static/images/icons/1.svg" alt="">${car.seats}</span>
                    <span class="d-atr"><img src="/static/images/icons/2.svg" alt="">${car.luggage_capacity}</span>
                    <span class="d-atr"><img src="/static/images/icons/3.svg" alt="">${car.doors}</span>
                    <span class="d-atr"><img src="/static/images/icons/4.svg" alt="">${car.body}</span>
                  </div>
                  <div class="d-price">
                    Daily rate from <span>$${100 + index * 30}</span>
                    <a class="btn-main" href="/cars/${car.id}">Rent Now</a>
                  </div>
                </div>
              </div>
            </div>
          </div>`;

        container.append(html);
      });

      // 若已初始化 Owl Carousel，要重新啟動：
      container.owlCarousel({
        items: 3,
        loop: true,
        margin: 10,
        nav: true,
        responsive: {
          0: { items: 1 },
          768: { items: 2 },
          992: { items: 3 }
        }
      });
      $(document).trigger('cars-loaded');
    },
    error: function () {
      alert("載入車輛資料失敗");
    }
  });
});