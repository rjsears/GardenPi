#!/usr/bin/python3

# -*- coding: utf-8 -*-

"""
run.py for use with neptune/GardenPi V1.0.0

Starts flask dev server.
"""

VERSION = "V1.0.0 (2020-07-31)"

from system_logging import setup_logging
from system_logging import read_logging_config
import logging

#Setup Module level logging here. Main logging config in system_logging.py


#from gardenpi import app
from routes import app

if __name__ == '__main__':
    setup_logging()
    level = read_logging_config('logging', 'log_level')
    level = logging._checkLevel(level)
    log = logging.getLogger(__name__)
    log.setLevel(level)
    app.run(host='0.0.0.0', port=8080, debug=True)