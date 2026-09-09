"""Readiness information without credential values or connection strings."""
import os
from django.conf import settings
from django.db import connection
from django.http import JsonResponse
from ml_model.configuration import analysis_mode


def health_view(request):
    database_ok = False
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            database_ok = cursor.fetchone()[0] == 1
    except Exception:
        pass
    serverless = bool(os.getenv('VERCEL') or os.getenv('AWS_LAMBDA_FUNCTION_NAME'))
    persistent = connection.vendor != 'sqlite' or not serverless
    media_persistent = settings.CLOUDINARY_CONFIGURED or not serverless
    analysis = analysis_mode()
    ready = database_ok and persistent and media_persistent and analysis == 'gemini'
    response = JsonResponse({
        'status': 'ok' if database_ok else 'unavailable', 'production_ready': ready,
        'database': {'connected': database_ok, 'persistent': persistent},
        'media': {'provider': 'cloudinary' if settings.CLOUDINARY_CONFIGURED else 'local', 'persistent': media_persistent},
        'analysis': analysis,
    }, status=200 if database_ok else 503)
    response['Cache-Control'] = 'no-store'
    return response
