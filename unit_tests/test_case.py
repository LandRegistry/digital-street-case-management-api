from unittest import TestCase, mock
from case_management_api.exceptions import ConflictError
from case_management_api.main import app
from case_management_api.extensions import db
from case_management_api.models import Case, User, Address, X500Name
import json
import copy

# Test data
address = Address("1", "Digital Street", "Bristol", "Bristol", "United Kingdom", "BS2 8EN")

seller_address = Address("11", "Digital Street", "Bristol", "Bristol", "United Kingdom", "BS2 8EN")
seller = User(1, "Lisa", "Seller", "lisa.seller@example.com", "12345678901", seller_address)

seller_conveyancer_address = Address("12", "Digital Street", "Bristol", "Bristol", "United Kingdom", "BS2 8EN")
seller_conveyancer1 = User(2, "Natasha",
                           "Conveyancer",
                           "natasha.conveyancer@example.com", "10293847565",
                           seller_conveyancer_address)
seller_conveyancer2 = User(3, "Tash",
                           "Conveyancer",
                           "natasha2.conveyancer@example.com", "10293847567",
                           seller_conveyancer_address)

buyer_address = Address("13", "Digital Street", "Bristol", "Bristol", "United Kingdom", "BS2 8EN")
buyer = User(4, "David", "Buyer", "david.buyer@example.com", "10987654321", buyer_address)

buyer_conveyancer_address = Address("14", "Digital Street", "Bristol", "Bristol", "United Kingdom", "BS2 8EN")
buyer_conveyancer = User(5, "Samuel",
                         "Conveyancer",
                         "samuel.conveyancer@example.com", "10293847566",
                         buyer_conveyancer_address)

case1 = Case("sell", "ABCD123",
             seller_conveyancer1, seller,
             buyer, X500Name("Conveyancer B", "Plymouth", "GB"), buyer_conveyancer,
             address)
case2 = Case("sell", "ABCD123",
             seller_conveyancer2, seller,
             buyer, X500Name("Conveyancer B", "Plymouth", "GB"), buyer_conveyancer,
             address)
case2.title_number = "ZQV888860"
case3 = Case("sell", "DCBA321",
             seller_conveyancer1, seller,
             buyer, X500Name("Conveyancer B", "Plymouth", "GB"), buyer_conveyancer,
             address)
case3.title_number = "ZQV888860"
case3.status = "completed"

standard_dict = {
    "case_reference": "ABCD123".upper(),
    "case_type": "buy",
    "assigned_staff_id": 3,
    "client_id": 1,
    "status": "active",
    "address": {
        "house_name_number": "1",
        "street": "Digital Street",
        "town_city": "Bristol",
        "county": "Bristol",
        "country": "England",
        "postcode": "BS2 8EN"
    },
    "title_number": "ZQV888860",
    "counterparty_id": 2,
    "counterparty_conveyancer_org": {
        "organisation": "Generic Conveyancing Company",
        "locality": "Plymouth",
        "country": "GB",
        "state": "Devon"
    },
    "counterparty_conveyancer_contact_id": 4
}


