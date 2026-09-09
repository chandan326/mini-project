from django.test import TestCase
from crops.models import Crop
from crops.catalog import INDIA_MAJOR_CROPS
from django.core.management import call_command

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

    def test_seed_command_adds_exactly_thirty_major_crops_idempotently(self):
        self.assertEqual(len(INDIA_MAJOR_CROPS), 30)
        self.assertEqual(len({crop['name'] for crop in INDIA_MAJOR_CROPS}), 30)
        call_command('seed_data', verbosity=0)
        self.assertEqual(Crop.objects.filter(name__in=[crop['name'] for crop in INDIA_MAJOR_CROPS]).count(), 30)
        call_command('seed_data', verbosity=0)
        self.assertEqual(Crop.objects.filter(name__in=[crop['name'] for crop in INDIA_MAJOR_CROPS]).count(), 30)
