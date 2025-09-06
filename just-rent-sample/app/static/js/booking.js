(function () {
    'use strict';

    // ===== Booking API 模組 - 集中管理所有訂單相關的 API 呼叫 =====
    const BookingAPI = {
        // 查詢可用車輛
        searchAvailable: function(params) {
            return fetch(`/api/bookings/available-cars?${params}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                });
        },
        
        // 取得訂單列表
        getAll: function() {
            return fetch('/api/bookings', {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            }).then(response => response.json());
        },
        
        // 建立新訂單（舊版本，保留兼容性）
        create: function(orderData) {
            return fetch('/api/bookings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(orderData)
            }).then(response => {
                if (response.status === 401) {
                    // 未登入，導向登入頁
                    alert('請先登入後再進行預訂');
                    window.location.href = '/login?next=/booking';
                    return null;
                }
                return response.json();
            });
        },
        
        // === 新增：預訂 API（同時建立 Booking 和 Order）===
        createReservation: function(reservationData) {
            return fetch('/api/bookings/reserve', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken() 
                },
                body: JSON.stringify(reservationData)
            }).then(response => {
                if (response.status === 401) {
                    alert('請先登入後再進行預訂');
                    window.location.href = '/login?next=/booking';
                    return null;
                }
                return response.json();
            });
        },
        
        // === 新增：付款處理 API ===
        processPayment: function(paymentData) {
            return fetch('/api/payments/process', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken() 
                },
                body: JSON.stringify(paymentData)
            }).then(response => response.json());
        },
        
        // 取消訂單
        cancel: function(orderId) {
            return fetch(`/api/bookings/cancel/${orderId}`, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken() 
                }
            }).then(response => response.json());
        }
    };
    
    // === 新增：CSRF Token 取得函數 ===
    function getCSRFToken() {
        const token = document.querySelector('meta[name="csrf-token"]');
        return token ? token.getAttribute('content') : '';
    }

    // 將 BookingAPI 掛載到 window 以供其他地方使用
    window.BookingAPI = BookingAPI;

    // === 新增：全域變數儲存當前預訂資訊 ===
    window.currentReservation = {
        bookingId: null,
        orderId: null,
        carId: null,
        carName: null,
        amount: null,
        rentalDays: null,
        isReserved: false  // 標記是否已預訂但未付款
    };

    // ===== 初始化 =====
    document.addEventListener('DOMContentLoaded', function () {
        initBookingForm();
        initCancelButtons();
        // 如果在訂單列表頁面，載入訂單
        if (window.location.pathname.includes('/orders') || window.location.pathname.includes('/bookings')) {
            loadOrders();
        }
    });

    /**
     * 初始化預訂表單
     */
    function initBookingForm() {
        const form = document.getElementById('contact_form');
        if (form) {
            form.addEventListener('submit', function (e) {
                e.preventDefault();
                searchAvailableCars();
            });
        }
    }

    // ===== API 呼叫相關 =====

    /**
     * 查詢可用車輛
     */
    function searchAvailableCars() {
        // 收集表單資料
        const carType = document.querySelector('input[name="Car_Type"]:checked').value;
        
        // 處理 typeahead 修改後的輸入框
        const pickupInput = document.getElementById('autocomplete');
        const dropoffInput = document.getElementById('autocomplete2');
        
        // 詳細除錯：檢查 DOM 結構
        console.log('=== 地址輸入框檢查 ===');
        console.log('pickup input:', pickupInput);
        console.log('pickup input value:', pickupInput.value);
        console.log('pickup input parent:', pickupInput.parentElement);
        console.log('dropoff input:', dropoffInput);
        console.log('dropoff input value:', dropoffInput.value);
        console.log('dropoff input parent:', dropoffInput.parentElement);
        
        // 檢查是否有 typeahead
        const hasTypeahead = typeof $ !== 'undefined' && $(pickupInput).data('ttTypeahead');
        console.log('有 typeahead?', hasTypeahead);
        
        // 嘗試多種方式取值
        let pickupLocation, dropoffLocation;
        
        // 方法1: 直接取 input.value
        pickupLocation = pickupInput.value.trim();
        dropoffLocation = dropoffInput.value.trim();
        console.log('方法1 - 直接取值:', {pickup: pickupLocation, dropoff: dropoffLocation});
        
        // 方法2: 如果有 typeahead，用 typeahead 方法
        if (hasTypeahead) {
            try {
                const typeaheadPickup = $(pickupInput).typeahead('val');
                const typeaheadDropoff = $(dropoffInput).typeahead('val');
                console.log('方法2 - typeahead 取值:', {pickup: typeaheadPickup, dropoff: typeaheadDropoff});
                
                if (typeaheadPickup) pickupLocation = typeaheadPickup.trim();
                if (typeaheadDropoff) dropoffLocation = typeaheadDropoff.trim();
            } catch(e) {
                console.log('typeahead 取值失敗:', e);
            }
        }
        
        // 方法3: 檢查 twitter-typeahead 容器內的隱藏 input
        const ttContainer1 = pickupInput.closest('.twitter-typeahead');
        const ttContainer2 = dropoffInput.closest('.twitter-typeahead');
        if (ttContainer1) {
            const hiddenInput1 = ttContainer1.querySelector('input.tt-hint') || ttContainer1.querySelector('input.tt-input');
            if (hiddenInput1 && hiddenInput1.value) {
                console.log('方法3 - 隱藏input1值:', hiddenInput1.value);
                pickupLocation = hiddenInput1.value.trim();
            }
        }
        if (ttContainer2) {
            const hiddenInput2 = ttContainer2.querySelector('input.tt-hint') || ttContainer2.querySelector('input.tt-input');
            if (hiddenInput2 && hiddenInput2.value) {
                console.log('方法3 - 隱藏input2值:', hiddenInput2.value);
                dropoffLocation = hiddenInput2.value.trim();
            }
        }
        
        console.log('最終取得的地址:', {pickup: pickupLocation, dropoff: dropoffLocation});
        console.log('=== 地址檢查結束 ===');
        const pickupDate = document.getElementById('date-picker').value;
        const pickupTime = document.getElementById('pickup-time').value;
        const returnDate = document.getElementById('date-picker-2').value;
        const returnTime = document.getElementById('collection-time').value;

        // 驗證必填欄位
        if (!pickupDate || !returnDate) {
            showAlert('請選擇取車和還車日期', 'danger');
            return;
        }

        if (!pickupLocation || !dropoffLocation) {
            showAlert('請選擇取車和還車地點', 'danger');
            return;
        }

        // 建立查詢參數
        const params = new URLSearchParams({
            car_type: carType,
            pickup_location: pickupLocation,
            dropoff_location: dropoffLocation,
            pickup_date: pickupDate,
            pickup_time: pickupTime || '00:00',
            return_date: returnDate,
            return_time: returnTime || '00:00'
        });

        // 顯示載入中
        showLoading();

        // 使用 BookingAPI 模組呼叫 API
        BookingAPI.searchAvailable(params)
            .then(data => {
                hideLoading();
                handleApiResponse(data);
            })
            .catch(error => {
                hideLoading();
                console.error('Error:', error);
                showAlert('發生錯誤，請稍後再試', 'danger');
            });
    }

    /**
     * 處理 API 回應
     */
    function handleApiResponse(data) {
        // 根據不同狀態處理
        if (data.status === 'error') {
            // 顯示錯誤訊息
            showAlert(data.message, 'danger');
        } else if (data.status === 'warning') {
            // 顯示警告訊息
            showAlert(data.message, 'warning');
        } else if (data.status === 'success') {
            // 顯示可用車輛
            if (data.cars && data.cars.length > 0) {
                displayCars(data.cars,
                    data.rental_days);
            } else {
                showAlert('沒有找到可用車輛', 'info');
            }
        }
    }

    // ===== UI 顯示相關 =====

    /**
     * 顯示提示訊息
     */
    function showAlert(message, type) {
        // 移除現有的 alert
        const existingAlerts =
            document.querySelectorAll('.alert.dynamic-alert');
        existingAlerts.forEach(alert => alert.remove());

        // 建立 alert div
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} 
  alert-dismissible fade show dynamic-alert`;
        alertDiv.setAttribute('role', 'alert');
        alertDiv.innerHTML = `
              ${message}
              <button type="button" class="btn-close" 
  data-bs-dismiss="alert" aria-label="Close"></button>
          `;

        // 找到要插入的位置（表單上方）
        const form =
            document.getElementById('contact_form');
        if (form && form.parentNode) {
            form.parentNode.insertBefore(alertDiv,
                form);
        } else {
            // 如果找不到表單，插入到主要內容區
            const container =
                document.querySelector('.container');
            if (container) {
                container.insertBefore(alertDiv,
                    container.firstChild);
            }
        }

        // 5秒後自動移除
        setTimeout(() => {
            if (alertDiv && alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    /**
     * 顯示車輛在 Modal 中
     */
    function displayCars(cars, rentalDays) {
        // 建立車輛 HTML
        let carsHTML = '<div class="row">';

        cars.forEach(car => {
            const totalPrice = car.price * rentalDays;
            carsHTML += `
                  <div class="col-md-6 mb-3">
                      <div class="card">
                          <div class="card-body">
                              <h5 
  class="card-title">${car.name}</h5>
                              <p class="card-text">
                                  
  <strong>車型：</strong>${car.body}<br>
                                  
  <strong>座位：</strong>${car.seats} 人<br>
                                  
  <strong>車門：</strong>${car.doors} 門<br>
                                  
  <strong>行李：</strong>${car.luggage_capacity} 件<br>
                                  
  <strong>等級：</strong>${car.car_level}<br>
                                  
  <strong>每日價格：</strong>NT$ ${car.price}<br>
                                  <hr>
                                  <strong 
  class="text-primary">總價：NT$ ${totalPrice} 
  (${rentalDays}天)</strong>
                              </p>
                              <button class="btn 
  btn-primary w-100" onclick="selectCarWithPayment(${car.id})">
                                  立即預訂
                              </button>
                          </div>
                      </div>
                  </div>
              `;
        });

        carsHTML += '</div>';

        // 檢查是否有 modal，如果沒有就建立一個
        let modal =
            document.getElementById('availableCarsModal');
        if (!modal) {
            createModal();
            modal =
                document.getElementById('availableCarsModal');
        }

        // 更新 modal 內容
        const modalBody =
            modal.querySelector('.modal-body');
        if (modalBody) {
            modalBody.innerHTML = carsHTML;
        }

        // 更新 modal 標題
        const modalTitle =
            modal.querySelector('.modal-title');
        if (modalTitle) {
            modalTitle.textContent = `可用車輛 (共 
  ${cars.length} 輛)`;
        }

        // 顯示 modal
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();

        // 重新取得地址資料，避免 typeahead 問題
        const pickupInput = document.getElementById('autocomplete');
        const dropoffInput = document.getElementById('autocomplete2');
        let currentPickupLocation, currentDropoffLocation;
        
        console.log('=== 儲存資料時的地址檢查 ===');
        
        // 使用相同的取值邏輯
        currentPickupLocation = pickupInput.value.trim();
        currentDropoffLocation = dropoffInput.value.trim();
        
        // 如果有 typeahead，嘗試用 typeahead 方法
        const hasTypeahead = typeof $ !== 'undefined' && $(pickupInput).data('ttTypeahead');
        if (hasTypeahead) {
            try {
                const typeaheadPickup = $(pickupInput).typeahead('val');
                const typeaheadDropoff = $(dropoffInput).typeahead('val');
                if (typeaheadPickup) currentPickupLocation = typeaheadPickup.trim();
                if (typeaheadDropoff) currentDropoffLocation = typeaheadDropoff.trim();
            } catch(e) {
                console.log('儲存時 typeahead 取值失敗:', e);
            }
        }
        
        console.log('儲存時最終地址:', {pickup: currentPickupLocation, dropoff: currentDropoffLocation});
        
        // 儲存查詢資料供後續使用
        window.bookingData = {
            pickup_location: currentPickupLocation,
            dropoff_location: currentDropoffLocation,
            pickup_date: document.getElementById('date-picker').value,
            pickup_time: document.getElementById('pickup-time').value || '00:00',
            return_date: document.getElementById('date-picker-2').value,
            return_time: document.getElementById('collection-time').value || '00:00',
            rental_days: rentalDays
        };
        
        // === 新增：儲存車輛資料供 selectCar 使用 ===
        window.lastSearchedCars = cars;
        
        // 除錯：印出儲存的資料
        console.log('儲存的 bookingData:', window.bookingData);
        console.log('儲存的 cars:', window.lastSearchedCars);
    }

    /**
     * 建立 Modal（如果不存在）
     */
    function createModal() {
        const modalHTML = `
              <div class="modal fade" 
  id="availableCarsModal" tabindex="-1" 
  aria-labelledby="availableCarsModalLabel" 
  aria-hidden="true">
                  <div class="modal-dialog modal-lg">
                      <div class="modal-content">
                          <div class="modal-header">
                              <h5 class="modal-title" 
  id="availableCarsModalLabel">可用車輛</h5>
                              <button type="button" 
  class="btn-close" data-bs-dismiss="modal" 
  aria-label="Close"></button>
                          </div>
                          <div class="modal-body">
                              <!-- 車輛內容將動態插入這裡 
  -->
                          </div>
                          <div class="modal-footer">
                              <button type="button" 
  class="btn btn-secondary" 
  data-bs-dismiss="modal">關閉</button>
                          </div>
                      </div>
                  </div>
              </div>
          `;

        document.body.insertAdjacentHTML('beforeend',
            modalHTML);
    }

    /**
     * 顯示載入動畫
     */
    function showLoading() {
        const btn =
            document.getElementById('send_message');
        if (btn) {
            btn.disabled = true;
            btn.setAttribute('data-original-text',
                btn.innerHTML);
            btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>搜尋中...';
        }
    }

    /**
     * 隱藏載入動畫
     */
    function hideLoading() {
        const btn =
            document.getElementById('send_message');
        if (btn) {
            btn.disabled = false;
            const originalText =
                btn.getAttribute('data-original-text') || 'Find a Vehicle';
            btn.innerHTML = originalText;
        }
    }

    // ===== 訂單相關 =====

    /**
     * === 新版：選擇車輛並建立預訂（包含付款流程）===
     * 這是新的主要函數，會建立 Booking + Order，然後開啟付款 Modal
     */
    window.selectCarWithPayment = function (carId) {
        // 確認是否有預訂資料
        if (!window.bookingData) {
            showAlert('請重新查詢車輛', 'danger');
            return;
        }

        const bookingData = window.bookingData;
        
        // 尋找選中的車輛資訊（需要價格資訊）
        const selectedCar = window.lastSearchedCars?.find(car => car.id === carId);
        if (!selectedCar) {
            showAlert('無法找到車輛資訊，請重新搜尋', 'danger');
            return;
        }

        // 計算總金額
        const totalAmount = selectedCar.price * bookingData.rental_days;

        // 準備預訂資料
        let pickupDateTime, returnDateTime;

        try {
            // 格式化日期時間，避免時區問題
            function formatDateTime(dateStr, timeStr) {
                let formattedDate = dateStr;
                if (dateStr.includes(',')) {
                    const date = new Date(dateStr + ' 12:00:00');
                    const year = date.getFullYear();
                    const month = String(date.getMonth() + 1).padStart(2, '0');
                    const day = String(date.getDate()).padStart(2, '0');
                    formattedDate = `${year}-${month}-${day}`;
                }
                const time = timeStr || '00:00';
                return `${formattedDate}T${time}:00`;
            }
            
            pickupDateTime = formatDateTime(bookingData.pickup_date, bookingData.pickup_time);
            returnDateTime = formatDateTime(bookingData.return_date, bookingData.return_time);
            
        } catch (error) {
            console.error('日期格式錯誤:', error);
            showAlert('日期格式錯誤，請重新選擇', 'danger');
            return;
        }

        // 準備預訂資料（新的 API 格式）
        const reservationData = {
            car_id: carId,
            pickup_location: bookingData.pickup_location,
            dropoff_location: bookingData.dropoff_location,
            pickup_datetime: pickupDateTime,
            return_datetime: returnDateTime,
            amount: totalAmount
        };
        
        console.log('=== 準備建立預訂 ===');
        console.log('reservationData:', reservationData);

        // 顯示確認對話框
        const confirmMessage = `
確定要預訂此車輛嗎？

車輛：${selectedCar.name}
取車：${bookingData.pickup_location} (${bookingData.pickup_date} ${bookingData.pickup_time})
還車：${bookingData.dropoff_location} (${bookingData.return_date} ${bookingData.return_time})
租期：${bookingData.rental_days} 天
總金額：NT$ ${totalAmount.toLocaleString()}

預訂後將需要完成付款。
        `.trim();

        if (!confirm(confirmMessage)) {
            return;
        }

        // 關閉車輛選擇 modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('availableCarsModal'));
        if (modal) {
            modal.hide();
        }

        // 顯示處理中
        showProcessing();

        // 使用新的預訂 API（同時建立 Booking 和 Order）
        BookingAPI.createReservation(reservationData)
        .then(data => {
            hideProcessing();

            if (data && data.status === 'success') {
                // 儲存預訂資訊到全域變數
                window.currentReservation = {
                    bookingId: data.booking_id,
                    orderId: data.order_id,
                    carId: carId,
                    carName: selectedCar.name,
                    amount: totalAmount,
                    rentalDays: bookingData.rental_days,
                    isReserved: true
                };
                
                // 更新 bookingData 加入預訂資訊
                window.bookingData.booking_id = data.booking_id;
                window.bookingData.order_id = data.order_id;
                window.bookingData.car_name = selectedCar.name;
                window.bookingData.amount = totalAmount;

                console.log('=== 預訂成功，準備開啟付款 ===');
                console.log('currentReservation:', window.currentReservation);

                // 檢查是否有付款 Modal
                const paymentModal = document.getElementById('paymentModal');
                if (paymentModal) {
                    // 直接顯示付款 Modal，不需要經過 showPaymentModal 的檢查
                    showPaymentModalDirect();
                } else {
                    // 如果沒有付款 Modal，顯示提示並導向
                    alert('預訂成功！請前往付款頁面完成付款。');
                    window.location.href = '/booking/payment/' + data.booking_id;
                }
                
            } else if (data) {
                showAlert(data.message || '預訂失敗', 'danger');
            }
        })
        .catch(error => {
            hideProcessing();
            console.error('Reservation Error:', error);
            showAlert('預訂失敗，請稍後再試', 'danger');
        });
    };

    /**
     * === 舊版：選擇車輛並直接建立訂單（保留兼容性）===
     * 注意：這個函數需要全域存取，所以掛載到 window 物件
     */
    window.selectCar = function (carId) {
        // 確認是否有預訂資料
        if (!window.bookingData) {
            showAlert('請重新查詢車輛', 'danger');
            return;
        }

        const bookingData = window.bookingData;

        // 準備訂單資料
        let pickupDateTime, returnDateTime;

        try {
            // 除錯：印出原始資料
            console.log('準備組合的資料:');
            console.log('pickup_date:', bookingData.pickup_date);
            console.log('pickup_time:', bookingData.pickup_time);
            console.log('return_date:', bookingData.return_date);
            console.log('return_time:', bookingData.return_time);
            
            // 格式化日期時間，避免時區問題
            function formatDateTime(dateStr, timeStr) {
                // 如果日期是 "August 18, 2025" 格式，轉換為 "2025-08-18"
                let formattedDate = dateStr;
                if (dateStr.includes(',')) {
                    const date = new Date(dateStr + ' 12:00:00'); // 加上中午時間避免時區問題
                    const year = date.getFullYear();
                    const month = String(date.getMonth() + 1).padStart(2, '0');
                    const day = String(date.getDate()).padStart(2, '0');
                    formattedDate = `${year}-${month}-${day}`;
                }
                
                // 確保時間格式正確
                const time = timeStr || '00:00';
                
                // 組合為本地時間格式
                return `${formattedDate}T${time}:00`;
            }
            
            pickupDateTime = formatDateTime(bookingData.pickup_date, bookingData.pickup_time);
            returnDateTime = formatDateTime(bookingData.return_date, bookingData.return_time);
            
            console.log('格式化後的時間:');
            console.log('pickup:', pickupDateTime);
            console.log('return:', returnDateTime);
            
        } catch (error) {
            console.error('日期格式錯誤:', error);
            showAlert('日期格式錯誤，請重新選擇', 'danger');
            return;
        }

        const orderData = {
            car_id: carId,
            pickup_location: bookingData.pickup_location,
            dropoff_location: bookingData.dropoff_location,
            pickup_datetime: pickupDateTime,
            return_datetime: returnDateTime
        };
        
        // 除錯：印出要傳送的訂單資料
        console.log('=== 要傳送給 API 的訂單資料 ===');
        console.log('orderData:', orderData);
        console.log('JSON.stringify(orderData):', JSON.stringify(orderData));

        // 顯示確認對話框
        if (!confirm(`確定要預訂這輛車嗎？\n取車地點：${bookingData.pickup_location}\n還車地點：${bookingData.dropoff_location}\n租期：${ bookingData.rental_days } 天`)) {
              return;
          }

          // 關閉 modal
          const modal = bootstrap.Modal.getInstance(document.getElementById('availableCarsModal'));
          if (modal) {
              modal.hide();
          }

          // 顯示處理中
          showProcessing();

          // 使用 BookingAPI 模組發送訂單請求
          BookingAPI.create(orderData)
          .then(data => {
              hideProcessing();

              if (data && data.status === 'success') {
                  // 顯示成功訊息
                  showSuccessMessage(data.message || '訂單建立成功！');

                  // 2秒後導向訂單頁面
                  setTimeout(() => {
                      window.location.href = '/account/orders';
                  }, 2000);
              } else if (data) {
                  showAlert(data.message || '訂單建立失敗', 'danger');
              }
          })
          .catch(error => {
              hideProcessing();
              console.error('Error:', error);
              showAlert('發生錯誤，請稍後再試', 'danger');
          });
      };

      /**
       * 顯示處理中的遮罩
       */
      function showProcessing() {
          const processingDiv =
  document.createElement('div');
          processingDiv.id = 'processing-overlay';
          processingDiv.innerHTML = `
        < div style = "position: fixed; top: 0; left: 
    0; width: 100 %; height: 100 %;
    background: rgba(0, 0, 0, 0.5);
    z - index: 9999;
    display: flex; align - items:
    center; justify - content: center; ">
        < div class="text-center text-white" >
                      <div class="spinner-border 
  text-light" style="width: 3rem; height: 3rem;"></div>
                      <div 
  class="mt-3">正在處理訂單...</div>
                  </div >
              </div >
        `;
          document.body.appendChild(processingDiv);
      }

      /**
       * 隱藏處理中的遮罩
       */
      function hideProcessing() {
          const overlay =
  document.getElementById('processing-overlay');
          if (overlay) {
              overlay.remove();
          }
      }

    // === 新增：統一狀態處理函數 ===
    
    /**
     * 取得訂單狀態資訊（統一處理邏輯，避免狀態不一致）
     */
    function getOrderStatusInfo(order) {
        // 檢查狀態一致性
        let orderBadgeClass, orderText, paymentBadgeClass, paymentText, paymentAction = '';
        
        // 如果付款已過期，訂單狀態應該視為已取消
        if (order.payment_status === 'expired') {
            orderBadgeClass = 'bg-danger';
            orderText = 'Expired/Cancelled';
            paymentBadgeClass = 'bg-danger';
            paymentText = 'Expired';
            
            // 記錄不一致的狀況
            if (order.status === 'confirmed') {
                console.warn(`訂單 #${order.id} 狀態不一致: booking_status=${order.status}, payment_status=${order.payment_status}`);
            }
        }
        // 如果已付款，訂單應為確認狀態
        else if (order.payment_status === 'paid') {
            orderBadgeClass = 'bg-success';
            orderText = 'Confirmed';
            paymentBadgeClass = 'bg-success';
            paymentText = 'Paid';
        }
        // 如果付款待處理
        else if (order.payment_status === 'pending') {
            orderBadgeClass = 'bg-warning';
            orderText = 'Pending Payment';
            paymentBadgeClass = 'bg-warning';
            paymentText = 'Pending';
            
            // 只有 pending 狀態才顯示補付款按鈕
            paymentAction = `<br><button class="btn btn-sm btn-primary retry-payment" 
                               data-booking-id="${order.id}" data-amount="${order.amount}"
                               style="font-size: 0.7rem; padding: 2px 6px;">Pay Now</button>`;
        }
        // 其他狀態
        else {
            // 根據訂單狀態決定
            if (order.status === 'confirmed') {
                orderBadgeClass = 'bg-success';
                orderText = 'Confirmed';
            } else if (order.status === 'pending') {
                orderBadgeClass = 'bg-warning';
                orderText = 'Pending';
            } else if (order.status === 'cancelled') {
                orderBadgeClass = 'bg-danger';
                orderText = 'Cancelled';
            } else if (order.status === 'completed') {
                orderBadgeClass = 'bg-info';
                orderText = 'Completed';
            } else {
                orderBadgeClass = 'bg-secondary';
                orderText = order.status || 'Unknown';
            }
            
            paymentBadgeClass = 'bg-secondary';
            paymentText = order.payment_status || 'N/A';
        }
        
        return {
            orderBadgeClass,
            orderText,
            paymentBadgeClass,
            paymentText,
            paymentAction
        };
    }

    // === 新增：付款相關函數 ===
    
    /**
     * 顯示付款 Modal (帶安全檢查)
     * 這個函數會被外部呼叫時使用
     */
    window.showPaymentModal = function() {
        const reservation = window.currentReservation;
        if (!reservation || !reservation.isReserved) {
            showAlert('沒有有效的預訂資訊', 'danger');
            return;
        }
        
        showPaymentModalDirect();
    };

    /**
     * 直接顯示付款 Modal (無安全檢查)
     * 這個函數用於預訂成功後直接開啟付款視窗
     */
    window.showPaymentModalDirect = function() {
        const reservation = window.currentReservation;
        
        // 更新訂單摘要
        const orderSummary = document.getElementById('order-summary');
        if (orderSummary && window.bookingData && reservation) {
            orderSummary.innerHTML = `
                <table class="table table-sm mb-0">
                    <tbody>
                        <tr>
                            <td width="30%"><strong>訂單編號</strong></td>
                            <td>#${reservation.orderId || 'PENDING'}</td>
                        </tr>
                        <tr>
                            <td><strong>車輛名稱</strong></td>
                            <td>${reservation.carName || 'N/A'}</td>
                        </tr>
                        <tr>
                            <td><strong>取車地點</strong></td>
                            <td>${window.bookingData.pickup_location || 'N/A'}</td>
                        </tr>
                        <tr>
                            <td><strong>取車時間</strong></td>
                            <td>${window.bookingData.pickup_date || 'N/A'} ${window.bookingData.pickup_time || ''}</td>
                        </tr>
                        <tr>
                            <td><strong>還車地點</strong></td>
                            <td>${window.bookingData.dropoff_location || 'N/A'}</td>
                        </tr>
                        <tr>
                            <td><strong>還車時間</strong></td>
                            <td>${window.bookingData.return_date || 'N/A'} ${window.bookingData.return_time || ''}</td>
                        </tr>
                        <tr>
                            <td><strong>租賃天數</strong></td>
                            <td>${reservation.rentalDays || 1} 天</td>
                        </tr>
                        <tr class="table-primary">
                            <td><strong>應付金額</strong></td>
                            <td><strong class="text-primary">NT$ ${(reservation.amount || 0).toLocaleString()}</strong></td>
                        </tr>
                    </tbody>
                </table>
            `;
        }
        
        // 顯示付款 Modal
        try {
            const paymentModal = new bootstrap.Modal(document.getElementById('paymentModal'));
            paymentModal.show();
            console.log('付款 Modal 已開啟');
        } catch (error) {
            console.error('開啟付款 Modal 失敗:', error);
            alert('無法開啟付款視窗，請重新操作');
        }
    };

    /**
     * 處理付款成功
     * 這個函數會被 booking.html 中的 TapPay 程式碼呼叫
     */
    window.handlePaymentSuccess = function(result) {
        console.log('=== 付款成功 ===');
        console.log('Payment result:', result);
        
        // 清除預訂狀態
        window.currentReservation.isReserved = false;
        
        // 建立成功訊息
        const successMessage = `
付款成功！

訂單編號：${result.order_number || window.currentReservation.orderId}
交易編號：${result.transaction_id || 'N/A'}
金額：NT$ ${window.currentReservation.amount.toLocaleString()}

您的預訂已確認，感謝您的訂購！
        `.trim();
        
        // 關閉付款 Modal
        const paymentModal = bootstrap.Modal.getInstance(document.getElementById('paymentModal'));
        if (paymentModal) {
            paymentModal.hide();
        }
        
        // 顯示成功訊息
        showSuccessMessage(successMessage);
        
        // 重置預訂資料
        window.currentReservation = {
            bookingId: null,
            orderId: null,
            carId: null,
            carName: null,
            amount: null,
            rentalDays: null,
            isReserved: false
        };
        
        // 導向訂單頁面
        setTimeout(() => {
            if (confirm('是否要查看訂單詳情？')) {
                window.location.href = '/account/orders';
            }
        }, 2000);
    };

    /**
     * 處理付款失敗
     * 這個函數會被 booking.html 中的 TapPay 程式碼呼叫
     */
    window.handlePaymentFailure = function(result) {
        console.log('=== 付款失敗 ===');
        console.log('Payment error:', result);
        
        const errorMessage = `
付款失敗

錯誤訊息：${result.message || '交易處理失敗'}
錯誤代碼：${result.error_code || 'UNKNOWN'}

請檢查您的信用卡資訊後重試，或聯繫客服。

注意：您的預訂仍然有效，請儘快完成付款。
        `.trim();
        
        alert(errorMessage);
        
        // 如果需要釋放預訂
        if (result.release_booking) {
            window.currentReservation.isReserved = false;
            // 關閉付款 Modal
            const paymentModal = bootstrap.Modal.getInstance(document.getElementById('paymentModal'));
            if (paymentModal) {
                paymentModal.hide();
            }
        }
    };

    /**
     * 取消預訂
     * 這個函數會被付款 Modal 的取消按鈕呼叫
     */
    window.cancelReservation = function() {
        const reservation = window.currentReservation;
        if (!reservation || !reservation.isReserved) {
            // 沒有有效預訂，直接關閉 Modal
            const paymentModal = bootstrap.Modal.getInstance(document.getElementById('paymentModal'));
            if (paymentModal) {
                paymentModal.hide();
            }
            return;
        }
        
        if (confirm('⚠️ 確定要完全取消此預訂嗎？\n\n取消後車輛將會釋放，您需要重新預訂。\n如果只是想稍後付款，請點擊「稍後付款」按鈕。')) {
            showProcessing();
            
            BookingAPI.cancel(reservation.bookingId)
            .then(data => {
                hideProcessing();
                if (data && data.success) {
                    alert('預訂已完全取消，車輛已釋放');
                    
                    // 重置預訂狀態
                    window.currentReservation.isReserved = false;
                    
                    // 關閉付款 Modal
                    const paymentModal = bootstrap.Modal.getInstance(document.getElementById('paymentModal'));
                    if (paymentModal) {
                        paymentModal.hide();
                    }
                    
                    // 可選：導向車輛搜尋頁面
                    if (confirm('是否要重新搜尋車輛？')) {
                        window.location.href = '/booking';
                    }
                } else {
                    showAlert(data?.message || '取消失敗', 'danger');
                }
            })
            .catch(error => {
                hideProcessing();
                console.error('Cancel error:', error);
                showAlert('取消失敗，請稍後再試', 'danger');
            });
        }
    };

    /**
     * 退出付款 (不取消預訂) - 全域函數
     * 這個函數可以被 booking.html 和補付款流程使用
     */
    window.exitPayment = function() {
        // 關閉付款 Modal，但不取消預訂
        const paymentModal = bootstrap.Modal.getInstance(document.getElementById('paymentModal'));
        if (paymentModal) {
            paymentModal.hide();
        }
        
        // 顯示提示訊息
        alert('您的預訂已保留，可以稍後在訂單頁面重新付款。請注意：預訂將在3分鐘後自動取消。');
        
        // 可選：導向訂單頁面
        if (confirm('是否要前往訂單頁面查看？')) {
            window.location.href = '/account/orders';
        }
    };

    /**
     * 顯示成功訊息
     */
    function showSuccessMessage(message) {
        const successDiv = document.createElement('div');
        successDiv.innerHTML = `
            <div style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
                        background: white; padding: 30px; border-radius: 10px; 
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1); z-index: 10000;
                        text-align: center;">
                <i class="fa fa-check-circle text-success" style="font-size: 48px;"></i>
                <h4 class="mt-3">${message}</h4>
                <p class="text-muted">即將跳轉至訂單頁面...</p>
            </div>
        `;
        document.body.appendChild(successDiv);
    }

    // ===== 訂單管理相關 =====
    
    /**
     * 載入訂單列表
     */
    function loadOrders() {
        console.log('Loading orders...');
        BookingAPI.getAll()
            .then(data => {
                if (data.success) {
                    console.log('Orders loaded:', data.bookings);
                    
                    // 儲存訂單資料供補付款使用
                    window.lastLoadedBookings = data.bookings;
                    
                    // 根據頁面類型渲染訂單
                    if (window.location.pathname.includes('/account/orders')) {
                        renderUserOrders(data.bookings);
                    } else if (window.location.pathname.includes('/admin/bookings')) {
                        renderAdminOrders(data.bookings, data.is_admin);
                    }
                }
            })
            .catch(error => {
                console.error('Error loading orders:', error);
                showAlert('無法載入訂單資料', 'danger');
            });
    }
    
    /**
     * 渲染用戶訂單頁面
     */
    function renderUserOrders(bookings) {
        // 分類訂單 - 修復邏輯，確保稍後付款的訂單正確顯示
        
        console.log('=== 訂單分類調試 ===');
        console.log('所有訂單:', bookings);
        
        const scheduled = bookings.filter(b => {
            // 檢查是否為有效的預定訂單
            const isValidBookingStatus = (b.status === 'pending' || b.status === 'confirmed' || b.status === 'scheduled');
            const isNotCancelled = b.status !== 'cancelled';
            
            // 重要：任何付款已過期的訂單都不應該出現在 scheduled 中
            if (b.payment_status === 'expired') {
                console.warn(`訂單 #${b.id} 付款已過期: booking_status=${b.status}, payment_status=${b.payment_status} -> 移到取消分類`);
                return false;
            }
            
            // 正常情況：booking 狀態有效且沒有被取消且付款未過期
            // 包括：pending/pending（稍後付款），confirmed/paid（已付款），等等
            const shouldShow = isValidBookingStatus && isNotCancelled;
            
            console.log(`訂單 #${b.id}: status=${b.status}, payment_status=${b.payment_status}, shouldShow=${shouldShow}`);
            return shouldShow;
        });
        
        const completed = bookings.filter(b => b.status === 'completed');
        
        // 取消的訂單包括：明確取消的 + 付款已過期的訂單（不管 booking status）
        const cancelled = bookings.filter(b => 
            b.status === 'cancelled' || 
            b.payment_status === 'expired'
        );
        
        console.log('分類結果:');
        console.log('- Scheduled:', scheduled.length, scheduled.map(b => `#${b.id}(${b.status}/${b.payment_status})`));
        console.log('- Completed:', completed.length);
        console.log('- Cancelled:', cancelled.length, cancelled.map(b => `#${b.id}(${b.status}/${b.payment_status})`));
        
        // 渲染預定訂單
        const scheduledBody = document.querySelector('#scheduled-orders-body');
        if (scheduledBody) {
            scheduledBody.innerHTML = scheduled.map(order => {
                // 決定訂單狀態和付款狀態（確保一致性）
                const statusInfo = getOrderStatusInfo(order);
                
                return `
                <tr>
                    <td><span class="d-lg-none d-sm-block">Order ID</span>
                        <div class="badge bg-gray-100 text-dark">#${order.order_id || order.id}</div>
                    </td>
                    <td><span class="d-lg-none d-sm-block">Car Name</span><span class="bold">${order.car_name}</span></td>
                    <td><span class="d-lg-none d-sm-block">Pick Up Location</span>${order.pickup_location}</td>
                    <td><span class="d-lg-none d-sm-block">Drop Off Location</span>${order.dropoff_location}</td>
                    <td><span class="d-lg-none d-sm-block">Pick Up Date</span>${formatDateTime(order.pick_up_time)}</td>
                    <td><span class="d-lg-none d-sm-block">Return Date</span>${formatDateTime(order.return_time)}</td>
                    <td>
                        <div class="badge rounded-pill ${statusInfo.orderBadgeClass}">${statusInfo.orderText}</div>
                    </td>
                    <td>
                        <div class="badge rounded-pill ${statusInfo.paymentBadgeClass}">${statusInfo.paymentText}</div>
                        ${order.amount ? `<br><small class="text-muted">NT$ ${order.amount.toLocaleString()}</small>` : ''}
                        ${statusInfo.paymentAction}
                    </td>
                    <td>
                        <div style="display: flex; justify-content: center; align-items: center;">
                            <button class="btn btn-danger btn-xs btn-cancel-order" data-order-id="${order.id}"
                                style="padding: 2px 8px; font-size: 0.8rem;">Cancel</button>
                        </div>
                    </td>
                </tr>
                `;
            }).join('');
        }
        
        // 渲染完成訂單
        const completedBody = document.querySelector('#completed-orders-body');
        if (completedBody) {
            completedBody.innerHTML = completed.map(order => {
                const statusInfo = getOrderStatusInfo(order);
                
                return `
                <tr>
                    <td><span class="d-lg-none d-sm-block">Order ID</span>
                        <div class="badge bg-gray-100 text-dark">#${order.order_id || order.id}</div>
                    </td>
                    <td><span class="d-lg-none d-sm-block">Car Name</span><span class="bold">${order.car_name}</span></td>
                    <td><span class="d-lg-none d-sm-block">Pick Up Location</span>${order.pickup_location}</td>
                    <td><span class="d-lg-none d-sm-block">Drop Off Location</span>${order.dropoff_location}</td>
                    <td><span class="d-lg-none d-sm-block">Pick Up Date</span>${formatDateTime(order.pick_up_time)}</td>
                    <td><span class="d-lg-none d-sm-block">Return Date</span>${formatDateTime(order.return_time)}</td>
                    <td>
                        <div class="badge rounded-pill bg-success">Completed</div>
                    </td>
                    <td>
                        <div class="badge rounded-pill ${statusInfo.paymentBadgeClass}">${statusInfo.paymentText}</div>
                        ${order.amount ? `<br><small class="text-muted">NT$ ${order.amount.toLocaleString()}</small>` : ''}
                        ${order.paid_at ? `<br><small class="text-muted">${formatDateTime(order.paid_at)}</small>` : ''}
                    </td>
                </tr>
                `;
            }).join('');
        }
        
        // 渲染取消訂單
        const cancelledBody = document.querySelector('#cancelled-orders-body');
        if (cancelledBody) {
            cancelledBody.innerHTML = cancelled.map(order => {
                const statusInfo = getOrderStatusInfo(order);
                
                // 對於取消的訂單，根據付款狀態顯示適當的文字
                let finalPaymentText = statusInfo.paymentText;
                if (order.payment_status === 'paid') {
                    finalPaymentText = 'Paid (Refund Required)';
                } else if (order.payment_status === 'refunded') {
                    finalPaymentText = 'Refunded';
                }
                
                return `
                <tr>
                    <td><span class="d-lg-none d-sm-block">Order ID</span>
                        <div class="badge bg-gray-100 text-dark">#${order.order_id || order.id}</div>
                    </td>
                    <td><span class="d-lg-none d-sm-block">Car Name</span><span class="bold">${order.car_name}</span></td>
                    <td><span class="d-lg-none d-sm-block">Pick Up Location</span>${order.pickup_location}</td>
                    <td><span class="d-lg-none d-sm-block">Drop Off Location</span>${order.dropoff_location}</td>
                    <td><span class="d-lg-none d-sm-block">Pick Up Date</span>${formatDateTime(order.pick_up_time)}</td>
                    <td><span class="d-lg-none d-sm-block">Return Date</span>${formatDateTime(order.return_time)}</td>
                    <td>
                        <div class="badge rounded-pill bg-danger">Cancelled</div>
                    </td>
                    <td>
                        <div class="badge rounded-pill ${statusInfo.paymentBadgeClass}">${finalPaymentText}</div>
                        ${order.amount ? `<br><small class="text-muted">NT$ ${order.amount.toLocaleString()}</small>` : ''}
                    </td>
                </tr>
                `;
            }).join('');
        }
        
        // 重新綁定取消按鈕和補付款按鈕
        initCancelButtons();
        initRetryPaymentButtons();
    }
    
    /**
     * 渲染管理員訂單頁面
     */
    function renderAdminOrders(bookings, isAdmin) {
        // 分類訂單
        const scheduled = bookings.filter(b => b.status === 'scheduled');
        const completed = bookings.filter(b => b.status === 'completed');
        const cancelled = bookings.filter(b => b.status === 'cancelled');
        
        // 渲染預定訂單
        const scheduledBody = document.querySelector('#admin-scheduled-body');
        if (scheduledBody) {
            scheduledBody.innerHTML = scheduled.map(booking => `
                <tr>
                    <td>${booking.id}</td>
                    <td>${booking.user_name} (id:${booking.user_id})</td>
                    <td>${booking.car_name} (id:${booking.car_id})</td>
                    <td>${booking.pickup_location}</td>
                    <td>${booking.dropoff_location}</td>
                    <td>${formatDateTime(booking.pick_up_time)}</td>
                    <td>${formatDateTime(booking.return_time)}</td>
                    <td>${booking.status}</td>
                    <td>
                        <button type="button" class="btn btn-danger btn-cancel-order"
                            data-order-id="${booking.id}">
                            取消
                        </button>
                    </td>
                </tr>
            `).join('');
        }
        
        // 渲染完成訂單
        const completedBody = document.querySelector('#admin-completed-body');
        if (completedBody) {
            completedBody.innerHTML = completed.map(booking => `
                <tr>
                    <td>${booking.id}</td>
                    <td>${booking.user_name} (id:${booking.user_id})</td>
                    <td>${booking.car_name} (id:${booking.car_id})</td>
                    <td>${booking.pickup_location}</td>
                    <td>${booking.dropoff_location}</td>
                    <td>${formatDateTime(booking.pick_up_time)}</td>
                    <td>${formatDateTime(booking.return_time)}</td>
                    <td>${booking.status}</td>
                </tr>
            `).join('');
        }
        
        // 渲染取消訂單
        const cancelledBody = document.querySelector('#admin-cancelled-body');
        if (cancelledBody) {
            cancelledBody.innerHTML = cancelled.map(booking => `
                <tr>
                    <td>${booking.id}</td>
                    <td>${booking.user_name} (id:${booking.user_id})</td>
                    <td>${booking.car_name} (id:${booking.car_id})</td>
                    <td>${booking.pickup_location}</td>
                    <td>${booking.dropoff_location}</td>
                    <td>${formatDateTime(booking.pick_up_time)}</td>
                    <td>${formatDateTime(booking.return_time)}</td>
                    <td>${booking.status}</td>
                </tr>
            `).join('');
        }
        
        // 重新綁定取消按鈕
        initCancelButtons();
    }
    
    /**
     * 格式化日期時間
     */
    function formatDateTime(isoString) {
        if (!isoString) return '';
        const date = new Date(isoString);
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        return `${year}-${month}-${day} ${hours}:${minutes}`;
    }
    
    /**
     * 初始化取消按鈕
     */
    function initCancelButtons() {
        // 綁定所有取消按鈕
        document.querySelectorAll('.btn-cancel-order').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.preventDefault();
                const orderId = btn.getAttribute('data-order-id');
                if (!orderId) return;
                if (!confirm('確定要取消此訂單嗎？')) return;

                // 使用 BookingAPI 模組取消訂單
                BookingAPI.cancel(orderId)
                    .then(data => {
                        if (data.success === true) {
                            showSuccessMessage(data.message || '訂單已取消');
                            setTimeout(() => window.location.reload(), 1500);
                        } else {
                            showAlert(data.message || '取消失敗', 'danger');
                        }
                    })
                    .catch(() => showAlert('發生錯誤，請稍後再試', 'danger'));
            });
        });
    }
    
    /**
     * 初始化補付款按鈕
     */
    function initRetryPaymentButtons() {
        document.querySelectorAll('.retry-payment').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.preventDefault();
                
                const bookingId = btn.getAttribute('data-booking-id');
                const amount = btn.getAttribute('data-amount');
                
                if (!bookingId || !amount) {
                    alert('訂單資訊不完整');
                    return;
                }
                
                // 確認是否要進行付款
                if (!confirm(`確定要為訂單 #${bookingId} 付款 NT$ ${parseFloat(amount).toLocaleString()} 嗎？`)) {
                    return;
                }
                
                // 觸發補付款流程
                retryPayment(bookingId, amount);
            });
        });
    }
    
    /**
     * 補付款處理
     */
    function retryPayment(bookingId, amount) {
        // 查找原始預訂資訊
        const bookings = window.lastLoadedBookings || [];
        const booking = bookings.find(b => b.id == bookingId);
        
        if (!booking) {
            alert('找不到訂單資訊');
            return;
        }
        
        // 檢查是否有 order_id
        if (!booking.order_id) {
            alert('訂單資料不完整，缺少 Order ID');
            console.error('Booking data missing order_id:', booking);
            return;
        }
        
        // 重新建立預訂資料結構供付款使用
        window.currentReservation = {
            bookingId: booking.id,
            orderId: booking.order_id, // 使用真正的 order ID
            carId: booking.car_id,
            carName: booking.car_name,
            amount: parseFloat(amount),
            rentalDays: 1, // 預設值
            isReserved: true
        };
        
        // 重新建立 bookingData 結構
        window.bookingData = {
            pickup_location: booking.pickup_location,
            dropoff_location: booking.dropoff_location,
            pickup_date: formatDate(booking.pick_up_time),
            pickup_time: formatTime(booking.pick_up_time),
            return_date: formatDate(booking.return_time),
            return_time: formatTime(booking.return_time),
            booking_id: booking.id,
            order_id: booking.order_id, // 使用真正的 order ID
            car_name: booking.car_name,
            amount: parseFloat(amount)
        };
        
        console.log('=== 補付款資訊 ===');
        console.log('currentReservation:', window.currentReservation);
        console.log('bookingData:', window.bookingData);
        
        // 開啟付款 Modal
        if (typeof showPaymentModalDirect === 'function') {
            showPaymentModalDirect();
        } else {
            alert('付款功能暫時無法使用，請重新整理頁面後再試');
        }
    }
    
    /**
     * 格式化日期 (ISO string 轉為 YYYY-MM-DD)
     */
    function formatDate(isoString) {
        if (!isoString) return '';
        const date = new Date(isoString);
        return date.toISOString().split('T')[0];
    }
    
    /**
     * 格式化時間 (ISO string 轉為 HH:MM)
     */
    function formatTime(isoString) {
        if (!isoString) return '00:00';
        const date = new Date(isoString);
        return date.toTimeString().slice(0, 5);
    }

})();