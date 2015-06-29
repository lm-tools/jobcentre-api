import os
import unittest
import tempfile
import json
from app import app

class APITestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        app.config.update(
          DIRECT_GOV_URL = 'http://los.direct.gov.uk'
        )

    def test_tests(self):
        assert 1 == 1

    def test_home(self):
        rv = self.app.get('/')
        assert 'Postcode' in rv.data

    def test_valid_postcode(self):
        rv = self.app.get('/api?postcode=sw98jx')
        assert rv.status_code == 200

    def test_invalid_postcode(self):
        rv = self.app.get('/api?postcode=XXXX444')
        assert rv.status_code == 400

    def test_bad_gateway(self):
        app.config.update(
          DIRECT_GOV_URL = 'http://not.direct.gov.uk'
        )
        rv = self.app.get('/api?postcode=sw98jx')
        assert rv.status_code == 502

    def test_404(self):
        rv = self.app.get('/doesnotexist')
        assert rv.status_code == 404

if __name__ == '__main__':
    unittest.main()