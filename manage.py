import os

from flask_script import Manager

from case_management_api.main import app

# ***** For Alembic start ******
from flask_migrate import Migrate, MigrateCommand
from case_management_api.models import *    # noqa
from case_management_api.extensions import db

migrate = Migrate(app, db)
# ***** For Alembic end ******

manager = Manager(app)

# ***** For Alembic start ******
manager.add_command('db', MigrateCommand)
# ***** For Alembic end ******


@manager.command
def runserver(port=9998):
    """Run the app using flask server"""

    os.environ["PYTHONUNBUFFERED"] = "yes"
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["COMMIT"] = "LOCAL"

    app.run(debug=True, port=int(port))


if __name__ == "__main__":
    manager.run()
