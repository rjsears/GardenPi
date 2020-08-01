#!/usr/bin/python3

# -*- coding: utf-8 -*-

"""
routes.py for use with neptune/GardenPi V1.0.0
"""

VERSION = "V1.0.0 (2020-07-31)"


# TODO Learn and implement Flask Blueprints


import sys
sys.path.append('/var/www/gardenpi_control/gardenpi/utilities')
sys.path.append('/var/www/gardenpi_control/gardenpi')
sys.path.append('/var/www/gardenpi_control')
import neptune
from use_database import sa_check_zone_times, onewire_temp_probes, screen_mode, sa_check_zone_times_jobid, sa_check_zone_times_conflict, read_mysql_database, water_usage, sa_check_power_zone_times_conflict, environmentals_data, electrical_data
from flask import render_template, redirect, url_for, request, flash, Flask
from gardenpi import app
from gardenpi.forms import Job1Form, Job2Form, PowerJob1Form, PowerJob2Form, SetTempAlertLimitForm, SetPowerAlertLimitForm
from datetime import datetime, timedelta, date
import system_info


from system_logging import setup_logging
from system_logging import read_logging_config
import logging


#Setup Module level logging here. Main logging config in system_logging.py
setup_logging()
level = read_logging_config('logging', 'log_level')
level = logging._checkLevel(level)
log = logging.getLogger(__name__)
log.setLevel(level)


@app.route('/')
def gardenpi():
    # Get Power Readings
    log.debug('gardenpi() called')
    current_power_keys = ['total_current_power_utilization', 'total_current_power_import',
                          'total_current_solar_production']
    power_data = {}
    for key in current_power_keys:
        power_data[key] = read_mysql_database("power_solar", key)
    any_zones_running = neptune.any_zones_running('water')
    any_power_zones_running = neptune.any_zones_running('power')
    current_water_source = (neptune.get_water_source()['source_to_use'])
    return render_template('gardenpi_index.html',
                           any_zones_running = any_zones_running,current_water_source = current_water_source,
                           any_power_zones_running = any_power_zones_running,
                           **power_data)

@app.route('/water_source')
def water_source():
    log.debug('water_source() called')
    water_source = neptune.get_water_source()
    is_fresh_zone_running = neptune.is_this_zone_running('fresh_water')
    is_fish_zone_running = neptune.is_this_zone_running('fish_water')
    any_zones_running = neptune.any_zones_running('water')

    return render_template('water_source.html', any_zones_running = any_zones_running,
                           is_fresh_zone_running = is_fresh_zone_running,
                           is_fish_zone_running = is_fish_zone_running,
                           **water_source)

@app.route('/toggle_water_source')
def toggle_water_source():
    log.debug('toggle_water_source() called')
    neptune.toggle_water_source()
    return redirect(url_for('water_source'))

@app.route('/water_stats')
def water_stats():
    log.debug('water_stats() called')
    zone_water_stats = neptune.get_allzone_water_stats()
    return render_template('water_stats.html',**zone_water_stats)

@app.route('/system_dashboard')
def system_dashboard():
    log.debug('system_dashboard() called')
    return render_template('system_dashboard.html')

@app.route('/tools')
def tools():
    log.debug('tools() called')
    any_notification_source_available = neptune.notifications('systemwide', 'enabled', 'check')
    systemwide_notifications_enabled = neptune.notifications('systemwide', 'enabled', 'enabled')
    return render_template('tools.html', systemwide_notifications_enabled = systemwide_notifications_enabled,
                           any_notification_source_available = any_notification_source_available)

@app.route('/toggle_screen')
def toggle_screen():
    log.debug('toggle_screen() called')
    neptune.toggle_screen_mode()
    return redirect(url_for('base_system_tools'))

@app.route('/base_system_tools')
def base_system_tools():
    log.debug('base_system_tools() called')
    kiosk_mode = screen_mode('check_mode')
    return render_template('base_system_tools.html', kiosk_mode=kiosk_mode)

@app.route('/hydroponics')
def hydroponics():
    log.debug('hydroponics() called')
    return render_template('hydroponics.html')

@app.route('/rodi')
def rodi():
    log.debug('rodi() called')
    rodiwater_tank_enabled = neptune.is_tank_enabled('rodiwater_tank')
    if rodiwater_tank_enabled:
        rodiwater_tank_level = neptune.get_tank_gallons('rodiwater_tank')
    else:
        rodiwater_tank_level = 0
    rodiwater_temp = onewire_temp_probes('get_current_temp', 'rodi_water', 0)
    is_zone_running_manually = neptune.is_this_zone_running_manually('zone28')
    is_zone_running = neptune.is_this_zone_running('zone28')
    is_zone_enabled = neptune.zone_enabled('zone28')
    return render_template('rodi.html', rodiwater_tank_level = rodiwater_tank_level,
                           rodiwater_temp = rodiwater_temp, rodiwater_tank_enabled = rodiwater_tank_enabled,
                           is_zone_running_manually = is_zone_running_manually,
                           is_zone_running = is_zone_running,
                           is_zone_enabled = is_zone_enabled)

@app.route('/environmentals')
def environmentals():
    log.debug('environmentals() called')
    environmental_keys = ['pi_cpu_temp', 'enclosure_temp', 'enclosure_humidity',
                          'enclosure_baro', 'shed_temp', 'shed_humidity', 'outdoor_temperature']
    environmental_data = {}
    for key in environmental_keys:
        environmental_data[key] = environmentals_data('readone', key, 0)

    worm_farm_temp = onewire_temp_probes('get_current_temp', 'worm_farm', 0)
    any_notification_source_available = neptune.notifications('systemwide', 'enabled', 'check')
    systemwide_notifications_enabled = neptune.notifications('systemwide', 'enabled', 'enabled')
    system_sms, system_pb, system_email = neptune.notifications('systemwide', 0, 'check')

    return render_template('environmentals.html', worm_farm_temp = worm_farm_temp,
                           any_notification_source_available = any_notification_source_available,
                           systemwide_notifications_enabled = systemwide_notifications_enabled,
                           system_sms = system_sms, system_pb = system_pb, system_email = system_email,
                           **environmental_data)

