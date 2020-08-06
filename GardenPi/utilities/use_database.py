#!/usr/bin/python3

# -*- coding: utf-8 -*-

"""
use_database.py for use with neptune/GardenPi V1.0.0
Systemwide database functions
"""

VERSION = "V1.0.0 (2020-08-05)"

#TODO Code and general cleanup and logging, move rest of MySQL calls over to SQLAlchemy


import system_info
import mysql.connector
from mysql.connector import Error
from influxdb import InfluxDBClient, exceptions
from sqlalchemy import create_engine, update, select, and_, exists,  or_, func, not_
from tables import zones, screen, scheduled_jobs, zones_currently_running, water_tanks, water_source, power, power_scheduled_jobs, environmental, electrical_usage, temperatures, systemwide_alerts, systemwide_notifications, hydroponic_zones
from system_logging import setup_logging
from system_logging import read_logging_config
import logging

# Instantiate SQAlchemy Database Engine
engine = create_engine(system_info.sqlalchemy_db_uri, pool_recycle=3600)

#Setup Module level logging here. Main logging config in system_logging.py
setup_logging()
level = read_logging_config('logging', 'log_level')
level = logging._checkLevel(level)
log = logging.getLogger(__name__)
log.setLevel(level)


def onewire_temp_probes(action, probe_name, current_temp):
    with engine.begin() as conn:
        if action == 'get_probe_id':
            return (conn.execute(select([temperatures.c.onewire_id]).where(temperatures.c.temp_zone == (probe_name)))).scalar()
        elif action == 'get_current_temp':
            return (conn.execute(select([temperatures.c.current_temp]).where(temperatures.c.temp_zone == (probe_name)))).scalar()
        elif action == 'update_temperature':
            conn.execute(temperatures.update().where(temperatures.c.temp_zone == probe_name).values({temperatures.c.current_temp: current_temp}))
        elif action == 'get_all_info':
            return (conn.execute(select([temperatures]))).fetchall()


def systemwide_notification(action, type, value):
    with engine.begin() as conn:
        if action == 'enabled':
            return (conn.execute(select([getattr(systemwide_notifications.c, type)]))).scalar()
        elif action == 'toggle':
            conn.execute(systemwide_notifications.update().values({type: value}))


def sa_read_water_source():
    log.debug('sa_read_water_source() called')
    with engine.begin() as conn:
        return conn.execute(select([water_source])).fetchall()


def sa_update_is_fish_water_available(available):
    with engine.begin() as conn:
        if available:
            conn.execute(water_source.update().values({water_source.c.fish_available: True}))
        else:
            conn.execute(water_source.update().values({water_source.c.fish_available: False}))


def sa_update_water_source(new_water_source):
    with engine.begin() as conn:
        conn.execute(water_source.update().values({water_source.c.selected_source: new_water_source}))


def sa_update_job_water_source(job_water_source):
    with engine.begin() as conn:
        conn.execute(water_source.update().values({water_source.c.job_water_source: job_water_source}))


def sa_read_forced_stop_jobs():
    with engine.begin() as conn:
        return (conn.execute(select([scheduled_jobs]).where(scheduled_jobs.c.forced_stop_manually == (True)))).fetchall()


def sa_read_zone_times(job_start_time, job_stop_time):
    with engine.begin() as conn:
        return (conn.execute(select([scheduled_jobs]).where(and_(scheduled_jobs.c.job_start_time == (job_start_time),
                                                                    scheduled_jobs.c.job_stop_time == (job_stop_time))))).fetchall()


def sa_check_zone_times(job_start_time, job_stop_time):
    with engine.begin() as conn:
        results = (conn.execute(select([func.count(scheduled_jobs.c.job_id)]).where(not_(or_(scheduled_jobs.c.job_stop_time <= (job_start_time),
                                                                                         (scheduled_jobs.c.job_start_time >= (job_stop_time))))))).scalar()
        if results:
            return (True)
        else:
            return (False)


