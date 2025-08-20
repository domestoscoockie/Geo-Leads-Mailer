from django.test import TestCase, override_settings
from apps.app.forms import SearchForm, SendEmailForm, RegisterForm


@override_settings(DJANGO_SETTINGS_MODULE='apps.settings_test')
class FormsTests(TestCase):
    def test_search_form_valid(self):
        form = SearchForm(data={'city': 'X', 'query': 'Y', 'grid_size': 5})
        self.assertTrue(form.is_valid())

    def test_send_email_form_default_delay(self):
        form = SendEmailForm(data={'location': 'L', 'subject': 'S', 'text': 'T'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['delay_min'], 1)

    def test_register_form_valid(self):
        form = RegisterForm(data={
            'username': 'u', 'email': 'u@example.com', 'password': 'secret12', 'language': 'pl', 'country': 'PL'
        })
        self.assertTrue(form.is_valid())
