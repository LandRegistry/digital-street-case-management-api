from unittest import TestCase, mock
from case_management_api.main import app
from case_management_api.extensions import db
from case_management_api.models import User, Address
import json

# Test data
address1 = Address("1", "Digital Street", "Bristol", "Bristol", "United Kingdom", "BS2 8EN")
seller1 = User(1, "Lisa", "Seller", "lisa.seller@example.com", "12345678901", address1)

address2 = Address("2", "Digital Street", "Bristol", "Bristol", "United Kingdom", "BS2 8EN")
seller2 = User(2, "Jim", "Seller", "jim.seller@example.com", "12345678902", address2)

standard_dict = {
    "identity": 1,
    "first_name": "Lisa",
    "last_name": "White",
    "email_address": "lisa.white@example.com",
    "phone_number": "07700900354",
    "address": {
        "house_name_number": "1",
        "street": "Digital Street",
        "town_city": "Bristol",
        "county": "Bristol",
        "country": "United Kingdom",
        "postcode": "BS2 8EN"
    }
}


# Tests the User endpoints
class TestUser(TestCase):

    def setUp(self):
        """Sets up the tests."""
        self.app = app.test_client()

    @mock.patch.object(db.Model, 'query')
    def test_001_get_users(self, mock_db_query):
        """Gets a list of all users."""
        mock_db_query.all.return_value = [seller1, seller2]

        response = self.app.get('/v1/users', headers={'accept': 'application/json'})

        print(response.get_data().decode())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)

    @mock.patch.object(db.Model, 'query')
    def test_002_get_users_by_email(self, mock_db_query):
        """Gets all users with the specified email (should only be one in the list)."""
        mock_db_query.filter_by.return_value.all.return_value = [seller1]

        response = self.app.get('/v1/users?email_address=' + seller1.email_address.upper(),
                                headers={'accept': 'application/json'})

        print(response.get_data().decode())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)

    @mock.patch.object(db.Model, 'query')
    def test_003_get_user(self, mock_db_query):
        """Gets a specified user."""
        mock_db_query.get.return_value = seller1

        response = self.app.get('/v1/users/' + str(seller1.identity), headers={'accept': 'application/json'})

        print(response.get_data().decode())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['first_name'], 'Lisa')

    @mock.patch.object(db.Model, 'query')
    def test_004_get_user_not_found(self, mock_db_query):
        """The given user id does not exist."""
        mock_db_query.get.return_value = None

        response = self.app.get('/v1/users/0', headers={'accept': 'application/json'})

        print(response.get_data().decode())

        self.assertEqual(response.status_code, 404)
        self.assertIn('User not found', response.get_data().decode())

    @mock.patch.object(db.session, 'commit')
    @mock.patch.object(db.session, 'add')
    def test_005_create_user(self, mock_db_add, mock_db_commit):
        """Creates a new user."""
        response = self.app.post('/v1/users', data=json.dumps(standard_dict),
                                 headers={'accept': 'application/json', 'content-type': 'application/json'})

        print(response.get_data().decode())

        self.assertEqual(response.status_code, 201)
        # Check we call the correct two database methods
        self.assertTrue(mock_db_add.called)
        self.assertTrue(mock_db_commit.called)

    # @mock.patch.object(db.session, 'commit')
    # @mock.patch.object(db.session, 'add')
    # def test_006_create_user_invalid_json(self, mock_db_add, mock_db_commit):
    #     """The json data used to create the user is invalid."""

    @mock.patch.object(db.session, 'commit')
    @mock.patch.object(db.session, 'add')
    @mock.patch.object(db.Model, 'query')
    def test_007_update_user(self, mock_db_query, mock_db_add, mock_db_commit):
        """Updates the details of a user."""
        mock_db_query.get.side_effect = [
            seller1,
            seller1.address
        ]

        standard_dict_update = standard_dict
        standard_dict_update['identity'] = 1
        standard_dict_update['first_name'] = "Sally"
        response = self.app.put('/v1/users/' + str(seller1.identity), data=json.dumps(standard_dict_update),
                                headers={'accept': 'application/json', 'content-type': 'application/json'})

        print(response.get_data().decode())

        self.assertEqual(response.status_code, 200)
        # Check we call the correct two database methods
        self.assertTrue(mock_db_add.called)
        self.assertTrue(mock_db_commit.called)

    @mock.patch.object(db.session, 'commit')
    @mock.patch.object(db.session, 'add')
    @mock.patch.object(db.Model, 'query')
    def test_008_update_user_invalid_user_identity(self, mock_db_query, mock_db_add, mock_db_commit):
        """The given user id does not exist."""
        mock_db_query.get.side_effect = [
            None,
            seller1.address
        ]

        standard_dict_update = standard_dict
        standard_dict_update['identity'] = 0
        standard_dict_update['first_name'] = "Sally"
        response = self.app.put('/v1/users/0', data=json.dumps(standard_dict_update),
                                headers={'accept': 'application/json', 'content-type': 'application/json'})

        print(response.get_data().decode())

        self.assertEqual(response.status_code, 404)
        # Check we do not call the any database methods
        self.assertFalse(mock_db_add.called)
        self.assertFalse(mock_db_commit.called)
        self.assertIn('User not found', response.get_data().decode())

    @mock.patch.object(db.session, 'commit')
    @mock.patch.object(db.session, 'add')
    @mock.patch.object(db.Model, 'query')
    def test_009_update_user_mismatch_user_identity(self, mock_db_query, mock_db_add, mock_db_commit):
        """The user id in the url does not match the user id in the request body."""
        mock_db_query.get.side_effect = [
            seller1,
            seller1.address
        ]

        response = self.app.put('/v1/users/82375', data=json.dumps(standard_dict),
                                headers={'accept': 'application/json', 'content-type': 'application/json'})

        print(response.get_data().decode())

        self.assertEqual(response.status_code, 400)
        # Check we do not call the any database methods
        self.assertFalse(mock_db_add.called)
        self.assertFalse(mock_db_commit.called)
        self.assertIn('User Identity mismatch', response.get_data().decode())

    # @mock.patch.object(db.session, 'commit')
    # @mock.patch.object(db.session, 'add')
    # @mock.patch.object(db.Model, 'query')
    # def test_009_update_user_invalid_json(self, mock_db_query, mock_db_add, mock_db_commit):
    #     """The json data used to update the user is invalid."""
