"""Apply the same ownership rules to HTML, API, feedback and PDF endpoints."""
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import Diagnosis


def accessible_diagnoses(request):
    guest_ids = request.session.get('diagnosis_ids', [])
    allowed = Q(user__isnull=True, id__in=guest_ids)
    if request.user.is_authenticated:
        allowed |= Q(user=request.user)
    return (Diagnosis.objects.filter(allowed).select_related('crop', 'predicted_disease', 'answers')
            .prefetch_related('images', 'predicted_disease__symptoms'))


def get_accessible_diagnosis(request, pk):
    return get_object_or_404(accessible_diagnoses(request), pk=pk)


def remember_diagnosis(request, diagnosis):
    if not diagnosis.user_id:
        ids = request.session.get('diagnosis_ids', [])
        request.session['diagnosis_ids'] = (ids + [str(diagnosis.id)])[-40:]
