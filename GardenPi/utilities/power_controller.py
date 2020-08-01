#!/usr/bin/python3

# -*- coding: utf-8 -*-

"""
power_controller.py for usage with neptune/GardenPi V1.0.0
Manages all of our power zones.
"""

VERSION = "V1.0.0 (2020-07-31)"



import sys
sys.path.append('/var/www/gardenpi_control/gardenpi')
from sqlalchemy import update, select, and_, create_engine
import system_info
from tables import power, power_scheduled_jobs, power_currently_running
from system_logging import setup_logging
from system_logging import read_logging_config
import logging
import wiringpi as mcp
mcp.wiringPiSetup()                    # initialise wiringpi
mcp.mcp23017Setup(96,0x25) #MCP2 GPIOs 96-111

# Instantiate SQAlchemy Database Engine
engine = create_engine(system_info.sqlalchemy_db_uri, pool_recycle=3600)

#Setup Module level logging here. Main logging config in system_logging.py
setup_logging()
level = read_logging_config('logging', 'log_level')
level = logging._checkLevel(level)
log = logging.getLogger(__name__)
log.setLevel(level)

class PowerZoneSchedule:
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
    def config_powerzoneschedule(cls, zone_name):
        with engine.begin() as conn:
            stmt = select([power_scheduled_jobs]).where(power_scheduled_jobs.c.zone.in_(zone_name))
            return [
                cls(
                    name=row[power_scheduled_jobs.c.zone],
                    job_id=row[power_scheduled_jobs.c.job_id],
                    zone_job=row[power_scheduled_jobs.c.zone_job],
                    job_enabled=row[power_scheduled_jobs.c.job_enabled],
                    job_start_time=row[power_scheduled_jobs.c.job_start_time],
                    job_stop_time=row[power_scheduled_jobs.c.job_stop_time],
                    job_duration=row[power_scheduled_jobs.c.job_duration],
                    job_running=row[power_scheduled_jobs.c.job_running],
                    monday=row[power_scheduled_jobs.c.monday],
                    tuesday=row[power_scheduled_jobs.c.tuesday],
                    wednesday=row[power_scheduled_jobs.c.wednesday],
                    thursday=row[power_scheduled_jobs.c.thursday],
                    friday=row[power_scheduled_jobs.c.friday],
                    saturday=row[power_scheduled_jobs.c.saturday],
                    sunday=row[power_scheduled_jobs.c.sunday],
                    forced_stopped_manually=row[power_scheduled_jobs.c.forced_stop_manually]
                )
                for row in conn.execute(stmt).fetchall()
            ]

    def sa_read_powerzone_schedule_by_zonejob(self, zone_name, zone_job):
        '''
        Uses SQLAlchemy to connect to db and return all jobs by job number.
        '''
        with engine.begin() as conn:
            return (conn.execute(select([power_scheduled_jobs]).where(and_(power_scheduled_jobs.c.zone == (zone_name),
                                                                        power_scheduled_jobs.c.zone_job == (zone_job))))).fetchall()


    def sa_read_powerzone_schedule_by_zonejobday(self, zone_name, zone_job, day):
        '''
        Uses SQLAlchemy to connect to db and return all jobs by job number and day.
        '''
        with engine.begin() as conn:
            results = (conn.execute(select([power_scheduled_jobs]).where(and_(power_scheduled_jobs.c.zone == (zone_name),
                                                                        power_scheduled_jobs.c.zone_job == (zone_job),
                                                                        power_scheduled_jobs.c.job_enabled == (True),
                                                                        getattr(power_scheduled_jobs.c, day) == (True))))).fetchall()
            return (results)

    def sa_read_zone_schedule_by_zone(self, zone_name):
        with engine.begin() as conn:
            results = (conn.execute(select([power_scheduled_jobs]).where(power_scheduled_jobs.c.zone == zone_name))).fetchall()
            return (results)

    def update_day(self, zone_name, zone_job, day_of_week, value):
        with engine.begin() as conn:
            conn.execute(power_scheduled_jobs.update().where(and_(power_scheduled_jobs.c.zone == (zone_name),
                                                            power_scheduled_jobs.c.zone_job == (zone_job))).values({getattr(power_scheduled_jobs.c, day_of_week): value}))

    def update_job_start_time(self, zone_name, zone_job, job_start_time):
        with engine.begin() as conn:
            conn.execute(power_scheduled_jobs.update().where(and_(power_scheduled_jobs.c.zone == (zone_name),
                                                            power_scheduled_jobs.c.zone_job == (zone_job))).values({power_scheduled_jobs.c.job_start_time: job_start_time}))

    def update_job_stop_time(self, zone_name, zone_job, job_stop_time):
        with engine.begin() as conn:
            conn.execute(power_scheduled_jobs.update().where(and_(power_scheduled_jobs.c.zone == (zone_name),
                                                            power_scheduled_jobs.c.zone_job == (zone_job))).values({power_scheduled_jobs.c.job_stop_time: job_stop_time}))

    def toggle_job(self, zone_name, zone_job):
        with engine.begin() as conn:
            job_enabled = (self.sa_read_powerzone_schedule_by_zonejob(zone_name, zone_job)[0][3])
            if job_enabled:
                    conn.execute(power_scheduled_jobs.update().where(and_(power_scheduled_jobs.c.zone == (zone_name),
                                                                    power_scheduled_jobs.c.zone_job == (zone_job))).values({power_scheduled_jobs.c.job_enabled: False}))
            else:
                conn.execute(power_scheduled_jobs.update().where(and_(power_scheduled_jobs.c.zone == (zone_name),
                                                                power_scheduled_jobs.c.zone_job == (zone_job))).values({power_scheduled_jobs.c.job_enabled: True}))

    def update_job_duration(self, zone_name, zone_job, job_duration):
        with engine.begin() as conn:
            conn.execute(power_scheduled_jobs.update().where(and_(power_scheduled_jobs.c.zone == (zone_name),
                                                            power_scheduled_jobs.c.zone_job == (zone_job))).values({power_scheduled_jobs.c.job_duration: job_duration}))


