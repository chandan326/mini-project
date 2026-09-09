from django.test import TestCase
from crops.models import Crop
from crops.catalog import CROP_SYMBOLS, INDIA_MAJOR_CROPS
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
        self.assertEqual(self.crop.icon_symbol, '🍅')

    def test_every_major_crop_has_a_related_symbol_and_unknowns_fall_back(self):
        names = {crop['name'] for crop in INDIA_MAJOR_CROPS}
        self.assertEqual(set(CROP_SYMBOLS), names)
        self.assertEqual(Crop(name='Dragon Fruit').icon_symbol, '🌱')

    def test_seed_command_adds_exactly_thirty_major_crops_idempotently(self):
        self.assertEqual(len(INDIA_MAJOR_CROPS), 30)
        self.assertEqual(len({crop['name'] for crop in INDIA_MAJOR_CROPS}), 30)
        call_command('seed_data', verbosity=0)
        self.assertEqual(Crop.objects.filter(name__in=[crop['name'] for crop in INDIA_MAJOR_CROPS]).count(), 30)
        call_command('seed_data', verbosity=0)
        self.assertEqual(Crop.objects.filter(name__in=[crop['name'] for crop in INDIA_MAJOR_CROPS]).count(), 30)
