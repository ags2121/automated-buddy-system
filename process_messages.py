from datetime import datetime
import util
import yaml

def is_high_risk(messsage):
	return len(set(messsage.split(' ')).intersection(['Help', 'help', 'h', 'H'])) == True	

def process_partner_msgs(tw_client):
	positive_response_threshold = 5
	db, cur = util.get_db_conn()

	cur.execute("""
		SELECT client_message_id, count(distinct user.uuid) as positive_responses
		FROM message INNER JOIN user on message.from = user.phone_number
		WHERE response_threshold_hit_on is NULL
		AND client_message_id is not NULL
		AND direction = 'inbound'
		AND user.type = 'partner'
		GROUP BY client_message_id
		""")
	results = cur.fetchall()

	for res in results:
		positive_responses, client_msg_id = res['positive_responses'], res['client_message_id']
		if positive_responses >= positive_response_threshold:

			cur.execute("""
				SELECT distinct user.*
				FROM message INNER JOIN user on message.from = user.phone_number
				WHERE client_message_id = %s
				AND direction = 'inbound'
				AND user.type = 'partner'
				""", (client_msg_id,))
			respondents = [row['phone_number'] for row in cur.fetchall()]

			cur.execute("""
				SELECT distinct user.*
				FROM message INNER JOIN user on message.to = user.phone_number
				WHERE client_message_id = %s
				AND direction = 'outbound-api'
				""", (client_msg_id,))
			recipients = cur.fetchall()

			for recipient in recipients:
				if recipient['phone_number'] not in respondents:
					util.send_sms(tw_client, recipient['phone_number'], 'do not show up for MSG ID: %s' % res['client_message_id'])

			cur.execute('UPDATE message SET response_threshold_hit_on = NOW() WHERE id = %s', (client_msg_id,))

	db.commit()
	cur.close()


def process_client_msgs(tw_client):
	db, cur = util.get_db_conn()
	cur.execute("""
		SELECT `id`, `from`, `body`, `user.uuid`, `user.type`
		FROM message INNER JOIN user on message.from = user.phone_number
		WHERE forwarded_on is NULL
		AND direction = 'inbound'
		AND user.type = 'client'
		ORDER BY sent_on
		""")
	new_msgs = cur.fetchall()

	forwarded_high_risk_msgs = {}
	for m in new_msgs:
		uuid, type_ = m['uuid'], m['type']

		if not is_high_risk(m['body']):
			continue

		location = get_client_location(uuid)
		if location == None:
			print('Client %s is not associated with a location' % uuid)
			continue

		partner_uuids = get_partners_for_location(location)
		if partner_uuids == None:
			print('No partners are associated with location %s' % location)
			continue

		partner_numbers = get_partner_numbers(db_cursor, partner_uuids)
		msg_template = 'MSG ID: {0} - MSG BODY: {1} (include MSG ID "{0}" in your response)'
		msg_template = '"{0}". Respond with "{1} omw" or "{1} noshow".'
		forwarded_high_risk_msgs[m['id']] = [util.send_sms(tw_client, number, msg_template.format(m['body'], m['id'])) for number in partner_numbers]

	# TODO: check response codes on forwarded_high_risk_msgs
	# if there are errors, don't mark new messages as processed
	print(forwarded_high_risk_msgs)
	ids = ', '.join(map(lambda x: '%s', new_msgs))
	cur.execute("""
		UPDATE message
		SET forwarded_on = NOW()
		WHERE id in (%s)
		""", ids % [m['id'] for m in new_msgs])
	db.commit()
	cur.close()

def get_client_location(client_uuid):
	client_location_map = yaml.load(open('clientuuid_to_location.yaml', 'r'))
	return client_location_map.get(client_uuid)

def get_partners_for_location(location):
	location_partner_map = yaml.load(open('location_to_partneruuid.yaml', 'r'))
	return location_partner_map.get(location)

def get_partner_numbers(cur, partner_uuids):
	partner_numbers = []
	for p in partner_uuids:
		if cur.execute('SELECT phone_number FROM user WHERE uuid = %s', (p,)) == 0:
			print('No record in DB for user with uuid: %s', p)
			continue
		partner_numbers.append(cur.fetchall()[0]['phone_number'])

	return partner_numbers
