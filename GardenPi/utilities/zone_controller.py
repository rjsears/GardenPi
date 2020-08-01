#!/usr/bin/python3

# -*- coding: utf-8 -*-

"""
zone_controller.py for usage with neptune/GardenPi V1.0.0
Manages all of our irrigation/hydroponics water zones.
"""

VERSION = "V1.0.0 (2020-07-31)"



import sys
sys.path.append('/var/www/gardenpi_control/gardenpi')
import system_info
from sqlalchemy import update, select, and_, create_engine
from tables import zones, scheduled_jobs, zones_currently_running, water_source, hydroponic_zones
from system_logging import setup_logging
from system_logging import read_logging_config
import logging
import wiringpi as mcp
mcp.wiringPiSetup()        # Initialise wiringpi
mcp.mcp23017Setup(64,0x26) # MCP0 GPIO 64-79
mcp.mcp23017Setup(80,0x27) # MCP1 GPIO 80-95

# Instantiate SQAlchemy Database Engine
engine = create_engine(system_info.sqlalchemy_db_uri, pool_recycle=3600)

#Setup Module level logging here. Main logging config in system_logging.py
setup_logging()
level = read_logging_config('logging', 'log_level')
level = logging._checkLevel(level)
log = logging.getLogger(__name__)
log.setLevel(level)

class ZoneSchedule:
    def __init__(self, name, job_id, zone_job, job_enabled, job_start_time, job_stop_time,
                 job_duration, job_running, monday, tuesday, wednesday, thursday, friday,
                 saturday, sunday, forced_stopped_manually):
        self.name = name
        self.job_id = job_id
        self.zone_job = zone_job
        self.job_enabled = job_enabled
        self.job_start_time = job_start_time
        self.job_stop_time = job_stop_time
        self.job_duration = job_duration
        self.job_running = job_running
        self.monday = monday
        self.tuesday = tuesday
        self.wednesday = wednesday
        self.thursday = thursday
        self.friday = friday
        self.saturday = saturday
        self.sunday = sunday
        self.forced_stopped_manually = forced_stopped_manually

    @classmethod
    def config_zoneschedule(cls, zone_name):
        with engine.begin() as conn:
            stmt = select([scheduled_jobs]).where(scheduled_jobs.c.zone.in_(zone_name))
            return [
                cls(
                    name=row[scheduled_jobs.c.zone],
                    job_id=row[scheduled_jobs.c.job_id],
                    zone_job=row[scheduled_jobs.c.zone_job],
                    job_enabled=row[scheduled_jobs.c.job_enabled],
                    job_start_time=row[scheduled_jobs.c.job_start_time],
                    job_stop_time=row[scheduled_jobs.c.job_stop_time],
                    job_duration=row[scheduled_jobs.c.job_duration],
                    job_running=row[scheduled_jobs.c.job_running],
                    monday=row[scheduled_jobs.c.monday],
                    tuesday=row[scheduled_jobs.c.tuesday],
                    wednesday=row[scheduled_jobs.c.wednesday],
                    thursday=row[scheduled_jobs.c.thursday],
                    friday=row[scheduled_jobs.c.friday],
                    saturday=row[scheduled_jobs.c.saturday],
                    sunday=row[scheduled_jobs.c.sunday],
                    forced_stopped_manually=row[scheduled_jobs.c.forced_stop_manually]
                )
                for row in conn.execute(stmt).fetchall()
            ]

    def sa_read_zone_schedule_by_zonejob(self, zone_name, zone_job):
        """
        Uses SQLAlchemy to connect to db and return all jobs by job number.
        """
        with engine.begin() as conn:
            return (conn.execute(select([scheduled_jobs]).where(and_(scheduled_jobs.c.zone == (zone_name),
                                                                        scheduled_jobs.c.zone_job == (zone_job))))).fetchall()


    def sa_read_zone_schedule_by_zonejobday(self, zone_name, zone_job, day):
        """
        Uses SQLAlchemy to connect to db and return all jobs by job number and day.
        """
        with engine.begin() as conn:
            return (conn.execute(select([scheduled_jobs]).where(and_(scheduled_jobs.c.zone == (zone_name),
                                                                        scheduled_jobs.c.zone_job == (zone_job),
                                                                        scheduled_jobs.c.job_enabled == (True),
                                                                        getattr(scheduled_jobs.c, day) == (True))))).fetchall()


    def sa_read_zone_schedule_by_zone(self, zone_name):
        with engine.begin() as conn:
            return (conn.execute(select([scheduled_jobs]).where(scheduled_jobs.c.zone == zone_name))).fetchall()


    def update_day(self, zone_name, zone_job, day_of_week, value):
        with engine.begin() as conn:
            conn.execute(scheduled_jobs.update().where(and_(scheduled_jobs.c.zone == (zone_name),
                                                            scheduled_jobs.c.zone_job == (zone_job))).values({getattr(scheduled_jobs.c, day_of_week): value}))

    def update_job_start_time(self, zone_name, zone_job, job_start_time):
        with engine.begin() as conn:
            conn.execute(scheduled_jobs.update().where(and_(scheduled_jobs.c.zone == (zone_name),
                                                            scheduled_jobs.c.zone_job == (zone_job))).values({scheduled_jobs.c.job_start_time: job_start_time}))

    def update_job_stop_time(self, zone_name, zone_job, job_stop_time):
        with engine.begin() as conn:
            conn.execute(scheduled_jobs.update().where(and_(scheduled_jobs.c.zone == (zone_name),
                                                            scheduled_jobs.c.zone_job == (zone_job))).values({scheduled_jobs.c.job_stop_time: job_stop_time}))

    def toggle_job(self, zone_name, zone_job):
        with engine.begin() as conn:
            job_enabled = (self.sa_read_zone_schedule_by_zonejob(zone_name, zone_job)[0][3])
            if job_enabled:
                    conn.execute(scheduled_jobs.update().where(and_(scheduled_jobs.c.zone == (zone_name),
                                                                    scheduled_jobs.c.zone_job == (zone_job))).values({scheduled_jobs.c.job_enabled: False}))
            else:
                conn.execute(scheduled_jobs.update().where(and_(scheduled_jobs.c.zone == (zone_name),
                                                                scheduled_jobs.c.zone_job == (zone_job))).values({scheduled_jobs.c.job_enabled: True}))

    def update_job_duration(self, zone_name, zone_job, job_duration):
        with engine.begin() as conn:
            conn.execute(scheduled_jobs.update().where(and_(scheduled_jobs.c.zone == (zone_name),
                                                            scheduled_jobs.c.zone_job == (zone_job))).values({scheduled_jobs.c.job_duration: job_duration}))

