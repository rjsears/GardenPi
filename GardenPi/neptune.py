#!/usr/bin/python3

# -*- coding: utf-8 -*-

"""
Neptune - Roman god of the Sea
This is our water and irrigation control system for our
garden, hydroponics and aquarium.
"""

__author__ = 'Richard J. Sears'
VERSION = "V1.0.0 (2020-08-04)"
# richardjsears@gmail.com

import sys
import subprocess
sys.path.append('/var/www/gardenpi_control/gardenpi/utilities')
sys.path.append('/var/www/gardenpi_control/gardenpi/test')
import time
from datetime import datetime
import system_info
from zone_controller import ZoneController, ZoneSchedule, HydroponicsController
from power_controller import PowerController, PowerZoneSchedule
from serial_controller import SerialController
import sentry_sdk
import use_database
from pushbullet import Pushbullet, errors as pb_errors
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from system_logging import setup_logging
from system_logging import read_logging_config
import logging.config, logging
import requests
import board
import busio
import adafruit_bme280
from ina219 import INA219
import types


## Setup our i2c bus for our sensors
i2c = busio.I2C(board.SCL, board.SDA)


# Error reporting to Sentry.IO
sentry_sdk.init("https://b7fa494cd9484fee8336e03f5b36d3a5@sentry.io/5189894",
                integrations=[SqlalchemyIntegration()])
from sentry_sdk import capture_exception

# Here we setup all of our zones via our zone_controller class.
zones = {zone.zone_name: zone for zone in ZoneController.read_config([n for [n] in use_database.read_all_zone_names()])}
zone_schedule = {schedule.name: schedule for schedule in ZoneSchedule.config_zoneschedule([n for [n] in use_database.read_all_zone_names()])}

# Here we set up our power outlets via our power_controller class.
power = {zone.zone_name: zone for zone in PowerController.read_config([n for [n] in use_database.read_all_power_zone_names()])}
power_zone_schedule = {schedule.name: schedule for schedule in PowerZoneSchedule.config_powerzoneschedule([n for [n] in use_database.read_all_userpower_zone_names()])}

# Here we setup all of our Hydroponic zones via our zone_controller class.
hydroponics = {zone.zone_name: zone for zone in HydroponicsController.read_config([n for [n] in use_database.read_all_hydroponic_zone_names()])}

#Serial Setup for tank volume class
tank = {tank.tank_name: tank for tank in SerialController.read_config([n for [n] in use_database.read_all_water_tank_names()])}

# Define some things that we need
today = datetime.today().strftime('%A').lower()
current_military_time = datetime.now().strftime('%H:%M:%S')

# Setup Module logging. Main logging is configured in system_logging.py
setup_logging()
level = read_logging_config('logging', 'log_level')
level = logging._checkLevel(level)
log = logging.getLogger(__name__)
log.setLevel(level)


def mightyhat_serial_setup():
    """
    This is the setup to our MightyHat (lowpowerlabs.com). You can disable this
    function if you are not using the MightyHat. Remove it here as well as in
    main() below.
    """
    log.debug("mightyhat_serial_setup() - Started")
    #TODO Finish setting up MightyHat message management
    try:
        global ser
        ser = serial.Serial(
            port='/dev/ttyAMA0',
            baudrate=115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1)
    except Exception as error:
        log.warning("EXCEPTION: mightyhat_serial_setup()")
        log.warning(error)
    log.debug("mightyhat_serial_setup() - Completed")

def zone_schedule_by_day(day):
    """Returns a list of all scheduled jobs by zone."""
    return (use_database.sa_read_zone_schedule_by_day(day))

def power_schedule_by_day(day):
    """Returns a list of all scheduled jobs by zone."""
    return (use_database.sa_read_power_schedule_by_day(day))


def get_schedule_by_zone_job(zone_name, zone_job):
    """Returns a list with job information based on zone and job id."""
    if zone_name in ([n for [n] in use_database.read_all_garden_zone_names()]):
        return (zone_schedule[zone_name].sa_read_zone_schedule_by_zonejob(zone_name, zone_job))
    elif zone_name in ([n for [n] in use_database.read_all_power_zone_names()]):
        return (power_zone_schedule[zone_name].sa_read_powerzone_schedule_by_zonejob(zone_name, zone_job))


def zone_enabled(zone_name):
    """Returns True/False (bool) based on if the zone is enabled or disabled. """
    if zone_name in ([n for [n] in use_database.read_all_zone_names()]):
        return zones[zone_name].enabled
    elif zone_name in ([n for [n] in use_database.read_all_power_zone_names()]):
        return power[zone_name].enabled
    elif zone_name in ([n for [n] in use_database.read_all_hydroponic_zone_names()]):
        return hydroponics[zone_name].enabled


def run_zone(zone_name):
    """
    Runs a zone. For water zones, determines the correct water source to use
    and also runs that zone. Also triggers water usage function so we can
    track water utilization by zone.
    """
    log.debug(f'run_zone() called with {zone_name}.')
    notify(zone_name, f'{zone_name} is Running', f'{zone_name} is now Running.')
    if zone_name in ([n for [n] in use_database.read_all_garden_zone_names()]):
        source_selected_this_job = (get_water_source()['source_to_use'])
        use_database.sa_update_job_water_source(source_selected_this_job)
        turn_on_water_source(source_selected_this_job)
        zones[zone_name].run()
        start_job_water_usage(zone_name)
    elif zone_name in ([n for [n] in use_database.read_all_power_zone_names()]):
        power[zone_name].run()
    elif zone_name in ([n for [n] in use_database.read_all_hydroponic_zone_names()]):
        sprinkler_transformer("on")
        hydroponics[zone_name].run()


def stop_zone(zone_name):
    """
    Stops a zone. For water zones, also stops the water source zone.
    Once the zones have been stopped, calls the function to calculate
    how much water was used. You have to be careful for jobs of 1 minute
    or less since it will not calculate properly unless you run this script
    sub-one-minute.
    """
    log.debug(f'stop_zone() called with {zone_name}.')
    notify(zone_name, f'{zone_name} Stopped', f'{zone_name} is now Stopped.')
    if zone_name in ([n for [n] in use_database.read_all_garden_zone_names()]):
        source_selected_this_job = (get_water_source()['job_water_source'])
        zones[zone_name].stop()
        turn_off_water_source(source_selected_this_job)
        time.sleep(2)
        calculate_job_water_usage(zone_name)
    elif zone_name in ([n for [n] in use_database.read_all_power_zone_names()]):
        power[zone_name].stop()
    elif zone_name in ([n for [n] in use_database.read_all_hydroponic_zone_names()]):
        hydroponics[zone_name].stop()
        sprinkler_transformer("off")


