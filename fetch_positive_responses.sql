SELECT 
	c.uuid as client_uuid,
	c.location_id,
	c.first_msg_sent,
	c.last_msg_sent,
	GROUP_CONCAT(distinct p.uuid) as partner_uuids_with_pos_response
FROM
(
SELECT user.uuid, message.from, min(message.sent_on) first_msg_sent, max(message.sent_on) last_msg_sent, lua.location_id
FROM message 
INNER JOIN user on message.from = user.phone_number
-- clients can only have 1 associated location for now
INNER JOIN location_user_association lua on lua.uuid = user.uuid

WHERE response_threshold_hit_on is null
AND user.`type` = 'client'
AND (message.body LIKE '%help%' or message.body LIKE '%ayuda%' or message.body LIKE 'h')
GROUP BY message.from, lua.location_id
) c

INNER JOIN 

(
SELECT message.body, message.sent_on, user.*, lua.location_id
FROM message 
INNER JOIN user on message.from = user.phone_number
-- parnters can be associated with more than one location
LEFT JOIN location_user_association lua on lua.uuid = user.uuid
WHERE user.`type` = 'partner'
AND (body LIKE '%omw%' or body LIKE '%On My Way!%')
) p

ON c.first_msg_sent <= p.sent_on
AND c.location_id = p.location_id
AND p.body LIKE concat('%', c.uuid, '%')
GROUP BY 1,2,3,4;