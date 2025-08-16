function validateBookingTime() {
    const pickupDate = document.getElementById('date-picker').value;
    const pickupTime = document.getElementById('pickup-time').value;
    const returnDate = document.getElementById('date-picker-2').value;
    const returnTime = document.getElementById('collection-time').value;

    if (!pickupDate || !pickupTime || !returnDate || !returnTime) return;

    const pickup = new Date(pickupDate + ' ' + pickupTime);
    const returnDt = new Date(returnDate + ' ' + returnTime);
    const now = new Date();

    if (pickup < now) {
        alert('取車時間不可早於現在時間，請重新選取。');
        document.getElementById('date-picker').value = '';
        return;
    }
    if (returnDt < pickup) {
        alert('還車時間不可早於取車時間，請重新選取。');
        document.getElementById('date-picker-2').value = '';
        return;
    }
}

// 綁定事件
document.getElementById('date-picker').addEventListener('change', validateBookingTime);
document.getElementById('pickup-time').addEventListener('change', validateBookingTime);
document.getElementById('date-picker-2').addEventListener('change', validateBookingTime);
document.getElementById('collection-time').addEventListener('change', validateBookingTime);