# Tests the Case endpoints
class TestCases(TestCase):

    def setUp(self):
        """Sets up the tests."""
        self.app = app.test_client()

    @mock.patch.object(db.Model, 'query')
    def test_001_get_cases(self, mock_db_query):
        """Gets a list of all cases."""
        mock_db_query.all.return_value = [case1, case2]

        response = self.app.get('/v1/cases', headers={'accept': 'application/json'})

        print(response.get_data().decode())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)

    @mock.patch.object(db.Model, 'query')
    def test_002_get_cases_for_assigned_staff(self, mock_db_query):
        """Gets a list of all cases with the assigned member of staff."""
        mock_db_query.filter_by.return_value.all.return_value = [case1, case3]

        response = self.app.get('/v1/cases?assigned_staff_id=1', headers={'accept': 'application/json'})

        print(response.get_data().decode())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)

    @mock.patch.object(db.Model, 'query')
    def test_003_get_cases_for_title_number(self, mock_db_query):
        """Gets a list of all cases with the title number."""
        mock_db_query.filter_by.return_value.all.return_value = [case2, case3]

        response = self.app.get('/v1/cases?title_number=ZQV888860', headers={'accept': 'application/json'})

        print(response.get_data().decode())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)

    @mock.patch.object(db.Model, 'query')
    def test_004_get_cases_for_status(self, mock_db_query):
        """Gets a list of all cases with the status."""
        mock_db_query.filter_by.return_value.all.return_value = [case1, case2]

        response = self.app.get('/v1/cases?status=active', headers={'accept': 'application/json'})

        print(response.get_data().decode())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)

    @mock.patch.object(db.Model, 'query')
    def test_004_get_cases_for_status_and_title_number(self, mock_db_query):
        """Gets a list of all cases with the status."""
        mock_db_query.filter_by.return_value.filter_by.return_value.all.return_value = [case2]

        response = self.app.get('/v1/cases?status=active&title_number=ZQV888860',
                                headers={'accept': 'application/json'})

        print(response.get_data().decode())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)

    @mock.patch.object(db.Model, 'query')
    def test_005_get_case(self, mock_db_query):
        """Gets a specified case."""
        mock_db_query.get.return_value = case1

        response = self.app.get('/v1/cases/' + case1.case_reference, headers={'accept': 'application/json'})

        print(response.get_data().decode())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['case_reference'], 'ABCD123')

    @mock.patch.object(db.Model, 'query')
    def test_006_get_case_invalid_case_ref(self, mock_db_query):
        """The given case reference does not exist."""
        mock_db_query.get.return_value = None

        response = self.app.get('/v1/cases/N0-1D', headers={'accept': 'application/json'})

        print(response.get_data().decode())

        self.assertEqual(response.status_code, 404)
        self.assertIn('Case not found', response.json['error_message'])

    @mock.patch.object(db.session, 'commit')
    @mock.patch.object(db.session, 'add')
    @mock.patch.object(db.Model, 'query')
    def test_007_create_case(self, mock_db_query, mock_db_add, mock_db_commit):
        """Creates a case."""
        mock_db_query.get.side_effect = [
            case1.assigned_staff,
            case1.client,
            case1.counterparty,
            case1.counterparty_conveyancer_contact
        ]

        response = self.app.post('/v1/cases', data=json.dumps(standard_dict),
                                 headers={'accept': 'application/json', 'content-type': 'application/json'})

        print(response.get_data().decode())

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['status'], 'active')
        # Check we call the correct two database methods
        self.assertTrue(mock_db_add.called)
        self.assertTrue(mock_db_commit.called)

    @mock.patch.object(db.session, 'commit')
    @mock.patch.object(db.session, 'add')
    @mock.patch.object(db.Model, 'query')
    @mock.patch.object(Case, 'set_title_number')
    def test_010_create_case_title_number_already_exists(self,
                                                         mock_case_set_title_number,
                                                         mock_db_query,
                                                         mock_db_add,
                                                         mock_db_commit):
        """The given title number already exists for an active case."""
        mock_db_query.filter_by.return_value.first.side_effect = [
            case1.assigned_staff,
            case1.client,
            case1.counterparty,
            case1.counterparty_conveyancer_contact
        ]
        mock_case_set_title_number.side_effect = ConflictError('An active case with this title number already exists')

        response = self.app.post('/v1/cases', data=json.dumps(standard_dict),
                                 headers={'accept': 'application/json', 'content-type': 'application/json'})

        print(response.get_data().decode())

        self.assertEqual(response.status_code, 409)
        # Check we do not call the any database methods
        self.assertFalse(mock_db_add.called)
        self.assertFalse(mock_db_commit.called)
        self.assertIn('An active case with this title number already exists', response.json['error_message'])

    @mock.patch.object(db.session, 'commit')
    @mock.patch.object(db.session, 'add')
    @mock.patch.object(db.Model, 'query')
    @mock.patch.object(Case, 'set_status')
    def test_010_create_case_invalid_status(self, mock_case_set_status, mock_db_query, mock_db_add, mock_db_commit):
        """The given case reference does not exist."""
        mock_db_query.filter_by.return_value.first.side_effect = [
            case1.assigned_staff,
            case1.client,
            case1.counterparty,
            case1.counterparty_conveyancer_contact
        ]
        mock_case_set_status.side_effect = ValueError('Status is invalid')

        local_standard_dict = copy.deepcopy(standard_dict)
        local_standard_dict['status'] = 'invalid status here'

        response = self.app.post('/v1/cases', data=json.dumps(local_standard_dict),
                                 headers={'accept': 'application/json', 'content-type': 'application/json'})

        print(response.get_data().decode())

        self.assertEqual(response.status_code, 400)
        # Check we do not call the any database methods
        self.assertFalse(mock_db_add.called)
        self.assertFalse(mock_db_commit.called)
        self.assertTrue(
            'Status is invalid' in response.json['error_message'] or 'is not one of' in response.json['error_message']
        )

    @mock.patch.object(db.session, 'commit')
    @mock.patch.object(db.session, 'add')
    @mock.patch.object(db.Model, 'query')
    @mock.patch.object(Case, 'set_status')
    def test_010_create_case_title_number_already_exists_status(self,
                                                                mock_case_set_status,
                                                                mock_db_query,
                                                                mock_db_add,
                                                                mock_db_commit):
        """The given case reference does not exist."""
        mock_db_query.filter_by.return_value.first.side_effect = [
            case1.assigned_staff,
            case1.client,
            case1.counterparty,
            case1.counterparty_conveyancer_contact
        ]
        mock_case_set_status.side_effect = ConflictError('An active case with this title number already exists')

        response = self.app.post('/v1/cases', data=json.dumps(standard_dict),
                                 headers={'accept': 'application/json', 'content-type': 'application/json'})

        print(response.get_data().decode())

        self.assertEqual(response.status_code, 409)
        # Check we do not call the any database methods
        self.assertFalse(mock_db_add.called)
        self.assertFalse(mock_db_commit.called)
        self.assertIn('An active case with this title number already exists', response.json['error_message'])

    # @mock.patch.object(db.session, 'commit')
    # @mock.patch.object(db.session, 'add')
    # @mock.patch.object(db.Model, 'query')
    # def test_008_create_case_invalid_json(self, mock_db_query, mock_db_add, mock_db_commit):
    #     """The json data used to create the case is invalid."""
    #     local_standard_dict = copy.deepcopy(standard_dict)
    #     del local_standard_dict['title_number']

    #     response = self.app.post('/v1/cases', data=json.dumps(local_standard_dict),
    #                              headers={'accept': 'application/json', 'content-type': 'application/json'})

    #     print(response.get_data().decode())

    #     self.assertEqual(response.status_code, 400)
    #     self.assertIn('"error_message":"\'case_reference\' is a required property', response.json['error_message'])
    #     # check we haven't tried calling the postgres database
    #     self.assertFalse(mock_db_query.called)
    #     # Check we do not call the any database methods
    #     self.assertFalse(mock_db_add.called)
    #     self.assertFalse(mock_db_commit.called)

    @mock.patch.object(db.session, 'commit')
    @mock.patch.object(db.session, 'add')
    @mock.patch.object(db.Model, 'query')
    def test_009_update_case(self, mock_db_query, mock_db_add, mock_db_commit):
        """Updates the details of a case."""
        mock_db_query.get.side_effect = [
            case1,
            case1.address
        ]

        response = self.app.put('/v1/cases/' + standard_dict['case_reference'], data=json.dumps(standard_dict),
                                headers={'accept': 'application/json', 'content-type': 'application/json'})

        print(response.get_data().decode())

        self.assertEqual(response.status_code, 200)
        # Check we call the correct two database methods
        self.assertTrue(mock_db_add.called)
        self.assertTrue(mock_db_commit.called)

    @mock.patch.object(db.session, 'commit')
    @mock.patch.object(db.session, 'add')
    @mock.patch.object(db.Model, 'query')
    def test_010_update_case_invalid_case_ref(self, mock_db_query, mock_db_add, mock_db_commit):
        """The given case reference does not exist."""
        mock_db_query.get.side_effect = [
            None,
            case1.address
        ]

        response = self.app.put('/v1/cases/N0-1D', data=json.dumps(standard_dict),
                                headers={'accept': 'application/json', 'content-type': 'application/json'})

        print(response.get_data().decode())

        self.assertEqual(response.status_code, 404)
        # Check we do not call the any database methods
        self.assertFalse(mock_db_add.called)
        self.assertFalse(mock_db_commit.called)
        self.assertIn('Case not found', response.json['error_message'])

    @mock.patch.object(db.session, 'commit')
    @mock.patch.object(db.session, 'add')
    @mock.patch.object(db.Model, 'query')
    def test_011_update_case_mismatch_case_ref(self, mock_db_query, mock_db_add, mock_db_commit):
        """The case reference in the url does not match the case reference in the request body."""
        mock_db_query.get.side_effect = [
            case1,
            case1.address
        ]

        response = self.app.put('/v1/cases/WR0NG-1D', data=json.dumps(standard_dict),
                                headers={'accept': 'application/json', 'content-type': 'application/json'})

        print(response.get_data().decode())

        self.assertEqual(response.status_code, 400)
        # Check we do not call the any database methods
        self.assertFalse(mock_db_add.called)
        self.assertFalse(mock_db_commit.called)
        self.assertIn('Case Reference mismatch', response.json['error_message'])

    @mock.patch.object(db.session, 'commit')
    @mock.patch.object(db.session, 'add')
    @mock.patch.object(db.Model, 'query')
    @mock.patch.object(Case, 'set_title_number')
    def test_010_update_case_title_number_already_exists(self,
                                                         mock_case_set_title_number,
                                                         mock_db_query,
                                                         mock_db_add,
                                                         mock_db_commit):
        """The given title number already exists for an active case."""
        mock_db_query.get.side_effect = [
            case1,
            case1.address
        ]
        mock_case_set_title_number.side_effect = ConflictError('An active case with this title number already exists')

        response = self.app.put('/v1/cases/' + standard_dict['case_reference'], data=json.dumps(standard_dict),
                                headers={'accept': 'application/json', 'content-type': 'application/json'})

        print(response.get_data().decode())

        self.assertEqual(response.status_code, 409)
        # Check we do not call the any database methods
        self.assertFalse(mock_db_add.called)
        self.assertFalse(mock_db_commit.called)
        self.assertIn('An active case with this title number already exists', response.json['error_message'])

    @mock.patch.object(db.session, 'commit')
    @mock.patch.object(db.session, 'add')
    @mock.patch.object(db.Model, 'query')
    @mock.patch.object(Case, 'set_status')
    def test_010_update_case_invalid_status(self, mock_case_set_status, mock_db_query, mock_db_add, mock_db_commit):
        """The given case reference does not exist."""
        mock_db_query.get.side_effect = [
            case1,
            case1.address
        ]
        mock_case_set_status.side_effect = ValueError('Status is invalid')

        local_standard_dict = copy.deepcopy(standard_dict)
        local_standard_dict['status'] = 'invalid status here'

        response = self.app.put('/v1/cases/' + local_standard_dict['case_reference'],
                                data=json.dumps(local_standard_dict),
                                headers={'accept': 'application/json', 'content-type': 'application/json'})

        print(response.get_data().decode())

        self.assertEqual(response.status_code, 400)
        # Check we do not call the any database methods
        self.assertFalse(mock_db_add.called)
        self.assertFalse(mock_db_commit.called)
        self.assertTrue(
            'Status is invalid' in response.json['error_message'] or 'is not one of' in response.json['error_message']
        )

    @mock.patch.object(db.session, 'commit')
    @mock.patch.object(db.session, 'add')
    @mock.patch.object(db.Model, 'query')
    @mock.patch.object(Case, 'set_status')
    def test_010_update_case_title_number_already_exists_status(self,
                                                                mock_case_set_status,
                                                                mock_db_query,
                                                                mock_db_add,
                                                                mock_db_commit):
        """The given case reference does not exist."""
        mock_db_query.get.side_effect = [
            case1,
            case1.address
        ]
        mock_case_set_status.side_effect = ConflictError('An active case with this title number already exists')

        response = self.app.put('/v1/cases/' + standard_dict['case_reference'], data=json.dumps(standard_dict),
                                headers={'accept': 'application/json', 'content-type': 'application/json'})

        print(response.get_data().decode())

        self.assertEqual(response.status_code, 409)
        # Check we do not call the any database methods
        self.assertFalse(mock_db_add.called)
        self.assertFalse(mock_db_commit.called)
        self.assertIn('An active case with this title number already exists', response.json['error_message'])

    # @mock.patch.object(db.session, 'commit')
    # @mock.patch.object(db.session, 'add')
    # @mock.patch.object(db.Model, 'query')
    # def test_012_update_case_invalid_json(self, mock_db_query, mock_db_add, mock_db_commit):
    #     """The json data used to update the case is invalid."""
    #     local_standard_dict = copy.deepcopy(standard_dict)
    #     del local_standard_dict['title_number']

    #     response = self.app.put('/v1/cases/' + local_standard_dict['case_reference'],
    #                             data=json.dumps(local_standard_dict),
    #                             headers={'accept': 'application/json', 'content-type': 'application/json'})

    #     self.assertEqual(response.status_code, 400)
    #     self.assertIn('"error_message":"\'case_reference\' is a required property', response.json['error_message'])
    #     # check we haven't tried calling the postgres database
    #     self.assertFalse(mock_db_query.called)
    #     # Check we do not call the any database methods
    #     self.assertFalse(mock_db_add.called)
    #     self.assertFalse(mock_db_commit.called)