class ZoneController:
    def __init__(self, name, number, description, gpio, enabled, running, running_manually, mcp, notifications, sms, pb, email):
        self.zone_name = name
        self.zone_number = number
        self.description = description
        self.gpio = gpio
        self.enabled = enabled
        self.running = running
        self.running_manually = running_manually
        self.mcp = mcp
        self.notifications = notifications
        self.sms = sms
        self.pb = pb
        self.email = email


    @classmethod
    def read_config(cls, zone_name):
        with engine.begin() as conn:
            stmt = select([zones]).where(zones.c.zone_name.in_(zone_name))
            return [
                cls(
                    name=row[zones.c.zone_name],
                    number=row[zones.c.zone_number],
                    description=row[zones.c.description],
                    gpio=row[zones.c.gpio],
                    enabled=row[zones.c.enabled],
                    running=row[zones.c.running],
                    running_manually=row[zones.c.running_manually],
                    mcp=row[zones.c.mcp],
                    notifications=row[zones.c.notifications],
                    sms=row[zones.c.sms],
                    pb=row[zones.c.pb],
                    email=row[zones.c.email]
                )
                for row in conn.execute(stmt).fetchall()
            ]

    def run_job(self, job_id):
        with engine.begin() as conn:
            enabled = (conn.execute(select([zones.c.enabled]).where(zones.c.zone_name == self.zone_name))).scalar()
        if enabled:
            with engine.begin() as conn:
                running = (conn.execute(select([zones.c.running]).where(zones.c.zone_name == self.zone_name))).scalar()
            if running:
                log.debug(f'Zone {self.zone_number} ({self.zone_name}) is already running.')
            else:
                self.running = True
                with engine.begin() as conn:
                    # With this db update we are updating the individual zone db record for the zone that is running.
                    conn.execute(zones.update().where(zones.c.zone_name == self.zone_name).values({zones.c.running: True}))
                    conn.execute(zones.update().where(zones.c.zone_name == self.zone_name).values({zones.c.running_manually: False}))
                    conn.execute(scheduled_jobs.update().where(scheduled_jobs.c.job_id == job_id).values({scheduled_jobs.c.job_running: True}))
                    # With this db update we are updating the system_wide indication that "a" or "any" zone is running.
                    # To access this, call use_database.zones_running_now() and it will return True or False on a systemwide
                    # basis.
                    conn.execute(zones_currently_running.update().values({zones_currently_running.c.currently_running: True}))
                    conn.execute(zones_currently_running.update().values({zones_currently_running.c.run_manually: False}))
                    conn.execute(zones_currently_running.update().values({zones_currently_running.c.run_by_job: True}))
                    conn.execute(zones_currently_running.update().values({zones_currently_running.c.job_id: job_id}))
                    mcp.pinMode(self.gpio, 1)
                    mcp.digitalWrite(self.gpio, 1)
                log.debug(f'Zone {self.zone_number} ({self.zone_name}) is now RUNNING.')
        else:
            log.debug(f'ERROR: Zone {self.zone_number} ({self.zone_name}) is DISABLED. Please enable it first.')

    def run(self):
        with engine.begin() as conn:
            enabled = (conn.execute(select([zones.c.enabled]).where(zones.c.zone_name == self.zone_name))).scalar()
        if enabled:
            with engine.begin() as conn:
                running = (conn.execute(select([zones.c.running]).where(zones.c.zone_name == self.zone_name))).scalar()
            if running:
                log.debug(f'Zone {self.zone_number} ({self.zone_name}) is already running.')
            else:
                self.running = True
                with engine.begin() as conn:
                    # With this db update we are updating the individual zone db record for the zone that is running.
                    conn.execute(zones.update().where(zones.c.zone_name == self.zone_name).values({zones.c.running: True}))
                    conn.execute(zones.update().where(zones.c.zone_name == self.zone_name).values({zones.c.running_manually: True}))
                    # With this db update we are updating the system_wide indication that "a" or "any" zone is running.
                    # To access this, call use_database.zones_running_now() and it will return True or False on a systemwide
                    # basis.
                    conn.execute(zones_currently_running.update().values({zones_currently_running.c.currently_running: True}))
                    conn.execute(zones_currently_running.update().values({zones_currently_running.c.run_manually: True}))
                    conn.execute(zones_currently_running.update().values({zones_currently_running.c.run_by_job: False}))
                    conn.execute(zones_currently_running.update().values({zones_currently_running.c.job_id: 0}))
                    mcp.pinMode(self.gpio, 1)
                    mcp.digitalWrite(self.gpio, 1)
                log.debug(f'Zone {self.zone_number} ({self.zone_name}) is now RUNNING.')
        else:
            log.debug(f'ERROR: Zone {self.zone_number} ({self.zone_name}) is DISABLED. Please enable it first.')

      #  if not self.enabled:
       #     raise Exception(f'ERROR: Zone {self.zone_number} ({self.name}) is DISABLED. Please enable it first.')

    def stop_job(self, job_id, forced):
        with engine.begin() as conn:
            running =  (conn.execute(select([zones.c.running]).where(zones.c.zone_name == self.zone_name))).scalar()
        if running:
            self.running = False
            with engine.begin() as conn:
                # With this db update we are updating the individual zone db record for the zone that is running.
                conn.execute(zones.update().where(zones.c.zone_name == self.zone_name).values({zones.c.running: False}))
                conn.execute(zones.update().where(zones.c.zone_name == self.zone_name).values({zones.c.running_manually: False}))
                conn.execute(scheduled_jobs.update().where(scheduled_jobs.c.job_id == job_id).values({scheduled_jobs.c.job_running: False}))
                if forced:
                    conn.execute(scheduled_jobs.update().where(scheduled_jobs.c.job_id == job_id).values({scheduled_jobs.c.forced_stop_manually: True}))
                    conn.execute(zones_currently_running.update().values({zones_currently_running.c.force_stopped: True}))
                # With this db update we are updating the system_wide indication that "a" or "any" zone is running.
                # To access this, call use_database.zones_running_now() and it will return True or False on a systemwide
                # basis.
                conn.execute(zones_currently_running.update().values({zones_currently_running.c.currently_running: False}))
                conn.execute(zones_currently_running.update().values({zones_currently_running.c.run_manually: False}))
                conn.execute(zones_currently_running.update().values({zones_currently_running.c.run_by_job: False}))
                conn.execute(zones_currently_running.update().values({zones_currently_running.c.job_id: 0}))
                mcp.digitalWrite(self.gpio, 0)
            log.debug(f'Zone {self.zone_number} ({self.zone_name}) is now STOPPED.')
        else:
            log.debug(f'Zone {self.zone_number} ({self.zone_name}) is not currently running!!.')


    def stop(self):
        with engine.begin() as conn:
            enabled = (conn.execute(select([zones.c.enabled]).where(zones.c.zone_name == self.zone_name))).scalar()
        if enabled:
            with engine.begin() as conn:
                running = (conn.execute(select([zones.c.running]).where(zones.c.zone_name == self.zone_name))).scalar()
            if running:
                self.running = False
                with engine.begin() as conn:
                    # With this db update we are updating the individual zone db record for the zone that is running.
                    conn.execute(zones.update().where(zones.c.zone_name == self.zone_name).values({zones.c.running: False}))
                    conn.execute(zones.update().where(zones.c.zone_name == self.zone_name).values({zones.c.running_manually: False}))
                    # With this db update we are updating the system_wide indication that "a" or "any" zone is running.
                    # To access this, call use_database.zones_running_now() and it will return True or False on a systemwide
                    # basis.
                    conn.execute(zones_currently_running.update().values({zones_currently_running.c.currently_running: False}))
                    conn.execute(zones_currently_running.update().values({zones_currently_running.c.run_manually: False}))
                    conn.execute(zones_currently_running.update().values({zones_currently_running.c.run_by_job: False}))
                    conn.execute(zones_currently_running.update().values({zones_currently_running.c.job_id: 0}))
                    mcp.digitalWrite(self.gpio, 0)
                log.debug(f'Zone {self.zone_number} ({self.zone_name}) is now STOPPED.')
            else:
                log.debug(f'Zone {self.zone_number} ({self.zone_name}) is not currently running.')
        else:
            log.debug(f'ERROR: Zone {self.zone_number} ({self.zone_name}) is DISABLED. Please enable it first.')

    def enable(self):
        with engine.begin() as conn:
            enabled = (conn.execute(select([zones.c.enabled]).where(zones.c.zone_name == self.zone_name))).scalar()
        if enabled:
            log.debug(f'Zone {self.zone_number} ({self.zone_name}) is already enabled.')
        else:
            self.enabled = True
            with engine.begin() as conn:
                conn.execute(zones.update().where(zones.c.zone_name == self.zone_name).values({zones.c.enabled: True}))
            log.debug(f'Zone {self.zone_number} ({self.zone_name}) has been enabled.')

    def disable(self):
        with engine.begin() as conn:
            enabled = (conn.execute(select([zones.c.enabled]).where(zones.c.zone_name == self.zone_name))).scalar()
        if enabled:
            with engine.begin() as conn:
                running = (conn.execute(select([zones.c.running]).where(zones.c.zone_name == self.zone_name))).scalar()
            if running:
                log.debug(f'Zone {self.zone_number} ({self.zone_name}) is currently running.')
                log.debug(f'Shutting off Zone {self.zone_number} ({self.zone_name}) before disabling.')
                self.stop()
            self.enabled = False
            with engine.begin() as conn:
                conn.execute(zones.update().where(zones.c.zone_name == self.zone_name).values({zones.c.enabled: False}))
            log.debug(f'Zone {self.zone_number} ({self.zone_name}) has been disbled.')
        else:
            log.debug(f'Zone {self.zone_number} ({self.zone_name}) is already disabled.')

    def notification_toggle(self, notification):
        with engine.begin() as conn:
            if getattr(self, notification):
                conn.execute(zones.update().where(zones.c.zone_name == self.zone_name).values({notification: False}))
                setattr(self, notification, False)
                log.debug(f'System Notifications: ({notification}) for Zone {self.zone_number} ({self.zone_name}) Disabled.')
            else:
                conn.execute(zones.update().where(zones.c.zone_name == self.zone_name).values({notification: True}))
                setattr(self, notification, True)
                log.debug(f'System Notifications: ({notification}) for Zone {self.zone_number} ({self.zone_name}) Enabled.')