def water_pump(action):
    """
    Activates/Deactivates the relay that supplies AC power to the
    old fish water Water Pump.
    """
    log.debug(f'water_pump() called with {action}.')
    if action == "on":
        power[system_info.water_pump].run()
    else:
        power[system_info.water_pump].stop()


def sprinkler_transformer(action):
    """
    Activates/Deactivates the relay that supplies AC power to the
    sprinkler transformer.
    """
    log.debug(f'sprinkler_transformere() called with {action}.')
    if action == "on":
        power[system_info.water_transformer].run()
    else:
        power[system_info.water_transformer].stop()


def turn_on_water_source(zone_name):
    """Turns on selected water source."""
    log.debug(f'turn_on_water_source() called with {zone_name}.')
    if zone_name == "fish_water":
        water_pump("on")
    sprinkler_transformer("on")
    zones[zone_name].run()
    start_job_water_usage(zone_name)


def turn_off_water_source(zone_name):
    """Turns off selected water source."""
    zones[zone_name].stop()
    sprinkler_transformer("off")
    calculate_job_water_usage(zone_name)
    if zone_name == "fish_water":
        water_pump("off")


def run_job(zone_name, job_id):
    """
    Runs a specific job. Selects correct water source and makes necessary
    calls to activate water pump and/or 24V AC-AC transformer as needed.
    """
    notify(zone_name, f'{zone_name} job is Running', f'{zone_name} Job {job_id} is Running.')
    if zone_name in ([n for [n] in use_database.read_all_garden_zone_names()]):
        source_selected_this_job = (get_water_source()['source_to_use'])
        use_database.sa_update_job_water_source(source_selected_this_job)
        turn_on_water_source(source_selected_this_job)
        zones[zone_name].run_job(job_id)
        start_job_water_usage(zone_name)
    elif zone_name in ([n for [n] in use_database.read_all_power_zone_names()]):
        power[zone_name].run_job(job_id)


def stop_job(zone_name, job_id, forced):
    """
    Stops a running job. If the 'forced' bit is set by manual user input, prevents
    the job from restarting until 'forced' has been reset which happens at 1:00 am.
    """
    if forced:
        notify(zone_name, f'{zone_name} job FORCE Stopped', f'{zone_name} Job {job_id} has FORCE Stopped.')
    else:
        notify(zone_name, f'{zone_name} job Stopped', f'{zone_name} Job {job_id} has Stopped.')
    if zone_name in ([n for [n] in use_database.read_all_garden_zone_names()]):
        source_selected_this_job = (get_water_source()['job_water_source'])
        zones[zone_name].stop_job(job_id, forced)
        turn_off_water_source(source_selected_this_job)
        time.sleep(2)
        calculate_job_water_usage(zone_name)
    elif zone_name in ([n for [n] in use_database.read_all_power_zone_names()]):
        power[zone_name].stop_job(job_id, forced)


#TODO when zone disabled, check to see if it is running before doing anything
def disable_zone(zone_name):
    """
    Disable a power or water zone. This will prevent any jobs on that zone
    (manually or otherwise) from running until zone is reenabled.
    """
    notify(zone_name, f'{zone_name} Disabled', f'{zone_name} has been Disabled.')
    if zone_name in ([n for [n] in use_database.read_all_zone_names()]):
        zones[zone_name].disable()
    elif zone_name in ([n for [n] in use_database.read_all_power_zone_names()]):
        power[zone_name].disable()
    elif zone_name in ([n for [n] in use_database.read_all_hydroponic_zone_names()]):
        hydroponics[zone_name].disable()


def enable_zone(zone_name):
    """Enable a disabled zone."""
    notify(zone_name, f'{zone_name} Enabled', f'{zone_name} has been Enabled.')
    if zone_name in ([n for [n] in use_database.read_all_zone_names()]):
        zones[zone_name].enable()
    elif zone_name in ([n for [n] in use_database.read_all_power_zone_names()]):
        power[zone_name].enable()
    elif zone_name in ([n for [n] in use_database.read_all_hydroponic_zone_names()]):
        hydroponics[zone_name].enable()


def job_enabled(zone_name, zone_job):
    """Determines if a specific job is enabled."""
    return get_schedule_by_zone_job(zone_name, zone_job)[0][3]


def toggle_job(zone_name, job):
    """Utilized by a Flask to enable or disable a scheduled zone/power job."""
    if zone_name in ([n for [n] in use_database.read_all_garden_zone_names()]):
        zone_schedule[zone_name].toggle_job(zone_name, job)
    elif zone_name in ([n for [n] in use_database.read_all_power_zone_names()]):
        power_zone_schedule[zone_name].toggle_job(zone_name, job)


def update_day(zone_name, zone_job, day_of_week, value):
    """Utilized by Flask to modify job schedules."""
    if zone_name in ([n for [n] in use_database.read_all_garden_zone_names()]):
        zone_schedule[zone_name].update_day(zone_name, zone_job, day_of_week, value)
    elif zone_name in ([n for [n] in use_database.read_all_power_zone_names()]):
        power_zone_schedule[zone_name].update_day(zone_name, zone_job, day_of_week, value)


def update_job_start_time(zone_name, zone_job, job_start_time):
    """Utilized by Flask to modify job schedules."""
    if zone_name in ([n for [n] in use_database.read_all_garden_zone_names()]):
        zone_schedule[zone_name].update_job_start_time(zone_name, zone_job, job_start_time)
    elif zone_name in ([n for [n] in use_database.read_all_power_zone_names()]):
        power_zone_schedule[zone_name].update_job_start_time(zone_name, zone_job, job_start_time)


def update_job_stop_time(zone_name, zone_job, job_stop_time):
    """Utilized by Flask to modify job schedules."""
    if zone_name in ([n for [n] in use_database.read_all_garden_zone_names()]):
        zone_schedule[zone_name].update_job_stop_time(zone_name, zone_job, job_stop_time)
    elif zone_name in ([n for [n] in use_database.read_all_power_zone_names()]):
        power_zone_schedule[zone_name].update_job_stop_time(zone_name, zone_job, job_stop_time)


def update_job_duration(zone_name, zone_job, job_duration):
    """Utilized by Flask to modify job schedules."""
    if zone_name in ([n for [n] in use_database.read_all_garden_zone_names()]):
        zone_schedule[zone_name].update_job_duration(zone_name, zone_job, job_duration)
    elif zone_name in ([n for [n] in use_database.read_all_power_zone_names()]):
        power_zone_schedule[zone_name].update_job_duration(zone_name, zone_job, job_duration)


