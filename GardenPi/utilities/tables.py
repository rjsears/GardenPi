#!/usr/bin/python3

# -*- coding: utf-8 -*-

"""
tables.py for use with neptune/GardenPi V1.0.0
"""

VERSION = "V1.0.0 (2020-08-05)"

import sqlalchemy as sa
metadata = sa.MetaData()

zones = sa.Table(
    'zones',
    metadata,
    sa.Column('zone_name', sa.VARCHAR(collation='utf8_unicode_ci', length=15), primary_key=True, nullable=False),
    sa.Column('zone_number', sa.Integer(), nullable=False),
    sa.Column('description', sa.VARCHAR(collation='utf8_unicode_ci', length=40), nullable=False),
    sa.Column('gpio', sa.Integer(), nullable=False),
    sa.Column('enabled', sa.Boolean(), nullable=False),
    sa.Column('running', sa.Boolean(), nullable=False),
    sa.Column('running_manually', sa.Boolean(), nullable=False),
    sa.Column('gallons_start', sa.Integer(), nullable=False),
    sa.Column('gallons_stop', sa.Integer(), nullable=False),
    sa.Column('gallons_current_run', sa.Integer(), nullable=False),
    sa.Column('gallons_last_run', sa.Integer(), nullable=False),
    sa.Column('total_gallons_used', sa.Integer(), nullable=False),
    sa.Column('mcp', sa.VARCHAR(collation='utf8_unicode_ci', length=4), nullable=False),
    sa.Column('notifications', sa.Boolean(), nullable=False),
    sa.Column('sms', sa.Boolean(), nullable=False),
    sa.Column('pb', sa.Boolean(), nullable=False),
    sa.Column('email', sa.Boolean(), nullable=False),
)

hydroponic_zones = sa.Table(
    'hydroponic_zones',
    metadata,
    sa.Column('zone_name', sa.VARCHAR(collation='utf8_unicode_ci', length=15), primary_key=True, nullable=False),
    sa.Column('zone_number', sa.Integer(), nullable=False),
    sa.Column('description', sa.VARCHAR(collation='utf8_unicode_ci', length=40), nullable=False),
    sa.Column('gpio', sa.Integer(), nullable=False),
    sa.Column('enabled', sa.Boolean(), nullable=False),
    sa.Column('running', sa.Boolean(), nullable=False),
    sa.Column('running_manually', sa.Boolean(), nullable=False),
    sa.Column('gallons_start', sa.Integer(), nullable=False),
    sa.Column('gallons_stop', sa.Integer(), nullable=False),
    sa.Column('gallons_current_run', sa.Integer(), nullable=False),
    sa.Column('gallons_last_run', sa.Integer(), nullable=False),
    sa.Column('total_gallons_used', sa.Integer(), nullable=False),
    sa.Column('mcp', sa.VARCHAR(collation='utf8_unicode_ci', length=4), nullable=False),
    sa.Column('notifications', sa.Boolean(), nullable=False),
    sa.Column('sms', sa.Boolean(), nullable=False),
    sa.Column('pb', sa.Boolean(), nullable=False),
    sa.Column('email', sa.Boolean(), nullable=False),
)

scheduled_jobs = sa.Table(
    'scheduled_jobs',
    metadata,
    sa.Column('job_id', sa.Integer(), primary_key=True, nullable=False),
    sa.Column('zone', sa.VARCHAR(collation='utf8_unicode_ci', length=15), nullable=False),
    sa.Column('zone_job', sa.Integer(), nullable=False),
    sa.Column('job_enabled', sa.Boolean(), nullable=False),
    sa.Column('job_start_time', sa.TIME(), nullable=False),
    sa.Column('job_stop_time', sa.TIME(), nullable=False),
    sa.Column('job_duration', sa.Integer(), nullable=False),
    sa.Column('job_running', sa.Boolean(), nullable=False),
    sa.Column('monday', sa.Boolean(), nullable=False),
    sa.Column('tuesday', sa.Boolean(), nullable=False),
    sa.Column('wednesday', sa.Boolean(), nullable=False),
    sa.Column('thursday', sa.Boolean(), nullable=False),
    sa.Column('friday', sa.Boolean(), nullable=False),
    sa.Column('saturday', sa.Boolean(), nullable=False),
    sa.Column('sunday', sa.Boolean(), nullable=False),
    sa.Column('forced_stop_manually', sa.Boolean(), nullable=False),
)

