from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch

from apps.admin_app.models import User, SearchQuery
from apps.app.utils import kilometers_to_geo_minutes, google_search, save_files


@override_settings(DJANGO_SETTINGS_MODULE='apps.settings_test')
class UtilsTests(TestCase):
    def test_kilometers_to_geo_minutes_bounds(self):
        self.assertAlmostEqual(kilometers_to_geo_minutes(0), 0.25)
        self.assertAlmostEqual(kilometers_to_geo_minutes(200), 60.0)

    def test_save_files_writes_to_disk(self):
        f1 = SimpleUploadedFile("a.txt", b"hello")
        f2 = SimpleUploadedFile("b.txt", b"world")
        paths = save_files([f1, f2])
        self.assertEqual(len(paths), 2)

    @patch('apps.app.utils.LocationQuery')
    def test_google_search_calls_locationquery(self, MQ):
        MQ.return_value.set_query.return_value = MQ.return_value
        MQ.return_value.generate_rectangles.return_value = [(0, 0, 1, 1)]
        MQ.return_value.search.return_value = {"q": {}}
        user = User.objects.create(username='u', email='u@example.com', password='x')
        sq = google_search('City', 'pizza', 5, user)
        self.assertIsInstance(sq, SearchQuery)