def get_water_source():
    """
    This function looks at various things to determine which water source
    (fish or fresh) should be utilized when watering. It looks to see if
    fish is enabled AND if there is fish water (tank_water_level_monitor.py).
    If water source set to automatic and fish is enabled and available, it will
    always choose fish over fresh.
    """
    log.debug('get_water_source() called')
    water_source_data = use_database.sa_read_water_source()
    selected_source = water_source_data[0][0]
    fish_available = water_source_data[0][1]
    job_water_source = water_source_data[0][2]
    fresh_enabled = zone_enabled('fresh_water')
    fish_enabled = zone_enabled('fish_water')
    source_to_use = _source_to_use()
    return {'selected_source': selected_source, 'fresh_enabled': fresh_enabled,
            'fish_enabled': fish_enabled, 'fish_available':fish_available,
            'source_to_use':source_to_use, 'job_water_source': job_water_source}


#https://refactoring.guru/replace-nested-conditional-with-guard-clauses
def _source_to_use():
    """
    Works with get_water_source() to determine which source to utilize.
    This basically allows me to toggle through available sources via
    Flask.
    """
    log.debug('_source_to_use() called')
    water_source_data = use_database.sa_read_water_source()
    selected_source = water_source_data[0][0]
    fish_available = water_source_data[0][1]
    fresh_enabled = zone_enabled('fresh_water')
    fish_enabled = zone_enabled('fish_water')
    if (
        selected_source in {"automatic_water", "fish_water"}
        and fish_available
        and fish_enabled
    ):
        return "fish_water"
    if (
            selected_source in {"automatic_water", "fresh_water"}
            and fresh_enabled
    ):
            return "fresh_water"
    return "system_disabled"


def toggle_water_source():
    """
    Utilized by Flask to toggle through available water sources. Also uses get_water_source()
    to determine which source(s) are available. The mapping allows us to toggle our water
    source via web interface as opposed to a drop down. If the current source is 'fish_water'
    then the next source toggled would be 'automatic_water' and so forth.
    """
    sources = types.MappingProxyType(
        {
            "fish_water": "automatic_water",
            "fresh_water": "fish_water",
            "automatic_water": "fresh_water",
        }
    )
    use_database.sa_update_water_source(sources[get_water_source()["selected_source"]])


def switch_from_fish_source():
    """
    If we run out of fish water we need to switch water sources.
    This is called from tank_water_level_monitor.py which monitors
    a non-contact level sensor and when it determines that our old
    fish tank water tank is empty switches back over to fresh water.
    """
    source_selected_this_job = (get_water_source()['job_water_source'])
    if (
            any_zones_running('water')
            and source_selected_this_job == 'fish_water'
    ):
        use_database.sa_update_is_fish_water_available(False)
        turn_off_water_source('fish_water')
        source_selected_this_job = 'fresh_water'
        use_database.sa_update_job_water_source(source_selected_this_job)
        turn_on_water_source(source_selected_this_job)


def toggle_fish_available(available):
    """
    Used by tank_water_level_monitor.py to toggle availability of
    used fish tank water.
    """
    use_database.sa_update_is_fish_water_available(available)


# Stop all zones
def stop_all():
    """Immediately stops all zones systemwide (Garden, Power & Hydro)."""
    for zone_name in ([n for [n] in use_database.read_all_zone_names()]):
        zones[zone_name].stop()
    for zone_name in ([n for [n] in use_database.read_all_power_zone_names()]):
        power[zone_name].stop()
    for zone_name in ([n for [n] in use_database.read_all_hydroponic_zone_names()]):
        hydroponics[zone_name].stop()


def any_zones_running(type):
    """
    Returns True/False if any zones are running (power or water). Specifically does not
    return "parasitic" zones, those zones required as a result of something else. In this
    case this is power8 (sprinkler transformer), intake fan or exhaust fan.
    This is utilized in our Flask GUI to show if any zones are running and make changes based
    on that information.
    """
    return (use_database.are_any_zones_running_now(type))


def what_zone_is_running_now(type):
    """
    Returns the name of any zones which are running (power or water). Specifically does not
    return "parasitic" zones, those zones required as a result of something else. In this
    case this is power8 (sprinkler transformer), intake fan or exhaust fan, and 'fresh and fish'
    water zones.

    This is utilized in our Flask GUI to show if any zones are running and make changes based
    on that information.
    """
    return (use_database.what_zone_is_running_now(type))


def is_this_zone_running(zone_name):
    """Used by Flask to determine is a 'specific' zone is running rather than 'any' zone."""
    return (use_database.zone_running(zone_name))


def is_this_zone_running_manually(zone_name):
    """Used by Flask to determine if a specific zone has been started manually."""
    return (use_database.zone_running_manually(zone_name))


def run_zone_test(zone_name):
    """
    Test a single zone. If the zone is disabled, enable it and run the test.
    Then disable it once the test has been completed. This WILL activate the
    zone in question! For testing only, not used in production, hence the
    print() statement.
    """
    try:
        if zones[zone_name].enabled:
            zones[zone_name].run()
            time.sleep(5)
            zones[zone_name].stop()
        else:
            print(f'Zone {zone_name} is DISABLED. Enabling for test.')
            zones[zone_name].enable()
            zones[zone_name].run()
            time.sleep(5)
            zones[zone_name].stop()
            zones[zone_name].disable()
    except Exception as e:
        capture_exception(e)

#TODO Expand this and run_zone_test() to test all zones including power, water and hydroponic.
def run_all_zones_test():
    """
    Test all garden water zones including fresh and fish utilizing run_zone_test().
    """
    try:
        for zone_name in ([n for [n] in use_database.read_all_zone_names()]):
            run_zone_test(zone_name)
    except Exception as e:
        capture_exception(e)


def get_gallons_total():
    """
    The gallon tracking utilizing a separate system that I have in place (EmonCMS) that reads
    smart water meters that I have installed on my home. If you do not have any smart
    water meters this function will not be usable.
    """
    if system_info.water_monitoring:
        get_gallons_total = use_database.read_emoncms_database("data", system_info.irrigation_gallons_total)
        return int("%1.0f" % get_gallons_total)
    else:
        return 0


def get_current_gpm():
    """
    Utilizes an Emoncms system that I have in place that reads smart water meters that
    I have installed on my home and returns current Gallons Per Minute of water utilization.
    """
    if system_info.water_monitoring:
        return (use_database.read_emoncms_database("data", system_info.current_gpm))
    else:
        return 0


