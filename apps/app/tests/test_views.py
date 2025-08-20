from django.test import TestCase, override_settings
from django.urls import reverse
from unittest.mock import patch

from apps.admin_app.models import User, SearchQuery, Company


@override_settings(DJANGO_SETTINGS_MODULE='apps.settings_test')
class ViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='u', email='u@example.com', password='x')

    def test_index_get(self):
        resp = self.client.get(reverse('index'))
        self.assertEqual(resp.status_code, 200)

    @patch('apps.app.views.google_search')
    def test_index_post_creates_or_uses_query(self, mock_gs):
        mock_sq = SearchQuery.objects.create(location='City', query='pizza', accuracy=10)
        mock_gs.return_value = mock_sq
        session = self.client.session
        session['uid'] = self.user.id
        session.save()
        resp = self.client.post(reverse('index'), data={'city': 'City', 'query': 'pizza', 'grid_size': 5})
        self.assertEqual(resp.status_code, 200)

    @patch('apps.app.tasks.send_bulk_emails.delay')
    def test_send_email_post_queues_tasks(self, delay_mock):
        session = self.client.session
        session['uid'] = self.user.id
        session.save()
        resp = self.client.post(reverse('send_email'), data={
            'location': 'Loc', 'subject': 'S', 'text': 'T', 'delay_min': 1,
            'recipients[]': ['a@x.com', 'b@y.com']
        })
        self.assertEqual(resp.status_code, 200)
        delay_mock.assert_called_once()

    def test_get_queries_for_location_requires_login(self):
        resp = self.client.get(reverse('get_queries_for_location'), data={'location': 'X'})
        self.assertEqual(resp.status_code, 401)

    def test_get_companies_for_location_query_requires_login(self):
        resp = self.client.get(reverse('get_companies_for_location_query'), data={'location': 'X', 'query': 'Q'})
        self.assertEqual(resp.status_code, 401)

    def test_get_queries_for_location_ok(self):
        session = self.client.session
        session['uid'] = self.user.id
        session.save()
        sq1 = SearchQuery.objects.create(location='X', query='Q1')
        sq2 = SearchQuery.objects.create(location='Y', query='Q2')
        self.user.results.add(sq1, sq2)
        resp = self.client.get(reverse('get_queries_for_location'), data={'location': 'X'})
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Q1', resp.json().get('queries', []))

    def test_get_companies_for_location_query_ok(self):
        session = self.client.session
        session['uid'] = self.user.id
        session.save()
        sq = SearchQuery.objects.create(location='X', query='Q')
        self.user.results.add(sq)
        c1 = Company.objects.create(name='A', email='a@x.com')
        c2 = Company.objects.create(name='B', email='')
        sq.companies.add(c1, c2)
        resp = self.client.get(reverse('get_companies_for_location_query'), data={'location': 'X', 'query': 'Q'})
        self.assertEqual(resp.status_code, 200)
        companies = resp.json().get('companies', [])
        self.assertEqual(len(companies), 1)
