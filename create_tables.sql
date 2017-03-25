DROP TABLE IF EXISTS `message`;
CREATE TABLE `message` (
  `to` varchar(15) NOT NULL,
  `from` varchar(15) NOT NULL,
  `body` varchar(1600) NOT NULL,
  `sent_on` timestamp NULL DEFAULT NULL,
  `processed_on` timestamp NULL DEFAULT NULL,
  `message_type` varchar(15) DEFAULT NULL,
  `direction` varchar(15) DEFAULT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
);

DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `uuid` varchar(5) NOT NULL,
  `phone_number` varchar(15) NOT NULL,
  `type` varchar(10) NOT NULL,
  PRIMARY KEY (`phone_number`)
);