@app.route('/environmental_notifications', methods=['GET','POST'])
def environmental_notifications():
    log.debug('environmental_notifications() called')
    system_sms, system_pb, system_email = neptune.notifications('systemwide', 0, 'check')
    worm_farm_max_temp_sms = neptune.notifications('worm_farm_max_temp', 'sms', 'enabled')
    worm_farm_max_temp_pb = neptune.notifications('worm_farm_max_temp', 'pb', 'enabled')
    worm_farm_max_temp_email = neptune.notifications('worm_farm_max_temp', 'email', 'enabled')
    enclosure_max_temp_sms = neptune.notifications('enclosure_max_temp', 'sms', 'enabled')
    enclosure_max_temp_pb = neptune.notifications('enclosure_max_temp', 'pb', 'enabled')
    enclosure_max_temp_email = neptune.notifications('enclosure_max_temp', 'email', 'enabled')
    pi_max_cpu_temp_sms = neptune.notifications('pi_max_cpu_temp', 'sms', 'enabled')
    pi_max_cpu_temp_pb = neptune.notifications('pi_max_cpu_temp', 'pb', 'enabled')
    pi_max_cpu_temp_email = neptune.notifications('pi_max_cpu_temp', 'email', 'enabled')

    form = SetTempAlertLimitForm()
    form.worm_farm_max_temp.data = str(neptune.get_alert_limit('worm_farm_max_temp'))
    form.pi_max_cpu_temp.data = str(neptune.get_alert_limit('pi_max_cpu_temp'))
    form.enclosure_max_temp.data = str(neptune.get_alert_limit('enclosure_max_temp'))

    if form.validate_on_submit():
        neptune.update_alert_limit('worm_farm_max_temp', request.form['worm_farm_max_temp'])
        neptune.update_alert_limit('pi_max_cpu_temp', request.form['pi_max_cpu_temp'])
        neptune.update_alert_limit('enclosure_max_temp', request.form['enclosure_max_temp'])
        flash("Alert Limits Updated", "success")
        return redirect(url_for('environmental_notifications'))
    else:
        print("Validation Failed")
        print(form.errors)

    return render_template('environmental_notifications.html',
                           system_sms = system_sms, system_pb = system_pb, system_email=system_email,
                           worm_farm_max_temp_sms = worm_farm_max_temp_sms, worm_farm_max_temp_pb = worm_farm_max_temp_pb,
                           worm_farm_max_temp_email = worm_farm_max_temp_email, enclosure_max_temp_sms = enclosure_max_temp_sms,
                           enclosure_max_temp_pb = enclosure_max_temp_pb, enclosure_max_temp_email = enclosure_max_temp_email,
                           pi_max_cpu_temp_sms = pi_max_cpu_temp_sms, pi_max_cpu_temp_pb = pi_max_cpu_temp_pb,
                           pi_max_cpu_temp_email = pi_max_cpu_temp_email, form = form)

@app.route('/power_usage_notifications', methods=['GET','POST'])
def power_usage_notifications():
    log.debug('power_usage_notifications() called')
    system_sms, system_pb, system_email = neptune.notifications('systemwide', 0, 'check')
    ac_circuit_max_amps_sms = neptune.notifications('ac_circuit_max_amps', 'sms', 'enabled')
    ac_circuit_max_amps_pb = neptune.notifications('ac_circuit_max_amps', 'pb', 'enabled')
    ac_circuit_max_amps_email = neptune.notifications('ac_circuit_max_amps', 'email', 'enabled')
    ac_minimum_volts_sms = neptune.notifications('ac_minimum_volts', 'sms', 'enabled')
    ac_minimum_volts_pb = neptune.notifications('ac_minimum_volts', 'pb', 'enabled')
    ac_minimum_volts_email = neptune.notifications('ac_minimum_volts', 'email', 'enabled')
    dc_max_amps_sms = neptune.notifications('dc_max_amps', 'sms', 'enabled')
    dc_max_amps_pb = neptune.notifications('dc_max_amps', 'pb', 'enabled')
    dc_max_amps_email = neptune.notifications('dc_max_amps', 'email', 'enabled')
    dc_minimum_volts_sms = neptune.notifications('dc_minimum_volts', 'sms', 'enabled')
    dc_minimum_volts_pb = neptune.notifications('dc_minimum_volts', 'pb', 'enabled')
    dc_minimum_volts_email = neptune.notifications('dc_minimum_volts', 'email', 'enabled')

    form = SetPowerAlertLimitForm()
    form.ac_circuit_max_amps.data = str(neptune.get_alert_limit('ac_circuit_max_amps'))
    form.dc_max_amps.data = str(neptune.get_alert_limit('dc_max_amps'))
    form.ac_minimum_volts.data = str(neptune.get_alert_limit('ac_minimum_volts'))
    form.dc_minimum_volts.data = str(neptune.get_alert_limit('dc_minimum_volts'))

    if form.validate_on_submit():
        neptune.update_alert_limit('ac_circuit_max_amps', request.form['ac_circuit_max_amps'])
        neptune.update_alert_limit('dc_max_amps', request.form['dc_max_amps'])
        neptune.update_alert_limit('ac_minimum_volts', request.form['ac_minimum_volts'])
        neptune.update_alert_limit('dc_minimum_volts', request.form['dc_minimum_volts'])
        flash("Alert Limits Updated", "success")
        return redirect(url_for('power_usage_notifications'))
    else:
        print("Validation Failed")
        print(form.errors)

    return render_template('power_usage_notifications.html',
                           system_sms = system_sms, system_pb = system_pb, system_email=system_email,
                           ac_circuit_max_amps_sms = ac_circuit_max_amps_sms, ac_circuit_max_amps_pb=ac_circuit_max_amps_pb,
                           ac_circuit_max_amps_email=ac_circuit_max_amps_email, ac_minimum_volts_sms=ac_minimum_volts_sms,
                           ac_minimum_volts_pb=ac_minimum_volts_pb, ac_minimum_volts_email=ac_minimum_volts_email,
                           dc_max_amps_sms=dc_max_amps_sms, dc_max_amps_pb=dc_max_amps_pb, dc_max_amps_email=dc_max_amps_email,
                           dc_minimum_volts_sms=dc_minimum_volts_sms, dc_minimum_volts_pb=dc_minimum_volts_pb,
                           dc_minimum_volts_email=dc_minimum_volts_email, form = form)


