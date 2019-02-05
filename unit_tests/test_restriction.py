from unittest import TestCase, mock
from case_management_api.main import app
from case_management_api.extensions import db
from case_management_api.models import Restriction

# Test data
restriction1 = Restriction('BX102', 'CBCR', 'RESTRICTION: No disposition of the registered estate by the proprietor \
                            of the registered estate is to be registered without a written consent signed by the \
                            proprietor for the time being of the Charge dated *CD* in favour of *CP* \
                            referred to in the Charges Register.')
restriction2 = Restriction('BCL03', 'OJPR', 'RESTRICTION: No disposition by a sole proprietor of the registered \
                            estate (except a trust corporation) under which capital money arises is to be registered \
                            unless authorised by an order of the court.')


# Tests the Restriction endpoints
class TestRestriction(TestCase):

    def setUp(self):
        """Sets up the tests."""
        self.app = app.test_client()

    @mock.patch.object(db.Model, 'query')
    def test_001_get_restrictions(self, mock_db_query):
        """Gets a list of all restrictions."""
        mock_db_query.all.return_value = [restriction1, restriction2]

        response = self.app.get('/v1/restrictions', headers={'accept': 'application/json'})

        print(response.get_data().decode())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)

    @mock.patch.object(db.Model, 'query')
    def test_002_get_restrictions_by_type(self, mock_db_query):
        """Gets a list of restrictions with the type specified."""
        mock_db_query.filter_by.return_value.all.return_value = [restriction1]

        response = self.app.get('/v1/restrictions?type=BCL03', headers={'accept': 'application/json'})

        print(response.get_data().decode())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)

    @mock.patch.object(db.Model, 'query')
    def test_003_get_restriction(self, mock_db_query):
        """Gets a specific restriction by its id."""
        mock_db_query.get.return_value = restriction1

        response = self.app.get('/v1/restrictions/' + restriction1.restriction_type, headers={'accept': 'application/json'})

        print(response.get_data().decode())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['restriction_type'], 'CBCR')

    @mock.patch.object(db.Model, 'query')
    def test_004_get_restriction_not_found(self, mock_db_query):
        """The given restriction id does not exist."""
        mock_db_query.get.return_value = None

        response = self.app.get('/v1/restrictions/ABCDEFG', headers={'accept': 'application/json'})

        print(response.get_data().decode())

        self.assertEqual(response.status_code, 404)
        self.assertIn('Restriction not found', response.get_data().decode())
