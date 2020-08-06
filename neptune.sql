-- MySQL dump 10.17  Distrib 10.3.22-MariaDB, for debian-linux-gnueabihf (armv8l)
--
-- Host: localhost    Database: neptune
-- ------------------------------------------------------
-- Server version	10.3.22-MariaDB-0+deb10u1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `electrical_usage`
--

DROP TABLE IF EXISTS `electrical_usage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `electrical_usage` (
  `dc_voltage` decimal(3,2) NOT NULL,
  `dc_current` decimal(7,3) NOT NULL,
  `dc_power` decimal(7,3) NOT NULL,
  `dc_shunt_voltage` decimal(7,3) NOT NULL,
  `ac_current` decimal(4,2) NOT NULL,
  `ac_voltage` decimal(5,2) NOT NULL,
  PRIMARY KEY (`dc_voltage`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `electrical_usage`
--

LOCK TABLES `electrical_usage` WRITE;
/*!40000 ALTER TABLE `electrical_usage` DISABLE KEYS */;
INSERT INTO `electrical_usage` VALUES (5.07,1.185,6.593,12.260,0.24,119.80);
/*!40000 ALTER TABLE `electrical_usage` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `environmental`
--

DROP TABLE IF EXISTS `environmental`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `environmental` (
  `pi_cpu_temp` decimal(4,1) NOT NULL,
  `enclosure_temp` decimal(4,1) NOT NULL,
  `enclosure_humidity` decimal(3,1) NOT NULL,
  `enclosure_baro` decimal(4,2) NOT NULL,
  `shed_temp` decimal(4,1) NOT NULL,
  `shed_humidity` decimal(3,1) NOT NULL,
  `outdoor_temperature` decimal(4,1) NOT NULL,
  `sprinklers_running` tinyint(1) NOT NULL,
  PRIMARY KEY (`pi_cpu_temp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `environmental`
--

