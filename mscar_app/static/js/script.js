// Базовые утилиты
function getCSRFToken() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    return csrfToken ? csrfToken.value : getCookie('csrftoken');
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function isUserAuthenticated() {
    return document.body.classList.contains('logged-in');
}

// Уведомления
function showNotification(message, type = 'info') {
    // Удаляем существующие уведомления
    document.querySelectorAll('.notification').forEach(n => n.remove());
    
    const notification = document.createElement('div');
    notification.className = `notification alert-${type}`;
    notification.textContent = message;
    
    // Стили
    const styleMap = {
        'success': { bg: '#d1fae5', color: '#065f46', border: '#a7f3d0' },
        'error': { bg: '#fee2e2', color: '#991b1b', border: '#fecaca' },
        'warning': { bg: '#fef3c7', color: '#92400e', border: '#fde68a' },
        'info': { bg: '#dbeafe', color: '#1e40af', border: '#bfdbfe' }
    };
    
    const style = styleMap[type] || styleMap.info;
    
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        padding: 12px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        animation: slideIn 0.3s ease-out;
        background-color: ${style.bg};
        color: ${style.color};
        border: 1px solid ${style.border};
        font-weight: 500;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 300);
    }, 3000);
}

// Функции для закладок
function toggleBookmark(modId, isFromBookmarksPage = false) {
    if (!isUserAuthenticated()) {
        showNotification('Войдите в систему чтобы добавлять закладки', 'warning');
        return;
    }
    
    // Блокируем кнопку
    const buttons = document.querySelectorAll(`[onclick*="toggleBookmark(${modId})"]`);
    buttons.forEach(btn => {
        btn.disabled = true;
        btn.style.opacity = '0.7';
    });
    
    // Правильный URL - начинается с /mod/
    fetch(`/mod/${modId}/bookmark/`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCSRFToken(),
        },
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        // Разблокируем кнопки
        buttons.forEach(btn => {
            btn.disabled = false;
            btn.style.opacity = '1';
        });
        
        if (data.is_bookmarked) {
            showNotification('Мод добавлен в закладки', 'success');
            updateBookmarkButton(modId, true);
        } else {
            showNotification('Мод удален из закладок', 'info');
            updateBookmarkButton(modId, false);
            
            // Если на странице закладок
            if (window.location.pathname.includes('/bookmarks/') || isFromBookmarksPage) {
                removeBookmarkCard(modId, data.bookmarks_count);
            }
        }
        
        // Обновляем бейдж в шапке
        updateBookmarksBadge(data.bookmarks_count);
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Ошибка при обновлении закладки', 'error');
        buttons.forEach(btn => {
            btn.disabled = false;
            btn.style.opacity = '1';
        });
    });
}

function updateBookmarkButton(modId, isBookmarked) {
    const buttons = document.querySelectorAll(`button[onclick*="toggleBookmark(${modId})"]`);
    buttons.forEach(button => {
        const icon = button.querySelector('i');
        
        if (isBookmarked) {
            button.classList.add('active');
            button.title = 'Удалить из закладок';
            if (icon) icon.className = 'fas fa-bookmark';
            // Обновляем текст если есть
            const textSpan = button.querySelector('.btn-text');
            if (textSpan) textSpan.textContent = 'В закладках';
        } else {
            button.classList.remove('active');
            button.title = 'Добавить в закладки';
            if (icon) icon.className = 'far fa-bookmark';
            // Обновляем текст если есть
            const textSpan = button.querySelector('.btn-text');
            if (textSpan) textSpan.textContent = 'В закладки';
        }
    });
}

function updateBookmarksBadge(count) {
    const badge = document.getElementById('bookmarksBadge');
    if (badge) {
        badge.textContent = count;
        if (count > 0) {
            badge.style.display = 'flex';
        } else {
            badge.style.display = 'none';
        }
    }
}

// Функции для страницы закладок
function updateBookmarksCount(count) {
    const countElement = document.getElementById('bookmarksCount');
    if (countElement) {
        countElement.textContent = `Найдено: ${count}`;
    }
}

