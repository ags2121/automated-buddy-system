from datetime import datetime
import util
import yaml

def is_high_risk(messsage):
	return len(set(messsage.split(' ')).intersection(['Help', 'help', 'h', 'H'])) == True

def process_new_client_msgs(tw_client):
	db, cur = util.get_db_conn()
	cur.execute("""
		SELECT `id`, `from`, `body`
		FROM message
		WHERE processed_on is NULL
		AND direction = 'inbound'
		ORDER BY sent_on
		""")
	new_msgs = cur.fetchall()

	forwarded_high_risk_msgs = {}
	for m in new_msgs:
		if is_high_risk(m['body']):
			if cur.execute('SELECT `uuid` FROM user WHERE phone_number = %s', (m['from'],)) == 0:
				print('Text received from unknown number: %s' % m['from'])
				continue

			client_uuid = cur.fetchall()[0]['uuid']
			location = get_client_location(client_uuid)
			if location == None:
				print('Message id %s is not from a client.' % m['id'])
				continue

			partner_uuids = get_partners_for_location(location)
			if partner_uuids == None:
				print('No partners are associated with location %s' % location)
				continue

			partner_numbers = get_partner_numbers(cur, partner_uuids)
			msg_template = 'MSG ID: {} - MSG BODY: {} (include MSG ID in your response)'
			forwarded_high_risk_msgs[m['id']] = [util.send_sms(tw_client, number, msg_template.format(m['id'], m['body'])) for number in partner_numbers]

	# TODO: check response codes on forwarded_high_risk_msgs
	# if there are errors, don't mark new messages as processed
	print(forwarded_high_risk_msgs)
	print('yo')
	ids = ', '.join(map(lambda x: '%s', new_msgs))
	cur.execute("""
		UPDATE message
		SET processed_on = NOW()
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

if __name__ == '__main__':
	process_new_messages()
