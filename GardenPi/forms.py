#!/usr/bin/python3

# -*- coding: utf-8 -*-

"""
forms.py for usage with neptune/GardenPi V1.0.0
"""

VERSION = "V1.0.0 (2020-07-31)"


from flask_wtf import FlaskForm
from wtforms import SubmitField, BooleanField, FloatField, StringField, SelectField, TextAreaField, SelectMultipleField, widgets

from wtforms.validators import InputRequired, Length, DataRequired

def hours():
    return [('0', 'hour'),('0', '12 AM'), ('1', '1 AM'), ('2', '2 AM'), ('3', '3 AM'), ('4', '4 AM'),
            ('5', '5 AM'), ('6', '6 AM'), ('7', '7 AM'), ('8', '8 AM'), ('9', '9 AM'),
            ('10', '10 AM'), ('11', '11 AM'), ('12', '12 PM'), ('13', '1 PM'),
            ('14', '2 PM'), ('15', '3 PM'), ('16', '4 PM'), ('17', '5 PM'),
            ('18', '6 PM'), ('19', '7 PM'), ('20', '8 PM'), ('21', '9 PM'),
            ('22', '10 PM'), ('23', '11 PM')]

def minutes():
    return [('0', 'minute'), ('0', '00'), ('5', '05'), ('10', '10'), ('15', '15'), ('20', '20'), ('25', '25'),
            ('30', '30'), ('35', '35'), ('40', '40'), ('45', '45'), ('50', '50'), ('55', '55')]

def days():
    return [('monday', 'Monday'), ('tuesday', 'Tuesday'), ('wednesday', 'Wednesday'),
            ('thursday', 'Thursday'), ('friday', 'Friday'), ('saturday', 'Saturday'),('sunday', 'Sunday')]

def duration():
    return [('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'),
            ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10'), ('15', '15'),
            ('20', '20'), ('25', '25'), ('30', '30')]

def powerduration():
    return [('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'),
            ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10'), ('15', '15'),
            ('20', '20'), ('25', '25'), ('30', '30'), ('40','40'),('50','50'), ('60', '1 Hour'),
            ('90', '1.5 Hours'), ('120', '2 Hours'), ('150', '2.5 Hours'), ('180', '3 Hours'),
            ('240', '4 Hours'), ('300', '5 Hours'), ('360', '6 Hours')]

def pimaxcputemp():
    return [('145.0', '145°F'), ('150.0', '150°F'), ('155.0', '155°F'), ('160.0', '160°F'), ('165.0', '165°F'),
    ('170.0', '170°F'), ('175.0', '175°F'), ('180.0', '180°F'), ('185.0', '185°F'), ('190.0', '190°F')]

def wormfarmmaxtemp():
    return [('75.0', '75°F'), ('80.0', '80°F'), ('81.0', '81°F'), ('82.0', '82°F'), ('83.0', '83°F'),
    ('84.0', '84°F'), ('85.0', '85°F'), ('86.0', '86°F'), ('87.0', '87°F'), ('88.0', '88°F'),
            ('89.0', '89°F'), ('90.0', '90°F'), ('95.0', '95°F'), ('100.0', '100°F')]

def enclosuremaxtemp():
    return [('100.0', '100°F'), ('105.0', '105°F'), ('110.0', '110°F'), ('115.0', '115°F'), ('120.0', '120°F'),
    ('125.0', '125°F'), ('130.0', '130°F'), ('135.0', '135°F'), ('140.0', '140°F'), ('145.0', '145°F'),
            ('150.0', '150°F'), ('155.0', '155°F'), ('160.0', '160°F'), ('165.0', '165°F')]

def accircuitmaxamps():
    return [('1.0', '1 Amp'), ('2.0', '2 Amps'), ('3.0', '3 Amps'), ('4.0', '4 Amps'), ('5.0', '5 Amps'),
    ('6.0', '6 Amps'), ('7.0', '7 Amps'), ('8.0', '8 Amps'), ('9.0', '9 Amps'), ('10.0', '10 Amps'),
            ('11.0', '11 Amps'), ('12.0', '12 Amps'), ('13.0', '13 Amps'), ('14.0', '14 Amps')]