class HydroponicsController:
    def __init__(self, name, number, description, gpio, enabled, running, running_manually, mcp, notifications, sms, pb, email):
        self.zone_name = name
        self.zone_number = number
        self.description = description
        self.gpio = gpio
        self.enabled = enabled
        self.running = running
        self.running_manually = running_manually
        self.mcp = mcp
        self.notifications = notifications
        self.sms = sms
        self.pb = pb
        self.email = email


    @classmethod
    def read_config(cls, zone_name):
        with engine.begin() as conn:
            stmt = select([hydroponic_zones]).where(hydroponic_zones.c.zone_name.in_(zone_name))
            return [
                cls(
                    name=row[hydroponic_zones.c.zone_name],
                    number=row[hydroponic_zones.c.zone_number],
                    description=row[hydroponic_zones.c.description],
                    gpio=row[hydroponic_zones.c.gpio],
                    enabled=row[hydroponic_zones.c.enabled],
                    running=row[hydroponic_zones.c.running],
                    running_manually=row[hydroponic_zones.c.running_manually],
                    mcp=row[hydroponic_zones.c.mcp],
                    notifications=row[hydroponic_zones.c.notifications],
                    sms=row[hydroponic_zones.c.sms],
                    pb=row[hydroponic_zones.c.pb],
                    email=row[hydroponic_zones.c.email]
                )
                for row in conn.execute(stmt).fetchall()
            ]

    def run_job(self, job_id):
        with engine.begin() as conn:
            enabled = (conn.execute(select([hydroponic_zones.c.enabled]).where(hydroponic_zones.c.zone_name == self.zone_name))).scalar()
        if enabled:
            with engine.begin() as conn:
                running = (conn.execute(select([hydroponic_zones.c.running]).where(hydroponic_zones.c.zone_name == self.zone_name))).scalar()
            if running:
                log.debug(f'Zone {self.zone_number} ({self.zone_name}) is already running.')
            else:
                self.running = True
                with engine.begin() as conn:
                    # With this db update we are updating the individual zone db record for the zone that is running.
                    conn.execute(hydroponic_zones.update().where(hydroponic_zones.c.zone_name == self.zone_name).values({hydroponic_zones.c.running: True}))
                    conn.execute(hydroponic_zones.update().where(hydroponic_zones.c.zone_name == self.zone_name).values({hydroponic_zones.c.running_manually: False}))
                    conn.execute(scheduled_jobs.update().where(scheduled_jobs.c.job_id == job_id).values({scheduled_jobs.c.job_running: True}))
                    # With this db update we are updating the system_wide indication that "a" or "any" zone is running.
                    # To access this, call use_database.zones_running_now() and it will return True or False on a systemwide
                    # basis.
                    conn.execute(zones_currently_running.update().values({zones_currently_running.c.currently_running: True}))
                    conn.execute(zones_currently_running.update().values({zones_currently_running.c.run_manually: False}))
                    conn.execute(zones_currently_running.update().values({zones_currently_running.c.run_by_job: True}))
                    conn.execute(zones_currently_running.update().values({zones_currently_running.c.job_id: job_id}))
                    mcp.pinMode(self.gpio, 1)
                    mcp.digitalWrite(self.gpio, 1)
                log.debug(f'Zone {self.zone_number} ({self.zone_name}) is now RUNNING.')
        else:
            log.debug(f'ERROR: Zone {self.zone_number} ({self.zone_name}) is DISABLED. Please enable it first.')

    def run(self):
        with engine.begin() as conn:
            enabled = (conn.execute(select([hydroponic_zones.c.enabled]).where(hydroponic_zones.c.zone_name == self.zone_name))).scalar()
        if enabled:
            with engine.begin() as conn:
                running = (conn.execute(select([hydroponic_zones.c.running]).where(hydroponic_zones.c.zone_name == self.zone_name))).scalar()
            if running:
                log.debug(f'Zone {self.zone_number} ({self.zone_name}) is already running.')
            else:
                self.running = True
                with engine.begin() as conn:
                    # With this db update we are updating the individual zone db record for the zone that is running.
                    conn.execute(hydroponic_zones.update().where(hydroponic_zones.c.zone_name == self.zone_name).values({hydroponic_zones.c.running: True}))
                    conn.execute(hydroponic_zones.update().where(hydroponic_zones.c.zone_name == self.zone_name).values({hydroponic_zones.c.running_manually: True}))
                    # With this db update we are updating the system_wide indication that "a" or "any" zone is running.
                    # To access this, call use_database.zones_running_now() and it will return True or False on a systemwide
                    # basis.
                    conn.execute(zones_currently_running.update().values({zones_currently_running.c.currently_running: True}))
                    conn.execute(zones_currently_running.update().values({zones_currently_running.c.run_manually: True}))
                    conn.execute(zones_currently_running.update().values({zones_currently_running.c.run_by_job: False}))
                    conn.execute(zones_currently_running.update().values({zones_currently_running.c.job_id: 0}))
                    mcp.pinMode(self.gpio, 1)
                    mcp.digitalWrite(self.gpio, 1)
                log.debug(f'Zone {self.zone_number} ({self.zone_name}) is now RUNNING.')
        else:
            log.debug(f'ERROR: Zone {self.zone_number} ({self.zone_name}) is DISABLED. Please enable it first.')

      #  if not self.enabled:
       #     raise Exception(f'ERROR: Zone {self.zone_number} ({self.name}) is DISABLED. Please enable it first.')

    def stop_job(self, job_id, forced):
        with engine.begin() as conn:
            running =  (conn.execute(select([hydroponic_zones.c.running]).where(hydroponic_zones.c.zone_name == self.zone_name))).scalar()
        if running:
            self.running = False
            with engine.begin() as conn:
                # With this db update we are updating the individual zone db record for the zone that is running.
                conn.execute(hydroponic_zones.update().where(hydroponic_zones.c.zone_name == self.zone_name).values({hydroponic_zones.c.running: False}))
                conn.execute(hydroponic_zones.update().where(hydroponic_zones.c.zone_name == self.zone_name).values({hydroponic_zones.c.running_manually: False}))
                conn.execute(scheduled_jobs.update().where(scheduled_jobs.c.job_id == job_id).values({scheduled_jobs.c.job_running: False}))
                if forced:
                    conn.execute(scheduled_jobs.update().where(scheduled_jobs.c.job_id == job_id).values({scheduled_jobs.c.forced_stop_manually: True}))
                    conn.execute(zones_currently_running.update().values({zones_currently_running.c.force_stopped: True}))
                # With this db update we are updating the system_wide indication that "a" or "any" zone is running.
                # To access this, call use_database.zones_running_now() and it will return True or False on a systemwide
                # basis.
                conn.execute(zones_currently_running.update().values({zones_currently_running.c.currently_running: False}))
                conn.execute(zones_currently_running.update().values({zones_currently_running.c.run_manually: False}))
                conn.execute(zones_currently_running.update().values({zones_currently_running.c.run_by_job: False}))
                conn.execute(zones_currently_running.update().values({zones_currently_running.c.job_id: 0}))
                mcp.digitalWrite(self.gpio, 0)
            log.debug(f'Zone {self.zone_number} ({self.zone_name}) is now STOPPED.')
        else:
            log.debug(f'Zone {self.zone_number} ({self.zone_name}) is not currently running!!.')


    def stop(self):
        with engine.begin() as conn:
            enabled = (conn.execute(select([hydroponic_zones.c.enabled]).where(hydroponic_zones.c.zone_name == self.zone_name))).scalar()
        if enabled:
            with engine.begin() as conn:
                running = (conn.execute(select([hydroponic_zones.c.running]).where(hydroponic_zones.c.zone_name == self.zone_name))).scalar()
            if running:
                self.running = False
                with engine.begin() as conn:
                    # With this db update we are updating the individual zone db record for the zone that is running.
                    conn.execute(hydroponic_zones.update().where(hydroponic_zones.c.zone_name == self.zone_name).values({hydroponic_zones.c.running: False}))
                    conn.execute(hydroponic_zones.update().where(hydroponic_zones.c.zone_name == self.zone_name).values({hydroponic_zones.c.running_manually: False}))
                    # With this db update we are updating the system_wide indication that "a" or "any" zone is running.
                    # To access this, call use_database.zones_running_now() and it will return True or False on a systemwide
                    # basis.
                    conn.execute(zones_currently_running.update().values({zones_currently_running.c.currently_running: False}))
                    conn.execute(zones_currently_running.update().values({zones_currently_running.c.run_manually: False}))
                    conn.execute(zones_currently_running.update().values({zones_currently_running.c.run_by_job: False}))
                    conn.execute(zones_currently_running.update().values({zones_currently_running.c.job_id: 0}))
                    mcp.digitalWrite(self.gpio, 0)
                log.debug(f'Zone {self.zone_number} ({self.zone_name}) is now STOPPED.')
            else:
                log.debug(f'Zone {self.zone_number} ({self.zone_name}) is not currently running.')
        else:
            log.debug(f'ERROR: Zone {self.zone_number} ({self.zone_name}) is DISABLED. Please enable it first.')

    def enable(self):
        with engine.begin() as conn:
            enabled = (conn.execute(select([hydroponic_zones.c.enabled]).where(hydroponic_zones.c.zone_name == self.zone_name))).scalar()
        if enabled:
            log.debug(f'Zone {self.zone_number} ({self.zone_name}) is already enabled.')
        else:
            self.enabled = True
            with engine.begin() as conn:
                conn.execute(hydroponic_zones.update().where(hydroponic_zones.c.zone_name == self.zone_name).values({hydroponic_zones.c.enabled: True}))
            log.debug(f'Zone {self.zone_number} ({self.zone_name}) has been enabled.')

    def disable(self):
        with engine.begin() as conn:
            enabled = (conn.execute(select([hydroponic_zones.c.enabled]).where(hydroponic_zones.c.zone_name == self.zone_name))).scalar()
        if enabled:
            with engine.begin() as conn:
                running = (conn.execute(select([hydroponic_zones.c.running]).where(hydroponic_zones.c.zone_name == self.zone_name))).scalar()
            if running:
                log.debug(f'Zone {self.zone_number} ({self.zone_name}) is currently running.')
                log.debug(f'Shutting off Zone {self.zone_number} ({self.zone_name}) before disabling.')
                self.stop()
            self.enabled = False
            with engine.begin() as conn:
                conn.execute(hydroponic_zones.update().where(hydroponic_zones.c.zone_name == self.zone_name).values({hydroponic_zones.c.enabled: False}))
            log.debug(f'Zone {self.zone_number} ({self.zone_name}) has been disbled.')
        else:
            log.debug(f'Zone {self.zone_number} ({self.zone_name}) is already disabled.')

    def notification_toggle(self, notification):
        with engine.begin() as conn:
            if getattr(self, notification):
                conn.execute(hydroponic_zones.update().where(hydroponic_zones.c.zone_name == self.zone_name).values({notification: False}))
                setattr(self, notification, False)
                log.debug(f'System Notifications: ({notification}) for Zone {self.zone_number} ({self.zone_name}) Disabled.')
            else:
                conn.execute(hydroponic_zones.update().where(hydroponic_zones.c.zone_name == self.zone_name).values({notification: True}))
                setattr(self, notification, True)
                log.debug(f'System Notifications: ({notification}) for Zone {self.zone_number} ({self.zone_name}) Enabled.')


def main():
    print("Not intended to be run directly.")
    print("This is the systemwide ZoneController module.")
    print("It is called by other modules.")
    exit()


if __name__ == '__main__':
    main()