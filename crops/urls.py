from django.urls import path
from . import views

urlpatterns = [
    path('', views.crop_list_view, name='crop_list'),
    path('<slug:slug>/', views.crop_detail_view, name='crop_detail'),
]
