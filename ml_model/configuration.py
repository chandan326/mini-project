"""Shared readiness rules for the form, API and health endpoint."""
import re
from django.conf import settings


def live_configuration_error():
    if not settings.ENABLE_AI_GENERATION:
        return 'Live image analysis is currently disabled.'
    if settings.AI_PROVIDER != 'gemini':
        return 'The configured image-analysis provider is not supported.'
    if not settings.GEMINI_API_KEY:
        return 'Live image analysis has not been configured yet.'
    if not re.fullmatch(r'gemini-[A-Za-z0-9._-]+', settings.GEMINI_MODEL):
        return 'The image-analysis model configuration is invalid.'
    return None


def analysis_mode():
    if settings.DEMO_MODE:
        return 'demo'
    return 'unavailable' if live_configuration_error() else 'gemini'
