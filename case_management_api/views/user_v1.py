from flask import Blueprint, Response, current_app, request
from case_management_api.exceptions import ApplicationError
from case_management_api.extensions import db
from sqlalchemy import exc
from case_management_api.models import User, Address
from flask_negotiate import consumes, produces
from jsonschema import validate, ValidationError, FormatChecker, RefResolver
import json

# This is the blueprint object that gets registered into the app in blueprints.py.
user_v1 = Blueprint('user_v1', __name__)

openapi_filepath = 'openapi.json'

# JSON schema for case requests
with open(openapi_filepath) as json_file:
    openapi = json.load(json_file)

ref_resolver = RefResolver(openapi_filepath, openapi)
user_request_schema = openapi["components"]["schemas"]["User"]


@user_v1.route("/users", methods=["GET"])
@produces("application/json")
def get_users():
    """Get a list of all Users."""
    current_app.logger.info('Starting get_users method')

    results = []

    # Get filters
    email_address = request.args.get('email_address')

    # Query DB
    if email_address:
        query_result = User.query.filter_by(email_address=email_address.lower()).all()
    else:
        query_result = User.query.all()

    # Format/Process
    for item in query_result:
        results.append(item.as_dict())

    # Output
    return Response(response=json.dumps(results, sort_keys=True, separators=(',', ':')),
                    mimetype='application/json',
                    status=200)


@user_v1.route("/users/<identity>", methods=["GET"])
@produces("application/json")
def get_user(identity):
    """Get a specific User."""
    current_app.logger.info('Starting get_user method')

    # Query DB
    query_result = User.query.get(identity)

    # Throw if not found
    if not query_result:
        raise ApplicationError("User not found", "E404", 404)

    # Format/Process
    result = query_result.as_dict()

    # Output
    return Response(response=json.dumps(result, sort_keys=True, separators=(',', ':')),
                    mimetype='application/json',
                    status=200)


@user_v1.route("/users", methods=["POST"])
@consumes("application/json")
@produces("application/json")
def create_user():
    """Create a User."""
    user_request = request.json
    current_app.logger.info('Starting create_user: {}'.format(user_request['identity']))

    # Validate input
    try:
        validate(user_request, user_request_schema, format_checker=FormatChecker(), resolver=ref_resolver)
    except ValidationError as e:
        raise ApplicationError(e.message, "E001", 400)

    # Add new address
    address = Address(
        user_request['address']['house_name_number'],
        user_request['address']['street'],
        user_request['address']['town_city'],
        user_request['address']['county'],
        user_request['address']['country'],
        user_request['address']['postcode']
    )

    # Add new user
    user = User(
        user_request['identity'],
        user_request['first_name'],
        user_request['last_name'],
        user_request['email_address'],
        user_request['phone_number'],
        address
    )

    # Add and Commit
    db.session.add(address)
    db.session.add(user)
    try:
        db.session.commit()
    # Check for existing user
    except exc.IntegrityError:
        raise ApplicationError("User already exists", "E003", 409)

    return Response(response=str(user),
                    mimetype='application/json',
                    status=201)


@user_v1.route("/users/<identity>", methods=["PUT"])
@consumes("application/json")
@produces("application/json")
def update_user(identity):
    """Updates a User's details."""
    user_request = request.json
    current_app.logger.info('Starting update_user: {}'.format(identity))

    # Validate input
    try:
        validate(user_request, user_request_schema, format_checker=FormatChecker(), resolver=ref_resolver)
    except ValidationError as e:
        raise ApplicationError(e.message, "E001", 400)

    # Validate user
    if not (int(user_request['identity']) == int(identity)):
        raise ApplicationError('User Identity mismatch', 'E004', 400)

    # Get existing user
    user = User.query.get(int(identity))
    if not user:
        raise ApplicationError('User not found', 'E404', 404)

    # Modify user
    user.identity = user_request['identity']
    user.first_name = user_request['first_name']
    user.last_name = user_request['last_name']
    user.email_address = user_request['email_address']
    user.phone_number = user_request['phone_number']

    # Get existing address
    address = Address.query.get(user.address_id)
    if not address:
        raise ApplicationError('Address not found', 'E404', 404)

    # Modify address
    address.house_name_number = user_request['address']['house_name_number']
    address.street = user_request['address']['street']
    address.town_city = user_request['address']['town_city']
    address.county = user_request['address']['county']
    address.country = user_request['address']['country']
    address.postcode = user_request['address']['postcode']

    # Update and Commit
    db.session.add(address)
    db.session.add(user)
    db.session.commit()

    return Response(response=str(user),
                    mimetype='application/json',
                    status=200)
