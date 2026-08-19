from django.test import TestCase
from crops.models import Crop
from diseases.models import Disease, Symptom

class DiseaseModelTest(TestCase):
    def setUp(self):
        self.crop = Crop.objects.create(name="Potato", name_hi="आलू")
        self.symptom = Symptom.objects.create(name="Brown spots", code="brown_spots")
        self.disease = Disease.objects.create(
            name="Early Blight",
            crop=self.crop,
            description="Fungal spots"
        )
        self.disease.symptoms.add(self.symptom)

    def test_disease_creation(self):
        self.assertEqual(self.disease.crop.name, "Potato")
        self.assertEqual(self.disease.symptoms.count(), 1)
