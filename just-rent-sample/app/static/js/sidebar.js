document.addEventListener('DOMContentLoaded', () => {
    const sidebarItems = document.querySelectorAll('.sidebar-item');

    sidebarItems.forEach(item => {
        item.addEventListener('click', () => {
            // 移除所有項目的 active 類別
            sidebarItems.forEach(i => i.classList.remove('active'));
            // 為當前點擊的項目添加 active 類別
            item.classList.add('active');
        });
    });
});