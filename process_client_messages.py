import util
import logging
import os
import time

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler("./process_client_messages.log")
logger.addHandler(fh)

def process_client_msgs(tw_client):
	db, cur = util.get_db_conn()

	with open('fetch_client_messages.sql', 'r') as queryfile:
		query=queryfile.read()

	cur.execute(query)
	new_msgs = cur.fetchall()

	forwarded_high_risk_msgs = {}
	for m in new_msgs:
		client_uuid = m['client_uuid']

		if not m['is_high_risk']:
			continue

		# TODO: truncate client message body to fit into max body char limit
		msg_template = 'Client {1} says: "{0}". Respond with "{1} omw" or "{1} noshow".'
		partner_numbers = m['partner_numbers'].split(',')
		forwarded_high_risk_msgs[m['id']] = [util.send_sms(tw_client, number, msg_template.format(m['body'], client_uuid)) for number in partner_numbers]

	if len(new_msgs) == 0:
		return

	# TODO: check response codes on forwarded_high_risk_msgs
	# if there are errors, don't mark new messages as processed		

	ids = ', '.join(map(lambda x: '%s', new_msgs))
	cur.execute("""
		UPDATE message
		SET processed_on = NOW()
		WHERE id in (%s)
		""" % ids, [m['id'] for m in new_msgs])

	db.commit()
	cur.close()

if __name__ == '__main__':	
	os.system("pkill -xf 'python process_client_messages.py' || true")
	while True:
		process_client_msgs(util.get_twilio_client())
		time.sleep(2)
