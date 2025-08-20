from django.test import TestCase, override_settings
from unittest.mock import patch

from apps.admin_app.models import User, SearchQuery, Company
from apps.app.utils import extract_companies


@override_settings(DJANGO_SETTINGS_MODULE='apps.settings_test')
class ModelsTests(TestCase):
    @patch('apps.admin_app.models.Company.save_mail')
    def test_extract_companies_iterates_only_when_all_empty(self, save_mail_mock):
        user = User.objects.create(username='u', email='u@example.com', password='x')
        sq = SearchQuery.objects.create(location='Loc', query='Q', accuracy=1)
        sq.user.add(user)
        c1 = Company.objects.create(name='A')
        c2 = Company.objects.create(name='B')
        sq.companies.add(c1, c2)

        extract_companies(sq, 5)
        self.assertEqual(save_mail_mock.call_count, 2)

        save_mail_mock.reset_mock()
        c1.email = 'a@x.com'
        c1.save(update_fields=['email'])
        extract_companies(sq, 5)
        save_mail_mock.assert_not_called()
