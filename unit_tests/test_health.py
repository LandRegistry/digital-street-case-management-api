import unittest

from case_management_api.main import app


class TestHealth(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_health(self):
        self.assertEqual((self.app.get('/health')).status_code, 200)

    def test_health_cascade(self):
        self.assertEqual((self.app.get('/health/cascade/6')).status_code, 200)

    def test_health_cascade_incorrect_value(self):
        self.assertEqual((self.app.get('/health/cascade/-1')).status_code, 500)
        self.assertEqual((self.app.get('/health/cascade/7')).status_code, 500)
