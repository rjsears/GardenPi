<h2 align="center">
  <a name="gardenpi_logo" href="https://github.com/rjsears/GardenPi"><img src="https://github.com/rjsears/GardenPi/blob/master/images/gardenpi_cover.jpg" alt="GardenPi" height="700" width="550"></a>
  <br>
  GardenPi (V1.0.0 - August 4th, 2020)
  </h2>
  <p align="center">
  Multizone Hydroponic / Aquaponic / Irrigation &amp; Fish Tank Water management and monitoring platform
  </p>
<h4 align="center">Be sure to :star: my repo so you can keep up to date on any updates and progress!</h4>
<br>
<div align="center">
    <a href="https://github.com/rjsears/GardenPi/commits/master"><img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/rjsears/GardenPi?style=plastic"></a>
    <a href="https://github.com/rjsears/GardenPi/issues"><img alt="GitHub issues" src="https://img.shields.io/github/issues/rjsears/GardenPi?style=plastic"></a>
    <a href="https://github.com/rjsears/GardenPi/blob/master/LICENSE"><img alt="License" src="https://img.shields.io/github/license/rjsears/GardenPi?style=plastic"></a>
</h4>
</div>
<br>
<p><font size="3">
GardenPi, powered by Neptune.py is designed to manage, monitor and control a series or sprinkler valves and a multitude of sensors for pretty much any sized irrigation / hydroponic / aquaponic project. It can be scaled (using the hardware I used) from 1 to 32 zones for water and 7 zones for power. It is built almost entirely in Python3 with a Flask web interface and relies on a lot of css to make the interface very fast. It is written and designed to run on the Raspberry Pi 4.  

Hopefully, this might provide some inspiration for others in regard to their automation projects. Contributions are always welcome.</p>
<div align="center"><a name="top_menu"></a>
  <h4>
    <a href="https://github.com/rjsears/GardenPi#overview">
      Overview
    </a>
    <span> | </span>
    <a href="https://github.com/rjsears/GardenPi/blob/master/enclosure/readme.md">
      Parts List
    </a>
    <span> | </span>
    <a href="https://github.com/rjsears/GardenPi#dependencies">
      Dependencies
    </a>
    <span> | </span>
    <a href="https://github.com/rjsears/GardenPi#install">
      Installation & Configuration
    </a>
    <span> | </span>
    <a href="https://github.com/rjsears/GardenPi/tree/master/GardenPi">
      Code
    </a>
    <span> | </span>
    <a href="https://github.com/rjsears/GardenPi#schematics">
      Schematics
    </a>
    <span> | </span>
    <a href="https://github.com/rjsears/GardenPi/issues?q=is%3Aissue+is%3Aopen+sort%3Aupdated-desc">
      Todo List
    </a>
    <span> | </span>
    <a href="https://github.com/rjsears/GardenPi#icons">
      Icons
    </a>
  </h4>
</div>

<hr>

#### <a name="overview"></a>Overview & Theory of Operation
GardenPi was designed around my family's desire to get more heavily into gardening, hydroponics, and eventually aquaponics. Since we have several fish tanks and do large water changes weekly, we wanted to be able to use that nutrient-rich water for the garden instead of just dumping it down the drain. So weekly my wife would have to cart fish tank water around the garden beds to water the plants manually and then switch back to a hose. This was getting very time consuming and tedious. Because of that, the basic concept of GardenPi was born.

The gardening part would have been pretty easy, we could have used a simple irrigation controller but as you can see we needed several water sources, in our case freshwater (street water) and water from our fish tanks and standard irrigation controllers did not provide the functions we needed to manage the process of moving back and forth between water sources. So I designed a new irrigation layout and my sons and I dug up the yard and installed six separate garden irrigation zones separate from our lawn irrigation and installed valves so we could switch between street water and an IBC tank filled with fish tank water. Now I just needed the software to manage it all.

As with any project, I wanted to look more long term. Our family sat down and talked about what we really wanted to do. One was to get into much larger fish tanks ~200-500 gallons), greatly expand our garden to provide more space for year-around growing (we live in Phoenix), start to dabble into full hydroponics and eventually move into full aquaponics and eliminate street water gardening altogether, relying 100% on old fishtank & aquaponic wastewater instead. Street water would be managed by a RODI system and fed into the fish and aquaponic tanks and all plant water would come from the fish. As you can imagine this would require quite a bit of management and thinking ahead and out-of-the-box.