zones_currently_running = sa.Table(
    'zones_currently_running',
    metadata,
    sa.Column('currently_running', sa.Boolean(), primary_key=True, nullable=False),
    sa.Column('run_manually', sa.Boolean(), nullable=False),
    sa.Column('run_by_job', sa.Boolean(), nullable=False),
    sa.Column('job_id', sa.SmallInteger(), nullable=False),
    sa.Column('force_stopped', sa.Boolean(), nullable=False)
)

water_source = sa.Table(
    'water_source',
    metadata,
    sa.Column('selected_source', sa.VARCHAR(collation='utf8_unicode_ci', length=15), primary_key=True, nullable=False),
    sa.Column('fish_available', sa.Boolean(), nullable=False),
    sa.Column('job_water_source', sa.VARCHAR(collation='utf8_unicode_ci', length=15), nullable=False)
)

power = sa.Table(
    'power',
    metadata,
    sa.Column('zone_name', sa.VARCHAR(collation='utf8_unicode_ci', length=15), primary_key=True, nullable=False),
    sa.Column('zone_number', sa.Integer(), nullable=False),
    sa.Column('description', sa.VARCHAR(collation='utf8_unicode_ci', length=40), nullable=False),
    sa.Column('gpio', sa.Integer(), nullable=False),
    sa.Column('enabled', sa.Boolean(), nullable=False),
    sa.Column('running', sa.Boolean(), nullable=False),
    sa.Column('running_manually', sa.Boolean(), nullable=False),
    sa.Column('mcp', sa.VARCHAR(collation='utf8_unicode_ci', length=4), nullable=False),
    sa.Column('notifications', sa.Boolean(), nullable=False),
    sa.Column('sms', sa.Boolean(), nullable=False),
    sa.Column('pb', sa.Boolean(), nullable=False),
    sa.Column('email', sa.Boolean(), nullable=False),
)

power_scheduled_jobs = sa.Table(
    'power_scheduled_jobs',
    metadata,
    sa.Column('job_id', sa.Integer(), primary_key=True, nullable=False),
    sa.Column('zone', sa.VARCHAR(collation='utf8_unicode_ci', length=15), nullable=False),
    sa.Column('zone_job', sa.Integer(), nullable=False),
    sa.Column('job_enabled', sa.Boolean(), nullable=False),
    sa.Column('job_start_time', sa.TIME(), nullable=False),
    sa.Column('job_stop_time', sa.TIME(), nullable=False),
    sa.Column('job_duration', sa.Integer(), nullable=False),
    sa.Column('job_running', sa.Boolean(), nullable=False),
    sa.Column('monday', sa.Boolean(), nullable=False),
    sa.Column('tuesday', sa.Boolean(), nullable=False),
    sa.Column('wednesday', sa.Boolean(), nullable=False),
    sa.Column('thursday', sa.Boolean(), nullable=False),
    sa.Column('friday', sa.Boolean(), nullable=False),
    sa.Column('saturday', sa.Boolean(), nullable=False),
    sa.Column('sunday', sa.Boolean(), nullable=False),
    sa.Column('forced_stop_manually', sa.Boolean(), nullable=False),
)

power_currently_running = sa.Table(
    'power_currently_running',
    metadata,
    sa.Column('zone_name', sa.VARCHAR(collation='utf8_unicode_ci', length=15), primary_key=True, nullable=False),
    sa.Column('currently_running', sa.Boolean(), primary_key=True, nullable=False),
    sa.Column('run_manually', sa.Boolean(), nullable=False),
    sa.Column('run_by_job', sa.Boolean(), nullable=False),
    sa.Column('job_id', sa.SmallInteger(), nullable=False),
    sa.Column('force_stopped', sa.Boolean(), nullable=False),
)

