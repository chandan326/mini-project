from django.urls import path
from . import views

urlpatterns = [
    path('', views.CropListAPIView.as_view(), name='api_crop_list'),
    path('<slug:slug>/', views.CropDetailAPIView.as_view(), name='api_crop_detail'),
]
