from django.urls import path
from . import views

urlpatterns = [
    path('<uuid:pk>/images/<int:image_id>/', views.image_view, name='diagnosis_image'),
    path('', views.wizard_view, name='wizard'),
    path('result/<uuid:pk>/', views.result_view, name='diagnosis_result'),
    path('feedback/<uuid:pk>/', views.feedback_view, name='diagnosis_feedback'),
]