environmental = sa.Table(
    'environmental',
    metadata,
    sa.Column('pi_cpu_temp', sa.DECIMAL(4,1), primary_key=True, nullable=False),
    sa.Column('enclosure_temp', sa.DECIMAL(4,1), nullable=False),
    sa.Column('enclosure_humidity', sa.DECIMAL(3,1), nullable=False),
    sa.Column('enclosure_baro', sa.DECIMAL(4,2), nullable=False),
    sa.Column('shed_temp', sa.DECIMAL(4,1), nullable=False),
    sa.Column('shed_humidity', sa.DECIMAL(3,1), nullable=False),
    sa.Column('outdoor_temperature', sa.DECIMAL(4,1), nullable=False),
)

electrical_usage = sa.Table(
    'electrical_usage',
    metadata,
    sa.Column('dc_voltage', sa.DECIMAL(3, 2), primary_key=True, nullable=False),
    sa.Column('dc_current', sa.DECIMAL(7, 3), nullable=False),
    sa.Column('dc_power', sa.DECIMAL(7, 3), nullable=False),
    sa.Column('dc_shunt_voltage', sa.DECIMAL(7, 3), nullable=False),
    sa.Column('ac_current', sa.DECIMAL(4, 2), nullable=False),
    sa.Column('ac_voltage', sa.DECIMAL(5, 2), nullable=False),
)

screen = sa.Table(
    'screen',
    metadata,
    sa.Column('kioskmode', sa.Boolean(), primary_key=True, nullable=False),
)

temperatures = sa.Table(
    'temperatures',
    metadata,
    sa.Column('temp_zone', sa.VARCHAR(collation='utf8_unicode_ci', length=17), primary_key=True, nullable=False),
    sa.Column('onewire_id', sa.VARCHAR(collation='utf8_unicode_ci', length=17), nullable=False),
    sa.Column('current_temp', sa.DECIMAL(4, 1), nullable=False),
    sa.Column('enabled', sa.Boolean(), nullable=False),
)

water_tanks = sa.Table(
    'water_tanks',
    metadata,
    sa.Column('tank_name', sa.VARCHAR(collation='utf8_unicode_ci', length=20), primary_key=True, nullable=False),
    sa.Column('description', sa.VARCHAR(collation='utf8_unicode_ci', length=40), nullable=False),
    sa.Column('tty', sa.VARCHAR(collation='utf8_unicode_ci', length=6), nullable=False),
    sa.Column('enabled', sa.Boolean(), nullable=False),
    sa.Column('current_level_inches', sa.DECIMAL(3, 1), nullable=False),
    sa.Column('current_volume_gallons', sa.Integer(), nullable=False),
    sa.Column('gallons_per_inch', sa.DECIMAL(2, 1), nullable=False),
    sa.Column('max_tank_volume', sa.Integer(), nullable=False),
    sa.Column('tank_empty_depth', sa.Integer(), nullable=False),
)

systemwide_notifications = sa.Table(
    'systemwide_notifications',
    metadata,
    sa.Column('enabled', sa.Boolean(), nullable=False),
    sa.Column('sms', sa.Boolean(), nullable=False),
    sa.Column('pb', sa.Boolean(), nullable=False),
    sa.Column('email', sa.Boolean(), nullable=False),
)

systemwide_alerts = sa.Table(
    'systemwide_alerts',
    metadata,
    sa.Column('sensor_name', sa.VARCHAR(collation='utf8_unicode_ci', length=20), primary_key=True, nullable=False),
    sa.Column('notifications', sa.Boolean(), nullable=False),
    sa.Column('sms', sa.Boolean(), nullable=False),
    sa.Column('pb', sa.Boolean(), nullable=False),
    sa.Column('email', sa.Boolean(), nullable=False),
    sa.Column('alert_limit', sa.DECIMAL(4,1), nullable=False),
    sa.Column('alert_sent', sa.Boolean(), nullable=False),

)

power_solar = sa.Table(
    'power_solar',
    metadata,
    sa.Column('total_current_power_utilization', sa.SmallInteger(), primary_key=True, nullable=False),
    sa.Column('total_current_power_import', sa.SmallInteger(),nullable=False),
    sa.Column('total_current_solar_production', sa.SmallInteger(), nullable=False),
)