def sa_check_zone_times_conflict(job_start_time, job_stop_time, job_id):
    with engine.begin() as conn:
        results = (conn.execute(select([func.count(scheduled_jobs.c.job_id)]).where(not_(or_(scheduled_jobs.c.job_id == job_id,scheduled_jobs.c.job_stop_time <= job_start_time,
                                                                                    scheduled_jobs.c.job_start_time >= job_stop_time))))).scalar()
        if results:
            return (True)
        else:
            return (False)


def sa_check_power_zone_times_conflict(zone_name, job_start_time, job_stop_time, job_id):
    with engine.begin() as conn:
        results = (conn.execute(select([func.count(power_scheduled_jobs.c.job_id)]).where(and_(power_scheduled_jobs.c.zone == zone_name, (not_(or_(power_scheduled_jobs.c.job_id == job_id,power_scheduled_jobs.c.job_stop_time <= job_start_time,
                                                                                    power_scheduled_jobs.c.job_start_time >= job_stop_time))))))).scalar()
        if results:
            return (True)
        else:
            return (False)


def sa_check_zone_times_jobid(job_start_time, job_stop_time):
    with engine.begin() as conn:
        results = (conn.execute(select([scheduled_jobs.c.job_id]).where(not_(or_(scheduled_jobs.c.job_stop_time <= (job_start_time),
                                                                                    scheduled_jobs.c.job_start_time >= job_stop_time))))).fetchall()
        for job in results:
            return (conn.execute(select([scheduled_jobs]).where(scheduled_jobs.c.job_id == job[0]))).fetchall()


def are_any_zones_running_now(type):
    if type == 'water':
        with engine.begin() as conn:
            return (conn.scalar(select([exists().where(zones.c.running)])))
    elif type == 'power':
        with engine.begin() as conn:
            return (conn.scalar(select([exists().where(and_(power.c.running, (not_(or_(power.c.zone_name == 'power8', power.c.zone_name == 'power7', power.c.zone_name == 'intake_fan', power.c.zone_name == 'exhaust_fan')))))])))


def what_zone_is_running_now(type):
    if type == 'water':
        with engine.begin() as conn:
            return (conn.execute(select([zones.c.zone_name]).where(and_(zones.c.running,(not_(or_(zones.c.zone_name == 'fish_water', zones.c.zone_name == 'fresh_water')))))).scalar())
    elif type == 'power':
        with engine.begin() as conn:
            return (conn.execute(select([power.c.zone_name]).where(and_(power.c.running,(not_(or_(power.c.zone_name == 'power8', power.c.zone_name == 'power7', power.c.zone_name == 'intake_fan', power.c.zone_name == 'exhaust_fan')))))).scalar())


def update_running(is_running):
    with engine.begin() as conn:
        conn.execute(zones_currently_running.update().values({zones_currently_running.c.currently_running: is_running}))


def sa_read_zone_schedule_by_zonejobday(self, zone_name, zone_job, day):
    """
    Uses SQLAlchemy to connect to db and return all jobs by job number and day.
    """
    with engine.begin() as conn:
        return (conn.execute(select([scheduled_jobs]).where(and_(scheduled_jobs.c.zone == (zone_name),
                                                                    scheduled_jobs.c.zone_job == (zone_job),
                                                                    scheduled_jobs.c.job_enabled == (True),
                                                                    getattr(scheduled_jobs.c, day) == (True)))).fetchall())

def zone_enable(zone_name):
    with engine.begin() as conn:
        conn.execute(zones.update().where(zones.c.zone_name == zone_name).values({zones.c.enabled: True}))

#TODO - Fix This
def sa_read_zone_schedule(zone_name):
    '''
     Uses SQLAlchemy to connect to db and return all jobs for a particular zone.
    '''
    with engine.begin() as conn:
        stmt = select([scheduled_jobs]).where(scheduled_jobs.c.zone == zone_name)
        results = conn.execute(stmt).fetchall()
        return (results)


def sa_read_zone_schedule_by_job(zone_name, zone_job):
    """
    Uses SQLAlchemy to connect to db and return all jobs by job number.
    """
    with engine.begin() as conn:
        return (conn.execute(select([scheduled_jobs]).where(and_(scheduled_jobs.c.zone == (zone_name), scheduled_jobs.c.zone_job == (zone_job)))).fetchall())

