<h2 align="center">
  <a name="gardenpi_logo" href="https://github.com/rjsears/GardenPi"><img src="https://github.com/rjsears/GardenPi/blob/master/images/gardenpi_cover.jpg" alt="GardenPi" height="600" width="500"></a>
  <br>
  GardenPi (V1.0.0 - August 3rd, 2020)
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
GardenPi, powered by Neptune.py is designed to manage, monitor and control a series or sprinkler valves and a multitide of sensors for pretty much any sized irrigation / hydroponic / aquaponic project. It can be scaled (using the hardware I used) from 1 to 32 zones for water and 7 zones for power. It is built almost entirely in Python3 with a Flask web interface and releys on a lot of css to make the interface very fast. It is written and designed to run on the Raspberry Pi 4.  

Hopefully, this might provide some inspiration for others in regard to their automation projects. Contributions are always welcome.</p>
<div align="center"><a name="top_menu"></a>
  <h4>
    <a href="https://github.com/rjsears/GardenPi#overview">
      Overview
    </a>
    <span> | </span>
    <a href="https://github.com/rjsears/GardenPi/blob/master/enclosure/readme.md">
      Pieces & Parts
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
    <a href="https://github.com/rjsears/GardenPi/tree/master/gardenpi">
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
  </h4>
</div>

<hr>

#### <a name="overview"></a>Overview & Theory of Operation
GardenPi was designed around my family's desire to get more heavily into gardening, hydroponics, and eventually aquaponics. Since we have several fish tanks and do large water changes weekly, we wanted to be able to use that nutrient-rich water for the garden instead of just dumping it down the drain. So weekly my wife would have to cart fish tank water around the garden beds to water the plants manually and then switch back to a hose. This was getting very time consuming and tedious. Because of that, the basic concept of GardenPi was born.

The gardening part would have been pretty easy, we could have used a simple irrigation controller but as you can see we needed several water sources, in our case freshwater (street water) and water from our fish tanks and standard irrigation controllers did not provide the functions we needed to manage the process of moving back and forth between water sources. So I designed a new irrigation layout and my sons and I dug up the yard and installed six separate garden irrigation zones separate from our lawn irrigation and installed valves so we could switch between street water and an IBC tank filled with fish tank water. Now I just needed the software to manage it all.

As with any project, I wanted to look more long term. Our family sat down and talked about what we really wanted to do. One was to get into much larger fish tanks ~200-500 gallons), greatly expand our garden to provide more space for year-around growing (we live in Phoenix), start to dabble into full hydroponics and eventually move into full aquaponics and eliminate street water gardening altogether, relying 100% on old fishtank & aquaponic wastewater instead. Street water would be managed by a RODI system and fed into the fish and aquaponic tanks and all plant water would come from the fish. As you can imagine this would require quite a bit of management and thinking ahead and out-of-the-box.

The system designed for <em>our<em> needs ended up with the following configuration:
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
</ul>

In additional to these zones/sensors, the system would also interact directly with our already installed power and water monitoring systems. This system were build on EmonCMS which is part of the OpenEnergy Project. We use our EmonCMS data to gather water utilization information for GardenPi via smart water meters on our property and do the same for monitoring the AC circuit utilization for GardenPi. Other data such as outside temperature and humidity is likewise drawn from an outside source, namely a David Vantage PRO2 system we have installed on the property.

This is the overview of how the system will be put together:<br><br>
<img src="https://github.com/rjsears/GardenPi/blob/master/images/gardenpi_physical_20200803.jpg" alt="GardenPi Physical Layout" height="600" width="800"></a>
<br><br>
The goal of version 1.0.0 of GardenPi was to build and test the hardware and get the garden irrigation, sensor readings, and automatic water switching installed and working. As I progress with other versions I will continue to build out all other functionality as we continue to build out our gardens, hydroponics and aquaponics. 

GardenPi is very flexable in regards to what you use, how many zones you want, if you want power zones, etc. If you have specific questions about the code or how things are put together, fell free to open an issue and I will do my best to help.

<hr>
<em>PLEASE NOTE: This project <b>IS NOT</b> intended to be a "plug-and-play" installation, rather a starting point for someone that wants to use all (or part) of the repo to monitor and manage their irrigation system(s).  There <u>will be</u> significant modifications required by the user even if they are using a clean Pi install. Things in the code such as smart water monitoring and electrical monitoring are integrated with other sensors and automation platforms that I am currently using. I will try my best to point these areas out, but if you do not use those things, major code changes will have to be made to make GardenPi work <u>for you</u>. If you are not comfortable using Python and making these types of changes, this project might not be for you. 
  
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
Next you will need to setup your MySQL/OtherSQL database. Add the necessary user (we use a database name of ```neptune``` and a user of ```neptune``` but these can be anything you like. Use the <a href="https://github.com/rjsears/GardenPi/blob/master/neptune.sql">neptune.sql</a> file to get your structure and initial data setup. 

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
Next, grab the repo via git or download it above and place it in the ```/var/www/gardenpi_control``` directory. Once you have done that, we need to modify the system_info.py file. This is the file where all of our database information and API credentials for Email, Twilio, Pushbullet are stored. Make all necessary changes and save the file. 

The GardenPi software is written to utilize several other automation platforms that I have installed in our house. 

Once you have completed all of these steps, you can change into your base directory and run the test flask file:


