(function () {
    'use strict';

    // ===== 初始化 =====
    document.addEventListener('DOMContentLoaded',
        function () {
            initBookingForm();
        });

    /**
     * 初始化預訂表單
     */
    function initBookingForm() {
        const form =
            document.getElementById('contact_form');
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

        // 呼叫 API
        fetch(`/api/bookings/available-cars?${params}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                  }
                return response.json();
            })
            .then(data => {
                hideLoading();
                handleApiResponse(data);
            })
            .catch(error => {
                hideLoading();
                console.error('Error:', error);
                showAlert('發生錯誤，請稍後再試',
                    'danger');
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
  btn-primary w-100" onclick="selectCar(${car.id})">
                                  選擇此車
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
        
        // 除錯：印出儲存的資料
        console.log('儲存的 bookingData:', window.bookingData);
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
     * 選擇車輛並建立訂單
     * 注意：這個函數需要全域存取，所以掛載到 window 
物件
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

          // 發送訂單請求
          fetch('/api/bookings', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
              },
              body: JSON.stringify(orderData)
          })
          .then(response => {
              if (response.status === 401) {
                  // 未登入，導向登入頁
                  alert('請先登入後再進行預訂');
                  window.location.href =
  '/login?next=/booking';
                  return null;
              }
              return response.json();
          })
          .then(data => {
              hideProcessing();

              if (data && data.status === 'success') {
                  // 顯示成功訊息
                  showSuccessMessage(data.message ||
  '訂單建立成功！');

                  // 2秒後導向訂單頁面
                  setTimeout(() => {
                      window.location.href =
  '/account/orders';
                  }, 2000);
              } else if (data) {
                  showAlert(data.message ||
  '訂單建立失敗', 'danger');
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

  })();