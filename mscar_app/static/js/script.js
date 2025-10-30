document.addEventListener('DOMContentLoaded', function() {
    
    // Обработка кнопки профиля
    const profileBtn = document.querySelector('.icon-btn .fa-user-circle')?.closest('.icon-btn');
    if (profileBtn) {
        profileBtn.addEventListener('click', function() {
            window.location.href = '/profile/';
        });
    }
    
    // Обработка кнопки входа
    const loginBtn = document.querySelector('.icon-btn .fa-sign-in-alt')?.closest('.icon-btn');
    if (loginBtn) {
        loginBtn.addEventListener('click', function() {
            window.location.href = '/login/';
        });
    }
    
    // Обработка кнопки регистрации
    const registerBtn = document.querySelector('.icon-btn .fa-user-plus')?.closest('.icon-btn');
    if (registerBtn) {
        registerBtn.addEventListener('click', function() {
            window.location.href = '/register/';
        });
    }
});

function openDownloadModal(modId) {
    const modal = document.getElementById('downloadModal');
    const modalContainer = modal.querySelector('.modal-container');
    
    // Загружаем содержимое модального окна
    fetch(`/mod/${modId}/download-modal/`)
        .then(response => response.text())
        .then(html => {
            modalContainer.innerHTML = html;
            modal.style.display = 'flex';
            document.body.style.overflow = 'hidden'; // Блокируем скролл
        })
        .catch(error => {
            console.error('Error loading download modal:', error);
        });
}

function closeDownloadModal() {
    const modal = document.getElementById('downloadModal');
    modal.style.display = 'none';
    document.body.style.overflow = 'auto'; // Разблокируем скролл
}

// Закрытие модального окна при клике вне его
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('downloadModal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeDownloadModal();
            }
        });
    }
    
    // Обработка успешных скачиваний
    document.querySelectorAll('.download-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            // Можно добавить аналитику или дополнительную логику
            console.log('Download initiated:', this.href);
        });
    });
});

document.addEventListener('DOMContentLoaded', function() {
    // Анимация карточ
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