def dcmaxamps():
    return [('1.0', '1 Amp'), ('2.0', '2 Amps'), ('3.0', '3 Amps'), ('4.0', '4 Amps'), ('5.0', '5 Amps'),
    ('6.0', '6 Amps'), ('7.0', '7 Amps'), ('8.0', '8 Amps'), ('9.0', '9 Amps'), ('10.0', '10 Amps'),
            ('11.0', '11 Amps'), ('12.0', '12 Amps'), ('13.0', '13 Amps'), ('14.0', '14 Amps')]

def acminimumvolts():
    return [('115.0', '115 Volts'), ('116.0', '116 Volts'), ('117.0', '117 Volts'), ('118.0', '118 Volts'),
    ('119.0', '119 Volts')]

def dcminimumvolts():
    return [('4.5', '4.5 Volts'), ('4.6', '4.6 Volts'), ('4.7', '4.7 Volts'), ('4.8', '4.8 Volts'),
    ('4.9', '4.9 Volts')]


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class Job1Form(FlaskForm):
    start_hour_job1 = SelectField('Start Hour:', choices = hours())
    start_minute_job1 = SelectField('Start Hour:', choices=minutes())
    duration_job1 = SelectField('Duration:', choices=duration(), default = '5' )
    monday_job1 = BooleanField('Monday')
    tuesday_job1 = BooleanField('Tuesday')
    wednesday_job1 = BooleanField('Wednesday')
    thursday_job1 = BooleanField('Thursday')
    friday_job1 = BooleanField('Friday')
    saturday_job1 = BooleanField('Saturday')
    sunday_job1 = BooleanField('Sunday')
    submit_job = SubmitField('Submit')

class Job2Form(FlaskForm):
    start_hour_job2 = SelectField('Start Hour:', choices=hours())
    start_minute_job2 = SelectField('Start Hour:', choices=minutes())
    duration_job2 = SelectField('Duration:', choices=duration(), default = '5')
    monday_job2 = BooleanField('Monday')
    tuesday_job2 = BooleanField('Tuesday')
    wednesday_job2 = BooleanField('Wednesday')
    thursday_job2 = BooleanField('Thursday')
    friday_job2 = BooleanField('Friday')
    saturday_job2 = BooleanField('Saturday')
    sunday_job2 = BooleanField('Sunday')
    submit_job = SubmitField('Submit')

class PowerJob1Form(FlaskForm):
    start_hour_job1 = SelectField('Start Hour:', choices = hours())
    start_minute_job1 = SelectField('Start Hour:', choices=minutes())
    duration_job1 = SelectField('Duration:', choices=powerduration(), default = '5' )
    monday_job1 = BooleanField('Monday')
    tuesday_job1 = BooleanField('Tuesday')
    wednesday_job1 = BooleanField('Wednesday')
    thursday_job1 = BooleanField('Thursday')
    friday_job1 = BooleanField('Friday')
    saturday_job1 = BooleanField('Saturday')
    sunday_job1 = BooleanField('Sunday')
    submit_job = SubmitField('Submit')

class PowerJob2Form(FlaskForm):
    start_hour_job2 = SelectField('Start Hour:', choices=hours())
    start_minute_job2 = SelectField('Start Hour:', choices=minutes())
    duration_job2 = SelectField('Duration:', choices=powerduration(), default = '5')
    monday_job2 = BooleanField('Monday')
    tuesday_job2 = BooleanField('Tuesday')
    wednesday_job2 = BooleanField('Wednesday')
    thursday_job2 = BooleanField('Thursday')
    friday_job2 = BooleanField('Friday')
    saturday_job2 = BooleanField('Saturday')
    sunday_job2 = BooleanField('Sunday')
    submit_job = SubmitField('Submit')

class SetTempAlertLimitForm(FlaskForm):
    worm_farm_max_temp = SelectField('Maximum Temp:', choices=wormfarmmaxtemp())
    pi_max_cpu_temp = SelectField('Maximum Temp:', choices=pimaxcputemp())
    enclosure_max_temp = SelectField('Maximum Temp:', choices=enclosuremaxtemp())

class SetPowerAlertLimitForm(FlaskForm):
    ac_circuit_max_amps = SelectField('Max Amps:', choices=accircuitmaxamps())
    dc_max_amps = SelectField('Max Amps:', choices=dcmaxamps())
    ac_minimum_volts = SelectField('Minimum Volts:', choices=acminimumvolts())
    dc_minimum_volts = SelectField('Minimum Volts:', choices=dcminimumvolts())