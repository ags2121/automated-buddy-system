DROP TABLE IF EXISTS `message`;
CREATE TABLE `message` (
  `phone_number` varchar(10) NOT NULL,
  `message_body` varchar(6) NOT NULL,
  `sent_on` timestamp NULL DEFAULT NULL,
  `processed_on` timestamp NULL DEFAULT NULL,
  `message_type` varchar(8) DEFAULT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
);

DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `uuid` varchar(5) NOT NULL,
  `phone_number` varchar(10) NOT NULL,
  `type` varchar(7) NOT NULL,
  PRIMARY KEY (`phone_number`)
);