def sa_read_zone_schedule_by_day(day):
    """
    SA query that joins on zones and gets all active jobs but only if zone is enabled.
    """
    with engine.begin() as conn:
        return (conn.execute(select([scheduled_jobs]).select_from(scheduled_jobs.join(zones, zones.c.zone_name == scheduled_jobs.c.zone))
                                .where(and_(zones.c.enabled == (True), scheduled_jobs.c.job_enabled == (True),getattr(scheduled_jobs.c, day) == (True)))).fetchall())

def sa_read_power_schedule_by_day(day):
    """
    SA query that joins on zones and gets all active jobs but only if zone is enabled.
    """
    with engine.begin() as conn:
        return (conn.execute(select([power_scheduled_jobs]).select_from(power_scheduled_jobs.join(power, power.c.zone_name == power_scheduled_jobs.c.zone))
                                .where(and_(power.c.enabled == (True), power_scheduled_jobs.c.job_enabled == (True),getattr(power_scheduled_jobs.c, day) == (True)))).fetchall())

# https://github.com/sqlalchemy/sqlalchemy/issues/5245 (Read this to see why values is a dict.)
def sa_update_zone_config(table_name, zone_name, field_name, field_value):
    with engine.begin() as conn:
        conn.execute(update([table_name]).where(table_name.c.name == zone_name).values({field_name: field_value}))


def forced_stopped_jobs(action, job_id):
    with engine.begin() as conn:
        if action == 'readall':
            return (conn.execute(select([scheduled_jobs]).where(scheduled_jobs.c.forced_stop_manually == True))).fetchall()
        elif action == 'check':
            return (conn.execute(select([zones_currently_running.c.force_stopped]))).scalar()
        elif action == 'update':
            conn.execute(scheduled_jobs.update().where(scheduled_jobs.c.job_id == job_id).values({scheduled_jobs.c.forced_stop_manually: False}))
        elif action == 'reset':
            conn.execute(zones_currently_running.update().values({zones_currently_running.c.force_stopped: False}))


def read_all_zone_info():
    with engine.begin() as conn:
        return (conn.execute(select([zones]))).fetchall()


def read_all_zone_names():
    with engine.begin() as conn:
        return (conn.execute(select([zones.c.zone_name]))).fetchall()


def read_all_hydroponic_zone_names():
    with engine.begin() as conn:
        return (conn.execute(select([hydroponic_zones.c.zone_name]))).fetchall()


def read_all_power_zone_names():
    with engine.begin() as conn:
        return (conn.execute(select([power.c.zone_name]))).fetchall()

# Intentional misspelling of power7 zone until I decide how I want to deal with it. Power7 provides
# power for our fish water main water pump, not sure we need to be able to schedule it or not, but
# if I do, I have to have it returned in this fucntion.
def read_all_userpower_zone_names():
    with engine.begin() as conn:
        return conn.execute(select([power.c.zone_name]).where(not_(or_(power.c.zone_name == 'power8', power.c.zone_name == 'ppower7', power.c.zone_name == 'intake_fan',power.c.zone_name == 'exhaust_fan')))).fetchall()

def read_all_garden_zone_names():
    with engine.begin() as conn:
        return conn.execute(select([zones.c.zone_name]).where(not_(or_(zones.c.zone_name == 'fish_water', zones.c.zone_name == 'fresh_water')))).fetchall()

def read_all_water_tank_names():
    with engine.begin() as conn:
        return (conn.execute(select([water_tanks.c.tank_name]))).fetchall()


