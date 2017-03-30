import util
import daemon
import logging
import os
import time

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler("./process_partner_messages.log")
logger.addHandler(fh)

def process_partner_msgs(tw_client):
	positive_response_threshold = 1
	db, cur = util.get_db_conn()

	cur.execute("""
		SELECT client_message_id, count(distinct user.uuid) as positive_responses
		FROM message INNER JOIN user on message.from = user.phone_number
		WHERE response_threshold_hit_on is NULL
		AND client_message_id is not NULL
		AND direction = 'inbound'
		AND user.type = 'partner'
		AND (body LIKE '%omw%' or body LIKE '%On My Way!%')
		GROUP BY client_message_id
		""")
	results = cur.fetchall()
	logger.debug(positive_response_threshold)
	logger.debug(results)

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
			respondent_numbers = [row['phone_number'] for row in cur.fetchall()]

			if cur.execute("""
				SELECT uuid
				FROM user INNER JOIN message on message.from = user.phone_number
				WHERE message.id = %s;
				""", (client_msg_id,)) == 0:
				logger.warn('Message id %s was not a client message. This may indicate a bug in the program.' % client_msg_id)
				continue

			client_uuid = cur.fetchall()[0]['uuid']
			recipients_numbers = util.get_partner_numbers(cur, util.get_partners_for_location(util.get_client_location(client_uuid)))

			for recipient_number in recipients_numbers:
				if recipient_number not in respondent_numbers:
					util.send_sms(tw_client, recipient_number, 'do not show up for MSG ID: %s' % res['client_message_id'])

			cur.execute('UPDATE message SET response_threshold_hit_on = NOW() WHERE id = %s', (client_msg_id,))

	db.commit()
	cur.close()

if __name__ == '__main__':	
	os.system("pkill -xf 'python process_partner_messages.py' || true")
	with daemon.DaemonContext(files_preserve = [fh.stream]):
		while True:
			process_partner_msgs(util.get_twilio_client())
			time.sleep(2)
