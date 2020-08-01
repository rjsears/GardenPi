#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Part of GardenPi. This is the logging module.
For use with neptune/GardenPi V1.0.0
"""

VERSION = "V1.0.0 (2020-07-31)"


import sys
import os
import yaml
import logging.config
sys.path.append('/var/www/gardenpi_control/gardenpi')
import system_info
import mysql.connector
from mysql.connector import Error
import logging.config, logging

def setup_logging(default_path='/var/www/gardenpi_control/gardenpi/logging.yaml', default_level=logging.CRITICAL, env_key='LOG_CFG'):
    """Module to configure program-wide logging. Designed for yaml configuration files."""
    log_level = read_logging_config('logging', 'log_level')
    log = logging.getLogger(__name__)
    level = logging._checkLevel(log_level)
    log.setLevel(level)
    system_logging = read_logging_config('logging', 'system_logging')
    if system_logging:
        path = default_path
        value = os.getenv(env_key, None)
        if value:
            path = value
        if os.path.exists(path):
            with open(path, 'rt') as f:
                try:
                    config = yaml.safe_load(f.read())
                    logging.config.dictConfig(config)
                except Exception as e:
                    print(e)
                    print('Error in Logging Configuration. Using default configs. Check File Permissions (for a start)!')
                    logging.basicConfig(level=default_level)
                    #capture_exception(e)
        else:
            logging.basicConfig(level=default_level)
            print('Failed to load configuration file. Using default configs')
            return log
    else:
        log.disabled = True


def read_logging_config(table, column):
    try:
        connection = mysql.connector.connect(user=system_info.mysql_username,
                                      password=system_info.mysql_password,
                                      host=system_info.mysql_servername,
                                      database=system_info.mysql_database)
        cursor = connection.cursor(buffered=True)
        cursor.execute(("SELECT %s FROM %s") % (column, table))
        for data in cursor:
            database_value = (data[0])
            return database_value
        cursor.close()
        connection.close()
    except Error as error:
        print(error)



def main():
    print("This script is not intended to be run directly.")
    print("This is the systemwide logging module.")
    print("It is called by other modules.")
    exit()


if __name__ == '__main__':
    main()