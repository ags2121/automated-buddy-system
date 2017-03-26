import util
import csv

import pprint
pp = pprint.PrettyPrinter(indent=4)

def insert(rows, table, cursor):
	columns = ', '.join(map(lambda x: '`%s`' % x, rows[0].keys()))
	for row in rows:
		values = ', '.join(map(lambda x: x if x == 'NULL' else "'%s'" % x, row.values()))
		cursor.execute('INSERT INTO %s(%s) VALUES(%s)' % (table, columns, values))	

def create_db():
	db, cursor = util.get_db_conn()

	with open('create_tables.sql', 'r') as queryfile:
		queries=queryfile.read().split(';')

	[cursor.execute(query) for query in queries if query != '\n']

	users = [row for row in csv.DictReader(open('user.csv'))]
	#messages = [row for row in csv.DictReader(open('message.csv'))]

	insert(users, 'user', cursor)
	#insert(messages, 'message', cursor)
	db.commit()
	cursor.close()

def write_messages_to_db(tw_client):
	twilio_date_fmt = '%Y-%m-%d'
	db, cursor = util.get_db_conn()
	cursor.execute('SELECT MAX(forwarded_on) as forwarded_on FROM message')
	time_of_last_processed_msg = cursor.fetchall()[0]['forwarded_on']

	date_sent = time_of_last_processed_msg.strftime(twilio_date_fmt) if time_of_last_processed_msg != None else None
	latest_msgs = tw_client.messages.list(DateSent=date_sent)

	msgs_for_db = []
	for msg in latest_msgs:

		# if msg is from partner phone number, unpack the client id referred to in the message body
		client_msg_id = 'NULL'
		get_partner_phone_sql = "SELECT phone_number FROM user WHERE phone_number = %s AND type = 'partner'"
		if msg.direction == 'inbound' and cursor.execute(get_partner_phone_sql, (msg.from_,)):
			first_token = msg.body.split(' ')[0]
			if first_token.isnumeric():
				client_msg_id = first_token

		msg_for_db = {'from': msg.from_, 'to': msg.to, 'body': msg.body, 'direction': msg.direction, 'sent_on': msg.date_sent, 'client_message_id': client_msg_id}
		msgs_for_db.append(msg_for_db)

	insert(msgs_for_db, 'message', cursor)

	db.commit()
	cursor.close()
	return latest_msgs

def main():
	create_db()
	write_messages_to_db(util.get_twilio_client())