The system designed for <em>our</em> needs ended up with the following configuration:
<ul>
  <li>27  x "Water" Zones (Expandable to 32 Zones total)</li>
  <li>8 x "Power" Zones</li>
  <li>6 x "Temperature" Zones (including one for our worm farm)</li>
  <li>3 x "Humidity" Zones</li>
  <li>1 x Barometric Sensor</li>
  <li>DC Current and Voltage Sensors</li>
  <li>AC Current and Voltage Sensors</li>
  <li>4 x Ultrasonic Water Level Detectors</li>
  <li>4 x Non-Contact Liquid Level Sensors</li>
  <li>7" Touchscreen for local control</li>
</ul>

In addition to these zones/sensors, the system also interacts directly with our already installed power and water monitoring systems. This system was build on EmonCMS which is part of the OpenEnergy Project. We use our EmonCMS data to gather water utilization information for GardenPi via smart water meters on our property and do the same for monitoring the AC circuit utilization for GardenPi. Other data such as outside temperature and humidity are likewise drawn from an outside source, namely a Davis Vantage PRO2 system we have installed on the property. A script grabs all of this data and writes it to a MySQL database and sends the necessary information over to GardenPi. This information is written directly to the ```neptune``` database automatically by outside scripts. If you do not use these readings you can set them to 0 in the database and that is all that will be displayed in the web interface.

This is the broad overview of how the system is designed:<br><br>
<img src="https://github.com/rjsears/GardenPi/blob/master/images/gardenpi_physical_20200803.jpg" alt="GardenPi Physical Layout" height="600" width="800"></a>
<br><br>
The goal of version 1.0.0 of GardenPi was to build and test the hardware and get the garden irrigation, sensor readings, and automatic water switching installed and working. As I progress with other versions I will continue to build out all other functionality as we continue to build out our gardens, hydroponics and aquaponics. 

GardenPi is very flexable in regards to what you use, how many zones you want, if you want power zones, etc. If you have specific questions about the code or how things are put together, fell free to open an issue and I will do my best to help.
<br><br>
<hr>
<em>PLEASE NOTE: This project <b>IS NOT</b> intended to be a "plug-and-play" installation, rather a starting point for someone that wants to use all (or part) of the repo to monitor and manage their irrigation system(s).  There <u>will be</u> significant modifications required by the user even if they are using a clean Pi install. Things in the code such as smart water monitoring and electrical monitoring are integrated with other sensors and automation platforms that I am currently using. I will try my best to point these areas out, but if you do not use those things, major code changes will have to be made to make GardenPi work <u>for you</u>. If you are not comfortable using Python and making these types of changes, this project might not be for you. My goal in later versions if to have flags for this and set them at runtime and not have so much code that needs to be manually corrected, but in version 1.0.0, that code will still need to be modified. Some examples are down further.
<br><br>  
Hopefully, this might provide some inspiration for others in regard to their garden automation projects.</em>
<hr>

#### <a name="dependencies"></a>Software Dependencies
There are a lot of moving parts to any particular project. I will try and list all of the dependencies that you will need to use this repo. It is outside the scope of this documentation to cover the installation and configuration of some of these items. Also, some of these are optional (like Influx/Grafana) depending on how much you want to impliment. Also, I don't plan on listing the more common libraries (like datetime) that come prepackaged with Python. If I had to add them (pip3 install xxx), I will try to list them here. I have included a <a href="https://github.com/rjsears/GardenPi/blob/master/GardenPi/requirements.txt">"requirements.txt"</a> file for use with pip3. Versions were as of this writing.
<ul>
  <li><a href="https://httpd.apache.org/">Apache2</a> or <a href="https://www.nginx.com/">Nginx</a> Web Server</li>
  <li><a href="https://www.mysql.com/">MySQL</a> or other SQL server</li>
  <li><a href="https://uwsgi-docs.readthedocs.io/en/latest/">Web Server Gateway Interface</a> (uWSGI) (for Flask)</li>
  <li><a href="https://www.influxdata.com/">InfluxDB</a></li>
  <li><a href="https://grafana.com/">Grafana</a></li>
  <li><a href="https://flask.palletsprojects.com/en/1.1.x/">Flask (1.1.2)</a></li>
  <li><a href="https://pypi.org/project/Flask-WTF/">Flask WTF (0.14.3)</a></li>
  <li><a href="https://requests.readthedocs.io/en/master/">Requests</a></li>
  <li><a href="https://pyyaml.org/wiki/PyYAMLDocumentation">PyYaml</a></li>
  <li><a href="https://dev.mysql.com/doc/connector-python/en/">MySQL Connector</a></li>
  <li><a href="https://github.com/influxdata/influxdb-python">InfluxDBClient</a></li>
  <li><a href="https://www.sqlalchemy.org/">SQLAlchemy (1.3.18)</a></li>
  <li><a href="https://docs.sentry.io/platforms/python/">Sentry-SDK (Optional, I use it for error tracking)</a></li>
  <li><a href="https://pypi.org/project/pyserial/">PySerial (3.4)</a></li>
  <li><a href="https://pypi.org/project/PyYAML/">PyYaml (5.3.1)</a></li>
  <li><a href="https://wtforms.readthedocs.io/en/2.3.x/">WTForms (2.3.3)</a></li>
  <li><a href="https://pypi.org/project/adafruit-circuitpython-bme280/">Adafruit BME280 Libraries (2.4.3)</a></li>
  <li><a href="https://pypi.org/project/pi-ina219/">Pi INA219 Libraries (1.3.0)</a></li>
  <li><a href="https://pypi.org/project/pushbullet.py/0.11.0/">Pushbullet (0.11.0) - (Optional, used for notifications)</a></li>
  <li><a href="https://pypi.org/project/twilio/">Twilio (6.44.1) - (Optional, used for notifications)</a></li>
  <li><a href="https://pypi.org/project/wiringpi/">WiringPi (2.6.0)</a></li>
  <li><a href="https://pypi.org/project/PyYAML/">PyYaml (5.3.1)</a></li>
 </ul>
 <hr>
 
 I also use phpMyAdmin and so some of the configuration files reflect modifications for that. If you plan to use it as well, flling the install instructions and make the necessary changes. The configuration files for nginx assume phpmyadmin with fastcgi. You can remove these settings if you are not using phpmyadmin.