@app.route('/electrical')
def electrical():
    log.debug('electrical() called')
    electrical_keys = ['dc_voltage', 'dc_current', 'dc_power',
                          'dc_shunt_voltage', 'ac_current', 'ac_voltage']
    electrical_usage_data = {}
    for key in electrical_keys:
        electrical_usage_data[key] = electrical_data('readone', key, 0)

    any_notification_source_available = neptune.notifications('systemwide', 'enabled', 'check')
    systemwide_notifications_enabled = neptune.notifications('systemwide', 'enabled', 'enabled')
    system_sms, system_pb, system_email = neptune.notifications('systemwide', 0, 'check')
    return render_template('electrical.html', any_notification_source_available=any_notification_source_available,
                           systemwide_notifications_enabled=systemwide_notifications_enabled, system_sms=system_sms,
                           system_pb=system_pb, system_email=system_email , **electrical_usage_data)

@app.route('/tank_levels')
def tank_levels():
    log.debug('tank_levels() called')
    fishwater_tank_enabled = neptune.is_tank_enabled('fishwater_tank')
    rodiwater_tank_enabled = neptune.is_tank_enabled('rodiwater_tank')
    hydroponic_tank_enabled = neptune.is_tank_enabled('hydroponic_tank')

    if fishwater_tank_enabled:
        fishwater_tank_level = neptune.get_tank_gallons('fishwater_tank')
    else:
        fishwater_tank_level = 0

    if rodiwater_tank_enabled:
        rodiwater_tank_level = neptune.get_tank_gallons('rodiwater_tank')
    else:
        rodiwater_tank_level = 0

    if hydroponic_tank_enabled:
        hydroponic_tank_level = neptune.get_tank_gallons('hydroponic_tank')
    else:
        hydroponic_tank_level = 0

    temperature_keys = ['fish_water', 'hydroponic_tank', 'rodi_water']
    temperature_data = {}
    for key in temperature_keys:
        temperature_data[key] = onewire_temp_probes('get_current_temp', key, 0)

    return render_template('tank_levels.html',
                           fishwater_tank_level = fishwater_tank_level,
                           rodiwater_tank_level = rodiwater_tank_level,
                           hydroponic_tank_level = hydroponic_tank_level,
                           fishwater_tank_enabled = fishwater_tank_enabled,
                           rodiwater_tank_enabled = rodiwater_tank_enabled,
                           hydroponic_tank_enabled = hydroponic_tank_enabled,
                           **temperature_data)

@app.route('/toggle_source_zones/<zone>')
def toggle_source_zones(zone):
    log.debug(f'toggle_source_zones() called with zone: {zone}')
    zone = f'{zone}_water'
    is_zone_enabled = neptune.zone_enabled(zone)
    if is_zone_enabled:
        neptune.disable_zone(zone)
    else:
        neptune.enable_zone(zone)
    return redirect(url_for('water_source'))

@app.route('/zone_control')
def zone_control():
    log.debug('zone_control() called')
    current_zones = system_info.garden_zones
    zone_running_data = {}
    for zone in current_zones:
        zone_running_data[zone] = neptune.is_this_zone_running(zone)

    return render_template('zone_control.html',
                           **zone_running_data)


@app.route('/zone/<int:id>')
def zone(id):
    zone = f'zone{id}'
    log.debug(f'zone() called with zone: {zone}')
    any_zones_running = neptune.any_zones_running('water')
    is_zone_enabled = neptune.zone_enabled(zone)
    is_zone_running = neptune.is_this_zone_running(zone)
    is_zone_running_manually = neptune.is_this_zone_running_manually(zone)
    job1_enabled = (neptune.get_schedule_by_zone_job(zone, '1')[0][3])
    job2_enabled = (neptune.get_schedule_by_zone_job(zone, '2')[0][3])
    job1_running = (neptune.get_schedule_by_zone_job(zone, '1')[0][7])
    job2_running = (neptune.get_schedule_by_zone_job(zone, '2')[0][7])
    total_zone_water_usage = water_usage(zone, 'read_total_gallons_used', 0)
    running_current_total_gallons = water_usage(zone, 'read_gallons_current_run', 0)
    current_gpm = neptune.get_current_gpm()
    current_water_source = (neptune.get_water_source()['source_to_use'])
    any_notification_source_available = neptune.notifications('systemwide', 'enabled', 'check')
    notifications_enabled = neptune.notifications(zone, 'notifications', 'enabled')
    systemwide_notifications_enabled = neptune.notifications('systemwide', 'enabled', 'enabled')
    sms_enabled = neptune.notifications(zone, 'sms', 'enabled')
    pb_enabled = neptune.notifications(zone, 'pb', 'enabled')
    email_enabled = neptune.notifications(zone, 'email', 'enabled')

    if job1_running:
        job_id = (neptune.get_schedule_by_zone_job(zone, '1')[0][0])
    elif job2_running:
        job_id = (neptune.get_schedule_by_zone_job(zone, '2')[0][0])
    else:
        job_id = ''

    return render_template('zone.html',
                           zone_enabled = is_zone_enabled,
                           is_zone_running = is_zone_running,
                           is_zone_running_manually = is_zone_running_manually,
                           any_zones_running = any_zones_running,
                           job1_enabled = job1_enabled,
                           job2_enabled=job2_enabled,
                           job1_running = job1_running,
                           job2_running = job2_running,
                           total_zone_water_usage = total_zone_water_usage,
                           running_current_total_gallons = running_current_total_gallons,
                           current_gpm = current_gpm,
                           current_water_source = current_water_source,
                           notifications_enabled = notifications_enabled,
                           any_notification_source_available = any_notification_source_available,
                           systemwide_notifications_enabled = systemwide_notifications_enabled,
                           sms_enabled = sms_enabled, email_enabled = email_enabled, pb_enabled = pb_enabled,
                           job_id = job_id, id = id)



