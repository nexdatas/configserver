--
-- Table structure for table `components`
--

DROP TABLE IF EXISTS `components`;
CREATE TABLE `components` (
  `name` varchar(100) BINARY NOT NULL,
  `xml` longtext BINARY NOT NULL,
  `mandatory` tinyint(1) NOT NULL,
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

--
-- Table structure for table `datasources`
--

DROP TABLE IF EXISTS `datasources`;
CREATE TABLE `datasources` (
  `name` varchar(100) BINARY NOT NULL,
  `xml` mediumtext BINARY NOT NULL,
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;


--
-- Table structure for table `properties`
--

DROP TABLE IF EXISTS `properties`;
CREATE TABLE `properties` (
  `name` varchar(100) BINARY NOT NULL,
  `value` varchar(100) BINARY NOT NULL,
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
INSERT INTO properties values('revision','0');