#### <a name="install"></a>Installation & Configuration
There are a <b><em>LOT</em></b> of different sites that will explain how to install and configure Nginx/Apache, MySQL, InfluxDB, Grafana, PHP, etc so I will not waste space here duplicating those instructions. 
<hr>

##### Raspian Image & Pi Basic Setup
I would highly recommend starting with a brand new Raspian image. Once you have installed your new image, login and update it:
```
sudo apt update && apt upgrade -y
```

I have included a <b>Pi4</b> compatible <a href="https://github.com/rjsears/GardenPi/blob/master/confix.txt">config.txt</a> file that you can place in your ```/boot``` directory, but ONLY if you used a brand new image for this project and are using a Pi4. Otherwise you should look at the entries and determine what you need based on how you currently have your Pi configured. Again, I would highly recommand starting with a fresh image. If you are reusing your Pi, pay close attention to these entries in ```/boot/config.txt```. If you need to change them from the defaults, you will need to also alter code within the project:
```
dtparam=i2c_arm=on
dtoverlay=disable_wifi
dtoverlay=disable-bt
enable_uart=1
dtoverlay=w1-gpio
dtoverlay=sc16is752-i2c,int_pin=24,addr=0x48
dtoverlay=sc16is752-i2c,int_pin=26,addr=0x4d
```

Please note on the ```dtoverlay=disable_wifi``` only set this if you are hardwiring your Pi, otherwise you will not have any wifi capabilities.

Reboot your Pi and make sure that everything such as your network, SSH, etc still all work as required.
<hr>

##### Installation Setup
Please read over the software dependancies above and install and configure <b><em>at least</em></b> your web server (and uWSGI if using it) and database engines. Python3 should already be installed, but if not, go ahead and install that as well. Don't worry about the other Python requirements, we will get to that later in the install. You should be able to connect to your database from the command line and you should be able to get to your web server default webpage. If you cannot, please do not go any further until your resolve any issues you have with those installations.

###### Directory Structure
Here is the overall directory structure that I use with my installation:

```
root@scripts:/var/www/#
└── gardenpi_control
    └── gardenpi
        ├── static
        ├── templates
        └── utilities
```

In the gardenpi_control directory is where ```run.py``` and my ```system_backup.sh``` script lives.

Logs are stored in ```/var/log/gardenpi```

Create the necessary directory structure and change ownership:
```
mkdir -p /var/www/gardenpi_control/
chown www-data:www-data /var/www/gardenpi_control
mkdir /var/log/gardenpi
chown www-data:www-data /var/log/gardenpi
```

All directories should be owned by your web server user, in my case this is ```www-data```.
<hr>