def water_usage(zone_name, action, value):
    with engine.begin() as conn:
        if action == 'update_gallons_stop':
            conn.execute(zones.update().where(zones.c.zone_name == zone_name).values({zones.c.gallons_stop: value}))
        elif action == 'read_gallons_stop':
            return (conn.execute(select([zones.c.gallons_stop]).where(zones.c.zone_name == (zone_name)))).scalar()
        elif action == 'read_gallons_start':
            return (conn.execute(select([zones.c.gallons_start]).where(zones.c.zone_name == (zone_name)))).scalar()
        elif action == 'read_total_gallons_used':
            return (conn.execute(select([zones.c.total_gallons_used]).where(zones.c.zone_name == (zone_name)))).scalar()
        elif action == 'read_gallons_last_run':
            return (conn.execute(select([zones.c.gallons_last_run]).where(zones.c.zone_name == (zone_name)))).scalar()
        elif action == 'read_gallons_current_run':
            return (conn.execute(select([zones.c.gallons_current_run]).where(zones.c.zone_name == (zone_name)))).scalar()
        elif action == 'update_gallons_start':
            conn.execute(zones.update().where(zones.c.zone_name == zone_name).values({zones.c.gallons_start: value}))
        elif action == 'update_gallons_current_run':
            conn.execute(zones.update().where(zones.c.zone_name == zone_name).values({zones.c.gallons_current_run: value}))
        elif action == 'update_gallons_last_run':
            conn.execute(zones.update().where(zones.c.zone_name == zone_name).values({zones.c.gallons_last_run: value}))
        elif action == 'update_total_gallons_used':
            conn.execute(zones.update().where(zones.c.zone_name == zone_name).values({zones.c.total_gallons_used: value}))


def environmentals_data(action, field_name, field_value):
    with engine.begin() as conn:
        if action == 'readall':
            return ((conn.execute(select([environmental]))).fetchall())
        elif action == 'readone':
            return ((conn.execute(select([getattr(environmental.c, field_name)])))).scalar()
        else:
            conn.execute(environmental.update().values({field_name: field_value}))


def electrical_data(action, field_name, field_value):
    with engine.begin() as conn:
        if action == 'readall':
            return ((conn.execute(select([electrical_usage]))).fetchall())
        elif action == 'readone':
            return ((conn.execute(select([getattr(electrical_usage.c, field_name)])))).scalar()
        else:
            conn.execute(electrical_usage.update().values({field_name: field_value}))

def solar_data(action, field_name, field_value):
    with engine.begin() as conn:
        if action == 'readall':
            return ((conn.execute(select([power_solar]))).fetchall())
        elif action == 'readone':
            return ((conn.execute(select([getattr(power_solar.c, field_name)])))).scalar()
        else:
            conn.execute(power_solar.update().values({field_name: field_value}))
            
def notification_alerts(sensor_name, action, field_name, field_value):
    with engine.begin() as conn:
        if action == 'enabled':
            return conn.execute(select([getattr(systemwide_alerts.c, field_name)]).where(systemwide_alerts.c.sensor_name == sensor_name)).scalar()
        elif action == 'was_alert_sent':
            return conn.execute(select([systemwide_alerts.c.alert_sent]).where(systemwide_alerts.c.sensor_name == sensor_name)).scalar()
        elif action == 'set_alert_sent':
            conn.execute(systemwide_alerts.update().where(systemwide_alerts.c.sensor_name == sensor_name).values({systemwide_alerts.c.alert_sent: field_value}))
        elif action == 'toggle':
            if conn.execute(select([getattr(systemwide_alerts.c, field_name)]).where(systemwide_alerts.c.sensor_name == sensor_name)).scalar():
                conn.execute(systemwide_alerts.update().where(systemwide_alerts.c.sensor_name == sensor_name).values({field_name: False}))
            else:
                conn.execute(systemwide_alerts.update().where(systemwide_alerts.c.sensor_name == sensor_name).values({field_name: True}))
        elif action == 'readall':
            return (conn.execute(select([systemwide_alerts.c.sensor_name]))).fetchall()
        elif action == 'get_alert_limit':
            return (conn.execute(select([systemwide_alerts.c.alert_limit]).where(systemwide_alerts.c.sensor_name == sensor_name))).scalar()
        else:
            conn.execute(systemwide_alerts.update().where(systemwide_alerts.c.sensor_name == sensor_name).values({field_name: field_value}))


def zone_name_in_notification_alerts(zone_name):
    with engine.begin() as conn:
        return conn.execute(select([systemwide_alerts.c.sensor_name]).where(systemwide_alerts.c.sensor_name == zone_name)).scalar()


