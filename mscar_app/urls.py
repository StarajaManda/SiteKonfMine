from django.urls import path
from . import views

app_name = 'mscar_app'

urlpatterns = [
    path('', views.mod_list, name='mod_list'),
    path('mod/<int:mod_id>/', views.mod_detail, name='mod_detail'),
    path('mod/<int:mod_id>/download/', views.download_mod, name='download_mod'),
    path('mod/<int:mod_id>/download/<int:version_id>/', views.download_mod, name='download_mod_version'),
    path('mod/<int:mod_id>/download-modal/', views.download_modal, name='download_modal'),
]