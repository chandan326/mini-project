import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib import messages
from crops.models import Crop
from diseases.models import Symptom
from .models import Diagnosis, Feedback
from .services import create_diagnosis_session, process_diagnosis_images, execute_diagnosis_pipeline
from knowledge_base.services import get_disease_knowledge

def wizard_view(request):
    """5-Step Diagnosis Wizard UI."""
    crops = Crop.objects.filter(is_active=True)
    symptoms = Symptom.objects.all()

    if request.method == 'POST':
        crop_id = request.POST.get('crop_id')
        if not crop_id:
            messages.error(request, 'Please select a crop to proceed.')
            return redirect('wizard')

        crop = get_object_or_404(Crop, id=crop_id)
        
        # Collect uploaded images (up to 5)
        image_files = []
        for i in range(1, 6):
            img = request.FILES.get(f'image_{i}')
            if img:
                image_files.append(img)

        if not image_files:
            messages.error(request, 'Please upload at least 1 clear image of the affected plant.')
            return redirect('wizard')

        # Collect farmer questionnaire answers
        affected_parts = request.POST.getlist('affected_parts')
        visible_symptoms = request.POST.getlist('visible_symptoms')

        answers_data = {
            'first_noticed': request.POST.get('first_noticed', 'Today'),
            'affected_parts': affected_parts,
            'visible_symptoms': visible_symptoms,
            'is_spreading': request.POST.get('is_spreading', 'Not sure'),
            'weather_condition': request.POST.get('weather_condition', 'Humid'),
            'treatment_applied': request.POST.get('treatment_applied', 'No'),
            'treatment_details': request.POST.get('treatment_details', ''),
        }

        # Create session & process
        diagnosis = create_diagnosis_session(crop=crop, user=request.user)
        process_diagnosis_images(diagnosis, image_files)
        execute_diagnosis_pipeline(diagnosis, answers_data)

        return redirect('diagnosis_result', pk=diagnosis.id)

    return render(request, 'diagnosis/wizard.html', {
        'crops': crops,
        'symptoms': symptoms
    })

def result_view(request, pk):
    """Detailed Assessment Result View."""
    diagnosis = get_object_or_404(Diagnosis, pk=pk)
    disease = diagnosis.predicted_disease
    knowledge = get_disease_knowledge(disease) if disease else None
    
    # Check if feedback already submitted
    has_feedback = diagnosis.feedbacks.exists()

    return render(request, 'diagnosis/result.html', {
        'diagnosis': diagnosis,
        'disease': disease,
        'knowledge': knowledge,
        'has_feedback': has_feedback
    })

def feedback_view(request, pk):
    """Handles POST feedback submission for diagnosis."""
    diagnosis = get_object_or_404(Diagnosis, pk=pk)
    if request.method == 'POST':
        is_helpful = request.POST.get('is_helpful') == 'true'
        reason = request.POST.get('reason', '')
        comments = request.POST.get('comments', '')

        Feedback.objects.create(
            diagnosis=diagnosis,
            is_helpful=is_helpful,
            reason=reason,
            comments=comments
        )
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'message': 'Thank you for your feedback!'})
        
        messages.success(request, 'Thank you for helping improve our agricultural platform!')
        return redirect('diagnosis_result', pk=diagnosis.id)

    return HttpResponseBadRequest("Invalid method")