LOCK TABLES `environmental` WRITE;
/*!40000 ALTER TABLE `environmental` DISABLE KEYS */;
INSERT INTO `environmental` VALUES (163.5,121.0,6.0,28.50,131.8,7.4,111.2,0);
/*!40000 ALTER TABLE `environmental` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `hydroponic_zones`
--

DROP TABLE IF EXISTS `hydroponic_zones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hydroponic_zones` (
  `zone_name` varchar(15) COLLATE utf8_unicode_ci NOT NULL,
  `zone_number` tinyint(4) NOT NULL,
  `description` varchar(40) COLLATE utf8_unicode_ci NOT NULL,
  `gpio` tinyint(1) NOT NULL,
  `enabled` tinyint(1) NOT NULL,
  `running` tinyint(1) NOT NULL,
  `running_manually` tinyint(1) NOT NULL,
  `gallons_start` int(11) NOT NULL,
  `gallons_stop` int(11) NOT NULL,
  `gallons_current_run` int(11) NOT NULL,
  `gallons_last_run` int(11) NOT NULL,
  `total_gallons_used` int(11) NOT NULL,
  `mcp` varchar(4) COLLATE utf8_unicode_ci NOT NULL,
  `notifications` tinyint(1) NOT NULL,
  `sms` tinyint(1) NOT NULL,
  `pb` tinyint(1) NOT NULL,
  `email` tinyint(1) NOT NULL,
  PRIMARY KEY (`zone_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `hydroponic_zones`
--

LOCK TABLES `hydroponic_zones` WRITE;
/*!40000 ALTER TABLE `hydroponic_zones` DISABLE KEYS */;
INSERT INTO `hydroponic_zones` VALUES ('zone10',10,'Fish Tank Output to Holding Tank',73,1,0,0,0,0,0,0,0,'mcp0',0,0,0,0),('zone11',11,'Fish Tank Return',74,1,0,0,0,0,0,0,0,'mcp0',0,0,0,0),('zone12',12,'Feed From Sump',75,1,0,0,0,0,0,0,0,'mcp0',0,0,0,0),('zone13',13,'From Tank Water Change Line',76,1,0,0,0,0,0,0,0,'mcp0',0,0,0,0),('zone14',14,'From RODI Clean Water Tank',77,1,0,0,0,0,0,0,0,'mcp0',0,0,0,0),('zone15',15,'From Sump to Chiller',78,1,0,0,0,0,0,0,0,'mcp0',0,0,0,0),('zone16',16,'From Fish Water Tank',79,1,0,0,0,0,0,0,0,'mcp0',0,0,0,0),('zone17',17,'From Nutrient Tank',80,1,0,0,0,0,0,0,0,'mcp1',0,0,0,0),('zone18',18,'From RODI Tank',81,1,0,0,0,0,0,0,0,'mcp1',0,0,0,0),('zone19',19,'Recirculation to RODI Tank',82,1,0,0,0,0,0,0,0,'mcp1',0,0,0,0),('zone20',20,'Recirculation to Fish Water Tank',83,1,0,0,0,0,0,0,0,'mcp1',0,0,0,0),('zone21',21,'Recirculation to Nutrient Tank',84,1,0,0,0,0,0,0,0,'mcp1',0,0,0,0),('zone22',22,'Out To Chiller Input',85,1,0,0,0,0,0,0,0,'mcp1',0,0,0,0),('zone23',23,'Holding Tanks output to Drain',86,1,0,0,0,0,0,0,0,'mcp1',0,0,0,0),('zone24',24,'Chiller to Fish Water Return',87,1,0,0,0,0,0,0,0,'mcp1',0,0,0,0),('zone25',25,'Chiller to RODI Tank Return',88,1,0,0,0,0,0,0,0,'mcp1',0,0,0,0),('zone26',26,'Chiller to Nutrient Tank Return',89,1,0,0,0,0,0,0,0,'mcp1',0,0,0,0),('zone27',27,'Chiller to Sump Return',90,1,0,0,0,0,0,0,0,'mcp1',0,0,0,0),('zone28',28,'Fresh Water to RODI System',91,1,0,0,0,0,0,0,0,'mcp1',1,1,1,1),('zone9',9,'Fish Tank  Output to Drain',72,1,0,0,0,0,0,0,0,'mcp0',0,0,0,0);
/*!40000 ALTER TABLE `hydroponic_zones` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `logging`
--

DROP TABLE IF EXISTS `logging`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `logging` (
  `console` tinyint(1) NOT NULL,
  `system_logging` tinyint(1) NOT NULL,
  `log_level` varchar(8) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`console`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `logging`
--

LOCK TABLES `logging` WRITE;
/*!40000 ALTER TABLE `logging` DISABLE KEYS */;
INSERT INTO `logging` VALUES (1,1,'DEBUG');
/*!40000 ALTER TABLE `logging` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `power`
--

DROP TABLE IF EXISTS `power`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `power` (
  `zone_name` varchar(15) COLLATE utf8_unicode_ci NOT NULL,
  `zone_number` tinyint(4) NOT NULL,
  `description` varchar(40) COLLATE utf8_unicode_ci NOT NULL,
  `gpio` tinyint(1) NOT NULL,
  `enabled` tinyint(1) NOT NULL,
  `running` tinyint(1) NOT NULL,
  `running_manually` tinyint(1) NOT NULL,
  `mcp` varchar(4) COLLATE utf8_unicode_ci NOT NULL,
  `notifications` tinyint(1) NOT NULL,
  `sms` tinyint(1) NOT NULL,
  `pb` tinyint(1) NOT NULL,
  `email` tinyint(1) NOT NULL,
  PRIMARY KEY (`zone_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `power`
--

LOCK TABLES `power` WRITE;
/*!40000 ALTER TABLE `power` DISABLE KEYS */;
INSERT INTO `power` VALUES ('exhaust_fan',10,'Exhaust Cooling Fan',105,1,1,1,'mcp2',1,0,0,1),('intake_fan',9,'Intake Cooling Fan',104,1,1,1,'mcp2',1,0,0,1),('power1',1,'Power Outlet 1',96,1,0,0,'mcp2',1,0,0,1),('power2',2,'Power Outlet 2',97,1,0,0,'mcp2',1,1,1,1),('power3',3,'Power Outlet 3',98,1,0,0,'mcp2',1,1,1,1),('power4',4,'Power Outlet 4',99,1,0,0,'mcp2',1,1,1,1),('power5',5,'Power Outlet 5',100,1,0,0,'mcp2',1,1,1,1),('power6',6,'Power Outlet 6',101,1,0,0,'mcp2',1,1,1,1),('power7',7,'Water Pump for old fish water',102,1,0,0,'mcp2',1,1,1,1),('power8',8,'Sprinkler Transformer 110v Power',103,1,0,0,'mcp2',0,0,0,0);
/*!40000 ALTER TABLE `power` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `power_currently_running`
--

DROP TABLE IF EXISTS `power_currently_running`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `power_currently_running` (
  `zone_name` varchar(15) COLLATE utf8_unicode_ci NOT NULL,
  `currently_running` tinyint(1) NOT NULL,
  `run_manually` tinyint(1) NOT NULL,
  `run_by_job` tinyint(1) NOT NULL,
  `job_id` tinyint(4) NOT NULL,
  `forced_stopped` tinyint(1) NOT NULL,
  PRIMARY KEY (`zone_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `power_currently_running`
--

LOCK TABLES `power_currently_running` WRITE;
/*!40000 ALTER TABLE `power_currently_running` DISABLE KEYS */;
INSERT INTO `power_currently_running` VALUES ('power1',0,0,0,0,0),('power2',0,0,0,0,0),('power3',0,0,0,0,0),('power4',0,0,0,0,0),('power5',0,0,0,0,0),('power6',0,0,0,0,0),('power7',0,0,0,0,0);
/*!40000 ALTER TABLE `power_currently_running` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `power_scheduled_jobs`
--

DROP TABLE IF EXISTS `power_scheduled_jobs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `power_scheduled_jobs` (
  `job_id` int(11) NOT NULL AUTO_INCREMENT,
  `zone` varchar(15) COLLATE utf8_unicode_ci NOT NULL,
  `zone_job` tinyint(1) NOT NULL,
  `job_enabled` tinyint(1) NOT NULL,
  `job_start_time` time NOT NULL,
  `job_stop_time` time NOT NULL,
  `job_duration` smallint(6) NOT NULL,
  `job_running` tinyint(1) NOT NULL,
  `monday` tinyint(1) NOT NULL,
  `tuesday` tinyint(1) NOT NULL,
  `wednesday` tinyint(1) NOT NULL,
  `thursday` tinyint(1) NOT NULL,
  `friday` tinyint(1) NOT NULL,
  `saturday` tinyint(1) NOT NULL,
  `sunday` tinyint(1) NOT NULL,
  `forced_stop_manually` tinyint(1) NOT NULL,
  PRIMARY KEY (`job_id`),
  KEY `zone` (`zone`),
  CONSTRAINT `power_scheduled_jobs_ibfk_1` FOREIGN KEY (`zone`) REFERENCES `power` (`zone_name`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `power_scheduled_jobs`
--

LOCK TABLES `power_scheduled_jobs` WRITE;
/*!40000 ALTER TABLE `power_scheduled_jobs` DISABLE KEYS */;
INSERT INTO `power_scheduled_jobs` VALUES (1,'power1',1,0,'16:25:00','16:27:00',2,0,1,1,1,1,1,1,1,0),(2,'power1',2,0,'10:05:00','10:10:00',5,0,1,1,1,1,1,1,1,0),(3,'power2',1,0,'07:10:00','07:15:00',5,0,1,1,1,1,1,1,1,0),(4,'power2',2,0,'19:10:00','19:15:00',5,0,1,1,1,1,1,1,1,0),(5,'power3',1,0,'07:15:00','07:20:00',5,0,1,1,1,1,1,1,1,0),(6,'power3',2,0,'19:15:00','19:20:00',5,0,1,1,1,1,1,1,1,0),(7,'power4',1,0,'07:20:00','07:25:00',5,0,1,1,1,1,1,1,1,0),(8,'power4',2,0,'19:20:00','19:25:00',5,0,1,1,1,1,1,1,1,0),(9,'power5',1,0,'07:25:00','07:30:00',5,0,1,1,1,1,1,1,1,0),(10,'power5',2,0,'19:25:00','19:30:00',5,0,1,1,1,1,1,1,1,0),(11,'power6',1,0,'07:30:00','07:35:00',5,0,1,1,1,1,1,1,1,0),(12,'power6',2,0,'23:30:00','23:35:00',5,0,1,1,1,1,1,1,1,0),(13,'power7',1,0,'07:30:00','07:35:00',5,0,1,1,1,1,1,1,1,0),(14,'power7',2,0,'23:30:00','23:35:00',5,0,1,1,1,1,1,1,1,0);
/*!40000 ALTER TABLE `power_scheduled_jobs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `power_solar`
--

DROP TABLE IF EXISTS `power_solar`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `power_solar` (
  `total_current_power_utilization` smallint(6) NOT NULL,
  `total_current_power_import` smallint(6) NOT NULL,
  `total_current_solar_production` smallint(6) NOT NULL,
  PRIMARY KEY (`total_current_power_utilization`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `power_solar`
--

LOCK TABLES `power_solar` WRITE;
/*!40000 ALTER TABLE `power_solar` DISABLE KEYS */;
INSERT INTO `power_solar` VALUES (5779,4659,1120);
/*!40000 ALTER TABLE `power_solar` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `scheduled_jobs`
--

DROP TABLE IF EXISTS `scheduled_jobs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `scheduled_jobs` (
  `job_id` int(11) NOT NULL AUTO_INCREMENT,
  `zone` varchar(15) COLLATE utf8_unicode_ci NOT NULL,
  `zone_job` tinyint(1) NOT NULL,
  `job_enabled` tinyint(1) NOT NULL,
  `job_start_time` time NOT NULL,
  `job_stop_time` time NOT NULL,
  `job_duration` tinyint(4) NOT NULL,
  `job_running` tinyint(1) NOT NULL,
  `monday` tinyint(1) NOT NULL,
  `tuesday` tinyint(1) NOT NULL,
  `wednesday` tinyint(1) NOT NULL,
  `thursday` tinyint(1) NOT NULL,
  `friday` tinyint(1) NOT NULL,
  `saturday` tinyint(1) NOT NULL,
  `sunday` tinyint(1) NOT NULL,
  `forced_stop_manually` tinyint(1) NOT NULL,
  PRIMARY KEY (`job_id`),
  KEY `zone` (`zone`),
  CONSTRAINT `scheduled_jobs_ibfk_1` FOREIGN KEY (`zone`) REFERENCES `zones` (`zone_name`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `scheduled_jobs`
--

LOCK TABLES `scheduled_jobs` WRITE;
/*!40000 ALTER TABLE `scheduled_jobs` DISABLE KEYS */;
INSERT INTO `scheduled_jobs` VALUES (1,'zone1',1,1,'07:00:00','07:03:00',3,0,1,1,1,1,1,1,1,0),(2,'zone1',2,1,'19:00:00','19:03:00',3,0,1,1,1,1,1,1,1,0),(3,'zone2',1,1,'07:05:00','07:07:00',2,0,1,1,1,1,1,1,1,0),(4,'zone2',2,1,'19:05:00','19:07:00',2,0,1,1,1,1,1,1,1,0),(5,'zone3',1,1,'07:10:00','07:12:00',2,0,1,1,1,1,1,1,1,0),(6,'zone3',2,1,'19:10:00','19:12:00',2,1,1,1,1,1,1,1,1,0),(7,'zone4',1,1,'07:15:00','07:17:00',2,0,1,1,1,1,1,1,1,0),(8,'zone4',2,1,'19:15:00','19:17:00',2,0,1,1,1,1,1,1,1,0),(9,'zone5',1,1,'07:20:00','07:23:00',3,0,1,1,1,1,1,1,1,0),(10,'zone5',2,1,'19:20:00','19:23:00',3,0,1,1,1,1,1,1,1,0),(11,'zone6',1,1,'07:30:00','07:35:00',5,0,1,1,1,1,1,1,1,0),(12,'zone6',2,1,'19:30:00','19:35:00',5,0,1,1,1,1,1,1,1,0);
/*!40000 ALTER TABLE `scheduled_jobs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `screen`
--

DROP TABLE IF EXISTS `screen`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `screen` (
  `kioskmode` tinyint(1) NOT NULL,
  PRIMARY KEY (`kioskmode`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `screen`
--

LOCK TABLES `screen` WRITE;
/*!40000 ALTER TABLE `screen` DISABLE KEYS */;
INSERT INTO `screen` VALUES (1);
/*!40000 ALTER TABLE `screen` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `systemwide_alerts`
--

DROP TABLE IF EXISTS `systemwide_alerts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `systemwide_alerts` (
  `sensor_name` varchar(20) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `notifications` tinyint(1) NOT NULL,
  `sms` tinyint(1) NOT NULL,
  `pb` tinyint(1) NOT NULL,
  `email` tinyint(1) NOT NULL,
  `alert_limit` decimal(4,1) NOT NULL,
  `alert_sent` tinyint(1) NOT NULL,
  PRIMARY KEY (`sensor_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `systemwide_alerts`
--

LOCK TABLES `systemwide_alerts` WRITE;
/*!40000 ALTER TABLE `systemwide_alerts` DISABLE KEYS */;
INSERT INTO `systemwide_alerts` VALUES ('ac_circuit_max_amps',1,1,0,1,13.0,0),('ac_minimum_volts',1,0,0,1,116.0,0),('dc_max_amps',1,0,0,1,5.0,0),('dc_minimum_volts',1,0,0,1,4.8,0),('enclosure_max_temp',1,0,0,1,140.0,0),('pi_max_cpu_temp',1,0,0,1,175.0,0),('worm_farm_max_temp',1,1,0,1,82.0,0);
/*!40000 ALTER TABLE `systemwide_alerts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `systemwide_notifications`
--

DROP TABLE IF EXISTS `systemwide_notifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `systemwide_notifications` (
  `enabled` tinyint(1) NOT NULL,
  `sms` tinyint(1) NOT NULL,
  `pb` tinyint(1) NOT NULL,
  `email` tinyint(1) NOT NULL,
  PRIMARY KEY (`enabled`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `systemwide_notifications`
--

LOCK TABLES `systemwide_notifications` WRITE;
/*!40000 ALTER TABLE `systemwide_notifications` DISABLE KEYS */;
INSERT INTO `systemwide_notifications` VALUES (1,1,1,1);
/*!40000 ALTER TABLE `systemwide_notifications` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `temperatures`
--

DROP TABLE IF EXISTS `temperatures`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `temperatures` (
  `temp_zone` varchar(17) COLLATE utf8_unicode_ci NOT NULL,
  `onewire_id` varchar(17) COLLATE utf8_unicode_ci NOT NULL,
  `current_temp` decimal(4,1) NOT NULL,
  `enabled` tinyint(1) NOT NULL,
  PRIMARY KEY (`temp_zone`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `temperatures`
--

LOCK TABLES `temperatures` WRITE;
/*!40000 ALTER TABLE `temperatures` DISABLE KEYS */;
INSERT INTO `temperatures` VALUES ('fish_water','28-01192a024197',114.3,1),('fishtank_sump','28-01192a1fd434',115.0,1),('hydroponic_tank','28-01192a52b3fa',114.1,1),('rodi_water','28-0119299e87c5',115.0,1),('worm_farm','28-01192a04062d',80.0,1);
/*!40000 ALTER TABLE `temperatures` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `water_source`
--

DROP TABLE IF EXISTS `water_source`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `water_source` (
  `selected_source` varchar(15) COLLATE utf8_unicode_ci NOT NULL,
  `fish_available` tinyint(1) NOT NULL,
  `job_water_source` varchar(15) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`selected_source`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `water_source`
--

LOCK TABLES `water_source` WRITE;
/*!40000 ALTER TABLE `water_source` DISABLE KEYS */;
INSERT INTO `water_source` VALUES ('automatic_water',0,'fresh_water');
/*!40000 ALTER TABLE `water_source` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `water_tanks`
--

DROP TABLE IF EXISTS `water_tanks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `water_tanks` (
  `tank_name` varchar(20) COLLATE utf8_unicode_ci NOT NULL,
  `description` varchar(40) COLLATE utf8_unicode_ci NOT NULL,
  `tty` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `enabled` tinyint(1) NOT NULL,
  `current_level_inches` decimal(3,1) NOT NULL,
  `current_volume_gallons` int(11) NOT NULL,
  `gallons_per_inch` decimal(2,1) NOT NULL,
  `max_tank_volume` int(11) NOT NULL,
  `tank_empty_depth` int(11) NOT NULL,
  PRIMARY KEY (`tank_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `water_tanks`
--

LOCK TABLES `water_tanks` WRITE;
/*!40000 ALTER TABLE `water_tanks` DISABLE KEYS */;
INSERT INTO `water_tanks` VALUES ('fishtanksump_tank','Fish tank sump','ttySC3',1,0.0,0,0.0,0,0),('fishwater_tank','Tank that holds used fish tank water','ttySC0',1,40.0,200,8.2,328,40),('hydroponic_tank','Holding tank for nutrient water','ttySC2',1,0.0,50,2.0,75,25),('rodiwater_tank','Fresh RODI water for fish tank','ttySC1',1,0.0,300,8.2,328,40);
/*!40000 ALTER TABLE `water_tanks` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `zones`
--

DROP TABLE IF EXISTS `zones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `zones` (
  `zone_name` varchar(15) COLLATE utf8_unicode_ci NOT NULL,
  `zone_number` tinyint(4) NOT NULL,
  `description` varchar(40) COLLATE utf8_unicode_ci NOT NULL,
  `gpio` tinyint(1) NOT NULL,
  `enabled` tinyint(1) NOT NULL,
  `running` tinyint(1) NOT NULL,
  `running_manually` tinyint(1) NOT NULL,
  `gallons_start` int(11) NOT NULL,
  `gallons_stop` int(11) NOT NULL,
  `gallons_current_run` int(11) NOT NULL,
  `gallons_last_run` int(11) NOT NULL,
  `total_gallons_used` int(11) NOT NULL,
  `mcp` varchar(4) COLLATE utf8_unicode_ci NOT NULL,
  `notifications` tinyint(1) NOT NULL,
  `sms` tinyint(1) NOT NULL,
  `pb` tinyint(1) NOT NULL,
  `email` tinyint(1) NOT NULL,
  PRIMARY KEY (`zone_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `zones`
--

LOCK TABLES `zones` WRITE;
/*!40000 ALTER TABLE `zones` DISABLE KEYS */;
INSERT INTO `zones` VALUES ('fish_water',8,'Fish Water Supply',71,1,0,0,1187360,1187360,0,0,0,'mcp0',1,0,0,0),('fresh_water',7,'Fresh Water Supply',70,1,0,0,1253780,1253790,0,10,1314,'mcp0',1,0,0,0),('zone1',1,'Back & Side of House',64,1,0,0,1253740,1253760,0,20,660,'mcp0',1,0,0,1),('zone2',2,'Currently Unused & Disconnected',65,0,0,0,1229630,1229630,0,0,0,'mcp0',1,1,0,0),('zone3',3,'Large Planter Boxes by Shed',66,1,0,0,1253760,1253770,0,10,270,'mcp0',1,0,0,1),('zone4',4,'Shallow Watering',67,1,0,0,1253770,1253780,0,10,180,'mcp0',1,0,0,1),('zone5',5,'Main Garden',68,1,0,0,1253780,1253790,0,10,234,'mcp0',1,0,0,1),('zone6',6,'Currently Unused & Disconnected',69,0,0,0,1247860,1247860,0,0,0,'mcp0',1,0,0,1);
/*!40000 ALTER TABLE `zones` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `zones_currently_running`
--

DROP TABLE IF EXISTS `zones_currently_running`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `zones_currently_running` (
  `currently_running` tinyint(1) NOT NULL,
  `run_manually` tinyint(1) NOT NULL,
  `run_by_job` tinyint(1) NOT NULL,
  `job_id` tinyint(4) NOT NULL,
  `force_stopped` tinyint(1) NOT NULL,
  PRIMARY KEY (`currently_running`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `zones_currently_running`
--

LOCK TABLES `zones_currently_running` WRITE;
/*!40000 ALTER TABLE `zones_currently_running` DISABLE KEYS */;
INSERT INTO `zones_currently_running` VALUES (0,0,0,0,0);
/*!40000 ALTER TABLE `zones_currently_running` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-08-06 15:03:36