@app.route('/toggle_zone/<int:id>')
def toggle_zone(id):
    zone = f'zone{id}'
    log.debug(f'toggle_zone() called with zone: {zone}')
    is_zone_enabled = neptune.zone_enabled(zone)
    if is_zone_enabled:
        neptune.disable_zone(zone)
    else:
        neptune.enable_zone(zone)
    return redirect(url_for('zone', id=id))

@app.route('/toggle_rodi_zone')
def toggle_rodi_zone():
    log.debug('toggle_rodi_zone() called')
    zone = 'zone28'
    is_zone_enabled = neptune.zone_enabled(zone)
    if is_zone_enabled:
        neptune.disable_zone(zone)
    else:
        neptune.enable_zone(zone)
    return redirect(url_for('rodi'))


@app.route('/toggle_job/<int:id>/<job>')
def toggle_job(id, job):
    zone = f'zone{id}'
    log.debug(f'toggle_job() called with zone: {zone} and job: {job}')
    url = f'schedulejob{job}'
    neptune.toggle_job(zone, job)
    return redirect(url_for(url, id = id))

@app.route('/manual_run/<int:id>')
def manual_run(id):
    zone = f'zone{id}'
    log.debug(f'manual_run() called with zone: {zone}')
    neptune.run_zone(zone)
    return redirect(url_for('zone', id = id))

@app.route('/manual_run_rodi')
def manual_run_rodi():
    log.debug('manual_run_rodi() called')
    zone = 'zone28'
    neptune.run_zone(zone)
    return redirect(url_for('rodi'))


@app.route('/force_stop_zone_scheduled/<int:id>/<int:job_id>')
def force_stop_zone_scheduled(id, job_id):
    zone = f'zone{id}'
    log.debug(f'force_stop_zone_scheduled called with zone: {zone} and job id: {job_id}')
    neptune.stop_job(zone, job_id, True)
    return redirect(url_for('zone', id = id))

@app.route('/stop_zone/<int:id>')
def stop_zone(id):
    zone = f'zone{id}'
    log.debug(f'stop_zone() called with zone: {zone}')
    neptune.stop_zone(zone)
    return redirect(url_for('zone', id = id))

@app.route('/stop_rodi_zone')
def stop_rodi_zone():
    log.debug('stop_rode_zone() called')
    zone = 'zone28'
    neptune.stop_zone(zone)
    return redirect(url_for('rodi'))

@app.route('/schedule/<int:id>')
def schedule(id):
    zone = f'zone{id}'
    log.debug(f'schedule() called with zone: {zone}')
    job1_enabled = (neptune.get_schedule_by_zone_job(zone, '1')[0][3])
    job2_enabled = (neptune.get_schedule_by_zone_job(zone, '2')[0][3])
    return render_template('schedule.html', id=id,
                           job1_enabled = job1_enabled,
                           job2_enabled = job2_enabled)

@app.route('/schedulejob1/<int:id>',methods=['GET','POST'])
def schedulejob1(id):
    zone1_with_conflict = ''
    job1_with_conflict = ''
    zone = f'zone{id}'
    log.debug(f'schedulejob1() called with zone: {zone}')
    form = Job1Form()
    job1_jobid = (neptune.get_schedule_by_zone_job(zone, '1')[0][0])
    job1_enabled = (neptune.get_schedule_by_zone_job(zone, '1')[0][3])
    job1_start_time = (neptune.get_schedule_by_zone_job(zone, '1')[0][4])
    job1_duration = (neptune.get_schedule_by_zone_job(zone, '1')[0][6])
    job1_monday = (neptune.get_schedule_by_zone_job(zone, '1')[0][8])
    job1_tuesday = (neptune.get_schedule_by_zone_job(zone, '1')[0][9])
    job1_wednesday = (neptune.get_schedule_by_zone_job(zone, '1')[0][10])
    job1_thursday = (neptune.get_schedule_by_zone_job(zone, '1')[0][11])
    job1_friday = (neptune.get_schedule_by_zone_job(zone, '1')[0][12])
    job1_saturday = (neptune.get_schedule_by_zone_job(zone, '1')[0][13])
    job1_sunday = (neptune.get_schedule_by_zone_job(zone, '1')[0][14])
    form.start_hour_job1.data = str(job1_start_time.hour)
    form.start_minute_job1.data = str(job1_start_time.minute)
    form.duration_job1.data = str(job1_duration)
    form.monday_job1.data = job1_monday
    form.tuesday_job1.data = job1_tuesday
    form.wednesday_job1.data = job1_wednesday
    form.thursday_job1.data = job1_thursday
    form.friday_job1.data = job1_friday
    form.saturday_job1.data = job1_saturday
    form.sunday_job1.data = job1_sunday

    if form.validate_on_submit():
        # Uodate job start/stop times and duration based on form input
        job1_new_start_hour = request.form['start_hour_job1']
        job1_new_start_minute = request.form['start_minute_job1']
        job1_new_start_time = datetime.strptime(job1_new_start_hour + ':' + job1_new_start_minute + ':00', '%H:%M:%S').time()
        job1_new_duration = int(request.form['duration_job1'])
        job1_delta = timedelta(minutes = job1_new_duration)
        job1_new_stoptime = ((datetime.combine(date(1,1,1), job1_new_start_time) + job1_delta).time())

        jobs1 = [('monday_job1', 1, 'monday'), ('tuesday_job1', 1, 'tuesday'),
                 ('wednesday_job1', 1, 'wednesday'), ('thursday_job1', 1, 'thursday'),
                 ('friday_job1', 1, 'friday'), ('saturday_job1', 1, 'saturday'),
                 ('sunday_job1', 1, 'sunday')]

        #Update selected days of week based on job
        for job in jobs1:
            jobfield = job[0]
            jobnumber = job[1]
            dayofjob = job[2]
            value = bool(request.form.get(jobfield, False))
            neptune.update_day(zone, jobnumber, dayofjob, value)

        # Since we can only run one zone at a time, verify here that there are no conflicting jobs.
        job1_time_conflict = sa_check_zone_times_conflict(job1_new_start_time, job1_new_stoptime, job1_jobid)
        if job1_time_conflict:
            zone1_with_conflict = sa_check_zone_times_jobid(job1_new_start_time, job1_new_stoptime)[0][1]
            job1_with_conflict = sa_check_zone_times_jobid(job1_new_start_time, job1_new_stoptime)[0][2]
            flash(f'Schedule Conflict with {zone1_with_conflict} - Job: {job1_with_conflict}', 'error')
            return render_template('schedule1_error.html', id=id)
        else:
            flash("Schedule Updated", "success")
            neptune.update_job_start_time(zone, '1', job1_new_start_time)
            neptune.update_job_stop_time(zone, '1', job1_new_stoptime)
            neptune.update_job_duration(zone, '1', job1_new_duration)
        return redirect(url_for('schedulejob1', id=id))

    else:
        print("Page Refresh")
        print(form.errors)
    return render_template('schedulejob1.html',form = form, job1_enabled = job1_enabled, id = id)

