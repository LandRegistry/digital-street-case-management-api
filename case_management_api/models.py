from case_management_api.extensions import db
import json
from datetime import datetime
from case_management_api.exceptions import ConflictError


class Case(db.Model):
    """Class representation of a Case."""
    __tablename__ = 'case'

    # Fields
    case_reference = db.Column(db.String, primary_key=True)
    case_type = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String, nullable=False)
    title_number = db.Column(db.String, nullable=True)
    assigned_staff_id = db.Column(db.String, db.ForeignKey('user.identity'), nullable=False)
    client_id = db.Column(db.String, db.ForeignKey('user.identity'), nullable=False)
    counterparty_id = db.Column(db.String, db.ForeignKey('user.identity'), nullable=False)
    counterparty_conveyancer_org = db.Column(db.String, nullable=False)
    counterparty_conveyancer_contact_id = db.Column(db.String, db.ForeignKey('user.identity'), nullable=False)
    address_id = db.Column(db.Integer,
                           db.ForeignKey('address.address_id', ondelete="CASCADE", onupdate="CASCADE"),
                           nullable=False)

    # Relationships
    assigned_staff = db.relationship("User",
                                     backref=db.backref('cases', lazy='dynamic'),
                                     foreign_keys='Case.assigned_staff_id')
    client = db.relationship("User", foreign_keys='Case.client_id')
    counterparty = db.relationship("User", foreign_keys='Case.counterparty_id')
    counterparty_conveyancer_contact = db.relationship("User", foreign_keys='Case.counterparty_conveyancer_contact_id')
    address = db.relationship("Address", backref=db.backref('cases', lazy='dynamic'), uselist=False, cascade="all")

    # Methods
    def __init__(self,
                 case_type,
                 case_reference,
                 assigned_staff, client,
                 counterparty, counterparty_conveyancer_org, counterparty_conveyancer_contact,
                 address):
        self.case_reference = case_reference.upper()
        self.case_type = case_type.lower()
        self.created_at = datetime.utcnow()
        self.status = "active"
        self.assigned_staff = assigned_staff
        self.assigned_staff_id = assigned_staff.identity
        self.client = client
        self.client_id = client.identity
        self.counterparty = counterparty
        self.counterparty_id = counterparty.identity
        self.counterparty_conveyancer_org = str(counterparty_conveyancer_org)
        self.counterparty_conveyancer_contact = counterparty_conveyancer_contact
        self.counterparty_conveyancer_contact_id = counterparty_conveyancer_contact.identity
        self.address = address

    def __repr__(self):
        return str(self)

    def __str__(self):
        return json.dumps(self.as_dict(), sort_keys=True, separators=(',', ':'))

    def as_dict(self, embed=[]):
        result = {
            "case_reference": self.case_reference,
            "case_type": self.case_type,
            "status": self.status,
            "title_number": self.title_number,
            "address": self.address.as_dict(),
            "counterparty_conveyancer_org": X500Name.from_string(self.counterparty_conveyancer_org).as_dict(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else self.updated_at
        }

        embeddable_objects = ['assigned_staff', 'client', 'counterparty', 'counterparty_conveyancer_contact']
        for object_name in embeddable_objects:
            object_name = object_name.lower()

            if object_name in embed or object_name + '_id' in embed:
                result[object_name] = getattr(self, object_name).as_dict()
            else:
                object_name += '_id'
                result[object_name] = getattr(self, object_name)

        return result

    def set_title_number(self, new_title_number):
        if new_title_number is not None:
            if len(Case.query
                       .filter_by(status='active')
                       .filter(Case.title_number.isnot(None), Case.title_number == new_title_number)
                       .all()
                   ) > 0:
                raise ConflictError('An active case with this title number already exists')

        self.title_number = new_title_number

    def set_status(self, new_status):
        statuses = ['active', 'completed', 'terminated']
        if new_status not in statuses:
            raise ValueError('Status is invalid')

        if (new_status == 'active'):
            if len(Case.query
                       .filter(Case.case_reference != self.case_reference)
                       .filter_by(status=new_status)
                       .filter(Case.title_number.isnot(None), Case.title_number == self.title_number)
                       .all()
                   ) > 0:
                raise ConflictError('An active case with this title number already exists')

        self.status = new_status


class User(db.Model):
    """Class representation of a User."""
    __tablename__ = 'user'

    # Fields
    identity = db.Column(db.String, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email_address = db.Column(db.String, nullable=False, unique=True, index=True)
    phone_number = db.Column(db.String, nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey('address.address_id'), nullable=False)

    # Relationships
    address = db.relationship("Address", backref=db.backref('users', lazy='dynamic'), uselist=False)

    # Methods
    def __init__(self, identity, first_name, last_name, email, phone, address):
        self.identity = identity
        self.first_name = first_name
        self.last_name = last_name
        self.email_address = email.lower()
        self.phone_number = phone
        self.address = address

    def __repr__(self):
        return json.dumps(self.as_dict(), sort_keys=True, separators=(',', ':'))

    def as_dict(self):
        return {
            "identity": self.identity,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email_address": self.email_address,
            "phone_number": self.phone_number,
            "address": self.address.as_dict()
        }


class Address(db.Model):
    """Class representation of a Address."""
    __tablename__ = 'address'

    # Fields
    address_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    house_name_number = db.Column(db.String, nullable=False)
    street = db.Column(db.String, nullable=False)
    town_city = db.Column(db.String, nullable=False)
    county = db.Column(db.String, nullable=True)
    country = db.Column(db.String, nullable=False)
    postcode = db.Column(db.String, nullable=False)

    # Methods
    def __init__(self, house_name_number, street, town_city, county, country, postcode):
        self.house_name_number = house_name_number
        self.street = street
        self.town_city = town_city
        self.county = county
        self.country = country
        self.postcode = postcode

    def __repr__(self):
        return json.dumps(self.as_dict(), sort_keys=True, separators=(',', ':'))

    def as_dict(self):
        return {
            "address_id": self.address_id,
            "house_name_number": self.house_name_number,
            "street": self.street,
            "town_city": self.town_city,
            "county": self.county,
            "country": self.country,
            "postcode": self.postcode
        }


class X500Name(object):
    """Class representation of an X500Name."""

    # Fields
    organisation = None
    locality = None
    country = None
    state = None
    organisational_unit = None
    common_name = None

    # Methods
    def __init__(self, organisation, locality, country):
        self.organisation = organisation
        self.locality = locality
        self.country = country

    @staticmethod
    def from_string(str_obj):
        items = {}
        for item in str_obj.split(','):
            k, v = item.split('=')
            items[k.replace(' ', '')] = v

        organisation = items.get('O')
        locality = items.get('L')
        country = items.get('C')
        state = items.get('ST')
        organisational_unit = items.get('OU')
        common_name = items.get('CN')

        x500name = X500Name(organisation, locality, country)
        x500name.state = state
        x500name.organisational_unit = organisational_unit
        x500name.common_name = common_name

        x500name.validate()
        return x500name

    @staticmethod
    def from_dict(dict_obj):
        organisation = dict_obj['organisation']
        locality = dict_obj['locality']
        country = dict_obj['country']
        state = dict_obj.get('state')
        organisational_unit = dict_obj.get('organisational_unit')
        common_name = dict_obj.get('common_name')

        x500name = X500Name(organisation, locality, country)
        x500name.state = state
        x500name.organisational_unit = organisational_unit
        x500name.common_name = common_name

        x500name.validate()
        return x500name

    # Based on: https://docs.corda.net/releases/release-V3.3/generating-a-node.html#node-naming
    def validate(self):
        # Check 3 required values exist
        if not self.organisation:
            raise TypeError("Missing: organisation")
        if not self.locality:
            raise TypeError("Missing: locality")
        if not self.country:
            raise TypeError("Missing: country")

        # Check value length
        if len(self.organisation) < 2 or len(self.organisation) > 128:
            raise ValueError("Wrong length: organisation (min: 2, max: 128)")
        if len(self.locality) < 2 or len(self.locality) > 64:
            raise ValueError("Wrong length: locality (min: 2, max: 64)")
        if len(self.country) != 2:
            raise ValueError("Wrong length: country (min: 2, max: 2)")
        if self.state and (len(self.state) < 2 or len(self.state) > 64):
            raise ValueError("Wrong length: state (min: 2, max: 64)")
        if self.organisational_unit and (len(self.organisational_unit) < 2 or len(self.organisational_unit) > 64):
            raise ValueError("Wrong length: organisational_unit (min: 2, max: 64)")
        if self.common_name and (len(self.common_name) < 2 or len(self.common_name) > 64):
            raise ValueError("Wrong length: common_name (min: 2, max: 64)")

        for name, item in self.as_dict(False).items():
            if not item:
                continue

            # Check value's first letter is upper case
            if not item[0].isupper():
                raise ValueError("First character is not uppercase: " + name)

            # Check value has no leading or trailing whitespace
            if item.strip() != item:
                raise ValueError("Has leading or trailing whitespace: " + name)

            # Check value has invalid characters
            invalid_chars = [',', '=', '$', '"', '\'', '\\']
            if any(char in item for char in invalid_chars):
                raise ValueError("Contains invalid characters: " + name)

            # Check value has invalid characters
            if '\00' in item:
                raise ValueError("Contains null character: " + name)
        return True

    def __str__(self, should_validate=True):
        if should_validate:
            self.validate()

        items = []
        items.append("O=" + self.organisation)
        items.append("L=" + self.locality)
        items.append("C=" + self.country)
        if self.state:
            items.append("ST=" + self.state)
        if self.organisational_unit:
            items.append("OU=" + self.organisational_unit)
        if self.common_name:
            items.append("CN=" + self.common_name)

        return ','.join(items)

    def __repr__(self):
        return str(self)

    def as_dict(self, should_validate=True):
        if should_validate:
            self.validate()

        return {
            "organisation": self.organisation,
            "locality": self.locality,
            "country": self.country,
            "state": self.state,
            "organisational_unit": self.organisational_unit,
            "common_name": self.common_name,
        }


class Restriction(db.Model):
    """Class representation of a Restriction."""
    __tablename__ = 'restriction'

    # Fields
    restriction_id = db.Column(db.String, primary_key=True)
    restriction_type = db.Column(db.String)
    restriction_text = db.Column(db.String)

    # Methods
    def __init__(self, restriction_id, restriction_type, restriction_text):
        self.restriction_id = restriction_id.upper()
        self.restriction_type = restriction_type.upper()
        self.restriction_text = restriction_text

    def __repr__(self):
        return str(self)

    def __str__(self):
        return json.dumps(self.as_dict(), sort_keys=True, separators=(',', ':'))

    def as_dict(self, embed=[]):
        result = {
            "restriction_id": self.restriction_id,
            "restriction_type": self.restriction_type,
            "restriction_text": self.restriction_text
        }
        return result
