from django.urls import path
from . import views

urlpatterns = [
    path('', views.wizard_view, name='wizard'),
    path('result/<uuid:pk>/', views.result_view, name='diagnosis_result'),
    path('feedback/<uuid:pk>/', views.feedback_view, name='diagnosis_feedback'),
]
