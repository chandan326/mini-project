from django.urls import path
from . import views

urlpatterns = [
    path('download/<uuid:pk>/', views.download_report_pdf_view, name='download_report_pdf'),
]