def calculate_current_run_gallons(zone_name):
    """
    Utilizing smart water meters installed on my house calculates how many gallons have
    been used by a zone at this moment in time.
    """
    if system_info.water_monitoring:
        run_gallons_start = get_gallons_total()
        run_gallons_stop = use_database.water_usage(zone_name, 'read_gallons_stop', 0)
        gallons_current_run = int(run_gallons_start) - int(run_gallons_stop)
        use_database.water_usage(zone_name, 'update_gallons_current_run', gallons_current_run)
        return gallons_current_run
    else:
        return 0


def calculate_gallons_used(zone_name):
    """
    Utilizing smart water meters I have installed on my house, calculates total gallons
    of water used each time it is called.
    """
    if system_info.water_monitoring:
        gallons_start = use_database.water_usage(zone_name, 'read_gallons_start', 0)
        gallons_stop = use_database.water_usage(zone_name, 'read_gallons_stop', 0)
        gallons_used = int(gallons_stop) - int(gallons_start)
        use_database.water_usage(zone_name, 'update_gallons_last_run', gallons_used)
    else:
        pass


def start_job_water_usage(zone_name):
    """ Make *sure* we start with zero gallons used. Only used once when we start a zone."""
    if system_info.water_monitoring:
        use_database.water_usage(zone_name, 'update_gallons_stop', get_gallons_total())
        use_database.water_usage(zone_name, 'update_gallons_start', get_gallons_total())
    else:
        pass


def calculate_job_water_usage(zone_name):
    """
    Function to calculate total water used for a zone or job. Must be utilizing some type of
    water monitoring.
    """
    if system_info.water_monitoring:
        run_gallons_stop = get_gallons_total()
        use_database.water_usage(zone_name, 'update_gallons_stop', run_gallons_stop)
        calculate_gallons_used(zone_name)
        use_database.water_usage(zone_name, 'update_gallons_current_run', 0)
        current_total_gallons_used = use_database.water_usage(zone_name, 'read_total_gallons_used', 0)
        gallons_last_run = use_database.water_usage(zone_name, 'read_gallons_last_run', 0)
        new_total_gallons_used = (current_total_gallons_used + gallons_last_run)
        use_database.water_usage(zone_name, 'update_total_gallons_used', new_total_gallons_used)
    else:
        pass


def update_water_stats():
    """Updates the water stats on running zone."""
    log.debug('update_water_stats() called')
    if system_info.water_monitoring:
        if any_zones_running('water'):
            zone_name = what_zone_is_running_now('water')
            current_fill_gallons = calculate_current_run_gallons(zone_name)
            log.info(f'Total {zone_name} Gallons this run: {current_fill_gallons}')
            log.debug(f'Total {zone_name} Gallons this run: {current_fill_gallons}')
        else:
            pass
    else:
        pass


def get_allzone_water_stats():
    """Function used by Flask to build water stats page in GUI."""
    zone_data = use_database.read_all_zone_info()
    zone_water_info = {}
    for zone in zone_data:
        zone_name = zone[0]
        zone_total_gallons = zone[11]
        if system_info.water_monitoring:
            zone_water_info.update({zone_name : zone_total_gallons})
        else:
            zone_water_info.update({zone_name: 0})
    return zone_water_info


def reset_forced_stopped_jobs():
    """
    If you force stop a job for some reason the job will not restart unless we reset it here.
    If you force stop and DO NOT want the job to run again, you much disable the job or the zone.
    """
    log.debug('reset_forced_stopped_jobs() called')
    zones_forced_stopped = use_database.forced_stopped_jobs('check', 0)
    if zones_forced_stopped:
        if current_military_time > '01:00:00' and current_military_time < '01:01:00':
            for jobs in use_database.forced_stopped_jobs('readall', 0):
                job_id = jobs[0]
                use_database.forced_stopped_jobs('update', job_id)
                use_database.forced_stopped_jobs('reset', 0)


#TODO Work on stop_all() function to make sure it updates all water info if/when called.
#TODO Rewrite to not bother to check if sprinklers are running if we are using fish_water.
def can_we_run():
    """
    This function looks to make sure the system has not been disabled (ie - not fresh or
    fish water available or enabled) and also checks to see if our sprinklers are running.
    In my case, I cannot run my sprinklers AND run utilizing 'fresh_water' as a source.
    :return:
    """
    log.debug('can_we_run() called')
    if (get_water_source()['source_to_use']) == 'system_disabled':
        log.debug('System has been disabled. Not able to run any zones or jobs.')
        return False
    else:
        log.debug('System Enabled.')
    sprinklers_running = get_sprinkler_status()
    if sprinklers_running:
        if any_zones_running('water'):
            stop_all()
            log.debug('Sprinklers detected running while zone or job running. All zones stopped.')
        log.debug('Sprinklers are running. Not able to run any zones or jobs.')
        return False
    else:
        log.debug('Sprinklers are not running.')
    return True


#TODO fix this so that we only check for disable if we are NOT currently running a job!!!
#TODO verify this works with sprinkler status, also need to add in pool fill status.
#TODO If system becomes disabled during a zone run, stop all zones.
def run_zone_scheduled_jobs():
    """
    This function checks to see what scheduled jobs ready to be run based on the time-of-day
    and stop the job after the correct amount of time.
    """
    log.debug('run_zone_scheduled_jobs() called')
    if can_we_run():
        jobs_today = zone_schedule_by_day(today)
        for job in jobs_today:
            zone_name = job[1]
            job_id = job[0]
            job_by_id_is_running = job[7]
            job_forced_stop_manually = job[15]
            job_start_time = job[4].strftime('%H:%M:%S')
            job_stop_time = job[5].strftime('%H:%M:%S')
            if (job_start_time <= current_military_time < job_stop_time
                and not job_by_id_is_running
                and not job_forced_stop_manually):
                log.debug(f'Zone: {zone_name}, Job ID: {job_id}: Starting')
                run_job(zone_name, job_id)
                return
            if (zones[zone_name].running and current_military_time > job_stop_time and job_by_id_is_running):
                log.debug(f'Zone: {zone_name}, Job ID: {job_id}: Stopped')
                stop_job(zone_name, job_id, False)
                check_gpm_now(zone_name, job_id)
                return
        log.debug('No scheduled zone jobs to start or stop.')


