
$(document).ready(function () {
  $.ajax({
    url: '/api/cars', // 替換成實際 API 路徑
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
                <img src="/static/images/cars/bmw-m5.jpg" class="img-fluid" alt="">
              </div>
              <div class="d-info">
                <div class="d-text">
                  <h4>${car.name}</h4>
                  <div class="d-item_like">
                    <i class="fa fa-heart"></i><span>${Math.floor(Math.random() * 100)}</span>
                  </div>
                  <div class="d-atr-group">
                    <span class="d-atr"><img src="/static/images/icons/1.svg" alt="">${car.seat_number}</span>
                    <span class="d-atr"><img src="/static/images/icons/2.svg" alt="">N/A</span>
                    <span class="d-atr"><img src="/static/images/icons/3.svg" alt="">${car.door_number}</span>
                    <span class="d-atr"><img src="/static/images/icons/4.svg" alt="">${car.body}</span>
                  </div>
                  <div class="d-price">
                    Daily rate from <span>$${100 + index * 30}</span>
                    <a class="btn-main" href="/car/${car.id}">Rent Now</a>
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
    },
    error: function () {
      alert("載入車輛資料失敗");
    }
  });
});

