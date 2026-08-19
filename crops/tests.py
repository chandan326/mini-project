from django.test import TestCase
from crops.models import Crop

class CropModelTest(TestCase):
    def setUp(self):
        self.crop = Crop.objects.create(
            name="Tomato",
            name_hi="टमाटर",
            scientific_name="Solanum lycopersicum"
        )

    def test_crop_creation(self):
        self.assertEqual(self.crop.name, "Tomato")
        self.assertEqual(self.crop.slug, "tomato")
        self.assertTrue(self.crop.is_active)
