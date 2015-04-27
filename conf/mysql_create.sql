--
-- Table structure for table `components`
--

CREATE TABLE IF NOT EXISTS `components` (
  `name` varchar(100) BINARY NOT NULL,
  `xml` longtext BINARY NOT NULL,
  `mandatory` tinyint(1) NOT NULL,
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

--
-- Table structure for table `datasources`
--

CREATE TABLE IF NOT EXISTS `datasources` (
  `name` varchar(100) BINARY NOT NULL,
  `xml` mediumtext BINARY NOT NULL,
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;


--
-- Table structure for table `properties`
--

CREATE TABLE IF NOT EXISTS `properties` (
  `name` varchar(100) BINARY NOT NULL,
  `value` varchar(100) BINARY NOT NULL,
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

--
-- Table structure for table `selections`
--

CREATE TABLE IF NOT EXISTS `selections` (
  `name` varchar(100) BINARY NOT NULL,
  `selection` mediumtext BINARY NOT NULL,
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;


--
-- Init the revision counter if not exists
--
INSERT INTO properties  (name, value) SELECT * FROM (SELECT 'revision', '0') AS tmp WHERE NOT EXISTS ( SELECT name FROM properties WHERE name ='revision' ) LIMIT 1;
