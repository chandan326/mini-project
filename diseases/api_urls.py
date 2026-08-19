from django.urls import path
from . import views

urlpatterns = [
    path('', views.DiseaseListAPIView.as_view(), name='api_disease_list'),
    path('<int:pk>/', views.DiseaseDetailAPIView.as_view(), name='api_disease_detail'),
]
