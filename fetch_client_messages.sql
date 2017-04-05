SELECT 
	message.id,
	user.uuid as client_uuid,
	body,
	sent_on,
	IF(message.body LIKE '%help%' or message.body LIKE '%ayuda%' or message.body LIKE 'h', true, false) is_high_risk,
	GROUP_CONCAT(distinct p.phone_number) as partner_numbers
	
FROM message INNER JOIN user on message.from = user.phone_number

INNER JOIN location_user_association cl on cl.uuid = user.uuid
LEFT JOIN location_user_association pl on pl.`location_id` = cl.location_id AND pl.uuid != user.uuid
INNER JOIN user p on p.uuid = pl.uuid

WHERE processed_on is NULL
AND direction = 'inbound'
AND user.type = 'client'
GROUP BY 1
ORDER BY sent_on