def zone_name_in_hydroponic_zones(zone_name):
    with engine.begin() as conn:
        return conn.execute(select([hydroponic_zones.c.zone_name]).where(hydroponic_zones.c.zone_name == zone_name)).scalar()


def zone_name_in_power_zones(zone_name):
    with engine.begin() as conn:
        return conn.execute(select([power.c.zone_name]).where(power.c.zone_name == zone_name)).scalar()


def zone_name_in_zones(zone_name):
    with engine.begin() as conn:
        return conn.execute(select([zones.c.zone_name]).where(zones.c.zone_name == zone_name)).scalar()


def zone_name_in_userpower_zones(zone_name):
    with engine.begin() as conn:
        return conn.execute(select([power.c.zone_name]).where(and_(power.c.zone_name == zone_name, (not_(or_(power.c.zone_name == 'power8', power.c.zone_name == 'power7', power.c.zone_name == 'intake_fan',power.c.zone_name == 'exhaust_fan')))))).scalar()


def zone_name_in_garden_zones(zone_name):
    with engine.begin() as conn:
        return conn.execute(select([zones.c.zone_name]).where(and_(zones.c.zone_name == zone_name, (not_(or_(zones.c.zone_name == 'fish_water', zones.c.zone_name == 'fresh_water')))))).scalar()


def screen_mode(action):
    with engine.begin() as conn:
        if action == 'check_mode':
            return (conn.execute(select([getattr(screen.c, 'kioskmode')]))).scalar()
        else:
            conn.execute(screen.update().values({screen.c.kioskmode: action}))


def zone_running_manually(zone_name):
    if zone_name_in_zones(zone_name):
        with engine.begin() as conn:
            return (conn.execute(select([zones.c.running_manually]).where(zones.c.zone_name == zone_name))).scalar()
    elif zone_name_in_power_zones(zone_name):
        with engine.begin() as conn:
            return (conn.execute(select([power.c.running_manually]).where(power.c.zone_name == zone_name))).scalar()
    elif zone_name_in_hydroponic_zones(zone_name):
        with engine.begin() as conn:
            return (conn.execute(select([hydroponic_zones.c.running_manually]).where(hydroponic_zones.c.zone_name == zone_name))).scalar()


def zone_running(zone_name):
    if zone_name_in_zones(zone_name):
        with engine.begin() as conn:
            return (conn.execute(select([zones.c.running]).where(zones.c.zone_name == zone_name))).scalar()
    elif zone_name_in_power_zones(zone_name):
        with engine.begin() as conn:
            return (conn.execute(select([power.c.running]).where(power.c.zone_name == zone_name))).scalar()
    elif zone_name_in_hydroponic_zones(zone_name):
        with engine.begin() as conn:
            return (conn.execute(select([hydroponic_zones.c.running]).where(hydroponic_zones.c.zone_name == zone_name))).scalar()

'''
def read_mysql_zone_config(table_name, zone_name):
  #  log.debug( f'read_mysql_database_zoneinfo() called with ({table})')
    try:
        connection = mysql.connector.connect(user=system_info.mysql_username,
                                      password=system_info.mysql_password,
                                      host=system_info.mysql_servername,
                                      database=system_info.mysql_database)
        cursor = connection.cursor(buffered=True)
        cursor.execute(f"Select * FROM {table_name} WHERE name =  \"{zone_name}\"")
        for data in cursor:
            database_values = (data)
            return database_values
        cursor.close()
        connection.close()
    except Error as error:
     #   log.warning("Failed to read record from database: {}".format(error))
        exit()

'''

def read_mysql_database(table, column):
   # log.debug( f'read_mysql_database() called with ({table}, {column})')
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
    except Error as error :
      #  log.warning("Failed to read record from database: {}".format(error))
        exit()

