from django.urls import path
from . import views

urlpatterns = [
    path('<uuid:pk>/', views.download_report_pdf_view, name='api_download_report_pdf'),
]