// ИСПРАВЛЕННАЯ ФУНКЦИЯ - правильное определение пустого списка закладок
function removeBookmarkCard(modId, newCount) {
    const card = document.getElementById(`modCard-${modId}`);
    if (card) {
        // Анимация удаления
        card.style.opacity = '0';
        card.style.transform = 'translateX(20px)';
        
        setTimeout(() => {
            // Удаляем карточку
            card.remove();
            
            // Обновляем счетчик
            updateBookmarksCount(newCount);
            
            // Находим контейнер с закладками
            const container = document.getElementById('bookmarksContainer');
            if (!container) return;
            
            // Проверяем, остались ли еще карточки модов
            // Ищем ВСЕ карточки в контейнере, включая те, что могут быть скрыты
            const allModCards = container.querySelectorAll('.mod-card');
            const featuredMods = container.querySelector('.featured-mods');
            
            if (allModCards.length === 0) {
                // Скрываем сетку модов если она есть
                if (featuredMods) {
                    featuredMods.style.display = 'none';
                }
                
                // Проверяем, есть ли уже сообщение
                let noBookmarksMessage = document.getElementById('noBookmarksMessage');
                
                if (!noBookmarksMessage) {
                    // Создаем новое сообщение
                    noBookmarksMessage = document.createElement('div');
                    noBookmarksMessage.id = 'noBookmarksMessage';
                    noBookmarksMessage.className = 'no-mods';
                    noBookmarksMessage.innerHTML = `
                        <i class="fas fa-bookmark fa-3x"></i>
                        <h3>У вас пока нет закладок</h3>
                        <p>Добавляйте моды в закладки, чтобы легко находить их позже!</p>
                        <a href="/" class="action-btn primary-btn">
                            <i class="fas fa-search"></i> Найти моды
                        </a>
                    `;
                    
                    // Добавляем стили
                    noBookmarksMessage.style.cssText = `
                        text-align: center;
                        padding: 3rem;
                        background: var(--white);
                        border-radius: var(--border-radius);
                        box-shadow: var(--shadow-sm);
                        display: block;
                    `;
                    
                    container.appendChild(noBookmarksMessage);
                } else {
                    // Показываем существующее сообщение
                    noBookmarksMessage.style.display = 'block';
                }
            }
        }, 300);
    }
}

// Модальное окно скачивания
function openDownloadModal(modId) {
    const modal = document.getElementById('downloadModal');
    const modalContainer = modal.querySelector('.modal-container');
    
    fetch(`/mod/${modId}/download-modal/`)
        .then(response => response.text())
        .then(html => {
            modalContainer.innerHTML = html;
            modal.style.display = 'flex';
            document.body.style.overflow = 'hidden';
        })
        .catch(error => {
            console.error('Error loading download modal:', error);
            showNotification('Ошибка при загрузке модального окна', 'error');
        });
}

function closeDownloadModal() {
    const modal = document.getElementById('downloadModal');
    modal.style.display = 'none';
    document.body.style.overflow = 'auto';
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Обработка кнопок профиля
    document.querySelectorAll('.icon-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            const icon = this.querySelector('i');
            if (icon && icon.classList.contains('fa-user-circle')) {
                window.location.href = '/profile/';
            } else if (icon && icon.classList.contains('fa-sign-in-alt')) {
                window.location.href = '/login/';
            } else if (icon && icon.classList.contains('fa-user-plus')) {
                window.location.href = '/register/';
            }
        });
    });
    
    // Обработка модального окна скачивания
    const modal = document.getElementById('downloadModal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeDownloadModal();
            }
        });
    }
    
    // Обработка скачиваний
    document.querySelectorAll('.download-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            console.log('Download initiated:', this.href);
        });
    });
    
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
    
    // Инициализация страницы закладок
    const bookmarksContainer = document.getElementById('bookmarksContainer');
    if (bookmarksContainer) {
        // Убедимся, что сообщение скрыто если есть закладки
        const cards = bookmarksContainer.querySelectorAll('.mod-card');
        const noBookmarksMessage = bookmarksContainer.querySelector('#noBookmarksMessage');
        
        if (cards.length > 0 && noBookmarksMessage) {
            noBookmarksMessage.style.display = 'none';
        } else if (cards.length === 0 && noBookmarksMessage) {
            noBookmarksMessage.style.display = 'block';
        }
    }
});

// Добавляем CSS анимации
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    .notification { animation: slideIn 0.3s ease-out; }
`;
document.head.appendChild(style);