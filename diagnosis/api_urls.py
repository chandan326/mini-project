from django.urls import path
from . import api_views

urlpatterns = [
    path('create/', api_views.DiagnosisCreateAPIView.as_view(), name='api_diagnosis_create'),
    path('<uuid:pk>/', api_views.DiagnosisDetailAPIView.as_view(), name='api_diagnosis_detail'),
    path('feedback/', api_views.FeedbackCreateAPIView.as_view(), name='api_diagnosis_feedback_create'),
]