##### Database Configuration for GardenPi
Next you will need to setup your MySQL/OtherSQL database. Once you have installed and secured your SQL installation, add the necessary user (we use a database name of ```neptune``` and a user of ```neptune``` but these can be anything you like. Use the <a href="https://github.com/rjsears/GardenPi/blob/master/neptune.sql">neptune.sql</a> file to get your structure and initial data setup. 

Once you are done with setting up and securing your database engine, then you can grab the neptune.sql file and run the following command:
```
mysql -u root -p"$DATABASE_PASS" neptune < neptune.sql
```
Check your MySQL/OtherSQL settings to make sure that they work for you and the SQL portion setup should be complete.

```
MariaDB [(none)]> use neptune;

Database changed
MariaDB [neptune]> show tables;
+--------------------------+
| Tables_in_neptune        |
+--------------------------+
| electrical_usage         |
| environmental            |
| hydroponic_zones         |
| logging                  |
| power                    |
| power_currently_running  |
| power_scheduled_jobs     |
| power_solar              |
| scheduled_jobs           |
| screen                   |
| systemwide_alerts        |
| systemwide_notifications |
| temperatures             |
| water_source             |
| water_tanks              |
| zones                    |
| zones_currently_running  |
+--------------------------+
17 rows in set (0.001 sec)
```
<hr>

##### External Account Creation
Now, let's create any external accounts that you may need to use for your notifications. If you plan on using email notifications, please remember that your Pi <em>must</em> be configured ahead of time to send emails. This setup will vary based on what MTA you are using. I utilize Postfix, but please read the documentation for your particular MTA and make sure you can send emails from the command line before turning on email notifications. Signup and set up Pushbullet (free) and/or Twilio ($) if you plan on using them for notifications. Make sure to note down your API credentials as we will need them later in the setup. 
<hr>

##### Cloning the Repo
Next, grab the repo via git or download it and place it in the ```/var/www/gardenpi_control``` directory. Once you have done that, we need to modify the system_info.py file. This is the file where all of our database information and API credentials for Email, Twilio, Pushbullet are stored. Make all necessary changes and save the file. 

You <b><em>DO NOT NEED</em></b> the ```images``` or the ```enclosure``` directories in this repo. These just hold information on the overall project build and for the various readme files. You can safely delete these directories after you clone.

Once you have done this, the first thing you need to do is switch into the directory where you have placed the repo and run pip3 against the requirements.txt file:
```pip3 install -r requirements.txt```
This will install all of the current python requirements needed for GardenPi to run.

#### Initial changes to make before starting
These setup instructions assume that you have built your GardenPi system exactly as I have built mine, including that all of your sensors and GPIO expanders are using the same I2C addresses that I am using in my setup. You can change these settings in the various function files as necessary to meet your needs. Take a look in ```zone_controller.py``` for the settings for GPIOs 64 - 95 and in ```power_controller.py``` for GPIOs 96 - 111. 

Likewise, if you are using serial expanders, you would need to modify these two lines in ```/boot/confix.txt``` to meet the needs of both your inturrupt pin as well as your I2C address:
```
dtoverlay=sc16is752-i2c,int_pin=24,addr=0x48
dtoverlay=sc16is752-i2c,int_pin=26,addr=0x4d
```
<hr>
The GardenPi software is written to utilize several other automation platforms that I have installed in our house. These system monitor our water usage with smart water meters and per-circuit power consumption for our AC circuits. The power information is dispayed on the main page of the GardenPi app while the water information is used to calculate and display zone water usage. If you have some type of power monitoring, then you could very easily modify your software to update the 'electrical_usage' table in the GardenPi/neptune database with your ac current and voltage.

##### Modify system_info.py
If you do not have or do not want to use the water and AC power monitoring, make sure these fields in ```system_info.py``` are set to False (the default). 

```
power_monitoring = False
water_monitoring = False
```

When you set these to ```False```, then the interface will just show 0 for water utilization and solar utilization. You could also modify the ```routes.py``` and associated template files to remove that code altogether.


For those of you using EmonCMS to store water data, make the necessary changes to the following variables in ```system_info.py```:

```
## Setup our EmonCMS Database Connection
emoncms_servername = 
emoncms_username = 
emoncms_password = 
emoncms_db = 
```

You will also need to update these variables to point to your specific emon feed:

```
irrigation_gallons_total = "feed_62"
current_gpm = "feed_63"
```

These entires are only good if you have a Rachio sprinkler system:
```
rachio_headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer xxxxxxxxxxxxxxxxxxxxxxxxx'}
rachio_url = 'https://api.rach.io/1/public/device/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxx/current_schedule'
```

If you have a Rachio, make sure to make changes to the following variables:
```
# Used for Sprinkler Bypass
sprinkler_bypass = 'Yes'
sprinkler_type = 'Rachio'  # Timer or Rachio - sprinkler_bypass must be set to "Yes" for this to make any difference
```

Otherwsie make sure to update these variables:
```
# Set Sprinkler start and stop times here if using 'Timer' setting above.
sprinklerstart = '04:00:00'
sprinklerstop = '06:00:00'
```

Finally, since we use SQLAlchemy, you need to modify the following line to suit your setup:
```
# SQLAlchemy URI Info
sqlalchemy_db_uri = 'mysql+mysqlconnector://neptune:your_secret_password@gardenpi/neptune'
```
<hr>

#### Kiosk Mode Setup
If you are using a touchscreen with your GardenPi installation, there are sereral things you need to do in order for it to work properly and to be able to switch back and forth via the web interface. Fist, you need to make sure your X is configured properly. I have included my ```lightdm.conf``` and the display setup script to rotate the display automaticaly to the verticle position. You will see this display script reference on line 120 of the lightdm configuration file: ```display-setup-script=/usr/share/dispsetup.sh``` 

Place the ```dispsetup.sh``` script in ```/usr/share``` directory, the ```lightdm.cnf``` file in the ```/etc/lightdm``` directory and you are ready to move on to the next step.

Next we want to be able to switch between kiosk mode and regular desktop mode via our interface. To do this, we need to make some system configuration changes and copy some files around as well as allow the changes to be done by our web server user. 

First, make sure the following directory exists:
```/home/pi/.config/lxsession/LXDE-pi```
Once that directory exists, copy the file ```autostart``` from the repo into that directory. Next, place the ```gardenpi_desktop.sh``` script from the repo into a directory of your choosing. Modify like 877 of ```neptune.py``` to point to that directory:

```subprocess.check_call(['sudo', '/usr/bin/gardenpi_desktop.sh', 'gardenpi'])```

Once that has been completed, you need to modify your ```/etc/sudoers``` file to allow your web server user the ability to execute that script by adding this line to the bottom of the file:
```www-data ALL = NOPASSWD: /usr/bin/gardenpi_desktop.sh```
This assumes that your web server runs as ```www-data```, if not, use the appropriate account here.

Once you are done with all of that, reboot and test your setup. Your screen should come up in verticle orientation and you should be able to toggle between Desktop and Kiosk mode from the web interface.

#### Reboot and Halt from Web Interface
GardePi has the ability to reboot or halt your Pi from the GUI web interface, but in order for this to work, we need to modify the ```/etc/sudoers``` file by adding in the following lines at the bottom of the file:
```
www-data ALL = NOPASSWD: /sbin/halt
www-data ALL = NOPASSWD: /sbin/shutdown
```
The Halt and reboot functions should now work from the web interface. This assumes that your web server runs as ```www-data```, if not, use the appropriate account here.

#### <a name="schematics"></a>Electrical Schematics
Here are the system electrical schematics for GardenPi

<img src="https://github.com/rjsears/GardenPi/blob/master/images/gardenpi_schematics_page1%20.jpg" alt="GardenPi Schematics Page 1" height="600" width="1000"><br>
<img src="https://github.com/rjsears/GardenPi/blob/master/images/gardenpi_schematics_page2.jpg" alt="GardenPi Schematics Page 2" height="600" width="1000"><br>
<img src="https://github.com/rjsears/GardenPi/blob/master/images/gardenpi_schematics_page3.jpg" alt="GardenPi Schematics Page 3" height="600" width="1000"><br>


#### In Conclusion
I hope these instructions are enough to get you started on your project. As time permits I will be updating the code to make it mode modular at the system level, but until then, someone using this software will have to take the time to go through the code and modify it to meet their needs. I will do what I can to help, please just open an issue and I will do what I can to help out. Check back here often as I expand this readme and the install instruction as I make modifications to make things (installing and running) easier. 

Also, take a minute to check out the <a href="https://github.com/rjsears/GardenPi/blob/master/GardenPi/utilities/system_backup_restore/system_backup.sh">"system backup and restore script"</a>. This is the utility that I wrote to backup a fully operational GardenPi instance including every configuration file needed to make gardenPi run and to restore it to a new Pi OS image automatically. I will be writing the basic readme soon with full instruction to follow. If you look at the code carefully, in the restore functionality you will find absolutely everything that I do to restore the image, what software is installed,   


#### <a name="icons"></a>GardenPi Icons
There are a LOT of icons in GardenPi. I could not have done such a good job without the help of <a href="https://www.flaticon.com/">FlatIcon.com</a>. If you ever need an icon, check them out. All of the icons here at GardenPi were free from FlatIcon!


