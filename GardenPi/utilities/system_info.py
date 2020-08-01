#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
system_info.py for use with neptune/GardenPi V1.0.0
Holds some basic system information and configuration.
Will slowly move most of this to MySQL.
"""

VERSION = "V1.0.0 (2020-07-31)"


# URL that we use to check and see if we have internet connectivity.
check_url = 'www.google.com'

# See neptune.py/run_job()
check_gpm = 1


# Here is all of our MySQL Connection information
mysql_servername = "gardenpi"
mysql_username = "neptune"  # Your main MySQL admin username or username that is the exact same for both databases
mysql_password = "super_secret_password"  # Your main MySQL admin password or password that is exact same for both databases
mysql_database = "neptune"  # The name of your fish tank  (or other) database.

# SQLAlchemy URI Info - change password
sqlalchemy_db_uri = 'mysql+mysqlconnector://neptune:super_secret_password@gardenpi/neptune'


## Information for our Influx Databases. Used to access our electrical information database
influx_host = 'gardenpi'
influx_port = 8086
influx_user = 'gardenpi'
influx_password = 'super_secret_password'
influx_dbname = 'electrical_monitoring'


## Setup our EmonCMS Database Connection - used to access various sensor database tables for our smart water meters
emoncms_servername = "gardenpi"
emoncms_username = "emoncms"
emoncms_password = "super_secret_password"
emoncms_db = "emoncms"

## Info for our notifications.py
## Set Notification Accounts#
alert_email = ['youremail1@gmail.com', 'youremail2@gmail.com']
twilio_from = '+187655512129'
twilio_account = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
twilio_token = 'xxxxxxxxxxxxxxxxxx'
twilio_to = ['+1675xxxxxxx', '+1780xxxxxxx']
pushbilletAPI = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # pushbullet API token (http://www.pushbullet.com)


# Zone Information
# This defines all of the zones that we can possible control with our system.
allzones = ['zone1', 'zone2', 'zone3', 'zone4', 'zone5', 'zone6', 'fresh_water', 'fish_water']
allpowerzones = ['power1', 'power2', 'power3', 'power4', 'power5', 'power6', 'power7', 'power8', 'intake_fan', 'exhaust_fan']
alluserpowerzones = ['power1', 'power2', 'power3', 'power4', 'power5', 'power6', 'power7']
fanpower = ['intake_fan', 'exhaust_fan']

allhydrozones = ['zone9', 'zone10', 'zone11', 'zone12', 'zone13', 'zone14', 'zone15', 'zone16', 'zone17', 'zone18', 'zone19', 'zone20', 'zone21', 'zone22', 'zone23', 'zone24', 'zone25', 'zone26', 'zone27', 'zone28']

water_tanks = ['fishwater_tank', 'rodiwater_tank', 'hydroponic_tank', 'fishtanksump_tank']

# Which power zone controls our AC-to-AC Transformer?
water_transformer = 'power8'

# Which power zone controls our AC power to our old Fish Tank Water Water Pump?
water_pump = 'power7'

#This defines only the zones we want exposed to the end user for job scheduling
garden_zones = ['zone1', 'zone2', 'zone3', 'zone4', 'zone5', 'zone6']

# What temperature probes/zones do we have?
temp_probes = ['']

#This determines how many static jobs there are per day per zone.
number_of_jobs = [1,2]
job_ids = [1,2,3,4,5,6,7,8,9,10,11,12]


# Stuff we need to track water usage using EmonCMS
#irrigation_gallons_total = "feed_254"
#current_gpm = "feed_285"
irrigation_gallons_total = "feed_62"
current_gpm = "feed_63"

# Used for Sprinkler Bypass
sprinkler_bypass = 'Yes'  # Set this to "No" to disable all sprinkler checks
sprinkler_type = 'Timer'  # Timer or Rachio - sprinkler_bypass must be set to "Yes" for this to make any difference

# Set Sprinkler start and stop times here if using 'Timer' setting above.
sprinklerstart = '23:00:00'
sprinklerstop = '23:00:00'

# If you have a Rachio Sprinkler System, this is the curl request to get the sprinkler status.
# You must have your own system, you must get your Auth:Bearer ID as well as you device ID
# from Rachio in order to use this subprocess.
rachio_headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer xxxxxxxxx-xxxxxx-xxxxx-xxxxx-xxxxxxxxxxx'}
rachio_url = 'https://api.rach.io/1/public/device/xxxxxxxxx-xxxxxx-xxxxx-xxxxx-xxxxxxxxxxx/current_schedule'

#Where do we read our circuit power information from - used to track realtime power usage on 120V AC Circuit to GArdenPi
gardenpi_power_circuit_current = 'XXX340_ch9_a'
gardenpi_power_circuit_volts = 'XXX340_volts'


def main():
    print("This script is not intended to be run directly.")
    print("This is the systemwide Credentials & Settings module.")
    print("It is called by other modules.")
    exit()


if __name__ == '__main__':
    main()
