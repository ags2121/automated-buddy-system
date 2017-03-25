from twilio.rest import TwilioRestClient
import MySQLdb
import csv
import yaml
import pprint 
pp = pprint.PrettyPrinter(indent=4)

def get_twilio_client(config):
	return TwilioRestClient(config['account_sid'], config['auth_token'])

def get_db_conn(config):
	db = MySQLdb.connect(
		host=config['host'], 
		user=config['user'], 
		passwd=config['password'], 
		db=config['database'])
	return db, db.cursor()

def insert(rows, table, cursor):
	columns = ', '.join(map(lambda x: '`%s`' % x, rows[0].keys()))
	for row in rows:
		values = ', '.join(map(lambda x: x if x == 'NULL' else "'%s'" % x, row.values()))
		cursor.execute('INSERT INTO %s(%s) VALUES(%s)' % (table, columns, values))	

def seed_db(db_config):
	db, cursor = get_db_conn(db_config)

	with open('create_tables.sql', 'r') as queryfile:
		queries=queryfile.read().split(';')

	[cursor.execute(query) for query in queries if query != '\n']

	users = [row for row in csv.DictReader(open('user.csv'))]
	messages = [row for row in csv.DictReader(open('message.csv'))]

	insert(users, 'user', cursor)
	insert(messages, 'message', cursor)
	db.commit()
	cursor.close()

def fetch_messages(db_config):
	twilio_date_fmt = '%Y-%m-%d'
	db, cursor = get_db_conn(db_config)
	cursor.execute('SELECT MAX(processed_on) FROM message')
	time_of_last_processed_msg = cursor.fetchall()[0][0]

	date_sent = time_of_last_processed_msg.strftime(twilio_date_fmt) if time_of_last_processed_msg != None else None
	latest_msgs = client.messages.list(DateSent=date_sent)

	msgs_for_db = [{'from': msg.from_, 'to': msg.to, 'body':msg.body, 'direction': msg.direction, 'sent_on': msg.date_sent} for msg in latest_msgs]
	insert(msgs_for_db, 'message', cursor)

	db.commit()
	cursor.close()
	return latest_msgs

config = yaml.load(open('credentials.yaml', 'r'))
db_config = config['db']
client = get_twilio_client(config['twilio'])

def main():
	seed_db(db_config)
	fetch_messages(db_config)
