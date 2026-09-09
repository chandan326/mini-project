from pathlib import Path

from django.conf import settings
from django.test import TestCase

from crops.models import Crop


class DiscoveryTutorialTests(TestCase):
    def setUp(self):
        Crop.objects.create(name='Potato', name_hi='आलू', scientific_name='Solanum tuberosum')

    def test_home_and_crop_directory_have_accessible_search(self):
        for url in ['/', '/crops/']:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertContains(response, 'data-crop-search-root', count=1)
                self.assertContains(response, 'id="cropFilter"', count=1)
                self.assertContains(response, 'Potato आलू Solanum tuberosum')
                self.assertContains(response, 'data-crop-clear')
                self.assertContains(response, 'No crops found.')
                self.assertContains(response, 'js/crop-search.js')

    def test_tutorial_is_lazy_loaded_with_controls_and_transcript(self):
        for url in ['/', '/how-it-works/', '/crops/']:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertContains(response, 'id="tutorialDialog"', count=1)
                self.assertContains(response, 'controls playsinline preload="none"')
                self.assertContains(response, 'data-src="/static/video/agrihealth-tutorial.mp4"')
                self.assertContains(response, 'Cancel / Close')
                self.assertContains(response, 'Read the tutorial transcript')
                self.assertContains(response, 'AI guidance is not a confirmed diagnosis.')

    def test_bundled_tutorial_assets_exist(self):
        base = Path(settings.BASE_DIR) / 'static' / 'video'
        self.assertGreater((base / 'agrihealth-tutorial.mp4').stat().st_size, 100_000)
        self.assertTrue((base / 'agrihealth-tutorial-poster.jpg').is_file())
