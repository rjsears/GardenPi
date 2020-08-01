#!/usr/bin/python3

# -*- coding: utf-8 -*-

"""
__init__.py for usage with neptune/GardenPi V1.0.0
I use Sentry.IO to track trackbacks and errors, remove if
you are not using it.
"""

VERSION = "V1.0.0 (2020-07-31)"

import sys
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
sys.path.append('/var/www/gardenpi_control/gardenpi/utilities')
sys.path.append('/var/www/gardenpi_control/gardenpi')
from flask import Flask

sentry_sdk.init(
    dsn="https://xxxxxxxxxxxxxxxxxxxxxxxxx@sentry.io/5189890",
    integrations=[FlaskIntegration()])

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = 'kjashflkajshflkjhsalfkjhasdkjfha'


# Must import AFTER the above otherwise you will get a circular reference
# due to the fact that routes.py imports the app stuff.
from gardenpi import routes