def update_mysql_database(table,column,value):
   # log.debug(f'update_mysql_database() called with Table: {table}, Column: {column}, Value: {value}')
    try:
        connection = mysql.connector.connect(user=system_info.mysql_username,
                                      password=system_info.mysql_password,
                                      host=system_info.mysql_servername,
                                      database=system_info.mysql_database)
        cursor = connection.cursor(buffered=True)
        sql_update = "UPDATE " + table + " SET " + column + " = %s"
        cursor.execute(sql_update, (value,))
        connection.commit()
        cursor.close()
        connection.close()
    except Error as error :
        pass
      #  log.warning(f'Failed to Update record in database: {error}')
        exit()


def insert_mysql_database(table,column,value):
   # log.debug(f'insert_mysql_database() called with Table: {table}, Column: {column}, Value: {value}')
    try:
        connection = mysql.connector.connect(user=system_info.mysql_username,
                                      password=system_info.mysql_password,
                                      host=system_info.mysql_servername,
                                      database=system_info.mysql_database)
        cursor = connection.cursor(buffered=True)
        sql_insert = "INSERT INTO " + table + " SET " + column + " = %s"
        cursor.execute(sql_insert, (value,))
        connection.commit()
        cursor.close()
        connection.close()
    except Error as error :
        pass
      #  log.warning(f'Failed to insert record in database: {error}')
        exit()


def update_influx_database(measurement, value, tank_name):
   # log.debug(f'update_influx_database called with (Measurement: {measurement}, Value {value}, Tank Name: {tank_name})')

    client = InfluxDBClient(system_info.influx_host, system_info.influx_port, system_info.influx_user, system_info.influx_password,
                            system_info.influx_dbname, timeout=2)
    json_body = [
        {
            "measurement": measurement,
            "tags": {
                "tank": tank_name
            },
            "fields": {
                "value": value
            }
        }
    ]
    try:
        client.write_points(json_body)
        client.close()
    except (exceptions.InfluxDBClientError, exceptions.InfluxDBServerError) as e:
        pass
      #  log.warning(f'Failed to Update record in Influx database: {e}')

    if system_info.redundant_influx:
        client2 = InfluxDBClient(system_info.influx2_host, system_info.influx2_port, system_info.influx2_user, system_info.influx2_password,
                                system_info.influx2_dbname, timeout=2)
        try:
            client2.write_points(json_body)
            client2.close()
        except (exceptions.InfluxDBClientError, exceptions.InfluxDBServerError) as e:
            pass
          #  log.warning(f'Failed to Update record in Influx database: {e}')

def read_influx_database_power(measurement, device):
    client = InfluxDBClient(system_info.influx_host, system_info.influx_port, system_info.influx_user, system_info.influx_password, 'electrical_monitoring')
    results = client.query(("SELECT %s from %s ORDER by time DESC LIMIT 1") % (device, measurement))
    points = results.get_points()
    for item in points:
        return item[device]

def read_influx_database_temps(measurement):
    #log.debug(f'read_influx_database called with (Measurement: {measurement}, Tank Name: {tank_name})')
    client = InfluxDBClient(system_info.influx_host, system_info.influx_port, system_info.influx_user, system_info.influx_password, 'temp_monitoring')
    results = client.query(f'SELECT temp from temp WHERE device = {measurement} ORDER by time DESC LIMIT 1')
    points = results.get_points()
    for item in points:
        return item['temp']


def read_emoncms_database(type, table):
 #   log.info("read_emoncms_database() called with Type: {}, Table: {})".format(type, table))
    try:
        connection = mysql.connector.connect(user=system_info.emoncms_username,
                                      password=system_info.emoncms_password,
                                      host=system_info.emoncms_servername,
                                      database=system_info.emoncms_db)
        cursor = connection.cursor(buffered=True)
        cursor.execute(("SELECT `%s` FROM `%s` ORDER by time DESC LIMIT 1") % (type, table))
        for data in cursor:
            database_value = (data[0])
            return database_value
        cursor.close()
        connection.close()
    except Error as error :
        print(error)
      #  log.warning( "Failed to read record from database: {}".format(error))
        exit()
  #  finally:
  #      if(connection.is_connected()):
   #         connection.close



def main():
    print("Not intended to be run directly.")
    print("This is the systemwide Influx & MySQL database module.")
    print("It is called by other modules.")
    exit()


if __name__ == '__main__':
    main()