def check_gpm_now(zone_name, job_id):
    """
    Function that utilizes our smart water meters and EmonCMS to check and make sure our water valves close
    properly once a job has completed. The sleep time of 30 seconds should give EmonCMS enough time to update
    the necessary GPM database before we actually check it. However it is possible to get a false negative
    in the even the database has not been updated within that 30 seconds.
    """
    log.debug('check_gpm_now() called')
    if system_info.check_gpm:
        time.sleep(30)
        gpm_now = get_current_gpm()
        log.debug(f'Current GPM after Zone: {zone_name}, Job ID: {job_id} STOPPED is: {gpm_now}')
        if gpm_now > 0:
            notify(zone_name, 'Possible Water Valve Malfunction', f'GPM is currently {gpm_now}gpm and it should be 0. Please check your valves.')


def run_power_scheduled_jobs():
    """
    This function checks to see what scheduled jobs ready to be run based on the time-of-day
    and stop the job after the correct amount of time. This is for our power zones.
    """
    log.debug('run_power_scheduled_jobs() called')
    jobs_today = power_schedule_by_day(today)
    for job in jobs_today:
        zone_name = job[1]
        job_id = job[0]
        job_by_id_is_running = job[7]
        job_forced_stop_manually = job[15]
        job_start_time = job[4].strftime('%H:%M:%S')
        job_stop_time = job[5].strftime('%H:%M:%S')
        if (job_start_time <= current_military_time < job_stop_time
            and not job_by_id_is_running
            and not job_forced_stop_manually):
            log.info(f'Power Zone: {zone_name}, Job ID: {job_id}: Starting')
            run_job(zone_name, job_id)
            return
        if (power[zone_name].running and current_military_time > job_stop_time and job_by_id_is_running):
            log.info(f'Power Zone: {zone_name}, Job ID: {job_id}: Stopped')
            stop_job(zone_name, job_id, False)
            return
    log.debug('No scheduled power jobs to start or stop.')

def check_zone_scheduled_jobs(day):
    """
    Simple function to verify schedule based on day passed to function.
    This will only show jobs that will actually run based on if the zone is enabled.
    """
    log.debug('check_zone_scheduled_jobs() Started.')
    jobs_today = zone_schedule_by_day(day)
    for job in jobs_today:
        zone_name = job[1]
        job_id = job[0]
        job_by_id_is_running = job[7]
        job_forced_stop_manually = job[15]
        job_start_time = job[4].strftime('%H:%M:%S')
        job_stop_time = job[5].strftime('%H:%M:%S')
        print(zone_name)
        print(job_id)
        print(job_by_id_is_running)
        print(job_forced_stop_manually)
        print(job_start_time)
        print(job_stop_time)

def check_power_scheduled_jobs(day):
    """
    Simple function to verify schedule based on day passed to function.
    This will only show jobs that will actually run based on if the zone is enabled.
    """
    log.debug('check_power_scheduled_jobs() Started.')
    jobs_today = power_schedule_by_day(day)
    for job in jobs_today:
        zone_name = job[1]
        job_id = job[0]
        job_by_id_is_running = job[7]
        job_forced_stop_manually = job[15]
        job_start_time = job[4].strftime('%H:%M:%S')
        job_stop_time = job[5].strftime('%H:%M:%S')
        print(zone_name)
        print(job_id)
        print(job_by_id_is_running)
        print(job_forced_stop_manually)
        print(job_start_time)
        print(job_stop_time)

def get_sprinkler_status():
    """
    This function determines if your sprinklers are running. It can be as simple
    as a "timer" mode, or in my case, utilizing the Rachio so I can query it
    directly to see if it is running.
    """
    log.debug("get_sprinkler_status() Started.")
    """ Function to determine if our sprinklers are currently running. """
    if system_info.sprinkler_type == 'Timer':
        log.debug('get_sprinkler_status() called via \'Timer\'')
        if system_info.sprinklerstart < current_military_time < system_info.sprinklerstop:
            return True
        else:
            return False
    else:
        log.debug("get_sprinkler_status() called via requests() (Rachio)")
        r = requests.get(system_info.rachio_url, headers=system_info.rachio_headers)
        if r.content == b'{}':
            return False
        else:
            return True


def get_enclosure_environmentals():
    """
    This function utilizes the I2C bus to read the  BME280 temp/humidity/pressure sensor
    installed in our system enclosure. We then utilize this information to turn on or off
    our system fans based on the temperature. We also store this information in our
    database and it is then used in our GUI.
    """
    log.debug('get_enclosure_environmentals() called')
    try:
        bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)  # Setup our BME280 environmental monitor
        enclosure_tempF=(bme280.temperature *9/5 + 32)  # Let's convert these to US readings
        pressure_in_inches = (bme280.pressure * 0.02953)
        log.debug(f'Enclosure Temperature: {enclosure_tempF:.1f} °F')
        log.debug(f'Enclosure Humidity: {bme280.humidity:.1f} %')
        log.debug(f'Enclosure Pressure: {bme280.pressure:.1f} hPa')
        log.debug(f'Enclosure Pressure: {pressure_in_inches:.2f} inHg')
        use_database.environmentals_data('update', 'enclosure_temp', enclosure_tempF)
        use_database.environmentals_data('update', 'enclosure_humidity', bme280.humidity)
        use_database.environmentals_data('update', 'enclosure_baro', pressure_in_inches)
        use_database.environmentals_data('update', 'pi_cpu_temp', get_pi_cpu_temp())
    except Exception as e:
        log.debug(f'get_enclosure_environmentals(): Unknown Error!')
        capture_exception(e)



def get_shed_environmentals():
    """
    We have our system installed in our garden shed. Utilizing an existing Home automation and
    tracking platform called EmonCMS, I read our shed information for use in our GUI. It is marked
    garage here as I swiped my garage sensor and put it in the shed. Also grabs out "outdoor" temp
    provided by by our Vantage Pro2.
    """
    log.debug('get_shed_environmentals() called')
    use_database.environmentals_data('update', 'shed_temp', use_database.read_influx_database_temps("'garage'")) #says garage but that is old sensor name now in the shed.
    use_database.environmentals_data('update', 'shed_humidity', use_database.read_influx_database_temps("'garage_humidity'"))
    use_database.environmentals_data('update', 'outdoor_temperature', use_database.read_influx_database_temps("'outside'")) #outdoor temp


