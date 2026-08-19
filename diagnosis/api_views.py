from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from crops.models import Crop
from .models import Diagnosis, Feedback
from .serializers import DiagnosisSerializer, FeedbackSerializer
from .services import create_diagnosis_session, process_diagnosis_images, execute_diagnosis_pipeline

class DiagnosisCreateAPIView(APIView):
    def post(self, request):
        crop_id = request.data.get('crop_id')
        if not crop_id:
            return Response({'error': 'crop_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        crop = get_object_or_404(Crop, id=crop_id)
        diagnosis = create_diagnosis_session(crop=crop, user=request.user)

        # Collect images
        image_files = []
        for key in request.FILES:
            if key.startswith('image'):
                image_files.append(request.FILES[key])

        if image_files:
            process_diagnosis_images(diagnosis, image_files)

        answers_data = {
            'first_noticed': request.data.get('first_noticed', 'Today'),
            'affected_parts': request.data.getlist('affected_parts') if hasattr(request.data, 'getlist') else request.data.get('affected_parts', []),
            'visible_symptoms': request.data.getlist('visible_symptoms') if hasattr(request.data, 'getlist') else request.data.get('visible_symptoms', []),
            'is_spreading': request.data.get('is_spreading', 'Not sure'),
            'weather_condition': request.data.get('weather_condition', 'Humid'),
            'treatment_applied': request.data.get('treatment_applied', 'No'),
            'treatment_details': request.data.get('treatment_details', ''),
        }

        execute_diagnosis_pipeline(diagnosis, answers_data)

        serializer = DiagnosisSerializer(diagnosis)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class DiagnosisDetailAPIView(generics.RetrieveAPIView):
    queryset = Diagnosis.objects.all()
    serializer_class = DiagnosisSerializer

class FeedbackCreateAPIView(generics.CreateAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
