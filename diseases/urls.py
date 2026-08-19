from django.urls import path
from . import views

urlpatterns = [
    path('', views.disease_list_view, name='disease_list'),
    path('<int:pk>/', views.disease_detail_view, name='disease_detail'),
]
