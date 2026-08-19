from abc import ABC, abstractmethod
from .preprocessing import validate_and_preprocess_image

class PlantDiseasePredictor(ABC):
    """
    Abstract Base Class for Plant Disease Predictors.
    Allows easy swapping between DemoPredictor, PyTorch, TensorFlow, or ONNX models.
    """

    @abstractmethod
    def load_model(self):
        """Loads model weights or initializes model connection."""
        pass

    def preprocess(self, image_file):
        """Validates and preprocesses single image."""
        return validate_and_preprocess_image(image_file)

    @abstractmethod
    def predict_single(self, image_file, crop):
        """
        Runs model prediction on a single image.
        Returns dict: {'disease_id': int, 'disease_name': str, 'probabilities': dict}
        """
        pass

    @abstractmethod
    def aggregate_predictions(self, image_predictions, crop, answers):
        """
        Combines 5-image prediction probabilities, farmer questionnaire inputs, and symptom matches.
        Returns dict with ensemble confidence, top disease match, inconsistency flags, and explanations.
        """
        pass
