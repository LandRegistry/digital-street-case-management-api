from flask import Blueprint, Response, current_app, request
from case_management_api.exceptions import ConflictError, ApplicationError
from case_management_api.extensions import db
from sqlalchemy import exc
from case_management_api.models import Case, User, Address, X500Name
from flask_negotiate import consumes, produces
from jsonschema import validate, ValidationError, FormatChecker, RefResolver
import datetime
import json

# This is the blueprint object that gets registered into the app in blueprints.py.
case_v1 = Blueprint('case_v1', __name__)

openapi_filepath = 'openapi.json'

# JSON schema for case requests
with open(openapi_filepath) as json_file:
    openapi = json.load(json_file)

ref_resolver = RefResolver(openapi_filepath, openapi)
case_request_schema = openapi["components"]["schemas"]["Case"]


@case_v1.route("/cases", methods=["GET"])
@produces("application/json")
def get_cases():
    """Get a list of all Cases."""
    current_app.logger.info('Starting get_cases method')

    results = []

    # Get filters
    filter_assigned_staff_id = request.args.get('assigned_staff_id')
    filter_title_number = request.args.get('title_number')
    filter_status = request.args.get('status')

    # Query DB
    query = Case.query
    if filter_assigned_staff_id:
        query = query.filter_by(assigned_staff_id=filter_assigned_staff_id)
    if filter_title_number:
        query = query.filter_by(title_number=filter_title_number)
    if filter_status:
        query = query.filter_by(status=filter_status)
    query_result = query.all()

    # Format/Process
    embed_str = request.args.get('embed')
    objects_to_embed = embed_str.split(',') if embed_str else {}

    for item in query_result:
        results.append(item.as_dict(embed=objects_to_embed))

    # Output
    return Response(response=json.dumps(results, sort_keys=True, separators=(',', ':')),
                    mimetype='application/json',
                    status=200)


@case_v1.route("/cases/<case_reference>", methods=["GET"])
@produces("application/json")
def get_case(case_reference):
    """Get a specific Case."""
    current_app.logger.info('Starting get_case method')

    # Query DB
    query_result = Case.query.get(case_reference)

    # Throw if not found
    if not query_result:
        raise ApplicationError("Case not found", "E404", 404)

    # Format/Process
    embed_str = request.args.get('embed')
    objects_to_embed = embed_str.split(',') if embed_str else {}

    result = query_result.as_dict(embed=objects_to_embed)

    # Output
    return Response(response=json.dumps(result, sort_keys=True, separators=(',', ':')),
                    mimetype='application/json',
                    status=200)


@case_v1.route("/cases", methods=["POST"])
@consumes("application/json")
@produces("application/json")
def create_case():
    """Create a Case."""
    case_request = request.json
    current_app.logger.info('Starting create_case: {}'.format(case_request['case_reference']))

    # Validate input
    try:
        validate(case_request, case_request_schema, format_checker=FormatChecker(), resolver=ref_resolver)
    except ValidationError as e:
        raise ApplicationError(e.message, "E001", 400)

    # Get details for new case
    assigned_staff = User.query.get(case_request['assigned_staff_id'])
    client = User.query.get(case_request['client_id'])
    counterparty = User.query.get(case_request['counterparty_id'])
    counterparty_conveyancer_org = X500Name.from_dict(case_request['counterparty_conveyancer_org'])
    counterparty_conveyancer_contact = User.query.get(case_request['counterparty_conveyancer_contact_id'])

    # Add new address
    address = Address(
        case_request['address']['house_name_number'],
        case_request['address']['street'],
        case_request['address']['town_city'],
        case_request['address']['county'],
        case_request['address']['country'],
        case_request['address']['postcode']
    )

    # Throw if not found
    if not assigned_staff:
        raise ApplicationError("Assigned Staff not found", "404", 404)
    if not client:
        raise ApplicationError("Client not found", "404", 404)
    if not counterparty:
        raise ApplicationError("Counterpartynot found", "404", 404)
    if not counterparty_conveyancer_contact:
        raise ApplicationError("Counterparty Conveyancer Contact not found", "404", 404)

    # Add new case
    case = Case(
        case_request['case_type'],
        case_request['case_reference'],
        assigned_staff, client,
        counterparty, counterparty_conveyancer_org, counterparty_conveyancer_contact,
        address
    )

    try:
        case.set_title_number(case_request['title_number'])
    except ConflictError:
        raise ApplicationError('An active case with this title number already exists', 'E409', 409)

    try:
        case.set_status(case_request['status'])
    except ConflictError:
        raise ApplicationError('An active case with this title number already exists', 'E409', 409)
    except ValueError:
        raise ApplicationError('Status is invalid', 'E400', 400)

    # Add and Commit
    db.session.add(address)
    db.session.add(case)
    try:
        db.session.commit()
    # Check for existing case
    except exc.IntegrityError:
        raise ApplicationError("Case already exists", "E003", 409)

    return Response(response=str(case),
                    mimetype='application/json',
                    status=201)


@case_v1.route("/cases/<case_reference>", methods=["PUT"])
@consumes("application/json")
@produces("application/json")
def update_case(case_reference):
    """Updates a Case's details."""
    case_request = request.json
    current_app.logger.info('Starting update_case: {}'.format(case_request))

    # Validate input
    try:
        validate(case_request, case_request_schema, format_checker=FormatChecker(), resolver=ref_resolver)
    except ValidationError as e:
        raise ApplicationError(e.message, "E001", 400)

    # Get existing case
    case = Case.query.get(case_reference)
    if not case:
        raise ApplicationError('Case not found', 'E404', 404)

    # Validate case
    if not (case.case_reference == case_request['case_reference'] == case_reference):
        print(case.case_reference)
        print(case_request['case_reference'])
        print(case_reference)
        raise ApplicationError('Case Reference mismatch', 'E004', 400)

    # Modify case
    case.case_type = case_request['case_type']
    case.updated_at = datetime.datetime.utcnow()

    try:
        case.set_title_number(case_request['title_number'])
    except ConflictError:
        raise ApplicationError('An active case with this title number already exists', 'E409', 409)

    try:
        case.set_status(case_request['status'])
    except ConflictError:
        raise ApplicationError('An active case with this title number already exists', 'E409', 409)
    except ValueError:
        raise ApplicationError('Status is invalid', 'E400', 400)

    case.assigned_staff_id = case_request['assigned_staff_id']
    case.client_id = case_request['client_id']
    case.counterparty_id = case_request['counterparty_id']
    case.counterparty_conveyancer_org = str(X500Name.from_dict(case_request['counterparty_conveyancer_org']))
    case.counterparty_conveyancer_contact_id = case_request['counterparty_conveyancer_contact_id']

    # Get existing address
    address = Address.query.get(case.address_id)
    if not address:
        raise ApplicationError('Address not found', 'E404', 404)

    # Modify address
    address.house_name_number = case_request['address']['house_name_number']
    address.street = case_request['address']['street']
    address.town_city = case_request['address']['town_city']
    address.county = case_request['address']['county']
    address.country = case_request['address']['country']
    address.postcode = case_request['address']['postcode']

    # Update and Commit
    db.session.add(address)
    db.session.add(case)
    db.session.commit()

    return Response(response=str(case),
                    mimetype='application/json',
                    status=200)