def get_gardenpi_power():
    """
    Utilizes I2C bus to read DC watt meter (voltage, current, power and shunt voltage) via
    a DFRobot digital DC Watt Meter. Utilizing a 'whole house' electrical monitoring system, we
    also read AC current and voltage on the circuit dedicated to the system enclosure.
    """
    log.debug('get_gardenpi_power() called')
    SHUNT_OHMS = 0.01
    MAX_EXPECTED_AMPS = 4.0
    ina = INA219(SHUNT_OHMS, MAX_EXPECTED_AMPS)
    ina.configure(ina.RANGE_16V, ina.GAIN_1_40MV)
    log.debug("Bus Voltage: %.3f V" % ina.voltage())
    log.debug("Bus Current: %.3f mA" % ina.current())
    log.debug("Power: %.3f mW" % ina.power())
    log.debug("Shunt voltage: %.3f mV" % ina.shunt_voltage())
    use_database.electrical_data('update', 'dc_voltage', ina.voltage())
    use_database.electrical_data('update', 'dc_current', (ina.current()/1000))
    use_database.electrical_data('update', 'dc_power', (ina.power()/1000))
    use_database.electrical_data('update', 'dc_shunt_voltage', ina.shunt_voltage())
    use_database.electrical_data('update', 'ac_current',use_database.read_influx_database_power("energy", system_info.gardenpi_power_circuit_current))
    use_database.electrical_data('update', 'ac_voltage',(use_database.read_influx_database_power("energy", system_info.gardenpi_power_circuit_volts) + 2.0)) # Adjustment for low reading on transformer


def read_temp_raw(onewire_id):
    """Function to read raw temp from one_wire DS18B20 temp probes."""
    onewire_probe_address = ('/sys/bus/w1/devices/' + onewire_id + '/w1_slave')
    f = open(onewire_probe_address, 'r')
    lines = f.readlines()
    f.close()
    return lines


def read_temp(onewire_id):
    """Function to convert raw temp from one_wire DS18B20 temp probes from C to F."""
    lines = read_temp_raw(onewire_id)
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw(onewire_id)
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos + 2:]
        temp_f = float(temp_string) / 1000 * 9.0 / 5.0 + 32.0
        return (f'{temp_f:.1f}')


def read_onewire_temp_probes():
    """Function to look in database for a list of onewire probes and then get their temps."""
    log.debug('read_onewire_temp_probes() called')
    temp_zones = (use_database.onewire_temp_probes('get_all_info', 0, 0))
    for zone in temp_zones:
        if zone[3]:
            use_database.onewire_temp_probes('update_temperature', zone[0], read_temp(zone[1]))
            log.debug(f'Temperature: {zone[0]} - {zone[2]}°F')


#TODO Do RODI Functions...not sure if we are actaully going to do something here or handle manually.
def rodi_control(action):
    pass


def is_tank_enabled(tank_name):
    """Function to determine if a specific tank is enabled."""
    return tank[tank_name].enabled


# TODO Finish tank function - update gallons in db and rework routes.py to read this info from db instead of real time.
def get_tank_gallons(tank_name):
    """
    Utilizes serial_controller.py to read gallons based on sizes and other information about each
    tank listed in mysql database. This is informational only, we do not make any decisions based
    on this data but rather on our non-contact liquid sensors. More needs to be added for additional
    tanks. Also see tank_water_level_monitor.py
    """
    try:
        dis_min = 0  # Minimum ranging threshold: 0mm
        dis_max = 4500  # Highest ranging threshold: 4500mm
        tank[tank_name].set_dis_range(dis_min, dis_max)
        tank[tank_name].getDistance() / 25.4
        check_count = 0
        while not tank[tank_name].last_operate_status == tank[tank_name].STA_OK:
            check_count +=1
            time.sleep(.1)
            tank[tank_name].getDistance() / 25.4
            if check_count == 5:
                # log/Do something here #TODO DO I need to raise an exception here...?
                return
            print(check_count)
        tank[tank_name].set_dis_range(dis_min, dis_max)
        check_distance = (tank[tank_name].getDistance() / 25.4)
        distance = int(check_distance)
        if distance >= tank[tank_name].tank_empty_depth:
            tank_level = 0
        else:
            tank_level = int(abs((distance * tank[tank_name].gallons_per_inch) - tank[tank_name].max_tank_volume))
        return tank_level
    except Exception as e:
        log.debug(f'get_tank_gallons(): Unknown Error! Tank values not updated.')
        capture_exception(e)


# Function to read and return the temp of our CPU
def get_pi_cpu_temp():
    """Read Pi Temp for GUI display via Flask."""
    log.debug('get_pi_cpu_temp() called')
    while True:
        try:
            tFile = open('/sys/class/thermal/thermal_zone0/temp')
            temp = float(tFile.read())
            tempC = temp / 1000
            pi_cpu_temp_F = (tempC * 9 / 5 + 32)
            return (f'{pi_cpu_temp_F:.1f}')
        except:
            tFile.close()
            capture_exception(e)


def toggle_screen_mode():
    """Function called by Flask to toggle touchscreen between kiosk and desktop modes."""
    if use_database.screen_mode('check_mode'):
        try:
            subprocess.check_call(['sudo', '/usr/bin/gardenpi_desktop.sh', 'desktop'])
            use_database.screen_mode(0)
        except subprocess.CalledProcessError as error:
            log.debug(f'toggle_screen_mode error: {error}')
            capture_exception(error)
    else:
        try:
            subprocess.check_call(['sudo', '/usr/bin/gardenpi_desktop.sh', 'gardenpi'])
            use_database.screen_mode(1)
        except subprocess.CalledProcessError as error:
            log.debug(f'toggle_screen_mode error: {error}')
            capture_exception(error)


def notifications(zone_name, notification, action):
    """Notification functions: Read, toggle, etc."""
    if zone_name == 'systemwide':
        if action == 'enabled':
            return use_database.systemwide_notification('enabled', notification, 0)
        elif action == 'toggle':
            if use_database.systemwide_notification('enabled', notification, 0):
                use_database.systemwide_notification('toggle', notification, False)
            else:
                use_database.systemwide_notification('toggle', notification, True)
        elif action == 'check':
            system_sms = use_database.systemwide_notification('enabled', 'sms', 0)
            system_pb = use_database.systemwide_notification('enabled', 'pb', 0)
            system_email = use_database.systemwide_notification('enabled', 'email', 0)
            return system_sms, system_pb, system_email
    elif use_database.zone_name_in_zones(zone_name):
        if action == 'enabled':
            if notification == 'notifications':
                return (getattr(zones[zone_name], notification))
            else:
                if use_database.systemwide_notification('enabled', notification, 0):
                    return (getattr(zones[zone_name], notification))
                else:
                    return False
        elif action == 'toggle':
            zones[zone_name].notification_toggle(notification)
    elif use_database.zone_name_in_power_zones(zone_name):
        if action == 'enabled':
            if notification == 'notifications':
                return (getattr(power[zone_name], notification))
            else:
                if use_database.systemwide_notification('enabled', notification, 0):
                    return (getattr(power[zone_name], notification))
                else:
                    return False
        elif action == 'toggle':
            power[zone_name].notification_toggle(notification)
    elif use_database.zone_name_in_hydroponic_zones(zone_name):
        if action == 'enabled':
            if notification == 'notifications':
                return (getattr(hydroponics[zone_name], notification))
            else:
                if use_database.systemwide_notification('enabled', notification, 0):
                    return (getattr(hydroponics[zone_name], notification))
                else:
                    return False
        elif action == 'toggle':
            hydroponics[zone_name].notification_toggle(notification)
    elif use_database.zone_name_in_notification_alerts(zone_name):
        if action == 'enabled':
            return use_database.notification_alerts(zone_name, 'enabled', notification, 0)
        elif action == 'toggle':
            use_database.notification_alerts(zone_name, 'toggle', notification, 0)