@app.route('/schedulejob2/<int:id>',methods=['GET','POST'])
def schedulejob2(id):
    zone2_with_conflict = ''
    job2_with_conflict = ''
    zone = f'zone{id}'
    log.debug(f'schedulejob2() called with zone: {zone}')
    form = Job2Form()
    job2_jobid = (neptune.get_schedule_by_zone_job(zone, '2')[0][0])
    job2_enabled = (neptune.get_schedule_by_zone_job(zone, '2')[0][3])
    job2_start_time = (neptune.get_schedule_by_zone_job(zone, '2')[0][4])
    job2_duration = (neptune.get_schedule_by_zone_job(zone, '2')[0][6])
    job2_monday = (neptune.get_schedule_by_zone_job(zone, '2')[0][8])
    job2_tuesday = (neptune.get_schedule_by_zone_job(zone, '2')[0][9])
    job2_wednesday = (neptune.get_schedule_by_zone_job(zone, '2')[0][10])
    job2_thursday = (neptune.get_schedule_by_zone_job(zone, '2')[0][11])
    job2_friday = (neptune.get_schedule_by_zone_job(zone, '2')[0][12])
    job2_saturday = (neptune.get_schedule_by_zone_job(zone, '2')[0][13])
    job2_sunday = (neptune.get_schedule_by_zone_job(zone, '2')[0][14])
    form.start_hour_job2.data = str(job2_start_time.hour)
    form.start_minute_job2.data = str(job2_start_time.minute)
    form.duration_job2.data = str(job2_duration)
    form.monday_job2.data = job2_monday
    form.tuesday_job2.data = job2_tuesday
    form.wednesday_job2.data = job2_wednesday
    form.thursday_job2.data = job2_thursday
    form.friday_job2.data = job2_friday
    form.saturday_job2.data = job2_saturday
    form.sunday_job2.data = job2_sunday

    if form.validate_on_submit():
        # Uodate job start/stop times and duration based on form input
        job2_new_start_hour = request.form['start_hour_job2']
        job2_new_start_minute = request.form['start_minute_job2']
        job2_new_start_time = datetime.strptime(job2_new_start_hour + ':' + job2_new_start_minute + ':00', '%H:%M:%S').time()
        job2_new_duration = int(request.form['duration_job2'])
        job2_delta = timedelta(minutes = job2_new_duration)
        job2_new_stoptime = ((datetime.combine(date(1,1,1), job2_new_start_time) + job2_delta).time())

        jobs2 = [('monday_job2', 2, 'monday'), ('tuesday_job2', 2, 'tuesday'),
                 ('wednesday_job2', 2, 'wednesday'), ('thursday_job2', 2, 'thursday'),
                 ('friday_job2', 2, 'friday'), ('saturday_job2', 2, 'saturday'),
                 ('sunday_job2', 2, 'sunday')]

        #Update selected days of week based on job
        for job in jobs2:
            jobfield = job[0]
            jobnumber = job[1]
            dayofjob = job[2]
            value = bool(request.form.get(jobfield, False))
            neptune.update_day(zone, jobnumber, dayofjob, value)

        # Since we can only run one zone at a time, verify here that there are no conflicting jobs.
        job2_time_conflict = sa_check_zone_times_conflict(job2_new_start_time, job2_new_stoptime, job2_jobid)
        if job2_time_conflict:
            zone2_with_conflict = sa_check_zone_times_jobid(job2_new_start_time, job2_new_stoptime)[0][1]
            job2_with_conflict = sa_check_zone_times_jobid(job2_new_start_time, job2_new_stoptime)[0][2]
            flash(f'Schedule Conflict with {zone2_with_conflict} - Job: {job2_with_conflict}', 'error')
            return render_template('schedule2_error.html', id=id)
        else:
            flash("Schedule Updated", "success")
            neptune.update_job_start_time(zone, '2', job2_new_start_time)
            neptune.update_job_stop_time(zone, '2', job2_new_stoptime)
            neptune.update_job_duration(zone, '2', job2_new_duration)

        return redirect(url_for('schedulejob2', id=id))

    else:
        print("Validation Failed")
        print(form.errors)
    return render_template('schedulejob2.html',form = form, job2_enabled = job2_enabled, id = id)


@app.route('/power_zone_control')
def power_zone_control():
    log.debug('power_zone_control() called')
    current_power_zones = system_info.allpowerzones
    power_zone_running_data = {}
    for zone in current_power_zones:
        power_zone_running_data[zone] = neptune.is_this_zone_running(zone)

    return render_template('power_zone_control.html',
                           **power_zone_running_data)

