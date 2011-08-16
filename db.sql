CREATE DATABASE `shadowmind` /*!40100 DEFAULT CHARACTER SET latin1 */$$

CREATE TABLE `_board` (
	  `id` int(11) NOT NULL AUTO_INCREMENT,
	  `vendor` varchar(45) DEFAULT NULL,
	  `string` varchar(255) DEFAULT NULL,
	  `serial` varchar(255) DEFAULT NULL,
	  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1$$

CREATE TABLE `_cpu` (
	  `id` int(11) NOT NULL AUTO_INCREMENT,
	  `string` varchar(255) NOT NULL,
	  `serial` varchar(255) DEFAULT NULL,
	  `slot` varchar(45) DEFAULT NULL,
	  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1$$

CREATE TABLE `_disk` (
	  `id` int(11) NOT NULL AUTO_INCREMENT,
	  `string` varchar(255) DEFAULT NULL,
	  `serial` varchar(255) DEFAULT NULL,
	  `size` varchar(45) DEFAULT NULL,
	  PRIMARY KEY (`id`),
	  UNIQUE KEY `serial_UNIQUE` (`serial`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1$$

CREATE TABLE `_face` (
	  `id` int(11) NOT NULL AUTO_INCREMENT,
	  `string` varchar(255) DEFAULT NULL,
	  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1$$

CREATE TABLE `_host` (
	  `id` int(11) NOT NULL AUTO_INCREMENT,
	  `hostname` varchar(255) DEFAULT NULL,
	  `string` varchar(255) DEFAULT NULL,
	  `arch` varchar(45) DEFAULT NULL,
	  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1$$

CREATE TABLE `_ipv4` (
	  `id` int(11) NOT NULL AUTO_INCREMENT,
	  `addr` varchar(15) DEFAULT NULL,
	  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1$$

CREATE TABLE `_mem` (
	  `id` int(11) NOT NULL AUTO_INCREMENT,
	  `string` varchar(255) DEFAULT NULL,
	  `size` int(11) DEFAULT NULL,
	  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1$$

CREATE TABLE `_net` (
	  `id` int(11) NOT NULL AUTO_INCREMENT,
	  `string` varchar(255) DEFAULT NULL,
	  `hwaddr` varchar(17) DEFAULT NULL,
	  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1$$

CREATE TABLE `current` (
	  `id` int(11) NOT NULL AUTO_INCREMENT,
	  `main_id` int(11) DEFAULT NULL,
	  `gadget_type` varchar(12) DEFAULT NULL,
	  `gadget_id` int(11) DEFAULT NULL,
	  `status_time` datetime DEFAULT NULL,
	  `status` tinyint(1) DEFAULT NULL,
	  `historical` tinyint(1) DEFAULT NULL,
	  PRIMARY KEY (`id`),
	  UNIQUE KEY `id_UNIQUE` (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=10 DEFAULT CHARSET=latin1$$

CREATE TABLE `main` (
	  `id` int(11) NOT NULL AUTO_INCREMENT,
	  `machine_id` varchar(40) DEFAULT NULL,
	  `update_time` datetime DEFAULT NULL,
	  PRIMARY KEY (`id`),
	  UNIQUE KEY `machine_id_UNIQUE` (`machine_id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1$$

