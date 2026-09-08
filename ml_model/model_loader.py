from .demo_predictor import DemoPredictor


def get_predictor():
    # Stateless image preprocessor/demo adapter. Live multi-photo inference is
    # selected explicitly by execute_diagnosis_pipeline; never silently falls back.
    return DemoPredictor()
