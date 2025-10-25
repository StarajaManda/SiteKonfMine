document.addEventListener('DOMContentLoaded', function() {
    // Анимация карточек
    document.querySelectorAll('.mod-card').forEach(card => {
        card.addEventListener('mouseover', () => {
            card.style.transform = 'translateY(-7px)';
        });
        
        card.addEventListener('mouseout', () => {
            card.style.transform = 'translateY(0)';
        });
    });

    // Анимация кнопок
    document.querySelectorAll('.action-btn').forEach(btn => {
        btn.addEventListener('mouseover', () => {
            if(btn.classList.contains('primary-btn')) {
                btn.style.backgroundColor = '#0d5e2c';
            } else {
                btn.style.backgroundColor = '#e5e7eb';
            }
        });
        
        btn.addEventListener('mouseout', () => {
            if(btn.classList.contains('primary-btn')) {
                btn.style.backgroundColor = '#1a9047';
            } else {
                btn.style.backgroundColor = '#f3f4f6';
            }
        });
    });

    // Авто-сабмит фильтров
    document.querySelectorAll('.filter-select').forEach(select => {
        select.addEventListener('change', function() {
            this.closest('form').submit();
        });
    });
});