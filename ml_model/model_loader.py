from django.conf import settings
from .demo_predictor import DemoPredictor

_predictor_instance = None

def get_predictor():
    """Returns singleton instance of the configured plant disease predictor."""
    global _predictor_instance
    if _predictor_instance is None:
        if getattr(settings, 'DEMO_MODE', True):
            _predictor_instance = DemoPredictor()
        else:
            # Fallback to DemoPredictor if custom model weights are not loaded yet
            _predictor_instance = DemoPredictor()
    return _predictor_instance