@app.route('/power/<int:id>')
def power(id):
    zone = f'power{id}'
    log.debug(f'power() called with powerzone: {zone}')
    any_zones_running = neptune.any_zones_running('power')
    is_zone_enabled = neptune.zone_enabled(zone)
    is_zone_running = neptune.is_this_zone_running(zone)
    is_zone_running_manually = neptune.is_this_zone_running_manually(zone)
    job1_enabled = (neptune.get_schedule_by_zone_job(zone, '1')[0][3])
    job2_enabled = (neptune.get_schedule_by_zone_job(zone, '2')[0][3])
    job1_running = (neptune.get_schedule_by_zone_job(zone, '1')[0][7])
    job2_running = (neptune.get_schedule_by_zone_job(zone, '2')[0][7])
    any_notification_source_available = neptune.notifications('systemwide', 'enabled', 'check')
    notifications_enabled = neptune.notifications(zone, 'notifications', 'enabled')
    systemwide_notifications_enabled = neptune.notifications('systemwide', 'enabled', 'enabled')
    sms_enabled = neptune.notifications(zone, 'sms', 'enabled')
    pb_enabled = neptune.notifications(zone, 'pb', 'enabled')
    email_enabled = neptune.notifications(zone, 'email', 'enabled')

    if job1_running:
        job_id = (neptune.get_schedule_by_zone_job(zone, '1')[0][0])
    elif job2_running:
        job_id = (neptune.get_schedule_by_zone_job(zone, '2')[0][0])
    else:
        job_id = ''

    return render_template('power.html',
                           zone_enabled = is_zone_enabled,
                           is_zone_running = is_zone_running,
                           is_zone_running_manually = is_zone_running_manually,
                           any_zones_running = any_zones_running,
                           job1_enabled = job1_enabled,
                           job2_enabled=job2_enabled,
                           job1_running = job1_running,
                           job2_running = job2_running,
                           job_id = job_id, id = id,
                           notifications_enabled=notifications_enabled,
                           any_notification_source_available=any_notification_source_available,
                           systemwide_notifications_enabled=systemwide_notifications_enabled,
                           sms_enabled=sms_enabled, email_enabled=email_enabled, pb_enabled=pb_enabled
                           )

@app.route('/toggle_power_zone/<int:id>')
def toggle_power_zone(id):
    zone = f'power{id}'
    log.debug(f'toggle_power_zone() called with powerzone: {zone}')
    is_zone_enabled = neptune.zone_enabled(zone)
    if is_zone_enabled:
        neptune.disable_zone(zone)
    else:
        neptune.enable_zone(zone)
    return redirect(url_for('power', id=id))

@app.route('/toggle_power_job/<int:id>/<job>')
def toggle_power_job(id, job):
    zone = f'power{id}'
    log.debug(f'toggle_power_job() called with zone: {zone} and job: {job}')
    url = f'powerschedulejob{job}'
    neptune.toggle_job(zone, job)
    return redirect(url_for(url, id = id))

@app.route('/manual_power_run/<int:id>')
def manual_power_run(id):
    zone = f'power{id}'
    log.debug(f'manual_power_run() called with powerzone: {zone}')
    neptune.run_zone(zone)
    return redirect(url_for('power', id = id))

@app.route('/force_stop_power_zone_scheduled/<int:id>/<int:job_id>')
def force_stop_power_zone_scheduled(id, job_id):
    zone = f'power{id}'
    log.debug(f'force_stop_power_zone_scheduled() called with powerzone: {zone} and job id: {job_id}')
    neptune.stop_job(zone, job_id, True)
    return redirect(url_for('power', id = id))

@app.route('/stop_power_zone/<int:id>')
def stop_power_zone(id):
    zone = f'power{id}'
    log.debug(f'stop_power_zone() called with zone: {zone}')
    neptune.stop_zone(zone)
    return redirect(url_for('power', id = id))

@app.route('/power_schedule/<int:id>')
def power_schedule(id):
    zone = f'power{id}'
    log.debug(f'power_schedule() called with powerzone: {zone}')
    job1_enabled = (neptune.get_schedule_by_zone_job(zone, '1')[0][3])
    job2_enabled = (neptune.get_schedule_by_zone_job(zone, '2')[0][3])
    return render_template('power_schedule.html', id=id,
                           job1_enabled = job1_enabled,
                           job2_enabled = job2_enabled)

