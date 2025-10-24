from django.urls import path
from . import views

app_name = 'mscar_app'

urlpatterns = [
    path('', views.mod_list, name='mod_list'),
    path('mod/<int:mod_id>/', views.mod_detail, name='mod_detail'),
]