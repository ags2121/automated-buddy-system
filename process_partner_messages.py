import util
import logging
import os
import time

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler("./process_partner_messages.log")
logger.addHandler(fh)

def process_partner_msgs(tw_client):
	positive_response_threshold = 2
	db, cur = util.get_db_conn()

	with open('fetch_positive_responses.sql', 'r') as queryfile:
		query=queryfile.read()

	cur.execute(query)
	results = cur.fetchall()
	logger.debug(positive_response_threshold)
	logger.debug(results)

	for res in results:
		partner_uuids_with_pos_response = res['partner_uuids_with_pos_response'].split(',')

		if len(partner_uuids_with_pos_response) >= positive_response_threshold:

			client_uuid, client_location_id = res['client_uuid'], res['location_id']
			first_msg_sent, last_msg_sent = res['first_msg_sent'], res['last_msg_sent']

			ids = ', '.join(map(lambda x: '%s', partner_uuids_with_pos_response))

			cur.execute("""
				SELECT phone_number
				FROM user
				LEFT JOIN location_user_association lua on lua.uuid = user.uuid
				WHERE lua.location_id = '%(client_location_id)s'
				AND user.type = 'partner'
				AND user.uuid not in (%(ids)s)
				""" % {'client_location_id': client_location_id, 'ids': ids}, [p for p in partner_uuids_with_pos_response])

			non_pos_respondent_numbers = [row['phone_number'] for row in cur.fetchall()]

			for num in non_pos_respondent_numbers:
				util.send_sms(tw_client, num, 'Client %s has received enough positive responses.' % client_uuid)

			cur.execute("""
				UPDATE message 
				SET response_threshold_hit_on = NOW() 
				WHERE sent_on 
				BETWEEN %s AND %s
				""", (first_msg_sent, last_msg_sent,))

	db.commit()
	cur.close()

if __name__ == '__main__':	
	os.system("pkill -xf 'python process_partner_messages.py' || true")
	while True:
		process_partner_msgs(util.get_twilio_client())
		time.sleep(2)