@app.route('/powerschedulejob1/<int:id>',methods=['GET','POST'])
def powerschedulejob1(id):
    zone1_with_conflict = ''
    job1_with_conflict = ''
    zone = f'power{id}'
    log.debug(f'powerschedulejob1() called with powerzone: {zone}')
    form = PowerJob1Form()
    job1_jobid = (neptune.get_schedule_by_zone_job(zone, '1')[0][0])
    job1_enabled = (neptune.get_schedule_by_zone_job(zone, '1')[0][3])
    job1_start_time = (neptune.get_schedule_by_zone_job(zone, '1')[0][4])
    job1_duration = (neptune.get_schedule_by_zone_job(zone, '1')[0][6])
    job1_monday = (neptune.get_schedule_by_zone_job(zone, '1')[0][8])
    job1_tuesday = (neptune.get_schedule_by_zone_job(zone, '1')[0][9])
    job1_wednesday = (neptune.get_schedule_by_zone_job(zone, '1')[0][10])
    job1_thursday = (neptune.get_schedule_by_zone_job(zone, '1')[0][11])
    job1_friday = (neptune.get_schedule_by_zone_job(zone, '1')[0][12])
    job1_saturday = (neptune.get_schedule_by_zone_job(zone, '1')[0][13])
    job1_sunday = (neptune.get_schedule_by_zone_job(zone, '1')[0][14])
    form.start_hour_job1.data = str(job1_start_time.hour)
    form.start_minute_job1.data = str(job1_start_time.minute)
    form.duration_job1.data = str(job1_duration)
    form.monday_job1.data = job1_monday
    form.tuesday_job1.data = job1_tuesday
    form.wednesday_job1.data = job1_wednesday
    form.thursday_job1.data = job1_thursday
    form.friday_job1.data = job1_friday
    form.saturday_job1.data = job1_saturday
    form.sunday_job1.data = job1_sunday

    if form.validate_on_submit():
        # Uodate job start/stop times and duration based on form input
        job1_new_start_hour = request.form['start_hour_job1']
        job1_new_start_minute = request.form['start_minute_job1']
        job1_new_start_time = datetime.strptime(job1_new_start_hour + ':' + job1_new_start_minute + ':00', '%H:%M:%S').time()
        job1_new_duration = int(request.form['duration_job1'])
        job1_delta = timedelta(minutes = job1_new_duration)
        job1_new_stoptime = ((datetime.combine(date(1,1,1), job1_new_start_time) + job1_delta).time())

        jobs1 = [('monday_job1', 1, 'monday'), ('tuesday_job1', 1, 'tuesday'),
                 ('wednesday_job1', 1, 'wednesday'), ('thursday_job1', 1, 'thursday'),
                 ('friday_job1', 1, 'friday'), ('saturday_job1', 1, 'saturday'),
                 ('sunday_job1', 1, 'sunday')]

        #Update selected days of week based on job
        for job in jobs1:
            jobfield = job[0]
            jobnumber = job[1]
            dayofjob = job[2]
            value = bool(request.form.get(jobfield, False))
            neptune.update_day(zone, jobnumber, dayofjob, value)

        # Verify power jobs for this power outlet do not overlap each other.
        job1_time_conflict = sa_check_power_zone_times_conflict(zone, job1_new_start_time, job1_new_stoptime, job1_jobid)
        if job1_time_conflict:
            # zone2_with_conflict = sa_check_zone_times_jobid(job2_new_start_time, job2_new_stoptime)[0][1]
            # job2_with_conflict = sa_check_zone_times_jobid(job2_new_start_time, job2_new_stoptime)[0][2]
            flash(f'Schedule Conflict with - Job: 2', 'error')
            return render_template('powerschedule1_error.html', id=id)
        else:
            flash("Schedule Updated", "success")
            neptune.update_job_start_time(zone, '1', job1_new_start_time)
            neptune.update_job_stop_time(zone, '1', job1_new_stoptime)
            neptune.update_job_duration(zone, '1', job1_new_duration)
        return redirect(url_for('powerschedulejob1', id=id))

    else:
        print("Page Refresh")
        print(form.errors)
    return render_template('powerschedulejob1.html',form = form, job1_enabled = job1_enabled, id = id)


@app.route('/powerschedulejob2/<int:id>',methods=['GET','POST'])
def powerschedulejob2(id):
    zone2_with_conflict = ''
    job2_with_conflict = ''
    zone = f'power{id}'
    log.debug(f'powerschedulejob2() called with powerzone: {zone}')
    form = PowerJob2Form()
    job2_jobid = (neptune.get_schedule_by_zone_job(zone, '2')[0][0])
    job2_enabled = (neptune.get_schedule_by_zone_job(zone, '2')[0][3])
    job2_start_time = (neptune.get_schedule_by_zone_job(zone, '2')[0][4])
    job2_duration = (neptune.get_schedule_by_zone_job(zone, '2')[0][6])
    job2_monday = (neptune.get_schedule_by_zone_job(zone, '2')[0][8])
    job2_tuesday = (neptune.get_schedule_by_zone_job(zone, '2')[0][9])
    job2_wednesday = (neptune.get_schedule_by_zone_job(zone, '2')[0][10])
    job2_thursday = (neptune.get_schedule_by_zone_job(zone, '2')[0][11])
    job2_friday = (neptune.get_schedule_by_zone_job(zone, '2')[0][12])
    job2_saturday = (neptune.get_schedule_by_zone_job(zone, '2')[0][13])
    job2_sunday = (neptune.get_schedule_by_zone_job(zone, '2')[0][14])
    form.start_hour_job2.data = str(job2_start_time.hour)
    form.start_minute_job2.data = str(job2_start_time.minute)
    form.duration_job2.data = str(job2_duration)
    form.monday_job2.data = job2_monday
    form.tuesday_job2.data = job2_tuesday
    form.wednesday_job2.data = job2_wednesday
    form.thursday_job2.data = job2_thursday
    form.friday_job2.data = job2_friday
    form.saturday_job2.data = job2_saturday
    form.sunday_job2.data = job2_sunday

    if form.validate_on_submit():
        # Uodate job start/stop times and duration based on form input
        job2_new_start_hour = request.form['start_hour_job2']
        job2_new_start_minute = request.form['start_minute_job2']
        job2_new_start_time = datetime.strptime(job2_new_start_hour + ':' + job2_new_start_minute + ':00', '%H:%M:%S').time()
        job2_new_duration = int(request.form['duration_job2'])
        job2_delta = timedelta(minutes = job2_new_duration)
        job2_new_stoptime = ((datetime.combine(date(1,1,1), job2_new_start_time) + job2_delta).time())

        jobs2 = [('monday_job2', 2, 'monday'), ('tuesday_job2', 2, 'tuesday'),
                 ('wednesday_job2', 2, 'wednesday'), ('thursday_job2', 2, 'thursday'),
                 ('friday_job2', 2, 'friday'), ('saturday_job2', 2, 'saturday'),
                 ('sunday_job2', 2, 'sunday')]

        #Update selected days of week based on job
        for job in jobs2:
            jobfield = job[0]
            jobnumber = job[1]
            dayofjob = job[2]
            value = bool(request.form.get(jobfield, False))
            neptune.update_day(zone, jobnumber, dayofjob, value)

        # Verify power jobs for this power outlet do not overlap each other.
        job2_time_conflict = sa_check_power_zone_times_conflict(zone, job2_new_start_time, job2_new_stoptime, job2_jobid)
        if job2_time_conflict:
            #zone2_with_conflict = sa_check_zone_times_jobid(job2_new_start_time, job2_new_stoptime)[0][1]
            #job2_with_conflict = sa_check_zone_times_jobid(job2_new_start_time, job2_new_stoptime)[0][2]
            flash(f'Schedule Conflict with - Job: 1', 'error')
            return render_template('powerschedule2_error.html', id=id)
        else:
            flash("Schedule Updated", "success")
            neptune.update_job_start_time(zone, '2', job2_new_start_time)
            neptune.update_job_stop_time(zone, '2', job2_new_stoptime)
            neptune.update_job_duration(zone, '2', job2_new_duration)

        return redirect(url_for('powerschedulejob2', id=id))

    else:
        print("Validation Failed")
        print(form.errors)
    return render_template('powerschedulejob2.html',form = form, job2_enabled = job2_enabled, id = id)