def send_email(recipient, subject, body):
    """
    Part of our notification system.
    Setup to send email via the builtin linux mail command.
    Your local system **must** be configured already to send mail or this will fail.
    https://stackoverflow.com/questions/27874102/executing-shell-mail-command-using-python
    https://nedbatchelder.com/text/unipain.html
    """
    try:
        subprocess.run(['mail', '-s', subject, recipient], input=body, encoding='utf-8')
        log.debug(f"Email Notification Sent: Subject: {subject}, Recipient: {recipient}, Message: {body}")
    except subprocess.CalledProcessError as e:
        log.debug(f'send_email error: {e}')
        capture_exception(e)
    except Exception as e:
        log.debug(f'send_email: Unknown Error! Email not sent.')
        capture_exception(e)


# Setup to send out Pushbullet alerts. Pushbullet config is in system_info.py
def send_push_notification(title, message):
    """Part of our notification system. This handles sending PushBullets."""
    try:
        pb = Pushbullet(system_info.pushbilletAPI)
        push = pb.push_note(title, message)
        log.debug(f"Pushbullet Notification Sent: {title} - {message}")
    except pb_errors.InvalidKeyError as e:
        log.debug(f'Pushbullet Exception: Invalid API Key! Message not sent.')
        capture_exception(e)
    except Exception as e:
        log.debug(f'Pushbullet Exception: Unknown Pushbullet Error: {e}. Message not sent.')
        capture_exception(e)


def send_sms_notification(body, phone_number):
    """Part of our notification system. This handles sending SMS messages."""
    try:
        client = Client(system_info.twilio_account, system_info.twilio_token)
        message = client.messages.create(to=phone_number, from_=system_info.twilio_from, body=body)
        log.debug(f"SMS Notification Sent: {body}.")
    except TwilioRestException as e:
        log.debug(f'Twilio Exception: {e}. Message not sent.')
        capture_exception(e)
    except Exception as e:
        log.debug(f'Twilio Exception: {e}. Message not sent.')
        capture_exception(e)


def notify(zone_name, title, message):
    """ Notify system for email, pushbullet and sms (via Twilio)"""
    if notifications('systemwide', 'enabled', 'enabled'):   # Are notifications enabled at the system level?
        if notifications(zone_name, 'notifications', 'enabled'):  # Are notifications enabled at the zone level that caused the notification?
            system_sms, system_pb, system_email = notifications('systemwide', 0, 'check') #Specific notiication type must be enabled at the system level and zone level.
            sms = notifications(zone_name, 'sms', 'enabled') and system_sms
            pushbullet = notifications(zone_name, 'pb', 'enabled') and system_pb
            email = notifications(zone_name, 'email', 'enabled') and system_email
            if pushbullet:
                send_push_notification(title, message)
            if email:
                for email_address in system_info.alert_email:
                    send_email(email_address, title, message)
            if sms:
                for phone_number in system_info.twilio_to:
                    send_sms_notification(message, phone_number)
        else:
            pass
    else:
        pass


def reboot_halt_system(action):
    """Function to reboot or halt system, called via Flask."""
    if action == 'reboot':
        log.info('System REBOOT Called via Web Interface.')
        subprocess.check_call(['sudo', 'shutdown', '-r', 'now'])
    elif action == 'halt':
        log.info('System HALT Called via Web Interface.')
        subprocess.check_call(['sudo', 'shutdown', '-h', 'now'])


def enclosure_fan_control():
    """Function to turn on or off our intake/exhaust fans depending on temperature of enclosure."""
    log.debug('enclosure_fan_control() Started.')
    if (use_database.environmentals_data('readone', 'enclosure_temp', 0)) > 80:
        if not is_this_zone_running('intake_fan'):
            run_zone('intake_fan')
            log.debug('intake_fan is now running')
        if not is_this_zone_running('exhaust_fan'):
            run_zone('exhaust_fan')
            log.debug('exhaust_fan is now running')
    else:
        if is_this_zone_running('intake_fan'):
            stop_zone('intake_fan')
            log.debug('intake_fan has been stopped')
        if is_this_zone_running('exhaust_fan'):
            stop_zone('exhaust_fan')
            log.debug('exhaust_fan has stopped')

def get_alert_limit(sensor):
    """ Used by send_system_notifications() to look up alert limits for system notifications."""
    return use_database.notification_alerts(sensor, 'get_alert_limit', 0, 0)

def update_alert_limit(sensor, new_limit):
    """ Used by routes.py to update alert limits vi web."""
    return use_database.notification_alerts(sensor, 'update_alert_limit', 'alert_limit', new_limit)


