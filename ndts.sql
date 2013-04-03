--
-- Table structure for table `components`
--

DROP TABLE IF EXISTS `components`;
CREATE TABLE `components` (
  `name` varchar(100) NOT NULL,
  `xml` longtext NOT NULL,
  `mandatory` tinyint(1) NOT NULL,
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

--
-- Table structure for table `datasources`
--

DROP TABLE IF EXISTS `datasources`;
CREATE TABLE `datasources` (
  `name` varchar(100) NOT NULL,
  `xml` mediumtext NOT NULL,
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
