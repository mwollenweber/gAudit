-- MySQL dump 10.13  Distrib 5.5.38, for osx10.10 (x86_64)
--
-- Host: localhost    Database: gAudit
-- ------------------------------------------------------
-- Server version	5.5.38

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `gAudit`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `gAudit` /*!40100 DEFAULT CHARACTER SET latin1 */;

USE `gAudit`;

--
-- Table structure for table `authorizationfiles`
--

DROP TABLE IF EXISTS `authorizationfiles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `authorizationfiles` (
  `domain` varchar(64) NOT NULL,
  `createdBy` varchar(64) NOT NULL,
  `tdstamp` datetime DEFAULT NULL,
  `data` blob,
  PRIMARY KEY (`domain`,`createdBy`),
  KEY `ix_authorizationFiles_domain` (`domain`),
  KEY `ix_authorizationFiles_createdBy` (`createdBy`),
  KEY `ix_authorizationFiles_tdstamp` (`tdstamp`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `availableauditfiles`
--

DROP TABLE IF EXISTS `availableauditfiles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `availableauditfiles` (
  `requestID` int(11) NOT NULL,
  `domain` varchar(64) NOT NULL,
  `fileNumber` int(11) NOT NULL,
  `url` varchar(512) DEFAULT NULL,
  `tdstamp` datetime DEFAULT NULL,
  `downloadStatus` int(11) DEFAULT NULL,
  `exportStatus` int(11) DEFAULT NULL,
  PRIMARY KEY (`requestID`,`domain`,`fileNumber`),
  KEY `ix_availableAuditFiles_domain` (`domain`),
  KEY `ix_availableAuditFiles_tdstamp` (`tdstamp`),
  CONSTRAINT `availableauditfiles_ibfk_1` FOREIGN KEY (`requestID`) REFERENCES `emailExportAudits` (`requestID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `domainaccounts`
--

DROP TABLE IF EXISTS `domainaccounts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `domainaccounts` (
  `emailAddress` varchar(128) NOT NULL,
  `username` varchar(128) DEFAULT NULL,
  `domain` varchar(64) DEFAULT NULL,
  `fName` varchar(32) DEFAULT NULL,
  `lName` varchar(32) DEFAULT NULL,
  `isMailboxSetup` smallint(6) DEFAULT NULL,
  `isSuspended` smallint(6) DEFAULT NULL,
  `lastLogin` datetime DEFAULT NULL,
  `recordUpdated` datetime DEFAULT NULL,
  PRIMARY KEY (`emailAddress`),
  KEY `ix_domainAccounts_isMailboxSetup` (`isMailboxSetup`),
  KEY `ix_domainAccounts_recordUpdated` (`recordUpdated`),
  KEY `ix_domainAccounts_domain` (`domain`),
  KEY `ix_domainAccounts_emailAddress` (`emailAddress`),
  KEY `ix_domainAccounts_lName` (`lName`),
  KEY `ix_domainAccounts_lastLogin` (`lastLogin`),
  KEY `ix_domainAccounts_username` (`username`),
  KEY `ix_domainAccounts_fName` (`fName`),
  KEY `ix_domainAccounts_isSuspended` (`isSuspended`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `emailexportaudits`
--

DROP TABLE IF EXISTS `emailexportaudits`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `emailexportaudits` (
  `requestID` int(11) NOT NULL AUTO_INCREMENT,
  `domain` varchar(64) NOT NULL,
  `emailAddress` varchar(128) DEFAULT NULL,
  `adminEmailAddress` varchar(128) DEFAULT NULL,
  `username` varchar(128) DEFAULT NULL,
  `status` varchar(32) DEFAULT NULL,
  `contentType` varchar(32) DEFAULT NULL,
  `requestDate` datetime DEFAULT NULL,
  `beginDate` datetime DEFAULT NULL,
  `endDate` datetime DEFAULT NULL,
  `tdstamp` datetime DEFAULT NULL,
  `includeDeleted` int(11) DEFAULT NULL,
  `completedDate` datetime DEFAULT NULL,
  `numberOfFiles` int(11) DEFAULT NULL,
  `downloadStatus` int(11) DEFAULT NULL,
  `exportStatus` int(11) DEFAULT NULL,
  `gAuditUser` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`requestID`,`domain`),
  KEY `ix_emailExportAudits_beginDate` (`beginDate`),
  KEY `ix_emailExportAudits_status` (`status`),
  KEY `ix_emailExportAudits_adminEmailAddress` (`adminEmailAddress`),
  KEY `ix_emailExportAudits_username` (`username`),
  KEY `ix_emailExportAudits_domain` (`domain`),
  KEY `ix_emailExportAudits_tdstamp` (`tdstamp`),
  KEY `ix_emailExportAudits_requestID` (`requestID`),
  KEY `ix_emailExportAudits_contentType` (`contentType`),
  KEY `ix_emailExportAudits_gAuditUser` (`gAuditUser`),
  KEY `ix_emailExportAudits_requestDate` (`requestDate`),
  KEY `ix_emailExportAudits_completedDate` (`completedDate`),
  KEY `ix_emailExportAudits_emailAddress` (`emailAddress`),
  KEY `ix_emailExportAudits_endDate` (`endDate`)
) ENGINE=InnoDB AUTO_INCREMENT=506883209 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `et`
--

DROP TABLE IF EXISTS `et`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `et` (
  `start` int(10) unsigned NOT NULL,
  `end` int(10) unsigned NOT NULL,
  `tdstamp` datetime DEFAULT NULL,
  PRIMARY KEY (`start`,`end`),
  KEY `ix_et_end` (`end`),
  KEY `ix_et_start` (`start`),
  KEY `ix_et_tdstamp` (`tdstamp`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `exportaudits`
--

DROP TABLE IF EXISTS `exportaudits`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `exportaudits` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `requestID` int(11) DEFAULT NULL,
  `length` int(11) DEFAULT NULL,
  `domain` varchar(64) DEFAULT NULL,
  `emailAddress` varchar(128) DEFAULT NULL,
  `adminEmailAddress` varchar(128) DEFAULT NULL,
  `fileNumber` int(11) DEFAULT NULL,
  `decryptionStatus` varchar(64) DEFAULT NULL,
  `tdstamp` datetime DEFAULT NULL,
  `md5` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_exportAudits_requestID` (`requestID`),
  KEY `ix_exportAudits_md5` (`md5`),
  KEY `ix_exportAudits_emailAddress` (`emailAddress`),
  KEY `ix_exportAudits_domain` (`domain`),
  KEY `ix_exportAudits_tdstamp` (`tdstamp`),
  KEY `ix_exportAudits_decryptionStatus` (`decryptionStatus`),
  KEY `ix_exportAudits_adminEmailAddress` (`adminEmailAddress`),
  KEY `ix_exportAudits_length` (`length`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `geoip`
--

DROP TABLE IF EXISTS `geoip`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `geoip` (
  `start` int(10) unsigned NOT NULL DEFAULT '0',
  `end` int(10) unsigned NOT NULL DEFAULT '0',
  `code` varchar(2) NOT NULL DEFAULT '',
  `name` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`start`,`end`,`code`),
  KEY `start` (`start`,`end`),
  KEY `code` (`code`),
  KEY `start_2` (`start`),
  KEY `end` (`end`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `gpgkeys`
--

DROP TABLE IF EXISTS `gpgkeys`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `gpgkeys` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `domain` varchar(64) DEFAULT NULL,
  `tdstamp` datetime DEFAULT NULL,
  `owner` varchar(128) DEFAULT NULL,
  `private` blob,
  `public` blob,
  PRIMARY KEY (`id`),
  KEY `ix_gpgKeys_owner` (`owner`),
  KEY `ix_gpgKeys_domain` (`domain`),
  KEY `ix_gpgKeys_tdstamp` (`tdstamp`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ip2country`
--

DROP TABLE IF EXISTS `ip2country`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ip2country` (
  `ip` int(10) unsigned NOT NULL DEFAULT '0',
  `code` varchar(2) NOT NULL DEFAULT '',
  PRIMARY KEY (`ip`,`code`),
  KEY `ip` (`ip`),
  KEY `code` (`code`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `knownBad`
--

DROP TABLE IF EXISTS `knownBad`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `knownBad` (
  `ip` int(10) unsigned NOT NULL DEFAULT '0',
  `source` varchar(256) NOT NULL DEFAULT '',
  `tdstamp` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`ip`,`source`,`tdstamp`),
  KEY `ip` (`ip`),
  KEY `source` (`source`),
  KEY `tdstamp` (`tdstamp`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `logins`
--

DROP TABLE IF EXISTS `logins`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `logins` (
  `username` varchar(32) NOT NULL DEFAULT '',
  `domain` varchar(32) NOT NULL DEFAULT '',
  `ip` int(10) unsigned NOT NULL DEFAULT '0',
  `event` varchar(32) DEFAULT NULL,
  `tdstamp` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`username`,`domain`,`ip`,`tdstamp`),
  KEY `username` (`username`),
  KEY `domain` (`domain`),
  KEY `ip` (`ip`),
  KEY `event` (`event`),
  KEY `tdstamp` (`tdstamp`),
  KEY `username_2` (`username`,`domain`,`ip`),
  KEY `username_3` (`username`,`domain`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `mdlblock`
--

DROP TABLE IF EXISTS `mdlblock`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `mdlblock` (
  `ip` int(10) unsigned NOT NULL,
  `url` varchar(256) DEFAULT NULL,
  `domain` varchar(256) NOT NULL,
  `date` datetime DEFAULT NULL,
  `reverseLookup` varchar(256) DEFAULT NULL,
  `description` varchar(256) DEFAULT NULL,
  `registrant` varchar(256) DEFAULT NULL,
  `tdstamp` datetime DEFAULT NULL,
  `comment` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`ip`,`domain`),
  KEY `ix_mdl_date` (`date`),
  KEY `ix_mdl_domain` (`domain`),
  KEY `ix_mdl_registrant` (`registrant`),
  KEY `ix_mdl_reverseLookup` (`reverseLookup`),
  KEY `ix_mdl_ip` (`ip`),
  KEY `ix_mdl_url` (`url`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user2country`
--

DROP TABLE IF EXISTS `user2country`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user2country` (
  `username` varchar(32) NOT NULL DEFAULT '',
  `domain` varchar(32) NOT NULL DEFAULT '',
  `code` varchar(2) NOT NULL DEFAULT '',
  PRIMARY KEY (`username`,`domain`,`code`),
  KEY `username` (`username`),
  KEY `username_2` (`username`,`domain`),
  KEY `code` (`code`),
  KEY `username_3` (`username`,`code`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nickname` varchar(64) DEFAULT NULL,
  `email` varchar(120) DEFAULT NULL,
  `role` smallint(6) DEFAULT NULL,
  `password_hash` varchar(128) DEFAULT NULL,
  `fName` varchar(32) DEFAULT NULL,
  `lName` varchar(32) DEFAULT NULL,
  `accountCreated` datetime DEFAULT NULL,
  `lastLogin` datetime DEFAULT NULL,
  `confirmed` smallint(6) DEFAULT NULL,
  `disabled` smallint(6) DEFAULT NULL,
  `acountApproved` smallint(6) DEFAULT NULL,
  `org` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_users_nickname` (`nickname`),
  UNIQUE KEY `ix_users_email` (`email`),
  KEY `ix_users_confirmed` (`confirmed`),
  KEY `ix_users_fName` (`fName`),
  KEY `ix_users_acountApproved` (`acountApproved`),
  KEY `ix_users_lastLogin` (`lastLogin`),
  KEY `ix_users_disabled` (`disabled`),
  KEY `ix_users_lName` (`lName`),
  KEY `ix_users_org` (`org`)
) ENGINE=MyISAM AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2015-01-12 12:20:01
