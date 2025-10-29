from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'mscar_app'

urlpatterns = [
    path('', views.mod_list, name='mod_list'),
    path('mod/<int:mod_id>/', views.mod_detail, name='mod_detail'),
    path('mod/<int:mod_id>/download/', views.download_mod, name='download_mod'),
    path('mod/<int:mod_id>/download/<int:version_id>/', views.download_mod, name='download_mod_version'),
    path('mod/<int:mod_id>/download-modal/', views.download_modal, name='download_modal'),
    
    # Аутентификация
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Профиль и моды
    path('profile/', views.profile, name='profile'),
    path('bookmarks/', views.bookmarks, name='bookmarks'),  # ✅ Теперь функция существует
    path('mod/<int:mod_id>/bookmark/', views.toggle_bookmark, name='toggle_bookmark'),  # ✅ И эта тоже
    path('mod/create/', views.create_mod, name='create_mod'),
    path('mod/<int:mod_id>/add-version/', views.add_version, name='add_version'),
]