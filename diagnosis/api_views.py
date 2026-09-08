import logging
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from rest_framework import generics, status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from .access import accessible_diagnoses, get_accessible_diagnosis
from .models import Feedback
from .serializers import DiagnosisSerializer, FeedbackSerializer, FeedbackInputSerializer
from .submission import submit_diagnosis

logger = logging.getLogger(__name__)


@method_decorator(csrf_protect, name='dispatch')
class DiagnosisCreateAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    throttle_scope = 'diagnosis'

    def post(self, request):
        try:
            diagnosis = submit_diagnosis(request, request.data, request.FILES)
        except (ValidationError, APIException):
            raise
        except Exception:
            logger.exception('Assessment submission failed')
            return Response({'error': 'We could not complete the assessment. Your photos are still selected; please retry.'}, status=503)
        return Response(DiagnosisSerializer(diagnosis, context={'request': request}).data, status=status.HTTP_201_CREATED)


class DiagnosisDetailAPIView(generics.RetrieveAPIView):
    serializer_class = DiagnosisSerializer

    def get_queryset(self):
        return accessible_diagnoses(self.request)


@method_decorator(csrf_protect, name='dispatch')
class FeedbackCreateAPIView(APIView):
    throttle_scope = 'feedback'

    def post(self, request):
        from rest_framework import serializers
        identifier = serializers.UUIDField().run_validation(request.data.get('diagnosis'))
        diagnosis = get_accessible_diagnosis(request, identifier)
        serializer = FeedbackInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        feedback, created = Feedback.objects.update_or_create(diagnosis=diagnosis, defaults=serializer.validated_data)
        return Response(FeedbackSerializer(feedback).data, status=201 if created else 200)
