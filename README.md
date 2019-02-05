# HM Land Registry Digital Street Proof of Concept - Case Management API

## Available routes

|Route|What it does|
|---|---|
|**GET** /health|Returns some basic information about the app (JSON)|
|**GET** /health/cascade/\<depth\>|Returns the app's health information as above but also the health information of any database and HTTP dependencies, down to the specified depth (JSON)|
|**GET** /cases|Returns a list of cases in the conveyancer's management system (JSON)|
|**POST** /cases|Creates a new case in the conveyancer's management system (JSON)|
|**GET** /cases/\<case_reference\>|Returns a case with the specified id. (JSON)|
|**PUT** /cases/\<case_reference\>|Modifies a case with the specified id. (JSON)|
|**GET** /users|Returns a list of users in the conveyancer's management system (JSON)|
|**POST** /users|Creates a new user in the conveyancer's management system (JSON)|
|**GET** /users/\<identity\>|Returns a user with the specified id. (JSON)|
|**PUT** /users/\<identity\>|Modifies a user with the specified id. (JSON)|
|**GET** /restrictions|Returns a list of restrictions in the conveyancer's management system (JSON)|
|**GET** /restrictions/\<restrictions_id\>|Returns a restrictions with the specified id. (JSON)|

## Quick start

### Docker

This app supports the Land Registry [common development environment](https://github.com/LandRegistry/common-dev-env) so adding the following to your dev-env config file is enough:

```YAML
  case-management-api:
    repo: git@github.com:LandRegistry/digital-street-case-management-api.git
    branch: master
```

The Docker image it creates (and runs) will install all necessary requirements and set all environment variables for you.

### Standalone

#### Environment variables to set

* PYTHONUNBUFFERED *(suggested value: yes)*
* PORT
* LOG_LEVEL
* COMMIT
* APP_NAME
* MAX_HEALTH_CASCADE
* DEFAULT_TIMEOUT *(suggested value: 30)*

  *(The default timeout is applied to all calls which go via g.requests but can be overriden on a case by case basis with the standard timeout argument)*

##### When not using gunicorn

* FLASK_APP *(suggested value: user_api/main.py)*
* FLASK_DEBUG *(suggested value: 1)*

#### Running (when not using gunicorn)

(The third party libraries are defined in requirements.txt and can be installed using pip)

```shell
python3 -m flask run
or
flask run
or
make run
```

## Testing

### Unit tests

The unit tests are contained in the unit_tests folder. [Pytest](http://docs.pytest.org/en/latest/) is used for unit testing. To run the tests use the following command:

```bash
make unittest
(or just py.test)
```

To run them and output a coverage report and a junit xml file run:

```bash
make report="true" unittest
```

These files get added to a test-output folder. The test-output folder is created if doesn't exist.

You can run these commands in the app's running container via `docker-compose exec case-management-api <command>` or `exec case-management-api <command>`. There is also an alias: `unit-test case-management-api` and `unit-test case-management-api -r` will run tests and generate reports respectively.

### Integration tests

The integration tests are contained in the integration_tests folder. [Pytest](http://docs.pytest.org/en/latest/) is used for integration testing. To run the tests and output a junit xml use the following command:

```shell
make integrationtest
(or py.test integration_tests)
```

This file gets added to the test-output folder. The test-output folder is created if doesn't exist.

To run the integration tests if you are using the common dev-env you can run `docker-compose exec case-management-api make integrationtest` or, using the alias, `integration-test case-management-api`.
