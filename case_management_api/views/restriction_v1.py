from flask import Blueprint, Response, current_app, request
from case_management_api.exceptions import ApplicationError
from case_management_api.models import Restriction
from flask_negotiate import produces
from jsonschema import validate, ValidationError, FormatChecker, RefResolver
import json

# This is the blueprint object that gets registered into the app in blueprints.py.
restriction_v1 = Blueprint('restriction_v1', __name__)


@restriction_v1.route("/restrictions", methods=["GET"])
@produces("application/json")
def get_restrictions():
    """Get a list of all Restrictions."""
    current_app.logger.info('Starting get_restrictions method')

    results = []

    # Get filters
    restriction_type = request.args.get('type')

    # Query DB
    query = Restriction.query
    if restriction_type:
        query = query.filter_by(restriction_type=restriction_type)
    query_result = query.all()

    # Format/Process
    for item in query_result:
        results.append(item.as_dict())

    # Output
    return Response(response=json.dumps(results, sort_keys=True, separators=(',', ':')),
                    mimetype='application/json',
                    status=200)


@restriction_v1.route("/restrictions/<restriction_id>", methods=["GET"])
@produces("application/json")
def get_restriction(restriction_id):
    """Get a specific Case."""
    current_app.logger.info('Starting get_restriction method')

    # Query DB
    query_result = Restriction.query.get(restriction_id)

    # Throw if not found
    if not query_result:
        raise ApplicationError("Restriction not found", "E404", 404)

    result = query_result.as_dict()

    # Output
    return Response(response=json.dumps(result, sort_keys=True, separators=(',', ':')),
                    mimetype='application/json',
                    status=200)