def send_system_notifications():
    """
    Function to check a series of system sensors and temperatures and send alerts
    based on those settings.
    """
    log.debug('send_system_notifications() called')
    if float(get_pi_cpu_temp()) < get_alert_limit('pi_max_cpu_temp'):
        if use_database.notification_alerts('pi_max_cpu_temp', 'was_alert_sent', 0, 0):
            use_database.notification_alerts('pi_max_cpu_temp', 'set_alert_sent', 0, False)
            log.info("Pi CPU Temp back to Normal")
            notify('pi_max_cpu_temp', 'Pi CPU Temp Normal', 'Your Pi CPU Temperature is back to Normal.')
    else:
        if not use_database.notification_alerts('pi_max_cpu_temp', 'was_alert_sent', 0, 0):
            notify('pi_max_cpu_temp', 'Pi CPU High Temp Alert', f'Your Rpi CPU Temperature is {get_pi_cpu_temp()}!')
            use_database.notification_alerts('pi_max_cpu_temp', 'set_alert_sent', 0, True)
            log.info(f'Your RPI CPU Temperature is Critical at {get_pi_cpu_temp()}!')

    if use_database.onewire_temp_probes('get_current_temp', 'worm_farm', 0) < get_alert_limit('worm_farm_max_temp'):
        if use_database.notification_alerts('worm_farm_max_temp', 'was_alert_sent', 0, 0):
            use_database.notification_alerts('worm_farm_max_temp', 'set_alert_sent', 0, False)
            log.info("Worm Farm Temp back to Normal")
            notify('worm_farm_max_temp', 'Worm Farm Temp Normal', 'Your Worm Farm Temperature is back to Normal.')
    else:
        if not use_database.notification_alerts('worm_farm_max_temp', 'was_alert_sent', 0, 0):
            notify('worm_farm_max_temp', 'Worm Farm High Temp Alert', f'Your Worm Farm Temperature is {use_database.onewire_temp_probes("get_current_temp", "worm_farm", 0)}!')
            use_database.notification_alerts('worm_farm_max_temp', 'set_alert_sent', 0, True)
            log.info(f'Your Worm Farm Temperature is Critical at {use_database.onewire_temp_probes("get_current_temp", "worm_farm", 0)}!')

    if use_database.environmentals_data('readone', 'enclosure_temp', 0) < get_alert_limit('enclosure_max_temp'):
        if use_database.notification_alerts('enclosure_max_temp', 'was_alert_sent', 0, 0):
            use_database.notification_alerts('enclosure_max_temp', 'set_alert_sent', 0, False)
            log.info("System Enclosure Temperature back to Normal")
            notify('enclosure_max_temp', 'System Enclosure Temp Normal', 'Your System Enclosure Temperature is back to Normal.')
    else:
        if not use_database.notification_alerts('enclosure_max_temp', 'was_alert_sent', 0, 0):
            notify('enclosure_max_temp', 'System Enclosure High Temp Alert', f'Your System Enclosure Temperature is {use_database.environmentals_data("readone", "enclosure_temp", 0)}!')
            use_database.notification_alerts('enclosure_max_temp', 'set_alert_sent', 0, True)
            log.info(f'Your System Enclosure Temperature is Critical at {use_database.environmentals_data("readone", "enclosure_temp", 0)}!')

    if use_database.electrical_data('readone', 'ac_current', 0) < get_alert_limit('ac_circuit_max_amps'):
        if use_database.notification_alerts('ac_circuit_max_amps', 'was_alert_sent', 0, 0):
            use_database.notification_alerts('ac_circuit_max_amps', 'set_alert_sent', 0, False)
            log.info("AC Current load is back to Normal")
            notify('ac_circuit_max_amps', 'AC Current Load', 'Your AC Current Load is back to Normal.')
    else:
        if not use_database.notification_alerts('ac_circuit_max_amps', 'was_alert_sent', 0, 0):
            notify('ac_circuit_max_amps', 'AC Current HIGH', f'Your AC Current Load is HIGH at: {use_database.electrical_data("readone", "ac_current", 0)}!')
            use_database.notification_alerts('ac_circuit_max_amps', 'set_alert_sent', 0, True)
            log.info(f'Your AC Current Load is Critical at {use_database.electrical_data("readone", "ac_current", 0)}!')

    if use_database.electrical_data('readone', 'dc_current', 0) < get_alert_limit('dc_max_amps'):
        if use_database.notification_alerts('dc_max_amps', 'was_alert_sent', 0, 0):
            use_database.notification_alerts('dc_max_amps', 'set_alert_sent', 0, False)
            log.info("DC Current load is back to Normal")
            notify('dc_max_amps', 'DC Current Load', 'Your DC Current Load is back to Normal.')
    else:
        if not use_database.notification_alerts('dc_max_amps', 'was_alert_sent', 0, 0):
            notify('dc_max_amps', 'AC Current HIGH', f'Your AC Current Load is HIGH at: {use_database.electrical_data("readone", "dc_current", 0)}!')
            use_database.notification_alerts('dc_max_amps', 'set_alert_sent', 0, True)
            log.info(f'Your DC Current Load is Critical at {use_database.electrical_data("readone", "dc_current", 0)}!')
    
    if use_database.electrical_data('readone', 'ac_voltage', 0) > get_alert_limit('ac_minimum_volts'):
        if use_database.notification_alerts('ac_minimum_volts', 'was_alert_sent', 0, 0):
            use_database.notification_alerts('ac_minimum_volts', 'set_alert_sent', 0, False)
            log.info("AC Circuit Voltage is back to Normal")
            notify('ac_minimum_volts', 'AC Voltage Normal', 'Your AC Voltage is back to Normal.')
    else:
        if not use_database.notification_alerts('ac_minimum_volts', 'was_alert_sent', 0, 0):
            notify('ac_minimum_volts', 'AC Voltage LOW', f'Your AC Voltage is LOW at: {use_database.electrical_data("readone", "ac_voltage", 0)}!')
            use_database.notification_alerts('ac_minimum_volts', 'set_alert_sent', 0, True)
            log.info(f'Your AC Voltage is LOW at {use_database.electrical_data("readone", "ac_voltage", 0)}!')
    
    if use_database.electrical_data('readone', 'dc_voltage', 0) > get_alert_limit('dc_minimum_volts'):
        if use_database.notification_alerts('dc_minimum_volts', 'was_alert_sent', 0, 0):
            use_database.notification_alerts('dc_minimum_volts', 'set_alert_sent', 0, False)
            log.info("DC Circuit 5V Voltage is back to Normal")
            notify('dc_minimum_volts', 'DC 5V Voltage Normal', 'Your DC 5V Voltage is back to Normal.')
    else:
        if not use_database.notification_alerts('dc_minimum_volts', 'was_alert_sent', 0, 0):
            notify('dc_minimum_volts', 'AC Voltage LOW', f'Your DC 5V Voltage is LOW at: {use_database.electrical_data("readone", "dc_voltage", 0)}!')
            use_database.notification_alerts('dc_minimum_volts', 'set_alert_sent', 0, True)
            log.info(f'Your DC 5V Voltage is LOW at {use_database.electrical_data("readone", "dc_voltage", 0)}!')

                     
def main():
    log.debug('neptune.py main() Started.')
    run_zone_scheduled_jobs()
    run_power_scheduled_jobs()
    update_water_stats()
    send_system_notifications()
    enclosure_fan_control()
    read_onewire_temp_probes()
    get_shed_environmentals()
    get_enclosure_environmentals()
    get_gardenpi_power()
    reset_forced_stopped_jobs()


if __name__ == '__main__':
    main()