class PowerController:
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
            stmt = select([power]).where(power.c.zone_name.in_(zone_name))
            return [
                cls(
                    name=row[power.c.zone_name],
                    number=row[power.c.zone_number],
                    description=row[power.c.description],
                    gpio=row[power.c.gpio],
                    enabled=row[power.c.enabled],
                    running=row[power.c.running],
                    running_manually=row[power.c.running_manually],
                    mcp=row[power.c.mcp],
                    notifications=row[power.c.notifications],
                    sms=row[power.c.sms],
                    pb=row[power.c.pb],
                    email=row[power.c.email]
                )
                for row in conn.execute(stmt).fetchall()
            ]

    def run_job(self, job_id):
        with engine.begin() as conn:
            enabled = (conn.execute(select([power.c.enabled]).where(power.c.zone_name == self.zone_name))).scalar()
        if enabled:
            with engine.begin() as conn:
                running = (conn.execute(select([power.c.running]).where(power.c.zone_name == self.zone_name))).scalar()
            if running:
                log.debug(f'Zone {self.zone_number} ({self.zone_name}) is already running.')
            else:
                self.running = True
                with engine.begin() as conn:
                    # With this db update we are updating the individual zone db record for the zone that is running.
                    conn.execute(power.update().where(power.c.zone_name == self.zone_name).values({power.c.running: True}))
                    conn.execute(power.update().where(power.c.zone_name == self.zone_name).values({power.c.running_manually: False}))
                    conn.execute(power_scheduled_jobs.update().where(power_scheduled_jobs.c.job_id == job_id).values({power_scheduled_jobs.c.job_running: True}))
                    # With this db update we are updating the system_wide indication that "a" or "any" zone is running.
                    # To access this, call use_database.zones_running_now() and it will return True or False on a systemwide
                    # basis.
                    conn.execute(power_currently_running.update().where(power_currently_running.c.zone_name == self.zone_name).values({power_currently_running.c.currently_running: True}))
                    conn.execute(power_currently_running.update().where(power_currently_running.c.zone_name == self.zone_name).values({power_currently_running.c.run_manually: False}))
                    conn.execute(power_currently_running.update().where(power_currently_running.c.zone_name == self.zone_name).values({power_currently_running.c.run_by_job: True}))
                    conn.execute(power_currently_running.update().where(power_currently_running.c.zone_name == self.zone_name).values({power_currently_running.c.job_id: job_id}))
                    mcp.pinMode(self.gpio, 1)
                    mcp.digitalWrite(self.gpio, 1)
                log.debug(f'Zone {self.zone_number} ({self.zone_name}) is now RUNNING.')
        else:
            log.debug(f'ERROR: Zone {self.zone_number} ({self.zone_name}) is DISABLED. Please enable it first.')

    def run(self):
        with engine.begin() as conn:
            enabled = (conn.execute(select([power.c.enabled]).where(power.c.zone_name == self.zone_name))).scalar()
        if enabled:
            with engine.begin() as conn:
                running = (conn.execute(select([power.c.running]).where(power.c.zone_name == self.zone_name))).scalar()
            if running:
                log.debug(f'Zone {self.zone_number} ({self.zone_name}) is already running.')
            else:
                self.running = True
                with engine.begin() as conn:
                    # With this db update we are updating the individual zone db record for the zone that is running.
                    conn.execute(power.update().where(power.c.zone_name == self.zone_name).values({power.c.running: True}))
                    conn.execute(power.update().where(power.c.zone_name == self.zone_name).values({power.c.running_manually: True}))
                    # With this db update we are updating the system_wide indication that "a" or "any" zone is running.
                    # To access this, call use_database.zones_running_now() and it will return True or False on a systemwide
                    # basis.
                    conn.execute(power_currently_running.update().where(power_currently_running.c.zone_name == self.zone_name).values({power_currently_running.c.currently_running: True}))
                    conn.execute(power_currently_running.update().where(power_currently_running.c.zone_name == self.zone_name).values({power_currently_running.c.run_manually: True}))
                    conn.execute(power_currently_running.update().where(power_currently_running.c.zone_name == self.zone_name).values({power_currently_running.c.run_by_job: False}))
                    conn.execute(power_currently_running.update().where(power_currently_running.c.zone_name == self.zone_name).values({power_currently_running.c.job_id: 0}))
                    mcp.pinMode(self.gpio, 1)
                    mcp.digitalWrite(self.gpio, 1)
                log.debug(f'Zone {self.zone_number} ({self.zone_name}) is now RUNNING.')
        else:
            log.debug(f'ERROR: Zone {self.zone_number} ({self.zone_name}) is DISABLED. Please enable it first.')

    def stop_job(self, job_id, forced):
        with engine.begin() as conn:
            running =  (conn.execute(select([power.c.running]).where(power.c.zone_name == self.zone_name))).scalar()
        if running:
            self.running = power
            with engine.begin() as conn:
                # With this db update we are updating the individual zone db record for the zone that is running.
                conn.execute(power.update().where(power.c.zone_name == self.zone_name).values({power.c.running: False}))
                conn.execute(power.update().where(power.c.zone_name == self.zone_name).values({power.c.running_manually: False}))
                conn.execute(power_scheduled_jobs.update().where(power_scheduled_jobs.c.job_id == job_id).values({power_scheduled_jobs.c.job_running: False}))
                if forced:
                    conn.execute(power_scheduled_jobs.update().where(power_scheduled_jobs.c.job_id == job_id).values({power_scheduled_jobs.c.forced_stop_manually: True}))
                    conn.execute(power_currently_running.update().where(power_currently_running.c.zone_name == self.zone_name).values({power_currently_running.c.force_stopped: True}))
                # With this db update we are updating the system_wide indication that "a" or "any" zone is running.
                # To access this, call use_database.zones_running_now() and it will return True or False on a systemwide
                # basis.
                conn.execute(power_currently_running.update().where(power_currently_running.c.zone_name == self.zone_name).values({power_currently_running.c.currently_running: False}))
                conn.execute(power_currently_running.update().where(power_currently_running.c.zone_name == self.zone_name).values({power_currently_running.c.run_manually: False}))
                conn.execute(power_currently_running.update().where(power_currently_running.c.zone_name == self.zone_name).values({power_currently_running.c.run_by_job: False}))
                conn.execute(power_currently_running.update().where(power_currently_running.c.zone_name == self.zone_name).values({power_currently_running.c.job_id: 0}))
                mcp.digitalWrite(self.gpio, 0)
            log.debug(f'Zone {self.zone_number} ({self.zone_name}) is now STOPPED.')
        else:
            log.debug(f'Zone {self.zone_number} ({self.zone_name}) is not currently running!!.')


    def stop(self):
        with engine.begin() as conn:
            enabled = (conn.execute(select([power.c.enabled]).where(power.c.zone_name == self.zone_name))).scalar()
        if enabled:
            with engine.begin() as conn:
                running = (conn.execute(select([power.c.running]).where(power.c.zone_name == self.zone_name))).scalar()
            if running:
                self.running = False
                with engine.begin() as conn:
                    # With this db update we are updating the individual zone db record for the zone that is running.
                    conn.execute(power.update().where(power.c.zone_name == self.zone_name).values({power.c.running: False}))
                    conn.execute(power.update().where(power.c.zone_name == self.zone_name).values({power.c.running_manually: False}))
                    # With this db update we are updating the system_wide indication that "a" or "any" zone is running.
                    # To access this, call use_database.zones_running_now() and it will return True or False on a systemwide
                    # basis.
                    conn.execute(power_currently_running.update().where(power_currently_running.c.zone_name == self.zone_name).values({power_currently_running.c.currently_running: False}))
                    conn.execute(power_currently_running.update().where(power_currently_running.c.zone_name == self.zone_name).values({power_currently_running.c.run_manually: False}))
                    conn.execute(power_currently_running.update().where(power_currently_running.c.zone_name == self.zone_name).values({power_currently_running.c.run_by_job: False}))
                    conn.execute(power_currently_running.update().where(power_currently_running.c.zone_name == self.zone_name).values({power_currently_running.c.job_id: 0}))
                    mcp.digitalWrite(self.gpio, 0)
                log.debug(f'Zone {self.zone_number} ({self.zone_name}) is now STOPPED.')
            else:
                log.debug(f'Zone {self.zone_number} ({self.zone_name}) is not currently running.')
        else:
            log.debug(f'ERROR: Zone {self.zone_number} ({self.zone_name}) is DISABLED. Please enable it first.')

    def enable(self):
        with engine.begin() as conn:
            enabled = (conn.execute(select([power.c.enabled]).where(power.c.zone_name == self.zone_name))).scalar()
        if enabled:
            log.debug(f'Zone {self.zone_number} ({self.zone_name}) is already enabled.')
        else:
            self.enabled = True
            with engine.begin() as conn:
                conn.execute(power.update().where(power.c.zone_name == self.zone_name).values({power.c.enabled: True}))
            log.debug(f'Zone {self.zone_number} ({self.zone_name}) has been enabled.')

    def disable(self):
        with engine.begin() as conn:
            enabled = (conn.execute(select([power.c.enabled]).where(power.c.zone_name == self.zone_name))).scalar()
        if enabled:
            with engine.begin() as conn:
                running = (conn.execute(select([power.c.running]).where(power.c.zone_name == self.zone_name))).scalar()
            if running:
                log.debug(f'Zone {self.zone_number} ({self.zone_name}) is currently running.')
                log.debug(f'Shutting off Zone {self.zone_number} ({self.zone_name}) before disabling.')
                self.stop()
            self.enabled = False
            with engine.begin() as conn:
                conn.execute(power.update().where(power.c.zone_name == self.zone_name).values({power.c.enabled: False}))
            log.debug(f'Zone {self.zone_number} ({self.zone_name}) has been disbled.')
        else:
            log.debug(f'Zone {self.zone_number} ({self.zone_name}) is already disabled.')

    def notification_toggle(self, notification):
        with engine.begin() as conn:
            if getattr(self, notification):
                conn.execute(power.update().where(power.c.zone_name == self.zone_name).values({notification: False}))
                setattr(self, notification, False)
                log.debug(f'System Notifications: ({notification}) for Zone {self.zone_number} ({self.zone_name}) Disabled.')
            else:
                conn.execute(power.update().where(power.c.zone_name == self.zone_name).values({notification: True}))
                setattr(self, notification, True)
                log.debug(f'System Notifications: ({notification}) for Zone {self.zone_number} ({self.zone_name}) Enabled.')

def main():
    print("Not intended to be run directly.")
    print("This is the systemwide PowerController module.")
    print("It is called by other modules.")
    exit()


if __name__ == '__main__':
    main()