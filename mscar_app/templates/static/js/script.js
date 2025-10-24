document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.mod-card').forEach(card => {
        card.addEventListener('mouseover', () => {
            card.style.transform = 'translateY(-7px)';
        });
        
        card.addEventListener('mouseout', () => {
            card.style.transform = 'translateY(0)';
        });
    });

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

    const filterSelects = document.querySelectorAll('.filter-select');
    filterSelects.forEach(select => {
        select.addEventListener('change', function() {
            this.closest('form').submit();
        });
    });

    const searchForm = document.querySelector('.search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const searchInput = this.querySelector('.search-input');
            if (!searchInput.value.trim()) {
                searchInput.value = '';
            }
        });
    }
});