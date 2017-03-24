from twilio.rest import TwilioRestClient
import MySQLdb
import csv
import yaml

db_config = yaml.load(open('credentials.yaml', 'r'))['db']

def seed_db():
	conn = MySQLdb.connect(
		host=db_config['host'], 
		user=db_config['user'], 
		passwd=db_config['password'], 
		db=db_config['database'])
	cur = conn.cursor()

	with open('create_tables.sql', 'r') as queryfile:
		queries=queryfile.read().split(';')

	[cur.execute(query) for query in queries if query != '\n']

	users = [row for row in csv.DictReader(open('user.csv'))]
	messages = [row for row in csv.DictReader(open('message.csv'))]

	def insert(rows, table):
		columns = ', '.join(map(lambda x: x, rows[0].keys()))
		print(columns)
		for row in rows:
			values = ', '.join(map(lambda x: x if x == 'NULL' else "'%s'" % x, row.values()))
			cur.execute('INSERT INTO %s(%s) VALUES(%s)' % (table, columns, values))

	insert(users, 'user')
	insert(messages, 'message')
	conn.commit()
	cur.close()

