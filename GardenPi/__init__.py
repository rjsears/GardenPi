#!/usr/bin/python3

# -*- coding: utf-8 -*-

"""
__init__.py for usage with neptune/GardenPi V1.0.0

"""

VERSION = "V1.0.0 (2020-08-05)"

import sys
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
sys.path.append('/var/www/gardenpi_control/gardenpi/utilities')
sys.path.append('/var/www/gardenpi_control/gardenpi')
from flask import Flask

## CHANGE THIS if you plan on using Sentry, this is a Bogus Entry
sentry_sdk.init(
    dsn="https://e4f5fcf4e9ea4a2284e14e39d00d321d@sentry.io/5189890",
    integrations=[FlaskIntegration()])

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
## CHANGE THIS SECRET_KEY to something else!!
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba887'


# Must import AFTER the above otherwise you will get a circular reference
# due to the fact that routes.py imports the app stuff.
from gardenpi import routes
