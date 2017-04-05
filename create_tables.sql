DROP TABLE IF EXISTS `message`;
CREATE TABLE `message` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `from` varchar(15) NOT NULL,
  `to` varchar(15) NOT NULL,
  `body` varchar(1600) NOT NULL,
  `sent_on` timestamp NULL DEFAULT NULL,
  `processed_on` timestamp NULL DEFAULT NULL,
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
INSERT INTO `user` (`uuid`, `phone_number`, `type`)
VALUES
  ('nsC1','xxxxxxxxx1','client'),
  ('nsP1','+xxxxxxxxx2','partner'),
  ('nsP2','+xxxxxxxxx3','partner');

DROP TABLE IF EXISTS `location_user_association`;
CREATE TABLE `location_user_association` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `location_id` varchar(1) NOT NULL DEFAULT '',
  `uuid` varchar(5) DEFAULT NULL,
  PRIMARY KEY (`id`)
);
INSERT INTO `location_user_association` (`id`, `location_id`, `uuid`)
VALUES
  (1,'A','nsP1'),
  (2,'A','nsP2'),
  (3,'A','nsC1');