@app.route('/reboot')
def reboot():
    log.debug('reboot() called')
    return render_template('reboot.html')

@app.route('/reboot_now')
def reboot_now():
    log.debug('reboot_now() called')
    neptune.reboot_halt_system('reboot')

@app.route('/halt')
def halt():
    log.debug('halt() called')
    return render_template('halt.html')

@app.route('/halt_now')
def halt_now():
    log.debug('halt_now() called')
    neptune.reboot_halt_system('halt')

@app.route('/systemwide_notifications')
def systemwide_notifications():
    log.debug('systemwide_notifications() called')
    any_notification_source_available = neptune.notifications('systemwide', 'enabled', 'check')
    systemwide_notifications_enabled = neptune.notifications('systemwide', 'enabled', 'enabled')
    systemwide_sms_enabled = neptune.notifications('systemwide', 'sms', 'enabled')
    systemwide_pb_enabled = neptune.notifications('systemwide', 'pb', 'enabled')
    systemwide_email_enabled = neptune.notifications('systemwide', 'email', 'enabled')
    return render_template('systemwide_notifications.html', any_notification_source_available = any_notification_source_available,
                           systemwide_notifications_enabled = systemwide_notifications_enabled,
                           systemwide_sms_enabled = systemwide_sms_enabled,
                           systemwide_pb_enabled = systemwide_pb_enabled,
                           systemwide_email_enabled = systemwide_email_enabled)

@app.route('/toggle_systemwide_notifications/<type>')
def toggle_systemwide_notifications(type):
    log.debug(f'toggle_systemwide_notifications() called with: {type}')
    neptune.notifications('systemwide', type, 'toggle')
    return redirect(url_for('systemwide_notifications'))

@app.route('/notifications/<int:id>')
def notifications(id):
    zone = f'zone{id}'
    log.debug(f'notifications() called with: {zone}')
    systemwide_notifications_enabled = neptune.notifications('systemwide', 'enabled', 'enabled')
    systemwide_sms_enabled = neptune.notifications('systemwide', 'sms', 'enabled')
    systemwide_pb_enabled = neptune.notifications('systemwide', 'pb', 'enabled')
    systemwide_email_enabled = neptune.notifications('systemwide', 'email', 'enabled')
    notifications_enabled = neptune.notifications(zone, 'notifications', 'enabled')
    sms_enabled = neptune.notifications(zone, 'sms', 'enabled')
    pb_enabled = neptune.notifications(zone, 'pb', 'enabled')
    email_enabled = neptune.notifications(zone, 'email', 'enabled')
    return render_template('notifications.html', notifications_enabled = notifications_enabled,
                           systemwide_notifications_enabled = systemwide_notifications_enabled,
                           systemwide_email_enabled = systemwide_email_enabled,
                           systemwide_pb_enabled = systemwide_pb_enabled,
                           systemwide_sms_enabled = systemwide_sms_enabled,
                           sms_enabled = sms_enabled, email_enabled = email_enabled,
                           pb_enabled = pb_enabled, id = id)

@app.route('/toggle_notifications/<int:id>/<notification>/')
def toggle_notifications(id, notification):
    zone = f'zone{id}'
    log.debug(f'toggle_notifications() called with zone: {zone}')
    neptune.notifications(zone, notification, 'toggle')
    return redirect(url_for('notifications', id = id))

@app.route('/toggle_environmental_notifications/<zone>/<notification>/')
def toggle_environmental_notifications(zone, notification):
    log.debug(f'toggle_environmental_notifications() called with zone: {zone} and: {notification}')
    neptune.notifications(zone, notification, 'toggle')
    return redirect(request.referrer)


@app.route('/power_notifications/<int:id>')
def power_notifications(id):
    zone = f'power{id}'
    log.debug(f'power_notifications() called with powerzone: {zone}')
    systemwide_notifications_enabled = neptune.notifications('systemwide', 'enabled', 'enabled')
    systemwide_sms_enabled = neptune.notifications('systemwide', 'sms', 'enabled')
    systemwide_pb_enabled = neptune.notifications('systemwide', 'pb', 'enabled')
    systemwide_email_enabled = neptune.notifications('systemwide', 'email', 'enabled')
    notifications_enabled = neptune.notifications(zone, 'notifications', 'enabled')
    sms_enabled = neptune.notifications(zone, 'sms', 'enabled')
    pb_enabled = neptune.notifications(zone, 'pb', 'enabled')
    email_enabled = neptune.notifications(zone, 'email', 'enabled')
    return render_template('power_notifications.html', notifications_enabled = notifications_enabled,
                           systemwide_notifications_enabled = systemwide_notifications_enabled,
                           systemwide_email_enabled = systemwide_email_enabled,
                           systemwide_pb_enabled = systemwide_pb_enabled,
                           systemwide_sms_enabled = systemwide_sms_enabled,
                           sms_enabled = sms_enabled, email_enabled = email_enabled,
                           pb_enabled = pb_enabled, id = id)

@app.route('/toggle_power_notifications/<int:id>/<notification>/')
def toggle_power_notifications(id, notification):
    zone = f'power{id}'
    log.debug(f'toggle_power_notifications() called with powerzone: {zone}')
    neptune.notifications(zone, notification, 'toggle')
    return redirect(url_for('power_notifications', id = id))


# This allows us to call static pages utilizing Flask as opposed to Nginx.
@app.route('/<string:page_name>/')
def render_static(page_name):
    return render_template('%s.html' % page_name)