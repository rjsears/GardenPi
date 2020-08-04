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
GardenPi runs on the Raspberry Pi4. The following software is what I am using and to the extent you can replace the functionality with something else (apache vs nginx, for example) it should work fine. This is just what I chose to use. This is the base software, please see <a href="https://github.com/rjsears/GardenPi/blob/master/GardenPi/requirements.txt">equirements.txt</a> for a list of necessary python libraries needed to run GardenPi. If you are going to run GardenPi and the system backup and restore utility for GardenPi, you will need all of these programs:


<ul>
  <li>Lastest Version of the Raspberry Pi OS - Full version with Desktop</li>
  <li>Python3</li>
  <li>Nginx</li>
  <li>MarinaDB</li>
  <li>uWsgi & uWsgi Emperor</li>
  <li>Locate</li>
  <li>Unclutter - Used to hide mouse in Kiosk mode</li>
  <li>wGet</li>
  <li>Postfix (or other MAT) - Used for sending email notifications</li>
</ul>
