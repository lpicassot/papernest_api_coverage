from django.test import TestCase
from api.utils import get_coverage_data, get_provider_name
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

# Unit Tests
class TestUtils(TestCase):
    """Test get_coverage_data function, 
    to verify particular key in dictionary returned from a json file by get_coverage_data function"""
    def test_get_coverage_data(self):
        result = get_coverage_data()

        expected_key = "-4.558;48.469"

        self.assertIn(expected_key, result)


    def test_get_provider_name(self):
        """Test get_provider_name function"""
        name = '20801'
        result = get_provider_name(name)
        self.assertEqual(result, 'Orange')

        name = 'nonexistent'
        result = get_provider_name(name)
        self.assertIsNone(result)



# Functional Test whole process (internet required for 3th party API)
class AccountTests(APITestCase):
    def test_create_account(self):
        """Ensure all endpoint works ok."""
        url = reverse('get_coverage')
        query_param = 'rue%20de%20verd%2031'
        response = self.client.get(url, {'q': query_param})
        response_data = response.json()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Orange', response_data)
        self.assertIn('2G', response_data['Orange'])

