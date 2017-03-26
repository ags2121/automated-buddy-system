DROP TABLE IF EXISTS `message`;
CREATE TABLE `message` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `from` varchar(15) NOT NULL,
  `to` varchar(15) NOT NULL,
  `body` varchar(1600) NOT NULL,
  `sent_on` timestamp NULL DEFAULT NULL,
  `forwarded_on` timestamp NULL DEFAULT NULL,
  `direction` varchar(15) DEFAULT NULL,
  `response_threshold_hit_on` timestamp NULL DEFAULT NULL,
  `client_message_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
);

DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `uuid` varchar(5) NOT NULL,
  `phone_number` varchar(15) NOT NULL,
  `type` varchar(10) NOT NULL,
  PRIMARY KEY (`phone_number`)
);
