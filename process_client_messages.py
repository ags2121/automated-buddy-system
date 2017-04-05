	import util
import daemon
import logging
import os
import time

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler("./process_client_messages.log")
logger.addHandler(fh)

def is_high_risk(messsage):
	return len(set(messsage.split(' ')).intersection(['Help', 'help', 'h', 'H'])) == True	

def process_client_msgs(tw_client):
	db, cur = util.get_db_conn()
	cur.execute("""
		SELECT `id`, `from`, `body`, user.`uuid`, user.`type`
		FROM message INNER JOIN user on message.from = user.phone_number
		WHERE processed_on is NULL
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

		location = util.get_client_location(uuid)
		if location == None:
			logger.warn('Client %s is not associated with a location' % uuid)
			continue

		partner_uuids = util.get_partners_for_location(location)
		if partner_uuids == None:
			logger.warn('No partners are associated with location %s' % location)
			continue

		partner_numbers = util.get_partner_numbers(cur, partner_uuids)
		msg_template = '"{0}". Respond with "{1} omw" or "{1} noshow".'
		forwarded_high_risk_msgs[m['id']] = [util.send_sms(tw_client, number, msg_template.format(m['body'], m['id'])) for number in partner_numbers]

	# TODO: check response codes on forwarded_high_risk_msgs
	# if there are errors, don't mark new messages as processed
	# logger.warn(forwarded_high_risk_msgs)
	if len(new_msgs) == 0:
		return

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
	with daemon.DaemonContext(files_preserve = [fh.stream]):
		while True:
			process_client_msgs(util.get_twilio_client())
			time.sleep(2)		
