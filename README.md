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

First, create any other accounts that you may need to use for your notifications. If you plan on using email notifications, please remember that your server must be configured ahead of time to send emails. This will vary based on what MTA you are using. I utilize Postfix, but please read the documentation for your particular MTA and make sure you can send emails from the command line before turning on email notifications. Signup and set up Pushbullet (free) and/or Twilio ($) if you plan on using them for notifications. Make sure to note down your API credentials as we will need them later in the setup. 

Here is the directory structure that I use with my installation:

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

Create the necessary directories and change ownership:
```
mkdir -p /var/www/gardenpi_control/
chown www-data:www-data /var/www/gardenpi_control
mkdir /var/log/gardenpi
chown www-data:www-data /var/log/gardenpi
```

All directories should be owned by your web server user, in my case that is ```www-data```.

Once that is done and before we get started with the repo itself, we need to make sure all of our basic software has been installed. Before going any further, please install and <em>test/<em> the following packages:
<ul>
  <li>Web Server Software - If using Nginx, the <a href="https://github.com/rjsears/GardenPi/blob/master/gardenpi.conf">gardenpi.conf</a> file above should work for you.</li>
  <li>uWSGI - needed for Flask</li>
  <li>MySQL or other SQL engine & libraries</li>
  <li>InfluxDB - If you plan on using it</li>
  <li>Grafana - If you plan on using it</li>
</ul>

Next you will need to setup your MySQL/OtherSQL database. Add the necessary user (we use a database name of ```neptune``` and a user of ```neptune``` but these can be anything you like. Use the <a href="https://github.com/rjsears/GardenPi/blob/master/neptune.sql">neptune.sql</a> file to get your structure and initial data setup. 
Here is the basic setup of MySQ. First login to MySQL:
```
root gardenpi: ~ #  mysql -u root -p
Enter password: 
Welcome to the MariaDB monitor.  Commands end with ; or \g.
Your MariaDB connection id is 196236
Server version: 10.3.22-MariaDB-0+deb10u1 Raspbian 10

Copyright (c) 2000, 2018, Oracle, MariaDB Corporation Ab and others.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

MariaDB [(none)]>
```
From there, you can run the following commands to create teh neptune database. Don't forget to replace the 'PASS" fields with a password of your choice:
```
UPDATE mysql.user SET Password=PASSWORD('$DATABASE_PASS') WHERE User='root';
DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');
DELETE FROM mysql.user WHERE User='';
DELETE FROM mysql.db WHERE Db='test' OR Db='test\_%';
FLUSH PRIVILEGES;
CREATE DATABASE neptune /*\!40100 DEFAULT CHARACTER SET utf8 */;
CREATE USER neptune@localhost IDENTIFIED BY '$NEPTUNE_DB_PASS';
GRANT ALL PRIVILEGES ON neptune.* TO 'neptune'@'localhost';
FLUSH PRIVILEGES;
```
Once you are done with that, then you can grab the neptune.sql file and run the following command:
```
mysql -u root -p"$DATABASE_PASS" neptune < neptune.sql
```
Check yur MySQL/OtherSQL setting to make sure that they work for you and the SQL portion setup should be complete.




My goal is to have multiple tanks being monitored so you may end up wanting to change the name, etc. If you do, please make sure you modify all the database calls to point to the correct database. This is setup in the <a href="https://github.com/rjsears/GardenPi/blob/master/GardenPi/utilities/system_info.py">system_info.py</a> file and we will modify that once we get the repo.

Next, grab the repo via git or download it above and place it in the ```/var/www/gardenpi_control``` directory. Once you have done that, we need to modify the system_info.py file. This is the file where all of our database information and API credentials for Email, Twilio, Pushbullet are stored. Make all necessary changes and save the file. 

Once you have completed all of these steps, you can change into your base directory and run the test flask file:


